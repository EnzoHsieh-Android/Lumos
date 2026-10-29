severity: minor

四問都沒有「第二種做法」,也沒有跨層直呼。有 6 條 minor:命名、驗證位置、錯誤處理和落點與鄰居不一致,結構是對的。

## 問 1 分層與依賴方向:對齊

- 設計是收集腳本取數並歸併到呼叫位置層,lumos 排名和印出,skill 只寫怎麼用。這跟鄰居一樣。鄰居是收集腳本只縮減資料(`heap_result` 在 `scripts/templates/android-stability-collect.sh:460`,`cycle_numbers` 在 `:289`),判定在 `scripts/lumos`(`_macrobench_judge_stability` 在 `:40181`)。
- 呼叫方向沒變。lumos 只讀結果檔,不接裝置(`_macrobench_stab_load` 在 `:39982`)。收集腳本不 import lumos,只用 subprocess 呼叫它(`:112` 的 `load_config`)。
- 新增的兩支範本(`android-stability-native.sql`、`android-stability-heapprofd.pbtxt`)跟 `android-stability-cycle.sql`、`android-stability-record.pbtxt` 同層,也走 `_VENDORED_TREE_FILES`(`scripts/lumos:31959`)。

## 問 2 命名與錯誤處理:大致對齊,有 4 條 minor(F1 到 F4)

- 狀態用 `src()`(`collect.sh:376`),原因寫法也是 unsupported/failed 加 reason,跟 `heap_result` 一致。
- 型別錯回 2 擋下,跟 `_macrobench_stab_optional_err` 一致。
- F1 到 F4 見下。

## 問 3 第二種做法:對齊,spec 寫的「沿用」都做得到,另有 1 條 minor(F5)

- 錄製和停錄:`start_record`(`:305`)和 `stop_record`(`:335`)寫死了範本名、`record.pbtxt`、`lumos-stability-` 前綴、`cycle.pftrace` 和訊息裡的 `stability.max_record_s`。spec 列的 5 個參數正好是這幾處,加參數就能沿用,不用另寫一套。
- 保存規則:`heap-native.pftrace` 符合 `prune_old_snapshots` 的樣式 `heap-.*\.pftrace`(`:148`),7 天自動刪沿用。
- 清理:`abort_record` 和 `state["rec"]` 這個槽沿用,第一段 `del state["rec"]`(`:495` 附近)之後再開第二段,不衝突。
- 解析:`heap_counts`(`:251`)用 split 再 `",".join` 湊回,`cycle_numbers`(`:289`)用 split。兩者換成共用的 csv.reader 函式,輸出是 TP 的引號格式,做得到。
- 查詢範本:`android-ui-attribution.sql` 確有 `WITH RECURSIVE`,測試也有 `_ms_sql`(`scripts/test_lumos.py:18421`)這套用 sqlite3 對假表跑的做法可沿用。
- 只提醒的輸出:`low_iterations` 和 `stability_unjudged`(`scripts/lumos:40311`)是獨立於門檻的固定鍵,`native_retained` 比照放初始字典,同一種做法。

## 問 4 落點:大致合理,有 1 條 minor(F6)

- 兩支新範本放 Systems/android-stability-collector。該篇 about_code 本來就列 cycle.sql、heap-classes.sql 和 record.pbtxt,所以不另開。
- lumos 端的驗證和印出放 Systems/macrobenchmark-adapter。它的 about_code 有 `scripts/lumos`,所以不另開。
- 兩份計劃的分工沒問題:這份做排行,判漲停另開 `Projects/原生記憶體增長判法_計劃`。

### F1 `native_retained` 的驗證散在兩處,跟其他 stability 選填鍵不同
severity: minor
blocking: 否
引句:「lumos 在 `_macrobench_stab_top_err` 驗(那裡拿得到 `stability_scenarios`)」
file: `scripts/lumos:39557`
1. stability 段所有選填鍵(`test_data`、`strictmode`、`category`、`max_record_s`、`adb_serial`、`mapping`)的型別都在 `_macrobench_stab_optional_err`(`:39557` 到 `:39574`)驗。
2. `_macrobench_stab_top_err`(`:39475`)目前只呼叫 `_macrobench_stab_cfg_err` 和 `_e2e_scenarios_err`。情境名對照 `stability_scenarios` 的檢查,鄰居是由 `_e2e_cfg_err(..., scen=)` 帶 `scen` 進去做(`:40603`、`:40571`)。
3. spec 把型別、重複、對照情境名全塞進 `top_err`。接手的人要猜 stability 的鍵到底看 optional_err 還是 top_err。
4. spec 沒說型別檢查是否仍放 optional_err,只把跨段對照放 top_err。

### F2 `"@default"` 是新的「stability 段本身」寫法
severity: minor
blocking: 否
引句:「`"@default"` 代表沒指定情境的那一段(沒設 LUMOS_STABILITY_SCENARIO」
file: `scripts/templates/android-e2e-run.sh:304`
1. 鄰居在收集腳本和 e2e 腳本內部用 `None` 代表 stability 段本身(`android-e2e-run.sh:304` 到 `:307`、`:473`)。設定檔裡沒有這個名字,`features` 的記憶體情境只能指到 `stability_scenarios` 的名字(`scripts/lumos:40572`)。
2. spec 在設定檔裡造一個字面值 `"@default"`,設定檔格式多了一個特殊值。
3. 這個值不會跟情境名撞,因為 `_e2e_scenarios_err` 的情境名只收 `[A-Za-z0-9_-]+`(`:40483`)。但 skill 的 reference.md 設定表要補寫,spec 的第 7 條有列這張表。

### F3 `sites` 每項的驗證跟鄰居不同
severity: minor
blocking: 否
引句:「retained 用 `_secev_int` 驗整數、再擋負數,不合格的呼叫位置不採用」
file: `scripts/lumos:40020`
1. 鄰居的數字驗證是 `_macrobench_stab_val`(`:40020`,有限數、非負),不合格就把整個來源列成「沒判」並附原因(`:40031` 到 `:40035`),形狀不對也不噴例外(`:40028`)。
2. spec 自己組了 `_secev_int` 加負數檢查,改成逐項丟棄再印一行「有 N 個沒採用」。
3. `sites` 不是清單、項目不是物件、缺 `func` 等欄位的處理,spec 沒寫,鄰居對形狀不對有明確做法。

### F4 讀來源段的訊息和「打開了沒」的判斷,沿用 `_macrobench_stab_src` 對不起來
severity: minor
blocking: 否
引句:「讀來源段沿用 `_macrobench_stab_src`;印的函式獨立於門檻輸出」
file: `scripts/lumos:40010`
1. `_macrobench_stab_src` 回 `(None, 原因字串)`。缺段時是「結果檔沒有 X 這個來源」,非 ok 時是「X 沒收到(狀態):原因」。spec 要的是缺段時寫 unsupported 加「結果檔沒有 native_retained 段」,非 ok 時印「原生配置排行沒跑成:<原因>」。字串對不上,只能在呼叫前自己先判斷缺段,訊息會變成雙重前綴。
2. S15 的條件是「打開了但 status 不是 ok」才印,但結果檔裡「沒替這個情境打開」和「沒宣告測試資料」「Android 版本不支援」都是 unsupported。lumos 分不出是哪一種,印或不印沒有依據。
3. lumos 也不能靠結果檔反查是不是打開的情境:結果檔的 `scenario` 欄是情境說明文字,不是 `stability_scenarios` 的名字(`collect.sh:405`)。spec 沒說誰負責區分。

### F5 第一段先寫結果檔再原子替換、第二段包 try/except Exception,是這支檔裡新的錯誤處理
severity: minor
blocking: 否
引句:「收集腳本先把第一段的結果寫成結果檔(這時 `native_retained` 段寫 failed「第二段沒跑完」)」
file: `scripts/templates/android-stability-collect.sh:528`
1. 現行 `main()` 在 `measure` 全部做完後,用 `open(out, "w")` 一次寫出結果檔。這支檔裡沒有任何原子替換,中斷時的訊息明寫「沒寫結果檔」(約 `:547`)。
2. spec 讓第二段被中斷時結果檔已經在磁碟上,這句訊息會變成不實。spec 沒列要改它。
3. spec 也沒說原子替換用哪個寫法。`scripts/lumos` 有 `_write_bytes_atomic`(`:28506`),但收集腳本是獨立複製出去的,不能 import 它。
4. `measure` 之外,現行例外處理是 `except BaseException: cleanup(state); raise`(約 `:552`),不吞例外。spec 的第二段「任何意外都寫成 failed」是新做法,理由也成立,但接手的人會不知道哪一種是慣例。

### F6 `lands_in` 漏了兩個會被改到的地方
severity: minor
blocking: 否
引句:「[[Projects/Android逐層診斷_計劃]] 的分層 WHY 補一條例外:打開 native_retained 的情境在收集階段就錄 heapprofd」
file: `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:6`
1. `macrobenchmark-adapter` 的負責範圍寫「讀 stability.json 判記憶體與穩定性」,並寫「不擋推送」。spec 的第 7 條只提到要改 collector 的負責範圍,沒提 adapter。lumos 端新增一份不進判定的排行與一個設定鍵驗證,該篇範圍描述要跟著改。
2. `native_retained` 寫進設定會變動 e2e 的記憶體設定指紋。指紋規則歸 `Systems/android-e2e-acceptance`(`Systems/android-e2e-acceptance.md:16`),spec 在「遷移」只寫了影響,沒把這篇列進 `lands_in`。
3. spec 的第 7 條要改的 skill、reference.md、兩份別的計劃,都有寫落點,這部分沒問題。

不對齊共 6 條,其中 major 0 條
