severity: major

# 邊界與輸入審查報告——Java 補棧(code-java補棧/r1-slice-code.patch)

審查範圍:`scripts/lumos` 新增的 `JAVA_TEST_RE`、`java-junit` test profile、`_init_config_skeleton` 的 `ranked[:3]`→`ranked`,以及新增的 Java/Python 七/五題效能追問觸發正則。全部發現都是實跑量出來的,不是純推測。

---

## 發現①:JAVA_TEST_RE 對「很多個 @Test 但都找不到 void」的檔是二次方時間,可被拖到幾十秒

severity: major
blocking: 是
引句:「JAVA_TEST_RE = re.compile(」

file: `scripts/lumos:3373`(即補丁裡的新增行,新正則本體)

```python
JAVA_TEST_RE = re.compile(
    r"@(?:Test|ParameterizedTest|RepeatedTest)\b.*?\bvoid\s+([A-Za-z_]\w*)\s*\(",
    re.S)
```

作者自己在註解裡寫的取捨是「Kotlin 版用 `[^{]*?`(遇到 `{` 就斷),Java 版故意換成無界的 `.*?`,為了跨過 `@ValueSource(ints = {1, 2, 3})` 的大括號」。這段推理本身沒錯,但代價比作者想的大:`[^{]*?` 在真實程式碼裡幾乎每隔幾個字元就會撞到一個 `{` 而提前失敗、放棄這次嘗試;`.*?` 沒有任何字元能讓它提前放棄,只要遇到「這次 `@Test` 找不到 void」,它就會一路掃到檔案結尾。

當一支 `.java` 檔裡有 N 個 `@Test`(或 `@ParameterizedTest`/`@RepeatedTest`),而其中有一段連續的 `@Test` 之後很久都沒出現 `void`(例如中間混進大量非 void 方法、或檔案本身是壞的/生成的/惡意構造的),`discover_test_methods` 對這支檔跑 `mre.finditer(txt)` 的總時間會是 O(N × 平均剩餘長度),也就是檔案大小的二次方——不是指數級 catastrophic backtracking,但一樣會把整個工具卡住。

`discover_test_methods` 不是旁支功能,它是 `code-loop check`(bound-tests-gate,pre-push/CI 擋點)、`doctor` Check T、`cmd_archive` 共用的核心函式(`_platform_test_index` 在第 8579 行呼叫它),掃描對象是整個 `src/` 目錄底下所有 `.java` 檔——包含消費專案裡別人寫的、或惡意構造的檔案。

**實測(用 `importlib.machinery.SourceFileLoader("lum", "scripts/lumos")` 載入後直接呼叫正則):**

```
k=100   len=10600   time=0.0044s  matches=0
k=500   len=53000   time=0.1074s  matches=0
k=2000  len=212000  time=1.7207s  matches=0
k=5000  len=530000  time=10.7962s matches=0
k=10000 len=1060000 time=43.61s  matches=0
```

（`k` = 檔案裡 `@Test` 出現次數,每次後面接 100 個不含 `void` 的字元,全檔完全沒有任何一個 `void`)

也就是說:一支 1MB、裡面有一萬個 `@Test` 但都沒接 void 的 `.java` 檔,單這支檔的方法掃描就要 43 秒。如果一個消費專案(或惡意 PR)裡放進這樣一支檔案,`lumos doctor`/`lumos code-loop check`/pre-push hook 會被這一支檔卡住幾十秒到幾分鐘,而且這條路徑在 pre-push/CI 是**擋點**,不是背景工作。

順帶一提:我也用同樣手法測了既有的 `KOTLIN_TEST_RE`(`[^{]*?`版),發現如果全檔完全沒有任何 `{`(同樣是刻意構造的病態輸入),Kotlin 版也有同樣的二次方問題(k=10000 時 47.35s)。所以這不是「Java 版比 Kotlin 版更糟」的新退化,而是「這個作者延續了一個既有的病態設計、套用到新語言,而且沒有測試覆蓋這個角度」——`t_java_profile_discovery` 只驗證了功能正確性(有沒有抓到方法名),完全沒有驗過大檔/多 `@Test`/無 void 的效能邊界。

**沒有跑但值得一提**:正常真實的 JUnit 測試檔幾乎不會踩到這個問題,因為 `@Test` 後面通常緊接著它自己的 `void`。真正會踩雷的是①生成檔/損毀檔②惡意構造的檔(這正是本次審查鏡頭要求的輸入類型)。

---

## 發現②:`@Test` 寫在 Java 字串字面裡會被當成「真的測試方法」收進去,可以偽造 bound-tests-gate 的「real」判定

severity: major
blocking: 是
引句:「"exts": {".java"}, "method_re": JAVA_TEST_RE, "scaffold_ext": ".java",」

file: `scripts/lumos:3931`(`discover_test_methods` 本體,非本次新增但被補丁新增的 `java-junit` profile〔`scripts/lumos:3514-3515`〕直接接上,且被新測試漏掉)

`discover_test_methods` 在比對 `mre.finditer(txt)` 之前,只做了註解剝除(`// ...`、`/* ... */`),完全沒有剝字串字面。所以只要一支 `.java` 檔裡任何地方(不必是測試檔、也不必是同一個類別)有一段字串常量長得像:

```java
String doc = "Example usage: @Test\n    void fakePhantomTest() { assertTrue(true); }";
```

`fakePhantomTest` 就會被收進 `discover_test_methods()` 回傳的方法名集合裡。

**實測**:

```python
(root / "src/test/java/shop/T.java").write_text(
    'package shop;\n'
    'class T {\n'
    '    String doc = "Example usage: @Test\\n    void fakePhantomTest() { assertTrue(true); }";\n'
    '}\n')
lum.discover_test_methods(root, dict(lum.TEST_PROFILES["java-junit"]))
# => {'fakePhantomTest'}
```

為什麼這條 blocking:圖譜自己記錄的 `bound-tests-gate` ★INVARIANT★(`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`)講的是「code-loop check 對 impact 固定席上合約綁的測試逐支真跑,任一紅/懸空(dangling)/偽證據(fake)/方法名不合法 → blocked」。但 `_classify_one`(`scripts/lumos:8603`)判斷「real / fake / dangling」的邏輯是:

```python
if name in methods_for(plat):
    sts.append("real")
elif name in hay_for(plat):
    sts.append("fake")
else:
    sts.append("dangling")
```

`methods_for(plat)` 就是 `discover_test_methods()` 的回傳集合。字串字面裡的假名字既然已經混進這個集合,判定結果是 `"real"`,不是 `"fake"`——這比 `"fake"` 更嚴重,因為 `"fake"` 至少還會被 bound-tests-gate 擋下來,`"real"` 則會被當成「這個 ★INVARIANT★ 有真的可執行證據」直接放行。任何人只要在專案裡任意一支 `.java` 檔塞一段字串常量,寫上 `@Test\n void <隨便取名>() {}`,就能讓另一篇筆記寫 `[test:<隨便取名>]` 通過 Check T 與 bound-tests-gate,而那支「測試」根本沒有被跑過——這正好是 `bound-tests-gate.md` 這篇筆記存在的理由被繞過。

這個根因(`discover_test_methods` 不剝字串字面)不是這次 diff 新開的洞,C#/Kotlin/Python 等既有 profile 理論上一樣有這個問題(我沒有時間逐一驗證每個既有 profile,只驗證了 java-junit)。但這次 diff 把同一個有漏洞的機制原封不動接到新的 `java-junit` profile 上,而且新增的 `t_java_profile_discovery`/`t_java_stack_wiring` 兩支測試都只驗證了「註解裡的假測試會被剝掉」(`// @Test`、`/* @Test */`),完全沒有測「字串裡的 `@Test`」這個同樣容易構造、殺傷力更大(判定成 real 而非 fake)的路徑。既然這次審查鏡頭明確要求測「字串裡有 @Test」,而且這條路徑直接打穿一條寫進圖譜的 ★INVARIANT★,我把它列為 major/blocking。

---

## 發現③:CJK/非 ASCII 開頭的 Java 測試方法名,JAVA_TEST_RE 完全抓不到(靜默漏掉,不是誤判)

severity: minor
blocking: 否
引句:「void\s+([A-Za-z_]\w*)\s*\(」

file: `scripts/lumos:3373`

捕獲群組是 `[A-Za-z_]\w*`——首字元被鎖死在 ASCII 範圍,`\w`(Python 3 預設 Unicode 模式)雖然能匹配中文字元,但只在「非首字元」位置生效。也就是說,一個合法的 Java 識別字(JLS 允許 Unicode 字母當識別字)如果整個方法名是中文(例如 `void 測試付款成功() {}`),會被整條正則直接跳過、完全不出現在回傳集合裡;但只要首字元是 ASCII(例如 `void paymentéSpecial() {}`),後面帶重音字元則沒事。

**實測**:

```python
# 檔內容:
#   @Test\n    void 測試付款成功() { }
#   @Test\n    void paymentéSpecial() { }
lum.discover_test_methods(root, dict(lum.TEST_PROFILES["java-junit"]))
# => {'paymentéSpecial'}   —— 中文方法名整個消失,沒有任何錯誤或警告
```

影響:如果某篇筆記寫 `[test:測試付款成功]` 綁一個真的存在、真的會被 JUnit 執行的中文方法名測試,`discover_test_methods` 找不到它,`_classify_one` 判定會落到 `dangling`(因為它也不會出現在 `hay_for()` 的 haystack 裡?——這點我沒有跑第二次去確認 `build_code_haystack` 是否同樣受限,但至少 `methods_for` 這一關會誤判成不存在),導致 bound-tests-gate 誤擋一個其實有真證據的高風險 PR。

列為 minor 而非 major 的理由:①這不是這次 diff 新引入的退化——`KOTLIN_TEST_RE`、`TEST_METHOD_RE`(C#)等既有正則的捕獲群組用的都是同一種 `[A-Za-z_]\w*` 寫法,是整個工具鏈既有的、跨語言一致的既有限制,這次只是把同一個限制延伸到新的 `java-junit`;②真正踩到的前提是「方法名整個以非 ASCII 字元開頭」,在 Java 生態裡少見(即使中文團隊也多半用拼音或英文命名測試方法),命中機率遠低於發現①②。仍值得記一筆,因為這個 repo 本身是中文優先、且審查鏡頭明確要求測 Unicode 方法名。

---

## 已測過但沒發現問題的邊界(供交叉核對,附指令與輸出)

1. **`_init_config_skeleton` 的 `ranked[:3]`→`ranked`(多語言全列)**:已知的可辨識副檔名總共只有 18 種(`_stack_guess()` 反查出來的,不是 50 種——這點值得指出,因為題目假設「50 種副檔名」,但工具目前的正典表根本不到 50 種已知副檔名,未知副檔名一律在 `_stack_ext_counts` 就被濾掉,不會進到 `_init_config_skeleton` 的迴圈)。用全部 18 種各建 2 個檔實測:

   ```
   python3 -c "... lum._init_config_skeleton(root) ..."
   ```
   輸出是合法 JSON,7 個平台鍵(swift/kotlin/java/node/csharp/dart/python),`.kts`/`.jsx`/`.mjs`/`.cjs`/`.mts`/`.cts`/`.tsx` 正確地被同語言家族的 profile 吸收合併(這是設計本來就要的行為,不是撞名 bug);`.sql`/`.vue`/`.ps1` 因為沒有任何 `TEST_PROFILES` 認領而被跳過,不會產出殘缺的平台項。沒有發現撞名/覆蓋/非法 JSON。

2. **`.JAVA` 大寫副檔名 / 無副檔名 / 檔名含空白與中文**:`_stack_ext_counts`(`.lower()`)、`discover_test_methods`(`Path(f).suffix.lower()`)、`_stack_key_for_file`(`.lower()`)、呼叫 `_idiom_skill_for` 前的 `ext = pf.suffix.lstrip(".").lower()` 都一致做了小寫正規化。實測 `結帳 測試 Checkout.JAVA` 檔名+大寫副檔名,方法掃描與副檔名計數都正常。沒有發現 bug。

3. **七題 Java 觸發正則(when/when_raw)的病態輸入**:把全部 java 題目用到的正則(含 `when_raw` 的 SQL 型)逐條對抗性測試(近似匹配但故意失敗的長輸入,1k~100k 字元),沒有一條超過 0.5 秒,也沒有 catastrophic backtracking 的跡象。`_stack_applicability` 是逐「diff 行」比對,不是整檔,天生就比 `JAVA_TEST_RE`(整檔比對)安全很多。

4. **巢狀註解 `/* outer /* inner */ still outer */`**:`re.sub(r"/\*.*?\*/", "", txt, flags=re.S)` 的非貪婪比對會停在第一個 `*/`,這跟 Java 編譯器本身「不支援巢狀註解」的語意一致(Java 也是在第一個 `*/` 結束),不是 bug。

5. **`@Test` 出現在檔尾、後面完全沒內容**:`JAVA_TEST_RE.search()` 正確回傳 `None`,不會拋例外或掛住(前提是檔案裡沒有大量重複 `@Test`——見發現①)。

---

## 結論

最嚴重 severity:**major**(兩條:發現①效能二次方拖累擋點指令、發現②字串字面偽造 real 測試綁定,雙雙 blocking)。blocking 共 2 條(發現①②);另有 1 條 minor/不 blocking(發現③)。
