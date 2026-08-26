### ext-f1 / 否決不成立

引句:「回放只證「判定邏輯+帳未變」,不證判定正確」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:42`  
佐證:file: `scripts/test_lumos.py:15951`  
佐證:file: `scripts/test_lumos.py:16077`  
佐證:file: `scripts/test_lumos.py:16190`  
佐證:file: `scripts/lumos:10236`

說明:「CI 已跑全套測試，所以 golden replay 沒增量」這個否決不成立。現有測試確實密集覆蓋 disposal 的人工 fixture，包括正常判定、路由、壞帳與缺欄等；但 fixture 驗的是作者預先想到的局部狀態。回放則遍歷實際凍結帳、各席報告、snapshot、路徑解析及 SHA 關係，能抓到 fixture 未建模的歷史資料形狀、真檔遺失或事後變動。它的增量是「真帳整合回歸」，不是再次單測判定函式。

不過 spec 已誠實限定它不證明判定正確；golden 若由當下同一份邏輯 `--freeze` 自產，也不能成為獨立正確性 oracle。故 S1/S2 可成立，但賣點只能是歷史相容性與資料完整性，不能升格成判定正確性回測。

### ext-f2 / major

引句:「任何 loop 判定漂移→LINE 喊人」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:32`  
佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:41`

說明:否決成立。spec 把所有漂移直接解釋成「讀側邏輯被改壞或帳被動」，漏掉第三種正常情況：判定制度經核准演進，而且本來就應該改變歷史輸出。此時全量 golden 變紅是預期結果，卻仍逐 loop 喊人。

目前沒有定義 golden schema/version、判定制度版本、核准 rebaseline 流程、預期差異清單，亦沒有把「輸入指紋變動」與「同輸入下判定變動」分流。fail-open 只避免阻斷主流程，不能避免 LINE 告警風暴及其後的告警疲勞。S4 在補齊版本化與合法漂移消音機制前，不宜照案實作。

### ext-f3 / major

引句:「全量 golden 回放,任何 loop 判定漂移」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:32`  
佐證:file: `governance/autonomous-loop.sh:135`  
佐證:file: `governance/autonomous-loop.sh:241`

說明:否決成立。週跑雖可借既有排程，但「不建新排程」不等於沒有新增運算成本。spec 要求全量回放，卻沒有目前 loop 數、單 loop 檔案數與耗時基線、總時限、成長上界、增量策略、分批策略或超時後語意；golden 數量只會累增，因此成本是無界線性成長。

而既有週期工作已在同一 autonomous-loop 串行執行考卷等任務。新增全量 replay 若變慢，會延後同一 runner 後續工作。至少應先量測首批全跑 wall time，設定總 budget/timeout，改為「新 golden 必跑＋存量輪替抽樣」，並定義何時才升級為全量；否則 S4 的週跑成本沒有可驗收邊界。
