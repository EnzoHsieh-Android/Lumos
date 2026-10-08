severity: major

## integration-F1

severity: major  
blocking: 是  
引句:「保留原處置閘，舊帳仍以同樣判準拒絕；不清除歷史錯帳，不增減輪數，不重置前案。」

spec 只限定快照須為有效 UTF-8，未規定載體報告本身的編碼判準。寫側以 `errors="replace"` 讀報告，讀側卻嚴格解碼。

具體輸入：合法全錨報告末尾混入 `0xff`，快照為正常 UTF-8。寫側把壞位元替換後仍找到全錨引句，追加成功帳並回 rc0；讀側重驗同一檔時拋 `UnicodeDecodeError`，判閘失敗。這直接違反寫讀同判準，且留下不可撤帳。驗收測試只有正常 UTF-8 報告，未封住此路。

源碼佐證 file: `scripts/lumos:9523`、`scripts/lumos:9568`、`scripts/lumos:22926`、`scripts/test_lumos.py:25654`

## integration-F2

severity: major  
blocking: 是  
引句:「不得追加成功 canary 帳列或印成功訊息。普通與 -O 執行都驗；ID 包含 none 及一般 ID。」

spec 未要求「做引句判定的位元」必須與隨帳雜湊的位元相同，現有流程分次讀檔，存在檢查後換檔競態。

具體輸入：檢查先讀到含全錨引句的報告；在引句通過後、雜湊前，編輯器把報告換成正規化但零引句版本。工具會雜湊新版、追加帳列並印成功；讀側的雜湊重驗通過，最後才因零引句失敗。靜態測試檔無法覆蓋。設計應規定單次讀取位元同時供解析與雜湊，或在追加前驗證內容未變。

源碼佐證 file: `scripts/lumos:9523`、`scripts/lumos:9568`、`scripts/lumos:9585`、`scripts/lumos:9657`

## 其餘核對

前掃 PF1 成立：分支確由 loop＋auditor 觸發，新測試已補 loop、快照及 `reported` 前置斷言。PF2 的非 UTF-8 快照確會在寫側逸出，但 spec 是否納入仍未明定；F1 是更直接、且會成功落錯帳的對稱缺口。

合法空輪仍走無載體分支、重驗留痕而略過引句；舊帳讀側不變。相關合約逐條：落盤可讀回、不印假成功不受正常路徑破壞；second 純 telemetry 不受影響；條款綁定第五步不受影響；既有翻紅釘有前置斷言，但未覆蓋 F1/F2。

風險：併發為 F2；守衛為 F1/F2。效能僅沿用既有線性引句掃描；資源未新增長存資源；無外部送出。功能提交可回退，但已誤追加的帳不能撤，故回退不能消除兩項實害。

最嚴重為 major；blocking 共 2。唯讀沙箱未建立 CLI 現場、未重跑收據，這不是產品紅燈。

已讀材料：

- `governance/review-reports/carrier-quote-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/carrier-quote-preflight/preflight-intake.md`
- `governance/review-reports/carrier-quote-preflight/r1-graph-context.txt`