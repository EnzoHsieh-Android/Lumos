severity: clean

我已讀完兩份 patch,並用 `git show` 對照 `e98debe1` 的 `scripts/lumos`、`scripts/templates/android-e2e-run.sh` 和 `scripts/test_lumos.py` 的相鄰既有碼。三問都對齊,沒有第二種做法,也沒有跨層直呼。

## 1. 分層與依賴方向:對齊
- 範本腳本只寫自己 run 目錄裡的東西。它把 `evidence` 補進 steps 紀錄,現場放在 `ui/<名>.try<N>/` 和 `ui/<名>.try<N>.crash.txt`。它沒碰 `history.jsonl`,也沒呼叫 lumos 的帳本函式(patch 的 `android-e2e-run.sh` 段)。
- lumos 只讀 steps.json 並把路徑帶進判定結果,沒有重做閃退緩衝收集。`_e2e_ui_evidence` 把壞欄位當沒有,和同檔 `_e2e_tail` 對外來資料的處理一致。
- 總表欄位沒有反向影響綁版本的查證紀錄。`_e2e_case_results` 的 docstring 寫明不帶不穩,`_e2e_history_append` 在總表那份才補 `flaky`。這是刻意分開,方向正確。
- 範本腳本的新函式 `maestro_has_evidence_flags`、`device_time`、`crash_log` 沿用腳本內既有的 `run()`、`adb()`、`say()`。`global EVIDENCE` 同腳本已有 `global SEL`(`android-e2e-run.sh:558`)為先例。
- 總表讀寫沿用 `_repo_path_unsafe`、`_local_ledger_append`、`_canary_ledger_rows`(`scripts/lumos:41376-41380`、`:20387`)。

## 2. 命名與錯誤處理:對齊
- 命名:`_e2e_*` 前綴和 `E2E_*` 常數都和同檔群組一致,「flaky」也沿用 judge 既有詞。`fail_evidence` 刻意避開 `evidence`,說明寫在 `_e2e_judge_ui` 的行內註解。
- 終端訊息:`  ! 不穩帳:` 的前綴和同檔 `scripts/lumos:41218` 一致。擋下訊息仍走 `_say_block`,新碼沒有自己印「擋下:」。範本腳本的 `say("提醒:…")` 和 `android-e2e-run.sh:366` 同款。
- 外來文字出口:點名、`history --flaky`、`_e2e_history_line` 整行、judge 的 UI 行都整行過 `_out_clean`,和 `scripts/lumos:41218`、`:41545` 同一個單一出口。
- 錯誤回傳:`history` 讀不到總表時維持 `_say_block` 加 rc 2。點名讀不到時靜默不印,符合計劃的「只提醒」。

## 3. 第二種做法:沒有
- **`_e2e_run_key` 不共用 `_ci_latest_attempts`:理由屬實。**
  - 我開兩邊的碼對照。`_ci_latest_attempts`(`scripts/lumos:59011-59038`)靠 `attempt` 和 `conclusion` 取最壞,吃整份清單。
  - 同嘗試次數、同壞度時它保留先到的那筆(條件是 `bad > cur[1]`)。總表需要的是「同一次執行留最後一次判定」,語意相反,所以不能共用。
  - 兩邊「只看 None、轉字串」的口徑相同。這次修補把原本多出的 `rid != ""` 拿掉,反而更貼近既有判法。
- **逐行讀帳:** 沿用 `_canary_ledger_rows`,沒有自創讀法。`rows` deque 和 `runs` OrderedDict 是同一個函式內依模式二選一,執行鍵由 `_e2e_run_key` 單一來源產生,點名與 `--flaky` 共用 `_e2e_flaky_tally`。
- **裝置時間格式:** `date '+%m-%d %H:%M:%S.000'` 在 `android-stability-collect.sh:484` 和 `android-e2e-run.sh` 的 `device_time` 各一份,兩支腳本是獨立檔案不能互相 import。這個做法和既有慣例相同:`android-e2e-run.sh` 的 test_data 那行已有「測試抽出兩邊比相等」的先例。這次 `scripts/test_lumos.py:19556` 附近也有同款比對測試「裝置時間格式跟收集腳本逐字相同」。
- **測試載入:** `_load_lumos_inproc()` 在基準版的 `t_android_e2e_*` 內已有 8 處以上使用(`t_android_e2e_changed_edges`、`t_android_e2e_fingerprint`、`t_android_e2e_r4_edges` 等),新增的兩處呼叫不是新做法。

目標架構:這次是「on」,但 prompt 沒附「[目標架構]」段,所以只照鄰居比對,沒有可套用的目標規則。

不對齊共 0 條,其中 major 0 條
