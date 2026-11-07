# r1 收貨紀錄(android現成檢查接上ci與推送前)

preflight-4: ran

## 首輪前掃(2026-11-06,sonnet 一席,只讀)

命中:未定義的詞 2、壞引用 3、範圍矛盾 4、機械宣稱驗語意 6。①②③與存在類直接修真檔;語意類逐條列修改前→後(修改前全文備份在會談暫存區 b4-before-preflight.md,不進卷證)。沒有核心裁定節。

| # | 前掃發現(語意類) | 修改前 | 修改後 |
|---|---|---|---|
| 語1 | T4 的出口是 detekt 專用函式與「detekt 宣告實際會怎樣」標題,T4 又要求宣告裡有 detekt 命令 | 「跟 detekt 的 T4 同一個出口」 | 新函式 `_lint_android_ci_advisories` 自帶代號與文字表,另起標題「Android 現成檢查有沒有接上」;A1、A2 不要求有 detekt 命令 |
| 語2 | 外掛缺失時 detekt 會不會先寫空 SARIF 是外部行為,計劃沒實跑證據 | (未驗) | 2026-11-06 實跑:`--plugins` 指不存在的 jar,detekt rc 1、不產 SARIF,新增告警閘走環境不可用;計劃原句成立,不改字 |
| 語3 | 型錄 Android Lint 列數口徑:前掃數到 102 | 「型錄 103 列提到」 | 「型錄約 100 列提到」 |
| 語4 | 型錄〈輸入與口徑〉的通電批次值清單沒有新字樣 | (未提) | 範圍 4 加「值清單同步加這兩個字樣」 |
| 語5 | check.py 對通電批次只驗非空,沒有值域 | (計劃沒宣稱) | 不改,改字樣不會被自檢擋 |
| 語6 | T4 讀 workflow 沒有大小上限,A1、A2 的 1 MB 與 200 支是新限制 | 「同樣只看字面」連帶暗示同一套上限 | 寫明建置檔的上限是本案新設,workflow 檔沿用 T4 讀法 |

另修:A1 任務名邊界寫死(`lint` 或 `lint` 接大寫變體,排除 `Fix`、`Vital`、`Analyze`、`Report` 開頭與 `updateLintBaseline`),S1 加 `lintAnalyzeDebug`;版本目錄外掛別名列舉;外掛本機目錄標新增慣例;本 repo CI 多下載外掛並驗雜湊,讓 S3 在 CI 必跑;A2 不看版本,S2 加 0.5.0 jar 與第 201 支建置檔兩例。

## r1 收貨(2026-11-06,四席全數交回後一次存檔)

- 四席(正確性、邊界、接手、架構對齊,全 sonnet)審同一份 r1-snapshot.md(98 行,sha256 24c355b4…)。從子代理逐字稿存檔;四份已是正規化格式。
- quote-check:正確性 5/5、接手 13/13、架構對齊 19/19 全錨;邊界 10 句有 2 句錨不到(#7 不足 10 字、#9 是截斷),那兩句不採信,所屬 F7、F9 另有佐證與重現,照採。refcheck 四份全 ok。
- 席位沒有改 repo:`git status` 只有本輪卷證與編排者自己的改動;審查席臨時目錄存完報告後已刪。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 一正1 | 正確性 F1、邊界 F1 | 本機 detekt 1.23.8 用現行共用設定跑標準 Compose 檔 | HIT:報 FunctionNaming 3(含 `fun Other()`)、LongParameterList、MagicNumber、TopLevelPropertyNaming、UnusedPrivateMember;加 detekt 官方 Compose 頁六項後只剩 `fun Other()` |
| 一接2 | 接手 F2、邊界 F2 | 席位讀外掛 jar 內 `config/config.yml` | HIT(席位原輸出):`Material2`、`PreviewNaming`、`UnstableCollections` 是 `active: false` |
| 一正2 | 正確性 F2、接手 F3、F4、邊界 F3、F4 | 對照 `scripts/lumos` 的 `_detekt_ci_has_typed_task` 全文掃描,計劃 A1 要求「前面是 gradlew」 | HIT:`./gradlew --no-daemon lintDebug` 判不到、`lintKotlin` 被當成 Android Lint |
| 一接8 | 接手 F8、邊界 F5、正確性 F3 | `grep -c '內建:' skills/kotlin-idioms/checks-catalog.md` | HIT:型錄用「內建:」寫 Android Lint 規則,計劃口徑沒列 |
| 一架1 | 架構 F1 | `grep -n '_KT_BUILD_ANDROID' scripts/lumos` | HIT:既有 Android 建置檔判法 |
| 一接5 | 接手 F5、邊界 F8、架構 F4 | 本機實跑 `detekt --plugins <不存在的 jar>` | HIT:rc 1、不產 SARIF,整條 detekt 被判環境不可用 |
| 一接1 | 接手 F1、邊界 F9 | `gh api repos/slackhq/compose-lints/releases` 列各版建置用的 lint 版本 | HIT:1.6.0 要 AGP 9.3+;1.4.2 用 lint 31.7.1 建 |

refuted: none

## 先查世界

- PRIOR-ART: Compose 專案的 detekt 設定——detekt 官方 Compose 頁(https://detekt.dev/docs/introduction/compose/ )列六項:FunctionNaming 對 Composable 忽略、TopLevelPropertyNaming 允許 PascalCase、LongParameterList 忽略預設值參數、MagicNumber 忽略屬性宣告、未使用私有函式對 Preview 忽略、TooManyFunctions 不算 Preview;compose-rules 規則頁也要求 `ignoreAnnotated: ['Preview']`(https://mrmans0n.github.io/compose-rules/rules/ )。採用全部六項;本機實跑驗過 1.23.8 認得這些鍵、誤報消失。原計劃寫「compose-rules 官方建議 FunctionNaming」出處錯,改指 detekt 官方頁。
- PRIOR-ART: 外掛缺檔拖垮整條 detekt——detekt CLI 有 `--disable-default-rulesets`(`detekt --help` 列出),外掛規則另開一條宣告只跑外掛,缺檔只影響那條。採用。
- PRIOR-ART: Slack 外掛與 AGP 版本——lint 版本號等於 AGP 加 23(lint 31 對 AGP 8、32 對 AGP 9);發行說明 1.6.0 要 AGP 9.3+、1.4.2 用 lint 31.7.1 建(https://github.com/slackhq/compose-lints/releases )。範本改給版本表。
- PRIOR-ART: `check` 帶 lint——AOSP 提交讓 `check` 依賴 `lint`(https://android.googlesource.com/platform/tools/base/+/cc9093a%5E%21 ,年代較舊,S5 實跑時 `--dry-run` 核對);Gradle `build` 依賴 `check`(https://docs.gradle.org/current/userguide/base_plugin.html )。

## 歸因

- 第一輪,沒有上一輪修補可回歸。

## 逐條去向(30 條全折,0 放行,0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 一正1、一邊1、一正4、一接9 | 正確性 F1、F4,邊界 F1,接手 F9 | 折:共用設定改加 detekt 官方 Compose 頁六項,出處改指 detekt 官方頁;S3 改驗六條誤報消失、一般函式照報 |
| 一正2、一接3、一接4、一邊3、一邊4 | 正確性 F2,接手 F3、F4,邊界 F3、F4 | 折:A1 改成整行掃 Gradle 呼叫裡的任務詞,收 `check`、`build`、`arguments:`,排除 `Kotlin` 開頭;S1 加五種寫法 |
| 一正3、一接8、一邊5 | 正確性 F3,接手 F8,邊界 F5 | 折:範圍 4 口徑改成切段、認 `androidx`/`內建`/`slack`/`cr` 開頭帶規則碼,排除待查、預設關、相近、opt-in;S4 改成照口徑重算全表比對 |
| 一接2、一邊2 | 接手 F2,邊界 F2 | 折:預設關三條不標接電,另開 `compose.yml` 寫明不開與原因;天花板列出 |
| 一正5、一接10 | 正確性 F5,接手 F10 | 折:CI 下載後放進 `LUMOS_DETEKT_COMPOSE_JAR`,CI 找不到判紅、本機才跳過 |
| 一接5、一邊8、一架4 | 接手 F5,邊界 F8,架構 F4 | 折:compose-rules 另開一條只跑外掛的宣告(`--disable-default-rulesets`),缺檔只影響那條;外掛目錄寫成「一律套件管理器」的例外並寫理由;新增 A3 提醒外掛檔不在 |
| 一接1、一邊9 | 接手 F1,邊界 F9 | 折:範本給 AGP 對 Slack 外掛版本表,S5 記 AGP 版本,REVISIT 兩種 AGP 各跑一次 |
| 一接6、一邊6 | 接手 F6,邊界 F6 | 折:CI 設定檔納入 GitLab、Bitrise、CircleCI、Jenkins、Azure;沒宣告就不判寫進天花板 3 |
| 一接7 | 接手 F7 | 折:新增範圍 5,改 kotlin-idioms SKILL.md 三處與共用設定檔頭、linter 目錄「五條」 |
| 一邊7 | 邊界 F7 | 折:讀檔一律 `errors="replace"`,S1 加非 UTF-8 例 |
| 一邊10、一架1 | 邊界 F10,架構 F1 | 折:Android 判法沿用 `_KT_BUILD_FILES`/`_KT_BUILD_ANDROID`(認 `libs.plugins.android` camelCase 別名),往下三層;S1 加兩例 |
| 一架2 | 架構 F2 | 折:條目格式 `[CI] A1:`,另一支印出函式與標題 |
| 一架3 | 架構 F3 | 折:抽共用 `_ci_config_texts`,T4 改用它、判定不變,S1 釘 |
| 一架5 | 架構 F5 | 折:lands_in 加 `Systems/bound-tests-gate`(`.github/workflows/ci.yml` 的家) |
