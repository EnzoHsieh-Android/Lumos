severity: major

## logic-F1

severity: major  
blocking: 是

引句:「混合提交的路由核對，可採信已由有效家宣告、且同一提交實際改動的測試檔。」

佐證 file: `governance/review-reports/test-home-writeback/r1-snapshot.md:20`  
佐證 file: `governance/review-reports/test-home-writeback/r1-snapshot.md:29`  
佐證 file: `scripts/lumos:27110`  
佐證 file: `scripts/lumos:27611`

觀察：較廣集合只從整段 diff 的 B/N 兩個端點建立；`_nodehome_required` 又只遍歷該端點的 `side.files`。逐提交雖保留自己的 `g_paths/content_notes.own`，卻沒有該提交版本的路由分類。

具體輸入：base 尚無、但 TestHome 已宣告 scripts/test_temp.py；C1 同時新增該測試、修改持續存在的 `src/a.py`、寫回 TestHome；C2 再刪除該測試；檢查 `base..C2`。測試只在 C1 存在，因此 B/N 較廣集合都沒有它；C1 的 `g_paths` 與 `own` 雖有它，S13 仍會把 TestHome 判成錯家。

判準：既然合約採信「同一提交實際改動」，分類也必須能使用該提交的前後快照；否則需明文排除整段範圍內短暫存在的測試。現算法沒有達到 S1/S4 的一般逐提交語意。

## logic-F2

severity: major  
blocking: 是

引句:「內容判定與foreign-ref檢查器應保留純測試綁定豁免、只改測試的啟動條件」

佐證 file: `governance/review-reports/test-home-writeback/r1-snapshot.md:39`  
佐證 file: `scripts/test_lumos.py:47816`  
佐證 file: `scripts/test_lumos.py:47848`  
佐證 file: `scripts/lumos:27613`

觀察：`test-only` 控制修改測試後，寫的是該測試自己的 TestHome。即使實作錯把測試加入 `g_code`、啟動規則三，路由仍會相交並回 rc0；此控制無法證明「只改測試不啟動」。

具體輸入：只改 scripts/test_checks.py，同提交改寫僅擁有 `src/a.py` 的 Production 節點。正確結果因未碰需安家程式而是 rc0；若錯誤擴張 `g_code`，則會以測試檔啟動並錯誤拒收 Production。現有24控制不會翻紅。

判準：S5 是正式驗收條款，測試應加入上述「純測試＋非測試家節點」反控制，以殺掉路由集合誤用為啟動集合的實作。

風險逐類：

- 守衛：有上述兩項 blocking。
- 併發：無 finding；設計只讀索引／提交快照，不借工作樹。
- 效能資源：無 finding；兩版各多一次既有線性分類，沿用 shebang 快取，沒有新程序或持久資源。
- 回退：無 finding；局部移除廣視圖即可恢復舊判定，原安家、內容與逐提交帳保留。
- 外部送出：無；本機 Git／圖譜判定不發送網路請求。
- 不可逆：無；不遷移資料、不刪帳、不改外部狀態。

其餘已讀章節無 finding：問題與範圍、最小候選的安家／路由分離、S2/S3、既有紅燈、回退、實務隱患、REVISIT。固定節點 `Systems/每支檔有家` 為既有落點且圖譜鏡頭列出 0 條正式合約；未見提案破壞正式合約。

總結：最高 severity 為 major；blocking 2。唯讀環境不可建立 fixture，未重跑測試，不視為產品紅燈。

已讀材料完整：

- `governance/review-reports/test-home-writeback/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/test-home-writeback/preflight-intake.md`
- `governance/review-reports/test-home-writeback/r1-graph-context.txt`