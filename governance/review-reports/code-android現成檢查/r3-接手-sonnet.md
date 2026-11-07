severity: major

整體判斷:r3 的程式和 linter 目錄對得上(我照文件在最小 repo 實跑過 A1)。問題集中在計劃的驗收條款、同節點的舊句子,以及 Slack 版本表的邊界。`-k lint_android_ci` 91 條全綠,`-k kt_catalog_batch4` 13 條全綠。

### F1 計劃驗收條款 S1 還寫 lintAnalyzeDebug 應照印,現在不印
severity: major
blocking: 是
引句:「只有 `lintKotlin`、`lintFix`、`lintVitalRelease`、`lintAnalyzeDebug`、`updateLintBaseline` 應 照印」
- file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:81`
- 這一輪 `_ANDROID_LINT_NONCHECK` 拿掉了 `Analyze` 和 `Report`,測試也把 `lintAnalyzeDebug` 從「照印 A1」清單刪掉,但條款沒跟著改。條款綁在 `[test:t_lint_android_ci_advice]`,條款和測試現在對不上。
- 最小重現:Android 專案加 `.lumos/lint.json`(kt 棧),workflow 只寫 `./gradlew lintAnalyzeDebug`,跑 `lumos lint-check --json`。advisories 裡沒有 A1,條款卻說應該印。
- 同一條款尾端還寫「T4 的判定 應 跟改用共用讀檔函式前相同」。`_ci_config_texts` 已在 r3 刪掉,那個「共用讀檔函式」不存在了,是壞引用。
- 引句:「T4 的判定 應 跟改用共用讀檔函式前相同」

### F2 同一個節點裡新舊 WHY 打架
severity: minor
blocking: 否
引句:「A1 CI 設定檔沒有 Android Lint 任務、A2 用 Compose 卻一套 Compose 規則都沒接」
- file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:33`
- r3 在下一行新加了「A1 用證據模型」的 WHY,但第 33 行仍把 A1 說成「CI 設定檔沒有 Android Lint 任務」。這是舊的判斷題,而且只看 CI 設定檔、不看建置檔。
- 這就是專案規定要照「新行為」重寫的內部矛盾(摘要裡新舊衝突)。

### F3 計劃實務隱患和天花板還說 A1 是「判有沒有接」,又說跟 T4 同形
severity: minor
blocking: 否
引句:「會判成沒接而多印提醒;只是提醒、不擋,這是只看字面的代價(跟 T4 同形)」
- file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:69`
- 同檔第 114 行的天花板 4 也寫「A1 照樣判成沒接」。
- r2 的折入紀錄明寫「計劃與 linter 目錄寫明 T4 讀原文、A1 去註解,不再說兩者同形」。這兩處是漏網。「判成沒接」也和證據模型的「找不到跡象才提醒」措辭不一致。

### F4 天花板沒寫「有 lint 區塊或 baseline 檔就不印,即使 CI 根本沒跑」
severity: minor
blocking: 否
引句:「③建置檔有 `lint { }` 或 `lintOptions { }` 區塊,或專案往下三層內有 `lint-baseline.xml`(範本第 1、2 步的痕跡)」
- file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:53`
- 實跑:`build.gradle.kts` 只有 `android { lint { abortOnError = false } }`、沒有任何 CI 檔,`lumos lint-check --json` 不印 A1。
- 這種「為了關掉 lint 而寫的區塊」很常見。天花板 2 只列了 `-x lint`、`echo`、job 名稱,沒列「設定了但 CI 沒跑」。
- 範本照做時,做完第 1、2 步還沒做第 3 步,A1 就消失了。這正是 A1 要抓的狀態。linter 目錄有把區塊列為跡象,所以不算說錯,是漏列的代價。
- S1 條款也沒收 ③ 的兩個案例,測試有而條款沒有。

### F5 Slack 版本表和它自己的挑法規則不一致,且有缺口
severity: minor
blocking: 否
引句:「AGP 9.4 以上用 `1.6.1`(lint 32.4.1);AGP 9.3 用 `1.5.5`(lint 32.3.2);AGP 8.7 到 8.x 用 `1.4.2`(lint 31.7.1)」
- file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:183`
- 我開了發行頁核對,三個建置用 lint 版本都屬實:1.4.2 是 31.7.1,1.5.5 是 32.3.2 加 AGP lint plugin 9.3.2,1.6.1 是 32.4.1。「lint = AGP + 23」有直接證據。
- 但表有三個問題:
  - 規則寫「建置用 lint 不高於專案 lint」。AGP 9.3.0 或 9.3.1 的 lint 是 32.3.0 或 32.3.1,低於 1.5.5 的 32.3.2。AGP 9.4.0 對 1.6.1、AGP 8.7.0 對 1.4.2 也有同樣問題。
  - AGP 9.0 到 9.2 沒有任何一列,「更舊的照發行說明挑」也蓋不到這段。發行頁有 1.5.0(lint 32.2.1),可以對 AGP 9.2。
  - AGP 8.13 這類專案,規則會選 1.4.3(lint 31.13.2),表卻寫 1.4.2。
- 計劃有 `REVISIT:2026-12-15` 要實跑驗證,所以降為 minor。

### F6 依據來源:lintVital 只看 fatal 的出處,三個引用頁都沒提到
severity: minor
blocking: 否
引句:「DSL 參考頁 `checkReleaseBuilds`:release 建置只看 fatal 級(lintVital)」
- file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:142`
- kotlinter README、lint 指南、DSL 頁我都抓下來搜過,`lintVital` 這個字零次。DSL 頁只說 `checkReleaseBuilds`「release builds run lint on issues with severity=fatal」,是旁證,任務名到行為是作者推出來的。
- 真正含 `lintVitalRelease` 與 fatal 的是下一行引用的 AOSP 提交 `cc9093a`,可以改引它。
- 其他幾條都屬實:Scorecard `checks.md` 的 SAST 與 CI-Tests 引句逐字存在;kotlinter 的 `lintKotlin: report Kotlin lint errors` 存在;`lintFix` 對應 `--apply-suggestions` 存在;Android lint 頁的「strongly recommend… continuous integration」存在;`r2-ciexp.md`、`r1-正確性-sonnet.md` 查證段、`r1-intake.md` 都存在。
- 另一處小誤標:「lint 使用指南」其實是 googlesamples 的 custom-lint-rules 使用手冊,不是 developer.android.com 的官方指南。內容仍支持那句。

### F7 A1 認 `lint` 不分工具,非 Gradle 的 lint 也算跡象
severity: minor
blocking: 否
引句:「任何一個詞是 lint 任務名(`lint`、`lint` 接大寫變體名、可帶 `:模組:` 前綴、Bitrise 的 `android-lint`;」
- file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:53`
- 實跑:workflow 只有 `run: npm run lint`,沒有 Gradle lint,A1 不印。
- `needs: build` 這種寫法也會讓提到 gradle 的檔被當成有跡象。天花板列了 `echo`、`-x lint`、job 名稱,沒列「別的工具的 lint」。這是少印方向,不是誤報。

### F8 測試耗時警示
severity: minor
blocking: 否
引句:「(r2:直接呼叫函式,不再每例起一個 lint-check 子程序,壓測試耗時;端到端那條上面 S2 已驗)」
- file: `scripts/test_lumos.py:126356` 附近(`t_lint_android_ci_advice`)
- 修補要壓耗時,但我本機跑 `-k lint_android_ci` 仍印 `69.6s t_lint_android_ci_advice (餘裕 3x) ⚠ 餘裕不足 3 倍`,超時上限 180 秒。
- 可能受其他會談並行影響,不確定。CI 若比本機慢 2.6 倍以上會紅。

沒發現問題的項目:
- `_android_ci_lint_evidence` 對 100 萬字元單行(`a:` 重複、`a-` 重複、空白詞)耗時 0.02 到 0.16 秒,沒有正規式效能問題。
- 範圍外手法紀錄那列更正文字 58 字,符合 60 字限制,沒帶 `|`、`[[`、反引號。
- 三篇改動的節點 `lumos lint` 都是 0 問題。

總結:最嚴重是 F1(驗收條款 S1 與測試、程式行為不符,另有壞引用),會擋 1 條;其餘 7 條是文件措辭、版本表精度、出處與天花板漏列。

審查席暫存目錄 `/private/tmp/lumos-seat-work/code-android現成檢查/接手-sonnet` 已用字面路徑刪除。
