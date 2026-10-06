severity: minor

## F1

severity: minor  
blocking: 否  
引句:「r1(2026-10-06,6席):3條/blocking 2/兩項守衛缺口及收據入口精度均折入」

「均折入」仍有鏡像缺口：本輪 `fold-check` 實際為 rc1。新加入的 S5「`--snapshot` 讀取失敗診斷」只出現在正文、未進 summary；既有 S1「`--snapshot` 與編碼錯誤」也仍是單邊。不能把目前狀態描述為鏡像已完整兜齊。

佐證 file: `docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md:72`  
佐證 file: `governance/review-reports/snapshot-encoding-preflight/r1-fold-checks.json:7`

## F2

severity: minor  
blocking: 否  
引句:「十份真實案例必須來自實際審查操作，測試/變異/人工注入收據不計入十份。」

receipt-F1 在計劃正文已擴成「編碼／I/O」配對案例、逐案例人工 JSON 格式，並明示未新增自動收集器；但落點 `Systems/design-loop` 的鏡像仍只寫「十份實際編碼拒收與恢復收據」。它漏掉 I/O 案例與人工蒐證邊界，後續只讀系統節點的人可能按較窄的舊口徑收貨。

佐證 file: `docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md:68`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:233`

其餘核對無 finding：

- 原 34／38／42 沒有與新 46 或獨立 24 混版。46 是 32/14；獨立 24 是 2/22。
- 生產 CLI52 未改；`cmd_canary` 仍保留原本延後至 hash 出口的 I/O 行為。
- S4 保留未知解析故障：廣捕捉 mutant 為 44/2，唯普通與 `-O` 的 `_quote_rows` RuntimeError 控制失敗。
- 五條最新規格閘只有 `--no-run` 的綁定、句式及回退形狀結果；材料沒有把它說成五條執行全綠。計劃中的「相依四支全綠」是歷史四支回歸，未與五條混稱。
- 十份收據只是未來人工蒐證格式，沒有冒稱已蒐到十份，也沒有宣稱建立 collector。

已讀材料路徑：

- `CLAUDE.md`
- `docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/design-loop.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-fold-diff.patch`
- `governance/review-reports/snapshot-encoding-preflight/r1-intake.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-logic.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-resources.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-rollback.md`
- `governance/review-reports/snapshot-encoding-preflight/r1-fold-source-bind.json`
- `governance/review-reports/snapshot-encoding-preflight/r1-quote-parser-broad-catch-mutant.json`
- `governance/review-reports/snapshot-encoding-preflight/r1-fold-checks.json`
- `governance/review-reports/snapshot-encoding-preflight/r1-fold-46-red.json`
- `governance/review-reports/snapshot-encoding-preflight/r1-fold-io24-red.json`
- `scripts/lumos`
- `scripts/test_lumos.py`