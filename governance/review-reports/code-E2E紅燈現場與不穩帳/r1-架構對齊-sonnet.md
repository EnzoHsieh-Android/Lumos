severity: minor

## 三問

**1. 分層與依賴方向:對齊。**
- 範本腳本只寫自己的 run 目錄和 `steps.json`(`save()` 在 `scripts/templates/android-e2e-run.sh:436`)。它沒碰 `history.jsonl`。
- lumos 只讀 `steps.json` 的 `evidence` 欄位,不重做範本腳本的事。方向和既有的一樣:範本腳本寫 `steps.json`,`_e2e_judge_ui` 讀,`_e2e_history_append` 寫總表,`_e2e_history_cmd` 讀總表。
- 新增的 `_e2e_flaky_*` 和 `_e2e_history_items`、`_e2e_history_line` 都放在 `_e2e_history_*` 那一群旁邊。讀帳走既有的 `_canary_ledger_rows`(`scripts/lumos:20387`)。
- 沒有跨層直呼。
- 唯一的結構小問題是 F3。

**2. 命名與錯誤處理:大致對齊。**
- 範本腳本新增的 `maestro_has_evidence_flags`、`device_time`、`crash_log` 都用既有的 `run()` 和 `adb()`(`:127`、`:159`),輸出走 `say()`,錯誤回 `None`、不丟例外。
- `global EVIDENCE` 有先例:`global SEL`(`:557`),宣告也跟 `SEL = None` 並排(`:52`)。
- lumos 側的讀不到總表就不印,跟既有 `_e2e_history_append` 的寫不進去只提醒一致。
- 有三處小出入,見 F3、F4、F5。

**3. 第二種做法:沒有主要違反,有兩處值得記。**
- 讀 jsonl、跑子程序、寫 JSON 都重用既有 helper,沒有自創。
- 不穩次數的算法有兩份(F1)。
- 讀裝置時間的格式複製了一份,沒有配對的守衛(F2)。

### F1 不穩次數在同一份 diff 裡算了兩套
severity: minor
blocking: no
引句:「        for i in r.get("items") if isinstance(r.get("items"), list) else []:」
`scripts/lumos:41367`(`_e2e_history_append` 一帶,新函式從 `_e2e_flaky_counts` 起)
1. `_e2e_flaky_counts`(點名用)和 `_e2e_flaky_report`(`history --flaky` 用)各自寫了一遍同樣的篩選:`kind == "ui"`、`result in (pass, fail)`、`flaky is True`。
2. 窗口語意不同:前者是每支 flow 自己最近 20 筆,後者是 `--last` 筆總表行。
3. 鄰居的做法是一份讀法給 `history` 全部用(`_e2e_history_cmd` 的讀帳迴圈,`:41463` 附近)。接手的人改「什麼算第二次才過」時要同時改兩處。

### F2 裝置時間格式複製一份,沒有配對守衛
severity: minor
blocking: no
引句:「    rc, out, _ = adb(serial, "shell", "date '+%m-%d %H:%M:%S.000'")」
`scripts/templates/android-stability-collect.sh:484`(收集腳本是 `shell("date '+%m-%d %H:%M:%S.000'")`)
1. `device_time` 的 docstring 寫「格式同收集腳本」,但沒有測試抽出兩邊比相等。
2. 專案在兩支獨立腳本共用規則時,慣例是測試比兩邊那一行逐字相同,例如 `scripts/templates/android-e2e-run.sh:335` 的註解。
3. 改格式時另一邊靠記憶同步。

### F3 `evidence` 同名三種形狀,輸出端靠檔名尾巴反推種類
severity: minor
blocking: no
引句:「        scene, crash = [e for e in ev if not e.endswith(".crash.txt")], [e for e in ev if e.endswith(".crash.txt")]」
`scripts/lumos:42532`(`_e2e_print_runs`);對照 `_e2e_history_append` 的 `"evidence": str(Path(".lumos")…)`
1. 總表一行的 `evidence` 是字串路徑。`steps.json` 每步的 `evidence` 是 `{dir, crash}` 字典。judge 結果的 `evidence` 是路徑清單。
2. `_e2e_ui_evidence` 把字典攤平成清單,丟掉 `dir` 和 `crash` 的標籤。印的時候又靠 `.crash.txt` 後綴猜回去。
3. 範本腳本取檔名的規則和 lumos 的後綴判斷之間沒有明寫的契約,也沒有跨檔的守衛。
4. 鄰居的 `reports`、`report` 是結構化欄位,不靠檔名反推。

### F4 新印出的 flow 名稱清理不一致
severity: minor
blocking: no
引句:「        print(f"{_out_clean(f, 300)}  {n} 次裡 {k} 次第二次才過  最近一次證據 {ev}")」
`scripts/lumos:41437` 的 `_e2e_history_line`(同群既有函式,flow 名稱原樣印出)
1. `_e2e_flaky_report` 的 flow 名稱過了 `_out_clean`。
2. 同一份 diff 的 `_e2e_flaky_notify`(印 `{fl}`)和 `_e2e_history_line`(印 `shaky` 清單)都沒過。
3. `_out_clean` 在專案裡是「外來文字單一出口」(`:19371`、`:19382`)。同一個名稱在三個印字點的處理不同。

### F5 在 `step()` 之外改最後一步再存檔
severity: minor
blocking: no
引句:「            st.data["steps"][-1]["evidence"] = {"dir": ev if EVIDENCE else None, "crash": crash}」
`scripts/templates/android-e2e-run.sh:443`(`step()` 是寫步驟紀錄的唯一入口,欄位都在 `rec` 裡成形)
1. 其他所有步驟欄位都由 `step()` 一次寫好、一次存檔。
2. 新碼多了一次 `st.save()`,並且依賴「剛 append 的是最後一個」。
3. 結構沒錯,但跟既有寫法不同。

不對齊共 5 條,其中 major 0 條
