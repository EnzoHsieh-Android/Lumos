"""改制回測 [S4] 週跑模組(2026-08-26)——autonomous-loop.sh 每週呼叫一次。

做什麼:①補漏凍結:帳上已收斂且帶 spec_path、但 governance/replay/ 還沒有 verdict 的
loop 自動 --freeze;沒有 spec_path 的(舊帳)列名單喊人不硬猜。②回放:新凍結(從未回放過)
必跑+存量輪替抽 5 包(游標檔記「這一圈抽過誰」,輪完清空重來——無狀態隨機抽會有包
長年抽不到,r2 delta d-f4/r3 d-f3)。③總預算 300 秒,超時截斷,訊息講跑了幾包略過幾包。
④差異分四類(邏輯漂移/帳被動/凍結檔被動佚失/golden 過期),前三類=紅喊人,過期=指路重凍。

fail-open:本模組任何失敗都不該擋 autonomous-loop 主流程(呼叫端 || true)。
狀態檔 .rotation-cursor 是週跑自身狀態(比照 run_nags 週戳記的「job 狀態檔」擺法),非帳。
"""
import json
import subprocess
import time
from pathlib import Path

BUDGET_SECONDS = 300
SAMPLE_PER_WEEK = 5
RED_MARKERS = ("邏輯漂移", "帳被動", "凍結檔被動", "佚失")
STALE_MARKER = "golden 過期"


def _read_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _converged_loops_with_specpath(repo):
    """治理帳 converged 的 loop → 帳本裡該 loop 的 spec_path(最後一筆有者勝;無=None)。"""
    conv = []
    seen = set()
    gov = Path(repo) / "docs" / ".governance-log.jsonl"
    for line in _read_lines(gov):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        # cb3 折入(finder-f1+s4-f1):治理帳 schema=kind+nodes(原讀 phase/loop=永遠選不中,
        # 補凍上線即死,自家測試還捏同一套錯 schema 陪葬);行可為合法 JSON 非物件(null)→isinstance 擋。
        if not isinstance(d, dict):
            continue
        _nodes = d.get("nodes") or []
        if d.get("kind") == "converged" and _nodes and _nodes[0] not in seen:
            seen.add(_nodes[0])
            conv.append(_nodes[0])
    spec_of = {}
    for line in _read_lines(Path(repo) / "docs" / ".canary-log.jsonl"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("loop") in seen and d.get("spec_path"):
            spec_of[d["loop"]] = d["spec_path"]
    return [(lid, spec_of.get(lid)) for lid in conv]


def _read_lines(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def run_weekly(repo, lumos="scripts/lumos"):
    """回傳 dict:{frozen:[], unfreezable:[], replayed:[], skipped:[], red:[], stale:[], errors:[]}。"""
    repo = Path(repo)
    rdir = repo / "governance" / "replay"
    rdir.mkdir(parents=True, exist_ok=True)
    out = {"frozen": [], "unfreezable": [], "replayed": [], "skipped": [],
           "red": [], "stale": [], "errors": []}
    t0 = time.time()

    def _left():
        return BUDGET_SECONDS - (time.time() - t0)

    def _run(args, timeout):
        return subprocess.run(["python3", str(repo / lumos), *args],
                              capture_output=True, text=True, timeout=timeout,
                              cwd=str(repo))

    # ── ① 補漏凍結 ──
    have = {p.parent.name for p in rdir.glob("*/verdict.json")}
    for lid, spec_path in _converged_loops_with_specpath(repo):
        if lid in have:
            continue
        if not spec_path:
            out["unfreezable"].append(lid)
            continue
        if _left() < 30:
            out["skipped"].append(f"freeze:{lid}")
            continue
        try:
            r = _run(["loop", "replay", lid, "--freeze", "--spec", spec_path,
                      "--repo", str(repo)], timeout=max(30, _left()))
            (out["frozen"] if r.returncode == 0 else out["errors"]).append(
                lid if r.returncode == 0 else f"freeze:{lid}:rc{r.returncode}")
        except subprocess.TimeoutExpired:
            out["errors"].append(f"freeze:{lid}:timeout")

    # ── ② 名單:新凍結必跑+存量輪替抽樣 ──
    allv = sorted(p.parent.name for p in rdir.glob("*/verdict.json"))
    cur_p = rdir / ".rotation-cursor"
    cur = _read_json(cur_p, {"cycle_started": "", "done": [], "seen": []})
    new = [l for l in allv if l not in set(cur.get("seen", []))]
    pool = [l for l in allv if l not in set(new) and l not in set(cur.get("done", []))]
    sample = pool[:SAMPLE_PER_WEEK]

    # ── ③ 回放(預算內);跑完基本盤後按實測耗時判「升級全量」——
    # spec 機械條件:單包耗時×存量 ≤60 秒就全跑(2026-08-26 首跑實測 0.24s/包,17 包 4.1s)。
    def _replay_one(lid):
        if _left() < 15:
            out["skipped"].append(lid)
            return 0.0
        t1 = time.time()
        try:
            r = _run(["loop", "replay", lid, "--golden",
                      f"governance/replay/{lid}/verdict.json", "--repo", str(repo)],
                     timeout=max(15, _left()))
        except subprocess.TimeoutExpired:
            out["errors"].append(f"replay:{lid}:timeout")
            return time.time() - t1
        text = r.stdout + r.stderr
        out["replayed"].append(lid)
        if any(m in text for m in RED_MARKERS) and r.returncode != 0:
            out["red"].append(lid)
        elif STALE_MARKER in text:
            out["stale"].append(lid)
        elif r.returncode != 0:
            out["errors"].append(f"replay:{lid}:rc{r.returncode}")
        return time.time() - t1
    spent = 0.0
    base = new + sample
    for lid in base:
        spent += _replay_one(lid)
    rest = [l for l in allv if l not in set(base)]
    if base and out["replayed"] and rest:
        avg = spent / max(1, len(out["replayed"]))
        if avg * len(allv) <= 60 and _left() > avg * len(rest) + 15:
            for lid in rest:
                _replay_one(lid)
            sample = sample + rest   # 全跑視同整圈抽完(游標推進涵蓋)

    # ── ④ 游標推進(輪完一圈清空重來) ──
    # cb3 ext-f3/s4-f3:seen 只記「真的回放過的」新包——預算見底被 skip 的新包保留必跑資格。
    cur["seen"] = sorted(set(cur.get("seen", [])) | {l for l in new if l in set(out["replayed"])} | set(sample))
    cur["done"] = sorted(set(cur.get("done", [])) | set(s for s in sample if s in out["replayed"]))
    if set(cur["done"]) >= set(allv):
        cur = {"cycle_started": "", "done": [], "seen": cur["seen"]}
    try:
        import os as _os
        _tmp = cur_p.with_suffix(".tmp")
        _tmp.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
        _os.replace(_tmp, cur_p)   # cb3 s4-f4:比照 backlog.py 暫存+原子換檔,半寫殘檔不歸零進度
    except OSError:
        out["errors"].append("cursor:write-fail")
    return out


def build_msg(out):
    """組 LINE 白話訊息;None=無事不發。紅=喊人;過期=指路重凍;unfreezable=舊帳名單提醒。"""
    parts = []
    if out["red"]:
        parts.append("🔴 回放紅燈(邏輯漂移/帳被動/凍結檔被動)——這幾個要人看:" + ",".join(out["red"])
                     + ";逐個重查:lumos loop replay <id> --golden governance/replay/<id>/verdict.json")
    if out["stale"]:
        parts.append("golden 過期(制度已演進非漂移):" + ",".join(out["stale"])
                     + ";確認後重凍:lumos loop replay <id> --freeze --spec <計劃> --note <理由>")
    if out["errors"]:
        parts.append("回放執行錯誤:" + ",".join(out["errors"][:5]))
    if out["unfreezable"]:
        parts.append(f"舊帳無 spec_path 凍不了 {len(out['unfreezable'])} 個(不硬猜):" + ",".join(out["unfreezable"][:5]))
    if not parts:
        return None
    head = f"[改制回測週跑] 跑了 {len(out['replayed'])} 包/略過 {len(out['skipped'])} 包/新凍 {len(out['frozen'])} 包"
    # cb3 s4-f2:bash 逐行抽 MSG: 前綴——多行只剩第一行,紅燈清單整段蒸發只發太平句。單行分號串接。
    return head + ";" + ";".join(parts)


def build_log_lines(out):
    """給 wrapper 逐行 log 的白話摘要(2026-09-05 第二輪審視 d4;架構 r1 A:文字在 python 端組、shell 只抽 LOG: 前綴——
    原本 shell 端 cut -c1-160 剛好切掉 red/stale,翻案了也看不見)。第一行永遠有計數;紅燈另起一行點名。"""
    lines = [f"跑了 {len(out.get('replayed', []))} 包;翻案(紅) {len(out.get('red', []))};過期(制度演進) {len(out.get('stale', []))};錯誤 {len(out.get('errors', []))}"]
    if out.get("red"):
        lines.append("🔴 回放紅燈要人看:" + ",".join(out["red"][:5]) + "(逐個 lumos loop replay <id> --golden governance/replay/<id>/verdict.json)")
    return lines


if __name__ == "__main__":
    import sys
    r = run_weekly(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(json.dumps(r, ensure_ascii=False))
    for _l in build_log_lines(r):
        print("LOG:" + _l)
    m = build_msg(r)
    if m:
        print("MSG:" + m)
