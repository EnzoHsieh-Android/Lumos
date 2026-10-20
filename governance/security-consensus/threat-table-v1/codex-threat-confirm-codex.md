結論: 不可核可

定稿已補強多數問題，但入口分類仍會讓重要威脅完全不出題。以下三項必改；不需要新增證據種類。

1. **瀏覽器安全附問漏掉檔案與匯出入口。**

   原文：「瀏覽器會自動帶憑證或允許跨來源呼叫的 **http_api、web_page、admin** 另問……改狀態的請求怎麼防 CSRF?」

   反例：使用 cookie 驗證的 CSV 匯入端點登記為 `file_upload`，可以修改帳務資料，卻不會被問 CSRF。背景的 `kind` 是單一值，沒有自動繼承 `http_api` 題目的規則。CSRF 檢查應依是否涉及瀏覽器憑證與狀態變更判斷。[OWASP CSRF 指引](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

   **改法：**刪除這段的三種 kind 限制，改成「這個入口若供瀏覽器使用，且會自動帶憑證或允許跨來源呼叫，另問……」。Codex#2 的處置尚未完整做到它宣稱採納的「瀏覽器可達入口」。

2. **拆出 flow-sequence 後，批次與檔案匯入漏問業務流程。**

   原文：適用入口為「**http_api、web_page、webhook_in、message_consumer、admin**」；另規定「**跳步驟與竄改業務參數歸 flow-sequence**」。

   反例：`batch` 對已取消訂單出貨；`file_upload` 匯入負數數量或竄改單價。這些可以沒有注入、越權、重送或並發，因此其他類別不能補上。

   **改法：**適用入口至少加入 `batch`、`file_upload`、`cli`，涵蓋批次、匯入與管理命令的流程操作；沒有此類流程才判不適用。Claude#S5 拆類的理由成立，但拆完的入口對映不完整。

3. **audit 排除仍需追查的敏感操作。**

   原文：適用入口為「**admin、http_api、webhook_in、message_consumer、batch、export**」。

   反例：登記為 `file_download` 的病歷下載、`file_upload` 的帳務匯入、`web_page` 的帳號管理表單，都不會被問「誰做了什麼、成功或被拒、事後能否追查」。`data-exposure` 只問資料是否外洩，不能補上事件紀錄。[OWASP 日誌指引](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

   **改法：**加入 `web_page`、`file_upload`、`file_download`、`cli`；模板限定應記錄的安全相關操作與敏感資料存取，不要求記錄每一次普通瀏覽。Codex#11 以「會改狀態或帶走資料的六種入口」作為排除理由不成立。

**其他處置理由：**

- 拆分秘密管理與密碼學、部署面另標 `config-deploy`、人工替代使用 `review + manual_check_scope`、動態掃描不抵行為證據，理由成立。
- outbound 不套全部入口，配合強制另登 `outbound_call`，可接受。
- Codex#4、#6 的「CLI 操作者自己跑，所以沒有跨信任邊界」不能當一般原則。AI 或本人啟動 CLI，仍可能處理外來檔案、遠端資料或高權限操作。#6 的另登 `batch/file_upload` 可作補救，但必須成為定稿的明文盤點要求，不能只留在處置理由。

**單人可行性：**本機小規模並發、惡意輸入反例與故障敏感度測試，本身沒有必然做不到的下限。但背景要求人工審查且審查人不得是作者：AI 撰寫、人實際核對可以符合；若唯一的人也是作者，便需要另一位人類審查者，不能用另一個 AI 代替。這是既有背景限制，不能宣稱所有單人工作方式都能獨立完成。

本次僅審查文件，未修改任何檔案。


