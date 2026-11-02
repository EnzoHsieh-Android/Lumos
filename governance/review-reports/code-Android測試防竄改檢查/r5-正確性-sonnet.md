severity: minor

縮範圍之後的修補大體成立。我找不到會做出錯誤行為的輸入,下面六條是修補不完整或測試沒釘到的地方。我的暫存目錄 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet` 已刪。

### F1 父型別行尾逗號或冒號的修補只看行尾 50 字,中間夾註解或空行就失效
severity: minor
blocking: 否 — 類別路徑掉成空字串只造成函式鍵錯位與同名互撞,刪測試、改斷言仍會列。
引句:「if stripped[max(j, p - 50):p].rstrip().endswith((",", ":")):」
file: `scripts/lumos:48478`(修後)
失敗場景:註解在修補後會被剝成空白。
- `class FooTest : Base(),` 後面接超過 50 字的行尾註解,下一行才接 `Other {`:視窗全是空白,類別被當成沒有本體,`FooTest.a` 掉成 `a`。
- `class A :` 換行 `// legacy` 再換行 `Base() {`:同樣掉成 `a`。
- `class A :` 後面接空行再接 `Base() {`:同樣掉成 `a`。
- 一支檔裡兩個這樣的類別各有測試 `a`,鍵變成 `a` 與 `a#2`;刪掉第一個類別的 `a`,第二個的鍵會順位補上,比對配到錯的那一對。

測試只釘最簡單的「逗號行尾」。我把 `(",", ":")` 改成 `(",",)` 後,`-k tq_guard` 仍是 173 全綠,所以冒號寫法沒有測試釘住。
重現:
- 把 `class FooTest : Base(),   // <50 字以上的註解>` 換行 `    Other {` 再帶一支 `@Test fun a()` 的文字交給 `_tg_functions`。
- 修前 `fcd27439`:鍵為 `['a','a#2','a#3','a#4']`,全部掉路徑。
- 修後 `5516466e`:短註解的三個類別路徑回來了(`BarTest.a`、`BazTest.a`),長註解的 `FooTest.a` 與 `QuxTest.a` 仍是 `a`、`a#2`。
- 冒號加註解行的 `class A :` 換行 `// legacy` 換行 `Base() {`,修前修後都是 `['a']`。

歸因:有證據的原有漏查。修補是部分修復,修前也掉路徑,沒有變糟。

### F2 `buildSrc/src/test` 仍是測試檔這件事沒有任何測試釘住
severity: minor
blocking: 否 — 現行分類是對的,只是這行被改寫而測試覆蓋不到;不是驗收條款。
引句:「if name.endswith((".gradle", ".gradle.kts", ".kts")) or in_build_dir:」
file: `scripts/lumos:48395-48397`(修後)
失敗場景:`in_build_dir` 靠 `and not _rg_is_test_path(p)` 才讓 `buildSrc/src/test/kotlin/FooTest.kt` 與 `build-logic/convention/src/test/...` 歸成 test。我在暫存 clone 拿掉那個 `and not`,`-k tq_guard` 173 條仍全綠。這樣改之後,這些目錄底下的測試被刪或加 `@Ignore` 都不再出候選。測試裡 `buildSrc` 只出現在「`buildSrc/src/main/kotlin/A.kt` 為 None」那一條。
重現:改壞後用 `_tg_kind("buildSrc/src/test/kotlin/FooTest.kt")` 得到 None,原本是 `"test"`。
歸因:有證據的原有漏查。修前版 `fcd27439` 的測試檔也沒有 `buildSrc` 的案例。分類本身修前修後一致:`buildSrc/src/test`、`build-logic/.../XTest.kt`、`functionalTest` 都是 test,誤成 None 的只有 `.gradle*`、`.kts` 和 buildSrc 的非測試檔,這是預期。

### F3 catch 裡的 `check(`、`require(`、`should*` 識別字讓真的吞掉 fail() 的寫法不再列
severity: minor
blocking: 否 — 由設計放寬,跟 catch 裡 `assertTrue(true)` 早就不列是同一種近似;這裡是新增的放過面。
引句:「catch_checks = has("assert", c.end(), cb_end) or has("infix", c.end(), cb_end) or has("check", c.end(), cb_end)」
file: `scripts/lumos`(`_tg_catch_no_fail`)
失敗場景:`@Test fun a() { try { foo(); fail("x") } catch (e: Throwable) { check(true) } }` 的 catch 接住 `fail` 丟的 AssertionError,實質吞掉。`{ if (shouldLog) println(e) }` 也一樣,因為 `_TG_INFIX_RE` 是 `\bshould[A-Z]\w*\b(?!\s*=)`,任何 `shouldXxx` 識別字都算中綴斷言。
重現:`_tg_catch_no_fail` 對 `try { foo(); fail("x") } catch (e: Throwable) { check(true) }` 修前 True,修後 False;`{ if (shouldLog) println(e) }`、`{ require(attempts < 3) }` 同樣 True 變 False。`println(e)` 兩版都是 True,真正的吞掉仍列。
歸因:有證據的修復回歸,是刻意放寬,不是誤改。

### F4 Kotest 中綴斷言只算在 catch 那側,try 側不算斷言,吞掉 Kotest 斷言的寫法不列
severity: minor
blocking: 否 — 計劃 S6 寫的「斷言字」不含中綴,行為符合文字,但同一份判讀對兩側不對稱。
引句:「if _TG_CATCH_ASSERT.search(c.group(1)) and has("assert", t.end(), tb_end) and not catch_checks and not has("throw", c.end(), cb_end):」
file: `scripts/lumos`(`_tg_catch_no_fail`)
失敗場景:`@Test fun a() { try { result shouldBe 5 } catch (e: AssertionError) { println(e) } }`。try 裡只有 `shouldBe`,`pos["assert"]` 不含中綴,吞掉那一條不成立,測試永遠綠而沒有候選。同一檔其他地方的 `shouldBe` 卻已經被 catch 側與 no-assertion 判讀當成斷言。
重現:`_tg_catch_no_fail` 對上面那一行修前修後都是 False(空 catch 的 `catch (e: AssertionError) { }` 兩版都是 True)。
歸因:有證據的原有漏查,修前修後相同。

### F5 「超過的部分沒有比對」對整支檔太大的情況說反了
severity: minor
blocking: 否 — 只是訊息措辭誤導,候選仍會擋下且可放行。
引句:「"tq/too-large": ("檔案超過比對工具的上限,超過的部分沒有比對", "人工看這支檔的改動,或拆小"),」
file: `scripts/lumos:48968`(修後)
失敗場景:單檔超過 5 MB 或 10 萬行時整支檔完全不解析(`_tg_analyze` 的 TOOLARGE 分支直接 return,不進 `_tg_test_file`)。訊息卻暗示前面的部分有比對,讀的 AI 會以為只有尾巴沒看。
重現:一支 6.16 MB 的測試檔,末尾新增 `@Ignore @Test fun b()`。`lumos test-guard --diff HEAD~1..HEAD` 只輸出一條「`app/src/test/kotlin/ATest.kt:0 [tq/too-large] 檔案超過比對工具的上限,超過的部分沒有比對`」,新增的 `@Ignore` 完全沒被看。修前 `fcd27439` 的訊息是「沒有比對」,準確。
歸因:有證據的修復回歸(措辭)。

### F6 計劃與程式註解裡還有建置檔、CI 的殘留敘述
severity: minor
blocking: 否 — 純文件與註解不一致,不影響行為。
引句:「(建置檔的逾時移到第二批)」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:126`、`:202`;`scripts/lumos:49091`
失敗場景:
- 計劃第 126 行 `tq/snapshot-changed` 仍寫「測試檔、建置檔裡 `changeThreshold`…」,但程式已不掃建置檔。
- 第 202 行「六、考場實跑」仍列「build 檔加 `ignoreFailures`、CI 檔 `-x test`」當每條規則的壞改動,現在這兩類不出候選,照單做考場實跑會看到沒抓到。
- `_tg_has_long_line` 的註解仍說「建置檔、CI 是逐行線性的判讀」。

重現:`grep -n "建置檔" 計劃檔`,第 126、202 行不在「第二批」段內,也沒標「第二批」。
歸因:有證據的修復回歸(拿掉規則時漏改)。

## 圖譜鏡頭
`lumos impact` 附不上,我讀了 `Systems/pitfalls-lint-adapter`、`Systems/room-guard`、`Systems/測試假綠形態` 做判斷,三者宣稱的行為這份 diff 都沒破壞。
- `pitfalls-lint-adapter`:它只依賴 `tq/` 前綴與候選結構,diff 只移除了兩條規則,沒有碰指紋算法、放行檔或自動放行路徑。
- `room-guard`:只共用 `_rg_bracket_map`、`_rg_methods` 與 `_rg_is_test_path`,這輪沒改它們。
- `測試假綠形態`:與這份 diff 無交集。

`Systems/test-guard` 的 responsibility 與 WHY 已跟上縮範圍,被取代的 WHY 也標了 superseded。

## 三問
**① 原問題的修復效果有何行為證據?** 下面各項的案例都是我自己跑的;前五項有修前修後對照,第六項沒有修前版,以測試輸出為證。
- **G1 縮範圍**
  - 輸入與預期:`app/build.gradle.kts`、`gradle.properties`、`buildSrc/src/main/**`、`.github/workflows/*.yml` 不歸任何一類;`buildSrc/src/test/**/FooTest.kt`、`build-logic/.../src/test/...` 與 `functionalTest` 仍是 test。
  - 修前修後的 `_tg_kind`:修前把建置檔、`buildSrc/src/main/*.kt` 歸成 build,修後全是 None;test 路徑兩版都是 test。
  - 測試:`-k tq_guard` 173 條全綠。
- **G3 敘述擷取**
  - `assumeTrue(System.getenv("CI") == "(")` 接 `assertEquals`:修前身分吞進下一行,變成 `…=="(")assertEquals(1,1)}`;修後只剩 `assumeTrue(System.getenv("CI")=="(")`。
  - `"c i"` 與 `"ci"`:修前身分相同;修後 `env=="c i"` 與 `env=="ci"` 不同。
  - 修後行為正確的案例:字元常值 `'('`、多行原始字串、`${x}(` 模板、`list[0]`、lambda、CRLF 多行、`.let{}` 鏈與 Truth 鏈,都落在單一敘述。
- **G2 深巢狀**:3000 層每層一支測試,0.06 秒、最大鍵 205 字、3000 把鍵全部不同;兩個深層、結尾相同的 `Same.t` 不撞鍵(摘要含完整路徑)。
- **G5 類別本體**:短註解的行尾逗號修後路徑回來(見 F1);F1 列的長註解、註解行、空行例外仍失效。
- **G4 catch**
  - 修前修後都列:`println(e)`、`check(true)` 這類 try 沒 fail 的吞掉、空 catch。
  - 修前列、修後不列:`try { foo(); fail("x") } catch (e: Throwable) { e.message shouldBe "x" }`(符合意圖)。
  - 修後多列:`try { foo() } catch (e: Exception) { check(e is IOException) }`,try 沒 fail 而 catch 有檢查,與既有 `assertEquals` 的處理一致。
- **G6 閘與放行**:`-k lint_new` 82 條、`-k lint_waive` 31 條全綠;我沒有另外對自動放行三個出口做改壞實驗。
- 對 324 支真實的 `*Test.kt` 比較修前修後,函式鍵、`_tg_test_hits` 與 `_tg_catch_no_fail` 零差異。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立,但 F1(類別路徑)、F3(catch 放寬)、F5(訊息)是修補處的缺口。
- 相鄰路徑未退化:`_tg_stmt_at` 簽名只有一個呼叫端;8 萬行與 7 萬行跨行 assume 的壓力輸入 0.1 秒內完成,與修前相當;`#N` 多載計數與 `_tg_kinds` 的改名處理沒變。
- 建置檔與 CI 規則拿乾淨:`scripts/lumos` 內沒有殘留引用,`_tg_analyze` 的 `per_kind` 只剩 main,沒有 KeyError 路徑。

**③ 新發現的同一案例在修前修後各是什麼結果?** 已附在各 finding 的「重現」欄:
- F1:修前全掉路徑,修後只有短註解的修好。
- F3:`check(true)` 修前 True、修後 False。
- F5:6 MB 檔修前訊息為「沒有比對」,修後為「超過的部分沒有比對」。
- F2、F4:修前修後相同。
- F6:是修後才出現的殘留。

未驗範圍:
- 計劃第 202 行的考場實跑與 Verification 檔的 44 條歷史數字,我沒有重跑。
- 自動放行三個出口的測試,我沒做改壞實驗。
- F1 的鍵錯位對其他 `tq/` 規則的實際影響,我沒有端到端量過。
- 沒有逐條核對 `lumos lint` 對圖譜筆記的形狀要求。

全部只是小缺口,沒有會做出錯誤行為或破壞合約的問題,這一批可以放行。
