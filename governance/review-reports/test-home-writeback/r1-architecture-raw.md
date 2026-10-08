severity: clean

未發現 architecture finding。

## 架構逐問

① 分層：通過。提案只在既有分類入口加入預設關閉的較廣視圖，並限於 S13 路由比對；正式 `reqN/reqB`、`code_touched`、`g_code`、S13b 仍走原集合，沒有跨層直呼。對照 `scripts/lumos:27105`、`scripts/lumos:27511`、`scripts/lumos:27605`、`scripts/lumos:27638`；設計界線見 `governance/review-reports/test-home-writeback/r1-snapshot.md:29`。

② 命名與錯誤處理：通過。`include_tests` 被明定為提案 API、預設關閉，語意是形成「可核對路由檔」而非改寫需要安家的集合；現有呼叫端可維持預設語意。快照也保留讀取失敗、UTF-8、symlink、ignore 等既有排除，沒有新增例外處理支線。對照 `scripts/lumos:27105`、`scripts/lumos:27114`、`scripts/lumos:27118`、`governance/review-reports/test-home-writeback/r1-snapshot.md:29`。

③ 第二套做法：通過。測試辨認仍由 `_nodehome_is_test` 與 `_nodehome_layout` 提供，家仍由 `_home_map_from_notes` 算，逐提交仍使用 `_nodehome_commit_groups` 產出的 `g_paths/content_notes/own`；未另建分類器、owner 表或 commit 解析器。對照 `scripts/lumos:26770`、`scripts/lumos:26821`、`scripts/lumos:27144`、`scripts/lumos:27401`、`scripts/lumos:27444`。

④ lands_in：通過。唯一落點 `Systems/每支檔有家` 的責任範圍本來就涵蓋提交前、推送前的歸屬及寫回落點檢查；本案沒有形成需要獨立系統節點的新責任。對照 `governance/review-reports/test-home-writeback/r1-snapshot.md:10`、`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:6`、`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:67`。

## 風險逐類

- 守衛：未排除，但正反控制涵蓋 mixed、刪除、改名、逐提交隔離、ignore、symlink、JSON、無家及 S13b；承諾尚非實作證據。
- 併發：只讀已捕獲的索引／提交快照；不從工作樹猜版本，未新增共享可變狀態。
- 效能資源：兩版各多一次既有線性分類掃描，shebang 沿用快取；未新增程序或持久資源。
- 回退：局部移除較廣路由視圖即可，舊安家、內容、foreign-ref 與逐提交算法保留。
- 外部送出：無網路送出或外部副作用。
- 不可逆：無資料遷移、刪帳或不可回復操作。

因唯讀環境無可寫暫存區，未執行合成 fixture；已核對 HEAD、正式 CLI SHA-256 與指定測試原始碼，不把未重跑列為產品紅燈。

各節已讀無 finding：問題與最小範圍、最小候選、驗收條款、已有紅燈、回退、實務隱患、REVISIT、前掃收貨、固定圖譜落點。

總結：最高 severity clean；blocking 0。

已讀材料：`governance/review-reports/test-home-writeback/r1-snapshot.md`、`scripts/lumos`、`scripts/test_lumos.py`、`governance/review-reports/test-home-writeback/preflight-intake.md`、`governance/review-reports/test-home-writeback/r1-graph-context.txt`。