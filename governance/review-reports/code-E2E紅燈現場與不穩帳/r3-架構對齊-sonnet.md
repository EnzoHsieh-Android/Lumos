severity: minor

我只讀了程式,沒有跑測試。`_ci_latest_attempts` 和 `_out_clean` 等既有函式,我是對照第 745721d8 版的 `scripts/lumos` 看的。

## 問 1 分層與依賴方向:對齊
- 範本腳本只呼叫 `adb`、`maestro`,把結果寫進自己的 `steps.json`,沒碰 lumos 的帳本。`scripts/templates/android-e2e-run.sh` 的 `device_time`、`crash_log` 和 `accept()` 都是這樣。
- 「跑完才知道的欄位,直接補進 `st.data` 再 `st.save()`」是這支腳本本來的做法,例如 `st.data["collector_override"]`、`st.data["device_stuck"]`。第 3 輪修補把 `step(after=)` 這個新參數拿掉,改回這個做法,是往既有方向收。
- lumos 這側的流向是 `steps.json` 的 `evidence`,經 `_e2e_ui_evidence` 變成 UI 結果的 `fail_evidence`,再由 `_e2e_print_runs` 印出來。
- 判定結果還是由 judge 決定,點名由 `_e2e_flaky_notify` 負責,兩條線沒有混在一起。
- 總表的 `flaky` 欄位只由 `_e2e_history_append` 補進 `case_results`,補的時候用 `dict(i, flaky=True)` 產生新字典。綁版本的查證紀錄 `_e2e_case_results` 的 `items` 沒被改到。`_e2e_case_results` 的說明新加一句指向補欄位的地方,這是兩處要同步的地方,但有文件指引。
- 點名放在 `_e2e_history_append` 末尾。它的五個呼叫點(`scripts/lumos` 約 41388、42475、42479、42485、42511、42553 行)每一次記總表都會點名,沒有漏的路徑。
- `_e2e_flaky_counts` 用 `_canary_ledger_rows` 逐行讀帳,`_e2e_history_cmd` 也是,這是鄰居檔既有的讀帳核心。

## 問 2 命名與錯誤處理:大致對齊,有一處說明不精確
- 函式都叫 `_e2e_*`,常數都叫 `E2E_*`,放在函式之間,跟同檔 `E2E_GATE_BUDGET_SEC` 的位置一樣。
- 錯誤處理:
  - 讀不到總表時不印點名,靜默略過。
  - 讀總表出 OSError 時,`_e2e_history_cmd` 走 `_say_block` 回 2,跟既有路徑一致。
  - 寫總表失敗時印「提醒:」到 stderr,是原本就有的。
- 點名行的 `  ! ` 前綴,跟 `_e2e_select_cmd` 印「這些改到的檔沒有對應功能」的 `print(f"  ! ...")` 同一套。
- 外來文字出口:歷史行、點名、`--flaky` 行、UI 結果行都改成整行過一次 `_out_clean`,跟 `_say_block` 的單一出口寫法一致。
- 範本腳本的 `say("提醒:…")` 跟同檔其他提醒一致。
- 見 F1,是一處說明跟實際做法對不上。

## 問 3 第二種做法:不算引入第二種做法
- 不共用 `_ci_latest_attempts` 的理由我查過是真的。
  - `_ci_latest_attempts` 靠 `attempt` 和 `conclusion` 欄位比較。
  - 總表的行沒有這兩個欄位,全部會變成 `att=0, bad=1`。那樣 `cur is None or att > cur[0] or (att == cur[0] and bad > cur[1])` 只有第一行會進去,最後的重判行永遠不會取代第一行。
  - 它也是整行為單位,不是每支 flow 各取一次。
  - 所以用它,真正的重判結果會被丟掉,不共用的理由成立,不單獨判 major。
  - `_e2e_flaky_tally` 是單一實作,點名和 `--flaky` 共用,沒有兩套。
- 跨腳本格式比對:`device_time` 的 date 格式和 `android-stability-collect.sh:484` 的一樣,測試用 `re.findall(r"date '(\+[^']+)'")` 抽兩邊比相等(snapshot 926-929 行)。這是專案既有的「逐字相同、測試比相等」做法(跟 `android-e2e-run.sh` 約 360 行 `test_data` 那條同一套),沒有新做法。
- 逐行讀帳、外來文字清理、記總表,都用既有函式 `_canary_ledger_rows`、`_local_ledger_append`、`_out_clean`、`_say_block`,沒有自創。

### F1 說明寫「口徑同 `_ci_latest_attempts`」,但空字串 run_id 的處理不同
severity: minor
blocking: no
引句:「同 _ci_latest_attempts 的口徑;那支是 CI 的」
對照的既有檔位置:file: `scripts/lumos:58997`(`_ci_latest_attempts`)
1. `_e2e_flaky_tally` 的說明和 `android-e2e-acceptance` 的 WHY 都說 run_id 數字、字串算同一次是「同 `_ci_latest_attempts` 的口徑」。
2. 兩邊對空字串 run_id 的處理其實不同:
   - `_ci_latest_attempts` 只有 `rid is None` 才算沒有 run_id,`""` 會 `str()` 後與其他 `""` 歸成同一次。
   - `_e2e_flaky_tally` 把 `rid != ""` 當成沒有 run_id,每行各算一次。
3. 接手的人讀到說明會以為兩邊行為一樣。真正相同的只有「數字和字串 run_id 轉字串比」這一點。
4. 影響很小:`_e2e_history_append` 寫總表時 `rid` 來自 `steps.run_id` 或 run 目錄名,不會是空字串。

不對齊共 1 條,其中 major 0 條
