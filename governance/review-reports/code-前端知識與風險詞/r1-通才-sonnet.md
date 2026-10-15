severity: major

通才鏡頭共 3 條,最嚴重 major(1 條),其餘 2 條 minor。表態記錄裡 py-eventloop、py-parallel、py-memory、py-hotpath 的 na 我讀 diff 後同意,改動確實沒有 async 或熱迴圈。

**固定席節點:** 這份 diff 不影響各節點宣稱的行為,我沒找到破壞點。

- lumos-cli-read(search 排除 superseded):沒動 search。
- 測試假綠形態、bound-tests-gate:新測試都有前置斷言(命中的對照組),也都有翻紅對照組。
- design-loop(spec 型審查的處置閘)、guard-kill、lumos-cli-lifecycle:diff 沒碰這些路徑。
- pitfalls-code-loop(RISK 節點):這次改動就落在它的範圍內,見下面 F2。
- 其餘「超出上限只列名」的節點:我沒逐一展開,不下判斷。

## F1 「送出請求」只認 給/至/往/到 四個去處字,其他去處寫法門被判成風險低
severity: major
blocking: 是

- **diff 位置:** `_PITFALL_SEND_RE` 的第 4 個分支 `(?<!請求|表單)送出(?!請求|表單|第[二兩2][個次]請求)`,與第 1 個分支 `送出(?=[^,.;!?。、\n]*[給至往])`。
- **問題:** 送出後面接「請求」就整個放行,只靠後面同一句有 給、至、往 或緊貼的「到」救回。去處用「向、對、予、打」寫,或去處寫在前面,就被當成前端語境,整行不命中 external-send。「請求送出」(前綴是請求)同樣放行。原本裸字「送出」一律命中,這是新增的漏判,規則版本 13 的註解寫「只會少命中」。
- **重現:** 在 web-fe-knowledge 工作樹用 `m._door_keyword_hits(行)` 呼叫,結果全是空清單,沒有任何類別命中:
  - 「系統會向客戶送出請求」
  - 「後端送出請求向第三方物流」
  - 「對第三方送出請求」
  - 「排程會送出請求打外部 API」
  - 「送出請求予客戶」
  - 「將重試請求送出」
  - 「排程把補發請求送出」
  - 「系統於逾時後自動送出請求(含客戶 ID)」
- **後果:** 只靠「送出請求」字樣、沒有別的風險詞的計劃,門判成低,可以直接實作、不派設計審。
- **測試為什麼抓不到:** `t_door_keyword_send_with_destination_still_hits` 只測 到、給、至 三種寫法,拿掉「向、對」也照綠。
- 引句:「送出(?=[^,.;!?。、\n]*[給至往])|(?<=請求|表單)送出(?=到)|送出(?=(?:請求|表單)到)」

## F2 目錄名 seeds/fixtures/e2e 或檔名帶 seed 的檔,連產品型樣的 claims 掃描都跳過,正式環境用的 seed 刪除語句不計入風險分級
severity: minor
blocking: 否

- **diff 位置:** `_TEST_INFRA_PATH_RE` 與 `_pitfall_diff_collect` 裡新增的 `and not _TEST_INFRA_PATH_RE.search(cur_file)`。
- **問題:** 正規式第三種形狀的 `.sh` 檔名只要含 seed 就算測試基礎設施,例如 `scripts/seed-prod.sh`。目錄 `db/seeds/` 底下的任何檔也算,例如 `db/seeds/prod_cleanup.sql`。這些檔寫 `DELETE FROM`、`DROP TABLE` 不再產生「寫入有沒有交易包裹?」這類 claim。
- **重現:** 臨時 repo,分支只新增 `db/seeds/prod_cleanup.sql`(內容 `DELETE FROM users WHERE 1=1; DROP TABLE orders;`)和 `scripts/seed-prod.sh`(內容 `psql "$PROD_URL" -c "DELETE FROM users"`)。執行 `lumos pitfalls --diff main..HEAD --no-lint`,輸出 `tier: standard(有程式檔改動、沒命中風險型樣)`,沒有任何 claim。對照:同一個分支多放 `scripts/cleanup.sql` 寫 `DELETE FROM users;`,就出現該 claim,tier 變 high。
- **降級原因:** 計劃明講這是設計取捨(示範 order-web 的 e2e 腳本),而且這次分類只依路徑樣式,沒有 sql 以外的其他訊號補回來,所以我標 minor,不標 major。
- 引句:「if (cur_file and _stack_changed_ok(cur_file, vend_skip) and not _TEST_INFRA_PATH_RE.search(cur_file)」

## F3 PAYMENT 例外把 _LIMIT、_COUNT、_WINDOW 這類業務限額也一併放行
severity: minor
blocking: 否

- **diff 位置:** `_PITFALL_PAYMENT_RE` 的尾碼清單 `TIMEOUT|TTL|…|LIMIT|COUNT|RETRIES|WINDOW`,中間允許任意數量的 `_[A-Z0-9]+` 段。
- **問題:** `PAYMENT_AMOUNT_LIMIT`、`PAYMENT_DAILY_LIMIT` 這類單筆或每日付款額度,是金流本身的業務參數,卻跟 `PAYMENT_TIMEOUT` 一樣被放行。
- **重現:** `_door_keyword_hits("PAYMENT_AMOUNT_LIMIT")` 回空清單。`PAYMENT_LIMIT 單筆上限` 也是空清單。
- **後果:** 一行只寫這個識別字、沒有「金流、退款、扣款」等其他詞的計劃,不會命中 payment。
- **為什麼降到 minor:** 計劃只例舉 TIMEOUT、RETRY_COUNT 這類技術參數,清單把 LIMIT、COUNT、WINDOW 也算進去,是範圍比實際需要寬。
- 引句:「|LIMIT|COUNT|RETRIES|WINDOW))(?![A-Za-z0-9_]))」

## 其他角度
- **被刪掉的行為:** `--check` 的 ✓/✗ 輸出整段搬進 `_pitfalls_check_print`,回傳值與印出文字逐字相同,沒有遺失。
- **跨檔追蹤:** `_stack_key_for_file` 新增的 `infra` 鍵,四個呼叫端(`_pitfall_diff_collect`、`_tension_candidates_into`、impact hook、`_review_role_for`)都不會因為多一個鍵而出錯。`_STACK_TRIGGERS` 從 specs 派生,不會漏掉 infra。
- **角色鏡頭副作用(不算 finding):** `e2e/`、`fixtures/`、`seeds/` 底下的 `.py` 與 `.ts` 檔,棧別鍵從 py、node、vue 改成 infra,`_review_role_for` 因此回 None,不再是 backend 或 frontend。diff 沒有說明這個副作用是刻意的,但我也舉不出具體壞處。
- **效率:** `_TEST_INFRA_PATH_RE.search(cur_file)` 放在逐新增行的迴圈裡,對同一個路徑重複比對。成本很小,不列為 finding。

最嚴重 severity:major(1 條 blocking)。
