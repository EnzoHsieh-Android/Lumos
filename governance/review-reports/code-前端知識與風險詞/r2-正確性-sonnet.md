severity: major

審查範圍:修後版本 f14f6808 的 `scripts/lumos`、`scripts/test_lumos.py`。我走過正規式邊界、輸入實測和改壞實驗,也用修前版本 d2297c94 對照。

發現 1、2 是重現過的缺陷,發現 3 是測試抓不住的改壞,發現 4、5 是低嚴重度。

1. e2e 資料夾底下的 `lib/`、`src/` 子資料夾被誤排出 infra(歸因:有證據的修復回歸)
severity: major
   blocking: 是
   - 問題:`_TEST_INFRA_PATH_RE` 開頭的 `^(?!(?:[^/]+/)*?(?:src|lib)/)` 是整條路徑任一處出現 `src/` 或 `lib/` 就否決。程式註解與 S50 寫的是「e2e 不在 src/、lib/ 底下」,但這個寫法連 e2e 之下的 `lib/` 也否決了。
   - 具體例(修後版本 `_stack_key_for_file`):
     - `e2e/lib/db.py` 回 `py`(修前 `infra`)。
     - `e2e/src/helpers.ts`、`tests/e2e/lib/util.ts`、`apps/web/e2e/support/lib/x.ts` 都回 `None`(修前都是 `infra`)。
   - 隔離重現(只改 `e2e/lib/h.py`,內容 `import requests; r = requests.get(url)`):
     - 修前:`stack_questions` 有 `infra`,`claims` 為空。
     - 修後:`stack_questions` 變 `py`,適用題也是 `py`,`claims` 多出 `e2e/lib/h.py`。
   - 後果:e2e 輔助程式改問產品程式的題,不再問 infra 的題(埠、逾時、殺程序、路徑),還會被當產品程式算 claims。
   - 測試缺口:`t_test_infra_path_tightened` 只測 `src/e2e/…`、`lib/e2e/…`(e2e 之上),沒有 e2e 之下的 `lib`、`src`。
   - 佐證:`file: scripts/lumos:30703`
   - 引句:「_TEST_INFRA_PATH_RE = re.compile(r"^(?!(?:[^/]+/)*?(?:src|lib)/)(?:[^/]+/)*?e2e/|\.e2e\.|」

2. 去處詞表漏掉常見去處,「由第三方處理」這類後句去處放過(歸因:有證據的原有漏查;前端語境收窄是本分支設計)
severity: minor
   blocking: 否
   - 輸入實測,修後都不回「對外送出」:
     - `系統送出請求通知供應商`:「供應商」不在詞表,「廠商」在。
     - `系統送出請求，由第三方物流處理`:去處在逗號後的下一子句,子句邊界把它切開。
     - `表單送出 Slack 通知`:Slack、email 等也不在詞表。
   - 這是設計取捨,不是實作錯。但「該判高被判低」的窗口確實存在,詞表不全。要不要補「供應商、平台、服務商」,交編排者裁。
   - 引句:「_PITFALL_SEND_DEST = r"(?:[給至往向對予]|外部|第三方|客戶(?!端)|廠商|銀行|物流|partner|external)"」

3. 測試抓不住「客戶端」排除、80 字範圍與多數去處詞(歸因:修補新增的行為,測試漏守)
severity: major
   blocking: 是
   - 做法:我把實作逐項改壞,跑 `t_door_keyword*`、`t_stack_key`、`t_test_infra*`、`t_infra*`、`t_req_fe*` 等相關測試,看哪些變紅。
   - 沒有任何行為測試變紅的改壞(只有 `t_door_rule_version_pin` 因指紋變而紅,換新指紋就全綠):
     - 拿掉 `客戶(?!端)` 的排除:`客戶端送出請求` 修後不回,改壞後會回,測試照綠。這是修補明說要收窄的行為。
     - 80 字範圍改成 20 字或 400 字:照綠。`t_door_keyword_send_long_line_linear` 只量速度,不驗範圍的語意。
     - 單獨拿掉 `向`、`對`、`予`、`往`、`第三方`、`廠商`、`銀行`、`物流`、`external` 任一個:照綠。S45 的例句每句都有第二個去處字或詞兜底,例如「向第三方物流」「予客戶」。
   - 有抓到的:去掉 `給`、`外部`、`partner`、「收到」排除、第三個分支、各 PAYMENT 尾碼、全形逗號。
   - 注意:我的複本環境裡 `t_pitfalls_frontend_three_entries_agree` 一開始就紅(沒有 git 環境),所以那個鍵的紅燈不算。
   - 引句:「hits = ("系統會向客戶送出請求", "後端送出請求向第三方物流", "對第三方送出請求", "送出請求予客戶", "送出表單資料到外部客服系統",」

4. 去處字太普通,前端例外很容易失效(歸因:有證據的原有漏查;去處字原本就有「給至往」)
severity: minor
   blocking: 否
   - 輸入實測,修後都回「對外送出」,等於前端例外沒生效:
     - `按鈕在請求完成前至少不會送出第二個請求`:「至少」的「至」。
     - `表單對話框送出後顯示成功`:「對話框」的「對」。
     - `送出請求後收到回應再往下`:「往下」的「往」。
   - 方向是多報,不會讓該判高的被判低。但這正是這次修補要消的誤報,而且詞表單字去處越多越嚴重。

5. 殺程序題只認選項附參數緊貼的 `xargs`(歸因:有證據的修復不完整;修前完全沒認 xargs)
severity: minor
   blocking: 否
   - 輸入實測,`infra-pid` 與 `infra-signal` 都不亮:
     - `xargs -I {} kill -9 {}`
     - `echo $PIDS | xargs -r -n 1 kill`
     - `xargs -I % kill %`
     - `process.kill (pid)`(括號前有空格)
   - 原因:`(?:-\S+\s+)*` 只吃選項字串,吃不掉分開寫的參數。
   - 亮的:`xargs kill`、`xargs -I{} kill {}`、`xargs -n1 -r kill`。
   - 引句:「|(?<![A-Za-z0-9_])xargs\s+(?:-\S+\s+)*)\s*"」

已驗過沒問題的:
- 效能:十萬字的「給」、「請求送出給」重複兩萬次、「對對對送」重複三萬次,門與 `--check` 都在 0.5 秒內跑完。
- `PAYMENT_TIMEOUT`、`PAYMENT_TIMEOUT_MS`、`ORDER_PAYMENT_TIMEOUT`、`PAYMENT_MAX_RETRIES` 正確放過。
- 以下都照算金流:`PAYMENT_TIMEOUTS`、`PAYMENT_TIMEOUT_URL`、`PAYMENT_API_KEY`、`PAYMENT_AMOUNT_LIMIT`、`PAYMENT_GATEWAY_TIMEOUT`、`payment_timeout`、`Payment_TIMEOUT`。
- `EXPORT=1`、`SUPPORT=1`、`REPORT=x` 不亮 `infra-shared`。
- `客戶端送出請求` 不命中;`客戶端送出請求到伺服器` 命中,符合設計。
- 80 字邊界:去處在送出前 80 字內命中,81 字時前向分支不命中,但裸「送出」分支仍命中(因為前面沒有請求或表單),所以不會漏。

未驗範圍:
- `pitfalls --check` 對 NFKC 會折成 `。` 的半形標點(例如 U+FF61)是否與門一致,我沒逐一實測。
- `_req_frontend_hit` 的版本號緊貼寫法(Vue3、React18)沒做改壞實驗,因為我的替換錨點沒對上。
- 計劃與筆記內容沒審。

三問回答:
- ① 原問題的修復效果:送出去處字與去處詞、PAYMENT 尾碼、全形標點、xargs 與 `process.kill`、`PORT` 前綴這幾條,我的輸入實測都有行為證據。e2e 路徑部分有一處回歸(發現 1)。
- ② 修補處的相鄰路徑:發現 1 的 e2e 之下 `lib`、`src` 修前後結論相反;發現 5 的 `xargs` 變體仍漏。其他相鄰路徑(`.sh`、`tests/e2e/…`、`playwright/e2e`、`cypress/e2e`)結論與預期一致。
- ③ 新發現在修前、修後各是什麼結果:
  - 發現 1:修前 `infra`,修後 `py` 並多出 claims。
  - 發現 2、4:修前就是這樣,歸因為原有漏查。
  - 發現 3:修前沒有這些行為,測試漏守是新行為造成。
  - 發現 5:修前完全不認 `xargs`,修後認一部分。
- 補充:`scripts/e2e_test.sh`、`scripts/run_test.sh` 因檔名含 `_test.` 被 `_PITFALL_DIFF_TEST_PAT` 先擋、拿不到 infra 題。修前修後結果相同,計劃也已明文列為不收,所以不當 finding。

最嚴重 severity: major,blocking 共 2 條(發現 1、發現 3)。
