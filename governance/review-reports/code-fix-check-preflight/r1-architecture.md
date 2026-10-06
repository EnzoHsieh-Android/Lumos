severity: clean

blocking: 否

未發現架構一致性問題。

### 架構三問

1. 分層／依賴方向：對齊。前置判斷仍位於 `cmd_loop_fix_check` 編排層，沿用 `_fix_item_record`、`_fix_item_repeat`、測試索引、`_spec_gate_judge_items` 與 `_bound_tests_check`，沒有跨層直呼或新增 runner。

file: `scripts/lumos:12480`  
file: `scripts/lumos:12549`  
file: `scripts/lumos:12799`  
file: `scripts/lumos:12835`  
file: `scripts/lumos:12873`

2. 命名、錯誤回傳、日誌：對齊。`preflight_failed`、`not_run_items` 與既有 `items_fail`、`failed_items` 語意一致；失敗仍回 rc1、寫一筆 `warned`，事件寫入失敗仍不改判定。隔離工作樹仍由原 context manager 收尾。

file: `scripts/lumos:1535`  
file: `scripts/lumos:12735`  
file: `scripts/lumos:12835`  
file: `scripts/lumos:12894`  
file: `scripts/lumos:12897`

3. 是否出現第二種做法：否。新欄位緊鄰 `failed_items` 接入同一 `_GOV_FIELD_TYPES` 與 `cmd_gov` mapper；JSON、治理事件及人類可讀提示只是同一判定的不同輸出面，沒有平行狀態機或第二套治理帳讀法。

file: `scripts/lumos:8303`  
file: `scripts/lumos:8371`  
file: `scripts/lumos:8388`  
file: `scripts/lumos:12895`  
file: `scripts/lumos:12904`

### 圖譜固定席逐項對照

- `reversibility-governance-ledger`：一致。`not_run_items` 同步加入型別表與 mapper；舊列缺欄保持 `None`，錯型別仍由共用讀側略過。
- `bound-tests-gate`：一致。有效前置條件仍真跑 `_bound_tests_check`；動態修正測試紅仍繼續跑合約測試，前置失敗則明示 `bound-tests` 未執行，不偽裝成綠。  
  file: `scripts/lumos:12839`  
  file: `scripts/lumos:12873`
- `guard-kill`：無衝突。本 delta 未改 guard-kill 的 rc 優先序或 JSON 輸出，亦未新增旁路。
- `授權與歸屬`：無衝突。未變更 vendored toolkit、deinit、LICENSE 或 SPDX 路徑。
- `測試假綠形態`：一致。測試以 runner 日誌確認零啟動，並對有效、修正測試真紅、合約真紅三案確認兩段實際執行及原判定保留。  
  file: `scripts/test_lumos.py:69587`  
  file: `scripts/test_lumos.py:69661`
- `lumos-cli-read`：無衝突。未改 search、superseded 或 stale 篩選。
- `lumos-cli-lifecycle`：無衝突。未改 re-inject 或 CLAUDE.md sentinel。
- `pitfalls-code-loop`：無第二套 code-loop 行為；圖譜 delta 僅追加既有驗證引用，本次程式行為集中在 fix-check。

### 查證範圍

- 已逐行讀完 `r1-source.patch`：307/307 行。
- 已逐行讀完 `r1-graph.patch`：347/347 行。
- `r1-snapshot.patch` 僅核對 3399 行及 SHA-256，未讀內容。
- 已讀全部八個有內容的圖譜固定席；只列名節點未展開。
- pitfalls manifest：`tier=standard`，`stack_questions_applicable={}`。
- 嘗試執行 `python3 scripts/test_lumos.py -k fix_check_preflight`，但唯讀沙盒沒有可寫暫存目錄，測試框架在啟動前以 `FileNotFoundError: No usable temporary directory` 結束；這不是被審程式失敗。

最高等級：clean  
blocking 條數：0