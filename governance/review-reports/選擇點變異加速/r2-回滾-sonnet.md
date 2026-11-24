severity: major

## 逐節走查(收拾殘局視角)

先講結論:設計裡寫治理帳或影響推送閘判定的入口共 7 個。查完程式後,其中 3 個「判錯了怎麼辦」的答案跟 spec 寫的不符或沒寫清楚。

| 入口 | 判錯時的收回路徑 | 查證結果 |
|---|---|---|
| choice-kill 事件與 `judged` | `--recheck`、`merge_ver` | 見 finding 1、2、3、4 |
| `merge_ver` 欄 | 升版讓舊帳過期 | 推送閘會認,前提是用新版工具;見 finding 1、3 |
| run 事件三個計數 | 只供統計 | 不進任何判定,無風險 |
| 弱證據升級 | 靠 `merge_ver` 作廢 | 同 `merge_ver`;升級後的 killed 與一般 killed 在帳上不分,只能靠 `judged=merged` 辨認 |
| `--recheck` 覆蓋 | 追加新紀錄 | 見 finding 2、7 |
| `LUMOS_CHOICE_NO_MERGE` | 全域關 | 只影響 `choice-kill` 產生新帳,見 finding 5 |
| 放行檔優先 | 已放行不重跑 | spec 已寫明並放行,不重複報 |

逐項查證:

- **`merge_ver` 作廢能不能讓推送閘把舊的錯誤殺掉判成過期:能,前提是版本升在新版工具上。** `_choice_disposition` 是推送前、`code-loop pass` 預判、`choice-kill` 挑行(`_choice_kill_pick`)、`choice-points`(`_choice_ledger_status`)共用的唯一判定函式。spec 把規則加在這一支,四條路徑會一起生效。
  - file: `scripts/lumos:78074`(`_choice_disposition`)
  - file: `scripts/lumos:78347`(`_choice_kill_pick` 的呼叫端)
  - file: `scripts/lumos:78782`(`_choice_push_judge` 的呼叫端)
  - file: `scripts/lumos:77897`(`_choice_ledger_status` 的呼叫端)
- **舊版工具讀帶 `judged`、`merge_ver` 的新帳:不會出錯,但不認它們。** `_gov_event_types_ok` 只檢查 `_GOV_FIELD_TYPES` 裡登記過的欄位,沒登記的欄位直接略過。所以 spec 說的「舊版讀到不認得的欄位照略過」成立,舊版會把合併判定當有效處置。
  - file: `scripts/lumos:18434`
- **`LUMOS_CHOICE_NO_MERGE` 在推送前自動跑或 `code-loop pass` 預判的路徑上有沒有作用:沒有作用,而且本來就不該有。** 這兩條路徑只讀帳,不跑 `choice-kill`。`pass` 預判甚至讀工作目錄的帳,沒有任何程式自動呼叫 `choice-kill`。我用 grep 查過 `scripts/lumos`、`skills`、`hooks`,沒有程式化啟動。
  - file: `scripts/lumos:78733`

## 發現

### 1. 回退節「先升版本讓它們過期再還原」在還原之後失效
severity: major
blocking: 是

spec 回退節說:「還原後的舊版不認 `judged` 與 `merge_ver`……所以還原前先照上一點把可疑的合併判定 `--recheck --no-merge` 重跑一遍,或先升版本讓它們過期再還原。」

「升版本」這條路是錯的。`merge_ver` 的比較只存在於新版的 `_choice_disposition`。還原功能提交之後,工具裡沒有這個比較,常數與比較一起消失。舊版只看 `verdict`,帳上那筆 `judged=merged` 的錯誤 killed,又會被當成有效處置。

例子:
1. 發現合併讀法有錯,把 `_CHOICE_MERGE_VER` 改成 2,舊 killed 暫時全部過期。
2. 接著還原功能提交。
3. 舊版工具讀同一份帳,`merge_ver` 欄被略過,錯誤的 killed 判定又全部生效,推送閘照樣放行。
4. 整個過程中沒有任何一筆新紀錄,所以升版本沒有留下任何持久的修正。

只有 `--recheck --no-merge` 先重跑完並追加新紀錄,還原後才安全。按字面實作,操作者會多一條不可靠的路徑,並以為它有效。

引句:「或先升版本讓它們過期再還原。」
file: `scripts/lumos:78074`(`_choice_disposition` 現況沒有版本欄,過期判定完全靠新工具)
file: `scripts/lumos:18434`(舊版 `_GOV_FIELD_TYPES` 不認 `merge_ver`)

### 2. `--recheck` 沒定義「哪些行這次不用再重跑」,批次重判永遠不前進
severity: major
blocking: 是

spec 寫的是:「單獨用時重跑範圍裡所有有紀錄的行——連已有有效處置的 killed 與「守的測試沒變」帶過去的 survived 都重跑,新紀錄追加在後、以最新一筆為準……`--max-mutants`、`--max-seconds` 照樣截。」

現況 `_choice_kill_pick` 靠「已處置就跳過」讓多次呼叫逐步前進。`--max-mutants` 預設 30。`--recheck` 把「有紀錄」整個當成要重跑,重跑完的行仍然「有紀錄」。沒有任何標記區分「這次 recheck 已經重判過」。

例子:範圍內 197 行有紀錄。第一次 `--recheck` 跑前 30 行,追加 30 筆新紀錄。第二次 `--recheck` 的條件還是「有紀錄」,挑的是同一批前 30 行,永遠到不了第 31 行。

按字面實作,spec 寫的收回路徑「`--recheck` 逐行重判」在整批規模下做不完。唯一可行的是逐行帶 `--only`,197 次呼叫。S13 只測了單行與「重跑範圍內所有行」,沒測分批前進。

另外「以最新一筆為準」只是檔內順序(finding 7),不是時間順序。

引句:「單獨用時重跑範圍裡所有有紀錄的行——連已有有效處置的 killed 與」
file: `scripts/lumos:78334`(`_choice_kill_pick`:靠 `done` 與 `carried` 前進)
file: `scripts/lumos:78012`(`_CHOICE_MAX_MUTANTS = 30`)

### 3. 過期規則沒說套用到哪些 verdict,字面讀會讓 survived 行無上限地擋推送
severity: minor
blocking: 否

spec 寫:「同鍵最新一筆 `judged` 是 merged、而 `merge_ver` 小於目前的 `_CHOICE_MERGE_VER` → 算過期」,沒限定 verdict;S12 只測 killed。

若在 `_choice_disposition` 開頭一律套用,survived 與 no_result 的 merged 紀錄也會變成 `"stale"`:
- 對推送閘:survived 原本只擋回報上限抽中的那批(`_choice_cap_pick`),變成 `"過期"` 後不受上限,全部擋。
- 對 `choice-kill` 挑行:survived 原本「守的測試沒變就帶過去不重跑」,變成每行都重跑。

加上 finding 1 的回收成本:升版本之後,所有 merged 行都要重跑才能推;重跑若為了保險帶 `--no-merge`,就退回現在 15–18 小時的慢路徑。這些 spec 沒寫清楚是刻意還是漏了。⚠ 交編排者決定:過期只對 killed,還是對所有 merged。

引句:「同鍵最新一筆 `judged` 是 merged、而 `merge_ver` 小於目前的 `_CHOICE_MERGE_VER` → 算過期」
file: `scripts/lumos:78782`(`_choice_push_judge` 的 survived 走上限抽樣,stale 走 `"過期"` 無上限)

### 4. 現行「過期」的說明文字與指令會誤導 merge_ver 過期的行
severity: minor
blocking: 否

現行 `"stale"` 的語意固定是「殺掉它的測試已沒有條款綁」。對應的輸出與手冊:
- `choice-points` 印「過期(殺掉它的測試已沒有條款綁)」。
- 手冊 `06-代碼審與推送.md` 寫「過期(殺掉它的測試沒有條款綁了)→ 重綁或重跑」。

spec 只說推送閘與 `_choice_kill_pick` 照既有過期處理,沒更新這兩處。`merge_ver` 過期的行會被指示去「重綁」,其實綁定沒問題,該做的只是重跑。〈落點〉列了要改手冊,但沒列要把過期分成兩種原因。

引句:「擋、`_choice_kill_pick` 照」
file: `scripts/lumos:77905`(`out[k]` 的過期字串)

### 5. `LUMOS_CHOICE_NO_MERGE` 的取值語意沒定,而且只管得到自己環境裡跑的 `choice-kill`
severity: minor
blocking: 否

兩個問題:
1. spec 只寫 `LUMOS_CHOICE_NO_MERGE=1`,沒定 `0`、`true`、空字串怎麼算。同檔其他旗標讀法不一(例 `LUMOS_KILL_TIMEOUT_FLOOR` 是 `float()`,`LUMOS_CHOICE_SINCE` 是 strip 後比對)。出事時的緊急開關,取值含糊會讓操作者以為關了其實沒關,或相反。
2. 開關只在 `choice-kill` 程序環境裡有效。推送前、`pass` 預判印出的提示是不帶旗標的字串。AI 會談照抄提示執行,環境沒傳到的子程序、已經開著的會談都不會帶上變數。spec 說「出事時一次關掉所有呼叫」,實際是「每個會談自己匯出」。

這個開關對已寫進帳的合併判定毫無作用,spec 回退節有講,屬正確。

引句:「環境變數 `LUMOS_CHOICE_NO_MERGE=1` 等同 `--no-merge`,出事時一次關掉所有呼叫」
file: `scripts/lumos:78845`(推送前提示的指令字串不帶任何旗標或環境)

### 6. `merge_ver` 比較在多數讀帳路徑沒有型別防線
severity: minor
blocking: 否

spec 說新欄位要登記進 `_GOV_FIELD_TYPES`、整數用 `type(x) is int`。但只有推送路徑(`_choice_push_ledger`)會經 `_gov_event_types_ok` 篩事件。`_choice_ledger_index`、`_gov_vc_gate_events` 只檢查 `file`、`fp`、`verdict` 是字串。

手改或壞掉的紀錄帶 `merge_ver: "x"` 或 `null`,`_choice_disposition` 裡的 `<` 比較會丟 `TypeError`。範圍涵蓋 `choice-kill`、`choice-points` 兩條。推送路徑反而是把整筆事件丟掉,退回同鍵上一筆,可能把更早的 killed 翻成最新。spec 沒要求比較時型別安全。

引句:「新欄位照既有慣例登記進 `_GOV_FIELD_TYPES`(整數用 `type(x) is int` 排除 bool)。」
file: `scripts/lumos:78061`(`_choice_ledger_index` 只驗三個字串欄)

### 7. 「最新一筆」是檔內行序,不是時間順序
severity: minor
blocking: 否

`_choice_ledger_index` 與 `_gov_rows_at` 都用檔內順序,不看 `ts`。`.gitattributes` 沒有 `merge=union`。

⚠ 例子(推測,未實測):分支 A 對某行 `--recheck` 產生 single 紀錄並提交。同一行(同鍵 `fp`)在別的分支留下舊的 merged killed,合併後排在後面。檔內順序讓舊的反而成了「最新」。這是既有設計。但 `--recheck` 的合約是「新紀錄一定蓋過舊的」,spec 沒說明這個前提在合併帳檔時是否仍成立。

引句:「新紀錄追加在後、以最新一筆為準」
file: `scripts/lumos:65601`(`_gov_rows_at` 以行序回傳)

### 其餘節
- 白話、WHY、PRIOR-ART、RETIRE-IF、REVISIT、舊否決比對、實測、用詞:已讀,無 finding。
- 〈做法〉1 到 5(組指令、讀結果檔、合併基準、判定、一致範圍):這輪鏡頭是回滾,偏向守衛面判錯。已讀,無額外 finding。
- 〈做法〉6 的「`--no-merge` 時輸出與帳跟現在相同」:已讀,無 finding。
- 驗收條款 S1 到 S19:S12、S13、S14 對應上面 finding 2、3、5,未涵蓋。其餘已讀,無 finding。
- 〈不做〉、〈落點〉、〈預期效益〉、〈人裁紀錄〉、〈審計修正紀錄〉:已讀,無 finding。

## 同族掃描:判錯後怎麼收回

- **killed 判定的收回(finding 1、2、3、7):** 只有「新版工具下升 `merge_ver` 或逐行 `--recheck`」這一族。字面上沒有跨工具版本的路徑。
- **開關(finding 5):** 全域關只產生新帳,無法收回舊帳。
- **帳讀取的穩健性(finding 6、7):** 型別與順序前提都沒寫進 spec。
- **同族還有一處我沒找到:** 回報上限與 `merge_ver` 過期的交互(finding 3)。其他入口(run 事件計數、`gov` 讀欄)純統計,不影響判定。

## 風險類

- 守衛面:finding 1、2、3、7。
- 回滾:finding 1、2。
- 相容(新帳在舊版工具):`_gov_event_types_ok` 只驗登記欄位,舊版略過新欄,spec 寫的成立,無額外隱患。
- 資源:無,本鏡頭沒有新增隱患。
- 效能:無,本鏡頭沒有新增隱患。

發現共 7 條
