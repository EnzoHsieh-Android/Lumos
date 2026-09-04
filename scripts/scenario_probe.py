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


def tool_calls_from_codex_json(lines):
    """codex exec --json → [(tool_name, 摘要字串)] 依時間序(Projects/Codex完全支援_計劃 S3)。
    只認 item.completed:command_execution→("Bash", 指令全文,剝掉 /bin/zsh -lc '…' 外殼);file_change→("Edit", 路徑串);
    回 (calls, final_text)。事件形狀在 0.144.1 實看,改版要重驗。"""
    calls, final = [], ""
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        if ev.get("type") != "item.completed":
            continue
        it = ev.get("item") or {}
        t = it.get("type")
        if t == "command_execution":
            cmd = str(it.get("command", ""))
            m = re.match(r"^\S*(?:zsh|bash|sh) -lc (['\"])(.*)\1$", cmd, re.S)   # 0.144.1 實看單、雙引號外殼都有
            calls.append(("Bash", (m.group(2).replace("'\\''", "'") if m.group(1) == "'" else m.group(2).replace('\\"', '"')) if m else cmd))
        elif t == "file_change":
            calls.append(("Edit", " ".join(str(c.get("path", "")) for c in (it.get("changes") or []) if isinstance(c, dict))[:200]))
        elif t == "agent_message":
            final = str(it.get("text") or "")
    return calls, final


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
                        # ★不截斷 Bash 指令★(code-ablation-probe r1 邊界席):判「有沒有敲 lumos」的正則比對這個字串,
                        # 截到 200 字會把落在後面的 `lumos <子指令>` 漏掉,系統性低估 M1/M2/M3。存全文,只有純顯示的其他工具截。
                        summ = str(inp.get("command", ""))
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


# ── 修法 A ablation(Projects/修法A_lumos先行ablation_計劃)──────────────────────────
# 「不帶」組要拔的是 CLAUDE.md 裡「第一個工具呼叫是 lumos」那一小節(到「鐵則」之前),
# 其餘(## 標題、兩行前提、三條鐵則、白話、skill 表)原樣。邊界字串跟 scripts/templates/graph-discipline.md 同源;
# 範本改標題這裡會找不到 → make_sandbox 直接炸,寧可實驗跑不起來,不要靜默跑一個沒拔乾淨的「不帶」組。
RULE_HEAD = "### 第一個工具呼叫是 `lumos`"
RULE_END = "### 鐵則"   # 2026-09-05 範本標題去數字(Codex行為精修 F9);同源=scripts/templates/graph-discipline.md


def strip_lumos_first_rule(text):
    """回 (新文字, 有沒有砍到)。找不到兩個邊界、順序反了、或標記不只出現一次 → 原文、False。
    ★r1 邊界席:兩個標記若各出現多次,find 只取第一個、可能砍錯段且無聲。要求各恰好一次,否則安全回退★。"""
    if text.count(RULE_HEAD) != 1 or text.count(RULE_END) != 1:
        return text, False
    s = text.find(RULE_HEAD)
    e = text.find(RULE_END)
    if s < 0 or e < 0 or e <= s:
        return text, False
    return text[:s] + text[e:], True


# 2026-09-02 實跑教訓:帳號用量上限(「You've hit your session limit · resets 12:10pm」)一到,claude -p 4 秒就回、
# 零工具呼叫,探針把它記成「沒敲到期望指令」——168 場裡 115 場是這種假失敗。這類場次要標出來、不算分。
LIMIT_RE = re.compile(r"hit your (session|usage) limit|usage limit|rate limit|too many requests|overloaded", re.I)


def is_limit_hit(calls, final_text, result_event):
    """零工具呼叫 + 回覆/結果事件寫著用量或速率上限 → 這場是儀器被擋,不是被測 AI 的行為。"""
    if calls:
        return False
    if LIMIT_RE.search(final_text or ""):
        return True
    ev = result_event or {}
    return bool(ev.get("is_error")) and bool(LIMIT_RE.search(json.dumps(ev, ensure_ascii=False)))


# 「敲 lumos」=Bash 裡跑了 lumos 的某個子指令:`scripts/lumos search`、`python3 scripts/lumos show`、`lumos doctor`。
# ★2026-09-02 第一版用 \blumos\b 字界比對,把 `grep … docs/lumos-toolchain-knowledge/` 這種路徑也算成敲了 lumos,
# 拔散文那組的「敲過率」被灌到 98.8%——路徑裡的 lumos 後面接的是 -,子指令後面接的是空白+字母。★
# ★r1 code-ablation-probe 再修★:原前置字元類含引號 ' 與 ",害 rg 'lumos search'、echo "lumos doctor"
# 這種只是搜尋/印出規則文字的被算成敲了 lumos(灌 M2/M3)。移除引號、留路徑分隔 / 與指令分隔符。
LUMOS_CALL_RE = re.compile(r"(?:^|[\s;&|(`/])lumos\s+[a-z]")


def lumos_stats(calls):
    """回 (整場有沒有敲過 lumos 子指令, 第一次敲的是第幾個工具呼叫)。只認 Bash 指令字串;Skill 調用不算;路徑裡的 lumos 不算。"""
    for i, (name, summ) in enumerate(calls):
        if name == "Bash" and LUMOS_CALL_RE.search(str(summ)):   # str() 防禦:與 backfill_limit 一致(r1 邊界席)
            return True, i
    return False, None


def global_skills_health():
    """回「壞掉的」全域 skill symlink 清單 [(名字, 指向)](空=健康)。
    壞掉=懸空(目標不存在)或指進臨時沙盒(路徑含 lumos-probe-)。偵測探針把 ~/.claude/skills 重連到沙盒的事故;
    LUMOS_PROBE 擋不到的未知路徑靠這道事後抓。"""
    skills = Path.home() / ".claude" / "skills"
    bad = []
    if not skills.exists():
        return bad
    for d in sorted(skills.iterdir()):
        if not d.is_symlink():
            continue
        tgt = os.readlink(str(d))
        if not d.exists() or "lumos-probe-" in tgt:   # d.exists() 對 symlink 是「跟隨後存不存在」
            bad.append((d.name, tgt))
    return bad


def make_sandbox(src, arm="with"):
    """複製工作樹到臨時目錄,並★切斷所有能把東西推出去的路★。回副本路徑。
    arm="without":commit 前先砍 CLAUDE.md 的「第一個工具呼叫」小節(見 strip_lumos_first_rule),
    這樣情境之間的 git checkout -- . 不會把它復原。

    2026-08-23 事故:守衛題 a05 的情境是「沒有我就開工做」,被測 AI 真的改了計劃檔並 push——
    臨時副本是 rsync 來的,.git/config 裡的 remote 跟著複製,push 就直接推到真遠端,
    主幹多了一筆 author=probe@local 的「probe snapshot」(已覆蓋)。
    隔離不只是「動到的只是副本」,還要「副本推不出去」。三道:
      ① 拔掉所有 remote(沒有目標就沒得推)
      ② pre-push hook 寫死 exit 1(就算被測 AI 自己加回 remote 也擋;hooksPath 指向副本內的專用目錄)
      ③ 假身分 probe@local 維持——即使前兩道都失效,GitHub 上也認得出這不是人
    """
    tmp = Path(tempfile.mkdtemp(prefix="lumos-probe-"))
    work = tmp / "repo"
    work.mkdir(parents=True)
    subprocess.run(["rsync", "-a", "--exclude", "node_modules", "--exclude", ".venv",
                    f"{src}/", f"{work}/"], check=True)
    # ① 拔 remote
    r = subprocess.run(["git", "remote"], cwd=str(work), capture_output=True, text=True)
    for name in r.stdout.split():
        subprocess.run(["git", "remote", "remove", name], cwd=str(work))
    # ② 副本專用 hooks 目錄:pre-push 硬擋;其餘 hook 不存在=不跑(取代原本指向 /dev/null 的做法)
    hooks = tmp / "hooks"
    hooks.mkdir()
    (hooks / "pre-push").write_text("#!/bin/sh\necho '探針沙盒:禁止 push' >&2\nexit 1\n", encoding="utf-8")
    (hooks / "pre-push").chmod(0o755)
    subprocess.run(["git", "config", "core.hooksPath", str(hooks)], cwd=str(work))
    if arm == "without":
        cm = work / "CLAUDE.md"
        new, ok = strip_lumos_first_rule(cm.read_text(encoding="utf-8"))
        if not ok:
            raise RuntimeError("without 組:CLAUDE.md 找不到「第一個工具呼叫」小節的邊界,拔不乾淨,實驗無效,停手")
        cm.write_text(new, encoding="utf-8")
    # commit 成乾淨狀態(含未 commit 的改動——索引/筆記常是剛寫還沒 commit)
    subprocess.run(["git", "add", "-A"], cwd=str(work))
    subprocess.run(["git", "-c", "user.name=probe", "-c", "user.email=probe@local",
                    "commit", "-qm", "probe snapshot", "--no-verify"], cwd=str(work))
    return work


def _validate_scenario(sc):
    """題目缺必要欄位就回一句錯誤字串(否則 None)。★r1 邊界席:缺 expect 的畸形題原本會先燒一次真實
    claude -p 才在索引時炸,白花稀缺配額;改成派工前先擋。"""
    if not sc.get("id"):
        return "題目缺 id"
    if not sc.get("prompt"):
        return f"題目 {sc.get('id')} 缺 prompt"
    if not sc.get("expect"):
        return f"題目 {sc.get('id')} 缺 expect(判準),不跑"
    return None


def _codex_home_dir():
    """Codex 家目錄一律問 scripts/lumos 的 _codex_home()(單源;code-codex-refine r1 架構 #2:別再第二套算 CODEX_HOME)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    path = str(ROOT / "scripts" / "lumos")
    try:
        spec = importlib.util.spec_from_file_location("_lumos_for_probe", path, loader=SourceFileLoader("_lumos_for_probe", path))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        return mod._codex_home()
    except Exception as e:   # r2 delta #4:載不進(改到一半的語法錯)不能把整場判成儀器例外,退回同語意的預設
        print(f"  (hook_trace:載入 scripts/lumos 失敗,CODEX_HOME 退用預設:{type(e).__name__})", file=sys.stderr)
        env = os.environ.get("CODEX_HOME")
        return Path(env).expanduser() if env else Path.home() / ".codex"


# lumos 各 hook 注入 Codex 時的首行標頭(入口 hook / impact 鏡頭 / 派工鏡頭 / 收工擋停);Stop 的續做提示另帶 hook_run_id=
_LUMOS_HOOK_HEADS = ("本專案用 lumos 知識圖譜", "必看——", "LUMOS-LENS", "LUMOS-STOP")


def _codex_hook_trace(thread_id):
    """從 Codex 逐字稿數「lumos 的 hook 有沒有真的注入」與「收工擋停有沒有發生」。
    逐行當 JSON 讀(架構 #4:不拿子字串當結構),只認 lumos 自家 hook 的首行標頭:developer 訊息以 _LUMOS_HOOK_HEADS 之一開頭=注入一次;
    user 訊息帶 <hook_prompt hook_run_id=…>=Stop 續做提示一次(外家 #3:Codex 自己的 skills 清單也含 "lumos",字串出現不算)。
    hook 要不要 fire 取決於這台機器審過信任沒(Projects/Codex完全支援_計劃 誠實界線)——沒 fire 的場要看得出來,不能默默算「Codex 沒理 lumos」。"""
    if not thread_id:
        return None
    hits = sorted(_codex_home_dir().glob(f"sessions/*/*/*/rollout-*-{thread_id}.jsonl"), key=lambda q: q.stat().st_mtime)
    if not hits:
        return None
    hits = hits[-1:]   # 同 thread 多份 rollout 取最新(邊界 F3:glob 無序)
    fired = stop_seen = 0
    for line in hits[0].read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue   # 半行(Codex 還在寫)略過
        pl = ev.get("payload") if isinstance(ev, dict) else None
        if not isinstance(pl, dict) or pl.get("type") != "message":
            continue
        texts = [c.get("text", "") for c in (pl.get("content") or []) if isinstance(c, dict)]
        text = "\n".join(t for t in texts if isinstance(t, str))
        if pl.get("role") == "developer" and text.lstrip().startswith(_LUMOS_HOOK_HEADS):
            fired += 1
        if pl.get("role") == "user" and "hook_run_id=" in text and "LUMOS-STOP" in text:
            stop_seen += 1
    return {"hooks_fired": fired, "stop_block_seen": stop_seen}


def run_one_codex(sc, workdir, timeout, model, arm="with", stop_block="on", bypass_trust=False):
    """Codex 版 runner:`codex exec --json -C <沙盒> --sandbox workspace-write <prompt>`。
    預設不帶 --dangerously-bypass-hook-trust(本機審過信任 hook 就會跑;沒審過 hook 不 fire、結果 hooks_fired=0 看得出);
    --codex-bypass-hook-trust 只給隔離環境。stop_block=off 設 LUMOS_STOP_BLOCK_OFF=1 關掉 Codex 收工擋停(對照組)。
    模型由 codex 設定決定(-m 可覆寫);用量上限偵測 Codex 側沒對應訊號,limit_hit 恆 False 並在 result_subtype 標 codex。"""
    bad = _validate_scenario(sc)
    if bad:
        return {"id": sc.get("id", "?"), "cat": sc.get("cat"), "passed": False, "reason": f"儀器例外: {bad}", "first_tool": None,
                "n_calls": 0, "calls": [], "secs": 0, "stderr": "", "arm": arm, "ever_lumos": False, "first_lumos_idx": None,
                "limit_hit": False, "result_subtype": "codex", "harness": "codex"}
    # stdin 必重導向 DEVNULL:codex exec 沒有 tty 時會等 stdin(2026-08-23 外家席實測「stdin 要重導否則掛住」)
    cmd = ["codex", "exec", "--json", "--sandbox", "workspace-write", "-C", str(workdir)]
    if bypass_trust:
        cmd.append("--dangerously-bypass-hook-trust")
    if model:
        cmd += ["-m", model]
    cmd.append(sc["prompt"])
    env = dict(os.environ); env["LUMOS_PROBE"] = "1"
    if arm == "without":
        env["LUMOS_ENTRY_HOOK_OFF"] = "1"
    if stop_block == "off":
        env["LUMOS_STOP_BLOCK_OFF"] = "1"
    t0 = time.time()
    instrument_fail = None   # 超時 / 非零退出 = 儀器例外,這場不算分(code-codex-s3 r1 外家 #3:半途已印期望指令也不能判過)
    try:
        r = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env, stdin=subprocess.DEVNULL)
        out, err = r.stdout, r.stderr[-400:]
        if r.returncode != 0:
            instrument_fail = f"codex exec 退出碼 {r.returncode}"
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = "timeout"; instrument_fail = f"codex exec 超時 {timeout}s"
    calls, final = tool_calls_from_codex_json(out.splitlines())
    thread_id = None
    for ln in out.splitlines():
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("type") == "thread.started":
            thread_id = ev.get("thread_id"); break
    trace = _codex_hook_trace(thread_id)
    ok, why, first = judge(calls, sc["expect"], sc.get("forbid_before", []))
    if instrument_fail:
        ok, why = False, f"儀器例外: {instrument_fail}(這場不算分)"
    answer_content_ok = None
    if sc.get("answer_expect"):
        miss_a = [e for e in sc["answer_expect"] if not re.search(e, final or "", re.I)]
        answer_content_ok = not miss_a
        if ok and not answer_content_ok:
            ok, why = False, f"敲對了指令,但答案缺關鍵事實: {miss_a}"
    ever, first_idx = lumos_stats(calls)
    return {"id": sc["id"], "cat": sc.get("cat"), "passed": ok, "reason": why, "first_tool": calls[0] if calls else None,
            "n_calls": len(calls), "calls": calls, "secs": round(time.time() - t0, 1), "stderr": err if not ok else "",
            "answer": (final or "")[:1500], "arm": arm, "ever_lumos": ever, "first_lumos_idx": first_idx,
            "answer_content_ok": answer_content_ok, "limit_hit": False, "result_subtype": "codex", "harness": "codex",
            "stop_block": stop_block, "thread_id": thread_id, "hook_trace": trace}


def run_one(sc, workdir, max_turns, timeout, model, arm="with"):
    bad = _validate_scenario(sc)
    if bad:
        return {"id": sc.get("id", "?"), "cat": sc.get("cat"), "passed": False,
                "reason": f"儀器例外: {bad}", "first_tool": None, "n_calls": 0, "calls": [],
                "secs": 0, "stderr": "", "arm": arm, "ever_lumos": False, "first_lumos_idx": None,
                "limit_hit": False, "result_subtype": None}
    # ★逐題開放 Agent(2026-08-22)★:預設禁,因為多數題目不需要、開了只是燒錢又慢。
    # 但「要說沒有之前先派乾淨 agent 對一次」這條紀律,★不派 agent 就測不出來★——
    # 題目標 allow_agent:true 才放行,其餘照舊禁。
    allow_agent = bool(sc.get("allow_agent"))
    tools = ["Bash", "Read", "Grep", "Glob", "Edit", "Write", "Skill"]
    if allow_agent:
        tools.append("Agent")
    cmd = ["claude", "-p", sc["prompt"], "--output-format", "stream-json", "--verbose",
           "--max-turns", str(max_turns), "--no-session-persistence",
           "--permission-mode", "acceptEdits",
           "--allowedTools", *tools]
    if not allow_agent:
        cmd += ["--disallowedTools", "Agent"]
    if model:
        cmd += ["--model", model]
    env = dict(os.environ)
    env.pop("CLAUDECODE", None); env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    # ★探針沙盒事故防線(2026-09-02,見 make_sandbox 註)★:被測 session 的 HOME 是真的 ~/,
    # 一旦它跑 lumos install/update/bootstrap 就會把真的 ~/.claude/skills 重連到沙盒、沙盒清掉後全斷。
    # LUMOS_PROBE=1 讓那幾個指令在探針下直接拒絕(scripts/lumos:_refuse_if_probe)。
    env["LUMOS_PROBE"] = "1"
    if arm == "without":
        env["LUMOS_ENTRY_HOOK_OFF"] = "1"   # SessionStart 入口 hook 看到就靜默,同一句提醒不能從第二個口進來
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
    result_ev = {}
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
            result_ev = ev
    # ★r1 外家/正確性席:答案內容對不對 與 通過閘(敲對指令+答對)分開記★——
    # M4 若只看 passed,會把「答案對但先 grep」記成失敗,混淆「答案對不對」與「走對路徑沒有」。
    answer_content_ok = None
    if sc.get("answer_expect"):
        miss_a = [e for e in sc["answer_expect"] if not re.search(e, final or "", re.I)]
        answer_content_ok = not miss_a
        if ok and not answer_content_ok:
            ok, why = False, f"敲對了指令,但答案缺關鍵事實: {miss_a}"
    limit_hit = is_limit_hit(calls, final, result_ev)
    if limit_hit:
        ok, why = False, "儀器例外: 帳號用量/速率上限,claude -p 沒真的跑,這場不算分"
    ever, first_idx = lumos_stats(calls)
    return {"id": sc["id"], "cat": sc.get("cat"), "passed": ok, "reason": why,
            "first_tool": calls[0] if calls else None, "n_calls": len(calls),
            "calls": calls, "secs": round(time.time() - t0, 1), "stderr": err if not ok else "",
            "answer": (final or "")[:1500],
            "arm": arm, "ever_lumos": ever, "first_lumos_idx": first_idx,
            "answer_content_ok": answer_content_ok,
            "limit_hit": limit_hit, "result_subtype": result_ev.get("subtype"), "harness": "claude"}


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
    # ── 修法 A ablation 兩個旗標(預設值=改前行為)──
    ap.add_argument("--runs", type=int, default=1,
                    help="每題重跑幾次(預設 1)。同一題這次過下次不過是常態,不重跑就分不出規矩效果與運氣")
    ap.add_argument("--runner", choices=["claude", "codex"], default="claude",
                    help="被測的 harness:claude=claude -p(預設);codex=codex exec --json(S3;模型由 codex 設定決定,-m 可覆寫)")
    ap.add_argument("--stop-block", choices=["on", "off"], default="on",
                    help="codex runner:off=設 LUMOS_STOP_BLOCK_OFF=1 關掉收工擋停(對照組;Projects/Codex行為精修_計劃)")
    ap.add_argument("--codex-bypass-hook-trust", action="store_true",
                    help="codex runner 帶 --dangerously-bypass-hook-trust(★只准隔離環境★;本機審過信任不需要)")
    ap.add_argument("--arm", choices=["with", "without"], default="with",
                    help="with=現況;without=沙盒 CLAUDE.md 砍「第一個工具呼叫」小節+入口 hook 靜默(見 Projects/修法A_lumos先行ablation_計劃)")
    ap.add_argument("--wait-on-limit", type=int, default=0,
                    help="撞到帳號用量上限時最多等幾秒(每 300 秒重試同一場;預設 0=不等,照記成儀器例外)。"
                         "2026-09-02 實跑:4 路平行約 35 分鐘就撞上限,之後 115 場全是 4 秒假失敗")
    a = ap.parse_args()
    if a.runs < 1:
        print("✗ --runs 至少 1", file=sys.stderr); return 2
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
    src = Path(a.repo).resolve()
    if not (src / ".git").exists():
        print(f"✗ --repo {src} 不是 git repo(找不到 .git),停手", file=sys.stderr)
        return 2
    work = make_sandbox(src, a.arm)
    # skills 走 ~/.claude(symlink 回本 repo),不用複製
    print(f"探的是: {src}\n臨時副本: {work}" + (f"\n組別: {a.arm}  每題 {a.runs} 次" if (a.arm != "with" or a.runs > 1) else ""),
          file=sys.stderr)
    results = []
    waited = 0
    try:
        for sc in scs:
            for k in range(1, a.runs + 1):
                while True:
                    try:
                        res = (run_one_codex(sc, work, a.timeout, a.model, a.arm, a.stop_block, a.codex_bypass_hook_trust) if a.runner == "codex"
                               else run_one(sc, work, a.max_turns, a.timeout, a.model, a.arm))
                    except Exception as e:   # 一題炸掉不拖累整批:記成失敗,繼續
                        res = {"id": sc.get("id", "?"), "cat": sc.get("cat"), "passed": False,
                               "reason": f"儀器例外: {type(e).__name__}: {e}", "first_tool": None,
                               "n_calls": 0, "calls": [], "secs": 0, "stderr": "",
                               "arm": a.arm, "ever_lumos": False, "first_lumos_idx": None,
                               "limit_hit": False, "result_subtype": None}
                    if res.get("limit_hit") and waited < a.wait_on_limit:
                        print(f"  ⏸ {sc['id']} 撞到帳號用量上限,等 300 秒再試同一場(已等 {waited}s / 上限 {a.wait_on_limit}s)", flush=True)
                        time.sleep(300); waited += 300
                        continue
                    break
                res["run"] = k
                results.append(res)
                mark = "✓" if res["passed"] else "✗"
                ft = f"{res['first_tool'][0]}: {res['first_tool'][1][:70]}" if res["first_tool"] else "(沒有任何工具呼叫)"
                tag = f" #{k}" if a.runs > 1 else ""
                print(f"  {mark} {res['id']:22s}{tag} {res['secs']:6.1f}s  第一動作→ {ft}", flush=True)
                if not res["passed"]:
                    print(f"      {res['reason']}", flush=True)
                subprocess.run(["git", "checkout", "-q", "--", "."], cwd=str(work))
                subprocess.run(["git", "clean", "-qfdx"], cwd=str(work))   # -x:連 gitignore 的產出也清,情境之間不互染
    finally:
        bad = global_skills_health()
        if bad:
            print("\n" + "!" * 60, file=sys.stderr)
            print(f"✗ 事故:全域 ~/.claude/skills 有 {len(bad)} 個連結被動到(懸空或指進沙盒):", file=sys.stderr)
            for name, tgt in bad:
                print(f"    {name} → {tgt}", file=sys.stderr)
            print("  修:在真 repo 跑一次\n    python3 scripts/lumos install --force\n"
                  "  這代表某條路徑繞過了 LUMOS_PROBE 防線,見 Issues/探針沙盒改動真全域機器狀態", file=sys.stderr)
            print("!" * 60, file=sys.stderr)
        n = len(results); p = sum(1 for r in results if r["passed"])
        lim = sum(1 for r in results if r.get("limit_hit"))
        print(f"\n{p}/{n} 個情境 Claude 自己敲對了 lumos 指令" + (f"(組別 {a.arm})" if a.arm != "with" else "")
              + (f";其中 {lim} 場撞帳號用量上限沒真的跑,不算分" if lim else ""))
        if a.runs > 1:
            per = {}
            for r in results:
                per.setdefault(r["id"], [0, 0]); per[r["id"]][1] += 1; per[r["id"]][0] += 1 if r["passed"] else 0
            print("每題通過次數: " + "  ".join(f"{i} {c}/{t}" for i, (c, t) in per.items()))
        if a.out:
            # ★r1 併發席:健康檢查結果要進 JSON,不能只印 stderr——跑批只讀這個檔,
            # 印在 log 沒人看,平行時一場事故會靜默污染整批★。skills_health 非空 = 這批之後受污染。
            Path(a.out).write_text(json.dumps({"results": results, "passed": p, "total": n,
                                               "arm": a.arm, "runs": a.runs,
                                               "skills_health_bad": bad}, ensure_ascii=False, indent=1), encoding="utf-8")
        if a.history:
            with open(a.history, "a", encoding="utf-8") as hf:
                hf.write(json.dumps({"ts": a.ts, "seed": a.seed, "passed": p, "total": n,
                                     "failed": [r["id"] for r in results if not r["passed"]],
                                     **({"arm": a.arm, "runs": a.runs} if (a.arm != "with" or a.runs > 1) else {})},
                                    ensure_ascii=False) + "\n")
        if not a.keep:
            # r3 s2 實測抓到:原寫 rmtree(tmp) 但 tmp 是 make_sandbox 的區域變數,這裡 NameError、
            # 被 finally 吞掉——每週漏一個沙盒目錄,/tmp 已積 40 個。work=<tmp>/repo,清父目錄。
            shutil.rmtree(work.parent, ignore_errors=True)
    if bad:
        return 3   # ★全域 skills 事故:與「有題沒過(1)」分開,跑批看到 3 立刻停整批(r1 併發席)
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main())
