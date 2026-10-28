severity: minor

## 問 1 分層與依賴方向:對齊

- **lumos 沒碰裝置。** `_macrobench_native_retained` 只讀 stability.json。這跟 `_macrobench_stab_heap` 讀同一份檔、`scripts/lumos:40039` 的 `_macrobench_stab_native_unreachable` 同層。裝置動作全在收集腳本裡。
- **收集腳本沒自己判過不過。** `native_phase` 只寫 `status`/`reason`/`sites`,判定留給 lumos。lumos 這邊也標了只提醒、不進任何判定。這跟收集腳本檔頭「不判過不過」一致。
- **設定驗證沒有重驗。** 情境名對照 `stability_scenarios` 放在 `_macrobench_stab_top_err`。收集腳本照舊先跑 `lumos macrobench --check-config`,見 `android-stability-collect.sh:316`。腳本內多查的 test_data 與 sdk 是裝置端才知道的事,不算重驗。
- **整數驗證沿用既有的。** `_secev_int` 在 `scripts/lumos:8578`,`_macrobench_stab_heap` 也用同一個。
- **e2e 範本只多傳一個環境變數。** `LUMOS_STABILITY_STEP_BUDGET_S` 的傳法跟既有的 `LUMOS_STABILITY_SCENARIO` 同一種,沒有跨層。
- **印出位置跟鄰居一樣。** 兩個呼叫點(`_macrobench_without_results` 與正常路徑)都緊接在 `_macrobench_print_thresholds` 後面,`scripts/lumos:40306`。

## 問 2 命名與錯誤處理:有兩處不一致

**1. 狀態形狀自己手組,沒走 `src()`/`_macrobench_stab_src`**
severity: minor
blocking: 否
引句:「return {"enabled": True, "status": "failed", "reason": MACROBENCH_NATIVE_BAD + bad, "sites": []}」
- 既有做法:收集腳本用 `src(value, why, status_if_none)` 產生來源段,見 `android-stability-collect.sh:489`。lumos 端用 `_macrobench_stab_src` 統一回 (None, 原因),見 `scripts/lumos:40020`。
- 這次:兩端都手組 dict。lumos 端另外發明 `MACROBENCH_NATIVE_BAD` 這個前綴,靠 `startswith` 區分「形狀不對」和「沒跑成」。
- 鄰居本身不全一致:`strictmode_result` 在 `android-stability-collect.sh:454` 也手寫 `{"status": "unsupported"...}`。所以收集腳本這端只算輕微,lumos 端偏離較明顯。
- 代價:`status`/`reason` 多了第三種組法,之後改狀態詞要改三處。

**2. 失敗處理多了一套:吞掉所有例外,逾時另寫一句**
severity: minor
blocking: 否
引句:「return {"enabled": True, "status": "failed", "reason": f"第二段出了意外({type(e).__name__})"}」
- 既有做法:`main()` 對 `BaseException` 是 `cleanup(state)` 後 `raise`,見 `android-stability-collect.sh:693`。`heap_counts` 對逾時沒有特判,統一回 `f"trace_processor 算不了快照:{err.strip()[-200:] or rc}"`,逾時字樣已在 `err` 裡,見 `android-stability-collect.sh:374`。
- 這次:`native_phase` 用 `except Exception` 轉成 `failed`,`native_query` 逾時另寫 `"查詢逾時"`。
- 為什麼不算 major:這一段是只提醒,降級成 failed 說得通,結構沒壞。但這是專案裡第一處把例外吞成 reason 的地方,且只留型別名,排查時看不到原因。
- 代價:逾時字樣和其他查詢不一致,例外細節看不到。

## 問 3 第二種做法:一處邊界,一處重複

**3. 文字欄用 hex 輸出,而既有查詢用逗號重接**
severity: minor
blocking: 否
引句:「select 'site' as kind, hex(substr(func, 1, 500)) as a, hex(so) as b, hex(substr(caller, 1, 500)) as c」
- 既有做法:`heap_counts` 對含逗號的類別名用 `deobfuscate(",".join(cells[:-1]), mapping)` 重接,見 `android-stability-collect.sh:382`。
- 這次:同樣是 trace_processor 文字欄,改用 SQL 端 hex 再 `bytes.fromhex` 解回。
- 為什麼只標 minor:切行與去引號共用 `tp_rows`,不是另一套解析器。hex 只是對引號與換行這種「重接救不回來」的情況加碼。我判不準這算不算第二種做法,請編排者定奪。
- 代價:同一檔現在有兩種處理文字欄的做法,新增查詢時不知道該選哪個。

**4. `native_run` 把 `measure()` 的流程複製了一份**
severity: minor
blocking: 否
引句:「shell(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1")」
- 既有做法:`measure()` 在 `android-stability-collect.sh:476` 起:停 App → 啟動 → `read_exits` → `pidof` → 暖機 → `start_record` → 驅動 → `stop_record` → `exit_diff`。
- 這次:`native_run` 把這一串又寫一遍,只換了錄製範本。
- 做得對的地方:`start_record` 與 `stop_record` 都加了預設參數去重用。這一層沒有另起爐灶。
- 代價:`measure()` 日後改流程(例如加清理步驟)時,這一份容易漏改。

其餘比對都對齊:
- 擋下用 `die()`,回 2。
- 暫存清理走既有的 `abort_record`/`stop_record` 的 `finally rm`,沒有另一套。
- 查詢輪廓與 `android-ui-attribution.sql` 一樣用 `WITH RECURSIVE`。
- 檔案已加進 `_VENDORED_TREE_FILES`。
- `preflight` 的 gitignore 檢查有涵蓋新檔名。

## 表態記錄

`py-external satisfied — scripts/scenario_probe.py:1077` 這題指的是別的檔。這次 diff 裡沒有對應的外來資料新路徑被漏報,我沒有發現它與本 diff 衝突,不判張力。

不對齊共 4 條,其中 major 0 條
