severity: major

派工尾端沒有附節點固定席,所以沒有固定席的「不影響」判定要寫。我的實驗檔(detekt 1.23.8 加 compose-rules 0.4.28 外掛的暫存目錄)已用字面絕對路徑刪除。

查證結果:
- 外掛 jar 的 sha256 與 spec 寫的 `b8c732…ddd6` 一致。
- 外掛放在本機 detekt 1.23.8 上能跑。
- `--plugins` 選項存在,`naming: FunctionNaming: ignoreAnnotated: ['Composable']` 有效:`@Composable fun Header()` 不再被報,`fun Other()` 照報。
- `RememberMissing`、`MutableParams`、`MutableStateAutoboxing`、`ComposableNaming` 都實際報出。
- `com.slack.lint.compose:compose-lint-checks:1.6.1` 與 `io.nlopez.compose.rules:detekt:0.4.28` 都存在。
- 1.6.0 發行說明寫 "Note this requires AGP/lint 9.3+."。
- Android Lint 官方頁的 `baseline = file(...)`、`-Dlint.baselines.continue=true`、`checkDependencies`、`lint<變體>` 寫法都對得上。

## F1
severity: major
blocking: 是 — 照字面做,共用設定一接 compose-rules,每個新增的 `@Preview` 都會被推送前閘擋下,實作者會做出會被規則自己的退場條件(誤報超過一成)判掉的設定。

**位置**:範圍 2「共用設定……只加 `naming: FunctionNaming: ignoreAnnotated: ['Composable']`」。

**問題**:
- 引入 compose-rules 後,Preview 函式有兩條互相打架的新告警,共用設定只處理了命名那一條。
- 寫成 `private` 會被 detekt 內建的 `UnusedPrivateMember` 報「Private function … is unused」。
- 寫成 public 會被 compose-rules 的 `PreviewPublic` 報。
- 兩邊都是「新增告警」,閘一律擋。
- spec 的驗收條款 S3 只驗 `FunctionNaming` 與 `RememberMissing`,抓不到這個。
- 「實務隱患」只談 FunctionNaming,沒提 Preview。

**實測**:detekt 1.23.8 加外掛 0.4.28,用 `android.yml` 疊上 `ignoreAnnotated` 的設定跑一支檔,檔裡有 `@Preview @Composable private fun GreetingPreview()` 和 `@Preview @Composable fun PublicPreview()`。
- 輸出有 `C.kt:11:13: Private function GreetingPreview is unused. [UnusedPrivateMember]`。
- 輸出有 `[PreviewPublic]`。

**佐證**:
- 外部:https://detekt.dev/docs/introduction/compose/ 寫「Set `ignoreAnnotated` to include `Preview` …」。
- 外部:https://raw.githubusercontent.com/mrmans0n/compose-rules/main/docs/rules.md 第 789 行寫「Be sure to set Detekt's … ignoreAnnotated configuration … to ['Preview'] for compatibility with this rule.」

## F2
severity: major
blocking: 是 — A1 的判定字面會對常見的 CI 寫法誤印「哪裡都沒擋」,對另一種常見外掛的任務名又誤判成已接上。

**位置**:範圍 3 的 A1。

引句:「任務名剛好是 `lint`,或 `lint` 接大寫開頭的變體名,前面是 `gradlew` 或 `:模組:`」

**問題**:
- **誤報**:CI 只要在 `lint` 前面還有別的 token,就不算數。例如:
  - `./gradlew assembleDebug lintDebug`
  - `./gradlew --no-daemon lintDebug`
  - `./gradlew test lint`
  - `gradle lintDebug`(用 gradle 動作時是裸 `gradle`)
  - 這些都是真的在跑 Android Lint,A1 卻會印「Android Lint 與 Slack compose-lints 哪裡都沒擋」。
  - 對照:現有 `_detekt_ci_has_typed_task` 是用 `\bdetekt[A-Za-z0-9]*` 掃全文,沒有前綴限制。
- **漏報**:`lint` 接大寫變體名的規則會把 kotlinter 外掛(org.jmailen.kotlinter)的 `lintKotlin`、`lintKotlinMain` 當成 Android Lint 任務。只跑 ktlint 類檢查的 Android 專案,A1 反而沉默。
  - 這是我對 kotlinter 任務名的認識,沒有在本機跑過,⚠。
  - 「實務隱患」那條字面誤判只列了 shell 腳本與 composite action,沒列這兩種。

**佐證**:
- `scripts/lumos:38915` 的 `_detekt_ci_has_typed_task` 是現有對照。
- 外部:https://developer.android.com/studio/write/lint 寫 "capitalize the variant name and prefix it with `lint`"。

## F3
severity: minor
blocking: 否 — 只會讓型錄裡一批 Android Lint 列沒被標到、少數預設關的檢查被標成已接電,不會讓程式壞掉。

**位置**:範圍 4 與條款 S4。

引句:「現成規則欄點名了 Android Lint、androidx、Slack 規則碼(不是「待查」)的列」

**問題**:
- **漏標**:型錄現成規則欄寫 Android Lint 內建檢查時,用的是 `內建:` 前綴,例如 API-22 `內建:TrustAllX509TrustManager…`、API-23 `內建:UsingHttp…`。
  - 型錄〈輸入與口徑〉自己寫「androidx/內建 = Android Lint」。
  - spec 的判定口徑只列 Android Lint、androidx、Slack,沒列 `內建:`。
  - 我數到只靠 `內建:` 點名的有約 22 列,例如 ARCH-4、PERF-1、PERF-12、PERF-38。
  - 這些列照字面會留在「批四(現成規則)」,和「CI 範本:Android Lint」標籤並存。
  - S4 的測試也驗不到。
- **誤標**:CI 範本的 `lint { }` 區塊沒有 `enable +=`,預設關的檢查不會跑。PERF-3 的現成規則欄明寫「WrongThreadInterprocedural(預設關)」,卻會被標成「CI 範本:Android Lint」。

**佐證**:
- `skills/kotlin-idioms/checks-catalog.md:11`(口徑)與 `:15`(規則庫簡稱)。
- `skills/kotlin-idioms/checks-catalog.md:625`(PERF-3 的現成規則欄)。

## F4
severity: minor
blocking: 否 — 只是出處寫錯,設定本身經實測有效。

**位置**:PRIOR-ART ③與預期值表 S3 的來源欄。

引句:「compose-rules 官方建議對 `Composable` 註解忽略,共用設定照做」

**問題**:
- compose-rules 的 detekt 頁與 rules 頁都沒有 `FunctionNaming` / `ignoreAnnotated: ['Composable']` 的建議。detekt 頁只出現 `ModifierMissing` 的註解範例 `# ignoreAnnotated: ['Potato', 'Banana']`,rules 頁只有 `['Preview']` 那條。
- 這條建議出自 detekt 自己的 Compose 頁,該頁還建議 `Preview`、`LongParameterList`、`TopLevelPropertyNaming` 等調整。出處寫錯,也讓 F1 的 Preview 調整被漏看。

**佐證**:https://mrmans0n.github.io/compose-rules/detekt/ 、https://detekt.dev/docs/introduction/compose/ 。

## F5
severity: minor
blocking: 否 — 屬測試怎麼找外掛的決定,實作時補上就能解決,不會出壞系統。

**位置**:範圍 2 與條款 S3。

引句:「讓 S3 在 CI 必跑」

**問題**:
- 本機外掛放 `$HOME/.local/share/lumos/detekt-plugins/…`。
- CI 步驟只說「照 detekt 的做法多下載」,`ci.yml` 現有的 detekt 是放在 `$RUNNER_TEMP/detekt`,放進 PATH。
- spec 沒定義 `t_detekt_compose_rules_shared_config` 怎麼找到外掛 jar(固定路徑、環境變數,還是別的)。
- 也沒說 CI 上找不到時要判紅,還是照條款文字跳過。
- 照字面做,CI 可能下載了外掛、測試卻在別的路徑找不到而跳過,「CI 必跑」就落空。

**佐證**:
- `.github/workflows/ci.yml:150-165` 是現有的 detekt 下載步驟。
- `scripts/test_lumos.py:126179` 現有測試用 `LUMOS_DETEKT` 環境變數或 PATH 找 detekt,對照可參考。

## 風險類逐類(實務隱患)
- **金流**:無,spec 已排除,不碰付款與點數。
- **對外送出**:無,健檢只讀本機檔。
- **資安**:無新增面,sha256 已核對,下載由人執行。
- **不可逆**:無,提醒與文件退提交即回。
- **守衛放寬**:有,見 F1。FunctionNaming 對 Composable 關掉本身有效,實測 `ComposableNaming` 接得住小寫開頭與有回傳值的 Composable。
- **外掛檔不在**:detekt 以 rc=1 結束、不產 SARIF。
  - 閘在 `scripts/lumos:40594` 一帶對 `ok=False` 回 env,走既有的環境不可用放行。
  - 也就是缺 jar 時整條 detekt(含 `GlobalCoroutineUsage` 等原有規則)被放行。
  - spec 已明寫這是既有行為並由健檢計數,我判不新增 finding。
- **效能**:無。單檔 detekt 加外掛約 0.83 秒,不加約 0.78 秒。

## 逐節
- 前言、PRIOR-ART:有 F4。
- 用詞:已讀,無 finding。
- 範圍 1:已讀,無 finding。範本 DSL 與官方頁一致。
- 範圍 2:有 F1、F5。
- 範圍 3:有 F2。
- 範圍 4:有 F3。
- 不做、實務隱患:已讀,無獨立 finding,FunctionNaming 那條見 F1。
- 驗收條款、預期值表:已讀,條款 S1 的涵蓋缺口見 F2,條款 S3 的缺口見 F1、F5。
- 回退、天花板:已讀,無 finding。
- 交叉引用:related 與 lands_in 的 5 個節點、`Projects/Macrobenchmark退步提醒_計劃` 都存在。

總結:最嚴重是 major,blocking 共 2 條(F1、F2)。
