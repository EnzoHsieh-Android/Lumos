severity: major

我把 sweep 裡 104 個 Android Lint 檢查頁重新抓下來,逐頁讀等級、預設開關和所屬套件。另外對照了 Slack compose-lints 的 CHANGELOG、compose-rules 的 detekt 設定頁,以及 ColorsDetector 原始碼。六包各抽的 CATCH 列都站得住,但下面這些列不是。

結論先講:代理讀官方頁這個做法有效,但它沒有把「字面判錯」的代價改成「多審」,只是把判斷搬到證據表。計劃〈用詞〉定義的「預設開啟、warning 以上」沒有進證據表欄位,也沒有進 sweep 的判準。結果 117 列「擋得到」裡,我至少找到 6 列(UI-43、UI-44、UI-45、UI-46、UI-92、UI-96)在計劃自己的定義下其實擋不到。這個錯誤率跟被翻案的 12 列同量級。

## 各包抽查結果(判 CATCH 的列)

- p1 的 API-22(TrustAllX509TrustManager):Error 等級,頁上原文逐字吻合,成立。
- p2 的 UI-59(ModifierClickableOrder):compose-rules 頁上的 ❌ 例就是 clickable 在 clip 前,成立。sweep 把方向寫反了,但結論對。
- p3 的 UI-91:UnusedMaterial3ScaffoldPaddingParameter 是 Error 等級,成立。UI-96 見 finding 1,UI-92 見 finding 3。
- p4 的 ARCH-18、ARCH-19:頁面只有說明沒有範例,但目錄自己有 2026-11-05 的實跑命中記錄佐證,成立。
- p5 的 DATA-5:ApplySharedPref 是 Warning 等級,成立。
- p6 的 PERF-13:NotifyDataSetChanged 是 Warning 等級,成立。
- 網頁原文抽樣:我把 sweep 裡 102 筆引在 lint 頁的原文拿去逐字比對,只有 4 筆對不上,原因是換行、反引號或引自別的網址,不是捏造。

## 1. UI-96 的唯一檢查等級是 Hint,卻判成 CATCH,計劃只降了 UI-64

severity: major
blocking: 是

失敗場景:UI-96 只標「批四(CI 範本:Android Lint)」,唯一的檢查是 `ArcAnimationSpecTypeIssue`。官方頁寫 Severity 為 Hint,並說明「just a hint; it's a "weak" warning」。範例輸出也是 `Hint: Arc animation is intended for 2D values`。範本開了 `warningsAsErrors`,Hint 仍不會讓建置失敗。p4 把 UI-96 判 CATCH,證據表也寫 117 列之一,但計劃範圍 2 只降 UI-64、UI-80、TEST-25 三列。UI-96 照字面進證據表,「CI 會擋」就是假的。

同族的 UI-13:`mutableStateOf(0)` 那個壞例只被 Hint 等級的 `AutoboxingStateCreation` 報。`.value` 那個壞例有 Warning 等級的 `AutoboxingStateValueProperty` 擋,另有 compose-rules 的 `MutableStateAutoboxing`(預設開啟)。所以 UI-13 靠第二個壞例可以保留,但證據表那筆必須寫 `AutoboxingStateValueProperty`,不能寫 `AutoboxingStateCreation`。

引句:「與預設關或等級是 Hint 的 3 列(UI-64、UI-80、TEST-25)」

佐證:https://googlesamples.github.io/android-custom-lint-rules/checks/ArcAnimationSpecTypeIssue.md.html 和 https://googlesamples.github.io/android-custom-lint-rules/checks/AutoboxingStateCreation.md.html(都是 Severity Hint)。sweep/p4.md 的 UI-96 那列。

## 2. Slack 的四條檢查有版本門檻,證據沒記版本,範本在 AGP 8.x 下根本沒有這幾條

severity: major
blocking: 是

失敗場景:UI-43(`ComposeItemKeyHashCode`)、UI-45(`ComposeRedundantComposable`)、UI-46(`ComposeNonRestartableComposable`)、UI-44(`ComposeReadOnlyComposable`)都只靠 Slack 外掛,通電批次是「批四(CI 範本:Android Lint)」。p2 讀的是 Slack 規則頁(main 分支,不分版本)。

Slack 的 CHANGELOG 寫 1.5.0(2026-05-26)才新增 `ComposeItemKeyHashCode` 和 `ComposeRedundantComposable`,1.6.0 才新增 `ComposeNonRestartableComposable`。`ComposeReadOnlyComposable` 的加入版本我沒查到,但 CHANGELOG 最早提到它是在 1.5.3 的 Enhancement,所以至少也不在 1.4.x。

`Systems/linter精選目錄.md` 的版本對照寫:AGP 8.7.1 到 9.2.0 用 `1.4.2`,AGP 9.2.1 到 9.3.1 用 `1.5.0`,AGP 9.4.1 以上才用 `1.6.1`。目錄自己 2026-11-05 的實跑環境是 AGP 8.13.2,對到的就是 1.4.x。所以在那個環境下,這四列的 CI 檢查根本不存在,UI-46 要 AGP 9.4.1 以上才有。

引句:「判定擋得到的 117 列寫進證據表」

佐證:https://raw.githubusercontent.com/slackhq/compose-lints/main/CHANGELOG.md(1.5.0、1.6.0 的 New 條目)。`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:185`。

## 3. UI-92 的 ConflictingOnColor 只管 Material 2,壞例卻寫 colorScheme

severity: major
blocking: 是

失敗場景:UI-92 壞例欄寫「colorScheme 中 primary == secondary 卻 onPrimary ≠ onSecondary」,這是 Material 3 的用語。官方頁的 Artifact 是 `androidx.compose.material:material-android`,也就是 M2 函式庫。我讀了偵測器 `ColorsDetector.kt`,它只比對 `Colors`、`lightColors`、`darkColors`,沒有 `lightColorScheme`。只用 M3 的專案不會載入這條檢查,壞例不會被報。

p3 自己註明「範例放在 androidx.compose.material(Material 2)套件下,頁面沒說 Material 3 也會報」,仍然判 CATCH。這讓計劃的「報壞寫法欄(第 3 欄)裡至少一個例子」定義被放寬了。

引句:「判定擋得到的 117 列寫進證據表」

佐證:https://googlesamples.github.io/android-custom-lint-rules/checks/ConflictingOnColor.md.html,以及 androidx 原始碼 `compose/material/material-lint/src/main/java/androidx/compose/material/lint/ColorsDetector.kt`(第 62 到 67 行、第 231 到 233 行)。

## 4. 證據表欄位沒有承載「擋得到」定義的維度,三個 major 都是這個缺口

severity: major
blocking: 是

失敗場景:證據表欄位只有「型錄列編號、檢查、擋得到的壞例、官方頁或原始碼逐字一句、網址、查證日期」。定義要求的預設開關、等級、載入檢查的套件與版本都沒有欄位,自檢也驗不到。所以 finding 1 到 3 這三類錯會在日後新增列時重演。

天花板一節只承認「讀錯」,但這三類錯不是讀錯字面,是判準沒套用。下一次有人補證據,仍然只要貼一句「官方頁原文」就過關。目標「代價從悄悄多宣稱變成被擋下來要補證據」不成立:自檢擋下的只是證據缺漏,證據假的過得去。

改法:證據表加 `等級`、`預設`、`套件@版本` 三欄,自檢驗等級在 Warning/Error/Fatal 之一、預設為開。這三欄官方頁都有現成欄位(Severity、Artifact、Since、「disabled by default」)。UI-80 頁上有「This issue is disabled by default」這句,可以機械檢查。

引句:「自檢只驗證據存在且與型錄一致,不驗證據本身對不對」

佐證:官方檢查頁的 Severity、Artifact、Since 欄位格式固定,例如 `ComposableLambdaParameterNaming.md.html` 第 12 行。

## 5. 「環境沒有」的前提與型錄自己的實跑記錄衝突

severity: minor
blocking: 否

為什麼標 minor:這是方法選擇與文件矛盾,不是直接讓某列判錯;列錯的後果已在 finding 1 到 3 計入。

目錄裡有 21 列寫著「Android Lint 實跑命中 …(2026-11-05,AGP 8.13.2 實驗專案複本)」,`Projects/Android現成檢查接上CI與推送前_計劃.md` 的 S5 也是手動實跑。所以真跑 Lint 的環境至少曾經有過,比「讀頁面當證據」更準,一次就能同時判掉等級、預設和版本。

有兩個後續問題:
- 實跑記錄同樣只記「命中」,UI-13 的實跑命中就是 Hint 等級那條。REVISIT 的真跑要明寫「Warning 以上才算命中」,否則會重演 finding 1。
- UI-11 的實測欄寫著「實跑命中 ComposeViewModelForwarding」,但計劃把它判為擋不到並退回批一。S3 沒有說要改掉或註明那句實跑記錄,同一列會自相矛盾。

引句:「這要 Android Gradle 外掛與專案骨架,工具鏈測試環境沒有」

佐證:`skills/kotlin-idioms/checks-catalog.md` 的 UI-11 列、UI-13 列、API-9 列。

## 6. UI-100 的 p4 與 p7 判定不一致,p7 靠的前提壞例欄沒寫

severity: minor
blocking: 否

為什麼標 minor:壞例是簡寫,實務上多預覽註解都帶 `@Preview`,誤判的實際風險低。

p4 把 UI-100 判 UNSURE,理由是壞例 `annotation class DarkLight` 沒帶 `@Preview`。p7 判 CATCH,理由是「多預覽註解本來就帶 @Preview」,並承認「本列壞例沒寫出註解行」。compose-rules 的判斷是「身上任一個註解名稱含 Preview」,照字面,這個壞例不會被報。證據表應該把壞例補成 `@Preview annotation class DarkLight`,否則「擋得到哪個壞例」那欄跟型錄壞例欄對不上。

引句:「六包代理讀官方頁、判不出的 10 列再派一席讀檢查器原始碼」

佐證:sweep/p4.md 與 sweep/p7-src.md 的 UI-100。

## 已檢查、無問題

- compose-rules 的 detekt 設定只有 `UnstableCollections`、`PreviewNaming`、`Material2` 預設關,型錄 cr 側的接電列沒有用到後兩條。
- Slack 的 `ComposeMutableParameters` 在 1.5.0 被預設關,但 1.5.1 又改回預設開啟,UI-26 和 UI-27 沒問題。

最高等級 major;blocking 4 條
