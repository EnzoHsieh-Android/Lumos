severity: minor  
blocking:否  
file:line：`docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:62`  
引句:「有綁測試的節點是個位數,交集是集合運算」

實測目前是 432 篇節點，其中：

- 綁測試節點：10 篇，不是個位數
- 綁測試合約行：25 條
- 已抽出的正文路徑：48 個

數字雖錯，但方案的純成本確實便宜：載入後掃合約約 1.01 ms、十篇正文抽路徑約 4.12 ms、2354×48 的集合交集平均約 1.77 μs。應修正文案與基準，不構成否決理由。

### 其餘實測結論

- S3 首推成立：`pre-push` 已從 stdin 取得 `local_sha`，新 ref 轉成 `EMPTY_TREE..local_sha`，見 `scripts/hooks/pre-push:24-31,127-135`。實跑 `git diff --name-only EMPTY_TREE..HEAD` 取得 2354 檔，約 0.02 秒。
- S6 改動面不大：治理帳 mapper 已保留 `kind`，且去重鍵已包含 `gate + kind`，見 `scripts/lumos:3859-3861,3898`。主要是 `_render_gov_stats` 增加 bound-tests 子分類與測試；`gov --stats` 現行約 0.43 秒。只要把子表限定在 `gate=bound-tests`，不必改其他閘的既有總表欄位。
