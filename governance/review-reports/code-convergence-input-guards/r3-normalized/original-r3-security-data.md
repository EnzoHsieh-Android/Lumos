severity: minor

security-data-F1
severity: minor
blocking: 否

引句:「比對 main cc032633 與本批修正後來源，_nodehome_evaluate 的 Ruff 複雜度皆為52；只有 def 新增 staged_route_tests 使原已放行的舊告警換指紋。辯方已獨立核對，並在測試家寫回計劃綁2026-10-20重驗；超過52就撤回這筆精確放行。」

觀察：新增 waiver `36c23613f0cfca05` 不只放行複雜度 52。強指紋只含 rule、檔名與命中程式片段，不含訊息裡的複雜度數值；呼叫端又只用 key 判斷放行。因此函式簽名不變時，未來升到 53 仍會被同一 waiver 靜默吃掉。

受影響：`.lumos/lint-waivers.json:2022`；佐證 file: `scripts/lumos:27752`、`scripts/lumos:27766`、`scripts/lumos:28043`。

判準：既然 waiver 合約明寫「超過52就撤回」，53 必須產生未放行結果，不能依賴日後人工記得撤回。

具體輸入：固定載入 `f6787629227f40761e0969ae6e871198551f3e35` 與 `95735eff7f3e17c930d43eecde5dd9d7c4fe9eff` 的 `scripts/lumos`、各版 `.lumos/lint-waivers.json`；使用同一 `_nodehome_evaluate` 定義行，只把 C901 訊息從 52 改為 53。

命令：以 `python3 -c` 從兩版來源 AST 擷取並實際執行 `_lint_new_norm_snippet`、`_lint_new_key`，載入同版 waiver 集合；全程記憶體內執行、未寫 fixture。

原輸出：

```text
f6787629 score=52 key=36c23613f0cfca05 weak=False waived=False
f6787629 score=53 key=36c23613f0cfca05 weak=False waived=False
95735eff score=52 key=36c23613f0cfca05 weak=False waived=True
95735eff score=53 key=36c23613f0cfca05 weak=False waived=True
```

後果：未來在不改函式簽名的情況下增加分支，`lint-new` 不會對超過 52 的回歸翻紅。評為 minor，因目前程式行為未直接受影響，受損的是單一函式的未來治理閘。

修補候選：讓 C901 waiver 額外保存並比較上限值，或令 C901 指紋包含解析出的實際複雜度；新增 52 仍放行、53 必須保留為新告警的測試。

保留候選：其他 rule、file、snippet 仍必須得到不同 key；既有 261 筆 waiver 值不得改動。這兩項已獨立核對，不能用「修掉 53」為由擴大其他 waiver 的失效範圍。

三問：

- 修復：部分成立。同一實際 Ruff 命令在修前、修後都報 `_nodehome_evaluate` 為 `52 > 10`；修前未放行、修後精確 key 已放行，因此目前的換指紋假紅確實解除。但「超過52撤回」尚未落成機械邊界。
- 保留：成立。語意比較為 261→262，新增僅 `36c23613f0cfca05`，removed 0、changed-existing 0；其他 rule/file/snippet 實驗仍未放行。anchor 的路徑集合沒有新增或刪除，只更新 `scripts/test_lumos.py` 雜湊與核可說明。
- 新發現：有，即 security-data-F1。

資料與控制盤點：

- `r3-file-index.txt` 與 `git -c core.quotepath=false diff --name-only c4f2b0cf..95735eff` 完整逐檔、同序吻合；836 檔、無重複，20 modified、816 added，無刪除。
- active 55：8 個明確控制／可執行檔、42 個 `docs/lumos-toolchain-knowledge/**` 現行圖譜輸入、5 個現行 ledger。
- 8 個明確 active：`.lumos/lint-waivers.json`、`governance/anchor-baseline.json`、`governance/review-reports/code-convergence-input-guards/r2-fix.json`、`scripts/lumos`、`scripts/test_lumos.py` 與索引末三個 skill 文件。`r2-fix.json` 未當成 archive。
- 5 個 active ledger：四個 `docs/.*-log.jsonl` 與 `governance/rel-cascade/**`；新增 rel-cascade 檔只有 header，沒有 terminal 事件，未新增抑制範圍。
- archive_only 781：`governance/replay/**` 4、`governance/research/**` 163、`governance/review-reports/**` 614；後者已排除 active 的 `r2-fix.json`。
- waiver raw diff 為 2360 行序列化／換序噪音；語意上只有一筆新增，換鍵序未被視為核可。
- anchor raw diff 12 行；anchor 路徑集合不變，只接受測試檔的新雜湊，沒有擴大受保護或可執行檔集合。

固定合約：

- design-loop 計劃格式／綁定測試：本席資料變更不影響；waiver 與 anchor 不參與 loop-id 或材料副檔名判定。
- search stale/superseded：不影響；沒有修改搜尋篩選資料或設定。
- bound-tests：資料範圍未擴張；anchor 仍是相同檔案集合。實際測試執行邏輯由其他席覆蓋。
- guard-kill rc 優先序：不影響；沒有新增可改寫 rc 的控制值。
- guard-kill JSON 純度：不影響；沒有新增 stdout／stderr 配置。
- LICENSE 不得 vendored：不影響；索引沒有 vendored 白名單配置變更。
- SPDX 複製檔要求：不影響；本席控制資料沒有改變複製集合。
- 假綠前置斷言：anchor 僅核可測試檔新雜湊，不等於測試有效性核可；其殺傷力不由本席宣稱。

已讀材料（完整）：

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-file-index.txt`：836 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-active-controls.json`：66 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 個邏輯行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 行
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 必讀合計：1405 行

額外定點上下文及行數：

- `governance/review-reports/code-convergence-input-guards/r2-fix.json`：110 行
- `scripts/lumos` 定點唯一上下文：235 行
- `governance/anchor-baseline.json`：19 行
- `governance/rel-cascade/c-20261006174706-73fdece2.jsonl`：1 行
- 審查額外上下文合計：365 行
- 專案入口指令 `AGENTS.md`：另讀 97 行，不作補丁證據

最高級/阻擋數：minor / 0。

三問未判定範圍：未跑全套；index、parser、cache 修補及其他席負責的完整來源／圖譜／控制覆蓋不由本席判定；archive_only 內容未執行，除明確 active 的 `r2-fix.json` 外未讀前輪席報告。