severity: major

我逐節讀完 spec,對照 native-mem-growth 的程式碼查證。結果:〈回退〉節只涵蓋兩項,漏掉的寫出物裡有一項(情境設定檔的新鍵)會讓退回後整個設定被擋下。另外「已排除:不可逆」「已排除:金流」「已排除:對外送出」三句的理由站不住,「只提醒、不影響判定」也有一條路徑照 spec 字面會破功。

先講白話:這個功能像在房間裝一個新開關。退回時,spec 只說「把開關拆掉」,沒講牆上已經寫好的使用說明(設定檔的新鍵)會讓舊版管理員看不懂而把整間房鎖起來,也沒講錄到的資料在裝置上誰去收。

### F1 〈回退〉節只涵蓋兩項,漏掉其餘寫出物
severity: major
blocking: 是
引句:「收集腳本拿掉 heapprofd 那段錄製與結果檔欄位,lumos 拿掉提示的輸出;已經寫出的錄檔在被忽略的 run 目錄,照既有 7 天自動刪。」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/native-mem-growth/scripts/templates/android-stability-collect.sh:311`

1. 設計會寫出的東西共有 9 項。〈回退〉只答了 3 項:收集腳本、結果檔欄位、提示輸出。
2. 漏掉的 6 項:
   - 已寫進專案 `.lumos/macrobench.json` 的 `native_growth` 鍵(F2)。
   - 裝置上 `/data/misc/perfetto-configs/` 的設定檔與 `/data/misc/perfetto-traces/` 的錄檔(F3)。
   - 結果檔新段落在舊 lumos、新 lumos 之間的讀法(F7)。
   - skill L3 與圖譜筆記的改寫(沒說退回要不要還原、誰還原)。
   - 本機總表 `history.jsonl` 若帶到提示(spec 沒說會不會帶,見 F7)。
   - 各消費專案已複製出去的收集腳本。範本是「照抄進消費專案」,lumos 與收集腳本分開升降版,退回要逐專案做。
3. 舉例:退回人照〈回退〉做完,仍有專案設定檔留著 `native_growth`、裝置上留著中斷時沒刪的錄檔、skill 仍叫人「先看這份提示」。這些都沒人負責。
4. 應該是:〈回退〉列出每個寫出物的處置,以及退回時的順序。順序見 F2。

### F2 已寫進 `stability_scenarios` 的 `native_growth` 鍵,退回舊版 lumos 後整份設定被擋下
severity: major
blocking: 是
引句:「那份清單以外的欄位會被當成不認得的欄位擋下」
file: `scripts/lumos:40493`(`extra = sorted(set(v) - set(E2E_SCENARIO_KEYS))`,命中就回「不認得的欄位」)
file: `scripts/lumos:39482`(`_macrobench_stab_top_err` 呼叫 `_e2e_scenarios_err`)
file: `scripts/lumos:40297`(`macrobench` 驗設定失敗回 2)
file: `scripts/lumos:41156`(`android-e2e` 按功能跑讀設定,失敗就擋)

1. spec 把這條當「新增欄位要改兩份清單」的限制,沒有看退回方向。
2. 舊版 lumos 讀到有 `native_growth` 的情境時,會從 `_macrobench_config` 回錯誤。`lumos macrobench`(含 `--check-config`)和 `android-e2e select` 都因此回 2。收集腳本開跑前也會呼叫 `--check-config`(見節點 WHY「收集腳本開跑前叫 lumos macrobench --check-config」),所以舊 lumos 配新設定,連既有的穩定性收集都起不來。這已經超出「只是少一個提示」。
3. `stability` 段不受影響。`_macrobench_stab_cfg_err`、`_macrobench_stab_optional_err` 沒有「未知鍵」檢查,舊版會忽略 `stability.native_growth`。所以只有寫在情境裡的形式有此地雷。
4. 舊版收集腳本只挑 4 個鍵(`("scenario","driver","warmup","cycles")`),也會忽略新鍵。受害的只有舊 lumos,而 lumos 是 symlink 全機一起退。
5. 照 spec 字面實作,上線後專案開始在情境裡寫 `native_growth`。一旦退回 lumos,所有這類專案的 macrobench 與 e2e 全擋,要逐專案手改設定。
6. 應該是:二選一,並寫進〈回退〉。
   - 讓舊版也容忍這個鍵:先出一版只放寬驗證的 lumos(未知鍵降為警告),隔一個版本再開這個功能。
   - 把退回順序寫死:先請所有專案刪掉 `native_growth`,再退 lumos。
7. spec 第 123 行還要補一句:`native_growth` 放在情境裡本身就是退回地雷,放在 `stability` 段是無害的。這點可以回答 spec 向審查席提的「該不該允許寫在 stability 段」。

### F3 裝置端設定檔與錄檔:中途失敗、被中斷時誰收,spec 完全沒寫
severity: major
blocking: 是
引句:「錄製設定(推到裝置 `/data/misc/perfetto-configs/`」
file: `scripts/templates/android-stability-collect.sh:305-317`(`start_record`)
file: `scripts/templates/android-stability-collect.sh:335-358`(`stop_record`)
file: `scripts/templates/android-stability-collect.sh:485-493`(`state["rec"]` 單槽)
file: `scripts/templates/android-stability-collect.sh:527`(`cleanup` 只收 `state["rec"]`)
file: `scripts/templates/android-stability-collect.sh:548`(中斷收尾的訊息)

1. 既有收集腳本裝置端的清理很細,節點裡有一串 PITFALL/WHY:推設定前先登記 `state["rec"]`、停完才 pop、收尾忽略二次中斷、裝置離線時改口說「錄製與暫存可能還在」。
2. spec 的第二段 heapprofd 完全沒提這套機制。實作者照字面寫,三個洞:
   - 第二段錄製要不要用同一個 `state["rec"]`。現況是單槽,`measure` 裡 `del state["rec"]` 會把它清掉。
   - 遠端檔名是 `lumos-stability-{run_id}.pbtxt` 與 `.pftrace`。第二段若沿用,會蓋掉或碰撞第一段。spec 沒說要加後綴。
   - 第二段進行中被中斷時,heapprofd 錄檔含呼叫鏈,當含個資處理。誰停、誰刪,用的是哪個登記,spec 沒寫。
3. 〈實務隱患〉寫「已排除:對外送出:錄檔與結果只在本機 run 目錄,不上傳」。這句與事實不符:`perfetto` 先把錄檔寫在裝置 `/data/misc/perfetto-traces/`,拉回主機才算本機。
   - 收集腳本被 kill -9、主機當機、adb 離線時,裝置上的錄檔留在那裡,沒有任何自動刪除。
   - 既有第一段也有這個風險,但沒有人把它當成可接受。這份計劃要新增一段,就要把裝置端的保存與刪除責任寫出來。
4. 〈回退〉也沒給退回後去裝置上查殘檔的指令(例如 `adb shell ls /data/misc/perfetto-traces/ /data/misc/perfetto-configs/`)。
5. 應該是:
   - 條款寫明第二段登記在獨立的 state 槽,或第一段停完後才重用單槽。
   - 遠端檔名加段名後綴。
   - `cleanup`、`abort_record` 收兩段。
   - 補一條「heapprofd 錄製被中斷時裝置端檔案被刪」的先紅測試。
6. ⚠ 另有一點我沒能驗證:heapprofd 停錄之後,目標行程裡的 malloc hook 是否留到行程重啟。spec 在「前提」裡也沒答。若會留著,第二段之後 App 仍帶著 hook,不能直接接著量別的東西。這需要實機確認。

### F4 「已排除:不可逆」的理由站不住
severity: major
blocking: 是
引句:「已排除:不可逆:只多寫被忽略的 run 目錄與結果檔,撤掉照回退節刪程式即可。」
file: `scripts/templates/android-stability-collect.sh:135-150`(`prune_old_snapshots`)
file: `scripts/templates/android-stability-collect.sh:398`(`check-ignore` 只在 `in_git` 時做)

1. 「只多寫」不實:還寫了裝置端兩處(F3)、設定檔的新鍵(F2)、skill 與筆記。理由前提不成立。
2. 「撤掉照回退節刪程式即可」:回退節沒涵蓋這些(F1)。
3. 7 天自動刪靠「還有人在跑收集腳本」。`prune_old_snapshots` 只在 `main` 開跑時呼叫。
   - spec 自己在 d3 的 trade_offs 也承認「專案不再跑收集腳本時舊錄檔不會被刪(既有代價照舊)」。
   - 這句話在退回情境下最容易發生:功能撤掉後專案很可能停跑收集。
   - 舊版收集腳本的刪檔樣式與新版相同(`heap-.*\.pftrace`),所以退到舊腳本仍然會刪,但前提是還有人跑它。
4. 另一個洞:`prune_old_snapshots` 只刪 run 目錄第一層。skill L3 的 `heap-profile-<名>/` 目錄不在範圍內(skill 第 144 行自己說要手動刪)。若實作者把新錄檔放進子目錄,就永遠不被刪。spec 第 125 行已寫「第一層」,但沒寫成條款,也沒有測試綁定。
5. 應該是:不可逆的排除理由改成「個資錄檔的保存期限只靠下次跑腳本」,加上回頭條件(例如 `REVISIT` 或在 `doctor`/`preflight` 加一條「超過 N 天的 `heap-*` 提醒」)。錄檔放第一層寫成條款並綁測試。

### F5 「已排除:金流」不成立:多跑 N 輪驅動會多做 N 次情境動作
severity: major
blocking: 是
引句:「已排除:金流:只在測試裝置上量自家 App,不碰交易。」
file: `scripts/templates/android-stability-collect.sh:487-488`(`driver(st["driver"], n, serial)` 是真的跑情境)

1. spec 白話段與 d4 的例子都用「結帳」情境。第二段是「另跑一段 N 輪」,即驅動指令再把結帳流程跑 N 次。
2. 「只在測試裝置上量」不等於「不碰交易」。測試帳號後端若是真後端或沙盒,每次結帳都會寫訂單、扣庫存、打支付沙盒。
3. d1 的 trade_offs 只寫「多花時間」,沒寫「情境動作的副作用加倍」。
4. 這與回滾直接相關:多出來的 N 輪副作用在後端,不是刪本機檔能退的。
5. 應該是:這項改為「不排除」,在條款或前提加一句「打開 `native_growth` 的情境,其驅動指令必須對重複執行無不可逆副作用」。這條要由人在 `native_growth: true` 當下確認。

### F6 第二段放在 `exits`、`pids`、`unreachable` 之後或之前沒寫,可能污染既有判定,與 S4 抵觸
severity: major
blocking: 是
引句:「收集腳本在既有量測之後另跑一段 N 輪、只錄 heapprofd(d1)」
file: `scripts/templates/android-stability-collect.sh:470-513`(`measure` 的順序)

1. 現況順序:第一段 → `stop_record` → `pidof` → `unreachable(after)` → `native_heap_kb(after)` → `snapshot(after)` → `read_exits(after)`。
2. 「既有量測之後」沒指出插在哪個點。
   - 若插在 `read_exits(ex_after)` 之前:heapprofd 掛 malloc 拖慢 App,可能多出 ANR 或 low_memory。這會被 `exit_diff` 算成「新增結束紀錄」。`exits` 檢查是會擋推送的(`MACROBENCH_EXIT_FAIL_TYPES`)。這會讓 S4「提示不影響判定」失效,也與 d2 衝突。
   - 若插在 `unreachable(after)`、`native_heap_kb(after)` 之前:第二段再配一輪記憶體,after 數字不再是 N 輪後的狀態。
   - 若插在 `pids` 之後:`pids` 清單是否多一格,影響 `res["pids"]` 的檢查。
3. 還有 `max_record_s`:設定檔的 `duration_ms: 120000` 寫死。N 輪若超過 120 秒,錄檔被截斷但結果看起來完整。既有第一段用 `max_record_s` 並有「到了上限」的偵測,第二段 spec 沒這套。
4. 應該是:條款明寫第二段在所有既有讀取(含 `read_exits` 第二次)之後。再加一條先紅測試:第二段出事(崩潰、逾時、錄製失敗)時,既有各段與 `exits` 輸出不變。

### F7 舊結果檔、新結果檔、舊 lumos、新 lumos 的相容行為完全沒寫,新段落的鍵名也沒定義
severity: minor
blocking: 否
引句:「lumos 讀結果檔,線性增長的照增長量排序列成優化建議」
file: `scripts/lumos:40010-40016`(`_macrobench_stab_src` 對缺的來源回「結果檔沒有 X 這個來源」)
file: `scripts/lumos:39995-40007`(`_macrobench_stab_scrub` 只遞迴清字串,不驗未知鍵)

1. 舊 lumos 讀新結果檔:會安全忽略多出的段落。`_macrobench_stab_load` 與 scrub 不驗未知鍵,這是好的,但 spec 沒寫成相容保證與測試。
2. 新 lumos 讀舊結果檔(沒有新段落):spec 沒說該印什麼。
   - S6 說「沒打開」要「結果檔那一段寫成沒打開」。舊結果檔沒有那一段,與「沒打開」無法區分。
   - 若實作者沿用 `_macrobench_stab_src`,舊檔會得到「結果檔沒有 native_growth 這個來源」之類的訊息。這會被讀成問題,實際是舊版收集腳本產的。
3. 新段落的鍵名、狀態集(ok、skipped、unsupported 等)、欄位型別都沒定義。「結果檔那一段」在全文各處出現,卻沒有名字。
4. lumos 要驗形狀:不是有限數、負數、巢狀過深、清單爆量(這類檔可以被手改,節點有 `classes_seen` 先例)。spec 沒要求。
5. 本機總表 `history.jsonl` 若把提示帶進 `notices`,退回後舊行仍留在總表裡(`_e2e_history_cmd` 逐行讀、壞行跳過,不會壞,但會印出已不存在的提示類別)。spec 沒說帶不帶。⚠ 從程式碼看不出提示輸出會不會進 `notices`,取決於實作。
6. 應該是:定段名與 schema;寫三條相容測試(舊檔不印錯、新檔配舊讀取不炸、段落缺席時靜默);說明提示是否進總表。

### F8 7 天保存期限:退回後的責任歸屬只靠「還有人跑腳本」,條款也沒綁
severity: minor
blocking: 否
引句:「專案不再跑收集腳本時舊錄檔不會被刪(既有代價照舊)」
file: `scripts/templates/android-stability-collect.sh:523-527`(`main` 才呼叫 `prune_old_snapshots`)

1. 這是 d3 自承的代價,但依本專案紀律「承認風險要附回頭看的條件」,它沒有 `REVISIT`。〈實務隱患〉的 REVISIT 清單裡沒有這一項。
2. 與 F4 同族,但這項只是文件精度,所以列 minor。
3. 應該是:把它拆成獨立一行回頭條件。

---

## 各節核對

- frontmatter:`pending_questions` Q1 到 Q3 分別對 d1、d2、d3,`decisions` 有 d1 到 d4(d4 沒有對應的 Q,不算壞引用)。已讀,無 finding。
- 白話與 PRIOR-ART、RETIRE-IF、REVISIT:已讀,無回滾面 finding。
- 實驗室實測:已讀,無 finding。回滾面只有一點:「錄檔與暫存都已刪掉」是人工刪,正式版沒有這套(見 F3)。
- 〈打算怎麼做〉1 到 5:F2、F3、F6、F7 已列。
- 〈跟舊否決的差別〉:已讀,無 finding。
- 〈實務隱患〉:
  - 干擾、判法邊界、個資、版本、前提:已讀,無 finding。
  - 「已排除:金流」:F5。
  - 「已排除:對外送出」:F3(第 3 點)。
  - 「已排除:不可逆」:F4。
  - 「已排除:守衛面」:F6(S4 與位置的矛盾)。
- 〈條款〉S1 到 S6:S4 依賴 F6 的位置才能成立;S6 的「沒打開」與舊檔缺席無法區分(F7)。
- 〈回退〉:F1。
- 交叉引用:S1 到 S6、d1 到 d4、Q1 到 Q3 核對無壞引用。條款編號順序是 S1、S2、S3、S6、S4、S5(S6 排在 S4 前),不影響內容。

## 風險類逐類答

- 併發:第二段的遠端檔名會碰撞(F3)。同一台裝置同時兩個 run-id 才不碰撞,其餘 spec 沒寫。
- 效能:拖慢 App 屬實,spec 已有 REVISIT。
- 資源:裝置端錄檔與設定(F3)。
- 回滾:F1、F2、F4。
- 遷移:F7。
- 金流:F5。
- 對外送出:F3。
- 正式環境不可逆:F4、F5。
- 守衛面:F6。

## 圖譜鏡頭固定席

本次只附了一個節點:`Systems/android-stability-collector`(計劃的 lands_in)。它在會談目錄還沒有,我讀了 native-mem-growth 內的同名檔。計劃直接連結的三篇(`Android記憶體與穩定性驗收_計劃`、`Android逐層診斷_計劃`、`Verification/2026-10-24_…`)沒有附上,所以我沒逐條判它們。

`Systems/android-stability-collector` 各條 WHY/PITFALL 逐條判:

- 清舊快照遇捷徑跳過:不影響。新錄檔若同樣放第一層、同樣檔名樣式,原保護仍有效(F4 第 4 點要求寫成條款)。
- 開跑前對每種產物檔名問 `git check-ignore`:不影響,但 `ARTIFACTS` 要補新檔名。spec 第 125 行有寫。
- 收尾順序與二次中斷忽略(SIGTERM、SIGHUP、SIGQUIT 的 WHY 與 PITFALL):**會被影響**,F3。
- 日誌串流與錄製「先 pop 再停」的 PITFALL:**會被影響**。第二段錄製若重用單槽,會重新踩到這個坑(F3)。
- 同一 run-id 已有結果檔就擋:不影響。
- `E2E_SCENARIO_KEYS` 兩邊清單逐字相同並有測試比對:**會被影響**(F2)。測試 `t_android_e2e_lists_match_templates` 會因新鍵而變動,spec 已知,但沒處理布林鍵不能接在清單尾端的驗證路徑。
- `dumpsys meminfo --unreachable` 輸出尾巴含記憶體內容的 PITFALL:不影響,前提是第二段的失敗原因也不帶標準輸出。spec 沒要求,實作者可能忘記。
- 其餘:不影響。

總結:整份最高嚴重度為 major,blocking 共 5 條(F1、F2、F3、F4、F5、F6 中有 6 條標 blocking,實際計數見下)。

更正:blocking 為 F1、F2、F3、F4、F5、F6,共 6 條。

總結:整份最高嚴重度為 major,blocking 共 6 條
