severity: major

## F1 doctor 自己寫了一份「掛鉤放哪個目錄」的辨認條件,跟安裝端、enforcement 各一套,Codex 那半沒有任何測試守
severity: major
blocking: 是 — 同一件事(哪條註冊是 lumos 自家掛鉤)現在有三種辨認法,新的這套只有 Claude 半邊被測試守著,接手的人要在三套之間猜
引句:「if (base in ours and (d.endswith("/.claude/hooks") or d == codex_dir)」
1. 安裝端決定命令長相的地方是 scripts/merge-claude-settings.py 的 `_hook_cmd` 與 `_HOOKS_SUBDIR`(Claude 寫 `${HOME}/.claude/hooks/…`,Codex 寫 CODEX_HOME 底下的絕對路徑)。同檔案的 enforcement_status 認自家掛鉤是用 `needle in cmd` 子字串比對,目錄用 `home / ".claude" / "hooks"` 這種 Path。這份 diff 在 `_hook_python_problems` 第三次用字串 `"/.claude/hooks"` 加 `codex_dir` 自己拼一份,判準跟前兩者都不同。
2. 名單這半 r2 有抽成 `_own_hook_scripts()` 並用 ⑨ 守一致;目錄這半沒有任何機械守衛:測試 ⑦⑧ 的假設定檔是手寫死的 `${HOME}/.claude/hooks/…`,不是拿 merger 真的產出來餵,所以安裝端改目錄或命令格式,doctor Q 段只會靜默變成「沒有註冊」(seen 為空、不報警),不會紅。
3. Codex 分支完全沒有正向測試。重現(在 mktemp 出來的複製品上,沒動 clone):把 scripts/lumos 第 19951 行的 `or d == codex_dir` 換成 `or False`,清 __pycache__ 後跑
   `/opt/homebrew/bin/python3 scripts/test_lumos.py -k t_doctor_flags_stale_hook_python`
   輸出 `9 passed, 0 failed`——Codex 註冊的舊直譯器從此不再被認出,測試照綠。
file: `scripts/merge-claude-settings.py:80-160`
file: `scripts/lumos:19997-20042`
file: `scripts/test_lumos.py:51697-51720`
⚠ 我沒找到專案裡「已註冊掛鉤路徑」的單一辨認函式可對;若視為「三處本來就各寫各的」,則降 minor。修法方向只是讓這條判準有一個來源或至少有一條吃 merger 真實輸出的測試(含 codex)。

## F2 迴圈裡把 `d` 改名指成目錄字串,跟同函式的 `d` 是設定檔字典撞名
severity: minor
blocking: 否 — 結構對、目前行為正確,只是命名跟同函式與鄰居(enforcement_status 也用 `d` 表設定字典)不一致
引句:「d, _, base = script.rpartition("/")」
1. `_hook_python_problems` 迴圈頭 `d = _json.loads(...)` 是設定檔字典,迴圈內層新加的這行把 `d` 重新綁成路徑字串;下一個家(codex)進迴圈才又被覆寫回字典。目前因為外層 `.values()` 只在進迴圈時求值一次所以沒壞,但之後有人在內層之後再讀 `d.get(...)` 就會踩到。
file: `scripts/lumos:19926-19952`

## 三問結論
1. 分層與依賴方向:已看,無 finding。`_own_hook_scripts` 放在 `_hook_python_problems` 旁、由 enforcement 測試守(⑨),方向與鄰居一致;shell 內嵌段仍是三掛鉤四安裝腳本逐字同一份(t_python_launcher_blocks_agree 守),LUMOS_PYTHON 的處理在 shell 段與 lumos 的 `_py_resolve` 語意不同(shell 不合格往下找、lumos 停下)但有文字明說,不算第二套。
2. 命名與錯誤處理:F2。uv 逾時與執行失敗分開回報的寫法(`_py_uv_find` 回 (路徑, 說明))與 `_py_probe` 一致,已看,無 finding。
3. 第二種做法:F1。get.ps1 只加註解、`_py_which` 只改判準,已看,無 finding。表態記錄裡 py-external tension:existing 指的 scripts/slim-scan.py:41 不帶逾時屬實;這份 r3 差異沒動到 python-path 的呼叫端,四欄與 diff 不矛盾,已看,無 finding。

不對齊共 2 條,其中 major 1 條;blocking 共 1 條。
