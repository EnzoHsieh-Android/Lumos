severity: major

## rollback-F1
severity: major  
blocking: 是  
引句:「不得追加成功 canary 帳列或印成功訊息。」  
源碼佐證 file: `scripts/lumos:9523`、`scripts/lumos:9568`、`scripts/lumos:9589`、`scripts/lumos:9657`

設計漏了讀檔到記帳間的競態：報告先讀入、快照另讀來驗引句，之後才重新讀檔計算雜湊並追加帳本。具體輸入：載體起初有合法引句；驗完後、算雜湊前，另一程序把報告改成同 severity 但零引句。結果會把新版零引句報告的雜湊成功落帳，處置閘稍後才失敗，正是本案要避免的不可撤錯帳。

修正判準：報告與快照各自只讀一次 bytes，以同一份 bytes 解碼、抽引句及計算雜湊；或在追加前重讀並確認內容未變。需有可控換檔測試，證明競態時 rc2 且帳逐位元不變。

## 逐節覆核

- 問題與核心裁定：除 rollback-F1 外，`none` 真實 ID、全輪集合與單席數量分離正確。
- 驗收：普通與 `-O`、零引句、正向載體、缺失快照、空輪前置均有對應斷言；唯獨未覆蓋讀取後換檔。
- 編碼界線：`scripts/lumos:9568` 對非 UTF-8 仍會拋 `UnicodeDecodeError`，因只捕捉 `OSError`。這是既有錯誤；spec 明定新判準只處理有效 UTF-8，且未要求修復該例外，因此不列 finding。
- 回退：新守衛在追加前拒收，不產生外部不可逆狀態；撤回局部功能即可恢復寫側，歷史帳與收據不需清除。
- 風險：併發有上述阻斷洞；效能僅線性掃描，資源沿用既有整檔讀取，無新增外部送出；金流、正式資料、Windows 排除合理。
- 合約：落盤讀回合約不受影響；second telemetry 不受影響；處置閘第五步不變；假綠合約已有 loop、snapshot 與 `reported` 前置斷言，未見破壞。

最嚴重：major；blocking findings：1。受唯讀沙箱限制，未建立 CLI 現場或重跑測試，以上為逐行靜態覆核。

已讀材料：

- `governance/review-reports/carrier-quote-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/carrier-quote-preflight/preflight-intake.md`
- `governance/review-reports/carrier-quote-preflight/r1-graph-context.txt`