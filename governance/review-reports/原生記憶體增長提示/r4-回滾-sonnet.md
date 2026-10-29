severity: major

我逐節讀完 r4-snapshot.md,並對照 `native-mem-growth` repo 的程式碼查證。〈回退〉的主線成立:舊版 lumos 確實不驗 stability 段的未知鍵,`lumos update` 也確實只補不刪。有一條〈實務隱患〉的已排除理由站不住,另有五條回退細節要補。

### F1 〈已排除:守衛面〉說不改推送前檢查,但 e2e 整段收集有 3600 秒上限,打開第二段會讓它逾時
severity: major
blocking: 是
引句:「只提醒,不改任何判定、回傳碼或推送前檢查」
file: `scripts/templates/android-e2e-run.sh:58`、`scripts/templates/android-e2e-run.sh:411`、`scripts/templates/android-e2e-run.sh:477-480`
1. 問題:e2e 把收集腳本整支當一個 step,上限是 `T_LONG`(預設 3600 秒)。第二段多跑暖機加量測,再加停錄與查詢,全算在同一個 step 裡。
2. 具體例:某情境第一段本來要 50 分鐘,打開 `native_retained` 後約 100 分鐘。
   - 照 spec 字面:〈時間〉只叫人「打開前先估一次」,〈守衛面〉卻寫不改任何推送前檢查。
   - 實際:`st.step("stability", …)` 逾時回 None,e2e 設 `device_stuck`,印「剩下的情境與效能這次都不跑」,後面的情境判成沒判完。推送前的 e2e 紀錄因此不是 pass,推送被擋。
   - 應該是:承認打開這項會改變 e2e 的耗時與判定風險。〈回退〉要寫「逾時時的止血做法」。S4 要加「整個 step 逾時」這一種,現在只列 App 結束、驅動失敗、意外例外、被中斷。
3. 同一條還有一處:`main()` 被中斷時印「沒寫結果檔」並 `sys.exit(2)`,見 `scripts/templates/android-stability-collect.sh:531` 起。依 S17,第一段結果檔已先寫好,這句訊息會變成假話。run-id 也因 `preflight` 的「已經有結果檔」檢查而不能重用,spec 沒提。
4. 佐證:spec 自己〈時間〉那條寫了單步上限是 3600 秒,與〈守衛面〉互相矛盾。

### F2 〈回退〉只說「預設留著設定鍵」,沒有不改指紋的關閉辦法,回退後 opt-in 仍處於啟用狀態
severity: minor
blocking: 否
引句:「刪掉會讓 e2e 的記憶體設定指紋再變一次、每條分支推送前要整套重跑」
file: `scripts/lumos:40746-40748`(`memory-config` 雜湊整份 stability 段與 stability_scenarios)、`scripts/lumos:41567`
1. 問題:舊版 lumos 確實不驗 stability 段未知鍵(`_macrobench_stab_cfg_err`、`_macrobench_stab_optional_err`,`scripts/lumos:39542-39570`),所以「保留鍵」可行。
2. 但是:
   - 回退若是因為〈金流〉的副作用,鍵還留著,等於授權還在。日後任何人重新套回程式碼,就立刻恢復多下 W+N 次單,沒有重新確認。
   - 要馬上停掉而不退程式,唯一辦法是把鍵改成 `[]`。這同樣改指紋,spec 沒寫這條路的代價。
3. 應補:保留鍵只在「因別的原因回退」時成立。因金流副作用回退時,要連鍵一起刪,並接受整套重跑。
4. 已確認:鍵留著時指紋不變,舊版 lumos 不會因它報錯。

### F3 消費專案殘檔不只是「留著」:回退後 `.sql` 會被當成專案自己的程式碼
severity: minor
blocking: 否
引句:「`lumos update` 只補不刪,退回後專案裡的 `scripts/templates/android-stability-heapprofd.pbtxt`(新增)與 `android-stability-native.sql` 會留著」
file: `scripts/lumos:32019-32045`(`_vendored_state`)、`scripts/lumos:31994-32008`(`_vendored_manifest_write` 只寫 `_VENDORED_ALL` 上的檔)、`scripts/lumos:5967`(`.sql` 在 `CODE_EXTS_T`)、`scripts/lumos:32858`
1. 已確認:`_vendor_toolchain` 的複製迴圈沒有刪除路徑,「只補不刪」屬實。
2. 漏的後果:
   - 退回後第一次 `lumos update` 重寫 `.lumos/vendored.json`,這兩支檔不再在清單上,也不在指紋表裡。
   - 手動刪之前,`.sql` 會被技術棧計數、推送前風險分級當成專案自己的程式。
   - 手動刪那一次提交,在推送前分級也是「改了專案程式」,會多出風險。
3. 沒影響的部分:`scripts/hooks/pre-commit` 把 `scripts/templates/*` 整夾豁免,所以提交前的圖譜閘不會擋這次刪除。
4. 應補:註明這段期間會被當成專案程式,以及刪除提交的風險分級。

### F4 殘檔與裝置殘留的刪除指令沒給;一般寫法會違反字面絕對路徑規則
severity: minor
blocking: 否
引句:「要手動清就刪各 run 目錄第一層這兩個檔名」
file: `scripts/templates/android-stability-collect.sh:134-149`(`prune_old_snapshots` 只認 `heap-.*\.pftrace`,不刪 `record*.pbtxt`)
1. 問題:
   - 消費專案那條有「寫字面路徑」。run 目錄那條和裝置那條(〈回退〉「裝置上」)只給 `ls`,沒給刪除指令。
   - run-id 不固定,照字面只能用萬用字元或 find,而使用者的規則禁止這種寫法。
2. 具體例:裝置上的 `lumos-native-<run-id>.pbtxt` 與 `.pftrace`、各 run 目錄的 `record-native.pbtxt`,現在無法照 spec 刪乾淨。
3. 應補:先列出清單,再對每個實際存在的檔寫字面 `rm`。
4. 已確認:`heap-native.pftrace` 符合舊版 prune 的樣式,舊收集腳本仍會在 7 天後刪它。這點成立。但不再跑收集腳本的專案,錄檔會一直留著,spec 已承認。

### F5 〈回退〉沒列共用解析函式的改動,也沒回答「退回後第一段受不受影響」
severity: minor
blocking: 否
引句:「抽成一支共用函式,裡面用 csv.reader」
file: `scripts/templates/android-stability-collect.sh:251-303`(`heap_counts` 與 `cycle_numbers` 現用 `split(",")`)、`scripts/test_lumos.py:22147-22170`(`_ms_collect` 用假 TP)
1. 問題:這是整份設計裡唯一改到第一段既有程式碼的地方。〈回退〉逐項清單沒列它,只靠「同一支檔同一次還原」帶過。
2. 風險:有人只拿掉第二段、留下共用函式,或只還原函式不還原呼叫端,第一段會是什麼狀態,spec 沒寫。
3. 「行為不變,用既有測試守」的說法 ⚠ 沒驗到:我沒讀到假 TP 的 heap 輸入是否含逗號或引號類別名。這正是 `csv.reader` 與 `split` 會分歧的情況。
4. 應補:把它列進〈回退〉,並寫明它可獨立保留或還原。

### F6 〈已排除:對外送出〉說「都不離開測試裝置與本機」,但排行會印給 AI 並寫進進版控的收據
severity: minor
blocking: 否
引句:「都不離開測試裝置與本機」
file: `skills/lumos-android-evidence/reference.md:3`(收據目錄 `.lumos/receipts/<run-id>/` 進版控)、`docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:40`(已有先例:輸出尾巴印給 AI 被代碼審判成洩漏)
1. 問題:spec 第 7 步讓「從排行來的呼叫位置」進收據並標 [INFERRED]。第 6 步又讓 lumos 把函式名、.so 檔名、呼叫者印出來,這些會進 AI 的視野。
2. 具體例:SDK 的 JNI 函式名與大小會出現在進版控的 `report.md`,所以「不離開本機」不成立。
3. 敏感度:欄位是符號名與位元組數,不含記憶體內容,不算高。
4. 應改成:「錄檔本體不離開;彙總後的函式名與大小會進 AI 視野與收據」。

### F7 新舊版本組合:舊收集腳本配新 lumos 且情境已打開時,文字輸出完全沉默,skill 的處置也沒寫
severity: minor
blocking: 否
引句:「結果檔沒有這段(舊收集腳本)→ status 寫 unsupported「結果檔沒有 native_retained 段」、不印」
file: `scripts/lumos:40010-40016`(`_macrobench_stab_src`)
1. 問題:收集腳本在專案裡(vendored),skill 呼叫的 `lumos` 可能是全域那支,兩者版本可能錯開。
2. 具體例:使用者已打開 `native_retained`,收集腳本是舊的,新 lumos 什麼也不印(S9),使用者以為排行是空的。
3. 漏的合約:skill 遇到「鍵存在但 status 為 unsupported,且原因是結果檔沒有該段」時該怎麼做,S19 只寫了「鍵不存在」。
4. 應補:鍵存在但為 unsupported 時,也照舊手動錄 L3,不當成零筆。
5. 補充:spec 只列了三種組合。「skill 舊、lumos 新」無害,應明寫。

### 各節與〈實務隱患〉逐項
- frontmatter、白話、PRIOR-ART、RETIRE-IF、實驗室實測、〈排行怎麼算〉:已讀,無 finding。
- 〈打算怎麼做〉第 1 步:已讀,無 finding。設定鍵不寫進 `stability_scenarios`,避開 `scripts/lumos:40474-40495` 的未知欄位拒收,這點正確。
- 〈打算怎麼做〉第 2 至 7 步:除 F1、F5、F7 外,已讀,無 finding。
- 〈條款〉:已讀,F1 提到 S4 缺逾時;F7 提到 S9、S19 缺鍵存在但 unsupported 的情形。
- 〈回退〉其餘項目:已讀。收集腳本還原、skill 與筆記照 git 還原,無問題。
- 〈實務隱患〉:
  - 已排除:對外送出:站不住,見 F6。
  - 已排除:守衛面:站不住,見 F1。
  - 金流(不排除):理由站得住。W+N 次翻倍屬實,前提是 `stability.test_data` 的人裁。唯一缺口是關閉辦法,見 F2。
  - 不可逆(不排除):站得住。它與〈回退〉互相一致。
  - 其餘:量測干擾、時間、中斷、多行程、個資、版本、前提這幾條沒有回滾面的問題。
- 風險類(併發、效能、資源、回滾、遷移):
  - 併發:無新增。同一時間只跑一個 perfetto,`state["rec"]` 同一槽。
  - 資源:裝置暫存與本機錄檔的殘留見 F4。
  - 效能與回滾:見 F1、F2。
  - 遷移:指紋變動在〈遷移〉已寫,補充見 F2。

### 固定席逐篇判
- `Systems/android-stability-collector`:不破壞宣稱的行為。第一段結果欄位 `pids`、`exits`、`unreachable`、`native_heap_kb` 不動,新段另存。要留意 F5(共用解析)與 F1(中斷訊息「沒寫結果檔」會變成假話)。
- `Systems/macrobenchmark-adapter`:不影響。新鍵放在 stability 段,不經過門檻檔;新增兩支範本必須登記 `_VENDORED_TREE_FILES`,spec 已寫。
- `Systems/android-e2e-acceptance`:有影響,見 F1。指紋合約(`memory-config` 雜湊整份 stability 段)spec 描述正確。3600 秒 step 上限會被拉長的收集撞到。
- `Projects/Android記憶體與穩定性驗收_計劃`:不破壞。spec 已列要把「只剩 Native Heap 前後數字」那句改掉,並補「用同一條驅動指令呼叫兩次」。
- `Projects/Android逐層診斷_計劃`:不破壞。d4 的預設關、按情境開,維持了「每次都錄」被否決的理由。

總結:整份最高嚴重度為 major,blocking 共 1 條
