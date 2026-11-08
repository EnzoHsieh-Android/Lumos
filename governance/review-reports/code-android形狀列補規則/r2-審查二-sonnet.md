severity: major

找到 2 條 major、2 條 minor。四條新規則的行為都對,`check.py` 與相關測試也全綠(`check.py` 0 問題;`-k kotlin_rulepack` 328 過、`-k kt_catalog` 202 過)。問題集中在測試抓不住的改壞,其中一條正是上一輪修補聲稱已補好的那類。

全部實驗都在 `/tmp/lumos-seat-work/code-android形狀列補規則/審查二-sonnet/`。我沒動 repo。改壞測試是在複本 `cp1/` 裡跑,並用對照組確認複本的規則包確實有被測試載入:把 `@Named` 比對改壞後,`C134` 和 `t_kotlin_rulepack_samples` 變紅。

severity: major
blocking: 是

ARCH-59 的 `plain-provider` 清單含 `Singleton`、`Reusable`、`[A-Z]…Scoped`,但沒有任何例子或樣本用到這幾個。`@Provides @Singleton fun a(): OkHttpClient` 搭配另一個 `@Named` 的同型別綁定,是最常見的壞形狀,卻沒被測試保護。

- 重現:在複本 `cp1/configs/ast-grep/kotlin-android/rules/architecture.yml` 把 `Binds|Singleton|Reusable` 改成 `Binds|Reusable`,跑 `LUMOS_AST_GREP=<sg> python3.14 scripts/test_lumos.py -k kotlin_rulepack_security_rules`,結果 `277 passed, 0 failed`。
- 同一改壞下,我另寫的 `@Provides @Singleton fun a()` 加 `@Provides @Named("x") fun b()` 兩個同型別綁定,改壞版掃不出、原規則報在第 7 行。
- 逐例表 `C134`~`C148` 和 `samples/{bad,good}/kt-hilt-binding-missing-qualifier` 都沒有 `@Singleton`、`@Reusable`、`…Scoped`。

引句:「regex: '\A(\s*(@(Provides|Binds|Singleton|Reusable|JvmStatic|Suppress|Deprecated|OptIn|[A-Z][A-Za-z]*Scoped)」

severity: major
blocking: 是

ARCH-62 的泛型寫法 `fromFragment<$I>` 和 `fromView<$I>`,對應改壞測不到。上一輪被點的是「fromFragment、fromView 對應改壞測不到」,這輪只補了 `::class.java` 形式的例子;泛型形式只有 `fromApplication<E>` 有例(`C145`),`fromActivity<>` 只靠壞例樣本的命中次數 ≥2 間接守著。

- 重現:在複本 `rules-unwired/architecture.yml` 刪掉 `fromFragment<$I>($$$)` 和 `fromView<$I>($$$)` 兩行,跑 `-k kotlin_rulepack`,結果 `328 passed, 0 failed`。
- 原規則對 `fromFragment<E>(f)`、`fromView<E>(v)`、`fromActivity<E>(v)`(`E` 裝在 `SingletonComponent`)都會報(第 9、10、11 行),所以是測試缺口,不是規則錯。
- 全 repo `grep -c "fromFragment<\|fromView<" scripts/test_lumos.py` 得 0,樣本目錄裡也沒有。

引句:「- pattern: EntryPointAccessors.fromFragment<$I>($$$)」

severity: minor
blocking: 否

`utils/has-registration-call.yml` 檔頭寫「不論前面有沒有接收者」,但「沒有接收者的裸呼叫」(例如 `listen()`、`registerX()`)那一支沒有任何測試或樣本。UI-32 的壞例樣本全是 `mgr.registerListener`、`view.addOn…` 這種有接收者的寫法。

- 重現:在複本刪掉第一個 `any` 分支,`-k kotlin_rulepack` 仍是 328 過。
- 改壞後的實際差別:`DisposableEffect { listen(); onDispose { } }` 會從「UI-32 報」變成「UI-33 報」,兩條給出相反的建議。我掃過確認。
- 這個缺口在舊 UI-32 就有,現在改成兩條規則共用同一份判斷,影響變大。UI-33 只在 `rules-unwired/`,所以我只給 minor。

引句:「regex: ^(add\w*(Listener|Observer|Callback)|register\w*|subscribe|setOn\w+Listener|listen)$」

severity: minor
blocking: 否

這是修補自己帶進來的問題:`@InstallIn(` 的比對改成 `[\s\S]*` 跨行後,括號內夾的註解文字也會被吃進去。

- 輸入:`@InstallIn(\n    ActivityComponent::class, // SingletonComponent::class\n)` 加 `EntryPointAccessors.fromApplication(c, E3::class.java)`。
- 結果:該報沒報,漏報。
- 範圍:`[\s\S]*` 只在 annotation 節點內,不會越過 `)` 吃到下一個宣告,所以只有註解夾在引數裡這一種情形。
- 影響:只是漏報,不會誤報。

引句:「regex: '^@(dagger\.hilt\.)?InstallIn\([\s\S]*\bActivityComponent::class' }」

## 修補鏡頭三問

**1. 上一輪的問題有沒有修好**

- **fromFragment、fromView 的 `::class.java` 形式**:`C153`~`C155` 補上,我自己造輸入驗過,對應錯會報、對應對不報。泛型形式沒補完,見 finding 2。
- **多行 `@InstallIn` 誤報**:我造了 `@InstallIn(\n SingletonComponent::class,\n)`,不報,修好了。
- **map 的 `.asFlow()` 誤報**:我造了換行接 `.asFlow()`、`?.asFlow()`、`.asFlow()` 後面夾註解,都不報,修好了。
- **測試另寫型錄讀法**:改走 `m.main_rows()`。第 5 欄(從 0 起算)確實是「現成規則」欄(欄序為編號、名稱、壞寫法形狀、標準寫法、後果、現成規則),修好了。
- **`scan` 回傳形狀**:一律三元組。repo 內 `scan(` 的呼叫端只有 `check.py` 兩處和 `test_lumos.py` 一處,都已多解一個值,沒有漏改的兩元組解法。
- **逐例表第五欄**:`*opt` 解構對舊四元組和新五元組都正確,`()` 空元組也會被當成完整檔,新舊混用沒問題。
- **註解與檔尾換行**:`check.py` 通過,未見問題。

**2. 修補有沒有帶進新問題**

- **`[\s\S]*` 越界**:不會越過 `)` 吃到下一個宣告,只有 finding 4 那一種。
- **`asFlow` 限制**:只作用在 `$L` 上,`$L` 是別的形狀時不受影響。
  - 這個排除只管字串尾端,所以 `ds.asFlow().let { it }.map { it.await() }` 或 `.asFlow().onEach{}.map{…}` 這類尾端不是 `.asFlow()` 的 Flow 變形仍會誤報,只是少見。
  - 這是已知的單檔天花板。
- **UI-32 抽出共用判斷**:新舊 `kt-compose-dispose-empty-cleanup` 在我造的 10 種輸入(`addObserver`、`?.`、`!!.`、`setOnClickListener`、註解、兩段並列等)上輸出的行號完全相同,行為沒變。

**3. 同一族還有沒有沒改到的地方**

沒有別的 `scan` 呼叫端。另外兩個小漏報我不單列為 finding:

- `dagger.hilt.android.EntryPointAccessors.fromApplication(…)` 這種帶完整套件名的寫法不報。
- `@dagger.Named(…)` 或 `@javax.inject.Named(…)` 這種帶套件名的限定詞,ARCH-59 的 `^@Named\(` 不認,所以不報。

這兩項計劃〈天花板〉已經寫到。

## 其他說明

- 圖譜鏡頭:派工詞附的固定席筆記是逾時說明,略過。
- 角色卡(be-api-compat、be-authz):只涉及 `scan` 內部回傳形狀變更,沒有對外 API,也沒有端點,不適用。
- 效能:沒有針對大型或深層巢狀輸入另跑效能檢查。
- 我建過的路徑(都在 `/tmp/lumos-seat-work/code-android形狀列補規則/審查二-sonnet/` 底下):`t/`、`mut1/`、`cp1/`。
