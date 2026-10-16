severity: minor

已逐類看過:
- 提示注入(①):已看,無。前端提醒那行只回印計劃全文裡命中的框架字樣(`_REQ_FE_WHEN` 限定的詞),不是自由文字。
- 讀寫與執行越界(②):已看,無。新增程式沒有 subprocess、環境變數、檔案寫入或下載。我對 diff 裡 scripts/lumos 的新增行和全 diff 做了關鍵字搜尋,沒有新密鑰或信箱。
- 風險詞例外(送出、`PAYMENT_*` 尾碼):已看,只有推論(見 F2)。
- e2e 路徑分流:F1。

## F1
severity: minor
blocking: 否
引句:「if (cur_file and _stack_changed_ok(cur_file, vend_skip) and not _TEST_INFRA_PATH_RE.search(cur_file)」
- 誰:使用者本人或照常操作的 AI,改了一支正式環境程式,檔案所在資料夾剛好叫 `e2e`。例子是端對端加密模組 `crypto/e2e/`,不在 `src/` 或 `lib/` 底下。
- 從哪:`lumos pitfalls --diff <範圍>`,也就是推送前的風險分級。
- 送什麼:`crypto/e2e/store.py` 新增 `requests.post(...)` 沒帶逾時,加上 `DELETE FROM orders`。
- 拿到什麼:`_TEST_INFRA_PATH_RE` 把整個資料夾當成測試基礎設施,掃程式碼型樣的那一段直接跳過,分級成 `tier: standard(有程式檔改動、沒命中風險型樣)`。同樣的內容放在 `app/charge.py` 就是 `tier: high`。結果是少了一次高風險審查。
- 重現:我在 /tmp 暫存 repo 實跑過,`crypto/e2e/store.py` 單獨改動時輸出就是 standard。程式註解只替 `src/` 與 `lib/` 開了例外。
- 為什麼降到 minor:被跳過的型樣只有 HTTP 逾時、`open(`、`SELECT` 的 N+1、`sleep`、`threading` 與 `INSERT/UPDATE/DELETE` 沒包交易。這些屬資源和併發,不是對外送出或金流的詞表,影響面窄。這個資料夾名稱撞名的前提也偏窄。
- file: `scripts/lumos:30703`

## F2(推論)
severity: minor
blocking: 否
引句:「(?<!請求|表單)送出(?!請求|表單|第[二兩2][個次]請求)」
- 誰:寫計劃的 AI。
- 從哪:`lumos pitfalls <計劃> --check`,以及門的關鍵字掃描。
- 送什麼:計劃寫「表單送出,系統轉發資料並通知客戶」。「送出」前後緊貼表單或請求,去處詞「客戶」又隔了逗號,不在同一子句。
- 拿到什麼:`external-send` 不再命中,少要一節「## 實務隱患」。
- 為什麼只算推論:真正的對外動作通常還會帶別的詞,例如 `webhook`、`send`、`對外`、`stripe`。我沒有造出一個只靠「送出」命中、改後會整個掉到零命中的實例,所以不升級。
- file: `scripts/lumos:8046`(`_PITFALL_SEND_WHEN` 定義處,對照 r2-snapshot.patch 約第 71–75 行)

最嚴重 severity: minor;blocking 共 0 條。
