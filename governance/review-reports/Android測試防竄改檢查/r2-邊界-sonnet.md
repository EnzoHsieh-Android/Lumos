severity: major

我讀完全文,對程式現況逐項查證,並用 `_rg_*`、`_strip_c_comments`、`_nodehome_cat_blobs_capped`、`_lens_git` 直接載入主程式實跑。下面每條重現數字都是我在臨時 repo 跑出來的。實驗檔在 `/tmp/lumos-seat-work/Android測試防竄改檢查/邊界-sonnet/`,請編排者收貨後刪。

## 逐節

- 問題與最小解、名詞:已讀,無 finding。
- 做法一的讀法、五類檔、斷言字、規則表、抓不到的:有 finding,見 1 到 8、11 到 15。
- 做法二:有 finding,見 9、10、12、16。
- 做法三(Semgrep)、做法四(標準改寫)、做法五(六條小修):已讀,無 finding。三者不碰邊界輸入,只動規則與文件;五只加測試。
- 做法六(考場)、第二批、REVISIT:已讀,無 finding。
- 驗收條款 S1 到 S22:S15 有 finding(見 9);S11、S16 的壓力檔不夠(見 1)。
- 回退:有 finding,見 16。
- 實務隱患:資安那條的宣稱被 1、2 推翻(見 1)。
- 審計修正紀錄:已讀,無 finding。

## Findings

### 1. 修法治不了二次方:註記後的簽章比對本身就是二次方,而且截止時間打斷不了
severity: major
blocking: 是——照 spec 修完,病態檔仍會讓推送卡死,條款與資安宣稱都不成立。
引句:「改成帶起始位置的比對、不切片(實測 2 MB、5 萬個註記行的檔要 20.5 秒)」
file: `scripts/lumos:47782` 的 `dm = re.match(r"(?:[^(@{};]|@[\w.]+(?=\s))*?\b(\w+)...\(", text[k:], re.S)`。
- 這條 regex 的 `@[\w.]+(?=\s)` 分支讓它能一路吃過後面的註記,沒遇到 `(`、`{`、`;` 就掃到檔尾。
- 它對每個註記行都跑,而且排在「是不是測試註記」的判斷之前。
- 重現:`"@A\nval x = 1\n" * N` 先過 `_rg_strip`,再呼叫 `_rg_methods`。N=2000(26 KB)花 2.07 秒,N=4000(52 KB)花 8.95 秒,時間隨 N 平方成長。
- 改成 `pattern.match(text, pos)` 不切片後我又跑一次:N=4000 還是 8.6 秒。所以 spec 寫的修法(不切片)沒有用,慢的是 regex 本身。
- S11、S16 的壓力檔是註記後面都有括號的檔,regex 很快停下,條款會綠。真正的病態輸入不在任何條款裡。
- 單檔上限是 5 MB,照平方外推遠超過 300 秒。
- `_rg_methods` 是純 Python 迴圈,spec 的「比對工具超過截止時間也一樣記成沒跑完」沒辦法在單一檔案內打斷,要靠每支檔之間才檢查。
- 實務隱患那句「不會讓判讀變成二次方」不成立。
- 建議:先判 `anns & kinds` 再跑簽章 regex;簽章 regex 限長(例如只看註記後 N 個字元);S11 加一個「註記後無括號」的壓力檔;截止時間寫成每支檔開跑前檢查,並明講單檔跑到一半無法中斷。

### 2. 斷言敘述逐個配括號,極深的合法巢狀是二次方,「每支檔一趟」不成立
severity: minor
blocking: 否——要深到編譯器自己都撐不住,實際風險低,但資安宣稱寫死了「極深巢狀」。
引句:「一個斷言敘述 = 從斷言字到它對應的右括號,再接上後面連著的 `.名稱(…)` 鏈」
file: `scripts/lumos:47377` 的 `_rg_balanced` 每次從斷言字起掃到對應右括號。
- 重現:`"assertTrue(" * D + "x" + ")" * D`,對每個斷言字呼叫 `_rg_balanced`。D=2000(24 KB)0.93 秒,D=4000 3.74 秒,D=8000(96 KB)15.6 秒。
- 這種檔括號配得平,不會被 `tq/unparsable` 攔下。`tq/catch-no-fail` 對每個 `try`、`runCatching` 若也各自配對,同樣是二次方。
- 「括號配對每支檔一趟」只對整檔的深度檢查成立,對「每個斷言、每個 try 各配一次」不成立。
- 建議:用單趟堆疊一次算出所有括號配對表,規則共用;或限制巢狀深度,超過列 `tq/unparsable`。

### 3. 重用的 `_rg_split_args` 把 `<`、`>` 當括號,有比較運算或 lambda 箭頭的預期值切不對
severity: major
blocking: 是——spec 要求 `tq/expected-changed` 靠參數個數定預期值位置,切錯會靜默漏判。
引句:「依呼叫名與參數個數,參數用 `_rg_split_args` 切」
file: `scripts/lumos:47391-47406`,迴圈把 `<` 和 `>` 都算進深度。
- 實跑結果:
  - `if (a > b) 1 else 2, x` 得到 1 個參數(應為 2)。
  - `listOf(1,2).map { x -> x * 2 }, result` 得到 1 個參數。
  - `a < b, true` 得到 1 個參數。
  - `items.filter { it.n > 0 }, 3` 得到 1 個參數。
- 預期值裡有 `->` 或比較運算的 `assertEquals`,參數個數判成 1,規則落到「不認得的形狀」就不列。這類斷言被改預期值時漏判。
- spec 只列了三處要擴充(運算式本體、切片、反引號名),沒有提 `_rg_split_args`。
- 建議:加進擴充清單,補「`>` 與 `->` 不算括號」的 Room 守衛回歸測試和 S4 反例。

### 4. 同一份 spec 收 `kotlin.test.Test`,但三、四參數 `assertEquals` 的順序照 JUnit 排,kotlin.test 的字串預期值會被當訊息
severity: major
blocking: 是——用 kotlin.test 的專案,字串預期值被改會判成「只改訊息」而放過。
引句:「三個參數而第一個是字串常值 → 第一個是訊息、第二個是預期值」
- kotlin.test 的簽章是 `assertEquals(expected, actual, message)`,訊息在最後;有容差的版本是 `(expected, actual, absoluteTolerance, message)`。這是官方 API 事實,我沒有在本機跑。
- 例:`assertEquals("A", result, "m")` 把 `"A"` 改成 `"B"`。spec 的規則把第一個字串當訊息、第二個 `result` 當預期值,結果是「只改訊息字串不列」,真正的預期值被改卻沒列。
- 四個參數的 `(expected, actual, tol, message)` 同理被當成 JUnit 的 `(message, expected, actual, delta)`。
- spec 在做法一第 82 行(測試註記那條)把 `kotlin.test.Test` 明列為認得的註記,所以 kotlin.test 的 `assertEquals` 在範圍內。
- 建議:依檔案的 import(`org.junit` 對 `kotlin.test`)選參數表,或兩種都比對,取任一種解讀有差就列。

### 5. 運算式本體的修法只講一種寫法,常見的換行寫法仍然斷在 `=` 那一行
severity: major
blocking: 是——新增的 Kotlin 測試用這些寫法時,`tq/no-assertion` 會誤報,`tq/assert-weakened` 比到空本體。
引句:「運算式本體 `fun x() = runTest { … }` 的 `=` 後面接大括號時一路配到對應的右大括號」
file: `scripts/lumos:47735-47752` 的 `_rg_method_end`,遇到 `=` 就收在該行行尾。
- 現況實跑,以下三種都只配到 `=` 那一行:
  - `fun long_name() =` 換行後接 `assertEquals(…)`,本體算出來是空的。
  - `fun b() = runTest(UnconfinedTestDispatcher()) {`,`=` 和 `{` 之間有括號。
  - `fun d() =` 換行 `runTest {`。
- ktlint 風格在簽名太長時就是把 `=` 放行尾,所以這是常規寫法,不是冷門。
- spec 的修法字面只涵蓋 `= runTest {`,S5、S16 的例子也只有這一種。
- 建議:寫明規則是「`=` 之後第一個非空白 token 起,若在本行或下幾行出現 `{` 就配到對應右大括號,否則配到表達式結束」,並為三種寫法各補測試。

### 6. CI 規則的「步驟」定義吃不到 GitLab 與 job 層級的關鍵字,規則表列的 `allow_failure: true` 實際永遠不會命中
severity: major
blocking: 是——這是各家 CI 最直接的繞法,spec 列了卻抓不到。
引句:「同一個步驟(同縮排的 `-` 開頭到下一個)裡有 Gradle 呼叫而且 `continue-on-error: true`、`allow_failure: true` 或 `if: false` 的次數差大於 0」
- GitLab 的 `allow_failure: true` 是 job 層級,和 `script:` 平行。`script:` 底下才是 `- ./gradlew test` 這種清單項,所以「同縮排的 `-` 到下一個」框出來的只是一行指令,框不到 `allow_failure`。
- GitHub 的 job 層級 `continue-on-error: true`、`if: false` 與 `steps:` 平行,同樣在任何步驟之外。
- 五類檔列了 `azure-pipelines.yml`、`bitrise.yml`、`codemagic.yaml`、`Jenkinsfile`,但規則沒有對應鍵:
  - Azure 的 `continueOnError: true`。
  - Bitrise 的 `is_skippable: true`。
  - Codemagic 的 `ignore_failure: true`。
  - Jenkinsfile 是 Groovy,沒有「`-` 步驟」,`catchError(...)` 這類寫法完全沒涵蓋。
- 結果是列了的 CI 檔大部分只有「`-x test` 和 `|| true`」兩種寫法有效。
- 建議:規則改以「所屬 job 或區塊」為單位判斷(job 的開頭到下一個同層 key),各家鍵名逐家列表;沒能涵蓋的家,在「抓不到的」明寫。

### 7. 「呼叫 Gradle 的行」只看同一行有沒有 `gradlew`,續行與 action 參數都漏
severity: major
blocking: 是——長 Gradle 指令幾乎都會折行,`-x test` 放在續行就逃掉。
引句:「同一行有 `gradlew` 或 `gradle ` 指令」
- 這幾種寫法的 `-x test`、`|| true` 那一行都沒有 `gradlew`:
  - `run: |` 區塊裡 `./gradlew build \` 換行 `-x test`。
  - `gradle/gradle-build-action` 的 `with: arguments: build -x test`。
  - Bitrise 的 `gradle-runner` 步驟,用 `gradle_task: test`。
- 我用 `_strip_c_comments` 檢查過,這些行本身都不會被剝掉。
- 規則以「行」為單位,所以這些都不會被認成 Gradle 呼叫。
- 建議:改成「同一指令」:接續行(行尾 `\`、YAML 折疊)合併後再判,並把 `arguments:`、`gradle_task:` 這類已知欄位列進來。

### 8. 剝字串模式只寫一種,規則表又需要字串內容;CI 的 yml 也不能走 C 式剝法
severity: major
blocking: 是——S7、S10 要求命中的規則,照字面實作永遠不會命中。
引句:「剝字串與註解:`_strip_c_comments(..., blank_strings=True, keep_newlines=True)`」
file: `scripts/lumos:6756`,`blank_strings=True` 會把字串內容清空,只留引號。
- 實跑 `_rg_strip` 的結果:
  - `exclude("**/*Test*")` 變成 `exclude("")`。
  - `check.dependsOn("test")` 變成 `check.dependsOn("")`。
  - `Class.forName("org.junit.Test")` 變成 `Class.forName("")`。
  - `"robolectric".equals(x, true)` 變成 `"".equals(x, true)`。
  - Groovy 的 `exclude '**/*Test*'` 變成 `exclude ''`。
- `tq/build-config` 的「`exclude` 的字串含 `Test`」與 `dependsOn("test`、`tq/test-env-sniff` 的 `"robolectric"` 與 `Class.forName("org.junit` 都需要字串內容。
- 反過來,若這些檔「不剝」,改成註解的 `// check.dependsOn("test")` 仍會算成命中,「改動後沒了」就判不出來。實跑 `_strip_c_comments(..., blank_strings=False)` 的行為是註解被剝、字串保留,這才是這幾類檔需要的模式。
- 對 yml 要另算:C 式剝法把 `//` 當註解。
  - `run: ./gradlew test -Dscan.url=https://s.example.com || true` 剝完剩 `run: ./gradlew test -Dscan.url=https:`,行尾的 `|| true` 被吞掉。
- 建議:分檔類指定模式。測試檔用 `blank_strings=True`;建置檔與正式程式檔用 `blank_strings=False`;yml 另寫 `#` 註解剝法,不走 C 式剝法。

### 9. 「答 n 也記 AI 放的」和宣稱照搬的 `_e2e_waive_cmd` 相反,而且漏了防永久等待的旗標
severity: major
blocking: 是——S15 把「人明確拒絕」編成「放行成功」。
引句:「沒有互動終端、讀不到回答或答 n 都記 `by: ai`」
file: `scripts/lumos:42702-42708`。
- `_e2e_waive_cmd` 在 `ans is False`(答 n)時印「沒放行」並回 rc=1,不寫紀錄。只有 `ans is None`(沒有終端、沒人回答)才記 `by: ai`。
- spec 讓答 n 也寫入放行,而放行檔一寫入,該指紋就被放過。人答「不確認」反而讓放行生效。
- 同一個呼叫在 `scripts/lumos:42702` 帶 `stdin_timeout=True`。`_confirm_tty` 說明(`scripts/lumos:33627`)寫明這是為了「掛著虛擬終端、沒有人在的流程才不會永遠等」。spec 只說「用既有的 `_confirm_tty`」,沒有帶這個旗標。預設值是 `False`,走 `input()`,偽終端下沒人答就永遠等。
- 建議:S15 改成「答 n 回 1 不寫」,明寫 `stdin_timeout=True`。
- 這裡也有 spec 自己的矛盾:正文說「照搬」,條款卻寫了不同的行為。

### 10. 現有放行紀錄全都有 `by` 欄,「舊紀錄沒有 `by` 欄」不成立
severity: minor
blocking: 否——可以靠實作時讀懂,但字面解讀會把全部舊放行當成 AI 放的。
引句:「舊紀錄沒有 `by` 欄的當人放的」
file: `scripts/lumos:38721`,`_lint_waivers_add` 寫入 `"by": who`,值是 `$USER`。
- 每一筆既有放行都有 `by`,值是使用者名稱(例如 `enzo`),不是 `human` 或 `ai`。
- 照 e2e 的驗證形狀(`scripts/lumos:41925` 的 `w.get("by") in ("human", "ai")`)直接套,舊紀錄全部變成「不合法」或被當 AI 放。
- 若 `$USER` 恰好是 `ai`,會被誤認為 AI 放的。
- 建議:新紀錄用新欄位(例如 `by_kind`),或明寫「`by` 不是 `ai` 的一律當人放的」,並補一個 `USER=ai` 的測試。

### 11. 非 UTF-8 路徑在「讀改了哪些檔」就被毀損,再被當成「空檔」靜默略過
severity: minor
blocking: 否——只影響非 UTF-8 檔名,但 spec 把它歸為「不算讀不出來」。
引句:「不存在的那一端(新增檔沒有改動前、刪除檔沒有改動後)當空檔,不算讀不出來」
file: `scripts/lumos:62974` 的 `_lens_git`,預設 `text=True, errors="replace"`。
- 重現:用 `git update-index --cacheinfo` 加入 `app/src/test/<Big5 位元組>Test.kt`。
  - `_lens_git(... diff --name-status -z ...)` 得到的路徑被換成 `����Test.kt`(U+FFFD)。
  - 用這個路徑呼叫 `_nodehome_cat_blobs_capped` 得到 `[None]`。
  - 改用 `binary=True` 再以 surrogateescape 解碼,同一個檔讀得到內容。
- 結果:名稱毀損的新增檔,兩端都是空,什麼規則都不會跑,也不會列 `tq/unreadable`。
- spec 只處理了「路徑含換行」,沒有處理含非 UTF-8 位元組的路徑。
- 建議:name-status 用 `binary=True`,路徑以位元組為準;讀不到而狀態不是 A 或 D 的,一律列 `tq/unreadable`。

### 12. 內容編碼完全沒寫;例外路徑只有全域出口,沒有逐檔放行
severity: minor
blocking: 否——正常 UTF-8 專案不受影響。
引句:「出口是 `lint_new.gate` 設 warn(印出、留帳)或 off、或 `LUMOS_SKIP_LINT_NEW`(有候選時留帳)」
- 全文 grep 沒有出現「UTF」「解碼」「編碼」「BOM」「NUL」「二進位」。
- 要把 `bytes` 交給 `_rg_strip` 就得先解碼。用嚴格 UTF-8 解 Big5、UTF-16 的測試檔會 `UnicodeDecodeError`。用 `surrogateescape` 解碼,之後算 sha256 指紋時 `.encode("utf-8")` 會 `UnicodeEncodeError`。
- 依 spec,任何非預期例外都記成 `guard` 並擋下,出口只有關整道閘。這一支檔就能讓所有碰到它的推送卡住,沒有像 `tq/unparsable` 那樣能針對路徑與物件編號放行的出口。
- 建議:寫明解碼用 `errors="replace"`;含 NUL 的檔列 `tq/unparsable`;「guard」類擋下也給指紋放行。

### 13. 斷言字名單漏掉 JUnit 4 慣用寫法,會誤報 `tq/no-assertion`
severity: minor
blocking: 否——有放行出口,但這是標準寫法,不是專案自訂的輔助。
引句:「`assert` 接大寫開頭的名字」
- 不在名單內,卻是常見的檢查寫法:
  - Kotlin 標準庫的 `assert(cond)`。
  - JUnit 4 的 `thrown.expect(...)`(`ExpectedException` rule)。
  - `throw AssertionError(...)`。
- 〈已知的誤報〉只說「專案自訂的斷言輔助」,沒有涵蓋這三種現成的寫法。
- 建議:補進名單,或至少納入 S22 的量測清單。

### 14. 函式鍵沒處理同一類別內的同名多載
severity: minor
blocking: 否——需要預先存在同名測試才會漏。
引句:「同一支檔裡用它對改動前後」
- 函式鍵只用「類別路徑加函式名」。Kotlin 與 Java 允許同一類別裡有同名但參數不同的測試(例如 `@ParameterizedTest` 的兩個多載)。
- 鍵相同時,改動前後怎麼配對沒寫。刪掉其中一個,鍵仍然存在,`tq/test-removed` 不會列。
- S2 只涵蓋巢狀類別同名。
- 建議:鍵加上參數型別簽章或「第幾個同名」,補同名多載的測試。

### 15. 幾個邊界行為沒有定義
severity: minor
blocking: 否——都是定義缺口,實作時各自會有猜測。
引句:「一支函式最多比 2000 個敘述」
- 超過 2000 時是略過、截斷還是列 `tq/unparsable`,沒寫。
- `tq/unreadable` 在讀法和 S11 都提到,規則表沒有這一列,指紋怎麼算沒寫。
- 截圖基準圖要「綁 git 物件編號」,但讀法只取 name-status 檔名清單,物件編號從哪來沒寫(需要 `--raw` 或 `ls-tree`)。
- `tq/gate-config` 的「改動前與改動後的值不同」,在改動前沒有設定檔或沒有該鍵時,是否以預設值 `block` 比,沒寫。
- S9 寫「路徑以 docs、fastlane 開頭」,五類檔的定義是「在 `docs/`、`fastlane/`、`metadata/` 底下、含 `phoneScreenshots`、`tabletScreenshots`」,兩邊範圍不同。
- 單檔上限 5 MB,但整批總量上限沒定。`_nodehome_cat_blobs_capped` 有 `max_total_bytes` 參數,spec 沒用,一次改 300 支檔最壞要讀 3 GB。

### 16. 回退節和關閘留帳互相矛盾
severity: minor
blocking: 否——只是文字衝突,但實作和 S14 可能寫成不同的樣子。
引句:「單次推送用 `LUMOS_SKIP_LINT_NEW=1`(碰到五類檔時留帳)」
- 回退節寫「碰到五類檔時留帳」,設定 off 那句也是同樣寫法。
- 做法二〈關閘留帳〉和 S14 寫的是「有候選才寫帳,沒有候選不寫」,並特別強調常駐關閘的 Android 專案不會每次推送多一行。
- 兩邊對「沒候選時要不要留帳」的答案相反。
- 建議:回退節改成「有候選時留帳」。

## 固定席節點逐條判

- `Systems/test-quality-cli`:不破壞。計劃不改 `scripts/test_quality.py`,只在 `scripts/test_test_quality_cli.py` 加測試。
- `Issues/deinit整夾刪使用者檔`:不破壞。它牽連的是同一支測試檔,計劃只往裡加測試,不碰 deinit 路徑。
- `Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject 只覆蓋 sentinel 之間):不破壞。計劃只新增子命令和 `.lumos/lint-waivers.json` 欄位,不改注入邏輯;sentinel 外的內容不被動到。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):計劃本身不破壞。但這份計劃要新增的釘住測試要照它帶前置斷言。
  - 例如 S14「off 時比對照樣在背後跑」,測試要先證明比對真的跑了才算數。
  - S19、S20 的「放寬就紅」也一樣要帶。
  - 計劃目前只寫「逐條改壞一次確認各自會紅」,沒寫前置斷言。
- `Verification/測試品質第四輪修補驗證`:不破壞。它牽連 `scripts/test_quality.py`,計劃不動它。

## 風險類逐類答

- 邊界輸入:空範圍、純刪除、純改設定檔、合併提交、空樹起點,spec 都有交代。有缺口的是非 UTF-8 路徑與內容編碼(11、12)、函式鍵同名多載(14)、2000 上限溢出(15)。
- 效能與資源:`_C_STRIP_PAT` 剝字串是線性的,我用 5 MB 的引號、`/*`、反引號、三引號、`'` 各跑一次,最慢 0.53 秒。問題在後面的辨識層:1 的 regex 二次方,2 的逐個配括號二次方,15 的總量沒上限。
- 守衛面(Kotlin 與 Java 辨識):函式辨識、參數切分、運算式本體、斷言字各有洞(3、4、5、13)。
- 守衛面(建置、CI):剝字串模式矛盾(8),CI 規則的步驟與行定義吃不到各家寫法(6、7)。
- 守衛面(放行與 AI 標記):答 n、逾時旗標、`by` 欄衝突(9、10)。
- 資安:實務隱患寫「病態輸入…不會讓判讀變成二次方或丟例外放行」,被 1、2、12 推翻。
- 併發:放行檔沿用既有上鎖,治理帳沿用追加寫法,已讀,無 finding。
- 金流、對外送出、不可逆:spec 已排除,我檢查後同意,無 finding。

總結:最嚴重等級 major,blocking 共 8 條
