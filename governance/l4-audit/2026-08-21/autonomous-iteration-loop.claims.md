C1. `governance/autonomous-loop.sh` 由 `governance/daily-governance.sh` 串接呼叫(daily-governance.sh 第 26 行以 `--dry-run 6` 呼叫),而非獨立 cron;launchd 排程名為 `com.enzo.lumos.daily-governance`,09:30 單次喚醒。 | 預期驗證點: governance/daily-governance.sh:26、launchd plist com.enzo.lumos.daily-governance

C2. `autonomous-loop.sh` 會驗證當日 `governance/reports/governance-<date>.json` 是否存在:真模式無報即跳(不視為錯誤),dry-run 模式 fallback 使用最近一份日報。 | 預期驗證點: governance/autonomous-loop.sh

C3. `autonomous-loop.sh` 主流程用 `while` 迴圈包 skip→continue 選下一個 gap,並有 `SKIP_CAP=3` 防止空燒(無限跳過)。 | 預期驗證點: governance/autonomous-loop.sh 中 SKIP_CAP 變數

C4. `autonomous_loop/gap_select.py` 讀取日報 `gaps[]`(schema 為 `{weakness, suggestion}`)加上 `backlog.jsonl`,去重排序後選 top-1。 | 預期驗證點: governance/autonomous_loop/gap_select.py

C5. N=1 gate 邏輯(`pending_exists`):dry-run 模式檢查 `governance/pending/*.md` 是否有檔案,真模式檢查 `gh pr list head:auto/spec-` 是否有 open PR;若有則新 gap 只進 backlog 不展開。 | 預期驗證點: governance/autonomous_loop/gap_select.py 中 pending_exists 相關邏輯

C6. `covered.jsonl` 用於永久排除已被既有 spec 覆蓋的 gap。 | 預期驗證點: governance/autonomous_loop/{gap_select.py,backlog.py} 中對 covered.jsonl 的讀寫

C7. `autonomous_loop/cross_audit.py` 呼叫 qwen3-max(DashScope 國際 endpoint)做跨家族複核,回傳格式含 `{status, worst_severity, ...}`;`status==degraded` 代表 fail-open(觸發條件為 no_key / http / timeout)。 | 預期驗證點: governance/autonomous_loop/cross_audit.py

C8. `orchestrator_result.py` 負責從 orchestrator 回傳文字中提取「最後一個合法 JSON」,以容錯敘述文字中夾雜 `{clean,minor}` 等干擾字串。 | 預期驗證點: governance/autonomous_loop/orchestrator_result.py

C9. CONVERGED 的定義為 `lumos loop status <topic> --need 2` exit code 0,即連續 2 輪 canary caught 且 severity ∈ {clean,minor}。 | 預期驗證點: scripts/lumos 的 `loop status --need` 旗標實作

C10. 失控保護機制:design-loop 輪數上限(max cap)= 6 輪,且 N=1 並發限制;連續撞 cap 會觸發停止並發 LINE 告警。 | 預期驗證點: governance/autonomous_loop/orchestrator-prompt.md 或 design-loop 相關設定中的輪數上限與 LINE 告警邏輯

C11. 放行閘路徑:dry-run 寫入 `governance/pending/<date>-<topic>.md`;真模式(`--pr`)則 commit 到 `auto/spec-<topic>-<date>` branch、以 `gh pr create` 開 PR、並發 LINE 通知。 | 預期驗證點: governance/autonomous-loop.sh 中 dry-run 與 --pr 分支邏輯、gh pr create 呼叫點

C12. `requeue_unconverged`(未收斂處置)機制:未收斂 gap 的 value_score 乘以 0.7 衰減,累計 `unconverged` 次數達上限 3 次後轉入 covered(放棄自動處理、留待人工)。 | 預期驗證點: governance/autonomous_loop/backlog.py 中 requeue_unconverged 相關函式/邏輯

C13. `scripts/test_autonomous_loop.py` 共有 27 個測試全數通過(27 passed)。 | 預期驗證點: 執行 `python3 -m pytest scripts/test_autonomous_loop.py` 或等效指令,確認測試數與通過數

C14. 2026-08-18 的變更:七處 LINE 通知的 token 傳遞方式從 shell 內插(`t='$(cat …)'`)改為透過 `LINE_TOKEN` 環境變數傳遞,並在 Python 端以 `os.environ.get` 讀取。 | 預期驗證點: governance/autonomous_loop 內 LINE 通知相關程式碼(如 line_notify.py)及該日期附近的 git commit/diff

C15. design-loop 在 autonomous 版本中對 skill 預設有覆寫:起手用 opus auditor(而非 skill 預設「sonnet 起手、連 2 次 missed 才升 opus」),且 canary 限用 type a/b/c、禁用 type d。 | 預期驗證點: governance/autonomous_loop/orchestrator-prompt.md 中 auditor 起手模型與 canary type 限制的設定
