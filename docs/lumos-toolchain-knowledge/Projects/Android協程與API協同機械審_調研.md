---
type: project
status: done
created: 2026-11-04
updated: 2026-11-08
tags:
  - type/project
  - status/done
  - scope/stack-knowledge
related:
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/棧別提問表態閘]]"
  - "[[Systems/lint-declaration-health]]"
  - "[[Projects/kotlin慣例skill_計劃]]"
  - "[[Systems/效能檢核目錄]]"
---
# Android協程與API協同機械審_調研

> 白話:問題是「本工具對 Android 的協程 scope 用法、以及同一個功能裡多支 API 怎麼串怎麼並,有沒有審?沒有的話世界上怎麼機械審?」答案是有審,但幾乎全靠問審查員;唯一的機械檢查(detekt)照工具教的接法跑,大部分協程規則其實沒在跑。下面是現況盤點、本機實驗、世界解與建議順序。

PRIOR-ART: 先盤點本工具既有三道(共用 detekt 設定、棧別提問、kotlin-idioms 文件),再搜世界:detekt 官方協程規則集、structured-coroutines 規則包、Sonar Kotlin 協程規則、androidx 自帶 lint、TS/Dart 的「串行獨立等待」規則、kotlinx 官方虛擬時間測試。裁定=借用現成規則與測試工具,只在 Kotlin 沒有輪子的地方(串行獨立等待、行動端外呼逾時)自寫規則。

## 現況:三道防線各管什麼(2026-11-04 盤點,以程式碼為準)

| 項目 | 機械檢查 | 審查員提問 | 只在文件 |
|---|---|---|---|
| GlobalScope 裸用 | 共用 detekt 設定已開(不要型別資訊,照標準接法會響;2026-11-08 起照 `{LINT_FILES_CSV}` 接法推送前擋新增) | 協程題 | |
| 吞掉取消訊號 | 共用設定已開(要型別資訊,見下方實驗:照命令列樣板多半沒在跑;推送前不擋,消費專案照 [[Systems/linter精選目錄]] 的 CI 型別檢查範本接上後由 CI 擋新增) | 執行緒題 | kotlin-idioms R10 |
| Dispatcher 寫死 | detekt 預設開(同樣要型別資訊;推送前不擋,消費專案照 [[Systems/linter精選目錄]] 的 CI 型別檢查範本接上後由 CI 擋新增) | 執行緒題 | |
| scope 沒跟生命週期 | | 協程題 | |
| runBlocking | | 協程題 | R12 原說要禁,2026-11-04 改成不全面禁(同步介面橋接是正當用法) |
| Job/SupervisorJob 傳進 launch | | | R12 |
| Flow 收集跟生命週期 | 2026-11-04 起共用設定禁 collectAsState(要型別資訊才跑;推送前不擋,消費專案照 [[Systems/linter精選目錄]] 的 CI 型別檢查範本接上後由 CI 擋新增) | Flow 題 | R13 |
| 互不依賴的 API 串著等 | | 協程題第一問 | R1 |
| 一支失敗其他支要不要取消 | | | R1 |
| 行動端外呼逾時與重試 | | **Kotlin 沒有**(同題只掛在 Java 棧) | |
| 舊回應蓋新資料、重複送出、callback 轉 suspend | | 只有代碼審角色卡的前端題(派工時開卡才出現) | R7 間接 |

棧別提問的題目表見 [[Systems/棧別提問表態閘]];共用 detekt 設定與標準接法的家是 [[Systems/linter精選目錄]];宣告健檢見 [[Systems/lint-declaration-health]]。

## 本機實驗:標準接法下協程規則沒在跑

做法:一支故意埋協程錯誤的小檔,用 detekt 1.23.8(brew 版)照標準接法跑,再逐步補參數對照。

- **照標準接法(只給原始碼目錄)**:埋了五種錯,只抓到 GlobalScope 一種。原因:其餘規則要型別資訊,沒給就不跑,也不出任何警告。
- **加上型別參數(classpath 給協程函式庫與標準庫、JDK 位置;jvm-target 後來實測不影響)**:Dispatcher 寫死、回傳 Flow 卻標 suspend、協程裡用 Thread.sleep、多餘的 suspend 都響了。
- **吞取消訊號那條**:標準庫是 Kotlin 2.0.21 時響,換 2.3.21 就不響(協程函式庫 1.8.1 與 1.10.2 結果相同)。推測是 detekt 1.23.8 內建的 Kotlin 編譯器讀不懂新版標準庫的中繼資料,所以解析不到 runCatching。
- **kotlin-idioms 推薦的兩條規則在 1.23.8 不存在**:finally 裡呼叫 suspend 那條與測試沒包 runTest 那條只在 detekt 2.0 預覽版;設定檔寫了不存在的規則,detekt 整個拒跑(設定驗證失敗),一筆 SARIF 都不產。
- **1.23.8 正式版協程規則共 7 條**,當時預設關、共用設定還沒開的只剩「suspend 函式又掛在 CoroutineScope 上」那條(2026-11-04 [[Projects/Android的detekt規則說實話_計劃]] 已補開);補開後帶型別資訊會響。用 ForbiddenMethodCall 禁 collectAsState 帶型別資訊也會響。
- 官方文件(2.0 預覽版那頁)明寫:沒有型別解析時,要型別的規則「不會跑」;沒提會不會警告,實驗中沒有警告。

FACT:detekt 1.23.8 搭 Kotlin 2.3.21 標準庫時 SuspendFunSwallowedCancellation 不響、搭 2.0.21 會響 [來源:外部] [confirmed:2026-11-04] [查:本機 detekt 1.23.8 對探針檔實跑] [recheck:detekt 升版時]

## 世界解

**A. 既有工具把規則真的跑起來(最便宜)**
- detekt 協程規則集:正式版 7 條,其中多數要型別解析;Android 專案要嘛用 Gradle 外掛的 `detekt<Variant>` 任務(自帶型別),要嘛 CLI 帶 `--classpath` 與 `--jdk-home`(`--jvm-target` 實測不影響)。
- 「規則開了其實沒跑」要用正樣本抓:拿一支埋好錯誤的檔跑,該響沒響就紅。

**B. androidx 函式庫自帶的 lint(Android Lint 層)**
- CoroutineCreationDuringComposition(組建畫面時直接 launch)、FlowOperatorInvokedInComposition、RepeatOnLifecycleWrongUsage 等,隨函式庫附帶,不用另外裝;Android Lint 能輸出 SARIF,可走既有橋接。

**C. 第三方規則包**
- structured-coroutines(Apache-2.0):編譯器外掛、detekt(41 條)、Android Lint(33 條)、IDE 檢查四種形式;抓 Job 傳進 builder、當場 new CoroutineScope、suspend 內 runBlocking、async 結果沒人拿、finally 裡 suspend、長迴圈沒讓出取消點。單一作者、約 165 星、專案約 10 個月,新版要求 Kotlin 2.4。
- Sonar Kotlin 協程 12 條(S6305 公開可變 StateFlow、S6315 Deferred 沒用、S6316 用內建 withTimeout、S6307 main-safe 等),要裝 SonarQube 那套。

**D. 「互不依賴卻串著等」:Kotlin 沒輪子,TS/Dart 有**
- Vercel NO_SERIAL_ASYNC_CALLS、react-doctor server-sequential-independent-await、Dart saropa_lints AvoidSequentialAwaits:連續兩行都在等、第二行沒用到第一行的結果就提醒;刻意保守,寧漏不誤報。Kotlin 版可用 ast-grep 或自訂 detekt 規則照抄這個判準。
- 行動端外呼(Retrofit/OkHttp/Ktor)建立時沒設逾時,同樣可寫成結構比對規則。

**E. 語意問題用測試機械驗(唯一能機械化「該不該並行」的路)**
- kotlinx-coroutines-test 的虛擬時間:假 API 各延遲 1 秒,斷言總共只過 1 秒(串著等會是 2 秒);用測試排程器控制兩個請求誰先回,斷言畫面最後是新資料;清掉 ViewModel 後斷言假 API 收到取消。可做成範本,綁進 `[test:]`。

## 建議順序與落地

1. 先把現有接好(A):落地計劃 [[Projects/detekt協程規則真的在跑_計劃]]。
2. Kotlin 棧補提問:從 Java 棧搬外呼逾時與重試題;加一題「舊回應、重複送出、callback 轉 suspend」。
3. 測試範本(E)與自寫規則(D);第三方規則包(C)先拿一個消費專案試。

REVISIT:2026-12-15 第 2、3 步還沒立案就回來決定做不做,不做寫理由。

## 來源

- detekt 協程規則集:https://detekt.dev/docs/next/rules/coroutines
- detekt 型別解析:https://detekt.dev/docs/gettingstarted/type-resolution
- structured-coroutines:https://klibs.io/project/santimattius/structured-coroutines
- Sonar Kotlin 協程規則:https://community.sonarsource.com/t/the-kotlin-analyzer-prevents-developers-from-doing-mistakes-with-coroutines/47507
- Vercel NO_SERIAL_ASYNC_CALLS:https://vercel.com/docs/conformance/rules/no_serial_async_calls
- react-doctor:https://www.react.doctor/docs/rules/react-doctor/server-sequential-independent-await
- kotlinx-coroutines-test:https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md
- androidx lint 清單:https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html

REVISIT:2026-12-15 實測本工具讀不讀得懂 Android Lint 的 SARIF(B 段要接 androidx 隨附 lint 的前提),讀得懂就把 B 段併進寫法檢查標準的 A 級
