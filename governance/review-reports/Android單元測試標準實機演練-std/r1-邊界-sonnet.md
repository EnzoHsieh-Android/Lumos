severity: major

審稿範圍:先逐節讀完 spec,再用小腳本直接 import 工作樹的 `scripts/test_quality.py` 重現。交叉引用已核對:三篇 `related` 筆記與驗證紀錄都在,S5 列的七支測試名與兩支守衛(`t_secev_fault_truth_assertion_counts_like_assertion`、`t_test_quality_standard_android_drill_lessons`)都存在,`scripts/lumos` 裡的指紋表與目前 `scripts/test_quality.py` 的 sha256 一致。

## Findings

**1. 裝置那路新加的 `Caused by` 切割用了會平方爆炸的正則**
severity: major
blocking: 是(新引入的效能退化,出現在推送前閘會讀的不可信報告上;報告上限是 10 MiB 與 16 MiB,實際上沒有限制)
引句:「裝置那路改成同一條規則:第一行剛好是這兩個型別之一(可接冒號加訊息),而且要有 JUnit `Assert` 的堆疊。」
- file: `scripts/test_quality.py:134` 的 `re.split(r'\n\s*Caused by:', text, maxsplit=1)`。
- 這行對每個換行字元都用 `\s*` 吃光後面的空白(`\s` 也吃換行),找不到 `Caused by:` 再逐字退回,整體是 O(n²)。改動前是 `startswith` 加 `re.search`,是線性的。
- 重現:構造 `<failure>` 文字,第一行 `java.lang.AssertionError: x`,後面接 N 組 `\n  `(換行加兩格空白)。
  - 純 `\n` 填滿:10,000 個約 0.17 秒,40,000 個約 2.7 秒,80,000 個(80 KB)約 10.7 秒。
  - `\n  ` 填滿:10,000 組(30 KB)約 0.5 秒,80,000 組(240 KB)約 33 秒。
  - 大小每加倍,耗時約乘四。
  - 照這個斜率外推,在 10 MiB 上限內會卡數小時。
- 呼叫路徑:`capture` 的 `junit()` 與安全證據閘的 `_secev_junit_facts` 都會走到。後者讀的是被推提交樹裡的報告,所以一份異常報告就能讓 pre-push 掛住。
- spec 的「守衛面」與「效能」兩段都沒提這個新正則的成本。全域規則要求修補後對大型輸入跑效能檢查,這一步沒做。
- 建議:改成逐行掃描,或把 `\s*` 限成 `[ \t]*`(那樣每個換行只掃自己那一行,是線性的),並補一支大輸入的測試。

**2. 型別名單只收兩個字面型別,同族的 JUnit 與 Hamcrest 斷言失敗沒掃到**
severity: major
blocking: 是(這輪修的就是「名單漏掉實際出現的斷言型別」,同族沒一次掃完;標準又用「這類」暗示涵蓋更廣)
引句:「也就是 JUnit 的 `assertEquals`(數字或字串)、`assertTrue`(帶不帶訊息都行)這類」
- 這句引的是標準檔,不在 spec 內,所以在本條下以 file 指出:file: `skills/lumos-project-notes/commands/test-quality-standard.md:155`,「裝置那一路收得到哪些失敗」那條。
- 重現 1,JUnit 的 `assertArrayEquals`:
  - 裝置文字第一行是 `org.junit.internal.ArrayComparisonFailure: …`,後面有 `at org.junit.Assert.assertArrayEquals(` 堆疊。我試過,`assertion_failure` 是 False。
  - 本機報告 `type="org.junit.internal.ArrayComparisonFailure"` 也是 False。原因:`file: scripts/test_quality.py:111` 的正則要求 `.` 或行首緊接 `ComparisonFailure`,而這個型別是 `ArrayComparisonFailure`。
  - 但它是 `AssertionError` 的子類,正是 JUnit 自己的斷言失敗。依賴只有 JUnit 時,陣列(`ByteArray`、`IntArray`)輸出的測試最自然的斷言就是它。
- 重現 2,Hamcrest 的 `MatcherAssert.assertThat`:
  - 裝置文字第一行是 `java.lang.AssertionError: `,但堆疊只有 `org.hamcrest.MatcherAssert.assertThat`,沒有 `org.junit.Assert` 幀。我試過,結果是 False。
  - 同樣的失敗在本機報告有型別欄,會被認出,所以本機與裝置兩條路的行為不對稱。
  - 標準只寫了「Truth 在裝置上收不到」,沒寫這兩種。
- 後果:照標準寫、用到這些斷言的人,拿到的是 `nonassertion_failure` 拒收,而且看起來像「假實作當掉」。這跟 spec 修字串比較缺口的理由完全同型。
- 建議:要嘛把 `ArrayComparisonFailure` 納入精確名單(本機與裝置都要),要嘛在標準的「收不到」清單明寫這兩種並指到驗證紀錄。同時補一支反例或正例測試。

**3. 假實作用 `fail()` 丟錯,會騙過「當掉不算抓到錯」的防線**
severity: minor
blocking: 否(標準可用一句話補上;工具本來就分不出,屬已知限制沒寫明)
引句:「假實作(記憶體裡的假資料來源)遇到沒排好的呼叫就丟例外;收證不把這種紅算成抓到錯。」
- spec 與標準都把「當掉」定義成丟的不是斷言的例外。
- 如果假實作用 JUnit 的 `fail("unexpected call")` 或自己丟 `AssertionError`:
  - 裝置那路,第一行是 `java.lang.AssertionError: …`,堆疊有 `org.junit.Assert.fail`,會被認成斷言失敗。
  - 本機那路,型別本來就是 `AssertionError`,也認。
- 這種「當掉」會被算成抓到錯,正是 S1 要擋的情況。
- 標準沒有警告「假實作要丟非 `AssertionError` 的例外」。
- 建議:標準加一句規範假實作丟 `IllegalStateException` 之類,並在「機器抓不到」清單補上這種。

**4. 裝置那路的 `Caused by` 切割會被訊息內容騙到,收窄也沒列進影響面**
severity: minor
blocking: 否(假陰性,保守方向,但會讓合格故障收據被拒)
引句:「要有 JUnit `Assert` 的堆疊。」
- 這句引的是 spec 對裝置規則的描述;「Caused by 之前」的限定在 `file: scripts/test_quality.py:134`。切割是純文字的:只要斷言訊息本身有一行以 `Caused by:` 開頭,就會在訊息裡被切掉,擋在 `Assert` 堆疊之前。
- 重現:`org.junit.ComparisonFailure: expected:<Request failed`、換行、`Caused by: timeout> but was:<Request failed>`,後面接 `at org.junit.Assert.assertEquals(…)`。我試過,結果是 False,而這是一個真的字串 `assertEquals` 失敗。被測輸出若是帶原因的錯誤文字,就會中。
- 另外,舊規則是「全文有 `Assert` 幀就算」,新規則改成只看 `Caused by` 之前,是收窄。
  - 凡是舊版記成 True、新版重算成 False 的收據,核對時都會因為「記錄的結果跟重算不同」被拒。
  - spec 的收據相容性說明只舉了 Truth 型別這個「放寬」方向,沒提收窄方向。
- 建議:至少在說明裡補上收窄方向,並加一支「訊息含 `Caused by:` 行」的測試記下目前行為。

**5. 裝置規則的正規化行為沒被任何測試釘住**
severity: minor
blocking: 否(不影響現況正確性,但守不住)
引句:「改成同一條規則:第一行剛好是這兩個型別之一(可接冒號加訊息)」
- `file: scripts/test_quality.py:132-133` 的 `text.strip()` 與 `first … .strip()` 負責前導空行與 `\r\n`。我試過,前導空行、CRLF、Tab 後接訊息都能正確判成 True。
- 我在副本裡拿掉這兩個 `strip()`,執行 `scripts/test_test_quality_cli.py` 裡 device、truth、assertion 這幾組新測試,沒有任何一支新翻紅(只有兩支原本就紅、與這次改動無關的案例)。也就是有人日後拿掉,測試仍全綠。
- 其他我試過、現行行為合理的形狀(不需處理):
  - 多個 `<failure>`:有一個不是斷言失敗就整體 False。
  - `failure` 與 `error` 並存:整份被 `suite_error` 拒收。
  - CDATA:正常。
  - 全形冒號、BOM:判 False,保守,且 AGP 實際不會產出,不列。
  - `Suppressed:` 在第一行是一般例外時:False。
- 建議:補一支含前導空行加 `\r\n` 的正例。

**6. 標準的 Gradle 寫法只給 Kotlin DSL 一種**
severity: minor
blocking: 否
引句:「Gradle 預設這時會失敗(`filter.isFailOnNoMatchingTests` 預設開」
- 這句在標準裡,對應處是 `file: skills/lumos-project-notes/commands/test-quality-standard.md:142`。
- 同一節講 `returnDefaultValues` 時 Groovy 與 Kotlin 寫法都列了,這裡只給 Kotlin 的 `isFailOnNoMatchingTests`。
- 照標準用 grep 查專案有沒有關掉零選中保護時,Groovy 的 `failOnNoMatchingTests = false` 會被漏掉。Gradle 9 的 `failOnNoDiscoveredTests` 同理。
- 建議:兩種 DSL 都寫上。

## 逐節結論

- 問題與最小解、名詞:已讀。名詞表自洽,「歸因」與 S1 歸因的區分有交代。除上列外沒有 finding。
- 做法第 1–6 步:已讀,無 finding。
- 做法第 7 步:見 1、2、4,另補一點:「消費專案裝的收證工具副本要等下次 `lumos update`」這句有交代版本落差。
- S1–S4(manual):已讀,無 finding。
  - S2、S4 如實寫了「主目錄演練前狀態沒記錄」。
  - S4 的 develop 提交編號是公開 repo 能放的資訊,沒洩漏考場套件、類別名或本機路徑。
- S5、S6:已讀,測試名全部存在,指紋表與目前檔案一致。S5 的條款句式與 finding 1、2、5 有關。
- 回退、審計修正紀錄:已讀,無 finding。回退段對「還原後收據要重收」的說法跟程式一致。

## 實務隱患鏡頭

- **效能:有隱患**,見 finding 1。
- **守衛面(新增放行面):有隱患**,見 finding 2、3。
  - 放寬的是故障敏感度那條路,JUnit 宣告那條仍擋。
  - 我查了 `_secev_junit_declared`,斷言失敗與非斷言失敗都不放行,spec 說「兩者都不放行」成立。
- **金流、對外送出、不可逆:無,理由同 spec**,被測只是現金收支類別 ViewModel,工具鏈這邊只是讀報告。
- **公開卷證洩漏:無**。spec 本身沒有考場套件名、類別名、欄位名、本機路徑或裝置序號。

## 固定席節點

派工尾端沒有附固定席節點,無可判。

總結:最嚴重等級 major,blocking 2 條
