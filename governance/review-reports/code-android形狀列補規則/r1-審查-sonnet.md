severity: major

審查範圍:diff 全文、`check.py --sg` 自檢(規則 228 條,問題 0)、子集測試(267 passed)、ast-grep 實跑自造輸入。跟 UI-32 改前後的比對沒有發現差異。

**UI-32 改引共用判斷後的行為比對(無差異)**
- 做法:改前版本用 `git show aacdae252:.../rules/compose.yml` 取出,放在 `/tmp/lumos-seat-work/code-android形狀列補規則/審查-sonnet/old/`。改後是 `.../new/`。兩邊各跑 `sgconfig.yml`,輸入是 25 種註冊呼叫寫法。
- 寫法涵蓋 `o.addObserver`、`register(x)`、`x?.addListener`、`x!!.registerCallback`、lambda 裡的 register、`registered`、`setOnClickListener` 等。
- 結果:改前和改後都是同樣 17 個檔被 `kt-compose-dispose-empty-cleanup` 報。剩下 8 個檔(字串裡的 addListener、`::registerX`、`unregisterListener`、非呼叫的 `x.subscribe` 等)被 UI-33 報。
- 25 個輸入裡,UI-32 與 UI-33 沒有重疊,也沒有兩邊都漏的。

**固定席筆記與角色卡**
- 固定席筆記:派工詞寫明鏡頭計算逾時、沒附,略過。
- 角色卡(be-api-compat、be-authz):這份 diff 沒有端點、對外欄位或授權路徑,不適用。

---

severity: major
blocking: 是
標題:ARCH-62 的逐例表缺 fromView 的報例,以及 fromFragment、fromView 的正當不報例;改壞這兩支的元件對應,測試和樣本照綠。

file: `scripts/test_lumos.py`(`_KTSEC_CASES` 的 C140~C152)、`configs/ast-grep/kotlin-android/rules-unwired/architecture.yml`(fromFragment、fromView 兩支)

計劃範圍 5 寫「ARCH-62 的四個 fromX 各一例報、一例不報」。實際只有:
- fromApplication:報(C140)、不報(C141、C146、C152)。
- fromActivity:報(C142)。
- fromFragment:報(C143)。
- fromView:只有不報一例(C144,用 `ViewNoFragmentComponent`)。
- 好例樣本只有 fromApplication 和 fromActivity<>。

具體改壞(我在自己臨時目錄的複本上做,沒動 repo):
```
sed -i '' 's/\\bFragmentComponent::class/\\bFragmentComponentX::class/; s/(ViewComponent|ViewNoFragmentComponent)/(ViewNoFragmentComponent)/' mutcfg/rules-unwired/architecture.yml
```
輸入是 `@InstallIn(FragmentComponent::class)` 的 entry point 搭 `EntryPointAccessors.fromFragment(f, EF::class.java)`,以及 `@InstallIn(ViewComponent::class)` 搭 `fromView(v, EV::class.java)`。
- 原版:`[]`(不報,正確)。
- 改壞版:`[16, 17]`(兩個正當寫法都被誤報)。

改壞版過得了現有測試:
- C143 預期 fromFragment 搭 Singleton 報 1 次,仍然是 1。
- C144 預期 fromView 搭 ViewNoFragment 不報,仍然是 0。
- 樣本好例沒有 fromFragment、fromView,所以也不會紅。

同樣地,整支刪掉 fromView 那一段,也沒有任何例會紅,因為沒有 fromView 的報例。

補法:至少加 fromFragment 搭 FragmentComponent 不報、fromView 搭 ViewComponent 不報、fromView 搭 Singleton 報三例。

引句:「("src/main/kotlin/C144.kt", 'package sec\n\n@EntryPoint\n@InstallIn(ViewNoFragmentComponent::class)\ninterface E {\n    fun foo(): Foo\n}\n\nfun get(x: Any) = EntryPointAccessors.fromView(x, E::class.java)\n', "kt-hilt-entrypoint-accessor-mismatch", 0, {"top": True, "lines": ()}),」

---

severity: minor
blocking: 否
標題:ARCH-62 遇到多行 `@InstallIn(` 會把正確寫法誤報成不符。

file: `configs/ast-grep/kotlin-android/rules-unwired/architecture.yml`,四個分支的 `regex: '^@(dagger\.hilt\.)?InstallIn\(.*\b…::class'`

`.` 不跨行。ktlint 預設格式、尾逗號的多行寫法會讓「含允許元件」的判斷失敗,於是走到「沒有允許元件就報」。

重現輸入(`interface` 本體寫多行,避開解析器限制):
```
@EntryPoint
@InstallIn(
    SingletonComponent::class,
)
interface E1 {
    fun foo(): Foo
}
… EntryPointAccessors.fromApplication(c, E1::class.java)
```
- 另一個輸入:`@InstallIn(\n ActivityComponent::class,\n SingletonComponent::class\n)` 同樣被報,但它明明含 SingletonComponent。
- 結果:這兩處都被 `kt-hilt-entrypoint-accessor-mismatch` 報(行 50、51)。單行寫法、`value = [..]`、完整套件名都不報。
- 逐例表、樣本、計劃〈天花板〉都沒提這個限制。規則目前只登記不擋,但推送前會印出來,給出錯的修法建議。
- 修法:`.*` 改成 `[\s\S]*`,或用 `(?s)`。

引句:「                  - has: { stopBy: end, kind: annotation, regex: '^@(dagger\.hilt\.)?InstallIn\(.*\b(SingletonComponent|ApplicationComponent)::class' }」

---

severity: minor
blocking: 否
標題:搬到會擋的 `rules/` 的 `kt-map-await-deferred`,會擋到正當寫法,而且訊息的建議對它們是錯的。

file: `configs/ast-grep/kotlin-android/rules/api.yml`

實跑輸入,以下全部被報(error):
- `fl: Flow<Deferred<Int>>` 的 `fl.map { it.await() }`:Flow 沒有 awaitAll,逐筆處理是本意。
- `List<Task<Int>>` 的 `t.map { it.await() }`:Play services 的 Task。
- `Sequence<Deferred>` 的 `ds.map { it.await() }.toList()`。

這屬於計劃〈天花板〉已承認的誤報(量測 3/40,其中 2 個是 Flow 的 map),不是新發現。補一個計劃沒講到的點:`.asFlow().map` 這類形狀其實可以直接寫成排除,例如 `$L` 不是以 `.asFlow()` 結尾,不必等 REVISIT 的三個月後。

另一邊是漏報:`ds?.map { it.await() }` 不報(實測)。

引句:「    - pattern: $L.map { it.await() }」

---

severity: minor
blocking: 否
標題:型錄 API-2 的實測狀態欄引用了已經不存在的 `review-fp` 樣本,且同一句話重複兩次。

file: `skills/kotlin-idioms/checks-catalog.md`,API-2 列

文字寫「Play services Task.await() 是已知誤報(review-fp 樣本)」,但:
- `samples/good/kt-map-await-deferred/` 下只有 `kt-map-await-deferred.kt`,沒有 `review-fp-` 檔。
- 計劃範圍 4 明說 API-2 過條件就拿掉那個樣本。
- 同欄稍後又寫一次「Play services Task.await() 是已知誤報(單檔看不到型別),這次抽樣沒出現」。
- 照前一句去找樣本會找不到。

引句:「Play services Task.await() 是已知誤報(review-fp 樣本);2026-11-09 樣本外 294 處」

---

severity: minor
blocking: 否
標題:測試 docstring 的案例編號範圍與實際新增的案例對不上。

file: `scripts/test_lumos.py`,`t_kotlin_rulepack_security_rules` 的 docstring

docstring 寫「C127~C148」,但新增案例到 C152(C149、C150、C151、C152 也在同一段),而且 C139~C148 在表裡排在 C152 之後、順序混雜。照編號範圍去找翻紅釘會漏掉 C149~C152。docstring 文末雖然有提到 C149、C150、C152,編號範圍那句仍是錯的。

引句:「形狀列補規則([[Projects/Android形狀列補規則_計劃]] S2、S4,C127~C148,選填第五欄 top 與 lines)」

---

**其他核對**
- ARCH-59 實跑:@Named、同檔 @Qualifier、@IntoSet、@Suppress、參數型別、泛型不同、nullable 回傳、companion 內與外的綁定、行內註解,都與預期一致。漏報(nullable 回傳、跨 companion)偏保守,不是誤報。
- `scan` 的 `with_lines`:不帶參數的既有呼叫(check.py 兩處)行為不變;缺 `range` 會被 `KeyError` 接住回 None;逐例表舊四元組與新五元組用 `*opt` 解包是安全的。
- 型錄〈統計〉的數字(228、error 49、warning 118、hint 49、其中 27 條、守到 131、待查證 50、規則代號待查 47)與真規則包一致,`check.py` 自檢通過。
- 次要觀察:`rules-unwired/api.yml` 檔尾被去掉換行(diff 顯示 `\ No newline at end of file`),是與本案無關的雜訊,沒發現實際影響。

我在臨時目錄建過的路徑,都在 `/tmp/lumos-seat-work/code-android形狀列補規則/審查-sonnet/` 之下:`src/`、`new/`、`old/`、`c/`、`h/`、`e/`、`d/`、`m/`、`mutcfg/`。沒有改 repo,也沒有刪除任何東西。

severity: major
(最高)
