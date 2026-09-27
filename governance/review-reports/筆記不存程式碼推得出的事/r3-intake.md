# r3 收貨紀錄(筆記不存程式碼推得出的事,設計審)

凍結材料:r3-snapshot.md(= r3-work.md,編排者 r3 前改寫後的整份,130 行)、r3-delta.patch(相對 r2 快照)。分級 high。
6 席全新:正確性 opus;邊界、接手、併發、架構對齊 sonnet;外家否決 Codex(從 clone 目錄啟動)。全部收齊前沒動被審材料。

## 收貨三道

- report-normalize:6 份最後都已正規化。併發席總結句寫了「無 blocker」被判成總結藏更高等級、架構對齊席 F4 的等級寫成 ⚠——兩份都請該席自己改(只改那一行,內容不動),改完重收。
- quote-check:6 份全錨定(對 r3-snapshot.md)。
- refcheck:併發席 1 個 missing,其餘全對得上。
- seat-check:派工單材料欄照 r2 同形。

## 編排者重現

| 發現 | 重現 | 結果 |
|---|---|---|
| r3a-F3 / r3c-F2 範圍函式回的是集合、不帶行號、刪掉的行還在 | 讀碼:`_ns_range_added` 以 set 收文字、丟掉行號(`dest.setdefault(p, set()).update(t_.strip() for _n, t_ in rows …)`) | HIT(讀碼確認;正確性席另在 /tmp 實測) |
| r3b-F1 第三處寫死提交前掛鉤 | 讀碼:`_ns_range_added` 裡逐提交判上線讀 `{sha}:scripts/hooks/pre-commit` | HIT(讀碼確認) |
| r3c-F3 初始化不會寫忽略設定 | 讀碼:`_scaffold_project` 只寫 docs/.gitignore、`_init_additive_setup` 只寫 governance/.gitignore;根 .gitignore 裡的 .lumos 條目是本 repo 手寫 | HIT(讀碼確認) |
| r3b-F5 〈擋什麼的初步實測〉查無此篇 | `grep -n 擋什麼的初步實測` 於 Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md → 第 127 行是那個段落標題 | MISS(段落存在,席位拿檔名去找) |
| 其餘條目 | 皆為設計層論證(計劃文字與程式現況的對照),各席附 file:line,引句全錨定;逐條去向見重寫稿 | 採信,折進重寫稿 |

## 處置

35 條:34 條折進重寫稿 [[Projects/筆記內容審_計劃]](逐條去向見該篇〈前身 r3 發現怎麼處理〉),1 條駁回(r3b-F5,見上表)。輪內有 blocker(r3b-F1),已折。
核心設計的洞修法等於重寫,Enzo 2026-09-27 裁「重寫、開新一輪審查」;本編號以 `loop rewrite` 收尾,後繼編號 筆記內容審。
