# r2 收貨(2026-11-07,標準級:審查-sonnet + 架構對齊-sonnet,兩席都是新席)

兩席全數錨定、格式正規。全輪 2 條 minor;修補三問兩席都答「修補做到宣稱的、沒帶新問題」,本輪 2 條都不是 r1 修補造成(c1 是 r1 前就有的 --json 分支,d1 是 r1 前就有的索引寫法)。

| id | 席 | 一句 | 去向 | 重現 |
|---|---|---|---|---|
| c1 | 審查 | 計劃寫「完整檢查都另印」,--json 刻意不印沒交代、沒測試守純 JSON | 折:計劃補 --json 例外;加 ⑧ | HIT:把提醒挪進 --json 分支 → ⑧紅 |
| d1 | 架構 | catalog_unverified 用裸索引 c[1]、c[11],鄰居先取成具名變數 | 折:改成 name, src = c[1], c[11] | HIT:讀碼對照 check.py catalog_problems;來源欄索引改錯 → ③紅 |

## 先查世界

- PRIOR-ART: c1——CLI 機器可讀輸出模式只輸出結構化資料、提示走別的管道是通例(例:git 的 --porcelain 輸出格式保證穩定,https://git-scm.com/docs/git-status#_porcelain_format_version_1 );採用:--json 維持純 JSON 並用測試釘住。
- d1 是本 repo 內部寫法一致性,不涉外部做法。

## 改壞驗證

⑧、來源欄索引各改壞一次各自翻紅,還原後 `-k kt_catalog` 38 通過。
