# r2 收貨紀錄(lumos事件帳)

- 四席報告格式正規化:全數已是正規化格式;架構席原稿 F4、F5 的 severity 行尾附 ⚠,編排者把 ⚠ 搬進同條 blocking 判準句,等級值不變。
- quote-check:四份全數錨定 r2 快照。
- refcheck:`governance/runtime/` 相關與 `docs/knowledge/` 報不存在——執行期才建、或是圖譜佈局名稱,預期。

## 編排者重現表

| id | 宣稱 | 重現指令 | 結果 | 處置 |
|---|---|---|---|---|
| c1 / h1 | `cmd_teardown` 直呼 `_teardown_global_hooks`,不經 `_teardown_global_claude` | `grep -n "_teardown_global_hooks(Path(__file__)" scripts/lumos` | HIT(cmd_teardown 第①步兩行直呼) | 折 |
| c1 / h1 | `_teardown_global_claude` 只是相容包裝、無指令呼叫者 | `grep -n "_teardown_global_claude" scripts/lumos` | HIT(只有定義一處) | 折 |
| c1 / h1 | `cmd_uninstall` 不碰全域 hook、開頭有探針拒絕 | 讀 `cmd_uninstall` 開頭 8 行 | HIT | 折 |
| h1 | `_teardown_global_hooks` 設定檔壞時提前返回 | 讀 `_teardown_global_hooks` 第①段 | HIT | 折(改掛 cmd_uninstall 一併避開) |
| e2 | 只有 `session.end` 的輸入帶 `sessionId` | 型別檔 `SessionEndInput` 與 `TurnCompleteFields`、`ToolCallInput` | HIT | 折 |
