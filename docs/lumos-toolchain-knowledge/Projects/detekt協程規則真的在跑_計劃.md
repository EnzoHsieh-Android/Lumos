---
type: project
status: superseded
created: 2026-11-04
updated: 2026-11-04
tags:
  - type/project
  - status/superseded
  - scope/stack-knowledge
lands_in:
  - Systems/lint-declaration-health
  - Systems/linter精選目錄
related:
  - "[[Projects/Android協程與API協同機械審_調研]]"
  - "[[Systems/lint-declaration-health]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Projects/Android的detekt規則說實話_計劃]]"
---
# detekt協程規則真的在跑_計劃

> **已作廢(2026-11-04)**:設計審第一輪四席發現推送前的新增告警檢查對 Android detekt 只記錄不擋、Android 專案用 detekt 指令列帶 classpath 走不通,冒煙探針修不到真正的洞。使用者裁定拆兩案:[[Projects/Android的detekt規則說實話_計劃]](先說實話)與 [[Projects/Android的detekt推送前真的擋_計劃]](讓它真的擋)。以下是當時的設計,不是現況;審查卷證在 governance/review-reports 底下同名資料夾。

> 白話:共用的 detekt 設定特地開了幾條協程規則,但照工具教的接法跑,detekt 拿不到型別資訊,那些規則就安靜地不跑(不報錯、不警告)。這個計劃讓「規則有沒有真的在跑」被機械驗出來:冒煙時拿一支埋好錯誤的探針檔跑一次,該響沒響就算宣告有問題;平常健檢看到指令沒帶型別參數就先提醒。順手把設定補齊、把文件裡寫錯的規則名改掉。出身與實驗數據見 [[Projects/Android協程與API協同機械審_調研]]。

PRIOR-ART: ①正樣本驗證(拿已知會中的樣本跑,沒中就代表檢查器壞了)是 lint 界與本 repo 既有的做法——[[Projects/社群規則第二批_計劃]] 的自寫規則正樣本驗證、[[Systems/lint-declaration-health]] 的冒煙層都是同一形狀,本案只是把冒煙從「有沒有產出 SARIF」往下多驗一層「該響的規則有沒有響」。②探針內容照 detekt 官方協程規則文件的違規範例寫。③「靜態看指令字面先提醒」用健檢 F 段既有「有 eslint 設定但沒接」那則提醒的同一個形狀(提醒函式帶空清單:不計問題、不讓 CI 變紅);那個形狀目前只用在「沒宣告」那一支,本案是在 F 段新加一個判斷,不是改既有分支。不新建機制。
RETIRE-IF: detekt 本身在設定了需要型別的規則卻沒有型別資訊時會報錯或警告(那時探針就是重工);或連續三個月沒有任何消費專案用 detekt 指令列宣告(都改走 Gradle 任務,探針套不上)。

## 用詞

- **型別資訊/型別參數**:detekt 指令列的 `--classpath`(或 `-cp`)、`--jvm-target`、`--jdk-home` 三個參數。detekt 很多規則要知道每個呼叫的型別才判得了,沒給就不跑。
- **探針**:一小段故意寫錯的 Kotlin 原始碼,當字串常數寫在 lumos 本體裡;冒煙時寫進一個暫存目錄當 detekt 的輸入,跑完刪掉。不另外附檔,所以消費專案不用多裝任何東西。
- **探針驗的五條**(都是 detekt 1.23.8 正式版的協程規則):GlobalCoroutineUsage(GlobalScope 裸用,不用型別資訊,用來確認共用設定有被讀到)、InjectDispatcher(Dispatcher 寫死)、SleepInsteadOfDelay(協程裡用 Thread.sleep,要 JDK 位置)、SuspendFunWithFlowReturnType(回傳 Flow 卻標 suspend)、SuspendFunWithCoroutineScopeReceiver(suspend 函式又掛在 CoroutineScope 上,本案補開)。後四條要型別資訊。
- **吞取消訊號**:規則 SuspendFunSwallowedCancellation(在 runCatching 裡呼叫 suspend 函式)。
- **共用 Android 設定**:本 repo 分發的 detekt 設定檔,家是 [[Systems/linter精選目錄]];指令裡出現它的檔名路徑(結尾是 configs 底下 detekt 資料夾的 android.yml)就算引用。

## 範圍

- 冒煙(`lumos lint-check --smoke`)多驗一層:kt 命令是 detekt 指令列、引用共用 Android 設定、帶 `--input`(或 `-i`)時,把那個參數的值(連同外面的引號)整段換成探針暫存目錄再跑一次,比對探針五條有沒有響。這段換參數的程式是新寫的,既有冒煙只會換 `{LINT_FILES}` 佔位符。
- 靜態提醒:任何 kt 的 detekt 指令列(不限引用共用設定,因為 detekt 預設開的 InjectDispatcher 等幾條同樣要型別資訊)沒帶 `--classpath`/`-cp`,lint-check 與健檢 F 段都印一段提醒;不改退出碼、不計入健檢問題。健檢那段放在 F 段既有分支之後,只要宣告讀得出來(合法 JSON)就判,不管格式有沒有問題。
- 共用 detekt 設定補開兩條:SuspendFunWithCoroutineScopeReceiver,以及 ForbiddenMethodCall 只禁 collectAsState(收畫面狀態要用 collectAsStateWithLifecycle);設定開頭的用法改成帶型別參數的標準接法。
- 文件:[[Systems/linter精選目錄]] 的標準接法樣板改帶型別參數;kotlin-idioms 的 R12、機檢接線段改正(CoroutineLaunchedInTestWithoutRunTest 在 1.23.8 不存在、寫進設定會讓 detekt 整個拒跑;runBlocking 不全面禁;吞取消訊號的版本限制)。

**不做**:不改新增告警閘與風險分級呼叫 linter 的程式(探針只在冒煙跑,不進每次推送);不替 Gradle 任務接法做探針(沒有 `--input` 可換);不碰任何消費專案的宣告;不加 runBlocking 全面禁用(OkHttp Authenticator 這類同步介面裡橋接 suspend 是正當用法,ForbiddenMethodCall 分不出在不在 suspend 裡);探針不驗 collectAsState(要消費專案的型別資訊裡有 Compose runtime,沒用 Compose 的 Android 專案會被誤判成「沒在跑」)。

## 實務隱患

- 消費專案若自己的設定刻意關掉某條探針規則,探針會判成「沒在跑」。訊息要講清楚缺的是哪條,讓人判斷是刻意關的還是型別資訊沒給。
- 「吞取消訊號」那條在較新的 Kotlin 標準庫下怎樣都不響(detekt 1.23.8 版本限制),不能算宣告錯,只能提醒,否則用 Kotlin 2.3 的專案會永遠紅。
- 指令字串是 shell 字串,換 `--input` 要處理引號與 `--input=x` 寫法;換不到就照實說「探針套不上」、不記成問題(跟 S3 同一件事),不能假裝驗過。
- 共用設定補開的兩條會影響消費專案每次推送的新增告警檢查:那道檢查在合併基準與這次改動上用同一份設定各跑一次、只擋新增的告警,所以既有的寫法不會一夕變紅;但之後新寫的 collectAsState 或掛在 CoroutineScope 上的 suspend 函式會被擋。這是本案要的效果。現在沒帶型別資訊的消費專案,這兩條本來就不會響,在它補上型別參數之前沒有差別。
- 舊否決對照:[[Systems/android-e2e-acceptance]] 否決過「把值加 shell 引號換進使用者指令的佔位符」,因為使用者可能已經自己包了引號、疊兩層會壞。本案不是換佔位符,是把使用者原本的 `--input 值` 整段(連同值外面的引號)換成探針目錄,只有一層引號,不會疊。

## 驗收條款

- [S1] 當 kt 命令是 detekt 指令列、引用共用 Android 設定、帶 `--input`,執行 `lumos lint-check --smoke` 時,應 另外把輸入換成內建探針檔跑一次;探針結果缺 GlobalCoroutineUsage、InjectDispatcher、SleepInsteadOfDelay、SuspendFunWithFlowReturnType、SuspendFunWithCoroutineScopeReceiver 任一條時 應 記成問題、退出碼 1,訊息點名缺的規則並給補型別參數的修法;五條都響時 應 退出碼 0 並印一行探針確認規則有在跑 [test:t_lintcheck_smoke_detekt_probe]
- [S2] 當探針五條都響、只缺吞取消訊號那條時,`lumos lint-check --smoke` 應 退出碼 0 並印提醒,說明是 detekt 1.23.8 搭較新 Kotlin 標準庫的版本限制 [test:t_lintcheck_smoke_detekt_probe_cancel_note]
- [S3] 當 detekt 指令列宣告沒有 `--input` 可換時,`lumos lint-check --smoke` 應 印「這條沒辦法用探針驗」的提醒、不記成問題;命令不是 detekt 或沒引用共用設定時 應 完全不跑探針 [test:t_lintcheck_smoke_detekt_probe_skips]
- [S4] 當 kt 命令是 detekt 指令列且沒帶 `--classpath` 或 `-cp` 時,`lumos lint-check`(不帶冒煙)應 印型別資訊提醒而退出碼照舊,`lumos doctor` 的 linter 宣告段 應 印同一段提醒且不計入問題;命令走 Gradle 或已帶 classpath 時兩處都 應 不提醒 [test:t_lintcheck_detekt_classpath_reminder]
- [S5] 當用 detekt 1.23.8 搭共用 Android 設定、帶齊型別參數跑探針時,設定驗證應通過,suspend 函式掛 CoroutineScope 與 collectAsState 兩條應各自響 [manual:2026-11-04 本機 detekt 1.23.8 實跑,兩條皆響、設定驗證通過;做法記在調研筆記]

## 回退

退回本案的提交即可:冒煙回到只驗「有沒有產出可解析的 SARIF」,lint-check 與健檢 F 段不再印型別資訊提醒(健檢本來就不跑 linter,只驗宣告格式);共用設定退回後兩條規則回到關閉。沒有寫入任何消費專案的檔,探針用的暫存目錄跑完即刪。

## 天花板

1. 探針只證明「型別資訊夠讓這幾條規則跑」,不證明消費專案自己的程式碼都被分析到(`--input` 指錯目錄照樣過)。
2. Gradle 任務接法驗不到。

REVISIT:2026-12-15 看消費專案有沒有改走 Gradle 任務接法;有就評估 Gradle 接法要怎麼驗規則有在跑。 [closed:2026-11-04 本案作廢,Gradle 接法併入推送前真的擋那案的設計]
REVISIT:2027-03-01 查 detekt 2.0 出正式版沒;出了就重跑探針確認吞取消訊號那條恢復,並補開 2.0 才有的兩條(finally 裡呼叫 suspend、測試沒包 runTest)。 [closed:2026-11-04 本案作廢,搬到說實話那案]
