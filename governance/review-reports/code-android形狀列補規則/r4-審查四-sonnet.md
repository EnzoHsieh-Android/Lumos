severity: major

整體判斷：第三輪後的修補大致守住了它聲稱的項目，只找到一條會誤擋推送的規則誤報。`kotlin_rulepack_security_rules` 子集 405 項全過，`check.py --catalog-only` 回報型錄問題 0 個。

severity: major
blocking: 否

**API-2 的 `.asFlow()` 排除只認接收者「結尾」，中間夾 `.buffer()` 這類算子的 Flow 仍被報成 error**

- 輸入：
  ```kotlin
  suspend fun i(ds: List<Deferred<Int>>) = ds.asFlow().buffer().map { it.await() }.toList()
  ```
- 重現：對臨時目錄的 kt 檔跑 `ast-grep scan -c sgconfig.yml --json=compact`，這行被報成 `kt-map-await-deferred`（error，推送閘會擋）。
- 原因：`constraints.L` 的 `not: regex: '\.asFlow\(\)$'` 在這個輸入裡綁到的 `$L` 是 `ds.asFlow().buffer()`，結尾不是 `.asFlow()`，排除沒生效。
- 為什麼要緊：`asFlow().map { async{…} }.buffer(n).map { it.await() }` 是常見的「有上限並行」寫法。Flow 沒有 `awaitAll` 可改，規則給的建議在這裡不成立。
- 規則包節點只說接收者以 `.asFlow()` 結尾的已排除，沒提中間夾 `.buffer()`、`.flowOn()`、`.conflate()` 的情況。〈天花板〉寫的是「變數看不出型別」，這個形狀不在其中。
- 另外已記在〈天花板〉、我不重複報：Play services 的 `Task`、retrofit 的 `Call`、型別是 `Flow<Deferred>` 的變數，這輪實跑確實都被報。
- 建議：把排除改成接收者鏈裡任何位置出現 `.asFlow()`（例如去掉 `$`、改用 `\.asFlow\(\)`），再補一例。C202 的 `asFlow().toList().map` 應該仍報，要保留。
- 這條的重現是我在複本實跑，不是從 diff 抄來的；diff 裡對應的規則段落是下面這行。

引句:「      regex: '\.asFlow\(\)$'」

**三問的結論（其餘都沒有找到問題）**

- ① C185~C221 與 Key 清單：C218~C221 逐個 Key 各一例；我另外實跑 `@ApiKey`（同檔宣告為 `@Qualifier`）的綁定，確實被當成限定詞而不是多重綁定，所以 `\w+Key` 改窄後的漏報確實修好了。泛型型別 `List<String>` 對 `List<Int>`、可空回傳 `Foo?`、帶接收者的函式，實跑都沒有誤報。
- ② 修補有沒有帶進新問題：Key 清單改窄後，沒找到該排除卻沒排除的多重綁定。Dagger 的 `@MapKey` 一定配 `@IntoMap`，而 `@IntoMap` 仍在排除清單裡。
- ③ 那 7 項「等價改壞」：拿掉 `^` 後，只有註解文字裡又套了別的註解（例如 `@Wrapper(@Named("x"))`）這種理論輸入才會讓結果不同。我試了兩個這類輸入，結果都跟有 `^` 時一樣，沒找到真實寫法能區分，所以我認為判定在實務上成立，不報。
- 我沒查到 Hilt 官方原始碼對 `fromView` 允許哪幾個元件（兩個官方網址都回 404），所以 `ViewNoFragmentComponent`、`ViewWithFragmentComponent` 的對應「未驗」。

我在 `/tmp/lumos-seat-work/code-android形狀列補規則/審查四-sonnet/` 建過的路徑已全數刪除，目前沒有殘留。
