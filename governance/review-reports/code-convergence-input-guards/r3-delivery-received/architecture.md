severity: major

## delivery-架構對齊-codex-F1

severity: major  
blocking: 是

引句:「起終版本也不能共用一版設定；以固定變更集合、逐版設定及有界新宣告重讀釘住」

觀察：同一項「測試檔可否作為寫回路由證據」存在兩套版本政策。提交前路徑會分別從固定的新舊版本讀取設定與 vendored 狀態；推送範圍路徑卻把終點版本的 `cfg`、`skip` 傳給每個歷史提交及其父版本。因此，範圍後段若修改 `.lumos/config.json` 或 vendored 狀態，會倒灌到前段提交，造成舊提交的測試證據被錯誤放行或撤回。

這不是一般判斷錯誤，而是同功能的第二種來源機制：staged 以版本為真相來源，push-range 以終點設定重解所有歷史版本。

file: `scripts/lumos:29499`  
提交前路徑從捕獲樹讀新設定，並在 `29506–29512` 另讀起點設定及 vendored 狀態。

file: `scripts/lumos:29516`  
推送路徑的 helper 接受單一 `cfg, skip`，在 `29522–29535` 對父版及本版全部重用。

file: `scripts/lumos:30052`  
呼叫端只從 `tip_where` 建立設定及 vendored 狀態，並在 `30073–30074` 傳給所有提交群組。

本批新增：是；這條分岔隨新增的 `_nodehome_group_route_tests` 與 `route_cfg/route_skip` 傳遞路徑引入。

建議收斂：讓版本快取同時保存該 SHA 自己的檔案清單、reader、設定與 vendored 狀態，staged／push-range 共用同一個固定版本 snapshot loader。

## 逐節結果

- 載體快照輸入守衛：已讀，無架構 finding。讀取、UTF-8 解碼及解析例外的責任有分開；可修正輸入錯誤回傳 rc2，未知 parser 錯誤不被吞掉。
- 測試家寫回路由：發現 F1。
- 固定 Git readers／有界批次 reader：已讀，無其他 finding。新路徑沿用 `_nodehome_reader` 與 `_nodehome_cat_blobs_capped`，沒有另造 Git subprocess reader。
- 命名與錯誤回傳：已讀，無 finding。`_nodehome_*` 命名仍在既有邊界內；額外證據讀不到時撤回該證據、保留正式裁判的形狀一致。
- 修訂輪、跑滿回顧與技能文件：已讀，無 finding。詳細機制集中在 `templates.md` §3.1／§9，其餘入口採指路，未形成第二套執行框架。
- guard-kill 與圖譜文字調整：已讀，無架構 finding。

## 圖譜固定席逐條判定

- `Issues/canary-record未落盤事件`：影響；快照讀取或解碼失敗現在於追加帳本前明確 rc2。
- `Systems/lumos-cli-read`：不影響；search 的 superseded/stale 過濾路徑未改。
- `Systems/design-loop`：影響脈絡；新增修訂輪與回顧指路，但第五步條款閘 invariant 未改。
- `Systems/pitfalls-code-loop`：影響操作流程；修補鏡頭加入 code-loop，風險分級計算未改。
- `Systems/bound-tests-gate`：不影響；合約測試執行與阻擋條件未改。
- `Systems/guard-kill`：影響說明與驗證邊界；guard-kill 執行、rc 優先序及 JSON invariant 未改。
- `Systems/授權與歸屬`：不影響；vendored 授權檔規則與複製集合未改。
- `Systems/測試假綠形態`：影響；新增固定版本、ABA、測試家隔離等假綠案例；既有現場成立 invariant 未改。
- `Systems/loop-convergence-recording`：影響；`regression_set` 與跑滿回顧的因果判讀流程被補充。
- `Systems/lumos-cli-lifecycle`：不影響；CLI 啟停與生命週期未改。
- `Systems/reversibility-governance-ledger`：影響入口順序；快照錯誤先退出、不進 writer，帳本寫入器本身未改。
- `Systems/lumos-deinit`：不影響。
- `Systems/節點範圍與索引守衛`：不影響其執行邏輯；僅新增／更新圖譜節點與連結。
- `Systems/check-t-sentinel`：不影響。
- `Systems/doctor-irreversible-hint`：不影響。
- `Systems/check-r-guard`：不影響。
- `Systems/cochange-guard`：不影響。
- `Systems/lumos-refcheck`：不影響工具行為；文件仍沿用既有 refcheck 格式。
- `Systems/canary-audit`：影響；載體快照拒收與新驗證紀錄直接屬於此流程。
- `Systems/slim-get-一行安裝`：不影響。
- `Systems/slim-install-安裝器`：不影響。
- `Systems/slim-uninstall-一行卸載`：不影響。
- `Projects/雙向門放行_計劃`：不影響。
- `Projects/規格落成可驗收條件_計劃`：不影響。
- `Projects/引用座標依實際換行_計劃`：不影響。
- `Projects/逃逸自動記_計劃`：不影響。
- `Projects/異常派工單回報輸入錯誤_計劃`：不影響其派工單驗證；本批是載體快照與 home 路由。
- `Systems/core-invariant-baseline`：不影響。
- `Systems/judge-severity-gate`：不影響；修訂輪文件明文保留既有 severity／處置語意。

## 實讀與限制

- 固定 HEAD：已核對為 `c09d12037d1f0d5a5ce92bd09ccda1ed048a2319`。
- 指定 `architecture.patch`：757/757 行完整讀取。
- `graph-lens.txt`：57/57 行完整讀取。
- `source.patch`：實讀 1–375，共 375 行，涵蓋全部產品碼 delta；另搜尋 14 個 hunk 標頭。
- 固定版本鄰居程式：279 行。
- 規則：`lumos-project-notes` 94 行、`CLAUDE.md` 101 行，共195行。
- 派工文字：8行。
- 搜尋輸出：32行；HEAD／材料清單／行數等中繼資料23行。
- 受控總量：1726行，未超過1800行。
- 未讀：`source.patch` 376–1299 的測試實作正文、MOC全文、鏡頭中只列名節點的全文。因此不宣稱完整測試覆蓋；本次 major 由產品碼兩條相反的版本來源路徑直接成立。
- 未讀任何 `review-reports` 或其他席報告；未執行測試、未做 Git 實驗、未寫入 repo 或外部系統。