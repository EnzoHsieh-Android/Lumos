severity: minor

r2 的 F1 到 F6 都照方向修了,這一輪沒有會擋的不對齊。剩下兩條小的:一條是新增的找行輔助函式,一條是 pass/skip 的標記檔優先政策仍與表態分家。

## r2 六條核對

- **F5(讀治理帳只留一支)**:已修。`_kt_bj_ledger_events` 整支刪掉,盲判改走 `_codeloop_ledger_events`(`scripts/lumos:72286`)。`_codeloop_ledger_events` 收字串或位元組,壞行改接 `(ValueError, RecursionError)`,與 `_drift_jsonl_parse`(`scripts/lumos:57567`)一致。pass/skip 退帳(`scripts/lumos:69960`)、表態(`scripts/lumos:71642`)、合併側(`scripts/lumos:71762`)、盲判都是這一支。
- **F6(表態與盲判同一條真相規則)**:已修。`_codeloop_read_dispositions` 去掉 `marker_only` 與標記檔讀取,只讀帳、分支名完全相同(`scripts/lumos:71630`)。`_codeloop_write_marker` 與 `_codeloop_write_dispositions` 刪除,我在 repo 裡 grep 不到殘留的 `dispositions.json` 讀寫。
- **F1**:已修。`_codeloop_default_range` 被 `_kt_bj_segments`(`scripts/lumos:72569`)與 `_codeloop_guard_verdict`(`scripts/lumos:73066`)共用。
- **F2**:已修。判定函式改經 `_merge_side_ledger_cached`(`scripts/lumos:71744`)拿帳,不再直接伸手拿 `cache["ledger"]`。
- **F3**:已修。旗標平著傳進 `cmd_code_loop`,組合檢查回到 `_cmd_codeloop_blind_judge` 裡。
- **F4**:改名在 check.py 段,第一段 patch 顯示 `_abbr_table` 與 `_abbr_hit`。

## ① 模組邊界

結構對。範圍計算、治理帳讀取、合併側快取鍵都收進各自的歸屬函式,沒有跨層直呼。預設範圍收斂成 `_codeloop_default_range`,`_codeloop_default_base` 在 repo 裡只剩它一個呼叫端(`scripts/lumos:72908`)。

引句:「快取的鍵只有合併查找這一區知道,判定函式經這一支拿」
對照:`scripts/lumos:71744`。快取鍵由 `_merge_side_ledger`(`scripts/lumos:71731`)寫、由同一區的存取函式讀,邊界乾淨。

引句:「mb, _dr = _codeloop_default_range(repo_root, head_sha, "HEAD")」
對照:`scripts/lumos:73066`。呼叫端各自決定範圍為 None 時怎麼辦,`_codeloop_default_range` 只算範圍。這是收斂,不是另起一套。

## ② 命名與錯誤處理

沒有新的不一致。旗標改平傳後,`getattr(args, "cl_bj_*", 預設)` 與同一段其他子指令的寫法一樣(`scripts/lumos:76343-76353`)。壞行接法統一為 `(ValueError, RecursionError)`,讀帳失敗用 `except OSError` 回空或 None,與 `_codeloop_read_from_ledger`(`scripts/lumos:69961`)一致。

引句:「except (ValueError, RecursionError):」
對照:`scripts/lumos:57567` 的 `_drift_jsonl_parse` 與 `scripts/lumos:72170` 的 `_kt_sit_reminder_log`。三處接法相同。

## ③ 第二種做法

**F1**
severity: minor
blocking: 否
引句:「def _ledger_lines_having(raw, toks):」
- 它另寫了一套「在位元組裡找行界」的邏輯(`rfind(b"\n")`、`find(b"\n")`),跟 `_ledger_lines`(`scripts/lumos:21516`)的切行規則並存。
- 它沒有另立切行規則:整本有 `\r` 時直接退回 `_ledger_lines`,沒有 `\r` 時只認 `\n`,結果與 `_ledger_lines` 相同。
- 專案裡已有同類的位元組專用寫法:`_ledger_physical_lines`(`scripts/lumos:21556`,分塊讀)與 `_kt_sit_reminder_log` 的 `raw.split(b"\n")`(`scripts/lumos:72190`)。這是既有模式的又一例,不算第二種做法。
- 殘留風險是切行規則現在多一處要跟 `_ledger_lines` 保持同步。docstring 已寫明等價關係,測試有沒有綁等價關係我沒查。
- 要說對齊,最乾淨的是把它的位置與等價關係掛在 `_ledger_lines` 旁,目前已經相鄰。

**F2** ⚠ 判不準,交編排者
severity: minor
blocking: 否
引句:「★只讀治理帳★(代碼審 code-android情境題盲判 r2 乙,跟盲判同一條規則:只追加的帳是唯一真相):原本本機標記檔」
- 這次沒有引入第二種做法。表態與盲判現在是同一條規則。
- pass/skip 的 `_codeloop_read`(`scripts/lumos:69937`)仍是標記檔優先、不存在才退帳。這是改動前就有的做法,r2 範圍外。
- 現在專案裡有兩套「標記檔 vs 帳」讀法並存,但並存是 pass/skip 自己的歷史,不是這次造成的。
- 我在 patch 的圖譜段沒看到把這個並存寫成帶回頭條件的 `REVISIT:`,只在 `_codeloop_read_dispositions` docstring 裡寫「跟 pass/skip 分開重建」。
- 判不準的是要不要要求補一行 REVISIT,留給編排者。

不對齊共 2 條,其中會擋的 0 條。
