# code-選擇點變異加速第四段 r3 收貨紀錄

## 收貨(七席齊了才落地;報告從逐字稿原樣存)

- 材料:七席同一份 r3-snapshot.patch(1197 行,排除卷證與自動帳本),外加這輪差異 r3-repair.patch 與 r3-repair-binding.json;全席 `--reviewed` 填同一份快照的 sha(r2-記帳更正.md)。
- 七份 refcheck 全 ok;有引句的五份全錨,資源、資安兩份 clean 沒有引句。合約與圖譜那份 Finding 1 原寫 major 但 blocking 否,退回原席依它自己的判準重判,改成 major、blocking 是;架構對齊那份只跑 `report-normalize --write`。
- 編號:正確性 n1–n2、邊界 e1、合約與圖譜 k1–k5、通才 g1–g2、架構對齊 a1;資源、資安 0 條。
- 跑滿上限(3 輪)仍有 major:先查方向、攤人裁;使用者 2026-11-26 選「加開一輪」。

## 先查世界(方向)

- PRIOR-ART:驗收條款對測試的追溯——常見做法是每條驗收條款標覆蓋狀態(完整、部分、無),部分覆蓋的記缺口並補測試(https://cdn.jsdelivr.net/npm/@ptnglobal/bmad-method@4.43.1/bmad-core/tasks/trace-requirements.md 、https://cursa.app/en/page/traceability-linking-user-stories-criteria-scenarios-and-test-cases)。
- 方向:對 — k1 是 S2 條款被綁定測試部分覆蓋(有失敗那句只由第二段的測試守),補案例進綁定測試即可,不用換形狀。

## 發現與處置(同輪有 major,全部折入)

| id | 席 | 一句 | 處置 |
|---|---|---|---|
| k1 | 合約 1 | S2「快篩有失敗時照第二段的結果檔名單」綁定測試沒有有失敗案 | 折:events_order 補一案 |
| k2 | 合約 2 | 合併基準逾時帶事件後字樣變「逾時(跑到測試後掛住)」,BASE_WHY 沒對應、第二段 S10 沒註記、沒測試 | 折:BASE_WHY 加鍵、S10 標部分被取代、補斷言 |
| k3 | 合約 3 | `_kill_merge_failed_first`、`_kill_merge_screen`、classify、breaker、`_KillMerge` 的說明過期 | 折:改說明 |
| k4 | 合約 4 | 測試註解寫三案、docstring 少列新案 | 折:改註解與 docstring |
| k5 | 合約 5 | 計劃審計修正紀錄沒有代碼審各輪 | 折:補代碼審 r1–r3 條目 |
| n1 | 正確性 1 | gov 讀回 merge_init_off(含舊帳缺欄)沒有測試 | 折:補斷言 |
| n2 | 正確性 2 | SKIPPED 進通過層沒有測試 | 折:補解析案 |
| e1 | 邊界 1 | `{method}` 後面直接接 `&&`、`;`、`|` 時合併指令切錯 | 折:那一段含殼層元字元就判形狀不支援;補案 |
| g1 | 通才 1 | 重試條件比對字串字面 | 折:原因字樣收成常數,classify 與重試共用 |
| g2 | 通才 2 | `_KillMerge` 說明「只數計斷路器的那幾種」過期 | 折:同 k3 |
| a1 | 架構 1 | 累計原因三行複製三份 | 折:抽成共用函式 |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| k1 | 讀 t_choice_kill_merge_events_order 的 cases:hang、hang 殺、zero、hang 沒事件,沒有 fail | HIT |
| e1 | `_choice_merge_shape("./gradlew :app:testDebugUnitTest --tests {method}&& echo")` 回非 None | 待修時重現 |
| n2 | grep events_order 裡 SKIPPED | HIT:0 次 |

## regression_set

- 有證據屬上一輪修補造成:k4(修後新增案、註解沒跟上)。其餘原有漏查;k5 未判定。
