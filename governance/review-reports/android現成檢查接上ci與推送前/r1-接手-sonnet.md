severity: major

審查範圍:只審 r1-snapshot.md。對照 `scripts/lumos`、`configs/detekt/android.yml`、`skills/kotlin-idioms/checks-catalog.md`、`SKILL.md`、`Systems/linter精選目錄.md`,外部查證用官方頁與發行說明。

### F1 Slack compose-lints 範本版本 1.6.1 要 AGP 9.3 以上,多數消費專案一接就撞牆
severity: major
blocking: 是,範本第一個預設值對 AGP 8.x 專案不能用,而判準是「照範本一步步接會撞牆」。
- spec 段落:範圍 1(CI 範本)、PRIOR-ART ②、實務隱患「AGP 版本與 Slack 外掛不合」。
引句:「`dependencies { lintChecks("com.slack.lint.compose:compose-lint-checks:1.6.1") }`(註明 1.6.x 要 AGP 9.3 以上,舊 AGP 照發行說明挑對得上的版本)」
- 問題 1:範本把需要 AGP 9.3 以上的版本寫成預設。本 repo 型錄自己的 Android Lint 實跑用的是 AGP 8.13.2 實驗專案。AGP 8.x 的專案照抄,Lint 任務會載不進外掛。
- 問題 2:「照發行說明挑」沒有可執行的對照。我查到的發行說明只有兩處寫了版本需求:1.6.0 寫「Note this requires AGP/lint 9.3+.」,1.5.5 寫 build against lint 32.3.2 與 AGP lint plugin 9.3.2。1.6.1、1.5.0 到 1.5.4、1.4.x 只寫 build against lint 的版本號,或沒寫。範本需要補一張 AGP 對 Slack 外掛版本表,但 spec 沒有這項。
- 問題 3:S5 只驗「公開範例專案」,沒指定 AGP 版本,驗不出這道牆。
- 佐證:https://github.com/slackhq/compose-lints/releases(內容經 WebFetch 摘要,逐字未獨立核對,⚠)。
- 佐證:`skills/kotlin-idioms/checks-catalog.md:170` 起各列的「AGP 8.13.2 實驗專案複本」。

### F2 「compose-rules 外掛規則預設開」不成立,型錄會把沒開的規則標成「推送前擋」
severity: major
blocking: 是,範圍 2 與範圍 4 對 UI-37 等列的宣稱為假,擋不到卻標成已接電。
- spec 段落:範圍 2 與範圍 4。
引句:「共用設定 `configs/detekt/android.yml` 加 `Compose: active: true` 不必要(外掛規則預設開)」
- 官方 detekt 頁(https://mrmans0n.github.io/compose-rules/detekt/)寫明 `Material2`、`PreviewNaming`、`UnstableCollections` 是 `active: false` 的 opt-in 規則。
- 型錄 `skills/kotlin-idioms/checks-catalog.md:345`(UI-37)的現成規則欄寫著 `cr:compose:unstable-collections / UnstableCollections(opt-in)`。`checks-catalog.md:408`(UI-100)的現成規則欄有 `cr:compose:preview...`,我只讀到這一段,沒確認是 `PreviewNaming`,⚠。
- 範圍 4 的改字規則是「點名 compose-rules 規則碼的列」,沒排除 opt-in。UI-37 與 UI-100 會被標成「批四(推送前:detekt 外掛 compose-rules)」,實際沒開。
- 修法方向:共用設定要明寫要開哪幾條 opt-in,或型錄對 opt-in 規則改標。S3 只驗了 `RememberMissing`,驗不到這點。

### F3 A1 的字面判準自相矛盾,常見的 Gradle 寫法會誤判
severity: major
blocking: 是,判準與 S1 的例子對不上,會對已接 CI 的專案印假提醒。
- spec 段落:範圍 3 的 A1。
引句:「任務名剛好是 `lint`,或 `lint` 接大寫開頭的變體名,前面是 `gradlew` 或 `:模組:`」
- 「前面是 `gradlew`」若指緊鄰的詞,以下寫法都判成沒接:`./gradlew --no-daemon lintDebug`、`./gradlew --stacktrace lint`、`./gradlew test lintDebug`、`./gradlew -p app lint`。每一種都是有跑 Lint 的 CI。
- 官方頁示範 `./gradlew lintDebug`。多任務與選項在 CI 裡是常態。
- 既有 `_detekt_ci_has_typed_task`(`scripts/lumos:38915`)用 `\bdetekt[A-Za-z0-9]*` 全文掃,沒有「前面是」這個限制。spec 稱 A1「同 `_detekt_ci_has_typed_task`」,但實際判準比它窄,兩者對不上。
- Android Gradle 外掛的 `check` 任務會依賴 Lint,`./gradlew check` 或 `build` 是實際在跑 Lint 的 CI。範圍 3 與實務隱患只提了「包在 shell 腳本、用 composite action」,漏了這一類。⚠ 這點引自 AGP 行為,spec 沒寫、我沒另找文件。

### F4 A1 把 kotlinter 的 `lintKotlin` 當成 Android Lint,漏提醒
severity: major
blocking: 是,健檢要在專案沒接 Android Lint 時說實話,這會在沒接時反而不印。
- spec 段落:範圍 3 的 A1。
- 判準「`lint` 接大寫開頭的變體名」會匹配 kotlinter(Gradle 的 ktlint 外掛)的 `lintKotlin`、`lintKotlinMain`。排除表只列了 `Fix`、`Vital`、`Analyze`、`Report`、`updateLintBaseline`。
- 場景:專案 CI 只跑 `./gradlew lintKotlin`,A1 判成已接 Android Lint,不印提醒。S1 的測試案例沒涵蓋這一類。

### F5 把外掛加進同一條 detekt 命令,jar 缺了或和 detekt 版本不合,整條既有 detekt 防線一起失效
severity: major
blocking: 是,改動讓既有防護多了新的失效途徑,與安裝慣例也衝突。
- spec 段落:範圍 2、實務隱患「compose-rules 外掛版本綁 detekt」。
引句:「外掛檔不在時 detekt 整條失敗、新增告警閘照既有規則判環境不可用(閘的既有行為,不改)」
- 後果:新機器、換機、沒下載 jar,GlobalScope 裸用、複雜度、命名等現有規則也一起被自動放行。spec 只當成「閘的既有行為」,沒承認這是它新增的退化面。
- `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:124` 的慣例是「安裝=`brew install detekt`(套件管理器管生命週期)…外部工具一律裝進套件管理器」。spec 另開手動下載到 `~/.local/share/lumos/detekt-plugins/` 的新慣例,沒說明為何不能走套件管理器,也沒更新那一行。
- brew 的 detekt 不釘版本,而外掛釘 0.4.28(對 detekt 1.23.8)。detekt 一升,宣告就壞並被放行。
- 較安全的做法是外掛另開一條獨立宣告,或外掛檔不在時只退回不帶外掛的命令。spec 沒討論。

### F6 專案沒有 `.lumos/lint.json` 或沒有 kt 棧宣告時,A1、A2 完全不印
severity: minor
blocking: 否,與既有 T4 同形,是範圍限制,但和白話段「在專案是 Android 卻沒接時說實話」的承諾有落差。
- spec 段落:範圍 3,「宣告裡有 `kt` 棧而且是 Android 專案時」。
- `scripts/lumos:39092` 的 `if not lf["declared"]` 在沒有 lint.json 時直接早退,不會跑任何提醒。健檢 F 段也只在 `_lf["declared"]` 為真時才判(`scripts/lumos:4171`)。
- 最沒接的專案(沒有 lint.json)反而最安靜。天花板一節沒寫這點。

### F7 落地後會變假的句子,沒列進要改的範圍
severity: major
blocking: 是,下一個維護者會被舊句子誤導,而且 `lands_in` 漏了 `skills/kotlin-idioms/SKILL.md`。
- spec 段落:`lands_in` 與範圍 1、2。
- `skills/kotlin-idioms/SKILL.md:125`:R16 機檢欄寫 compose-rules「32 條」。spec 與型錄統計是 29 列,兩者口徑不同,spec 沒說明。
- `skills/kotlin-idioms/SKILL.md:228`:「加掛 compose-rules(detekt plugin jar)補 R16 整組」。這句要改成具體的外掛接法與下載指令,否則外掛怎麼接沒人說。
- `skills/kotlin-idioms/SKILL.md:17`:`REVISIT:2027-05-01` 要核對 compose-rules 與 Slack 規則名及條數。本案 2026-11-06 已實跑過一部分,此條要結案或改寫,spec 沒提。
- `configs/detekt/android.yml` 檔頭註解第 3 至 5 行的用法,以及「共用設定」那一條的「五條」,在加 `FunctionNaming` 設定後要同步。範圍 2 只說「理由寫在檔內註解」,沒說更新檔頭用法與 `linter精選目錄.md:125` 的「五條」。
- `linter精選目錄.md:124`「外部工具一律裝進套件管理器」與本案手動下載的衝突,見 F5。

### F8 範圍 4 沒說「內建」碼的列算不算 Android Lint
severity: minor
blocking: 否,是口徑缺口,但實作腳本會直接撞到,且影響約 20 列。
- spec 段落:範圍 4、S4。
引句:「現成規則欄點名了 Android Lint、androidx、Slack 規則碼(不是「待查」)的列」
- 型錄〈輸入與口徑〉(`checks-catalog.md:15`)寫「androidx/內建 = Android Lint」。型錄有約 20 列只寫 `內建:` 的現成規則,例如 `checks-catalog.md:170`(API-22 的 `內建:TrustAllX509TrustManager…`),另外還有 `IDE:` 開頭的 Android Lint 檢查名。
- spec 的列舉沒有「內建」與「IDE:」。一次性腳本要不要把這些列算進去,spec 沒定。S4 的測試因此可以兩種結果都過。

### F9 「compose-rules 官方建議對 Composable 忽略 FunctionNaming」找不到出處
severity: minor
blocking: 否,我只能標 ⚠,但這句是共用設定改動的唯一理由。
- spec 段落:PRIOR-ART ③、預期值表 S3 列。
引句:「compose-rules 官方建議對 `Composable` 註解忽略,共用設定照做」
- 我取到的 detekt 頁(https://mrmans0n.github.io/compose-rules/detekt/)內容裡沒有 `FunctionNaming` 這條建議,只有 `ModifierMissing` 的 `ignoreAnnotated` 範例。WebFetch 是摘要,可能漏,所以標 ⚠。
- spec 沒給出建議的具體網址或章節。CI 與守衛面都以它為依據,應附出處。

### F10 S3 測試在 CI 怎麼找到外掛 jar,spec 沒定
severity: minor
blocking: 否,是可執行性缺口。
- spec 段落:範圍 2、S3。
引句:「本機沒有 detekt 或外掛時跳過並印原因,CI 必跑」
- 本機 jar 在 `$HOME/.local/share/lumos/detekt-plugins/`,CI 照既有 detekt 步驟下載到 `$RUNNER_TEMP`(`.github/workflows/ci.yml:157`)。測試靠什麼(環境變數、固定路徑)找到 jar,spec 沒寫。
- 既有 detekt 步驟是把二進位放進 `PATH`,jar 沒有同樣機制。沒定義時,CI 可能整支被跳過而仍綠。

### 其他節
- 用詞、不做、回退、天花板:已讀,無 finding(F6 與 F7 另列)。
- 實務隱患逐類:
  - 金流、對外送出、不可逆:無。spec 已排除,我查證這部分沒有新增路徑。
  - 資安:無新增風險。下載有釘 sha256,我未自行驗證該雜湊,GitHub 頁顯示 4 個資產,但沒載入檔名清單,檔名 `detekt-compose-0.4.28-all.jar` 是否存在未能核對,⚠。
  - 守衛面放寬:成立(F5、F9)。
  - 基準線:官方頁確認 `baseline = file("lint-baseline.xml")` 與 `-Dlint.baselines.continue=true` 的說法與範本一致,沒有檔名或位置問題。

### 固定席節點
- `Systems/linter精選目錄`:會破壞其宣稱的行為。第 124 行「外部工具一律裝進套件管理器」與手動 jar 下載衝突(F5、F7)。
- `Systems/lint-declaration-health`:不影響既有判定。新函式獨立、不改退出碼,T4 的讀法沒被改,但要補提醒清單的說明。
- `Systems/kotlin規則包`:不影響。本案不碰 ast-grep 規則包,只動型錄通電批次字樣。

最嚴重 severity:major。blocking 共 6 條(F1、F2、F3、F4、F5、F7)。
