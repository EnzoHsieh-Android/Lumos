severity: clean

本輪未找到可利用的洞,沒有 finding。三類逐類結論在下面。我逐 hunk 讀了 `r2-repair-code.patch`,再用 Read/Grep 對照 repo 真代碼(`scripts/lumos`)查證。沒有另跑實驗,所以沒有臨時目錄要清。

## 附:逐類結論

**①提示注入:已看,無。**
- `--import` 與 also 的字串(`_KILL_IMPORT_RE.fullmatch`,見 `scripts/lumos:26751`):
  - 這個形狀檢查是整串 fullmatch,只收 ASCII 識別字加點,沒有 `$`,所以換行、分號、註解、反引號都進不來。
  - `_kill_also_issue` 另外要求多出來的每一行都符合 import 形狀。
  - `_situation_rule_imports_problem` 在 import 形狀檢查通過之後才把 `imp` 原樣放進訊息,其餘外來文字都經 `_kill_esc`。
  - 治理帳 `imports` 欄、kill-log note、確認畫面印的都是已過形狀檢查的字串。
- also 套用範圍(`_kill_also_apply`):
  - 只會把一整行原文換成「原行加 import 行」。
  - `old` 由工具從 HEAD 現算,不是外來輸入。
  - `_kill_mutated` 只在臨時配方(override)認 also,筆記宣告的配方帶了也不理。
  - 套用在記憶體裡做,只寫進 `target`,而 `target` 仍受 `wt_real` 圍欄。
- `run_cmd` 檢查的擋下訊息:
  - 印出去的只有設定鍵、固定的格式說明、`_kill_esc(t)[:60]` 的任務名,以及通過 `^[A-Za-z0-9_.-]+$` 的模組候選。
  - 建置檔內容與 `--file` 都沒有原樣印出。
- `fail_excerpt`:
  - 每行經 `_kill_esc`,最多 12 行,每行 ≤200 字,總長 ≤800 字。
  - Gradle 輸出文字進給 AI 看的訊息這點,上一輪 x1 已放行,不重報。

**②讀寫與執行越界:已看,無。**
- `_kill_run_dir`(`scripts/lumos:26441`):
  - `rel` 取自 `realpath(proot)` 相對 `realpath(top)`。
  - 檢查包含 `rel.startswith("..")`、`isdir`、`realpath(d)` 必須在 `real_wt + os.sep` 底下。
  - 指到樹外的符號連結、或連結指回工作樹根,都 fail-closed 判 error。
  - `run_cmd` 改在平台根子資料夾跑後,原本寫 `cd <平台根> &&` 的舊設定會在基準階段非綠而 abort,不會假綠。
  - `_kill_plat_top` 用 list 形式呼叫 git,沒有 shell 插值。
- `--diff` 範圍字串:
  - 先過 `_lens_range_ok`:不以 `-` 開頭、不含空白、不含 `...`、恰好一個 `..`。
  - 兩端各自再擋 `-` 開頭。
  - 兩端再用 `rev-parse --verify -q --end-of-options <端>^{commit}` 解析。
  - 右端必須等於 `head`,所以不會被當成 git 選項,也不會繞過分岔點的邏輯。
  - 舊版 git 若不支援 `--end-of-options`,會被當成解析不到而拒絕,是 fail-closed。
- 檔頭掃描(`_situation_rule_header_scan`)只讀 HEAD 內容、只決定插入行號,不開檔、不跟連結。
- 這批差異沒有新增密鑰或信箱。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 人裁的 `run_cmd` 檢查:
  - 改用 `_detekt_walk_segments` 切段,多空白、續行、`env`/`time`/`FOO=1` 前綴、`sh -c` 展開、`gradlew.bat`、`gradle` 都會被正規化。
  - `_gradle_args_tasks` 的帶值選項表加了 `--tests`,`app:test` 與 `:app:test` 同義處理。
  - 未涵蓋的情形:模組用 convention plugin 套 Android 外掛、`_KT_BUILD_ANDROID` 認不得,或任務用駝峰縮寫。這些情形下 `--tests` 會讓 Gradle 在基準階段報錯非綠,結果是 abort,不是假通過。無整段通過的路徑。
  - 沒有 `{method}` 的整套跑法,在 cmd_guard_kill 側被標弱證據,人裁只認無弱證據的 killed。
- 檔頭掃描:
  - 檔頭裡未閉合的區塊註解或 `@file:` 括號會讓該行 `clean` 為 False。
  - 未閉合字串最壞是把後面整份檔當成註解行,結果是插入點不成立而拒絕,或多判一個「已有 import」,都偏向拒絕。
- 路徑遮罩(`_kill_mask_paths`):
  - 後面接 `.` 或 `-` 的家目錄前綴不會被換成 `~`,例如行尾句點。
  - 這只洩漏本機使用者名稱,不是密鑰,且 kill-log 本來就在本機,不報。

最後一行總結:最嚴重 severity 為 clean,blocking 共 0 條。
