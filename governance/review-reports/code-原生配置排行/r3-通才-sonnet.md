severity: clean

我讀完整份 diff 和修補差異,沒找到會做出錯行為的問題。下面是已驗的主張、未驗範圍、manifest 判定、固定席和三問。

## 已驗的主張與證據

**G1 時間上限(原問題:預估與截止時間兩套算法)**
- 我從 `223de76` 抽出收集腳本內嵌的 Python,把裝置呼叫換成替身後直接跑 `native_phase`。
- 「驅動」欄是傳給 `driver` 的逾時秒數,「q」是傳給 `native_query` 的逾時秒數。

| 上限 / 第一段秒數 | 結果 | 傳進去的逾時 |
|---|---|---|
| 140 / 10 | 回 failed「時間不夠,不跑第二段(第一段 10 秒,這一步只剩 130 秒)」 | 沒呼叫任何驅動 |
| 1000 / 100 | ok | 驅動 780、780,q 885 |
| 3600 / 600 | ok | 驅動 1800、1800,q 1800 |

- 780 等於上限扣 `NATIVE_TAIL`(120)再扣已過秒數,885 等於再扣 `NATIVE_FINISH`(15),都不超過 `T_LONG`。預估和截止共用 `NATIVE_TAIL`,兩邊不再矛盾。
- 判斷式 `2*elapsed+NATIVE_TAIL > remaining` 展開後是 `3*elapsed+120 > b`,跟舊式 `elapsed+(2*elapsed+120) > budget` 等價。預估行為沒變,只是改成共用常數。
- 上限只在 `main` 讀一次。`inf`、`nan`、`0`、負數都走 `die`,且發生在 `preflight` 與動裝置之前。
- e2e 範本傳 `f"{T_LONG:g}"`。`LUMOS_E2E_LONG_TIMEOUT` 是 3600 時,收集腳本讀到 `3600`,結果合法。
- `NATIVE_MARGIN` 與 `deadline` 在 `223de76` 的 scripts、skills、knowledge 裡沒有殘留引用。

**G2 收錄製順序(原問題:先 pop 再收,收的那幾秒被中斷會漏)**
- 現在是 `state.get("rec")`,收完才 `state.pop`。收的過程中收到 `Terminated`,`state["rec"]` 還在,main 的 `cleanup` 會再收一次。
- `start_record` 失敗後 state 裡是 `(None, 原因, None)`,`abort_record` 對 `rec[2] is None` 回 True。這個路徑不會誤殺,也不會誤報殘留。
- `Terminated` 是 `Exception` 的子類,`except Terminated: raise` 排在 `except Exception` 前面,順序正確。`KeyboardInterrupt` 不被 `except Exception` 吃掉。

**G3 命名**
- `preflight` 的參數從 `native_on` 改成 `native`,不再跟模組函式 `native_on()` 同名。呼叫端 `preflight(st, native_on(st, scen))` 是位置參數,沒有被改名影響。
- 我 grep `223de76` 全 repo,沒有 `native_on=` 關鍵字呼叫。

**G4 SQL `having sum(size) != 0`**
- 淨留量為 0 的呼叫點對 `agg` 的 `sum`、`>= 1 MiB` 門檻和 `max(sym)` 都沒有貢獻。同一 `func/so/sys` 下 `sym` 相同,所以 `max(sym)` 不變。
- 負淨留量的呼叫點仍保留。
- `pick` 的 `caller` 選擇只在「所有候選都是 0 或負數」時才可能不同,對排行輸出沒有實際影響。
- 我沒有實機 `trace_processor`,這一條只靠推導,沒跑 SQL。未驗。

**tp_rows 抽出**
- `heap_counts` 的 `rows[1:]` 跟舊的 `splitlines()[1:]` 等價。
- `cycle_numbers` 的 `cells[0]=="cycle"` 跟舊的 `startswith('"cycle"')` 等價。`android-stability-cycle.sql` 的欄名是 `key`,表頭不會誤配。
- `native_query` 拿掉逾時特判後,逾時改走 `rc != 0` 分支,原因帶「逾時(N 秒)」,仍是 failed。

**G6 --json 清理**
- `stab_load` 已經用 `_esc_clean` 洗過所有字串,`_macrobench_native_retained` 再用 `_events_clean` 補清格式字元並截長。重複清理冪等,沒有副作用。
- 輸出的 sites 列若帶額外鍵,不會被清理。收集腳本不會寫這種鍵,所以沒有實際場景,不列 finding。

**其他呼叫端**
- e2e 的 `_e2e_judge_stability` 只讀 `threshold_*` 這幾個鍵,新增 `native_retained` 不影響判定。
- 步驟輸出存成檔,沒有尾端截斷,200 個 site 的大 JSON 不會被切壞。

## 未驗範圍
- 沒有實機、`trace_processor`、`adb`,SQL 與 heapprofd 設定的實際行為未驗。
- 測試檔另一席看,我沒讀 `test_lumos.py` 的新測試。
- 文件與 skill 的修補(docs、skill 的 patch)不在我拿到的正式程式差異內,未讀。

## pitfalls manifest(15 條)
- 收集腳本 `:263`、`:316` 的 `open(...).read()`:**誤報**。範本讀取是一行讀完的短命腳本,沒有長期持有。這是既有寫法,只是從 `heap_counts` 搬進 `tp_rows`。
- 收集腳本 `:489` 的 `time.sleep(SETTLE)`:**誤報**。它在 `fresh_launch` 裡只睡一次,不在迴圈裡,不會累積延遲。
- `android-stability-native.sql` 的 18、22、24、53、62、76、79、82、85、89、91、93 行共 12 條 SELECT / N+1:**誤報**。這些是同一支單次執行的 CTE 與 UNION 子查詢,不被迴圈呼叫。
- 圖譜的 `sql-sargable` 張力候選(`rtrim(path, replace(path,...))`):**誤報**。這是「去掉尾端非分隔字元」的字串技巧,不是 WHERE 欄位被函式包住,也沒有索引可廢。
- 沒有併發類題目。

## 圖譜固定席
- 固定席是 `lumos-cli-read`、`guard-kill`、`design-loop`、`測試假綠形態`、`lumos-cli-lifecycle`、`bound-tests-gate`、`pitfalls-code-loop` 等的 INVARIANT 或 RISK。這次 diff 在 `scripts/lumos` 只動 `macrobench` 的設定驗證、`native_retained` 讀取與列印,以及 vendored 清單。
- 沒有觸及 search 排除規則、guard kill 的 rc 與 JSON、設計審處置閘、還原翻紅釘、reinject 的 sentinel 外內容、bound-tests 閘。
- vendored 清單新增兩支範本:`android-stability-heapprofd.pbtxt`、`android-stability-native.sql`。它跟生命週期節點的安裝與更新有關。
- 這份 diff 看不出 `lumos update` 的安裝端是否真的會把這兩支發下去。這點歸其他席的文件與測試範圍,我不判定。
- 備援段與「這次新增的殘留」段沒有附上。

## 三問
1. **原問題的修復效果有何行為證據?** 時間上限、錄製順序、命名的修復都有程式碼與替身實跑證據(見上面 G1 到 G3)。SQL 省工只有推導證據(G4)。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立。
   - 正常路徑:沒設上限、有設上限且夠時間、上限太小,三條都實跑過。
   - 錯誤路徑:驅動逾時、查詢逾時、錄製開不成、`Terminated` 在收錄製時進來,我追過程式,都落在 failed 或 cleanup。
   - 相鄰路徑:`heap_counts`、`cycle_numbers` 共用 `tp_rows`,語意沒變。`preflight` 的呼叫端沒受影響。
3. **新發現的同一案例修前修後各是什麼結果?** 沒有新發現。

最高嚴重度 clean,blocking 0 條。
