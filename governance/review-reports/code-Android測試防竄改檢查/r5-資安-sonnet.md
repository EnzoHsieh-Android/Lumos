severity: minor

## ①提示注入

已看,無。這一輪新增的外來文字進輸出的路徑,仍走 `_tg_cand` 裡的 `_out_clean`。類別路徑換成摘要沒有新增自由文字出口。

## ②讀寫與執行越界

已看,無。
- 本輪沒有新增 subprocess、檔案寫入或 shell 插值。
- 路徑摘要只用 `hashlib.sha256`。
- 建置檔與 CI 的分支整段移除,`_tg_retry_ok` 的 `git grep` 也跟著拿掉,攻擊面縮小。
- 公開檔的私有識別字:
  - 我從考場 `/Users/enzo/mOrangePos` 取出 `com.citrus`、403 個類別名和約 2600 個方法與變數名,對凍結 patch 的新增行比對。
  - 只命中範本通用名(`ExampleUnitTest`、`ExampleInstrumentedTest`)。
  - 沒有套件名,也沒有本機路徑。
  - 沒有可用的考場方法名。
- 建置檔與 CI 規則移出後,把測試搬走仍會被抓到(實測,同一個基準測試檔):
  - 搬進 `buildSrc/src/main/kotlin/` 會出 `tq/test-removed`。
  - 改名成 `.kts` 會出 `tq/test-removed`。
  - 改名成 `.kt.txt` 會出 `tq/test-removed`。
  - 搬進測試目錄下一個叫 `buildSrc` 的套件資料夾不會出候選,因為它仍是測試檔、函式鍵不變,行為也沒變。
  - 結論:沒有新的「改名或放進 buildSrc 就不再被當測試檔」旁路。
- 類別路徑摘要:`#`、sha256 前 16 碼、`…`、最內層後 100 字。不同的完整路徑要撞同一把鍵,得有 64 位元的雜湊碰撞,不是照常操作能走到的。

## ③非刻意、一步就能繞過的守衛

### S1 assume 身分的「標點兩側去空白」連字串常值頭尾的空白也吃掉,既有 assume 的字面改動不算新增
severity: minor
blocking: 否 — 要先有一個條件字串帶頭尾空白或標點旁空白的既有 assume,而且改動是刻意的,不是照常操作會走到的
引句:「    return re.sub(r"\s*([^\w\s])\s*", r"\1", text), k」
file: `scripts/lumos:48915`(說明文字同檔 `scripts/lumos:48857`「字串常值裡的空白差異照樣算(只在標點兩側去空白)」)
攻擊路徑:
- 誰:照常操作、被紅燈逼著讓測試過的 AI。
- 從哪裡:編輯一個已經在主線上的 assume,例如 `assumeFalse(System.getProperty("user.dir").contains(" "))`。
- 送什麼:只把字串常值 `" "` 改成 `""`。引號本身算標點,所以引號內側的空白被正規化掉。`contains("")` 恆為真,這個 `assumeFalse` 變成永遠跳過。
- 拿到什麼:`tq/skip-added` 不報,身分字串跟改前完全一樣。「字串常值 `"c i"` 跟 `"ci"` 仍不同」只對字詞之間的空白成立。
重現(臨時 repo,改前一個提交、改後一個提交):
```
python3.14 /Users/enzo/harness/lumos-tq-android/scripts/lumos test-guard --repo <臨時repo> --diff HEAD~1..HEAD
→ 作弊候選 0 條
```
對照:`contains(" ")` 改成 `contains("a b")` 會正確列出 `tq/skip-added`。
修法方向:空白正規化改在剝掉字串的 `blank` 文字上算,字串內容原樣保留。
歸因:有證據的原有漏查。修前版 `lumos_before test-guard` 用 `re.sub(r"\s+","",…)` 去掉全部空白,同一個改動同樣是 0 條。本輪只把範圍縮小到頭尾與標點旁,沒有變嚴重。

### S2 catch 裡的 `check(`/`require(` 被當成「有檢查」,讓「try 有 fail() 卻被 catch(Throwable) 吞掉」的候選消失
severity: minor
blocking: 否 — 同一缺口已存在:catch 裡放 `assertTrue(true)` 修前版就不報。這一輪只多了一種寫法,不是新缺口
引句:「catch_checks = has("assert", c.end(), cb_end) or has("infix", c.end(), cb_end) or has("check", c.end(), cb_end)」
file: `scripts/lumos:48822`
攻擊路徑:
- 誰:照常操作的 AI。
- 從哪裡:新增一支測試,`try { assertEquals(...); fail("expected") } catch (e: Throwable) { check(true) }`。
- 送什麼:catch 裡放無實質內容的 `check(true)` 或 `require(true)`。
- 拿到什麼:第二條判斷「try 裡的斷言被接住、catch 不檢查」因為 `catch_checks` 為真而不成立,`tq/catch-no-fail` 不報。斷言失敗被吞掉,測試仍綠。
重現(新增 `BazTest.kt`,只有上述一支測試):
- 修後版 `test-guard --diff HEAD~1..HEAD`:0 條。
- 修前版 `lumos_before`:列出 `tq/catch-no-fail`。
- 把 `check(true)` 換成 `org.junit.Assert.assertTrue(true)`:修前版也是 0 條,所以是同一類缺口。
歸因:有證據的修復回歸。這個具體寫法修前版會抓,修後版放掉。它沒有放寬其他規則:`try` 沒有 `fail` 時,`catch` 裡有 `require(` 反而會被列出,更嚴。

### S3 `lumos` 對 AI 的指令說明和 `--help` 仍宣稱 test-guard 看建置檔與 CI,實際已不看
severity: minor
blocking: 否 — 只是說明與行為不符。輸出最後「抓不到的」清單有寫明,沒有機制被繞過
引句:「放寬 Gradle 或 CI 的測試設定(推送前新增告警閘也會跑)」
file: `scripts/lumos:70965`(`scripts/lumos:72187` 的 argparse help 同樣寫「建置或 CI 的測試設定被放寬」)
攻擊路徑:
- 誰:照說明選工具的使用者或 AI。
- 從哪裡:讀 `lumos` 的指令說明或 `lumos test-guard --help`。
- 送什麼:因為相信「建置與 CI 有人看」,把 `ignoreFailures` 或 `-x test` 這類設定改進 `build.gradle` 或 CI 檔。
- 拿到什麼:閘照樣通過,守衛的覆蓋範圍和它對外宣稱的不一致。
重現:`grep -n '放寬 Gradle 或 CI' /Users/enzo/harness/lumos-tq-android/scripts/lumos`,再對有 `ignoreFailures = true` 的 `build.gradle` 改動跑 test-guard,得 0 條。
歸因:有證據的修復回歸。修前版這句話是真的,本輪砍掉建置檔與 CI 規則時沒有同步更新這兩處。

三項都是 minor、blocking 否:類別路徑摘要沒有鍵撞、搬走測試仍被 `tq/test-removed` 抓到、公開檔沒有私有識別字,另有一個窄範圍的字面空白漏洞、一個 `check(` 回歸、一處過期說明。
