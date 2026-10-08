severity: minor

審查範圍:逐 hunk 讀完 `/tmp/code3-r1.patch` 全部 892 行。在 repo 副本跑了 `python3.14 scripts/test_lumos.py -k slots_`(170 項全過,0 失敗),並直接呼叫 S17、S18、S19 的函式讀本 repo 圖譜與自造病態輸入。沒有改任何檔。

## Findings

**U1** S17 會點名筆記裡「用散文提到 `[被取代:]`」的那一行,訊息卻是「寫法認不出」,使用者照著改會一頭霧水。
引句:「        for v in _slot_vals(sp, "被取代"):」
- 原因:`slot_parse` 把正文裡的 `[被取代:]` 或 `[被取代:…]` 也當成欄位,值是空字串。`_slot_vals` 沒濾掉空值,空值走到 `_slot_replacement_dead` 的最後一個分支,回「寫法認不出」。
- 最小重現:對本 repo 圖譜呼叫 `_doctor_replacement_lines(Env(docs/lumos-toolchain-knowledge))`,回傳 `['Systems/lumos-cli-read.md:14:[被取代:] 寫法認不出(要 [[節點]]、節點路徑#dN 或 無 <理由>)']`。第 14 行是這份 diff 自己新增的 S17 說明句,上線後本專案的 doctor 一跑 S17 就點名自己。
- 消費專案:只要有筆記在正文講解這個語法(例如寫 `[被取代:…]`),就會中。條數不多,不會一次噴幾百條。
- 修法:在 `_doctor_replacement_lines` 略過空值,或限定只判 `[status:superseded]` 的行。lint 端的 `_slot_replacement_err` 已用 `if val.get("被取代")` 略過空值,S17 跟它對齊就好。
- 加測試:補一條「散文提到 `[被取代:]` 不列」的紅綠測試。

severity: minor
blocking: 否 — 只是軟提醒、不計入問題數,不擋推送也不崩;但會讓本專案自己的 doctor 常駐一條誤報。

## 其他檢查(沒找到問題,依鏡頭列出)

1. **崩潰面**:S17、S18、S19 對 `[[]]`、指到不存在決策、壞值、本 repo 實際資料都沒有未接住的例外。`_metric_gate_off` 對讀設定的例外一律當「沒關」。
2. **噴量**:S19 最多列 20 條加總數。S17 只列有問題的。S18 沒有度量式 RULE 時直接早退,不讀治理帳。
3. **推送時撤除條件**:`_drift_retire_report` 搬到 try 外面,但它內部只有 `_gate_event_or_warn`,該函式不改判定。兜底記 `handle: None` 跟舊句檢查(m1)的先例一致;repo 內沒有讀這個欄位做算術的地方。
4. **`drift ack --kind retire` 新擋**:擋下訊息講得清楚,第一行號照收,測試已覆蓋。`drift fix` 不讀 `_DRIFT_SCAN_KINDS`,所以不受新增 retire 影響。
5. **scan 新增 retire 種類**:`--json` 多了 `kind: retire` 的項目,下游沒有按種類寫死的消費者。
6. **回滾**:還原提交後,Issue 檔回到 open 並帶回 REVISIT 行,`_DRIFT_SCAN_KINDS` 恢復排除 retire。沒有遺留狀態,治理帳只是多了幾筆無害的紀錄。
7. **⚠ 未處理的小缺口(不標嚴重度)**:`[被取代:[[節點#d2]]]` 這種「連結加決策錨點」的寫法,lint 接受,S17 只查節點、不查決策是否翻案,所以漏報、不誤報。

## 圖譜鏡頭

這份 diff 尾端沒有附 `LUMOS-IMPACT` 固定席筆記段,所以我自己判了它改動到的節點,都不影響:

- `Systems/存量漂移守衛`:新增 scan 兜底與推送帳修正,跟它既有的合約不衝突。它的 WHY 行已同步更新,且綁了 `[test:t_slots_doctor_reminders]` 與 `[test:t_slots_retire_issue_followups]` 兩支測試。
- `Systems/lumos-cli-read`:新增的 S17、S18、S19 在 doctor 裡都是軟提醒,不計入問題數、不寫治理帳。這跟同節點 S16 那條 WHY 的行為一致,沒有破壞。
- `Issues/撤除條件檢查末輪遺留四項`:四項都在 diff 裡有對應修法和測試,收成 done 合理。
- `Projects/筆記格子寫法與過期檢查_計劃`:第 3 步進度只是補述,沒有合約變動。

最高嚴重度 minor,blocking 0 條
