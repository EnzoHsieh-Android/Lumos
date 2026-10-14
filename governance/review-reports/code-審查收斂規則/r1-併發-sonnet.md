severity: minor

我讀了主程式 patch 並實測熱路徑成本,找到兩條 minor,沒有 major 或 blocker。

severity: minor
blocking: 否 — 只在索引寫失敗這種少見情況才觸發,doctor 會報,不是靜默放行。
引句:「atomic_write_verify(path, new_lines, f"[residual:{ref}]", check)
        n = _residual_index_write(env)」
問題:`guard residual` 先寫合約行、再寫索引,兩步各自原子,合在一起不原子。第二步失敗時,合約行已經改了,指令卻印「擋下」並回 rc 2。重試時走不到索引寫入:
- `--add` 看到 `ref in have`,印「已經有了」並回 rc 0,不會補寫索引。
- `--remove` 回「沒有東西可拿」並回 rc 2。

具體失敗情境:
- 觸發:`governance/` 被換成捷徑,或磁碟唯讀,讓 `_write_refusal_reason` 擋下,丟出 `WriteBlocked`。這個例外同時是 `ValueError` 和 `RuntimeError`,所以被 except 接住。
- 結果:第一次 `--add` 印「擋下」,實際上 `[residual:…]` 已寫進合約行,索引沒更新。
- 後續:AI 照訊息重跑,得到「已經有了」rc 0,以為完成。
- 後果:pitfalls 讀不到這條殘留,改到守的程式也不會升 high。
- 補救:只有 doctor 的「索引對不上」提醒,以及手動跑 `--reindex`,但訊息都沒提。
- 另外:`Env(env.vault)` 重載若丟出非 `ValueError`/`RuntimeError` 的例外,會直接噴堆疊,同樣留下寫了一半的狀態。

建議:索引寫失敗時印「合約行已寫、索引沒更新,請跑 --reindex」。或讓「已經有了」那條路徑也補寫索引。

佐證:``file: `scripts/lumos`(patch 內 `_cmd_guard_residual_locked` 的 try 區塊與 `if ref in have:` 的提早 return)``

severity: minor
blocking: 否 — 漏掉的是索引內容的新鮮度,doctor 不報;但分級本來就只會少升,不會誤放行既有分級。
引句:「want = {(e["node"], e["fp"]): e for e in _residual_index_entries(env, with_tests=False)}」
問題:doctor 比對索引時用 `with_tests=False`,比較欄位只有 `residuals` 和 `about_code`。索引裡的 `test_files` 完全不驗。

具體失敗情境:
- 前提:合約綁的測試被搬到另一支測試檔,或改名,圖譜和合約行都沒動。
- 結果:索引的 `test_files` 指向舊檔,doctor 通過。
- 後續:之後有人改新的測試檔,`_residual_tier_hits` 比對不到,不升 high。
- 對照:`about_code` 的漂移 doctor 抓得到,`test_files` 抓不到。
- 同時:`_residual_test_files` 在找不到測試或讀不到設定時靜默不列,`--reindex` 後也看不出少了哪些。

建議:doctor 也用 `with_tests=True` 比對,或至少在說明裡明寫 `test_files` 不受 doctor 守護。

佐證:``file: `scripts/lumos`(patch 內 `_doctor_residual_lines`、`_residual_index_entries`)``

已讀,無 finding:
- **`pitfalls --diff` 熱路徑成本:** 在 review-converge 實測,`_residual_tier_hits` 在沒有索引的 repo 上約 0.02 到 0.06 秒(三種範圍寫法)。每次最多多 2 次 `git show`,外加 1 次 `git diff --name-only` 和 `...` 範圍的 1 次 `merge-base`。`git show` 失敗和讀不出 JSON 都回空集合,`RecursionError` 也接住了。
- **git 呼叫逾時退路:** `git show` 逾時(20 秒)、`git diff` 逾時(60 秒)或回傳非 0,都靜默回空,分級退回舊算法而不是擋下。這是 fail-open,我認為合理:索引只用來多升 high,不會把原本的 high 降級。
- **`guard residual-ask` 寫帳:** 查重和寫帳都在 `_vault_write_lock` 內,同一個反例不會因競態寫兩筆。`_gate_event` 回 `None`(沒有 docs/)和 `False` 都走 `ok is not True`,印「沒記到」並回 rc 1。`residual-ask` 已加進 `_KNOWN_GATES`,且不在本機帳分流名單,`_gov_vc_gate_events` 讀得到。每次讀整本治理帳約 20MB,單人使用下可忽略。
- **`--reindex`:** 只讀圖譜和測試檔,沒有指令之間共用的快取,成本和索引條數成正比。拿寫入鎖,且 `_write_lf` 用 tmp 加 `os.replace` 原子寫入。
- **doctor 新檢查:** `extract_contracts` 本來就要逐篇跑。`_pq_decision_state` 沒傳 `cache`,每個 ref 可能重建一次路徑索引,只跟 ref 條數成正比。算不出來時有 try/except 並明講,不是靜默。

最高等級 minor,共 2 條,blocking 0 條。
