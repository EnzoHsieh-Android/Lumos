#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# MIT licensed. Full text: scripts/lumos header, or LICENSE at
# https://github.com/EnzoHsieh-Android/Lumos
"""PreToolUse hook(matcher Bash):代理要繞過 Lumos 的閘時,先問人。

單源:Projects/代理繞閘字樣問人_計劃(d1 厚掛鉤偏離、d2 寧可漏問)。

流程:
  1. 讀一次 stdin 原文 → 便宜的預篩(在 guard 之外,不跑子程序、不記事件;絕大多數 Bash 停在這)。
  2. 過了預篩才進 `_hookevent.guard`:解析事件 → `decide` → 命中就印 permissionDecision "ask"。
  3. 任何例外都放行(這是問人層,不是安全邊界)。

★存活事件只記「活著沒」★:不記問了幾次(_hookevent.py 檔頭的界線);事後量測拿 Claude 事件帳
重跑 `bypass_reasons`。
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from _hookevent import guard as _guard, mark
except Exception:          # 共用模組缺席也不能讓 Bash 卡住
    _guard = None

    def mark(kind, note=""):
        return None


# ── 逾時預算(逐字複本,見 impact-hook.py;有測試要求各份一模一樣)──────
#
# 天花板由註冊表 HOOK_BUDGET 一處生成,用 --budget 傳進來;這支只拿它當查遠端、查工作樹的 git 子程序逾時。
_BUDGET_RATIO = 0.7
_BUDGET_FLOOR = 1.0          # 再怎麼扣也留 1 秒,不要算出 0 或負數
_BUDGET_START = None         # 這支 hook 開始跑的時刻(第一次用到時記)


def _outer_budget(default=10.0):
    """從 argv 讀 --budget <秒>;沒有就回 default(保守值,不是猜大的)。
    ★上限夾住★:異常大的值會讓內層跟著失控放大,等於整個 fail-open 形同虛設。"""
    import sys as _s
    argv = _s.argv
    got = None
    for i, a in enumerate(argv):
        if a == "--budget" and i + 1 < len(argv):
            try:
                got = float(argv[i + 1])
            except ValueError:
                got = None
            break
        if a.startswith("--budget="):
            try:
                got = float(a.split("=", 1)[1])
            except ValueError:
                got = None
            break
    if got is None or got <= 0:
        got = default
    return min(float(got), 600.0)


def _inner_budget(elapsed=None, default=10.0):
    """內層某一段還能用幾秒:天花板 × 0.7 − 這支 hook 到目前為止已經花掉的時間,下限 1 秒。

    ★已耗時間自己算,不靠呼叫端記得傳★(2026-09-07 代碼審 r1 通才席抓到):
    第一版的 elapsed 預設 0,而六個呼叫點裡只有一個真的傳了值——於是同一支 hook
    只要依序呼叫兩次,理論上限就是 2 × 0.7 × 外層 = 1.4 倍外層,**結構性地超過天花板**。
    實測:進場提醒那支 7+7=14 秒 vs 外層 10;CI 狀態那支 10.5+10.5=21 秒 vs 外層 15。
    ★這正是這批改動宣稱要修掉的問題,只是換個地方重新發生。★

    ★★這是「還剩多少」不是「每段配額」★★——很容易誤解,所以講清楚:
    回傳的是「從現在到預算用完還有幾秒」。所以連續呼叫兩次拿到的兩個數字**不該相加**:
    第一次拿到 7 秒、真的用掉 5 秒之後,第二次會拿到 2 秒。
    只有在「第一段其實沒用多久」時第二次才會拿到接近 7 秒——那也是對的,因為時間真的還在。
    ★守衛要驗的是「真的用掉時間之後,下一次拿到的會變少,而且總和不超過天花板」★,
    不是「兩次的數字相加小於天花板」(那個判準本身就錯,會逼出錯誤的修法)。

    ★誠實邊界★:天花板小於約 1.43 秒時,下限 1 秒會反過來大於外層。各支的天花板看註冊表 HOOK_BUDGET
    (merge-claude-settings.py),目前都離這個門檻很遠;真要調到那麼小的話這個假設就不成立了。
    """
    import time as _tm
    global _BUDGET_START
    if _BUDGET_START is None:
        _BUDGET_START = _tm.monotonic()
    used = (_tm.monotonic() - _BUDGET_START) if elapsed is None else float(elapsed)
    return max(_BUDGET_FLOOR, _outer_budget(default) * _BUDGET_RATIO - used)
# ── ★逾時預算結束★ ──────────────────────────────────────────────────

MAX_LEN = 20000                     # 超過就不做結構分類,走字面判(把要掃的字數壓在幾萬步以內)
MAX_EXPAND = 4096                   # 變數展開後的長度上限;超過就當判不出
MAX_GIT_CALLS = 4                   # 一次判斷最多跑幾個 git 子程序;超過就當「查不到」(=不豁免、照問)
_PRE_WORDS = ("--no-veri", "hookspath", "lumos_skip_", "include.path", "includeif.")
_PRE_SHORT_N = re.compile(r"(?<![\w-])-[a-z]*n[a-z]*\b")
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_SKIP_ASSIGN = re.compile(r"^LUMOS_SKIP_[A-Za-z0-9_]*\+?=")
_GITDIR_NAME = re.compile(r"^(GIT_DIR|GIT_WORK_TREE|GIT_COMMON_DIR)(\+?=|$)")       # export/declare 的名稱
_GITDIR_ASSIGN = re.compile(r"^(GIT_DIR|GIT_WORK_TREE|GIT_COMMON_DIR)\+?=")           # 一般詞只認賦值形式
_CFG_ENV_ASSIGN = re.compile(r"^GIT_CONFIG_(KEY_[0-9]+|PARAMETERS)=(.*)$", re.S)
_KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "time", "exec", "command", "nohup", "builtin"}
_GATED_SUBS = ("commit", "push")    # Lumos 的閘只有提交前與推送前;其他子指令跳過的掛鉤本 repo 沒裝(計劃〈範圍〉)
_GIT_VALUE_OPTS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env", "--attr-source"}
_GIT_DIR_OPTS = ("--git-dir", "--work-tree")
_COMMIT_VALUE_LONG = {"--message", "--file", "--author", "--date", "--template", "--reuse-message", "--reedit-message",
                      "--fixup", "--squash", "--cleanup", "--trailer", "--pathspec-from-file"}
_PUSH_VALUE_LONG = ("--push-option", "--repo", "--receive-pack", "--exec")
_REMOTE_WRITES = {"add", "rename", "remove", "rm", "set-url"}          # 會改到遠端位址的 git remote 子指令
_ENV_VALUE_OPTS = {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"}
_COMPOUND_OPEN = {"if", "while", "until", "for", "case", "select"}
_COMPOUND_CLOSE = {"fi", "done", "esac"}
_GIT_EXE = re.compile(r"^git(-(commit|push|config|remote))?$")     # git,或直接叫子指令執行檔(r4 資安席)
_CONFIG_VALUE_OPTS = {"-f", "--file", "--blob", "--default", "--type", "--comment"}
_CONFIG_WRITE_FLAGS = {"--unset", "--unset-all", "--replace-all", "--add"}
_CONFIG_READ_FLAGS = {"--get", "--get-all", "--get-regexp", "--list", "-l", "--get-urlmatch"}
_CONFIG_SECTION_FLAGS = {"--remove-section", "--rename-section"}
_CONFIG_GLOBAL_FLAGS = {"--global", "--system", "--file", "-f", "--blob"}
_UNKNOWN = ("unknown",)
_MASK_CHARS = "();|&<>\n#`'\" \t$\\"  # 引號裡與被跳脫的這些字元先換成私用區字元,切詞時才不會被當成結構
_MASK_BASE = 0xE000
_FD_MARK = "\ue0ff"                 # 導向前的檔案代號(`2>` 的 2、`{fd}>` 的 {fd})的標記,不在遮罩範圍內
_FD_REDIR = re.compile(r"(\d+|\{[A-Za-z_][A-Za-z0-9_]*\})(?=[<>])")
_LIT_DOLLAR = "\ue0fe"             # 單引號裡或被跳脫的 `$`:還原成這個字,不會被當成變數展開(`cd '$D'` 的 $D 是字面)
_ANSI_ESC = {"n": "\n", "t": "\t", "r": "\r", "a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b", "f": "\f", "v": "\v",
             "\\": "\\", "'": "'", '"': '"', "?": "?"}
_REASON_TEXT = {
    "no-verify": "推送或提交帶了 --no-verify,推送前閘與提交前閘不會跑",
    "commit-n": "提交帶了 -n(就是 --no-verify),提交前閘不會跑",
    "c-hookspath": "用 -c、--config-env 或 GIT_CONFIG_* 把這次的掛鉤目錄換掉(含引入別的設定檔),Lumos 的閘不會跑",
    "config-hookspath": "改寫或拆掉 core.hooksPath(或引入別的設定檔),之後每次提交與推送都不再經過 Lumos 的閘",
    "lumos-skip": "設了 LUMOS_SKIP_* 環境變數,會關掉 Lumos 的一道閘",
    "literal": "指令切不開或太長,照字面看是在跳過 Lumos 的閘",
}


def _command_text(raw: str) -> str:
    """stdin 原文 → 指令本身;解不開 JSON 就回原文(壞事件照樣交給後面記失敗)。"""
    try:
        ev = json.loads(raw)
        cmd = ev.get("tool_input", {}).get("command") if isinstance(ev, dict) else None
        return cmd if isinstance(cmd, str) else ""
    except Exception:
        return raw


def _looks_bypass(text: str) -> bool:
    """字樣比對(預篩與字面判共用這一份):引號與反斜線拿掉後,有繞閘字樣、拆掉或改名 core 區段,
    或同時有 git、commit 與含 n 的短旗標。"""
    low = re.sub(r"['\"\\]", "", text).lower()
    if any(w in low for w in _PRE_WORDS):
        return True
    if re.search(r"(remove|rename)-section", low) and re.search(r"\bcore\b", low):
        return True
    return "git" in low and re.search(r"\bcommit\b", low) is not None and _PRE_SHORT_N.search(low) is not None


def prefilter(raw: str) -> bool:
    """看原文加上解碼後的指令(`--no-ver''ify` 這種拆字、續行、ANSI 引號都認得)。超過 MAX_LEN 不做前處理,
    只看原文——分類器那邊也只做字面判(r4 併發資源席:超長指令的前處理會撐破預算)。"""
    text = _command_text(raw)
    norm = ""
    if len(text) <= MAX_LEN:
        try:
            norm = _unmask(_Normalizer(text).run())     # 跟分類器同一套:接續行、解 ANSI 引號、拿掉註解與 heredoc 內文
        except Exception:
            norm = ""
    return _looks_bypass(text + "\n" + norm)


def _temp_roots():
    """暫存根:常見的系統暫存位置(審查席、測試、mktemp 會用到的),再加上本機的 tempfile.gettempdir()。"""
    return ["/tmp", "/private/tmp", "/var/tmp", "/private/var/tmp", "/var/folders", "/private/var/folders",
            tempfile.gettempdir()]


def _under_temp(path: str) -> bool:
    rp = os.path.realpath(path)
    for root in _temp_roots():
        rr = os.path.realpath(root).rstrip("/")
        if rr and (rp == rr or rp.startswith(rr + "/")):
            return True
    return False


# ── 前處理:續行、註解、heredoc、引號遮罩、指令替換 ─────────────────

def _skip_arith(cmd: str, i: int) -> int:
    """i 指在 `$((` 上;回傳配對的 `))` 之後的位置(算式裡不會有引號,直接數括號)。"""
    depth, j = 0, i + 1
    while j < len(cmd):
        if cmd[j] == "(":
            depth += 1
        elif cmd[j] == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return len(cmd)


def _read_delim(cmd: str, i: int):
    """從 i 讀 heredoc 結束字;回 (字, 新位置),讀不到回 ("", i)。"""
    while i < len(cmd) and cmd[i] in " \t":
        i += 1
    word = []
    while i < len(cmd) and cmd[i] not in " \t\n;&|<>()":
        ch = cmd[i]
        if ch in "'\"":
            j = cmd.find(ch, i + 1)
            if j == -1:
                return "", i
            word.append(cmd[i + 1:j])
            i = j + 1
        elif ch == "\\" and i + 1 < len(cmd):
            word.append(cmd[i + 1])
            i += 2
        else:
            word.append(ch)
            i += 1
    return "".join(word), i


def _find_terminator(cmd: str, pos: int, word: str, dash: bool):
    """從 pos 那一行起找獨佔一行的結束字(<<- 允許前置 Tab);回結束字那一行之後的位置,找不到回 None。"""
    n = len(cmd)
    while pos <= n:
        k = cmd.find("\n", pos)
        line = cmd[pos:k if k != -1 else n]
        if (line.lstrip("\t") if dash else line) == word:
            return k + 1 if k != -1 else n
        if k == -1:
            return None
        pos = k + 1
    return None


_ANSI_NUMERIC = (("x", re.compile(r"[0-9A-Fa-f]{1,2}"), 16), ("u", re.compile(r"[0-9A-Fa-f]{1,4}"), 16),
                 ("U", re.compile(r"[0-9A-Fa-f]{1,8}"), 16))
_ANSI_OCT = re.compile(r"[0-7]{1,3}")


def _ansi_escape(cmd: str, k: int):
    """`$'…'` 裡反斜線後面(位置 k)的數字跳脫:\\xHH、\\uHHHH、\\UHHHHHHHH、\\NNN(八進位)、\\cX(控制字元)。
    回 (解出的字, 下一個位置);不是數字跳脫回 None。比對從位置 k 原地做,不切片(切片讓整趟變平方時間,r4 併發資源席)。
    `\\c` 後面緊接結尾單引號時照字面留下,不吃掉那個引號(bash 實測;吃掉會讓引號一路開到指令尾,r4 邊界輸入席)。"""
    ch = cmd[k]
    for lead, pat, base in _ANSI_NUMERIC:
        if ch == lead:
            m = pat.match(cmd, k + 1)
            if m:
                code = int(m.group(0), base)
                return (chr(code) if code < 0x110000 else ""), m.end()
    m = _ANSI_OCT.match(cmd, k)
    if m:
        return chr(int(m.group(0), 8)), m.end()
    if ch == "c" and k + 1 < len(cmd) and cmd[k + 1] != "'":
        return chr(ord(cmd[k + 1]) & 0x1F), k + 2
    return None


def _ansi_decode(cmd: str, i: int):
    """i 指在 `$'` 上;回 (解出來的字串, 結尾單引號之後的位置)。"""
    out, j = [], i + 2
    while j < len(cmd):
        ch = cmd[j]
        if ch == "'":
            return "".join(out), j + 1
        if ch == "\\" and j + 1 < len(cmd):
            dec = _ansi_escape(cmd, j + 1)
            if dec is not None:
                out.append(dec[0])
                j = dec[1]
                continue
            out.append(_ANSI_ESC.get(cmd[j + 1], "\\" + cmd[j + 1]))
            j += 2
            continue
        out.append(ch)
        j += 1
    return "".join(out), len(cmd)


def _unescaped_tick(cmd: str, i: int) -> int:
    """從 i 起第一個沒被跳脫的反引號位置(前面連續反斜線是偶數個),找不到回 -1。
    註解裡的 \\` 不是結尾(r3 單reviewer:拿它當結尾會提早收層,換行後的繞閘落進雙引號字面而漏問)。"""
    j = cmd.find("`", i)
    while j != -1:
        k = j
        while k > i and cmd[k - 1] == "\\":
            k -= 1
        if (j - k) % 2 == 0:
            return j
        j = cmd.find("`", j + 1)
    return -1


def _comment_end(cmd: str, i: int, in_tick: bool) -> int:
    """位置 i 的 # 註解吃到哪裡(回下一個要讀的位置)。反引號層裡:bash 先找到結尾反引號才解析裡面,
    註解吃不到它(r2 單reviewer);換行只找到結尾反引號為止,不然每個註解都掃到尾。"""
    t = _unescaped_tick(cmd, i) if in_tick else -1
    k = cmd.find("\n", i, t) if t != -1 else cmd.find("\n", i)
    if k == -1:
        k = t
    return len(cmd) if k == -1 else k


def _mask(ch: str) -> str:
    k = _MASK_CHARS.find(ch)
    return chr(_MASK_BASE + k) if k >= 0 and ch else ch


def _has_mask_range(text: str) -> bool:
    return any(_MASK_BASE <= ord(c) < _MASK_BASE + len(_MASK_CHARS) for c in text)


def _unmask(tok: str) -> str:
    """遮罩字元還原成原字;被保護的 `$` 還原成 _LIT_DOLLAR(不會被當成變數展開)。"""
    if not _has_mask_range(tok):
        return tok
    return "".join(_MASK_CHARS[ord(c) - _MASK_BASE] if _MASK_BASE <= ord(c) < _MASK_BASE + len(_MASK_CHARS) else c
                   for c in tok).replace("$", _LIT_DOLLAR)


class _Normalizer:
    """一趟掃過指令:追蹤引號(`$(` 與雙引號裡的反引號各重開一層)、接起續行、拿掉註解與 heredoc 內文、引號裡與被跳脫的
    結構字元換成遮罩字元、ANSI 引號解出內容後當成引號裡的字。heredoc 找不到結束字就停止剝(寧可多問)。
    整趟是線性的;續行在這裡接(不另開一趟),才不會被註解或 heredoc 裡的撇號騙。
    雙引號裡的反引號一樣會執行(bash 實測 echo "`git status`"),原本跟其他字一起遮掉、裡面的繞閘看不到
    (2026-10-14 原生 /code-review 實跑 echo "`git commit --no-verify`" 回空清單)。現在跟 `$(` 同一套:開一層反引號層,
    裡面照引號外的規則走,遇到第一個沒被跳脫的反引號收掉(不論那時在不在內層引號裡,同 bash);反引號層沒有括號深度可數,
    層內的右括號只照字輸出、不收層。輸出保留成對反引號,交給 _split_cmdsubs 抽出另外判;層內被跳脫的反引號已遮罩,
    那邊用 find 找結尾不會誤切。層內註解只吃到下一個反引號為止。沒處理 bash 在反引號裡先把「反斜線接反斜線、反斜線接反引號」還原掉一個反斜線的那一步(引號外的反引號也一樣),
    屬有心改寫的範圍。"""

    def __init__(self, cmd: str):
        self.cmd = cmd
        self.out = []
        self.ctx = [[False, False, 0, False]]   # 每層:[在單引號裡, 在雙引號裡, 這層 `$(` 裡的括號深度, 是反引號層]
        self.pending = []
        self.heredoc_ok = True

    def run(self) -> str:
        i = 0
        while i < len(self.cmd):
            i = self.step(i)
        return "".join(self.out)

    def step(self, i: int) -> int:
        cur = self.ctx[-1]
        ch = self.cmd[i]
        if cur[3] and ch == "`":
            self.ctx.pop()                   # 反引號層:第一個沒被跳脫的反引號收層
            self.out.append(ch)
            return i + 1
        if cur[0]:
            return self._in_single(i, cur)
        if ch == "\\":
            return self._backslash(i, cur)
        if self.cmd.startswith("$(", i) and not self.cmd.startswith("$((", i):
            self.ctx.append([False, False, 0, False])
            self.out.append("$(")
            return i + 2
        if cur[1]:
            return self._in_double(i, cur, ch)
        return self._bare(i, cur, ch)

    def _backslash(self, i: int, cur) -> int:
        nxt = self.cmd[i + 1:i + 2]
        if nxt == "\n":
            return i + 2                     # 續行:bash 連反斜線帶換行一起拿掉
        self.out.append(_mask(nxt))          # 被跳脫的字元就是普通字(引號外與雙引號裡都一樣)
        return i + 2

    def _in_single(self, i: int, cur) -> int:
        ch = self.cmd[i]
        if ch == "'":
            cur[0] = False
            self.out.append(ch)
        else:
            self.out.append(_mask(ch))
        return i + 1

    def _in_double(self, i: int, cur, ch: str) -> int:
        if ch == '"':
            cur[1] = False
            self.out.append(ch)
        elif ch == "`":
            self.ctx.append([False, False, 0, True])
            self.out.append(ch)
        else:
            self.out.append(ch if ch == "$" else _mask(ch))    # 雙引號裡的 $ 照常展開("$D")
        return i + 1

    def _bare(self, i: int, cur, ch: str) -> int:
        special = self._bare_special(i, cur, ch)
        if special is not None:
            return special
        if ch == "'":
            cur[0] = True
        elif ch == '"':
            cur[1] = True
        self.out.append(ch)
        return i + 1

    def _bare_special(self, i: int, cur, ch: str):
        """引號外的結構:算式、ANSI 引號、括號層、註解、heredoc、換行剝內文;都不是回 None。"""
        cmd = self.cmd
        if cmd.startswith("$((", i):
            j = _skip_arith(cmd, i + 1)
            self.out.append(cmd[i:j])
            return j
        if cmd.startswith("((", i) and (i == 0 or cmd[i - 1] in " \t\n;&|("):
            j = _skip_arith(cmd, i)          # 算術命令 `(( 1<<EOF ))`:裡面的 << 是位移,不是 heredoc(r4 資安席)
            self.out.append(cmd[i:j])
            return j
        if cmd.startswith('$"', i):
            return i + 1                     # $"…"(語系翻譯字串)內容照雙引號看
        fd = _FD_REDIR.match(cmd, i) if (i == 0 or cmd[i - 1] in " \t\n;&|()") else None
        if fd:
            self.out.append(_FD_MARK + "".join(_mask(c) for c in fd.group(1)))
            return fd.end(1)                 # `2>`、`{fd}>` 的檔案代號:標記起來,切詞後連同導向剔除
        if cmd.startswith("$'", i):
            text, j = _ansi_decode(cmd, i)
            self.out.append("".join(_mask(c) for c in text) or "''")
            return j
        if ch in "()" and len(self.ctx) > 1:
            return self._paren(i, cur, ch)
        if ch == "#" and (i == 0 or cmd[i - 1] in " \t\n;&|()"):
            return _comment_end(cmd, i, cur[3])
        if self.heredoc_ok and cmd.startswith("<<", i) and not cmd.startswith("<<<", i) and (i == 0 or cmd[i - 1] != "<"):
            return self._heredoc_op(i)
        if ch == "\n" and self.pending:
            return self._drop_bodies(i)
        return None

    def _paren(self, i: int, cur, ch: str) -> int:
        if ch == "(":
            cur[2] += 1
        elif cur[2] == 0:
            if not cur[3]:                   # 反引號層不靠括號收
                self.ctx.pop()
        else:
            cur[2] -= 1
        self.out.append(ch)
        return i + 1

    def _heredoc_op(self, i: int):
        dash = self.cmd.startswith("<<-", i)
        word, k = _read_delim(self.cmd, i + 2 + int(dash))
        if not word:
            return None
        self.pending.append((word, dash))
        self.out.append(self.cmd[i:k])
        return k

    def _drop_bodies(self, i: int) -> int:
        self.out.append("\n")
        pos = i + 1
        for word, dash in self.pending:
            end = _find_terminator(self.cmd, pos, word, dash)
            if end is None:
                self.heredoc_ok = False      # 找不到結束字:這個與之後都不剝,也不再找(避免每行重掃到尾)
                break
            pos = end
        self.pending = []
        return pos


def _paren_pairs(text: str) -> dict:
    """一次掃完,回 {左括號位置: 配對的右括號位置}(引號裡的括號已遮罩,直接數;線性時間)。"""
    pairs, stack = {}, []
    for j, ch in enumerate(text):
        if ch == "(":
            stack.append(j)
        elif ch == ")" and stack:
            pairs[stack.pop()] = j
    return pairs


def _split_cmdsubs(text: str):
    """$(…)、反引號、程序替換 <(…)、>(…) 換成判不出的佔位詞,裡面的指令抽出來另外判;$((…)) 算式只換掉。
    回 (外層文字, [每一層裡面的指令文字…]);找不到配對的保留原樣。一趟掃完、巢狀也一次拆開
    (逐層重掃在三千層巢狀下要好幾秒,r4 修補後的效能檢查)。反引號裡的內容原樣交回,由呼叫端再拆。"""
    pairs = _paren_pairs(text)
    layers, ends, inner, i, n = [[]], [], [], 0, len(text)
    while i < n:
        if ends and i == ends[-1]:
            ends.pop()
            body = "".join(layers.pop())
            if body.strip():
                inner.append(body)
            i += 1
            continue
        nxt = _cmdsub_at(text, i, pairs)
        if nxt is None:
            layers[-1].append(text[i])
            i += 1
            continue
        kind, end = nxt
        _placeholder(layers[-1])
        if kind == "open":
            layers.append([])
            ends.append(end)
            i += 2
        else:
            if kind == "tick" and text[i + 1:end - 1].strip():
                inner.append(text[i + 1:end - 1])
            i = end
    while len(layers) > 1:              # 理論上不會發生(配對表保證會關);保守起見併回外層
        layers[-2].extend(layers.pop())
    return "".join(layers[0]), inner


def _cmdsub_at(text: str, i: int, pairs: dict):
    """位置 i 是不是替換的開頭:回 ("open", 右括號位置)、("arith"/"tick", 結尾之後的位置),都不是回 None。"""
    if text.startswith("$((", i) and (i + 1) in pairs:
        return "arith", pairs[i + 1] + 1
    if text.startswith(("$(", "<(", ">("), i) and (i + 1) in pairs:
        return "open", pairs[i + 1]
    if text[i] == "`":
        close = text.find("`", i + 1)
        if close != -1:
            return "tick", close + 1
    return None


def _placeholder(out: list):
    if not (out and out[-1] == "__LUMOS_CMDSUB__"):
        out.append("__LUMOS_CMDSUB__")   # 相鄰的替換併成一個佔位詞,不拼出超長的詞


class _Sep(str):
    """切詞時就認定的分隔符(`;`、`&&`、`|`、換行、括號…)。引號裡還原回來的同樣字元是一般 str,不會被當成分隔。
    這個 repo 沒有同形先例;用 str 子類別是為了讓「是不是結構」在切詞當下定下來,之後不再看字面猜。"""


class _Redir(str):
    """切詞時就認定的導向運算子(`>`、`>>`、`&>`、`2>&1` 的 `>&`…);引號裡的 `>` 不會變成這個。"""


def _tokens(text: str):
    lex = shlex.shlex(text, posix=True, punctuation_chars="();<>|&\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    lex.commenters = ""
    out = []
    for t in lex:
        if _is_sep(t):
            out.append(_Sep(t))
        elif _is_redirect(t):
            out.append(_Redir(t))
        elif t and all(c in "();<>|&\n" for c in t):
            k = min(t.index(c) for c in "<>" if c in t)   # `)>`、`;>`:前面是分隔、後面是導向
            if t[:k]:
                out.append(_Sep(t[:k]))
            out.append(_Redir(t[k:]))
        else:
            out.append(_unmask(t))
    return out


def _is_sep(tok: str) -> bool:
    return bool(tok) and all(c in "();|&\n" for c in tok)


def _is_redirect(tok: str) -> bool:
    return bool(tok) and all(c in "<>&|" for c in tok) and any(c in "<>" for c in tok)


def _strip_redirects(words):
    """拿掉導向:運算子、它的目標,以及運算子前面的檔案代號(前處理標記過的 `2>` 的 2)。"""
    out, skip = [], False
    for w in words:
        if skip:
            skip = False
            continue
        if isinstance(w, _Redir):
            skip = True
            continue
        if w.startswith(_FD_MARK):
            continue                         # 檔案代號(前處理就標好,不靠「是不是數字」猜:`-m 1 >x` 的 1 是參數)
        out.append(w)
    return out


# ── 目錄與變數 ──────────────────────────────────────────────────────

def _expand(word: str, variables: dict):
    """展開同一條指令裡先賦值的變數;判不出(含指令替換、~、沒賦值過的變數)回 _UNKNOWN。"""
    if word.startswith("~") or "__LUMOS_CMDSUB_" in word:
        return _UNKNOWN
    names = re.findall(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)", word)
    if any(not isinstance(variables.get(a or b), str) for a, b in names):
        return _UNKNOWN
    if len(word) + sum(len(variables[a or b]) for a, b in names) > MAX_EXPAND:
        return _UNKNOWN              # `A=$A$A` 連續翻倍會指數膨脹(r3 併發資源席實測三十幾次吃掉十幾 GB)
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)",
                  lambda m: variables[m.group(1) or m.group(2)], word)


def _join(base, rel):
    """接路徑但不做純文字化簡:`連結/..` 在 git -C 與作業系統是先進連結再往上一層,文字化簡會走錯地方
    (r3 資安席);要比較時一律交給 realpath。"""
    if rel is _UNKNOWN:
        return rel
    if rel.startswith("/"):
        return rel
    if isinstance(base, str):
        return os.path.join(base, rel)
    return _UNKNOWN


_GIT_STATE = {"calls": 0, "cache": {}, "dead": False}
_IN_HOOK = {"on": False}


def _restart_budget():
    """重新起算預算。逐字複本區塊的 `_BUDGET_START` 只有這裡會從外面改(進場、或不是掛鉤進場的每次判斷);
    複本區塊改名這個變數時,測試「不是掛鉤進場時每次判斷重新起算預算」會紅。"""
    global _BUDGET_START
    _BUDGET_START = None


def _git_out(d: str, *args):
    """在 d 跑 git;回 (rc, stdout, stderr)。逾時、起不來、這次判斷已跑滿 MAX_GIT_CALLS 次、或先前已逾時回 (None, "", "")。
    同樣的查詢只跑一次;逾時用共用的 _inner_budget(從進場算起)。"""
    key = (d, *args)
    if key in _GIT_STATE["cache"]:
        return _GIT_STATE["cache"][key]
    if _GIT_STATE["calls"] >= MAX_GIT_CALLS or _GIT_STATE["dead"]:
        return None, "", ""
    budget = _inner_budget(default=5.0)
    if budget <= _BUDGET_FLOOR:
        _GIT_STATE["dead"] = True    # 預算已用到下限(例如找 repo 根就花掉大半):不再跑,下限 1 秒會讓每次 git 都還能等滿(r4 併發資源席)
        return None, "", ""
    _GIT_STATE["calls"] += 1
    try:
        r = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True, timeout=budget)
        res = (r.returncode, r.stdout.strip(), r.stderr)
    except Exception:
        _GIT_STATE["dead"] = True    # 逾時或起不來:這次判斷不再跑 git(git 卡住時每次都等滿會撐破外層預算)
        res = (None, "", "")
    _GIT_STATE["cache"][key] = res
    return res


def _existing_temp_dir(eff) -> bool:
    return isinstance(eff, str) and os.path.isdir(eff) and _under_temp(eff)


def _not_real_repo(eff) -> bool:
    """生效目錄確定不是真 repo(拋棄式):判斷當下就存在、在暫存根底下(解開符號連結後),
    而且共用 git 目錄也在暫存根底下;或 git 明說它不在任何 repo 裡。不靠同一條指令裡的推論
    (同指令建的目錄、mktemp、remote add 都不算——兩輪審查都在這類推論上找到繞法,計劃 d3)。"""
    if not _existing_temp_dir(eff):
        return False
    rc, out, err = _git_out(eff, "rev-parse", "--git-common-dir")
    if rc != 0:
        return rc is not None and "not a git repository" in err.lower()
    if not _under_temp(os.path.join(eff, out)):
        return False
    rc, urls, _err = _git_out(eff, "config", "--get-regexp", r"^remote\..*\.(url|pushurl)$")
    if rc is None or rc not in (0, 1):
        return False
    # 有網路遠端的就不是實驗 repo(暫存目錄裡的真工作副本,r3 通才席)
    return all(_local_url(line.split(" ", 1)[-1]) is not None for line in urls.splitlines() if line.strip())


def _local_url(url: str):
    """遠端位址是明確的本機路徑(/、./、../、file://)就回路徑,否則回 None(`host:path` 這種一律當網路位址)。"""
    if url.startswith("file://"):
        return url[len("file://"):]
    return url if url.startswith(("/", "./", "../")) else None


def _push_remote_arg(args):
    """push 的目的地:有 `--repo`(含縮寫 `--rep`)就是它的值(這時位置參數是 refspec),否則第一個位置參數;
    吃值選項(含縮寫)的值不算位置參數;沒有回 None。"""
    for k, a in enumerate(args):
        name, eq, val = a.partition("=")
        if name in ("--rep", "--repo"):
            return val if eq else (args[k + 1] if k + 1 < len(args) else None)
    skip = False
    for a in args:
        if skip:
            skip = False
        elif a == "-o" or _long_takes_value(a, _PUSH_VALUE_LONG):
            skip = True
        elif not a.startswith("-"):
            return a
    return None


def _temp_target(eff, path: str) -> bool:
    p = _join(eff, path)
    return isinstance(p, str) and os.path.exists(p) and _under_temp(p)


def _push_target_temp(eff, args) -> bool:
    """push 的目標確定在暫存根底下才算拋棄式:路徑參數要在判斷當下存在;遠端名稱要在已存在的暫存目錄裡、
    用 `git remote get-url --push` 查到明確的本機路徑。沒寫遠端、查不到、網路位址都不算。"""
    remote = _push_remote_arg(args)
    if remote is None:
        return False
    local = _local_url(remote)
    if local is not None:
        return _temp_target(eff, local)
    if not _existing_temp_dir(eff):
        return False
    rc, url, _err = _git_out(eff, "remote", "get-url", "--push", remote)
    local = _local_url(url) if rc == 0 and url else None
    return local is not None and _temp_target(eff, local)


# ── git 指令解析 ────────────────────────────────────────────────────

def _short_flags_n(flags: str):
    """commit 的一組短旗標(不含開頭 -):回 (有沒有 n, 下一個詞是不是這組旗標吃的值)。"""
    for idx, ch in enumerate(flags):
        if ch == "n":
            return True, False
        if ch in "mFCct":
            return False, idx == len(flags) - 1
        if ch in "Su":
            return False, False
    return False, False


def _long_takes_value(a: str, longs) -> bool:
    """長選項(git 認唯一前綴縮寫,`--push-o` 就是 `--push-option`)要不要吃下一個詞當值(r4 資安席)。"""
    return a.startswith("--") and "=" not in a and len(a) > 3 and any(o.startswith(a) for o in longs)


def _opt_words(sub, args):
    """選項位置上的詞:吃值選項的值、`--` 之後的詞都不算(`-m --no-verify` 的 --no-verify 是訊息,r4 合約圖譜席)。"""
    longs = _COMMIT_VALUE_LONG if sub == "commit" else _PUSH_VALUE_LONG
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "--":
            break
        if not a.startswith("-") or a == "-":
            continue
        out.append(a)
        if a.startswith("--"):
            skip = _long_takes_value(a, longs)
        elif sub == "commit":
            skip = _short_flags_n(a[1:])[1]
        else:
            skip = a == "-o"
    return out


def _commit_short_n(args) -> bool:
    return any(_short_flags_n(a[1:])[0] for a in _opt_words("commit", args) if not a.startswith("--"))


def _config_split(args):
    """config 參數拆成 (旗標集合, 位置參數清單)。"""
    flags, pos, skip = set(), [], False
    for a in args:
        if skip:
            skip = False
        elif a in _CONFIG_VALUE_OPTS:
            flags.add(a)
            skip = True
        elif a.startswith("-") and a != "-":
            flags.add(a.split("=", 1)[0])
        else:
            pos.append(a)
    return flags, pos


def _hooks_key(key: str) -> bool:
    """會換掉掛鉤目錄的設定鍵:core.hooksPath,以及引入別的設定檔(include.path、includeIf.*.path,r4 資安席)。"""
    k = key.lower()
    return k == "core.hookspath" or k == "include.path" or (k.startswith("includeif.") and k.endswith(".path"))


def _config_writes_hookspath(args) -> bool:
    flags, pos = _config_split(args)
    if flags & _CONFIG_SECTION_FLAGS:
        return bool(pos) and pos[0].lower() == "core"     # 拆掉或改名整個 core 區段,hooksPath 跟著沒了
    if pos and pos[0] in ("set", "unset"):
        return len(pos) >= 2 and _hooks_key(pos[1])
    if pos and pos[0] in ("remove-section", "rename-section"):
        return len(pos) >= 2 and pos[1].lower() == "core"
    if not pos or not _hooks_key(pos[0]):
        return False
    if flags & _CONFIG_WRITE_FLAGS:
        return True
    if flags & _CONFIG_READ_FLAGS:
        return False
    return len(pos) >= 2


def _parse_git(words, gi):
    """words[gi] 是 git(或 git-commit 這類子指令執行檔);回 (子指令, 參數, -C 目錄們, 設定鍵們,
    有沒有 --git-dir/--work-tree);沒有子指令回 None。"""
    name = os.path.basename(words[gi])
    if name != "git":
        return name[len("git-"):], words[gi + 1:], [], [], False     # 直接叫 git-commit:沒有全域選項(r4 資安席)
    j, gdirs, cfgs, moved, n = gi + 1, [], [], False, len(words)
    while j < n and words[j].startswith("-"):
        w = words[j]
        name, eq, val = w.partition("=")
        if name in _GIT_DIR_OPTS:
            moved = True
        if name == "--config-env" and eq:
            cfgs.append(val)
        if w in _GIT_VALUE_OPTS and j + 1 < n:
            if w in ("-c", "--config-env"):
                cfgs.append(words[j + 1])
            elif w == "-C":
                gdirs.append(words[j + 1])
            j += 1
        j += 1
    if j >= n:
        return None
    return words[j], words[j + 1:], gdirs, cfgs, moved


def _cfg_text_hooks(text: str) -> bool:
    """一段設定文字(GIT_CONFIG_KEY_n 的值、GIT_CONFIG_PARAMETERS)裡有沒有會換掉掛鉤目錄的鍵。"""
    low = text.lower()
    return "core.hookspath" in low or "include.path" in low or "includeif." in low


def _env_cfg_hookspath(words) -> bool:
    """GIT_CONFIG_KEY_n= 或 GIT_CONFIG_PARAMETERS= 帶會換掉掛鉤目錄的鍵。"""
    return any(_cfg_text_hooks(v) for v in _env_cfg_values(words))


def _hit_codes(sub, args, cfgs, skip):
    """這條 git 指令命中哪些繞閘形狀(還沒扣拋棄式)。"""
    hits = []
    if sub in _GATED_SUBS and any(a.startswith("--no-veri") and "--no-verify".startswith(a) for a in _opt_words(sub, args)):
        hits.append("no-verify")
    if sub == "commit" and _commit_short_n(args):
        hits.append("commit-n")
    if sub in _GATED_SUBS and any(_hooks_key(c.split("=", 1)[0]) for c in cfgs):
        hits.append("c-hookspath")
    if sub == "config" and _config_writes_hookspath(args):
        hits.append("config-hookspath")
    if sub in _GATED_SUBS and skip:
        hits.append("lumos-skip")
    return hits


def _exempt(sub, eff, args, remotes_dirty=False, gitdir_seen=False) -> bool:
    """命中算不算拋棄式:push 看推送目標(同一條指令前面動過遠端設定就不算——判斷當下查到的是改之前的位址);
    commit 與只寫 repo 本身的 config 看是不是實驗 repo;寫使用者或系統層設定的 config 一律不算。"""
    if sub == "push":
        return not remotes_dirty and not gitdir_seen and _push_target_temp(eff, args)
    if sub == "config":
        flags, _ = _config_split(args)
        return not (flags & _CONFIG_GLOBAL_FLAGS) and _not_real_repo(eff)
    if sub == "commit":
        return _not_real_repo(eff)
    return False


def _prefix_assigns(seg, i, upto):
    """這一段在位置 upto 之前、以「指令前綴」身分出現的賦值:段首的,與 env 後面的(跳過 env 的選項與
    `-u 名稱`、`-C 目錄` 這類選項的值,r4 正確性席)。當成一般參數出現的(`grep X=1 檔`)不算。"""
    out = [w for w in seg[:i] if _ASSIGN.match(w)]
    for k in range(i, upto):
        if os.path.basename(seg[k]) != "env":
            continue
        j = k + 1
        while j < upto and (seg[j].startswith("-") or _ASSIGN.match(seg[j])):
            if _ASSIGN.match(seg[j]):
                out.append(seg[j])
            j += 2 if seg[j] in _ENV_VALUE_OPTS else 1
    return out


def _prefix_skip(seg, i, upto) -> bool:
    return any(_SKIP_ASSIGN.match(w) for w in _prefix_assigns(seg, i, upto))


class _Walker:
    """逐段走過切好的詞:追蹤 cd 目錄(子殼層、背景、管線各自隔開,條件式 cd 只在緊接 && 時算數)、
    變數、export,收集命中代號。任何地方設過 GIT_DIR 這一族或用了 --git-dir/--work-tree,整條都不給拋棄式豁免。"""

    def __init__(self, cwd):
        start = os.path.normpath(cwd) if isinstance(cwd, str) and cwd.startswith("/") else _UNKNOWN
        self.stack = [start]
        self.variables = {}
        self.exported_skip = False
        self.exported_cfg = False
        self.gitdir_seen = False
        self.remotes_dirty = False
        self.exported_remote = False
        self.cond_pending = False
        self.brace_stack = []           # 每個開著的大括號群組:[進群組前的目錄, 群組裡有沒有改過目錄]
        self.brace_close = None
        self.compound = []              # 每個開著的 if/for/while/until/case/select:裡面有沒有改過目錄
        self.seg_conditional = False
        self.found = []

    def run(self, toks):
        seg, prev = [], ""
        for t in toks:
            if not isinstance(t, _Sep):
                seg.append(t)
                continue
            self._finish(seg, prev, t)
            seg, prev = [], t
        self._finish(seg, prev, "")
        return list(dict.fromkeys(self.found))

    def _finish(self, seg, prev, nxt):
        """跑完一段,再依前後的分隔符決定這段的 cd 算不算數,最後處理括號層。"""
        before = self.stack[-1]
        self.seg_conditional = False
        changed = self.segment(seg)
        p, q = _sep_core(prev), _sep_core(nxt)
        bg = _is_pipe(q) or (q.startswith("&") and not q.startswith("&&"))
        if changed:
            self._scope_cd(before, p, q, bg)
        if self.brace_close is not None:
            before_group, moved = self.brace_close
            if bg:
                self.stack[-1] = before_group      # `{ cd X; } | cat`、`{ …; } &`:群組在子殼層跑
            elif moved:
                self.stack[-1] = _UNKNOWN          # 群組可能是函式本體(`f() { cd X; }`)沒有真的跑,r4 正確性席
            self.brace_close = None
        if self.cond_pending and q and not q.startswith("&&"):
            self.stack[-1] = _UNKNOWN        # && 鏈結束後,不知道條件式 cd 有沒有跑
            self.cond_pending = False
        for c in nxt:
            if c == "(":
                self.stack.append(self.stack[-1])
            elif c == ")" and len(self.stack) > 1:
                self.stack.pop()

    def _scope_cd(self, before, p, q, bg):
        """這一段改了目錄:依前後分隔符決定改動算不算數。`&&`、`||` 後面接換行仍是同一條鏈(r4 正確性席)。"""
        p = p.rstrip(";")
        if self.compound:
            self.compound[-1] = True     # 結構結束時才知道這段有沒有跑,見 _compound
        if self.brace_stack:
            self.brace_stack[-1][1] = True
        if _is_pipe(p) or bg:
            self.stack[-1] = before          # 管線與背景執行的段在子殼層跑,cd 不影響後面
        elif self.seg_conditional or p.endswith("||") or q.startswith("||"):
            self.stack[-1] = _UNKNOWN        # if/while 條件裡、|| 兩側的 cd:跑沒跑到判不出
        elif p.endswith("&&"):
            if q.startswith("&&"):
                self.cond_pending = True     # && 之後的 cd 再緊接 &&:這條 && 鏈裡 cd 一定跑過
            else:
                self.stack[-1] = _UNKNOWN

    def _assign(self, w):
        name, val = w.split("=", 1)
        name = name.rstrip("+")
        self.variables[name] = _expand(val, self.variables)
        return name

    def segment(self, seg) -> bool:
        """處理一段;回這段有沒有改變目前目錄(cd、pushd、popd)。"""
        seg = _strip_redirects(seg)
        self._note_braces(seg)
        i = 0
        while i < len(seg) and (seg[i] in _KEYWORDS or _ASSIGN.match(seg[i])):
            i += 1
        self._compound(seg, i)
        if any(_GITDIR_ASSIGN.match(w) for w in _prefix_assigns(seg, i, len(seg))):
            self.gitdir_seen = True  # 只認指令前綴與 env 後面的賦值;`echo GIT_DIR=x` 不算(r4 邊界輸入席)
        if i >= len(seg):            # 只有賦值:設 shell 變數(沒有 export,子程序看不到)
            for w in seg:
                if _ASSIGN.match(w):
                    self._assign(w)
            return False
        cmd = os.path.basename(seg[i])
        if cmd in ("cd", "pushd", "popd"):
            self._dir_change(cmd, seg, i)
            return True
        builtin = {"export": self._export, "declare": self._declare, "typeset": self._declare}.get(cmd)
        if builtin:
            builtin(seg[i + 1:])
        else:
            self._command(seg, i)
        return False

    def _note_braces(self, seg):
        """大括號群組的開合。"""
        if seg and seg[0] == "{":
            self.brace_stack.append([self.stack[-1], False])
        if seg and seg[0] == "}":
            self.brace_close = self.brace_stack.pop() if self.brace_stack else None

    def _compound(self, seg, i):
        """if/for/while/until/case/select 的開合:本體或分支裡改過目錄的,結構結束後目錄判不出——
        條件不成立、迴圈零次、分支沒中時那個 cd 沒跑(r4 正確性席、邊界輸入席)。結構裡面照常追蹤。"""
        words = seg[:i] + ([os.path.basename(seg[i])] if i < len(seg) else [])
        for w in words:
            if w in _COMPOUND_OPEN:
                self.compound.append(False)
            elif w in _COMPOUND_CLOSE and self.compound:
                if self.compound.pop():
                    self.stack[-1] = _UNKNOWN
                    if self.compound:
                        self.compound[-1] = True

    def _dir_change(self, cmd, seg, i):
        if cmd == "cd":
            self._cd(seg[i + 1:])
            self.seg_conditional = any(w in ("if", "elif", "while", "until", "!") for w in seg[:i])
        else:
            self.stack[-1] = _UNKNOWN

    def _cd(self, rest):
        rest = [a for a in rest if not (a.startswith("-") and a != "-")]
        if not rest or rest[0] == "-":
            self.stack[-1] = _UNKNOWN
        else:
            self.stack[-1] = _join(self.stack[-1], _expand(rest[0], self.variables))

    def _mark_exported(self, name):
        if name.startswith("LUMOS_SKIP_"):
            self.exported_skip = True
        val = str(self.variables.get(name, "")).lower()
        if name.startswith("GIT_CONFIG_") and _cfg_text_hooks(val):
            self.exported_cfg = True
        if name.startswith("GIT_CONFIG_") and ("remote." in val or "url." in val):
            self.exported_remote = True
        if _GITDIR_NAME.match(name):
            self.gitdir_seen = True

    def _export_names(self, rest):
        for w in rest:
            if _ASSIGN.match(w):
                self._mark_exported(self._assign(w))
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", w) and w in self.variables:
                self._mark_exported(w)

    def _export(self, rest):
        if "-n" in rest:
            return                   # export -n:取消匯出
        self._export_names(rest)

    def _declare(self, rest):
        if any(a.startswith("-") and "x" in a for a in rest):
            self._export_names(rest)

    def _command(self, seg, i):
        """一般指令:段裡的 lumos 指令前以前綴身分帶 LUMOS_SKIP_*、或段裡第一個 git 詞開始的 git 指令。"""
        lk = next((k for k in range(i, len(seg)) if os.path.basename(seg[k]) == "lumos"), None)
        if lk is not None and (self.exported_skip or _prefix_skip(seg, i, lk)):
            self.found.append("lumos-skip")
        gi = next((k for k in range(i, len(seg)) if _GIT_EXE.match(os.path.basename(seg[k]))), None)
        if gi is not None:
            self._git(seg, i, gi)

    def _git(self, seg, i, gi):
        parsed = _parse_git(seg, gi)
        if parsed is None:
            return
        sub, args, gdirs, cfgs, moved = parsed
        eff = self.stack[-1]
        for d in gdirs:
            eff = _join(eff, _expand(d, self.variables))
        if moved:
            self.gitdir_seen = True
        if self.gitdir_seen:
            eff = _UNKNOWN           # 動的不一定是生效目錄那個 repo
        if self.exported_cfg or _env_cfg_hookspath(seg[:gi]):
            cfgs = [*cfgs, "core.hooksPath"]
        env_vals = _env_cfg_values(seg[:gi])
        if _cfg_touches_remotes(cfgs) or any("remote." in v.lower() or "url." in v.lower() for v in env_vals):
            self.remotes_dirty = True    # `-c remote.*.pushurl=`、`GIT_CONFIG_KEY_n=url.*` 這次就改了推送位址
        skip = self.exported_skip or _prefix_skip(seg, i, gi)
        for code in _hit_codes(sub, args, cfgs, skip):
            if not _exempt(sub, eff, args, self.remotes_dirty or self.exported_remote, self.gitdir_seen):
                self.found.append(code)
        if _changes_remotes(sub, args):
            self.remotes_dirty = True


def _changes_remotes(sub, args) -> bool:
    """這條 git 指令會不會改到推送位址:`git remote` 的寫入子指令,或 `git config` 碰到 remote.* / url.* 的鍵。"""
    if sub == "remote":
        rest = [a for a in args if a not in ("-v", "--verbose", "-vv")]
        return bool(rest) and rest[0] in _REMOTE_WRITES     # prune、update、show 不改位址(r4 規格符合席)
    if sub == "config":
        flags, pos = _config_split(args)
        if flags & _CONFIG_READ_FLAGS:
            return False
        if pos and pos[0] in ("set", "unset", "remove-section", "rename-section"):
            pos = pos[1:]
            return bool(pos) and pos[0].lower().startswith(("remote", "url"))
        if not pos or not pos[0].lower().startswith(("remote.", "url.")):
            return bool(flags & _CONFIG_SECTION_FLAGS) and bool(pos) and pos[0].lower().startswith(("remote", "url"))
        return bool(flags & _CONFIG_WRITE_FLAGS) or len(pos) >= 2
    return False


def _cfg_touches_remotes(keys) -> bool:
    return any(str(k).lower().startswith(("remote.", "url.")) for k in keys)


def _env_cfg_values(words):
    """同段 git 之前的 GIT_CONFIG_KEY_n= 與 GIT_CONFIG_PARAMETERS= 的值。"""
    return [m.group(2) for m in (_CFG_ENV_ASSIGN.match(w) for w in words) if m]


def _sep_core(sep: str) -> str:
    """分隔符的語意核心:換行等同 `;`(`a && b⏎c` 的換行跟分號一樣會結束 && 鏈)。"""
    core = sep.replace("\n", ";")
    if not core.strip(";"):
        return ";" if core else ""
    return core


def _is_pipe(sep: str) -> bool:
    return (sep.startswith("|") and not sep.startswith("||")) or (sep.endswith("|") and not sep.endswith("||")) or "|&" in sep


def bypass_reasons(command: str, cwd) -> list:
    """回這條指令的命中代號清單(去重、保序);空清單=放行。"""
    _GIT_STATE["calls"] = 0
    _GIT_STATE["cache"] = {}
    _GIT_STATE["dead"] = False
    if not _IN_HOOK["on"]:
        _restart_budget()            # 不是掛鉤進場(例如拿事件帳批次重跑):每次判斷重新起算預算
    if len(command) > MAX_LEN:
        return _literal(command)      # 太長:只看字面
    text, pending = _split_cmdsubs(_Normalizer(command).run())
    try:
        found = _Walker(cwd).run(_tokens(text))
        while pending:               # 替換裡的指令另外判;目錄當判不出,不給拋棄式豁免(r4 資安席、邊界輸入席)
            outer, more = _split_cmdsubs(pending.pop())
            found += _Walker(None).run(_tokens(outer))
            pending += more
    except ValueError:
        return _literal(command)
    return list(dict.fromkeys(found))


def _literal(command: str) -> list:
    """切不動或太長時只看字面:有 git 或 lumos,而且看起來在跳過閘(--no-verify、改掛鉤目錄、LUMOS_SKIP、提交 -n)就問。"""
    low = command.lower()
    if "git" not in low and "lumos" not in low:
        return []
    return ["literal"] if _looks_bypass(command) else []


def _reason_text(codes) -> str:
    what = ";".join(_REASON_TEXT.get(c, c) for c in codes)
    return ("發生什麼:這條指令會跳過 Lumos 的閘(" + what + ")。\n"
            "為什麼在意:閘被跳過就沒人檢查這次推送或提交;代理被擋時順手繞過是已知模式。\n"
            "怎麼做:確定要跳過就按允許;不確定就拒絕,讓代理改成修好被擋的原因。")


def decide(event):
    """回要印的 JSON 物件,或 None(放行)。內部例外一律放行並 mark error。"""
    try:
        if not isinstance(event, dict):
            return None
        ti = event.get("tool_input")
        if not isinstance(ti, dict):
            return None
        cmd = ti.get("command")
        if not isinstance(cmd, str) or not cmd:
            return None
        cwd = event.get("cwd")
        codes = bypass_reasons(cmd, cwd if isinstance(cwd, str) else None)
    except Exception as e:
        mark("error", type(e).__name__ + ":" + str(e)[:120])
        return None
    if not codes:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                   "permissionDecisionReason": _reason_text(codes)}}


def main(raw: str) -> int:
    out = decide(json.loads(raw))
    if out:
        print(json.dumps(out, ensure_ascii=False))
    return 0


def entry(stdin_bytes: bytes) -> int:
    """掛鉤進入點。跟鄰居掛鉤不同:讀 stdin 與預篩放在 guard 之外——guard 每次都跑 git 並寫存活事件,
    每條 Bash 都進 guard 會擠掉其他掛鉤的存活紀錄(計劃〈做法〉、Systems/代理繞閘問人 的 PITFALL)。
    共用模組在模組頂層載入(鄰居在 `__main__` 裡載),因為 `decide` 的 `mark` 在測試直接呼叫時也要有。"""
    _IN_HOOK["on"] = True
    _restart_budget()
    _inner_budget(default=5.0)       # 預算從進場就開始算,不是從第一次跑 git 才算
    try:
        return _entry_body(stdin_bytes)
    finally:
        _IN_HOOK["on"] = False       # 同一個行程之後的批次判斷不繼承這次進場的預算起點(r4 併發資源席)


def _entry_body(stdin_bytes: bytes) -> int:
    try:
        raw = stdin_bytes.decode("utf-8", "replace")
        go = prefilter(raw)
    except Exception:
        return 0
    if not go:
        return 0
    if _guard:
        return _guard("pretooluse-bypass-ask-hook", __file__, lambda: main(raw), swallow=True)
    try:
        return main(raw)
    except Exception:
        return 0


if __name__ == "__main__":
    try:
        _stdin = sys.stdin.buffer.read()
    except Exception:
        sys.exit(0)
    sys.exit(entry(_stdin))
