severity: major

severity: major
blocking: 是
引句:「r"@(?:Test|ParameterizedTest|RepeatedTest)\b.*?\bvoid\s+([A-Za-z_]\w*)\s*\("」
`JAVA_TEST_RE` 在每個無法配對的 `@Test` 起點都會用 `.*?` 掃到檔尾，形成二次方退化。實測無 `void` 的輸入從 6.5 KB／0.0146 秒、13 KB／0.0594 秒、26 KB／0.2365 秒增至 52 KB／0.9481 秒；約 260 KB 的同型輸入超過 30 秒仍未完成。`discover_test_methods` 會對每支 Java 測試檔執行此正則，因此單一惡意或生成出的測試檔即可卡住 doctor、合約檢查及推送流程。位置：`scripts/lumos:3373`。

實跑：
```text
$ python3 -c '... SourceFileLoader("lum","scripts/lumos") ... for n in (500,1000,2000,4000) ...'
500 6500 0 0.0146
1000 13000 0 0.0594
2000 26000 0 0.2365
4000 52000 0 0.9481
```

severity: major
blocking: 是
引句:「# 代價:萬一有人把 @Test 標在非 void 方法上(JUnit 會拒跑),這條會抓到下一個 void 方法的名字。」
正則沒有把註解與緊接的方法宣告限制在同一個 declaration。除註解在非 `void` 方法上的已知情況外，JUnit 合法的 composed annotation 定義也能使用 `@Test` 作為 meta-annotation；正則會越過整個 annotation type，將後續任意類別的第一個 `void` 方法誤報為測試。這會讓 Check T 接受一個測試引擎根本不會執行的方法，破壞「綁到可執行證據」的核心保證。位置：`scripts/lumos:3369`。

實跑：
```text
$ python3 -c 'from importlib.machinery import SourceFileLoader; m=SourceFileLoader("lum","scripts/lumos").load_module(); s="import java.lang.annotation.*;\n@Test\n@Retention(RetentionPolicy.RUNTIME)\n@interface FastTest {}\nclass Helper { void setUp() {} }"; print(m.JAVA_TEST_RE.findall(s))'
['setUp']
```

總結:最嚴重 severity 是 major、blocking 2 條。
