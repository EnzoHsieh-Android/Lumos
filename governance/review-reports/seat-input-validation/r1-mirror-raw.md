severity: clean

已完整核對當前 spec 與 `governance/review-reports/seat-input-validation/` 本輪全部卷證，零 finding。

折入前後一致：

- 六席原報 5 條、blocking 3；encoding-F1 與 landing-F1 去重折入，原 major 等級仍完整保留。
- logic-F1 的觀察仍記為 HIT；僅「本案必修」判準由單問題辯方 evidence 排除，未抹除原報。
- 第一份雙問題報告的 minor／blocking true 矛盾有明載，整份未採用且原檔保留。
- S1–S4 定義與測試綁定一致；S2 已加入不可編碼字串、普通／`-O`、先驗後讀要求。
- UTF 路徑沿用 `os.fsencode` 的平台編碼與錯誤處理器，保留可編碼的 surrogateescape 路徑。
- `lands_in` 改至已有收貨三道及 seat-check 合約的 `Systems/design-loop`，未擴張原 14 個 read/traverse 原語責任。
- fold-check 的 reverse-omission 仍按 project 無 summary 提醒處理，未用程式現況摘要掩蓋。
- Unicode 紅測卷證為 160 斷言、66 綠、94 紅；生產函式未改。

未驗邊界：未重跑 CLI／測試、未檢查同輪外報告、未驗未來生產實作。