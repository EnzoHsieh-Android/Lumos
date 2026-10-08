severity: minor

範圍:併發與資源(最壞時序)。沒有 blocker 或 major;試過三個疑點,只有 P1 成立。

**P1**
severity: minor
blocking: 否。總預算 20 秒的承諾不成立,但不會讓寫表態失敗,也不會放行錯誤結果。
`_backing_valid_rows` 只在每個還沒快取的 sha 迴圈頂端檢查預算;進 `_codeloop_record_valid(..., detail=True)` 後一個 sha 最多兩次 git,各有 `_disp_git_timeout()`(預設 8 秒);最壞 19.9 秒時進入新 sha,兩次各卡滿 8 秒,總共約 36 秒。收到 unsure 仍整題記 none,行為安全,只有耗時超出宣稱。修法:把剩餘時間傳進去,單次逾時取 min(預設, 剩餘)。
引句:「cache[sha] = _codeloop_record_valid(repo_root, sha, head_sha, detail=True)」
引句:「_BACKING_BUDGET = 20.0   # 寫表態時版本驗證的總預算(秒);超過的題記 none」
未能重現:只做程式推演,沒有實際注入卡住的 git。

逐項查證,判為不成立:
1. 補換行與追加交錯:雙行程各 400 行約 1KB、對齊起跑重複 15 次,每次讀回 800 行無遺失或撕裂;O_APPEND 單次 write 原子;補換行只在最後位元組不是換行時動作;讀取逐行容錯。只有刷出中途被砍才會留殘行,正是補換行要處理的。
2. 沙盒清理:mkdtemp 在缺 run_cmd 的 return 2 之後才執行;建立後所有路徑在同一個 try/finally;新增的 worktree add 帶 sha、node_dirty、蓋章迴圈不產生要清理的資源。既有問題:缺 run_cmd 時前面平台結果不落帳,偏向沒有背書,不危險。
3. 子行程例外與逾時:`_codeloop_record_valid` 兩次 git 帶 timeout,逾時與非零都轉 unsure;`_contract_backing_apply` 外層 try 包住;`_backing_mark` 在 try 外但不做 I/O;cmd_guard_kill 新增的三個 git 呼叫沒 timeout,同既有風格、不在寫表態路徑,不升級。
4. 檔案 handle 皆 with 或自動關閉。
5. 快取以 sha 為鍵、單次呼叫內有效,unsure 也快取,判定一致。

圖譜鏡頭:沒有逐條對照固定席;就本鏡頭,diff 不破壞 guard-kill 的沙盒隔離與清理、kill-log 追加語意。

最高嚴重度:minor;blocking 條數:0
