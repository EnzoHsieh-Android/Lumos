# code-android情境題盲判 r4 收貨(2026-11-07,跑滿上限後加開的一輪)

範圍:修補差異 `e7da27914..8adbef902`,265 行。兩席全新:通才(附角色卡)、架構對齊。修正關卡 r3 第二次才過(沒受影響那條第一次漏寫理由)。加開依據:r3 cap-decision extra-round 與已記的跑滿回顧 cap-retro.json。

## 收貨三道

- 正規化:兩份已正規化。
- quote-check:兩份全數錨定。
- refcheck:全對得上。

## 前輪驗收

- 第三輪 3 條:通才席在複本實跑帳尾 `\r`、`\r\n`、空檔、半行、捷徑,表態、盲判、pass/skip 寫完都讀得回;新測試改壞 4 處 3 處紅。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 通才-F1 | 席位複本把 `_codeloop_gov_log` 的 `except (OSError, UnicodeEncodeError)` 改回 `except OSError`,新測試 6 passed | HIT |
| 架構對齊-F1 | 讀 patch:`_codeloop_gov_append` 回的原因從 `{e}` 改成 `{e.__class__.__name__}` | HIT |

## 去向(這輪沒有 major,兩條附理由放行)

- 通才-F1(minor)放行:現行程式正確,只是少一條守它的測試;記進 [[Issues/治理帳與審查帳其他讀寫函式的硬化缺口]],跟同一支寫入器「寫不進去時靜默」那件一起補。
- 架構對齊-F1(minor)放行:原因字串只印給人看、例外類別名仍分得出是哪一類;同樣記進那篇 Issue。
