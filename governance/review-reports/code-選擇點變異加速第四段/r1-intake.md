# code-選擇點變異加速第四段 r1 收貨紀錄

## 收貨(七席齊了才落地;報告從逐字稿原樣存)

- 材料:六席審程式與測試的 r1-code.patch(770 行;整份 1951 行超過 1800 行上限,拆包);資安席審整份 r1-snapshot.patch;合約與圖譜席兩份都給,引句錨在整份。
- 七份 quote-check 全錨(資安席 clean、沒有引句)、refcheck 全 ok;正確性、合約與圖譜、架構對齊三份只跑 `report-normalize --write` 搬等級行。
- 編號:正確性 c1–c3、資源 r1–r4、邊界 b1–b3、合約與圖譜 k1–k5、通才 g1–g2、架構對齊 a1–a3;資安 0 條。

## 先查世界

- PRIOR-ART:斷路器恢復時歸零失敗計數——常見實作在關閉狀態的成功處理清掉失敗計數、半開試探成功才關回(https://smallrye.io/docs/smallrye-fault-tolerance/6.3.0/reference/circuit-breaker.html 、https://hexdocs.pm/ex_resilience/0.4.0/ExResilience.CircuitBreaker.md)。採用:跳開與恢復時兩個連續計數都歸零(c1、r1、b1、k1、g1)。
- PRIOR-ART:重試的每次上限取「設定上限」與「剩下總期限」較小者,不替每次重試另給一個完整期限(https://oneuptime.com/blog/post/2026-08-14-retry-timeout-deadline-budget/view)。採用:重試上限 min(cap, 剩下時限)(c2、r3、b2、g2)。
- PRIOR-ART:Python `re` 沒有內建回溯保護,Sonar 建議能不用正規式就不用(https://rules.sonarsource.com/python/type/Security%20Hotspot/RSPEC-5852 、https://discuss.python.org/t/add-an-opt-in-timeout-parameter-to-re-to-mitigate-catastrophic-backtracking/107766)。採用:事件行改用字串切(c3、r2)。

## 發現與處置

| id | 席 | 一句 | 處置 |
|---|---|---|---|
| c1 | 正確性 1 | 恢復後 hang_streak 沒歸零,掛住一次就又跳開 | 折:恢復與跳開都歸零兩個計數;S3 補兩案 |
| c2 | 正確性 2 | 重試沿用同一個 cap | 折:min(cap, 剩下時限);S6 補一案 |
| c3 | 正確性 3 | 事件行正規式在長行上二次方 | 折:改字串切;S2 補長行一秒內解完 |
| r1 | 資源 1 | 同 c1 | 折:同 c1 |
| r2 | 資源 2 | 同 c3 | 折:同 c3 |
| r3 | 資源 3 | 同 c2 | 折:同 c2 |
| r4 | 資源 4 | 門檻 15 放大掛住的耗時 | 折:實務隱患寫明代價與 RETIRE-IF ② |
| b1 | 邊界 1 | 同 c1 | 折:同 c1 |
| b2 | 邊界 2 | 同 c2 | 折:同 c2 |
| b3 | 邊界 3 | Kotlin 反引號名含 `(` 對不到 | 折:實務隱患寫明(沿用既有 fullname 規則,只影響順序) |
| k1 | 合約 1 | 同 c1 | 折:同 c1 |
| k2 | 合約 2 | guard-kill WHY 沒跟上「只在找不到結果檔時重試」 | 折:改那行 |
| k3 | 合約 3 | 計劃四處舊說法 | 折:白話、PRIOR-ART、落點、不做、回退、依據來源都改 |
| k4 | 合約 4 | 計劃說 sh["init"] 改 None,程式沒做 | 折:改計劃寫法(那個值不再讀) |
| k5 | 合約 5 | 不帶腳本時只斷言 init 是 None,沒斷言照常合併 | 折:S1 補「指令跟不帶 init 一樣」 |
| g1 | 通才 1 | 同 c1 | 折:同 c1 |
| g2 | 通才 2 | 同 c2 | 折:同 c2 |
| a1 | 架構 1 | 新門檻不能注入 | 折:`_KillMerge(hang_breaker=…)`;S3 補一案 |
| a2 | 架構 2 | 跳開寫法複製兩份 | 折:抽成 `_kill_merge_trip` |
| a3 | 架構 3 | 加引號第三份複製 | 折:抽成 `_cmd_arg_quote`,`_run_cmd_expand` 與合併指令共用 |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| c1 | 15 次掛住 → pass → 1 次掛住,直接呼叫 `_kill_merge_breaker` | HIT:修前 hang_streak 16、又跳開 |
| c2 | 假 `_kill_run` 每次扣 70 秒、剩 100 | HIT:修前重試上限仍 100 |
| c3 | `"a > " * 60000` 餵 `_choice_merge_events` | HIT:修前數十秒 |
| k2 | 讀 guard-kill 第 68 行 | HIT |

## 修補後自我變異

- 恢復與跳開兩處歸零同時拿掉 → S3 兩案翻紅(單拿一處另一處接得住,兩處是同一行為的兩個入口);重試沿用 cap → S6 翻紅;門檻不從參數讀 → 注入那案翻紅;行首空白不擋 → S2 翻紅。
