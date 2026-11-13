severity: major

## 1. 分層與依賴方向:不對齊
- 對照:鎖的建立、持有登記、刪除都收在 `_vault_write_lock` 一支裡,外面的人只能用 `with`。檔級位置在 `scripts/lumos:30703-30757`,它的 finally 在 `scripts/lumos:30751-30757`。鎖位置由 `_vault_lock_where`(`scripts/lumos:30659`)決定。
- 修補後,人裁指令層多了 `_situation_rule_drop_lock`(`scripts/lumos:75788-75799`)。它自己讀鎖檔第一行比對程序編號、`unlink`,還直接 `pop` 鎖模組私有的 `_VAULT_LOCK_HELD` 和 `_VAULT_LOCK_VAULTS`。
- `_situation_rule_commit` 也自己呼叫 `_vault_lock_where(env.vault)[0]` 取鎖路徑,再塞進 `st.lock`。
- 這是指令層直接操作寫入鎖的內部檔和內部登記表,屬於跨層直呼(見 a1)。
- 新增的 `_KILL_RUN_LIVE` 登錄表放在 `_kill_run`,方向跟 `_LINT_WT_REG["procs"]`(`scripts/lumos:41544`)一樣:低層登記、高層收。這一塊對齊。
- `_spec_gate_ruled_events` 抽出來後,`_spec_gate_ruled_ids` 與人裁指令共用同一套比對,讀帳只有 `_gov_vc_gate_events` 一支,也對齊。
- `_disk_spelling` 改為直接呼叫既有函式(`scripts/lumos:31204`,patch 中 `scripts/lumos:75638`),對齊,原本另寫的 `_situation_rule_plan_case` 已刪。
- 引句:「def _situation_rule_drop_lock(lock):」

## 2. 命名與錯誤處理:大致對齊
- 命名:新函式都用 `_situation_rule_*` 前綴,跟同檔鄰居一致。`_spec_gate_ruled_events` 回 `(結果, 帳壞原因)`,跟 `_gov_vc_gate_events`(`scripts/lumos:23568`)同一種回傳形狀。
- rc:拒絕走 `_situation_rule_say` 回 2,帳沒記回 1,已完成回 0,跟 patch 前一致。
- 訊息:帶外部內容的地方都有過 `_kill_esc`(seg、row、gerr、原話)。
- 處理器內印訊息用 `os.write(2)`(`_situation_rule_stderr`),鄰居 `_lint_wt_on_term`(`scripts/lumos:41553-41565`)用 `print(file=sys.stderr)`。docstring 說處理器會重入 stderr 的緩衝層、會丟 RuntimeError。這個理由站得住,且只用在處理器內,不判不一致。
- 引句:「_situation_rule_stderr(f"\n{st.force_msg}\n")」

## 3. 第二種做法:有一條
- 強制結束收程序群組:呼叫既有的 `_kill_proc_group`,最後 `os._exit`,跟 `_lint_wt_on_term` 同一套。docstring 與圖譜 WHY 也寫明「第一個訊號要轉例外才能走 finally」,不同之處站得住,不算第二種做法。
- 殘鎖:專案已有兩套收鎖做法。`_vault_write_lock` 的 finally 用程序編號比對(`scripts/lumos:30751-30757`)。`_excl_lock_cleanup_failed` 與 `_excl_lock_is_mine`(`scripts/lumos:70675-70690`)用 inode 與內容身分比對,專收建鎖到一半的半成品。
- 新的 `_situation_rule_drop_lock` 是第三份。它重寫一遍「第一行是自己的 pid 才刪」,又手動改持有登記。
- 它的理由是:`os._exit` 不跑 finally,KeyboardInterrupt 可能落在建好鎖檔、還沒進 try 的幾行之間。這兩個情境確實存在,所以需要一個能從外部收鎖的出口。
- 但理由只支持「要有出口」,不支持放在指令層、複製比對邏輯。出口應該放在 `_vault_write_lock` 旁邊,由它的 finally 與強制結束共用。
- 引句:「_VAULT_LOCK_HELD.pop(str(lock), None)」

## a1 指令層另寫一套收殘鎖並直接動寫入鎖的內部登記
severity: major
blocking: 是
引句:「_VAULT_LOCK_HELD.pop(str(lock), None)」
file: `scripts/lumos:30746`

⚠ 判不準處:這個需求(`os._exit` 前收鎖)是真的,所以是否要歸「第二種做法」交編排者裁。我判 major 的依據是它同時符合「跨層直呼」(指令層動鎖模組的私有表)和「第三份收鎖邏輯」。最小改法是把這段收進 `_vault_write_lock` 同區,讓 finally 與強制結束共用。

不對齊共 1 條,其中 major 1 條

附註:派工詞提到的 `.warming` 鎖檔我查過,檔案已不存在,我沒有刪任何東西。
