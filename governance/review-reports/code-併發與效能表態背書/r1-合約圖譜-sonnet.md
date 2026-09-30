severity: minor

合約與圖譜鏡頭:沒有破壞任何 ★INVARIANT★,沒有 blocker 或 major;三處文件或測試與計劃不一致,皆 minor。

已核對沒問題:七題清單與 SKILL.md、兩份 reference.md、Systems/棧別提問表態閘 WHY 一致;covers 更新規則符合 reference 與 S3;weak 三來源與文件一致;提醒單行、pre-push grep 提醒能轉印;補救順序三處一致;說明圖已更新(不在 snapshot patch 但在 HEAD);S1–S16 綁的 16 支測試都存在且全綠(contract_backing 30、contract_evidence 6、guard_kill 67、kill_recipe_key 6、kill_log_partial 3、dispatch_lens_shows 4、gov_stats_contract 2;另 guard_kill_rc_precedence 4、dispositions 100、stack_question 81 全綠);固定席 guard-kill 的 rc 優先序與 --json 純度合約仍綠,另兩篇沒有 ★INVARIANT★。

**G1**
severity: minor
blocking: 否,文件說法過時,不影響程式行為。
計劃第 7 項要改 Systems/棧別提問表態閘 的現況行、KEY 行與天花板段,diff 只加 WHY 與 REVISIT:第 35 行 KEY「錨點只抓最懶的謊——驗存在不驗內容」、第 90 行表格「不驗」寫成測試有沒有殺傷力、第 95 行天花板段沒提七題例外。未能重現為測試,是文件對照。
引句:「刻意偏離「寫入只驗形狀、證據推送前才驗」」
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:35`
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:90`
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:95`

**G2**
severity: minor
blocking: 否,後面的 WHY 有補,只是 FLOW 摘要不完整。
guard-kill 第 22 行 FLOW 仍只寫 kill-log 留痕,沒提 covers、recipe_id、head_sha、weak。
引句:「kill-log 每筆多 covers、recipe_id、head_sha」
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:22`

**G3**
severity: minor
blocking: 否,測試綠、邏輯正確,只是條款字面沒被完整覆蓋。
S1 沒驗推送前檢查;S7 只測兩支小函式,沒走 cmd_guard_kill 端到端驗補換行真的在寫入前被呼叫;S13 只驗 `_dispositions_verdict` 回傳 warnings,沒驗 check 實際印出的提醒行(`scripts/lumos:38168`)與 pre-push 轉印(`scripts/hooks/pre-push:450`)。
引句:「沒標的題寫表態時不加 backing、推送前檢查不多提醒」

其他:十處裡只有第 7 項(G1、G2)沒改全;全 repo 搜舊說法,現行文件沒再漏;README、ARCHITECTURE 不提 kill-log。

最高嚴重度:minor;blocking 0 條。
