preflight-4: ran

# 代碼審試行改道：設計審第 1 輪前掃

2026-10-04，唯讀前掃先核四類：未定義詞、壞引用、內部矛盾、機械宣稱的語意。`lumos refcheck` 回 `missing=0, out_of_range=0`，`prose-lint` 無命中，`pitfalls --check` 有實務隱患節；`spec-gate` 判高風險、S1–S6 六條全靠人工驗收、相依兩支測試綠。這些不是設計審 PASS。

| 前掃 id | 原稿缺口與證據 | 凍結前修正 |
|---|---|---|
| P1 | 「本段設計審正式 PASS」未指新 loop；舊 `review-repair-pilot` 的 PASS 只驗舊快照，拿新版計劃重算 `G3 hash` 失敗。 | 指定 `review-repair-pilot-decouple` 對凍結新版計劃的 `loop status --disposal` PASS，另以 Verification 記 hash 和生效時刻；舊 PASS 不借用。 |
| P2 | 「首次開工」可指開始實作或首輪派工，A 先實作晚派、B 晚實作早派會產生不同樣本順序。 | 唯一時鐘改成修改程式／審查前的候選登記時刻；首派只算審查耗時。同秒照持鎖寫入先後。 |
| P3 | 原稿只靠口頭「單一寫入者」，兩會談可同時讀到空表各自領第2案。 | 唯一計劃位置用原子 `mkdir` 短鎖護候選／交接寫入，表記協調者與 active 狀態；殘鎖不自動搶占。 |
| P4 | 一處寫獨立 worktree，另一處 `worktree／分支`；只切分支仍會載入目前未提交探針草稿，審材與測試現場不一致。 | 一律要求另一個獨立乾淨 worktree，記基準提交與差異範圍；branch-only 不算隔離。 |

前掃四條由同一席提出，原始逐字引句與對照位置保留在該席回覆；上述修改均在本輪凍結前，故不計作正式席 finding。接下來全席需重查這四處及新舊計劃銜接，不能把前掃當成正式放行。
