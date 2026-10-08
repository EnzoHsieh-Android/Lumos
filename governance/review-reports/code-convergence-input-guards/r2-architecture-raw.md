severity: major

## alignment-F1

severity: major  
blocking: 是

引句:「+                _qrows = _quote_rows(_rtext, _sbytes.decode("utf-8"))」

觀察：新路徑把 `_quote_rows` 放在捕捉 `OSError` 的區塊內；既有 report 解碼與 `cmd_quote_check` 都只捕捉讀檔／解碼，解析器呼叫在區塊外。

判準：只有快照本身的當次讀取或 UTF-8 解碼失敗可轉成輸入錯誤 rc2；解析器內部故障應逸出，不能偽裝成「快照檔案讀不到」。這是既有做法一致性，不是新增政策。

具體輸入 → 錯結果：使用合法 UTF-8 report/snapshot，令 `_quote_rows` 拋出 `OSError("parser-side")`。目前 `cmd_canary` 會回 rc2 並顯示 `--snapshot 指的檔案讀不到`；同一解析器在 `cmd_quote_check` 則會逸出。這會把內部解析缺陷錯報成投稿材料問題。

可執行證據：將 `t_canary_carrier_invalid_snapshot_encoding` 現有 `quote_fault` shim 的 `RuntimeError` 改成 `OSError`，預期目前會得到 rc2，而不是未知解析故障的 rc1／traceback。建議把 read/decode 留在 `try`，再於區塊外呼叫 `_quote_rows`。

file: `scripts/lumos:9580`  
file: `scripts/lumos:9538`  
file: `scripts/lumos:23290`

本席環境為唯讀，測試會建立暫存 vault，故未實跑此反控制；以上是逐句控制流推論，不把未跑冒稱收據。

## 唯一鏡頭其餘判定

- N 分層：不報。`_nodehome_mark_note_content` 仍是逐提交讀取／標記層；判定層只收到 `route_tests`／`staged_route_tests`，沒有跨層開 Git reader。
- N 分類：不報。新增 helper 借用 `_nodehome_is_test`、`_nodehome_required` 與既有 reader，沒有第二套測試分類器。
- N lightweight side：不報。雖手動組裝候選 side，但版本清單、首行讀取及正式 eligibility 都沿用既有原語，現有材料不足以證明產生第二套結果語意。
- N 錯誤返回：不報。版本清單失敗會清空該 group 的額外證據，未跨提交合成；正式程式退路保持原狀。
- H report 解碼：除 F1 外一致。載體 report 使用 bytes 嚴格解碼並保存同份 raw hash；非載體仍維持原替換字元行為。
- `r2-pitfalls.json` 的複雜度與測試閉包告警不屬此架構鏡頭，未當 finding。

## 固定圖譜鏡頭逐項判定

- `Systems/design-loop.md`：不影響；未改設計審 loop 類型、計劃載體或條款綁定判定。
- `Systems/lumos-cli-read.md`：不影響；未改 search 的 superseded/stale 濾網。
- `Systems/pitfalls-code-loop.md`：不影響；未改風險分級或 code-loop 流程。
- `Systems/bound-tests-gate.md`：不影響；未改 impact 固定席、綁定測試執行或 blocked 判定。
- `Systems/guard-kill.md`：不影響；未改 rc 優先序或 JSON stdout 純度。
- `Systems/授權與歸屬.md`：不影響；未動 vendored 清單、deinit 或 SPDX 檔頭。
- `Systems/測試假綠形態.md`：未破壞；新增測試有現場／版本／故障入口前置斷言。F1 是缺少另一例外類型的架構一致性反控制，不把新 PITFALL 自行升格成合約。
- `Systems/lumos-cli-lifecycle.md`：不影響；未動 CLAUDE sentinel 注入或外部內容保存。

## 已讀材料

- `governance/review-reports/code-convergence-input-guards/r2-source.patch`
- `governance/review-reports/code-convergence-input-guards/r2-graph.patch`
- `governance/review-reports/code-convergence-input-guards/r2-file-index.txt`
- `governance/review-reports/code-convergence-input-guards/r2-graph-lens.txt`
- `governance/review-reports/code-convergence-input-guards/r2-pitfalls.json`
- `governance/review-reports/code-convergence-input-guards/r2-dispositions.json`
- `governance/review-reports/code-convergence-input-guards/r2-test-layers.txt`

## 額外定點上下文

- `scripts/lumos:9519-9539`
- `scripts/lumos:9569-9598`
- `scripts/lumos:23276-23295`
- `scripts/lumos:27567-27585`
- `scripts/lumos` 的 55 行符號／解碼定位索引
- `/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md`
- `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md`
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`

最高級：major；blocking：1。