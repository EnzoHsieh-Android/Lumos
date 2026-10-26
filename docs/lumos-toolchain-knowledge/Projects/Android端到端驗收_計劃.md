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

白話:Android App 改完、推送之前,在本機接著實機跑一次「端到端驗收」:UI 流程走不走得完(Maestro flow)、畫面跟人核可過的基準圖一不一樣(截圖比對)、效能有沒有變慢、記憶體有沒有洩漏或閃退。跑完寫一份綁在「這一版 App 程式與驗收素材的內容」上的查證紀錄,推送前的 `code-loop check` 檢查這一版有沒有一份通過(或有人放行)的紀錄:整套跑過且通過,或這次改動碰到的功能都按功能跑過且通過(見〈推送前怎麼按功能判〉),沒有就擋推送。第一版只擋本機推送,CI 上擋合併另開一案(見 REVISIT)。毫秒類效能(啟動時間、每幀耗時、凍結幀)第一版只提醒、不擋,等 [[Projects/Android效能判定統計化_計劃]] 的第 1、3、4 條(20 輪、同場比較、太吵指標只列出)都上線再改成擋。2026-10-24 Enzo 提「整合 Maestro,將效能測試、UI 測試成為 Android 端 E2E 的驗收標準」;2026-10-25 對話裡逐段確認了範圍、擋法、做法與三段設計,設計審 r1 之後又裁了放行權與 CI 範圍。

PRIOR-ART: Maestro CLI(`maestro test` 跑 flow,`--format junit --output` 出測試報告、`-e KEY=VAL` 傳參數、`--udid`/`--device` 指定裝置,內建 `assertScreenshot`);使用者自己的 maestro-visual-toolkit(github.com/EnzoHsieh-Android/maestro-visual-toolkit,本機在 ~/harness/maestro-visual-toolkit:人核可基準圖、門檻用環境變數 THRESHOLD(不准低於 99.5)、紅框差異圖、狀態列固定、裝置與 adb 路徑寫在安裝時產生的 `.maestro/visual-env.sh`、用 `.maestro/.lock-<裝置>` 鎖,原本只在模擬器驗過;本 repo 的 [[Projects/Maestro截圖基準比對_調研]] 與 [[Projects/截圖基準驗收流程_計劃]]);Lumos 既有的 Maestro flow 綁功能筆記(`[test:maestro:<名>]`,綁 flow 的 `name:`,[[Projects/Android側UI測試綁圖譜工作流_計劃]]);既有的 Macrobenchmark 判定(`lumos macrobench`,[[Systems/macrobenchmark-adapter]])與記憶體穩定性收集([[Systems/android-stability-collector]]);code-loop check 既有的安全證據判定([[Systems/安全證據閘]]:設定只讀主線版、主線用它挑主線與分岔點的那套算法、判不清就擋,不走 fail-open)與表態判定(證據一律對被推送提交的檔案樹驗);環境變數整道關掉、記一筆 `skipped-env` 的做法(`LUMOS_SKIP_NOTE_SHAPE`);既有的終端確認 `_confirm_tty`(回「答了 y」「答了別的」「沒人能答」三種)、原子寫入 `_write_lf`、獨佔鎖檔 `_excl_lock_try`、工作目錄有沒有改動的 `_dirty_non_bookkeeping`、判斷在不在 CI 的 `_in_ci`。借用:以上全部;自建只有一支串四塊的範本腳本、一個彙整判定與寫紀錄的子命令、code-loop check 裡多一道判定、`lumos macrobench` 多一個指定結果目錄的旗標與 `e2e` 段的格式檢查。不選:Maestro Cloud 與 Firebase Test Lab 這類雲端裝置(跟「本機實機跑」的決定衝突,雲端裝置的效能不能當基準);Gradle Managed Devices 的模擬器(同上)。
RETIRE-IF: 連續兩個真實專案跑滿三個月,掃那兩個專案的 `.lumos/e2e-records/`:有放行的指紋數多過「歷次結果裡有過 pass」的指紋數,或 AI 放行佔全部放行的一半以上,就把擋推送降回只提醒(撤法見〈回退〉)。
REVISIT:2027-03-31 查效能判定統計化第 1、3、4 條上線了沒;都上線就把毫秒類效能從只提醒改成擋,條款另開
REVISIT:2026-12-31 第一版只擋本機推送:評估加 PR 觸發的 CI 步驟範本(用 PR 分支頂端算指紋、主線分岔點到頂端的樹差異判要不要紀錄),讓專案能把它設成合併前必須通過;另評估 tag 推送要不要也跑這道
REVISIT:2026-12-31 回頭看治理帳 android-e2e 的 waived 裡 by=ai 的筆數與看過的比例,AI 放行多過人放行、或待看超過兩週沒人看,就改成沒有互動終端時不准放行(代碼審 code-e2e-gate r3 資安席:AI 一步就能放行是設計取捨,靠事後通知補)
REVISIT:2026-12-31 回頭看治理帳 android-e2e 的 skipped-env(用環境變數整道關掉)次數,多過擋下次數的一成就查是哪種誤擋逼人關掉

WHY:驗收沒過就擋推送、可以放行 [出處:2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」] [因:驗收沒過的程式不該默默推上去;實機驗收會誤擋,要留一條有紀錄的出口] [不選:只提醒(跟「成為驗收標準」的目的不符);不准放行(誤擋時只能改走略過檢查,沒有紀錄)]
WHY:AI 也能放行,但標成 AI 放的,而且每次推送、開場與體檢都把還沒人看過的 AI 放行列出來 [出處:2026-10-25 設計審 r1 後 Enzo 選「AI 能放行,但要通知你」] [因:無人看顧時驗收會因裝置狀態誤擋,完全不准 AI 放行會讓流程卡死;但 AI 最省力的路就是放行,要看得到] [不選:只有人能放行(無人看顧時卡死);照舊 10 字理由就放行(事後分不出是人還是 AI);AI 放行累積幾筆就擋(Enzo 裁的是「能放行」,累積就擋等於收回)] [代價:「通知」是在人會看的地方列出來,不是推播;人幾天不開會談就幾天看不到]
WHY:第一版只擋本機推送,CI 擋合併另開一案 [出處:2026-10-25 設計審 r1 後 Enzo 選「第一版只擋本機推送」;原本 10-24 選的「CI 驗收據」延後] [因:現行 CI 只在推到主線時跑 code-loop check,PR 上不跑;推到主線時合併提交的樹混了別人的改動,指紋跟分支上驗收時不同;做到 PR 要另寫 PR 事件的步驟範本,範圍大] [不選:第一版就做 PR 步驟(範圍大、要先把本機這道跑穩)] [代價:略過推送前檢查就擋不住,見 REVISIT]
WHY:查證紀錄的鎖照用 `_vault_write_lock`、殘留鎖不自動接手,推翻設計審 r3 折入的「程序不在就接手」 [出處:代碼審 code-e2e-gate r1 架構對齊席] [因:靠鎖裡的程序編號接手有競態(兩個等待者同時看到舊程序不在,後到者會刪掉前到者剛建好的鎖),專案的 `_excl_lock_try` 明文不這樣做;另寫一把鎖是第二種做法] [不選:自寫會接手的鎖(設計審 r3 原折法)] [代價:殘留鎖要人工清;推送本身不拿這把鎖,出口 LUMOS_SKIP_ANDROID_E2E=1 照樣有效] [test:t_android_e2e_record_lock_blocked]
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
3. 紀錄要提交進版控;`.lumos/e2e-records/` 跟其他簿記檔一樣,在代碼審留痕之後提交不會讓留痕失效(它在簿記目錄清單裡)。
4. 推送前 `code-loop check` 多一道「Android E2E 驗收」判定(判定順序與按功能那段見〈推送前怎麼按功能判〉):
   - 先看這個專案用不用 E2E(照安全證據閘先查登記痕跡、再挑主線的順序):被推送提交與主線候選的 `.lumos/macrobench.json` 都沒有 `e2e` 段→不跑,輸出一字不變(不印任何一行,CI 裡也一樣)。讀不到不算「沒有」:先用 `git ls-tree` 看那個路徑在不在樹裡,在樹裡卻讀不出內容(物件缺、git 失敗)→擋。
   - 在 CI 裡(`_in_ci`)不跑這道,只在上一步判定有 `e2e` 段時印一句「第一版只在本機推送時判」;`LUMOS_SKIP_ANDROID_E2E=1`(只認 `1`,同 `LUMOS_SKIP_BOUND_TESTS`)時整道不跑,記一筆治理帳 `skipped-env`(照 `LUMOS_SKIP_NOTE_SHAPE` 的做法)。
   - 主線:照安全證據閘那套挑主線(`_secev_mainline`;推的是分支:主線候選裡挑含分岔點、歷史最長的那條;推的就是主線本身:用推送前的主線位置);主線找不到→擋;新 repo 第一次推(回的是空樹起點)→當成主線版沒有 `e2e` 段;主線版沒有 `e2e` 段→不跑。
   - 何時要求:分岔點 = 被推送提交跟主線的 `git merge-base`(不是這次推送的範圍起點:分支上次推上去的提交沒驗收,這次只改文件也照樣要求);算不出分岔點(沒有共同祖先、淺層 clone 截斷歷史)→擋並說原因。選檔設定用被推送提交的 `e2e` 段;被推送提交沒有這一段時改用主線版的,這時 judge 與 waive 都算不出指紋,擋下訊息改成「這個提交沒有 e2e 段:先把主線合進來再驗收;刻意刪掉的那一次用 `LUMOS_SKIP_ANDROID_E2E=1` 關掉」。用同一份設定算分岔點與被推送提交兩端的指紋(看兩端的樹,不逐提交看:改了又改回來就不要求),不同才要求;分岔點那一端的樹沒有某個 `app_dirs` 項目(分支新加的模組)時,那一項當成空的照算,被推送提交那一端缺才擋(S17)。
   - 怎麼判:從被推送提交的檔案樹讀 `.lumos/e2e-records/<被推送提交的指紋>.json`(不讀工作目錄);依序驗 schema、指紋欄位等於檔名、`runs` 與 `feature_runs` 每一筆的結束時間(`runs` 的結束時間、`feature_runs` 的 `ended`)是讀得懂的帶時差 ISO 時間,再照〈推送前怎麼按功能判〉的判定順序判。找不到紀錄→擋;工作目錄裡有這個指紋的紀錄、只是還沒提交,訊息改成「這一版的查證紀錄還沒提交」並印出路徑與提交指令;提交裡的紀錄讀不懂→擋,叫人修好或刪掉那份紀錄(讀不懂的紀錄放行與重跑都不會覆蓋它)。擋下時印哪一塊沒過或少了哪一塊、紀錄路徑、要跑的指令;放行指令帶完整指紋與被推送提交(`lumos android-e2e waive <完整指紋> --commit <提交> --note …`),不靠 HEAD 預設。
   - 判不清就擋(回 1),跟安全證據閘一樣不走 fail-open:紀錄讀不懂(JSON 壞掉、schema 比這版 lumos 新、result 不是認得的值、指紋欄位對不上、`ended` 讀不懂)、主線找不到、算不出分岔點、主線版的 `e2e` 段本身不合格或在樹裡卻讀不出、被推送提交的 `app_dirs` 有一項不存在、整道超過時間預算、或其他內部錯誤,都擋並說原因;出口是 `LUMOS_SKIP_ANDROID_E2E=1` 關掉一次。
   - 時間預算:整道 60 秒,每次 git 拿剩下的時間(照安全證據閘 `_SECEV_BUDGET_SEC` 與 `_secev_git_left` 的做法);推送前算指紋的 `git ls-tree` 帶 pathspec,只列 `app_dirs` 與驗收素材,不列整個 repo。用完預算→擋,訊息說是逾時與怎麼關掉一次。
   - 每次跑這道(過或擋都算),只要被推送提交的紀錄裡有還沒人看過的 AI 放行,就多印一行「提醒:有 N 筆 AI 放行還沒人看過」與看的指令;按功能放行時另印「提醒:按功能放行…」那一行。兩行都以「提醒」開頭:pre-push 在放行路徑只轉印含「提醒」等字的行,不這樣寫真的 git push 時就看不到。兩行由 `_cl_say_e2e_notes` 印,接在放行與擋下共用的尾段 `_cl_say_tail`(放行時 `_cl_say_ok_extras` 另印一行判定結果);`_codeloop_guard_verdict` 每次呼叫重置新加的 `last_e2e`。
   - 治理帳(閘名 `android-e2e`,不進本機帳清單 `_GOV_LOCAL_PAIRS`,跟安全證據一樣進版控帳):擋下記 `blocked`(帶 hard)、按功能放行記 `passed-by-feature`、環境變數關掉記 `skipped-env`、偵測到 CI 而沒判記 `ci`、放行記 `waived`。
   - 位置與接線:跟安全證據判定一樣排在所有放行早退之前;擋下種類 `android_e2e`,接進 `_cl_say_block`、`_codeloop_kg_finish` 的明細、pre-push 的擋下原因對照表 `pp_cl_reason` 與逃生路那段文字;對照表句子的正本在 [[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉5,測試檔的 `_PPC_KIND_SENTENCES` 一起加,兩支守衛測試(對照表對 lumos、句子對計劃)抽種類名的樣式改成收數字(`android_e2e` 有個 2)、「五句」改「六句」,計劃正本那行的標記字一起改(改測試檔要 Enzo 簽章);擋下訊息不得含 pre-push 用來記逃逸帳的那兩串字。ci.yml 的擋下說明不加這一種(CI 不跑這道)。
   - tag 推送只跑安全證據,這道不跑(見 REVISIT)。
5. 放行 `lumos android-e2e waive <指紋> --commit <提交> --note "<理由>"`(擋下訊息印的就是這一行;指紋只收完整 64 碼,縮寫回 2、不新建紀錄;不帶指紋時算 HEAD 的、並把算到的完整指紋印出來):
   - 理由去掉空白後至少 10 個字。
   - 先在鎖外用 `_confirm_tty` 問一次「確定放行嗎」:答了 y → 記成人放行(誰取 git 的 user.name,沒設就取登入帳號);答了別的 → 不放行、回 1;沒有互動終端(沒有控制終端時立刻回,有終端但沒人答時等 `LUMOS_TTY_TIMEOUT` 秒,預設 30)→ 記成 AI 放行(誰記 `ai`);按 Ctrl-C → 不放行、回 1、不寫帳。`_confirm_tty` 走「標準輸入是終端」那條路時原本不會逾時;waive 與 `--ack` 呼叫它時打開 `stdin_timeout`,那條路也等 `LUMOS_TTY_TIMEOUT` 秒:掛著虛擬終端、沒有人在的流程才不會永遠等(其他呼叫端照舊,init 的互動行為不變)。
   - 確認之後才拿鎖,在鎖裡重讀整份、合併、整份寫回(寫入用 `_write_lf`)。鎖用專案既有的 `_vault_write_lock`(照 lint-waive):殘留鎖不自動接手,搶不到時不寫並說出鎖檔位置與人工清鎖的前提;推送本身不拿這把鎖(判定只讀提交樹),所以殘留鎖只擋放行與 judge,推送照樣可以用 `LUMOS_SKIP_ANDROID_E2E=1` 關掉一次。
   - 放行寫在紀錄的 `waivers` 清單(只增不刪;同一個指紋再放行一次就多一筆;之後重跑 judge 不會蓋掉);沒有紀錄就新建一份只有放行的紀錄(`runs` 是 null、`history` 是空清單)。每一筆的欄位見〈查證紀錄長怎樣〉。
   - 治理帳記一筆:閘名 `android-e2e`、事件種類 `waived`(閘名登記進已知閘名清單 `_KNOWN_GATES`),附人或 AI、指紋、理由。
   - `lumos android-e2e waive --list` 列出所有紀錄裡的放行與有沒有被人看過。
   - 通知:除了上面每次推送那一行,`lumos doctor` 把還沒人看過的 AI 放行列成提醒(不讓 `doctor --ci` 變紅);開場提示另印一行「有 N 筆 AI 放行還沒人看過」與看的指令(不算防護層:不進 `lumos enforcement` 的列與分母,那裡查的是有沒有裝上;開場提示只在有 `docs/*-knowledge` 的專案印,沒有紀錄目錄也不印)。doctor 與開場提示掃工作目錄 `.lumos/e2e-records/` 裡的紀錄,舊指紋的也算:沒人看過就一直列;只讀一般檔(不跟著捷徑走),照修改時間由新到舊最多 500 份、單份 2MB,一份讀不懂只跳過那一份。人用 `lumos android-e2e waive --ack <指紋>…`(可一次給多個)或 `--ack --all` 標成看過(同樣要終端確認,只有答 y 才算),改完的紀錄要提交,別台機器才看得到。

## 查證紀錄長怎樣

- `schema`:格式版本(第一版是 1);判定遇到比自己新的版本就擋,請人更新 lumos。
- `fingerprint`:對一個提交的檔案樹,用那個提交的 `e2e` 段,取 `app_dirs` 底下(扣掉 `exclude`)與驗收素材的每一個項目,用 `git ls-tree -r -z` 的 mode、型別、物件編號與路徑,依路徑的位元組順序排好,每一項寫成「mode、物件編號、路徑」三段、段與段之間用 NUL 分開、每項後接換行;最後再接一行「`e2e-config`、NUL、`e2e` 段的 sha256」(段落先寫成鍵排序、不留空白、不轉義中文的 JSON 再算),整串算 sha256。只取 `e2e` 段不取整個 `macrobench.json`:改效能基準或 `results_dirs` 不用重跑 E2E;例外是 `e2e` 段開了記憶體時,最外層的 `stability` 段與 `stability_scenarios` 另算一行 `memory-config` 雜湊接在後面(決策 d1)。用 git 物件編號而不讀檔案內容:上萬檔的目錄也是一次 git 呼叫、子模組用它記的提交編號、符號連結用它指向的路徑、Git LFS 用指標檔,改權限(mode)也會讓指紋變。
- `runs`:最近一次整套跑的完整結果(每一次整套 judge 覆蓋這一欄,按功能跑不碰它,不動 `waivers` 與 `history`;沒跑過整套的紀錄是 null:只有放行的、或只做過按功能跑的(只有 `feature_runs`),判定看 `waivers` 有沒有算數的放行,不看 `runs` 是不是 null):result(pass、fail、unjudged)、run-id、開始與結束時間(本機時區、帶時差的 ISO 格式)、裝置型號與系統版本、建出的 APK 與裝置上實際安裝那份的 sha256、判定的提交編號、四塊明細(每支 flow 的結果與是否不穩定、每個畫面的結果與原因、效能與記憶體每條的結果與原因)、`notices`(只提醒的項目)。
- `history`:每次 judge 追加一筆(result、run-id、結束時間;按功能跑的那筆另帶 `kind: feature` 與挑到的情境),只增不刪;RETIRE-IF 從這裡數時只數沒有 `kind` 的整套那幾筆,按功能的通過不算整版驗過。
- `feature_runs`:按功能跑的結果,`功能.情境` → `result`、`complete`、`skipped`(略過的塊:`macrobench`、`stability`)、`items`(每項 `kind`、`name`、`result`)、`run_id`、`ended`、`commit`,沒有會判項目時另有 `reason`(見〈按功能與使用情境跑〉);整套跑不碰它。整套跑比某個情境的 `feature_runs` 晚而且沒過時,兩邊會說不同的話:推送前檢查比兩邊的結束時間,取較新的那個(見〈推送前怎麼按功能判〉)。
- `waivers`:每筆是 `by`(`human` 或 `ai`)、`who`、`at`(帶時差的 ISO 時間)、`note`、`commit`(放行時給的提交,只收這個 repo 解得到的、存完整 40 碼;沒給就是 HEAD)、`acked`(布林)、`acked_by`、`acked_at`;判定只把 `by` 是 human 或 ai、`note` 非空的那筆算成放行,`[{}]`、`[null]` 這種不算放行、也不算讀不懂。
- 寫一半被殺留下的 `<指紋>.json.<…>.tmp-wlf` 暫存檔,判定只讀 `<指紋>.json`,不受影響。
- 原始檔只在本機;紀錄只放摘要與數字。
- 改了 `app_dirs`、`exclude`、驗收素材或 `e2e` 段本身,指紋就全變、舊紀錄都對不上,要重跑一次:這是刻意的(驗收的範圍或標準變了就該重驗),不做舊紀錄遷移。舊紀錄檔不自動刪,一份只有幾 KB;run 目錄在被 git 忽略的產物目錄,清理照產物目錄既有做法由人清;每個記憶體情境另有 `<run-id>.<情境>` 目錄(錄製檔與日誌),整套跑一次就多 1+情境數份,收集腳本只清七天前的記憶體快照,其餘也由人清。
- 同一個指紋重跑、這次沒過,會蓋掉先前的 pass:最近一次的結果才算數(重跑出現的失敗就是真訊號),先前通過的次數留在 `history`。

## 這次要改到的地方

- 新子命令 `lumos android-e2e`(judge、waive)與它的家 `Systems/android-e2e-acceptance`(新開;code-loop check 那一道的細節也寫在這裡,跟安全證據閘、表態閘各有自己的家一樣)。
- `code-loop check` 多一道判定:[[Systems/pitfalls-code-loop]] 只加一行連結,不寫細節。
- `lumos macrobench`:讀設定那支函式加 `e2e` 段的格式檢查、接受只有 `e2e` 段的設定檔;加 `--results-dir`(設定沒有 `results_dirs` 也能跑):寫進 [[Systems/macrobenchmark-adapter]],那篇另補一句「`e2e` 段由 Systems/android-e2e-acceptance 負責」。
- pre-push 的擋下原因對照表與逃生路文字:寫進它們的家 [[Systems/bound-tests-gate]];對照表句子同步改 [[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉5 的正本(含標記字「五句」改「六句」)與測試檔的 `_PPC_KIND_SENTENCES`,兩支守衛測試抽種類名的樣式改成收數字。ci.yml 不改。
- 治理帳已知閘名 `_KNOWN_GATES` 加 `android-e2e`;`lumos doctor` 與開場提示列出沒人看過的 AI 放行(開場那行由開場掛鉤印,不進 `lumos enforcement`)。
- 共用函式:歸屬判斷與指紋範圍判斷從 `_e2e_changed_features`、`_e2e_fingerprint` 抽出來,三處共用;`_e2e_fingerprint` 加 pathspec 與「這一端缺 `app_dirs` 項目當空的」選項。
- `_confirm_tty`:加 `stdin_timeout` 選項,waive 與 `--ack` 用它讓標準輸入是終端那條路也逾時;`LUMOS_TTY_TIMEOUT` 寫成負數、NaN 時用預設。
- `e2e` 段的設定檢查加 `shared_paths`;README.md、README.en.md 的功能對照表段落、skill 的 `e2e.features` 欄位清單補 `shared_paths`;skill〈端到端驗收〉裡「推送前檢查還不會擋、還沒有放行指令」那句,與「推之前整套跑一次」的說法照按功能放行改寫。
- `android-e2e waive` 是新的二層子指令:`HELP_WHEN` 表補一條「什麼時候用」。
- 新範本腳本 `android-e2e-run.sh` 放 `scripts/templates/`(含 `--preflight`),家是 `Systems/android-e2e-acceptance`;收集腳本不改。
- skill lumos-android-evidence:reference.md 的 Maestro 驅動範例照前置實測修正;〈端到端驗收〉一節補齊接入順序、怎麼跑、紅了看哪裡、怎麼放行、AI 放行會被列出來、怎麼整道關掉一次、共用程式要列進 `shared_paths`。
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
- 按功能放行:一支歸在功能 A 底下、其實別的功能也在用的程式,沒標進 `shared_paths` 時,改壞別的功能不會被擋;推上主線前也不強制整套跑(Enzo 裁「按功能開發寫正式紀錄也算合理」的代價),靠專案自己把共用程式列進 `shared_paths`。
REVISIT:2027-04-30 數逃逸帳裡歸因到按功能放行的筆數、治理帳 passed-by-feature 按指紋去重後的筆數,照〈推送前怎麼按功能判〉的 RETIRE-IF 判要不要撤掉按功能這條路
- 截圖與 UI 報告可能拍到畫面上的使用者資料:只留在被 git 忽略的產物目錄,`--preflight` 驗產物目錄有被忽略。

## 實驗室驗收

在 macrobench-lab 上每一塊各準備「應該擋」與「不該擋」,每一組都要照預期:

- UI 流程:應該擋=按鈕失效不跳頁、清單少一列(兩次都沒過);不該擋=正常版連跑 5 次都過;偶爾慢一點才出現的畫面要被標成不穩定、不擋。
- 截圖:應該擋=元素位置跑掉、一整塊不見、文字被切;不該擋=只有時間電量變、同一版本連拍 3 次都相符。只差幾個字抓不到,列為限制。
- 效能與記憶體:應該擋=Java 套件沒 release、C/C++ 套件沒 release、中途閃退(改由 Maestro 驅動);只提醒不擋=注入啟動變慢、每列變慢。
- 擋推送:應該擋=改了 App 程式沒跑驗收就推、跑了沒過、改程式後拿舊紀錄改檔名充數、換了基準圖沒重跑、改了共用 flow 沒重跑、同一個提交裡把 `stability` 關掉或拿掉一支主線要求的 flow、分支上次沒驗收就推上去這次只改文件、驗收跑到一半提交了新的程式;不該擋=只改文件、只改單元測試、沒過但有人放行、壓提交或 rebase 後內容沒變、改了又改回來、分支新加一支 flow 並跑過驗收、紀錄已產生但還沒提交時訊息指出要提交。
- 放行:AI 放行會出現在推送那一行、doctor 與開場提示(`lumos enforcement` 不多一列);人答 n 不會產生放行;人標看過後不再列。
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
- 2026-10-26 Enzo 裁「只針對功能開發寫正式檢驗紀錄也算合理」(開發是按功能分派的):推送前檢查按「這次改動碰到哪些功能」去要那些功能的 `feature_runs`,碰到共用程式、對不到功能的檔、改了驗收設定、或說不出改了哪支檔,才要整套 `runs`;判法見下一節〈推送前怎麼按功能判〉。
- 終端在四塊結果之後照情境各列一行:「情境 player.open-close:沒過;沒過或沒判完:stability player」,最後一行講結果有沒有寫進查證紀錄;是哪一個 check 沒過看上面的「✗ 記憶體 player:native_unreachable」那行,證據目錄看總表或 `history`。

### 推送前怎麼按功能判

白話:推送前那道檢查(〈資料怎麼流〉第 4 步)先看整套跑過沒;沒有可用的整套結果,就看這次改動碰到哪些功能,要那些功能的每個情境在這一版都按功能跑過、而且通過。碰到大家共用的程式、對不到功能的檔、改了驗收設定、或說不出改了哪支檔,還是要整套跑。

PRIOR-ART: 最小解在推送前判定這一層,從改動推「受影響的單位」;世界解過:Nx 的 affected(從改動的檔推出受影響的專案,另用 implicitDependencies 標「改到它全部都算受影響」的共用檔)、Bazel 的 rdeps 查詢;借用 Nx 的做法(檔對到功能、共用清單一律算全部),不另做相依分析(要讀 Kotlin 的 import,超出 vault-free 的範圍)。
RETIRE-IF: 按功能放行上線後半年內,逃逸帳(`lumos loop escape`)記了兩筆以上「按功能放行推上去、沒驗到的功能被改壞」,就把按功能這條路撤掉、改回只認整套(撤法見〈回退〉)。

- 設定:`e2e` 段加 `shared_paths`(字串清單,選填):大家共用的程式,例如網路層、共用元件、`Application`。路徑寫法同 `features` 的 `paths`(S26 那套形狀檢查,`_e2e_relpath_err`),跟 `paths` 一樣不驗存不存在。
- 判定順序(接在〈資料怎麼流〉第 4 步讀到合格紀錄之後):
  1. `waivers` 裡有一筆算數的放行→過。
  2. `runs` 是 pass 而且涵蓋主線版要求的塊(S8、S9):再看 `feature_runs` 裡有沒有哪個情境 result 是 fail、而且結束時間不早於 `runs`(同一秒算較新);有→擋,點名那個情境(最新的結果說沒過);沒有→過。只看 fail:沒判完、不完整的開發中途跑不推翻整套的 pass。
  3. 其他(沒有 `runs`、`runs` 不是 pass、或沒涵蓋)→改走按功能,以下任一條成立就要整套:
     - 兩端的設定不一樣:`e2e` 段的正規化雜湊不同,或指紋裡的 `memory-config` 那一行不同(決策 d1)。設定改了,每個情境驗什麼都可能變。
     - 改到的檔:`git diff --name-only -z --no-renames <分岔點> <被推送提交>`(帶 `-z`,中文檔名才不會被跳脫成引號字串;改名的新舊路徑都算),只留指紋範圍裡的檔(跟算指紋同一支範圍判斷)。指紋範圍裡一支改到的檔都沒有、指紋卻不同→要整套(說不出改了什麼,就不按功能放行)。
     - 每支改到的檔,用被推送提交的 `features` 找歸屬(`paths` 包住它、或某個情境的 `flows` 列了它;走到這一步兩端的 `e2e` 段一樣,用哪一版都相同);落在 `shared_paths` 底下、或找不到歸屬→要整套。
  4. 不用整套時,要驗的情境是歸屬到的每個功能的每個情境;只列效能、沒有會判項目的情境不用驗(效能只提醒,按功能跑也判不出過不過),在放行那一行列成「沒驗:<情境>(只列效能)」。
  5. 每個要驗的情境,`feature_runs` 裡要有一筆 result 是 pass、`skipped` 裡沒有 `stability`(略過效能不算缺,效能只提醒)、`items` 涵蓋那個情境列的 flow、畫面與記憶體情境;`runs` 是 fail 而且結束時間不早於那一筆→那個情境算沒過。
  6. 全部符合→過,多印一行「提醒:按功能放行:驗了 <情境清單>;這一版沒有整套驗過」。不符合→擋,只印一種原因:要整套時印是哪幾支檔或哪個原因(共用、對不到功能、設定改了、說不出改了什麼)與整套跑的指令;否則印哪幾個情境缺或沒過,與 `--case <功能>.<情境>` 的指令。
- 歸屬判斷與指紋範圍判斷抽成共用函式,`--changed`(`_e2e_changed_features`)、指紋(`_e2e_fingerprint`)與推送前判定三處共用,路徑比對沿用 `_e2e_under`、`_e2e_norm`,不另寫一套。
- 擋下種類照用 `android_e2e`,原因文字不同;判不清就擋(S17)照舊。
- 按功能放行在治理帳記一筆 `passed-by-feature`,附指紋、被推送提交與情境清單;同一個指紋重推會多記,數的時候按指紋去重。

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
- [S8] 當主線版有 `e2e` 段、而且被推送提交跟主線的 merge-base 與被推送提交兩端的指紋不同時,`code-loop check` 的 Android E2E 判定應從被推送提交的檔案樹讀紀錄,照〈推送前怎麼按功能判〉的判定順序判:有算數的放行、或整套 pass 且涵蓋主線版要求的塊→放行;找不到紀錄、或三條路都不符合→回 1 擋下並印出哪一塊沒過、要跑的指令與帶完整指紋和提交的放行指令;兩端指紋相同(只改文件、只改單元測試、改了又改回)→不要求;分支上次推上去的提交沒驗收、這次只改文件→照樣要求;主線版沒有 `e2e` 段→不跑;在 CI 裡→不跑 [test:t_android_e2e_gate]
- [S9] 當被推送的提交自己改弱 `e2e` 段(關掉 stability、拿掉主線版要求的 flow、畫面或 check)時,判定應照主線版要求的塊核對紀錄並擋下、印出少了哪一塊;分支新加 flow 或改 `app_dirs` 並跑過驗收時,判定應認得那份紀錄 [test:t_android_e2e_gate_reads_mainline_config]
- [S10] 當紀錄沒提交(工作目錄有、提交裡沒有,訊息要說「這一版的查證紀錄還沒提交」並印提交指令)、紀錄的指紋欄位跟檔名對不上、JSON 壞掉、schema 比這版新、有 `runs` 而 result 不是認得的值、或 `runs` 的結束時間、`feature_runs` 任一筆的 `ended` 讀不懂時,判定應擋下(回 1);`waivers` 裡有一筆 `by` 是 human 或 ai、`note` 非空的放行時應放行(即使 `runs` 是 null);`runs` 是 null、沒有算數的放行、只有 `feature_runs` 的紀錄應改走按功能判;`[{}]` 這種放行不算數 [test:t_android_e2e_gate_bad_record]
- [S11] 當分支被壓提交或 rebase、App 程式與驗收素材的內容沒變時,判定應照舊認得原本的紀錄 [test:t_android_e2e_gate_survives_rebase]
- [S12] 當 code-loop check 有其他判定會提早放行時,Android E2E 判定應仍然先跑;擋下時 `--keep-going` 的機讀行、pre-push 的擋下原因與逃生路都要印出 android_e2e 的說明,對照表句子跟計劃正本一致、兩支守衛測試認得含數字的種類名;放行時「提醒:」開頭的 AI 放行待看行與按功能放行行,經過真的 pre-push 也印得出來 [test:t_android_e2e_gate_wiring]
- [S13] 當執行 `lumos android-e2e waive <指紋> --commit <提交> --note <理由>` 時,lumos 應在理由去掉空白後少於 10 個字、或指紋不是完整 64 碼時回 2 且不新建紀錄;確認在拿鎖之前問:終端答 y 時記成人放行、答了別的或按 Ctrl-C 時不放行並回 1、不寫帳,沒有互動終端時記成 AI 放行,標準輸入是終端但沒人答時等 `LUMOS_TTY_TIMEOUT` 秒後記成 AI 放行;成功時把放行加進紀錄的 waivers(沒有紀錄就新建 `runs` 為 null 的紀錄)、之後重跑 judge 不會蓋掉;治理帳記一筆 android-e2e 的 waived [test:t_android_e2e_waive]
- [S14] 當被推送提交的紀錄裡有還沒被人看過的 AI 放行時,`code-loop check` 的這道不論放行或擋下都應多印一行「提醒:」開頭的待看筆數;工作目錄任一份紀錄有沒人看過的 AI 放行時,`lumos doctor` 應列成提醒(`--ci` 不因此變紅)、開場提示應另印一行,`lumos enforcement` 不多一列;人用 `waive --ack <指紋>…` 或 `--ack --all` 答 y 確認後三處都不再列,答別的或沒人答時不標看過 [test:t_android_e2e_ai_waiver_notice]
- [S15] 當 `lumos macrobench` 帶 `--results-dir <目錄>` 時,應只讀那個目錄底下的結果檔、照舊用專案的基準與門檻,設定檔沒有 `results_dirs` 也照跑 [test:t_macrobench_results_dir]
- [S16] 當範本腳本 `android-e2e-run.sh` 跑完、中途有一步失敗、或被 INT、TERM、HUP 中斷時,它應寫出 `steps.json` 並呼叫 judge,不留下沒有紀錄的半套結果;開跑前檢查沒過(工作目錄有未提交改動或沒追蹤的新檔、裝置沒連上或鎖屏、同一台裝置有另一次驗收在跑)時不開跑並說原因;裝置鎖裡記的程序已經不在時清掉並接手 [test:t_android_e2e_run_script]
- [S17] 當主線找不到、算不出分岔點、主線版的 `e2e` 段不合格或在樹裡卻讀不出、被推送提交的 `app_dirs` 有一項不存在、整道超過 60 秒預算、或判定內部出錯時,判定應擋下(回 1)並說原因,不放行;`LUMOS_SKIP_ANDROID_E2E=1` 時整道不跑並記一筆治理帳 skipped-env;被推送提交與主線都沒有 `e2e` 段的專案,這道不跑、輸出一字不變 [test:t_android_e2e_gate_unclear_blocks]
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
- [S29] 當 `e2e` 段的 `shared_paths` 不是字串清單、或有一項不合路徑規則(同 `features` 的 `paths`)時,`macrobench --check-config` 應回 2 並點名;沒寫 `shared_paths`、或寫了還不存在的路徑,照舊合格 [test:t_android_e2e_shared_paths_config]
- [S30] 當紀錄的 `runs` 是 pass 而且涵蓋主線版要求的塊、但有一個情境的 `feature_runs` result 是 fail、結束時間不早於 `runs`(同一秒算較新)時,判定應擋下並點名那個情境;較新的那筆只是沒判完或不完整時應放行 [test:t_android_e2e_gate_newest_wins]
- [S31] 當沒有可用的整套結果、兩端設定相同、指紋範圍內有改到的檔而且都歸屬到功能、那些功能每個要驗的情境都有 result 是 pass、`skipped` 沒有 `stability`、`items` 涵蓋情境列的 flow、畫面與記憶體情境的 `feature_runs` 時,判定應放行並印「提醒:按功能放行」那一行、在治理帳記一筆附指紋的 `passed-by-feature`;只列效能的情境不用驗、列在那一行;有一個要驗的情境缺、不是 pass、略過了記憶體、少了項目、或 `runs` 是 fail 而且結束時間不早於它(同一秒算較新)時,應擋下並印 `--case` 指令;中文檔名的改動照樣歸屬得到 [test:t_android_e2e_gate_by_feature]
- [S32] 當改到的檔落在 `shared_paths` 底下、對不到功能、兩端的 `e2e` 段雜湊或 `memory-config` 那一行不同、或指紋不同但指紋範圍內一支改到的檔都沒有時,判定應要求整套結果:沒有可用的整套結果就擋下、印出是哪幾支檔或哪個原因與整套跑的指令,即使所有按功能的紀錄都是 pass;指紋範圍外的檔不影響判定 [test:t_android_e2e_gate_needs_full]
- [S33] 當在 macrobench-lab 上只改播放頁並 `--case player.open-close` 跑過、只改清單頁卻只跑了播放器、改到 `shared_paths` 列的檔只按功能跑過這三種情況各推一次時,判定應依序放行、擋下並印 `--case list.scroll`、擋下並要整套 [manual:SM-X710 上三種情況各推一次到本機假遠端,結果寫進驗證紀錄]
- [S34] 當查證紀錄的讀改寫鎖搶不到(另一個程序在寫,或被 TERM、HUP、kill -9 留下的殘留鎖)時,judge 與 waive 應不寫、回錯誤訊息並說出鎖檔位置與「確認相關程序都已停止才人工清鎖」;寫紀錄用的是專案既有的 `_vault_write_lock`,不自動接手殘留鎖 [test:t_android_e2e_record_lock_blocked]
- [S35] 當判定在 60 秒預算內算不完(git 慢、樹很大)時,應擋下並說是逾時與怎麼關掉一次;算指紋的 `git ls-tree` 只列 `app_dirs` 與驗收素材 [test:t_android_e2e_gate_budget]
- [S36] 當分岔點那一端的樹沒有被推送提交新加的 `app_dirs` 項目時,判定應把那一項當空的照算、認得已提交的紀錄;被推送提交沒有 `e2e` 段而主線有時,擋下訊息應說「先把主線合進來」,不叫人重跑驗收或放行 [test:t_android_e2e_gate_missing_side]
- [S37] 當同一批改動分別交給 `--changed` 與推送前判定時,兩邊對每支檔的歸屬與「在不在指紋範圍」應一致(共用同一支判斷) [test:t_android_e2e_scope_shared]
- [S38] 當分岔點與被推送提交都沒有 `e2e` 段(主線採用之前分出去的舊分支)而兩端指紋相同時,判定應回不要求;這次拿掉了 `e2e` 段(分岔點還有)時應擋下但不叫人合主線(三方合併保留這邊的刪除,合了也補不回)、在意的原因講拿掉了驗收設定;提交裡的紀錄讀不懂時,接下來那段應叫人修好或刪掉那份紀錄、不印放行指令(讀不懂的紀錄放行寫不進去) [test:t_android_e2e_gate_cfg_sides]
- [S39] 當推送前判定偵測到 CI(`CI` 或 `GITHUB_ACTIONS` 有設)而不跑這道時,應記一筆治理帳 ci,提醒行講明不是在 CI 裡就清掉這兩個變數再推 [test:t_android_e2e_gate_ci_escape]
- [S40] 當擋下原因裡要印被推送提交的檔名時應先清掉控制字元;`waive --commit` 應只收這個 repo 解得到的提交(完整或縮寫,存完整 40 碼),沒給就存 HEAD;`LUMOS_TTY_TIMEOUT` 超過一天時應用預設;帶分支名的擋下事件整行應裝得進 4096 位元組;`app_dirs` 一項包住另一項時應照常算指紋 [test:t_android_e2e_input_guards]
- [S41] 當 doctor 與開場提示讀工作目錄的紀錄時,兩處應用同一套規則:照修改時間由新到舊最多 500 份、單份 2MB(太大的佔名額不讀、另計成「超過 2MB 沒讀」並叫人修好或刪掉)、總時間 3 秒(開場掛鉤另跟外層剩下的時間取小),沒讀到的份數講出來,一份讀不懂(含巢狀深到遞迴爆掉)只跳過那一份;`waive --list` 與 `--ack` 是人明著下的指令,應讀全部紀錄(不設份數上限),時間上限都是 60 秒、用完講沒讀到幾份,`--list` 邊讀邊印;`--ack` 遇到寫不進去的那份應不停在半路,其他份照標、講出沒標的那份並回 2 [test:t_android_e2e_record_scan]
- [S42] 當判定、`--changed` 或涵蓋報告查改到的檔歸到哪些功能時,應照 paths 整段路徑包住或情境 flows 列了它判,十萬支檔對上萬條功能路徑應在幾秒內算完 [test:t_android_e2e_owner_index]
- [S43] 當擋下原因或結果清單裡帶外來文字(被推送提交的設定值、紀錄的鍵名、檔名)時,判定應在結果出口統一把控制字元換掉 [test:t_android_e2e_gate_output_clean]
- [S44] 當紀錄超過 doctor 與開場提示的份數上限時,`waive --list` 應列得出名額外那份的放行、`waive --ack <指紋>` 應標得到它;`--ack` 時間用完時應講出沒讀到幾份 [test:t_android_e2e_waive_all_records]
- [S45] 當路徑深一萬層、flows 上萬條、`--changed` 改到幾十支檔時,歸屬、範圍與重複檢查應在幾秒內做完(查表只查到功能路徑最深那一層、flows 用集合、重複檢查用計數、`--changed` 只建一次查表) [test:t_android_e2e_scope_perf]
- [S46] 當紀錄讀不懂時,判定、放行與重跑應用同一套「讀不懂」(紀錄格式、欄位型別與結束時間):schema 比這版新→叫人更新 lumos、不叫人刪;git 暫時讀不出→不叫人刪;結束時間讀不懂、欄位型別不對、巢狀深到遞迴爆掉、單份超過 2MB→放行不寫、判定擋下叫人修好或刪掉;讀不懂的訊息保留位置 [test:t_android_e2e_record_unreadable]
- [S47] 當結束時間跨時差、分支把 flow 改名、主線在分岔後才加了驗收要求、舊分支只改記憶體設定、`--commit` 給解不到或剛好是分支名的十六進位、放行時按 Ctrl-C 時,判定與放行應各照計劃判(跨時差照真實先後;舊名不算缺;叫人先合主線;訊息講記憶體設定不一樣;回 2;回 1 不寫) [test:t_android_e2e_gate_r3_paths]
- [S48] 當 `shared_paths` 有一項不在 `app_dirs` 底下、或路徑寫成 `.//x` 這種去掉 `./` 之後是絕對路徑的寫法時,`macrobench --check-config` 應判不合格 [test:t_android_e2e_config_r3]
- [S49] 當查主線候選失敗、被推送提交又整個沒有 `.lumos/macrobench.json`、而上一版有 `e2e` 段時,判定應擋下(這次刪掉了驗收設定),上一版也沒有時照舊不跑 [test:t_android_e2e_gate_uses_unclear]
- [S50] 當主線在分岔後改了驗收設定(例如 `app_dirs` 多一個模組)、照這一版的設定看兩端一樣、照主線的設定看這次改到了要驗收的檔時,判定應擋下並叫人先合主線;只改文件時照樣不要求 [test:t_android_e2e_gate_mainline_wider]
- [S51] 當設定的路徑含控制字元、換行或看不見的格式字元、超過 64 層,或 app_dirs、exclude、shared_paths 超過 200 項時,`macrobench --check-config` 應判不合格;e2e 指令印的每一行「擋下:」都應清掉控制字元;結果與擋下訊息裡不應出現 pre-push 用來記逃逸帳的兩串字 [test:t_android_e2e_text_gates]
- [S52] 當提交裡的紀錄超過單份上限(2MB,跟寫入與掃描同一個)時,判定應擋下並叫人修好或刪掉,就算它帶著放行也不放;git 暫時讀不出紀錄時應擋下但不叫人刪;`waive --list` 應標明太大的那份,時間用完講沒讀到幾份 [test:t_android_e2e_record_size_gate]
- [S53] 當開場掛鉤剩下的預算不夠時應少讀並講沒讀;查主線失敗、上一版查不出來時應擋,根提交不擋;這一版自己把驗收設定改弱、整套結果因此不夠時,應叫人把設定改回去、不叫人合主線 [test:t_android_e2e_gate_r4_paths]
- [S54] 當 e2e 區或 macrobench 要印「擋下:」時,應一律走底層的 `_say_block`(過 `_out_clean`:另清換行類字元、方向標記與 BOM,拆開 pre-push 記逃逸帳的兩串字,而那兩串字跟 pre-push 實際比對的一樣);e2e 區的程式不應有直接印「擋下:」的地方;`judge --precheck` 遇到檔名帶換行與 ESC 的未追蹤檔,印出的不應有偽造的獨立一行 [test:t_android_e2e_say_single_exit]
- [S55] 當被推送提交改到的檔名、或 `--changed` 看到的檔名帶控制字元或看不見的字元時,應擋下或回錯誤、叫人先改名;取上一版應走既有的 `_push_rev`,淺層 clone 截斷的歷史應算判不出;查主線一個候選都沒有、被推送提交又沒有設定檔、上一版判不出時應擋;讀提交樹時 git 物件缺應擋但不叫人刪 [test:t_android_e2e_git_names_and_parent]
- [S56] 當工作目錄有超過 2MB 的紀錄時,doctor、開場提示與 `--ack` 應另計成「超過 2MB 沒讀」(不混進讀超過時間);`waive --list` 沒讀完時收尾不應說沒有任何放行;放行寫完會超過上限時應不寫;設定的 exclude、shared_paths 超過上限、路徑超過 64 層(照正規化後算)、帶代理字元或私用區字元時應判不合格 [test:t_android_e2e_big_records]

## 審計修正紀錄

- r1(2026-10-25,6 席:正確性、守衛、邊界、整合、通才、架構對齊):55 條/blocking 32/CI 在 PR 不跑、放行太便宜、APK 沒綁原始碼、紀錄格式與讀法、指紋定義、範本腳本介面、判定分流、接線清單;Enzo 另裁 AI 可放行但要通知、第一版只擋本機推送;55 條全折。
- r2(2026-10-25,6 席同上鏡頭、全新代理):59 條/blocking 33/回退指錯檔、指紋選檔設定與 `e2e` 段雜湊、分岔點算法與 CI、判不清改成擋、驗收中途換版與髒樹範圍、終端答 n、只有放行的紀錄、AI 放行通知落點、RETIRE-IF 資料來源、只有 e2e 段的設定檔、對照表句子正本、鎖殘留與原子寫入;折 58 條、放行 1 條(舊版 lumos 沒有這道判定時不另加版本探測,見 r2-intake.md)。
- 2026-10-26 先加〈只跑某一塊〉(--only 按大類挑),同日 Enzo 說粒度要到功能與使用情境,改寫成〈按功能與使用情境跑〉與 S22–S27,--only 那版沒推就改掉。新設計動到設定格式與收集腳本,spec-gate 判計劃風險高;Enzo 說「直接開工」,沒另開設計審,實作走代碼審、開發完在實驗室實跑。
- 代碼審 code-e2e-by-feature r1(2026-10-26,7 席:正確性、資源、邊界、合約、通才、資安、架構對齊):43 條/blocking 6/按功能跑「不寫紀錄」的說法與實作相反、測試沒守住分岔點與記憶體情境、--changed 漏挑新目錄與 flow 檔、開跑時髒卻記成這一版驗過、總表另起寫法、整套跑漏了記憶體情境;43 條全折,補 S28。
- 代碼審 code-e2e-by-feature r2(2026-10-26,7 席同上):30 條/blocking 7/效能方法名收了 $ 被 sh 展開成別支、不蓋掉完整結果的條件把真失敗也蓋掉、沒有會判項目時三處說法矛盾、紀錄前提與分岔點與整套各判一次沒有測試守住,另有 --changed 邊角、替身收集腳本與殘留情境變數、總表按情境;30 條全折。卷證 governance/review-reports/code-e2e-by-feature/。
- r3(2026-10-26,6 席:正確性、邊界、整合、資源併發、回滾、架構對齊;只審推送前檢查與放行,另含新補的〈推送前怎麼按功能判〉):52 條/blocking 28/判定順序三處打架、指紋變了卻空集合放行、只列效能的情境過不了、讀不懂時偏放行、兩端不對稱、確認與鎖的順序與殘留、放行路徑的提醒行被 pre-push 濾掉、enforcement 語意不合、撤除條件量不到;折 47 條、放行 5 條 minor(見 r3-intake.md)。
- 代碼審 code-e2e-gate r1(2026-10-27,7 席:正確性、邊界、資源、合約與文件、通才、架構對齊、資安):35 條/blocking 13/只改設定就放行、出口排在讀設定之後、只列效能的功能沒紀錄就擋、捷徑指到 /dev/zero 卡住開場掛鉤、自寫的鎖是第二種做法而且有接手競態、--list 原樣印外來文字、幾道判斷沒有測試守;35 條全折(S34 改成不接手殘留鎖,推翻設計審 r3 的折法)。卷證 governance/review-reports/code-e2e-gate/。
- 代碼審 code-e2e-gate r2(2026-10-27,7 席同上、全新代理、加修補鏡頭):28 條/blocking 6/舊分支(兩端都沒有 e2e 段)只改文件被誤擋(r1 修補引入)、本機殘留 CI 變數時整道不判也不留帳、深層巢狀紀錄讓列出指令崩潰、紀錄份數上限沒測試也沒提示、開場掛鉤讀紀錄沒有總時間上限、拿掉 e2e 段時叫人合主線解不開;28 條全折(歸屬判斷改成按路徑前綴查表、掛鉤複本改成逐字相同、預算不讀環境變數)。
- 代碼審 code-e2e-gate r3(2026-10-27,7 席同上、全新代理、加修補鏡頭):39 條/blocking 13/設定值與紀錄鍵名原樣進擋下訊息(r2 只清了檔名)、waive --list 與 --ack 到不了超過 500 份之外的紀錄、查表遇到極深路徑變平方(r2 修補引入)、flows 重複檢查與範圍判斷是平方、shared_paths 寫在 app_dirs 外等於沒寫、跨時差與改名 flow 沒有測試守、--commit 解不到的提交沒有測試守;39 條全折(外來文字改在結果出口統一清,不再逐點補)。這是上限的第三輪,修正差異另見回顧。
- 代碼審 code-e2e-gate r4(2026-10-27,破例加開,7 席同上、全新代理、只審第三輪的修正差異):31 條/blocking 9/放行與設定檢查的錯誤訊息不經結果出口(外來文字第四次出現)、判定讀紀錄的上限是 16MB 跟寫入的 2MB 不一致、太大的紀錄被講成讀超過 60 秒、git 暫時失敗的分流靠比對訊息文字且沒有測試、掛鉤預算沒有測試守、五道沒改乾淨;31 條全折(外來文字改成源頭拒收加指令出口統一清,大小上限判定與寫入同一個)。破例的決定與跑滿回顧見 governance/review-reports/code-e2e-gate/cap-retro.json。
- 代碼審 code-e2e-gate r5(2026-10-27,第二次破例加開,7 席同上、只審第四輪的修正差異):約 30 條/blocking 14/judge 與開工前檢查的擋下行仍原樣印外來檔名(第五次)、控制字元判斷與取上一版另寫一套沒用專案既有的、git 暫時失敗用字串子類別當旗標、macrobench 往上呼叫 e2e 專屬函式、淺層 clone 被當成根提交、太大紀錄裡的放行看不到、幾道新判斷的測試把被測函式整個替換掉;全折(清理搬到底層並加掃語法樹的守衛測試、從 git 取來的檔名源頭擋、改用 _path_special_chars 與 _push_rev、測試改用真的淺層 clone 與真的缺物件)。
- 卷證:governance/review-reports/android端到端驗收/(r1-intake.md、r2-intake.md、r3-intake.md 有逐條重現與去向)

## 回退

- 判定:一次推送要關掉這道,設 `LUMOS_SKIP_ANDROID_E2E=1`(記一筆治理帳);要長期關,從主線版的 `.lumos/macrobench.json` 刪掉 `e2e` 段(刪段的那次推送本身用環境變數關,合進主線後判定就不跑),其他判定不受影響。
- 紀錄與放行:`.lumos/e2e-records/` 是新增的檔,刪掉不影響其他功能;放行寫在治理帳的事件只是統計來源,不影響其他判定。
- 降回只提醒(頂上那條 RETIRE-IF):在程式裡把這道的擋下改成提醒(同新增告警閘的 warn),一次程式改動;不做成設定開關,因為開關放在 `e2e` 段會改指紋、所有紀錄都要重跑。
- 撤掉按功能這條路(〈推送前怎麼按功能判〉的 RETIRE-IF):在程式裡拿掉判定順序第 3 到 6 步(沒有可用的整套結果就擋),一次程式改動;設定裡的 `features`、`shared_paths` 不用刪(刪了會改 `e2e` 段雜湊、所有紀錄要重跑)。已經按功能放行推上去的版本不回頭補驗:之後只要改到 App,指紋一變就要求整套。
- 程式:判定、放行與通知是新增的,回退就是撤掉那次提交。順序:消費專案先刪 `e2e` 段或設環境變數,再還原 lumos;`.lumos/e2e-records/` 留在簿記目錄清單、`_macrobench_config` 接受只有 `e2e` 段的寫法也留著(那兩樣屬於已上線的按功能跑,撤掉會讓已提交的紀錄使代碼審留痕失效、只有 `e2e` 段的設定檔讀不了);還原測試檔的對照表句子要 Enzo 簽章。
