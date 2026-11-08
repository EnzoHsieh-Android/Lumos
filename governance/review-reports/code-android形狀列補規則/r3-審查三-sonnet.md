severity: major

本輪 ARCH-59 與 ARCH-62 的結構條件有三處改壞後測試照綠(兩個 major),另有兩個 minor 漏報。四條規則的實際行為(誤報、漏報)我沒找到新的錯。C158~C184 守得住各自聲稱的那一項,修補本身沒有帶進新問題。角色卡的 be-api-compat、be-authz 不適用:這份 diff 是 lint 規則包,沒有對外 API 或端點。

驗證方式:

- 在臨時目錄複本逐項改壞,每項同時跑逐例表 C127~C184 與 `check.py --sg` 樣本自檢。
- 兩個 major 另在 `git clone` 的複本上套單一改壞,跑真測試 `-k kotlin_rulepack_security_rules`。
- 先在複本把 `fromApplication` 樣式改成 `fromApplicationZ`,測試轉紅(329 passed, 2 failed),證明複本確實讀自己的設定。
- 未驗:`lumos impact` 鏡頭逾時、沒附固定席筆記,略過;`lumos lint` 兩篇節點都是 0 問題。

severity: major
blocking: 是
ARCH-59「同型別」這個核心條件沒有任何例子守著,拿掉照綠。規則靠 `$T` 把要報的綁定和同模組裡有限定詞的綁定綁在同一個型別上,還靠 `$Q` 把註解名綁到同檔 `@Qualifier` 宣告。

- **改壞一**:拿掉自己這邊的 `$T` 那段(`all: - has: kind: user_type pattern: $T`)。
  - 輸入:同一個 module 裡 `@Provides fun gson(): Gson` 加 `@Provides @Named("auth") fun client(): OkHttpClient`。型別不同,正確結果是 0 報,改壞後多報 `gson`。
  - 結果:C127~C184 全綠,`check.py` 0 問題,真測試 331 passed, 0 failed。
  - 原因:所有 C 例和好例樣本的「有限定詞的那個」都跟「沒限定詞的那個」同型別。
- **改壞二**:拿掉同檔 `@Qualifier` 宣告那邊的 `$Q`。同檔有 `@Qualifier annotation class AuthClient`,另一個綁定掛 `@MyScopeLike`(沒宣告成限定詞),改壞後會被誤當限定詞,多報。C 例和 `check.py` 照綠。
- **補法**:各加一例。同模組不同型別的綁定要 0 報;同檔有 `@Qualifier` 宣告、但別的註解不是限定詞時不能算限定詞。

引句:「# 同一個 module 裡同型別的綁定,有的確定有限定詞、有的確定沒有,報沒有的那幾個。」

severity: major
blocking: 是
ARCH-62 有三個條件改壞照綠,其中 fragment、view 兩支的 `$I` 連結是「用自己的 entry point 比對」的核心。

- **改壞一**:fromFragment(以及 fromView)那支的 `not: has` 拿掉 `pattern: $I`。
  - 輸入:同檔 `E1` 掛 `@InstallIn(FragmentComponent::class)`、`E2` 掛 `@InstallIn(SingletonComponent::class)`,呼叫 `EntryPointAccessors.fromFragment(x, E2::class.java)`。正確結果是報,改壞後因為檔裡別處有 FragmentComponent 就不報了。
  - 結果:真測試 331 passed, 0 failed。
  - 原因:所有 C 例每檔只有一個 entry point。fromApplication 和 fromActivity 那兩支改壞會被樣本「壞例至少命中 2 處」撞掉,fragment、view 這兩支沒人撞。
- **改壞二**:`\bFragmentComponent::class` 拿掉 `\b`。
  - 輸入:`@InstallIn(ViewWithFragmentComponent::class)` 的 entry point 搭配 `fromFragment`。這是真實存在的 Hilt 元件,正確結果是報,改壞後因為字尾剛好是 FragmentComponent 而不報。
  - 結果:C 例與樣本都綠。`ActivityComponent`、`SingletonComponent` 的 `\b` 同理沒有例子。
- **改壞三**:`entry-point-not-in` 的 `has` 拿掉 `stopBy: end`。
  - 輸入:巢狀宣告 `class Host { @EntryPoint @InstallIn(ActivityComponent::class) interface Nested }`,搭配 `fromApplication(x, Nested::class.java)`。正確結果是報,改壞後不報。
  - 結果:C 例與樣本都綠。
- **補法**:加兩 entry point 同檔例(fragment、view 各一)、`ViewWithFragmentComponent` 例、巢狀 entry point 例。

引句:「- has: { kind: type_identifier, pattern: $I }」

severity: minor
blocking: 否
ARCH-59 的 `binding` 判斷把任何 `@\w+Key` 都當多重綁定的鍵,同檔宣告的限定詞 `@ApiKey` 因此被排除,規則漏報。
- 輸入:同檔 `@Qualifier annotation class ApiKey`,同模組 `@Provides fun plain(): String` 加 `@Provides @ApiKey fun key(): String`。我在複本實跑,0 報。
- 對照:把 `ApiKey` 改名 `ApiToken`,同樣輸入就報在第 9 行。
- 這是漏報,不是誤報,方向安全,但「同檔 `@Qualifier` 宣告」被名字尾綴吃掉,計劃〈天花板〉沒寫。

引句:「regex: '@(IntoSet|IntoMap|ElementsIntoSet|\w+Key)\b'」

severity: minor
blocking: 否
共用判斷 `utils/has-registration-call.yml` 的 `^`、`$` 錨點和 `(javax\.inject\.)?`、`setOn\w+Listener` 的收窄,拿掉照綠。r2 掃描只做了「拿掉 | 選項」,沒掃這幾類。
- 拿掉 `^`:`unregisterReceiver(r)` 會被當成 `register…`,把本來是 UI-33 的區塊改判成會擋的 UI-32。
- 拿掉 `$`、把 `setOn\w+Listener` 改成 `setOn\w+`:`subscribeOn(...)`、`setOnClick(...)` 之類會被誤當註冊。
- 拿掉 ARCH-59 的 `(javax\.inject\.)?` 或 `@Named\(` 的括號:照綠。
- 影響限於這幾種罕見寫法,所以只標 minor。

引句:「regex: ^(add\w*(Listener|Observer|Callback)|register\w*|subscribe|setOn\w+Listener|listen)$」

severity: minor
blocking: 否
API-2 用 `?.map { it.await() }` 不報,而它是會擋的 error 級規則。
- 輸入:`suspend fun a(ds: List<Deferred<Int>>?) = ds?.map { it.await() }`,實跑 0 報。
- 對照:`ds.map { it.await() }` 報。
- 〈天花板〉只寫了 lambda 第一行是註解、有型別參數、`it.await() + 1`,沒寫安全呼叫 `?.`。

引句:「- pattern: $L.map { it.await() }」

修補鏡頭三問:

- **① 有沒有守住**:C158~C184 各自對得上聲稱的項目。我抽驗拿掉 IntoMap、IntoSet、ElementsIntoSet、非限定詞清單各項,都有對應的 C 例轉紅。
- **② 有沒有帶進新問題**:新例預期行號都對,harness 逐例核對後 C127~C184 全數吻合。沒有把規則誤報寫成「該報」的例子。
- **③ 同族還有沒守到的**:就是上面的結構條件(`$T`、`$Q`、`$I`、`\b`、`stopBy`)和錨點。r2 的「拿掉 | 選項、拿掉 pattern 行」掃描涵蓋不到。

我在 `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/` 建過的路徑如下(沒刪,交編排者處理):

- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/cfg`(規則包複本)
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/rc`(repo 的 git clone,改壞實驗用)
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/p1`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/p2`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/p3`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/p4`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/p5`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/p6`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/mroot`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/harness.py`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/mut.py`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/m0.json`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/m1.json`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/m2.json`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/m2b.json`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/m3.json`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/m4.json`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/t1.out`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/EAP.java`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/EAP.kt`
- `/tmp/lumos-seat-work/code-android形狀列補規則/審查三-sonnet/arch.bak`
