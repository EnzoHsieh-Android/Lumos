severity: clean

我先核對第四輪架構對齊席 F1:讀單支 blob 另開一條路。它確實修好了。F2 已附理由放行,我認為理由成立(連結檔名存成 NFD 時只會多擋,要動共用的列樹函式才修得到)。這輪沒有新的不對齊。

**① 模組邊界**
`_plan_blob` 不再自己跑 `git cat-file blob`,改呼叫 `scripts/lumos:46124` 的 `_nodehome_cat_blobs_capped`。這是上一輪點名的既有函式,上限放在批次讀取這一層。上限沿用 `scripts/lumos:53298` 的 `_NOTE_REREAD_FP_MAX`,沒有另訂數字。逾時仍走 `_disp_git_timeout`。

行數另寫了一支 `_repo_ref_source_line_count`,放在 `_repo_ref_source_lines` 旁邊。它的說明明寫與後者同一語意,只是不建行清單。這是以記憶體為由抽出的計數版,不算跨層,也不是第二套算法。

`_plan_tree` 仍走 `_drift_list` / `_drift_oids`(`scripts/lumos:56279`、`scripts/lumos:56302`),只補一份非一般檔集合。

引句:「got = _nodehome_cat_blobs_capped(root, [spec], _NOTE_REREAD_FP_MAX, timeout=_disp_git_timeout())」

**② 命名與錯誤處理**
- `_plan_cache_put` 現在回傳寫入的值(`scripts/lumos:14287`)。`_plan_blob` 與 `_plan_tree` 都依賴這個回傳值,三處用法一致。
- 快取三態改成「key 在且為 None」、「`.get` 為 None」、「已有值」三段,和 `scripts/lumos:14586` 的註解一致。這個「失敗也記進快取」的做法只在 plan 這一族用,上一輪已被接受。
- `_nodehome_cat_blobs_capped` 回 None 時,`_plan_blob` 不快取,下次再試。`_nodehome_cat_blobs` 本身也是這樣處理(`scripts/lumos:46124` 之後)。
- `_plan_src_miss_reason` 先擋 NUL 與編不成檔名的路徑,os 呼叫另接 `OSError`、`ValueError`。專案裡已有同形的 NUL 與 `os.fsencode` 檢查直接寫在呼叫點(`scripts/lumos:37048`),所以沒有另起一種錯誤處理。這個檢查沒有放進共用的 `_repo_ref_token_unsafe`,因為擋下原因這條路只在 plan 這一族,屬局部判斷,算是對的取捨。

引句:「except (OSError, ValueError):」

**③ 第二種做法**
- **新的樹清單快取:** 不是又一套讀 git 樹的方式。列樹仍然只走 `_drift_list`,`_PLAN_TREE_CACHE` 只存衍生的非一般檔集合與失敗標記。
- **符號連結解析:** 專案原本沒有這一塊。這輪加的 `fold=True` 是同一個函式內的另一組比對函式(`link_at` / `file_at`),走法沒變,不是另寫一支解析器。原本在 `_plan_src_miss_reason` 裡自己掃清單的大小寫比對已刪掉,改成共用這條走法,第二種做法反而減少一處。
- **`_plan_sources_uncomment`:** 這輪沒動它,上一輪的結論不變。
- **`_plan_head`:** 這輪沒動,沒有第二套問版本的做法。它自己跑 `rev-parse`(對照 `_lens_full_sha`)是上一輪已判定的舊帳。

引句:「link_at, file_at = (lambda c: nl.get(c.lower())), (lambda c: fl.get(c.lower()))」

不對齊共 0 條,其中會擋的 0 條。
