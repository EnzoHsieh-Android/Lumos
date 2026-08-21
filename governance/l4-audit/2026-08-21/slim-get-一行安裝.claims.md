C1. `slim/get.sh` 的流程順序為：檢查 `git` 指令存在（找不到則清楚錯誤訊息 + rc2、不留 traceback）→ 若 `~/.lumos-slim` 已是合法 git repo（有 `.git`）則執行 `git pull --ff-only` → 若已存在但非 git repo 則拒絕並 rc2、印訊息 → 若不存在則 `git clone` → 檢查 `install.sh` 存在 → 執行 `~/.lumos-slim/install.sh "$@"`（額外參數如 `--force` 原樣轉發） | 預期驗證點: slim/get.sh 原始碼、slim/get.ps1 原始碼

C2. ★INVARIANT★ 三支 `.ps1`（推定為 get.ps1/install.ps1/uninstall.ps1）必須是 ASCII-only 且不加 BOM（2026-08-03 Windows 真機回歸測試推翻前一版「必須加 BOM」的結論） | 預期驗證點: slim/*.ps1 檔案編碼與 BOM 檢查、scripts/test_lumos.py 中 t_slim_ps1_ascii_only_no_bom、t_slim_ps1_real_parser_accepts_both_execution_paths

C3. ★INVARIANT★ 三支 `.ps1` 的 `param()` 不得使用保留自動變數名 `$Args`，應改用 `$ScriptArgs` 等非保留名，否則 `@Args` splatting 展開為空、`--force`／`--here`／`-y` 等參數全部靜默失效 | 預期驗證點: slim/*.ps1 中 param() 宣告、scripts/test_lumos.py 中 t_slim_ps1_args_param_not_shadowed_by_automatic_variable、t_ps1_args_shadowing_is_real_language_behavior

C4. `&` 呼叫外部程式（如 git.exe）之後必須接 `| Out-Host`，否則 stdout 混入函式回傳值、`return $LASTEXITCODE` 會使呼叫端收到 Object[] 而非數字 | 預期驗證點: slim/*.ps1 中所有 `&` 呼叫語法、scripts/test_lumos.py 中 t_slim_ps1_subprocess_output_does_not_pollute_return

C5. `get.ps1` 的 `Invoke-Get` 函式中，`git pull` 分支有檢查 `$LASTEXITCODE`、`git clone` 分支曾漏檢查（2026-08-02 發現，已修復），修復方式為 clone 後補 `$LASTEXITCODE -ne 0` 判斷並印網路/權限錯誤訊息、return 2 | 預期驗證點: slim/get.ps1 中 Invoke-Get 函式、scripts/test_lumos.py 中 t_slim_get_ps1_every_git_call_checks_lastexitcode

C6. 固定安裝落點為 `~/.lumos-slim`（Windows 對應為 `$HOME\.lumos-slim`），此路徑同時是 `Systems/slim-uninstall-一行卸載` 判斷 `~/.local/bin/lumos` 是否為本包所裝的 sha256 內容比對基準 | 預期驗證點: slim/get.sh、slim/get.ps1、slim/uninstall.sh 中對 ~/.lumos-slim 路徑常數的引用

C7. `REPO_URL` 可用環境變數 `LUMOS_SLIM_REPO_URL` 覆蓋（測試用途，可指向本地 git repo 路徑），生產環境預設寫死 GitHub URL、不吃命令列參數覆蓋 | 預期驗證點: slim/get.sh 中 REPO_URL 變數定義與環境變數覆蓋邏輯

C8. `Task 14` 修復：`get.ps1` 收尾原本是裸的 `exit $LASTEXITCODE`，因 `get.ps1` 是 README 一行版 `irm ... | iex` 直接執行的腳本，`exit` 易關掉使用者當下 PowerShell 視窗，修復後改為 `$global:LASTEXITCODE = $LASTEXITCODE`、不再呼叫 `exit` | 預期驗證點: slim/get.ps1 結尾程式碼、scripts/test_lumos.py 中 t_slim_ps1_scripts_avoid_session_killing_trailing_exit

C9. `Task 15` 修復：`get.ps1` 早期 4 處錯誤分支（找不到 git、`git pull` 失敗、目的地已存在但非本包 clone、`install.ps1` 缺失）的裸 `exit 2` 改為包進 `Invoke-Get` 函式、`Write-Error` 後各自 `return 2`，腳本最下方把函式回傳值收進 `$rc` 再寫回 `$global:LASTEXITCODE` | 預期驗證點: slim/get.ps1 中 4 處錯誤分支程式碼、scripts/test_lumos.py 中 t_slim_ps1_error_branches_still_halt_via_return

C10. `Task 16` 修復①（BLOCKER）：`get.ps1` 頂部原本設定 `$ErrorActionPreference = "Stop"`，導致 4 處 `Write-Error` 變成終止型例外、`return 2` 執行不到；修復方式為 4 處 `Write-Error` 都加上 `-ErrorAction Continue` | 預期驗證點: slim/get.ps1 中 4 處 Write-Error 呼叫、scripts/test_lumos.py 中 t_slim_ps1_write_error_noterminating_under_stop_preference

C11. `Task 16` 修復③（MINOR）：`$ErrorActionPreference = "Stop"` 的賦值位置從頂層（函式外）搬進 `Invoke-Get` 函式內部第一行，理由是 `iex` 在呼叫端當下 scope 執行、頂層賦值會外溢污染使用者互動 shell 設定且裝完不還原 | 預期驗證點: slim/get.ps1 中 $ErrorActionPreference 賦值所在位置（應在 Invoke-Get 函式內部第一行而非檔案頂層）

C12. `Task 13`：新增 Windows 對應腳本 `slim/get.ps1`，`slim/get.sh` 本身的 clone/pull/檢查/呼叫邏輯完全沒動；同批中 `slim/install.sh` 從「承載全部邏輯」改為「薄殼轉發給 `install.py`」 | 預期驗證點: slim/get.ps1 檔案存在、slim/get.sh 邏輯與舊版對照、slim/install.sh 內容（應為薄殼轉發）

C13. TEST 宣稱：`t_slim_get_idempotent` 共 7 項檢查全綠，涵蓋首次執行 rc0、第二次執行不出現 clone 式爆炸訊息且 stderr 無 traceback、`.git` 目錄未被破壞、帶 `--force` 轉發給 install.sh 可完整跑完 rc0 | 預期驗證點: scripts/test_lumos.py 中 t_slim_get_idempotent 測試函式（`python3 scripts/test_lumos.py -k slim_get`）

C14. TEST 宣稱：`t_slim_get_no_git` 共 3 項檢查全綠，限縮 `PATH` 模擬 git 缺失，斷言 rc2、清楚錯誤訊息（非 traceback）、`~/.lumos-slim` 未被建立 | 預期驗證點: scripts/test_lumos.py 中 t_slim_get_no_git 測試函式

C15. 本 repo 根目錄既有的 `get.sh`/`get.ps1`（完整版 Lumos 遠端一鍵裝）與 `slim/get.sh`（精簡版）是兩支獨立腳本、不同交付對象：前者 clone `EnzoHsieh-Android/Lumos` 後委派 `bootstrap`，後者目標 repo 是 `citrus-android-developer/Citrus_Lumos`，只做「clone/更新+執行 install.sh」兩件事，不含專案層四分流/`_confirm_tty`/hooks 接線等邏輯 | 預期驗證點: repo 根目錄 get.sh/get.ps1 內容 vs slim/get.sh 內容、兩者目標 repo URL 差異
