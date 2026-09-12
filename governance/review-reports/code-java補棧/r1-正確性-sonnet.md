severity: blocker

---

severity: blocker
blocking: 是
引句:「r"@(?:Test|ParameterizedTest|RepeatedTest)\b.*?\bvoid\s+([A-Za-z_]\w*)\s*\(",」
file: `scripts/lumos:3373`

**什麼輸入會出錯**:`JAVA_TEST_RE` 用 `.*?`(非貪婪、`re.S` 跨行)從 `@Test` 一路找到下一個 `void 方法名(`。去註解(c-style,剝 `//` 與 `/*...*/`)有做,但**字串字面完全沒剝**。只要 `@Test` 到真正目標方法之間出現任何字串(最常見就是 `@DisplayName("...")`)裡剛好含有「void 加識別字加左括號」這種文字,regex 會先在字串裡「找到」一個假方法名,然後把真正要找的、後面才出現的那個真測試方法整個跳過——不是漏掉一部分,是那支真測試從此在 `discover_test_methods` 回傳的集合裡完全消失。

實測(用 `importlib.machinery.SourceFileLoader` 載入 `scripts/lumos`,對一支合成的 Java 測試檔跑 `discover_test_methods`):

```java
// /tmp/javaproj/src/test/java/shop/Weird.java
package shop;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

class Weird {
    @Test
    @DisplayName("should call void run() properly")
    void realTargetMethod() {
        assertTrue(true);
    }

    @Test
    boolean returnsNonVoidByMistake() {
        return true;
    }

    void unrelatedHelperFarBelow() {
        doStuff();
    }
}
```

```python
import importlib.machinery, importlib.util
from pathlib import Path
loader = importlib.machinery.SourceFileLoader("_lumos_inproc", "/Users/enzo/harness/lumos-toolchain/scripts/lumos")
spec = importlib.util.spec_from_loader("_lumos_inproc", loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
prof = dict(mod.TEST_PROFILES["java-junit"])
print(mod.discover_test_methods(Path("/tmp/javaproj"), prof))
```

輸出:
```
discovered methods: {'unrelatedHelperFarBelow', 'run'}
```

真正標了 `@Test` 而且回傳型別確實是 `void` 的 `realTargetMethod` **完全沒被收進去**;反而多了兩個根本不是測試方法的名字:
- `run`——是從 `@DisplayName("should call void run() properly")` 這句字串裡「void run(」直接被當成方法簽章抓出來的,`run` 這個字在檔案裡連方法定義都沒有。
- `unrelatedHelperFarBelow`——這是第二個 `@Test`(標在 `returnsNonVoidByMistake`,回傳型別是 `boolean` 不是 `void`,JUnit 本來就不會真的跑它)之後,regex 找不到緊接著的 void 方法,於是一路跳過整個 `returnsNonVoidByMistake` 方法體,抓到再下一個、完全無關的 `unrelatedHelperFarBelow`。程式裡的註解只承認第二種情況(「代價:…這條會抓到下一個 void 方法的名字」),但沒發現字串字面(第一種情況)會讓一支**寫得完全正確、真的有 `@Test`+`void`** 的方法憑空消失。

**錯成什麼樣、為什麼是 blocker**:`discover_test_methods` 的回傳集合是 `_platform_test_index` / `_classify_one`(`scripts/lumos:8579` 附近)拿去判斷 `[test:X]` 綁定是 `real`/`fake`/`dangling` 的唯一依據——這正是本次 impact 固定席釘住的 `bound-tests-gate.md` ★INVARIANT★(「任一紅/懸空(dangling/fake)…→ blocked=True rc1」)。照上面的重現:一支貨真價實、JUnit 真的會執行的 `@Test void realTargetMethod()`,只因為它的 `@DisplayName` 字串裡剛好出現「void 識別字(」這種常見英文敘述(例如描述被測方法本身是 void 回傳、或描述某個 callback),就會被 Check T / `code-loop check` 誤判成「懸空」或「偽證據」,擋下一個完全正常、有真測試覆蓋的 Java 分支;反過來,像 `run` 這種從字串裡冒出來的假名字也可能巧合對上某條 `[test:run]` 的合約引用,讓沒有任何測試方法撐著的宣稱被誤判成「real」而放行。這兩個方向都直接命中 impact 附帶的 fixed-seat 合約,屬於會實際影響 gate 判定結果的正確性錯誤,不是風格或效能問題,故列 blocker。

---

severity: major
blocking: 是
引句:「'\\bActivity\\b', '\\bContext\\b', 'findViewById', 'RecyclerView'」
file: `scripts/lumos:16694`

**什麼輸入會出錯**:`java-android` 這題的觸發字裡有一條裸的 `\bContext\b`,而 `_STACK_TRIGGERS` 對所有 `when` pattern 一律用 `re.I`(不分大小寫)編譯。`Context`/`context` 是 Java 後端程式裡極常見的識別字(Spring 的 `ApplicationContext`、`SecurityContext`、JPA 的 `PersistenceContext`、Servlet 的 `ServletContext`……幾乎每個非 Android 的 Java 專案都會有變數或型別直接叫 `Context`/`context`),跟 Android 生命週期完全無關。這批改動在計劃裡明確承諾「兩邊都吃得到…改 Spring/JPA 的檔不會被問 Activity 洩漏,改 Activity 的檔也不會被問交易邊界」,但 `\bContext\b` 這一條會讓這個承諾在最常見的 Spring 場景下直接破功。

實測:

```python
import importlib.machinery, importlib.util
loader = importlib.machinery.SourceFileLoader("_lumos_inproc", "/Users/enzo/harness/lumos-toolchain/scripts/lumos")
spec = importlib.util.spec_from_loader("_lumos_inproc", loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)

jpa_service_lines = [
    "@Service",
    "class OrderService {",
    "    @Autowired",
    "    private ApplicationContext context;",
    "    List<Order> all() { return repo.findAll(); }",
    "}",
]
app, meta = mod._stack_applicability({"java": jpa_service_lines}, 300)
print({r['id'] for r in meta['java'] if r['applicable']})
```

輸出:
```
{'java-data', 'java-android'}
```

這是一支徹頭徹尾的 Spring Data JPA 後端 service(用 `findAll()` 觸發 `java-data` 完全正確),裡面沒有任何 Activity、View、AsyncTask 之類的 Android 東西,只因為注入了一個名叫 `context` 的 `ApplicationContext` 欄位,就連帶被問到「Android:Context/Activity 有沒有被單例、static 欄位或長活物件握著…」這種跟這支檔案毫無關係的問題。單獨一行 `ApplicationContext context = SpringApplication.run(...)` 或 `SecurityContext context = SecurityContextHolder.getContext();` 也都會單獨命中 `java-android`(已各自驗證,見下方補充輸出)。

補充驗證(單行、無 java-data 混淆):
```
ApplicationContext context = SpringApplication.run(App.class, args);  -> {'java-android'}
SecurityContext context = SecurityContextHolder.getContext();          -> {'java-android'}
```

**錯成什麼樣**:這不是「多問一題無傷大雅」的效能建議噪音,而是這批改動自己白紙黑字寫明的設計承諾(平台特有題互不干擾)被最常見的 Spring/JPA 寫法直接打臉——任何用了 `ApplicationContext`/`SecurityContext`/`@PersistenceContext` 之類 Spring/Java EE 標準物件的後端檔案,都會被要求回答一組完全不適用的 Android 生命週期問題,且因為棧別提問走的是表態閘(需要人工把「applicable」的題目答掉才能過 `code-loop`),這會對幾乎所有 Spring 後端專案造成系統性的誤判與額外表態負擔。判 major 而非 blocker,是因為它不會讓錯誤的判定「悄悄放行」或阻擋工具本身運作,只是逼人多答一題本不該出現的問題,且該問題容易被一眼識破為誤判。

---

總結:本次改動最嚴重問題是 blocker——`JAVA_TEST_RE` 因未剝字串字面,會讓真正有效的 `@Test void` 方法憑空消失、並把字串裡的文字誤判成方法名,直接影響 Check T / code-loop 的 bound-tests 判定(fixed-seat 合約範圍內)。另有一條 major——`java-android` 的 `\bContext\b` 觸發字過於寬泛,會讓幾乎所有 Spring/JPA 後端檔案被誤問 Android 生命週期問題,違反計劃自己宣稱的「平台特有題互不干擾」。blocking 共 2 條(blocker 1 條、major 1 條)。
