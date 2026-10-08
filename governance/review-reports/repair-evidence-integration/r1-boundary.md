severity: major

boundary-F1

severity: major

blocking: 是

觀察：`write-tree` 失敗時，設計要求退回活動索引執行原正式檢查；但結尾發現索引變動時，只撤回 `staged_route_tests`，不撤回先後從不同索引狀態取得的改動清單、設定、圖譜及分類。失敗路徑仍可能用混合版本作出正式放行或阻擋。

獨立判準：守衛的正式判定必須綁定單一完整版本。無法建立固定樹時，應證明全部正式讀取前後為同一索引；不一致就撤回整次判定或按既有 fail-open 明確跳過，不能只撤回額外測試證據。

具體場景：物件庫唯讀使 `write-tree` 失敗，但 `ls-files`、`diff`、`show` 仍可讀。檢查先從索引 A 取得 changes，另一程序暫存成 B 後，程式從 B 讀設定與圖譜；即使最後留在 B，目前邏輯也只清空額外 route 證據，仍以 A/B 混合資料進 `_nodehome_evaluate`。若 B 又還原成 A，連現有前後索引比較也看不出 ABA。

引句:「捕獲失敗不借額外證據，保留原正式程式檢查退路，不修改安家集合、每提交規則或fail-open政策。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:29958`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:30041`

boundary-F2

severity: major

blocking: 是

觀察：待實作固定樹仍沿用會先做 NFC 正規化的 Git 路徑資料結構。原始 Git 路徑在成為 dict key、變更路徑及 `git show <tree>:<path>` 輸入前已被改寫；固定樹雖不可變，讀到的路徑身分仍可能錯誤。

獨立判準：Git 樹的查找鍵必須保留原始路徑位元組；供顯示或邏輯比較的正規化名稱必須另存。遇到正規化碰撞，至少要明確拒絕或標成未判定，不能靜默覆寫。

具體場景：Linux repo 同時追蹤預組字元 `src/Café.py` 與分解字元 `src/Café.py`。Git 將兩者視為不同路徑，但 `_nodehome_list` 會把兩者正規化成同一 key，後者覆寫前者；`_nodehome_changes` 也會把兩個變更壓成同一名稱，reader 最後可能讀錯 blob 或完全讀不到。新加入且無家的檔案可因此與已有家的同名兄弟混為一個，讓守衛錯誤放行或阻擋。Windows 被排除並未排除這個 Linux 場景。

引句:「可捕獲時，改動清單、設定、圖譜與分類讀同一樹；測試route不再從會動的索引借證。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:424`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:28908`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:28911`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:28955`；`/tmp/lumos-future-repair-regression-research/scripts/lumos:29212`

覆蓋與未驗邊界：

- 已覆蓋：staged 輸入、固定樹成功與失敗分支、索引 ABA、SHA-1/SHA-256 OID 接受範圍、Unicode 路徑身分、活動索引撤回範圍。
- `--diff` 路徑不使用本次 `write-tree` 方案，未發現本鏡頭新增缺陷。
- 稀疏索引、partial commit 的暫時 index、linked worktree、symlink、gitlink、非 UTF-8 與換行路徑均未實跑，維持未判定。
- 依指示未執行或安裝外部程式，亦未用既有綠筆記推導行為已驗。

實際閱讀帳：

- `lumos-design-loop/SKILL.md`：79 行。
- 唯一真 spec：67 行。
- r1 凍結副本：67 行。
- `r1-materials.md`：1185 行；因工具截斷另重讀 31 行。
- 行數核算與定點搜尋／上下文：87 行。
- 保守總計：1516/1800 行。

最高級：major；blocking：2。