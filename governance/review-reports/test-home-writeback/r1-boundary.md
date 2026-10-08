severity: major

## boundary-F1

severity: major

blocking: 是

引句:「只有S13寫回路由用同次g_paths與較廣視圖的交集；about_code前後版及每提交content_notes仍是原算法。」

佐證 file: `governance/review-reports/test-home-writeback/r1-snapshot.md:31`

佐證 file: `scripts/lumos:27506`

佐證 file: `scripts/lumos:27611`

佐證 file: `scripts/lumos:27616`

佐證 file: `scripts/test_lumos.py:47846`

觀察：提案只從整段範圍的 B/N 兩個端點建立較廣分類集合，但推送路由逐提交使用各提交自己的 `g_paths` 與 `content_notes.own`。若 C1 新增 `tests/test_tmp.py`、同提交修改程式並寫回擁有該測試的家，C2 再把它改名為 `tests/test_final.py` 並更新家，`test_tmp.py` 不存在於 B 或 N 的較廣集合。C1 的 `g_code` 因此只剩正式程式，與該提交的 `own={test_tmp.py}` 無交集，合法寫回仍會被判 route 違規。現有 `diff-split` 只驗「不可跨提交借證據」，沒有覆蓋範圍中途新增後改名／刪除的測試。

判準：S1 所稱「已由有效家宣告、且同一提交實際改動的測試檔」與 S4 的逐提交判定，必須以該提交前後可見的普通檔分類為準；不能只用整段端點集合近似。設計需補明逐提交分類來源及相應正向控制，否則真實多提交推送仍會錯誤拒收。

風險逐類：

- 守衛：有上述漏放行，屬阻擋性設計缺口。
- 併發：無新增共享狀態；維持提交快照讀取，未見競態。
- 效能／資源：端點各多一次既有掃描，shebang 有 side 快取；尚未見無界資源，但逐提交修法需訂讀取上限或重用快照。
- 回退：局部撤除較廣路由視圖即可恢復舊行為，路徑清楚。
- 外部送出：僅本機 Git／圖譜判定，沒有網路送出。
- 不可逆：不遷移資料、不刪帳，沒有不可逆操作。

固定圖譜節點的家定義、需要家集合、tag-only、foreign-ref、S13b與快照語意均未見被正式合約破壞；原計劃範圍未當成不可更動合約。

其餘已讀無 finding：問題與最小範圍、PRIOR-ART／RETIRE-IF、刪除與單次改名、regular-file／test／ignore／vendor／UTF-8、symlink／JSON反控制、回退、實務隱患、preflight intake、graph context。唯讀環境無可寫暫存區，未重跑 fixture；這不列為產品紅燈。

總結：最高 severity 為 major；blocking finding 1 件。

已讀材料：

- `governance/review-reports/test-home-writeback/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/test-home-writeback/preflight-intake.md`
- `governance/review-reports/test-home-writeback/r1-graph-context.txt`