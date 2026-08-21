C1 [✅] get.sh 流程順序(git檢查→rc2/存在.git則pull --ff-only/存在非git則rc2拒絕/不存在則clone→檢查install.sh→執行並轉發$@)與敘述完全一致 | 證據: slim/get.sh:28-56(git檢查28-33、.git判斷35-41、非git拒絕42-45、clone47-48、install.sh存在檢查51-54、執行56)

C2 [✅] 三支 .ps1(get.ps1/install.ps1/uninstall.ps1)確認為 ASCII-only 且無 BOM;對應測試存在且全綠 | 證據: `file slim/*.ps1` 均回報 "ASCII text"、`head -c3 | xxd` 首3位元組分別為 23 20 67/69/75(即"# g/i/u",無 EF BB BF BOM)、`grep -nP '[^\x00-\x7F]'` 三檔皆零命中;scripts/test_lumos.py:17694 t_slim_ps1_ascii_only_no_bom、17600 t_slim_ps1_real_parser_accepts_both_execution_paths 均存在,`python3 scripts/test_lumos.py -k slim_ps1` 79 passed 0 failed

C3 [✅] 三支 .ps1 的 param() 均用 $ScriptArgs 非 $Args;對應測試存在且通過 | 證據: slim/get.ps1:20 `param($RepoUrl, $Dest, $ScriptArgs)`、slim/install.ps1:21、slim/uninstall.ps1:21 同款;scripts/test_lumos.py:17733 t_slim_ps1_args_param_not_shadowed_by_automatic_variable、17668 t_ps1_args_shadowing_is_real_language_behavior 均存在,`-k ps1_args_shadowing` 3 passed 0 failed

C4 [✅] 三支 .ps1 的 `&` 外部呼叫皆接 `| Out-Host`;對應測試存在且通過 | 證據: slim/get.ps1:59 `& $InstallScript @ScriptArgs | Out-Host`、slim/install.ps1:34、slim/uninstall.ps1:34 同款;scripts/test_lumos.py:17768 t_slim_ps1_subprocess_output_does_not_pollute_return,`-k slim_ps1` 全綠含「& 呼叫必須接 | Out-Host」三檔各一條斷言全過

C5 [✅] get.ps1 Invoke-Get 中 pull/clone 分支現況皆檢查 $LASTEXITCODE,且 commit 298a83c(2026-08-02)證實原本 clone 分支確實漏檢、修復方式與敘述(補 $LASTEXITCODE -ne 0、印網路/權限錯誤訊息、return 2)完全吻合 | 證據: slim/get.ps1:34(pull分支檢查)、44-47(clone分支檢查+錯誤訊息+return 2);`git show 298a83c -- slim/get.ps1` diff 顯示新增此段,commit訊息「③ get.ps1 git clone 漏檢 $LASTEXITCODE(pull 那支有,是漏寫的不對稱)」;scripts/test_lumos.py:17798 t_slim_get_ps1_every_git_call_checks_lastexitcode,測試輸出含兩條「git 呼叫...後必須檢 $LASTEXITCODE」均過

C6 [✅] ~/.lumos-slim(Windows: $HOME\.lumos-slim)為固定落點,且此路徑(scripts/lumos)在 uninstall.py 中確為 sha256 比對基準之一 | 證據: slim/get.sh:26 `DEST="${HOME}/.lumos-slim"`、slim/get.ps1:64 `$Dest = Join-Path $HOME ".lumos-slim"`;slim/uninstall.py:236-241 `pkg_cli = pkg / "scripts" / "lumos"` 取 sha256 當比對基準——★但屬備援基準★:主要基準是 manifest.json 的 bin_sha256(uninstall.py:233-235),~/.lumos-slim/scripts/lumos 僅在「manifest 給不出參照時退回」(uninstall.py:203 註解「相容較舊安裝」),非唯一/主要基準,主張未區分主備但字面「同時是...比對基準」未算錯

C7 [✅] REPO_URL 可用 LUMOS_SLIM_REPO_URL 覆蓋、生產預設寫死 GitHub URL、命令列參數($@)只轉發給 install.sh 不解析覆蓋 REPO_URL | 證據: slim/get.sh:25 `REPO_URL="${LUMOS_SLIM_REPO_URL:-https://github.com/citrus-android-developer/Citrus_Lumos.git}"`,全檔僅此一處對 REPO_URL 賦值,無任何 `$1`/getopts 對其覆寫;get.ps1:63 同款環境變數覆蓋寫法

C8 [✅] get.ps1 收尾為 `$global:LASTEXITCODE = $rc`、無裸 `exit`,修復理由(irm|iex 一行版執行、exit 易關視窗)與 commit 563db37/80ee628 註解一致 | 證據: slim/get.ps1:66-67;scripts/test_lumos.py:18978 t_slim_ps1_scripts_avoid_session_killing_trailing_exit,`-k slim_ps1` 含「get.ps1 程式碼行完全不含裸 exit」「仍把 rc 寫回 $LASTEXITCODE」兩條均過

C9 [✅] 4 處早期錯誤分支(git 未找到/pull 失敗/目的地存在非本包/install.ps1 缺失)包進 Invoke-Get 函式、各自 return 2,函式回傳值收進 $rc 寫回 $global:LASTEXITCODE,與 commit 563db37(Task 15)diff 完全對應 | 證據: `git show 563db37 -- slim/get.ps1`,commit 訊息明寫「這支檔案早期還有 4 處錯誤分支的 exit 2...沒有一併改掉」並逐一列舉;scripts/test_lumos.py:19021 t_slim_ps1_error_branches_still_halt_via_return,`-k slim_ps1` 「get.ps1 邏輯已包進函式」「函式回傳值有被外層變數接住」均過

C10 [✅] Task 16 修復①:4 處 Write-Error 加 -ErrorAction Continue,commit 80ee628 訊息明寫「①BLOCKER...修法:6 處 Write-Error 都加 -ErrorAction Continue」(get.ps1 佔其中 4 處,install.ps1/uninstall.ps1 各 1 處,合計 6),與主張的「get.ps1 4 處」精確吻合(當時 get.ps1 尚無 clone 分支的第 5 處,該處係隔日 298a83c 才新增,同步套用同款寫法) | 證據: `git show 80ee628 -- slim/get.ps1` diff 逐一在4個既有 Write-Error 行尾加 -ErrorAction Continue;現況 get.ps1 共5處(第5處為clone分支,298a83c新增)皆有 -ErrorAction Continue,與時序不衝突;scripts/test_lumos.py:19100 t_slim_ps1_write_error_noterminating_under_stop_preference,`-k slim_ps1` 全過

C11 [✅] Task 16 修復③:$ErrorActionPreference = "Stop" 從頂層搬進 Invoke-Get 函式內部第一行,理由(iex 在呼叫端當下 scope 執行、頂層賦值外溢污染且不還原)與 commit 80ee628 訊息逐字對應 | 證據: slim/get.ps1:22(位於函式內第一行,param() 之後);`git show 80ee628 -- slim/get.ps1` diff 顯示此行從函式外移入函式內,commit訊息「③MINOR:get.ps1 的 $ErrorActionPreference 原本寫頂層,irm ... | iex 執行時會污染呼叫端互動 session...修法:搬進 Invoke-Get 函式內部第一行」

C12 [✅] commit 5fa02d2 新增 slim/get.ps1(全新檔案,55行),同批 slim/install.sh 從 296 行大幅刪減為薄殼轉發,slim/get.sh 完全未出現在該 commit 變更檔案清單中(邏輯未動) | 證據: `git show 5fa02d2 --stat` 檔案清單含 `slim/get.ps1 | 55 ++++`、`slim/install.sh | 296 ++---------------`,但**不含** slim/get.sh;commit 訊息「新增 install.ps1/uninstall.ps1/get.ps1 三支 Windows 入口」;主張中「Task 13」標籤本身無法從 commit message 直接核對(該訊息未寫 Task 編號),但敘述的實質行為(get.sh 未動、install.sh 變薄殼、新增 get.ps1)完全對應

C13 [✅] t_slim_get_idempotent 恰為 7 項 check(),涵蓋首次rc0/已建立/全域指令已裝/冪等不爆炸/stderr無traceback/.git未被破壞/--force轉發完整跑完rc0,實測全綠 | 證據: scripts/test_lumos.py:17901-17945 逐行7個 check() 呼叫;`python3 scripts/test_lumos.py -k slim_get` 輸出前7條全部 ✓,總計「13 passed, 0 failed」(含C14的3條與C5相關的3條前置/斷言)

C14 [✅] t_slim_get_no_git 恰為 3 項 check(),限縮 PATH 模擬 git 缺失,斷言 rc2/清楚錯誤訊息非traceback/~/.lumos-slim 未被建立,實測全綠 | 證據: scripts/test_lumos.py:17950-17972 逐行3個 check() 呼叫(`env = {"HOME":..., "PATH": str(empty_bin)}` 限縮PATH);`-k slim_get` 輸出後3條全部 ✓

C15 [✅] 根目錄 get.sh(clone EnzoHsieh-Android/Lumos 後委派 bootstrap)與 slim/get.sh(clone citrus-android-developer/Citrus_Lumos,只做clone/更新+install.sh)為兩支獨立腳本、目標repo不同、slim/get.sh確實不含四分流/_confirm_tty/hooks接線邏輯 | 證據: get.sh:10 `LUMOS_URL="${LUMOS_URL:-https://github.com/EnzoHsieh-Android/Lumos}"`、get.sh:30 委派 `lumos bootstrap`;slim/get.sh:25 `REPO_URL="${LUMOS_SLIM_REPO_URL:-https://github.com/citrus-android-developer/Citrus_Lumos.git}"`,全檔僅 git檢查/clone-pull/install.sh呼叫,無 bootstrap/_confirm_tty/hooks 相關字串

✅15 ❌0 ❓0 ⏭0
