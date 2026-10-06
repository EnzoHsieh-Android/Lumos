severity: minor

## key-F1 — 快取測試會放過完全不重用版本清單的實作

severity: minor

blocking: 否

引句:「        check(f"清單快取/{commits}:存活版本有界且返回釋放",」

觀察：測試只驗 `peak <= 3 and not alive`。若完全移除 `route_cache`、每次都重新呼叫 `_nodehome_list`，wrapper 反而更快釋放，這個斷言仍會通過；測試也未核對同一 SHA 是否只列舉一次。

判準：圖譜宣告「父版先讀、線性相鄰提交可共用」。回歸測試應在取消重用時翻紅，而不只是證明容器最終可釋放。

具體輸入 → 錯結果：12 個線性混合提交，正確快取只需列舉 13 個唯一版本；無快取實作會列舉 24 次，重複執行完整 `git ls-tree`，成本隨提交數與 repo 路徑數放大，但現有測試仍綠。相關入口見 `scripts/lumos:27368`。

證據：已實跑無寫檔的等價生命週期量測，模擬 24 次「不快取、建立後立即解包」；結果為 `no_cache_calls=24 peak=1 alive=0 predicate=True`。因環境不允許建立 temp，未實跑改碼 mutant，也未把此限制算成產品問題。

建議：在現有 4／12 提交案例另外記錄 `_nodehome_list` 的 SHA 與呼叫次數，分別斷言 5／13 次且相鄰共享版本只讀一次；保留現有存活上限斷言，並增加「移除 cache」翻紅釘。

## 固定鏡頭節點判定

| 內容節點 | 判定 | 理由 |
|---|---|---|
| `docs/lumos-toolchain-knowledge/Systems/design-loop.md` | 不影響 | 未更動設計迴圈辨識、審材副檔名或條款綁定判定；快照變更只在載體成功記帳前增加輸入拒收。 |
| `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md` | 不影響 | 沒有改動 search 的 superseded／stale 濾網或三路輸出。 |
| `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` | 不破壞 | 非法 UTF-8／當次 OSError 在成功 canary 前返回；未知 RuntimeError 仍逸出。blocked 治理紀錄的既有追加語意未擴大。 |
| `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md` | 不影響 | 未改 impact 固定席、測試方法解析、真跑或 blocked 判定。 |
| `docs/lumos-toolchain-knowledge/Systems/guard-kill.md` | 不影響 | 未改 kill 狀態優先序或 JSON stdout 路徑。 |
| `docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md` | 不影響 | 未更動 vendored 清單、deinit 或授權檔頭。 |
| `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md` | 未直接破壞 | H/N 測試有合法種子、路徑／索引／競態前置斷言；但版本清單「重用」這項資源性質仍有 key-F1 的假綠缺口。 |
| `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md` | 不影響 | 未碰 reinject 或 sentinel 外內容保存。 |

其餘固定鏡頭節點只有名稱，依派工指示未展開。`r2-test-layers.txt` 實際為空，沒有推論缺少 UI 層。

目前程式確實使用兩版 `route_cache`，所以 key-F1 是回歸測試殺傷力不足，不是已發生的錯誤結果。H 的同次 read／check／hash 身份，以及 N 的正式程式啟動、合法候選、失敗時撤回額外測試證據，未發現其他 delta 問題。

未跑全套；已核對 HEAD、main 基線及 CLI/test SHA256 均與派工詞相符。檔名索引實際為 442 行，已讀完全部 442 行。

額外定點 context：

- `scripts/lumos:27121,27261,27312,27343,27368,27413,27567,27598,27895,27938,27954,28038,28420`
- `scripts/lumos:27261-27319`
- `scripts/lumos:27343-27412`
- `scripts/lumos:27425-27432`
- `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md`
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`

最高級：minor；blocking 數：0。

已讀材料：

- `governance/review-reports/code-convergence-input-guards/r2-source.patch`
- `governance/review-reports/code-convergence-input-guards/r2-graph.patch`
- `governance/review-reports/code-convergence-input-guards/r2-file-index.txt`
- `governance/review-reports/code-convergence-input-guards/r2-graph-lens.txt`
- `governance/review-reports/code-convergence-input-guards/r2-pitfalls.json`
- `governance/review-reports/code-convergence-input-guards/r2-dispositions.json`
- `governance/review-reports/code-convergence-input-guards/r2-test-layers.txt`