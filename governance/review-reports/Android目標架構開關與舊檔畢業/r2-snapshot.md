---
type: project
status: doing
created: 2026-10-30
updated: 2026-10-30
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/arch-alignment-lens
  - Systems/android-arch-template
related:
  - "[[Projects/Android的MVVM與DDD目標架構範本_計劃]]"
  - "[[Systems/arch-alignment-lens]]"
---
# Android目標架構開關與舊檔畢業_計劃

> 白話:上一份範本是固定的十二條,專案只能整份照抄再自己刪。這份計劃把它改成「開關」:採用時由 AI 逐題問人六個架構選擇,再用一支產生器照答案組出規則節點、宣告與 Konsist 架構測試;另外讓舊檔可以照舊鄰居審、新檔才套目標規則,舊檔重構時從舊檔清單刪掉它那一行,就在同一個分支當場改照目標規則審。

## 用語

- **宣告**:`.lumos/config.json` 的 `arch_targets` 清單,每條 `{"path": 樣式, "node": 節點或 none}`,一支檔由上往下第一條命中的算數。
- **none**:命中這條的檔不套目標規則,照「鄰居」審——架構對齊審查席拿同資料夾、同副檔名、檔名最像的既有檔當對照,問新寫法跟它們一不一樣。
- **目標節點**:一篇 Systems 筆記,摘要裡的 `RULE:` 行就是這個範圍該照的規則;派工鏡頭(派審查席那一刻自動附在派工詞尾端的材料)會把規則原文附給架構對齊席。
- **舊檔清單**:`.lumos/arch-legacy.txt`(新增),一行一個 repo 相對路徑;列在上面、又落在某個目標節點範圍內的檔,照鄰居審。照字面整行比對,不當萬用字元。
- **起點版**:代碼審讀宣告與舊檔清單的那一版,也就是改動起點跟主線的分岔點(既有的可信版本讀法);沒有主線時各條路照現行做法:推送前風險分級把起點本身當起點版(畢業照常判),派工鏡頭整段不附(也就沒有畢業可言)。
- **Konsist**:讀 Kotlin 原始碼的架構測試庫,跑在一般 JVM 單元測試裡。
- **畢業**:舊檔重構成新架構後,從舊檔清單刪掉它那一行,改照目標規則審。

## 問題與最小解

立案:Enzo 2026-10-30 在 Android 範本合併後提出三件事——多模組要寫進範本、檢查要有開關(不只多模組,還有其他架構選擇)、舊 class 維護照既有架構而新 class 才套用;並補充「一開始配置時詢問我再決定」與「舊檔重構」。開關清單由 Enzo 同日從建議裡全選:模組切法、舊程式處理、用例層可省略、DDD 深度、介面策略、畫面狀態形式。畢業生效時機 Enzo 選「同分支就生效」(不選「先合一個只刪宣告的小合併請求」)。

現況:
- 範本的十二條與 Konsist 骨架寫死在技能文件 `skills/lumos-project-notes/commands/target-arch-android-template.md` 裡,不適用的規則要人自己刪,刪了規則卻忘了刪對應測試、或反過來,沒有東西會抓。
- arch_targets 只認 `path` 與 `node` 兩欄,第一條命中算數,樣式第一段要是寫死的資料夾名;一條不合法整份不用。
- 代碼審的宣告只讀起點版(防被審分支自己放寬怎麼被審),所以舊檔重構時在同一分支改宣告,這次重構照樣比鄰居——最需要照目標審的那次反而沒審到。

做法:
1. **開關資料檔**:Android 規則與 Konsist 測試的唯一來源搬到 `scripts/templates/android-arch-target.md`(新增),每條規則與每支測試標「哪些開關值才收」;登記進工具自帶檔清單 `_VENDORED_TREE_FILES`(`lumos update` 靠這張表分發,另有逐檔比對的測試)。新開 `Systems/android-arch-template` 當它的家。DDD 與前端兩份範本照舊是技能文件裡的抄貼式:它們沒有開關需求;06 那一列寫明「Android 用產生器、其他兩份照抄」,不讓接手的人猜。DDD 規則兩份各自是單源:DDD 範本管語言中立版,Android 資料檔管 Android 版(反例換成 Room、ViewModel),同義不同文是上一份範本就有的刻意安排,不互相抄。產生器的說明也寫在 `Systems/android-arch-template`;`Systems/arch-alignment-lens` 只多寫畢業與舊檔清單的讀法,因為那是架構對齊怎麼選基準的一部分。
2. **產生器** `lumos arch-template android`:
   - 必填:`--root <根套件>`、至少一個 `--scope <目錄>`(可重複,多模組每個模組各給一個)、六個開關各一個旗標(`--modules` `--legacy` `--usecase` `--ddd` `--interfaces` `--ui-state`,沒有預設值,要照訪談答案明給)。
   - 選填:`--node`(預設 `Systems/Android目標架構`)、`--test-file`(預設 `app/src/test/java/<根套件轉路徑>/arch/ArchitectureRulesTest.kt`)、`--test-platform <名>`(給了就把綁定寫成 `[test:<名>:<測試名>]`;那個平台要已在 `.lumos/config.json` 的 `platforms` 宣告,沒有就拒絕)、`--date`(預設今天)、`--revisit`(預設一年後)。
   - `--scope` 先去掉結尾斜線,再照宣告讀法同一套檢查(不能空、不能是 `.`、不能以 `./` 或 `/` 開頭、不能有反斜線或控制字元、第一段不能有萬用字元、不能少於兩段),不合法就拒絕;產出的宣告交給讀宣告的同一支函式讀一次,讀出的條數不同就拒絕。
   - 預設只印預覽(節點全文、宣告、舊檔清單幾行、架構測試全文);`--write` 才寫。
3. **寫入規則**:
   - 拒寫(整批不寫,說明是哪一個):節點檔已存在、架構測試檔已存在、`legacy=new-only` 而舊檔清單已存在、設定檔讀不懂(壞 JSON、非 UTF-8、開頭帶 BOM、頂層不是物件)、設定檔裡已有 `arch_targets` 這一鍵(值是 null 或空清單也算)。
   - 設定檔不存在就新建;存在就加 `arch_targets` 一鍵,其他鍵的值與順序保留,整檔重寫成兩格縮排、中文不跳脫(格式可能變,語意不變;預覽會印出來)。
   - 寫檔走 lumos 共用的 `_write_lf`(先寫暫存再替換);先寫新檔、設定檔最後寫,設定檔失敗就刪掉這次新建的檔。
   - 節點直接寫出完整內容(`lumos new` 的空範本放不下規則),名稱與負責範圍句(產生器寫固定的一句,至少 10 字)沿用 `lumos new` 同一套檢查;寫完自己跑一次 `lumos lint` 並印結果。
4. **舊程式處理** `--legacy`:
   - `all`:範圍內全部照目標審,不寫舊檔清單。「只套用指定目錄」就是只給那幾個 `--scope`。
   - `new-only`:舊檔清單寫入範圍內 git 已追蹤、會被架構對齊當程式檔看的每支檔(含 xml、gradle 腳本;不含測試檔),依字典序、轉 NFC、一行一個;檔名含換行或控制字元就拒絕並列出。清單沒有條數上限(查表比對)。
   - 每個 `--scope` 各一條目標宣告。
5. **讀舊檔清單**:推送前風險分級、派工鏡頭、代碼審判定三處,在讀宣告的同一版讀舊檔清單;改動檔落在目標範圍內又在清單上的,照鄰居審;改名的檔,舊路徑在清單上也照鄰居審。`lumos doctor` 只印一行摘要:清單幾支、其中幾支已不存在、幾支不在任何目標範圍(只提醒不擋)。
6. **畢業**:起點版與頂端版的宣告完全相同、頂端版舊檔清單只比起點版少行(沒有新增行)時,少掉的那幾行對應、而且這次範圍內有改動的檔,照它命中的目標節點審(沒改動的檔本來就不審);派工鏡頭的 500 條宣告與 5 秒上限照舊套在宣告上,清單是查表不受上限影響;規則原文照讀起點版。宣告有任何不同、清單有新增行、任一版讀不懂、這條路沒有可信起點版,就整批不畢業、全照起點版判。三處讀法共用一支判定函式。
7. **代碼審判定的說明行**:畢業時印「舊檔清單刪了 N 行,其中 M 支這次有改動、已照目標審」;清單新增行時印「舊檔清單新增 N 行,本次仍照起點版」;改名的檔舊路徑在清單上、新路徑沒補進清單時印「改名的舊檔 N 支沒同步改清單,架構測試會檢查它們」;宣告或目標節點有改時照舊印「下次推送才生效」;第一行的檔數標明「含畢業 N 支」。
8. **Konsist 那一半**:產生的架構測試自己往上找含 `.lumos/config.json` 的資料夾當根(找不到就讓測試紅並說明,不靜默變綠;Gradle 子模組的工作目錄不是 repo 根也找得到);`legacy=new-only` 產出的測試讀舊檔清單,清單不存在就紅;`legacy=all` 產出的測試不讀清單;只檢查「相對根的路徑落在某個 `--scope` 目錄底下(以斜線為界)、又不在舊檔清單上」的類別,比對前兩邊都轉 NFC;聚合根名單這類「被參照的對象」照全部正式程式算,舊檔的聚合根也算進去。範圍目錄寫成測試裡的常數,旁邊一行 `// lumos-arch-scope: <目錄>;<目錄>` 標記(多個範圍用分號隔開);`lumos doctor` 拿這組目錄跟 arch_targets 裡指向目標節點的 `<目錄>/**` 宣告當集合比,不一致就提醒。舊檔改名時要在同一個提交把清單那一行改成新路徑,不然架構測試會檢查它(第 7 點的說明行會點名)。
9. **開關語意**:
   - `modules=multi`:多一條「模組依賴」規則(presentation 不依賴 data、domain 模組不套 Android 外掛),交給 Gradle 擋;分層與 Android 匯入兩支 Konsist 測試照留(依功能拆模組時 domain 可能還在 Android library 裡)。
   - `ddd=lite`:拿掉聚合根、識別碼參照、值物件三條規則與三支對應測試;其餘所有提到聚合的規則都換成不提聚合的版本(現在是 Repository、用例、ViewModel 業務規則、測試邊界四條)。
   - `usecase=optional`:ViewModel 可收 domain 的 Repository 介面,只禁 data 層實作與資料來源;ViewModel 建構子那支測試跟著改成只擋 `RepositoryImpl`、`DataSource`、`Dao`、`Api` 結尾的型別;用例規則改成「有用例時」。
   - `interfaces=always`:深模組那條換成「用例與 Repository 一律介面加 Impl」,用例測試的篩選同時認 `UseCase` 與 `UseCaseImpl` 結尾,另加一支「每個 Impl 都實作同名介面」的測試。
   - `ui_state=single`:唯讀狀態那條換成「每個 ViewModel 只公開一個 uiState」,測試跟著換。
10. **文件與既有測試**:技能文件改成講訪談題目、開關表、產生器怎麼跑、已照舊範本採用的專案怎麼升級(先改名或刪掉舊節點與 arch_targets 再跑產生器;不升級也照常運作);06 那一列、技能首頁那句、`Systems/arch-alignment-lens`「下一次推送才生效」那句補上畢業例外;指令索引 INDEX.md 與 `--help` 的「什麼時候用」補上新指令(INDEX.md 有字數上限,要在上限內)。舊的三支範本測試:`t_arch_target_android_template_valid` 與 `t_arch_target_android_template_konsist_names_match` 改測產生器在「single、all、required、full、deep、any」這一組的產出(跟範本現在的十二條同組),`t_arch_target_android_template_linked_from_usage` 照留;舊計劃 `[[Projects/Android的MVVM與DDD目標架構範本_計劃]]` 的 S1、S3 綁定照名字不變,在那篇註明內容改由產生器提供。

舊否決對照:[[Projects/架構對齊可宣告目標架構_計劃]] 定了「代碼審只讀起點版宣告,分支改的宣告下一次推送才生效」,理由是被審分支不能自己改宣告決定自己怎麼被審。畢業部分推翻這條;Enzo 2026-10-30 在聽完這道保護與「另開一個只刪宣告的小合併請求」替代做法之後,仍選同分支生效。範圍因此只開一個口:宣告一字不改、舊檔清單只刪不加;規則原文照讀起點版。

PRIOR-ART:開關借 Android 官方架構指南本身的分歧點——領域層(用例)在指南裡標為可選、UI 狀態指南建議單一狀態物件但不強制;DDD 輕量版借「只取分層與 Repository、不取戰術模式」的常見做法;多模組借 Now in Android 的 core/feature 拆法。舊檔清單借靜態分析工具的 baseline 檔(採用當下凍結、新碼才擋,例:detekt baseline、Android Lint baseline 都是獨立檔、照字面比對、刪一行就恢復檢查)。產生器借 lumos 既有的寫檔函式與 `lumos new` 的名稱檢查,不加依賴。畢業只放寬「清單只刪不加」這一種改動,其他改動維持只讀起點版。
RETIRE-IF:2027-04-30 人裁時,若沒有任何 Android 專案用產生器建過目標架構節點,撤掉產生器與開關資料檔,範本退回固定版 [retire:人裁] [until:2027-04-30]。
RETIRE-IF:畢業判定若出現一次「分支靠刪清單行讓本該比鄰居的檔逃過審查」的實例,撤掉同分支生效、改回下次推送才生效 [retire:人裁] [until:2027-04-30]。

## 開關

| 開關 | 選項 | 影響 |
|---|---|---|
| 模組切法 `modules` | `single` 單模組 / `multi` 多模組 | multi 加一條模組依賴規則,Konsist 測試不減 |
| 舊程式處理 `legacy` | `all` 範圍內全部套用 / `new-only` 舊檔照舊 | new-only 寫舊檔清單;只套指定目錄=只給那幾個 `--scope` |
| 用例層 `usecase` | `required` 一定要有 / `optional` 可省略 | optional 時 ViewModel 可收 domain 的 Repository 介面,只禁 data 層實作與資料來源 |
| DDD 深度 `ddd` | `full` 完整 / `lite` 輕量 | lite 拿掉三條聚合類規則與測試,其餘規則換成不提聚合的版本 |
| 介面策略 `interfaces` | `deep` 深模組 / `always` 一律開介面 | always 換規則、用例測試篩選認 Impl、多一支介面測試 |
| 畫面狀態 `ui_state` | `single` 單一 UiState / `any` 不限 | single 換成「每個 ViewModel 只公開一個 uiState」規則與測試 |

## 驗收條款

- [S1] 當產生器跑遍六個開關的全部 64 種組合時,每一份產出的節點經 lumos lint 應回報 0 問題,目標架構規則讀法讀到的有效 RULE 行數應等於那個組合該收的規則數;每條帶測試綁定的 RULE 行指到的測試名都應在同一份 Konsist 檔裡有同名測試函式,Konsist 檔裡的每個測試函式也都應被某條 RULE 行或命名慣例清單認領;產出的 arch_targets 經讀宣告的函式讀出的條數應等於 --scope 的個數。 [test: t_arch_template_android_all_combos]
- [S2] 當只切換一個開關時,產出應只在那個開關負責的地方不同:usecase=optional 時 ViewModel 規則與測試不再禁 Repository 介面;ddd=lite 時沒有三條聚合類規則與三支對應測試,而且整份節點的 RULE 行不含「聚合」二字;interfaces=always 時沒有深模組那條、有一律介面那條,用例測試的篩選認 UseCaseImpl,並多一支介面測試;ui_state=single 時有單一 uiState 那條;modules=multi 時多一條模組依賴規則,而分層與 Android 匯入兩支測試仍在。 [test: t_arch_template_android_switch_effects]
- [S3] 當 legacy=new-only 時,舊檔清單應列出 --scope 底下 git 已追蹤、架構對齊當程式檔看的每支檔(含 xml 與 gradle 腳本,不含測試檔),轉 NFC、依字典序、一行一個,檔名含方括號或星號的照字面列出;檔名含控制字元時應拒絕;legacy=all 時不產舊檔清單;--scope 為空、點號、以 ./ 或 / 開頭、含反斜線或控制字元、第一段萬用字元或少於兩段時應拒絕,結尾斜線應被去掉;給了未在 platforms 宣告的 --test-platform 時應拒絕。 [test: t_arch_template_android_legacy_modes]
- [S4] 當產生器帶 --write 而節點檔、架構測試檔、舊檔清單(new-only 時)任一已存在,或設定檔讀不懂(含開頭帶 BOM),或設定檔已有 arch_targets 鍵(含 null 與空清單)時,應整批拒寫並說明是哪一個;都沒有時應全部寫出,設定檔原有的其他鍵值與順序保留,寫出的節點經 lumos lint 0 問題;設定檔寫入失敗時這次新建的檔應被刪掉。 [test: t_arch_template_android_write_refuses_existing]
- [S5] 當起點版與頂端版宣告相同、頂端版舊檔清單只少了幾行時,推送前風險分級與派工鏡頭都應把其中這次有改動的檔放進它命中的目標節點;清單同時新增了行、宣告有任何不同、任一版清單或宣告讀不懂、這條路沒有可信起點版時,都應照起點版判;改名的檔舊路徑在起點版清單上時照鄰居審。 [test: t_arch_target_graduate_same_branch]
- [S6] 當範圍內舊檔清單只刪了行時,代碼審判定應印刪了幾行、其中幾支有改動已照目標審,不印「下次推送才生效」;清單新增行時應印新增幾行、本次仍照起點版;改名的舊檔新路徑沒補進清單時應點名幾支;宣告或目標節點同時有改時兩種說明都印;第一行檔數應標明含畢業幾支。 [test: t_arch_target_graduate_check_note]
- [S7] 當讀技能文件的 Android 範本時,文件列出的開關名與選項應跟產生器實際收的開關旗標與選項完全一致。 [test: t_arch_template_android_doc_matches_switches]
- [S8] 當讀產生器產出的 Konsist 檔時,應有找不到根就失敗的程式、範圍目錄常數與列出全部範圍的 lumos-arch-scope 標記行,聚合根名單應取自全部正式程式而非過濾後的範圍;new-only 的產出應讀舊檔清單、清單不存在就失敗,all 的產出不讀清單。 [test: t_arch_template_android_konsist_legacy_shape]
- [S9] 當執行 lumos doctor 時,有舊檔清單應只印一行摘要(幾支、幾支已不存在、幾支不在目標範圍),架構測試的 lumos-arch-scope 標記跟 arch_targets 的目標宣告不一致時應印一行提醒,回傳碼不因此改變。 [test: t_arch_target_legacy_doctor_lines]
- [S10] 當在 macrobench-lab 用產生器 new-only 產出、在一支舊檔與一支新檔各埋一條 Konsist 抓得到的違規時,架構測試應只因新檔紅;從舊檔清單刪掉那支舊檔再跑,兩支都紅。 [manual: 在 macrobench-lab 跑 Gradle 單元測試看紅綠,結果寫進那個專案的驗證紀錄]

## 回退

刪掉產生器子命令(連同 `--help` 的「什麼時候用」)、開關資料檔 `scripts/templates/android-arch-target.md` 與它在工具自帶檔清單的那一行、`Systems/android-arch-template` 節點、舊檔清單讀法與畢業判定函式及三處呼叫、代碼審判定新增的說明行、doctor 新增的兩行、新增的九支測試;技能文件、06、技能首頁、INDEX.md、`Systems/arch-alignment-lens` 那句與舊計劃的註明改回上一版,兩支舊範本測試改回讀技能文件。已用產生器建好的節點與宣告是普通的節點與宣告,照常運作;舊檔清單回退後不再被讀,清單上的檔改照目標審,要照舊就在 arch_targets 加 none。不碰任何帳本。

## 實務隱患

- 效能:舊檔清單讀成集合查表,幾千行也只是一次讀檔;畢業多讀一次頂端版宣告與清單。doctor 最多多兩行(清單摘要一行、範圍標記不一致一行),不逐條列清單。
- 併發:產生器寫幾個新檔、在設定檔加一鍵;寫檔走暫存再替換,任一已存在就整批不寫;不跟其他指令共用狀態。
- 守衛面:畢業放寬了「只讀起點版」的保護,只放「宣告一字不改、清單只刪不加」這一種;規則原文仍讀起點版。Konsist 讀的是工作目錄這一版的清單,分支往清單加行能讓架構測試跳過那支檔——審查席照讀起點版清單照審,代碼審判定另印「清單新增 N 行」讓人看得到;單人、AI 依序操作的威脅模型下不另外擋。

REVISIT:2027-04-30 翻治理帳裡代碼審判定印過「舊檔清單新增 N 行」的推送,有出現在採用之後的就評估改成擋
- 已排除:金流:不碰任何金流或支付資料。
- 已排除:對外送出:產生器只寫本機專案檔。
- 已排除:不可逆:產生器拒寫已存在的檔,寫出的檔可直接刪除。

REVISIT:2027-01-31 Konsist 往上找根、照範圍目錄與舊檔清單過濾的寫法只在 macrobench-lab 一個單模組專案驗過;拿一個多模組的 Android 專案套一次,確認子模組的單元測試也找得到根、路徑比對也對

## 審計修正紀錄

- 首輪前掃(2026-10-30,Haiku 一席):語意類 3 條、範圍矛盾 2 條、未定義詞一組,已修真檔;前掃員判「範本不在技能文件」不成立(它只查了技能首頁),改寫成帶完整路徑。留痕 `governance/review-reports/Android目標架構開關與舊檔畢業/r1-intake.md`。
- r1(2026-10-30,4 席:正確性、邊界、接手、架構對齊):38 條/blocking 17/舊檔改用獨立清單檔、畢業收窄成「宣告不動、清單只刪」、範圍目錄可多個、多模組不拿測試、Konsist 只查範圍內新檔但參照對象算全部、寫入規則與舊測試處置寫明。席報告 `governance/review-reports/Android目標架構開關與舊檔畢業/`。
- r1 折入後鏡像核對(Haiku 一席,看折入差異加四份席報告):12 處各節講法對不上、1 條沒覆蓋(改名的舊檔在架構測試那頭)、8 條只覆蓋一半,全數補進做法、條款、回退與實務隱患。
- 不加新機制的最小解為什麼不夠(r1 折入時):舊檔清單原本逐檔寫成 none 宣告,不加新檔;但宣告有 500 條上限(派工鏡頭)、樣式會把檔名裡的方括號與星號當萬用字元、改名就掉出、doctor 每條死行各印一行、Konsist 那頭要解析 JSON 又要重做萬用字元語意,五個問題都出在「把清單塞進樣式比對」;獨立清單檔照字面查表,一次全解。doctor 的範圍標記比對是為了守「範圍目錄同時寫在宣告與測試常數」這兩份,沒有它兩邊分岔不會有人發現。
