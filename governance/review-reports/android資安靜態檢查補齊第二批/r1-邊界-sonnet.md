severity: major

下面兩條都針對 kt-webview-mixed-content-always,是我在臨時目錄用 ast-grep 0.51.1 實跑出來的。我把規則初稿的這一條單獨抽成規則檔,掛上 `utils/debug-only.yml` 後跑 `ast-grep scan`。樣本約 100 個 .kt。其他 12 條我沒有逐條測,所以不列。

**這條規則做對了的部分(實測)**
- 以下寫法都正確命中:
  - `w.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW`
  - 完整套件名
  - import 後直接寫常數,或用別名 import(`WS.MIXED_CONTENT_ALWAYS_ALLOW`)
  - `w?.settings?.…`、`w!!.settings…`
  - 在 `apply`、`with`、`let`、`also` 裡的賦值
  - `setMixedContentMode(mode = …)` 具名參數
  - 分行的呼叫鏈
  - `getSettings().setMixedContentMode(0)`
  - 字面值 0
- 以下寫法正確沒報:
  - NEVER_ALLOW、COMPATIBILITY_MODE 和字面值 1、2、10
  - 註解或字串裡寫著常數名
  - `if (BuildConfig.DEBUG)` 不加大括號、帶套件名的 `com.x.BuildConfig.DEBUG`、`when { BuildConfig.DEBUG -> … }`、`!BuildConfig.DEBUG … else`,以及這些分支裡再包 `apply` 或 lambda
  - `|| x` 的條件、`else` 分支、`!BuildConfig.DEBUG` 的 if 本體,都正確照樣報
  - `src/test`、`src/debug`、`src/debugFoo`、`src/androidTest` 被 `ignores` 排除;`src/main/java/test/` 沒被排除,符合預期
- 以上是我肯定的結論。我只測了 ast-grep 的命中結果,沒測推送閘本身。

**finding 1:setter 形式對任何巢狀呼叫的字面值 0 誤報**

severity: major
blocking: 是

這條規則會進推送前的閘,誤報會直接擋推送。原因在初稿裡:

`draft-rules.yml.txt:139` 的 `stopBy: end` 讓外層 `has` 往下找到任何深度的 `value_argument`。接著 `:141` 只要求那個 `value_argument` 的直接子節點是 `0` 或 `MIXED_CONTENT_ALWAYS_ALLOW`。所以參數裡隨便哪層的內層呼叫帶了字面值 0,都會命中,跟 `setMixedContentMode` 自己的實參無關。

實測輸入:
- `w.settings.setMixedContentMode(resolve(0, 1))` 被報
  - ast-grep 輸出:`error[kt-webview-mixed-content-always] … s2/a.kt:1:20`
- `w.settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW.coerceAtLeast(0))` 被報
- `w.settings.setMixedContentMode(computeMode(0))` 被報
- `w.settings.setMixedContentMode(pick(0, WebSettings.MIXED_CONTENT_NEVER_ALLOW))` 被報
- 賦值形式 `mixedContentMode = pick(0, NEVER)` 與 `x[0]` 沒被報,因為賦值那條用的 `has` 沒有 `stopBy: end`。同一條規則裡兩種寫法的行為不一致。

修法方向(我沒驗證):setter 那條的 `has` 改成只看緊貼 `setMixedContentMode` 的參數列,也就是不要 `stopBy: end`。一併處理 finding 2 的 if/elvis 時要小心,別重新引入同一個誤報。

**finding 2:漏報,值藏在 if、elvis、括號、轉型等表達式裡**

severity: minor
blocking: 否

賦值那條 `draft-rules.yml.txt:148` 的 `has: matches: always-allow` 只看賦值的直接子節點。值只要不是裸的常數或 0,就漏報。實測以下全部沒報:
- `w.settings.mixedContentMode = if (b) WebSettings.MIXED_CONTENT_ALWAYS_ALLOW else WebSettings.MIXED_CONTENT_NEVER_ALLOW`
- `w.settings.mixedContentMode = cfg ?: WebSettings.MIXED_CONTENT_ALWAYS_ALLOW`
- `w.settings.mixedContentMode = (WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)`
- `w.settings.mixedContentMode = when (b) { 1 -> WebSettings.MIXED_CONTENT_ALWAYS_ALLOW else -> 1 }`
- `w.settings.setMixedContentMode(if (b) WebSettings.MIXED_CONTENT_ALWAYS_ALLOW else WebSettings.MIXED_CONTENT_NEVER_ALLOW)`
- 加上 `.toInt()`、`!!`、`as Int` 的版本
- 透過常數間接:`val m = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW; …setMixedContentMode(m)`,或 `const val M = …` 再 `= M`

這條規則是在逮「預設寫法就是這個常數」的情況,漏掉這些是已知取捨,所以我降為 minor。`if (b) ALWAYS else NEVER` 其實是真的把 release 版也放寬了,值得在規則的 message 或計劃裡註明這是已知不抓。

常數間接和 `0x0`、`0b0`、`0_0` 這類十六進位、二進位字面值也漏報,但很少人這樣寫,我不列為問題。

誤報方向還有一個小發現:`BuildConfig.DEBUG` 先存進區域變數再 `if (dbg)`,會報。這是預期行為(規則只看語法結構,不追蹤變數),不算問題。

**相關檔案**
- 規則初稿:`/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint-2/governance/review-reports/android資安靜態檢查補齊第二批/experiment/draft-rules.yml.txt`
- 我的臨時目錄:`/tmp/lumos-seat-work/android資安靜態檢查補齊第二批/邊界-sonnet/`。我沒刪它,等編排者收貨後處理。
