## 判定

**rollback-F2 不成立，整條反駁。** 原報的 `severity: major` 仍原樣保留在 [r1-rollback-raw.md](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/code-convergence-input-guards/r1-rollback-raw.md:21)，本次未改檔。

原報把「資訊沒有寫成 `[test:]` 機器關聯」推成「違反 AGENTS v1.0、會被 lint/note-shape 拒收」，這兩步都不成立：

- AGENTS v1.0 只要求 WHY 有出處、PITFALL 有出處和防回歸測試／重現；沒有要求兩者一律使用方括號。
- 這些資訊實際存在。
- 相關新行全在正文，不是 `summary`；實際 lint 與 note-shape 格子擋都不會拒收。
- 它們沒有 `KEY:★INVARIANT★`，不構成強制合約測試鏈。

## 逐項證據

| 新行 | 實際來源／測試 |
|---|---|
| design-loop 編碼 PITFALL／WHY，[patch 260–261](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/code-convergence-input-guards/r1-graph.patch:260) | 計劃明列既有 Issue、獨立查證與 Python 官方文件來源：[計劃 19](/tmp/lumos-review-snapshot-encoding-preflight/docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md:19)、[計劃 21](/tmp/lumos-review-snapshot-encoding-preflight/docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md:21)。測試 `t_canary_carrier_invalid_snapshot_encoding` 確實存在並驗非法編碼、RuntimeError、帳不變等控制：[test_lumos.py:25800](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:25800)。WHY 不另須測試鏈。 |
| design-loop 一次性 I/O PITFALL，[patch 264](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/code-convergence-input-guards/r1-graph.patch:264) | R1 原報精確描述首次讀取失敗、稍後雜湊恢復造成未驗追加：[r1-logic.md:11](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/snapshot-encoding-preflight/r1-logic.md:11)。測試在 [test_lumos.py:25909](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:25909)，涵蓋普通／`-O`、首次／已有帳、合法／非法UTF8／不錨材料；既有收據為 24/0：[integration-focused-green.json:22](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/snapshot-encoding-preflight/integration-focused-green.json:22)。 |
| 每支檔有家的中間版本 PITFALL，[patch 330](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/code-convergence-input-guards/r1-graph.patch:330) | `r1-intermediate-baseline-counter.json` 實際保存 middle-delete／middle-rename 的 `false → true → false` 前置條件與舊碼 rc1：[counter:7](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/r1-intermediate-baseline-counter.json:7)。測試方法列出三個 middle 案例並建構逐提交版本：[test_lumos.py:47979](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:47979)、[test_lumos.py:48027](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:48027)。 |
| 測試假綠的 pure-test／shebang PITFALL，[patch 373](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/code-convergence-input-guards/r1-graph.patch:373) | logic-F2 與 resources-F2 分別記錄誤啟動及工作樹／索引漏洞：[r1-logic-raw.md:21](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/r1-logic-raw.md:21)、[r1-resources-raw.md:16](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/r1-resources-raw.md:16)。變異收據明載 pure-test 2 條及 shebang 4 條翻紅：[mutation-evidence.json:3](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/mutation-evidence.json:3)、[mutation-evidence.json:27](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/mutation-evidence.json:27)。 |
| 測試假綠的廣捕捉 PITFALL，[patch 375](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/code-convergence-input-guards/r1-graph.patch:375) | resources-F1 明確指出原控制漏掉 `_quote_rows -> RuntimeError`：[r1-resources.md:9](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/snapshot-encoding-preflight/r1-resources.md:9)。後續測試已有 quote-parser fault 注入：[test_lumos.py:25828](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:25828)；44/2 mutant 收據也存在：[r1-quote-parser-broad-catch-mutant.json:5](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/snapshot-encoding-preflight/r1-quote-parser-broad-catch-mutant.json:5)。 |

另外兩條新增 WHY 的來源也存在：整合對照在 [integration-counter.json:4](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/integration-counter.json:4)，成本前後收據在 [cost-baseline.json:4](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/cost-baseline.json:4) 與 [cost-after.json:4](/tmp/lumos-review-snapshot-encoding-preflight/governance/review-reports/test-home-writeback/cost-after.json:4)。

## lint／note-shape 是否拒收

**不會。**

- 三篇目標行都在 frontmatter 結束後的正文：design-loop frontmatter 結束於第 162 行、目標在 232–236；另外兩篇目標在 91、607、609。
- `lumos lint` 只把 `summary` 送進前綴檢查：[scripts/lumos:6389](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:6389)、[scripts/lumos:6406](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:6406)。
- note-shape 的格子檢查也明確只收 `reg == "summary"`：[scripts/lumos:29542](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:29542)。
- 現有 pre-commit 呼叫沒有 `--slots`：[pre-commit:230](/tmp/lumos-review-snapshot-encoding-preflight/scripts/hooks/pre-commit:230)；程式在缺少該旗標時直接不啟動格子檢查：[scripts/lumos:29225](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:29225)。Git 歷史也查不到 `note-shape --staged --slots` 上線點。
- test-ref 檢查只驗已經寫出的 `[test:]`／`[test-gone:]`；不存在 `[test:]` 並不會產生違規：[scripts/lumos:29970](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:29970)。
- 合約掃描只認 summary 裡以 `KEY:★INVARIANT★` 開頭的行：[scripts/lumos:5126](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:5126)、[scripts/lumos:5156](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:5156)。本案新行均不符合。

## 是否實跑

實跑：

- `lumos lint Systems/design-loop` → rc0，0 問題
- `lumos lint Systems/每支檔有家` → rc0，0 問題
- `lumos lint Systems/測試假綠形態` → rc0，0 問題
- 執行前後 `docs/.governance-log.jsonl` SHA256 相同。

未重跑產品測試；測試存在與涵蓋範圍採靜態原碼及既有固定來源收據核對。未執行可能落治理 telemetry 的 note-shape CLI，該部分依實作與 hook 接線靜態判定。沒有修改任何檔案、帳、快取。