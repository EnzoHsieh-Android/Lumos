severity: major

## 三問

**1. 分層與依賴方向:對齊,沒有跨層直呼。**
- 範本腳本只寫 steps.json(`scripts/templates/android-e2e-run.sh:454` 的 `rec.update(after(rc))`、約 502 行的 `evidence`)。它沒有碰 `scripts/lumos` 的帳本,方向跟 `scripts/templates/android-stability-collect.sh` 一樣。
- lumos 端只讀 steps.json。`_e2e_ui_evidence`(`scripts/lumos:40819`)把欄位不對的當沒有,跟同檔 `_e2e_steps`、`_e2e_tail` 這批 `_e2e_*` 的防禦寫法一致。
- 總表欄位沒有反過來影響綁版本的查證紀錄。flaky 只補進 `case_results`(`scripts/lumos:41366` 附近),`_e2e_case_results`(`scripts/lumos:41229`)沒動。這個分離是對的,但實作方式見 F2。
- 範本腳本與收集腳本的裝置時間格式,用「抽出兩邊的格式比相等」測試守住(`scripts/test_lumos.py:19556`)。這跟既有的逐字複本守衛一致,例如 `scripts/test_lumos.py:26617`、`scripts/test_lumos.py:26885`。

**2. 命名與錯誤處理:大致對齊,有三處小不一致(F3、F4、F5)。**
- 終端訊息:`say("提醒:…")` 對應 `scripts/templates/android-e2e-run.sh:66`。`print("  ! 不穩帳…")` 對應 `scripts/lumos:41218` 的 `  ! ` 前綴。寫不進總表走 stderr 的「提醒:」是既有寫法。
- 逐行讀帳走既有的 `_canary_ledger_rows`(`scripts/lumos:20387`),追加走 `_local_ledger_append`(`scripts/lumos:1698`)。這兩個沒有另起爐灶。

**3. 第二種做法:有一處(F1)。**
- 「同一個 run_id 只算一次」另寫了一套視窗式去重。
- 其餘的自創項(`after` 回呼、分欄 `evidence`、case_results 補丁)見 F2、F4、F5。

## Findings

### F1 同一個 run_id 重判只留最後一行,又寫了一套去重
severity: major
blocking: yes
引句:「def _e2e_window_put(dq, ids, r, val):」
對照的既有檔位置:file: `scripts/lumos:59003`(`_ci_latest_attempts`)

1. 新增的 `_e2e_window_put`(`scripts/lumos:41413` 起)用 `deque(maxlen)` 加 `ids` 計數器,實作「同一個 run_id 的舊行拿掉、只留最後一行、沒有 run_id 的照放」。
2. 同檔早已有同一語意的 `_ci_latest_attempts`。它的 docstring 寫明「同一個執行(run_id)重跑過的,只留最後一次嘗試;沒有 run_id 的原樣保留」,並且連「run_id 一筆存整數、一筆存字串也算同一個」都處理了。
3. 新碼的 run_id 處理比既有的窄:只認非空字串,不做 `str(rid)`。兩套對「什麼算同一次執行」的邊界已經不一樣。
4. 接手的人要猜:總表同一個 run 目錄重判的行,該用 CI 那套還是 `_e2e_window_put`。
5. 同一個總表讀取還分成兩種語意。一般 `history` 不去重,`--flaky` 與點名去重(`scripts/lumos:41490` 起的 `_e2e_history_cmd`)。同一支指令的兩個模式對「一次執行幾行」的答案不同。
6. ⚠ 交編排者:`_ci_latest_attempts` 吃整個 list、用 attempt 與結論嚴重度裁決。這裡是串流加視窗上限、單純「後者贏」,語意不同,不能直接替換。但「同 run_id 留最後」這個概念重複出現。判 major 是照本席錨(引入第二種做法)。若編排者要接受,需在筆記裡寫明為什麼不複用 `_ci_latest_attempts`,以及兩邊「run_id 相等」的口徑差異。

### F2 總表的 case_results 在寫入處補丁,不在產生處補
severity: minor
blocking: no
引句:「shaky = {_e2e_norm(x["flow"]) for x in blocks.get("ui") if x.get("flaky")}」
對照的既有檔位置:file: `scripts/lumos:41229`(`_e2e_case_results`)

1. 情境項目原本只由 `_e2e_case_results` 產生。`_e2e_history_append` 現在又用一份 `_e2e_norm(flow)` 的對照集合,對產出的 items 逐項 `dict(i, flaky=True)` 重寫一遍。
2. 結構上沒有跨層:查證紀錄不帶 flaky 是有意的,計劃與 Systems 筆記都有寫。
3. 接手的人要猜:「情境的 UI 項目長什麼樣」有兩個出處。`_e2e_case_results` 產生的是基本款,`_e2e_history_append` 補上去的是總表款。往後有人給 `_e2e_case_results` 加欄位,可能漏看這裡的補丁。

### F3 外來文字清理,同一個函式裡只清了一半
severity: minor
blocking: no
引句:「shaky = [_out_clean(i.get("name"), 300) for i in its if isinstance(i, dict)」
對照的既有檔位置:file: `scripts/lumos:41470`(同函式 `_e2e_history_line` 的 `bad = […]`)、`scripts/lumos:41222`

1. 新增的 `shaky` 清了 flow 名稱,同一函式上一行的 `bad` 列的是同一個來源的 `i.get('name')`,沒有清。
2. `_e2e_flaky_report` 印的 `ev`(證據路徑,也是從總表讀出來的外來字串)沒有清。
3. `_e2e_print_runs` 的 `x['flow']` 也沒有清。
4. 既有的外來文字出口 `_out_clean` 在 e2e 這群只用在 `scripts/lumos:41218`。新碼是第二批使用者,而且只蓋住新增的路徑。接手的人看不出「哪些輸出要過 `_out_clean`」的規則。
5. 錯誤處理一致性屬於本席範圍,所以列為 minor。

### F4 `evidence` 一個鍵三種形狀
severity: minor
blocking: no
引句:「out[-1]["evidence"] = ev」
對照的既有檔位置:file: `scripts/lumos:41366`(總表行 `"evidence": str(Path(".lumos")…)`,字串);`scripts/lumos:40819`(`_e2e_ui_evidence`)

1. steps.json 的 `evidence` 是 `{dir, crash}`(單數,可為 None)。
2. judge 的 UI 結果 `evidence` 是 `{dirs, crashes}`(複數,列表)。
3. 本機總表行的 `evidence` 是 run 目錄的字串。
4. 同一個詞指三種東西,而且 `_e2e_flaky_report` 的 `a[2] = r.get("evidence")` 讀的是第三種。結構是對的,命名會讓接手的人猜。

### F5 Steps.step 新增 after 回呼,範本腳本裡沒有先例
severity: minor
blocking: no
引句:「rec.update(after(rc))」
對照的既有檔位置:file: `scripts/templates/android-e2e-run.sh:512`(`st.data["collector_override"] = COLLECT`)、`scripts/templates/android-e2e-run.sh:519`

1. 這支腳本裡「跑完才知道的欄位」本來都是直接改 `st.data[...]` 再 `st.save()`。
2. 現在只有 `evidence` 這一個欄位走回呼:`Steps.step` 加了 `after=` 參數,呼叫端傳 lambda,還要用預設參數 `ev=ev, since=since` 綁值。
3. 回呼拋例外時,那一步(含 rc)還沒進 `self.data["steps"]` 就中斷了。這跟 `step` 內 `run` 的容錯寫法(`rc is None` 也要記一筆)不同。這點只比較錯誤處理的一致性,不是找 bug。
4. 修補前(`st.data["steps"][-1]["evidence"] = …`)其實跟 `scripts/templates/android-e2e-run.sh:524` 一帶的寫法一致,是修補把它換成了第二種機制。⚠ 若編排者認為回呼是為了讓「記一筆」原子化而有意引入,應在筆記寫明;目前筆記沒有說明。

不對齊共 5 條,其中 major 1 條
