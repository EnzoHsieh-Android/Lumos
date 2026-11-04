severity: major

邊界可執行鏡頭,r1 spec 審查。

白話:這份設計在「正常的改動」上寫得很細。換到冷門輸入,例如改檔名、反引號函式名、整檔重排、第一次推新分支,有幾條規則會漏掉,或一次擋下一大堆。放行用的指紋又綁得太鬆,放行一次,同一檔的同類改動都跟著放過。

實驗在 `/tmp/lumos-seat-work/Android測試防竄改檢查/邊界-sonnet/` 的臨時 git repo 做,已用字面絕對路徑刪除。

## 逐節

- 〈問題與最小解〉、〈名詞〉、〈第二批〉、〈回退〉、〈審計修正紀錄〉:已讀,無 finding。
- 〈做法一〉:finding 1 到 12。
- 〈做法二〉:finding 4、5、10、11。
- 〈做法三〉Semgrep:已讀,無 finding。
- 〈做法四〉到〈做法六〉與〈驗收條款〉:finding 3、6、8、12 相關,見各條。
- 〈實務隱患〉:效能那條「跟改動大小成正比」只在括號配對一次掃完時成立,見 finding 4。

## Findings

### 1. 放行指紋的身分字串太鬆,放行一次就放掉同檔同類的所有後來改動
severity: major
blocking: 是(不改,放行出口等於整檔永久免檢,實作者會做出壞系統)
引句:「指紋 = sha256(規則代號、檔案、身分字串)前 16 碼;身分字串用」
- 段落:〈做法一〉「身分字串用『測試函式名』或『正規化後的那一行』」,規則 `tq/skip-added`、`tq/build-config`、`tq/ci-config`。
- 問題:`tq/skip-added` 的身分是正規化後的一行,例如 `@Ignore`,不含所屬函式名。同一檔裡第一條 `@Ignore` 放行後,之後任何人在同一檔新加的 `@Ignore` 指紋完全相同,靜默通過。`continue-on-error: true`、`|| true`、`-x test` 也是同樣的結構。
- 同一次推送加兩條相同行,spec 沒說是兩條候選共用一個指紋,還是合成一條。
- 現有的新增告警閘靠 `_lint_new_diff_claims` 的 `Counter` 算次數來避開這點(基準版一次、現在版三次才算新增兩條)。放行比對只看 `key in waivers`。
- 佐證:file: `scripts/lumos:38660`(`Counter` 次數比對)、file: `scripts/lumos:38837`(`kept = [c for c in new if c.get("key") not in waivers]`)。
- 要補的是:身分字串帶所屬函式名或區塊,並寫明重複行怎麼處理。

### 2. 檔案分類用「改動後路徑」,改名成非測試檔就整支消失
severity: major
blocking: 是(漏掉「刪測試」這個頭號作弊)
引句:「檔案分類(路徑一律用改動後的;改名用 git 的改名偵測對回改動前):」
- 段落:〈做法一〉「檔案分類(路徑一律用改動後的…)」、`tq/test-removed`。
- 重現:`git mv FooTest.kt Foo.kt.disabled`。實測 `--find-renames` 回 `R100|…FooTest.kt|…Foo.kt.disabled`。
- 照字面,改動後路徑不是 `.kt`,不屬於任何一類,所有函式都不見了卻沒有候選。
- 同類路徑:搬到 `src/main`,或改成 `.bak`、`.txt`。
- 純刪除的檔沒有「改動後路徑」,分類規則也沒定義。現有 `_lint_new_changed_files` 對 `D` 直接 `i += 2` 不收,如果「有沒有碰到五類檔」沿用它,整支測試檔被刪的推送連工具都不會載入。
- 佐證:file: `scripts/lumos:38490`(`elif code == "D"` 不收)。
- 要補的是:分類要看改動前與改動後兩個路徑,任一邊是測試檔就算。「碰到五類檔」的判斷要自己列含刪除的清單。

### 3. 「搬家不算」只比名字,加上改名偵測門檻,assert-weakened 與 expected-changed 被整批繞過
severity: major
blocking: 是
引句:「而且這次改動的其他測試檔裡也沒有同名函式(搬家不算)」
- 段落:`tq/test-removed`「其他測試檔裡也沒有同名函式(搬家不算)」、`tq/assert-weakened`、`tq/expected-changed`。
- 重現一(實測):小測試檔改名加改內容,斷言全換成 `assertNotNull`。相似度低於 50%,git 回 `D|ATest.kt|A|BTest.kt`。
  - `a`、`b` 兩個函式名在別的改動檔裡都有,`test-removed` 被抑制。
  - 兩個斷言規則都要求「改動前後同一檔的同名函式」,配不到,整組弱化沒被看到。
- 重現二:「其他測試檔有同名」沒要求那個名字是新加的。`testSuccess`、`returnsEmpty` 這類常見名字,在大推送裡幾乎必然在另一支被改動的測試檔裡存在,刪掉其中一個就被抑制。
- 要補的是:搬家要比函式本體,或至少比斷言數;「同名」要限定新增。

### 4. 括號配對對冷門寫法沒有定義失敗時怎麼辦,而且例外路徑與「出錯就擋」矛盾
severity: major
blocking: 是
引句:「用括號配對找函式本體,略過字串與註解裡的括號。」
- 段落:〈名詞〉「測試函式」、〈做法二〉「載入失敗…擋下」、〈做法一〉效能那句。
- 只說「略過字串與註解裡的括號」,沒涵蓋字元常值 `'('`、`'"'`、跳脫引號、Kotlin 多行字串 `"""` 內含引號、`${…}` 裡的巢狀字串、巢狀區塊註解 `/* /* */ */`。
- 配對失敗後怎麼辦沒寫。
  - 一條路是吞掉後面的函式,讓沒斷言的測試借到下一支的斷言而漏判。
  - 另一條路是每個函式都掃到檔尾,導致 O(函式數×檔大小)。59,000 行加一個沒收尾的引號,約兩千個函式各掃一遍,可能超過 300 秒預算。
- 例外路徑跟 spec 宣稱的「出錯擋下、不是放行」互相矛盾:`_codeloop_lint_new_step` 外層有 `except Exception: _gate_failopen(...)`,任何沒在判定函式內接住的例外都會變成放行並記 fail-open。
- 反過來,如果在判定內接住並擋下,spec 只給了 `lint_new.gate` 設 warn 或 off 當出口,而這等於關掉整道閘。單一怪檔不能用指紋放行。
- 佐證:file: `scripts/lumos:67960`(外層 `except Exception` 轉 fail-open)。
- 要補的是:單檔分析失敗要逐檔轉成可放行的候選(類似 `tq/unreadable` 的 `tq/unparsable`),並寫明配對的單趟上限。

### 5. 反引號函式名、巢狀類別同名、`@Test` 後面夾別的註解,測試函式認不全
severity: major
blocking: 是
引句:「Kotlin 認 `fun 名稱(`,Java 認 `void 名稱(`;用括號配對找函式本體」
- 段落:〈名詞〉「Kotlin 認 `fun 名稱(`,Java 認 `void 名稱(`」。
- 反引號命名(`fun \`adds two (numbers)\`()`)是 Android Kotlin 測試最常見的風格。實測 `fun\s+(\w+)\(` 在含 `sub` 與反引號函式的檔上只認出 `sub`。名字含空格甚至含括號時,配對也會錯。
- 巢狀類別、JUnit5 `@Nested` 常有同名測試,以「函式名」當鍵會碰撞。刪掉其中一個函式,名字還在,`test-removed` 不會報;斷言數會被加總或互蓋。
- `@Test` 下面隔了 `@Throws(...)`、`@Ignore`、另一行註解,或同行 `@Throws(...) @Test fun`。spec 沒寫往前看幾行。
- `@TestFactory`、`@Theory`、`@TestTemplate`、`@kotlin.test.Test` 不在名單。
- 這是所有函式級規則的共同前提,漏掉就是整批漏判。
- 要補的是:名字取法要涵蓋反引號,鍵用「類別路徑加函式名」,註解往前看到上一個宣告或語句為止。

### 6. 「新增行」沒定義成與改動前相比的多重集差,重排、整檔重新縮排、改行尾都會把舊的跳過標記全報成新增
severity: major
blocking: 是(誤擋正常推送)
引句:「只看新增行的規則,略過整行是註解的」
- 段落:〈做法一〉「只看新增行的規則」、`tq/skip-added`、`tq/build-config`、`tq/ci-config`、`tq/no-assertion`「本體有改」。
- 重現:`ktlintFormat` 或 `spotlessApply` 的縮排變更、CI yml 整段縮排、LF 轉 CRLF、函式搬位置。
  - 所有行都出現在 diff 的新增側。
  - 舊的 `@Ignore`、`ignoreFailures = true`、`-x test` 全部被當成新增。
  - 每個舊的沒斷言冒煙測試都成了「本體有改」而報 `tq/no-assertion`。
- 現有閘靠基準版對現在版做次數差來避開這點,spec 沒沿用。
- 要補的是:新增行規則要先把改動前同檔同規則命中的正規化行次數扣掉。

### 7. 第一次推新分支(起點是空樹)的處理自相矛盾,且全印沒有上限
severity: major
blocking: 是
引句:「讀不了(不是 git、任一端不是提交)2」
- 段落:〈做法一〉「讀不了(不是 git、任一端不是提交)2」、〈做法二〉「兩端提交算不出來…自動放行」「`tq/` 候選改成全印」。
- 空樹是 tree 物件不是 commit。實測 `git rev-parse --verify 4b825dc…^{commit}` 回 128,`git diff 4b825dc… HEAD` 卻正常。
- 掛鉤在找不到主線的新分支首推、`pp_range_for` 回退時,明確用空樹當起點。
- 照 spec 兩端必須是提交,會回 2。依 §二,算不出兩端會被當成環境不可用而自動放行,也就是第一次推送整個倉庫的作弊比對靜默關掉。
- 如果實作者改成接受空樹,整個倉庫的既有測試都是「新增」。
  - 每個舊 `@Ignore`、每個沒斷言的舊冒煙測試、每個 `-x test` 的發布 workflow 都成為候選。
  - 擋下訊息全印,沒有上限。
  - `lint-waive` 一次只收一個指紋,沒有批次。
- 佐證:file: `scripts/lumos:57734`(`_EMPTY_TREE_SHA`)。
- 要補的是:明寫空樹起點怎麼辦(只掃不擋、或當作基準版為空、或限定印出條數並給批次出口)。

### 8. 預期值位置假設 `assertEquals` 第一個參數就是預期值,漏了帶訊息的重載與容差重載
severity: major
blocking: 是
引句:「`assertEquals`、`assertArrayEquals`、`assertContentEquals`、`assertSame` 的第一個參數」
- 段落:〈做法一〉「預期值的位置」、`tq/expected-changed`。
- JUnit4 `assertEquals(String message, Object expected, Object actual)` 第一個參數是訊息。舊 Java 測試很常見這種寫法。
  - 改預期值(第二個參數)不會被當成預期值的位置而漏判。
  - 改訊息字串反而被誤判為預期值被改。
- `assertEquals(1.0, x, 0.01)` 把容差 `0.01` 放寬到 `0.1`,三個位置都不是第一個參數,漏判。
- 具名參數 `assertEquals(expected = 3, actual = n)` 沒有定義。
- diff 區塊的配對也沒定義:`-U3` 下相鄰兩處改動會合進同一個區塊;一個區塊內多行刪、多行增時怎麼配對沒寫。S4 只測了一刪一增。
- 要補的是:列出各重載的預期值位置與多行配對規則。

### 9. 改測試名與規則定義衝突
severity: major
blocking: 是
引句:「再做幾個正常改動當對照(新增有斷言的測試、改測試名、把測試搬到另一支檔、改正式程式碼),不應出候選」
- 段落:〈做法六〉「正常改動當對照(…改測試名…),不應出候選」對上 `tq/test-removed`「改動後同一支檔沒有了」。
- 同一支檔改函式名,舊名字「沒有了」,其他測試檔也沒有這個名字,所以一定報候選。
- 「對照組不應出候選」與 S14 的驗收在這裡不可能同時成立。實作者要嘛不理對照組,要嘛自己發明改名偵測。
- 要補的是:定義改名偵測(本體相似度),或把改名從對照組拿掉並承認會報。

### 10. `tq/no-assertion` 對本專案自己點名的截圖測試會系統性誤報
severity: minor
blocking: 否
引句:「新增的測試函式,或本體有改的測試函式,本體裡一個斷言字都沒有」
- 段落:`tq/no-assertion`、`tq/snapshot-changed`。
- Paparazzi 的 `paparazzi.snapshot { }` 與 Roborazzi 的 `captureRoboImage()` 本體沒有任何「斷言字」,驗證由比對基準圖完成。
- 同樣情形:只靠自訂輔助函式(`checkState(...)`)的測試。
- 每次新增或改動這類測試都出候選。有放行出口,但規則自己點名了這兩個工具。
- 同族過寬:`should` 開頭中綴沒要求字界,`shouldRefresh = true` 這類變數被算成斷言。

### 11. 檔案分類有漏洞與過寬
severity: minor
blocking: 否
引句:「CI 檔:`.github/workflows/` 底下的 yml、`.gitlab-ci.yml`」
- 〈做法一〉測試目錄清單沒有 KMP 的 `src/commonTest`、`src/jvmTest`、`src/androidUnitTest`,只剩檔名以 `Test` 結尾才認得。
- CI 只認 `.yml`,GitHub 同樣接受 `.yaml`。
- `.github/actions/*/action.yml`、`gradle/*.gradle` 之類 `apply from` 的腳本、`settings.gradle`、其他慣例外掛資料夾名稱沒有涵蓋。
- 圖檔缺 `.jpeg`。
- `docs/screenshots/*.png`、`fastlane/**/phoneScreenshots/*.png` 一類 README 與商店截圖,路徑含 `screenshots`,更新文件圖片也會觸發 `tq/snapshot-changed`,而這是「純文件推送」。大小寫比對也沒定義。
- 檔名以 `Test` 結尾的正式檔(`SpeedTest.kt`、`AbTest.kt`)被當成測試檔,反而跳過 `tq/test-env-sniff`。
- 圖檔內容的讀法沒定義:一次改上百張時,是讀 blob 內容還是用 blob id。讀全文要避免當文字解碼。

### 12. 規則的語法形式只寫了 Kotlin DSL,Groovy 與 Provider API 寫法會漏判或誤判
severity: major
blocking: 是
引句:「同一行有 `test`(不分大小寫)而且有 `enabled = false` 或 `onlyIf { false }`」
- 段落:`tq/build-config`、S6。
- 規則寫「設成 true」,對 Groovy 的 `ignoreFailures true`、`returnDefaultValues true`(沒有 `=`)、`exclude '**/FooTest*'`(沒有括號)漏判。
- 「同一行有 test 而且有 `enabled = false`」只認同行。常見多行寫法 `tasks.withType(Test).configureEach { enabled = false }` 漏判。
- Gradle test-retry 外掛的 Kotlin DSL 官方寫法是 `failOnPassedAfterRetry.set(true)` / `maxRetries.set(3)`。
  - 規則要找 `failOnPassedAfterRetry = true`,合規的寫法反而被列。
  - 同一檔沒有時,重試設定分在慣例外掛與模組兩檔也會誤報。
- `exclude(` 後面含 `**` 這條,Jacoco 的 `exclude("**/R.class", "**/BuildConfig.*")` 會誤報,Groovy 不帶括號的寫法卻漏判,兩邊不對稱。
- 要補的是:把 Groovy、Kotlin 屬性賦值、Provider API 三種形式都列進規則,並加反例。

### 13. `tq/too-large` 與現有 oversize 重複,且「任一版本」會誤擋變小的檔
severity: minor
blocking: 否
引句:「測試檔、正式程式檔或建置檔任一版本超過新增告警閘的單檔上限(行數或位元組),沒比」
- 段落:`tq/too-large`、〈名詞〉。
- 一個超大測試檔需要放行兩次:現有 oversize 的指紋綁路徑,不含規則;`tq/too-large` 的身分字串沒定義。
- 「任一版本超過」讓把 8 萬行巨檔拆小的重構照樣報,而被刪的巨檔報 `too-large` 後放行,刪除就不再被比對。
- 正式程式檔只為了掃新增行就要讀整檔,生成的巨檔(超過 5MB)也會擋。

### 14. 其餘小項
severity: minor
blocking: 否
引句:「把數字換成佔位後一樣,而新行的最大數字比舊行大」
- `tq/timeout-raised`:`@Timeout(30)` 首字大寫,規則字樣 `timeout` 若區分大小寫就漏;單位換掉(`5.seconds` 改 `5.minutes`)置換數字後文字不同,漏判;CI 檔的 `timeout-minutes` 不在範圍。
- `tq/assert-weakened` 的弱斷言名單沒有 `assertTrue(n > 0)`、`assertTrue(x != null)`,`assertEquals` 改成 `assertTrue(n > 0)` 數量不變、強斷言變少卻沒有弱斷言增加,漏判。
- 新增檔或刪除檔的另一端版本不存在,spec 沒區分「不存在」與 `tq/unreadable`,字面實作會讓每個新增檔都報不可讀。
- 路徑含中文或空白時沒規定用 `-z` 與 `core.quotePath=false`;擋下訊息的 `lumos lint-waive` 指令已用 `shlex.quote`,沒問題。
- 註解略過只看前綴:`/* x */ @Ignore` 整行被當註解,真註解本體不以 `*` 起頭的行卻不略過。
- `|| true`、`-x` 在 CI 的過寬 FP(`adb … || true`、發布 workflow 的 `-x test`):有放行出口,RETIRE-IF 也設了量測,所以只列備查。
- Windows 路徑:git 輸出一律正斜線,從 git 讀內容,無此隱患。已讀,無 finding。

## 實務隱患逐類
- 守衛面:finding 1、4、6。
- 輸入邊界:finding 2、5、7、8。
- 效能:finding 4。
- 金流、對外送出、不可逆:無,原因同 spec。

## 固定席節點
- `Systems/test-quality-cli`:不影響其行為宣稱。判定改動(尾端堆疊區塊)與節點記載的「大輸入測試釘住線性」一致。但節點 `responsibility` 只寫「收證與 JUnit 一致性核對」,沒涵蓋「推送前改動比對」,新檔掛進 about_code 時要同步改負責範圍(鐵則 5)。
- `Systems/test-quality-scan`:不影響。Semgrep 自比規則補 Truth 不改它的邊界。
- `Systems/pitfalls-lint-adapter`:有張力。KEY 寫「lumos 只解 SARIF…不內建任何棧規則」,spec 的 `tq/` 規則是內建的 Kotlin/Java 規則,併進同一份新增告警。KEY 只是線索不是合約,但計劃把它列在 `lands_in` 卻沒說要怎麼改寫那條 KEY。該節點也還沒寫負責範圍。
- `Issues/收證歸因第三輪留下的小問題`:存在於 repo(commit 841cea7ad 起),spec 只修它,不影響。

總結:最嚴重等級 major,blocking 共 10 條(finding 1、2、3、4、5、6、7、8、9、12)。
