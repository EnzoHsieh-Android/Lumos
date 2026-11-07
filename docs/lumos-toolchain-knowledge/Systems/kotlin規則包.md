---
type: system
status: doing
created: 2026-11-05
updated: 2026-11-08
responsibility: 負責 Kotlin/Android 寫法的 ast-grep 規則包(規則、樣本、自我檢查)與型錄 checks-catalog.md 的格式;不負責新增告警閘本身的判定(那在 pitfalls-code-loop)、不負責 detekt 共用設定
aliases: []
about_code:
  - configs/ast-grep/kotlin-android/check.py
  - configs/ast-grep/kotlin-android/sgconfig.yml
  - configs/ast-grep/kotlin-android/sgconfig-hints.yml
  - skills/kotlin-idioms/checks-catalog.md
  - configs/ast-grep/kotlin-android/sgconfig-review.yml
  - skills/kotlin-idioms/test-templates.md
  - configs/ast-grep/kotlin-android/sgconfig-unwired.yml
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:標準寫法的單一來源是型錄 checks-catalog.md,每列要有真的打開讀過的官方出處;查不到的列標(出處不全),引用它的規則依據不足、不准擋人 [出處:2026-11-05 使用者「你的標準、最佳寫法來源要有依據,不要你自己寫」] [因:AI 自己寫的標準寫法會跟官方現況打架(查證時 18 列與官方衝突、DataStore 加密整組已棄用)] [test:t_kotlin_catalog_rows_wired]
  WHY:規則訊息格式「[型錄編號] 錯在哪;改用 <最短修法>」且不超過 120 字,完整寫法用編號查型錄 [出處:[[Projects/Android協程與API寫法機械檢查標準_計劃]] 設計審 r1] [因:新增告警閘解析 SARIF 截 120 字、擋下訊息也印 120 字] [test:t_kotlin_rulepack_messages_cite_catalog]
  PITFALL:只掃測試碼的規則若寫 `**/test/**`,祖先目錄叫 test 時整個反轉;還有測試變體目錄 `src/testDemo` 會被當正式碼 [出處:2026-11-05 設計審 r2 實測、nowinandroid 實測] [根因:ast-grep 的 files/ignores 相對規則設定檔所在目錄、比對完整路徑] [修法:錨在 `**/src/test*/**`、`**/src/androidTest*/**`] [test:t_kotlin_rulepack_samples]
  PITFALL:ast-grep 規則把 follows 與 not.has $A 平行寫在同一層時,$A 還沒綁定就被比對,規則對任何程式都不命中 [出處:2026-11-05 樣本實測 kt-sequential-independent-await 0 命中] [根因:ast-grep 不保證同層條件的執行順序] [修法:用 all 排順序] [test:t_kotlin_rulepack_samples]
  RULE:規則在真專案誤報超過命中的一成就降提示級、搬 rules-unwired/ 或改形狀 [依據:外部] [since:2026-11-05] [retire:人裁] [until:2027-05-05] [confirmed:2026-11-05] [查:Google Tricorder「沒用的告警壓在一成以下」]
  REVISIT:2027-02-05 拿兩個以上新的真 Android 專案再量一次會擋的規則(2026-11-05 只量實驗專案與 nowinandroid 共 30 處命中,多數規則只命中 1–3 處,估不準每條的誤報率)
  SEE:[[Systems/linter精選目錄]] [[Systems/pitfalls-code-loop]]
  PITFALL:規則包測試用 rglob 的第一個檔去改壞,在 Linux 上可能挑到剛放進去的 review-fp 樣本、把它蓋掉,兩條改壞驗證跟著失效(macOS 綠、CI 紅) [出處:2026-11-05 PR #158 合併後主線 CI] [根因:目錄列舉順序依檔案系統而定,APFS 恰好照名稱排、ext4 不是] [修法:照檔名挑或整個目錄都改,不用 next(rglob)] [test:t_kotlin_rulepack_samples]
  WHY:型錄〈情境決策表〉加「證據樣式」欄(主與例外兩段,各是(無)或一到三條正規式,照那一列標準寫法與不適用時的字面特徵推,不另立寫法);格式檢查改依表頭名稱取欄,另驗證據樣式能編譯、條數對、停用列的觸發字與證據樣式都是(無),列編號連號照舊 [出處:2026-11-06 [[Projects/Android寫法語意情境表態與盲判_計劃]] 範圍 1] [因:推送前情境題要拿樣式核表態指的那一行] [test:t_kt_catalog_evidence_patterns]
  WHY:決策表的讀法只有 check.py 的 dt_table/dt_row 一套(依表頭取欄、停用列不讀觸發字與證據樣式、標了換列的列例外一定要是(無)),scripts/lumos 用 importlib 借用;換列的列認「不適用時」格子裡出現的(換列)標記(格子任何位置都算),不從「見下一列」這類中文用語推 [出處:代碼審 code-android情境題與表態對程式 r1 D7、D10] [因:原本 lumos 與 check.py 各寫一套讀表、必有欄已經分歧(6 欄對 8 欄),換列靠中文字樣推、改個說法就悄悄變成可選例外] [test:t_kt_situation_catalog_single_reader]
  WHY:每列證據樣式附正例與反例(samples/situation/<列編號>.kt.txt,副檔名不是 .kt 免得推送閘把教材當產品碼),自檢經 scripts/lumos 真的切段與核對程式跑:正例要有一行對得上、反例要每一行都對不上(推送前對不上只提醒,自測守的是樣式本身沒壞,代碼審 r2)、樣本要切得出含那一列的段,反例要碰得到樣式真正在管的地方(順序、型別參數,r2 邊界 F12);壞寫法跟標準寫法只差在語意時那一段寫(無)交盲判 [出處:代碼審 r1 D1;ast-grep test 的 valid/invalid https://ast-grep.github.io/guide/test-rule.html ;Semgrep 的 ok/ruleid https://docs.semgrep.dev/writing-rules/testing-rules ] [因:人逐列寫的樣式在 56 列裡有 9 列擋掉型錄自己的標準寫法或放過對應的壞寫法] [不選:靠人逐列看] [test:t_kt_situation_evidence_samples]
  WHY:自檢程式的 dt_table 讀表那一輪順手帶出處(每列多 source 來源格、refs 展開後的網址、check_refs 對應檢查在型錄主表的名稱與來源與網址,縮寫照〈來源縮寫〉表展開;縮寫表讀法 _abbr_table 與比對 _abbr_hit 跟 catalog_problems 共用一套;縮寫表那兩支檔內輔助用底線開頭(代碼審 code-android情境題盲判 r2 戊);情境證據樣本的 situation_dir、situation_samples、load_lumos 沒加底線),lumos 從列上取出處給盲判材料;主表或縮寫表找不到時那幾格留空不報錯(讀得懂讀不懂歸 dt_table 與 catalog_problems) [出處:2026-11-06 [[Projects/Android寫法語意情境表態與盲判_計劃]] 範圍 4;使用者 2026-11-05 第 3 要點(來源與依據在語意盲判時輔助判別)] [因:讀表只留一套,出處也從同一輪讀(代碼審 code-android情境題盲判 r1 架構對齊 F6:原本另有 dt_sources 再走一輪決策表、縮寫比對的正規式寫了三處)] [不選:lumos 自己再寫一套讀主表;另一支 dt_sources 再走一輪] [test:t_kt_catalog_sources_in_rows] [test:t_blind_judge_template_excludes_dispositions] [test:t_kt_catalog_private_helpers]
  WHY:型錄第四批通電批次照固定口徑判(切段、認規則碼、排除待查、預設關、相近、opt-in 與官方預設關的六條),由型錄自檢 check.py 的 batch4_expected_tags 逐列重算比對(代碼審 r1 架構席:口徑只住一處) [出處:2026-11-06 Projects/Android現成檢查接上CI與推送前_計劃 設計審 r1] [因:兩席指出 compose-rules 預設關的三條會被標成已接電,實際沒在跑] [不選:一次性腳本改完就算(沒有守衛,下次改型錄就漂)] [test:t_kt_catalog_batch4_wiring]
  WHY:型錄 C 列的行為測試範本放 skills/kotlin-idioms/test-templates.md,型錄通電批次欄寫「行為測試或正向約束=範本 T<n>」指過去,自我檢查 template_problems 只驗那一節存在(範本內容對不對靠實驗與驗證紀錄) [出處:[[Projects/Android行為測試範本與架構測試_計劃]] 設計審 r1] [因:沿用既有欄位,不另造認領語法;範本紅綠要 Gradle 才跑得出,本 repo CI 不跑 Gradle] [不選:check.py --lab 產生實驗專案(自檢是唯讀職責)] [test:t_kotlin_test_templates_sections]
  PITFALL:Turbine 自己的檢查(awaitComplete、awaitError、expectNoEvents、區塊結束的 Unconsumed events)失敗丟 app.cash.turbine.TurbineAssertionError,收證工具 assertion_failure 照型別名判、不算斷言失敗,範本照抄會讓壞寫法的紅不被收證認 [出處:2026-11-06 範本紅綠矩陣實跑 T0 兩格] [根因:assertion_failure 只認型別名以 AssertionError 等結尾且前面是點,Turbine 的類別名是 TurbineAssertionError] [修法:範本改用 awaitEvent() 或 cancelAndConsumeRemainingEvents() 取事件再 assertEquals] [repro:skills/kotlin-idioms/test-templates.md T0〈測試〉×〈壞寫法:TEST-18 Saved 多發一次〉改回 awaitComplete() 跑 Gradle]
  WHY:template_problems 只認通電批次「行為測試或正向約束=」那一段的「範本 T<n>」、比對範本檔標題前先剝程式圍欄、讀不了 UTF-8 回 (<templates>, 原因);由 catalog_problems 把讀好的主表列傳進去,不另讀 [出處:代碼審 code-android行為測試範本 r1 甲 F1、F2,架構 F1、F2] [因:圍欄裡示範的標題會讓缺節被放過;同一格兩套解析口徑會漂移] [test:t_kotlin_test_templates_sections]
  PITFALL:T3 用 viewModelScenario().recreate() 的測試放進 Android 模組的本機單元測試,好寫法壞寫法一律例外紅 Method containsKey in android.os.BaseBundle not mocked [出處:代碼審 code-android行為測試範本 r1 丙 F1 實跑] [根因:Android 上 SavedState 就是 Bundle,本機單元測試的 android.jar 是空殼] [修法:範本預設改官方的複製 SavedStateHandle 寫法,viewModelScenario 版只標純 JVM 或 KMP] [test:t_kotlin_test_templates_content_guards]
  WHY:check.py 的剝圍欄(_fence_regions、_visible_lines)是刻意的另一份,規則照 CommonMark、口徑跟 scripts/lumos 的 _fence_regions 逐條對齊;主表只有 main_rows 一條讀法,範本標題只有 TEMPLATE_HEADING_RE 與 template_sections 一套,測試端呼叫同名函式不另抄 [出處:代碼審 code-android行為測試範本 r2 架 F1–F4] [因:check.py 零依賴、scripts/lumos 沒有 .py 副檔名不能 import;抄兩份的正則在邊界案例會分岔] [不選:check.py 動態載入 scripts/lumos(破壞零依賴、CI 單獨跑自檢時多一個相依)] [test:t_kotlin_template_fence_parity]
  WHY:範本檔加 T6–T13 與〈Android 實驗專案骨架〉,接型錄儀器批 25 列、API-9(T12,ArchUnit 讀位元組碼)、UI-39(T13,Konsist 讀宣告)、API-30(T4 補 Ktor);CO-5 改「不接(代碼審或真機)」,UI-39 名稱、壞寫法、標準寫法、後果四欄照強跳過頁改寫 [出處:[[Projects/Android儀器測試範本與架構測試_計劃]] 設計審 r1、決策 d1、d3] [因:要不看字面判協程歸屬與寫死 dispatcher,Konsist 看不進函式本體] [不選:K4 架構測試(宿主由執行時決定,改 T11 行為測試);K5(room-guard 已擋)] [test:t_kotlin_catalog_c_rows_batch_resolved]
  PITFALL:範本矩陣在 Android 實驗專案實跑時,儀器報告的失敗文字截在 64KB,斷言訊息帶整串例外(例 SQLiteException 的 4 萬個 ?)會把 JUnit 斷言框截掉,assertion_failure 判成不是斷言紅 [出處:2026-11-06 T6 DATA-21 模擬器實跑] [根因:AGP 儀器報告截斷失敗文字,收證要在第一個 Caused by 前找到 org.junit.Assert 框] [修法:儀器範本的斷言訊息只帶例外類別名或前幾行] [repro:skills/kotlin-idioms/test-templates.md T6〈測試:Room 2〉query_40000_ids 的訊息改回 exceptionOrNull() 在模擬器跑〈壞寫法:DATA-21 不分批〉]
  PITFALL:ArchUnit 凍結清單只設 allowStoreCreation=false 時,加一支用 FreezingArchRule 包的新規則或改既有規則的描述,會把當下違規靜默存成新的一份、測試綠(改描述時連同時新加的違規一起凍結) [出處:代碼審 code-android儀器測試範本 r1 範本丙 F1;驗證紀錄 E13 實跑] [根因:清單以規則描述當鍵,allowStoreCreation 只管索引檔 stored.rules 整份不見,不在索引裡的規則 FreezingArchRule.evaluate 直接存檔回成功,allowStoreUpdate 預設 true] [修法:範本 T12 的 archunit.properties 加 allowStoreUpdate=false,-ParchunitFreezeInit 同時打開建立與更新;代價是修掉舊違規也要帶屬性跑一次] [test:t_kotlin_test_templates_content_guards]
  PITFALL:範本內容守衛只比對「整節有沒有這串字」時,散文也寫了同一串設定,把 properties 圍欄裡的設定行改成 true 或刪掉,守衛照綠 [出處:代碼審 code-android儀器測試範本 r1 測試 F1 翻紅實驗] [根因:_kt_instr_template_problems 對 T12 只做整節子字串比對] [修法:只在 T12 的 properties 與 kotlin 圍欄裡比對整行 key=value 與 systemProperty 行;改壞只改程式行] [同族:t_kotlin_catalog_instrumented_batch_notes 的改壞只比對舊字串本身(測試 F3),已改成拿改壞資料跑同一組判準 _kt_ui39_problems] [test:t_kotlin_test_templates_content_guards]
  PITFALL:照 Android 實驗專案骨架組 app 模組建置停在 processDebugMainManifest [出處:2026-11-06 儀器測試範本代碼審 r1 修補實跑(驗證紀錄 E13)] [根因:骨架節沒列 app/src/main/AndroidManifest.xml,AGP 找不到就停] [test:t_kotlin_test_templates_content_guards]
  PITFALL:範本 T12 建清單片段的條件改成 if (true) 或拿掉,兩個 systemProperty 變常駐 true,內容守衛照綠 [出處:代碼審 code-android儀器測試範本 r2 通才 F2 翻紅實驗] [根因:_kt_instr_template_problems 只比對 systemProperty 行在不在 kotlin 圍欄,不看有沒有被 -ParchunitFreezeInit 條件包住] [修法:配大括號取 if (project.hasProperty("archunitFreezeInit")) 區塊,兩行只認區塊內] [同族:凍結格矩陣基準與 E13 對不上(通才 F1),加 _kt_t12_freeze_rows_problems] [test:t_kotlin_test_templates_content_guards]
  PITFALL:範本檔頭在第一個 `## ` 之前插一段含 `## ` 的圍欄,內容守衛把檔頭截在圍欄裡、漏讀後面的 T4 Ktor 句而誤報 [出處:代碼審 code-android儀器測試範本 r2 架構對齊 F1 同族收尾] [根因:_kt_instr_wording_problems 的檔頭用 split("\n## ") 手切字串,不看圍欄] [修法:檔頭取到第一個圍欄外的 `## `,圍欄判定走 check.py 的 _visible_lines,同 _kt_template_sections] [test:t_kotlin_test_templates_content_guards]
  REVISIT:2026-11-21 check.py 剝圍欄另寫一份的理由寫「scripts/lumos 沒有 .py 副檔名、不能 import 借用」,但情境題證據自測已用 load_lumos 載入主程式;決定要不要改成借主程式的 _fence_regions,(2026-11-08 起 --sg 自檢的 SARIF 探針也載主程式,「零依賴路徑不載主程式」這個理由已不成立)
  WHY:測試品質標準〈Android 本機單元測試的驗收標準〉協程與 Flow 兩段尾各加一句「照抄起手」指到 kotlin-idioms 的行為測試範本,並寫下範本實驗踩到的兩個坑(backgroundScope 的工作 advanceUntilIdle 不推、Turbine 自己的檢查失敗收證不算斷言) [出處:[[Projects/Android行為測試範本與架構測試_計劃]] 做法 4] [因:寫測試的人先讀標準,範本放在 kotlin-idioms 那邊,沒指路句就找不到] [不選:把範本全文搬進標準(會變兩份要同步)] [test:t_kotlin_test_templates_linked]
  WHY:測試品質標準加兩句指路:Room〈升級〉條指範本 T6,〈Android 本機單元測試的驗收標準〉用既有「照抄起手:…(T7–T11 節)」格式指範本,Robolectric 的 sdk=34 等骨架細節指到範本〈Android 實驗專案骨架〉節、不在標準重抄 [出處:[[Projects/Android儀器測試範本與架構測試_計劃]] 做法 4;代碼審 code-android儀器測試範本 r1 架構對齊 F2] [因:照抄起手的範本跟撰寫標準放兩處,標準要指得到範本;骨架細節抄兩處要同步維護] [test:t_kotlin_test_templates_linked]
  WHY:觸發字停用字表加 Composable、Inject、Modifier,D-33、D-34、D-39 拿掉這三個字 [出處:[[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 實驗 E9] [因:Now in Android 文件頻率超過 8%,當觸發字會讓改檔前推列每次都亮;三列剩下的字複量都低於 8%] [test:t_catalog_stop_triggers]
  WHY:型錄自檢另印「還沒逐列查證 N 列」:來源欄沒有〔查證 日期:網址〕、名稱也沒標(出處不全)的列,只提醒、不進 catalog_problems、不改退出碼;2026-11-07 逐列查完後剩 API-14、TEST-31 兩列(兩條會擋規則找不到官方原文,降不降級待人裁) [出處:[[Projects/Android寫法型錄逐列查證_計劃]]、[[Projects/計劃依據來源必填_計劃]] S5] [因:使用者要每列有打開讀過的官方出處,數字讓新增的列沒查證時每次自檢都看得到] [test:t_kt_catalog_unverified_rows]
  WHY:引用型錄出處不全列的規則只准放不接閘的 rules-unwired/(2026-11-08 起;原本是只准提示級,提示級也可能被專案自行宣告接閘),rules-unwired/ 也收還沒在真專案量過誤報的新規則,任何等級 [出處:[[Projects/規則包覆核兩級接新增告警閘_計劃]]] [因:覆核級與提示級將來可能接閘,依據不足的規則要有一個確定不擋的位置] [test:t_kotlin_rulepack_unwired_dir]
verified_by:
  - "[[Verification/2026-11-05_Kotlin規則包真專案實測]]"
  - "[[Verification/2026-11-06_Android行為測試範本紅綠矩陣實跑]]"
  - "[[Verification/2026-11-06_Android儀器測試範本與架構測試實跑]]"
---
# kotlin規則包

> 白話:Kotlin/Android 寫法的機械檢查規則包(ast-grep)與它的單一來源型錄。型錄每一列寫一種常見錯誤寫法、官方的標準寫法、出處網址、機器怎麼查、在哪一批接上自動檢查;規則包把能用語法結構比對的列寫成規則,推送前的新增告警閘只擋這次新增的告警,訊息帶型錄編號與最短修法。

## 檔案

- `configs/ast-grep/kotlin-android/sgconfig.yml`:會擋的規則(`rules/` 底下,error 與 warning)。消費專案照 [[Systems/linter精選目錄]] 的範本宣告這一份。
- `configs/ast-grep/kotlin-android/sgconfig-review.yml`:語意覆核級規則(`rules-review/`,ast-grep 的 info 等級):形狀抓得到可疑寫法、但要知道型別或語意才分得出對錯的規則(例:Firebase 的 `setValue` 跟 LiveData 同名)。不擋、也不降成提示級;範本還沒接;接不接(覆核級有已知誤報樣本,使用者 d5 與上面誤報一成 RULE 相撞)見 [[Projects/規則包覆核兩級接新增告警閘_計劃]] 待人裁。好例樣本裡檔名開頭 `review-fp-` 的,是這級規則已知會誤報的寫法,改規則形狀時拿來對照,自我檢查不算好例誤報。
- `configs/ast-grep/kotlin-android/sgconfig-hints.yml`:提示級規則(`rules-hints/`),誤報可能較高,範本預設不接。
- `configs/ast-grep/kotlin-android/sgconfig-unwired.yml`:不接閘的規則(`rules-unwired/`,任何等級):引用型錄出處不全列的規則(2026-11-08 從 `rules-hints/` 拆來 8 條),與還沒在真專案量過誤報的新規則;範本不宣告,型錄自檢 `catalog_problems` 擋出處不全的規則放到別的目錄。
- `rules/`、`rules-review/`、`rules-hints/`、`rules-unwired/` 底下的 yml 依型錄主題分檔;每條規則 `samples/bad/<id>/`、`samples/good/<id>/` 各有樣本(只掃測試碼的規則放 `src/test/` 底下)。樣本故意埋壞寫法,風險分級、棧別題、新增告警閘(含測試防竄改比對)、Room 守衛與每支檔有家都不把它們當產品碼(`_RULEPACK_SAMPLE_RE`、`.lumos/config.json` 的 `node_home.ignore`)。
- `configs/ast-grep/kotlin-android/check.py`:自我檢查(零依賴),`python3 check.py --sg <ast-grep>` 驗:每條規則壞例至少命中兩處、好例零命中且至少兩段、載入條數等於 id 數、只掃測試碼的規則對「祖先目錄叫 test 的正式碼」不命中、訊息格式;`--catalog-only` 驗型錄,另跑情境題證據樣式的正反例自測(situation_sample_problems);`--sg` 完整模式另用新增告警閘的 SARIF 解析掃兩條指定規則的壞例(SARIF 探針 `sarif_gate_rule_ids`)。
- `skills/kotlin-idioms/checks-catalog.md`:型錄。欄位與規則見它開頭的〈輸入與口徑〉;〈情境決策表〉是語意類情境的「看到這個 → 預設這樣寫 → 什麼時候例外」,列編號 D-n 只准往後加;〈待查證〉節不受檢查。
- `skills/kotlin-idioms/test-templates.md`:行為測試範本。型錄級含 C 的列有 60 列(T0–T5 純 JVM,T6–T13 要 Android 模組、Robolectric 或模擬器)通電批次寫「行為測試或正向約束=範本 T<n>」,範本檔每組一節 `## T<n> `,節裡有依據、依賴、測試、假依賴、好寫法、壞寫法與紅綠矩陣;`check.py` 的 `template_problems`(由 `catalog_problems` 呼叫)只驗「型錄寫的組在範本檔有那一節」。範本的紅綠只在實驗專案跑過(本 repo CI 不跑 Gradle),改範本程式就照範本的骨架節重跑那一組(T0–T5 照〈實驗專案骨架〉,T6–T13 照〈Android 實驗專案骨架〉)、把結果補進驗證紀錄 [[Verification/2026-11-06_Android行為測試範本紅綠矩陣實跑]](T6–T13 補進 [[Verification/2026-11-06_Android儀器測試範本與架構測試實跑]])。

自我檢查程式是零依賴的獨立檔,YAML 規則檔與型錄表格用自己的行級讀法(情境題證據樣式自測與 SARIF 探針用 load_lumos 把旁邊的 scripts/lumos 當模組載入,借它的比對函式與新增告警閘的 SARIF 解析;載不到就把原因當問題報出):規則檔統一寫成單行 `message:`、`id:` 不加引號,寫成別種形式會被報錯(不會漏報)。樣本目錄排除只認 `configs/ast-grep/<包>/samples/` 底下的 `.kt/.kts`(風險分級、測試防竄改比對、Room 守衛共用的 `_RULEPACK_SAMPLE_RE` 與每支檔有家的 `node_home.ignore` 兩處同一個範圍);消費專案若剛好有同形路徑的正式碼也會被排除,這是接受的取捨。

## 怎麼改

1. 改規則或加規則:同時補樣本,跑 `python3 configs/ast-grep/kotlin-android/check.py --sg <ast-grep>` 到 0 個問題。新規則一律先放語意覆核級(`rules-review/`)或不接閘的 `rules-unwired/`,對真專案量過誤報低於一成才升到會擋的 `rules/`;審查中被點出形狀分不出對錯的,不再放寬形狀,直接留在覆核級(代碼審跑滿回顧,卷證 `governance/review-reports/code-kotlin規則包/cap-retro.json`:三輪的最大宗都是放寬形狀又帶出新誤報)。
2. 改型錄:跑 `--catalog-only`(連證據樣式自測一起跑,會載入旁邊的 scripts/lumos;改了某列的證據樣式就同時改 `samples/situation/<列編號>.kt.txt` 的正反例,到 0 個問題);新寫的標準寫法一定附真的打開讀過的官方網址,查不到就在名稱標「(出處不全)」。
3. 決策表觸發字不准收常用字(停用字表在 check.py 的 `STOP_TRIGGERS`);第二批改檔前推列與第三批情境題靠它不吵。情境沒有不常見的字面特徵時觸發字寫「(無)」(全形半形括號都認),`dt_triggers` 解析成空清單、不出情境段;「(無)」跟別的觸發字並列、或格子空白,自我檢查都會報。第二、三批讀觸發字要走 `dt_triggers`,不要自己拆格子,不然「(無)」會被當成一個字去比對。
4. 有消費專案或範例專案時,拿會擋的規則對整份原始碼跑一次,逐條判真假;誤報超過一成照上面那條規則處理,結果寫回型錄的「實測狀態」欄。

## 2026-11-05 真專案實測

實驗專案(13 支 kt 檔)與 Google 官方範例 nowinandroid(310 支 kt 檔)整份掃:修前命中 30 處、誤報 13 處(nowinandroid 誤報率 55%);誤報集中在測試變體目錄(`src/testDemo`)、Compose 預覽與截圖測試、分不出查詢與指令。照實測改形狀 6 條、降提示級 3 條後重掃:實驗專案 8 處(7 真、1 判不準)、nowinandroid 9 處全真。逐條紀錄在型錄「實測狀態」欄,驗證紀錄見 [[Verification/2026-11-05_Kotlin規則包真專案實測]]。

## 測試品質接入標準指到行為測試範本(2026-11-06,[[Projects/Android行為測試範本與架構測試_計劃]])
- `skills/lumos-project-notes/commands/test-quality-standard.md`〈Android 本機單元測試的驗收標準〉的協程與 Flow 兩小段尾各加一條「照抄起手」,指到 kotlin-idioms 的行為測試範本(標準檔的家是 [[Systems/test-quality-cli]],這裡記的是範本這一側為什麼要它指過來);兩條各帶一個範本實驗踩到的坑:`backgroundScope` 的工作 `advanceUntilIdle()` 不推、Turbine 自己的檢查失敗丟 `TurbineAssertionError` 收證不算斷言。綁的測試 `t_kotlin_test_templates_linked`。
- 代碼審 r1(code-android行為測試範本,2026-11-06)改了同一份標準的三處:Flow 段舊的「錯誤用 `awaitError()` 收」那句補上「要當收證抓到錯的那一步不能靠這些,寫法見本段末條」;Flow 指路句補上 `awaitItem()` 等不到值也丟 `TurbineAssertionError`、要推到靜止後 `cancelAndConsumeRemainingEvents()` 一次比、有限流上 `expectNoEvents()` 會誤紅;〈畫面重建與程序被回收〉整條改寫成「Android 模組的本機單元測試照官方複製 SavedStateHandle,`ViewModelScenario.recreate()` 只在純 JVM 或 KMP 用」(它在 Android 模組因 `Bundle` 是空殼例外紅,實跑)。綁的測試同上,另驗連結目標存在與兩個坑的關鍵字。
