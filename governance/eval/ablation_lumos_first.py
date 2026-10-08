#!/usr/bin/env python3
"""修法 A ablation runner(Projects/修法A_lumos先行ablation_計劃):
「CLAUDE.md 那段『第一個工具呼叫是 lumos』+入口 hook 同句」帶/不帶,各跑同一組情境題,比四個尺。

做法(2026-09-02 第二版):工作單位=(組別, 題),每題需要幾場就叫探針跑幾場(`--only <題> --runs <缺幾場>`),
輸出一檔一次嘗試、永不覆蓋;重跑時先數每題已有的**有效**場次(排除撞用量上限/儀器例外),只補缺的。
第一版按 shard 切、4 路平行,35 分鐘撞到帳號用量上限,之後 115 場全是 4 秒假失敗。
現在只准單路派工，探針帶 --wait-on-limit 撞到就等重置再補同一場；並行需先驗證在途取消。

四個尺(讀法預註冊在計劃筆記,這裡只算數不解讀):
  M1 通過率(期望指令在禁做動作之前)  M2 整場有沒有敲過 lumos
  M3 首次敲 lumos 的步數中位(只算有敲的場)  M4 答案題(id 以 a 開頭)正確率

用法:
  governance/eval/ablation_lumos_first.py [--runs 3] [--workers 1] [--wait-on-limit 7200] [--out-dir …] [--merge-only]
"""
import argparse, datetime, errno, fcntl, hashlib, json, os, stat, statistics, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "scripts" / "scenario_probe.py"
DEFAULT_Q = ["governance/scenarios/commands.jsonl", "governance/scenarios/answers.jsonl"]
ARMS = ["with", "without"]


def _atomic_write_bytes(path, data):
    """同目錄暫存後取代目標；不跟隨既有目標符號連結。"""
    mode = None
    try:
        old = path.lstat()
        if stat.S_ISREG(old.st_mode):
            mode = stat.S_IMODE(old.st_mode) & 0o666
    except FileNotFoundError:
        pass
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".",
                                         delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(data)
            if mode is not None:
                os.fchmod(tmp.fileno(), mode)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def _atomic_write_text(path, content):
    _atomic_write_bytes(path, content.encode("utf-8"))


# ★r1 合約席:判準單一實作來源★——LIMIT_RE / LUMOS_CALL_RE 從探針 import,不在這裡重抄一份字面。
# 同目錄 retrieval_eval_multiword 早有此教訓(「計分一律 import,兩份實作立刻漂移」)。改判準只改探針一處。
sys.path.insert(0, str(ROOT / "scripts"))
from scenario_probe import LIMIT_RE, LUMOS_CALL_RE  # noqa: E402  ★單一實作來源★


def load_ids(files):
    """回題目 id 清單；重複 id 會讓精確選題命中多題，故在派工前拒絕。"""
    ids, seen = [], set()
    for f in files:
        for ln in (ROOT / f).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                qid = json.loads(ln)["id"]
                if (not isinstance(qid, str) or not qid.strip() or "," in qid
                        or not qid.isprintable()):
                    raise ValueError(f"題號不可為空白、含逗號或不可列印字元：{qid!r}")
                if qid in seen:
                    raise ValueError(f"題號重複，精確選題會命中多題：{qid!r}")
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


def invalid_batch_evidence(d, filename_arm=None):
    """新舊探針輸出的整批失效訊號；普通低有效場數的 inconclusive 不等於事故。"""
    for key in ("fatal", "inconclusive"):
        if key in d and type(d[key]) is not bool:
            return [f"{key} 型別錯誤，健康狀態不可判"]
    if "skills_health_bad" in d and not isinstance(d["skills_health_bad"], list):
        return ["skills 健康欄位型別錯誤，健康狀態不可判"]
    bad = d.get("skills_health_bad")
    if bad:
        return bad if isinstance(bad, list) else ["skills 健康欄位異常"]
    rows = d.get("results")
    if not isinstance(rows, list):
        return ["結果檔缺少逐場資料，健康狀態不可判"]
    arm = d.get("arm") or filename_arm
    if arm is not None and arm not in ARMS:
        return ["結果檔組別無效，健康狀態不可判"]
    if filename_arm in ARMS and d.get("arm") is not None and d["arm"] != filename_arm:
        return ["結果檔名與組別不一致，健康狀態不可判"]
    for row in rows:
        # 逐列跳過錯型元素會讓同檔成功外觀列抵缺場，整批拒收。
        if not isinstance(row, dict):
            return ["逐場資料不是物件，健康狀態不可判"]
        if not isinstance(row.get("id"), str) or not row["id"]:
            return ["逐場資料缺少有效題號，健康狀態不可判"]
        if type(row.get("passed")) is not bool:
            return ["逐場通過欄位型別錯誤，健康狀態不可判"]
        calls = row.get("calls")
        n_calls = row.get("n_calls", 0)
        if (type(n_calls) is not int or n_calls < 0 or (calls is not None and not isinstance(calls, list))
                or ("reason" in row and not isinstance(row["reason"], str))
                or ("fatal" in row and type(row["fatal"]) is not bool)
                or (row.get("answer") is not None and not isinstance(row["answer"], str))
                or ("limit_hit" in row and type(row["limit_hit"]) is not bool)
                or (row.get("answer_content_ok") is not None and type(row["answer_content_ok"]) is not bool)):
            return ["逐場計分欄位型別錯誤，健康狀態不可判"]
        if calls is not None and any(not isinstance(call, (list, tuple)) or len(call) != 2
                                     or not all(isinstance(part, str) for part in call) for call in calls):
            return ["逐場工具呼叫內容型別錯誤，健康狀態不可判"]
        retries = row.get("retry_attempts", [])
        if not isinstance(retries, list) or any(not isinstance(r, dict) for r in retries):
            return ["逐場重試紀錄型別錯誤，窗口用量不可判"]
        if arm is not None and row.get("arm") is not None and row["arm"] != arm:
            return ["逐場組別與結果檔不一致，健康狀態不可判"]
    if d.get("fatal") or any(isinstance(r, dict) and r.get("fatal") for r in rows):
        return ["探針整批 fatal；健康或清理結果不可判"]
    return []


def _result_json_files(out_dir):
    """只讀本工具兩組逐題或舊 shard 的正式結果，不把旁邊的 JSON 備註當探針。"""
    return sorted(p for p in Path(out_dir).glob("*.json")
                  if p.name.startswith(("with-", "without-")))


def load_results(out_dir):
    """讀目錄裡所有探針輸出(第一版 shard 檔與第二版逐題檔都吃),回 {arm: [result…]}。
    壞檔不拖垮整批；非物件頂層或逐場元素都拒收該檔。
    整批 fatal 的檔案即使逐場 reason=ok 也不可計分或抵掉缺場。"""
    by_arm = {a: [] for a in ARMS}
    unfinished = {p.stem for p in Path(out_dir).glob("*.pending")}
    for p in _result_json_files(out_dir):
        if p.stem in unfinished:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        if invalid_batch_evidence(d, p.name.split("-")[0]):
            continue
        arm = d.get("arm") or p.name.split("-")[0]
        rows = d.get("results")
        if arm in by_arm and isinstance(rows, list):
            by_arm[arm].extend(backfill_limit(r) for r in rows if isinstance(r, dict))
    return by_arm


def collect_skills_health(out_dir):
    """掃探針輸出的整批失效訊號，回 [(檔名, [失效原因…])]。
    健康檢查拋錯時壞連結欄是空；舊檔也可能只在逐場列上標 fatal。"""
    hits = []
    for p in sorted([*_result_json_files(out_dir), *Path(out_dir).glob("*.pending"),
                     *Path(out_dir).glob("*.candidate")]):
        if p.suffix == ".candidate":
            hits.append((p.name, ["探針候選結果尚未由父程序驗證，整批不可採信"]))
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            hits.append((p.name, ["結果檔無法讀取，健康狀態不可判"]))
            continue
        if not isinstance(d, dict):
            hits.append((p.name, ["結果檔格式錯誤，健康狀態不可判"]))
            continue
        evidence = invalid_batch_evidence(d, p.name.split("-")[0])
        if evidence:
            hits.append((p.name, evidence))
    return hits


def needed(by_arm, arm, qid, runs):
    """這題這組還缺幾場有效結果。"""
    have = sum(1 for r in by_arm.get(arm, []) if r.get("id") == qid and is_valid(r))
    return max(0, runs - have)


def runs_in_window(out_dir, hours=5.0, now=None):
    """最近 hours 小時內落地的探針場次(含撞上限的):算帳號窗口用掉多少。以檔案 mtime 為時間,沿用結果檔沒有時間戳的現況。"""
    now = time.time() if now is None else now
    n = 0
    for p in _result_json_files(out_dir):
        try:
            if now - p.stat().st_mtime > hours * 3600:
                continue
            rows = json.loads(p.read_text(encoding="utf-8")).get("results", [])
            n += sum(1 + len(r.get("retry_attempts", [])) for r in rows if isinstance(r, dict))
        except Exception:
            continue
    return n


def run_job(arm, qid, n, files, timeout, max_turns, out_dir, wait_on_limit, model="", max_per_window=0, stop=None):
    if stop is not None and stop.is_set():
        return (arm, qid, "skip 已偵測到全域 skills 事故,停止派工")
    if max_per_window:
        remaining = max_per_window - runs_in_window(out_dir)
        if remaining <= 0:
            return (arm, qid, f"skip 窗口已達 {max_per_window} 場上限,之後再補")
        n = min(n, remaining)
    stamp = f"{time.strftime('%H%M%S')}-{time.time_ns()}"
    qid_key = hashlib.sha256(qid.encode("utf-8")).hexdigest()[:16]
    out = Path(out_dir) / f"{arm}-q-{qid_key}-{stamp}.json"
    candidate = out.with_suffix(".candidate")
    log = Path(out_dir) / f"{arm}-q-{qid_key}-{stamp}.log"
    pending = Path(out_dir) / f"{arm}-q-{qid_key}-{stamp}.pending"
    cmd = [sys.executable, str(PROBE), "--scenarios", ",".join(str(ROOT / f) for f in files),
           f"--exact-id={qid}", "--runs", str(n), "--arm", arm, "--out", str(candidate),
           "--timeout", str(timeout), "--max-turns", str(max_turns), "--wait-on-limit", str(wait_on_limit)]
    if max_per_window:
        cmd += ["--max-attempts", str(remaining)]
    if model:
        cmd += ["--model", model]
    # 先留下保守事故標記；父程序被殺時，子程序可能還在跑，不能讓下批吃進其結果。
    marker = {"arm": arm, "qid": qid, "results": [], "fatal": True,
              "inconclusive": True, "skills_health_bad": [], "failure_type": "unfinished",
              "log_path": str(log), "candidate_path": str(candidate),
              "recovery_paths": [str(out), str(candidate), str(pending)],
              "retry_policy": "confirm-no-live-probe-then-archive-recovery-paths-and-rerun"}
    _atomic_write_text(pending, json.dumps(marker, ensure_ascii=False))
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as lf:
        lf.write("$ " + " ".join(cmd) + "\n")
        lf.flush()
        try:
            r = subprocess.run(cmd, cwd=str(ROOT), stdout=lf, stderr=subprocess.STDOUT, text=True)
        except (OSError, subprocess.TimeoutExpired) as exc:
            lf.write(f"探針子程序例外 {type(exc).__name__}: {exc}\n")
            lf.flush()
            try:
                prior_result = candidate.read_bytes()
            except OSError as read_exc:
                prior_result = None
                if not isinstance(read_exc, FileNotFoundError):
                    lf.write(f"舊結果無法讀取 {type(read_exc).__name__}: {read_exc}\n")
                    lf.flush()
            tombstone = {**marker, "failure_type": type(exc).__name__}
            # 先以單次原子取代釘住事故，再歸檔舊資料；歸檔中斷不能讓下次重跑吃回成功外觀。
            _atomic_write_text(out, json.dumps(tombstone, ensure_ascii=False))
            if prior_result is not None:
                try:
                    _atomic_write_bytes(out.with_suffix(".failed"), prior_result)
                    candidate.unlink(missing_ok=True)
                except OSError as archive_exc:
                    lf.write(f"舊結果歸檔失敗 {type(archive_exc).__name__}: {archive_exc}\n")
                    lf.flush()
            if stop is not None:
                stop.set()
            return (arm, qid, f"★探針批次失效★ {type(exc).__name__}——停止派工，檢查 {log}")
    bad_health = False
    unreadable = False
    try:
        d = json.loads(candidate.read_text(encoding="utf-8"))
        if not isinstance(d, dict):
            raise ValueError("invalid probe output")
        rows = d["results"]
        if (not isinstance(rows, list) or not all(isinstance(x, dict) for x in rows)
                or invalid_batch_evidence(d, arm) or d.get("arm") != arm
                or any(x.get("id") != qid for x in rows) or len(rows) != n
                or type(d.get("fatal")) is not bool or type(d.get("inconclusive")) is not bool
                or not isinstance(d.get("skills_health_bad"), list)):
            raise ValueError("invalid probe output")
        got = sum(1 for x in rows if is_valid(x))
        lim = sum(1 for x in rows if x.get("limit_hit"))
        bad_health = bool(invalid_batch_evidence(d))
    except Exception:
        got, lim = 0, 0
        unreadable = True
    if r.returncode not in (0, 1) or bad_health or unreadable:
        # 探針退出異常、結果檔不可讀或整批失效都設停止旗標，後續不再派工。
        tombstone = {**marker, "failure_type": f"returncode-{r.returncode}" if r.returncode not in (0, 1)
                     else "invalid-output"}
        _atomic_write_text(out, json.dumps(tombstone, ensure_ascii=False))
        if stop is not None:
            stop.set()
        return (arm, qid, f"★探針批次失效★ rc={r.returncode}——停止派工，檢查結果檔與探針日誌")
    os.replace(candidate, out)
    pending.unlink()
    return (arm, qid, f"rc={r.returncode} 有效 {got}/{n} 撞上限 {lim} {round(time.time() - t0)}s")


def _arm_stats(results, expected_ids, runs):
    # ★r1 正確性席:只算現在題庫裡的題★——out_dir 是跨天累積的逐題檔,題庫改過後舊題殘檔還在,
    # 不過濾會把舊題的通過/不通過靜默混進 M1-M4 與頭條差值。用 expected_ids 篩掉不在現行題庫的。
    idset = set(expected_ids)
    results = [r for r in results if r.get("id") in idset]
    # 以既有檔案排序決定每題前 runs 個有效場；超額列仍保留於原始結果但不增加權重。
    valid, accepted_per_id, surplus = [], {}, 0
    for row in results:
        if not is_valid(row):
            continue
        qid = row["id"]
        if accepted_per_id.get(qid, 0) >= runs:
            surplus += 1
            continue
        accepted_per_id[qid] = accepted_per_id.get(qid, 0) + 1
        valid.append(row)
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
            "missing": sum(max(0, runs - per.get(q, [0, 0])[1]) for q in expected_ids),
            "excluded_surplus": surplus,
            "instrument_errors": sum(not is_valid(r) for r in results),
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
    lines = [f"# 修法 A ablation 對照(記錄日期 {meta.get('date')};當次 Claude CLI {meta.get('claude_version', '?')})", "",
             f"題 {len(s['expected_ids'])} × 每組 {s['runs']} 次;讀法見 Projects/修法A_lumos先行ablation_計劃(預註冊,這裡只列數字)。"
             f"只算有效場(撞用量上限/儀器例外不算)。", "",
             "歷史結果可能跨日或跨模型版本；此處 CLI 版本不代表每場模型版本。", "",
             "| 尺 | with(現況) | without(拔散文) |", "|---|---|---|",
             f"| M1 通過率 | {a['m1_passed']}/{a['n']} = {pct(a['m1_rate'])} | {b['m1_passed']}/{b['n']} = {pct(b['m1_rate'])} |",
             f"| M2 敲過 lumos(分母排除截斷判不出的) | {a['m2_ever']}/{a['m2_n']} = {pct(a['m2_rate'])} | {b['m2_ever']}/{b['m2_n']} = {pct(b['m2_rate'])} |",
             f"| M3 首次步數中位(有敲的場數) | {a['m3_first_idx_median']} ({a['m3_n']}) | {b['m3_first_idx_median']} ({b['m3_n']}) |",
             f"| M4a 答案題(敲對指令+答對) | {a['m4_gated_passed']}/{a['m4_gated_n']} | {b['m4_gated_passed']}/{b['m4_gated_n']} |",
             f"| M4b 答案內容純對(不管走哪條路) | {a['m4_content_passed']}/{a['m4_content_n']} | {b['m4_content_passed']}/{b['m4_content_n']} |",
             f"| 同題多次不一致的題數 | {len(a['inconsistent_questions'])} | {len(b['inconsistent_questions'])} |",
             f"| 缺場 / 撞上限 / 其他儀器例外 | {a['missing']} / {a['limit_hits']} / {a['instrument_errors'] - a['limit_hits']} | {b['missing']} / {b['limit_hits']} / {b['instrument_errors'] - b['limit_hits']} |",
             f"| 超額有效場（保留原始資料、不計分） | {a.get('excluded_surplus', 0)} | {b.get('excluded_surplus', 0)} |",
             "", f"**M1 差(with − without)= {s['m1_delta_pp']} pp**", "",
             "題目鑑別力(這題對「這條規矩」測不測得到):" + "、".join(f"{k} {v} 題" for k, v in sorted(s.get("class_counts", {}).items())), "",
             "| 題 | with | without | 鑑別力 |", "|---|---|---|---|"]
    if s.get("skills_health_poisoned"):
        bad = ", ".join(name for name, _ in s["skills_health_poisoned"])
        lines[2:2] = [f"**整批不可採信：探針失效；請先處置 {bad}。**", ""]
    for q, v in s["per_question"].items():
        qmd = q.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f"| {qmd} | {v['with'][0]}/{v['with'][1]} | {v['without'][0]}/{v['without'][1]} | {s.get('question_class', {}).get(q, '')} |")
    if a["inconsistent_questions"] or b["inconsistent_questions"]:
        lines += ["", f"不一致題 with: {', '.join(a['inconsistent_questions']) or '—'};without: {', '.join(b['inconsistent_questions']) or '—'}"]
    return "\n".join(lines) + "\n"


def _run_locked_batch(a, files, ids, date, out_dir):
    if a.merge_only:
        meta_path = out_dir / "meta.json"
        try:
            if not stat.S_ISREG(meta_path.lstat().st_mode):
                raise ValueError("unsafe meta")
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict):
                raise ValueError("invalid meta")
            meta_changed = False
            if not isinstance(meta.get("date"), str) or not meta["date"].strip():
                meta["date"] = "來源日期未知"
                meta_changed = True
            if not isinstance(meta.get("claude_version"), str) or not meta["claude_version"].strip():
                meta["claude_version"] = "來源版本未知"
                meta_changed = True
            if meta_changed:
                _atomic_write_text(meta_path, json.dumps(meta, ensure_ascii=False, indent=1))
        except (OSError, ValueError):
            meta = {"date": "來源日期未知", "claude_version": "來源版本未知"}
            _atomic_write_text(meta_path, json.dumps(meta, ensure_ascii=False, indent=1))
    else:
        try:
            ver = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception:
            ver = "?"
        meta = {"date": date, "claude_version": ver, "runs": a.runs, "workers": a.workers,
                "timeout": a.timeout, "max_turns": a.max_turns, "questions": files, "n_questions": len(ids),
                "started": datetime.datetime.now().isoformat(timespec="seconds")}
        _atomic_write_text(out_dir / "meta.json", json.dumps(meta, ensure_ascii=False, indent=1))
    # 舊事故檔或上次被殺留下的半檔必須在派工前攔下；事後掃描仍檢查本輪新產物。
    poisoned = collect_skills_health(out_dir)
    live_failed = False
    if not a.merge_only and not poisoned:
        by_arm = load_results(out_dir)
        jobs = []
        for qid in ids:                       # 逐題、兩組交錯:中途被殺兩組進度也對稱
            for arm in a.arms.split(","):
                n = needed(by_arm, arm, qid, a.runs)
                if n:
                    jobs.append((arm, qid, n))
        total = sum(n for _, _, n in jobs)
        print(f"{len(ids)} 題 × {a.runs} 次 × {len(a.arms.split(','))} 組;還缺 {total} 場有效結果,"
              f"{len(jobs)} 個工作,單路派工,撞上限最多等 {a.wait_on_limit}s → {out_dir}", flush=True)
        import threading
        stop = threading.Event()
        for arm, qid, n in jobs:
            if stop.is_set():
                break
            _, _, st = run_job(arm, qid, n, files, a.timeout, a.max_turns, out_dir, a.wait_on_limit,
                               a.model, a.max_per_window, stop)
            print(f"  {arm} {qid}: {st}", flush=True)
        live_failed = stop.is_set()
    # ★r2 併發席:健康檢查要無條件掃一次,不能只靠本次新工作順手帶到★——
    # --merge-only 跳過整個工作迴圈,或本批 needed 全為 0(jobs 空)時,上一輪留下、已標事故的舊檔
    # 會被靜默合併出報告。這裡不管走不走 merge_only 都掃 out_dir 一次。
    poisoned = collect_skills_health(out_dir)
    if live_failed and not poisoned:
        poisoned = [("本次派工", ["探針程序失效且沒有可採信的結果檔"])]
    s = merge(out_dir, ids, a.runs)
    s["skills_health_poisoned"] = poisoned
    if poisoned:
        print("\n" + "!" * 60)
        print(f"✗ 偵測到 {len(poisoned)} 個探針失效結果檔——本次資料不可採信。", flush=True)
        print("  檢查結果檔與探針日誌；若 skills 連結損壞，在真 repo 執行 python3 scripts/lumos install --force。")
        print("  summary 仍產出，但失效檔不參與統計，並已標 skills_health_poisoned。")
        print("!" * 60)
    _atomic_write_text(out_dir / "summary.json", json.dumps(s, ensure_ascii=False, indent=1))
    md = render_md(s, meta)
    _atomic_write_text(out_dir / "summary.md", md)
    print("\n" + md)
    return 3 if poisoned else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=",".join(DEFAULT_Q))
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--workers", type=int, default=1,
                    help="live 探針只准 1 路；恢復並行前須驗證事故時可取消在途模型")
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
    if not a.merge_only and a.workers != 1:
        ap.error("live 探針目前只准 --workers 1；--merge-only 保留舊參數相容")
    arms = a.arms.split(",")
    if not arms or len(arms) != len(set(arms)) or any(arm not in ARMS for arm in arms):
        ap.error("--arms 只能指定不重複的 with,without")
    files = a.questions.split(",")
    ids = load_ids(files)
    date = datetime.date.today().isoformat()
    out_dir = (Path(a.out_dir) if a.out_dir else ROOT / "governance" / "eval" / "ablation-lumos-first" / date).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    # 同一輸出目錄的另一個 CLI 可能已在跑模型；其 stop 旗標不會跨進程共享。
    lock_fd = os.open(out_dir, os.O_RDONLY | os.O_DIRECTORY)
    legacy_fd = None
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # 過渡期舊版只鎖這支檔；同時取得可擋仍在跑的舊批次。
            legacy_fd = os.open(out_dir / ".ablation.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            fcntl.flock(legacy_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.ELOOP):
                raise
            print(f"✗ 探針批次鎖不可用或另一批次正在使用 {out_dir}；本次未改寫結果或摘要。", file=sys.stderr)
            return 3
        return _run_locked_batch(a, files, ids, date, out_dir)
    finally:
        if legacy_fd is not None:
            os.close(legacy_fd)
        os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
