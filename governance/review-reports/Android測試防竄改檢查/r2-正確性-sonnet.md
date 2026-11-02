severity: major

審查範圍:逐節讀完 r2-snapshot.md,對照 `/Users/enzo/harness/lumos-tq-android/scripts/lumos` 現況,並在臨時目錄載入該檔的 `_rg_methods`、`_rg_split_args`、`_rg_strip` 實跑。臨時目錄已刪。r1 已折的項目不重報。

## 做法一:比對工具

### F1 「本體相同」判法太鬆,刪測試可以被當成改名放過
severity: major
- blocking: 是(`tq/test-removed` 是這份計劃的核心規則,又是最直接的作弊動作,漏判算判錯)
- 引句:「本體 = 宣告那一行之後的剝過字串註解、壓掉空白的文字;相同就算改名或搬家,不列」
- 重現,三種輸入:
  - **一行寫完的測試。** `@Test fun a() { assertEquals(1, f()) }` 的「宣告那一行之後」是空字串。我實跑 `_rg_methods`:`a`、`b` 兩支一行測試各自的起行等於迄行,本體都是空。刪掉一支紅的一行測試,只要變更的測試檔裡還有任何一支一行測試或空本體,就判成「本體相同」而不列。
  - **字串被清空。** `_rg_strip('assertEquals("OK", s)')` 輸出 `assertEquals("", s)`。兄弟測試 `greetsAlice`、`greetsBob` 只差字串常值,刪掉紅的那支,剩下的那支讓它被當成改名。
  - **只要存在一支就算。** 規則寫「沒有一支本體相同的函式」,沒要求一對一。兩支本體相同的測試刪兩支、加一支,兩個刪除都不列。S2 要求「巢狀類別裡同名的兩支只刪一支時要列」,跟這條存在式比對互相打架。
- file: `scripts/lumos:47768-47790` 的 `_rg_methods` 只回傳 (名稱, 起行, 迄行, 是否交易),沒有任何「本體」概念。「本體」的取法完全要新寫,但計劃把它寫成既有函式的重用。

### F2 字串被整個清空,字串預期值與依賴字串內容的規則都看不見
severity: major
- blocking: 是(`tq/expected-changed` 的主力情境是改預期值,字串預期值最常見)
- 引句:「在剝過字串與註解的本體上比對,區分大小寫」
- 重現:
  - `_strip_c_comments(blank_strings=True, keep_newlines=True)` 只保留換行,字串內容換成空,所以字元位移跟原文對不上。我實跑,`assertEquals("OK", s)` 和 `assertEquals("ERR", s)` 剝完一模一樣。依「在剝過的本體上比對」,字串預期值 `"OK"` 改 `"ERR"` 永遠判成沒變。
  - 計劃另一處說 `tq/expected-changed` 的身分是「含常值的改動後原文」,但沒寫怎麼從剝過的文字回到原文。位移對不上,只能靠行號重切,這一步沒定義。
  - 同一個設計讀法(第一節〈讀法〉的剝法,沒有分規則的例外)讓下列規則整條失效:`tq/test-env-sniff` 的 `"robolectric"`、`Class.forName("org.junit`,以及 `tq/build-config` 的 `exclude` 字串含 `Test`、`dependsOn("test`。字串內容被清成空,這些字永遠對不到。S10 因此寫不出能綠的測試。
- 引句:「身分是含常值的改動後原文」
- file: `scripts/lumos:6756-6775`(`blank_strings` 分支回傳 `tok[0] + nl + tok[0]`)

### F3 運算式本體的規則字面太窄,常見寫法仍然斷在第一行
severity: major
- blocking: 是(多數 Kotlin 協程測試會被判成沒有斷言,或斷言完全看不到)
- 引句:「後面接大括號時一路配到對應的右大括號」
- 重現,用 `_rg_methods` 實跑:
  - `@Test fun a() = runTest(UnconfinedTestDispatcher()) {` 的 `=` 後面接的是 `runTest(…)`,不是大括號。
  - `fun c() =` 換行再接 `runTest {`,也不是「接大括號」。
  - 兩種現在都在宣告那一行結束,本體被截成空。
- 後果:新增這類測試,斷言在後面幾行,會被誤判成 `tq/no-assertion`。既有的這類測試弱化斷言,`tq/assert-weakened` 看不到。
- file: `scripts/lumos:47735-47752` 的 `_rg_method_end`:遇到 `=` 就回傳到行尾。
- 缺口:計劃要擴充的判法沒定義怎麼判斷「這個 `=` 之後的大括號屬於本體」。

### F4 反引號函式名不只是「取不到名字」,整支測試連同本體都不會被找到
severity: minor
- blocking: 否(S16 的測試會抓到,屬於實作時才發現的規格偏差)
- 引句:「剝字串會把反引號整段清空」
- 重現:`_rg_methods` 對 `` @Test fun `adds two (numbers)`() {…} `` 回傳空。剝完是 `` fun ``() ``,`dm` 正規式要求 `(` 前面有 `\w+`,整個比對失敗,函式連同本體都被略過。
- 缺口:計劃只說「函式名改從原文取」,沒說要改 `dm`。只改取名,這類測試仍然完全不被辨識。
- file: `scripts/lumos:47775`

### F5 S16 的五秒效能條款,照計劃寫的修法達不到
severity: minor
- blocking: 否
- 引句:「2 MB 有 5 萬個註記行的檔應在 5 秒內切完」
- 重現:我造 5 萬個非測試註記行(約 1.6 MB)的檔。
  - 原函式 15.3 秒。
  - 只把切片 `text[k:]` 改成帶起點的比對(計劃寫的修法),仍要 12.9 秒。
  - 剩下的主要成本是迴圈裡的 `text.count("\n", 0, k)`,每個註記都從檔頭數一次換行,同樣是二次方。把它換成預先算好的行偏移,同一輸入掉到 0.15 秒。
- 缺口:計劃的根因分析只點到切片。
- file: `scripts/lumos:47784`、`scripts/lumos:47789`

### F6 AI 把斷言換成永遠成立的寫法,四條斷言規則都不報
severity: major
- blocking: 是(漏掉教科書級作弊)
- 引句:「斷言數不變、只改被測呼叫的參數時不列」
- 重現,兩個輸入:
  - `assertTrue(result.isValid())` 改成 `assertTrue(true)`:斷言敘述數不變,強斷言數 0 對 0,`assertTrue` 沒有預期值位置,四條規則都不報。
  - `assertEquals(88, calc.total())` 改成 `assertEquals(88, 88)`:預期值位置的 88 沒變,「除了預期值的位置之外全部相同」不成立,於是不是 expected-changed。斷言數與強斷言數也沒變,所以也不是 assert-weakened。
- 後果:實際值被換成常值整個漏掉,而計劃把「Semgrep 自比規則」當成補這洞的唯一手段。計劃自己說這道規則在 CI 與預設環境都沒有 Semgrep,只在考場實跑過。推送前的閘並不跑它。
- 缺口:S4 把「改被測呼叫名」整類列入不列,沒有把「實際值被換成常值」排除在這個豁免之外。

### F7 `_rg_split_args` 對含 `>`、`<`、`->` 的參數會切錯,預期值位置判不出
severity: minor
- blocking: 否
- 引句:「參數用 `_rg_split_args` 切」
- 重現:我實跑,下列輸入都得到單一參數(該切成兩個)。
  - `x > y, true`
  - `a < b, flag`
  - `listOf(1,2).map { x -> x * 2 }, result`
- 原因:該函式把 `<`、`>` 當括號計深度,比較運算與 Lambda 的 `->` 會讓深度歪掉。
- 缺口:計劃只列了三處既有函式要擴充,沒有這一處。
- file: `scripts/lumos:47391-47405`

### F8 預期值位置的三參數規則只對 JUnit,kotlin.test 的字串預期值會取錯
severity: minor
- blocking: 否(漏判,不是誤擋)
- 引句:「三個參數而第一個是字串常值 → 第一個是訊息、第二個是預期值」
- 重現:kotlin.test 的簽名是 `assertEquals(expected, actual, message)`,訊息在最後。`assertEquals("Alice", user.name, "name mismatch")` 照這條會被判成「`"Alice"` 是訊息、`user.name` 是預期值」。把 `"Alice"` 改成 `"Bob"` 被當成改訊息而不列。

### F9 斷言對齊方式沒定義,在序列中間加一條斷言可能誤報
severity: minor
⚠
- blocking: 否
- 引句:「把兩邊的斷言敘述清單按順序對齊」
- 說明:「按順序對齊、短清單逐項比」讀成依索引逐項比時,有一個輸入會誤報。`assertEquals(State.Loading, vm.state)`、`assertEquals(State.Loaded, vm.state)` 兩條之間插入一條 `Refreshing`,實際值相同,索引錯位後 `Loaded` 對上 `Refreshing`,判成預期值被改。若本意是 diff 式對齊就要寫明,也要說明怎麼取「被替換的那幾對」。

### F10 `tq/build-config` 的「Test 區塊」判法會漏掉最典型的寫法
severity: major
- blocking: 是(停用整個測試任務的作弊漏掉了)
- 引句:「有 `Test` 字樣而且有 `enabled` 設成 false」
- 重現:
  - 區分大小寫的「Test」對不上 Groovy 的 `test { enabled = false }`,也對不上 Kotlin DSL 的 `tasks.test { … }`、`tasks.named("test")`。同一份計劃的逾時規則明確寫「不分大小寫」,這條沒寫,字面讀是區分大小寫。
  - 「最近的左大括號那一行」若照字面取文字上最近的 `{`,在 `test { testLogging { … } ; enabled = false }` 這種區塊裡,最近的是已經關閉的 `testLogging {`,不是外層 `test {`。要的是「最內層還沒關閉的區塊」,計劃沒這樣寫。

### F11 `tq/ci-config` 只看「同一行有 gradlew」,三種常見寫法漏掉
severity: major
- blocking: 是(`-x test`、容許失敗是計劃點名要擋的)
- 引句:「而且 `continue-on-error: true`、`allow_failure: true` 或 `if: false` 的次數差大於 0」
- 重現:
  - **續行。** `./gradlew build \` 換行 `-x test`,第二行沒有 `gradlew`,不列。
  - **Gradle 官方 Action。** `gradle/actions/setup-gradle` 與 `gradle-build-action` 的 `with: arguments: build -x test` 同樣沒有 `gradlew` 那一行,不列。
  - **工作層級。** GitLab 的 `allow_failure: true` 是 job 的同級鍵,不在 `- ./gradlew test` 這個清單項目裡。GitHub 的工作層級 `continue-on-error: true` 也不在任何步驟裡。「步驟 = 同縮排的 `-` 開頭到下一個」的定義涵蓋不到。
- 後果:計劃把 `.gitlab-ci.yml`、`bitrise.yml`、`.circleci/config.yml` 都列為 CI 檔,但規則對它們幾乎無效。

### F12 `exclude … Test` 規則會誤擋 JaCoCo 常見排除清單,新模組的樣板也各吃一條
severity: minor
- blocking: 否(有放行出口,但會養成機械放行)
- 引句:「`exclude` 的字串含 `Test`」
- 說明:JaCoCo 的 `classDirectories` 排除清單常見 `**/*Test*.*`。S7 只列 `**/R.class` 當不列的例子。新增 Robolectric 測試類別幾乎必帶 `@Config(sdk = [..])`,新模組的 build 檔常抄 `isReturnDefaultValues = true`。依「命中次數差大於 0」,新增檔每一處都算新增候選,沒有任何新檔豁免。

## 做法二:併進新增告警閘

### F13 現有放行紀錄已有 `by` 欄且是 `$USER`,計劃的相容規則前提不成立
severity: major
- blocking: 是(舊資料與新語意撞名,S15「沒有 by 欄的舊紀錄當人放的」無法對現有資料成立)
- 引句:「舊紀錄沒有 `by` 欄的當人放的」
- 重現:
  - `_lint_waivers_add` 現在就寫 `"by": who`(`$USER`)。
  - 本 repo 的 `.lumos/lint-waivers.json` 第 4、12、20 行都是 `"by": "enzo"`。
  - 照搬 `_e2e_waive_cmd` 的 `by: human|ai` 會在同一個欄位塞兩種意思,實際資料裡「有 by 欄但不是 human/ai」的紀錄怎麼分,計劃沒說。
  - 若實作成「`by` 不等於 human 就是 AI」,所有現有消費專案的舊放行會整批被列成「AI 放的,還沒人看過」。若實作成「只認 `ai`」,又與計劃這句規則的前提(沒有 by 欄)對不上。
  - 另外,這條規則把缺欄位的預設值定成「已被人確認」,手寫一筆省略 `by` 的放行就等於標成人放的。
- file: `scripts/lumos:38707-38722`、`/Users/enzo/harness/lumos-tq-android/.lumos/lint-waivers.json:4`

### F14 AI 標記並不阻止放行,修正紀錄裡「架空」的論述與機制對不上
severity: minor
- blocking: 否
- 引句:「就能放行自己的作弊,沒有任何人看,整道比對被架空」
- 說明:同一份計劃第二節寫明「只提醒、不擋」。`by: ai` 的放行照樣讓推送通過,只是事後被列出來。「不加標記就會被架空」的論述,在加了標記之後依然成立,機制補的是事後可見,不是阻擋。設計可以接受,但這段「新增機制」的必要性論述要跟著改成實際效果,否則下一輪審查會以為這裡有阻擋。

### F15 閘設定的觸發條件兩處寫法不同
severity: minor
- blocking: 否
- 引句:「但改動把它從 block 改成 warn 或 off 時,這一次照 block 判並列 `tq/gate-config`」
- 矛盾:規則表把 `tq/gate-config` 定義成「前後值不同,而改動後是 warn 或 off」,涵蓋 warn 改 off、off 改 warn(收緊)、缺值改 warn。判定順序一節只在「從 block 改」才強制照 block 判。off 改 warn 這類收緊,會出一條 `tq/gate-config` 候選,模式卻是 warn、不擋。缺值要不要當 block,也沒寫。

### F16 比對工具壞掉時,計劃列的設定出口在同一次推送內走不通
severity: minor
- blocking: 否(環境變數出口還在)
- 引句:「出口是 `lint_new.gate` 設 warn」
- 說明:比對工具丟例外記成 `kind: guard` 並擋下,沒有指紋可放行。照計劃改 `lint_new.gate` 為 warn 再推,那一次推送又被「同一次推送把閘關掉不算數」強制照 block 判,工具再丟一次例外,依然擋。實際只剩環境變數可用。
- 另有現有訊息對不上:
  - `scripts/lumos:38782` 把所有非 env 的未完成都寫成「條命令因為時間預算沒跑到」。
  - `_cl_say_lint_block` 無新增項時印的是「`lumos lint-waive <指紋> …`」。
  - 這兩處對 guard 錯誤都不對。計劃的「擋下訊息」一段沒提這兩處也要改。

### F17 回退一節與關閘留帳互相矛盾
severity: minor
- blocking: 否
- 引句:「連原本的新增告警一起關,碰到五類檔時留帳」
- 矛盾:做法二〈關閘留帳〉寫「有候選才寫一筆治理帳;沒有候選不寫」。回退一節寫 `off` 與 `LUMOS_SKIP_LINT_NEW=1` 都是「碰到五類檔時留帳」。實作者會挑一邊,S14 只釘了「有候選才寫」。

### F18 把「合併主線之後推送」延後處理,但同一支 repo 裡有現成解法
severity: major
- blocking: 是(合併主線再推是日常動作,每次都會把別人的改動算成推送者的候選)
- 引句:「合併主線之後推送,範圍裡別人的改動也會被比對工具算成這次的候選」
- 重現:閘走的範圍是 `remote..local`。`_lens_push_base` 的說明自己寫「這支在合過主線、沒設 upstream、CI 已 fetch 時會算錯」。
- 現成解:Room 守衛走的 `_note_audit_start` 加 `_push_range_start`(帶 `--push-remote`/`--pushed-ref`),專門處理這件事。計劃把比對工具定位成「跟 Room 守衛同一層、同一種寫法」,卻沒帶這兩個旗標。
- S22 的量測排除了合併提交,量不到這類誤報,低估實際擋人頻率。這些候選又只能由推送者(通常是 AI)放行,是批量機械放行的主要來源。
- file: `scripts/lumos:62474-62500`、`scripts/lumos:48901-48906`、`scripts/lumos:48016-48050`

### F19 空樹起點的重試可能是死路徑,「主線判法」指哪一支沒寫
severity: minor
⚠
- blocking: 否
- 引句:「找得到就用它當起點;找不到就照比對、全部只印不擋」
- 說明:閘前面的 `_codeloop_guard_verdict` 已經先用 `_lens_push_base`(只認 upstream)換掉全零起點。到達新增告警閘時拿到空樹,代表那一步已經找不到主線。計劃說「主線用推送掛鉤既有的判法」,沒寫是 `_lens_push_base` 還是 `_push_range_start`,若是前者,這裡的重試重複做同一件事。空樹時全部只印不擋,等於這種 repo 的第一次推送整個沒被檢查,CI 是淺層 clone 時同樣如此。

## 其他次要

### F20 放行綁指紋、沒有時間或提交成分,舊放行可被日後同樣的作弊重用
severity: minor
- blocking: 否
- 引句:「放行第一個不會順帶放掉第二個」
- 說明:指紋由 `(規則, 檔案, 身分, 第幾個)` 決定,放行檔永久有效。例如某測試曾被合理放行 `@Ignore`,之後重新啟用又被同樣加回 `@Ignore`,指紋相同,靜默放行。`tq/too-large` 更直接:放行一次,該檔之後所有改動永久不再被比對。
- 引句:「指紋綁路徑,同一支檔放行一次就好」

## 已讀,無 finding
- 做法三〈Semgrep 自比規則〉、做法四〈標準改寫〉、做法五〈上一輪延後的六條〉、做法六〈考場實跑〉。這幾節與我的鏡頭(判定邏輯)的交集有限,看到的問題都歸入上面各條。
- 〈驗收條款〉的 S1 到 S22 只在上述 F 條有牽涉時才提到,另無獨立 finding。
- 〈回退〉〈實務隱患〉除 F17 外無 finding。

## 風險類逐類答
- **判錯放過作弊**:有。F1(改名豁免太鬆)、F2(字串預期值看不見)、F6(實際值換成常數)、F10(`test {` 小寫)、F11(續行、官方 Action、工作層級)。
- **擋下正常改動**:有。F3(`runTest(...)` 被判成沒有斷言)、F12(JaCoCo 排除清單、新模組樣板)、F18(合併主線後推送把別人的改動算成自己的)。
- **效能與資源**:F5。S16 的五秒目標照計劃寫的修法達不到。其餘 S11 的大檔與 300 支檔 30 秒,以我量到的 12.9 秒數量級看過得去。
- **併發**:放行檔寫入沿用 `_vault_write_lock`,新增 `by` 欄不改鎖。不影響。
- **不可逆**:不涉及,考場提交不推不併。
- **資安**:AI 標記只靠終端提示與一個資料欄位,F13 說明缺欄預設為信任。計劃自己列了不防刻意偽造,我不重報。
- **fail-open、fail-closed 的選擇**:比對工具出錯擋下的方向合理,但 F16 說明出口在同一次推送內走不通。
- **固定席節點 `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只覆蓋 sentinel 之間 body)**:這份設計沒有碰 re-inject 與 sentinel 區塊,判不影響。
- **固定席節點 `Systems/測試假綠形態` 的 ★INVARIANT★(還原翻紅釘需前置斷言)**:這份設計不新增「修 bug 的還原翻紅釘」。比對工具自己的測試是否各自能翻紅,計劃第 244 行已寫「逐條改壞一次確認」,判不影響。

總結:最嚴重等級 major,blocking 共 8 條
