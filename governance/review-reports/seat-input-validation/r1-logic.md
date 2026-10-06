severity: major

## logic-F1

severity: major  
blocking: 是  
引句:「只接受缺省／null／清單型 materials，每項必須是非空且不含 NUL 的字串」  
file: `scripts/lumos:23296`

輸入 `{"materials":["must-read.md"],"materials":[]}` 含重複欄位；Python 會靜默保留最後一值，使結果成為空清單並回 rc0 vacuous。spec 未要求偵測重複鍵，錯派工單因此可假豁免。應在 JSON 解析階段拒絕重複欄位，並補普通／`-O` 測試。

## logic-F2

severity: major  
blocking: 是  
引句:「每項必須是非空且不含 NUL 的字串。以具體欄位的 ValueError 進既有 rc2 分支」  
file: `scripts/lumos:23314`

輸入 `{"materials":["\ud800"]}` 可被 Python JSON 解析，且通過「非空、無 NUL」規則；POSIX 路徑編碼會拋 `UnicodeEncodeError`，目前材料讀取只捕捉 `OSError`、`UnicodeDecodeError`，結果是 traceback／非 rc2。應預檢不可編碼的路徑字串或明確收進輸入錯誤分支，並補普通／`-O` 測試。

Python 記憶體探針已確認重複鍵覆蓋與 surrogate 編碼錯誤；依限制未執行真 CLI。

已讀材料：

- `governance/review-reports/seat-input-validation/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`
- `governance/review-reports/seat-input-validation/preflight-intake.md`
- `governance/review-reports/seat-input-validation/r1-graph-context.txt`