severity: major

本席驗了這輪的修補。有兩條 major、四條 minor。

## 發現

### F1 catch 的窄中綴認法讓 Kotest 呼叫寫法不再算檢查,「try 沒 fail、catch 裡斷言」漏報
severity: major
blocking: 是 — 修前會列的真假綠寫法修後不列(漏報)
引句:「_TG_INFIX_STRICT = re.compile(r"(?<=\s)should[A-Z]\w*(?=\s+[^\s=:])")」
file: `scripts/lumos:48824`

失敗場景:
- 新窄正規式要求 `should…` 前面是空白、後面空白再接值。
- Kotest 的點號呼叫寫法(`e.message.shouldBe("x")`、`.shouldNotBeNull()`、`.shouldBeInstanceOf<X>()`)前面是 `.`、後面是 `(` 或 `<`,全部不算 catch 的檢查。
- 結果:`try { foo() } catch (e: X) { e.message.shouldNotBeNull() }` 這種 try 沒有 fail 的假綠不再被列。
- 這個漏洞沒有寫進 `_TG_LIMITS`,也沒有寫進標準的「抓不到」。
- 計劃筆記只說明不改寬判法的理由是怕 `x.shouldBe(5)` 被誤列成「沒斷言」。它沒提 catch 這側會因此漏報。

重現(`--diff HEAD~1..HEAD --json`,舊版與新版同一個臨時 repo):
- 舊版 old:`assertEquals(1,f())`。新版 new:再加上下面這行。

```
try { foo() } catch (e: Exception) { e.message.shouldNotBeNull() }
```

- 修前(5516466e):`['tq/catch-no-fail']`。
- 修後(34bef2d8):`[]`。
- `e.message.shouldBe("x")` 與 `e.shouldBeInstanceOf<IllegalStateException>()` 同樣是修前列、修後不列。
- 對照:中綴寫法 `e.message shouldBe "x"` 修後仍列。

歸因:有證據的修復回歸(修前列、修後不列)。

### F2 窄中綴認法仍把一般變數當檢查,「窄收」只收了冒號與等號兩種
severity: minor
blocking: 否 — 只是多列一條可放行的候選,不影響漏報
引句:「_TG_INFIX_STRICT = re.compile(r"(?<=\s)should[A-Z]\w*(?=\s+[^\s=:])")」
file: `scripts/lumos:48824`

失敗場景:
- 後面只要是「空白再接任何非 `=`、`:`、空白的字」就算。
- 所以 `if (n < 3 && shouldRetry && ok)` 的 `shouldRetry &&` 算檢查。
- 行尾的 `val r = shouldRetry` 換行接下一行也算,因為換行屬於 `\s+`。
- 兩種都讓 catch 被當成「catch 裡有斷言」,在 try 沒有 fail 時列 `tq/catch-no-fail`。

重現:new 是 `try { foo() } catch (e: IllegalStateException) { if (n < 3 && shouldRetry && ok) { n++ } }`。修前與修後都是 `['tq/catch-no-fail']`。

歸因:有證據的原有漏查(修前同樣列;intake 例子只涵蓋 `: Boolean`、`=`、`.shouldLog(`)。

### F3 catch 型別括號互相巢狀時,`_TG_CATCH_ASSERT.search` 掃到右括號,平方級,超過 30 秒
severity: major
blocking: 是 — 超過計劃 S11 的 30 秒效能上限
引句:「_TG_CATCH_ASSERT.search(b, c.end(), close) and tried and not catch_checks」
file: `scripts/lumos:48858`

失敗場景:
- 修補把右括號改用括號對應表找,但搜尋範圍仍是「catch 左括號到右括號」整段。
- catch 的括號裡再放 `try{}catch(` 一層一層巢狀時,每層都重掃它包住的全部內層。
- 這就是「每個命中各自往後掃一段很遠的文字」的同族形狀。
- 修補後新增的 S11 項目只測「1 萬 6 千個 `catch(` 右括號擠在最後」(並列),沒測巢狀。
- 檔案不大:20000 層、38 萬位元組、4 萬行,都在 5MB 與 10 萬行上限內,也沒有超長行。

重現(python 產生測試檔,`rc=1`,只列一條 `tq/assert-weakened`;catch 本體 `{p()}` 非空且無檢查,才不會被前面的規則提早回傳):
- old:`@Test fun a() { assertEquals(1, f()) }`。new 的測試本體:

```
"try{}catch(\n"*D + "x\n" + "){p()}\n"*D + " assertEquals(1,2)"
```

- 實測時間(`lumos test-guard --diff HEAD~1..HEAD --json`):

| 層數 D | 修後 | 修前 |
|---|---|---|
| 2000 | 1.5 s | 1.5 s |
| 8000 | 7.4 s | 5.5 s |
| 16000 | 25.3 s | 17.0 s |
| 20000 | 39.5 s | 未測 |
| 32000 | 96.6 s | 未測 |

- cProfile 在 D=6000 時,`re.Pattern.search` 佔 3.4 秒,而且全在 `_tg_catch_no_fail`。
- 同一個函式裡其他位置的查找(`has()` 二分、`_TG_NONSPACE.search`、`_TG_CATCH.match`)各自只掃自己的區段,沒有這個問題。
- 建議:像 assert、fail 那幾種一樣,先算好 `_TG_CATCH_ASSERT` 的全部位置,再用二分查範圍。

歸因:有證據的原有漏查。修前 `[^)]*` 加 `c.group(1)` 同樣平方級,修補沒改掉,修後約慢 1.4 倍。

### F4 行尾逗號或冒號後接 FF、VT 時,類別路徑丟失
severity: minor
blocking: 否 — 只是函式鍵少了類別前綴,不影響規則是否列出
引句:「body = stripped[ls:p].rstrip(" \t\r")」
file: `scripts/lumos:48527`

失敗場景:
- 修前用 `str.rstrip()`,會剝掉所有 Unicode 空白。
- 修後只剝空格、tab、CR。
- 所以 `class A : B(),\f` 後面換行接 `C {`(FF 在 Java 與 Kotlin 都是合法空白),類別就被判成沒有本體。

重現:`class A : B(),\f\n   C { @Test fun a() … }`,刪掉那支測試。
- 修前函式鍵是 `A.a`。
- 修後是 `a`。
- `\v` 與 U+2003 同樣掉路徑。
- 影響很小:同名測試分屬不同類別時鍵會撞,會多一個 `#2`。

歸因:有證據的修復回歸。

### F5 assume 身分:Kotlin 字串樣板裡巢狀字串的空白差異不算,頭尾空白宣稱不完整
severity: minor
blocking: 否 — 只漏掉很罕見的巢狀樣板字串的空白改動
引句:「字串用剝註解那支的掃描式(_C_STRIP_PAT)認,不另寫一套。」
file: `scripts/lumos:48948`

失敗場景:
- 掃描式遇到巢狀的樣板字串會斷成三段,中間一段被當成字串外而被折疊空白。
- 例:`"${f("a b")}"` 改成 `"${f("a  b")}"`。
- 照這輪的說明,字串常值的空白差異該算,這裡卻不列。

重現:assume 內 `x == "${f("a b")}"` 改成 `"${f("a  b")}"`。
- 修前不列,修後也不列。
- 對照:一般字串 `"a b"` 改 `"a  b"` 修前不列、修後列(修補有效)。

歸因:有證據的原有漏查(修補把一般字串做對,巢狀樣板沒涵蓋)。

### F6 太大訊息:整支檔超過上限時,訊息分不出是整支沒比還是只有超長行
severity: minor
blocking: 否 — 只是訊息措辭,判定本身沒錯
引句:「"tq/too-large": ("超過比對工具的上限:整支檔超過上限時整支沒有比對;只有超長行時那幾行沒有比對、其餘照比", "人工看這支檔的改動,或拆小"),」
file: `scripts/lumos:49016`

失敗場景:
- 兩種情況共用同一句固定文字。
- 超長行的情況會在括號裡補一句「有一行超過 20000 字…」。
- 整支檔超過 5MB 的情況沒有補句,讀者要靠「沒有括號」去推斷。
- 修補要的「分得出」只做了一半。

重現:5.1MB 的測試檔輸出一行 `…[tq/too-large] 超過比對工具的上限:整支檔超過上限時整支沒有比對;只有超長行時…`,後面沒有任何說明是哪一種。

歸因:有證據的修復不完整。

## 圖譜鏡頭
- 專案內 `lumos impact --diff 047031883..34bef2d8` 列出 `Systems/test-quality-cli`、`Systems/測試假綠形態`、`Systems/lumos-cli-read` 等為家或相關節點,以及計劃 `Projects/Android測試防竄改檢查_計劃`。
- 計劃 S11 的效能清單沒有「catch 型別括號互相巢狀」,正是 F3 漏掉的角落。
- `Systems/test-guard` 新增的 PITFALL 寫著「catch 括號用共用的括號對應表」已修好乘積形狀,不涵蓋巢狀範圍。
- 新增的 WHY 說明窄認法的理由,沒記下 F1 的代價,也不在 `_TG_LIMITS` 與標準裡。
- 幫助文字與指令對照表已不提建置檔與 CI。專案內 `git grep` 沒再找到過時說法。

## 三問
1. **原問題的修復效果有什麼行為證據?** 有效,證據如下。
   - 字串常值頭尾、逗號後、內部空白改動,修前不列、修後列。
   - 字串外重排與換行重排兩版都不列。
   - 行尾逗號或冒號後接空行、註解行、CRLF 空行、tab,類別路徑修前掉成 `a`、修後是 `A.a`。
   - `check(true)` 與 `logger.shouldLog(e)` 不再被當檢查。
   - 快取正確性:我用 4000 筆隨機宣告片段(含 `class`、`object`、逗號、冒號、換行、註解、CRLF)做差異模糊測試,有快取版與每次重建快取版結果零差異,共跑兩個種子。
   - 修前的三個舊乘積形狀(1 萬 6 千個並列 `catch(`、1800 個類別後接 240 萬字空白、40 行各 3990 個沒收尾的 `fun <`):我沒獨立重跑,只靠 intake 所列的修前 9.9、11.3、8.5 秒與修後 3 秒內。
   - 我另測了 250 行各 2800 個 `fun <x`,新舊版都約 2 秒;9 萬個 assume 語句修前 4.6 秒、修後 4.8 秒,沒有退步。

2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 大致成立,但有三處例外。
   - F1:中綴寫法仍列,點號呼叫寫法不再列(修前列、修後不列)。
   - F4:FF、VT 在行尾逗號後的類別路徑掉了。
   - F3:新的括號查找沒改變平方級。
   - 另外 `String.rstrip` 換成 `rstrip(" \t\r")` 的差異只影響 FF、VT 與 Unicode 空白。

3. **新發現的同一案例,修前、修後各是什麼結果?**

| 案例 | 修前 | 修後 | 歸因 |
|---|---|---|---|
| F1 `e.message.shouldNotBeNull()` | 列 | 不列 | 修復回歸 |
| F2 `shouldRetry &&` | 列 | 列 | 原有 |
| F3 D=16000 巢狀 catch 括號 | 17.0 秒 | 25.3 秒 | 原有,略差 |
| F3 D=20000 | 未測 | 39.5 秒 | 原有,超 30 秒 |
| F4 FF 在 `,` 後 | `A.a` | `a` | 修復回歸 |
| F5 巢狀樣板字串 | 不列 | 不列 | 原有 |

總結:F3(巢狀 catch 括號的平方級掃描,2 萬層就超過 30 秒)與 F1(Kotest 點號呼叫寫法在 catch 裡不再算檢查)要處理,其餘四條是 minor;我的臨時目錄已用字面絕對路徑刪除。
