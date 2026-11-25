severity: minor

審稿範圍:對照 `scripts/lumos` 現況逐節讀完這份投稿。兩個固定席的判斷與實務隱患逐類答覆放在最後。

## 逐節

- 〈白話〉、〈實測(來源)〉、〈用詞〉、〈預期效益〉、〈不做〉、〈回退〉、〈依據來源〉、〈人裁紀錄〉:已讀,無 finding。
- 〈做法〉1 量單支基準:見 finding 1。
- 〈做法〉2 半開:已讀,無 finding。我用下面幾個極端輸入逐一推演,結果都能自洽。
  - 剛好 10 個後續壞法:`cool` 數到 10 時沒有第 11 個,不試探。
  - 跳開時已是最後一個壞法:同上,不試探。
  - 多個平台組:`cool`、`reopen`、`trips` 都以平台為鍵,各自獨立。
  - 試探碰到還原失敗:`_kill_merge_screen` 回 `break`,迭代器 `return`,照舊收手。
  - 中斷訊號落在試探中:`_kill_merge_screen` 在呼叫斷路器之前就先丟 `_KillHalt`,所以不會動到斷路器的任何狀態。
- 〈做法〉3 拒收代碼:見 finding 2。
- 〈做法〉4 壞法那筆記原因:已讀,無 finding。
  - `finish` 在 `_ChoiceKillRun` 裡一個壞法判完就寫,`whys` 在快篩當下就已寫入,所以時序站得住。
  - 舊帳缺 `merge_why`、`merge_reopen` 時,`gov` 投影用 `d.get(...) or {}`,讀成空字典做得到。
- 〈驗收條款〉與〈預期值表〉:已讀,無 finding。S2 的第 11 個、第 22 個與 `cool` 的計數方式一致。
- 〈RETIRE-IF〉:見 finding 3。

## Findings

1. 量基準只剩一個樣本決定要不要收手(〈做法〉1)
   - 引句:「平均:`measured` 少於 2 支時用單價 `_CHOICE_MERGE_UNIT_SECS`;2 支以上時用 `measured[1:]` 的平均。」
   - 輸入:剛好量到 2 支,`measured[1:]` 只有第二支一個值。
   - 發生什麼:若第二支因雜訊偏慢(例如 25 秒,其餘 4 秒),估算變成 25 × 169 × 1.5 > 剩下時限,直接放棄合併。
   - 這是 11-25 那個缺陷換成第二支再犯一次。
   - 計劃〈不選〉說「中位數與去掉第一支的平均相同」,但在 2 個樣本時兩者都等於單一點。
   - 因為 `_choice_merge_shape` 只收單一 Gradle 任務,冷編譯多半只落在第一支,所以我評為低嚴重度。
   - 佐證:file: `scripts/lumos:29030`,現行 `_kill_merge_singles` 的 `avg` 與 `left` 算式。
severity: minor
   - blocking: 否。放棄合併後仍會逐支跑,只是慢,不影響判定正確性。

2. 「結果檔讀不出來」只有部分路徑會帶代碼,且鍵數寫錯(〈做法〉3)
   - 引句:「讀檔的 OSError → `結果檔讀不出來(OSError)`;`_secev_junit_facts` 回的代碼 → `結果檔讀不出來(<代碼>)`。」
   - 輸入:結果資料夾的 `glob` 或 `stat` 丟 `OSError`。
   - 發生什麼:這條路徑在 `_choice_merge_facts` 的第一個 `try`,現況直接回 `None, "結果檔讀不出來"`,規格沒提到它。
     - 逐一對照後,「讀檔的 OSError」只涵蓋 `read_bytes` 那一處(現況該處內部記成 `"unreadable"`)。
     - `glob`、`stat` 那一處仍是無代碼的舊字樣,正是這份計劃要消除的「分不出來」。
   - 另一處:鍵數寫「最多 9 種」不對。
     - 能被斷路器計入、因此進 `merge_unclean` 的字串共 13 種:逾時、被系統收掉、找不到 JUnit 結果檔、超過大小上限,再加「讀不出來」9 種。
     - 這 9 種是 `report_unparseable`、`report_too_deep`、`report_malformed`、`report_duplicate_identity`、`zero_cases`、`suite_error`、`count_mismatch`、`evidence_too_large` 共 8 個代碼加 `OSError`。
     - 若實作者照「9 種」寫鍵數上限斷言,會誤紅。
   - 佐證:file: `scripts/lumos:28838`,`_choice_merge_facts` 的兩處 `OSError`。
   - 佐證:file: `scripts/test_quality.py:258`,`JUnitRejected` 在該檔共 7 種代碼。加上 `scripts/lumos:9046` 的 `_secev_junit_facts` 另回 `evidence_too_large`,合起來 8 個。
severity: minor
   - blocking: 否。只影響診斷資訊與文字數字,不影響判定。

3. RETIRE-IF ① 的度量量到的是「跑完時還在跳開」,不是「恢復後又跳開」(〈RETIRE-IF〉)
   - 引句:「其中 `merge_trips`(跳開次數)大於 `merge_reopen` 的超過一半」
   - 輸入:一次呼叫跳開 1 次、試探恢復 1 次,之後都乾淨;另一次呼叫跳開 2 次、恢復 1 次,結尾仍停在跳開。
   - 發生什麼:`trips` 恆大於等於 `reopen`,`trips > reopen` 只表示收尾時還停在跳開狀態。
     - 一次呼叫裡「跳開、恢復、再跳開、恢復」會得到 `trips = reopen = 2`,度量看不出它反覆跳開。
     - 這條撤除條件對它判不出來,對「結尾剛好停在跳開」的正常呼叫卻會誤計。
   - 佐證:對照〈做法〉2 的計數規則:跳開時 `trips` 加一,恢復時 `reopen` 加一。
severity: minor
   - blocking: 否。只影響日後回頭判斷的準確度。

## 固定席:`Systems/guard-kill`

- ★INVARIANT★ rc 優先序(`t_guard_kill_rc_precedence`):不影響。
  - 半開只改變誰被快篩判存活,不新增 verdict 種類。
  - 試探中還原失敗仍走既有的 `break` 加 `error` 列,rc2 路徑不變。
  - 試探通過交出的列仍是 `survived`,可能帶 `_mtime_unsure` 弱證據,與既有行為相同。
- ★INVARIANT★ `--json` 成功跑完時 stdout 恰一行 JSON(`t_guard_kill_json_purity`):不影響。
  - `merge` 參數只有 `choice-kill` 會傳,而且 `choice-kill` 對 `cmd_guard_kill` 用 `contextlib.redirect_stdout` 吞掉 stdout。
  - 規格只寫「印一行」恢復訊息,沒寫明走 stderr,實作應照現有跳開那行走 `sys.stderr`;現況斷路器的跳開行就是 stderr。

## 實務隱患(此功能碰到的風險類)

- 金流、對外送出:無。只在本機跑測試,不連網。
- 不可逆:無。治理帳只追加欄位,舊讀者缺欄會讀成空字典,`_GOV_FIELD_TYPES` 加三個字典欄位也不會讓舊行被跳過。
- 併發與交易:無新增。一次呼叫一棵工作樹、一條執行緒;訊號落在試探中的路徑已逐一推演過,沒有洞。
- 資源耗盡:無實質問題。
  - 持續沒跑乾淨時,每 10 個壞法多付一次試探,上限是既有的快篩 `cap`。
  - 試探結果非乾淨時,該壞法本來就會落到逐支,所以試探成本是額外增量,不是翻倍。
- 輸入邊界:
  - 基準少於 2 支:不做時限判斷。這會多量一支,最壞多花一支基準的時間,規格已在〈代價〉承認。
  - 剩下時限為 0 或負:`cap` 取 `max(remaining, 1.0)`,第一支被截斷時照舊回 False,與 S1 第三案一致。
  - `merge_why` 字串很長或帶數字:原因字串只來自固定代碼或「N 支對不到…」,長度有限。
  - 拒收代碼不在清單內:`JUnitRejected.code` 只有那 7 種,加上 `evidence_too_large` 共 8 種,不會出現清單外的值。

最嚴重 severity 為 minor,共 3 條 finding,blocking 共 0 條。
