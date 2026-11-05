---
type: project
status: todo
created: 2026-11-04
updated: 2026-11-05
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Issues/推送閘對Android的detekt只記錄不擋]]"
  - "[[Projects/Android的detekt規則說實話_計劃]]"
  - "[[Projects/detekt協程規則真的在跑_計劃]]"
  - "[[Systems/pitfalls-lint-adapter]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/android-e2e-acceptance]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
lands_in:
  - Systems/pitfalls-lint-adapter
  - Systems/linter精選目錄
  - Systems/lint-declaration-health
  - Systems/pitfalls-code-loop
---

# Android的detekt推送前真的擋_計劃

> 白話:Android 專案的 detekt 告警現在推送前從來不擋(見 [[Issues/推送閘對Android的detekt只記錄不擋]])。這案補三樣東西讓它真的擋:①多檔用逗號交給 detekt 的新佔位符;②一支不改專案建置檔的 Gradle 初始化腳本,把型別資訊寫成一個參數檔讓 detekt 指令讀;③推送時順手放一支埋好錯誤的探針檔一起跑,該響的規則沒響就代表型別資訊沒接上,擋下並講怎麼修,不再安靜放行。

PRIOR-ART: ①多檔交給 detekt:detekt 官方文件的提交前掛鉤範例就是把檔名用逗號串起來塞進 `--input`(detekt.dev 的 git-pre-commit-hook 頁,`IFS=,`),社群做法同形(`paste -sd,`);採用,做成明寫的新佔位符,不在替換函式裡偷偷依工具改串法(一條命令裡可能串兩個工具,猜錯會壞另一個)。②型別資訊:detekt 自己的 Gradle 外掛替 Android 變體組 classpath 的寫法是「變體的編譯 classpath(只留存在的)+ bootClasspath(android.jar)+ 專案自己編譯出的類別目錄」(detekt v1.23.8 原始碼 DetektAndroid.kt 的 registerAndroidDetektTask);維護者在 detekt 討論 #6550 說指令列要自己拿 classpath 只能自己寫任務印出來、官方不打算寫進文件。採用同一個組法,改用初始化腳本(`gradlew -I`)實作,不改消費專案的建置檔。官方同頁也警告「部分檔案的指令列跑法,要型別的規則有些不準,CI 要另跑全量」,列入天花板。③探針:正樣本驗證(拿已知會中的樣本跑,沒中就代表檢查器壞了)沿用作廢那案([[Projects/detekt協程規則真的在跑_計劃]])的想法,改成跟真的檢查同一次執行一起跑(不多跑一次 detekt),並解掉那案第一輪審查列的四個判定細節(見〈用詞〉探針一條)。
RETIRE-IF: detekt 正式版在「設了要型別的規則卻沒有型別資訊」時自己報錯或警告(探針就是重工,拆探針);或連續三個月沒有任何消費專案用到 `{LINT_FILES_CSV}`(拆佔位符與探針,文件改回只記錄);或探針擋下的次數裡誤擋(型別資訊其實有接上)多過真擋。

## 用詞

- **基準版、現在版**:新增告警閘把改動前、改動後的檔各抽到一個暫存快照目錄(程式裡叫 base、head),同一條命令在兩邊各跑一次,比對出「現在版才有的告警」。
- **P1、P2**:[[Projects/Android的detekt規則說實話_計劃]] 定的兩則提醒——P1「這條 detekt 命令沒有檔案佔位符,推送時只記錄不擋」,P2「帶了 `{LINT_FILES}` 但多檔時 detekt 拒跑,一樣擋不住」。
- **沒跑到**:新增告警閘既有的分類,一條命令這次沒有產出可比的結果;其中「環境類」(工具沒裝、跑不出結果)自動放行,其他類(時間預算不夠、檔太大)擋。本案新增兩類,都屬擋:`comma-path`(要檢查的檔路徑含逗號)與 `probe-missing`(探針該響的規則沒響,即「型別資訊沒接上」)。擋下訊息現在對非環境類一律寫「因為時間預算沒跑到」,要改成依類別各寫各的原因。
- **逗號佔位符**:宣告命令裡的 `{LINT_FILES_CSV}`。推送前的新增告警檢查、冒煙、風險分級把它換成「這次要檢查的檔、以命令執行目錄(專案根)為準的相對路徑、用逗號串成一個字串、整串一次加 shell 引號」。既有的 `{LINT_FILES}`(每個路徑各自加引號、空白相接)不變。兩個佔位符都由唯一那支替換函式處理;替換函式多收一個「命令執行目錄」參數,逗號佔位符的路徑相對它計算(新增告警閘現在傳給替換函式的是快照目錄裡的絕對路徑,所以這一步要做;冒煙與風險分級本來就是相對路徑)。
- **型別參數檔**:`build/lumos/detekt-typeinfo.args`(相對專案根)。內容是 detekt 指令列參數,一行一個:`--classpath`、組好的 classpath、`--jdk-home`、JDK 路徑、`--jvm-target`、目標版本。宣告命令用 `@build/lumos/detekt-typeinfo.args` 讀它(detekt 1.23.8 會展開 `@檔名`;2026-11-04 本機實測展開後四條要型別的協程規則全響)。
- **初始化腳本**:本 repo 分發的 `configs/detekt/lumos-detekt-typeinfo.init.gradle`(新增),Groovy 寫(初始化腳本編譯時拿不到 Android Gradle 外掛的類別,Kotlin 腳本會編譯失敗;Groovy 動態呼叫不用)。消費專案跑 `./gradlew -I <腳本路徑> lumosDetektTypeinfo` 產生型別參數檔。classpath 照 detekt 自己 Gradle 外掛的組法:每個套了 Android 外掛的模組,取指定變體(預設 debug,可用 `-PlumosDetektVariant=<變體>` 換)的編譯 classpath、bootClasspath、該變體 Kotlin 與 Java 編譯輸出目錄;所有模組聯集成一份、去重、只留存在的路徑。JDK 用跑 Gradle 的那個 JDK。任務先依賴各模組該變體的編譯任務,確保編譯輸出存在。
- **探針**:兩支故意寫錯的 Kotlin 原始碼,當字串常數寫在 lumos 本體裡;推送檢查時寫進這次的暫存目錄(`.lumos/lintbase-<隨機>/probe/`),只加進「現在版」那次 detekt 的輸入,不加進基準版那次。
  - 基本探針(只靠 Kotlin 標準庫與 JDK):觸發 RedundantSuspendModifier(suspend 函式裡沒有任何掛起呼叫)與 SleepInsteadOfDelay(suspend 函式裡呼叫 Thread.sleep,要 `--jdk-home`)。2026-11-04 實測:沒型別資訊兩條都不響;只給標準庫加 JDK 兩條都響。
  - 協程探針(要 kotlinx.coroutines 在 classpath 上):觸發 InjectDispatcher(寫死 Dispatchers.IO)與 SuspendFunWithFlowReturnType(回傳 Flow 的函式標了 suspend)。實測只給標準庫時兩條不響、加上協程 jar 兩條都響。
  - 比對規則時去掉 SARIF 規則代號的 `detekt.<規則集>.` 前綴,只比規則名(作廢那案 r1 邊界席第 10 點)。
  - 「這條命令要驗探針」的判定:命令被 [[Projects/Android的detekt規則說實話_計劃]] 那套字面判定認成 detekt 指令列,而且帶逗號佔位符。Gradle 任務接法不驗(它沒有佔位符,本來就只記錄)。
  - 協程探針只在「這次要檢查的現在版檔裡,有任何一支內文含 `kotlinx.coroutines` 字樣」時才要求(沒用協程函式庫的專案不會被誤判成沒接上;作廢那案 r1 接手席)。
  - 探針那次 detekt 沒產出可解析的結果時,沿用既有判定:整條命令記成「跑不出結果」;這種情況不再判探針(作廢那案 r1 邊界席第 2 點的第三種狀態)。

## 範圍

1. **逗號佔位符**:替換函式多認 `{LINT_FILES_CSV}`;程式裡每一處「命令有沒有檔案佔位符」的判斷改成兩種都認(新增告警檢查要不要跑、執行入口「佔位符沒換掉就不跑」、冒煙換檔、規則索引的形狀檢查、說實話那套判定的「推送時接得住」)。不新開第二支替換函式。「全程式只准一處替換佔位符」那支守衛測試(現在只認 `{LINT_FILES}` 字面與它的常數名,只准一處替換)要一起改:兩種佔位符都認,准許的替換處仍只在那一支函式裡(兩個佔位符各一處)。寫死 `{LINT_FILES}` 的提示文字(健檢的「接得住」說明、新增告警閘的沒跑原因、規則索引的形狀問題訊息)改成兩種都提。
2. **含逗號的路徑**:某支要檢查的檔的相對路徑含逗號時,detekt 會把它拆成兩個不存在的路徑而整條拒跑(2026-11-04 實測 rc=1、不產結果)。這條命令這次不跑,記成新的一類「沒跑到」(不是環境問題,不自動放行),擋下訊息點名那支檔、說明改檔名或用既有的整道關閉環境變數 `LUMOS_SKIP_LINT_NEW=1` 推這一次。
3. **探針**(放行讀取點是新加的:既有放行紀錄只在比對告警與檔太大兩處讀,探針缺規則不是一條告警,要另加一處讀放行紀錄、鍵是 `detekt-probe:<規則名>`):新增告警檢查對「要驗探針」的命令,在現在版那次把探針檔加進輸入;跑完把探針檔的結果從告警清單裡拿掉(不進差集、不會被當成新增告警),再看該響的規則有沒有響。少任何一條 → 這條命令記成「型別資訊沒接上」的「沒跑到」,擋下;訊息點名少了哪幾條規則、給重新產生型別參數檔的指令、說明若是自己的 detekt 設定刻意關了那條就用既有放行指令放行。放行指紋綁「探針+規則名」,用既有的 `lumos lint-waive`,不加新指令。
4. **冒煙**:`lumos lint-check --smoke` 換逗號佔位符時走同一支替換函式;對「要驗探針」的命令同樣加探針、同樣判,少規則就記成問題(退出碼 1)。
5. **初始化腳本**:新增上面那支 Groovy 腳本,任務名 `lumosDetektTypeinfo`。
6. **說實話那套提醒跟著改**:
   - 帶逗號佔位符的 detekt 指令列算「推送時接得住」,不再印 P1、P2。「接得住」的共用判斷改成兩種佔位符都認之後,P2 那一則要改成只看舊 `{LINT_FILES}`,否則逗號佔位符會誤印 P2。
   - 帶舊 `{LINT_FILES}` 的 detekt 指令列,P2 的文字改成「改用 `{LINT_FILES_CSV}`」。
   - 新增一條提醒:命令用 `@<路徑>` 讀參數檔、而那個檔(相對專案根)不存在 → 提醒先跑初始化腳本,附指令。只看檔在不在,不讀內容。
   - 逗號佔位符被包在引號裡(`"{LINT_FILES_CSV}"` 或 `'{LINT_FILES_CSV}'`)→ lint-check 記成格式問題(替換時已經加了一層引號,再包一層 detekt 會收到帶引號字元的路徑)。舊佔位符不追溯。
7. **文件**:[[Systems/linter精選目錄]] 的 detekt 標準接法樣板改成 `detekt @build/lumos/detekt-typeinfo.args --input {LINT_FILES_CSV} --build-upon-default-config --config <共用設定> --report sarif:{LINT_SARIF_OUT}`,加產生型別參數檔的步驟;共用設定 android.yml 開頭的講實話段改寫;kotlin-idioms 慣例文件〈型別資訊〉一節改寫;[[Issues/推送閘對Android的detekt只記錄不擋]] 推上去後結案。

**不做**:
- 不在替換函式裡依工具名自動決定串法(理由見 PRIOR-ART ①)。
- 不替 Gradle 任務接法(`detekt<變體>`)接新增告警檢查:它要整個專案能建置,快照目錄裡只有改到的檔,跑不起來。
- 不偵測型別參數檔過期(依賴改了但沒重產):只會讓新依賴裡的呼叫判不出型別,核心的標準庫與協程探針照樣驗得到;放進回頭條件。
- 不改任何消費專案的檔;不改既有 `{LINT_FILES}` 的行為。
- 不在風險分級那條路跑探針(它不擋推送,只算分級)。

## 實務隱患

- **探針規則被消費專案自己的設定關掉**:會被判成型別資訊沒接上而擋。訊息點名規則並給放行指令;放行綁規則名,關一次就好。
- **只檢查改到的檔,型別解析看不到專案其他原始碼**:改到的檔呼叫專案裡別支檔定義的 suspend 函式時,detekt 要從 classpath 找那個符號。初始化腳本把各模組的編譯輸出目錄放進 classpath 就是為了這個;編譯輸出是上次建置的版本,同一次改動新加的符號解析不到,相關規則會漏報。這是天花板第 1 條。
- **多模組聯集 classpath**:不同模組依賴同一套件的不同版本時,聯集會同時放進兩版,detekt 取先出現那版。只影響型別判斷的細節,不會讓規則整個不跑。
- **基準版與現在版用同一份型別參數檔**:兩次都用現在的依賴解析;跟既有「設定檔一律取現在版」同一個原則(同一份規則比兩次)。
- **探針多花的時間**:探針跟真的檢查同一次執行,只多分析兩支小檔,不多啟動一次 detekt。detekt 帶型別資訊時啟動與載入 classpath 本身較慢,整條命令仍受既有的時間預算管。
- **路徑含逗號**:見範圍第 2 條;用相對路徑是為了不讓專案所在目錄的名字含逗號就整個拒跑。
- **舊否決對照(2026-11-05 跑 `lumos rejections` 按概念比對)**:另一條相關否決是 [[Systems/lint-declaration-health]] 不在健檢裡「冒煙探針實跑驗規則」,當時就寫明改到本案做,同向不衝突。
- **舊否決對照**:[[Systems/android-e2e-acceptance]] 否決過「把值加 shell 引號換進使用者指令的佔位符」,因為使用者可能已經自己包了引號、疊兩層會壞。既有 `{LINT_FILES}` 本來就由替換函式加引號;新佔位符照同一個慣例,疊兩層的風險用範圍第 6 條最後一點的格式檢查擋在宣告階段。
- **資安**:不碰登入、權限、付款、個資、對外呼叫。初始化腳本只讀建置設定、寫一個本機檔;探針是寫死的常數字串。
- **跟主計劃改同一道閘**:[[Projects/Android協程與API寫法機械檢查標準_計劃]] 也擴充新增告警閘(多一種終點「工作樹」)。兩案都改同一支判定函式;本案先做(改的是替換與探針,範圍小),主計劃的工作樹終點在本案合進主線後再接,工作樹檢查對逗號佔位符命令同樣加探針。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只在本機跑 detekt 與 Gradle,不送資料出去
- 已排除:不可逆:新增佔位符與新檔,退提交即回原狀;消費專案留下的型別參數檔無人讀、無害
- 守衛面:改推送前的新增告警閘,屬守衛面,走完整設計審

## 驗收條款

- [S1] 當命令含 `{LINT_FILES_CSV}`、檔清單是 `a/X.kt` 與 `b/Y.kt` 時,替換函式應 換成一個加了引號的參數 `a/X.kt,b/Y.kt`;同一條命令同時含 `{LINT_FILES}` 時 應 兩個都換、各照各的串法;檔清單空時 應 原樣回傳 [test:t_lint_files_csv_substitution]
- [S2] 當命令只含 `{LINT_FILES_CSV}` 時,新增告警檢查、執行入口、冒煙、風險分級、說實話判定 應 都把它當成有檔案佔位符;執行入口收到沒換掉的 `{LINT_FILES_CSV}` 時 應 不執行並回「沒跑」 [test:t_lint_files_csv_recognized_everywhere]
- [S3] 當要檢查的檔裡有一支相對路徑含逗號時,新增告警檢查 應 不跑那條逗號佔位符命令、把它記成非環境類的沒跑到並擋下(閘設成擋的時候),訊息點名那支檔;同一次的其他命令照跑 [test:t_lint_new_csv_comma_path_blocks]
- [S4] 當一條 detekt 指令列帶逗號佔位符、基準版沒有 GlobalScope 裸用而現在版新增一處,且探針規則都響時,新增告警檢查 應 擋下那一條新增告警,而且探針檔產生的任何告警 應 不出現在新增清單裡;基準版已有的同一處 應 不擋 [test:t_lint_new_detekt_probe_passes_and_blocks_new]
- [S5] 當探針結果缺 RedundantSuspendModifier 或 SleepInsteadOfDelay 時,新增告警檢查 應 把那條命令記成型別資訊沒接上而擋下,訊息點名缺的規則、印產生型別參數檔的指令與放行指令;用那行放行指令放行後再跑 應 不再因為那條規則擋 [test:t_lint_new_detekt_probe_missing_blocks]
- [S6] 當這次現在版的檔都沒有 `kotlinx.coroutines` 字樣時,缺 InjectDispatcher 或 SuspendFunWithFlowReturnType 應 不擋;有任何一支含這個字樣時缺其中一條 應 擋 [test:t_lint_new_detekt_probe_coroutines_conditional]
- [S7] 當命令不是 detekt 指令列(含 Gradle 任務接法)或只帶舊 `{LINT_FILES}` 時,新增告警檢查 應 不加探針、行為跟改動前一樣;基準版那次的輸入 應 從不含探針檔 [test:t_lint_new_detekt_probe_scope]
- [S8] 當 `lumos lint-check --smoke` 遇到帶逗號佔位符的 detekt 指令列時,應 用專案裡的 kt 檔換成逗號串、加探針跑,缺基本探針規則 應 記成問題退出碼 1 並點名規則,全響 應 印一行探針確認規則有在跑 [test:t_lintcheck_smoke_detekt_csv_probe]
- [S9] 當 detekt 指令列帶逗號佔位符時,`lumos lint-check` 與健檢 應 不印 P1、P2;只帶舊 `{LINT_FILES}` 時 P2 的文字 應 指向 `{LINT_FILES_CSV}`;命令用 `@<路徑>` 而那個檔不存在時 應 印產生型別參數檔的提醒;逗號佔位符被引號包住時 lint-check 應 記成格式問題退出碼 1 [test:t_lint_detekt_advice_csv_and_argfile]
- [S10] 當本機裝了 detekt 1.23.8 時,用真的 detekt、共用 Android 設定、只給標準庫加 JDK 的型別參數檔,對一次改了兩支 kt 檔的提交跑新增告警檢查,應 擋下新增的 GlobalScope 裸用、探針判定通過;不給型別參數檔時 應 因型別資訊沒接上而擋;沒裝 detekt 時測試印略過 [test:t_lint_new_detekt_real_two_files]
- [S11] 當在一個真的 Android 專案(多模組、有 Compose 與協程)跑 `./gradlew -I <初始化腳本> lumosDetektTypeinfo` 時,應 產出型別參數檔,用它跑 detekt 時基本探針與協程探針四條規則 應 全響,且專案的建置檔 應 一字未改 [manual:在本機 Android 專案的乾淨複本上跑初始化腳本,記下產出的參數檔行數、探針四條規則響不響、git status 為空]

## 回退

退回本案的提交即可:逗號佔位符不再被認得(用了它的宣告回到「沒有檔案佔位符」→只記錄不擋,跟現在一樣),探針與新的一類「沒跑到」消失,說實話那套提醒回到現在的文字。初始化腳本是新檔,退回後消費專案留著的型別參數檔沒人讀、無害。沒有寫入任何消費專案的版控檔;探針寫在每次跑完就刪的暫存目錄裡。

## 天花板

1. 只檢查改到的檔:專案自己的符號靠上次建置的編譯輸出解析,同一次改動新加的符號解析不到;detekt 官方也說部分檔案的跑法有些要型別的規則不準。完整的型別檢查仍要靠 CI 跑全量的 Gradle 任務。
2. 探針證明「型別資訊夠讓標準庫與協程那幾條規則跑」,不證明 classpath 齊全(少一個不相干的套件探針照樣過)。
3. 型別參數檔過期不偵測。

REVISIT:2027-02-01 看消費專案擋下紀錄裡「型別資訊沒接上」那類有幾次是型別參數檔過期造成的;超過兩次就補過期偵測(依賴宣告檔內容的雜湊寫進參數檔旁,推送時比對)。
REVISIT:2027-03-01 查 detekt 2.0 出正式版沒;出了就驗 2.0 的 `--input` 是否仍只收逗號、`@參數檔` 是否照舊展開,並把探針改用 2.0 的規則名。
