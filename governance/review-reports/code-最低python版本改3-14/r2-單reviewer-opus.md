severity: minor

# 代碼審 r2 — 單 reviewer(正確性與邊界,opus)

審材:governance/review-reports/code-最低python版本改3-14/r2-snapshot.patch(605b0a65..57314d47)。
對照 clone-314 完整程式;相關測試子集在 /opt/homebrew/bin/python3(3.14)上全綠:t_python_resolver_order_and_floor 11、t_hooks_block_without_python314 10、t_python_launcher_blocks_agree 12、t_lumos_parses_under_old_grammar 5、t_doctor_flags_stale_hook_python 7、t_update_prints_python314_notice_and_slim_strips_floor 4、t_lumos_old_python_reexec_or_explain 6、t_installers_require_python314 6、t_hook_cmd_uses_running_python 4、t_windows_interpreter_pick* 7。

## F1 doctor Q 段的自家掛鉤篩選認不出 free-threaded 直譯器(python3.14t),那種註冊壞掉時不提醒
severity: minor
blocking: 否 — 只影響軟提醒的覆蓋面,不擋任何東西、不誤執行別人的腳本
引句:「and re.match(r"(?i)py(thon[0-9.]*)?(\.exe)?$", parts[0].replace("\\", "/").rsplit("/", 1)[-1])):」
1. merge-claude-settings.py 的 `_hook_cmd` 寫進設定的第一段是 `_PY = sys.executable`(三平台兩家都一樣)。
file: `scripts/merge-claude-settings.py:93`
2. 用 free-threaded 3.14 跑 `lumos install`(Homebrew `python-freethreading`、python.org 安裝器的 free-threaded 選項、uv 的 3.14t),sys.executable 的檔名是 `python3.14t`;上面的正規式在 `[0-9.]*` 之後要求直接結尾,`t` 對不上,這條註冊整條被當成「別的工具的掛鉤」略過。
3. 重現(臨時 HOME,設定裡兩條 lumos 自家掛鉤,直譯器都不存在):
   命令 `/nonexistent/python3.14t "${HOME}/.claude/hooks/impact-hook.py"` 與 `/nonexistent/python3.14 "${HOME}/.claude/hooks/lumos-entry-hook.py"`,呼叫 `_hook_python_problems(<臨時 HOME>)`,輸出:
   `([('claude', '/nonexistent/python3.14', '不存在')], ['claude 的掛鉤註冊的是 /nonexistent/python3.14:不存在'])`——3.14t 那條沒進 seen 也沒進 probs。
4. 後果:那支 3.14t 被移除後,doctor Q 段與 enforcement 的 python 列都不說,正是 [S10] 要抓的「註冊的直譯器不存在」。第二段已經限定是 lumos 自家掛鉤檔,第一段的正規式放寬成允許結尾的 `t` 就收得進來,不會多收別人的掛鉤。

## F2 _py_which 在 Windows 上把「目前目錄底下的整棵子樹」都拒收:目前目錄是磁碟根或家目錄時,正常安裝的直譯器、py、uv 也被當成不存在
severity: minor
blocking: 否 — 只在舊版 Python 啟動且目前目錄是安裝位置的祖先時誤判;固定位置那組(絕對路徑,不經 _py_which)仍可能補上
引句:「if there == here or there.startswith(here.rstrip("\\/") + os.sep):」
1. Windows「先看目前目錄」只在目前目錄**本身**找;這一行卻拒收整棵子樹,連 PATH 上絕對路徑、只是剛好落在目前目錄底下的安裝也拒收。
2. 目前目錄是磁碟根(`C:\`)時 `here.rstrip("\\/")` 變成 `c:`,再加 `\` 就是 `c:\`,整顆 C 槽的東西全部不收。
3. 重現(macOS 上照測試 ⑤b 的做法把 os.name 暫改成 nt,PATH=/opt/homebrew/bin:/usr/bin,呼叫 `_py_which("python3")`):
   `cwd= / shutil.which= /opt/homebrew/bin/python3 _py_which= None`
   `cwd= /opt shutil.which= /opt/homebrew/bin/python3 _py_which= None`
   ——shutil.which 找得到,_py_which 回 None;cwd="/" 就是磁碟根那段算式。
4. 具體情境:Windows 使用者預設的 python 是舊版,在家目錄 `C:\Users\me` 打 `lumos`;uv 裝的 `C:\Users\me\.local\bin\python3.14.exe`、`uv.exe` 都落在家目錄底下,被判「沒有這個指令」,說明還會把它們列進「不存在或沒有這個指令」那一行(明明存在)。`lumos install` 在家目錄跑時,`_pick_windows_launcher` 也會把 `%LOCALAPPDATA%\Programs\Python\Launcher\py.exe` 等全部略過、退回沒驗過的 `python`。
file: `scripts/lumos:16593`
5. 計劃與 PITFALL 寫的是「落在目前目錄底下的不收」,程式跟文字一致;問題在規則本身比它要擋的攻擊面(目前目錄本身、加上相對的 PATH 項)寬。⚠ 如果刻意要連子樹一起擋(防相對 PATH 項),磁碟根那個情況仍然是壞的,而且計劃沒寫這個取捨。

## F3 shell 那段在 LUMOS_PYTHON 有設但不能執行時默默略過,找不到任何 python 時的說明完全不提它,還叫人「去設 LUMOS_PYTHON」
severity: minor
blocking: 否 — 照樣擋下(方向保守),只是說明把人帶錯方向
引句:「if [ -n "${LUMOS_PYTHON:-}" ] && [ -x "$LUMOS_PYTHON" ]; then _LUMOS_ANY_EXE="$LUMOS_PYTHON"; return 0; fi」
1. 這次修正的理由是「找不到時的說明叫人設它,第一步不認等於給了一個用不了的出口」;但設了、路徑打錯(或檔案沒有執行權限)時,這一行直接往下找,不留任何紀錄。
2. 機器上沒有其他 python 時(這次修正要救的正是「只把 3.14 裝在自訂位置」的人),走到 `_LUMOS_NO_PY_MSG`,內容只列「試過 python3.14、python3.15、python3.16、固定位置、python3、python、py」,結尾再叫人設 LUMOS_PYTHON。
3. 重現(把 pre-commit 的 launcher 與 python-314 兩段抽出來 source;PATH 只放 sed;LUMOS_PYTHON_SEARCH_DIRS 指到空目錄):
   `env -i HOME=$T LUMOS_PYTHON_SEARCH_DIRS=$T/nowhere LUMOS_PYTHON=/opt/pythn314/bin/python3.14 PATH=$T/b REPO_ROOT=$PWD /bin/bash -c "source $T/blk.sh; _lumos_py314 || _lumos_block_no_py314"`
   輸出:「找不到任何 python(試過 python3.14、…、py)。…裝在別處就設 LUMOS_PYTHON=<那支 3.14 的絕對路徑>。」——完全沒提使用者已經設了 `/opt/pythn314/bin/python3.14`、而且它不能執行。
4. 對照:有其他 python 可用時,lumos 內部會回「LUMOS_PYTHON=…:不存在」,說得很清楚;只有 shell 這條路沒講。七份內嵌段(三支掛鉤、四支安裝腳本)都一樣。

## F4 lumos.cmd 仍然寫指令名、交給 cmd.exe 先找目前目錄,計劃承認「不在這次範圍」卻沒寫什麼時候回頭看
severity: minor
blocking: 否 — 這個攻擊面早就存在,不是這次新開的;缺的是紀律要求的回頭條件
引句:「包裝檔 `lumos.cmd` 裡照舊寫指令名(版本管理工具換 exe 是常態),那一層不在這次範圍。」
1. `_pick_windows_launcher` 現在用 `_py_which` 拿到目前目錄以外的絕對路徑去跑 `-c pass`,回傳的卻是 `" ".join(cand)`(指令名)。
file: `scripts/lumos:16593`
2. 執行時 cmd.exe 解析 `py`/`python3`/`python` 會先看目前目錄(沒設 NoDefaultCurrentDirectoryInExePath 時)。所以使用者在一個陌生 repo 根打 `lumos`,跑的可以是 repo 裡的 `py.exe`——就是 r1 資安席要擋的那一種,只是換成互動入口;「真的執行成功才算」驗過的那支,也不一定是之後真的會跑的那支。
3. CLAUDE.md 鐵則第 4 條:承認風險(這裡是「那一層不在這次範圍」)旁邊要有 `REVISIT:` 行或寫明綁哪個事件。計劃第 115 行沒有,python直譯器選擇 那篇的 PITFALL 也沒有。
file: `docs/lumos-toolchain-knowledge/Projects/最低Python版本改3.14_計劃.md:115`

## 其他修正逐項(已看,無 finding)
- doctor Q／enforcement 只看自家掛鉤:`ours` 取自 `_GLOBAL_CLAUDE_HOOKS` 去掉 `_hookevent.py`,跟 merge-claude-settings.py 的 `HOOK_ENTRIES` 六支一一對得上;POSIX Claude(`shlex.quote(py) "${HOME}/.claude/hooks/x.py"`)、Codex POSIX(`shlex.quote(py) "<hooks_dir>/x.py" --harness codex`)、兩家 Windows(`"C:/…/python.exe" "…/x.py"`)、舊版沒加引號的 `/usr/bin/python3 "${HOME}/…"`,shlex.split 後第二段的檔名都在 `ours` 裡。用臨時 HOME 實際跑兩家的合併器產生設定,再呼叫 `_hook_python_problems`,兩家都列出「合格」。測試 ⑥ 如果改回舊的「含 hooks/ 就收」,notify.sh 會被執行、side-effect 檔出現,會翻紅。已看,除 F1 外無 finding。
- 測試 ⑤b:實測 os.name 暫改 nt 之後 shutil.which 仍回傳那支檔,回 None 確實是 `_py_which` 的目前目錄判斷造成的,不是「現場走不到」。已看,無 finding。
- 測試 ⑦(launcher 認 LUMOS_PYTHON):base 環境已把 LUMOS_PYTHON_SEARCH_DIRS 指到空目錄、PATH 沒有 python,拿掉第一步就找不到 → 紅。已看,無 finding。
- 測試 ⑧(shell 清單比對 lumos 清單):改 `_py_candidates` 的版本號名稱順序、或 `_py_fixed_candidates` 前三個目錄,都會紅;只在 POSIX 成立,CI 只跑 ubuntu-latest。已看,無 finding。
- import 清單格:ast.walk 包含函式內的 import(`glob`、`subprocess`、`shutil`),merge 那支的結尾錨點第一次出現就在 `if __name__` 呼叫處。已看,無 finding。
- CI 那一行:只看 `CI`／`GITHUB_ACTIONS`;測試 ④ 先清掉兩個變數再設,本機與 CI 兩個方向都有斷言。已看,無 finding。
- pre-push「只推刪除也擋」:py314 那一段到 `anchor verify` 之間沒有提早 exit,敘述跟程式一致。已看,無 finding。
- 精簡版:產物保留 `_py_which`、`_hook_python_problems`、`_GLOBAL_CLAUDE_HOOKS`,用 /usr/bin/python3(3.9.6)編譯與 `--version` 都正常。已看,無 finding。
- README 兩份、升級注意、doctor Q 提示補的 Codex 重新審核:三處意思一致。已看,無 finding。

最嚴重等級 minor,blocking 共 0 條(共 4 條)。
