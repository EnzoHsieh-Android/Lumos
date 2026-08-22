#!/usr/bin/env python3
"""情境探針:模擬場景,看 Claude 會不會自己敲對的 lumos 指令(Projects/指令索引與情境測試_計劃)。

不是直接呼叫指令——那沒意義。做法:
  1. git clone --local 本 repo 到臨時目錄(Bash 可以放心開,動到的只是副本)
  2. 對每個情境跑 headless `claude -p <情境> --output-format stream-json`
  3. 從事件流抓工具呼叫順序;判準 = 期望的 `lumos <指令>` 出現在任何「禁止先做」的工具/指令之前
  4. 報告每個情境:過/不過、第一個工具呼叫是什麼、全部工具序列

判準的三個刻意設計(外審 2026-08-22 提過,裁定不改):
  - Skill 調用不算「敲到指令」——要測的就是「調了 skill 之後有沒有真的敲 lumos」。
  - forbid_before 對非 Bash 工具只比對工具名(Grep/Read/Edit…),不看內容;要禁的是「那一類動作」。
  - 副本裡 Claude 自己的 hooks(impact 注入等)照常觸發——探針量的是 Claude 在真實環境(規則+hook)下的行為;
    hook 注入不是工具呼叫,不會被算成它自己敲的指令。
  - 不開放 Agent 工具:子代理內部的動作對事件流是隱形的,會造成假通過/假失敗。

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
        hay = summ if name == "Bash" else f"{name}:{summ}"   # 非 Bash 工具用「工具名:參數」比,紀律題可寫 Edit:docs/…
        for e in expect:
            if e not in exp_idx and re.search(e, hay):
                exp_idx[e] = i
    missing = [e for e in expect if e not in exp_idx]
    if missing:
        return False, f"沒敲到期望指令: {missing}", None
    first = min(exp_idx.values())
    for i, (name, summ) in enumerate(calls[:first]):
        if name in ("Read", "Grep", "Glob") and "/.claude/skills/" in summ:
            continue   # 讀索引/skill 手冊是期望行為,不算「先做了別的」
        for f in forbid_before:
            if re.search(f, name) or (name == "Bash" and re.search(f, summ)):
                return False, f"在敲 lumos 之前先做了 {name}: {summ[:80]!r}", first
    return True, "ok", first


def run_one(sc, workdir, max_turns, timeout, model):
    cmd = ["claude", "-p", sc["prompt"], "--output-format", "stream-json", "--verbose",
           "--max-turns", str(max_turns), "--no-session-persistence",
           "--permission-mode", "acceptEdits",
           "--allowedTools", "Bash", "Read", "Grep", "Glob", "Edit", "Write", "Skill",
           "--disallowedTools", "Agent"]
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
    # ⑩ 答案對不對(工具鏈補強十件):情境可帶 answer_expect=[regex…],最後回覆文字要全部命中
    final = ""
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        if isinstance(ev, dict) and ev.get("type") == "result":
            final = ev.get("result") or ""
    if ok and sc.get("answer_expect"):
        miss_a = [e for e in sc["answer_expect"] if not re.search(e, final or "", re.I)]
        if miss_a:
            ok, why = False, f"敲對了指令,但答案缺關鍵事實: {miss_a}"
    return {"id": sc["id"], "cat": sc.get("cat"), "passed": ok, "reason": why,
            "first_tool": calls[0] if calls else None, "n_calls": len(calls),
            "calls": calls[:12], "secs": round(time.time() - t0, 1), "stderr": err if not ok else "",
            "answer": (final or "")[:1500]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT),
                    help="要被探的專案根目錄(預設=本 repo)。★探別的專案必須給★——"
                         "沒給的話不論在哪個目錄執行,複製的都是 lumos-toolchain 自己,"
                         "題目再怎麼寫都是在探錯的 repo(2026-08-22 實際踩過)")
    ap.add_argument("--scenarios", default=str(ROOT / "governance" / "scenarios" / "commands.jsonl"))
    ap.add_argument("--only", default="")
    # ★預設 8 → 18(2026-08-22)★:實測既有題庫最慢 6 步(s02/s11),8 只留 2 步餘裕;
    # absence 題組天生要「查不到→換方法再查」,最慢 12 步——吃預設會在它開口之前截斷,
    # 三題全假紅。假紅的下一步永遠是有人把閘關掉,所以預設本身要夠。
    # ★為什麼不設更大★:步數上限不是「越寬越安全」。給太多步,那些其實在瞎繞的題也可能
    # 繞到答對,反而把問題蓋掉。18 = 最慢那題(12 步)加一半餘裕,不是拍腦袋。
    ap.add_argument("--max-turns", type=int, default=18)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--model", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--keep", action="store_true", help="保留臨時副本")
    ap.add_argument("--sample", type=int, default=0, help="只抽 N 題(決定性:依 --seed 輪轉,給自主迴圈每週抽查用)")
    ap.add_argument("--seed", default="", help="抽樣種子(例:週數);同種子同題")
    ap.add_argument("--history", default="", help="把本次摘要 append 到這個 jsonl(ts/passed/total/failed)")
    ap.add_argument("--ts", default="", help="寫進 history 的時間戳(排程端給)")
    ap.add_argument("--dry-list", action="store_true", help="只印抽到的題目 id,不跑(測抽樣用)")
    a = ap.parse_args()
    scs = []
    for f in a.scenarios.split(","):
        scs += [json.loads(l) for l in Path(f).read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.only:
        keep = set(a.only.split(","))
        scs = [s for s in scs if s["id"] in keep or s["id"].split("-")[0] in keep]
    if a.sample and a.sample < len(scs):
        # 決定性輪轉:同一種子永遠抽同一組;種子換(每週)就換一組,幾週下來全部輪過
        import hashlib
        h = int(hashlib.sha256(a.seed.encode("utf-8")).hexdigest(), 16)
        start = h % len(scs)
        scs = [scs[(start + i * 3) % len(scs)] for i in range(a.sample)]
        seen, uniq = set(), []
        for s_ in scs:
            if s_["id"] not in seen:
                seen.add(s_["id"]); uniq.append(s_)
        scs = uniq
    if a.dry_list:
        print(",".join(s_["id"] for s_ in scs)); return 0
    tmp = Path(tempfile.mkdtemp(prefix="lumos-probe-"))
    work = tmp / "repo"
    # 複製工作樹(含未 commit 的改動——索引/筆記常是剛寫還沒 commit),再在副本裡 commit 成乾淨狀態
    work.mkdir(parents=True)
    src = Path(a.repo).resolve()
    if not (src / ".git").exists():
        print(f"✗ --repo {src} 不是 git repo(找不到 .git),停手", file=sys.stderr)
        return 2
    subprocess.run(["rsync", "-a", "--exclude", "node_modules", "--exclude", ".venv",
                    f"{src}/", f"{work}/"], check=True)
    subprocess.run(["git", "config", "core.hooksPath", "/dev/null"], cwd=str(work))
    subprocess.run(["git", "add", "-A"], cwd=str(work))
    subprocess.run(["git", "-c", "user.name=probe", "-c", "user.email=probe@local", "commit", "-qm", "probe snapshot", "--no-verify"], cwd=str(work))
    # skills 走 ~/.claude(symlink 回本 repo),不用複製
    print(f"探的是: {src}\n臨時副本: {work}", file=sys.stderr)
    results = []
    try:
        for sc in scs:
            try:
                res = run_one(sc, work, a.max_turns, a.timeout, a.model)
            except Exception as e:   # 一題炸掉不拖累整批:記成失敗,繼續
                res = {"id": sc.get("id", "?"), "cat": sc.get("cat"), "passed": False,
                       "reason": f"儀器例外: {type(e).__name__}: {e}", "first_tool": None,
                       "n_calls": 0, "calls": [], "secs": 0, "stderr": ""}
            results.append(res)
            mark = "✓" if res["passed"] else "✗"
            ft = f"{res['first_tool'][0]}: {res['first_tool'][1][:70]}" if res["first_tool"] else "(沒有任何工具呼叫)"
            print(f"  {mark} {res['id']:22s} {res['secs']:6.1f}s  第一動作→ {ft}", flush=True)
            if not res["passed"]:
                print(f"      {res['reason']}", flush=True)
            subprocess.run(["git", "checkout", "-q", "--", "."], cwd=str(work))
            subprocess.run(["git", "clean", "-qfdx"], cwd=str(work))   # -x:連 gitignore 的產出也清,情境之間不互染
    finally:
        n = len(results); p = sum(1 for r in results if r["passed"])
        print(f"\n{p}/{n} 個情境 Claude 自己敲對了 lumos 指令")
        if a.out:
            Path(a.out).write_text(json.dumps({"results": results, "passed": p, "total": n}, ensure_ascii=False, indent=1), encoding="utf-8")
        if a.history:
            with open(a.history, "a", encoding="utf-8") as hf:
                hf.write(json.dumps({"ts": a.ts, "seed": a.seed, "passed": p, "total": n,
                                     "failed": [r["id"] for r in results if not r["passed"]]}, ensure_ascii=False) + "\n")
        if not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main())
