severity: minor

## F1 `None in renames` 檢查放在逐檔迴圈裡重算,結果對每支檔都一樣(效能瑕疵,非正確性錯誤)
severity: minor
blocking: no

`_nodehome_merge_own_changes` 裡:

引句:「if blobs is None or None in renames:」

`renames` 在進入 `for n, x in enumerate(order):` 之前就已經固定(只在函式開頭 `for p in parents:` 那個迴圈算一次),之後不會再變。但 `None in renames` 這個判斷式被放進逐檔迴圈裡,對 `order` 裡每一支檔都重新掃一次 `renames`(長度=parents 數,通常 2,代價小,不是效能地雷),結果永遠一樣:只要有任一上一版的改名偵測失敗,`renames` 就含 `None`,於是**這整個合併裡所有檔案都被判成「照舊查」(kept)**,不是只有真的需要改名對照卻拿不到的那幾支。這跟提示裡要驗的「改名偵測失敗時的退路是否偏向照舊查」方向一致(★偏向多擋,不偏向少擋★,不算漏洞),只是判斷式的位置容易讓人誤以為是「逐檔各自判斷該不該用改名對照」,實際是「一旦任何一邊的 diff-tree 失敗,整個合併退回舊判法」,建議挪到迴圈外一次判斷可讀性更好,但不影響結果正確性。

## 已驗過、沒問題的部分

引句:「一次讀很多個「版本:路徑」的內容,回同順序的 bytes|None」

在 `/tmp` 造出下列邊界情況實際跑 `python3 scripts/lumos home check --diff <起點>..<合併> --repo <臨時倉庫>`,全部正確(不當機、不誤放行也不誤判):
- 路徑含空白(`src/a file with space.py`)解衝突後兩邊都留 → 正確不擋(`_nodehome_cat_blobs` 靠 blob 內容長度切割、不靠掃行,cat-file 失敗行只在 missing/ambiguous 才會把整個 spec 原樣印出,而該情況此檔並非 missing,所以沒有踩到「路徑本身含空白讓 missing 那行多切出欄位」這個潛在雷)。
- 路徑含中文(`src/中文目錄/檔案.py`,`-z` 輸出且用 `nfc()` 正規化)解衝突後兩邊都留 → 正確不擋。
- 改名一邊、改內容一邊(patch 內建的 `t_nodehome_merge_rename_one_side_not_blocked` 案例)實跑通過,且用手造的另一案例(相似度低於 50%、git 判不出改名,搭配 modify/delete 型態的合併衝突,`remerge-diff` 印出的是 `D`/`M` 而非 `R`)也沒有當機,只是照文件宣稱的方向多算一次「照舊查」,沒放行違規。
- 有子模組(submodule/gitlink)但子模組指標本身沒衝突的合併 → `remerge-diff` 根本不列子模組路徑,沒有進到 `_nodehome_cat_blobs`;程式碼裡對非 blob 型態(`head[1] != b"blob"` 但 `head[2].isdigit()`)有明確跳過分支,邏輯上能吃子模組/目錄物件,但沒能真的造出「子模組指標本身衝突」這個現場去實測(git 對這種巢狀 submodule 合併衝突不好造,判不準,標 ⚠)。
- `python3 scripts/test_lumos.py -k nodehome_merge` 18 案例全過,包含這份 patch 新增的 `t_nodehome_merge_rename_one_side_not_blocked`。

引句:「路徑裡有換行時批次讀取表達不了,整批當判不了。」

讀原始碼確認 `if any("\n" in s_ for s_ in specs): return None` 這道防線先於送進 `git cat-file --batch`,所以路徑含換行時不會讓後續輸出解析錯位;cat-file 成功時印的是重新算出的 40 碼 hex sha(不是原始 spec 字串),所以即使 spec 本身含空白也不會讓成功那一行被誤切——只有 missing/ambiguous 那行會原樣印出 spec、可能因空白被多切欄位,但程式碼用 `len(head) == 3` 排除掉這種情況(missing/ambiguous 只有 2 欄,含空白路徑會變 4+ 欄,兩者都落進 `else` 分支當成 None),方向仍是保守(當讀不到、判成照舊查),沒有讓解析整批錯位。

重點攻擊要求的「合併結果比兩個上一版」與「remerge-diff 新增行」等價性(兩邊都刪了某行但合併結果留著它、合併基底有兩邊都沒有的行)推演過,這兩種情境要嘛不可能發生在自動合併結果裡(兩邊都刪的行不會出現在合併結果)、要嘛就是算法定義下「新行」本來就該抓到的情況(手動把 base 才有的行敲回去,確實是新寫的),沒找到讓它偏向「少擋」以外的反例。
