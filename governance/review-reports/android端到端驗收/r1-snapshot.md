---
type: project
status: doing
created: 2026-10-25
updated: 2026-10-25
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/android-e2e-acceptance
  - Systems/pitfalls-code-loop
  - Systems/macrobenchmark-adapter
  - Systems/android-stability-collector
related:
  - "[[Projects/Android效能判定統計化_計劃]]"
  - "[[Projects/Android記憶體與穩定性驗收_計劃]]"
  - "[[Projects/Android側UI測試綁圖譜工作流_計劃]]"
  - "[[Projects/截圖基準驗收流程_計劃]]"
---
# Android端到端驗收_計劃

白話:Android App 改完、合併之前,在本機接著實機跑一次「端到端驗收」,四塊一起驗:UI 流程走不走得完(Maestro flow)、畫面跟人核可過的基準圖一不一樣(截圖比對)、效能有沒有變慢、記憶體有沒有洩漏或閃退。跑完寫一份綁在「這一版 App 程式內容」上的查證紀錄,推送前與 CI 都檢查這一版有沒有一份通過(或有人留理由放行)的紀錄,沒有就擋合併。毫秒類效能(啟動時間、每幀耗時、凍結幀)第一版只提醒、不擋,等 [[Projects/Android效能判定統計化_計劃]] 的第 1、3、4 條(20 輪、同場比較、太吵指標只列出)都上線再改成擋。2026-10-24 Enzo 提「整合 Maestro,將效能測試、UI 測試成為 Android 端 E2E 的驗收標準」;2026-10-25 對話裡逐段確認了範圍、擋法、做法與三段設計。

PRIOR-ART: Maestro CLI(`maestro test` 跑 flow,`--format junit --output` 出測試報告、`-e KEY=VAL` 傳參數,內建 `assertScreenshot` 截圖比對);使用者自己的 maestro-visual-toolkit(github.com/EnzoHsieh-Android/maestro-visual-toolkit:人核可基準圖、門檻 99.5%、紅框差異圖、狀態列固定,原本只在模擬器驗過;本 repo 的 [[Projects/Maestro截圖基準比對_調研]] 與 [[Projects/截圖基準驗收流程_計劃]]);Lumos 既有的 Maestro flow 綁功能筆記(`[test:maestro:<名>]`,[[Projects/Android側UI測試綁圖譜工作流_計劃]]);既有的 Macrobenchmark 判定(`lumos macrobench`,[[Systems/macrobenchmark-adapter]])與記憶體穩定性收集([[Systems/android-stability-collector]]);GitHub 分支保護的「合併前必須通過的檢查」。借用:以上全部;自建只有一支串四塊的範本腳本、一個彙整判定與寫紀錄的子命令、`code-loop check` 裡多一道判定。不選:Maestro Cloud 與 Firebase Test Lab 這類雲端裝置(跟「本機實機跑」的決定衝突,而且雲端裝置量的效能不能當基準);Gradle Managed Devices 的模擬器(同上,模擬器效能數字不能當基準)。
RETIRE-IF: 連續兩個真實專案跑滿三個月,E2E 驗收擋下的全是誤擋(人放行的理由都是「不是真問題」),或推送前改走略過檢查的次數多過正常通過的次數,就把擋合併降回只提醒。
REVISIT:[when-status:Projects/Android效能判定統計化_計劃=done][by:2027-06-30] 效能判定統計化第 1、3、4 條都上線後,把毫秒類效能從只提醒改成擋合併,條款另開

WHY:擋合併、人可留理由放行 [出處:2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」] [因:驗收沒過的程式不該默默進主線;但實機驗收會有誤擋,要留一條有紀錄的人工出口] [不選:只提醒(跟「成為驗收標準」的目的不符);不准放行(誤擋時只能改走略過檢查,沒有紀錄)]
WHY:驗收在本機實機跑,CI 只檢查查證紀錄 [出處:2026-10-24 Enzo 選「本機實機跑,CI 驗收據」] [因:CI 機器接不到實機;效能數字只有實機的能當基準] [不選:CI 跑模擬器(效能數字不能用,截圖也跟實機不同)]
WHY:做法採「範本腳本碰裝置、lumos 只判定與記帳」 [出處:2026-10-25 Enzo 選做法 A] [因:跟已上線、過了五輪代碼審的記憶體收集同一個分工(lumos 不碰裝置);CI 不用接裝置] [不選:lumos 自己操作裝置(打破「lumos 不碰裝置」,要重寫一整套裝置控制、逾時、收尾);雲端或 CI 模擬器(見上)]
WHY:紀錄綁 App 程式目錄的內容指紋,不綁提交編號 [出處:2026-10-25 Enzo 確認第二段] [因:壓提交、rebase 之後內容沒變,綁提交編號的留痕會失效、要重跑十幾分鐘的實機驗收;只改文件也不該要求重跑] [不選:綁提交編號(今天代碼審留痕就因此重做過好幾次)]
WHY:毫秒類第一版只提醒 [出處:2026-10-25 Enzo 選「毫秒類先只提醒」;[[Verification/2026-10-24_效能判定規則實機評測]]] [因:毫秒數字跨時段會漂,判定規則還沒校準完,擋了以後誤報就是硬成本] [不選:四塊全擋(誤擋多);只擋 UI 流程(記憶體洩漏與截圖這類數得出來的,沒理由不擋)]
WHY:Maestro flow 第一次失敗自動重跑一次,第二次過算過但紀錄標不穩定 [出處:2026-10-25 Enzo 確認第一段] [因:Maestro 常因動畫、載入時間偶發失敗,不給重跑會一直誤擋;不留標記又會把不穩定的 flow 藏起來] [不選:不重跑(誤擋);重跑到過為止(藏住真問題)]

## 設定(`.lumos/android-e2e.json`)

- `app_dirs`(必填):App 程式目錄清單,相對專案根(例 `["app/src", "app/build.gradle.kts"]`);指紋只算這些底下的檔,也是「這個分支有沒有改到 App 程式」的判準。
- `package`(必填):App 套件名(只收英數字、底線與點,跟收集腳本同一個規則)。
- `apk`(必填):要裝的 APK 路徑,相對專案根;範本腳本照它裝、紀錄記它的 sha256(另記裝置上實際安裝那份的 sha256)。
- `flows`(必填,至少一支):驗收用的 Maestro flow 路徑清單,相對專案根。
- `visual`(選填):截圖比對的畫面名清單,畫面名要對到 maestro-visual-toolkit 的慣例(flow 是 `.maestro/<畫面名>.yaml`、基準圖是 `.maestro/baseline/<畫面名>.png`);沒寫就不跑截圖這塊、紀錄寫「未設定」(不算通過也不擋)。用之前專案要先照 toolkit 的 `install.sh` 裝好 `.maestro/` 底下的腳本。
- `visual_threshold`(選填,預設 99.5):不得低於 99.5(toolkit 的 `visual-check.sh` 收到更低的門檻會回 2),不是有限數也擋。
- `adb_serial`(選填):多台裝置時指定哪一台,傳給 Maestro、收集腳本與 adb。
- 效能與記憶體沿用既有設定:Macrobenchmark 結果目錄與基準在 `.lumos/macrobench.json`,記憶體與穩定性在同檔的 `stability` 段(驅動指令換成 Maestro),判定的門檻在 `.lumos/macrobench-thresholds.json`;記憶體與穩定性要有寫了 `check` 的門檻條目才判得出東西(沒有時 `lumos macrobench` 只印 stability_unjudged,本計劃把它當成「沒判到」)。

## 一次驗收跑什麼(四塊)

| 塊 | 怎麼跑 | 怎麼判 | 沒過時 |
|---|---|---|---|
| UI 流程 | `flows` 每支 `maestro test --format junit --output <run 目錄>/ui/<名>.xml`(有 `adb_serial` 時加 `--device`) | 回傳碼是 0 而且報告裡至少一個測試案例、沒有失敗;第一次沒過重跑一次,第二次過算過、標不穩定 | 擋 |
| 截圖比對 | `visual` 每個畫面跑 `.maestro/visual-check.sh <畫面名> <run 目錄>/visual/<畫面名>/`(第二個參數讓差異圖、這次拍的、基準三張複製到 run 目錄) | 回傳碼 0 算過;1(不相符或環境問題)與 2(缺基準圖、參數錯)都算沒過,原因照腳本輸出記;腳本只有不相符時才印相符率,紀錄就只在那時記相符率 | 擋 |
| 毫秒類效能 | 專案的 Macrobenchmark(預設 20 輪)跑完,`lumos macrobench --json` | 照既有判定;`regressions` 與毫秒類門檻沒達寫進紀錄的 `notices` | 只提醒 |
| 記憶體與穩定性 | 既有收集腳本,`stability.driver` 換成 Maestro flow(腳本把 `{{CYCLES}}` 換成輪數、跑暖機與量測兩次),再 `lumos macrobench --json --stability <stability.json>` | 記憶體類(native_unreachable、java_growth、instances、peak_vitals)、閃退(exits)、StrictMode 這幾類:列在 threshold_failures 算沒過;列在 threshold_skipped(換了裝置、量測期間行程換過、來源沒量成)或整段 stability_unjudged 算「沒判到」,也不算通過;凍結幀(frozen)沒過或沒判到只寫進 `notices` | 擋(沒判到也擋,可人放行;凍結幀只提醒) |

## 資料怎麼流

0. 前置(實作第一步,做完才寫範本腳本):在 SM-X710 上實測兩件記憶體計劃與 toolkit 留下的待驗事項,結果寫進計劃再往下:Maestro flow 的 `repeat` 的 `times` 吃不吃 `${CYCLES}`(不行就改用 `while` 加計數,並改 skill reference 的 Maestro 驅動範例);toolkit 的狀態列固定在實機上固定得住(固定不住就改截圖區域或另找做法,先問 Enzo)。
1. 人或 AI 在專案根跑範本腳本 `android-e2e-run.sh`(工具鏈範本,跟記憶體收集腳本放一起):run-id 預設 `e2e-<年月日>-<時分秒>`,原始輸出放 `.lumos/artifacts/android/<run-id>/` 底下的 ui、visual、macrobench、stability 四個子目錄(產物目錄必須被 git 忽略,跟收集腳本同一個要求),不進版控。腳本依序:裝 APK、跑 UI 流程、截圖比對、Macrobenchmark、記憶體與穩定性收集(收集腳本照它自己的規則跑,開頭會先 `am force-stop`);任一塊中途失敗也繼續把剩下的跑完再進下一步。
2. 腳本最後呼叫 `lumos android-e2e judge <run 目錄>`:讀四塊的原始輸出、照上表判、算指紋,寫一份查證紀錄 `.lumos/e2e-records/<指紋>.json`(進版控);同一個指紋再跑一次就覆蓋成新的那份。
3. 推送前與 CI 的 `code-loop check` 多一道「Android E2E 驗收」判定:
   - 範圍:從這個分支跟主線的分岔點,到這次被推送的提交(不是只看這一次推送帶了哪些提交):這段裡有任何提交改到 `app_dirs` 底下的檔,就要求紀錄。這樣先略過檢查推了改程式的提交、再推一個只改文件的提交,CI 照樣擋。
   - 指紋從被推送的那個提交的檔案樹算(`git ls-tree` 取 `app_dirs` 底下的檔與內容),不看工作目錄。
   - 找對得上指紋的紀錄:結果是通過、或有人放行 → 這道過;找不到、沒過、或有「沒判到」→ 這道擋,印出要跑的指令(跑驗收,或放行)。
   - 位置:跟既有的安全證據判定一樣排在所有「放行早退」之前,不然會被跳過;pre-push 帶 `--keep-going` 時跟其他判定一起列出擋下原因,CI 照現在的行為第一道擋下就停。判定回 1 才擋;這道自己出錯(例如讀不了紀錄檔)時照 code-loop check 既有的做法回 2,pre-push 對非 1 的回傳碼照舊放行並印出原因——這是既有的 fail-open 行為,本計劃不改。
   - 專案沒有 `.lumos/android-e2e.json` 時這道不跑。
4. 人覺得是誤擋、或這次就是沒辦法跑(例如沒接裝置)時,`lumos android-e2e waive --note "<理由>"`(預設放行目前提交的指紋):有紀錄就在紀錄裡加上放行;沒有紀錄就新建一份只有放行的紀錄。寫下誰(git 設定的使用者)、哪一天、理由,治理帳記一筆 `android-e2e-waive` 事件;`lumos gov --stats` 會數放行次數(RETIRE-IF 要用)。

## 查證紀錄長怎樣

- 指紋:被推送那個提交的檔案樹裡,`app_dirs` 底下的檔,依路徑排序後「路徑+內容」一起算 sha256;不看提交編號、不看目錄外的檔。
- `result`:pass(四塊裡會擋的都過)、fail(有會擋的沒過)、unjudged(有會擋的沒判到、沒有會擋的沒過)、waived(人放行)。
- 各塊明細:每支 flow 的結果與是否不穩定;每個畫面的結果、原因、不相符時的相符率與差異圖路徑;效能的 `regressions` 與毫秒類門檻結果;記憶體與穩定性每條 check 在 failures、passed、skipped 哪一邊與原因。
- `notices`:只提醒、不影響 result 的項目(毫秒類退步、毫秒類門檻沒達、凍結幀)。
- 環境:裝置型號、系統版本、設定裡 APK 的 sha256、裝置上實際安裝那份的 sha256、run-id、開始與結束時間。
- `waiver`(有的話):誰、日期、理由。
- 原始檔只在本機;紀錄只放摘要與數字。

## 這次要改到的地方

- 新子命令 `lumos android-e2e`(judge、check、waive、check-config)與它的家 `Systems/android-e2e-acceptance`(新開)。
- `code-loop check` 多一道判定,排在放行早退之前:改到 [[Systems/pitfalls-code-loop]] 管的那支判定入口。
- 新範本腳本 `android-e2e-run.sh` 放 `scripts/templates/`,家節點同上。
- skill lumos-android-evidence 的 reference.md 已有一份 Maestro 驅動範例(沒實測過):前置步驟驗完後照結果修正;skill 補「E2E 驗收」一節:怎麼設定、怎麼跑、紅了怎麼看、怎麼放行、GitHub 要把 CI 設成合併前必須通過。
- 實驗室專案 macrobench-lab 加 Maestro flow、截圖基準、可注入的 UI 錯與 `.lumos/android-e2e.json`,驗收用。
- 試點真專案:Citrus_KDS。已知坑:KDS 在 SM-X710 用 benchmark-macro 1.2.4 跑不起來(確認不了畫面啟動完成,[[Verification/2026-10-23_macrobench實機端到端]]),實驗室用 1.4.1 可以;接 KDS 時要升版,改 KDS 依賴前先問 Enzo。

## 不做

- 毫秒類效能擋合併(等統計化計劃第 1、3、4 條,見上方 REVISIT)。
- iOS 端。
- 雲端裝置或 CI 上跑實機驗收。
- 驗證紀錄真的是在實機跑出來的:CI 只能檢查格式、指紋與結果,照 Lumos 的威脅模型(單人、AI 依序操作,不防刻意偽造)不另外防。
- 改 pre-push 對工具出錯時放行(fail-open)的既有行為。

## 實務隱患

- 已排除:金流:只讀驗收輸出與程式檔內容,不碰交易。
- 已排除:對外送出:驗收在本機跑,紀錄只進專案自己的 git,不送到外部服務。
- 已排除:不可逆:紀錄與放行都是新增的檔與帳,刪掉紀錄就回到沒驗收的狀態;不刪除任何專案檔。
- 守衛面:這份計劃就是新增一道擋合併的判定,誤擋會卡住開發、漏擋會讓沒驗收的程式進主線;兩邊都要有實驗室證據(見〈實驗室驗收〉)。
- 擋合併靠專案在 GitHub 把 CI 這道檢查設成「合併前必須通過」,lumos 開不了,只能寫進接入說明;沒開的專案只有本機推送前擋得住。
- 這道判定出錯時 pre-push 放行(既有 fail-open),所以紀錄檔壞掉會變成放行;CI 那邊照現在的行為,判定回 2 時 CI 步驟是否算紅要在實作時確認並寫進家節點。
- Maestro flow 與截圖都受裝置狀態影響(通知、鍵盤、系統對話框、狀態列時間),誤擋主要來源;截圖要先在 SM-X710 實測狀態列固定得住(前置步驟)。
- 一次驗收的時間:實驗室 App 上效能 20 輪就約 9 分鐘,加 UI 流程、截圖、記憶體收集會更久;真專案可能到幾十分鐘,時間太長會讓人改走略過檢查(見 RETIRE-IF)。

## 實驗室驗收

在 macrobench-lab 上每一塊各準備「應該擋」與「不該擋」:

- UI 流程:應該擋=按鈕失效不跳頁、清單少一列;不該擋=正常版連跑 5 次都過;偶爾慢一點才出現的畫面要被標成不穩定、不擋。
- 截圖:應該擋=元素位置跑掉、一整塊不見、文字被切;不該擋=只有時間電量變(靠固定狀態列)、同一版本連拍 3 次都相符。只差幾個字抓不到,列為限制。
- 效能與記憶體:應該擋=Java 套件沒 release、C/C++ 套件沒 release、中途閃退(改由 Maestro 驅動);只提醒不擋=注入啟動變慢、每列變慢。
- 擋合併:應該擋=改了 App 程式沒跑驗收就推、跑了沒過、改程式後拿舊紀錄充數、先略過檢查推改程式的提交再推只改文件的提交;不該擋=只改文件、沒過但有人放行、沒跑但有人放行、壓提交或 rebase 後內容沒變。

## 條款

- [S1] 當專案的 `.lumos/android-e2e.json` 缺必填欄位(app_dirs、package、apk、flows)、欄位型別不對、`visual_threshold` 不是有限數或低於 99.5、`package` 含英數字底線與點以外的字元、或任何路徑跳出專案根時,`lumos android-e2e check-config` 應回 2 並印出哪個欄位哪裡壞;設定合格時回 0 [test:t_android_e2e_config_strict]
- [S2] 當計算 App 程式內容指紋時,lumos 應只從指定提交的檔案樹算 `app_dirs` 底下的檔(路徑加內容);目錄外的檔改了指紋不變,目錄內任一檔改一個位元組指紋就變,工作目錄沒提交的改動、檔案列出順序與提交編號都不影響指紋 [test:t_android_e2e_fingerprint]
- [S3] 當判 UI 流程時,`lumos android-e2e judge` 應在回傳碼是 0、報告裡至少一個測試案例而且沒有失敗時才算這支 flow 過;回傳碼 0 但報告零案例、或報告有失敗都算沒過;第一次沒過、重跑那次過了算過並標不穩定 [test:t_android_e2e_judge_ui]
- [S4] 當判截圖比對時,judge 應在畫面的 `visual-check.sh` 回傳碼是 0 時才算過;回傳碼 1 或 2、或缺結果都算沒過並記下原因,不相符時記下相符率與差異圖路徑 [test:t_android_e2e_judge_visual]
- [S5] 當效能結果有退步或毫秒類門檻沒達時,judge 應只寫進紀錄的 notices,不影響 result;記憶體類、閃退或 StrictMode 的 check 列在 failures 時 result 是 fail,列在 skipped 或整段沒門檻可判時 result 是 unjudged;凍結幀沒過或沒判到只寫 notices [test:t_android_e2e_judge_perf_memory]
- [S6] 當任一塊的工具沒跑成(找不到 maestro、裝置斷線、輸出檔不在)時,judge 應把那一塊記成失敗、result 不得是 pass [test:t_android_e2e_judge_tool_failure]
- [S7] 當從分支跟主線的分岔點到被推送提交之間有提交改到 `app_dirs` 底下的檔時,`code-loop check` 的 Android E2E 判定應在找不到被推送提交指紋的紀錄、或紀錄 result 是 fail 或 unjudged 時回 1 擋下,並印出要跑的指令;result 是 pass 或 waived 時放行;這段沒改到 `app_dirs` 時不要求紀錄;專案沒有 `.lumos/android-e2e.json` 時這道判定不跑 [test:t_android_e2e_gate]
- [S8] 當分支先推了改 `app_dirs` 的提交、下一次只推改文件的提交時,Android E2E 判定應照樣要求紀錄 [test:t_android_e2e_gate_whole_branch]
- [S9] 當執行 `lumos android-e2e waive --note <理由>` 時,lumos 應在理由少於 10 個字時回 2;成功時有紀錄就在紀錄加上放行、沒有紀錄就新建一份 result 是 waived 的紀錄,寫下誰、日期、理由,並在治理帳記一筆 android-e2e-waive [test:t_android_e2e_waive]
- [S10] 當分支被壓提交或 rebase、App 程式內容沒變時,Android E2E 判定應照舊認得原本的紀錄 [test:t_android_e2e_gate_survives_rebase]
- [S11] 當 code-loop check 有其他判定會提早放行時,Android E2E 判定應仍然先跑(排在放行早退之前) [test:t_android_e2e_gate_before_early_exit]
- [S12] 當範本腳本 `android-e2e-run.sh` 跑完時,它應把四塊的原始輸出放在同一個 run 目錄的四個子目錄、再呼叫 judge;任一塊中途失敗也要把剩下的跑完並呼叫 judge,不得留下沒有紀錄的半套結果 [test:t_android_e2e_run_script]
- [S13] 當開始實作時,應先在 SM-X710 上實測 Maestro repeat 吃不吃 ${CYCLES} 與 toolkit 狀態列固定得住,結果寫進本計劃 [manual:前置步驟的兩項實測結果寫進〈資料怎麼流〉第 0 步之後]
- [S14] 當在 macrobench-lab 上照〈實驗室驗收〉逐組跑時,每一組的結果應照預期(應該擋的全擋、不該擋的全放) [manual:SM-X710 上逐組跑一次,結果寫進驗證紀錄]
- [S15] 當在 Citrus_KDS 上接 E2E 驗收時,四塊應都跑得起來、紀錄寫得出來,並記下一次驗收實際花多少時間 [manual:KDS 升 benchmark-macro 1.4.1 後在 SM-X710 跑一次,時間與結果寫進驗證紀錄]
- [S16] 當 AI 照 lumos-android-evidence skill 接 E2E 驗收時,skill 應寫明怎麼設定、怎麼跑、紅了怎麼看、怎麼放行,以及 GitHub 要把 CI 設成合併前必須通過 [manual:讀 skill 的 E2E 驗收一節,五件事都寫到]

## 回退

- 判定:專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑,其他判定不受影響。
- 紀錄與放行:`.lumos/e2e-records/` 是新增的檔,刪掉不影響其他功能;放行寫在治理帳的事件只是統計來源,不影響其他判定。
- 程式:新子命令與 `code-loop check` 那一道是新增的,回退就是撤掉那次提交;既有判定的程式碼不改。
