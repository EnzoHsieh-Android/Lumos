severity: minor

severity: minor
blocking: 否 — 多了一份縮排計算,但有寫出理由,也不跨層;只是日後維護要記得兩份各自的規則。
引句:「ind = len(pre) if tb not in pre else len(pre.expandtabs(_NOTE_REREAD_TAB))」
對照:既有寫法 ``scripts/lumos: `scripts/lumos:33828` `` 的 `_ns_indent` 用 `ln.expandtabs(4)` 算縮排,吃 str;另有 `scripts/lumos:29098` 用 `expandtabs(2)`。
判定理由:新增的 `_note_reread_indent` 吃 bytes、tab 展開 8 欄,另外在 `_note_reread_hunk_nodes` 的熱迴圈裡又內聯一份同樣的算法。專案裡本來就有依用途取 2 或 4 欄的縮排函式。新的常數 `_NOTE_REREAD_TAB` 旁邊的註解寫明了原因:要貼近 git 與 Python 的 8 欄預設,而且縮排鏈只在這條路徑內部算,不跟 `_ns_indent` 的續行判斷互通。這是用途不同,不算第二種做法。要留意的只有新函式和內聯副本之間會漂移,各自改規則時要同步改。

其他幾項我都看過,沒有不對齊:

- **`_nodehome_cat_blobs_capped` 加 `sizes=None` 選填參數:** 預設行為不變,其他 6 處呼叫(`28556`、`31533`、`32654`、`37049`、`39168` 等)都不受影響。新增兩處呼叫(單支讀與批次讀)都走這支有上限的共用讀法。上一版自己比大小、再呼叫沒上限的 `_nodehome_cat_blobs`,這次改掉,等於把第二種做法收回來。
- **分批讀的寫法:** `_note_reread_fp_prefetch` 與 `_note_reread_fp_blob` 都經由 `_nodehome_cat_blobs_capped` 讀,帶單支上限、總量上限、`deadline`、`timeout`,跟既有呼叫者一致。「從某一支起往後再讀一批、手上只留一批」是新的視窗邏輯,但只在這個回頭重讀的路徑內部,沒有既有的同類寫法可以重用。
- **`_NOTE_REREAD_DIFF_CTX` 與 `_note_reread_diff_fits`:** `_note_reread_diff` 和 `_note_reread_v2_cut` 現在共用同一個常數與同一支判斷。原本兩處各寫一套(3、1、0 與 `len(d) > CAP`),這次收成一份,方向正確。
- **hunk 標頭解析:** 改用共用的 `_NOTELINES_HUNK_RE`,刪掉本地的 `_NOTE_REREAD_HUNK_RE`,同樣是收斂。
- **`_note_reread_blocking`:** `_note_reread_rc`、`_note_reread_print_judged`、`_note_reread_ledger` 三處都呼叫這一支來判擋不擋,沒有各自再寫一套判斷。

不對齊共 1 條(minor),major 0 條。
