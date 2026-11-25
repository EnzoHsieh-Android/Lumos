severity: major

## 一、先答固定席節點

- `Systems/guard-kill` 的 rc 優先序合約:不影響。
  - 先紅順序只改 `_kill_merge_iter` 交出配方的順序。
  - rc 仍由 `cmd_guard_kill` 收尾那段,從 `results` 的 verdict 集合算(file: `scripts/lumos:28609`)。
  - `choice-kill` 把 `cmd_guard_kill` 的 stdout 收起來、不看它的 rc(file: `scripts/lumos:79000`),所以這個合約碰不到。
- `Systems/guard-kill` 的 `--json` 純度合約:不影響。
  - 新增的時限提示與斷路器行都走標準錯誤。
  - 合併只在 `choice-kill` 路徑啟用,`guard kill --json` 不傳 `merge`。
- `Systems/規格閘`:不影響判定。
  - 只新增 run 事件欄位。
  - 舊版讀新帳的結論見 F4 之後的「五問」。

## 二、逐節

### 白話、WHY 第 1 條、做法 1(先跑紅的)

severity: major
blocking: 是(判定與 `--no-merge` 可能不同,而 spec 明文宣稱相同)

- spec 宣稱:判定與 `--no-merge` 相同,只有「殺掉它的測試」可能不同。
- 這個宣稱對「逾時」不成立。
- 引句:「殺掉它的測試可能跟 `--no-merge` 記的不是同一支(判定相同)」
- 重現輸入:
  - 守的測試排序是 a、b、c;合併快篩有失敗,名單只有 c。
  - 壞法讓 c 單支強殺掉。
  - a 在壞法下單支跑得比逾時上限慢,但合併呼叫裡沒紅。a 不在名單裡。
  - 逾時上限是 `max(b_elapsed*5, floor)`(file: `scripts/lumos:28528`),只算單支。
  - 合併快篩的上限是 `max(m_el*5, floor)`(file: `scripts/lumos:28819`),大得多,所以 a 在合併裡可以不超時。
- `--no-merge` 的結果:
  - a 先跑,得 `timed_out_weak`。這個鍵在 `_CHOICE_STOP_ON` 裡(file: `scripts/lumos:78458`),同組停,c 被略過。
  - `_choice_kill_judge` 判 `no_result`「測試掛住」(file: `scripts/lumos:78668`)。
  - 同一個壞法不會記成殺掉。
- 本案的結果:
  - 先跑 c,強殺掉,同組停,判 `killed`。
- 兩邊差在 `killed` 對 `no_result`。
  - rc 不同:一個走 `no_result` 的 rc 2,一個算已處置。
  - 帳上的 `verdict` 也不同。
- 判定規則沒變,但「停止集合裡有三種鍵,先遇到誰就停在誰」使結果依賴順序。
  - 只有 `killed` 與 `timed_out_weak` 這對會造成判定不同。
  - `compile_error` 是壞法編不過,與測試順序無關。
- 第二個後果:
  - 「S5/S2 判定與 `--no-merge` 相同」的測試只在沒有逾時的輸入上成立。
  - 驗收條款沒有任何一案覆蓋「排在前面的單支逾時、名單裡的單支殺掉」。
- 修法方向(只描述結論):二選一。
  - 在 spec 明寫「逾時鍵先後會改判」並把它列入〈實務隱患〉與 RETIRE-IF。
  - 或讓先紅順序不跨過會逾時的測試。
- 另外補一案:S1 加「前面的單支逾時」。

### 實務隱患(「推送閘不讀它判放行」)

severity: major
blocking: 是(spec 用一句不實的事實把風險排除)

- 引句:「判定相同;`killing_test` 欄只做紀錄,推送閘不讀它判放行。」
- 這句不實。
  - `_choice_disposition` 把 `verdict == killed` 且 `killing_test` 在 `bound` 裡的行判成「有效處置」。
  - `killing_test` 不在 `bound` 裡就判 `stale`(file: `scripts/lumos:78528`)。
  - `_choice_dispositions`(file: `scripts/lumos:78338`)與 `bound` 比對的是帳上最新一筆的 `killing_test`。
- 重現:
  - 壞法的先紅順序第一支是 c(綁在計劃 P2),`--no-merge` 的原順序第一支是 a(綁在計劃 P1)。
  - 帳上記 c。之後 P2 的條款改綁或拿掉 c。
  - 這一行變 `stale`,推送閘要求重跑。
  - `--no-merge` 記的是 a,同一動作下仍是有效處置。
- 影響:
  - 同一個壞法的處置壽命、需要重跑的時機,會依合併快篩有沒有開而不同。
  - 〈回退〉「帳上的紀錄判定不受影響」也因此不成立:回退前記的 killer 與回退後不同,`stale` 的時機也不同。
- 這不是安全洞,只是 spec 的事實錯誤加一個沒講的行為差。

### 做法 2(一個壞法也合併)

已讀,無 finding。

- 拿掉 `mg.n_mutants < 2` 只影響 `_kill_merge_ready`(file: `scripts/lumos:28903`)。
- `n_mutants` 沒有別的讀點。
  - file: `scripts/lumos:78991` 是唯一建構點。
  - 測試用位置參數建構,簽名保留就相容。
- 被殺的單一壞法多付量齊基準的代價,spec 已寫明並接受。

### 做法 3(時限提示)

severity: minor
blocking: 否(提示照做後仍可能不合併,但會再印一次,不會誤判)

- 引句:「要合併請帶 --max-seconds <M 無條件進位到百>」
- 問題:提示給的 M 是「支數 × 10 × 1.5」進位到百,但閘門比的是「剩下的時限」,不是「帶進去的時限」。
- 時限的起點在 `cmd_choice_kill` 取 blobs 之前(file: `scripts/lumos:79067`)。
  - 之後還要建工作樹、跑單支基準、(多平台時)跑完前面的平台組,才到這個平台組的閘。
- 重現:
  - 169 支,M = 2535,提示 2600。
  - 使用者帶 2600。到閘時若前置已用掉超過 65 秒,剩下的就 < 2535,仍不合併,又印一行提示。
  - S7 的測試只驗 1800 與 3000 兩點,測不到這個縫。
- 提示需要加前置開銷的餘量,或在文字裡講明「還要加準備時間」。

### 做法 4(沒跑乾淨的原因)

severity: major
blocking: 是(欄位值與設計宣稱的用途不符:「原因查不出」會再發生)

- 引句:「合併基準不乾淨另記 run 事件的 `merge_base_why`(字串,`_CHOICE_MERGE_BASE_WHY` 那幾種;沒有就空字串)。」
- `_CHOICE_MERGE_BASE_WHY` 只有五個鍵:逾時、`rc 不是 0`、有失敗、編不過、被系統收掉(file: `scripts/lumos:28735`)。
- 合併基準的其他不乾淨原因,依 spec 的寫法都會記成空字串。
  - 「找不到 JUnit 結果檔」(rc 非 0 且不是編不過,file: `scripts/lumos:28863`)。
  - 「結果檔讀不出來」與「結果檔超過大小上限」(file: `scripts/lumos:28830`、`28838`)。
  - 「N 支對不到結果檔裡的名字」(file: `scripts/lumos:28871`)。
- `_kill_merge_base` 現在對這些原因是用 `.get(why, why)` 印出原字串(file: `scripts/lumos:28965`),spec 反而丟掉了。
- 另有兩條路也退回逐支,但完全不記原因:
  - `_kill_merge_singles` 回 False(量到一半時限不夠)。
  - 合併道少於 2 支(file: `scripts/lumos:28953`)。
- 結果:
  - `merge_base_why == ""` 同時代表「乾淨」「基準沒量成」「基準因未列原因失敗」。
  - 這正是 11-25 02:54 想避免的情形:帳上沒有原因,事後只能猜。
- 多平台時 `merge_base_why` 是單一字串,spec 沒說先後兩組的值怎麼合併。
  - 前一組失敗、後一組乾淨,是覆蓋成空字串,還是保留?S4 沒有覆蓋這個輸入。

### 做法 4(`unclean` 計數)

severity: minor
blocking: 否(計數本身與斷路器一致,只是跨平台沒分開)

- `unclean` 鍵只用原因字串、不分平台,但斷路器的 `streak` 是分平台的(file: `scripts/lumos:28885`)。
- 兩個平台各 3 次逾時,每個平台都沒跳開,但 `merge_unclean` 記 {逾時: 6}。
  - 讀帳的人看到 6 次會以為跳開過,對不上 `merge_tripped=false`。
- 單人、單平台為主的情況影響小;只要 REVISIT 讀這個欄位時知道它是跨平台合計。

### 預期效益與驗收條款

已讀,無 finding。

- S1 的三案符合 `_choice_kill_judge` 現行邏輯。
- S3 與 S7 的數字:169 × 15 = 2535,進位 2600,算術正確。

## 三、五問

- 新舊互讀:無問題。
  - 新欄位 `merge_unclean`、`merge_base_why` 對舊版 lumos 是未登記欄位,`_gov_event_types_ok` 只檢查表裡登記的鍵(file: `scripts/lumos:18475`),不會跳過整行。
  - 新版讀舊帳:缺欄位時 `d.get` 回 None,不影響。
  - 新增型別登記時,要確認寫端不會寫 null(表上的註解已警告過這點,file: `scripts/lumos:18433`)。
- 寫一半(中斷):無問題。
  - 重排不改寫帳時機;`finish` 仍是逐壞法判完才記。
  - 中斷時 run 事件仍會寫,`merge_unclean` 是已發生的計數。
- 衍生資料:見 F4。run 事件統計 `judged` 不受重排影響。
- 時間:見 F3。另外 `_kill_merge_singles` 量基準的時間在單一壞法也會花,已列為代價。
- 不可逆:無。工作樹是暫時的,帳只追加。

最嚴重 severity:major,blocking 共 3 條(F1 逾時改判、F2 `killing_test` 被推送閘讀取、F4 `merge_base_why` 空字串歧義)。
