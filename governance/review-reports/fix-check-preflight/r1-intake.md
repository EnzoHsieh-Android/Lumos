# 設計首輪前掃

preflight-4: ran

- 未定義詞、壞引用、範圍矛盾：前掃未報。
- 語意驗證 PF1 HIT：舊新增測試只有 `launches == 2`，runner 日誌只寫 cwd 與依賴連結，未識別兩段方法。原句「兩段 runner 都啟動」的背書從總次數改為記錄 `method` 並精確比對修正方法與合約方法各一次；紅綠控制仍保留。PF1 的重大後果可能被原有反向控制捕捉，本次不據此降級，補強驗證身份且原始報告不改。
- 提示驗證 PF2 HIT：原測試只驗任何 note 含未執行與重跑，改為同一提示包含修正測試、合約測試、未執行與重跑；不新增兩行輸出規則。
- 核心裁定與條款文字未改，修的是測試背書。正式程式仍未修改。

## 正式設計收貨與處置

- logic-F1 HIT：用忽略 record 的暫存突變跑原有五支測試，49 斷言全綠；單獨不合法類別仍啟動兩段。重現卷證 r1-findings-repro.json。已把單一 record 與混合錯誤分開測；核心原條款未降級。
- integration-F1 HIT：同一 consumer HEAD、同一紀錄，舊程式啟動兩段而原型零啟動，治理事件的 gate/kind/head_sha/loop/round/record_sha256/failed_items 都相同，只有 CLI notes 可知未執行。已在計劃追加可選 not_run_items 清單、相容舊列與 mapper 條款 S6；沿用原事件種類，不擴大放行條件。
- 兩條都有具體機械反例，免辯方直接折入；不接受、不降級。
- 四份 clean 報告 report-normalize/refcheck/seat-check 均過；quote-check 因零引句回 2，明記不適用且不宣稱全錨。它們零 findings、無處置清單；處置載體採有原文引句且 quote-check 過的 logic。沿用處置閘既有零發現略過語義，不更改報告或加假引句。
- 本輪六席原始報告先收齊才動 spec 或測試。原文行號 refcheck 只證存在，具體語意靠上述機械反例與方法身份，不拿行號存在當精確引句證據。
