severity: minor

整體判斷:這份設計大方向跟第一批一致,沒有第二種做法,也沒有跨層直呼。不對齊的地方都是命名與寫法層級,另有一處計劃漏寫。

## 1. 分層與依賴方向

規則放哪一級,跟既有做法對得上。

- 會擋的只有一條(`kt-webview-mixed-content-always`,放 `rules/api.yml`),其餘 12 條放 `rules-unwired/`,升級門檻是樣本外命中 ≥20、誤報 ≤10%。這跟第一批 `kt-webview-file-url-access` 放 `rules/`、其餘放 `rules-unwired/` 的做法相同,對照 `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` 的 WHY(資安四條自寫規則只有一條放會擋的 `rules/api.yml`)。
- 除錯判斷沒有另寫一套。初稿 13 條規則全都用 `not: matches: in-debug-only-branch` 引用共用的 `configs/ast-grep/kotlin-android/utils/debug-only.yml`,初稿裡沒有自己定義的除錯判斷。這點完全對齊,該 utils 檔頭註解正是第一批代碼審 r2 抽出來的。
- 沒有新開型錄類別。新列編號都落在既有的 API、ARCH、DATA 三類,延續第一批「不新開類別」的做法。
- 規則檔分檔:第一批規定「API 列的進 `api.yml`、DATA 列的進 `data.yml`」。第一批的 `kt-secretkeyspec-literal-key` 就放在 `rules-unwired/data.yml`。這份計劃只寫「其餘 12 條在 `rules-unwired/`」,沒說哪幾條進 `rules-unwired/api.yml`、哪幾條進 `rules-unwired/data.yml`。見 finding 3。

## 2. 命名與記錄寫法

**finding 1**
severity: minor
blocking: 否
引句:「路徑排除:八項清單(同第一批),Zip Slip 與 XXE 另排除建置腳本(`buildSrc`、`build-logic`、`*.gradle.kts`)。」
既有做法是每條規則的 `ignores` 恰好等於同一份八項清單。`scripts/test_lumos.py:126856`(`_KTSEC_IGNORES`)和 `scripts/test_lumos.py:126883` 的測試用「恰好是八項」去比。規則包 `rules*/` 底下沒有任何規則另加 `buildSrc` 一類的排除(grep 為 0)。這份計劃讓兩條規則的清單多出 3 項,是同一個欄位出現第二種清單。計劃雖然誠實寫了「另排除」,但 S2 的「路徑排除照範圍 4」跟既有「恰好八項」的斷言口徑不同。這是寫法分歧,不是新機制,所以只算 minor。

**finding 2**
severity: minor
blocking: 否
引句:「每條訊息 應 以這次新增或併入的型錄列編號開頭、不超過 120 字」
計劃條款與既有格式一致:`Systems/kotlin規則包.md` 的 WHY 規定「[型錄編號] 錯在哪;改用 <最短修法>」且不超過 120 字。但規則初稿違反這條。我數了初稿的訊息字數(不含前綴):

- `kt-xxe-documentbuilder` 227 字
- `kt-provider-openfile-traversal` 172 字
- `kt-object-input-stream` 151 字
- `kt-loadurl-external` 136 字
- `kt-static-iv` 131 字
- `kt-weak-cipher-suite` 129 字
- `kt-zip-slip` 126 字
- `kt-weak-key-size` 122 字

這 8 條連前綴都還沒算就超過 120。另外初稿的 `[SEC-xx]` 前綴計劃已說實作時要換掉。這兩點是初稿跟既有格式不一致,計劃有承諾修,所以不阻擋。

**finding 3**
severity: minor
blocking: 否
引句:「`kt-webview-mixed-content-always` 應 在 `rules/api.yml`,其餘 12 條 應 在 `rules-unwired/`」
既有的 `_KTSEC_PLACE`(`scripts/test_lumos.py:126849` 附近)逐條斷言規則在哪個目錄的哪支檔(例如 `("rules-unwired", "data.yml", "DATA-87")`)。這份 S2 只斷言目錄,沒斷言檔名。第一批範圍 4 的「放進按型錄主題分的既有規則檔」沒有被繼承,實作時可能全塞進同一支檔。

**finding 4**
severity: minor
blocking: 否
引句:「[S1] 當逐例測試對預期值表每一列 S1 的寫法各跑一次規則包時」
計劃另開 `t_kotlin_rulepack_security_rules_batch2`。既有 `t_kotlin_rulepack_security_rules`(`scripts/test_lumos.py:126860`)已有 `_KTSEC_CASES`、`_KTSEC_PLACE`、`_KTSEC_IGNORES` 三張表。計劃沒說是擴充既有三張表,還是另抄一份。若另抄,八項清單和 120 字檢查會出現第二份。我判不準計劃的意圖,標 ⚠。

**finding 5**
severity: minor
blocking: 否
引句:「`SdCardPath` 併進 DATA-27(那列原寫「代號待查」」
第一批併進既有列時,逐項寫了「級改 `A+D`、通電批次在原有兩段後加…」(`docs/lumos-toolchain-knowledge/Projects/Android資安與崩潰靜態檢查補齊_計劃.md:48` 附近的「併進既有列」)。這份計劃的併入列(DATA-27、79、82、83、85)只交代「現成規則欄」「名稱」「實測狀態」「來源」。「形狀」欄和「通電批次」欄(例如 `告警帶寫法=未接(規則在 rules-unwired/…)`)沒寫。DATA-83 原本標「批四」,併入不接閘的自寫規則後,通電批次的寫法沒有定。`configs/ast-grep/kotlin-android/check.py:120` 的 `batch4_expected_tags` 是逐列重算比對,所以這裡有機械檢查會紅。

另外,計劃沒提型錄〈統計節〉要照既有口徑重算,第一批有寫。S3 的「型錄自檢 0 個問題」會抓到,所以只算漏寫。

**量誤報口徑**
- 「判不準留在分母」跟第一批一致:舊版 TLS 的 19 處中 2 誤報 = 10.5%,判不準也算在分母。
- 本批新增了兩點,但有明寫,不算不一致:單條超過 40 處以種子 20261109 抽 40 處,第一批是全判;「外部協定強制算誤報」。

## 3. 第二種做法

沒有引入第二種機制。

- 除錯判斷共用 `utils/debug-only.yml`。
- 讀規則仍用 `check.py` 的 `load_rules`。
- 訊息格式、升級條件、型錄列欄位都沿用既有。

唯一接近的是 finding 1(第二份路徑排除清單)和 finding 4(可能另抄一份測試表),都是寫法分歧,不構成 major。

## 4. 落點

- `lands_in` 只列 `Systems/kotlin規則包`。這個節點的 `about_code` 已涵蓋 `check.py`、`sgconfig*.yml`、`checks-catalog.md`、`utils/debug-only.yml`,所以落點正確。第一批多列的 `Systems/linter精選目錄` 是因為改了範本,這批沒改範本,不用列。
- 計劃範圍 5 說「補一行 WHY」。節點裡已有一行 WHY 講「資安四條自寫規則放哪一級、升級條件」(`Systems/kotlin規則包.md` 第 53 行)。另寫新一行會讓同一條升級條件散在兩處。建議併進那一行,或明寫兩行的分工。這是落點寫法,算 minor 的 ⚠,不另編號。
- 計劃沒寫每條新規則的 `samples/bad/<id>/`、`samples/good/<id>/`。這是規則包的既有硬要求(`Systems/kotlin規則包.md:72`),回退節有提到「13 條規則與樣本」,規則包樣本測試會擋,所以只是計劃漏寫。

不對齊共 5 條,其中 major 0 條
