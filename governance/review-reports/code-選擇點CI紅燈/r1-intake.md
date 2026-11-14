# code-選擇點CI紅燈 r1 收貨紀錄

PR #205(改動選擇點)合進主線後 CI 紅三支(t_command_index_complete、t_choice_kill_interrupt、t_ci_status_and_gov),本迴圈審修補 ff4cb0909。分級 standard:正確性一席、架構對齊一席,材料 r1-snapshot.patch 222 行。兩份報告引句全數錨定。

## 重現表

| id | 核對 | 結果 |
|---|---|---|
| c1 | `ci-wait` 寫 no-run、timeout-waiting 事件傳 `"run_id": None`(`_ci_record` 呼叫端);載入修後 scripts/lumos 跑 `_gov_event_types_ok({'run_id': None, ...})` 回 False | HIT |
| c2 | bool 是 int 子類,`{"run_id": true}` 通過;讀者 `_render_gov_choice` 只原樣取出 run_id,其他讀者轉字串或判 None | HIT |
| c3 | INDEX.md 只留 `choice-*(改動選擇點)`;`t_command_index_complete` 看 commands/*.md 全部,06 子檔有完整說明,測試綠 | HIT |

## 分組與處置

| 組 | 根因 | 條目 | 處置 |
|---|---|---|---|
| M1 | 型別表新增欄位時只核對了帳檔現存行,沒核對寫端會寫的值(ci-wait 的 null run_id) | c1 | 折:run_id 收 str、int、None;t_ci_status_and_gov 補一筆 run_id 為 null 的 no-run 事件,gov 要看得到(先紅);型別表標頭註解「現有的行一筆都不會被跳過」改成要連寫端一起核 |
| — | bool 當 run_id | c2 | 放行(minor,附來源):同表 attempt、ran 等整數欄位的既有行為,讀者沒有算術或切片 |
| — | 總目錄只留簡寫 | c3 | 放行(minor,附來源):總目錄 4.5k 上限是分塊設計(t_command_index_complete),完整情境說明在 06 子檔且總目錄指得到;餘裕不足另一件事,不在本修補範圍 |

## 先查世界
- PRIOR-ART:M1 本專案 `_GOV_FIELD_TYPES` 既有多型欄位寫法 `"round": (str, int, type(None))`、`"secs": (int, float, type(None))`;採用同形,不另寫判斷。
- 排除:只看帳檔現存行判斷欄位型別(這次 c1 正是這樣漏掉寫端的 null)。

## 回歸因果
- 有證據的修補不完整(非新回歸):c1 在修補前也被跳過(修補前 run_id 只收 str),修補只補了 int。
- regression-set none。
