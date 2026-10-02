severity: minor

**邊界與輸入鏡頭**

**R2B1** S16 接回續行後,摘要寫成單行字串的 RULE 不再被檢查
severity: minor
blocking: 否 — 只影響提醒的涵蓋面,不擋推送、不崩潰,目前本 repo 圖譜沒有這種寫法。
1. 舊版對 `fields["summary"]` 的字串逐行判。新版改走 `_ns_summary_logical`,而它靠 `_notelines_regions` 判區塊。那支函式把 `summary:` 鍵本行標成 other,只有後面的縮排行才算 summary。
2. 所以 `summary: RULE:甲 [since:...] [retire:人裁] [until:2027-01-01]` 這種單行寫法(帶引號也一樣),整條 RULE 被略過。
3. 重現:用 `_note_from_text` 建兩篇筆記,內容都是沒寫 `[confirmed:]` 的 RULE。區塊寫法(`summary: |-` 加縮排行)回 1 條提醒。單行寫法 `summary: RULE:甲 ...` 與 `summary: "RULE:甲 ..."` 都回 0 條。
4. 單行寫法的 `[被取代:]`、度量、FACT 在 S17 到 S19 也一樣被略過,因為它們走同一條 `_slot_summary_entries`。這是既有涵蓋面,但 S16 這次從有涵蓋變成沒涵蓋。
5. 建議:要嘛在 S16 對非區塊的單行 summary 另外補判,要嘛在計劃筆記註明只認區塊寫法。
引句:「        if not isinstance(n.fields.get("summary"), str):」

**其餘逐項實跑,未發現問題**
1. S17 引用解析:
   - `[[X#d2|別名]]`、`[[ X#d2 ]]`、`[[Live#d2]]`、`X.md#d2` 都正確查到決策並判翻案。
   - `[[X#標題]]` 當節點查,不誤判成決策。
   - `[[#d1]]`、`[[ ]]`、`[[]]`、`#d1`、`X#d0` 都有結果、不崩潰,`#D2` 大寫判成寫法認不出。
   - `[[#d1]]` 與 `[[X#d2#d1]]` 的錯誤訊息文字不精確,但行照列出,所以不標。
2. 作廢標記:`[status:SUPERSEDED]`、`[status: superseded ]`、`[ status:superseded]`、全形冒號都被認出。`_ns_superseded` 沒有自己 strip,但 `slot_parse` 已處理,實測無差。
3. S18 度量值與週數:
   - 前後空白、`近04週`、門檻 `00` 與 `03` 前導零都正確。
   - 週數 1 與 8 成立、0 與 9 列成寫法不合。
   - 全形 `＝`、大寫閘名、超大門檻(26 位數)都不崩潰。
   - 週界上,事件恰在 cutoff 計入(`>=`),since 恰等於 cutoff 照判,晚一天不判。
4. 治理帳時間:
   - 只有日期、帶毫秒的 Z、`+0800`、`+08:00`、`20260930`、週格式都可解析。
   - 單獨的 `2026-09-26Z` 不是合法 ISO,整筆略過,這是 Python 行為。
   - `9999-12-31T23:59:59` 與 `0001-01-01T00:00:00`(不帶時區)只跳那一筆,不崩潰。
   - 帶時區的 0001 年那筆會讓 `_gov_metric_events` 的最舊時間變成 0001 年。這個暖機判斷邏輯在這次 diff 之前就是這樣,不是這次引入,所以不標。
5. `_metric_gate_off` 去掉 try 後:
   - 設定為 `[1,2]`、`{bad`、`null`、非 UTF-8、`{"note_shape":"x"}`、`{"lint_new":[1]}` 都回 False,不丟例外。
   - `lint_new` 的鍵確認是 `mode`,`_metric_gate_off` 改讀 `["mode"]` 是對的。
   - 各閘的 `off` 設定(`note_shape`、`note_audit`、`note_reread`、`drift_check`、`node_home`)都判得出 True。
6. 輸出消毒:
   - 檔名帶 `\x1b[31m`、行內帶 `\x1b]0;…\x07` 與 C1 控制碼,都被換成空格,rel 路徑本身也有清。
   - 300 字上限是截尾端,路徑與行號在最前面,不會被切到(除非路徑本身超過 300 字)。
7. 測試:`-k slots_doctor` 27 個通過,`-k stale_rules` 8 個通過。

**圖譜鏡頭(LUMOS-IMPACT 固定席)**
1. `Systems/lumos-cli-read`(doctor 的 S16 到 S19)與 `Systems/存量漂移守衛`:
   - 不影響節點宣稱的行為或合約。
   - 兩篇的 WHY 行已同步成新行為:S17 只看作廢行、S18 先重驗寫法、S19 條數照軟段上限、印出前清控制字元、config 統一走 `_doctor_cfg_bytes`。
   - 實跑與這些說法一致。
   - 唯一落差就是 R2B1:S16 的說法沒提單行 summary 不在涵蓋內。
2. `Projects/筆記格子寫法與過期檢查_計劃`:
   - 格子表與 S13 的措辭,和程式相符。
   - S13 寫「`drift scan` 列已表態在已表態」,與 `_DRIFT_SCAN_KINDS` 加入 retire 一致。
   - 不影響合約。
3. `Issues/撤除條件檢查末輪遺留四項`:
   - 狀態從 done 退回 doing,tags 同步,與「推上主線後結案」的說法一致。
   - `_drift_retire_report` 改成先記帳再印,rc 判完就定,記帳或印出出錯都不改判定,與 Issue 修法一致。
   - 這些測試 `t_slots_retire_issue_followups` 都通過。
4. `skills/lumos-project-notes/commands/04-自檢與健康.md`:文件改動,只有說明,對行為沒有影響。
5. `_doctor_cfg_bytes` 抽出:
   - 取代三處複製的版本,語意相同。
   - `_metric_gate_off` 的 `lint-new` 分支仍直接讀磁碟上的 config,不經 `_doctor_cfg_bytes` 的捷徑防護。這不是這次引入,也沒有具體失敗場景,所以不標。

最高嚴重度 minor,blocking 0 條
