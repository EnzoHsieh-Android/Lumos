severity: minor

審查範圍:`_diff_git_same_name`、`_diff_git_starts`、批次排除與不重算、推主線名稱邊界、跳過帳訊息。我用 scripts 目錄的副本做了真實 git 實驗與破壞測試,每次先清 `__pycache__`;實驗目錄已刪。

**已讀,無 finding**
- 真實 git 輸出實驗涵蓋 `x b/y2`、`a/b b/c`、` b/z`、含 tab 的 `q\tb/t`、`u b/u b/u`、`中 b/文`、含雙引號的 `e"q b/x`、`a b/a` 等路徑,以及偶數長度的檔名。路徑長度為 L 時,`diff --git` 行長固定是 2L+5(奇數),切點只會是正中間那個空白。
- `core.quotePath` 開關兩種設定、`--no-renames` 與 `-M` 共四組合,檔名都還原正確。
- 改名 `u b/u b/u` 到 `u` 時,`diff --git` 行與「`u b/u` 兩半相同」的行長得一模一樣,但 `rename to` 的優先序高於檔頭行,所以仍取 `u`。
- 引號分支就算拿掉,舊的 ` "b/` 取法也會得到同樣的名字,行為沒有差別。
- 32MB 邊界一致:`wanted` 用 `<=`,`_note_reread_fp_file` 用 `>`,正好 32MB 的檔兩邊都放行。
- 前綴固定為 `--src-prefix=a/ --dst-prefix=b/`,所以 `mnemonicPrefix` 不會讓 `_diff_git_same_name` 回傳 None。
- 破壞測試中,這些會翻紅:
  - `_diff_git_same_name` 整個失效:紅。
  - 批次不排除太大的檔:紅。
  - 批次不跳過已算過的檔:紅。
  - 推主線的固定名拿掉 master:紅。
  - 推主線的 `refs/heads/` 前綴檢查放寬:紅。
  - 推主線分支名改取最後一段:紅。
  - 跳過帳訊息改回「本機治理帳」:紅。
  - `_note_reread_diff` 的截斷不依檔頭切段:紅。

severity: minor
blocking: 否 — 只是測試覆蓋的缺口,現行程式行為正確,沒有使用者可見的錯誤
引句:「return [m.start() for m in re.finditer(rb"(?m)^diff --git " if isinstance(d, bytes) else r"(?m)^diff --git ", d)]」
問題:`_diff_git_starts` 的行首錨點 `(?m)^` 沒有測試守住。
具體失敗情境:
- 我把 bytes 與 str 兩條分支的 `(?m)^` 都拿掉、讓它匹配行中任何位置的 `diff --git `。
- `t_reread_fp_split_and_empty_diff`、`t_reread_fp_one_diff_for_all_files`、`t_note_audit_reread_prepare_diff_scope` 全部照綠。
- 這個 repo 的程式與測試內文本來就有 `diff --git ` 字樣(docstring、正則),內容行是 `+`、`-` 或空白開頭,一旦錨點壞了就會在行中間切段。
- 所以守這個行為的測試要有一個內容行含 `diff --git ` 的檔案。目前沒有。
佐證:改動在 ``scripts/lumos: `_diff_git_starts`(patch 新增)``,測試補丁沒有對應案例。

severity: minor
blocking: 否 — 只是測試覆蓋的缺口,現行程式行為正確
引句:「and left[len(q) + 2:] == right[len(q) + 2:]:」
問題:`_diff_git_same_name` 的「兩半相同」比對和引號分支沒有測試能逼出差別。
具體失敗情境:
- 我把相等比對換成永遠成立,`t_patch_fingerprint_b_in_path_name` 照綠。
- 拿掉整個引號分支也照綠,因為後備的舊取法剛好對引號檔名也正確。
- 這是一個守衛名義上存在、實際沒有被驗證的比對。
- 目前兩半不同的檔頭多半有 `rename to` 或 `+++` 蓋過它,所以不會出現錯誤的指紋。
- 但測試名稱聲稱守的是「兩半相同才取」,而這一條沒有案例:一個兩半不同、長度剛好對稱的複製或改名檔頭,例如 `a/orig b/copy`,不該被取成兩半相同。
佐證:``scripts/test_lumos.py: `t_patch_fingerprint_b_in_path_name`(patch 新增)``

severity: minor
blocking: 否 — 只影響極端規模下的效能,在 27 秒預算內
引句:「if got is None or path not in got[2]:     # 看這批問了誰、不看切出了誰」
問題:`got[2]` 是 list,每支檔都要做一次線性的 `in` 比對,原本 `got[1]` 是 dict。
具體失敗情境:
- 路徑參數上限 100KB,短路徑下一批最多約 1.6 萬支。
- 我量過 1.6 萬支每支掃一次約 1.4 秒;三千支只有 0.055 秒。
- 現實規模下可忽略。若要保守,可把 `asked` 存成 set。
- 正好 32MB 邊界也沒有案例(測試只用 4096 這個上限,沒有恰好等於上限的檔),但兩處比較符號一致,所以不列為 finding。
佐證:``scripts/lumos: `_note_reread_fp_diff`(patch 新增)``

最高等級 minor,blocking 0 條。
