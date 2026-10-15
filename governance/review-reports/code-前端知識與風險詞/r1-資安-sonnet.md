severity: minor

①提示注入已看,無。②讀寫與執行越界已看,無:diff 沒有新的 shell 插值、下載來源、密鑰或信箱,也沒有 hook 去執行不可信位置的檔。測試裡的 `subprocess.run` 只跑本 repo 自己的 `GRAPHCTL`。表態記錄的 py-external 一題是 satisfied,我沒有找到和它矛盾的證據。③守衛被意外走過:有三條,都是縱深類。

### 1. 路徑分流讓放在 seeds、fixtures 資料夾的正式環境程式不掃風險型樣
severity: minor
blocking: 否
引句:「if (cur_file and _stack_changed_ok(cur_file, vend_skip) and not _TEST_INFRA_PATH_RE.search(cur_file)」
- 誰:照常操作的 AI 或使用者本人。
- 從哪:改 `db/seeds/prod_backfill.ts`、`prisma/seeds/*.py` 這類資料夾名恰為 `seeds`、`seed`、`fixture(s)`、`e2e` 的程式檔。Rails 風格的 `db/seeds` 本來就會在正式環境跑。
- 送什麼:檔內有 `DELETE FROM users WHERE ...` 或 `UPDATE ... SET ...`。
- 拿到什麼:這些行不產生 claims,`_pitfall_tier` 從 high 降成 standard,「寫入有沒有交易包裹」那題不出現。計劃自己寫「仍要一席審」,所以不是整道閘消失,是少了 high 才有的代碼審。
- 說明:正則只看資料夾名,不看內容或用途。`seeds/` 和 `fixtures/` 是否真的只給測試用,diff 裡沒有機制確認。

### 2. payment 例外把 LIMIT、COUNT、RETRIES、WINDOW 當成無害參數
severity: minor
blocking: 否
引句:「r"|LIMIT|COUNT|RETRIES|WINDOW))(?![A-Za-z0-9_]))")」
- 誰:照常寫計劃的 AI。
- 從哪:計劃正文只寫 `調高 PAYMENT_RETRY_COUNT 到 5` 或 `PAYMENT_LIMIT 改 10 倍`。
- 送什麼:全大寫識別字,以 `_LIMIT`、`_COUNT`、`_RETRIES`、`_WINDOW` 結尾。
- 拿到什麼:我用 python3.14 跑過,這幾個字串 `payment` 都不命中,門判成 low,可能不走設計審。扣款重試次數會直接影響重複扣款,金額上限是金流語意。
- 說明:計劃的 d1 把 `ORDER_PAYMENT_RETRY_COUNT` 明寫成例子,所以這是已裁定的放寬。風險仍在:`TIMEOUT`、`TTL`、`DELAY` 之類是純時間參數,`LIMIT` 和 `RETRIES` 不是。
- 補充:此例外只作用於計劃文字的門判定。程式 diff 的分級走 `_PITFALL_DIFF_PATTERNS`,不受影響。

### 3. 「送出」前端語境例外,在去處不用給、至、往寫時會漏
severity: minor
blocking: 否
引句:「r"|(?<!請求|表單)送出(?!請求|表單|第[二兩2][個次]請求)")」
- 誰:照常寫計劃的 AI。
- 從哪:計劃正文寫 `送出請求(POST 到銀行)`、`送出請求 to partner API`、`送出請求,包含客戶資料到外部`。
- 送什麼:「送出請求」後面沒有緊貼「到」,同一子句也沒有給、至、往。
- 拿到什麼:我跑過這三種寫法,`external-send` 都不命中。如果同一段也沒有 webhook、notify 等其他詞,門判 low。
- 說明:對外送出而不用給、至、往、緊貼到的寫法,仍會被判成前端語境。多數真實寫法會被「給」「至」接住,所以只列 minor。

最嚴重 severity:minor,blocking 共 0 條。
