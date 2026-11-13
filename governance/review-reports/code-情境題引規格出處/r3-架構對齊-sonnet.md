severity: major

三問都以 `/Users/enzo/harness/lumos-spec-cite/scripts/lumos` 為對照,行號是該檔現況。

## 問 1 分層與依賴方向:對齊
新碼的位置和呼叫方向都跟鄰居一樣。
- 新加的 `_situation_rule_commit`、`_situation_rule_locked_write`、`_situation_rule_ledger_miss`、`_situation_rule_done` 都放在 `cmd_situation_rule` 上方,是同前綴的私有輔助函式,只由 `cmd_situation_rule` 往下呼叫。
- 寫計劃仍走既有的 `_vault_write_lock`、`_write_refusal_reason`(30508)和 `_write_bytes_atomic`。補記事件仍走 `_gate_event_build` 和 `_gate_event`。
- 規格閘那邊只是給 `_spec_gate_ruled_ids` 和 `_expected_requirement` 加一個選用參數 `ai_out`,資料往外傳,沒有反向依賴。
- 路徑包含判斷沿用現有慣例 `ppath.resolve().relative_to(vault.resolve())`,跟 `_spec_gate_twoway_gate` 同寫法。「Projects/ 是符號連結」用 `os.path.islink(str(...))`,既有先例在 871。

引句:「寫入與記帳在 _situation_rule_commit」(出自 `cmd_situation_rule` 的新 docstring;patch 第 758 行)

跨層直呼:未見。

## 問 2 命名與錯誤處理:對齊
- 命名:全部是 `_situation_rule_` 前綴,`_spec_gate_ruled_ai_lines` 沿用 `_spec_gate_` 前綴。
- rc:0 代表完成,1 代表計劃已動但帳沒記到,2 代表拒絕,跟 `_situation_rule_say` 一路到底的慣例一致。
- 錯誤訊息:仍然是 stderr 加 `_kill_esc` 跳脫。
- 讀計劃改走 `load_raw_for_edit`(30532)並把 `WriteBlocked` 轉成原因字串,這正是上一輪架構席點名要對齊的先例。
- 規格閘的提醒行用 `print` 到 stdout,帶 `[spec-gate]` 前綴,跟同函式一帶的做法相同。`⚠` 符號全檔有 162 處,不算新做法。
- 訊號處理(`_situation_rule_signals(defer=...)`):專案原本只有 `_lint_wt_begin`/`_lint_wt_end`/`_lint_wt_on_term`(41470–41540)這一套,而且處理器裡直接 `os._exit(3)`。人裁的收尾在 `_isolated_worktree` 的 finally 裡,`os._exit` 不跑 finally,只有轉成 `KeyboardInterrupt` 才會走到。這個理由站得住,也寫進了 docstring 和 `Systems/guard-kill` 的 WHY。「第二個以後的訊號只記下」是專案原本沒有的需求,沒有鄰居可借。所以我不把它算成第二種做法。

引句:「os._exit 不跑 finally,工作樹會留到下次清殘骸。兩套語意不同是刻意的」(patch 第 632–633 行)

## 問 3 第二種做法:有一處不對齊
- 訊號處理、路徑包含、讀檔拒 CRLF 與 BOM 這三項,都不是第二種做法(理由見上)。
- 「檔名大小寫逐層比對」是第二種做法。專案已有 `_disk_spelling(root, relp)`(31185):逐層 `os.listdir`,先精確比對,再比 NFC,最後比 `casefold`,回傳磁碟上的真實拼法。新加的 `_situation_rule_plan_case` 做的是同一件事,而且結構幾乎逐行對得上。它的 docstring 和 `Systems/guard-kill` 的 WHY 都沒說為什麼不能用 `_disk_spelling`。
- 兩者的小差異:`_disk_spelling` 讀不到目錄時回 `(None, 那層)`,新函式回 `prel` 本身;`_disk_spelling` 的 root 是 `Path`,新函式的 `vault` 也是 `Path`。這些都能在呼叫端用 `real, _ = _disk_spelling(vault, prel)` 再比 `real != prel` 吸收。這裡不構成刻意不同的理由。
- 另有 `_nfc_child`(463)是單層 NFC 比對,也是鄰居已有的相近做法。

## a1 檔名大小寫逐層比對另寫一套,專案已有 `_disk_spelling`
severity: major
blocking: 是
引句:「圖譜內路徑 prel 一層層對實際目錄列出的檔名(NFC 後一字不差)→ 對不上時回實際的路徑(大小寫不同那層換成實際檔名」
file: `/Users/enzo/harness/lumos-spec-cite/scripts/lumos:31185`

不對齊共 1 條,其中 major 1 條
