#!/usr/bin/env python3
"""情境探針:模擬場景,看 Claude 會不會自己敲對的 lumos 指令(Projects/指令索引與情境測試_計劃)。

不是直接呼叫指令——那沒意義。做法:
  1. git clone --local 本 repo 到臨時目錄(Bash 可以放心開,動到的只是副本)
  2. 對每個情境跑 headless `claude -p <情境> --output-format stream-json`
  3. 從事件流抓工具呼叫順序;判準 = 期望的 `lumos <指令>` 出現在任何「禁止先做」的工具/指令之前
  4. 報告每個情境:過/不過、第一個工具呼叫是什麼、全部工具序列

用法:
  scripts/scenario_probe.py [--scenarios governance/scenarios/commands.jsonl] [--only s01,s02]
                            [--max-turns 6] [--timeout 240] [--model ...] [--out 報告.json]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tool_calls_from_stream(lines):
    """stream-json → [(tool_name, 摘要字串)] 依時間序。"""
    calls = []
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        msg = ev.get("message") if isinstance(ev, dict) else None
        content = (msg or {}).get("content") if isinstance(msg, dict) else None
        if ev.get("type") == "assistant" and isinstance(content, list):
            for blk in content:
                if isinstance(blk, dict) and blk.get("type") == "tool_use":
                    name = blk.get("name", "?")
                    inp = blk.get("input") or {}
                    if name == "Bash":
                        summ = str(inp.get("command", ""))[:200]
                    elif name in ("Read", "Edit", "Write", "Glob", "Grep"):
                        summ = " ".join(str(inp.get(k, "")) for k in ("file_path", "pattern", "path") if inp.get(k))[:200]
                    elif name == "Skill":
                        summ = str(inp.get("skill", ""))
                    else:
                        summ = json.dumps(inp, ensure_ascii=False)[:200]
                    calls.append((name, summ))
    return calls


def judge(calls, expect, forbid_before):
    """回 (passed, reason, first_hit_index)。
    expect:每條 regex 必須各自命中至少一次(對 Bash 指令字串比對)。
    forbid_before:任何一條命中(工具名或 Bash 指令字串)若發生在「第一條 expect 命中」之前 → 不過。"""
    exp_idx = {}
    for i, (name, summ) in enumerate(calls):
        hay = summ if name == "Bash" else ""
        for e in expect:
            if e not in exp_idx and re.search(e, hay):
                exp_idx[e] = i
    missing = [e for e in expect if e not in exp_idx]
    if missing:
        return False, f"沒敲到期望指令: {missing}", None
    first = min(exp_idx.values())
    for i, (name, summ) in enumerate(calls[:first]):
        for f in forbid_before:
            if re.search(f, name) or (name == "Bash" and re.search(f, summ)):
                return False, f"在敲 lumos 之前先做了 {name}: {summ[:80]!r}", first
    return True, "ok", first


def run_one(sc, workdir, max_turns, timeout, model):
    cmd = ["claude", "-p", sc["prompt"], "--output-format", "stream-json", "--verbose",
           "--max-turns", str(max_turns), "--no-session-persistence",
           "--permission-mode", "acceptEdits",
           "--allowedTools", "Bash", "Read", "Grep", "Glob", "Edit", "Write", "Skill", "Agent"]
    if model:
        cmd += ["--model", model]
    env = dict(os.environ)
    env.pop("CLAUDECODE", None); env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env)
        out = r.stdout
        err = r.stderr[-400:]
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = "timeout"
    calls = tool_calls_from_stream(out.splitlines())
    ok, why, first = judge(calls, sc["expect"], sc.get("forbid_before", []))
    return {"id": sc["id"], "cat": sc.get("cat"), "passed": ok, "reason": why,
            "first_tool": calls[0] if calls else None, "n_calls": len(calls),
            "calls": calls[:12], "secs": round(time.time() - t0, 1), "stderr": err if not ok else ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default=str(ROOT / "governance" / "scenarios" / "commands.jsonl"))
    ap.add_argument("--only", default="")
    ap.add_argument("--max-turns", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--model", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--keep", action="store_true", help="保留臨時副本")
    a = ap.parse_args()
    scs = [json.loads(l) for l in Path(a.scenarios).read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.only:
        keep = set(a.only.split(","))
        scs = [s for s in scs if s["id"] in keep or s["id"].split("-")[0] in keep]
    tmp = Path(tempfile.mkdtemp(prefix="lumos-probe-"))
    work = tmp / "repo"
    # 複製工作樹(含未 commit 的改動——索引/筆記常是剛寫還沒 commit),再在副本裡 commit 成乾淨狀態
    work.mkdir(parents=True)
    subprocess.run(["rsync", "-a", "--exclude", "node_modules", "--exclude", ".venv",
                    f"{ROOT}/", f"{work}/"], check=True)
    subprocess.run(["git", "config", "core.hooksPath", "/dev/null"], cwd=str(work))
    subprocess.run(["git", "add", "-A"], cwd=str(work))
    subprocess.run(["git", "-c", "user.name=probe", "-c", "user.email=probe@local", "commit", "-qm", "probe snapshot", "--no-verify"], cwd=str(work))
    # skills 走 ~/.claude(symlink 回本 repo),不用複製
    print(f"臨時副本: {work}", file=sys.stderr)
    results = []
    for sc in scs:
        res = run_one(sc, work, a.max_turns, a.timeout, a.model)
        results.append(res)
        mark = "✓" if res["passed"] else "✗"
        ft = f"{res['first_tool'][0]}: {res['first_tool'][1][:70]}" if res["first_tool"] else "(沒有任何工具呼叫)"
        print(f"  {mark} {res['id']:22s} {res['secs']:6.1f}s  第一動作→ {ft}", flush=True)
        if not res["passed"]:
            print(f"      {res['reason']}", flush=True)
        subprocess.run(["git", "checkout", "-q", "--", "."], cwd=str(work))
        subprocess.run(["git", "clean", "-qfd"], cwd=str(work))
    n = len(results); p = sum(1 for r in results if r["passed"])
    print(f"\n{p}/{n} 個情境 Claude 自己敲對了 lumos 指令")
    if a.out:
        Path(a.out).write_text(json.dumps({"results": results, "passed": p, "total": n}, ensure_ascii=False, indent=1), encoding="utf-8")
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main())
