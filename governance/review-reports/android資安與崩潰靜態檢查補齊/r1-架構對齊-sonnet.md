severity: minor

四問全以快照、型錄、規則包實檔對照過。結構上沒有跨層直呼或第二套機制,所以沒有 major。不對齊共 4 條,全是 minor。

## 1. 分層與依賴方向

大致對齊,沒有 major。
- 型錄列分進現有 API、ARCH、DATA 三類,跟鄰居一致:API-22 信任所有憑證放 API(`skills/kotlin-idioms/checks-catalog.md:170`),ARCH-48 registerReceiver 旗標放 ARCH(`skills/kotlin-idioms/checks-catalog.md:472`),DATA-24 SQL 注入放 DATA(`skills/kotlin-idioms/checks-catalog.md:520`)。
- 不接閘的規則進 `rules-unwired/`,走既有 `CONFIGS` 的四個目錄(`configs/ast-grep/kotlin-android/check.py:26`)。
- `_B4_LINT` 加前綴是延伸既有機制(`configs/ast-grep/kotlin-android/check.py:107`)。
- 落點見第 4 問。

**Finding 1(規則檔分層)**
severity: minor
blocking: 否
引句:「會擋(`rules/`,新檔 `rules/security.yml`(新增)):」
既有九個規則檔都按型錄類別各自一檔,檔內訊息前綴只有一種。我用 grep 數過,api.yml 全是 `[API-`,data.yml 全是 `[DATA-`,architecture.yml 全是 `[ARCH-`。新檔 security.yml 按主題分,裡面會混 `[API-n]`(WebView、TLS)和 `[DATA-n]`(寫死金鑰)。
file: `configs/ast-grep/kotlin-android/rules/api.yml:1`
file: `configs/ast-grep/kotlin-android/rules/data.yml:41`
check.py 沒有強制檔名對應前綴,所以只是慣例沒跟,結構沒壞。照鄰居做法,應該 WebView 與 TLS 放 `rules/api.yml`,寫死金鑰放 `rules/data.yml`。

## 2. 命名與錯誤處理

**Finding 2(型錄前綴命名)**
severity: minor
blocking: 否
引句:「型錄現成規則欄寫成 `資安包:<檢查 id>`。」
現成規則欄的前綴,除了 `內建:` 以外,全是工具或提供者的原名:`androidx:`、`slack:`、`detekt:`、`Sonar:`、`structured-coroutines:`(`configs/ast-grep/kotlin-android/check.py:107`、`skills/kotlin-idioms/checks-catalog.md:3`、`skills/kotlin-idioms/checks-catalog.md:181`)。`資安包:` 是中文描述詞,不是提供者名。判不準這算不算 `內建:` 那種中文先例,標 ⚠。
訊息格式「[型錄編號] 錯在哪;改用 <最短修法>」、120 字上限、規則檔 `ignores:` 的寫法,計劃都沿用既有做法,沒有不一致。

## 3. 第二種做法

**Finding 3(路徑排除清單)**
severity: minor
blocking: 否
⚠ 判不準。
引句:「另加 `**/src/debug*/**`(debug 變體的程式只進 debug 版)。」
既有 `rules/` 和 `rules-unwired/` 裡沒有任何規則排除 `src/debug`(我 grep `src/debug` 零命中)。鄰居的排除清單都是測試類:`rules/state.yml:141` 是七項清單,`rules/data.yml:474` 和 `rules/perf.yml:132` 是較短的清單。這會變成第八項、只有新規則才有。
它也跟既有判法不同:API-19 判「有沒有被 DEBUG 包住」是看程式內容,不是靠目錄(`configs/ast-grep/kotlin-android/rules/api.yml:46`)。我把它列 minor 是因為它只是在既有清單上加一項,不是新的排除語法。

**Finding 4(「被除錯開關包住」的判法)**
severity: minor
blocking: 否
⚠ 判不準。
引句:「條件只要不是單純比 `Build.VERSION.SDK_INT` 就不報(結構判斷,不看旗標名)」
既有 API-19 判「有沒有被除錯開關包住」,是在 `if` 或 `when` 裡找字面 `BuildConfig.DEBUG`(`configs/ast-grep/kotlin-android/rules/api.yml:46`)。新規則的口徑反過來:任何非 SDK 版本比較的 `if` 都當作有開關。同一個概念在同一個規則包裡有兩種判法。
計劃有寫理由:實驗中只認含 debug 的條件,會讓 3 處全被排除。但它沒說明為什麼不跟 API-19 共用或對齊口徑。

另有一點只提醒、不列 finding:誤報量測改用 GitHub 程式搜尋語料,跟既有的 nowinandroid 整份掃不同(`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:83`)。計劃在 PRIOR-ART ④ 已寫明理由與口徑,屬有意偏離,所以不列。

## 4. 落點

**不列 finding,對齊。** `Systems/kotlin規則包` 管 check.py、型錄、`sgconfig*.yml`(`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:8`)。新規則、型錄、`_B4_LINT` 都落在它。範本那一行依賴落在 `Systems/linter精選目錄`〈標準接法〉第 1 步,Slack compose-lints 同樣寫在那裡(`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:180`)。兩篇都是既有節點,不必另開。

不對齊共 4 條,其中 major 0 條
