## Findings

### f1 — blocker

- spec 段落：設計 §2–§3「派工／VERDICT 規格」
- 引句:「★真相源=報告檔★(留痕稽核物;stdout 只判斷是否正常結束)」
- 問題：審計／複審 agent 只獲得 `Read,Grep,Glob`，沒有 `Edit`、`Write` 或 `Bash`，因此無法建立或完成「報告檔」。spec 又明定 stdout 不是真相源，卻沒有定義由 `selfaudit.py` 把哪一段 stdout 原子落成報告、報告路徑如何傳入、逾時後如何隔離半寫檔。照目前文字，正常審查也只能因報告不存在而 FAIL，整條 PASS 路徑不可達。今日兩份手動報告是既存檔案，但不證明這個唯讀 `claude -p` 工具面能產檔。
- 查證：`governance/autonomous-loop.sh:201-203`（既有派工把 stdout redirect 成 JSON）；`governance/review-reports/self-audit/2026-08-24-lumos-cli-write.md:1-5`（手動報告確為獨立 Markdown 檔）；`governance/ai-governance-research.sh:135`（唯讀模板只把 agent 輸出導向 shell stdout）。

### f2 — blocker

- spec 段落：設計 §6「執行模式」
- 引句:「selfaudit.py 只准寫三類(self_audit 戳/被審那篇/`pending/selfaudit/`+skip 檔),範圍刀機械驗」
- 問題：「範圍刀」只是 agent 執行後才跑的 `git diff --name-only`，不是寫入能力白名單。修 agent 已持有 `Edit`，越界修改在檢查前已落到真實 worktree；spec 對「越界=整輪作廢」沒有定義回復越界檔、保留原有 dirty changes、或用隔離 worktree 的方法。因此它既不能阻止越界，也不能安全復原，卻被當作解除 dry-run 禁令的機械授權。若 worktree 原先已有使用者修改，單純 `git diff --name-only` 還會把既有變更誤判為本輪越界；若直接 checkout/revert，則可能毀掉使用者工作。
- 查證：`governance/autonomous-loop.sh:6-12`（非 dry-run 入口目前硬拒絕）；`governance/autonomous-loop.sh:201-203`（既有 agent 直接在 repo 執行且持有 Edit）；`governance/external-reviews/2026-07-29-codex-round3-recheck.md:359-363`（既有裁定指出 repo 寫權隔離仍未完成）。

### f3 — major

- spec 段落：設計 §1「選目標／前置重構」
- 引句:「把 Check S 判定從 `run_doctor` 閉包抽成頂層函式 `_self_audit_lists(env) -> (sa_missing, sa_stale)`」
- 問題：被抽出的區塊不只計算兩份清單，還在每一個 missing/stale 節點上 append `check-s` governance event。若新函式只依宣告回傳兩份清單，`run_doctor --ci` 無法保持目前逐節點落帳行為；若 event 副作用留在 `run_doctor`，又必須重新從兩種不同形狀的結果還原節點。spec 的唯一回歸測試只比「兩邊算出同集」，沒有釘住 `gov_events`、排序前後資料形狀、或 `--ci` 帳。這會讓前置重構在自動審計尚未啟用前先靜默改壞 doctor 治理帳。
- 查證：`scripts/lumos:823-845`（判定迴圈同時 append `gov_events`）；`scripts/lumos:846-851`（missing 與 stale 原始資料形狀不同，之後才把 stale 轉顯示字串）；`scripts/lumos:459-466`（`gov_events` 是 `run_doctor` 區域狀態）。

### f4 — blocker

- spec 段落：設計 §1、§4「配額／per-篇週戳」
- 引句:「每篇處置完即記週戳分錄(★per-篇完成戳,非整輪頭尾★——s2f10:N=2 中途死掉,下次只補沒做完的那篇,不重派已完成的)」
- 問題：per-篇戳只能回答「這篇本週做過沒有」，不能單獨維持「全系統每週最多 N=2」。若排程每日進場、每次排除本週已完成篇後再選兩篇，會每天處理下一批，實際變成最多 14 篇／週，而非 2 篇／週。spec 沒定義本週已完成篇數如何計入剩餘 quota，也沒有測試「兩篇均完成後，同週下一次執行選零篇」。這直接破壞成本上限與重派抑制。
- 查證：`governance/autonomous-loop.sh:90-101`（既有 probe 用單一 ISO week seed 實現真正的每週一次）；`governance/autonomous-loop.sh:117-122`（既有 nags 用全域 week stamp 在本週第二次入口直接返回）。兩個所稱母版都不是僅靠 per-item stamp 控制總配額。

### f5 — major

- spec 段落：設計 §1、§4「skip／pending」
- 引句:「已有未結案 pending 檔的篇跳過,人清 pending 後自動恢復」
- 問題：`selfaudit-skip.jsonl` 被描述成仿 `covered.jsonl`，但 `covered.jsonl` 是永久集合；append 後沒有自動撤銷語意。另一方面 pending 的正式處置是移到 `pending/archive/`，不是刪除。spec 未定義選擇器究竟以 skip ledger 為準、以 active pending 檔為準，還是每次重建 skip；也未定義 archive 後如何精確撤銷同篇舊紀錄。照「covered 同款」實作會永久跳過，違反「清 pending 後自動恢復」。
- 查證：`governance/autonomous_loop/gap_select.py:25-38`（covered JSONL 載入為永久 set，mark 只 append）；`governance/autonomous_loop/gap_select.py:59-70`（covered 項永久排除，沒有撤銷）；`governance/autonomous-loop.sh:149-155`（既有人工處置明示移往 `pending/archive/`）。

### f6 — major

- spec 段落：設計 §4「pending >3 天喊人」
- 引句:「>3 天喊人:★selfaudit.py 每次跑自帶檢查+LINE★」
- 問題：「每次跑」沒有通知去重戳、成功送達判定或重試頻率。排程若每日執行，同一個未結案檔從第 4 天起會每天 LINE；若 token 缺失或傳送失敗，又沒有帳能區分「已喊」「未喊」。既有機制雖觸發位置不合本案，但至少清楚限定檔案範圍、mtime 與發送方式；新 spec 只寫一句，測試十條也完全沒有 aging 邊界、archive 排除、通知去重或傳送失敗案例。
- 查證：`governance/autonomous-loop.sh:149-160`（既有檢查使用 `-maxdepth 1 -mtime +3` 並直接 LINE）；`governance/autonomous-loop.sh:117-129`（週報另有 week stamp 去重）；`governance/autonomous_loop/line_notify.py:5-12`（通知回傳值存在，但 spec 未定義如何落帳消費）。

### f7 — major

- spec 段落：設計 §5「成本落帳」
- 引句:「成本錨 $1-2/篇 由帳目持續重驗(鐵則:承認風險附回頭看條件)」
- 問題：指定的 `canary record --tokens/--wallclock-min` 根本不保存美元成本，因此無法由該帳重驗「$1–2／篇」。`claude -p` JSON 確有 `total_cost_usd`，既有 orchestrator 只把 USD 印進 log，寫入 canary ledger 的仍只有 tokens 與分鐘。更且 FAIL 修復鏈可呼叫三個 agent，spec 沒說是一篇聚合三次成本或每個 subprocess 各記一筆；「每篇跑完一筆」會掩掉各階段成本與 timeout 浪費。
- 查證：`governance/autonomous-loop.sh:217-248`（USD 只在 log 行，ledger 僅接 `cost_cli_args`）；`governance/autonomous_loop/orchestrator_result.py:27-66`（抽得到 USD，但 CLI args 只產 tokens/wallclock）；`scripts/lumos:3429-3445`（canary schema 沒有 USD 欄）。

## 逐節結論

- 症狀：已讀，無 finding。
- 設計 §1 選目標：見 f3、f4、f5。
- 設計 §2 派工：見 f1。
- 設計 §3 VERDICT：見 f1。
- 設計 §4 處置：見 f2、f4、f5、f6。
- 設計 §5 成本落帳：見 f7。
- 設計 §6 執行模式：見 f2。
- 設計 §7 doctor 文案：已讀，無 finding。
- 不做什麼：已讀；其範圍保證未成立的否決問題併入 f2。
- 連動：已讀；pending 歸檔與 skip 恢復矛盾併入 f5。
- PRIOR-ART：已讀；週戳母版實際不支持本設計的 per-篇總配額，併入 f4。
- 測試十條：已讀；缺少報告產生路徑、doctor governance event 回歸、同週總 quota、pending aging/通知去重、越界修改復原，分別併入 f1、f3、f4、f6、f2。
- 實務隱患：已讀；「範圍刀」並非寫入隔離且無復原，併入 f2。
- 審計修正紀錄 r1：已讀；C、I、J 宣稱已折入，但仍分別留下 f2、f7、f4。
- 下一步：已讀，無獨立 finding。

最嚴重 severity：blocker
