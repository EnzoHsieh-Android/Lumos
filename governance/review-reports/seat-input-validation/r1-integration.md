severity: major

## integration-F1
severity: major  
blocking: 是  
引句:「每項必須是非空且不含 NUL 的字串。以具體欄位的 ValueError 進既有 rc2 分支」  
file: `scripts/lumos:23312`、`scripts/test_lumos.py:34014`

輸入 `{"materials":["\ud800"]}` 是合法 JSON；解析後字串非空且不含 NUL，會通過 spec 的全部預檢。其後 `Path.read_text` 編碼路徑時拋 `UnicodeEncodeError`，但材料讀取只捕捉 `OSError`、`UnicodeDecodeError`，結果是 rc1＋traceback，而非規定的 rc2 輸入診斷。新增測試也未涵蓋此類字串。設計須明定不可編碼路徑的 rc2 規則並在讀材料前驗完。

完整凍結 spec 已逐節讀完。其餘所限鏡頭未見具體退化：合法觀測仍規定 rc0，JSON 與既有越界帳欄位保持不變。僅以 Python 記憶體確認孤立 surrogate 會觸發 `UnicodeEncodeError`；唯讀沙箱未跑真 CLI。

已讀材料：

- `governance/review-reports/seat-input-validation/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`
- `governance/review-reports/seat-input-validation/preflight-intake.md`
- `governance/review-reports/seat-input-validation/r1-graph-context.txt`