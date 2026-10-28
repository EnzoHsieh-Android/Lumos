severity: major

### F1 `history --flaky --case <情境>` 對按功能跑的紀錄一律回報「沒有第二次才過」
severity: major
blocking: yes
引句:「+        _e2e_flaky_report([(r, _e2e_history_items(r, case)[0]) for r in rows])」
file: `scripts/lumos:41366`(case_results 只帶 result 與 items,items 沒有 flaky)

1. 輸入:`sh android-e2e-run.sh --case login.ok` 跑出一次第二次才過的紀錄,接著執行 `lumos android-e2e history --flaky --case login.ok`。
2. 按功能跑時,`_e2e_history_append` 寫的 `case_results[fc].items` 是 `_e2e_case_results` 重組的 `{"kind","name","result"}`,沒有 `flaky`。頂層 `items` 才有 `"flaky": true`。
3. `_e2e_history_items(r, case)` 在帶 `--case` 時改回傳 `case_results` 的 items。`_e2e_flaky_report` 在那裡找不到 `flaky`,印出「最近 1 筆紀錄裡沒有第二次才過的 flow」。這是錯話。一般的 `history --case` 那行也少了「第二次才過:…」。
4. 重現:我在 clone 裡加了臨時探針,用真範本腳本、假 maestro 跑一次 `rcs="1 0"`,跑完已刪。
   - 總表那行:`TOP [{... 'flaky': True}]`,`CASE {'login.ok': {... 'items': [{'kind':'ui','name':'.maestro/login.yaml','result':'pass'}]}}`
   - `--flaky`(不帶篩):`.maestro/login.yaml  1 次裡 1 次第二次才過`
   - `--flaky --case login.ok`:`最近 1 筆紀錄裡沒有第二次才過的 flow`
   - `--feature login`:正常,只有 `--case` 壞
5. 測試為何沒抓到:`t_android_e2e_flaky_history` 用 `_e2e_flaky_rows` 手造總表,只有頂層 `items`,沒有 `case_results`。真實的按功能紀錄形狀沒被測到,測試等於只驗了造資料的那一邊。
6. skill 與 README 都教人用 `--case`,所以這是常用路徑。

### F2 重判同一個 run 目錄會把同一次不穩重複計入,點名次數虛增
severity: minor
blocking: no
引句:「+                per[i["name"]].append(i.get("flaky") is True)」
file: `scripts/lumos:41406`(沒有依 run_id 去重)

1. 輸入:一次真實的第二次才過,之後對同一個 run 目錄執行 `lumos android-e2e judge <run> --no-record --history` 兩次。judge 的錯誤訊息本身就教人用 `--no-record` 重判。
2. 每次重判都會追加一行 `items` 相同的總表紀錄,`_e2e_flaky_counts` 把它們當三次獨立事件。
3. 重現(同探針):總表變成 3 行,終端印「! 不穩帳:.maestro/login.yaml 最近 3 次裡 3 次第二次才過」,實際只發生一次。誤導的是提醒文字,不影響判定與回傳碼,所以標 minor。
4. 重複寫總表是舊有行為,新增的是「重複一行被當成一次新事件」這個後果。

### 逐項核對(鏡頭 4)
- **(a) 條款 S1–S6 與 d1**
  - 只收 crash 緩衝、`-d -T`、不清日誌、不讀其他緩衝:實作吻合。
  - 讀不到裝置時間就不收:`crash_log` 在 `since` 為 None 時直接回 None,吻合。
  - 回傳碼 0 不讀:吻合。
  - `-T` 精度:毫秒固定 000,同一秒內較早的 crash 會被多收,屬 d1 已接受的範圍,不標。
  - S6 的 `--case` 組合有 F1 的缺口。
  - 沒有做多的地方。
- **(b) 舊版 Maestro**
  - `maestro_has_evidence_flags()` 必須 `rc is not None` 且兩個旗標都在 stdout 或 stderr 文字裡才帶旗標。
  - `--help` 失敗、逾時、執行不了(rc 為 None)、旗標不在輸出中,都是不帶旗標、印提醒、照跑,不會讓每支 flow 變紅。
  - 非 0 回傳碼但輸出含旗標時會帶旗標,實務上是正常現象。
- **(c) 只提醒的保證**
  - `_e2e_flaky_notify` 只 `print`,回傳 None,`_e2e_history_append` 的回傳值沒人用。`flaky` 只加在總表的 item 上。
  - `_e2e_judge_ui` 對 `evidence` 的處理發生在 `out.append` 之後,不影響 `result`。
  - `OSError` 已接。壞行由 `_canary_ledger_rows` 跳過。總表不存在時 `p.is_file()` 前就走寫入失敗分支,不會呼叫 notify。
  - 判定結果、回傳碼與推送前判定未被改動。
- **(d) macOS/Linux**
  - `date` 在手機端 shell 跑,格式 `+%m-%d %H:%M:%S.000` 與收集腳本一致。
  - `adb logcat` 的帶空白參數與收集腳本用法相同。
  - 跨年:logcat 補裝置當年,12-31 到 01-01 之間沒有可指出的錯誤輸入。
  - 時區:裝置時間與 logcat 輸出都是裝置本地時區,一致。
- **邊界走查**
  - `_e2e_ui_evidence(tries[:len(why)])`:第一次過時 `why` 為空,切片為空,不帶現場。第二次才過時只帶第一次。兩次都沒過時帶兩次。吻合 S3。
  - 窗口 20、門檻 3:deque `maxlen` 正確。`unjudged` 不進分母。
  - 新舊互讀:舊總表沒有 `flaky` 鍵時視為 False。舊 judge 讀新 steps.json 會忽略 `evidence`。

### manifest 命中逐條判定
0 條 claims,沒有需要判的項目。散文外的 hunk 已自行看過,見上面的 F1、F2。

### 圖譜鏡頭固定席
- **guard-kill、lumos-cli-lifecycle、lumos-cli-read、design-loop、測試假綠形態的 INVARIANT**:不影響。
  - 這次只動 `android-e2e` 的判定輸出、總表和 `history` 子命令,沒碰 guard kill 的 rc 優先序與 JSON 純度、re-inject、search 的 superseded 濾網、處置閘。
  - 測試假綠形態那條要求「還原翻紅釘」配前置斷言。本次新測試對旗標、crash、judge 都有前置斷言(例如 `lc == [...]` 與檔案存在)。但 F1 顯示 S6 的測試資料形狀不真實,是同一族的缺口。
- **loop-convergence-recording、pitfalls-code-loop、reversibility-governance-ledger**(RISK):不影響。沒有改到收斂記帳、pitfalls 評分或可逆性帳。`docs/.governance-log.jsonl` 與 `docs/.canary-log.jsonl` 的改動是追加帳,沒有改舊行。
- **其餘只列名的節點**:不影響,理由同上。
- **殘留徽章與新增殘留段**:派工單沒有附,不適用。

### 角色鏡頭
有附卡但未見卡片內容,且這份 diff 是工具腳本,沒有前後端業務碼,略過。

總結:整份最高嚴重度為 major
