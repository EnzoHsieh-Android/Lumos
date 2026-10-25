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
---
# Android端到端驗收_計劃

白話:Android App 改完、推送之前,在本機接著實機跑一次「端到端驗收」:UI 流程走不走得完(Maestro flow)、畫面跟人核可過的基準圖一不一樣(截圖比對)、效能有沒有變慢、記憶體有沒有洩漏或閃退。跑完寫一份綁在「這一版 App 程式與驗收素材的內容」上的查證紀錄,推送前的 `code-loop check` 檢查這一版有沒有一份通過(或有人放行)的紀錄,沒有就擋推送。第一版只擋本機推送,CI 上擋合併另開一案(見 REVISIT)。毫秒類效能(啟動時間、每幀耗時、凍結幀)第一版只提醒、不擋,等 [[Projects/Android效能判定統計化_計劃]] 的第 1、3、4 條(20 輪、同場比較、太吵指標只列出)都上線再改成擋。2026-10-24 Enzo 提「整合 Maestro,將效能測試、UI 測試成為 Android 端 E2E 的驗收標準」;2026-10-25 對話裡逐段確認了範圍、擋法、做法與三段設計,設計審 r1 之後又裁了放行權與 CI 範圍。

PRIOR-ART: Maestro CLI(`maestro test` 跑 flow,`--format junit --output` 出測試報告、`-e KEY=VAL` 傳參數、`--udid`/`--device` 指定裝置,內建 `assertScreenshot`);使用者自己的 maestro-visual-toolkit(github.com/EnzoHsieh-Android/maestro-visual-toolkit,本機在 ~/harness/maestro-visual-toolkit:人核可基準圖、門檻用環境變數 THRESHOLD(不准低於 99.5)、紅框差異圖、狀態列固定、裝置與 adb 路徑寫在安裝時產生的 `.maestro/visual-env.sh`、用 `.maestro/.lock-<裝置>` 鎖,原本只在模擬器驗過;本 repo 的 [[Projects/Maestro截圖基準比對_調研]] 與 [[Projects/截圖基準驗收流程_計劃]]);Lumos 既有的 Maestro flow 綁功能筆記(`[test:maestro:<名>]`,綁 flow 的 `name:`,[[Projects/Android側UI測試綁圖譜工作流_計劃]]);既有的 Macrobenchmark 判定(`lumos macrobench`,[[Systems/macrobenchmark-adapter]])與記憶體穩定性收集([[Systems/android-stability-collector]]);code-loop check 既有的安全證據判定([[Systems/安全證據閘]]:設定只讀主線版、內部出錯走 fail-open 記帳)與表態判定(證據一律對被推送提交的檔案樹驗);既有的終端確認 `_confirm_tty`(有人在真的終端機答 y 才算人)。借用:以上全部;自建只有一支串四塊的範本腳本、一個彙整判定與寫紀錄的子命令、code-loop check 裡多一道判定、`lumos macrobench` 多一個指定結果目錄的旗標。不選:Maestro Cloud 與 Firebase Test Lab 這類雲端裝置(跟「本機實機跑」的決定衝突,雲端裝置的效能不能當基準);Gradle Managed Devices 的模擬器(同上)。
RETIRE-IF: 連續兩個真實專案跑滿三個月,這道判定擋下後的處置裡「放行」多過「修好再跑通過」(治理帳 android-e2e 的 waived 對照紀錄裡的 pass),或 AI 放行佔全部放行的一半以上,就把擋推送降回只提醒。
REVISIT:[when-status:Projects/Android效能判定統計化_計劃=done][by:2027-06-30] 效能判定統計化第 1、3、4 條都上線後,把毫秒類效能從只提醒改成擋,條款另開
REVISIT:2026-12-31 第一版只擋本機推送:評估加 PR 觸發的 CI 步驟範本(用 PR 分支頂端算指紋、主線分岔點到頂端的樹差異判要不要紀錄),讓專案能把它設成合併前必須通過;另評估 tag 推送要不要也跑這道
REVISIT:2026-12-31 判定在算不出主線分岔點時走 fail-open 記帳:回頭看治理帳 android-e2e 的 failopen 次數,不為零就補一條「算不出就擋」的路

WHY:驗收沒過就擋推送、可以放行 [出處:2026-10-24 Enzo 為 E2E 驗收選「擋合併,人可留痕放行」] [因:驗收沒過的程式不該默默推上去;實機驗收會誤擋,要留一條有紀錄的出口] [不選:只提醒(跟「成為驗收標準」的目的不符);不准放行(誤擋時只能改走略過檢查,沒有紀錄)]
WHY:AI 也能放行,但標成 AI 放的、主動通知人 [出處:2026-10-25 設計審 r1 後 Enzo 選「AI 能放行,但要通知你」] [因:無人看顧時驗收會因裝置狀態誤擋,完全不准 AI 放行會讓流程卡死;但 AI 最省力的路就是放行,要看得到] [不選:只有人能放行(無人看顧時卡死);照舊 10 字理由就放行(事後分不出是人還是 AI)]
WHY:第一版只擋本機推送,CI 擋合併另開一案 [出處:2026-10-25 設計審 r1 後 Enzo 選「第一版只擋本機推送」;原本 10-24 選的「CI 驗收據」延後] [因:現行 CI 只在推到主線時跑 code-loop check,PR 上不跑;做到 PR 要另寫 PR 事件的步驟範本與合併提交的指紋算法,範圍大] [不選:第一版就做 PR 步驟(範圍大、要先把本機這道跑穩)] [代價:略過推送前檢查就擋不住,見 REVISIT]
WHY:做法採「範本腳本碰裝置、lumos 只判定與記帳」 [出處:2026-10-25 Enzo 選做法 A] [因:跟已上線的記憶體收集同一個分工(lumos 不碰裝置)] [不選:lumos 自己操作裝置(要重寫裝置控制、逾時、收尾)] [代價:範本腳本最後會呼叫 lumos android-e2e judge,跑驗收的那台機器要裝相容的 lumos(收集腳本不呼叫 lumos,這點跟它不同)]
WHY:紀錄綁「App 程式與驗收素材的整批內容指紋」,不綁提交編號、也不逐檔列在紀錄裡比 [出處:2026-10-25 Enzo 確認第二段;設計審 r1 架構對齊席要求寫明跟安全證據逐檔比法的差別] [因:壓提交、rebase 之後內容沒變,綁提交編號的留痕會失效、要重跑十幾分鐘的實機驗收;安全證據閘的逐檔比法適合收據列出少數幾支檔,這裡要涵蓋整個 App 程式目錄(可能上萬檔),逐檔列進紀錄太大,整批算一個指紋就夠回答「有沒有任何一支變了」] [不選:綁提交編號(代碼審留痕就因此重做過好幾次);逐檔列進紀錄比(紀錄太大)]
WHY:E2E 紀錄放 `.lumos/e2e-records/`,不放進 skill 的收據目錄 [出處:設計審 r1 架構對齊席要求寫明] [因:收據 `.lumos/receipts/<run-id>/` 是逐層診斷的證據,一次診斷一份、給人與 AI 重跑查詢;E2E 紀錄是推送檢查的輸入,一個指紋一份、要能用指紋直接找到] [不選:放進收據(判定要掃所有收據找指紋,收據格式也要為判定加欄位)]
WHY:Maestro flow 第一次失敗自動重跑一次,第二次過算過但紀錄標不穩定 [出處:2026-10-25 Enzo 確認第一段] [因:Maestro 常因動畫、載入時間偶發失敗;不留標記又會把不穩定的 flow 藏起來] [不選:不重跑(誤擋);重跑到過為止(藏住真問題)]
WHY:毫秒類第一版只提醒 [出處:2026-10-25 Enzo 選「毫秒類先只提醒」;[[Verification/2026-10-24_效能判定規則實機評測]]] [因:毫秒數字跨時段會漂,判定規則還沒校準完] [不選:四塊全擋(誤擋多)]

## 設定(`.lumos/macrobench.json` 的 `e2e` 段)

跟記憶體與穩定性一樣,放進既有的 `.lumos/macrobench.json` 當一段,不另開設定檔。推送檢查只讀主線那一版的這一段(跟安全證據閘「設定只讀主線版」同一個理由:被推送的提交不能自己決定要不要被檢查);同一個提交裡刪掉或改弱這一段,要等合進主線才生效。

- `app_dirs`(必填,至少一項):App 程式的目錄或檔,相對專案根(例 `["app", "gradle/libs.versions.toml", "settings.gradle.kts"]`);每一項在主線版的檔案樹裡都要存在,不得包住 `.lumos/`。目錄以「整段路徑」比對(`app/src` 不含 `app/src2`)。
- `exclude`(選填):`app_dirs` 底下不算進指紋、也不觸發要求的子路徑;沒寫時預設排除每個模組的 `src/test/` 與 `src/androidTest/`(只改單元測試不用重跑實機)。
- `package`(必填):App 套件名,規則跟收集腳本一樣;有 `stability` 段時兩邊要一致,不一致 check-config 回 2。`adb_serial` 同理(選填)。
- `build`(必填):建 APK 的指令(例 `./gradlew :app:assembleBenchmark`),範本腳本在乾淨的工作目錄上照它建;`apk`(必填)是建出來的 APK 路徑。
- `flows`(必填,至少一支):驗收用的 Maestro flow 路徑;截圖用的 flow 不要放這裡(toolkit 的截圖 flow 註解寫明不能跟其他 flow 一起全跑)。
- `visual`(選填):截圖比對的畫面名清單,照 toolkit 慣例帶 `_visual` 後綴(flow 是 `.maestro/<畫面名>.yaml`、基準圖是 `.maestro/baseline/<畫面名>.png`);`visual_threshold` 選填、預設 99.5、不得低於 99.5。用之前要先照 toolkit 的 `install.sh --platform android --device <序號> --app-id <套件名>` 裝好。
- `macrobench`(選填,預設 false):要不要跑效能這塊;要的話 `macrobench_cmd` 是跑 Macrobenchmark 的指令。
- `stability`(選填,預設 false):要不要跑記憶體與穩定性這塊;要的話用同檔既有的 `stability` 段設定(驅動指令換成 Maestro flow),`stability_checks` 列這一塊要求的 check(預設 native_unreachable、java_growth、instances、peak_vitals、exits、strictmode),門檻檔 `.lumos/macrobench-thresholds.json` 裡每一個都要有寫了 check 的條目,缺一個 check-config 回 2。
- 驗收素材:`flows` 的檔、`visual` 對應的 flow 與基準圖、門檻檔、這一段設定本身,都算進指紋(見〈查證紀錄〉);換基準圖或改門檻都要重跑。

## 第一次接入的順序

1. 裝 Maestro CLI(2.8 以上);要截圖的話照 toolkit 的 README 裝進專案、在實機上把每個畫面開到定位、人看過再用 `.maestro/visual-record.sh <畫面名>` 錄基準圖,基準圖跟 flow 一起開 PR 給人看。
2. 要效能或記憶體的話,先照既有說明接好 `lumos macrobench`(基準、門檻)與收集腳本(`stability` 段、門檻檔的 check 條目)。
3. 寫 `e2e` 段,跑 `lumos android-e2e check-config`(驗格式)與 `lumos android-e2e check-config --env`(驗環境:maestro 在不在、toolkit 腳本與基準圖在不在、裝置有沒有連上而且沒鎖屏、產物目錄有沒有被 git 忽略),兩個都過再跑第一次驗收。
4. 段落合進主線之後,推送檢查才開始要求紀錄。

## 一次驗收跑什麼(四塊)

| 塊 | 怎麼跑 | 怎麼判 | 沒過時 |
|---|---|---|---|
| UI 流程(必有) | `flows` 每支 `maestro test --format junit --output <run>/ui/<名>.try1.xml`(有序號時加 `--udid`);沒過再跑一次寫 `.try2.xml` | 回傳碼是 0 而且報告裡至少一個測試案例、沒有失敗才算這一次過;第一次過→過;第一次沒過、第二次過→過、標不穩定;兩次都沒過→沒過 | 擋 |
| 截圖比對(有 `visual` 才跑) | 每個畫面 `THRESHOLD=<visual_threshold> MAESTRO_DEVICE=<序號> .maestro/visual-check.sh <畫面名> <run 的絕對路徑>/visual/<畫面名>` | 回傳碼 0 算過;1(不相符或環境問題)與 2(缺基準圖、參數錯)都算沒過,原因與(不相符時才有的)相符率照腳本輸出記 | 擋 |
| 毫秒類效能(`macrobench: true` 才跑) | 照 `macrobench_cmd` 跑完,把這次開始後才產生的結果檔複製到 `<run>/macrobench/`,`lumos macrobench --json --results-dir <run>/macrobench`(新旗標:這次只讀這個目錄,不讀 `results_dirs`;基準照舊用專案的) | 退步、毫秒類門檻沒達、沒有基準、輪數不足都只寫進 notices;這塊沒跑成也只寫 notices | 只提醒 |
| 記憶體與穩定性(`stability: true` 才跑) | 收集腳本用同一個 run-id 跑(它把結果寫在 run 目錄最上層),再 `lumos macrobench --json --stability <run>/stability.json` | 只看門檻條目帶 check、而且 check 在 `stability_checks` 裡的:在 threshold_failures→沒過;在 threshold_skipped、或整段 stability_unjudged、或那個 check 根本沒出現在任何清單→沒判到;frozen 與沒帶 check 的門檻只寫 notices;收集腳本或 `lumos macrobench` 回非 0→這塊沒跑成 | 擋(沒判到也擋;frozen 只提醒) |

## 資料怎麼流

0. 前置(實作第一步,做完才寫範本腳本):在 SM-X710 上實測兩件待驗事項,結果寫進本計劃再往下:Maestro flow 的 `repeat` 的 `times` 吃不吃 `${CYCLES}`(不行就改用 `while` 加計數,並改 skill reference 的 Maestro 驅動範例);toolkit 的狀態列固定在實機上固定得住(固定不住先問 Enzo 要改截圖範圍還是另找做法,截圖這塊在那之前不進第一版)。
1. 範本腳本 `android-e2e-run.sh`(工具鏈範本,跟收集腳本放一起),在專案根跑:
   - 開跑前檢查:`app_dirs` 與驗收素材在工作目錄沒有未提交的改動(有就停,因為紀錄要綁提交)、裝置連上而且沒鎖屏、沒有另一次驗收在跑(`.lumos/artifacts/android/.e2e-lock`)、maestro 在、要截圖時 toolkit 腳本與基準圖在;上一次被強制中斷留下的 `.maestro/.lock-<序號>`,在確認沒有 visual-check.sh 正在跑之後才清。
   - run-id 預設 `e2e-<年月日>-<時分秒>`,run 目錄 `.lumos/artifacts/android/<run-id>/`(產物目錄必須被 git 忽略):ui、visual、macrobench 三個子目錄,記憶體與穩定性的輸出照收集腳本放在 run 目錄最上層。
   - 依序:照 `build` 建 APK、裝上去並記下裝置上實際安裝那份的 sha256、UI 流程、截圖、效能、記憶體與穩定性;結束時再讀一次裝置上安裝那份的 sha256(中途被換掉,紀錄記成沒跑成)。
   - 每一步的回傳碼、開始結束時間、每次嘗試的報告路徑寫進 `<run>/steps.json`(judge 讀它);任一步失敗也繼續把剩下的跑完;被 Ctrl-C 或 TERM 中斷時,寫下「中斷」再呼叫 judge。
2. 最後呼叫 `lumos android-e2e judge <run 目錄>`:讀 `steps.json` 與四塊的輸出、照上表判、對目前 HEAD 提交的檔案樹算指紋(工作目錄在 `app_dirs` 或驗收素材有未提交改動時拒絕寫紀錄),寫進 `.lumos/e2e-records/<指紋>.json`;終端印每一塊的結果、沒過的原因與證據路徑。
3. 紀錄要提交進版控;`.lumos/e2e-records/` 跟其他簿記檔一樣,在代碼審留痕之後提交不會讓留痕失效(實作時把它加進簿記目錄清單,並看過那份清單的其他用處)。
4. 推送前 `code-loop check` 多一道「Android E2E 驗收」判定:
   - 何時要求:主線版有 `e2e` 段,而且「主線分岔點的指紋」跟「被推送提交的指紋」不同(看兩端的樹差異,不逐提交看:改了又改回來就不要求)。主線分岔點用既有推送範圍的算法;算不出來(沒有主線、淺層 clone)時這道走 fail-open 並記一筆治理帳(見 REVISIT)。
   - 怎麼判:從被推送提交的檔案樹讀 `.lumos/e2e-records/<指紋>.json`(不讀工作目錄;沒提交的紀錄不算);紀錄裡的指紋欄位要等於檔名、等於重算值;最近一次結果是 pass、或有任何一筆放行 → 過;找不到、最近一次是 fail 或 unjudged 而且沒有放行 → 擋,印出哪一塊沒過、紀錄路徑、要跑的指令(重跑驗收,或放行)。
   - 紀錄讀不懂(JSON 壞掉、schema 比這版 lumos 新、result 不是認得的值、指紋欄位對不上)→ 擋(回 1),不走 fail-open,訊息說要重跑驗收或更新 lumos。其他沒料到的內部錯誤照 code-loop check 既有做法:接住、記一筆 fail-open 治理帳、這道放行。
   - 位置與接線:跟安全證據判定一樣排在所有放行早退之前;擋下種類 `android_e2e`,接進 `_cl_say_block`、`_codeloop_kg_finish` 的明細、pre-push 的擋下原因對照表(連同比對兩邊的測試)與逃生路那段文字、ci.yml 的擋下說明;擋下訊息不得含 pre-push 用來記逃逸帳的那兩串字。
   - CI:推到主線時分岔點就是頂端,這道不要求;第一版不另外接 CI(見 REVISIT)。tag 推送只跑安全證據,這道不跑(同上)。
5. 放行 `lumos android-e2e waive [<指紋>] --note "<理由>"`(預設放行被推送提交的指紋):
   - 理由去掉空白後至少 10 個字。
   - 用 `_confirm_tty` 問一次「確定放行嗎」:有人在終端機答 y → 記成人放行(誰取 git 的 user.name,沒設就取登入帳號);沒有互動終端或沒人回答 → 記成 AI 放行。
   - 放行寫在紀錄的 `waivers` 清單(只增不刪,之後重跑 judge 不會蓋掉);沒有紀錄就新建一份只有放行的紀錄。
   - 治理帳記一筆:閘名 `android-e2e`、事件種類 `waived`(閘名登記進已知閘名清單),附人或 AI、指紋、理由。
   - 通知:`lumos doctor` 與開場的 lumos 提示列出還沒被人看過的 AI 放行;人用 `lumos android-e2e waive --ack <指紋>`(同樣要終端確認)標成看過。

## 查證紀錄長怎樣

- `schema`:格式版本(第一版是 1);判定遇到比自己新的版本就擋,請人更新 lumos。
- `fingerprint`:對一個提交的檔案樹,取 `app_dirs` 底下(扣掉 `exclude`)與驗收素材的每一個項目,用 `git ls-tree -r -z` 的 mode、型別、物件編號與路徑,依路徑的位元組順序排好,每一項寫成「mode、物件編號、路徑」三段、段與段之間用 NUL 分開、每項後接換行,整串算 sha256。用 git 物件編號而不讀檔案內容:大 repo 也快、子模組用它記的提交編號、符號連結用它指向的路徑、Git LFS 用指標檔,改權限(mode)也會讓指紋變。
- `runs`:只留最近一次的結果(每一次 judge 覆蓋這一欄,不動 `waivers`):result(pass、fail、unjudged)、run-id、開始與結束時間(本機時區、帶時差的 ISO 格式)、裝置型號與系統版本、建出的 APK 與裝置上實際安裝那份的 sha256、判定的提交編號、四塊明細(每支 flow 的結果與是否不穩定、每個畫面的結果與原因、效能與記憶體每條的結果與原因)、`notices`(只提醒的項目)。
- `waivers`:每筆放行的人或 AI、誰、時間、理由、有沒有被人看過。
- 寫入一律用既有的原子寫入(先寫暫存檔再換名,暫存檔放在系統暫存目錄,不放進 `.lumos/e2e-records/`),judge 與 waive 都是「讀出整份、合併、整份寫回」。
- 原始檔只在本機;紀錄只放摘要與數字。
- 改了 `app_dirs`、`exclude`、驗收素材或 `e2e` 段本身,指紋就全變、舊紀錄都對不上,要重跑一次:這是刻意的(驗收的範圍或標準變了就該重驗),不做舊紀錄遷移。舊紀錄檔不自動刪,一份只有幾 KB;run 目錄在被 git 忽略的產物目錄,清理照產物目錄既有做法由人清。
- 指紋只用 `git ls-tree` 列出的物件編號,不讀檔案內容,上萬檔的目錄也是一次 git 呼叫。

## 這次要改到的地方

- 新子命令 `lumos android-e2e`(judge、waive、check-config)與它的家 `Systems/android-e2e-acceptance`(新開;code-loop check 那一道的細節也寫在這裡,跟安全證據閘、表態閘各有自己的家一樣)。
- `code-loop check` 多一道判定:[[Systems/pitfalls-code-loop]] 只加一行連結,不寫細節。
- `lumos macrobench` 加 `--results-dir`:寫進 [[Systems/macrobenchmark-adapter]]。
- pre-push 的擋下原因對照表與逃生路文字、ci.yml 的擋下說明:寫進它們的家 [[Systems/bound-tests-gate]]。
- 簿記目錄清單加 `.lumos/e2e-records/`:寫進 [[Systems/pitfalls-code-loop]] 那一行。
- 治理帳已知閘名加 `android-e2e`;`lumos doctor` 與開場提示列出沒人看過的 AI 放行。
- 新範本腳本 `android-e2e-run.sh` 放 `scripts/templates/`,家是 `Systems/android-e2e-acceptance`;收集腳本不改。
- skill lumos-android-evidence:reference.md 的 Maestro 驅動範例照前置實測修正;補「E2E 驗收」一節(接入順序、怎麼跑、紅了看哪裡、怎麼放行、AI 放行會被列出來)。
- 實驗室專案 macrobench-lab 加 Maestro flow、截圖基準、可注入的 UI 錯與 `e2e` 段,驗收用。
- 試點真專案:Citrus_KDS(現在沒有 `.maestro`、沒有 macrobench 設定,要從零接)。已知坑:KDS 在 SM-X710 用 benchmark-macro 1.2.4 跑不起來,實驗室用 1.4.1 可以([[Verification/2026-10-23_macrobench實機端到端]]);接 KDS 時要升版,改 KDS 依賴前先問 Enzo。

## 不做

- 毫秒類效能擋推送(等統計化計劃第 1、3、4 條,見 REVISIT)。
- CI 上擋合併、tag 推送跑這道(見 REVISIT)。
- iOS 端;雲端裝置或 CI 上跑實機驗收。
- 驗證紀錄真的是在實機跑出來的、AI 不會冒充人回答終端確認:照 Lumos 的威脅模型(單人、AI 依序操作,不防刻意偽造)不另外防。
- 改 pre-push 對工具出錯時放行(fail-open)的既有行為;改收集腳本。

## 實務隱患

- 已排除:金流:只讀驗收輸出與程式檔,不碰交易。
- 已排除:對外送出:驗收在本機跑,紀錄只進專案自己的 git,不送到外部服務。
- 已排除:不可逆:紀錄與放行都是新增的檔與帳,放行只增不刪;刪掉紀錄就回到沒驗收的狀態;不刪除任何專案檔(只清確認沒人在用的 toolkit 鎖目錄)。
- 守衛面:這是一道新的擋推送判定,誤擋會卡住開發、漏擋會讓沒驗收的程式推上去;兩邊都要有實驗室證據(見〈實驗室驗收〉)。
- 第一版略過推送前檢查就擋不住;CI 不補查(見 REVISIT)。
- `app_dirs` 漏列影響 App 行為的檔(其他模組、根目錄 gradle 檔、混淆設定),改了它們不會要求重驗;check-config --env 對 settings.gradle 列出、卻不在 `app_dirs` 的模組印提醒。
- Maestro flow 與截圖都受裝置狀態影響(通知、鍵盤、系統對話框、狀態列時間),是誤擋主要來源;截圖要先在 SM-X710 實測狀態列固定得住(前置)。
- 一次驗收的時間:實驗室 App 上效能 20 輪就約 9 分鐘,加其他三塊更久;真專案可能到幾十分鐘,時間太長會讓人放行或略過檢查(見 RETIRE-IF)。

## 實驗室驗收

在 macrobench-lab 上每一塊各準備「應該擋」與「不該擋」,每一組都要照預期:

- UI 流程:應該擋=按鈕失效不跳頁、清單少一列(兩次都沒過);不該擋=正常版連跑 5 次都過;偶爾慢一點才出現的畫面要被標成不穩定、不擋。
- 截圖:應該擋=元素位置跑掉、一整塊不見、文字被切;不該擋=只有時間電量變、同一版本連拍 3 次都相符。只差幾個字抓不到,列為限制。
- 效能與記憶體:應該擋=Java 套件沒 release、C/C++ 套件沒 release、中途閃退(改由 Maestro 驅動);只提醒不擋=注入啟動變慢、每列變慢。
- 擋推送:應該擋=改了 App 程式沒跑驗收就推、跑了沒過、改程式後拿舊紀錄改檔名充數、換了基準圖沒重跑、同一個提交裡刪掉 e2e 段;不該擋=只改文件、只改單元測試、沒過但有人放行、壓提交或 rebase 後內容沒變、改了又改回來。
- 放行:AI 放行會出現在 doctor;人標看過後不再列。

## 條款

- [S1] 當 `.lumos/macrobench.json` 的 `e2e` 段缺必填欄位(app_dirs、package、build、apk、flows)、型別不對、`visual_threshold` 不是有限數或低於 99.5、`package` 含英數字底線與點以外的字元、路徑跳出專案根、`app_dirs` 有一項在檔案樹裡不存在或包住 `.lumos/`、跟 `stability` 段的 package 或 adb_serial 不一致、或要了記憶體與穩定性卻有 `stability_checks` 列的 check 在門檻檔裡沒有條目時,`lumos android-e2e check-config` 應回 2 並印出哪個欄位哪裡壞;合格時回 0 [test:t_android_e2e_config_strict]
- [S2] 當計算指紋時,lumos 應只從指定提交的檔案樹,用每一項的 mode、物件編號與路徑(NUL 分隔、依路徑位元組排序)算 `app_dirs` 扣掉 `exclude` 加上驗收素材;目錄外的檔、預設排除的單元測試、工作目錄沒提交的改動、提交編號都不影響指紋;目錄內任一檔內容或權限改了、換了基準圖或門檻,指紋就變;`app/src` 不含 `app/src2`;子模組與符號連結不讓計算出錯 [test:t_android_e2e_fingerprint]
- [S3] 當判 UI 流程時,`lumos android-e2e judge` 應照 `steps.json` 的回傳碼與每次嘗試的報告判:回傳碼 0、至少一個測試案例、沒有失敗才算那一次過;第一次過→過;第一次沒過、第二次過→過並標不穩定;兩次都沒過、或回傳碼 0 但報告零案例→沒過 [test:t_android_e2e_judge_ui]
- [S4] 當判截圖比對時,judge 應在 visual-check.sh 回傳碼是 0 時才算那個畫面過;回傳碼 1 或 2、或缺結果都算沒過並記下原因,不相符時記相符率與差異圖路徑;沒設定 `visual` 時這塊記成未設定、不影響 result [test:t_android_e2e_judge_visual]
- [S5] 當判效能與記憶體時,judge 應把效能退步、毫秒類門檻沒達、沒有基準、輪數不足、這塊沒跑成都只寫進 notices;記憶體與穩定性只看帶 check 且在 `stability_checks` 裡的條目:在 failures 時 result 是 fail,在 skipped、整段沒判、或那個 check 沒出現在任何清單時 result 是 unjudged;frozen 只寫 notices [test:t_android_e2e_judge_perf_memory]
- [S6] 當會擋的那幾塊(UI 流程、有設定的截圖、有設定的記憶體與穩定性)有工具沒跑成、APK 沒裝成或中途被換掉、或這次被中斷時,judge 應讓 result 不是 pass [test:t_android_e2e_judge_tool_failure]
- [S7] 當工作目錄在 `app_dirs` 或驗收素材有未提交改動時,judge 應拒絕寫紀錄並回 2 [test:t_android_e2e_judge_dirty_tree]
- [S8] 當主線版有 `e2e` 段、而且主線分岔點與被推送提交的指紋不同時,`code-loop check` 的 Android E2E 判定應從被推送提交的檔案樹讀紀錄:最近一次是 pass、或有放行→放行;找不到、最近一次是 fail 或 unjudged 而且沒有放行→回 1 擋下並印出哪一塊沒過與要跑的指令;兩端指紋相同(只改文件、只改單元測試、改了又改回)→不要求;主線版沒有 `e2e` 段→不跑 [test:t_android_e2e_gate]
- [S9] 當被推送的提交自己刪掉或改弱 `e2e` 段時,判定應照主線版的設定判 [test:t_android_e2e_gate_reads_mainline_config]
- [S10] 當紀錄沒提交、紀錄的指紋欄位跟檔名或重算值對不上、JSON 壞掉、schema 比這版新、或 result 不是認得的值時,判定應擋下(回 1),不走 fail-open [test:t_android_e2e_gate_bad_record]
- [S11] 當分支被壓提交或 rebase、App 程式與驗收素材的內容沒變時,判定應照舊認得原本的紀錄 [test:t_android_e2e_gate_survives_rebase]
- [S12] 當 code-loop check 有其他判定會提早放行時,Android E2E 判定應仍然先跑;擋下時 `--keep-going` 的機讀行、pre-push 的擋下原因與逃生路都要印出 android_e2e 的說明 [test:t_android_e2e_gate_wiring]
- [S13] 當執行 `lumos android-e2e waive --note <理由>` 時,lumos 應在理由去掉空白後少於 10 個字時回 2;成功時把放行加進紀錄的 waivers(沒有紀錄就新建)、之後重跑 judge 不會蓋掉;有人在終端機答 y 時記成人放行、沒有人回答時記成 AI 放行;治理帳記一筆 android-e2e 的 waived [test:t_android_e2e_waive]
- [S14] 當有還沒被人看過的 AI 放行時,`lumos doctor` 應列出它們;人用 `waive --ack` 確認後不再列 [test:t_android_e2e_ai_waiver_notice]
- [S15] 當 `lumos macrobench` 帶 `--results-dir <目錄>` 時,應只讀那個目錄底下的結果檔、照舊用專案的基準與門檻 [test:t_macrobench_results_dir]
- [S16] 當範本腳本 `android-e2e-run.sh` 跑完、中途有一步失敗、或被中斷時,它應寫出 `steps.json` 並呼叫 judge,不留下沒有紀錄的半套結果;開跑前檢查沒過(工作目錄有未提交改動、裝置沒連上或鎖屏、另一次驗收在跑)時不開跑並說原因 [test:t_android_e2e_run_script]
- [S17] 當開始實作時,應先在 SM-X710 上實測 Maestro repeat 吃不吃 ${CYCLES} 與 toolkit 狀態列固定得住,兩項各寫下「可以」或「不行與改法」;狀態列不行時截圖這塊不進第一版 [manual:前置兩項實測結果寫進〈資料怎麼流〉第 0 步之後]
- [S18] 當在 macrobench-lab 上照〈實驗室驗收〉逐組跑時,每一組都應照預期(UI 正常版 5 次全過、截圖同版本 3 次全相符、應該擋的全擋、不該擋的全放);任一組不照預期就算沒過,修好重跑那一組 [manual:SM-X710 上逐組跑,每組結果寫進驗證紀錄]
- [S19] 當在 Citrus_KDS 上接 E2E 驗收時,至少 UI 流程這塊應跑得起來、紀錄寫得出來、推送檢查認得它,並記下一次驗收實際花多少時間;超過 30 分鐘時在驗證紀錄寫一條縮短的回頭條件;Enzo 不同意升 benchmark-macro 時,效能與記憶體兩塊在 KDS 不開、照實寫進驗證紀錄 [manual:SM-X710 上跑一次,時間、各塊結果與沒開的塊寫進驗證紀錄]
- [S20] 當 AI 照 lumos-android-evidence skill 接 E2E 驗收時,skill 應寫明接入順序、怎麼跑、紅了看哪裡、怎麼放行與 AI 放行會被列出來 [manual:讀 skill 的 E2E 驗收一節,五件事都寫到]

## 審計修正紀錄

- r1(2026-10-25,6 席:正確性、守衛、邊界、整合、通才、架構對齊):55 條/blocking 32/CI 在 PR 不跑、放行太便宜、APK 沒綁原始碼、紀錄格式與讀法、指紋定義、範本腳本介面、判定分流、接線清單;Enzo 另裁 AI 可放行但要通知、第一版只擋本機推送;55 條全折。
- 卷證:governance/review-reports/android端到端驗收/(r1-intake.md 有逐條重現與去向)

## 回退

- 判定:專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑,其他判定不受影響。
- 紀錄與放行:`.lumos/e2e-records/` 是新增的檔,刪掉不影響其他功能;放行寫在治理帳的事件只是統計來源,不影響其他判定。
- 程式:新子命令與 `code-loop check` 那一道是新增的,回退就是撤掉那次提交;既有判定的程式碼不改。
