severity: major

四條規則我都照 spec 寫出來並用 ast-grep 0.51.1 實跑。預期值表裡的 9 列全部符合,但有 6 個洞是 spec 沒寫到的。

## 固定席:對 `Systems/kotlin規則包` 的影響

不影響。四條規則先放 `rules-unwired/`,不在消費專案範本宣告的 `sgconfig.yml` 裡,不進新增告警閘。`check.py` 的 `_DIR_SEVERITY` 也允許 `rules-unwired` 放 hint 等級。該節點目前沒有合約行。

## Findings

severity: major
blocking: 是

**F1 ARCH-59 把 `@IntoSet`、`@Suppress` 這類非限定詞註解當成限定詞,造成誤報,與 spec「寧可少報」相反**
- spec 段落:〈範圍〉第 1 點(ARCH-59 清單寫死,清單外一律當限定詞)與〈天花板〉。
引句:「清單外的註解一律當成限定詞(寧可少報)」
- 我寫的規則照字面實作。範例是同一個 object 裡一個 `@Provides @IntoSet fun a(): Interceptor` 加一個 `@Provides fun b(): Interceptor`,以及 `@Provides @Suppress("x") fun s(): Foo` 加 `@Provides fun plain(): Foo`。
- 執行 `sh run.sh src/h2.kt` 後,第 12 行(plain 的 `b`)、第 59 行(`plain`)、第 62 行(`u`)都被報。這三個函式都是無辜的。
- 原因:`@IntoSet`、`@IntoMap`、`@StringKey`、`@Suppress`、`@Deprecated`、`@OptIn` 都不在清單裡,所以被當成限定詞。
- 當成限定詞的結果是「旁邊的無註解函式被報」,方向是多報,不是少報。多重綁定(multibinding)與 `@Suppress` 在 Hilt module 裡很常見。
- spec 要補的有兩項:清單要涵蓋這些註解,或改成只有認得的限定詞才算(`@Named`、`@Qualifier` 標記的註解)。好例也要加一段「容易誤報」的樣本。

severity: major
blocking: 是

**F2 `m.scan` 回傳 `(ruleId, file)`,沒有行號,spec 的「比對報在哪幾行」沒寫怎麼取得**
- spec 段落:〈範圍〉第 5 點。
引句:「用規則包設定檔實跑 ast-grep,比對**報在哪幾行**」
- `check.py` 的 `scan()` 只取 `d["ruleId"]` 和 `d["file"]`。`t_kotlin_rulepack_security_rules` 也只用 `(rid, rel)` 計次。
- 行號在 JSON 的 `range.start.line`,但現有 `scan` 把它丟掉。
- spec 沒說是新寫一個回傳行號的函式,還是改 `scan`。改 `scan` 會牽動所有現有呼叫端。
- 如果實作者沿用既有測試的次數比對,S2 就退化成「檔裡報了幾次」,抓不到「報錯行」。
- 補充一點:ast-grep 報的是節點起始行。
  - ARCH-59 報到第一個註解那一行(`@Provides` 那行),不是 `fun` 那行。
  - API-2 的鏈式 `ds\n.map{…}` 報在 `ds` 那行。
  - spec 預期值表寫「只報 a 那一行」有歧義,得明寫是哪一行。

severity: major
blocking: 是

**F3 預期值表只覆蓋每條規則的一個樣式,「規則被刪掉某個樣式」不會讓任何測試變紅**
- spec 段落:〈預期值表〉和〈範圍〉第 1 點。
引句:「`$L.map { it.await() }`、`$L.map { $X -> $X.await() }`、`$L.forEach { it.await() }`、`$L.forEach { $X -> $X.await() }`」
- API-2 有 4 個樣式,表裡只有 `ds.map { it.await() }`。
  - S1 只要求每條規則壞例至少命中 2 處。
  - 刪掉 3 個樣式只留 map,測試照綠。
  - 我把規則縮成單一 map 樣式後,表裡兩列仍全對。
- ARCH-62 有 4 組對應(fromApplication、fromActivity、fromFragment、fromView),表裡只有 fromApplication 對 Activity 和 Singleton。fromActivity、fromFragment、fromView 的元件對應寫錯或互換,沒有任何測試會紅。
- ARCH-59 的清單(Singleton、Reusable、JvmStatic、`*Scoped`、Binds)沒有逐項的列。
- UI-33 的 `onDispose {}` 與 `onDispose { }` 兩種寫法也沒有對應的列。
- 要補的列至少有:
  - API-2:forEach、具名 lambda 參數,以及每個樣式各一列。
  - ARCH-62:fromActivity、fromFragment、fromView 各一列壞例加一列好例。
  - ARCH-59:清單裡每個註解各一列。
  - 同一個 object 裡 `@Binds` 與 `@Provides` 混用的一列。

severity: major
blocking: 是

**F4 〈待查證〉改壞測試裡寫死的「51 列、48 列」沒列入要改的清單,改完後該測試失去隔離**
- spec 段落:〈範圍〉第 5 點最後一項。
- 檔案證據:`scripts/test_lumos.py` 的 `_KT_STATS_MUTATIONS`(約 129636 行起)。
- 其中三處把字串寫死:`.replace("- 待查證:51 列", "- 待查證:52 列")`、`"...50 列"` 與 `"規則代號待查 48 列"→47`。
- API-2 拿掉後,真型錄的統計會變成 50 列、47 列。這幾個 `replace` 找不到原字串,變成不生效。
- 那兩個案例本來的設計是「只留給〈待查證〉跟主表的雙向比對抓(不讓統計那道代抓)」。現在統計行沒跟著改,統計檢查會代抓,`pending_problems` 被拿掉測試照紅不到。
- spec 只說「`_KT_STATS_LINES` 的寫死值照新數改」和「換一列當錨點」。這幾個寫死的字串、以及 DATA-27 那條 52 列的變異,都沒列入。
- 該行的 `| API-2 | IJ:「Use awaitAll()` 與 `| API-3 | IJ:「Unused Deferred」` 的錨點則仍存在,不用動。

severity: minor
blocking: 否

**F5 解析器限制不只 spec 說的那一種,ARCH-59 也受影響,而且觸發條件更廣**
- spec 段落:〈實驗〉與〈天花板〉,後者只把此限制算在 ARCH-62 頭上。
- 我實跑重現了 spec 說的情形:兩個註解加單行 interface 本體會漏報。
- 另外以下寫法也失效,spec 沒列:
  - 兩個註解分兩行寫,但 `{` 在下一行、結尾 `}` 跟在最後一個成員同一行(`    fun f(): F }`)。
  - `public interface A7 { fun f(): F }` 加兩個註解。
  - `@InstallIn(` 參數跨多行,且 interface 本體寫在一行。
  - 兩個註解顛倒順序,或兩個註解寫在同一行。
- ARCH-59 的 `@Module @InstallIn(...) object M { @Provides fun a(): X = x(); … }`(一行本體)和 `fun b(): X = x() }` 的結尾括號寫法都被漏報(`src/p2.kt` 的 M3 與 M6)。
- 後果都是漏報,不是誤報,但〈天花板〉只寫了 ARCH-62 一條。REVISIT 的「一行寫完的 interface」要連 ARCH-59 的 object/class 一併量。

severity: minor
blocking: 否

**F6 API-2 的樣式在幾種常見寫法上漏報,也有 spec 沒列的誤報來源**
- spec 段落:〈範圍〉第 1 點(API-2 形狀)。
- 實跑 `src/t2.kt`、`src/t4.kt` 的結果:
  - 漏報:lambda 第一行是 `//` 或 `/* */` 註解(本體前有註解)、`map { d: Deferred<Int> -> d.await() }`(有型別的參數)、`map({ it.await() })`(括號形式)、`it.await() + 1`、`it?.await()`、`it.await()!!`、`{ x -> val y = x; y.await() }`。
  - 誤報(spec 只提 Play services `Task`):`Flow<Deferred>.map { it.await() }` 被報,Flow 的 map 本來就是序列式,不需要 awaitAll。
  - `{ it.await(); 1 }` 也被報,算合理。
- 鏈式 `ids.map { scope.async{…} }.map { it.await() }` 有報,也是 KDoc 要抓的寫法。
- 多行具名參數和尾隨 lambda 正常。
- 這些會影響保留集的命中數與誤報比例,spec 的天花板應該先寫出,尤其是有型別的 lambda 參數。

severity: minor
blocking: 否

**F7 UI-33 的誤報範圍比型錄形狀寫得廣**
- spec 段落:〈預期值表〉第 3 列。
- 實跑 `src/t5.kt`:`if (!enabled) return@DisposableEffect onDispose { }`(提早返回的合法寫法)被報。
- 型錄 UI-33 的形狀是「DisposableEffect 只有空 onDispose 且無註冊呼叫」,但 spec 預期值表第 3 列要求 `log("x"); onDispose { }` 也要報,規則其實不看有沒有註冊。這兩個口徑不一致,spec 沒講哪個為準。
- 好例該收一段提早返回的寫法作為「容易誤報」的樣本。

severity: minor
blocking: 否

**F8 ARCH-62 在少數寫法下漏報或誤報,spec 沒列**
- spec 段落:〈範圍〉第 1 點。
- 實跑 `src/e3.kt`:
  - 漏報:具名參數 `fromApplication(context = ctx, entryPoint = E::class.java)`、完整套件名 `dagger.hilt.android.EntryPointAccessors.fromApplication(...)`、巢狀 `Holder.E12::class.java`、沒有本體的 `interface E6`。
  - 誤報:`import ...SingletonComponent as SC` 後 `@InstallIn(SC::class)` 配 `fromApplication`(別名改了名字,規則不認得;我用邏輯推斷,沒實跑,但規則是用名字比對的)。
- 實作提醒:ast-grep 用 Rust regex,不支援 lookahead。「不是那個元件」得用 `all: [regex InstallIn, not: regex 元件名]` 的寫法,不能寫 `InstallIn\((?!…)`。我第一次就這樣寫過,載入失敗。
- 規則形狀與 `@InstallIn` 帶多個元件時的語意(含對應元件就不報)也值得寫進 spec。

severity: minor
blocking: 否

**F9 S5 與升級搬目錄的耦合**
- spec 段落:〈範圍〉第 5 點 S5 與第 4 點。
引句:「同時驗四列型錄現成規則欄的規則 id 在規則包裡存在、在計劃寫的目錄」
- 量完過關的規則會搬到 `rules/` 並升 error,S5 寫死「在 `rules-unwired/`」的話,搬完就會紅。
- 要讀型錄通電批次欄的值決定預期目錄。
- 另外 S2 的逐例表掃的設定檔,要涵蓋搬過去後的 `sgconfig.yml`,照 `t_kotlin_rulepack_security_rules` 跑全部 `m.CONFIGS` 即可。

## 已驗,無 finding

- **預期值表 9 列**:全部符合。
  - 指令:`sh run.sh src/t1.kt`、`src/t3.kt`、`src/h1.kt`、`src/e2.kt`。
  - 輸出摘要:API-2 報 map、不報 `awaitAll`;UI-33 報 `onDispose { }`、不報有 `remove` 的那段;ARCH-59 報 a、a+c 兩行、不報不同型別;ARCH-62 報 Activity 對 `fromApplication`、不報 Singleton 對 `fromApplication`、不報 `Other::class.java`。
- **ARCH-59 只比對回傳型別**:`@Named("q") c: Foo` 的參數限定詞不影響,`fun a(@Named("q") c: Foo): OkHttpClient` 仍被報(`src/h2.kt` 第 21 行),符合 spec 實驗那條。泛型實參不同(`List<String>` 對 `List<Int>`)不報。
- **解析器限制本身**:重現 spec 描述的「一行 interface 加兩個註解被解析成 `prefix_expression`」,用 `--debug-query=ast` 確認。
- **效能(spec 實務隱患那條)**:
  - 200 個函式的 Hilt module,0.02 秒。
  - 2000 個函式同型的 module(6000 行),1.24 秒;2000 個函式不同型,2.09 秒。這是平方成長。
  - 200 組 interface 加呼叫(2000 行),0.22 秒,這份檔同時有 200 個命中。
  - 2000 組(16000 行),11.5 秒。
  - 現有規則包整包掃 6000 行檔 0.33 秒、unwired 0.10 秒、2000 行檔 0.17 秒/0.05 秒。
  - 在真實規模(一個 Hilt module 一般不到 50 個函式)不是問題;病態規模下才會慢,而且遠低於 `SCAN_TIMEOUT` 120 秒。
- **S1 / `check()` 的樣本要求**:
  - 壞例至少 2 處命中、好例至少 2 段且零命中、`review-fp-` 開頭的檔案只對 `rules-review` 與 `rules-unwired` 規則豁免。
  - 訊息要求 `[型錄編號]` 開頭、≤120 字、含分號並有「改用」或「改成」、不含 `$`。
  - 這些都適用於四條新規則,spec 引用的句式符合。
  - 有一個提醒:ARCH-62 好例樣本的 interface 要多行本體,否則會被解析器吃掉變成零命中,過不了「好例至少兩段」。

## 總結

最嚴重 severity:major;blocking 4 條(F1、F2、F3、F4),非 blocking 5 條。

## 我建過的路徑

- `/tmp/lumos-seat-work/android形狀列補規則/規則可行-sonnet/rules/a.yml`:四條實驗規則。
- `/tmp/lumos-seat-work/android形狀列補規則/規則可行-sonnet/sgconfig.yml`
- `/tmp/lumos-seat-work/android形狀列補規則/規則可行-sonnet/run.sh`
- `/tmp/lumos-seat-work/android形狀列補規則/規則可行-sonnet/src/`:`t1.kt` 到 `t5.kt`、`h1.kt`、`h2.kt`、`e0.kt` 到 `e3.kt`、`p1.kt`、`p2.kt`。
- `/tmp/lumos-seat-work/android形狀列補規則/規則可行-sonnet/big/`:`b200.kt`、`b2000.kt`、`b2000d.kt`、`e200.kt`、`e2000.kt`。
- 我另外用過 `/tmp/h1.txt` 和 `/tmp/lumos-seat-work/out.txt`,已刪。

佐證:

- file: `scripts/test_lumos.py:129607`(`_KT_STATS_LINES`)
- file: `scripts/test_lumos.py:129636`(`_KT_STATS_MUTATIONS`)
- file: `configs/ast-grep/kotlin-android/check.py:914`(`scan` 回傳 `(ruleId, file)`)
- file: `configs/ast-grep/kotlin-android/check.py:886`(`message_problems`)
