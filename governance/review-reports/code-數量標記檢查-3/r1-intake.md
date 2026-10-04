# r1 收貨(code-數量標記檢查-3)

code-數量標記檢查-2 跑到 standard 上限 3 輪、第 3 輪仍有 major,使用者 2026-10-04 裁「照建議」:換編號破例再審一輪,重點驗第 3 輪的修法。
收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;兩席都沒動 repo(實驗在 /tmp/count3-work)。report-normalize 不用改;quote-check 全數錨定。本輪沒有 major。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 跑 /tmp/count3-work/eq.py 的 old()/new():`[test:a\0b]` | HIT:新版把原文的 NUL 刪掉,舊版保留 |
| F2 | 跑 star.py:`X=(1,2)` 後 `from m import *` | HIT:回 (2, None),星號 import 可能蓋掉 X |
| Z1 | 讀 `_strip_inline_markup` 說明 | HIT:還寫「全檔唯一」,沒講判定本體已經在另一支 |
| Z2 | 讀 `_count_rewrite` 的位置 | HIT:放在 `_drift_fix_*` 群裡,其餘 `_count_*` 在另一區 |

## 處置(全折)

- F1:判定本體改回傳「看不見的區段」而不是遮罩字串(拿字元當遮罩,原文本來有那個字元就分不清);兩個導出品各自從區段組。測試改成直接跟舊公式比、樣本含 NUL、先斷言樣本裡雙反引號與未閉合反引號都夠多;另跑 50 萬組隨機輸入跟舊公式 0 筆不同。
- F2:星號 import 判不了。
- Z1:`_strip_inline_markup` 說明補「判定本體在 _inline_hidden」。
- Z2:`_count_rewrite` 搬到其他 `_count_*` 旁邊。
