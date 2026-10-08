severity: minor

## receipt-F1

severity: minor  
blocking: 否  
引句:「在本案CLI與卷證入口核對十份真實編碼拒收及恢復收據」

重驗入口仍缺可重放的收據格式與保存位置。非法快照會在寫帳前拒收；`cmd_canary` 的成功 append 位於 `scripts/lumos:9679`，快照檢查則在此前完成（`scripts/lumos:9576`）。因此失敗案例不會自然留下 canary 帳列。

具體情況：連續執行十次非法輸入，只看到終端輸出，之後無法證明使用的 CLI 指紋、輸入 bytes、rc2、stderr、帳前後雜湊及配對恢復成功；仍可能被口頭計成「十份真實收據」。建議在 REVISIT 明定每份收據的必備欄位、失敗與恢復的配對規則、保存到哪個 Verification／卷證路徑，以及重驗命令。

## 其餘各節

- 範圍與回退：已限制為本案例外分支；明定保留零引句、報告編碼、換檔、負數守衛，不關閉整個 Unicode Issue。無 finding。
- 版本紅綠：34、38、42 三版數字分列，原始收據不得互覆；生產 CLI 明示尚未修改。CLI SHA256 確認為 `52c9c4…0276`，且相對 `53d1c458` 無差異。無 finding。
- 殺傷力：RuntimeError 與缺檔普通／`-O` 控制能殺掉廣捕捉 mutant；未把 mutant 結果冒稱生產已修。無 finding。
- 撤除：RETIRE-IF 要求共用嚴格入口且控制持續綠，並禁止吞錯或替換字元。無 finding。
- 合約：處置閘第五步不變；S1–S4 均有測試綁定，未具體破壞所附唯一 INVARIANT。
- 風險：併發保留同份 bytes 與後置雜湊核對；效能／資源沒有額外讀取或背景工作；不對外送出、無金流與不可逆操作；守衛面由四條驗收覆蓋。排除理由成立。

`refcheck` 實跑：0 壞引用。單一紅測試重跑因唯讀環境沒有可用暫存目錄，在測試啟動前中止；這是審查環境限制，不算產品問題，也不冒稱本席重跑了42條。

總結：最高 severity 為 minor；blocking 0。

已讀材料：

- `governance/review-reports/snapshot-encoding-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/snapshot-encoding-preflight/preflight-intake.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-graph-context.txt`