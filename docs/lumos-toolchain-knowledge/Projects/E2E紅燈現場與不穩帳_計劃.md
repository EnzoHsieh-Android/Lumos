---
type: project
status: doing
created: 2026-10-27
updated: 2026-10-27
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/android-e2e-acceptance
related:
  - "[[Projects/Android端到端驗收_計劃]]"
  - "[[Systems/android-stability-collector]]"
decisions:
  - content: 紅燈時的手機日誌只收 crash 緩衝、只收那次嘗試開跑之後的,不留整份日誌也不留 App 自己的日誌
    id: d1
    context: "flow 紅燈時要不要把手機日誌留成現場。既有的記憶體收集腳本刻意不留整份日誌(整台裝置的日誌常含帳號、權杖、網址,run 目錄會在本機留好幾天),只留 StrictMode 違規那幾行,見 Systems/android-stability-collector 那條 WHY"
    alternatives: 甲=只收 crash 緩衝、只收那次嘗試之後的;乙=收這個 App 行程開跑之後的全部日誌;丙=不收日誌,只留 Maestro 自己的現場
    why_chosen: Enzo 2026-10-27 選甲。App 閃退時看得到是哪一行,外洩面最小,跟收集腳本不留整份日誌的決定一致;乙會留下 App 自己印的帳號與網址,等於推翻那條決定的一部分
    trade_offs: 抓不到沒有閃退的錯誤訊息(例如 API 回錯、App 自己記的警告);crash 緩衝裡也可能有同一段時間別的 App 的崩潰,沒有再按套件過濾
    decided: 2026-10-27
    valid: true
---
# E2E紅燈現場與不穩帳_計劃

白話:Android 端到端驗收的 UI 流程紅了,現在只留一份測試報告(JUnit),AI 只看得到「哪一步沒過」,看不到當時畫面長怎樣、App 有沒有閃退,只能重跑去猜。另一方面,「第二次才過」只標在那一次,同一支 flow 連續十次都靠重跑才過也沒人知道。這份計劃補兩件事:①每次跑 flow 都把 Maestro 自己的現場(逐步記錄、失敗截圖、畫面結構)收進這次的 run 目錄,沒過時另收這段時間的閃退紀錄;②本機總表記下每支 flow 是不是第二次才過,最近常這樣的 flow 在判定結束時點名,`lumos android-e2e history --flaky` 看彙總。只多留證據、只提醒,過不過的判法不變。2026-10-27 Enzo 在 E2E 優化方向裡選了這兩項先做,閃退紀錄的範圍由 Enzo 裁(見 d1)。

PRIOR-ART: 最小解在既有的範本腳本與 judge 裡:腳本本來就逐次跑 `maestro test`、steps.json 每一步有欄位可加,本機總表本來就逐項記結果,只是沒記不穩。世界解過:①Maestro CLI 官方的 `--test-output-dir`(這次的 manifest、commands、logs、截圖)與 `--debug-output` 加 `--flatten-debug-output`(maestro.log、失敗自動截圖,不建時間戳子目錄,官方註明適合 CI),本機 Maestro 2.10.0 的 `maestro test --help` 兩個都有;②Android 的 crash 緩衝(`adb logcat -b crash`)只放 App 崩潰的堆疊,配 `-d -T <裝置時間>` 只讀某個時間點之後的,不清裝置的共用緩衝(收集腳本讀日誌也用 `-T` 這招);③不穩測試的業界做法:Bitrise 把先紅、重跑變綠的標成 flaky,Delivery Hero 近 20 天通過率低於 80% 自動隔離,Tuist 分「照跑不擋」與「不跑」兩種隔離。裁定:借用前兩者原樣接上;不穩帳借「依歷史次數點名」的形狀,但第一版只提醒、不隔離(隔離等於放寬擋法,要先有數字再請人裁,見 REVISIT)。
RETIRE-IF: 上線三個月後看兩個真實專案的本機總表:紅燈的那幾次都沒產生閃退紀錄檔、排查時也沒人引用 Maestro 現場,就把現場收集拿掉;不穩帳提醒零觸發,或點名過的 flow 有一半以上沒人改、之後也自己不再不穩(提醒是雜訊),就把點名與 `--flaky` 撤掉。
REVISIT:2027-01-31 看兩個專案總表裡不穩帳點名的次數與之後有沒有人修;有一半以上被點名後兩週內修好,評估第二步「點名夠多次的 flow 照跑但不擋」要不要做(要人裁,會放寬擋法);窗口 20 次與門檻 3 次照實際分布重定
REVISIT:2027-01-31 數兩個專案 run 目錄裡 `ui/` 底下的大小,單次驗收超過 200 MB 就改成只在沒過的那次留 Maestro 現場

## 一次 UI 流程多留什麼

1. 開跑前檢查問一次 `maestro test --help`:兩個旗標(`--test-output-dir`、`--debug-output`)都在才開現場收集;舊版 Maestro 沒有就印一行提醒、照舊跑,不擋(擋掉等於逼人升 Maestro 才能驗)。
2. 每次嘗試(第一次、重跑那次)都帶 `--test-output-dir <run>/ui/<名>.try<N>` 與 `--debug-output <run>/ui/<名>.try<N>/debug --flatten-debug-output`。放在 run 目錄底下,開跑前「產物目錄有沒有被 git 忽略」那道檢查一起涵蓋。通過的那次也留:Maestro 不帶這兩個旗標時本來就寫到使用者目錄,只是換個地方,而且第二次才過的那次,第一次的現場正是要看的。
3. 每次嘗試開跑前讀一次裝置時間(`adb shell date`,同收集腳本的格式);那次沒過(回傳碼不是 0)時讀 `adb logcat -b crash -d -T <那個時間>`,有內容才寫成 `<run>/ui/<名>.try<N>.crash.txt`。不清裝置的日誌、不讀其他緩衝;讀不到裝置時間就不收(不退回讀整個 crash 緩衝)。
4. steps.json 那一步多記 `evidence`(現場目錄、閃退紀錄檔或 null);judge 把沒過那幾次的現場路徑分成現場目錄與閃退紀錄兩欄帶進 UI 結果的 `fail_evidence`(印的時候照欄位,不看檔名),終端在沒過或第二次才過的 flow 後面印「現場 …」「閃退紀錄 …」。

## 不穩帳

1. 本機總表每一筆 UI 項目,第二次才過時多一個 `"flaky": true`(第一次就過、沒過、沒判到的照舊不帶這個鍵)。按功能跑時,總表那行每個情境自己的項目也帶(`history --case` 讀那份);提交的查證紀錄裡的情境結果不帶(見〈不做〉最後一條)。
2. 判定記完總表後(範本腳本帶 `--history`、這次有判出 UI 結果),對這次跑到的每支 flow 數總表最近 20 筆「有跑到它而且判出過或沒過」的紀錄裡,第二次才過的有幾筆(同一個 run 目錄重判會在總表多寫幾行,同一次執行只算一次,取那支 flow 最後一個判出結果的那次;重判被擋下、項目是空的那行不算);到 3 筆以上就在終端印一行點名:哪支 flow、幾次裡幾次、該怎麼做(先看那幾次第一次的現場,修 flow 的等待或 App 的時序,不要靠重跑)。
3. `lumos android-e2e history --flaky`:彙總最近 `--last` 次執行(預設 20;數的是不同執行,同一次執行重判多寫的行不佔名額、只算一次,數法跟點名同一套)的紀錄,照功能、情境篩過的也算得到,每支有第二次才過的 flow 一行:幾次裡幾次、最近一次的證據目錄;一般的 `history` 每行多列「第二次才過:…」。
4. 只提醒:不改判定結果、不影響回傳碼、推送前檢查不看它。

## 不做

- 不錄影(`maestro record` 要另外再跑一次 flow,多一倍時間,現場截圖與逐步記錄已經夠定位)。
- 不留整份日誌、不留 App 自己的日誌(d1)。
- 不自動隔離不穩的 flow(見 REVISIT)。
- 不改重跑次數與判法(第一次沒過重跑一次、第二次過算過標不穩,照 [[Projects/Android端到端驗收_計劃]])。
- 不把不穩帳放進提交的查證紀錄:查證紀錄綁版本、每版一份,跨版本的次數只有本機總表數得出來。

## 這次要改到的地方

- `scripts/templates/android-e2e-run.sh`:開跑前問 Maestro 旗標、每次嘗試帶兩個旗標、讀裝置時間、沒過時收閃退紀錄、steps.json 記 `evidence`。家是 [[Systems/android-e2e-acceptance]]。
- `scripts/lumos`:judge 的 UI 結果帶現場路徑、終端印現場、總表記 `flaky`、判定後點名、`history --flaky`。家同上。
- skill lumos-android-evidence〈紅了看哪裡〉一段補現場與閃退紀錄的位置、`history --flaky`。

## 實務隱患

- 個資:閃退堆疊可能帶例外訊息裡的資料;只收 crash 緩衝、只收這次嘗試之後的,寫在被 git 忽略的 run 目錄(跟截圖、JUnit 報告同一處、同一套由人清的做法)。Maestro 的現場有畫面截圖與畫面結構文字,跟截圖比對那塊留的東西同一類。
- 磁碟:每次嘗試多一個現場目錄;失敗截圖只在沒過時產生,見 REVISIT。
- 相容:舊版 Maestro 沒有那兩個旗標,問 `--help` 判斷,沒有就不帶(帶了不認得的旗標會讓每支 flow 都紅,等於誤擋)。
- 時間:每次驗收多問一次 `--help`,每次嘗試多一次 `adb shell date`,沒過時多一次讀日誌,各在一兩秒內。
- 已排除:金流:只多寫本機被 git 忽略的檔與本機總表,不碰交易。
- 已排除:對外送出:現場與閃退紀錄只寫在本機 run 目錄,不送任何外部服務。
- 已排除:不可逆:多寫的檔都在被忽略的 run 目錄或本機總表,撤掉照回退節刪程式即可,不留要人收拾的東西。
- 已排除:守衛面:判法、回傳碼與推送前判定都不變;總表多一個鍵,讀它的只有 `history` 與這次的點名。

## 條款

- [S1] 當 `maestro test --help` 列了 `--test-output-dir` 與 `--debug-output` 時,範本腳本每次跑 flow(含重跑那次)應帶 `--test-output-dir <run>/ui/<名>.try<N>` 與 `--debug-output <run>/ui/<名>.try<N>/debug --flatten-debug-output`;沒列時兩個都不帶、印一行提醒、照常跑完 [test:t_android_e2e_evidence_flags]
- [S2] 當某次嘗試回傳碼不是 0 時,範本腳本應用那次開跑前讀到的裝置時間讀 crash 緩衝(`logcat -b crash -d -T`),有內容才寫成 `<名>.try<N>.crash.txt`;回傳碼 0 時不讀;讀不到裝置時間時不讀;任何情況都不清裝置日誌、不讀其他緩衝 [test:t_android_e2e_crash_log]
- [S3] 當 flow 沒過或第二次才過時,judge 的 UI 結果應帶沒過那幾次的現場路徑(只列真的存在的),終端在那支 flow 後面印出來;第一次就過的不印 [test:t_android_e2e_judge_evidence]
- [S4] 當 flow 第二次才過時,本機總表那一項(按功能跑時連同該情境自己的那份)應多 `"flaky": true`;其他結果的項目不帶這個鍵 [test:t_android_e2e_flaky_mark]
- [S5] 當判定記完總表後,某支這次跑到的 flow 在最近 20 筆有跑到它、判出過或沒過的紀錄裡第二次才過的有 3 筆以上時,終端應印一行點名(flow、次數);同一次執行重判多寫的行只算一次;2 筆以下不印;回傳碼與紀錄內容不因此改變 [test:t_android_e2e_flaky_notice]
- [S6] 當跑 `lumos android-e2e history --flaky` 時,應對最近 `--last` 次執行的紀錄(重判多寫的行不佔名額;帶 `--case` 時看那個情境自己的項目;同一次執行重判的只算一次;沒判到的不算進分母)每支有第二次才過的 flow 印一行(幾次裡幾次、最近一次的證據目錄);沒有就印一句沒有;一般的 `history` 每行列出那一筆第二次才過的 flow [test:t_android_e2e_flaky_history]

## 回退

撤掉範本腳本裡的兩個旗標、讀時間與讀日誌那幾行,judge 不帶現場路徑;總表多出的 `flaky` 鍵留著沒人讀不影響,`history --flaky` 與點名整段拿掉。已經寫出的現場目錄在被忽略的 run 目錄裡,照既有做法由人清。
