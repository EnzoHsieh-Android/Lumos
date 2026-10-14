severity: minor

通才回歸席第七輪。我讀了修補差異,並在 review-converge 的 b0576518 上跑 `python3.14 scripts/test_lumos.py -k residual`,457 項全綠。你點名的幾處檢查結論如下。

- 沒有殘留的 repo 照常出 light:已讀,無 finding。`bnotes` 為空時不呼叫 `_residual_tree_paths`,也不產生 `unknown`。
- `_vault_slug_of` 加 `bare=` 後既有 8 處讀者:已讀,無 finding。讀者都不傳 `bare`,預設 False,行為不變。
- 拿掉 `_residual_graph_file`:已讀,無 finding。`scripts/lumos` 與 `scripts/test_lumos.py` 都沒有殘留的呼叫點,`_residual_index_notes` 與 `_residual_note_hits` 的新回傳形狀,各呼叫點也都已改。
- doctor 對舊格式索引:已讀,無 finding。只有沒有 `notes` 欄的條目走舊格式,補一行叫人 `--reindex`,不重複報 notes 不同。
- guard residual --add 與 --reindex 的輸出:已讀,無 finding。
- 鏡頭不寫快取的條件:發現下面兩條 minor。

severity: minor
blocking: 否 — 只影響 `dispatch-lens` 對同一範圍的快取命中,不影響分級放行與擋下的判定
引句:「時間不夠而兩版都沒有殘留索引、也沒改治理帳 → 回 [](r6 G4)」
問題:這次修補改了鏡頭輸出,包含殘留段的條件、內容與彙總行。但 `_LENS_SCHEMA` 仍是 5,快取鍵只含 `repo|base|head|schema5|extra`。
具體失敗情境:r6 G4 要修的是「沒有殘留的 repo 被印了『算不出來』」。這種輸出若已在修補前以同一 base 與 head 寫進快取,修補後 schema 沒變,同一範圍會一直命中舊快取,繼續拿到舊的錯誤輸出,直到 sha 改變。
佐證:``scripts/lumos: `scripts/lumos:49121` `` 與 ``scripts/lumos: `scripts/lumos:48658` ``

severity: minor
blocking: 否 — 只在預算用完或 git 慢時超支數秒,結果仍然安全(寧可印「算不出來」)
引句:「每次呼叫固定 3 秒上限:時間預算用完時才用,先判有沒有、再決定要不要印」
問題:`_lens_residual_absent` 在 `left()<1`(預算已用完)時才執行,卻最多再做 3 次各 3 秒的 git 呼叫(兩次 ls-tree、一次 diff),所以鏡頭會再超出 `_LENS_INNER_BUDGET` 最多約 9 秒。
具體失敗情境:hook 內層預算 45 秒、扣掉 5 秒保留,鏡頭已逼近上限時,這 9 秒可能讓外層 hook 逾時。逾時時,連原本該印的「算不出來」那句也印不出來。
佐證:``scripts/lumos: `scripts/lumos:49009` ``

severity: minor
blocking: 否 — 純粹是效能與降級,結果偏向升 high(安全方向)
引句:「tree = _residual_tree_paths(repo_root, base) if base and any(p is not None for p in bnotes.values()) else None」
問題:這個判斷一有殘留索引就對起點版本做整棵樹的 `git ls-tree -r`,不管這次推送有沒有改到任何圖譜檔。大 repo 每次跑 pitfalls 都付一次,並把全部路徑載進集合。
具體失敗情境:
- 逾時(上限 60 秒)或 git 失敗時 `tree=None`,所有記有路徑的條目連同 `touched` 都被改判成「列不出起點版本的檔案清單」。
- 鏡頭路徑上,`tree` 讀不到時,原本逐條列出的「改到存著決策的筆記」會被收成一行彙總,審查席少了逐條資訊。
- 只有改到圖譜檔(`gfiles` 非空)才需要樹,可以先看 `gfiles` 或 `changed` 再讀樹,或改用 `git cat-file --batch-check` 只查那幾個路徑。
佐證:``scripts/lumos: `scripts/lumos:44835` `` 與 ``scripts/lumos: `scripts/lumos:44673` ``

最高等級 minor,blocking 0 條。
