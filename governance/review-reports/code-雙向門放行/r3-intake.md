# r3 收貨(2026-09-17)

複核:r2 兩條(圍欄連結、家對照表唯一算法)通才席重跑測試確認關上;架構席 clean。

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-r3-sonnet | minor | HIT:同一行未閉合反引號之後的 [[連結]] 被 _strip_inline_markup 截掉,門訊號 2 漏偵測(既有「未閉合反引號後一律不信」取捨,訊號 1 同款) | accepted:既有取捨、要繞得刻意留反引號;列後續:連結掃描改只剝閉合的 code span |
| F2 | 單reviewer-r3-sonnet | minor | HIT:vault 在 repo 根時 vrel 為空,前綴比對永遠 False,靜默放行 | accepted:本工具鏈 vault 固定在 docs/ 下(CLAUDE.md);列後續:vrel 為空印一句放行 |
