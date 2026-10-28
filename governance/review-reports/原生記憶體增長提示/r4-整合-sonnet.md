severity: major

我逐節讀完 r4-snapshot.md,並對照收集腳本、`scripts/lumos`、`scripts/test_lumos.py`、skill 與固定席節點查證。章節包含前言與 pending_questions/decisions、白話段、PRIOR-ART/RETIRE-IF/REVISIT、實驗室實測、排行怎麼算、打算怎麼做 1-7、跟舊否決的差別、實務隱患、條款、回退、審計修正紀錄。

已讀無 finding 的部分:
- 前言與 pending_questions/decisions:Q1-Q3 對應 d1-d3,沒有斷掉的對應。
- 跟舊否決的差別:三條否決在目標計劃裡都找得到,依據是 `Android記憶體與穩定性驗收_計劃.md:25` 的「不選:…只看 Native Heap 趨勢」與 `:26` 的「每輪結束值判趨勢」。
- 回退:新舊版本錯配的描述與程式現況相符。舊 lumos 的 `_macrobench_stab_optional_err` 確實不驗未知鍵,`scripts/lumos:39557`。
- 審計修正紀錄:無 finding。

已確認屬實、不用改的宣稱:
- `_macrobench_stab_top_err(raw)` 能拿到 `stability_scenarios`,`scripts/lumos:39475`。
- `_events_clean(text, limit)` 與 `_secev_int` 都存在。
- `heap-*.pftrace` 的 7 天刪除樣式會涵蓋 `heap-native.pftrace`,`android-stability-collect.sh:148`。
- 情境名規則只收英數字、底線與連字號,所以 `@default` 不會撞名,`scripts/lumos:40488`。
- 驗收計劃裡「只剩 Native Heap 前後數字當線索」和「用同一條驅動指令呼叫兩次」兩句原文都在。
- e2e 指紋會把 `stability` 整段納入,所以加 `native_retained` 一定改指紋,`scripts/lumos:40747`。

### F1 lumos 沒有「這個情境有沒有打開」的依據,「打開了但 status 不是 ok」分不出來
severity: major
blocking: 是
引句:「打開了但 status 不是 ok → 印一行「原生配置排行沒跑成:<原因>」」
file: `scripts/templates/android-stability-collect.sh:~372`(`device_info`)、`scripts/lumos:40010`(`_macrobench_stab_src`)

1. 問題:第 5 步規定結果檔段落只有 `status`、`reason`、`main_process_only`、`sites`。第 2 步又規定「沒打開」也寫 `unsupported`(原因是「設定沒替這個情境打開 native_retained」)。
2. lumos 讀 stability.json 時,沒有任何欄位能區分「沒打開」和「打開了但沒宣告測試資料、或 Android 版本低於 30」。這三種都是 `unsupported`。
3. `device_info` 寫進結果檔的 `scenario` 是 `st["scenario"]`,也就是驅動函式名,不是情境名。所以 lumos 也沒辦法拿情境名去比對 `native_retained`。
4. 具體例:
   - 專案沒打開這項提示(預設),照字面實作可能讓每個專案每次都印一行「沒跑成」,違反 S9「不印」。
   - 反過來,只在 `unsupported` 時不印,最常見的設定錯誤就無聲:打開了卻忘了宣告 `test_data`,使用者看不到任何提示。這與 S15 要的行為相反。
5. 該補的:結果檔段落加一個明確欄位(例如 `opened: true/false`),並在 S9、S15 條款裡寫明靠它判斷。

### F2 一支範本「每次 TP 只跑一條回傳列的語句」,但第 4 步要三種輸出
severity: major
blocking: 是
引句:「每次 TP 呼叫只跑一條回傳列的語句」
file: `scripts/test_lumos.py:18456`(`t_android_memstab_templates_receipt_safe`)、`scripts/templates/android-stability-collect.sh:251,289`

1. 問題:第 4 步要同一個 `android-stability-native.sql` 範本支撐三件事。
   - 呼叫位置排行。
   - `stats` 表裡 error 或 data_loss 且值非 0 的項目。
   - 「`heap_profile_allocation` 沒有任何一列」。
2. 既有慣例是一支範本只放一條語句,而且整支只有最後一行以分號結尾。`t_android_memstab_templates_receipt_safe` 對既有範本逐支這樣驗,共用函式簽名也只收一支範本。
3. 第三件事不能從排行的結果推出來。排行已經篩掉不到 1 MiB 的項目,所以「正常版」(S5 要求「不列」)排行是空的,和「沒錄到」長得一樣。照字面用排行是否為空判斷,正常版會被誤判成 `failed「沒錄到原生配置記帳」`。
4. spec 沒有說三件事怎麼塞進單一語句。可行做法是用 UNION ALL 加一個類型欄,或拆成多支範本。兩種做法都會動到共用函式的簽名和 receipt_safe 測試的清單,所以 spec 要先選定。

### F3 測試工具(假 TP、假 adb、`_ms_sql`、登記清單)沒有列進要改的檔
severity: minor
blocking: 否
引句:「測試照既有 .sql 範本的做法,用 Python 內建 sqlite 對假表跑」
file: `scripts/test_lumos.py:22115`(`_MS_FAKE_TP`)、`:18387`(`_ms_sql`)、`:22364`(`t_android_memstab_vendored`)、`:18456`

1. `_MS_FAKE_TP` 靠查詢內容分流:含 `heap_graph_object` 走快照分支,其餘一律回 cycle 的列。新的 native 查詢會被當成 cycle 查詢,第二段的所有測試(S4、S7、S8、S17)都會拿到錯的輸出。
2. `_ms_sql` 的假表是寫死的,沒有 `heap_profile_allocation`、`stack_profile_*`、`stats`。
3. `t_android_memstab_vendored` 和 `receipt_safe` 各有一份寫死的檔名清單,新範本不會自動納入。
4. 假 adb 也要能處理 `lumos-native-*` 的錄製。
5. 共用解析改成 csv.reader 這一步沒有問題:既有假 TP 的輸出(`"class","instances"` 加 `"k","v"` 列、`"cycle",200000,…`)用 csv.reader 解析結果與現況一致。
6. 預設關,所以既有測試不會因這項而紅。但 spec 的「測試清單」只提到 `_VENDORED_TREE_FILES`,漏了上述幾處。

### F4 第二段的流程重排會牽動 main、preflight、cleanup 的簽名,spec 沒列,現有訊息也會變錯
severity: minor
blocking: 否
引句:「先把第一段的結果寫成結果檔(這時 `native_retained` 段寫 failed「第二段沒跑完」)」
file: `android-stability-collect.sh:112`(`load_config` 只回 `st`)、`:380`(`preflight(st)`)、`:516`(`cleanup`)、`:531`(`main`)

1. `load_config` 要多回情境名、`preflight` 要知道這次是否打開才能決定要不要加檢查檔名、`cleanup` 要拿到 `pkg` 才能停 App。這三個簽名都要改,spec 只提了 `load_config`。
2. 結果檔現在是 `measure` 回傳後才由 `main` 寫。改成「先寫、再跑第二段、再原子替換」,等於 `main` 的流程要重排。
3. `main` 的中斷訊息目前寫「收集被中斷,沒寫結果檔」。第二段被中斷時結果檔已經存在,這句會變成假話。spec 的實務隱患「中斷」那條只提結果檔已先寫好,沒提訊息要改。
4. 「沒打開」或「unsupported」時要不要先寫一次 `failed「第二段沒跑完」`,spec 沒說。這種情況本來就不跑第二段,不該出現這個暫時值。
5. `t_android_e2e_lists_match_templates` 會用 regex 抓 `load_config` 裡那行 `scen[k] for k in (…)`,改 `load_config` 時那行不能動(`scripts/test_lumos.py:19502`)。

### F5 沒給 `--stability` 時 `native_retained` 鍵的值沒定
severity: minor
blocking: 否
引句:「一開始就放進結果的初始字典(跟 stability_unjudged 同處)」
file: `scripts/lumos:40310`

1. 初始字典在沒有 `--stability` 時,`native_retained` 的值 spec 沒寫(None、unsupported 物件,或空物件)。
2. skill 規則是「鍵不存在 = lumos 太舊」,鍵一律存在。如果值是 None,skill 讀 `.status` 會出錯。
3. spec 要寫明沒給 `--stability` 時的固定值。

### F6 Systems 筆記的更新範圍沒涵蓋 lands_in 與受影響的 WHY
severity: minor
blocking: 否
引句:「並加進 Systems/android-stability-collector 的 about_code、改它的負責範圍」
file: `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md:18`

1. `lands_in` 列了 `Systems/macrobenchmark-adapter`,但第 7 步沒有任何對它的修改。該節點的負責範圍寫「判記憶體與穩定性」,新增一個不判定、只印的排行會超出這句。
2. collector 筆記 `:18` 的 WHY「收集腳本在主機端排全部順序(…再讀結束紀錄)」多了第二段後就不完整。它綁測試 `t_android_memstab_collect_driver_status`。
3. `Systems/android-e2e-acceptance` 的指紋 WHY 沒被提到。spec 在「遷移」那條講了指紋會變,卻沒列這一篇。
4. 該補的:第 7 步明列要動的三篇 Systems,以及 collector 的 WHY 順序行。

### F7 縮範圍後留下的殘句
severity: minor
blocking: 否
引句:「判法(前後兩半增量)只在實驗室一台裝置驗過,快取上限大於量測輪數時會誤判」
file: r4-snapshot.md d2 的 context

1. d2 的 context 描述的是已拆到另一份計劃的判法,這份計劃已經不做判法。
2. 實驗室表格的「heapprofd 判法」欄和「當時的草稿判法」段落還在,但第 100 行已經聲明這份只用結尾累計。讀者容易誤以為兩者都要實作。
3. 建議把 d2 的 context 改成排行本身的風險(快取與池會上榜、取樣估計會抖),表格欄名標明只供參考。

### 固定席逐篇判
- `Systems/android-stability-collector`:會受影響,但不破壞既有合約。第二段排在既有讀取之後,預設關,既有 WHY 與 PITFALL 綁的測試不受影響。要改的有 about_code(加兩支範本)、責任範圍,以及 `:18` 的順序 WHY(見 F6)。
- `Systems/macrobenchmark-adapter`:不破壞「只報、不擋推送」。新增輸出只提醒,不進 `threshold_failures`,與節點宣稱一致。責任範圍的「判」字需要補一句(F6)。
- `Systems/android-e2e-acceptance`:不影響判定。`_e2e_judge_stability` 只讀 `threshold_*` 與 `stability_unjudged`,多一個 JSON 鍵不影響。影響的是 e2e 記憶體設定指紋,spec 的「遷移」已寫到。單步 3600 秒上限也已提到。
- `Projects/Android記憶體與穩定性驗收_計劃`:不破壞。兩句要改的原文都存在,新增的提示不進判定,沒碰 `native_unreachable` 的合約。
- `Projects/Android逐層診斷_計劃`:不破壞。其 WHY 已有 `[例外:…]` 欄位,要補的內容併進該欄位。按情境打開、預設關,遵守「不選:每次都錄」的理由。
- `Projects/原生記憶體增長判法_計劃`:分工一致,不影響。判法計劃列的四種已知失效形狀,與提示計劃「實務隱患」第 159 行列的四種完全對應。兩篇互指的連結都成立,`lands_in` 相同也不衝突。

### 實務隱患逐類

| 風險類 | 結論 |
|---|---|
| 併發 | 同一台裝置同一行程只能有一個 heapprofd 工作階段。第一段沒有 heapprofd,第二段與第一段不重疊,e2e 的情境是序貫跑的。spec 已把 `heapprofd_rejected_concurrent` 列進 failed 原因。同一 repo 兩個收集同時跑會互撞,與第一段同一個天花板,無新增風險。 |
| 效能 | 第二段多一段 W+N 輪與最多 5 秒停錄。e2e 單步 3600 秒內包含第二段,逾時會讓 `st.step` 回 None,整個記憶體塊與後面的情境、效能一起被判成 unjudged。這個風險 spec 已用「長情境先估」處理。 |
| 資源 | 裝置暫存檔與 64 MiB buffer 沿用 `stop_record` 的 `finally`,中斷由 `abort_record` 收。新增的是 cleanup 停 App,需要 `pkg` 進 state(F4)。 |
| 回滾 | 回退段完整。`native_retained` 鍵預設留著以免指紋再變,這點已寫明。 |
| 遷移 | 只有改 `stability` 段的專案指紋才會變,沒打開的專案不受影響。 |

⚠ 我沒有查證 heapprofd 回傳的 `stack_profile_frame.name` 在 trace_processor 裡是否已 demangle。v57.2 的 `profile_packet_sequence_state.cc` 只把產生端給的字串原樣放進 `name`,沒有 demangle 步驟,所以 spec 同時比對「operator new」開頭與 `_Znw` 開頭是兩邊都防的合理寫法,不算缺陷。

總結:整份最高嚴重度為 major,blocking 共 2 條(F1、F2)。
