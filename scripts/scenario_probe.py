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
import argparse, ast, errno, json, os, re, secrets, shutil, stat, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _euid():
    """目前的有效使用者;單獨一個函式,測試才能只換掉這一處,不必改整個程序的 os 模組
    (代碼審 r6 架構席要求測試縫要窄;本專案別處直接呼叫 os.geteuid,這裡是刻意的例外)。"""
    return os.geteuid()


_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_NOCTTY = getattr(os, "O_NOCTTY", 0)


def _open_char_device(path):
    """開一個字元裝置來寫:不阻塞地開(檢查後被換成沒人讀的 FIFO 也不會卡住)、不跟隨連結、不把終端收成控制終端
    (lumos 的終端確認早就為同一件事加 O_NOCTTY);開到的若已不是字元裝置就關掉報錯;最後改回阻塞,
    終端讀得慢時才不會寫一半就 BlockingIOError。開跑前檢查與實際寫入共用這一個,兩邊判斷才不會分岔。"""
    fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK | _NOFOLLOW | _NOCTTY)
    try:
        if not stat.S_ISCHR(os.fstat(fd).st_mode):
            raise OSError(errno.EINVAL, "輸出位置在檢查後被換掉,已不是字元裝置", str(path))
        os.set_blocking(fd, True)
    except BaseException:
        os.close(fd)
        raise
    return fd


def _open_history(path):
    """開歷史檔來追加:只收「只有一個名字的普通檔」與字元裝置。不跟隨連結、不阻塞(換成沒人讀的 FIFO 也不卡住)、
    不收控制終端;開到的若是 FIFO、socket,或是有多個名字的普通檔(硬連結,可能連到別人的檔),關掉報錯。"""
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NONBLOCK | _NOFOLLOW | _NOCTTY, 0o666)
    try:
        st = os.fstat(fd)
        if stat.S_ISCHR(st.st_mode):
            os.set_blocking(fd, True)
        elif not (stat.S_ISREG(st.st_mode) and st.st_nlink == 1):
            raise OSError(errno.EINVAL, "歷史檔位置不是只有一個名字的一般檔案(可能在檢查後被換掉)", str(path))
    except BaseException:
        os.close(fd)
        raise
    return fd


def _output_target_problem(path, replace=True):
    """跑模型之前先看輸出位置寫不寫得出去;回問題描述或 None。replace=False 是追加用的歷史檔。
    規則跟 _atomic_write_bytes 與 _open_history 一一對應:取代模式下,字元裝置直接寫(這裡實際試開一次,
    開不起來就停)、其他非目錄的東西(連結、FIFO、socket)會被換成普通檔;追加模式只收只有一個名字的普通檔與
    字元裝置,其餘都會寫到別處或卡住。要新建(或取代)時父目錄必須可寫。"""
    path = Path(path)
    try:
        st = path.lstat()
    except FileNotFoundError:
        st = None
    except OSError as exc:                      # 檔名超過上限、父路徑是普通檔……
        return f"{path} 不能用({exc.strerror})"
    if st is not None:
        if stat.S_ISDIR(st.st_mode):
            return f"{path} 是目錄"
        if stat.S_ISCHR(st.st_mode):
            try:
                os.close(_open_char_device(path))
            except OSError as exc:              # 沒有控制終端時的 /dev/tty、沒寫入權的裝置……
                return f"{path} 開不起來({exc.strerror})"
            return None
        if stat.S_ISREG(st.st_mode):
            if not os.access(path, os.W_OK):
                return f"{path} 不可寫"
            if not replace:
                if st.st_nlink != 1:
                    return f"{path} 有多個名字(硬連結),追加會寫進別的名字指向的內容"
                return None
        elif not replace:
            return f"{path} 不是一般檔案(符號連結、FIFO 或 socket),追加會寫到別處或卡住"
    if not path.parent.is_dir():
        return f"{path.parent} 不存在或不是目錄"
    if not os.access(path.parent, os.W_OK | os.X_OK):
        return f"{path.parent} 不可寫,沒辦法" + ("在同目錄放暫存檔" if replace else "建立歷史檔")
    return None


def _atomic_write_text(path, content):
    _atomic_write_bytes(path, content.encode("utf-8"))


def _atomic_write_bytes(path, data):
    """以同目錄暫存檔原子取代目標,不跟隨既有目標的符號連結(消融腳本也 import 這一份,不另抄)。
    暫存檔跟 lumos 的 _write_lf 一樣用 O_EXCL 建立、讓 umask 自己生效——★不把整個程序的 umask 設成 0 再設回來★,
    那一瞬間別的執行緒建的檔會拿到錯的權限。
    既有普通檔只有「自己擁有、而且只有這一個名字」時才沿用它的權限位元(先前審查要求保留使用者刻意設的
    0640 這類權限);別人擁有的、或有多個名字(硬連結,可能是別人連到我某個寬權限檔)的,一律照新建檔。
    要沿用時暫存檔一建立就用那個權限(再被 umask 收窄也只會更嚴)、寫入前補回原值,內容不會先落在比原檔寬的暫存檔裡。
    既有目標是字元裝置(例如 /dev/null)時照舊直接寫入(見 _open_char_device);FIFO、socket 這類照修前一樣換成普通檔
    (直接開沒人讀的 FIFO 會永遠卡住)。既有普通檔不可寫時照舊報 PermissionError,不默默換掉。"""
    path = Path(path)
    try:
        old = path.lstat()
    except FileNotFoundError:
        old = None
    if old is not None and stat.S_ISCHR(old.st_mode):
        with os.fdopen(_open_char_device(path), "wb") as fh:
            fh.write(data)
        return
    if old is not None and stat.S_ISREG(old.st_mode) and not os.access(path, os.W_OK):
        raise PermissionError(errno.EACCES, "輸出檔不可寫", str(path))
    keep_mode = (stat.S_IMODE(old.st_mode) & 0o666
                 if old is not None and stat.S_ISREG(old.st_mode)
                 and old.st_uid == _euid() and old.st_nlink == 1 else None)
    for _ in range(100):                        # 隨機名撞名機率極低;設上限防異常狀況空轉(lumos 主程式另一處 O_EXCL 迴圈也設了上限)
        # 暫存檔名固定短,不帶目標檔名:目標檔名接近 255 bytes 上限時才不會超長
        tmp_path = path.with_name(f".probe-out-{os.getpid()}-{secrets.token_hex(4)}.tmp")
        try:
            fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW,
                         0o666 if keep_mode is None else keep_mode)
            break
        except FileExistsError:
            continue
    else:
        raise FileExistsError(errno.EEXIST, "連續 100 次都撞到既有的暫存檔名", str(path.parent))
    try:
        with os.fdopen(fd, "wb") as tmp:
            if keep_mode is not None:
                os.fchmod(tmp.fileno(), keep_mode)
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


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


# 判準版本(寫進歷史與結果檔):判準換過,前後的通過率不可直接比(Projects/探針判準對齊程式碼為主_計劃)。
# 2026-09-29 起:紀律第一步是先讀程式碼,題庫拿掉讀碼類禁令;撞回合上限/逾時=截斷、不算分。
GRADER_VERSION = "2026-10-03-source-results"
SANDBOX_VERSION = "2026-10-04-frozen-copy-config-reset"


def source_evidence(lines, harness, token):
    """只信成功工具的回傳；缺串流前提為 unknown，完整但沒讀到為 absent。"""
    if not token:
        return "unknown"
    pending, unknown, complete = set(), False, False
    eligible = {}
    for line in lines:
        try:
            ev = json.loads(line)
        except (ValueError, TypeError):
            if str(line).lstrip().startswith("{"):
                unknown = True
            continue
        if not isinstance(ev, dict):
            unknown = True
            continue
        if harness == "codex":
            if ev.get("type") == "turn.completed":
                complete = True
            item = ev.get("item")
            if not isinstance(item, dict) or item.get("type") != "command_execution":
                continue
            ident = item.get("id")
            if ev.get("type") in ("item.started", "item.updated"):
                if isinstance(ident, str) and ident:
                    pending.add(ident)
                else:
                    unknown = True
                continue
            if ev.get("type") != "item.completed":
                continue
            if isinstance(ident, str):
                pending.discard(ident)
            code, status = item.get("exit_code"), item.get("status")
            if type(code) is not int or status not in ("completed", "failed"):
                unknown = True
            elif code == 0 and status == "completed":
                output = item.get("aggregated_output")
                if not isinstance(output, str):
                    unknown = True
                elif token in output:
                    return "present"
            continue
        if ev.get("type") == "result":
            complete = ev.get("subtype") == "success"
        msg = ev.get("message")
        blocks = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, dict):
                unknown = True
                continue
            if ev.get("type") == "assistant" and block.get("type") == "tool_use":
                ident = block.get("id")
                if not isinstance(ident, str) or not ident or ident in eligible:
                    unknown = True
                    continue
                eligible[ident] = block.get("name") in ("Read", "Grep", "Bash")
                if eligible[ident]:
                    pending.add(ident)
            elif ev.get("type") == "user" and block.get("type") == "tool_result":
                ident = block.get("tool_use_id")
                if not isinstance(ident, str) or not ident or ident not in eligible:
                    unknown = True
                    continue
                if not eligible[ident]:
                    continue
                if ident not in pending:
                    unknown = True
                    continue
                pending.remove(ident)
                error = block.get("is_error", False)
                if type(error) is not bool:
                    unknown = True
                    continue
                if error:
                    continue
                output = block.get("content")
                if isinstance(output, list):
                    if all(isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str) for b in output):
                        output = "\n".join(b["text"] for b in output)
                    else:
                        output = None
                if not isinstance(output, str):
                    unknown = True
                elif token in output:
                    return "present"
    return "unknown" if unknown or pending or not complete else "absent"


def grade(sc, calls, final_text, source_state=None):
    """回 (passed, reason, answer_content_ok)。兩個執行器共用:先判工具序列,再看答案內容(有 answer_expect 才看)。
    儀器層的覆寫(用量上限/截斷/退出碼)由呼叫端在這之後做。"""
    if sc.get("source_probe"):
        # 讀碼題不再依命令regex猜檔案；其他題仍走原本的順序判準。
        ok = source_state == "present"
        why = "ok" if ok else ("未取得目標程式片段" if source_state == "absent" else "儀器例外: 缺少可判讀的原始讀碼結果")
    else:
        ok, why, _ = judge(calls, sc["expect"], sc.get("forbid_before", []))
    answer_content_ok = None
    if sc.get("answer_expect"):
        miss_a = [e for e in sc["answer_expect"] if not re.search(e, final_text or "", re.I)]
        answer_content_ok = not miss_a
        if ok and not answer_content_ok:
            ok, why = False, f"敲對了指令,但答案缺關鍵事實: {miss_a}"
    return ok, why, answer_content_ok


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
# 2026-09-21 範本改定位(程式碼為主、圖譜補脈絡):要拔的那一節從「第一個工具呼叫是 lumos」改名為「怎麼用」,
# 收在「寫筆記時」之前——寫法規範那節講的是怎麼記筆記、不是叫 AI 去查,拔它會超出本 ablation 的範圍。
RULE_HEAD = "### 怎麼用"
RULE_END = "### 寫筆記時"   # 同源=scripts/templates/graph-discipline.md(2026-09-05 去數字、2026-09-21 改定位)


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


# ★題目會跟著程式碼腐爛★(2026-09-21,Issues/探針以工作樹為來源會改到本體 同一天):
# 紀律題組六題有兩題叫 AI 去改一段 2026-09-11 就被移除的東西。AI 查了波及、讀了碼、
# 發現前提不成立就停下來問——這是正確行為,卻因為「沒照題目改完再寫回」被判不及格。
# 腐爛的題目不會報錯,只會安靜地量出「規矩失效」的假訊號,差一點就照它去改紀律。
# 兩層檢查,跑之前先驗:①題目裡提到的路徑要存在 ②`target` 宣告的字串要在那個檔裡找得到。
#
# ★比對前先剝掉整行註解★(審查席 blocker):本 repo 移除東西時的慣例是留一句提到舊名字的
# 註解說明它被拿掉了(pre-push 裡的 sync_nudge 就是),純字串比對會把那句註解當成「還健在」,
# 而那正好是原始事故的形狀——防線對最自然的寫法失效。只剝「整行都是註解」的行,
# 行尾註解不碰(剝了會誤傷字串字面值);Markdown 走 <!-- --> 區塊。
# ★誠實界線★:這只擋得住「整行註解」這一種殘留。名字被留在字串字面值、docstring 或
# 檔名裡的情形仍會判成健在,機械判不出來——真要確定,還是得人看一次。
_SCEN_LINE_COMMENT_RE = re.compile(r"^\s*(#|//|--|;)")
_SCEN_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
# 路徑候選:至少一層目錄。判準是「每一段都要含字母」——
# 版本對照 `0.144.1/0.153.2`(本 repo 筆記真的這樣寫,審查席 major)每段都是數字,擋掉;
# 沒有副檔名的 `scripts/hooks/pre-push` 與圖譜節點 `Systems/graph-sync-coverage` 都收得到,
# 不必為「有沒有副檔名」各寫一條規則。網址另外擋,不然 example.com/x 會被當成缺檔。
_SCEN_PATH_RE = re.compile(r"(?<![\w.-])((?:[\w.-]+/)+[\w.-]+)")
_SCEN_HAS_LETTER_RE = re.compile(r"[A-Za-z]")


def _scen_paths(prompt):
    """從題目文字抽出「看起來像檔案路徑或圖譜節點」的候選,保持出現順序、去重。"""
    out = []
    for m in _SCEN_PATH_RE.finditer(prompt):
        rel = m.group(1)
        if prompt[max(0, m.start() - 3):m.start()].endswith("//"):
            continue                      # 網址的一部分,不是 repo 裡的路徑
        if any(not _SCEN_HAS_LETTER_RE.search(seg) for seg in rel.split("/")):
            continue                      # 有一段沒字母 → 版本號之類,不是路徑
        if rel not in out:
            out.append(rel)
    return out


def _scen_resolve(repo, rel):
    """候選對應到實際檔案:先當一般路徑,再當圖譜節點(<vault>/<節點>.md)。找不到回 None。"""
    p = repo / rel
    if p.exists():
        return p
    if not rel.endswith(".md"):
        for vault in sorted(repo.glob("docs/*-knowledge")):
            cand = vault / (rel + ".md")
            if cand.exists():
                return cand
    return None


def _scen_visible_text(path):
    """把整行註解剝掉之後的內容——只有這裡出現的字串才算「東西還在」。"""
    txt = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".md", ".markdown", ".html", ".svg", ".xml"):
        txt = _SCEN_HTML_COMMENT_RE.sub("", txt)
        return txt
    return "\n".join(ln for ln in txt.split("\n") if not _SCEN_LINE_COMMENT_RE.match(ln))


def _check_one_target(sid, item, repo):
    """驗一條 target 宣告,回傳問題說明清單(空=沒問題)。"""
    if not isinstance(item, (list, tuple)) or not item or not str(item[0]).strip():
        return [f"{sid}:target 格式要寫成 [[路徑]] 或 [[路徑, 要找的字串], …]"]
    rel = str(item[0])
    needle = str(item[1]) if len(item) > 1 else None
    if needle == "":
        return [f"{sid}:target 的比對字串是空的,那等於沒驗內容——"
                f"只驗存在就寫成 [\"{rel}\"],不要留空字串"]
    f = repo / rel
    if f.is_dir():
        return [f"{sid}:target 指的 {rel} 是目錄,不是檔案——target 要指到單一檔案"]
    if not f.is_file():
        return [f"{sid}:target 指的 {rel} 不存在"]
    if needle is not None and needle not in _scen_visible_text(f):
        return [f"{sid}:{rel} 裡找不到 {needle}(整行註解不算數)"
                "——題目講的那段已經被改掉或移除"]
    return []


def check_scenario_targets(scenarios, repo):
    """回傳「這題的目標已經不在了」的說明清單(空=全部健在)。"""
    repo = Path(repo)
    bad = []
    for s in scenarios:
        sid = s.get("id", "(無 id)")
        prompt = s.get("prompt") or s.get("question") or ""
        for rel in _scen_paths(prompt):
            if _scen_resolve(repo, rel) is None:
                bad.append(f"{sid}:題目提到 {rel},但它在 repo 裡不存在(改名或刪掉了?)")
        for item in (s.get("target") or []):
            bad.extend(_check_one_target(sid, item, repo))
    return bad


def _git_env():
    """洗掉會蓋過 cwd 的 git 環境變數——它們一設,`cwd=副本` 就完全不算數,
    指令會落到別的 repo 上(2026-09-21 審查席在完全正常的來源上重現過本體遠端被拔光)。"""
    # command-scope config可覆蓋副本的remote/hooksPath；只拔定位變數不夠。
    # GIT_TRACE/GIT_TRACE2* 可直接指定寫入檔；AUTHOR/COMMITTER 會蓋過副本假身分。
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GIT_CONFIG", "GIT_TRACE", "GIT_AUTHOR_", "GIT_COMMITTER_"))}
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
              "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(k, None)
    # 不改HOME或真設定檔；探針Git只讀副本自己的設定。
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return env


class SourceProbeCleanupError(RuntimeError):
    """專用副本清不掉：不得以一般單題例外吞掉再續跑。"""


class ProbeHealthError(RuntimeError):
    """全域 skills 無法驗健康或已損壞：整批不能再跑。"""


class ProbeAttemptBudgetExceeded(RuntimeError):
    """消融派工的模型嘗試額度用完；重試也消耗一格。"""


def _prepare_source_probe(work, config, token):
    """只在尚未提交的自有副本注入Python註解；不追連結，不改語法。"""
    if not isinstance(config, dict):
        raise ValueError("source_probe 必須是物件")
    rel, prefix = config.get("path"), config.get("line_prefix")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError("source_probe 路徑必須在副本內")
    if not isinstance(prefix, str) or not prefix or "\n" in prefix or "\r" in prefix:
        raise ValueError("source_probe 缺目標行前綴")
    root = Path(work).resolve(strict=True)
    target = root
    for part in Path(rel).parts:
        target = target / part
        if target.is_symlink():
            raise ValueError("source_probe 不接受符號連結")
    info = target.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("source_probe 只接受單連結普通檔案")
    original = target.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise ValueError("source_probe 目標行須恰有一個")
    i = hits[0]
    body = lines[i].rstrip("\r\n")
    lines[i] = body + "  # " + token + lines[i][len(body):]
    updated = "".join(lines)
    if ast.dump(ast.parse(original), include_attributes=True) != ast.dump(ast.parse(updated), include_attributes=True):
        raise ValueError("source_probe 注入改變語法")
    target.write_text(updated, encoding="utf-8")


def _redact_source_token(value, token):
    if isinstance(value, str):
        # 摘要可能在標記中途截斷，連該前綴的殘段一併遮罩。
        return re.sub(r"LUMOS_READ_[0-9a-f]{0,32}", "[source-marker]", value) if token else value
    if isinstance(value, dict):
        return {k: _redact_source_token(v, token) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_redact_source_token(v, token) for v in value)
    return value


def _remove_sandbox(work):
    try:
        shutil.rmtree(work.parent)
    except OSError as e:
        raise SourceProbeCleanupError("專用副本移除失敗；停止整批") from e


def make_sandbox(src, arm="with", source_probe=None):
    """複製工作樹到臨時目錄，拒絕外指路徑並重建副本 Git 設定。回副本路徑。
    arm="without":commit 前先砍 CLAUDE.md 的「第一個工具呼叫」小節(見 strip_lumos_first_rule),
    後續逐場副本從這份已處理的基線複製。

    2026-08-23 事故:守衛題 a05 的情境是「沒有我就開工做」,被測 AI 真的改了計劃檔並 push——
    臨時副本是 rsync 來的,.git/config 裡的 remote 跟著複製,push 就直接推到真遠端,
    主幹多了一筆 author=probe@local 的「probe snapshot」(已覆蓋)。
    意外 push 的防線為空 remote 與副本專用 pre-push hook；這不封鎖模型主動指定 URL 或其他網路工具。
    """
    # ★隔離的前提:副本要有自己的 git 目錄★(2026-09-21,Issues/探針以工作樹為來源會改到本體)
    # 副本設定重建及 pre-push hook 都靠「git 指令落在副本上」才成立。
    # 前提不成立時它們會反過來寫進本體:真遠端被拔光、真 hooksPath 被指到臨時目錄,
    # 所有防護層靜默失效,而且要等到 push 失敗才有人發現。
    # ★用正面條件判,不列舉壞形狀★(審查席:第一版只擋「.git 是檔」,漏了 symlink 與 GIT_DIR):
    #   ① 問 git 來源的 git 目錄實際在哪,要求它就在來源底下(worktree/symlink/separate-git-dir 一起涵蓋)
    #   ② 問的時候與之後所有 git 呼叫都用洗過的環境,GIT_DIR / GIT_WORK_TREE 這類會蓋掉 cwd 的變數一律拔掉
    genv = _git_env()
    real_src = Path(os.path.realpath(src))
    probe = subprocess.run(["git", "-C", str(real_src), "rev-parse", "--absolute-git-dir"],
                           capture_output=True, text=True, env=genv)
    if probe.returncode != 0:
        raise RuntimeError(f"來源 {src} 問不出 git 目錄({probe.stderr.strip()[:120]}),沙盒隔離的前提不成立,停手")
    gitdir = Path(os.path.realpath(probe.stdout.strip()))
    if not str(gitdir).startswith(str(real_src) + os.sep):
        raise RuntimeError(
            f"來源 {src} 的 git 目錄在 {gitdir},不在來源目錄裡(常見原因:它是 git worktree、"
            ".git 是指到別處的 symlink、或用了 --separate-git-dir)。"
            "沙盒的隔離動作會寫進那個 git 目錄所屬的 repo——拔掉真遠端、改掉真 hooksPath,防護會靜默失效。"
            "要做對照組請用完整 clone(git clone),不要用 git worktree add。"
        )
    tmp = Path(tempfile.mkdtemp(prefix="lumos-probe-"))
    work = tmp / "repo"
    try:
        _populate_sandbox(src, work, tmp, arm, genv, source_probe)
    except BaseException:
        _remove_sandbox(work)
        raise
    return work


def _check_git_metadata_links(gitdirs):
    """Git目錄在副本內仍不夠：refs/objects等符號連結會把寫入導回來源。"""
    for gitdir in gitdirs:
        for parent, dirs, files in os.walk(gitdir):
            if any((Path(parent) / name).is_symlink() for name in dirs + files):
                raise RuntimeError("副本Git資料含符號連結，未執行隔離寫入")


def _check_copied_git_paths(work, genv):
    """複製可能保留絕對gitfile、commondir或core.worktree；Git寫入前重驗。"""
    probe = subprocess.run(
        ["git", "-C", str(work), "rev-parse", "--path-format=absolute",
         "--git-dir", "--git-common-dir", "--show-toplevel"],
        capture_output=True, text=True, env=genv,
    )
    paths = probe.stdout.splitlines()
    if probe.returncode != 0 or len(paths) != 3:
        raise RuntimeError("副本Git實際路徑無法確認，未執行隔離寫入")
    gitdir, common, toplevel = (Path(p).resolve() for p in paths)
    root = work.resolve()
    if (gitdir == root or not gitdir.is_relative_to(root)
            or common == root or not common.is_relative_to(root) or toplevel != root):
        raise RuntimeError("副本Git目錄或工作樹指向副本外，未執行隔離寫入")
    _check_git_metadata_links({gitdir, common})
    return gitdir, common


def _check_worktree_entries(work, gitdir, common):
    """副本不接受另一套Git資料或指到副本外的工作樹連結。"""
    root = work.resolve()
    metadata = {gitdir, common}
    if (root / ".git").is_symlink():
        raise RuntimeError("副本頂層Git連結未隔離")
    if (gitdir / "modules").exists() or (common / "modules").exists():
        raise RuntimeError("副本含子模組Git資料，未執行隔離寫入")
    if (gitdir / "worktrees").exists() or (common / "worktrees").exists():
        raise RuntimeError("副本含指向其他工作樹的Git資料，未執行隔離寫入")
    for parent, dirs, files in os.walk(root, followlinks=False):
        here = Path(parent)
        # bare repo 沒有 .git 入口，可能以任意名稱藏在工作樹；不可讓它帶自己的 remote/hook。
        if here != root and (here / "HEAD").is_file() and (here / "config").is_file() \
                and (here / "objects").is_dir() and (here / "refs").is_dir():
            raise RuntimeError("副本含巢狀bare Git資料，未執行隔離寫入")
        for name in dirs + files:
            path = here / name
            if path in metadata:
                continue
            if name.casefold() in (".git", ".gitmodules"):
                if path != root / ".git":
                    raise RuntimeError("副本含巢狀Git或子模組，未執行隔離寫入")
            if path.is_symlink():
                try:
                    target = path.resolve(strict=True)
                except (OSError, RuntimeError) as e:
                    raise RuntimeError("副本工作樹連結無法安全解析") from e
                if not target.is_relative_to(root):
                    raise RuntimeError("副本工作樹連結指向副本外，未啟動模型")
        dirs[:] = [name for name in dirs if here / name not in metadata]


def _reset_copied_git_config(work, gitdir, common, hooks, genv):
    """只保留讀取既有物件所需的格式；不執行複製來的Git動作設定。"""
    config = common / "config"
    ext = subprocess.run(
        ["git", "config", "--file", str(config), "--no-includes", "--null",
         "--get-regexp", r"^extensions\."], capture_output=True, env=genv,
    )
    if ext.returncode not in (0, 1):
        raise RuntimeError("副本Git擴充格式無法確認，未執行隔離寫入")
    keys = {row.partition(b"\n")[0].decode("ascii", "replace")
            for row in ext.stdout.split(b"\0") if row}
    if keys - {"extensions.worktreeconfig", "extensions.objectformat"}:
        raise RuntimeError("副本Git使用未支援的擴充格式，未執行隔離寫入")
    obj = subprocess.run(["git", "-C", str(work), "rev-parse", "--show-object-format=storage"],
                         capture_output=True, text=True, env=genv)
    if obj.returncode != 0 or obj.stdout.strip() not in ("sha1", "sha256"):
        raise RuntimeError("副本Git物件格式無法確認，未執行隔離寫入")
    fmt = obj.stdout.strip()
    body = ("[core]\n"
            f"\trepositoryformatversion = {1 if fmt == 'sha256' else 0}\n"
            "\tfilemode = true\n\tbare = false\n\tlogallrefupdates = true\n"
            "[user]\n\tname = probe\n\temail = probe@local\n")
    if fmt == "sha256":
        body += "[extensions]\n\tobjectformat = sha256\n"
    temporary = config.with_name("config.probe-new")
    temporary.write_text(body, encoding="utf-8")
    temporary.replace(config)
    worktree_config = gitdir / "config.worktree"
    if worktree_config.exists():
        worktree_config.unlink()
    subprocess.run(["git", "config", "--file", str(config), "core.hooksPath", str(hooks)],
                   env=genv, check=True)
    remote = subprocess.run(["git", "remote"], cwd=str(work), env=genv,
                            capture_output=True, text=True, check=True)
    effective_hook = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                                    cwd=str(work), env=genv, capture_output=True, text=True, check=True)
    if remote.stdout.strip() or effective_hook.stdout.strip() != str(hooks):
        raise RuntimeError("副本有效遠端或防推勾子不符合隔離條件")


def _check_gitlinks(work, genv):
    tracked = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=str(work),
                             env=genv, capture_output=True, check=True)
    if any(row.startswith(b"160000 ") for row in tracked.stdout.split(b"\0")):
        raise RuntimeError("副本索引含子模組gitlink，未啟動模型")


def _populate_sandbox(src, work, tmp, arm, genv, source_probe):
    work.mkdir(parents=True)
    subprocess.run(["rsync", "-a", "--exclude", "node_modules", "--exclude", ".venv",
                    f"{src}/", f"{work}/"], check=True)
    gitdir, common = _check_copied_git_paths(work, genv)
    _check_worktree_entries(work, gitdir, common)
    # 副本專用 hooks 目錄:pre-push 硬擋；其他 hook 不存在。
    hooks = tmp / "hooks"
    hooks.mkdir()
    (hooks / "pre-push").write_text("#!/bin/sh\necho '探針沙盒:禁止 push' >&2\nexit 1\n", encoding="utf-8")
    (hooks / "pre-push").chmod(0o755)
    _reset_copied_git_config(work, gitdir, common, hooks, genv)
    _check_gitlinks(work, genv)
    if arm == "without":
        cm = work / "CLAUDE.md"
        new, ok = strip_lumos_first_rule(cm.read_text(encoding="utf-8"))
        if not ok:
            raise RuntimeError("without 組:CLAUDE.md 找不到「第一個工具呼叫」小節的邊界,拔不乾淨,實驗無效,停手")
        cm.write_text(new, encoding="utf-8")
    if source_probe is not None:
        _prepare_source_probe(work, *source_probe)
    # 標記必須在快照中，否則收工hook會把儀器註解當成模型改碼。
    # commit 成乾淨狀態(含未 commit 的改動——索引/筆記常是剛寫還沒 commit)
    subprocess.run(["git", "add", "-A"], cwd=str(work), env=genv, check=True)
    commit = subprocess.run(["git", "-c", "user.name=probe", "-c", "user.email=probe@local",
                             "commit", "-qm", "probe snapshot", "--no-verify"],
                            cwd=str(work), env=genv, capture_output=True, text=True)
    if commit.returncode not in (0, 1):
        raise RuntimeError("副本快照提交失敗，不啟動模型")
    clean = subprocess.run(["git", "status", "--porcelain"], cwd=str(work), env=genv,
                           capture_output=True, text=True, check=True)
    if clean.stdout.strip():
        raise RuntimeError("副本快照不乾淨，不啟動模型")


def _validate_scenario(sc):
    """題目缺必要欄位就回一句錯誤字串(否則 None)。★r1 邊界席:缺 expect 的畸形題原本會先燒一次真實
    claude -p 才在索引時炸,白花稀缺配額;改成派工前先擋。"""
    if (not isinstance(sc.get("id"), str) or not sc["id"].strip()
            or not sc["id"].isprintable()):
        return "題目缺 id"
    if not sc.get("prompt"):
        return f"題目 {sc.get('id')} 缺 prompt"
    if not sc.get("expect"):
        return f"題目 {sc.get('id')} 缺 expect(判準),不跑"
    if "source_probe" in sc and (not isinstance(sc["source_probe"], dict) or not sc["source_probe"] or sc.get("forbid_before")):
        return "source_probe 必須有目標設定且不得混用順序禁令"
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


class ProbeAttemptLedgerError(RuntimeError):
    """持久額度帳不可判；不是模型行為失敗。"""


def default_attempt_ledger():
    return Path.home() / ".local/state/lumos/probe-attempts.sqlite3"


def _attempt_ledger_transaction(path, limit, claim=False, now=None):
    """同一交易核帳並選擇追加啟動意圖；不從可歸檔結果推算用量。"""
    if type(limit) is not int or limit < 0:
        raise ProbeAttemptLedgerError("窗口上限必須為非負整數")
    if limit == 0:
        return True if claim else None
    import math
    now = time.time() if now is None else now
    if not isinstance(now, (int, float)) or not math.isfinite(now) or now < 0:
        raise ProbeAttemptLedgerError("用量帳時鐘不可判")
    conn = None
    try:
        import sqlite3
        path = Path(path).absolute()
        try:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise ProbeAttemptLedgerError("用量帳必須為一般檔案")
            fresh = False
        except FileNotFoundError:
            fresh = True
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        conn = sqlite3.connect(str(path), timeout=5.0, isolation_level=None)
        conn.execute("BEGIN IMMEDIATE")
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if fresh and version == 0:
            conn.execute("CREATE TABLE ledger_meta (id INTEGER PRIMARY KEY CHECK(id=1), initialized_at REAL NOT NULL)")
            conn.execute("CREATE TABLE launch_intents (claimed_at REAL NOT NULL CHECK(typeof(claimed_at)='real' AND claimed_at>=0))")
            conn.execute("CREATE INDEX intents_time ON launch_intents(claimed_at)")
            conn.execute("INSERT INTO ledger_meta VALUES (1, ?)", (float(now),))
            conn.execute("PRAGMA user_version=1")
        elif version != 1:
            raise ProbeAttemptLedgerError("用量帳版本或結構不可判")
        meta = conn.execute("SELECT initialized_at FROM ledger_meta").fetchall()
        if len(meta) != 1 or type(meta[0][0]) is not float or not math.isfinite(meta[0][0]):
            raise ProbeAttemptLedgerError("用量帳初始化時間不可判")
        initialized = meta[0][0]
        latest = conn.execute("SELECT MAX(claimed_at) FROM launch_intents").fetchone()[0]
        if latest is not None and (type(latest) is not float or not math.isfinite(latest)):
            raise ProbeAttemptLedgerError("用量帳啟動時間不可判")
        if now < max(initialized, latest if latest is not None else initialized):
            raise ProbeAttemptLedgerError("時鐘早於已記用量時間，停止派工")
        used = conn.execute("SELECT COUNT(*) FROM launch_intents WHERE claimed_at > ?", (now - 18000,)).fetchone()[0]
        remaining = 0 if now < initialized + 18000 else max(0, limit - used)
        if claim and remaining:
            conn.execute("INSERT INTO launch_intents VALUES (?)", (float(now),))
        conn.commit()
        return bool(remaining) if claim else remaining
    except (OSError, ImportError) as exc:
        raise ProbeAttemptLedgerError(f"用量帳不可用: {type(exc).__name__}") from exc
    except Exception as exc:
        if isinstance(exc, ProbeAttemptLedgerError):
            raise
        raise ProbeAttemptLedgerError(f"用量帳交易失敗: {type(exc).__name__}") from exc
    finally:
        if conn is not None:
            try:
                if conn.in_transaction:
                    conn.rollback()
            finally:
                conn.close()


def attempt_ledger_remaining(path, limit, now=None):
    return _attempt_ledger_transaction(path, limit, now=now)


def claim_model_attempt(path, limit, now=None):
    return _attempt_ledger_transaction(path, limit, claim=True, now=now)


def run_one_codex(sc, workdir, timeout, model, arm="with", stop_block="on", bypass_trust=False, source_token=None, attempt_ledger=None, max_per_window=0):
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
    env = _git_env(); env["LUMOS_PROBE"] = "1"
    if arm == "without":
        env["LUMOS_ENTRY_HOOK_OFF"] = "1"
    if stop_block == "off":
        env["LUMOS_STOP_BLOCK_OFF"] = "1"
    t0 = time.time()
    instrument_fail = None   # 超時 / 非零退出 = 儀器例外,這場不算分(code-codex-s3 r1 外家 #3:半途已印期望指令也不能判過)
    truncated = False
    if max_per_window and not claim_model_attempt(attempt_ledger or default_attempt_ledger(), max_per_window):
        raise ProbeAttemptBudgetExceeded("本機持久窗口額度已用完，未啟動模型")
    try:
        r = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env, stdin=subprocess.DEVNULL)
        out, err = r.stdout, r.stderr[-400:]
        if r.returncode != 0:
            instrument_fail = f"codex exec 退出碼 {r.returncode}"
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = "timeout"
        instrument_fail = f"codex exec 超時 {timeout}s"
        truncated = True
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
    evidence = source_evidence(out.splitlines(), "codex", source_token) if sc.get("source_probe") else None
    ok, why, answer_content_ok = grade(sc, calls, final, evidence)
    if instrument_fail:
        ok, why = False, f"儀器例外: {instrument_fail}(這場不算分)"
    ever, first_idx = lumos_stats(calls)
    return {"id": sc["id"], "cat": sc.get("cat"), "passed": ok, "reason": why, "first_tool": calls[0] if calls else None,
            "n_calls": len(calls), "calls": calls, "secs": round(time.time() - t0, 1), "stderr": err if not ok else "",
            "answer": _redact_source_token(final or "", source_token)[:1500], "arm": arm, "ever_lumos": ever, "first_lumos_idx": first_idx,
            "source_evidence": evidence,
            "answer_content_ok": answer_content_ok, "limit_hit": False, "truncated": truncated,
            "result_subtype": "codex", "harness": "codex",
            "stop_block": stop_block, "thread_id": thread_id, "hook_trace": trace}


def _scenario_max_turns(sc, default):
    """每題可自帶 max_turns(2026-09-05 第二輪審視 d6:s15 這種要先查再建的題 18 步不夠,24 步時被砍在建檔前)。壞值退預設。
    ★只影響 claude runner:codex exec 沒有 --max-turns 這種旗標,codex runner 忽略此欄(外家 r1 m3,誠實寫在這裡與 --help)。★"""
    try:
        v = int(sc.get("max_turns", default))
        return v if v > 0 else default
    except (TypeError, ValueError):
        return default


def run_one(sc, workdir, max_turns, timeout, model, arm="with", source_token=None, attempt_ledger=None, max_per_window=0):
    max_turns = _scenario_max_turns(sc, max_turns)
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
    env = _git_env()
    env.pop("CLAUDECODE", None); env.pop("CLAUDE_CODE_ENTRYPOINT", None)
    # ★探針沙盒事故防線(2026-09-02,見 make_sandbox 註)★:被測 session 的 HOME 是真的 ~/,
    # 一旦它跑 lumos install/update/bootstrap 就會把真的 ~/.claude/skills 重連到沙盒、沙盒清掉後全斷。
    # LUMOS_PROBE=1 讓那幾個指令在探針下直接拒絕(scripts/lumos:_refuse_if_probe)。
    env["LUMOS_PROBE"] = "1"
    if arm == "without":
        env["LUMOS_ENTRY_HOOK_OFF"] = "1"   # SessionStart 入口 hook 看到就靜默,同一句提醒不能從第二個口進來
    t0 = time.time()
    timed_out = False
    returncode = 0
    if max_per_window and not claim_model_attempt(attempt_ledger or default_attempt_ledger(), max_per_window):
        raise ProbeAttemptBudgetExceeded("本機持久窗口額度已用完，未啟動模型")
    try:
        r = subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=timeout, env=env)
        out = r.stdout
        err = r.stderr[-400:]
        returncode = r.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = "timeout"
        timed_out = True
    calls = tool_calls_from_stream(out.splitlines())
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
    # ⑩ 答案對不對(工具鏈補強十件):情境可帶 answer_expect=[regex…],最後回覆文字要全部命中。
    # ★r1 外家/正確性席:答案內容對不對 與 通過閘(敲對指令+答對)分開記★——
    # M4 若只看 passed,會把「答案對但先 grep」記成失敗,混淆「答案對不對」與「走對路徑沒有」。
    evidence = source_evidence(out.splitlines(), "claude", source_token) if sc.get("source_probe") else None
    ok, why, answer_content_ok = grade(sc, calls, final, evidence)
    limit_hit = is_limit_hit(calls, final, result_ev)
    # ★截斷不算分★(Projects/探針判準對齊程式碼為主_計劃 [S1]):撞回合上限或逾時,紀錄不完整,判過判不過都是猜;
    # 以前記成「沒敲到期望指令」,9 月週抽四個失敗裡三個其實是這個。跟 Codex 執行器的逾時同一套處理。
    truncated = (not limit_hit) and (timed_out or result_ev.get("subtype") == "error_max_turns")
    if limit_hit:
        ok, why = False, "儀器例外: 帳號用量/速率上限,claude -p 沒真的跑,這場不算分"
    elif truncated:
        cause = f"逾時 {timeout}s" if timed_out else f"撞到回合上限 {max_turns}"
        ok, why = False, f"儀器例外: {cause},紀錄不完整,這場不算分(截斷)"
    elif returncode != 0:
        ok, why = False, f"儀器例外: claude -p 退出碼 {returncode}(這場不算分)"
    ever, first_idx = lumos_stats(calls)
    return {"id": sc["id"], "cat": sc.get("cat"), "passed": ok, "reason": why,
            "first_tool": calls[0] if calls else None, "n_calls": len(calls),
            "calls": calls, "secs": round(time.time() - t0, 1), "stderr": err if not ok else "",
            "answer": _redact_source_token(final or "", source_token)[:1500],
            "source_evidence": evidence,
            "arm": arm, "ever_lumos": ever, "first_lumos_idx": first_idx,
            "answer_content_ok": answer_content_ok,
            "limit_hit": limit_hit, "truncated": truncated,
            "result_subtype": result_ev.get("subtype"), "harness": "claude"}


def summarize_results(results, arm="with"):
    """一批結果 → 總結。分母只算有效場次(扣掉截斷、用量上限、其他儀器例外)。
    ★有效不到一半時分母退回整批★:自主迴圈只在總結行 p≠n 時發通知,不退回的話整批被截斷會是 0/0、安靜顯示全過。
    總結行第一行固定以「p/n 個情境 Claude 自己敲對了」開頭——governance/autonomous-loop.sh 的 run_probe 靠這個格式解析。"""
    def is_instr(r):
        return str(r.get("reason", "")).startswith("儀器例外")
    total = len(results)
    valid = [r for r in results if not is_instr(r)]
    excl = [r for r in results if is_instr(r)]
    n_trunc = sum(1 for r in excl if r.get("truncated"))
    n_limit = sum(1 for r in excl if r.get("limit_hit") and not r.get("truncated"))
    n_other = len(excl) - n_trunc - n_limit
    inconclusive = total > 0 and len(valid) * 2 < total
    p = sum(1 for r in valid if r.get("passed"))
    n = total if inconclusive else len(valid)
    per = {}
    for r in results:
        c = per.setdefault(r.get("id", "?"), [0, 0])
        c[1] += 1
        c[0] += 1 if r.get("truncated") else 0
    mostly = [q for q, (t, k) in per.items() if k > 1 and t * 2 > k]
    line = f"{p}/{n} 個情境 Claude 自己敲對了 lumos 指令" + (f"(組別 {arm})" if arm != "with" else "")
    parts = [f"{name} {k}" for name, k in (("截斷", n_trunc), ("用量上限", n_limit), ("其他儀器例外", n_other)) if k]
    if parts:
        line += ";不算分:" + "、".join(parts)
    if inconclusive:
        line += f";★有效場次 {len(valid)}/{total} 不到一半,這批不能下結論(分母退回整批)★"
    if mostly:
        line += "\n截斷過半的題(題目或步數上限要檢查,不是 AI 沒照規矩): " + ", ".join(mostly)
    return {"passed": p, "scored": n, "total": total, "valid_total": len(valid),
            "inconclusive": inconclusive, "mostly_truncated": mostly,
            "failed": [r.get("id") for r in valid if not r.get("passed")],
            "excluded": [r.get("id") for r in excl], "line": line}


def history_record(ts, seed, summary, arm="with", runs=1, sandbox_secs=0.0, model_secs=0.0, fatal=False):
    """週抽歷史一列:failed 只含有效場次沒過的題;被排除的另記;帶判準版本(換過判準的紀錄不可直接比)。"""
    rec = {"ts": ts, "seed": seed, "passed": summary["passed"], "total": summary["scored"],
           "valid_total": summary.get("valid_total", summary["scored"]),
           "failed": summary["failed"], "excluded": summary["excluded"],
           "inconclusive": summary.get("inconclusive", False), "fatal": fatal,
           "grader": GRADER_VERSION, "sandbox_version": SANDBOX_VERSION,
           "sandbox_secs": round(sandbox_secs, 3), "model_secs": round(model_secs, 3)}
    if arm != "with" or runs > 1:
        rec.update({"arm": arm, "runs": runs})
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT),
                    help="要被探的專案根目錄(預設=本 repo)。★探別的專案必須給★——"
                         "沒給的話不論在哪個目錄執行,複製的都是 lumos-toolchain 自己,"
                         "題目再怎麼寫都是在探錯的 repo(2026-08-22 實際踩過)")
    ap.add_argument("--scenarios", default=str(ROOT / "governance" / "scenarios" / "commands.jsonl"))
    ap.add_argument("--only", default="")
    ap.add_argument("--exact-id", default=None,
                    help="只跑 id 完全相等的一題；消融派工專用，找不到或重複時拒絕")
    # ★預設 8 → 18(2026-08-22)★:實測既有題庫最慢 6 步(s02/s11),8 只留 2 步餘裕;
    # absence 題組天生要「查不到→換方法再查」,最慢 12 步——吃預設會在它開口之前截斷,
    # 三題全假紅。假紅的下一步永遠是有人把閘關掉,所以預設本身要夠。
    # ★為什麼不設更大★:步數上限不是「越寬越安全」。給太多步,那些其實在瞎繞的題也可能
    # 繞到答對,反而把問題蓋掉。18 = 最慢那題(12 步)加一半餘裕,不是拍腦袋。
    ap.add_argument("--max-turns", type=int, default=18, help="claude runner 的回合上限(每題可用 max_turns 欄覆寫;codex runner 沒有對應旗標、忽略此值)")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--model", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--keep", action="store_true", help="保留最後一個普通題臨時副本；讀碼題仍清除")
    ap.add_argument("--sample", type=int, default=0, help="只抽 N 題(決定性:依 --seed 輪轉,給自主迴圈每週抽查用)")
    ap.add_argument("--seed", default="", help="抽樣種子(例:週數);同種子同題")
    ap.add_argument("--history", default="", help="把本次摘要 append 到這個 jsonl(ts/passed/total/failed)")
    ap.add_argument("--ts", default="", help="寫進 history 的時間戳(排程端給)")
    ap.add_argument("--dry-list", action="store_true", help="只印抽到的題目 id,不跑(測抽樣用)")
    ap.add_argument("--allow-stale-targets", action="store_true",
                    help="題目指的東西已經不存在也照跑(預設停手;腐爛的題目會量出假訊號)")
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
    ap.add_argument("--max-attempts", type=int, default=0,
                    help="本批最多啟動幾次模型，含用量重試；0=不設。消融派工的窗口額度專用")
    ap.add_argument("--max-per-window", type=int, default=0, help="本機共用帳五小時啟動意圖上限；0=停用記帳")
    ap.add_argument("--attempt-ledger", default="", help="共用用量帳路徑；首次初始化冷卻五小時，初始化前先停止舊探針")
    a = ap.parse_args()
    if a.runs < 1:
        print("✗ --runs 至少 1", file=sys.stderr); return 2
    if a.max_per_window < 0:
        print("✗ --max-per-window 不可為負", file=sys.stderr); return 2
    if a.max_attempts < 0:
        print("✗ --max-attempts 不可為負", file=sys.stderr); return 2
    # 輸出寫不出去要在花模型額度之前就知道,不能整批跑完才炸
    for flag, target, replace in (("--out", a.out, True), ("--history", a.history, False)):
        problem = target and _output_target_problem(target, replace=replace)
        if problem:
            print(f"✗ {flag} {problem},停手", file=sys.stderr); return 2
    if a.exact_id is not None and a.only:
        print("✗ --exact-id 與 --only 不可並用", file=sys.stderr); return 2
    if (a.exact_id is not None and (not a.exact_id.strip() or not a.exact_id.isprintable())):
        print("✗ --exact-id 不可為空白或含不可列印字元", file=sys.stderr); return 2
    scs = []
    for f in a.scenarios.split(","):
        scs += [json.loads(l) for l in Path(f).read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.exact_id is not None:
        scs = [s for s in scs if s.get("id") == a.exact_id]
        if len(scs) != 1:
            print("✗ --exact-id 必須且只能選到一題", file=sys.stderr); return 2
    elif a.only:
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
    # ★跑之前先驗題目的目標還在不在★:腐爛的題目會安靜地量出假訊號(見 check_scenario_targets)
    rot = check_scenario_targets(scs, src)
    if rot:
        print("✗ 題目腐爛了,這一輪不跑——量到的會是假訊號,不是規矩失效:", file=sys.stderr)
        for line in rot:
            print("    " + line, file=sys.stderr)
        print("  修法:把題目換成現在真的存在的目標(條件:①現在真的存在 ②改了會影響行為 "
              "③它的家有筆記在講它),或在題目加 target 欄位宣告要驗什麼。", file=sys.stderr)
        print("  真的要照跑(例如就是要量腐爛時的行為):--allow-stale-targets", file=sys.stderr)
        if not a.allow_stale_targets:
            return 3
    baseline = None
    sandbox_secs = 0.0
    model_secs = 0.0
    setup_error = None
    setup_started = time.monotonic()
    try:
        baseline = make_sandbox(src, a.arm)
    except Exception as e:
        setup_error = f"批次基線建立失敗: {type(e).__name__}: {e}"
    sandbox_secs += time.monotonic() - setup_started
    # skills 走 ~/.claude(symlink 回本 repo),不用複製
    if baseline is not None:
        print(f"探的是: {src}\n凍結基線: {baseline}" + (f"\n組別: {a.arm}  每題 {a.runs} 次" if (a.arm != "with" or a.runs > 1) else ""),
              file=sys.stderr)
    results = []
    waited = 0
    attempts_started = 0
    fatal = setup_error is not None
    fatal_reason = setup_error
    retained = None
    def run_at(workdir, token=None):
        extra = {"source_token": token} if token is not None else {}
        if a.max_per_window:
            extra.update(attempt_ledger=Path(a.attempt_ledger or default_attempt_ledger()).absolute(), max_per_window=a.max_per_window)
        return (run_one_codex(sc, workdir, a.timeout, a.model, a.arm, a.stop_block, a.codex_bypass_hook_trust, **extra) if a.runner == "codex"
                else run_one(sc, workdir, a.max_turns, a.timeout, a.model, a.arm, **extra))
    try:
        for sc in scs if baseline is not None else []:
            for k in range(1, a.runs + 1):
                retried = []
                while True:
                    work = None
                    token = "LUMOS_READ_" + secrets.token_hex(16) if sc.get("source_probe") else None
                    res = None
                    attempt_fatal = False
                    attempt_sandbox_secs = 0.0
                    attempt_model_secs = 0.0
                    setup_started = time.monotonic()
                    try:
                        bad = _validate_scenario(sc)
                        if bad:
                            raise ValueError(bad)
                        if a.max_attempts and attempts_started >= a.max_attempts:
                            raise ProbeAttemptBudgetExceeded("模型嘗試額度已用完")
                        # baseline 已套用 arm；每場從它複製，不能讓前場或來源的後續修改滲入。
                        work = make_sandbox(baseline, "with", source_probe=(sc["source_probe"], token) if token else None)
                        setup_elapsed = time.monotonic() - setup_started
                        sandbox_secs += setup_elapsed
                        attempt_sandbox_secs += setup_elapsed
                        model_started = time.monotonic()
                        try:
                            attempts_started += 1
                            res = _redact_source_token(run_at(work, token), token)
                        finally:
                            attempt_model_secs = time.monotonic() - model_started
                            model_secs += attempt_model_secs
                            # runner/解析器拋錯也可能已改到真 HOME；下一場前仍須驗健康。
                            try:
                                health = global_skills_health()
                            except Exception as e:
                                raise ProbeHealthError(f"全域 skills 健康檢查無法完成: {type(e).__name__}") from e
                            if health:
                                raise ProbeHealthError(f"全域 skills 健康檢查失敗({len(health)} 個連結)")
                    except Exception as e:
                        if work is None or isinstance(e, (SourceProbeCleanupError, ProbeHealthError,
                                                          ProbeAttemptBudgetExceeded, ProbeAttemptLedgerError)):
                            attempt_fatal = True
                        res = {"id": sc.get("id", "?"), "cat": sc.get("cat"), "passed": False,
                               "reason": _redact_source_token(f"儀器例外: {type(e).__name__}: {e}", token), "first_tool": None,
                               "n_calls": 0, "calls": [], "secs": 0, "stderr": "",
                               "arm": a.arm, "ever_lumos": False, "first_lumos_idx": None,
                               "limit_hit": False, "result_subtype": None, "source_evidence": "unknown" if sc.get("source_probe") else None,
                               "fatal": attempt_fatal}
                    finally:
                        # 讀碼標記的現場永不保留；普通題只保留最後一場通過隔離驗收的副本。
                        retain = bool(a.keep and not token and not attempt_fatal
                                      and res is not None and not res.get("limit_hit") and work is not None)
                        if work is not None:
                            cleanup_started = time.monotonic()
                            try:
                                if retain:
                                    if retained is not None:
                                        previous = retained
                                        retained = None
                                        _remove_sandbox(previous)
                                    retained = work
                                else:
                                    _remove_sandbox(work)
                            except SourceProbeCleanupError as e:
                                attempt_fatal = True
                                if retain:
                                    retained = None
                                # 若移除上一份保留副本失敗，這份新副本也不能留下。
                                if retain:
                                    try:
                                        _remove_sandbox(work)
                                    except SourceProbeCleanupError:
                                        pass
                                res = {"id": sc.get("id", "?"), "cat": sc.get("cat"), "passed": False,
                                       "reason": f"儀器例外: {e}", "first_tool": None,
                                       "n_calls": 0, "calls": [], "secs": 0, "stderr": "",
                                       "arm": a.arm, "ever_lumos": False, "first_lumos_idx": None,
                                       "limit_hit": False, "result_subtype": None,
                                       "source_evidence": "unknown" if token else None, "fatal": True}
                            finally:
                                cleanup_elapsed = time.monotonic() - cleanup_started
                                sandbox_secs += cleanup_elapsed
                                attempt_sandbox_secs += cleanup_elapsed
                        if work is None:
                            setup_elapsed = time.monotonic() - setup_started
                            sandbox_secs += setup_elapsed
                            attempt_sandbox_secs += setup_elapsed
                    res["sandbox_secs"] = round(attempt_sandbox_secs, 3)
                    res["model_secs"] = round(attempt_model_secs, 3)
                    if attempt_fatal:
                        fatal = True
                        fatal_reason = res["reason"]
                    if res.get("limit_hit") and waited < a.wait_on_limit:
                        try:
                            exhausted = bool(a.max_attempts and attempts_started >= a.max_attempts)
                            if a.max_per_window:
                                exhausted = exhausted or attempt_ledger_remaining(Path(a.attempt_ledger or default_attempt_ledger()).absolute(), a.max_per_window) <= 0
                            if exhausted:
                                raise ProbeAttemptBudgetExceeded("重試前模型額度已用完，未等待或啟動模型")
                        except (ProbeAttemptBudgetExceeded, ProbeAttemptLedgerError) as exc:
                            res.update(passed=False, fatal=True, limit_hit=False, reason=f"儀器例外: {type(exc).__name__}: {exc}")
                            fatal = True
                            fatal_reason = res["reason"]
                            break
                        retried.append({"reason": res.get("reason"),
                                        "sandbox_secs": res["sandbox_secs"],
                                        "model_secs": res["model_secs"]})
                        delay = min(300, a.wait_on_limit - waited)
                        print(f"  ⏸ {sc['id']} 撞到帳號用量上限,等 {delay} 秒再試同一場(已等 {waited}s / 上限 {a.wait_on_limit}s)", flush=True)
                        time.sleep(delay); waited += delay
                        continue
                    break
                if retried:
                    res["retry_attempts"] = retried
                res["run"] = k
                results.append(res)
                mark = "✓" if res["passed"] else "✗"
                ft = f"{res['first_tool'][0]}: {res['first_tool'][1][:70]}" if res["first_tool"] else "(沒有任何工具呼叫)"
                tag = f" #{k}" if a.runs > 1 else ""
                print(f"  {mark} {res['id']:22s}{tag} {res['secs']:6.1f}s  第一動作→ {ft}", flush=True)
                if not res["passed"]:
                    print(f"      {res['reason']}", flush=True)
                if fatal:
                    break
            if fatal:
                break
    finally:
        if baseline is not None:
            cleanup_started = time.monotonic()
            try:
                _remove_sandbox(baseline)
            except SourceProbeCleanupError as e:
                fatal = True
                fatal_reason = f"批次基線清理失敗: {e}"
            finally:
                sandbox_secs += time.monotonic() - cleanup_started
        try:
            bad = global_skills_health()
        except Exception as e:
            bad = []
            fatal = True
            health_reason = f"全域 skills 最終健康檢查無法完成: {type(e).__name__}"
            fatal_reason = f"{fatal_reason}；{health_reason}" if fatal_reason else health_reason
        if bad:
            print("\n" + "!" * 60, file=sys.stderr)
            print(f"✗ 事故:全域 ~/.claude/skills 有 {len(bad)} 個連結被動到(懸空或指進沙盒):", file=sys.stderr)
            for name, tgt in bad:
                print(f"    {name} → {tgt}", file=sys.stderr)
            print("  修:在真 repo 跑一次\n    python3 scripts/lumos install --force\n"
                  "  這代表某條路徑繞過了 LUMOS_PROBE 防線,見 Issues/探針沙盒改動真全域機器狀態", file=sys.stderr)
            print("!" * 60, file=sys.stderr)
        summ = summarize_results(results, a.arm)
        if fatal or bad:
            summ["inconclusive"] = True
            reason = fatal_reason or "全域 skills 健康檢查失敗"
            summ["line"] = (reason if reason.startswith("儀器例外:") else "儀器例外: " + reason) + "；整批不能下結論。 " + summ["line"]
        p, n = summ["passed"], summ["scored"]
        print("\n" + summ["line"])
        if a.runs > 1:
            per = {}
            for r in results:
                counts = per.setdefault(r["id"], [0, 0, 0])
                if str(r.get("reason", "")).startswith("儀器例外"):
                    counts[2] += 1
                else:
                    counts[1] += 1
                    counts[0] += 1 if r["passed"] else 0
            print("每題通過次數: " + "  ".join(
                f"{i} {c}/{t}" + (f" (不算分 {e})" if e else "")
                for i, (c, t, e) in per.items()))
        if a.out:
            # ★r1 併發席:健康檢查結果要進 JSON,不能只印 stderr——跑批只讀這個檔,
            # 印在 log 沒人看,平行時一場事故會靜默污染整批★。skills_health 非空 = 這批之後受污染。
            _atomic_write_text(Path(a.out), json.dumps({"results": results, "passed": p, "total": n,
                                                       "arm": a.arm, "runs": a.runs, "grader": GRADER_VERSION,
                                                       "excluded": summ["excluded"], "valid_total": summ["valid_total"],
                                                       "inconclusive": summ["inconclusive"], "fatal": fatal or bool(bad),
                                                       "sandbox_version": SANDBOX_VERSION,
                                                       "sandbox_secs": round(sandbox_secs, 3), "model_secs": round(model_secs, 3),
                                                       "skills_health_bad": bad}, ensure_ascii=False, indent=1))
        if a.history:
            with os.fdopen(_open_history(a.history), "a", encoding="utf-8") as hf:
                hf.write(json.dumps(history_record(a.ts, a.seed, summ, a.arm, a.runs,
                                                   sandbox_secs, model_secs, fatal or bool(bad)), ensure_ascii=False) + "\n")
        if retained is not None:
            print(f"保留最後副本: {retained}", file=sys.stderr)
    if bad or fatal:
        return 3   # ★全域 skills 事故:與「有題沒過(1)」分開,跑批看到 3 立刻停整批(r1 併發席)
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main())
