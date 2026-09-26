severity: minor

## F1 [cap-hint] 每行都重複標籤,跟既有「段落標籤只印一次、後續行不掛標籤」的寫法不一樣
severity: minor
blocking: no
引句:「lines.append(P + f"  {x['round']}:{f},最高 {x['max_severity'] or '?'}")」

`_cap_hint_lines` 把 `P = "[cap-hint] "` 這個標籤黏在回傳的每一行前面(`scripts/lumos:7471-7499`,含每輪折入行、閘狀態行、提示行、熔斷行)。但這份檔案裡既有的兩種「段落輸出」寫法都不是這樣:

1. `[disposal]` 系列(`_disposal_security_step` 等,`scripts/lumos:18200/18203/18223-18227/18243-18246/18250-18252/18264-18270`)是**開頭一行帶標籤**(例如 `print(f"[disposal] 資安席: ✗ — {why}")`),後面的補充說明用兩格縮排、**不再重複標籤**(`print("  在意的原因:...")`、`print("  接下來:...")`)。
2. `_review_yield_line`(`scripts/lumos:7503-7509`)是把整段漏斗數字彙整成**一行字串**回傳,呼叫端(`scripts/lumos:18663`)自己在外面接一次 `[disposal] ` 前綴,函式本身完全不處理多行。

`_cap_hint_lines` 回傳的是「每一行都自己重新掛一次 `[cap-hint] `」這種第三種形狀,在這支檔案裡沒有先例。也跟 `cmd_loop_next` 原本的文字輸出慣例不同:那邊是 `[next] {loop_id}: ...` 印一次表頭,後面「應派:」「圖譜:」等子項都是兩格縮排的純文字標籤(`scripts/lumos:10688-10743`),不會把 `[next]` 重複貼在每一行前面。建議跟著既有兩種寫法之一:要嘛開頭印一次 `[cap-hint]`、其餘行縮排不掛標籤;要嘛學 `_review_yield_line` 縮成一行讓呼叫端自己接前綴。

## F2 `_disposal_round_groups` 遠離同名家族 `_disposal_*_step`,還插進 `_review_yield_round`/`_review_yield_line` 這對緊密配對中間
severity: minor
blocking: no
引句:「def _disposal_round_groups(rounds):」

這支函式是從 `_loop_status_disposal` 內聯邏輯抽出來的(patch 對 `scripts/lumos:18292` 那段的削減可以看到),但落腳點卻放到 `scripts/lumos:7390`,離它唯一的兩個呼叫點都很遠:`_cap_hint`(同檔 7432 行,還算近)與 `_loop_status_disposal`(`scripts/lumos:18410` 附近,差了一萬多行)。這份檔案裡其他 `_disposal_` 開頭的處置閘子步驟——`_disposal_security_step`(18192)、`_disposal_clause_step`(18278)、`_disposal_landing_step`(18339)——全部緊挨著 `_loop_status_disposal`(18390)本體放,形成一個好找的家族群。`_disposal_round_groups` 沒有跟著這個既有慣例放在一起,反而落在完全不相干的 `_review_yield_round` 定義區。

連帶的問題是它插入的位置,直接切進 `_review_yield_round`(7366-7387)跟 `_review_yield_line`(7503-7509)中間——這兩支函式的關係是「算漏斗數字 dict → 印成一行字」的緊密配對(注釋也互相點名對方:`_review_yield_line` docstring 寫「把 `_review_yield_round` 的 dict 印成一行」)。插入約 140 行新機制在這對函式之間,原本靠得很近方便對照著讀的兩支函式現在被拉開了。建議把 `_disposal_round_groups` 挪到 `_disposal_security_step` 那個家族群附近(或至少緊鄰 `_loop_status_disposal`),把 `_cap_hint`/`_cap_hint_lines` 這組新機制整組搬到 `_review_yield_line` 之後,不要卡在既有配對中間。

已看,無:
- `_cap_hint`/`_cap_hint_lines` 的命名對仗(算結構 dict / 印成文字)跟 `_review_yield_round`/`_review_yield_line` 一致,是同一種「算 → 印」慣例,沒問題。
- `_cap_hint` 對 `_TIER_PARAMS` 用 `.get(tier) or (None, None)` 防禦式取值,跟 `cmd_loop_next`(`scripts/lumos:10513`)直接 `_TIER_PARAMS[eff_tier]` 索引不同,但 `_cap_hint` 讀的是舊帳上可能壞掉的 tier 值、`cmd_loop_next` 讀的是自己算出來已驗證過的 tier,情境不同,防禦式取值合理,不算另起一套。
- 圖譜 `WHY:` 行(`docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:30`)格式 `WHY:[日期 出處]內容...[test:...]` 跟同檔其他行(PITFALL/KEY 行)及全庫其他 `WHY:[...]` 行一致,出處、日期、`[test:]` 標籤都齊,符合 CLAUDE.md 要求。
- 測試裝飾器 `_cap_real_cutoff`(`scripts/test_lumos.py:33012-33260` 附近)改的是真的 `os.environ`,跟既有 `t_panel_probe_retired`(`scripts/test_lumos.py:6329`)用 `env2 = dict(os.environ)` 再傳給 `subprocess.run(..., env=env2)` 的做法不同;但檔案裡共用的 `run()` 輔助函式(`scripts/test_lumos.py:161`)沒有 `env=` 參數、一律吃行程真正的環境變數,而新測試裡有些案例(`_cap_hint_of`)是直接呼叫 in-process 函式而非透過子行程,單靠 `env2` 傳參覆蓋不到這種呼叫。用裝飾器統一改真環境變數、跑完還原,是在既有 `run()` 沒開 `env=` 口子的前提下合理的新寫法,不是無故另起一套。
- 測試夾具 `_cap_rows` 的命名風格(底線開頭、簡短、回傳待餵資料)跟既有 `_sevrep`(`scripts/test_lumos.py:212`)一致。

共 2 條(F1、F2,皆 minor、不阻擋)。
