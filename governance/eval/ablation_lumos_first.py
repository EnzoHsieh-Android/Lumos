#!/usr/bin/env python3
"""修法 A ablation runner(Projects/修法A_lumos先行ablation_計劃):
「CLAUDE.md 那段『第一個工具呼叫是 lumos』+入口 hook 同句」帶/不帶,各跑同一組情境題,比四個尺。

做法(2026-09-02 第二版):工作單位=(組別, 題),每題需要幾場就叫探針跑幾場(`--only <題> --runs <缺幾場>`),
輸出一檔一次嘗試、永不覆蓋;重跑時先數每題已有的**有效**場次(排除撞用量上限/儀器例外),只補缺的。
第一版按 shard 切、4 路平行,35 分鐘撞到帳號用量上限,之後 115 場全是 4 秒假失敗——所以現在預設 2 路、
探針帶 --wait-on-limit 撞到就等重置再補同一場。

四個尺(讀法預註冊在計劃筆記,這裡只算數不解讀):
  M1 通過率(期望指令在禁做動作之前)  M2 整場有沒有敲過 lumos
  M3 首次敲 lumos 的步數中位(只算有敲的場)  M4 答案題(id 以 a 開頭)正確率

用法:
  governance/eval/ablation_lumos_first.py [--runs 3] [--workers 2] [--wait-on-limit 7200] [--out-dir …] [--merge-only]
"""
import argparse, datetime, json, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "scripts" / "scenario_probe.py"
DEFAULT_Q = ["governance/scenarios/commands.jsonl", "governance/scenarios/answers.jsonl"]
ARMS = ["with", "without"]

# ★r1 合約席:判準單一實作來源★——LIMIT_RE / LUMOS_CALL_RE 從探針 import,不在這裡重抄一份字面。
# 同目錄 retrieval_eval_multiword 早有此教訓(「計分一律 import,兩份實作立刻漂移」)。改判準只改探針一處。
sys.path.insert(0, str(ROOT / "scripts"))
from scenario_probe import LIMIT_RE, LUMOS_CALL_RE  # noqa: E402  ★單一實作來源★


def load_ids(files):
    """回題目 id 清單,已去重(★r1 邊界席:題庫人手維護、複製貼上易出重複 id;重複會虛墊缺場數又雙倍排程/雙倍權重★)。"""
    ids, seen = [], set()
    for f in files:
        for ln in (ROOT / f).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                qid = json.loads(ln)["id"]
                if qid not in seen:
                    seen.add(qid); ids.append(qid)
    return ids


def backfill_limit(r):
    """舊結果檔沒有 limit_hit 欄:零工具呼叫 + 回覆是上限訊息 → 補標 True。有欄的原樣。
    用修正後的正則從 calls 重算 ever_lumos / first_lumos_idx(舊版正則把路徑/引號裡的 lumos 算進去,灌水)。
    ★截斷處理(r2 三分支,取代 r1「截斷保留 True」)★:第一版只存前 12 個呼叫。
      ①沒截斷 → 直接用重算值;②截斷且可見清單裡看得到真呼叫 → 確定 True;
      ③截斷且可見清單裡看不到真呼叫 → 分不清「真呼叫在被砍的第 13+ 筆」還是「舊值是舊正則假陽性」→ 標未知 None
      (_arm_stats 把 None 排除在 M2 分母外,不當 False 灌低、也不保留可能的假陽性 True)。"""
    if "limit_hit" not in r:
        r["limit_hit"] = (r.get("n_calls", 0) == 0) and bool(LIMIT_RE.search(r.get("answer") or ""))
    calls = r.get("calls") or []
    truncated = r.get("n_calls", 0) > len(calls)
    r["calls_truncated"] = truncated
    ever, idx = False, None
    for i, c in enumerate(calls):
        if isinstance(c, (list, tuple)) and len(c) == 2 and c[0] == "Bash" and LUMOS_CALL_RE.search(str(c[1])):
            ever, idx = True, i
            break
    if not truncated:
        r["ever_lumos"], r["first_lumos_idx"] = ever, idx
    elif ever:
        r["ever_lumos"], r["first_lumos_idx"] = True, idx   # 殘缺清單裡就看得到真呼叫 → 確定 True
    else:
        # ★r2 正確性席:截斷 + 殘缺清單裡看不到真呼叫 → 分不清「真呼叫在被砍掉的部分」還是「舊值是舊正則假陽性」。
        # 原本無條件保留 True 會把可從殘缺清單判掉的假陽性也留著(灌 M2);改標未知(None),_arm_stats 把 None 排除在 M2 分母外。★
        r["ever_lumos"], r["first_lumos_idx"] = None, None
    return r


def is_valid(r):
    """一場算不算數:撞用量上限或儀器例外都不算(不是被測 AI 的行為)。"""
    return not r.get("limit_hit") and not str(r.get("reason", "")).startswith("儀器例外")


def load_results(out_dir):
    """讀目錄裡所有探針輸出(第一版 shard 檔與第二版逐題檔都吃),回 {arm: [result…]}。
    ★r1 邊界席:一顆壞檔不拖垮整批——非 dict 頂層、results 內非 dict 元素都跳過,不讓 AttributeError 炸穿。"""
    by_arm = {a: [] for a in ARMS}
    for p in sorted(Path(out_dir).glob("*.json")):
        if p.name in ("summary.json", "meta.json"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        arm = d.get("arm") or p.name.split("-")[0]
        rows = d.get("results")
        if arm in by_arm and isinstance(rows, list):
            by_arm[arm].extend(backfill_limit(r) for r in rows if isinstance(r, dict))
    return by_arm


def collect_skills_health(out_dir):
    """掃探針輸出裡的 skills_health_bad 欄,回 [(檔名, [壞連結…])](空=乾淨)。
    ★r1 併發席:健康檢查不能只印 log——跑批讀這個,非空就停整批,免得一場沙盒事故靜默污染後續所有場次。"""
    hits = []
    for p in sorted(Path(out_dir).glob("*.json")):
        if p.name in ("summary.json", "meta.json"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("skills_health_bad"):
            hits.append((p.name, d["skills_health_bad"]))
    return hits


def needed(by_arm, arm, qid, runs):
    """這題這組還缺幾場有效結果。"""
    have = sum(1 for r in by_arm.get(arm, []) if r.get("id") == qid and is_valid(r))
    return max(0, runs - have)


def runs_in_window(out_dir, hours=5.0, now=None):
    """最近 hours 小時內落地的探針場次(含撞上限的):算帳號窗口用掉多少。以檔案 mtime 為時間,沿用結果檔沒有時間戳的現況。"""
    now = time.time() if now is None else now
    n = 0
    for p in Path(out_dir).glob("*.json"):
        if p.name in ("summary.json", "meta.json"):
            continue
        try:
            if now - p.stat().st_mtime > hours * 3600:
                continue
            n += len(json.loads(p.read_text(encoding="utf-8")).get("results", []))
        except Exception:
            continue
    return n


def run_job(arm, qid, n, files, timeout, max_turns, out_dir, wait_on_limit, model="", max_per_window=0, stop=None):
    if stop is not None and stop.is_set():
        return (arm, qid, "skip 已偵測到全域 skills 事故,停止派工")
    if max_per_window and runs_in_window(out_dir) >= max_per_window:
        # 事前上限(SWE-agent per-instance / bmad per-story 的窗口版):這個五小時窗口已經跑滿,不再開新工作;
        # 之後重跑 runner 會逐題補缺。比「撞到再等」省一次撞牆,也不會把 Enzo 的互動配額吃光。
        # ★r1 併發席:這道是 TOCTOU(多 worker 平行可同時放行、超額到 workers×n)——刻意接受:它只是禮貌性軟上限,
        #   真正的帳號硬上限由 --wait-on-limit 接住,超額有界(預設 workers=2),不會做出錯的判分。★
        return (arm, qid, f"skip 窗口已達 {max_per_window} 場上限,之後再補")
    stamp = time.strftime("%H%M%S")
    out = Path(out_dir) / f"{arm}-q-{qid}-{stamp}.json"
    log = Path(out_dir) / f"{arm}-q-{qid}-{stamp}.log"
    cmd = [sys.executable, str(PROBE), "--scenarios", ",".join(str(ROOT / f) for f in files),
           "--only", qid, "--runs", str(n), "--arm", arm, "--out", str(out),
           "--timeout", str(timeout), "--max-turns", str(max_turns), "--wait-on-limit", str(wait_on_limit)]
    if model:
        cmd += ["--model", model]
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as lf:
        lf.write("$ " + " ".join(cmd) + "\n")
        lf.flush()
        r = subprocess.run(cmd, cwd=str(ROOT), stdout=lf, stderr=subprocess.STDOUT, text=True)
    bad_health = False
    try:
        d = json.loads(out.read_text(encoding="utf-8"))
        got = sum(1 for x in d.get("results", []) if is_valid(x))
        lim = sum(1 for x in d.get("results", []) if x.get("limit_hit"))
        bad_health = bool(d.get("skills_health_bad"))
    except Exception:
        got, lim = 0, 0
    if r.returncode == 3 or bad_health:
        # 探針回 3 或結果檔標了 skills 事故:設停止旗標,其餘 worker 與後續工作不再派(r1 併發席 F1)
        if stop is not None:
            stop.set()
        return (arm, qid, f"★全域 skills 事故★ rc={r.returncode}——停止派工,先在真 repo 跑 lumos install --force")
    return (arm, qid, f"rc={r.returncode} 有效 {got}/{n} 撞上限 {lim} {round(time.time() - t0)}s")


def _arm_stats(results, expected_ids, runs):
    # ★r1 正確性席:只算現在題庫裡的題★——out_dir 是跨天累積的逐題檔,題庫改過後舊題殘檔還在,
    # 不過濾會把舊題的通過/不通過靜默混進 M1-M4 與頭條差值。用 expected_ids 篩掉不在現行題庫的。
    idset = set(expected_ids)
    results = [r for r in results if r.get("id") in idset]
    valid = [r for r in results if is_valid(r)]
    n = len(valid)
    m1 = sum(1 for r in valid if r.get("passed"))
    # ★r2 正確性席:ever_lumos 為 None = 截斷資料判不出,排除在 M2 分母外(不當成 False 灌低)★
    m2_known = [r for r in valid if r.get("ever_lumos") is not None]
    m2 = sum(1 for r in m2_known if r.get("ever_lumos"))
    idxs = [r["first_lumos_idx"] for r in valid if r.get("first_lumos_idx") is not None]
    m3 = statistics.median(idxs) if idxs else None
    ans = [r for r in valid if str(r.get("id", "")).startswith("a")]
    # M4 兩把尺:gated=敲對指令且答對(passed);content=純答案內容對(不管走哪條路,只在有記 answer_content_ok 的場算)
    content = [r for r in ans if r.get("answer_content_ok") is not None]
    per = {}
    for r in valid:
        per.setdefault(r["id"], [0, 0])
        per[r["id"]][1] += 1
        per[r["id"]][0] += 1 if r.get("passed") else 0
    inconsistent = sorted(i for i, (c, t) in per.items() if 0 < c < t)
    return {"n": n, "m1_passed": m1, "m1_rate": round(m1 / n, 4) if n else None,
            "m2_ever": m2, "m2_n": len(m2_known), "m2_rate": round(m2 / len(m2_known), 4) if m2_known else None,
            "m3_first_idx_median": m3, "m3_n": len(idxs),
            "m4_gated_passed": sum(1 for r in ans if r.get("passed")), "m4_gated_n": len(ans),
            "m4_content_passed": sum(1 for r in content if r.get("answer_content_ok")), "m4_content_n": len(content),
            "inconsistent_questions": inconsistent,
            "missing": max(0, len(expected_ids) * runs - n),
            "instrument_errors": len(results) - n,
            "limit_hits": sum(1 for r in results if r.get("limit_hit")),
            "per_question": per}


def classify_question(w, wo):
    """一題對「這條規矩」有沒有鑑別力。w/wo = [過幾次, 跑幾次]。
    區分=帶著比拔掉多過至少三分之二;反向=拔掉反而多過;都過/都不過=這題測不到這條規矩;其餘=弱/不穩。
    (借 skill-creator 的 analyzer:抓「不管有沒有裝都過」的斷言——那種題留在題庫裡只是在花配額。)"""
    if not w[1] or not wo[1]:
        return "缺資料"
    rw, rwo = w[0] / w[1], wo[0] / wo[1]
    if rw == 1 and rwo == 1:
        return "不區分(都過)"
    if rw == 0 and rwo == 0:
        return "不區分(都不過)"
    if rw - rwo >= 2 / 3:
        return "區分"
    if rwo > rw:
        return "反向"
    return "弱/不穩"


def merge(out_dir, expected_ids, runs):
    by_arm = load_results(out_dir)
    arms = {a: _arm_stats(by_arm[a], expected_ids, runs) for a in ARMS}
    per_q = {q: {a: arms[a]["per_question"].get(q, [0, 0]) for a in ARMS} for q in expected_ids}
    for a in ARMS:
        arms[a].pop("per_question", None)
    w, wo = arms["with"]["m1_rate"], arms["without"]["m1_rate"]
    delta = round((w - wo) * 100, 2) if (w is not None and wo is not None) else None
    classes = {q: classify_question(v["with"], v["without"]) for q, v in per_q.items()}
    class_counts = {}
    for c in classes.values():
        class_counts[c] = class_counts.get(c, 0) + 1
    return {"runs": runs, "expected_ids": expected_ids, "arms": arms, "m1_delta_pp": delta, "per_question": per_q,
            "question_class": classes, "class_counts": class_counts}


def render_md(s, meta):
    a, b = s["arms"]["with"], s["arms"]["without"]
    def pct(x): return "—" if x is None else f"{x * 100:.1f}%"
    lines = [f"# 修法 A ablation 對照({meta.get('date')};模型 {meta.get('claude_version', '?')})", "",
             f"題 {len(s['expected_ids'])} × 每組 {s['runs']} 次;讀法見 Projects/修法A_lumos先行ablation_計劃(預註冊,這裡只列數字)。"
             f"只算有效場(撞用量上限/儀器例外不算)。", "",
             "| 尺 | with(現況) | without(拔散文) |", "|---|---|---|",
             f"| M1 通過率 | {a['m1_passed']}/{a['n']} = {pct(a['m1_rate'])} | {b['m1_passed']}/{b['n']} = {pct(b['m1_rate'])} |",
             f"| M2 敲過 lumos(分母排除截斷判不出的) | {a['m2_ever']}/{a['m2_n']} = {pct(a['m2_rate'])} | {b['m2_ever']}/{b['m2_n']} = {pct(b['m2_rate'])} |",
             f"| M3 首次步數中位(有敲的場數) | {a['m3_first_idx_median']} ({a['m3_n']}) | {b['m3_first_idx_median']} ({b['m3_n']}) |",
             f"| M4a 答案題(敲對指令+答對) | {a['m4_gated_passed']}/{a['m4_gated_n']} | {b['m4_gated_passed']}/{b['m4_gated_n']} |",
             f"| M4b 答案內容純對(不管走哪條路) | {a['m4_content_passed']}/{a['m4_content_n']} | {b['m4_content_passed']}/{b['m4_content_n']} |",
             f"| 同題多次不一致的題數 | {len(a['inconsistent_questions'])} | {len(b['inconsistent_questions'])} |",
             f"| 缺場 / 撞上限 / 其他儀器例外 | {a['missing']} / {a['limit_hits']} / {a['instrument_errors'] - a['limit_hits']} | {b['missing']} / {b['limit_hits']} / {b['instrument_errors'] - b['limit_hits']} |",
             "", f"**M1 差(with − without)= {s['m1_delta_pp']} pp**", "",
             "題目鑑別力(這題對「這條規矩」測不測得到):" + "、".join(f"{k} {v} 題" for k, v in sorted(s.get("class_counts", {}).items())), "",
             "| 題 | with | without | 鑑別力 |", "|---|---|---|---|"]
    for q, v in s["per_question"].items():
        lines.append(f"| {q} | {v['with'][0]}/{v['with'][1]} | {v['without'][0]}/{v['without'][1]} | {s.get('question_class', {}).get(q, '')} |")
    if a["inconsistent_questions"] or b["inconsistent_questions"]:
        lines += ["", f"不一致題 with: {', '.join(a['inconsistent_questions']) or '—'};without: {', '.join(b['inconsistent_questions']) or '—'}"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=",".join(DEFAULT_Q))
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--workers", type=int, default=2, help="平行路數;瓶頸是帳號用量上限不是機器,多開沒用")
    ap.add_argument("--wait-on-limit", type=int, default=7200, help="探針撞上限時最多等幾秒(每 300 秒重試)")
    ap.add_argument("--max-per-window", type=int, default=50,
                    help="五小時內最多開幾場(含撞上限的);0=不設。2026-09-02 實測每窗口約 55 場才撞牆,預設留餘裕給人用")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--max-turns", type=int, default=18)
    ap.add_argument("--model", default="")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--merge-only", action="store_true", help="不跑,只合併既有輸出")
    a = ap.parse_args()
    files = a.questions.split(",")
    ids = load_ids(files)
    date = datetime.date.today().isoformat()
    out_dir = Path(a.out_dir) if a.out_dir else ROOT / "governance" / "eval" / "ablation-lumos-first" / date
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        ver = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        ver = "?"
    meta = {"date": date, "claude_version": ver, "runs": a.runs, "workers": a.workers,
            "timeout": a.timeout, "max_turns": a.max_turns, "questions": files, "n_questions": len(ids),
            "started": datetime.datetime.now().isoformat(timespec="seconds")}
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    if not a.merge_only:
        by_arm = load_results(out_dir)
        jobs = []
        for qid in ids:                       # 逐題、兩組交錯:中途被殺兩組進度也對稱
            for arm in a.arms.split(","):
                n = needed(by_arm, arm, qid, a.runs)
                if n:
                    jobs.append((arm, qid, n))
        total = sum(n for _, _, n in jobs)
        print(f"{len(ids)} 題 × {a.runs} 次 × {len(a.arms.split(','))} 組;還缺 {total} 場有效結果,"
              f"{len(jobs)} 個工作,{a.workers} 路平行,撞上限最多等 {a.wait_on_limit}s → {out_dir}", flush=True)
        import threading
        stop = threading.Event()          # 任一工作偵測到全域 skills 事故就 set,其餘工作看到就不派(r1 併發席 F1)
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(run_job, arm, qid, n, files, a.timeout, a.max_turns, out_dir, a.wait_on_limit, a.model,
                              a.max_per_window, stop)
                    for arm, qid, n in jobs]
            for f in futs:
                arm, qid, st = f.result()
                print(f"  {arm} {qid}: {st}", flush=True)
    # ★r2 併發席:健康檢查要無條件掃一次,不能只靠本次新工作順手帶到★——
    # --merge-only 跳過整個工作迴圈,或本批 needed 全為 0(jobs 空)時,上一輪留下、已標事故的舊檔
    # 會被靜默合併出報告。這裡不管走不走 merge_only 都掃 out_dir 一次。
    poisoned = collect_skills_health(out_dir)
    s = merge(out_dir, ids, a.runs)
    s["skills_health_poisoned"] = poisoned
    if poisoned:
        print("\n" + "!" * 60)
        print(f"✗ 偵測到全域 ~/.claude/skills 事故({len(poisoned)} 個結果檔標了受污染)——本次資料不可採信。", flush=True)
        print("  先修再重跑:\n    python3 scripts/lumos install --force")
        print("  見 Issues/探針沙盒改動真全域機器狀態。summary 仍產出但已標 skills_health_poisoned。")
        print("!" * 60)
    (out_dir / "summary.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    md = render_md(s, meta)
    (out_dir / "summary.md").write_text(md, encoding="utf-8")
    print("\n" + md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
