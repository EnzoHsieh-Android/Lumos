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
  - Systems/bound-tests-gate
related:
  - "[[Projects/Android效能判定統計化_計劃]]"
  - "[[Projects/Android記憶體與穩定性驗收_計劃]]"
  - "[[Projects/Android側UI測試綁圖譜工作流_計劃]]"
  - "[[Projects/截圖基準驗收流程_計劃]]"
decisions:
  - content: e2e 段開了記憶體時,macrobench.json 最外層的 stability 段與 stability_scenarios 也算進指紋(改 S2 的「其他段都不影響指紋」)
    id: d1
    context: 代碼審 code-e2e-by-feature r4 正確性席:記憶體情境的 driver、cycles 改弱後指紋不變,同一版舊的通過紀錄照樣算數;計劃〈查證紀錄〉的原則是驗收的範圍或標準變了就該重驗,門檻檔本來就算進指紋。考慮過:照舊不算(記憶體標準能在指紋外改弱);整份 macrobench.json 都算(改效能容差、results_dirs 也要重跑實機,太嚴)
    why_chosen: stability 段與情境決定記憶體這塊驗得多嚴,跟門檻檔同一類;只在 e2e 段開了記憶體時才算,沒開的專案指紋不變。代價:開了記憶體的專案升上這版後,既有紀錄全部對不上、要重跑一次
    decided: 2026-10-26
    valid: true
---
# Android端到端驗收_計劃

白話:Android App 改完、推送之前,在本機接著實機跑一次「端到端驗收」:UI 流程走不走得完(Maestro flow)、畫面跟人核可過的基準圖一不一樣(截圖比對)、效能有沒有變慢、記憶體有沒有洩漏或閃退。跑完寫一份綁在「這一版 App 程式與驗收素材的內容」上的查證紀錄,推送前的 `code-loop check` 檢查這一版有沒有一份通過(或有人放行)的紀錄,沒有就擋推送。第一版只擋本機推送,CI 上擋合併另開一案(見 REVISIT)。毫秒類效能(啟動時間、每幀耗時、凍結幀)第一版只提醒、不擋,等 [[Projects/Android效能判定統計化_計劃]] 的第 1、3、4 條(20 輪、同場比較、太吵指標只列出)都上線再改成擋。2026-10-24 Enzo 提「整合 Maestro,將效能測試、UI 測試成為 Android 端 E2E 的驗收標準」;2026-10-25 對話裡逐段確認了範圍、擋法、做法與三段設計,設計審 r1 之後又裁了放行權與 CI 範圍。

PRIOR-ART: Maestro CLI(`maestro test` 跑 flow,`--format junit --output` 出測試報告、`-e KEY=VAL` 傳參數、`--udid`/`--device` 指定裝置,內建 `assertScreenshot`);使用者自己的 maestro-visual-toolkit(github.com/EnzoHsieh-Android/maestro-visual-toolkit,本機在 ~/harness/maestro-visual-toolkit:人核可基準圖、門檻用環境變數 THRESHOLD(不准低於 99.5)、紅框差異圖、狀態列固定、裝置與 adb 路徑寫在安裝時產生的 `.maestro/visual-env.sh`、用 `.maestro/.lock-<裝置>` 鎖,原本只在模擬器驗過;本 repo 的 [[Projects/Maestro截圖基準比對_調研]] 與 [[Projects/截圖基準驗收流程_計劃]]);Lumos 既有的 Maestro flow 綁功能筆記(`[test:maestro:<名>]`,綁 flow 的 `name:`,[[Projects/Android側UI測試綁圖譜工作流_計劃]]);既有的 Macrobenchmark 判定(`lumos macrobench`,[[Systems/macrobenchmark-adapter]])與記憶體穩定性收集([[Systems/android-stability-collector]]);code-loop check 既有的安全證據判定([[Systems/安全證據閘]]:設定只讀主線版、主線用它挑主線與分岔點的那套算法、判不清就擋,不走 fail-open)與表態判定(證據一律對被推送提交的檔案樹驗);新增告警閘用環境變數整道關掉、留帳的做法;既有的終端確認 `_confirm_tty`(回「答了 y」「答了別的」「沒人能答」三種)、原子寫入 `_write_lf`、獨佔鎖檔 `_excl_lock_try`、工作目錄有沒有改動的 `_dirty_non_bookkeeping`、判斷在不在 CI 的 `_in_ci`。借用:以上全部;自建只有一支串四塊的範本腳本、一個彙整判定與寫紀錄的子命令、code-loop check 裡多一道判定、`lumos macrobench` 多一個指定結果目錄的旗標與 `e2e` 段的格式檢查。不選:Maestro Cloud 與 Firebase Test Lab 這類雲端裝置(跟「本機實機跑」的決定衝突,雲端裝置的效能不能當基準);Gradle Managed Devices 的模擬器(同上)。
RETIRE-IF: 連續兩個真實專案跑滿三個月,掃那兩個專案的 `.lumos/e2e-records/`:有放行的指紋數多過「歷次結果裡有過 pass」的指紋數,或 AI 放行佔全部放行的一半以上,就把擋推送降回只提醒。
REVISIT:2027-03-31 查效能判定統計化第 1、3、4 條上線了沒;都上線就把毫秒類效能從只提醒改成擋,條款另開
REVISIT:2026-12-31 第一版只擋本機推送:評估加 PR 觸發的 CI 步驟範本(用 PR 分支頂端算指紋、主線分岔點到頂端的樹差異判要不要紀錄),讓專案能把它設成合併前必須通過;另評估 tag 推送要不要也跑這道
REVISIT:2026-12-31 回頭看治理帳 android-e2e 的 skipped(用環境變數整道關掉)次數,多過擋下次數的一成就查是哪種誤擋逼人關掉

WHY:驗收沒過就擋推送、可以放行 [出處:2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」] [因:驗收沒過的程式不該默默推上去;實機驗收會誤擋,要留一條有紀錄的出口] [不選:只提醒(跟「成為驗收標準」的目的不符);不准放行(誤擋時只能改走略過檢查,沒有紀錄)]
WHY:AI 也能放行,但標成 AI 放的,而且每次推送、開場與體檢都把還沒人看過的 AI 放行列出來 [出處:2026-10-25 設計審 r1 後 Enzo 選「AI 能放行,但要通知你」] [因:無人看顧時驗收會因裝置狀態誤擋,完全不准 AI 放行會讓流程卡死;但 AI 最省力的路就是放行,要看得到] [不選:只有人能放行(無人看顧時卡死);照舊 10 字理由就放行(事後分不出是人還是 AI);AI 放行累積幾筆就擋(Enzo 裁的是「能放行」,累積就擋等於收回)] [代價:「通知」是在人會看的地方列出來,不是推播;人幾天不開會談就幾天看不到]
WHY:第一版只擋本機推送,CI 擋合併另開一案 [出處:2026-10-25 設計審 r1 後 Enzo 選「第一版只擋本機推送」;原本 10-24 選的「CI 驗收據」延後] [因:現行 CI 只在推到主線時跑 code-loop check,PR 上不跑;推到主線時合併提交的樹混了別人的改動,指紋跟分支上驗收時不同;做到 PR 要另寫 PR 事件的步驟範本,範圍大] [不選:第一版就做 PR 步驟(範圍大、要先把本機這道跑穩)] [代價:略過推送前檢查就擋不住,見 REVISIT]
WHY:判不清就擋,不走 fail-open [出處:設計審 r2 整合席指出最像的鄰居安全證據閘判不清就擋] [因:這是一道擋推送的判定,出錯時默默放行等於整道關掉;安全證據閘同樣排在放行早退之前、同樣判不清就擋] [不選:照 lint-new 那類只提醒的閘接住錯誤放行(那類閘本來就不擋)] [代價:工具自己的毛病會擋住推送;出口是環境變數整道關掉一次,有留帳]
WHY:做法採「範本腳本碰裝置、lumos 只判定與記帳」 [出處:2026-10-25 Enzo 選做法 A] [因:跟已上線的記憶體收集同一個分工(lumos 不碰裝置,連「裝置有沒有連上、有沒有鎖屏」這類開跑前檢查也放在範本腳本)] [不選:lumos 自己操作裝置(要重寫裝置控制、逾時、收尾)] [代價:範本腳本最後會呼叫 lumos android-e2e judge,跑驗收的那台機器要裝相容的 lumos;找 lumos 的方式照收集腳本(腳本旁的 `../lumos`,用 lumos 自己的 Python 版本底線)]
WHY:紀錄綁「App 程式與驗收素材的整批內容指紋」,不綁提交編號、也不逐檔列在紀錄裡比 [出處:2026-10-25 Enzo 確認第二段;設計審 r1 架構對齊席要求寫明跟安全證據逐檔比法的差別] [因:壓提交、rebase 之後內容沒變,綁提交編號的留痕會失效、要重跑十幾分鐘的實機驗收;安全證據閘的逐檔比法適合收據列出少數幾支檔,這裡要涵蓋整個 App 程式目錄(可能上萬檔),逐檔列進紀錄太大,整批算一個指紋就夠回答「有沒有任何一支變了」] [不選:綁提交編號(代碼審留痕就因此重做過好幾次);逐檔列進紀錄比(紀錄太大)]
WHY:指紋用被推送提交自己的 `e2e` 段選檔,要求跑哪幾塊則照主線版 [出處:設計審 r2 正確性、守衛、整合三席] [因:分支加了新 flow 或改了 `app_dirs`,用主線版選檔會跟分支上驗收時算的對不上、永遠找不到紀錄;但被推送的提交不能自己把驗收改弱,所以另外核對紀錄裡跑過的塊有沒有涵蓋主線版要求的] [不選:兩邊都用主線版(改設定的分支永遠過不了);兩邊都用分支版(同一個提交就能把驗收關掉)]
WHY:E2E 紀錄放 `.lumos/e2e-records/`,不放進 skill 的收據目錄 [出處:設計審 r1 架構對齊席要求寫明] [因:收據 `.lumos/receipts/<run-id>/` 是逐層診斷的證據,一次診斷一份、給人與 AI 重跑查詢;E2E 紀錄是推送檢查的輸入,一個指紋一份、要能用指紋直接找到] [不選:放進收據(判定要掃所有收據找指紋,收據格式也要為判定加欄位)]
WHY:Maestro flow 第一次失敗自動重跑一次,第二次過算過但紀錄標不穩定 [出處:2026-10-25 Enzo 確認第一段] [因:Maestro 常因動畫、載入時間偶發失敗;不留標記又會把不穩定的 flow 藏起來] [不選:不重跑(誤擋);重跑到過為止(藏住真問題)]
WHY:截圖比對照現狀進第一版,不另外遮掉狀態列 [出處:2026-10-25 前置實測後 Enzo 選「照現狀進第一版」] [因:三星平板時鐘與日期固定不住,但差異約 0.004%,遠小於 99.5% 門檻容許的 0.5%,實際不會誤擋] [不選:比對時遮掉狀態列(要先查 Maestro 有沒有現成裁切、沒有就得改 toolkit);第一版不做截圖(少掉一塊驗收)] [代價:`visual_threshold` 設到 99.99 以上會被時鐘跳分鐘誤擋;日期換天也一樣]
WHY:毫秒類第一版只提醒 [出處:2026-10-25 Enzo 選「毫秒類先只提醒」;[[Verification/2026-10-24_效能判定規則實機評測]]] [因:毫秒數字跨時段會漂,判定規則還沒校準完] [不選:四塊全擋(誤擋多)]

## 設定(`.lumos/macrobench.json` 的 `e2e` 段)

跟記憶體與穩定性一樣,放進既有的 `.lumos/macrobench.json` 當一段,不另開設定檔。格式檢查併進既有的 `lumos macrobench --check-config`(讀設定的那支函式多一段 `e2e` 的檢查;只有 `e2e` 段、沒有 `results_dirs` 也沒有 `stability` 段的檔要能通過)。推送檢查「要不要跑、要求跑哪幾塊」只照主線那一版的這一段(跟安全證據閘「設定只讀主線版」同一個理由:被推送的提交不能自己決定要不要被檢查);指紋選哪些檔則照被推送提交自己的這一段(見〈資料怎麼流〉第 4 步)。

- `app_dirs`(必填,至少一項):App 程式的目錄或檔,相對專案根(例 `["app", "gradle/libs.versions.toml", "settings.gradle.kts"]`);每一項在那個提交的檔案樹裡都要存在,不得包住 `.lumos/`。目錄以「整段路徑」比對(`app/src` 不含 `app/src2`)。
- `exclude`(選填):`app_dirs` 底下不算進指紋的子路徑;沒寫時預設排除每個模組的 `src/test/` 與 `src/androidTest/`(只改單元測試不用重跑實機)。
- `package`(必填):App 套件名,規則跟收集腳本一樣;有 `stability` 段時兩邊要一致。`adb_serial` 同理(選填)。
- `build`(必填):建 APK 的指令(例 `./gradlew :app:assembleBenchmark`);`apk`(必填)是建出來的 APK 路徑。
- `flows`(必填,至少一支):驗收用的 Maestro flow 路徑;截圖用的 flow 不要放這裡(toolkit 的截圖 flow 註解寫明不能跟其他 flow 一起全跑)。每支 flow 的「名」= 相對專案根的路徑去掉副檔名、`/` 換成 `__`(例 `.maestro/login.yaml` → `.maestro__login`),兩支同名回 2。
- `visual`(選填):截圖比對的畫面名清單,照 toolkit 慣例帶 `_visual` 後綴(flow 是 `.maestro/<畫面名>.yaml`、基準圖是 `.maestro/baseline/<畫面名>.png`);`visual_threshold` 選填、預設 99.5,要是 99.5 到 100 之間的數字(傳給 toolkit 時寫成一般小數,不寫成科學記號)。用之前要先照 toolkit 的 `install.sh --platform android --device <序號> --app-id <套件名>` 裝好。
- `macrobench`(選填,預設 false):要不要跑效能這塊;要的話 `macrobench_cmd` 是跑 Macrobenchmark 的指令。
- `stability`(選填,預設 false):要不要跑記憶體與穩定性這塊;要的話用同檔既有的 `stability` 段設定(驅動指令換成 Maestro flow),`stability_checks` 列這一塊要求的 check(預設 native_unreachable、java_growth、instances、peak_vitals、exits、strictmode),門檻檔 `.lumos/macrobench-thresholds.json` 裡每一個都要有寫了 check、而且 `scenario` 等於 `stability` 段情境名的條目,缺一個回 2。
- 驗收素材:整個 `.maestro/` 目錄(驗收 flow、它們用 `runFlow` 叫的共用 flow、`config.yaml`、toolkit 的腳本與基準圖;toolkit 寫進 `.gitignore` 的差異圖與鎖不在檔案樹裡)、`flows` 裡不在 `.maestro/` 底下的檔、門檻檔、這一段設定本身,都算進指紋(見〈查證紀錄〉);換基準圖、改共用 flow 或改門檻都要重跑。

## 第一次接入的順序

1. 裝 Maestro CLI(2.8 以上);要截圖的話照 toolkit 的 README 裝進專案、在實機上把每個畫面開到定位、人看過再用 `.maestro/visual-record.sh <畫面名>` 錄基準圖,基準圖跟 flow 一起開 PR 給人看。
2. 要效能或記憶體的話,先照既有說明接好 `lumos macrobench`(基準、門檻)與收集腳本(`stability` 段、門檻檔的 check 條目)。
3. 寫 `e2e` 段,跑 `lumos macrobench --check-config`(驗格式)與 新範本腳本的 `android-e2e-run.sh --preflight`(驗環境:maestro 在不在、toolkit 腳本與基準圖在不在、裝置有沒有連上而且沒鎖屏、產物目錄有沒有被 git 忽略、settings.gradle 列了卻不在 `app_dirs` 的模組),兩個都過再跑第一次驗收。
4. 段落合進主線之後,推送檢查才開始要求紀錄。

## 一次驗收跑什麼(四塊)

| 塊 | 怎麼跑 | 怎麼判 | 沒過時 |
|---|---|---|---|
| UI 流程(必有) | `flows` 每支 `maestro test --format junit --output <run>/ui/<名>.try1.xml`(有序號時加 `--udid`);回傳碼不是 0 再跑一次寫 `.try2.xml`(回傳碼 0 但報告零案例或有失敗,是 flow 或報告本身的問題,重跑結果一樣,直接算沒過) | 回傳碼是 0 而且報告裡至少一個測試案例、沒有失敗才算這一次過;第一次過→過;第一次沒過、第二次過→過、標不穩定;兩次都沒過→沒過 | 擋 |
| 截圖比對(有 `visual` 才跑) | 每個畫面 `THRESHOLD=<visual_threshold> MAESTRO_DEVICE=<序號> .maestro/visual-check.sh <畫面名> <run 的絕對路徑>/visual/<畫面名>`,標準輸出與錯誤輸出各存一個檔 | 回傳碼 0 算過;1(不相符或環境問題)與 2(缺基準圖、參數錯)都算沒過,原因與(不相符時才有的)相符率從存下的輸出讀 | 擋 |
| 記憶體與穩定性(`stability: true` 才跑) | 收集腳本用同一個 run-id 跑(它把結果寫在 run 目錄最上層),再 `lumos macrobench --json --stability <run>/stability.json` | 只看門檻條目帶 check、而且 check 在 `stability_checks` 裡的:在 threshold_failures→沒過;在 threshold_skipped、或整段 stability_unjudged、或那個 check 根本沒出現在任何清單→沒判到;frozen 與沒帶 check 的門檻只寫 notices;收集腳本或 `lumos macrobench` 回非 0→這塊沒跑成 | 擋(沒判到也擋;frozen 只提醒) |
| 毫秒類效能(`macrobench: true` 才跑,排最後) | 照 `macrobench_cmd` 跑完,把這次開始後才產生的結果檔複製到 `<run>/macrobench/`,`lumos macrobench --json --results-dir <run>/macrobench`(新旗標:這次只讀這個目錄,設定沒有 `results_dirs` 也能跑;基準照舊用專案的) | 退步、毫秒類門檻沒達、沒有基準、輪數不足都只寫進 notices;這塊沒跑成也只寫 notices | 只提醒 |

效能排最後:Macrobenchmark 的 Gradle 指令常會自己裝上、跑完再移除測試用的 App,排在記憶體那塊前面會讓後面沒有 App 可跑;裝置上那份 APK 的 sha256 在效能這塊之前讀第二次。

## 資料怎麼流

0. 前置(實作第一步,做完才寫範本腳本):在 SM-X710 上實測兩件待驗事項,結果寫進本計劃再往下:Maestro flow 的 `repeat` 的 `times` 吃不吃 `${CYCLES}`(不行就改用 `while` 加計數,並改 skill reference 的 Maestro 驅動範例);toolkit 的狀態列固定在實機上固定得住(固定不住先問 Enzo 要改截圖範圍還是另找做法,截圖這塊在那之前不進第一版)。
   - 前置實測結果(2026-10-25,SM-X710、Maestro 2.10.0):
     - repeat 吃變數:可以。`times: ${CYCLES}` 帶 `-e CYCLES=3` 時重複 3 次、斷言計數等於 3 通過;帶 5 時重複 5 次、同一個斷言失敗。skill reference 的驅動範例不用改。
     - 狀態列固定:部分可以。照 toolkit 的展示模式指令,通知圖示被隱藏、電量與 Wi-Fi 不動,但三星的時鐘不吃展示模式,65 秒內從 13:43 變 13:45,日期照常顯示。頂端 60 列的差異從沒開展示模式的 1009 個像素降到 166 個,集中在時鐘那一格;整張 2560×1600 畫面約差 0.004%,遠小於 99.5% 門檻容許的 0.5%。Enzo 裁照現狀進第一版(見 WHY)。
1. 範本腳本 `android-e2e-run.sh`(工具鏈範本,跟收集腳本放一起),在專案根跑:
   - 開跑前檢查:工作目錄除了簿記檔與被 git 忽略的檔,沒有任何未提交的改動、也沒有沒加進版控的新檔(用 `_dirty_non_bookkeeping` 連沒追蹤的檔一起算;Gradle 建置吃整個工作目錄,不只 `app_dirs`);裝置連上而且沒鎖屏;maestro 在;要截圖時 toolkit 腳本與基準圖在;同一台裝置沒有另一次驗收在跑。
   - 裝置鎖:放在 `~/.cache/lumos/android-e2e-lock/<序號>`(不放工作目錄,兩個工作樹對同一台裝置也擋得住),照 `_excl_lock_try` 寫入程序編號;鎖在、但寫的程序已經不在了(被 kill -9、斷電),印一句「清掉上次留下的鎖」再接手。toolkit 的 `.maestro/.lock-<序號>` 也一樣:確認沒有 visual-check.sh 程序在跑才清。
   - run-id 預設 `e2e-<年月日>-<時分秒>`,run 目錄 `.lumos/artifacts/android/<run-id>/`(產物目錄必須被 git 忽略):ui、visual、macrobench 三個子目錄,記憶體與穩定性的輸出照收集腳本放在 run 目錄最上層。
   - 依序:記下開跑時的 HEAD 提交編號;照 `build` 建 APK、裝上去並記下裝置上實際安裝那份的 sha256;UI 流程、截圖、記憶體與穩定性;再讀一次裝置上那份的 sha256(中途被換掉,這次記成沒跑成);最後效能。
   - `<run>/steps.json`(judge 讀它):`schema`(第一版是 1)、開跑時的 HEAD、每一步的回傳碼、開始結束時間、標準輸出與錯誤輸出存在哪、每次嘗試的報告路徑;任一步失敗也繼續把剩下的跑完;被 Ctrl-C、TERM 或關掉終端(HUP)中斷時,寫下「中斷」再呼叫 judge。
2. 最後呼叫 `lumos android-e2e judge <run 目錄>`:讀 `steps.json`(schema 不認得就回 2)與四塊的輸出、照上表判;目前 HEAD 跟開跑時不同、或工作目錄有開跑前檢查那種改動,就拒絕寫紀錄並回 2(驗的不是這一版)。用 HEAD 提交自己的 `e2e` 段算指紋,寫進 `.lumos/e2e-records/<指紋>.json`;終端印每一塊的結果、沒過的原因與證據路徑,最後一行印要提交的那支紀錄檔與指令。
3. 紀錄要提交進版控;`.lumos/e2e-records/` 跟其他簿記檔一樣,在代碼審留痕之後提交不會讓留痕失效(實作時把它加進簿記目錄清單,並看過那份清單的其他用處)。
4. 推送前 `code-loop check` 多一道「Android E2E 驗收」判定:
   - 在 CI 裡(`_in_ci`)不跑這道,印一句「第一版只在本機推送時判」;環境變數 `LUMOS_SKIP_ANDROID_E2E` 有設時整道關掉,記一筆治理帳 skipped(照新增告警閘 `LUMOS_SKIP_LINT_NEW` 的做法)。
   - 主線:照安全證據閘那套挑主線(推的是分支:主線候選裡挑含分岔點、歷史最長的那條;推的就是主線本身:用推送前的主線位置);主線版沒有 `e2e` 段→不跑。
   - 何時要求:分岔點 = 被推送提交跟主線的 `git merge-base`(不是這次推送的範圍起點:分支上次推上去的提交沒驗收,這次只改文件也照樣要求);選檔設定用被推送提交的 `e2e` 段(被推送提交刪掉了這一段,改用主線版的);用同一份設定算分岔點與被推送提交兩端的指紋,不同才要求(看兩端的樹,不逐提交看:改了又改回來就不要求)。
   - 怎麼判:從被推送提交的檔案樹讀 `.lumos/e2e-records/<被推送提交的指紋>.json`(不讀工作目錄);依序驗 schema、指紋欄位等於檔名、有放行→過;沒放行就看最近一次結果:result 是 pass 而且跑過的塊涵蓋主線版要求的(主線版每支 flow、每個畫面、要了的記憶體 check,被推送提交沒有改名或刪掉的都要在紀錄裡)→過;其他→擋,印出哪一塊沒過或少了哪一塊、紀錄路徑、要跑的指令(重跑驗收,或放行)。工作目錄裡有這個指紋的紀錄、只是還沒提交,訊息改成「提交這支紀錄」並印出路徑。
   - 判不清就擋(回 1),跟安全證據閘一樣不走 fail-open:紀錄讀不懂(JSON 壞掉、schema 比這版 lumos 新、result 不是認得的值、指紋欄位對不上)、主線找不到、主線版的 `e2e` 段本身不合格、被推送提交的 `app_dirs` 有一項不存在、或其他內部錯誤,都擋並說原因;出口是 `LUMOS_SKIP_ANDROID_E2E` 關掉一次。
   - 每次跑這道(過或擋都算),只要被推送提交的紀錄裡有還沒人看過的 AI 放行,就多印一行「有 N 筆 AI 放行還沒人看過」與看的指令。
   - 位置與接線:跟安全證據判定一樣排在所有放行早退之前;擋下種類 `android_e2e`,接進 `_cl_say_block`、`_codeloop_kg_finish` 的明細、pre-push 的擋下原因對照表 `pp_cl_reason` 與逃生路那段文字、ci.yml 的擋下說明;對照表句子的正本在 [[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉5,測試檔的 `_PPC_KIND_SENTENCES` 一起加(改測試檔要 Enzo 簽章);擋下訊息不得含 pre-push 用來記逃逸帳的那兩串字。
   - tag 推送只跑安全證據,這道不跑(見 REVISIT)。
5. 放行 `lumos android-e2e waive [<指紋>] --note "<理由>"`(預設放行 HEAD 提交的指紋):
   - 理由去掉空白後至少 10 個字。
   - 用 `_confirm_tty` 問一次「確定放行嗎」:答了 y → 記成人放行(誰取 git 的 user.name,沒設就取登入帳號);答了別的 → 不放行、回 1;沒有互動終端(沒有控制終端時立刻回,有終端但沒人答時等 `LUMOS_TTY_TIMEOUT` 秒,預設 30)→ 記成 AI 放行(誰記 `ai`)。
   - 放行寫在紀錄的 `waivers` 清單(只增不刪;同一個指紋再放行一次就多一筆;之後重跑 judge 不會蓋掉);沒有紀錄就新建一份只有放行的紀錄(`runs` 是 null、`history` 是空清單)。judge 與 waive 的「讀出整份、合併、整份寫回」包在鎖裡(照 lint-waive 的讀改寫鎖),寫入用 `_write_lf`。
   - 治理帳記一筆:閘名 `android-e2e`、事件種類 `waived`(閘名登記進已知閘名清單),附人或 AI、指紋、理由。
   - `lumos android-e2e waive --list` 列出所有紀錄裡的放行與有沒有被人看過。
   - 通知:除了上面每次推送那一行,`lumos doctor` 把還沒人看過的 AI 放行列成提醒(不讓 `doctor --ci` 變紅);`lumos enforcement` 多一列「android-e2e AI 放行待看」,有待看時標成沒生效,開場提示就會印出來(專案沒有 `docs/*-knowledge` 時開場提示不印,只剩推送那一行與 doctor)。人用 `lumos android-e2e waive --ack <指紋>` 標成看過(同樣要終端確認,只有答 y 才算),改完的紀錄要提交,別台機器才看得到。

## 查證紀錄長怎樣

- `schema`:格式版本(第一版是 1);判定遇到比自己新的版本就擋,請人更新 lumos。
- `fingerprint`:對一個提交的檔案樹,用那個提交的 `e2e` 段,取 `app_dirs` 底下(扣掉 `exclude`)與驗收素材的每一個項目,用 `git ls-tree -r -z` 的 mode、型別、物件編號與路徑,依路徑的位元組順序排好,每一項寫成「mode、物件編號、路徑」三段、段與段之間用 NUL 分開、每項後接換行;最後再接一行「`e2e-config`、NUL、`e2e` 段的 sha256」(段落先寫成鍵排序、不留空白、不轉義中文的 JSON 再算),整串算 sha256。只取 `e2e` 段不取整個 `macrobench.json`:改效能基準或 `results_dirs` 不用重跑 E2E。用 git 物件編號而不讀檔案內容:上萬檔的目錄也是一次 git 呼叫、子模組用它記的提交編號、符號連結用它指向的路徑、Git LFS 用指標檔,改權限(mode)也會讓指紋變。
- `runs`:最近一次整套跑的完整結果(每一次整套 judge 覆蓋這一欄,按功能跑不碰它,不動 `waivers` 與 `history`;只有放行的紀錄是 null):result(pass、fail、unjudged)、run-id、開始與結束時間(本機時區、帶時差的 ISO 格式)、裝置型號與系統版本、建出的 APK 與裝置上實際安裝那份的 sha256、判定的提交編號、四塊明細(每支 flow 的結果與是否不穩定、每個畫面的結果與原因、效能與記憶體每條的結果與原因)、`notices`(只提醒的項目)。
- `history`:每次 judge 追加一筆(result、run-id、結束時間;按功能跑的那筆另帶 `kind: feature` 與挑到的情境),只增不刪;RETIRE-IF 從這裡數時只數沒有 `kind` 的整套那幾筆,按功能的通過不算整版驗過。
- `feature_runs`:按功能跑的結果,`功能.情境` → result、complete、skipped、每項結果、run_id、ended、commit(見〈按功能與使用情境跑〉);整套跑不碰它。整套跑比某個情境的 `feature_runs` 晚而且沒過時,兩邊會說不同的話:推送前檢查比兩邊的結束時間,取較新的那個(見〈推送前怎麼按功能判〉)。
- `waivers`:每筆放行的人或 AI、誰、時間、理由、有沒有被人看過。
- 寫一半被殺留下的 `<指紋>.json.<…>.tmp-wlf` 暫存檔,判定只讀 `<指紋>.json`,不受影響。
- 原始檔只在本機;紀錄只放摘要與數字。
- 改了 `app_dirs`、`exclude`、驗收素材或 `e2e` 段本身,指紋就全變、舊紀錄都對不上,要重跑一次:這是刻意的(驗收的範圍或標準變了就該重驗),不做舊紀錄遷移。舊紀錄檔不自動刪,一份只有幾 KB;run 目錄在被 git 忽略的產物目錄,清理照產物目錄既有做法由人清;每個記憶體情境另有 `<run-id>.<情境>` 目錄(錄製檔與日誌),整套跑一次就多 1+情境數份,收集腳本只清七天前的記憶體快照,其餘也由人清。
- 同一個指紋重跑、這次沒過,會蓋掉先前的 pass:最近一次的結果才算數(重跑出現的失敗就是真訊號),先前通過的次數留在 `history`。

## 這次要改到的地方

- 新子命令 `lumos android-e2e`(judge、waive)與它的家 `Systems/android-e2e-acceptance`(新開;code-loop check 那一道的細節也寫在這裡,跟安全證據閘、表態閘各有自己的家一樣)。
- `code-loop check` 多一道判定:[[Systems/pitfalls-code-loop]] 只加一行連結,不寫細節。
- `lumos macrobench`:讀設定那支函式加 `e2e` 段的格式檢查、接受只有 `e2e` 段的設定檔;加 `--results-dir`(設定沒有 `results_dirs` 也能跑):寫進 [[Systems/macrobenchmark-adapter]],那篇另補一句「`e2e` 段由 Systems/android-e2e-acceptance 負責」。
- pre-push 的擋下原因對照表與逃生路文字、ci.yml 的擋下說明:寫進它們的家 [[Systems/bound-tests-gate]];對照表句子同步改 [[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉5 的正本與測試檔的 `_PPC_KIND_SENTENCES`。
- 簿記目錄清單加 `.lumos/e2e-records/`:寫進 [[Systems/pitfalls-code-loop]] 那一行。
- 治理帳已知閘名加 `android-e2e`;`lumos doctor`、`lumos enforcement` 列出沒人看過的 AI 放行。
- 新範本腳本 `android-e2e-run.sh` 放 `scripts/templates/`(含 `--preflight`),家是 `Systems/android-e2e-acceptance`;收集腳本不改。
- skill lumos-android-evidence:reference.md 的 Maestro 驅動範例照前置實測修正;補「E2E 驗收」一節(接入順序、怎麼跑、紅了看哪裡、怎麼放行、AI 放行會被列出來、怎麼整道關掉一次)。
- 實驗室專案 macrobench-lab 加 Maestro flow、截圖基準、可注入的 UI 錯與 `e2e` 段,驗收用。
- 試點真專案:Citrus_KDS(接入時從零建 `.maestro` 與 macrobench 設定)。已知坑:KDS 在 SM-X710 用 benchmark-macro 1.2.4 跑不起來,實驗室用 1.4.1 可以([[Verification/2026-10-23_macrobench實機端到端]]);接 KDS 時要升版,改 KDS 依賴前先問 Enzo。

## 不做

- 毫秒類效能擋推送(等統計化計劃第 1、3、4 條,見 REVISIT)。
- CI 上擋合併、tag 推送跑這道(見 REVISIT)。
- iOS 端;雲端裝置或 CI 上跑實機驗收。
- 驗證紀錄真的是在實機跑出來的、AI 不會冒充人回答終端確認:照 Lumos 的威脅模型(單人、AI 依序操作,不防刻意偽造)不另外防。
- 舊版 lumos 沒有這道判定、推送時不會發現:lumos 經符號連結更新,一台機器只有一份,不另加版本探測。
- 改收集腳本。

## 實務隱患

- 已排除:金流:只讀驗收輸出與程式檔,不碰交易。
- 已排除:對外送出:驗收在本機跑,紀錄只進專案自己的 git,不送到外部服務。
- 已排除:不可逆:紀錄與放行都是新增的檔與帳,放行只增不刪;刪掉紀錄就回到沒驗收的狀態;不刪除任何專案檔(只清確認沒有程序在用的鎖)。
- 守衛面:這是一道新的擋推送判定,誤擋會卡住開發、漏擋會讓沒驗收的程式推上去;兩邊都要有實驗室證據(見〈實驗室驗收〉)。
- 第一版略過推送前檢查就擋不住;CI 不補查(見 REVISIT)。
- `app_dirs` 漏列影響 App 行為的檔(其他模組、根目錄 gradle 檔、混淆設定),改了它們不會要求重驗;範本腳本的 `--preflight` 對 settings.gradle 列出、卻不在 `app_dirs` 的模組印提醒。
- Maestro flow 與截圖都受裝置狀態影響(通知、鍵盤、系統對話框、狀態列時間),是誤擋主要來源;截圖要先在 SM-X710 實測狀態列固定得住(前置)。
- 一次驗收的時間:實驗室 App 上效能 20 輪就約 9 分鐘,加其他三塊更久;真專案可能到幾十分鐘,時間太長會讓人放行或略過檢查(見 RETIRE-IF)。
- 判不清就擋:工具自己的毛病也會擋住推送,出口是環境變數關掉一次(見 REVISIT 回頭看次數)。
- 按功能放行:一支歸在功能 A 底下、其實別的功能也在用的程式,沒標進 `shared_paths` 時,改壞別的功能不會被擋;靠專案自己把共用程式列進 `shared_paths`,整套跑仍是推上主線前最後一次全面驗(見下一行回頭條件)。
REVISIT:2027-01-31 數治理帳的 passed-by-feature 筆數,與之後整套跑在沒驗到的功能紅的次數,照 RETIRE-IF 判要不要撤掉按功能這條路
- 截圖與 UI 報告可能拍到畫面上的使用者資料:只留在被 git 忽略的產物目錄,`--preflight` 驗產物目錄有被忽略。

## 實驗室驗收

在 macrobench-lab 上每一塊各準備「應該擋」與「不該擋」,每一組都要照預期:

- UI 流程:應該擋=按鈕失效不跳頁、清單少一列(兩次都沒過);不該擋=正常版連跑 5 次都過;偶爾慢一點才出現的畫面要被標成不穩定、不擋。
- 截圖:應該擋=元素位置跑掉、一整塊不見、文字被切;不該擋=只有時間電量變、同一版本連拍 3 次都相符。只差幾個字抓不到,列為限制。
- 效能與記憶體:應該擋=Java 套件沒 release、C/C++ 套件沒 release、中途閃退(改由 Maestro 驅動);只提醒不擋=注入啟動變慢、每列變慢。
- 擋推送:應該擋=改了 App 程式沒跑驗收就推、跑了沒過、改程式後拿舊紀錄改檔名充數、換了基準圖沒重跑、改了共用 flow 沒重跑、同一個提交裡把 `stability` 關掉或拿掉一支主線要求的 flow、分支上次沒驗收就推上去這次只改文件、驗收跑到一半提交了新的程式;不該擋=只改文件、只改單元測試、沒過但有人放行、壓提交或 rebase 後內容沒變、改了又改回來、分支新加一支 flow 並跑過驗收、紀錄已產生但還沒提交時訊息指出要提交。
- 放行:AI 放行會出現在推送那一行、doctor 與 enforcement;人答 n 不會產生放行;人標看過後不再列。
- 鎖:kill -9 中斷後下一次驗收能接手;兩個工作樹對同一台裝置同時開跑,後到的被擋。

## 按功能與使用情境跑(開發中檢測)

2026-10-26 Enzo 要的:開發中不跑整套,只跑當下開發的那個功能,或那個功能的某一個使用情境;四塊(UI 流程、截圖、效能、記憶體與穩定性)都要能按功能挑;整個檢測過程要能彈性調用、能自動化,而且每次都有檢測紀錄。這一節取代 2026-10-26 稍早寫的「--only 按塊挑」(按 ui、visual 這種大類挑,Enzo 說粒度不對)。

狀態:2026-10-26 Enzo 說「直接開工」,沒另開設計審,已實作在 EnzoHsieh-Android/e2e-only 分支,走代碼審;開發完在實驗室實跑。

### 一個使用情境是什麼

| 塊 | 一個使用情境 |
|---|---|
| UI 流程 | 一支 Maestro flow |
| 截圖 | 一個畫面的截圖 flow(toolkit 的 `<畫面>_visual`) |
| 效能 | 一個 Macrobenchmark 測試方法(例如 `ScrollBenchmark#scrollList`) |
| 記憶體與穩定性 | 一個反覆開關畫面的驅動情境(例如播放器畫面開關) |

### 功能對照表(設定的單一來源)

`.lumos/macrobench.json` 的 `e2e` 段加 `features`:每個功能列它的程式路徑與使用情境,每個情境列它的四種東西。flow 與截圖畫面要是整套清單(`flows`、`visual`)裡有的;效能寫測試方法名;記憶體寫 `stability_scenarios` 裡的情境名。

```json
"features": {
  "player": {
    "paths": ["app/src/main/java/com/example/mblab/PlayerActivity.kt", "app/src/main/java/com/example/mblab/sdk/"],
    "cases": {
      "open-close": {"flows": [".maestro/player_open.yaml"], "visual": [], "macrobench": [],
                     "stability": ["player_cycle"]}
    }
  },
  "list": {
    "paths": ["app/src/main/java/com/example/mblab/MainActivity.kt"],
    "cases": {
      "scroll": {"flows": [".maestro/list.yaml"], "visual": ["main_visual"], "macrobench": ["ScrollBenchmark#scrollList"],
                 "stability": []}
    }
  }
}
```

- 不另外用 Maestro 的 tags 標功能:效能與記憶體的測試寫在 Kotlin 裡貼不了標籤,兩套標法會漂;對照表一處寫齊。
- 效能:`macrobench_cmd` 可以帶 `{{TEST}}`,按功能跑時換成選到的測試方法、一個方法跑一次(例如 `sh scripts/run-bench.sh {{TEST}}`);情境列了效能測試方法卻沒帶 `{{TEST}}`,設定檢查就擋(S26)。帶了 `{{TEST}}` 之後,整套跑也只跑對照表列到的方法,沒列進任何情境的 Macrobenchmark 方法不會跑。方法名原樣換進 `sh -c`,所以不收 `$`(會被當變數展開、跑成別支)。
- 記憶體:可以有多個情境,寫在 `macrobench.json` 最外層、跟 `stability` 段並列的 `stability_scenarios`(情境名 → 蓋過 `stability` 段的 scenario、driver、warmup、cycles),收集腳本照選到的情境跑;門檻檔照舊用情境名對條目。原本只有一個情境的寫法照舊認得。
- 對照表裡寫了整套清單沒有的 flow 或畫面、門檻檔沒有的情境,`macrobench --check-config` 擋。

### 怎麼叫

```
sh scripts/templates/android-e2e-run.sh                            # 整套(推送前):全部跑、寫正式查證紀錄
sh scripts/templates/android-e2e-run.sh --changed                  # 自動:看這次改到的檔,挑對應功能的全部情境
sh scripts/templates/android-e2e-run.sh --feature player           # 指定功能:這個功能的全部情境
sh scripts/templates/android-e2e-run.sh --case player.open-close   # 指定情境(可以逗號接多個)
  加 --no-perf / --no-memory:這次不跑效能或記憶體(那兩塊一個情境要好幾分鐘)
```

- 建置與安裝每次都跑。
- `--changed` 比的是「HEAD 加上工作目錄沒提交的改動與沒追蹤的新檔」跟分岔點(主線)的差異,檔案落在哪個功能的 `paths` 裡就挑那個功能;一個功能都對不到時不靜默放過,印出改到的檔、提示補對照表或整套跑,回 2。
- 按功能跑不要求工作目錄乾淨(開發中本來就有沒提交的改動)。
- 改到的檔有些對得到功能、有些對不到時,`--changed` 照跑對得到的功能,另外列出「這些檔沒有對應功能」,提醒補對照表(推送前的整套跑照樣會驗到它們)。

### 檢測紀錄

- 每一次跑(整套或按功能)都在本機總表 `.lumos/artifacts/android/history.jsonl` 加一行:時間、run-id、HEAD、工作目錄有沒有沒提交的改動、怎麼挑的(整套、`--changed`、`--feature`、`--case` 與挑到的功能和情境)、每一項的結果(按功能跑另記每個情境自己的結果與項目,`history --case` 只列那個情境的)、證據目錄;judge 擋下沒寫紀錄的那次也記、附原因。總表在被 git 忽略的產物目錄裡,不進版控。
- `lumos android-e2e history [--feature <功能>] [--case <情境>] [--last N]` 列出歷史;每一行附證據目錄。
- 正式的查證紀錄(`.lumos/e2e-records/<指紋>.json`):整套跑寫 `runs`;按功能跑在工作目錄乾淨、HEAD 沒換時,把每個情境的結果寫進同一份紀錄的 `feature_runs`(`功能.情境` → result、complete、skipped、每項結果、run_id、ended、commit),不碰 `runs`;用了 `--no-perf`、`--no-memory` 而那個情境本來有那塊時 complete 是 false。沒提交時只記總表並說原因。判讀走 `judge --no-record`(名字沿用;意思是「不寫整套的 runs」),`steps.json` 帶 `selection` 欄,judge 沒帶 `--no-record` 讀到有 `selection` 的就拒寫、回 2。
- 2026-10-26 Enzo 裁「只針對功能開發寫正式檢驗紀錄也算合理」(開發是按功能分派的):推送前檢查按「這次改動碰到哪些功能」去要那些功能的 `feature_runs`,碰到共用程式或對不到功能的檔才要整套 `runs`;判法見下一節〈推送前怎麼按功能判〉。
- 終端在四塊結果之後照情境各列一行:「情境 player.open-close:沒過;沒過或沒判完:stability player」,最後一行講結果有沒有寫進查證紀錄;是哪一個 check 沒過看上面的「✗ 記憶體 player:native_unreachable」那行,證據目錄看總表或 `history`。

### 推送前怎麼按功能判

白話:推送前那道檢查(〈資料怎麼流〉第 4 步)先看整套跑過沒;沒有可用的整套結果,就看這次改動碰到哪些功能,要那些功能的每個情境在這一版都按功能跑過、而且通過。碰到大家共用的程式、或對不到功能的檔,還是要整套跑。

PRIOR-ART: 最小解在推送前判定這一層,從改動推「受影響的單位」;世界解過:Nx 的 affected(從改動的檔推出受影響的專案,另用 implicitDependencies 標「改到它全部都算受影響」的共用檔)、Bazel 的 rdeps 查詢;借用 Nx 的做法(檔對到功能、共用清單一律算全部),不另做相依分析(要讀 Kotlin 的 import,超出 vault-free 的範圍)。
RETIRE-IF: 按功能放行上線後,連續兩個真實專案跑滿三個月,同一段期間「按功能放行、之後整套跑卻在沒驗到的功能紅」的次數多過按功能放行次數的一成,就把按功能這條路撤掉、改回只認整套。

- 設定:`e2e` 段加 `shared_paths`(字串清單,選填,路徑寫法同 `features` 的 `paths`,S26 那套檢查照用;寫了不存在的路徑也擋):大家共用的程式,例如網路層、共用元件、`Application`。
- 判定順序(接在 S8 讀到合格紀錄之後;S8 的放行先看):
  1. 有放行→過(同 S8)。
  2. `runs` 是 pass 而且涵蓋主線版要求的塊(同 S8、S9):再看 `feature_runs` 裡有沒有哪個情境結束得比 `runs` 晚而且不是 pass;有→擋,印出那個情境(最新的結果說沒過);沒有→過。
  3. 其他(沒有 `runs`、`runs` 不是 pass、或沒涵蓋)→改走按功能:
     - 改到的檔:分岔點到被推送提交的差異(`git diff --name-only --no-renames`,改名的新舊路徑都算),只留指紋範圍裡的檔(`app_dirs` 扣掉 `exclude`、加上驗收素材;範圍跟 S2 算指紋同一套,兩端各用自己那版的 `e2e` 段取、取聯集)。範圍外的檔不影響判定。
     - 兩端的 `e2e` 段不一樣(正規化雜湊不同)→要整套。設定改了,每個情境驗什麼都可能變。
     - 每支改到的檔,在主線版與被推送提交兩版的 `features` 裡找歸屬(`paths` 包住它、或某個情境的 `flows` 列了它),兩版的結果取聯集;落在任一版的 `shared_paths` 底下、或兩版都找不到歸屬→要整套。
     - 要驗的情境:歸屬到的每個功能的每個情境。功能在主線版有、被推送提交拿掉了→要整套(防止拿掉功能來躲驗收)。
     - 每個要驗的情境,`feature_runs` 裡都要有一筆 result 是 pass、complete 是 true;那筆的項目要涵蓋主線版同名情境列的 flow、畫面與記憶體情境(主線版沒有這個情境就照被推送提交的),被推送提交改名或刪掉的不算缺(同 S9);`runs` 結束得比那筆晚而且不是 pass→那個情境算沒過。
     - 全部符合→過,多印一行「按功能放行:驗了 <情境清單>;這一版沒有整套驗過」。不符合→擋,只印一種原因:要整套時印是哪幾支檔(共用、對不到功能、設定改了)與整套跑的指令;否則印哪幾個情境缺或沒過,與 `--case <功能>.<情境>` 的指令。
- 擋下種類照用 `android_e2e`,原因文字不同;判不清就擋(S17)照舊。
- 按功能放行在治理帳記一筆:閘名 `android-e2e`、事件種類 `passed-by-feature`,附情境清單(RETIRE-IF 從這裡數)。

### 不做

- 不從圖譜的功能筆記推功能(那要讀 vault,端到端驗收目前是 vault-free 的);對照表寫在專案設定。
- 不做「只判記憶體某一項」:一個情境的開關資料是一起收的,只判一項省不了時間。

WHY:按功能跑的結果另存在查證紀錄的 feature_runs,不寫進整套的 runs;沒提交時只記總表 [出處:2026-10-26 Enzo 先要完善的檢測紀錄,後裁「只針對功能開發寫正式檢驗紀錄也算合理」] [因:開發按功能分派,每次逼整套跑不實際;但 runs 代表「這一版整套驗過」,混在一起推送前檢查就分不出驗了哪些;沒提交的版本對不上任何提交,不寫] [不選:按功能跑只記總表(原案,被 Enzo 改掉);寫進 runs 並標部分]
WHY:功能對照表寫在專案設定,不用 Maestro tags [出處:同上] [因:效能與記憶體的測試在 Kotlin 裡貼不了標籤,兩套標法會漂] [不選:flow 用 tags、其他用設定]

## 條款

- [S1] 當 `.lumos/macrobench.json` 的 `e2e` 段缺必填欄位(app_dirs、package、build、apk、flows)、型別不對、`visual_threshold` 不是 99.5 到 100 之間的數字、`package` 含英數字底線與點以外的字元、路徑跳出專案根、`app_dirs` 有一項不存在或包住 `.lumos/`、兩支 flow 同名、跟 `stability` 段的 package 或 adb_serial 不一致、或要了記憶體與穩定性卻有 `stability_checks` 列的 check 在門檻檔裡沒有情境相符的條目時,`lumos macrobench --check-config` 應回 2 並印出哪個欄位哪裡壞;只有 `e2e` 段的合格設定檔回 0 [test:t_android_e2e_config_strict]
- [S2] 當計算指紋時,lumos 應只從指定提交的檔案樹與那個提交的 `e2e` 段,用每一項的 mode、物件編號與路徑(NUL 分隔、依路徑位元組排序)算 `app_dirs` 扣掉 `exclude` 加上驗收素材,再接 `e2e` 段的正規化雜湊;目錄外的檔、預設排除的單元測試、工作目錄沒提交的改動、提交編號、`macrobench.json` 其他段都不影響指紋(例外:`e2e` 段開了記憶體時,最外層的 `stability` 段與 `stability_scenarios` 也算進去,它們決定記憶體驗得多嚴);目錄內任一檔內容或權限改了、換了基準圖、改了共用 flow 或門檻、改了 `e2e` 段,指紋就變;`app/src` 不含 `app/src2`;子模組與符號連結不讓計算出錯 [test:t_android_e2e_fingerprint]
- [S3] 當判 UI 流程時,`lumos android-e2e judge` 應照 `steps.json` 的回傳碼與每次嘗試的報告判:回傳碼 0、至少一個測試案例、沒有失敗才算那一次過;第一次過→過;第一次沒過、第二次過→過並標不穩定;兩次都沒過、或回傳碼 0 但報告零案例→沒過 [test:t_android_e2e_judge_ui]
- [S4] 當判截圖比對時,judge 應在 visual-check.sh 回傳碼是 0 時才算那個畫面過;回傳碼 1 或 2、或缺結果都算沒過並從存下的輸出記原因,不相符時記相符率與差異圖路徑;沒設定 `visual` 時這塊記成未設定、不影響 result [test:t_android_e2e_judge_visual]
- [S5] 當判效能與記憶體時,judge 應把效能退步、毫秒類門檻沒達、沒有基準、輪數不足、這塊沒跑成都只寫進 notices;記憶體與穩定性只看帶 check 且在 `stability_checks` 裡的條目:在 failures 時 result 是 fail,在 skipped、整段沒判、或那個 check 沒出現在任何清單時 result 是 unjudged;frozen 只寫 notices [test:t_android_e2e_judge_perf_memory]
- [S6] 當會擋的那幾塊(UI 流程、有設定的截圖、有設定的記憶體與穩定性)有工具沒跑成、APK 沒裝成或在記憶體塊結束前被換掉、或這次被中斷時,judge 應讓 result 不是 pass [test:t_android_e2e_judge_tool_failure]
- [S7] 當目前 HEAD 跟 `steps.json` 記的開跑 HEAD 不同、工作目錄有簿記檔以外的未提交改動或沒追蹤的新檔、或 `steps.json` 的 schema 不認得時,judge 應拒絕寫紀錄並回 2 [test:t_android_e2e_judge_dirty_tree]
- [S8] 當主線版有 `e2e` 段、而且被推送提交跟主線的 merge-base 與被推送提交兩端的指紋不同時,`code-loop check` 的 Android E2E 判定應從被推送提交的檔案樹讀紀錄:有放行、或最近一次是 pass 且涵蓋主線版要求的塊→放行;找不到、最近一次是 fail 或 unjudged 而且沒有放行→回 1 擋下並印出哪一塊沒過與要跑的指令;兩端指紋相同(只改文件、只改單元測試、改了又改回)→不要求;分支上次推上去的提交沒驗收、這次只改文件→照樣要求;主線版沒有 `e2e` 段→不跑;在 CI 裡→不跑 [test:t_android_e2e_gate]
- [S9] 當被推送的提交自己改弱 `e2e` 段(關掉 stability、拿掉主線版要求的 flow、畫面或 check)時,判定應照主線版要求的塊核對紀錄並擋下、印出少了哪一塊;分支新加 flow 或改 `app_dirs` 並跑過驗收時,判定應認得那份紀錄 [test:t_android_e2e_gate_reads_mainline_config]
- [S10] 當紀錄沒提交(工作目錄有、提交裡沒有,訊息要說「提交這支紀錄」)、紀錄的指紋欄位跟檔名對不上、JSON 壞掉、schema 比這版新、或有 `runs` 而 result 不是認得的值時,判定應擋下(回 1);只有放行、`runs` 是 null 的紀錄應放行 [test:t_android_e2e_gate_bad_record]
- [S11] 當分支被壓提交或 rebase、App 程式與驗收素材的內容沒變時,判定應照舊認得原本的紀錄 [test:t_android_e2e_gate_survives_rebase]
- [S12] 當 code-loop check 有其他判定會提早放行時,Android E2E 判定應仍然先跑;擋下時 `--keep-going` 的機讀行、pre-push 的擋下原因與逃生路都要印出 android_e2e 的說明,對照表句子跟計劃正本一致 [test:t_android_e2e_gate_wiring]
- [S13] 當執行 `lumos android-e2e waive --note <理由>` 時,lumos 應在理由去掉空白後少於 10 個字時回 2;終端答 y 時記成人放行、答了別的時不放行並回 1、沒有互動終端時記成 AI 放行;成功時把放行加進紀錄的 waivers(沒有紀錄就新建 `runs` 為 null 的紀錄)、之後重跑 judge 不會蓋掉;治理帳記一筆 android-e2e 的 waived [test:t_android_e2e_waive]
- [S14] 當被推送提交的紀錄裡有還沒被人看過的 AI 放行時,`code-loop check` 的這道應多印一行待看筆數、`lumos doctor` 應列成提醒(`--ci` 不因此變紅)、`lumos enforcement` 的那一列應標成沒生效;人用 `waive --ack` 答 y 確認後三處都不再列,答別的或沒人答時不標看過 [test:t_android_e2e_ai_waiver_notice]
- [S15] 當 `lumos macrobench` 帶 `--results-dir <目錄>` 時,應只讀那個目錄底下的結果檔、照舊用專案的基準與門檻,設定檔沒有 `results_dirs` 也照跑 [test:t_macrobench_results_dir]
- [S16] 當範本腳本 `android-e2e-run.sh` 跑完、中途有一步失敗、或被 INT、TERM、HUP 中斷時,它應寫出 `steps.json` 並呼叫 judge,不留下沒有紀錄的半套結果;開跑前檢查沒過(工作目錄有未提交改動或沒追蹤的新檔、裝置沒連上或鎖屏、同一台裝置有另一次驗收在跑)時不開跑並說原因;裝置鎖裡記的程序已經不在時清掉並接手 [test:t_android_e2e_run_script]
- [S17] 當主線找不到、主線版的 `e2e` 段不合格、被推送提交的 `app_dirs` 有一項不存在、或判定內部出錯時,判定應擋下(回 1)並說原因,不放行;`LUMOS_SKIP_ANDROID_E2E` 有設時整道不跑並記一筆治理帳 skipped [test:t_android_e2e_gate_unclear_blocks]
- [S18] 當開始實作時,應先在 SM-X710 上實測 Maestro repeat 吃不吃 ${CYCLES} 與 toolkit 狀態列固定得住,兩項各寫下「可以」或「不行與改法」;狀態列不行時截圖這塊不進第一版 [manual:前置兩項實測結果寫進〈資料怎麼流〉第 0 步之後]
- [S19] 當在 macrobench-lab 上照〈實驗室驗收〉逐組跑時,每一組都應照預期(UI 正常版 5 次全過、截圖同版本 3 次全相符、應該擋的全擋、不該擋的全放);任一組不照預期就算沒過,修好重跑那一組 [manual:SM-X710 上逐組跑,每組結果寫進驗證紀錄]
- [S20] 當在 Citrus_KDS 上接 E2E 驗收時,至少 UI 流程這塊應跑得起來、紀錄寫得出來、推送檢查認得它,並記下一次驗收實際花多少時間;超過 30 分鐘時在驗證紀錄寫一條縮短的回頭條件;Enzo 不同意升 benchmark-macro 時,效能與記憶體兩塊在 KDS 不開、照實寫進驗證紀錄 [manual:SM-X710 上跑一次,時間、各塊結果與沒開的塊寫進驗證紀錄]
- [S21] 當 AI 照 lumos-android-evidence skill 接 E2E 驗收時,skill 應寫明接入順序、怎麼跑、紅了看哪裡、怎麼放行、AI 放行會被列出來、怎麼整道關掉一次 [manual:讀 skill 的 E2E 驗收一節,六件事都寫到]
- [S22] 當範本腳本帶 `--case <功能>.<情境>` 或 `--feature <功能>` 跑時,它應建置、安裝,只跑對照表裡那些情境列的 flow、截圖、效能測試方法與記憶體情境,呼叫 `judge --no-record`;選到的都過時回 0、有沒過或沒判完時回 1;工作目錄有沒提交的改動時照樣開跑,不寫整套的 `runs`(按情境的結果寫不寫見 S27);終端最後照情境各列一行結果 [test:t_android_e2e_by_feature] [test:t_android_e2e_memory_by_case]
- [S23] 當帶 `--changed` 跑時,範本腳本應用「HEAD 加工作目錄改動與沒追蹤的新檔(逐檔)」對分岔點的差異挑出 `paths` 對得到的功能(改名的舊路徑也算;讀 git 失敗時回 2,不當成沒改動),改到的是某個情境列的 flow 檔時也挑那個功能,改到共用 flow、截圖素材、驗收設定或門檻卻對不到功能時列出來提醒;同時用 `--case` 而 `--changed` 對不到時照跑指名的;一個功能都對不到時回 2 並印出改到的檔與「補對照表或整套跑」;`--no-perf`、`--no-memory` 時不跑那兩塊,也不查那兩塊要的工具,沒配挑法時回 2;不認得的 `-` 開頭參數回 2 [test:t_android_e2e_by_feature] [test:t_android_e2e_changed_pick] [test:t_android_e2e_memory_by_case] [test:t_android_e2e_args_and_names] [test:t_android_e2e_changed_edges]
- [S24] 當 judge 沒帶 `--no-record`、讀到的 `steps.json` 有 `selection` 欄時,應拒絕寫紀錄並回 2;帶 `--no-record` 時只判選到的情境、不寫整套的 `runs` [test:t_android_e2e_by_feature]
- [S25] 當每一次範本腳本跑完(整套或按功能、過或沒過、被中斷)時,它應在 `.lumos/artifacts/android/history.jsonl` 加一行,含時間、run-id、HEAD、工作目錄有沒有改動、挑法、每一項的結果與證據目錄,judge 擋下沒寫紀錄的那次也記、附原因;`lumos android-e2e history` 照 `--feature`、`--case`、`--last`(正整數)篩出來 [test:t_android_e2e_history] [test:t_android_e2e_history_edges] [test:t_android_e2e_history_by_case]
- [S26] 當對照表寫了整套清單沒有的 flow 或畫面、門檻檔沒有的記憶體情境、或 `macrobench_cmd` 沒帶 `{{TEST}}` 卻有情境列了效能測試方法時,`macrobench --check-config` 應回 2 並點名;效能測試方法名不合規則(開頭 #、含空白、含 $)、功能 `paths` 不是正規寫法(`//`、`/./`、只寫 `.` 或 `./.`、反斜線、萬用字元;app_dirs、flows 同一套規則)、`macrobench_cmd` 不是字串、或 `stability_scenarios` 的輪數超過 10000 也回 2;原本只有一個記憶體情境的 `stability` 寫法照舊合格 [test:t_android_e2e_features_config] [test:t_android_e2e_args_and_names]
- [S27] 當按功能跑時開跑時與判讀時工作目錄都乾淨、HEAD 沒換,judge 應把每個挑到的情境寫進這一版查證紀錄的 `feature_runs`(result 照那個情境自己的項目算;略過情境本來有的效能或記憶體時 complete 是 false;一個會判的項目都沒有時 result 是 unjudged、complete 是 false),不碰 `runs`;同一版已有完整、判完的結果時,這次沒判完、或不完整但通過的不蓋掉它,這次沒過一律蓋掉,重判比既有那筆更早結束的那次也不蓋掉;一個情境沒判完時整次結果也是沒判完、回 1;之後整套跑寫 `runs` 時不蓋掉 `feature_runs` [test:t_android_e2e_by_feature] [test:t_android_e2e_feature_record_trust] [test:t_android_e2e_feature_record_rules]
- [S28] 當整套跑時,記憶體應收 `stability` 段本身加 `stability_scenarios` 每個情境、各判一次(段本身不帶 shell 殘留的情境變數);用了替身收集腳本(`LUMOS_E2E_COLLECT`)時不寫查證紀錄;多個效能測試方法時每跑完一個就收一次結果 [test:t_android_e2e_memory_by_case] [test:t_android_e2e_perf_per_method] [test:t_android_e2e_full_scenarios_judged]
- [S29] 當 `e2e` 段的 `shared_paths` 不是字串清單、有一項不合路徑規則、或寫了不存在的路徑時,`macrobench --check-config` 應回 2 並點名;沒寫 `shared_paths` 照舊合格 [test:t_android_e2e_shared_paths_config]
- [S30] 當紀錄的 `runs` 是 pass 而且涵蓋主線版要求的塊、但有一個情境的 `feature_runs` 結束得比 `runs` 晚而且不是 pass 時,判定應擋下並點名那個情境;沒有這種情境時放行 [test:t_android_e2e_gate_newest_wins]
- [S31] 當沒有可用的整套結果、改到的檔(指紋範圍內)都歸屬到功能、而且那些功能的每個情境都有 result 是 pass、complete 是 true、項目涵蓋主線版同名情境的 `feature_runs` 時,判定應放行並印「按功能放行」那一行、在治理帳記一筆 `passed-by-feature`;有一個情境缺、不是 pass、complete 是 false、少了主線版要的項目、或 `runs` 比它晚而且不是 pass 時,應擋下並印 `--case` 指令 [test:t_android_e2e_gate_by_feature]
- [S32] 當改到的檔落在任一版的 `shared_paths` 底下、兩版都對不到功能、兩端的 `e2e` 段不同、或主線版的功能被推送提交拿掉時,判定應要求整套結果:沒有可用的整套結果就擋下、印出是哪幾支檔或哪個原因與整套跑的指令,即使所有按功能的紀錄都是 pass;指紋範圍外的檔不影響判定 [test:t_android_e2e_gate_needs_full]
- [S33] 當在 macrobench-lab 上只改播放頁並 `--case player.open-close` 跑過、只改清單頁卻只跑了播放器、改到 `shared_paths` 列的檔只按功能跑過這三種情況各推一次時,判定應依序放行、擋下並印 `--case list.scroll`、擋下並要整套 [manual:SM-X710 上三種情況各推一次到本機假遠端,結果寫進驗證紀錄]

## 審計修正紀錄

- r1(2026-10-25,6 席:正確性、守衛、邊界、整合、通才、架構對齊):55 條/blocking 32/CI 在 PR 不跑、放行太便宜、APK 沒綁原始碼、紀錄格式與讀法、指紋定義、範本腳本介面、判定分流、接線清單;Enzo 另裁 AI 可放行但要通知、第一版只擋本機推送;55 條全折。
- r2(2026-10-25,6 席同上鏡頭、全新代理):59 條/blocking 33/回退指錯檔、指紋選檔設定與 `e2e` 段雜湊、分岔點算法與 CI、判不清改成擋、驗收中途換版與髒樹範圍、終端答 n、只有放行的紀錄、AI 放行通知落點、RETIRE-IF 資料來源、只有 e2e 段的設定檔、對照表句子正本、鎖殘留與原子寫入;折 58 條、放行 1 條(舊版 lumos 沒有這道判定時不另加版本探測,見 r2-intake.md)。
- 2026-10-26 先加〈只跑某一塊〉(--only 按大類挑),同日 Enzo 說粒度要到功能與使用情境,改寫成〈按功能與使用情境跑〉與 S22–S27,--only 那版沒推就改掉。新設計動到設定格式與收集腳本,spec-gate 判計劃風險高;Enzo 說「直接開工」,沒另開設計審,實作走代碼審、開發完在實驗室實跑。
- 代碼審 code-e2e-by-feature r1(2026-10-26,7 席:正確性、資源、邊界、合約、通才、資安、架構對齊):43 條/blocking 6/按功能跑「不寫紀錄」的說法與實作相反、測試沒守住分岔點與記憶體情境、--changed 漏挑新目錄與 flow 檔、開跑時髒卻記成這一版驗過、總表另起寫法、整套跑漏了記憶體情境;43 條全折,補 S28。
- 代碼審 code-e2e-by-feature r2(2026-10-26,7 席同上):30 條/blocking 7/效能方法名收了 $ 被 sh 展開成別支、不蓋掉完整結果的條件把真失敗也蓋掉、沒有會判項目時三處說法矛盾、紀錄前提與分岔點與整套各判一次沒有測試守住,另有 --changed 邊角、替身收集腳本與殘留情境變數、總表按情境;30 條全折。卷證 governance/review-reports/code-e2e-by-feature/。
- 卷證:governance/review-reports/android端到端驗收/(r1-intake.md、r2-intake.md 有逐條重現與去向)

## 回退

- 判定:一次推送要關掉這道,設 `LUMOS_SKIP_ANDROID_E2E=1`(記一筆治理帳);要長期關,從主線版的 `.lumos/macrobench.json` 刪掉 `e2e` 段(刪段的那次推送本身用環境變數關,合進主線後判定就不跑),其他判定不受影響。
- 紀錄與放行:`.lumos/e2e-records/` 是新增的檔,刪掉不影響其他功能;放行寫在治理帳的事件只是統計來源,不影響其他判定。
- 程式:新子命令與 `code-loop check` 那一道是新增的,回退就是撤掉那次提交;既有判定的程式碼只改 `lumos macrobench` 讀設定的那支(接受只有 `e2e` 段),撤掉時一起還原。
