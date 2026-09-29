severity: minor

# 代碼審 r3 單 reviewer(正確性與邊界)— 審 57314d47..b0eff2af

本輪先跑過相關測試:t_python_resolver_order_and_floor 13/13、t_hooks_block_without_python314 12/12、t_doctor_flags_stale_hook_python 9/9、t_python_launcher_blocks_agree 12/12,全綠。

## F1 uv 自己出錯(例如 repo 根有壞掉的 uv.toml)仍被說成「uv 找不到 3.14」,r2 說的「執行失敗與沒有 3.14 分開講」只做了一半
severity: minor
blocking: 否 — 只影響找不到時的說明與 uv 這一個候選,固定位置清單通常仍找得到 3.14,判定本身不會錯
引句:「return None, "uv 找不到 3.14"」
1. `_py_uv_find` 只把「逾時」和「OSError」分出來;uv 有執行、但回傳碼不是 0 的情況一律落到最後一行「uv 找不到 3.14」。uv 在「真的沒有 3.14」和「自己出錯」時回傳碼都是 2,只看回傳碼分不出來,而 stderr 被收了卻直接丟掉。
2. 重現(uv 0.x,本機):在一個放了壞掉 uv.toml 的目錄裡執行 `uv python find --system --no-python-downloads '>=3.14'`,輸出 `error: Failed to parse: uv.toml`、rc=2;同一條指令換到正常目錄,印出 `/opt/homebrew/opt/python@3.14/bin/python3.14`、rc=0。
3. 用 lumos 自己的函式跑同一個情境(cwd=壞 uv.toml 的目錄、PATH 只放 uv、`LUMOS_PYTHON_SEARCH_DIRS` 指到空目錄,/opt/homebrew/bin/python3.14 載入 scripts/lumos 呼叫 `_py_resolve()`),結果裡是 `('uv python find', 'uv 找不到 3.14')`,但 uv 其實找得到 3.14。git 掛鉤的目前目錄就是 repo 根,repo 根的 uv.toml／pyproject 設定壞掉會直接走到這裡。
4. 說明因此叫人去裝 3.14,真正原因(uv 設定檔壞了)不會出現。改法方向:回傳碼不是 0 時把 stderr 最後一行帶進結果說明。
file: `scripts/lumos:184`

## F2 LUMOS_PYTHON 不合格、但後面找得到別的 python 時,記下的原因從頭到尾沒印出來:安裝腳本安靜地回 0,之後每次提交卻因為同一個 LUMOS_PYTHON 被擋
severity: minor
blocking: 否 — 掛鉤擋下的時候 lumos 會講清楚原因,不會做出錯的判定;只是安裝那一刻沒提醒,原因要等到下一次提交才看得到
引句:「_LUMOS_NO_PY_MSG="$_LUMOS_ANY_NOTE$_LUMOS_NO_PY_BASE"」
1. 共用段只在「整份都找不到」的時候才把 `_LUMOS_ANY_NOTE` 接進 `_LUMOS_NO_PY_MSG`;只要往下找到任何一支 python 就 `return 0`,note 被丟掉,七個呼叫端都不會印。
2. 重現(本機,/bin/bash 3.2):`LUMOS_PYTHON=/nonexistent/python3.14 PATH=<只有 python3.14、tr、head 的目錄> bash -c 'set -euo pipefail; source <抽出的 launcher 段>; _lumos_any_python && echo "EXE=$_LUMOS_ANY_EXE NOTE=[$_LUMOS_ANY_NOTE]"'` → 回 0,EXE=那支 python3.14,note 有值但沒有人印。
3. 接著安裝腳本(install.sh、install-hooks.sh 等)用這支 3.14 exec lumos;lumos 已經是 3.14,開頭的檢查不會跑,install 流程也不看 LUMOS_PYTHON(全檔讀它的只有 `_py_resolve` 與 `cmd_python_path`),所以安裝 rc 0、什麼都沒說。
4. 下一次 `git commit`:pre-commit 叫 `lumos python-path`,它有設 LUMOS_PYTHON 就只認它 → 實測 `LUMOS_PYTHON=/nonexistent/python3.14 /opt/homebrew/bin/python3.14 scripts/lumos python-path` 印「擋下:LUMOS_PYTHON 指的不是一支可用的 Python 3.14」、rc=2 → Gate PY 擋下。
5. shell 那段的語意是「不合格就往下找」,lumos 那段是「有設就只認它、不往下找」,兩邊對同一個值給出相反的結論,而唯一能在安裝當下說出差別的 note 被丟了。這個流程在本 diff 之前就存在(舊版 `-x` 不過也會往下找),本輪新增的 note 機制沒涵蓋到這種情形。改法方向:在四支安裝腳本 exec 之前,若 `_LUMOS_ANY_NOTE` 有值就先印到 stderr(post-commit 維持安靜)。
file: `scripts/lumos:34388`

## 其餘各塊
- 七份 shell 共用段的 LUMOS_PYTHON 驗法:已看,無 finding。用 /bin/bash 3.2、`set -euo pipefail` 實測:`/usr/bin/true`、`/bin/echo` → 不收並記原因;路徑含空白的真 python → 收;`python3`(相對)→ 記「不是絕對路徑」;`C:\Python314\python.exe`、`C:/x/python.exe` → case 樣式認成絕對路徑、`-x` 不過就記原因;每種情形之後都有印出 AFTER,沒有中途結束。CRLF 輸出由 `tr -d '\r'` 處理。直譯器卡住時沒有逾時,不過本 diff 之前同一支直譯器本來就會直接拿去跑 lumos，同樣會卡住，不算新的退步(計劃已把第一跳沒逾時寫進界線)。
- 七個呼叫端印不印得到原因:四支安裝腳本與 pre-commit/pre-push(經 `_LUMOS_PY_ERR` → `_lumos_block_no_py314`)在「整份找不到」時都印得到;post-commit 刻意安靜 `exit 0`。有一個例外,見 F2。
- doctor 認自家掛鉤的目錄比對:已看,無 finding。對照 merge-claude-settings.py `_hook_cmd` 的寫法:POSIX Claude `"${HOME}/.claude/hooks/x.py"` → shlex 後目錄以 `/.claude/hooks` 結尾;Windows Claude `"C:/Users/…/.claude/hooks/x.py"` 同樣成立;Codex 兩個平台都寫 `str(HOOKS_DIR).replace("\\","/")`,來源都是 `CODEX_HOME` 或 `~/.codex` 再 expanduser,跟 doctor 的 `_codex_home(home)/"hooks"` 正斜線化後的字串相同(CODEX_HOME 不在 HOME 底下也一樣)。迴圈裡 `d` 被 rpartition 蓋掉,但外層 `.values()` 只取一次,下一家會重新指定,實際跑起來沒問題。
- `_py_which` 的新判斷:已看,無 finding。對過 3.14 與 3.9 的 `shutil.which` 原始碼:Windows 在目前目錄找到時回傳的是 `.\name`(相對路徑),新加的 isabs 判斷就會擋掉;PATH 裡寫成絕對路徑的目前目錄，由 realpath 的 dirname 比對擋掉;PATH 空項或 `.` 找到的也是相對路徑，會被擋。
- 新測試格會不會對症狀翻紅:已看,無 finding。⑤c 的 `cwdbin/python3.14` 真的存在(非空轉),改回擋整棵子樹或 abspath 都會紅;⑤d 改回 `except (TimeoutExpired, OSError)` 會紅;⑦b 改回只看 `-x` 會紅(`/usr/bin/true` 會被收);⑦⑧ 拿掉結尾 t 或目錄比對會紅;⑨ 有 `len >= 5` 下限，不會空轉。
- get.ps1 註解、計劃與系統筆記的更新:已看,無 finding(PITFALL 行與計劃〈實作時的決定〉的描述跟程式一致)。

最嚴重等級 minor,blocking 共 0 條(minor 共 2 條)。
