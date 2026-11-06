severity: minor

我沒有找到 blocker 或 major。`python3.14 scripts/test_lumos.py -k t_lint_android_ci_advice` 實跑 112 passed、0 failed。我依計劃寫的規則在臨時 repo 實跑 `lint-check --json`,結果跟計劃範圍 3、S1 的說法一致。S1 列的情況我只抽驗幾項,主要靠這支測試。

**F1**
severity: minor
blocking: 否
引句:「`check`、`build` 寫在跟 gradle 不同行的欄位(Azure Gradle 任務的 `tasks: 'check'`、Bitrise 的 `gradle_task: check`)不算跡象,也會多印 A1」
天花板只舉了 Azure 和 Bitrise 兩例,漏了 GitHub 最常見的 gradle action 寫法。重現:`.github/workflows/c.yml` 寫 `uses: gradle/gradle-build-action@v2` 加 `with:` 底下 `arguments: build`,其餘不寫 lint,實跑印 A1。原因是 `_is_gradle_head` 取路徑最後一段,`gradle/gradle-build-action` 不算 gradle 呼叫詞。建議天花板補上 `with: arguments: build/check` 這一類。

**F2**
severity: minor
blocking: 否
引句:「AGP 9.4 以上用 1.6.1(lint 32.4.1);AGP 9.3 用 1.5.5(lint 32.3.2);AGP 9.0 到 9.2 用 1.4.2」
表的邊界跟自己的挑法規則(lint = AGP 加 23、外掛建置用的 lint 不高於專案 lint)不一致。AGP 9.4.0 的 lint 是 32.4.0,低於 1.6.1 的 32.4.1,表卻說 9.4 以上用 1.6.1。AGP 8.7.0 的 lint 是 31.7.0,低於 1.4.2 的 31.7.1,同樣不合。文件只補了 9.3.0、9.3.1 這個例子,這兩個邊界沒提,也沒再補一句統括。「表只是常見對照」那句有救一部分,但這兩處沒點名。此外 1.4.3 發行頁的 PR 標題寫 lint 31.13.2,版本表和〈依據來源〉都沒提 1.4.3,也沒說明為何不收(release note 本身沒寫建置用的 lint 版本)。

**F3**
severity: minor
blocking: 否
引句:「2026-11-06 下載 6 個公開 Android 專案的 GitHub workflow 實跑:nowinandroid、thunderbird、element-x、NewPipe 找到跡象」
這份實測是 r2 的舊模型跑的(整檔 gradle 加建置檔證據,見 `governance/review-reports/code-android現成檢查/r2-ciexp.md`)。r3、r4 改成同一邏輯行的 gradle 呼叫詞後,沒有重跑。我看了跡象詞,四個專案都留著 lint 任務名,結論應該仍成立,但文件把它寫成現行模型的實測依據,沒標明是舊模型。

**F4**
severity: minor
blocking: 否
引句:「`check`、`build` 只在同一邏輯行有 gradle 呼叫詞時才算,建置設定不算」
這句話的實際範圍比字面寬,文件沒講。命令列有 `-PbuildType=check`(`=` 是切詞字元)或 `cd app && ./gradlew test; make check`,都會因同一行有 `gradlew` 加 `check` 字樣而算有跡象。這是少印方向,符合「寧可少印、不誤報」,但天花板沒列。建議在天花板補一句「同一行任何位置的 check/build 字樣都算」。

**F5**
severity: minor
blocking: 否
引句:「專案是 Android,但 CI 設定檔(.github/workflows/、.gitlab-ci.yml 等)裡都找不到 Android Lint 的跡象」
A1 現在只看 CI 設定檔,但 `scripts/lumos:4181` 和 `scripts/lumos:39115` 的標題還寫「只看建置檔與 CI 設定檔字面判的」。`linter精選目錄.md` 第 186 行結尾也有同一句。A2 確實讀建置檔,所以整則提醒的標題不算錯,只是跟 A1 的收窄不一致,措辭精度問題。

**文件對文件**
- repo 的 docs/、skills/、configs/、scripts/lumos 註解裡,已沒有句子說 A1 看建置檔 lint 區塊或基準線檔。
- 也沒有「整檔提到 gradle」的舊說法。
- `_android_lint_config_evidence` 在這些位置零殘留。

**〈依據來源〉網址**
- Slack 發行頁:1.5.5 同時寫 lint 32.3.2 與 AGP lint plugin 9.3.2;1.5.0 寫 lint 32.2.1;1.6.0 寫「requires AGP/lint 9.3+」;1.6.1 寫 32.4.1;1.4.2 寫 31.7.1。全部屬實。
- AOSP 提交 cc9093a:`check` 依賴 lint、`lintVitalRelease` 只查 fatal 級,支持那句。
- googlesamples 使用手冊:`lintFix` 是 `--apply-suggestions` 的捷徑,支持那句。
- Scorecard checks.md:SAST 與 CI-Tests 的引句都在,「looks for known GitHub apps」只在 SAST 段,計劃也是這樣用的。
- Stack Overflow 21143556:沒能驗證。WebFetch 被擋,curl 遇到 Cloudflare 驗證頁。文件已自述是社群旁證。
- 版本表跟「建置用 lint 不高於專案 lint」的挑法,大致一致,例外見 F2。

**圖譜鏡頭**
固定席沒附。`lint-declaration-health.md` 新改的兩條 WHY 摘要行(A1 三則提醒、A1 證據模型),跟 `scripts/lumos` 的 `_android_ci_lint_evidence`、`_ci_config_paths` 一致,沒有對不上的地方。

總結:最嚴重是 minor(措辭與邊界精度),會擋 0 條
