severity: clean

這輪我沒找到任何能被利用的洞。我讀了完整的 patch,也讀了修補後 `check.py` 的 `_fence_regions` 與 `_visible_lines`(`/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/abe4deee-64ee-43ea-85c3-2a647e0b825a/scratchpad/check_new.py` 第 1409 到 1450 行,取自 e160da75)。

**① 提示注入:已看,無。**
- 這輪改的是型錄自檢。壞例檔內容、範本內文、型錄片段只拿來做比對。
- 它們都不會進派工詞、hook 附加段或任何指令。
- 錯誤訊息只回顯固定字串和 `f.name`、`cid`、`group`,沒有把壞例檔的自由文字帶進給 AI 的段落。

**② 讀寫與執行越界:已看,無。**
- 新增的 `_balanced_end`、`_one_annotation_end`、`_annotation_end`、`_next_statement`、`_bad_lines_in`、`_unpipe` 都是純字串處理,沒有 subprocess、eval、shell 插值或檔案寫入。
- 讀檔路徑沒變,仍是 `samples_dir/bad/<id>` 底下的 `rglob("*.kt*")`。
- 測試用 `tempfile.mkdtemp(prefix="gctl-badlines-")` 建暫存目錄,`finally` 裡用 `rmtree` 清掉,寫入範圍都在暫存目錄內。
- 假的去註解物件 `_MisLines` 只回傳字串,沒有副作用。
- patch 裡沒有新寫進的密鑰或信箱,也沒有下載來源。

**③ 一步就能繞過的守衛:已看,無。** 我檢查了兩個本案特別看的問題。
- 新的註記判讀會不會讓照常編輯一支壞例檔就意外通過:
  - 註記括號配對不起來時,各種寫法都會偏向「不跳過、標在註記那一行」,結果是片段對不上而報問題,不會變成放行。
  - 括號到檔尾沒關,回 `k`。
  - `@field:[A B]` 這類寫法,名稱後面接 `[`,函式會直接回 `i`,標在註記行。
  - 字元字面值裡帶括號(例 `@Foo('(')`)會讓深度算不回零,到檔尾回 `k`;`@Foo(')')` 則提早在註記行收尾。
  - 要讓註記吞掉後面的語句,得有一個多出來的收尾括號,那是不合法的 Kotlin,不屬於照常編輯。
  - 標記後面沒有任何語句時,仍是舊行為:不產生項目,片段找不到就報。
- 範本圍欄守衛會不會被一次照常編輯繞過:
  - 守衛用寬鬆讀法判斷是否有沒關的圍欄,奇數個圍欄標記會被擋下,方向是寧可多擋。
  - 要繞過得同時多出兩個孤立的圍欄標記,讓總數保持偶數,一次編輯做不到。
  - 守衛只在 `範本 T<n>` 這條改由路徑上跑,其他路徑不受影響,這是設計範圍,不算洞。

看過的檔:
1. `configs/ast-grep/kotlin-android/check.py`
2. `scripts/test_lumos.py`
3. `docs/lumos-toolchain-knowledge/Projects/情境決策點窮舉與壞寫法要叫得出_計劃.md`
4. `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`
5. `docs/lumos-toolchain-knowledge/Verification/2026-11-12_情境決策點窮舉實作驗證.md`

總結:最高等級 clean,共 0 條
