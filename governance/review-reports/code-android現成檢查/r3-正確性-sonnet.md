severity: major

F1 到 F5 的三問、實驗和圖譜判讀都附在後面,全部是實際跑過的結果。我沒有改 repo。唯一的例外是跑測試時工作樹多了 `docs/.canary-log.jsonl` 之類的既有改動。

**F1 計劃驗收條款 S1 還寫著 `lintAnalyzeDebug` 應照印,程式已不這樣判,測試也刪掉了這一例(屬 A1 排除名單修補)**
severity: major
blocking: 是
引句:「-    for line in ("./gradlew lintKotlin", "./gradlew lintFix", "./gradlew lintVitalRelease", "./gradlew lintAnalyzeDebug",」
file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:81`
- 失敗場景:S1 條款寫「只有 `lintKotlin`、`lintFix`、`lintVitalRelease`、`lintAnalyzeDebug`、`updateLintBaseline` 應 照印」。r2 把 `lintAnalyze`、`lintReport` 從 `_ANDROID_LINT_NONCHECK` 拿掉,但條款沒跟著改。
- 重現:對 `_android_ci_lint_evidence` 餵 `./gradlew lintAnalyzeDebug`,回 `True`(不印 A1),`lintReportDebug` 也是。`lintVitalRelease`、`updateLintBaseline`、`lintKotlin`、`lintFix` 都回 `False`。
- 為什麼測試抓不住:綁這條的是 `t_lint_android_ci_advice`,但測試清單已刪掉 `lintAnalyzeDebug` 那一例。`lumos spec-trace` 只檢查有沒有綁定,不檢查條款內容。所以驗收條款是假的,卻沒有任何東西會紅。
- 建議修法:把條款裡的 `lintAnalyzeDebug` 拿掉。
- 順帶:S1 末句「T4 的判定 應 跟改用共用讀檔函式前相同」指的 `_ci_config_texts` 已刪,措辭也過期。

**F2 A1 的「少印」範圍比文件寫的大很多(A1 證據模型 ②)**
severity: minor
blocking: 否
引句:「+                if gradle and _ANDROID_UMBRELLA_WORD.fullmatch(w):」
file: `scripts/lumos:39020` 附近的 `_android_ci_lint_evidence`
- 實跑結果,以下輸入都回 `True`(A1 不印),但實際都沒跑 Android Lint:
  - GitLab `stages: [build]`、`stage: build`,加 `./gradlew assembleDebug`。
  - GitLab `stage: lint`,加 `./gradlew detekt`。
  - 一個 `name: lint` 的 job,只跑 `ktlintCheck`。
  - `npm run lint` 加 `./gradlew assembleDebug`。
  - CircleCI workflows 裡的 `- build`。
- 原因:gradle 只要在檔裡出現一次,任何一個叫 `build` 或 `check` 的詞就算跡象;`lint` 也是任何一個詞就算。
- 文件缺口:測試和計劃只承認「`name: build`、`-x lint`、`echo`」。GitLab 的 stage 幾乎一定有 `build`,所以 GitLab 專案的 A1 實質上永遠不印。這是設計取捨,不是邏輯錯。
- 建議修法:把這幾種寫進天花板。

**F3 計劃寫「S5 實跑時用 `./gradlew check --dry-run` 核對」,但 S5 條款和 REVISIT 都沒有這件事**
severity: minor
blocking: 否
引句:「+   - **A1**:**證據模型**——建置檔與 CI 設定檔裡都找不到 Android Lint 的跡象才印」
file: `Android現成檢查接上CI與推送前_計劃.md:53`(對照第 85 行的 S5 和第 117 行的 REVISIT)
- 失敗場景:這個承諾沒有人會回頭做。範圍 3 那段的 `check --dry-run` 核對在 S5 [manual] 和 REVISIT 裡都找不到,`grep dry-run` 全計劃只有第 53 行這一處。
- 建議修法:補進 S5 或補一行 REVISIT。

**F4 A1 跡象 ③ 的三個分支測試改壞照綠(A1 證據模型 ③)**
severity: minor
blocking: 否
引句:「+_ANDROID_LINT_CONFIG = re.compile(r"^[ \t]*(?:lint|lintOptions)[ \t]*\{", re.M)」
file: `scripts/lumos:39040` 附近
- 測試只覆蓋 `lint {` 與 `app/lint-baseline.xml`。我能想到三種改壞,測試都不會紅:
  - 拿掉 `lintOptions` 分支。
  - 把深度上限 3 改成 10。
  - 拿掉 `_stack_scan_skip` 剪枝。
- 實跑 `lintOptions {`(Groovy)回 `True`,沒問題;`build/lint-baseline.xml` 與深度 4 的 baseline 都回 `False`,行為對。缺的是守衛測試,不是行為錯。
- 小問題:單行寫法 `android { lint { … } }` 因為 `^` 錨定,不被認作跡象。

**F5 A3 的「判不了就不判」沒涵蓋大括號展開(A3 判不了清單)**
severity: minor
blocking: 否
引句:「+        if any(ch in raw for ch in "`*?["):   # 命令替換與萬用字元要 shell 才算得出,判不了、不算」
file: `scripts/lumos:39075`
- 重現:`detekt --input a.kt --plugins tools/{p,q}.jar` 先被逗號拆成 `tools/{p` 與 `q}.jar`,兩個都不在,回 `True`,誤印 A3。這跟 r2 的反引號、萬用字元是同一形狀(要 shell 才算得出的值)。
- 影響很窄,實務上幾乎不會這樣寫。

## 修補三問

- **A1 證據模型**
  - ① 修好了:r2 的重現輸入全都回 `False`,包括 `assembleDebug && cp app/build/outputs/...`、`-Dkotlin.build.report.output=f -Pci.check=true`、`--init-script ci/check.gradle`、`//` 註解行。Bitrise、Azure、續行、矩陣各例回 `True`。
  - ② 帶進新問題:見 F1、F2。
  - ③ 同形狀:`_detekt_ci_has_typed_task`(T4)沒套 `//` 略過,但它是另一個函式,也不在本輪範圍。
- **A3 走訪器**
  - ① 修好了:反引號、`*`、`?`、`[`、`$(…)`、沒設的變數都回 `False`。
  - ② 沒有新錯:舊 `_detekt_plugin_values` 的 `sh -c` 單層展開、`&&` 與換行切段,新走訪器行為一致;`_detekt_command_codes` 的呼叫端只剩一處,沒有遺留。
  - ③ 同形狀:見 F5。
- **toml 剝註解**
  - ① 修好了:整行 `#`、行尾 `# …` 都剝掉,字串裡的 `"#com.android.x"` 保留,CRLF 正常。
  - ② 沒有新錯。
  - ③ 同形狀:`gradle/libs.versions.toml` 現在也吃 `_ANDROID_LINT_CONFIG`,toml 裡出現 `lint {` 行會被誤認成跡象,實務上不會發生。

## 實驗

我把函式載入臨時目錄實跑,四個函式都做了至少三正三反。

- `_android_ci_lint_evidence`:正例 10 個、反例 7 個,見 F2 的數據;其中 `lint${{ matrix.variant }}` 與 `lint$VARIANT` 會回 `False`,也就是會誤印 A1,屬於可接受的「多印」。
- `_android_lint_config_evidence`:正例 5 個(`lint {`、`lintOptions {`、深度 2 的 baseline、`lint{`、字串裡的 `lint {`),反例 9 個(註解、`build/`、深度 4、baseline 是資料夾、隱藏資料夾、`tasks.lint {` 等)。
- `_android_build_texts`:toml 註解、CRLF、`/* */`、settings、隱藏資料夾、深度 3 與 4、符號連結、具名管道(回空)、非 UTF-8 都符合預期。
- `_android_plugin_missing`:正例 8 個,反例 15 個(含 `sh -c` 巢狀兩層、gradle 命令、非 detekt 的 `-p`),除 F5 外都符合預期。
- 測試:`-k lint_android_ci` 為 91 個通過,最慢 71.6s,工具標了「餘裕不足 3 倍」;`-k detekt_` 為 129 個通過。

## 圖譜判讀

- `Systems/lint-declaration-health.md`:新增的 A1 證據模型 WHY 與程式一致。同篇舊 WHY 還寫「A1 CI 設定檔沒有 Android Lint 任務」,語意略舊但不矛盾。WHY 的 [代價:] 只提到「寫了字樣沒跑」,沒提到 F2 的範圍,屬極輕的文字缺口。
- `Systems/linter精選目錄.md`:A1 的描述和 Slack 版本表(1.6.1、1.5.5、1.4.2)與計劃一致,不影響它宣稱的行為。
- `Systems/kotlin規則包.md`:沒有 A1 到 A3 的描述,不影響。

## 計劃〈依據來源〉逐行

- 對得上:
  - OpenSSF Scorecard 的引文逐字核對正確(SAST 那三句、CI-Tests 那句)。
  - `r2-ciexp.md` 存在,內容和計劃寫的 6 個專案結果一致。
  - A3 判不了、toml 剝法、`lintKotlin`/`lintFix`/`lintVital` 排除、`check`/`build` 各行與程式一致。
  - `_kt_pack_check_module` 已刪,`_ktpack(copy=True)` 沿用到位。
- 對不上:
  - F1(S1 條款)。
  - F3(S5 核對承諾)。
  - 「A1 證據模型的實測」只有 GitHub workflow,不含 GitLab,所以推不出 F2 的範圍。
  - 該行寫 4 個找到跡象,但卷證顯示 NewPipe 與 thunderbird 的跡象詞裡有 `build`,結論仍成立,只是不夠有診斷力。

## 角色鏡頭

- 後端 `be-api-compat`:不影響。改動是 lint-check 的提醒文字與 `--json` 的 `advisories` 字串,A 系列條目格式 `[CI] A1:` 和 `[kt 第 N 條] A3:` 沒變,舊讀取端讀得懂。
- 後端 `be-authz`:不影響。沒有新增端點;A3 只讀對方的 `lint.json` 並做檔案存在判斷,不回顯路徑,與計劃寫的縱深防禦說法一致。

總結:最嚴重是計劃 S1 驗收條款與程式不一致且測試抓不住,會擋 1 條(F1),另有 4 條輕微不擋(F2 到 F5)。

臨時目錄 `/tmp/lumos-seat-work/code-android現成檢查/正確性-sonnet/` 留給編排者收貨後刪。
