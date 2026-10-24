severity: major

以下共 8 條 finding,3 條 major、5 條 minor。逐節讀完全份,沒有 blocker。固定席的 `Systems/macrobenchmark-adapter` 在會談目錄裡沒有這篇,所以我拿 `scripts/lumos` 的現行程式當對照,沒讀到該節點原文。

1. 原生掃描前沒有規定先逼出一次垃圾回收,結果會看時間點(⚠ 我沒有實機證據,只能從設計推論)
severity: major
blocking: 是(照字面實作可能漏報,或兩種設定下結果不同,判準屬 major)
引句:「錄第一份 Java 快照並掃一次沒人指著的原生記憶體、邊錄追蹤檔與日誌邊跑 N 輪、再錄第二份快照並再掃一次」
- 步驟 3 和 5 的順序是「先錄快照、再掃原生」。Java 快照是 `test_data` 宣告為 true 才錄的(S15)。
- 沒宣告時,掃描前沒有任何東西逼出垃圾回收或終結。SDK 的 Java 包裝物件還沒被回收,它持有的原生位址(Java 的 long 欄位)會被保守掃描當成「還有人指著」,就不算沒人指著。
- 這和 WHY 自己否決 Native Heap 與堆積總量的理由是同一類,都是回收時間點。結果就變成「有宣告測試資料才抓得到、沒宣告可能漏」,而且同一份 spec 沒講。
- spec 只有一次實驗室實測(5 塊 10485760 位元組),沒說當時有沒有先錄快照。
- 建議在兩次掃描前明定一個強制回收動作(例如 `am send-trim-memory` 或固定的回收步驟),並寫進 S1 的前提。
- 佐證:`scripts/lumos:39365`(判定端只吃數字,不管回收),`skills/lumos-android-evidence/SKILL.md:121`

2. 收據的重跑腳本「不用改」,但快照 7 天後會被刪,重跑會誤報比對不符
severity: major
blocking: 是(照字面做,快照一過期收據就永遠回 1,判準屬 major)
引句:「快照 7 天後刪,刪了之後收據裡跟快照有關的數字標成不能重跑」
- `android-receipt-rerun.sh` 沒有「檔案不存在就跳過」的分支。trace_processor 開不了檔會回非 0,該條被印成 BAD,整份回 1。
- 1 的意思是「比對不符」,不是「環境不足」。spec 只說要標成不能重跑,沒說怎麼標。
- 該腳本檢查 `expect` 不是 `-` 的條數至少要有一條,所以手改成 `expect=-` 也有可能剛好觸發「什麼都沒驗」的擋下。
- 同一節還要求整份貼上查詢範本,所以快照查詢一定會落入這個情況。
- 建議明寫三者之一:重跑腳本新增檔案缺失的分支、收據改回 `-`,或快照查詢不放進有 expect 的收據。
- 佐證:`scripts/templates/android-receipt-rerun.sh:30-36`、`scripts/templates/android-receipt-rerun.sh:76-79`

3. 現行 `--stability` 判定結果的欄位,和既有輸出與印字函式不相容,spec 只用一句帶過
severity: major
blocking: 是(照原函式實作會當掉或輸出殘缺,判準屬 major)
引句:「輸出沿用 threshold_failures、threshold_passed、threshold_skipped,每筆帶 `check` 與那一種的明細」
- 現行 `_macrobench_print_thresholds` 對每筆直接取 `r['metric']`、`r['stat']`、`r['current']` 和 `max` 或 `min`。check 條目沒有這些欄位,會 KeyError。
- `_macrobench_check_thresholds` 依 `t["metric"]` 和 `t["stat"]` 查表,也不能沿用。
- 「印字照 check 分支」只在「這次要改到的地方」一行,條款 S1 到 S8 沒有任何一條綁「文字輸出不崩」。
- 另外,技能 L0 的往下條件是「`threshold_failures` 不是空的就往 L1」。記憶體類失敗也會落在這個陣列,所以必須讓技能改成看 `check` 欄位。spec 有列「記憶體檢查沒過直接進 L3」,但沒說機械上怎麼區分。
- 佐證:`scripts/lumos:39675-39722`、`skills/lumos-android-evidence/SKILL.md:35`

4. 設定欄位 `driver_warmup` 與 `driver_cycles` 的語意互相矛盾
severity: minor
blocking: 否(實作者要猜,但不會出錯到不能用)
引句:「`driver_warmup`、`driver_cycles`(驅動指令,`{cycles}` 會換成輪數)」
- 欄位清單有兩個驅動指令欄位,各自帶 `{cycles}`。
- 但 WHY(驅動)寫「收集腳本在主機端呼叫驅動兩次……驅動指令裡的 `{cycles}` 換成輪數」,像是同一條指令用兩種輪數,同時範例只給一條指令。
- 建議二選一:一個欄位 `driver` 加 `{cycles}`,或兩個欄位並各給範例。
⚠

5. StrictMode 的計數單位和範圍(VM 規則、執行緒規則)沒有定義
severity: minor
blocking: 否(假紅風險,但屬於可事後校準)
引句:「從日誌串流挑出 StrictMode 行」
- 專案常把 ThreadPolicy 一起開(`detectAll` 之類),會把「主執行緒讀磁碟」也當成違規。
- 一筆違規在 logcat 裡是多行,堆疊每一行的 tag 也是 StrictMode。「有一筆」到底怎麼算沒定。
- 前面 WHY 又限定「VM 規則」。建議規定只認 `StrictMode policy violation` 開頭行,並用違規類別名篩(例如 `LeakedClosableViolation`)。

6. 結束紀錄的原因編號沒列全
severity: minor
blocking: 否(措辭精度,補一句即可)
引句:「其中崩潰(reason 4)、原生崩潰(5)、ANR(6)、低記憶體被殺(3)、記憶體上限(描述含 MemoryLimiter)五種判不過」
- 「記憶體上限」只用描述字串判,沒給原因編號。
- 被訊號殺掉的 SIGNALED(2)、EXCESSIVE_RESOURCE_USAGE(9)等沒歸類。
- 建議明寫「其餘一律只回報」,並列出這幾個編號。

7. `--stability` 的路徑解析基準和 `--update-baseline` 的互動沒講
severity: minor
blocking: 否(實作時一行可定,不會做出錯誤系統)
引句:「`--stability` 吃一份結果檔的路徑,不掃目錄」
- 現行 `macrobench` 只有 `--repo`、`--json`、`--update-baseline` 三個參數。
- 相對路徑是對 `--repo` 還是對當前目錄,以及 `--stability` 與 `--update-baseline` 同時給時怎麼辦,spec 都沒寫。
- 佐證:`scripts/lumos:66197-66200`

8. 官方 vitals 區間表我沒能核對
severity: minor
blocking: 否(出處已在 REVISIT 追蹤)
引句:「一般 App 3200–4800 MB 為 2.00 GB、4800–6800 MB 為 2.25 GB、6800–9216 MB 為 2.25 GB」
- 我試了 `developer.android.com/google/play/vitals/memory` 與子頁,都回 404。
- 相鄰兩段都是 2.25 GB,不尋常,spec 說另一席核對過一致。所以我不判錯,只提醒「兩段同值」再確認一次是不是抄漏。
⚠

各節判讀(除上列外):
- 白話、WHY 1 到 11、七種檢查表、資料怎麼流 1 到 2、5:已讀,無 finding。
- 實務隱患、回退:已讀,無 finding。
- 條款 S1 到 S19:已讀,除第 3 條提到的缺口外無 finding。

固定席 `Systems/macrobenchmark-adapter`:不影響。理由是 `_macrobench_mode` 現行程式「不接裝置」,spec 把接裝置的部分放在新範本;但第 3 條所說的印字函式和輸出欄位要同步改,節點才能維持它宣稱的行為。

總結:最高嚴重度 major,blocking 共 3 條
