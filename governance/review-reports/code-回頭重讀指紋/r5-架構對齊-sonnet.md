severity: minor

整體判斷:這份修補沒有引入第二種做法,也沒有跨層直呼。你特別點的四件事如下,我只讀了 patch 和 `reread-fp/scripts/lumos`,沒有執行任何東西。

- **一次 diff 切檔頭:** 檔名是用既有的 `_patch_file_changes` 還原的,沒有另寫引號規則。分段邊界是新寫的 `_note_reread_split_diff`,見下面那條 finding。
- **推主線判定的主線分支名來源:** 走既有的 `_push_mainlines` 加 `_push_mainline_full`,沒有另寫找主線的邏輯。固定名 `main` 和 `master` 是補強用的。分岔點在推主線時改用 pre-push 給的遠端舊值,否則仍走 `_lens_default_base`,這是同一條路徑上的分支,不是第二套。
- **分塊切行:** 專案裡沒有現成的大檔分塊讀 helper,我搜了 `lumos` 裡的切行用法,只有零散的 `split(b"\n", 1)`,沒有可共用的。新的 `_note_reread_line_blocks` 只用在 `_note_reread_hunk_nodes`,不構成第二種做法。
- **入口清 git 環境:** 屬於既定裁定。`main()` 裡新增 `GIT_GRAFT_FILE`、`GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF` 的處理,跟原有的 `GIT_NO_REPLACE_OBJECTS` 寫在同一處。

severity: minor
blocking: 否 — 兩者做的是同一件事但用途不同,沒有行為分歧
引句:「starts = [m.start() for m in re.finditer(rb"(?m)^diff --git ", raw)]」
對照:file: `reread-fp/scripts/lumos:37008`(`_note_reread_diff_once` 之後的 `re.split(r"(?m)^(?=diff --git )", d)` 做同樣的按檔切段)
判定理由:專案裡已有按 `diff --git` 行首切多檔 diff 的寫法,新的 `_note_reread_split_diff` 另寫了一份邊界正則。兩者差異如下:
- 舊的是對字串切段,新的要回傳位元組的起訖位置,才能原樣餵給 `_patch_file_changes`。
- 檔名還原已經交回 `_patch_file_changes`,所以只重複了「找行首邊界」這一步。
- 兩邊對 `diff --git` 行首的判定一致(都是 `(?m)^diff --git `)。

我歸為輕微重複,不是第二種做法。如果之後想收斂,可以把行首邊界抽成共用的一行 helper。

最高等級 minor,blocking 0 條。
