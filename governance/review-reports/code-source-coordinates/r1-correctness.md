severity: minor

## G1 — 新增圖譜決策缺少必要的 `[因:]`

severity: minor  
blocking:否

引句:「WHY:用共用引用驗證入口修正行數，避免審查與表態各補一套規則」

file: `docs/lumos-toolchain-knowledge/Projects/引用座標依實際換行_計劃.md:21`  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md:56`  
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:173`  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:595`

本次新增的四條 `WHY:` 都有 `[出處:]`，但沒有圖譜紀律要求的 `[因:]`。具體結果是決策原因只能從自由文字猜測，不能按規定被機器辨識；四篇執行 `lumos lint` 仍各回報 `0 問題`，因此目前守衛也未攔住。應替四條各補上對應的 `[因:…]`。這不影響執行行為，故為非阻擋 minor。

程式 delta 未發現可成立的行為缺陷：工作樹與釘版共用 LF 分割；空檔、多個末尾 LF、CR/CRLF、BOM、`None`、目錄、無行號、tuple 與 CLI rc 均維持原語義。fixture 的 Git 環境、設定、hooks、簽章及逾時隔離也與主題相符。

固定席逐條：

- `lumos-refcheck`：實作符合 d1/d2，只改座標存在性，不擴張語意驗證；圖譜形狀問題見 G1。
- `bound-tests-gate`：五支測試名稱均存在，未改 gate 或綁定測試執行政策。
- `guard-kill`：rc 優先序與 JSON 純度路徑皆未變。
- `授權與歸屬`：未改 vendored 白名單；`scripts/lumos` 的 SPDX、MIT 全文及測試檔 SPDX 均仍在。
- `測試假綠形態`：測試先驗證有效 Python、兩個 LF、真 Git 提交與 fixture 隔離；形狀問題見 G1。
- `lumos-cli-lifecycle`：未碰 re-inject 或 sentinel。
- `lumos-cli-read`：未碰 search/superseded/stale 行為。
- `design-loop`：計劃材料為 `.md`，未改處置閘分類或綁定規則。

資料狀態五問：無持久格式遷移；無半寫；manifest 為即時衍生；正式 Git timeout 政策未變；沒有不可逆動作。

驗證限制：指定五測在本席唯讀沙箱中於測試啟動前因無可寫臨時目錄而停止，未冒充綠燈。另以純記憶體核對八種來源字元可編譯、空檔／多 LF 分割，以及 subprocess 的 CR/CRLF 正規化，皆通過。

已讀：

- `r1-source.patch`：219/219 行
- `r1-graph.patch`：249/249 行
- `r1-snapshot.patch`：僅取 SHA-256 `11fc627e…a0907`
- 已核對釘版 HEAD `92de0532`、base `48c7d58e` 及指定圖譜鏡頭

最高等級：minor；blocking：0。