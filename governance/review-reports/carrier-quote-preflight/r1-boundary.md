severity: major

## boundary-F1
severity: major  
blocking: 是  
引句:「只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。」

S4 只驗「路徑不存在」，沒有釘住「檔案存在但不是 UTF-8」。現碼預檢只捕捉 `OSError`；`UnicodeDecodeError` 不是其子類，而後續既有 IO 檢查只算二進位雜湊，不會診斷編碼。

具體輸入：合法、全錨格式的載體報告＋內容为 `ff fe` 的 snapshot → `read_text()` 拋 `UnicodeDecodeError`，CLI rc1 並印 traceback；不是規格要求的 rc2、明確快照讀取診斷。應把「存在但無法解成 UTF-8」納入 S4 與測試，直接 rc2 且帳逐位元不變，不能僅把它當 `None` 延後，否則二進位雜湊路徑可能繼續記帳。

源碼佐證 file: `scripts/lumos:9568`  
源碼佐證 file: `scripts/lumos:9588`  
源碼佐證 file: `scripts/lumos:22925`  
測試缺口 file: `scripts/test_lumos.py:25638`

## 逐節結果

- 問題與範圍：已讀，無其他 finding。
- 核心裁定／驗收：除 F1 外，零列以 `_quote_rows() is None` 表示；不成對引號會產生 `ok:false` 格式列，仍由既有全錨分支拒收，不會誤當零列。`none` 真實 ID、未填 findings、集合數不同的正向控制正確。
- 回退：局部回退後讀側仍拒絕，無 finding。
- 實務隱患／落點：除 F1 與「保留 IO 區別」字面衝突外，無 finding。

## 合約與風險

- canary 落盤可讀回：拒收位於 append 前，帳不變斷言相符；不破壞。
- second 純 telemetry：未觸及。
- 處置閘第五步條款綁定：未觸及。
- 假綠前置斷言：新測試已帶 loop、snapshot、reported 前置；無 finding。
- 併發：未新增共享狀態協調；局部判斷無新競態。
- 效能／資源：僅載體既有線性全文讀取，無無界新增。
- 回退／外部送出：可提交級回退；無網路、金流或正式環境送出。
- 守衛：F1 使文字／IO 邊界仍可 traceback，故阻擋實作。

未建立 CLI 現場：唯讀沙箱下只以源碼及 Python 記憶體確認 `UnicodeDecodeError` 非 `OSError`，未把沙箱限制算產品紅燈。

總結：最嚴重為非 UTF-8 快照繞過預期 rc2 診斷；blocking 1。

已讀材料：

`governance/review-reports/carrier-quote-preflight/r1-snapshot.md`  
`scripts/lumos`  
`scripts/test_lumos.py`  
`governance/review-reports/carrier-quote-preflight/preflight-intake.md`  
`governance/review-reports/carrier-quote-preflight/r1-graph-context.txt`