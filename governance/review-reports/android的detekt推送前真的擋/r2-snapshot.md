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
- **沒跑到**:新增告警閘既有的分類,一條命令這次沒有產出可比的結果;其中「環境類」(工具沒裝、跑不出結果)自動放行,其他類(時間預算不夠、檔太大)擋。擋下訊息現在對非環境類一律寫「因為時間預算沒跑到」,要改成依類別各寫各的原因。本案新增的類別都屬擋,見下一條。
- **型別宣告命令**:被 [[Projects/Android的detekt規則說實話_計劃]] 那套字面判定認成 detekt 指令列、而且帶逗號佔位符的命令。本案只對這種命令「失敗就擋」——宣告了要型別資訊,就不能因為型別資訊壞了而安靜放行。這種命令的新類別:
  - `typeinfo-missing`:跑之前檢查命令裡每個 `@<路徑>` 參數檔(相對專案根):不存在、是空的、沒有 `--classpath`、classpath 裡有任何一個路徑不存在、或任何一行含空白字元,就不跑、擋下,訊息給重新產生的指令。(席位實測:參數檔不存在、路徑含空白、`--classpath` 後面空行,detekt 都只印用法、不產結果;classpath 指到不存在的 jar 時基本探針照樣過,所以要先查路徑存在。)
  - `typeinfo-broken`:跑了但沒產出結果,而且命令第一個詞找得到執行檔(工具有裝)——例如 `--jvm-target` 超出 detekt 支援範圍。擋下,訊息附 detekt 錯誤輸出的最後幾行。第一個詞找不到執行檔時照舊算環境類、自動放行(工具沒裝)。
  - `timeout`:逾時。一般命令逾時照舊算環境類;型別宣告命令逾時算擋。
  - `separator-path`:要檢查的檔裡有路徑含逗號或分號(detekt 用這兩個字分隔 `--input`,席位實測分號同樣拒跑)。
  - `probe-missing`:探針該響的規則沒響,即「型別資訊沒接上」。
- **逗號佔位符**:宣告命令裡的 `{LINT_FILES_CSV}`。新增告警檢查、冒煙、風險分級把它換成「這次要檢查的檔、用逗號串成一個字串、整串交給 `shlex.quote`」(一般路徑沒有特殊字元時不會多出引號)。既有的 `{LINT_FILES}`(每個路徑各自交給 `shlex.quote`、空白相接)不變。兩個佔位符都由唯一那支替換函式處理;替換函式多收一個選填參數「命令執行目錄」(預設不給,維持既有兩參數的呼叫):給了的時候,逗號佔位符裡的絕對路徑改寫成相對它的路徑,本來就是相對路徑的照原樣(視為已相對專案根)。新增告警閘與規則索引的實跑(`cmd_rule_check`)傳絕對路徑,所以要給這個參數;冒煙與風險分級本來就是相對路徑。
- **分批**:逗號串超過 64 KB 時,新增告警閘把檔清單切成多批各跑一次、合併結果;探針只放第一批。(Linux 單一參數上限 128 KB,大型改名一次動上千支檔就會超過。)
- **型別參數檔**:預設 `build/lumos/detekt-typeinfo.args`(相對 Gradle 根)。內容是 detekt 指令列參數,一行一個:`--classpath`、組好的 classpath、`--jdk-home`、JDK 路徑、`--jvm-target`、目標版本。宣告命令用 `@<相對專案根的路徑>` 讀它(detekt 1.23.8 會展開 `@檔名`;2026-11-04 本機實測展開後四條要型別的協程規則全響)。
- **初始化腳本**:本 repo 分發的 `configs/detekt/lumos-detekt-typeinfo.init.gradle`(新增),Groovy 寫(初始化腳本編譯時拿不到 Android Gradle 外掛的類別,Kotlin 腳本會編譯失敗;Groovy 動態呼叫不用)。放 `configs/detekt/` 不放 `scripts/templates/`:它跟共用設定 `android.yml` 一樣是使用者在自己的命令裡用工具鏈安裝路徑引用的檔,不是複製進專案的範本;家是 [[Systems/linter精選目錄]](那篇的 about_code 已管 `android.yml`)。消費專案跑 `./gradlew -I <腳本路徑> lumosDetektTypeinfo` 產生型別參數檔;任務只註冊在根專案。
  - classpath 照 detekt 自己 Gradle 外掛的組法:每個套了 Android 外掛的模組取指定變體(預設 debug,可用 `-PlumosDetektVariant=<變體>` 換)的編譯 classpath、bootClasspath、該變體 Kotlin 與 Java 編譯輸出目錄;每個純 Kotlin/JVM 模組(`kotlin("jvm")`、`java-library`)取 main 的編譯 classpath 與編譯輸出。所有模組聯集成一份、去重、只留存在的路徑。任務先依賴這些編譯任務。
  - 路徑含空白(例如 Android Studio 內建 JDK、家目錄有空白)時,在 `build/lumos/links/` 建一個不含空白的符號連結指過去,參數檔寫連結(detekt 的參數檔不吃引號,席位實測加雙引號、反斜線都失敗)。
  - JDK 用跑 Gradle 的那個 JDK;`--jvm-target` 取專案設定的 Kotlin/Java 目標版本,夾在 detekt 1.23.8 支援的 1.8 到 22 之間(席位實測 24、25 會讓 detekt 拒跑)。
  - 寫完印出宣告命令該用的 `@<路徑>`(相對 git 根;Gradle 根在子目錄時就帶子目錄前綴)。
  - 支援範圍:Android Gradle 外掛 8.x(用舊的變體介面,跟 detekt 1.23.8 外掛同一套);9.x 要改用新的變體介面,見回頭條件。
- **探針**:兩支故意寫錯的 Kotlin 原始碼檔,放在 `scripts/templates/detekt-probe/`(新增;跟既有 `.sql`、`.sh` 範本一樣把別的語言的內容放成檔,不寫成 lumos 裡的字串常數);推送檢查時複製進這次的暫存目錄(`.lumos/lintbase-<隨機>/probe/`),只加進「現在版」那次 detekt 的輸入,不加進基準版那次。
  - 基本探針(只靠 Kotlin 標準庫與 JDK):觸發 RedundantSuspendModifier 與 SleepInsteadOfDelay(要 `--jdk-home`)。2026-11-04 實測:沒型別資訊兩條都不響;只給標準庫加 JDK 兩條都響。基本探針證明的只是「有給型別參數」,classpath 的真假靠上面 `typeinfo-missing` 的路徑存在檢查。
  - 協程探針(要 kotlinx.coroutines 在 classpath 上):觸發 InjectDispatcher 與 SuspendFunWithFlowReturnType。實測只給標準庫時兩條不響、加上協程 jar 兩條都響。只在「這次要檢查的現在版檔裡,有任何一支內文含 `kotlinx.coroutines` 字樣」時才要求。
  - 探針檔的所有結果(包括 MagicNumber 這類別的規則命中)都從告警清單拿掉,靠路徑落在暫存目錄的 `probe/` 底下認出來;比對規則時去掉 SARIF 規則代號的 `detekt.<規則集>.` 前綴。
  - 放行:鍵跟既有放行指紋同形,是 `sha256("detekt-probe" + 分隔字元 + 規則名)` 取前 16 碼;擋下訊息直接印出這把鍵與 `lumos lint-waive` 指令。訊息也寫明「若是專案自己的 detekt 設定關掉了那條規則或用 excludes 排除了探針路徑,放行即可」。
  - 探針那次 detekt 沒產出可解析的結果時,不再判探針,照上面 `typeinfo-broken`/環境類的規則判。

## 範圍

1. **逗號佔位符**:替換函式多認 `{LINT_FILES_CSV}`;程式裡每一處「命令有沒有檔案佔位符」的判斷改成兩種都認(新增告警檢查要不要跑、執行入口「佔位符沒換掉就不跑」、冒煙換檔、規則索引的形狀檢查與實跑、說實話那套判定的「推送時接得住」)。不新開第二支替換函式。「全程式只准一處替換佔位符」那支守衛測試(白名單制,現在只認 `{LINT_FILES}` 字面與它的常數名)要一起改:兩種佔位符都認,准許的替換處仍只在那一支函式裡(兩個佔位符各一處);新寫的檢查函式(分隔字元、型別宣告判定)若提到新佔位符要列進白名單並寫理由。寫死 `{LINT_FILES}` 的提示文字(健檢的「接得住」說明、新增告警閘的沒跑原因、規則索引的形狀問題訊息)改成兩種都提。
2. **型別宣告命令失敗就擋**:新增告警閘對型別宣告命令照〈用詞〉的五個新類別判;擋下訊息依類別寫原因與修法。`separator-path` 的出口:放行那支檔(鍵同形雜湊,`sha256("detekt-sep-path" + 分隔字元 + 路徑)` 前 16 碼),放行後那支檔不送進 detekt、在結果裡列成沒檢查;或改檔名。不需要用整道關閉。
3. **探針**:新增告警檢查對型別宣告命令,在現在版第一批把探針檔加進輸入;跑完拿掉探針結果,再看該響的規則有沒有響;少任何一條且沒放行 → `probe-missing`,擋下。放行讀取點是新加的(既有放行紀錄只在比對告警與檔太大兩處讀)。
4. **分批**:見〈用詞〉;只對逗號佔位符做。
5. **冒煙**:`lumos lint-check --smoke` 換逗號佔位符時走同一支替換函式,取樣檔時跳過含逗號或分號的路徑;對型別宣告命令同樣先做參數檔檢查、加探針(探針放冒煙自己的暫存目錄 `.lumos/lintbase-smoke-<隨機>/`,跑完刪)、取樣檔含 `kotlinx.coroutines` 時也驗協程探針;任一不過記成問題(退出碼 1)並點名原因。
6. **初始化腳本**:新增上面那支 Groovy 腳本,任務名 `lumosDetektTypeinfo`;登記進 [[Systems/linter精選目錄]] 的 about_code。
7. **說實話那套提醒跟著改**:
   - 帶逗號佔位符的 detekt 指令列算「推送時接得住」,不再印 P1、P2。「接得住」的共用判斷改成兩種佔位符都認之後,P2 那一則要改成只看舊 `{LINT_FILES}`,否則逗號佔位符會誤印 P2。
   - 帶舊 `{LINT_FILES}` 的 detekt 指令列,P2 的文字改成「改用 `{LINT_FILES_CSV}`」。
   - 新增一條提醒:命令用 `@<路徑>` 讀參數檔、而那個檔(相對專案根)不存在 → 提醒先跑初始化腳本,附指令。判定函式多一個選填參數「專案根」,不給時不做這條(維持「只看字面」的既有呼叫與表格測試)。
   - T1 那則的文字(現在寫「Android 專案的依賴散在建置快取,目前沒有現成取法」)改成指向初始化腳本;共用設定 android.yml 開頭講實話段的「接不進推送前檢查」同步改。
   - 逗號佔位符被包在引號裡(`"{LINT_FILES_CSV}"` 或 `'{LINT_FILES_CSV}'`)→ lint-check 記成格式問題。舊佔位符不追溯。
8. **CI 也跑真 detekt**:本 repo 的 CI 加一步,下載釘版本的 detekt-cli 1.23.8 與 kotlinx-coroutines-core-jvm jar(從官方發布處,比對寫死的 sha256,不符就讓那一步失敗),放進快取;S10 在 CI 上因此不略過。
9. **文件**:[[Systems/linter精選目錄]] 的 detekt 標準接法樣板改成 `detekt @build/lumos/detekt-typeinfo.args --input {LINT_FILES_CSV} --build-upon-default-config --config <共用設定> --report sarif:{LINT_SARIF_OUT}`,加產生型別參數檔的步驟(提醒新工作樹與 clean 之後要重跑,否則推送會被 `typeinfo-missing` 擋);kotlin-idioms 慣例文件〈型別資訊〉一節改寫;新類別與放行鍵寫進 [[Systems/pitfalls-code-loop]](新增告警閘本體的說明在那篇);[[Issues/推送閘對Android的detekt只記錄不擋]] 推上去後結案。

**不做**:
- 不在替換函式裡依工具名自動決定串法(理由見 PRIOR-ART ①)。
- 不替 Gradle 任務接法(`detekt<變體>`)接新增告警檢查:它要整個專案能建置,快照目錄裡只有改到的檔,跑不起來。
- 不偵測型別參數檔過期(依賴改了但沒重產):只會讓新依賴裡的呼叫判不出型別;放進回頭條件。路徑不存在(例如依賴升版後舊 jar 被清掉)由 `typeinfo-missing` 擋。
- 不改任何消費專案的檔;不改既有 `{LINT_FILES}` 的行為(含分批:舊佔位符不分批)。
- 不在風險分級那條路跑探針(它不擋推送,只算分級)。

## 實務隱患

- **探針規則被消費專案自己的設定關掉或排除**:會被判成型別資訊沒接上而擋。訊息點名規則、提到設定關掉或 excludes 這兩種可能,並給放行指令;放行綁規則名,一次就好。
- **新工作樹與 clean 之後必擋**:型別參數檔在 `build/` 底下、不進版控,新 clone、新工作樹、`./gradlew clean` 之後都不存在,推送會被 `typeinfo-missing` 擋,訊息給重產指令。這是刻意的:宣告了要型別資訊卻沒有,不能安靜放行(席位兩席獨立抓到原設計在這裡靜默放行)。
- **型別宣告命令逾時改成擋**:帶型別資訊的 detekt 啟動慢、基準版與現在版各跑一次;逾時不再自動放行,訊息教人調 `.lumos/config.json` 的 `lint_new.budget_sec`。
- **只檢查改到的檔,型別解析看不到專案其他原始碼**:改到的檔呼叫專案裡別支檔定義的 suspend 函式時,detekt 要從 classpath 找那個符號。初始化腳本把各模組的編譯輸出目錄放進 classpath 就是為了這個;編譯輸出是上次建置的版本,同一次改動新加的符號解析不到,相關規則會漏報。這是天花板第 1 條。
- **多模組聯集 classpath**:不同模組依賴同一套件的不同版本時,聯集會同時放進兩版,detekt 取先出現那版。只影響型別判斷的細節,不會讓規則整個不跑。
- **基準版與現在版用同一份型別參數檔**:兩次都用現在的依賴解析;跟既有「設定檔一律取現在版」同一個原則(同一份規則比兩次)。
- **探針多花的時間**:探針跟真的檢查同一次執行,只多分析兩支小檔,不多啟動一次 detekt(分批時只放第一批)。
- **路徑含逗號或分號**:見範圍第 2 條;用相對路徑是為了不讓專案所在目錄的名字含逗號就整個拒跑。
- **舊否決對照(2026-11-05 跑 `lumos rejections` 按概念比對)**:另一條相關否決是 [[Systems/lint-declaration-health]] 不在健檢裡「冒煙探針實跑驗規則」,當時就寫明改到本案做,同向不衝突。
- **舊否決對照**:[[Systems/android-e2e-acceptance]] 否決過「把值加 shell 引號換進使用者指令的佔位符」,因為使用者可能已經自己包了引號、疊兩層會壞。既有 `{LINT_FILES}` 本來就由替換函式加引號;新佔位符照同一個慣例,疊兩層的風險用範圍第 7 條最後一點的格式檢查擋在宣告階段。
- **資安**:不碰登入、權限、付款、個資、對外呼叫。初始化腳本只讀建置設定、寫本機檔與符號連結;探針是工具鏈附的固定檔。
- **跟主計劃改同一道閘**:[[Projects/Android協程與API寫法機械檢查標準_計劃]] 也擴充新增告警閘(多一種終點「工作樹」)。兩案都改同一支判定函式;本案先做(改的是替換與探針,範圍小),主計劃的工作樹終點在本案合進主線後再接,工作樹檢查對逗號佔位符命令同樣加探針。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只在本機跑 detekt 與 Gradle,不送資料出去
- 已排除:不可逆:新增佔位符與新檔,退提交即回原狀;消費專案留下的型別參數檔無人讀、無害
- 守衛面:改推送前的新增告警閘,屬守衛面,走完整設計審

## 驗收條款

- [S1] 當命令含 `{LINT_FILES_CSV}`、檔清單是 `a/X.kt` 與 `b/Y.kt` 時,替換函式應 換成 `shlex.quote` 過的一個參數 `a/X.kt,b/Y.kt`;給了命令執行目錄且清單是那個目錄底下的絕對路徑時 應 換成相對路徑;同一條命令同時含 `{LINT_FILES}` 時 應 兩個都換、各照各的串法;檔清單空時 應 原樣回傳;只給兩個參數的既有呼叫 應 行為不變 [test:t_lint_files_csv_substitution]
- [S2] 當命令只含 `{LINT_FILES_CSV}` 時,新增告警檢查、執行入口、冒煙、風險分級、說實話判定 應 都把它當成有檔案佔位符;執行入口收到沒換掉的 `{LINT_FILES_CSV}` 時 應 不執行並回「沒跑」 [test:t_lint_files_csv_recognized_everywhere]
- [S3] 當要檢查的檔裡有一支相對路徑含逗號或分號時,新增告警檢查 應 不跑那條逗號佔位符命令、記成 separator-path 擋下(閘設成擋的時候),訊息點名那支檔與放行鍵;放行那支檔後 應 其他檔照跑、那支列成沒檢查;同一次的其他命令照跑 [test:t_lint_new_csv_comma_path_blocks]
- [S4] 當一條 detekt 指令列帶逗號佔位符、基準版沒有 GlobalScope 裸用而現在版新增一處,且探針規則都響時,新增告警檢查 應 擋下那一條新增告警,而且探針檔產生的任何告警 應 不出現在新增清單裡;基準版已有的同一處 應 不擋 [test:t_lint_new_detekt_probe_passes_and_blocks_new]
- [S5] 當探針結果缺 RedundantSuspendModifier 或 SleepInsteadOfDelay 時,新增告警檢查 應 把那條命令記成型別資訊沒接上而擋下,訊息點名缺的規則、印產生型別參數檔的指令與放行指令;用那行放行指令放行後再跑 應 不再因為那條規則擋 [test:t_lint_new_detekt_probe_missing_blocks]
- [S6] 當這次現在版的檔都沒有 `kotlinx.coroutines` 字樣時,缺 InjectDispatcher 或 SuspendFunWithFlowReturnType 應 不擋;有任何一支含這個字樣時缺其中一條 應 擋 [test:t_lint_new_detekt_probe_coroutines_conditional]
- [S7] 當命令不是 detekt 指令列(含 Gradle 任務接法)或只帶舊 `{LINT_FILES}` 時,新增告警檢查 應 不加探針、行為跟改動前一樣;基準版那次的輸入 應 從不含探針檔 [test:t_lint_new_detekt_probe_scope]
- [S8] 當 `lumos lint-check --smoke` 遇到帶逗號佔位符的 detekt 指令列時,應 取樣時跳過路徑含逗號或分號的檔、用其餘 kt 檔換成逗號串、先做參數檔檢查再加探針跑(探針放冒煙自己的暫存目錄、跑完刪);參數檔檢查不過或缺基本探針規則 應 記成問題退出碼 1 並點名原因;取樣檔含 `kotlinx.coroutines` 而缺協程探針規則 應 同樣記問題;全響 應 印一行探針確認規則有在跑 [test:t_lintcheck_smoke_detekt_csv_probe]
- [S9] 當 detekt 指令列帶逗號佔位符時,`lumos lint-check` 與健檢 應 不印 P1、P2;只帶舊 `{LINT_FILES}` 時 P2 的文字 應 指向 `{LINT_FILES_CSV}`;命令用 `@<路徑>` 而那個檔不存在時 應 印產生型別參數檔的提醒;逗號佔位符被引號包住時 lint-check 應 記成格式問題退出碼 1 [test:t_lint_detekt_advice_csv_and_argfile]
- [S10] 當本機裝了 detekt 1.23.8、而且本機 Gradle 快取找得到 kotlinx-coroutines-core-jvm 的 jar 時,用真的 detekt、共用 Android 設定、標準庫加協程 jar 加 JDK 的型別參數檔,對一次改了兩支 kt 檔(其中一支 import kotlinx.coroutines 並新增一處 GlobalScope 裸用)的提交跑新增告警檢查,應 擋下新增的 GlobalScope 裸用、探針判定通過;參數檔不存在時 應 記成 typeinfo-missing 擋下;兩個前提缺一就印略過(本機);CI 照範圍 8 一定有這兩樣,不略過 [test:t_lint_new_detekt_real_two_files]
- [S11] 當在一個真的 Android 專案(多模組含一個純 Kotlin 模組、有 Compose 與協程、Android Gradle 外掛 8.x)跑 `./gradlew -I <初始化腳本> lumosDetektTypeinfo` 時,應 產出型別參數檔且印出宣告要用的 `@<路徑>`,用它跑 detekt 時基本探針與協程探針四條規則 應 全響,且專案的建置檔 應 一字未改;把 JDK 換成路徑含空白的那份再跑,參數檔 應 改寫成不含空白的符號連結 [manual:在實驗專案複本上跑初始化腳本,記下參數檔行數、探針四條規則響不響、git status 為空;另用 Android Studio 內建 JDK 跑一次看連結]
- [S12] 當型別宣告命令的參數檔不存在、是空的、沒有 `--classpath`、classpath 有不存在的路徑、或某行含空白時,新增告警檢查 應 不跑該命令、記成 typeinfo-missing 擋下並印重產指令;命令跑了沒產出結果而第一個詞找得到執行檔時 應 記成 typeinfo-broken 擋下並附錯誤輸出末幾行;第一個詞找不到執行檔時 應 照舊環境類放行;型別宣告命令逾時 應 擋,一般命令逾時 應 照舊放行 [test:t_lint_new_detekt_typeinfo_fail_closed]
- [S13] 當逗號串超過 64 KB 時,新增告警檢查 應 分批跑、合併結果,探針 應 只在第一批;舊 `{LINT_FILES}` 應 不分批 [test:t_lint_new_csv_batches]

## 回退

退回本案的提交即可:逗號佔位符不再被認得(型別宣告命令失敗就擋的五個類別也一起消失)(用了它的宣告回到「沒有檔案佔位符」→只記錄不擋,跟現在一樣),探針與新的一類「沒跑到」消失,說實話那套提醒回到現在的文字。初始化腳本是新檔,退回後消費專案留著的型別參數檔沒人讀、無害。沒有寫入任何消費專案的版控檔;探針寫在每次跑完就刪的暫存目錄裡。

## 天花板

1. 只檢查改到的檔:專案自己的符號靠上次建置的編譯輸出解析,同一次改動新加的符號解析不到;detekt 官方也說部分檔案的跑法有些要型別的規則不準。完整的型別檢查仍要靠 CI 跑全量的 Gradle 任務。
2. 探針證明「型別資訊夠讓標準庫與協程那幾條規則跑」,路徑存在檢查證明 classpath 裡的檔都在,兩者合起來仍不證明 classpath 齊全(少一個不相干的套件照樣過)。
3. 型別參數檔過期不偵測。

REVISIT:2027-02-01 看消費專案擋下紀錄裡「型別資訊沒接上」那類有幾次是型別參數檔過期造成的;超過兩次就補過期偵測(依賴宣告檔內容的雜湊寫進參數檔旁,推送時比對)。
REVISIT:[when-status:Projects/Android的detekt推送前真的擋_計劃=done][by:2027-04-01] 查 Android Gradle 外掛 9.x 是否已拿掉舊的變體介面;拿掉了就把初始化腳本改用新的變體介面取編譯 classpath,並在 9.x 專案重跑 S11
REVISIT:2027-03-01 查 detekt 2.0 出正式版沒;出了就驗 2.0 的 `--input` 是否仍只收逗號、`@參數檔` 是否照舊展開,並把探針改用 2.0 的規則名。

## 審計修正紀錄

- r1(2026-11-05,四席 sonnet:通才、正確性、邊界、架構對齊):27 條/blocking 10/型別參數檔不存在或壞掉時 detekt 不出結果、被當環境問題靜默放行(三席獨立實測抓到),改成「宣告了要型別資訊的命令失敗就擋」;另補分號、分批、初始化腳本的空白路徑與純 Kotlin 模組;全部 27 條折入(CI 不裝 detekt 那條原想放行,但同輪有 blocker 不能放行,改成 CI 也裝)。
- 卷證:governance/review-reports/android的detekt推送前真的擋/(r1-intake.md 有先查世界與逐條去向)
