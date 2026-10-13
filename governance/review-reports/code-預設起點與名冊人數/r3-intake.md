# r3 收貨紀錄(一般分級上限輪:單審+架構對齊,全新席,同門 sonnet;外家未派)

兩席引句全數錨定,載體選單審。單審席第 3 條自標 `severity: clean`(各情況核對無差異),不算發現。

## 機械重現表

| finding | 重現命令/查證 | 結果 |
|---|---|---|
| X1 | 單審席在暫存 repo 實跑:分支與標籤同名時 `git symbolic-ref -q --short HEAD` 回 `heads/foo` | HIT |
| X2 | 讀 `t_codeloop_default_base_prefers_newest_mainline`:上游 `refs/heads/main` 縮寫不含斜線 | HIT |
| Y1 | 讀 `cmd_loop_next`:`old_panel` 與 `disposal` 同一條件一正一反 | HIT |
| Y2 | 讀 `cmd_loop_next`:註解舊版殘留重複 | HIT |
| Y3 | grep `branch.*.remote` 只有這一處 | HIT(⚠) |
| Y4 | 讀 `Systems/pitfalls-code-loop` WHY 行 | HIT |

## 處置

- 全部 6 條 minor 放行。理由:這是一般分級上限輪(第 3 輪),本輪沒有 major;此時改程式就沒有任何全新席再看過修正差異。六條統一開 `Issues/預設起點與名冊人數收尾小問題` 追蹤,下一個小修 PR 照常走代碼審修掉。
- refuted:無。回歸:X1 是 r2 修補 V2 時帶進(原本用 `@{upstream}` 不吃分支名縮寫)。
