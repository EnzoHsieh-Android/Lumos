severity: minor

**檢查範圍**:我讀了修補差異與 `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos` 裡的 `_note_reread_fp_file`、`_note_reread_fp_diff`、`_note_reread_fp_diff_batch`、`_patch_file_changes`。另外在臨時 repo 對含 ` b/` 檔名、tab 檔名(引號寫法)、二進位檔、改名、空檔刪除等情形,用真的 `git diff` 輸出跑過 `_patch_file_changes`,檔名全部還原正確。臨時目錄已刪。

severity: minor
blocking: 否 — 只多一點無謂比對成本,不影響判定結果
引句:「if got is None or path not in got[2]:     # 看這批問了誰、不看切出了誰」
問題:`got[2]` 是 `list(paths)`,`path not in got[2]` 是線性掃描,以前是 dict 查找。每支檔每次都掃一遍,一批最多約兩千支路徑(路徑參數上限 100KB)。
具體失敗情境:一批約兩千支路徑、約一千支檔依序被要求時,約 200 萬次字串比對,毫秒級。目前不會造成錯誤或逾時,順手改成 `set` 就沒事。
佐證:``file: `scripts/lumos:36565` ``

**被排除的大檔之後怎麼判**:已讀,無 finding。
- 型別變更、任一邊超過 32MB、大小缺漏的檔,`_note_reread_fp_file` 在進 diff 之前就回 `(None, "型別變更" / "太大" / "查大小失敗")`。
- `_note_reread_contrast_fp_v2` 看到 why 就整篇退回 v1 對照指紋,跟上一版行為一致。
- `wanted` 的條件跟 `_note_reread_fp_file` 的條件逐項一致,不會有「批次排除了、卻被要求 diff」的檔。
- 這時要求的檔不在 `diff_order`,走 `[path]` 單支,不會壞掉。
- `done` 的鍵 `(base["bp"], scan["tip"], path)` 跟 `scan["fpfile"]` 的快取鍵相同,跳過已算過的檔是對的。

**`_patch_file_changes` 的其他使用者(凍結 patch 指紋)**:已讀,無 finding。
- 檔名優先序仍是 plus、rename、minus、hdr,`hdr` 只在沒有這三種檔頭的段(二進位、只改權限、空檔新增刪除)才當檔名。
- 這些段的檔名只會更準:路徑含 ` b/` 時舊法取到 `y2` 這種殘段,新法取到整條。
- 一般文字改動不碰 `hdr`,指紋與上一版相同。
- 兩半相同的判斷沒有誤判。改名後新舊名剛好讓兩半相同的情形,只可能出現在改名檔頭(有 `rename to`),會蓋過 `hdr`。`--no-renames` 時不會有改名。
- 改名且檔名含 ` b/`、兩邊不同時,走原本的 `rfind`,被 `rename to` 蓋過,結果正確。
- `_diff_git_starts` 取代 `re.split` 的切段,在 str 上對 `^` 的語意相同(只認 `\n`)。起點 0 用集合去重,前導空字串由 `p.strip()` 濾掉。結果相等。

**資料狀態五問**:已讀,無 finding。
- 空 diff:單支問不到就整段給,空輸出走原本的「diff 空」,退回 v1。
- 檔案換成同名資料夾:切得出就只取自己那段。
- 單支問且名字還原不出來:只可能是這支或它底下的檔,代價是名字還原失敗時可能多算到資料夾內的檔,屬極少見寫法。
- 快取只留最後一批:要求順序與批次順序相反時,會重新問「未算過」的檔。已算過的不重算,最壞次數有界。
- 訊息文字「跳過記進 docs/.governance-log.jsonl」:`skipped-env` 確實不在 `_GOV_LOCAL_PAIRS`,所以寫進版控帳,說法屬實。

最高等級 minor,blocking 0 條。
