# code-android情境題盲判 r3 收貨(2026-11-07,末輪)

範圍:修補差異 `ffb47f857..e7da27914`,1625 行一包。兩席全新:通才(修補差異加前輪驗收,附角色卡)、架構對齊。修正關卡 r2 第三次才過(修正紀錄的函式錨點第一次指錯函式、第二次多一個括號)。

## 收貨三道

- 正規化:兩份已正規化。
- quote-check:兩份全數錨定。
- refcheck:全對得上。

## 前輪驗收

- 第二輪 13 條:通才席與架構對齊席核對皆修好;`_ledger_lines_having` 與 `_ledger_lines` 通才席用 20 萬份亂數帳比對結果完全一致。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 通才-F1 | 席位臨時複本:帳尾沒換行時跑 `code-loop dispositions`,印成功、新事件黏在舊最後一行後面、`_codeloop_read_dispositions` 回 None;讀碼:`_codeloop_gov_append` 直接寫,同檔 `_gate_event` 有 `_ledger_tail_needs_newline` 補換行 | HIT |
| 架構對齊-F1 | 讀碼:`_ledger_lines_having` 有 `\r` 時退回 `_ledger_lines`、沒有時只認 `\n` | HIT |
| 架構對齊-F2 | 讀碼:`_codeloop_read`(pass/skip)仍標記檔優先 | HIT(既有做法) |

## 先查世界

PRIOR-ART:只追加的帳寫入前補行尾換行——本 repo 主寫入器 `_gate_event` 已用 `_ledger_tail_needs_newline` 先補 `\n` 再寫(JSON Lines 規格每筆一行、以換行分隔,https://jsonlines.org/ );採用:`_codeloop_gov_append` 照同一支函式補,不另寫判斷。

## 分組與去向(輪內有 major,全數折入)

- 甲 帳尾換行:通才-F1(major)→ `_codeloop_gov_append` 寫入前用 `_ledger_tail_needs_newline`;補先紅測試(帳尾沒換行時寫表態、寫盲判,寫完讀得回,前一行不被吃)。
- 乙 找行與切行同步:架構對齊-F1(minor)→ 由既有等價測試守(修補時加的 300 份亂數帳比對);修補時確認它綁在 `_ledger_lines` 等價關係上。
- 丙 pass/skip 仍標記檔優先:架構對齊-F2(minor)→ Systems/棧別提問表態閘補一行 REVISIT,另開 Issue 記同族。

## 跑滿上限

這是 standard 的第三輪(上限),輪內有 major 不能放行。依使用者先前授予的裁量權記 cap-decision extra-round(修法小、加一輪代價低),並依手冊派乾淨代理起草跑滿回顧。
