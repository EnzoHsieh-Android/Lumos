severity: major

## rollback-F1

severity: major  
blocking: 是

引句:「about_code前後版及每提交content_notes仍是原算法。」

佐證 file: `scripts/lumos:27511`  
佐證 file: `scripts/lumos:27611`  
佐證 file: `scripts/lumos:27444`  
佐證 file: `governance/review-reports/test-home-writeback/r1-snapshot.md:31`

觀察：設計只為整段範圍的 B／N 兩個端點建立較廣路由集合；逐提交雖保留自己的 `g_paths` 與 `content_notes.own`，卻沒有該提交前後版本的測試分類。現有程式正是先在 `_nodehome_evaluate` 建一次 B／N 集合，再逐組判定。

具體輸入：同一推送範圍中，提交一把測試 scripts/test_old.py 改名為 scripts/test_mid.py，同提交修改程式並向宣告 scripts/test_mid.py 的測試家寫回；提交二再把它改名為 scripts/test_final.py。`test_mid.py` 不存在於範圍兩端，因此不會進較廣集合；提交一的 `own ∩ 路由檔` 為空，錯誤回 rc1。新增後又刪除測試亦同。

判準：既有正式語意要求推送前依每提交自己的路徑與歸屬判定，一次推送多次改名不得受端點名稱影響。應為每個 group 使用該提交前後快照套既有分類器，或在建立 `content_notes` 時保存同提交的合法路由集合；並補「中途改名再改名／新增後刪除」普通與 `-O` 控制。

風險逐類：

- 守衛：有上述誤擋，屬阻擋項。
- 併發：只讀提交快照，未見新增共享可變狀態。
- 效能資源：目前兩次既有掃描有界；若改為逐提交分類，需補提交數放大下的耗時收據。
- 回退：局部移除 `include_tests` 視圖可恢復舊行為，回退敘述成立。
- 外部送出：無網路或發布動作。
- 不可逆：無資料遷移或帳目刪除。

其餘已讀章節無 finding：問題與歷史範圍、驗收 S1–S3／S5、既有紅燈收據措辭、回退、實務隱患及真實收據 REVISIT。受唯讀且無可寫暫存目錄限制，未重跑 fixture；不列為產品紅燈。

總結：最高 severity 為 major；blocking 1。

已讀材料：

- `governance/review-reports/test-home-writeback/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/test-home-writeback/preflight-intake.md`
- `governance/review-reports/test-home-writeback/r1-graph-context.txt`