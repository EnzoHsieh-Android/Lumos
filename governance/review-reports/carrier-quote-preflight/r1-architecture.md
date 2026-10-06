severity: minor

## architecture-F1

severity: minor  
blocking: 否  
引句:「只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。」

非 UTF-8 快照的寫側結果沒有釘死。具體輸入：零引句載體報告＋內容为 `ff fe` 的快照。現況嚴格解碼只捕捉 `OSError`，會漏出 `UnicodeDecodeError`、得到 rc1/traceback；若實作者依「只在有效 UTF-8 時辨認」改成略過檢查，又會把必然被讀側拒絕的載體寫進不可撤帳本。讀側已把同一情況視為可預期失敗。spec 應明定走 rc2、不得追加帳列，並補相應驗收案例；目前 S4 只覆蓋檔案缺失。

源碼佐證 file: `scripts/lumos:9565`  
源碼佐證 file: `scripts/lumos:9585`  
源碼佐證 file: `scripts/lumos:22925`  
測試缺口 file: `scripts/test_lumos.py:25638`

## 四問

① 分層與依賴方向：其餘乾淨。`cmd_canary` 在寫側呼叫共用 `_quote_rows`；處置閘仍自行讀回重算，沒有寫側直呼讀側閘，也未削弱其權威。對照 `scripts/lumos:9560`、`scripts/lumos:22330`、`scripts/lumos:22870`。

② 命名／例外／返回碼：載體以 `findings_set` 是否存在辨認，與讀側一致；零引句由 `_quote_rows` 的 `None` 表示。rc2 符合既有無效輸入慣例，唯 Unicode 解碼例外如 F1 未定。對照 `scripts/lumos:9305`、`scripts/lumos:22344`、`scripts/lumos:22812`。

③ 第二種做法：未發現另造抽取器、另設載體判準或讓寫側取代處置閘；沒有第二種做法。對照 `scripts/lumos:22330`、`scripts/lumos:22925`。

④ lands_in：落在 `Systems/canary-audit` 合理；改的是記帳前拒收。`design-loop` 與測試假綠節點是相依合約，不是新行為落點。對照 `governance/review-reports/carrier-quote-preflight/r1-snapshot.md:11`、`scripts/lumos:9163`。

## 合約與風險

- 落盤可讀回：拒收位於 append 前，不破壞；成功仍經讀回自驗。`scripts/lumos:9657`
- second 純 telemetry：未觸及，且 second 無 loop 欄。`scripts/lumos:9717`
- 處置閘第五步計劃／條款合約：未改。`scripts/lumos:23025`
- 還原翻紅前置：新測試帶 loop、snapshot，並以錯誤訊息及 reported 路徑證明命中；合法正向與空輪另控。`scripts/test_lumos.py:25612`
- 併發：零引句判定只依報告；快照內容競態不改此判定。
- 效能／資源：沿用既有單次全文讀取與抽取，沒有新增無界工作。
- 回退：局部寫側守衛，可回退；歷史帳不改。
- 外部送出：無。
- 守衛：普通與 `-O`、正反控制齊；僅缺 F1 編碼案例。

最嚴重 minor；blocking 0。未建立新 CLI 現場，以上為唯讀開碼覆核。

已讀材料：

- `governance/review-reports/carrier-quote-preflight/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/carrier-quote-preflight/preflight-intake.md`
- `governance/review-reports/carrier-quote-preflight/r1-graph-context.txt`