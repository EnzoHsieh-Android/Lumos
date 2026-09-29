severity: minor

## F1 doctor / enforcement 會真的執行設定檔裡「任何含 hooks/ 的指令」的第一個詞,不限 Python
severity: minor
blocking: 否 — 縱深防禦;攻擊者要先能寫使用者的 ~/.claude/settings.json 或 ~/.codex/hooks.json,那時本來就能執行任意碼,沒有增加權限
引句:「path, why = _py_probe([exe], time.monotonic() + _PY_PROBE_TIMEOUT)」
file: `scripts/lumos:19883`(_hook_python_problems,由 doctor Check Q 與 enforcement_status 呼叫)
1. 誰:能改 ~/.claude/settings.json 的人(或使用者自己裝的、與 lumos 無關的第三方掛鉤)。入口:設定檔 hooks 段,任一項 command 只要含字串 hooks/。
2. _hook_python_problems 用 shlex.split(cmd)[0] 取第一個詞當「直譯器」,不驗它是不是 python,直接交給 _py_probe 以 `[exe, "-c", <探針碼>]` 執行。
3. 重現:臨時 HOME 的 settings.json 註冊 `<tmp>/x/hooks/foo --a`(foo 是寫標記檔的 sh 腳本),以 3.14 載入 scripts/lumos 後呼叫 `_hook_python_problems("<tmp>")`,foo 真的被執行,標記檔內容為 `ran -c import sys ...`。
4. 拿到什麼:doctor 與 enforcement(SessionStart 類流程會叫)每次都會以陌生參數 `-c <多行字串>` 執行別人的掛鉤程式;若該程式對未知參數有副作用,就被觸發。沒有提權。
5. 判準:只驗第一個詞的檔名結尾或 basename 像 python(python3、python3.14、py)再執行,其餘只報「非 Python 直譯器」。

## F2 Windows 上探測候選以裸指令名執行,目前目錄(可能是陌生 repo)在搜尋路徑內 ⚠推論,未能在 Windows 重現
severity: minor
blocking: 否 — 推論,攻擊路徑依賴 Windows 搜尋順序,本機為 macOS 無法重現
引句:「elif shutil.which(exe) is None:」
file: `scripts/lumos:_py_probe`(patch 內 _py_probe / _py_uv_find)
1. 誰:提供陌生 repo 的人。入口:repo 根目錄放 python3.14.exe / python.exe / uv.exe(或 .bat)。
2. Windows 的 shutil.which 與 CreateProcess 預設先搜目前目錄;git 掛鉤的工作目錄是 repo 根。
3. 只有 lumos 被 3.14 以前的 Python 啟動(_py_floor_gate → _py_resolve)、或 Windows 的 _pick_windows_launcher 才會走到裸名探測,此時候選 python3.14、py、uv、python3、python 都以裸名執行。
4. 拿到什麼:使用者在該 repo 提交或安裝時,執行 repo 裡的可執行檔。前提多(Windows、掛鉤已裝、舊直譯器、repo 已被信任到裝掛鉤)。
5. 判準:Windows 上探測前對 shutil.which 結果做 realpath,並排除位於 cwd 底下的結果。⚠ 判不準是否所有 Windows Python 版本都先搜 cwd。

## 已看,無 finding 的項目
- LUMOS_PYTHON / LUMOS_PYTHON_SEARCH_DIRS / LUMOS_REEXEC_PYTHON:皆為使用者自己 shell 環境控制;REEXEC 只能造成拒絕重跑,不能導向執行。LUMOS_PYTHON 強制絕對路徑並實際探測。已看,無。
- 固定位置候選(/opt/homebrew/bin、/usr/local/bin、~/.local/bin、uv、pyenv):皆為使用者或系統管理者擁有,與舊版 `command -v python3` 的信任面同級,沒有新增「別人可寫」位置。已看,無。
- 掛鉤內 `_lumos_py314` 用 `$REPO_ROOT/scripts/lumos python-path` 取路徑後執行:執行 repo 內 lumos 是既有信任模型(舊掛鉤本來就這樣跑),非新增。已看,無。
- `{python}` 代入:`_run_cmd_expand` POSIX 用 shlex.quote,{method} 仍 shlex.quote 且有白名單;run_cmd 來自 repo 設定檔本就是 shell 指令(既有)。Windows 的 list2cmdline 不擋 & 與 %,但 sys.executable 不受攻擊者控制。已看,無。
- merge-claude-settings 寫入設定:sys.executable 經 shlex.quote(POSIX)或雙引號(Windows),含空白或特殊字元不會被 shell 拆開;比原本未加引號更安全。授權範圍未放寬。已看,無。
- 密鑰與個資進 log:錯誤訊息只含直譯器路徑與版本。已看,無。
- 加密與傳輸:get.sh / get.ps1 的下載來源與驗證沒有改動。已看,無。
- CI:`pip install ruff==0.16.7` 有釘版本、來源為 PyPI,未帶 --require-hashes(供應鏈縱深防禦,不是這次新增的模式;actions 也沿用 tag 不釘 SHA)。ruff 只在 CI 當工具、沒有 secrets 傳入。⚠ 我無法離線確認 0.16.7 這個版本存在(pip index 在本機無法跑),若不存在 CI 會紅而非被利用。已看,無 finding。
- slim-gen 剝段:字串切割,只影響產出檔內容,無輸入來自外部。已看,無。

最高等級 minor,blocking 共 0 條
