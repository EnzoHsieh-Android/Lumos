severity: minor

審查範圍:資源席(第七輪)。實測在暫存目錄做完,已刪除。

**實測結果**
- **大 repo 的 `ls-tree -r`**:我造了 50 萬檔的 repo,用修補裡同一套寫法(`ls-tree -r -z --name-only --full-tree`,再逐筆 NFC 正規化成集合)。git 約 0.46 秒,整段約 0.61 秒,記憶體峰值約 164MB。真實的審查 repo(1.3 萬檔)只要 0.03 秒。耗時與記憶體都沒有失控。
- **大索引的分級耗時**:我載入真實的 `scripts/lumos` 跑 `_residual_index_notes`、`_residual_note_hits`、`_lens_residual_unknown_line`。3000 筆合約(9000 個殘留鍵)約 0.02 秒、40MB;3 萬筆(9 萬鍵、7.5 萬筆位置未知)約 0.22 秒、104MB。彙總成一行後輸出長度固定約 480 字,不隨筆數成長。
- **三個 git 呼叫與 45 秒**:見下面的 finding。

severity: minor
blocking: 否 — 只在 git 卡住時才可能多出幾秒,不會把誠實的操作擋下,也沒有留下孤兒行程
引句:「每次呼叫固定 3 秒上限:時間預算用完時才用,先判有沒有、再決定要不要印」
問題:`_lens_residual_absent` 的三個 git 呼叫各固定 3 秒上限,不看鏡頭剩下多少時間。殘留段的 deadline 是 `_t0 + 45 - 5`,也就是第 40 秒。預算用完才進這支函式,所以最壞是第 40 秒再加 3×3=9 秒,到第 49 秒,超過內層 45 秒的總帳。5 秒的保留量(`_LENS_FALLBACK_RESERVE`)被它吃掉還超出。
具體失敗情境:大 repo 或磁碟很慢,前面的 git 把預算耗到第 40 秒,接著 `ls-tree` 兩次加 `diff --quiet` 一次各卡滿 3 秒。鏡頭回傳時已過第 49 秒,若外層掛鉤的硬上限就是 45 秒,整個鏡頭會被砍,連「算不出來」那句必答題都沒印。
三個呼叫逾時只會讓 `_lens_git` 回 None,函式回 False,照常印「算不出來」。`subprocess.run` 逾時會殺掉子行程,沒有孤兒。
建議:把每次的 timeout 夾成 `min(3, 剩餘到 _t0+45 的秒數)`,不夠 1 秒就直接回 False。
佐證:file: `scripts/lumos:49009`

**同類的小提醒(不另列 finding)**
- `_residual_tree_paths` 在 pitfalls 分級路徑沒傳 deadline,timeout 固定 60 秒。這比鏡頭的 45 秒還長。
- 它在只要起點有任何帶路徑的 notes 時就會先跑,即使這次沒改任何圖譜檔(用不到那份樹)。
- 在 50 萬檔下實測 0.6 秒,所以只有 treeless 或 blobless 這類要現抓 tree 的 clone 才可能碰到 60 秒。逾時時 tree 變 None,所有 notes 路徑改判位置未知。
- 這時若有改圖譜檔就升 high,結果偏保守,不會漏。單人本機,不列 finding。

**已讀,無 finding**
- `_residual_index_notes` 及 `_residual_note_hits` 的迴圈:線性,沒有二次方成長。
- `_lens_residual_unknown_line`:`dict.fromkeys` 去重,只取前 3 個原因、前 3 支檔,輸出有界。
- 快取:算不出來的那次不寫快取,資源面沒有問題。

最高等級 minor,blocking 0 條。
