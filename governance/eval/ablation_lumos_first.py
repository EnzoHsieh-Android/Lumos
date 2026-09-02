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


def load_ids(files):
    ids = []
    for f in files:
        for ln in (ROOT / f).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                ids.append(json.loads(ln)["id"])
    return ids


# 與 scripts/scenario_probe.py 的 LIMIT_RE 同一句;只用來補標第一版(還沒有 limit_hit 欄)留下的結果檔
_LIMIT_TEXT = r"hit your (session|usage) limit|usage limit|rate limit|too many requests|overloaded"


# 與 scripts/scenario_probe.py 的 LUMOS_CALL_RE 同一句(路徑裡的 lumos-toolchain 不算敲 lumos)
_LUMOS_CALL = r"(?:^|[\s;&|(`'\"/])lumos\s+[a-z]"


def backfill_limit(r):
    """舊結果檔沒有 limit_hit 欄:零工具呼叫 + 回覆是上限訊息 → 補標 True。有欄的原樣。
    順手用修正後的規則從 calls 重算 ever_lumos / first_lumos_idx(第一版把路徑裡的 lumos 也算進去,灌水)。
    ★第一版只存前 12 個呼叫,超過的場次重算可能漏後段的 lumos 呼叫(偏低)★——n_calls > len(calls) 時記 calls_truncated。"""
    import re
    if "limit_hit" not in r:
        r["limit_hit"] = (r.get("n_calls", 0) == 0) and bool(re.search(_LIMIT_TEXT, r.get("answer") or "", re.I))
    calls = r.get("calls") or []
    ever, idx = False, None
    for i, c in enumerate(calls):
        if isinstance(c, (list, tuple)) and len(c) == 2 and c[0] == "Bash" and re.search(_LUMOS_CALL, str(c[1])):
            ever, idx = True, i
            break
    r["ever_lumos"], r["first_lumos_idx"] = ever, idx
    r["calls_truncated"] = r.get("n_calls", 0) > len(calls)
    return r


def is_valid(r):
    """一場算不算數:撞用量上限或儀器例外都不算(不是被測 AI 的行為)。"""
    return not r.get("limit_hit") and not str(r.get("reason", "")).startswith("儀器例外")


def load_results(out_dir):
    """讀目錄裡所有探針輸出(第一版 shard 檔與第二版逐題檔都吃),回 {arm: [result…]}。"""
    by_arm = {a: [] for a in ARMS}
    for p in sorted(Path(out_dir).glob("*.json")):
        if p.name in ("summary.json", "meta.json"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        arm = d.get("arm") or p.name.split("-")[0]
        if arm in by_arm and isinstance(d.get("results"), list):
            by_arm[arm].extend(backfill_limit(r) for r in d["results"])
    return by_arm


def needed(by_arm, arm, qid, runs):
    """這題這組還缺幾場有效結果。"""
    have = sum(1 for r in by_arm.get(arm, []) if r.get("id") == qid and is_valid(r))
    return max(0, runs - have)


def run_job(arm, qid, n, files, timeout, max_turns, out_dir, wait_on_limit, model=""):
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
    try:
        d = json.loads(out.read_text(encoding="utf-8"))
        got = sum(1 for x in d.get("results", []) if is_valid(x))
        lim = sum(1 for x in d.get("results", []) if x.get("limit_hit"))
    except Exception:
        got, lim = 0, 0
    return (arm, qid, f"rc={r.returncode} 有效 {got}/{n} 撞上限 {lim} {round(time.time() - t0)}s")


def _arm_stats(results, expected_ids, runs):
    valid = [r for r in results if is_valid(r)]
    n = len(valid)
    m1 = sum(1 for r in valid if r.get("passed"))
    m2 = sum(1 for r in valid if r.get("ever_lumos"))
    idxs = [r["first_lumos_idx"] for r in valid if r.get("first_lumos_idx") is not None]
    m3 = statistics.median(idxs) if idxs else None
    ans = [r for r in valid if str(r.get("id", "")).startswith("a")]
    per = {}
    for r in valid:
        per.setdefault(r["id"], [0, 0])
        per[r["id"]][1] += 1
        per[r["id"]][0] += 1 if r.get("passed") else 0
    inconsistent = sorted(i for i, (c, t) in per.items() if 0 < c < t)
    return {"n": n, "m1_passed": m1, "m1_rate": round(m1 / n, 4) if n else None,
            "m2_ever": m2, "m2_rate": round(m2 / n, 4) if n else None,
            "m3_first_idx_median": m3, "m3_n": len(idxs),
            "m4_answers_passed": sum(1 for r in ans if r.get("passed")), "m4_answers_n": len(ans),
            "inconsistent_questions": inconsistent,
            "missing": max(0, len(expected_ids) * runs - n),
            "instrument_errors": len(results) - n,
            "limit_hits": sum(1 for r in results if r.get("limit_hit")),
            "per_question": per}


def merge(out_dir, expected_ids, runs):
    by_arm = load_results(out_dir)
    arms = {a: _arm_stats(by_arm[a], expected_ids, runs) for a in ARMS}
    per_q = {q: {a: arms[a]["per_question"].get(q, [0, 0]) for a in ARMS} for q in expected_ids}
    for a in ARMS:
        arms[a].pop("per_question", None)
    w, wo = arms["with"]["m1_rate"], arms["without"]["m1_rate"]
    delta = round((w - wo) * 100, 2) if (w is not None and wo is not None) else None
    return {"runs": runs, "expected_ids": expected_ids, "arms": arms, "m1_delta_pp": delta, "per_question": per_q}


def render_md(s, meta):
    a, b = s["arms"]["with"], s["arms"]["without"]
    def pct(x): return "—" if x is None else f"{x * 100:.1f}%"
    lines = [f"# 修法 A ablation 對照({meta.get('date')};模型 {meta.get('claude_version', '?')})", "",
             f"題 {len(s['expected_ids'])} × 每組 {s['runs']} 次;讀法見 Projects/修法A_lumos先行ablation_計劃(預註冊,這裡只列數字)。"
             f"只算有效場(撞用量上限/儀器例外不算)。", "",
             "| 尺 | with(現況) | without(拔散文) |", "|---|---|---|",
             f"| M1 通過率 | {a['m1_passed']}/{a['n']} = {pct(a['m1_rate'])} | {b['m1_passed']}/{b['n']} = {pct(b['m1_rate'])} |",
             f"| M2 敲過 lumos | {a['m2_ever']}/{a['n']} = {pct(a['m2_rate'])} | {b['m2_ever']}/{b['n']} = {pct(b['m2_rate'])} |",
             f"| M3 首次步數中位(有敲的場數) | {a['m3_first_idx_median']} ({a['m3_n']}) | {b['m3_first_idx_median']} ({b['m3_n']}) |",
             f"| M4 答案題正確 | {a['m4_answers_passed']}/{a['m4_answers_n']} | {b['m4_answers_passed']}/{b['m4_answers_n']} |",
             f"| 同題多次不一致的題數 | {len(a['inconsistent_questions'])} | {len(b['inconsistent_questions'])} |",
             f"| 缺場 / 撞上限 / 其他儀器例外 | {a['missing']} / {a['limit_hits']} / {a['instrument_errors'] - a['limit_hits']} | {b['missing']} / {b['limit_hits']} / {b['instrument_errors'] - b['limit_hits']} |",
             "", f"**M1 差(with − without)= {s['m1_delta_pp']} pp**", "",
             "| 題 | with | without |", "|---|---|---|"]
    for q, v in s["per_question"].items():
        lines.append(f"| {q} | {v['with'][0]}/{v['with'][1]} | {v['without'][0]}/{v['without'][1]} |")
    if a["inconsistent_questions"] or b["inconsistent_questions"]:
        lines += ["", f"不一致題 with: {', '.join(a['inconsistent_questions']) or '—'};without: {', '.join(b['inconsistent_questions']) or '—'}"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=",".join(DEFAULT_Q))
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--workers", type=int, default=2, help="平行路數;瓶頸是帳號用量上限不是機器,多開沒用")
    ap.add_argument("--wait-on-limit", type=int, default=7200, help="探針撞上限時最多等幾秒(每 300 秒重試)")
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
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(run_job, arm, qid, n, files, a.timeout, a.max_turns, out_dir, a.wait_on_limit, a.model)
                    for arm, qid, n in jobs]
            for f in futs:
                arm, qid, st = f.result()
                print(f"  {arm} {qid}: {st}", flush=True)
    s = merge(out_dir, ids, a.runs)
    (out_dir / "summary.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    md = render_md(s, meta)
    (out_dir / "summary.md").write_text(md, encoding="utf-8")
    print("\n" + md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
