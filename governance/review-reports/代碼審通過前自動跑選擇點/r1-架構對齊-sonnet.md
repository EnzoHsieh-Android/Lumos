severity: major

我只讀了被審材料與 `scripts/lumos`,沒有跑任何東西。repo 裡的 `_choice_push_round` 目前只有 `(env, rr, git_range, push=None)` 四個參數,計劃要加的三個新參數還不存在。

**1. 分層與依賴方向**

先看新機制放的位置。接點在 `_codeloop_pass_gate`,排在 `_codeloop_pass_mech` 之後、`_codeloop_pass_verify` 之前:`_codeloop_pass_mech` 在 `scripts/lumos:73375`,`_codeloop_pass_gate` 在 `scripts/lumos:73396`。這跟鄰居一致。

接下來是判定本身,重用 `_choice_push_round`(`scripts/lumos:78838`),方向也對。鄰居 `_codeloop_pass_mech` 重用的是 `_codeloop_guard_verdict` 的 `mech_only` 收集模式(`scripts/lumos:79621`、`scripts/lumos:73380`)。兩者都是「加參數重用同一支判定」,這點一致。

問題在 pass 裡直呼 `cmd_choice_kill`。`_codeloop_pass_mech` 與 `_codeloop_pass_verify` 都只判斷、不跑測試、不寫配方結果。在行程內呼叫其他 `cmd_*` 的地方有兩類:
- `cmd_guard_kill` 被 `_kill_add_try`(`scripts/lumos:27683`)與 situation-rule(`scripts/lumos:76650`)呼叫,這兩處都是指令層呼叫指令層。
- `_codeloop_default_range`(`scripts/lumos:79505`)被 pass 與 check 共用,但它只算範圍。

沒有任何「記通過的 pass 或閘」直呼會跑測試、寫帳的 `cmd_*` 的先例。`scripts/lumos:76110` 以外也找不到。

反面證據在 `scripts/lumos:73405` 起那段註解:「掛在『擋』的路徑(check)不掛『記錄』的路徑(pass)——r1 架構席抓的」。這是專案原本把會跑測試的閘從 pass 擋在外面的明文方針。`_codeloop_pass_mech` 已經把機械兩道放進 pass,但那兩道不跑測試。

新的一道讓 pass 從「寫入口」變成會跑 Gradle、最長 600 秒以上、會寫 choice-kill 帳的流程,這是跨層直呼。此外,pass 原本沒有 `Env`(只有 repo_root),計劃要在 pass 裡臨時建 `Env(_vault_in(repo_root))`。`Env(` 的其他建構點(`scripts/lumos:73510`、`scripts/lumos:33286` 等)都在指令入口或 guard 判定內,pass 本身沒有。

file: `scripts/lumos:73375`、`scripts/lumos:73396`、`scripts/lumos:27683`、`scripts/lumos:76650`、`scripts/lumos:73510`、`scripts/lumos:78516`

severity: major
blocking: 是
引句:「行程內呼叫 `cmd_choice_kill(env, diff=範圍, max_seconds=_CHOICE_PASS_SECONDS)`,`_CHOICE_PASS_SECONDS` = 600 秒」

不能判成 clean 的另一點是,計劃的〈舊否決比對〉只比對了「pass 內重跑處置閘」與「另寫共用判定」,沒比對「pass 不跑測試」這條既有方針。⚠ 交編排者確認:這條方針是否已被 `_codeloop_pass_mech` 那次取代。我的判斷是只取代了機械兩道,沒取代跑測試。

**2. 命名與錯誤處理**

- 新函式 `_codeloop_pass_choice(repo_root, head_sha, branch)` 的簽章與 `_codeloop_pass_mech` 相同。
- 擋下事件用 `_gate_event_or_warn(repo_root, "code-loop-pass", "blocked", …, hard=True, …, extra={"blocks": …})`,沿用鄰居(`scripts/lumos:73389` 附近)。
- `blocks` 在鄰居是 `reason_kind` 清單,新增 `choice_reasons`(每種原因的行數)是新欄位,屬擴充,不算衝突。
- 擋下訊息沿用推送前同一段,pass 另加一句出口,跟鄰居一致。
- `_choice_push_round` 的 `label` 是二元組 `(前綴, 範圍說明)`,要穿過六支函式。鄰居是共用 `_cl_say_block` 後 pass 自己再印出口,不改被共用函式的訊息參數。
- 新參數的值也不一致:`ledger="worktree"` 用字串旗標,`_gov_rows_at` 與 `scripts/lumos:15415` 的慣例是 `rev=None`。`record=False` 在現況沒有對應(`_choice_push_event` 一律記)。

這些都是結構對、寫法與鄰居略有出入的小事。

severity: minor
blocking: 否
引句:「`ledger="worktree"` 時讀帳改用 `_gov_rows_at` 的工作目錄模式(rev=None)」

file: `scripts/lumos:73389`、`scripts/lumos:15415`、`scripts/lumos:65600`

**3. 第二種做法**

- 讀工作目錄帳:`_gov_rows_at(…, None, …)` 專案內已有先例(`scripts/lumos:15415`),`_choice_push_event` 內也已經用 `_gov_vc_gate_events` 讀工作目錄帳(`scripts/lumos:78760` 附近)。把它包成 `ledger` 參數是同一種做法的延伸,不算第二種。
- 抑制事件:現況是用「同一個 B 同一組 reason 已記過就不重記」去重(`scripts/lumos:78756`),沒有「呼叫端指定不記」的開關。計劃新增 `record=False` 是專案裡原本沒有的另一種事件抑制方式。
- 範圍:`_codeloop_default_range` 與 `_gate_failopen` 重用,一致。

severity: major
blocking: 是
引句:「`record`(要不要記 gate `choice-kill` 的 blocked/unverified 事件,預設記)」

判 major 的理由是它引入第二種事件抑制機制,跟既有的去重邏輯並存,且在同一支函式上疊三個旗標。鄰居收集模式(`mech_only`)是在同一個函式內分流,不是在事件層加開關。我判不準它該算結構問題還是命名問題,⚠ 交編排者。

file: `scripts/lumos:78756`、`scripts/lumos:79621`

**4. 落點合不合理**

- 計劃的 `lands_in` 只寫 `Systems/規格閘`。該節點 `about_code` 是 `scripts/lumos`,有 `_choice_push_round` 的內容(1 筆),但沒有 `_codeloop_pass_mech` 或 `_codeloop_pass_gate`。
- 管 pass 這一關的是 `Systems/pitfalls-code-loop`:「記通過之前」與 `_codeloop_pass_mech` 都寫在那篇,Android 寫法那份計劃的 `lands_in` 就是 `Systems/pitfalls-code-loop` 加 `Systems/棧別提問表態閘`。選擇點判定本體則在 `Systems/規格閘`(`choice-kill` 內容也在 `Systems/guard-kill`)。
- 新機制橫跨兩處,pass 的接點與擋下事件該寫進 `Systems/pitfalls-code-loop`,三個新參數的說明寫進 `Systems/規格閘`。只寫一邊會讓接手的人從 pass 查不到、或從選擇點查不到。
- 計劃已把 `Systems/pitfalls-code-loop` 列在「舊否決比對」連結裡,但沒列進 `lands_in`。

severity: minor
blocking: 否
引句:「lands_in:
  - Systems/規格閘」

file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`、`docs/lumos-toolchain-knowledge/Systems/規格閘.md`

不對齊共 4 條,其中 major 2 條
