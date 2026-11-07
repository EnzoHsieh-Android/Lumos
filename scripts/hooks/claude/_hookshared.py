#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# MIT licensed. Full text: scripts/lumos header, or LICENSE at
# https://github.com/EnzoHsieh-Android/Lumos
"""鉤子共用程式:收工點名(check-graph-sync.py)與收工寫法檢查(stop-lint-hook.py)兩支共用的那幾段。

★哪些放這裡、哪些不放★(單源 [[Systems/hook信任邊界]]〈2026-09-08 訂正〉:先問「這段東西漏帶的後果是什麼」):
- 放這裡的是漏帶只會「功能退化」的:家目錄底下的標記目錄、標記檔名消毒與 O_EXCL 佔名額、檔名消毒、git 防護設定。
  共用模組的代價是「安裝時漏帶」,靠兩道守衛盯:t_installed_hooks_bring_their_local_imports(在複製清單 _GLOBAL_CLAUDE_HOOKS)
  與錨點清單(ANCHOR_FILES);漏帶時兩支鉤子都整支靜默放行,不會執行不該執行的東西。
- ★不放這裡★的是跟安全邊界綁在一起的兩段:可信來源解析(決定執行哪一份 lumos)與逾時預算。它們在每支鉤子裡是逐字複本,
  由逐字比對的守衛盯著不准漂(回合結束檢查代碼審 r1 架構對齊席 F1、合約席 F1:這兩段曾搬進來,守衛跟著放寬到擋不住
  「換成從 PATH 找」,已搬回)。
- 匯入方式照先例 _hookevent.py:sys.path.insert 加 import;不用 importlib 去載另一支鉤子(那會連帶帶起它的模組層狀態)。

★只用標準庫、不做任何模組層 I/O★:收工寫法檢查那支在預篩沒過時根本不匯入這支(沒宣告 ast-grep 的專案每次收工只付 Python 啟動);
匯入成本見計劃實驗 E12。各段的出身與誠實邊界照原樣留在各自的註解裡(從 check-graph-sync.py 逐字搬來)。
"""
from __future__ import annotations
import os
import re
import sys
import time
from pathlib import Path

def _cache_dir_under_home(name: str, label: str) -> Path:
    """`<家目錄>/.cache/lumos/<name>`:mkdir(0700)後★先過 _stop_dir_ok 再做任何 chmod/清理★
    (code-codex-refine r2 外家:目錄若被換成指向別處的 symlink,之前會跟著 chmod 並刪掉目標裡
    超過 7 天的檔——現在 symlink/不是自己的/別人可寫 一律不碰,交給後面的 _stop_dir_ok 判不擋)。

    ★參數化而不是抄第二份★(2026-09-18 收工點名改問版本控制那一批):收工點名的去重紀錄
    需要自己的目錄(跟擋停標記混在一起會打破「只有擋過的 session 才留標記」這個性質),
    而這支檔已經因為「邏輯抄一份、一邊改另一邊沒跟上」吃過虧——所以共用同一套判準。"""
    d = Path.home() / ".cache" / "lumos" / name
    try:
        # ★逐層建、逐層檢查★(2026-09-16 補審 delta 那一輪):原本一次 mkdir 出整條路徑再檢查,
        # 上層被換成指向別處的連結時,★別人的目錄裡已經多出一個 stop-block 資料夾了★,
        # 檢查才說「不碰它」——跟上面那句「不在別人的目錄上寫標記」自己矛盾。
        # 主程式的 `_mkdir_trusted_under_home` 同一天改成這樣,這支 hook 是獨立檔不能 import,
        # ★所以邏輯抄一份、判準必須跟它對齊★(是真目錄、屬於自己、別人不可寫;任何一層不過就停手,
        # 已經建好的不回頭刪——刪反而是在動別人的東西)。
        if not _mkdir_under_home(".cache", "lumos", name):
            print(f"lumos {label}停用:{d} 這條路徑上有一層不是自己的真目錄"
                  "(被換成指向別處的連結、或別人也寫得進去)——不在那裡建東西。", file=sys.stderr)
            return d
        if not _stop_dir_ok(d):
            print(f"lumos {label}停用:標記目錄 {d} 不是自己的 0700 目錄(symlink / 別人可寫 / chmod 失敗)——修好權限才會再啟用", file=sys.stderr)   # r2 delta #3:靜默停用要有訊號(給 log,Codex 模型看不到)
            return d
        os.chmod(d, 0o700)
        now = time.time()   # lazy 清超過 7 天的標記(邊界 F5:註解與門檻要一致)
        for f in d.iterdir():
            try:
                if now - f.stat().st_mtime > 7 * 86400:   # 保留 7 天=「同 session 七天內只擋一次」的承諾
                    f.unlink()
            except OSError:
                pass
    except OSError:
        pass
    return d


def _mkdir_under_home(*segs) -> bool:
    """從家目錄往下逐層建、逐層檢查,全過才回 True。

    ★跟主程式 `_mkdir_trusted_under_home` 同一套判準★(2026-09-16):這支 hook 是獨立檔、
    不 import 主程式,所以邏輯抄一份;★判準有任何一邊改了,另一邊要跟著改★
    ——今天就是因為主程式改了、這裡沒跟上,兩份才不一致。

    每一段必須是一個單純的名字(路徑接合遇到絕對路徑會整個重置,`..` 也照走);
    每建一層就確認它是真目錄、屬於自己、別人不可寫;任何一層不過就停手,
    ★已經建好的不回頭刪★(刪反而是在動別人的東西)。

    ★誠實邊界★:路徑層檢查,擋不住同帳號搶跑(檢查完到下一層動作之間有時間差)。
    要真正關掉得改用 dirfd / O_NOFOLLOW 那一套;沒做的理由是能在你帳號下跑程式的人
    本來就能做任何事。**不得宣稱「換掉也擋得住」**。
    """
    import stat as _stat
    cur = Path.home()
    for seg in segs:
        if (not isinstance(seg, str) or not seg or seg in (".", "..")
                or "/" in seg or "\\" in seg or Path(seg).is_absolute()):
            return False
        cur = cur / seg
        try:
            cur.mkdir(exist_ok=True, mode=0o700)   # 不帶 parents:一層一層來才檢查得到每一層
        except FileExistsError:
            pass
        except OSError:
            return False
        try:
            if cur.is_symlink() or not cur.is_dir():
                return False
            st = cur.stat()
        except OSError:
            return False
        if hasattr(os, "getuid"):
            if st.st_uid != os.getuid():
                return False
            if st.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH):
                return False
    return True


def _stop_dir_ok(d: Path) -> bool:
    """標記目錄信任檢查(spec-conformance r1:跟 scripts/lumos 的 _lens_arm_dir_ok 同一套威脅模型):是目錄、owner 是自己、group/other 不可寫。
    不過關=不擋(寧可漏),不在別人的目錄上寫標記。

    ★誠實邊界(2026-09-16 補審 delta 那一輪:主程式那份有寫、這裡漏抄)★:這是路徑層檢查,
    擋不住同帳號搶跑——檢查完到真的寫標記檔之間有時間差,同 UID 的程序可以在那個縫裡把目錄換掉。
    要真正關掉得改用 dirfd / O_NOFOLLOW 那一套。**不得宣稱「換掉也擋得住」**。"""
    import stat as _stat
    try:
        if d.is_symlink():      # r2 外家:symlink 指到別處=別人的目錄,不信
            return False
        # r3 delta:父層(~/.cache 或 ~/.cache/lumos)是 symlink 也一樣——家目錄以下整條路徑不得經過 symlink
        # (家目錄本身可以是 symlink,macOS /var→/private/var 那種),所以拿「家目錄解析後 + 固定相對路徑」對照
        # ★名字不寫死★(2026-09-18 收工點名改問版本控制那一批):原本這裡寫死 "stop-block",
        # 於是同一個快取層底下新增任何目錄都永遠不過這關——去重紀錄就是這樣被靜默停用的。
        # 改成比對「家目錄解析後 + 固定的兩層 + 這個目錄自己的名字」,防連結繞路的意圖不變:
        # 解析後的路徑仍然必須落在 ~/.cache/lumos/<name>,中間經過任何連結都會對不上。
        if d.resolve() != (Path.home().resolve() / ".cache" / "lumos" / d.name):
            return False
        st = d.stat()
    except OSError:
        return False
    if not d.is_dir():
        return False
    if hasattr(os, "getuid"):
        if st.st_uid != os.getuid():
            return False
        if st.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH):
            return False
    return True


def _mark_name(s):
    """會談、回合編號、批次 → 標記檔名安全的字串;消毒後是空、"." 或 ".." 回 None(正確性席 F3:Path 語意會讓 "." 永遠「存在」而悄悄關掉擋停)。
    ★收工點名與收工寫法檢查共用這一份★(回合結束檢查代碼審 r1 架構對齊席 F2):兩邊的標記放在同一個 stop-block 目錄,
    消毒規則或長度上限一分家,同一個會談的標記檔名就對不上。"""
    n = re.sub(r"[^A-Za-z0-9_.-]", "_", str(s))[:120]
    return None if n in ("", ".", "..") else n


def _claim_mark(d: Path, name: str) -> bool:
    """在標記目錄 d 底下用 O_EXCL 原子建檔佔名額(兩個 hook 同時來只有一個成功);目錄不可信、名字不安全或任何 OSError 都回 False=不擋(寧可漏)。
    ★兩支鉤子共用這一份★(同上)。"""
    if not name or name in (".", "..") or any(ch in name for ch in "/\\\0") or not _stop_dir_ok(d):
        return False
    try:
        fd = os.open(str(d / name), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except OSError:
        return False
    try:
        os.write(fd, str(time.time()).encode("utf-8"))
    except OSError:
        pass          # 名額已佔(檔已建成),寫內容失敗不影響
    finally:
        os.close(fd)  # 正確性席 F2:fd 不漏
    return True


def _safe_path(p) -> str:
    """reason 會變成 Codex 的下一個 user prompt(r1 通才 F3):檔名來自工作樹,不信任 repo 的檔名不能夾帶換行/控制字元進提示。"""
    s = "".join(ch for ch in str(p) if ch.isprintable() and ch not in "\r\n")
    return s.replace("`", "'")[:160]   # r2 delta #2:反引號會跳出 code span,換成單引號


# ★被打開的資料夾不准指使我們執行指令★
# 版本控制有幾個設定項,它的值會被當成 shell 指令執行。這支 hook 是開啟資料夾就自動跑的,
# 而它查的就是「被打開的那個資料夾」——所以那些設定由攻擊者控制。
#
# ★為什麼是一份清單而不是逐個補★(同類問題冒出第三次之後換的形狀):
#   r1 資安席報了第一項 → 修法只補了自己新增的兩個呼叫點
#   r2 驗收席抓到漏補第三處(會去呼叫主程式那條)→ 改成注入環境變數涵蓋所有子行程
#   r2 資安複審又找到第二項設定 → 若繼續逐個補,下一輪還會有第三項
# 所以收成一份具名清單,新發現的往這裡加一行,並補一筆測試釘住它。
#
# ★誠實邊界,不得宣稱更多(這句話本身被審查打過臉一次)★:
#   這是★列舉法★,不是完備防護。清單上的擋得住,清單外的擋不住。
#   前一版註解寫過「主程式內部的呼叫也涵蓋得到(實測驗過)」——那句話只對當時清單上的那一項成立,
#   對後來發現的第二項是假的。**驗過的是哪幾項,就只能說哪幾項。**
#   沒列入的:別名、分頁器(r2 資安複審試過、不觸發)。★內容過濾器(clean、process)會觸發★——git status 遇到大小不變、
#   內容改過的檔會執行它(回合結束檢查代碼審 r3 資安席實測,推翻 r2 那句「塗抹指令不觸發」);它的名字由被打開的目錄決定、
#   這份清單列不到,所以不在這裡擋,改成找改動的那條路根本不跑 status(check-graph-sync.py 的 _wt_changed_nofilter)。
#   純 clone 不會把這些設定帶過來(實測);真正的交付路徑是「直接拿到別人的整個目錄」。
#   這支 hook 以外的地方(提交前、推送前那兩道閘)沒有走這條路——那些是使用者主動執行的,
#   不是開資料夾就自動跑,風險形狀不同,另案處理。
_GIT_UNSAFE_CONFIG = (
    "core.fsmonitor",   # r1 資安席:值會被當成指令執行,查工作樹狀態時觸發
    "diff.external",    # r2 資安複審:值會被當成指令執行,主程式逐檔比對差異時觸發
)


def _harden_git_env() -> None:
    """把上面那份清單套到★這支 hook 開出去的所有子行程★。

    用環境變數而不是逐個呼叫點加參數:版本控制會把它當成命令列上的 -c 參數,
    ★子行程一律繼承★,所以主程式內部的呼叫也涵蓋得到(實測驗過)。
    同名鍵已存在時採後值優先,所以附加在尾端是安全的(r2 資安複審實測驗過)。"""
    want = " ".join("'%s='" % k for k in _GIT_UNSAFE_CONFIG)
    cur = os.environ.get("GIT_CONFIG_PARAMETERS", "")
    os.environ["GIT_CONFIG_PARAMETERS"] = (cur + " " + want).strip()
