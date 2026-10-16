severity: major

這份 diff 在提示注入、讀寫與執行越界、密鑰與信箱三類上已看,無。第③類(守衛被意外走過)有 1 條 major 和 1 條 minor,明細在下面。

## 逐類結論
- ① 提示注入:已看,無。`_req_frontend_hint` 和 `_pitfalls_frontend_print` 印出的是 `_REQ_FE_WHEN` 比對到的固定詞,不是任意計劃文字。`when_raw` 只用在筆記比對,不進派工詞。
- ② 讀寫與執行越界:已看,無。diff 沒新增 hook、安裝腳本、下載網址、環境變數覆蓋或路徑寫檔。測試裡的 `subprocess.run([sys.executable, GRAPHCTL, "pitfalls", ...])` 是固定引數列表,沒有 shell 插值。
- 密鑰與信箱:已看,無。`PAYMENT_API_KEY`、`PAYMENT_SECRET` 只是測試用的字串,不是真憑證。
- ③ 非刻意走過守衛:發現 1 和 2。

### 發現 1
severity: major
blocking: 是
引句:「(?<!請求|表單)送出(?!請求|表單|第[二兩2][個次]請求)」
攻擊路徑:
- 誰:照常寫計劃的使用者,或照常操作的 AI。
- 從哪裡:計劃或 spec 裡的前端日常句,例如「表單送出到 Slack 頻道」「請求送出至 Salesforce CRM」。
- 送什麼:送出前面是請求或表單,去處是外部服務,但不是詞表裡那十一個詞(給、外部、第三方、客戶、廠商、供應商、銀行、物流、平台方、partner、vendor、external)之一。
- 拿到什麼:`external-send` 風險類沒被命中,計劃風險判低。本該進的代碼審或設計審被放過,對外送出資料的路徑沒人審。

我把修後 20df2187 的 `_PITFALL_SEND_WHEN` 實際編出來,餵 NFKC 後的句子,結果如下。
- 判低(沒命中)的句子:「表單送出到 Slack 頻道」、「請求送出至 Salesforce CRM」、「表單送出後把 email 寄到 Mailchimp」、「請求送出到 Datadog」、「表單送出至 OpenAI API」、「請求送出到合作夥伴」、「送出請求到 S3 bucket」、「表單送出後同步到 Google Analytics」。
- 照常命中的句子:「表單送出給客戶」、「請求送出到第三方」。

改前的 `送出` 是裸字,這些句子都會命中。這次改動把它們判低了,而判低靠的是「去處必須寫成詞表裡的外部名詞」。真正的外部服務名(Slack、Salesforce、Mailchimp、OpenAI、S3 等)、「夥伴」、「對方」都沒列。程式註解自己寫明「到」「至」不算去處,所以這是設計取捨,不是疏漏。但被放過的句子有真實的對外送出,這正是你點名要查的那一項。

### 發現 2
severity: minor
blocking: 否
引句:「(?:[^/]+/)*?e2e/|\.e2e\.|(?:^|/)(?:[^/]*[._-])?e2e(?:[._-][^/]*)?\.sh$」
攻擊路徑:
- 誰:照常操作的 AI 或使用者。
- 從哪裡:改了路徑裡任何一段資料夾叫 `e2e`、檔名帶 `.e2e.`、或 `.sh` 檔名以 e2e 開頭或結尾的正式程式,例如 `services/e2e/mailer.py`、`api/auth.e2e.ts`。
- 送什麼:這些檔的新增行。
- 拿到什麼:`_is_test_infra_file` 為真,這些檔改拿 infra 題組,pitfalls 的 claims 不再掃交易包裹、N+1 這類產品型樣,語言本身的棧別題也被換掉。這支檔少審一層。

我實測過這些路徑,`app/e2e/handler.py`、`server/e2e/pay.ts`、`api/auth.e2e.ts`、`services/e2e/mailer.py` 都判為測試基礎設施,只有 `src/e2e/` 底下的會被排除在外。diff 的註解已承認這個天花板(`crypto/e2e/` 這類產品資料夾仍會被當 e2e),所以只標縱深防禦。

最嚴重 severity: major,blocking 共 1 條
