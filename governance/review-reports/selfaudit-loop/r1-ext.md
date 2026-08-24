## 症狀（第 25–31 行）

已讀，無 finding。

## 設計（第 33–47 行）

### f1 — blocker

spec 段落：設計 §2–3

引句:「對每篇 `claude -p` 派乾淨 agent」

問題：現行自主 loop 明確禁止任何非 `--dry-run` 執行；但 PASS 路徑會修改圖譜 frontmatter。Spec 沒有定義這段究竟在 dry-run 中破例寫檔，還是解除整個 loop 的安全禁令。前者破壞 dry-run 合約，後者目前入口直接 rc=2，故主流程沒有合法可執行模式。

查證：`governance/autonomous-loop.sh:6-14`、`governance/autonomous-loop.sh:23-26`、`scripts/lumos:7578-7593`

### f2 — major

spec 段落：設計 §1

引句:「直接 import lumos 模組呼叫同一套判定,單一實作」

問題：Check S 候選判定不是可 import 的函式，而是 `run_doctor` 內的區域迴圈與區域變數 `sa_missing`、`sa_stale`。`scripts/lumos` 也不是正常 Python 模組檔名。新 picker 無法按 spec「直接 import 同一套判定」；若自行重寫就違反單一實作，若先重構則已超出 spec 宣稱的「零新演算法／全現成零件」，且缺相容測試。

查證：`scripts/lumos:459`、`scripts/lumos:823-851`、`scripts/lumos:6477-6523`

### f3 — major

spec 段落：設計 §2–3

引句:「結尾一行機械可讀判定 `VERDICT: PASS|FAIL`」

問題：沒有定義可接受的精確文法與完整性條件。需至少釘死「程序成功結束、報告完成落盤、最後一個非空行完全匹配 `^VERDICT: (PASS|FAIL)$`」；否則半寫報告、正文示例中的 `VERDICT: PASS`、同時出現 PASS/FAIL、或 agent 在結論後續寫文字，都可能被錯抽成 PASS 並自動蓋章。現有兩份手動報告也沒有 VERDICT 行，不能直接作為 parser fixture 或「同款 prompt」的實據。

查證：`governance/review-reports/self-audit/2026-08-24-lumos-cli-read.md:116`、`governance/review-reports/self-audit/2026-08-24-lumos-cli-write.md:109`、`scripts/lumos:7578-7583`

### f4 — major

spec 段落：設計 §3

引句:「pending >3 天既有喊人機制自然接手」

問題：既有 pending 不是單純通知匣，而是自主 loop 的全域 N=1 閘；dry-run 下只要任何 `pending/*.md` 存在，gap selection 就立即回空。每次 self-audit FAIL 因而會停止後續自主迴圈，直到人放行或歸檔；>3 天通知也只在 `GAP_JSON` 為空後執行。Spec 把它描述成無副作用的「自然接手」，漏掉了會凍結主 loop 的重大耦合。

查證：`governance/autonomous_loop/gap_select.py:16-22`、`governance/autonomous_loop/gap_select.py:59-64`、`governance/autonomous-loop.sh:141-164`

### f5 — major

spec 段落：設計 §1–4

引句:「按 PageRank 降冪取前 `N=2`」

問題：沒有任何失敗冷卻、已 pending 排除或最大重審次數。同一篇高 PageRank 筆記 FAIL 後仍然維持 missing/stale，下一週會再次排在最前，重派、重燒錢，並可能反覆覆寫同日命名或堆積 pending。既有 backlog 對未收斂項已有「降分、最多三次後轉人工」機制，但 spec 沒借用它。

查證：`scripts/lumos:837-850`、`governance/autonomous_loop/gap_select.py:41-56`

### f6 — major

spec 段落：設計 §4

引句:「單篇 timeout 15 分鐘;週配額 N=2」

問題：timeout 與週戳的提交時點未定義。若像 `run_nags` 一樣先執行、後寫週戳，第一篇完成而第二篇超時時，重跑會再次派第一篇；若先寫戳，agent 啟動失敗或半寫報告會吞掉整週配額。Spec 也沒有 per-node 完成帳或原子狀態，測試僅寫「週戳防重跑」，不足以覆蓋部分成功。

查證：`governance/autonomous-loop.sh:117-122`

## 不做什麼（第 49–52 行）

已讀，無 finding。

## PRIOR-ART（第 54–57 行）

### f7 — major

spec 段落：PRIOR-ART

引句:「派工/週戳/LINE 全抄 run_nags/run_probe 既有慣例」

問題：這些慣例沒有涵蓋本案最關鍵的寫入與成本語意。`run_nags` 不派 agent；`run_probe` 把失敗吞成 fail-open；orchestrator 才有 JSON 結果解析與實際成本抽取、落帳。本案卻宣稱每篇成本可控，未規格化 `--output-format json`、成本抽取、落帳失敗通知或成本帳歸屬，因此「全抄既有慣例」及成本誠實性均不成立。

查證：`governance/autonomous-loop.sh:90-112`、`governance/autonomous-loop.sh:117-130`、`governance/autonomous-loop.sh:200-221`、`governance/autonomous-loop.sh:222-251`

## 測試（第 59–63 行）

### f8 — major

spec 段落：測試

引句:「②VERDICT 抽取:PASS/FAIL/缺行(fail-closed)」

問題：測試矩陣缺少會決定能否安全蓋章的負例：agent 非零退出但留下 PASS、timeout 後半檔、正文含偽造 PASS、PASS 與 FAIL 同時存在、結論不是最後一行、self-audit 寫入失敗、第一篇成功第二篇失敗後重跑。現有三態測試無法證明 fail-closed。

查證：`governance/autonomous-loop.sh:201-215`、`scripts/lumos:7578-7593`

## 實務隱患（第 65–71 行）

### f9 — major

spec 段落：實務隱患／守衛面

引句:「今天 2/2 抓到證明有牙」

問題：兩篇同日、同類型 CLI 樞紐筆記的 2/2 命中，不能證明自動 PASS 的偽陽風險可接受，更不能推出「本案沒把它變差」。現行 Check S 只提醒人派乾淨 agent，工具本身不驗證審計是否真的乾淨；本案新增的是 agent 單席判決直接觸發寫入，風險顯著高於原先人工決定何時蓋章。Spec 未定義 PASS 門檻、抽查率或自動章的有效期差異。

查證：`scripts/lumos:823-826`、`scripts/lumos:7578-7583`、`governance/review-reports/self-audit/2026-08-24-lumos-cli-read.md:116`、`governance/review-reports/self-audit/2026-08-24-lumos-cli-write.md:109`

## 下一步（第 73–75 行）

已讀，無 finding。

最嚴重 severity：blocker
