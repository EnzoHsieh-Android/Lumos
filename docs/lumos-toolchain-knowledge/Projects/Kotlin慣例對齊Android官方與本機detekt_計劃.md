---
type: project
status: doing
created: 2026-11-01
updated: 2026-11-01
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/效能檢核目錄
  - Systems/linter精選目錄
related:
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Projects/Android目標架構開關與舊檔畢業_計劃]]"
  - "[[Projects/kotlin慣例skill_計劃]]"
---
# Kotlin慣例對齊Android官方與本機detekt_計劃

> 白話:Kotlin 慣例手冊與 Kotlin 審查題有三處跟 Android 官方最新建議或本機 detekt 實際行為對不上——教人用 SharedFlow 送一次性事件(官方明講不要)、沒提 ViewModel 收 Context 與程序被系統殺掉後的狀態還原、設定範例照抄會讓 detekt 1.23 整次跑不起來,另有兩條規則在命令列跑法下根本不會報。這份計劃把手冊、審查題與效能檢核目錄改成跟官方與實測一致。

## 問題與最小解

立案:Enzo 2026-11-01 要求「DDD 加 Android MVVM 架構上網搜最佳解,看現行機制可補全、優化或更彈性的作法」,看完對照後說「開始優化」。Android 的分層與 DDD 規則已由 [[Projects/Android目標架構開關與舊檔畢業_計劃]] 的產生器處理,這份只處理那份沒碰的通用層:慣例手冊、審查題、detekt 接線說明。

現況(2026-11-01 對照主線 8b1a1cfb0):
- Flow 審查題與效能檢核目錄同一列寫「狀態=StateFlow/事件=SharedFlow/單消費=Channel」。官方建議頁(2026-10-05 更新)把「不要從 ViewModel 送事件給 UI」列為強烈建議;官方 UI 事件頁(2026-05-18 更新)明講不要用 Channel 或其他串流送一次性事件,ViewModel 的事件要化成畫面狀態、畫面處理完回報。SharedFlow 預設沒有收的人時直接丟掉,畫面旋轉那一刻發的提示就不見。
- 慣例手冊沒有「ViewModel 不收 Context、不用 AndroidViewModel」,也沒有程序被系統殺掉後的狀態還原(官方狀態還原頁 2026-10-07 更新);洩漏題問的是反方向(長活物件抓著 ViewModel)。
- 慣例手冊〈機檢接線〉的設定範例開了 `CoroutineLaunchedInTestWithoutRunTest`。2026-11-01 本機 detekt 1.23.8 實測:這條規則不存在,照抄範例整次失敗(退出碼 3、「Property … is misspelled or does not exist」),一條都沒檢查;拿掉那一行就正常跑。
- 同一次實測:照 linter 精選目錄的 detekt 命令列樣板(只給 `--input`)跑,手冊點名的協程規則與共用設定開的三條,只有 `GlobalCoroutineUsage` 會報;`ForbiddenMethodCall`、`InjectDispatcher`、`RedundantSuspendModifier`、`SuspendFunWithFlowReturnType`、`SleepInsteadOfDelay`、`CouldBeSequence`、`SuspendFunSwallowedCancellation` 都零命中、也不出錯。同一份樣本帶上協程與標準庫 jar(`--classpath`)和 `--jdk-home` 之後,除了最後一條都會報;`SuspendFunSwallowedCancellation` 在 1.23.8 只抓 `runCatching` 包 suspend 呼叫,手冊壞例那種 `try/catch(Exception)` 帶齊型別資訊也不報。`ForbiddenImport` 不需型別資訊,抓得到 `runBlocking` 的 import。手冊與共用設定的註解都把這些規則寫成「開了就有守」。
- 手冊自己的回頭條件(2026-10-25 補上核對日期)已過期。

最小解:只改文字與審查題,不改判定邏輯、不改共用 detekt 設定的開關。
- 審查題改措辭不改 id(id 是表態的鍵,見 [[Systems/效能檢核目錄]]〈題目 id 對照〉),觸發字一個都不動——題目什麼時候亮、推送前要不要表態,跟改之前一樣。
- 手冊在 R18 之後加四條(不重排既有條號,既有 finding 引用的條號不錯位),修正機檢接線範例與三條規則的機檢說明,補上核對日期。
- 共用 detekt 設定只補註解,不改開關。

PRIOR-ART: 規則內容借 Android 官方三頁(架構建議頁、UI 事件頁、狀態還原頁)與 Manuel Vivo〈ViewModel: One-off event antipatterns〉;detekt 規則存在與否、預設開關用 `detekt --generate-config` 產的 1.23.8 預設設定逐條比對,型別資訊需求用最小樣本實跑。沒有新機制,全部借用既有的慣例手冊、審查題與效能檢核目錄。
RETIRE-IF: 官方 UI 事件頁改回建議用 Channel 或 SharedFlow 送一次性事件時,撤掉新加的事件條款與審查題那一句 [retire:人裁] [until:2027-11-01]。

## 做法

1. **Flow 審查題與效能檢核目錄那一列**:改成「狀態=StateFlow;ViewModel 給畫面的一次性結果(提示、導覽、錯誤)化成畫面狀態、畫面處理完回報;官方不建議 Channel/SharedFlow 送事件(沒人收時會漏),用了要寫理由;SharedFlow 只用在真的有多個收的人的廣播」,其餘(背壓、repeatOnLifecycle、shareIn 放函式回傳)照留。id 不變。
2. **洩漏審查題**:題目多問「ViewModel 有沒有收 Context/Activity 或繼承 AndroidViewModel(官方建議不要;要資源就移到畫面層或資料層)」。觸發字不動:題目照舊在改動出現 Context、Activity 這類字時亮;只寫 AndroidViewModel 的改動不會因此多亮一題(要加觸發字是改推送前的擋下條件,另開計劃走設計審)。
3. **Kotlin 慣例手冊**:
   - 新增 R19「ViewModel 不往畫面送一次性事件:處理完化成狀態」(壞例 Channel/SharedFlow、好例 userMessage 加 userMessageShown;使用者點擊觸發的導覽由畫面用回呼處理)。
   - 新增 R20「ViewModel 不碰 Context、不繼承 AndroidViewModel」。
   - 新增 R21「程序被系統殺掉:畫面要還原的最小資料放保存狀態,大資料放本機儲存」(SavedStateHandle 只放 ID、查詢字串這類小值;還原後用它從本機儲存重新載入;用開發者選項「不保留活動」測)。
   - 新增 R22「ViewModel 與資料層測試用假實作、直接斷言狀態值」。
   - 審查鏡頭的條號範圍改成 R1–R22。
   - 機檢接線範例拿掉 `CoroutineLaunchedInTestWithoutRunTest`(R12 改寫成「detekt 1.23 系列沒有這條」);R10 的 `SuspendFunSwallowedCancellation`、R12 與 R13 的 `ForbiddenMethodCall` 註明要型別資訊(Gradle 的 detekt 任務帶型別資訊,或命令列帶 `--classpath`),命令列不帶就零命中;R12 與 R13 另給不需型別資訊的 `ForbiddenImport` 寫法(只擋 import,寫完整套件名的呼叫繞得過)。
   - 〈核對邊界〉補 detekt 那部分的核對日期與版本,compose-rules 與 Slack compose-lints 那部分照實寫「未用本機工具核對」,並改寫回頭條件。
4. **共用 detekt 設定**:`SuspendFunSwallowedCancellation` 與 `CouldBeSequence` 兩段註解補「要型別資訊,照用法那行跑零命中」與 1.23.8 只抓 `runCatching` 的限制。開關不動。
5. **圖譜**:效能檢核目錄改 Flow 那一列、kt-flow 對照列,以及吞取消、長鏈兩列的機檢說明;linter 精選目錄的 detekt 標準接法補型別資訊的實測事實(它管共用設定那支檔)。命令列樣板本身不改:Android 的 classpath 要靠 Gradle 組,改用 Gradle 型別解析任務之前要先在消費專案實跑過 SARIF 輸出,這台機器沒有可實跑的專案,回頭條件記在 linter 精選目錄。

## 驗收條款

- [S1] 當讀 Kotlin 的 Flow 審查題與效能檢核目錄的「Channel/Flow 適用性」那一列時,兩處都應要求一次性結果化成畫面狀態,且都不再寫「事件=SharedFlow」或「事件廣播=SharedFlow」。 [test:t_kt_flow_question_events_as_state]
- [S2] 當讀 Kotlin 的洩漏審查題時,題目應問到 ViewModel 收 Context 或繼承 AndroidViewModel,且觸發字清單應跟改之前一字不差。 [test:t_kt_leaks_question_viewmodel_context]
- [S3] 當讀 Kotlin 慣例手冊時,應有一次性事件化成狀態、ViewModel 不碰 Context、程序被殺後的狀態還原、假實作測試四條,且審查鏡頭寫的條號範圍應涵蓋到手冊實際的最後一條。 [test:t_kotlin_idioms_android_official_rules]
- [S4] 當本機有 detekt 時,把慣例手冊〈機檢接線〉的設定範例照抄跑一次,detekt 應真的分析完(退出碼 2)而且範例開的 GlobalCoroutineUsage 抓到樣本那一行;設定壞掉(退出碼 1)或寫了不存在的規則(退出碼 3)都應判失敗;本機沒有 detekt 時印出「沒驗到」。 [test:t_kotlin_idioms_detekt_snippet_runs]
- [S5] 新增四條與改寫的審查題措辭,應逐條對照官方架構建議頁、UI 事件頁、狀態還原頁的原文,不寫官方沒說的限制。 [manual:對照官方三頁原文逐條核對措辭]

## 回退

還原這次提交即可:審查題措辭、手冊四條與接線範例、共用設定的註解、圖譜兩篇的文字、四支新測試。審查題 id 與觸發字都沒變,在途分支的表態不受影響。不碰任何帳本。

## 實務隱患

- 效能:四支測試只讀檔與呼叫一次適用性判定;S4 那支在有 detekt 的機器上多跑一次 detekt(約數秒)。
- 併發:只改文字與一個觸發字,不碰共用狀態。
- 已排除:金流:不碰任何金流或支付資料。
- 已排除:對外送出:不對外寄送任何東西。
- 已排除:不可逆:全部是文字與測試,還原提交即可回退。
- 已排除:守衛面:審查題只改措辭,id 與觸發字不動,不改任何判定與擋下條件;共用 detekt 設定只補註解、開關不動。


## 審計修正紀錄

- 代碼審 r1(standard,單席加架構對齊):S4 那支原本只排除退出碼 3,YAML 壞掉(退出碼 1)照綠,改成斷言退出碼 2 且抓到樣本那一行,S4 條款同步改寫;R22 的官方範例補上 `UnconfinedTestDispatcher(testScheduler)`;手冊新節標明只有 Android 專案適用、每條補依據行;測試守門改用 `_need_src`。沒裝 detekt 時印「沒驗到」而不記成略過那條放行:沿用同檔 dart 真機段的寫法。席報告:`governance/review-reports/code-Kotlin慣例對齊與Android單元測試驗收/`。

REVISIT:2026-12-01 另開計劃決定洩漏審查題要不要多 AndroidViewModel 觸發字(改的是推送前擋下條件,要走設計審)
