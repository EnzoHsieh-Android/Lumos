# r3 收貨紀錄(code-選擇點變異加速)

## 派工與收貨

- 2026-11-23 派七席(正確性、資源、邊界、整合、通才、架構對齊、資安),都是 sonnet 全新代理;修補鏡頭:修前 02fd3bdf5 → 修後 744f7b6d6。六席主審修補差異 r3-repair.patch(242 行),資安席讀整份 r3-snapshot.patch(2835 行,資安包不拆);派工依 r3-dispatch.json。
- 七席收齊才落地,報告從子代理逐字稿存檔(r3-<席>-sonnet.md)。
- 收貨三道:report-normalize 七份都已是正規化格式;quote-check 七份全數錨定;refcheck 資安席一條引用指向派工詞的鎖檔(席位自己說不存在),其餘全對得上。
- 修正關卡 r2 在 record 那步停(g2 撤回,見 r2-intake-更正.md),修正測試由編排者手跑 -k t_choice_kill 226 過 0 紅(r2-fix-evidence.txt)。

## 重現表

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| g1 | 通才 #1(major) | 編排者在 744f7b6d6 同時跑 4 份 `-k t_choice_kill_merge_screen_cap`:3 份 5 passed 1 failed、1 份 6 passed;紅的都是「r2 通才 #1 … 快篩有開跑」,log 顯示快篩沒走合併道(時限先被吃掉、合併沒啟用) | HIT,折入 |
| b1 | 邊界 #1(major) | 編排者在 744f7b6d6 暫存工作樹把合併基準呼叫的 `max(mg.remaining(), 1.0)` 換成 `1e9`,`-k t_choice_kill_merge`:132 passed、0 failed | HIT,折入 |
| b2 | 邊界 #2 | 讀碼與測試確認:`t_choice_kill_merge_budget_edge` 每支耗時都是 2.0,收手那步只有一筆實測,平均、總和、最後一筆、最大值算出相同 | HIT,折入 |
| c1 | 正確性 #1 | 同 b2(席位實測 `sum(measured) * left` 後 -k t_choice_kill_merge_budget 8 passed) | HIT,折入 |
| in1 | 整合 #1 | S20 條款字面是基準不綠的支不組進合併,`t_choice_kill_merge_no_lane_chunk` 守的是「配方一支都不在合併道不開快篩」,只寫在〈做法〉3 | HIT,折入 |
| in2 | 整合 #2 | 快篩上限受剩下時限約束、量基準中途重估兩條行為沒有條款句子(S4、S6 字面沒寫) | HIT,折入 |
| in3 | 整合 #3 | `git show 02fd3bdf5:docs/lumos-toolchain-knowledge/Systems/guard-kill.md` 有 `_kill_merge_in_lane`,744f7b6d6 版 0 筆 | HIT,折入 |

## 修補因果(--regression-set)

- g1:誤紅的案例是 r2 修補新加的端到端案例,修前不存在,機制由修補引入 → 修補造成。
- in1、in3:r2 修補新掛的綁定與拆 PITFALL 時漏帶 → 修補造成。
- b1:產品碼兩端相同,合併基準呼叫端在修補前就沒有測試守;r2 只替快篩補案例,沒補同族的合併基準 → 原有漏查。
- b2、c1:新測試的覆蓋缺口,修前沒有這支測試 → 不算回歸。
- in2:r1 加重估與快篩上限時就沒補條款句子 → 原有漏查。

## 先查世界

- PRIOR-ART:時限接線的測試(g1、b1)——查「真實睡眠造成的不穩測試」與「斷言傳入的逾時參數」:arti 專案明訂單元測試睡眠一律用模擬時間(真實睡眠反覆讓測試壞);Testing Library 與 Sinon 的假計時器文件用 spy 攔截計時呼叫、直接斷言傳入的延遲參數,或注入時鐘;Go 的 synctest 讓時間瞬間前進。採用:攔下 `_kill_run`,斷言快篩與合併基準兩處收到的逾時值不超過剩下總時限,不再靠真實睡眠觀察程序被收掉。排除:縮小睡眠與時限(本迴圈 r2 已證實在負載下隨機紅)。來源:https://gitlab.torproject.org/tpo/core/arti/-/issues/240 、https://testing-library.com/docs/using-fake-timers 、https://sinonjs.org/guides/how-to/fake-timers-async
- 方向:要換 — 時限接線這組連兩輪 major(r2 g1 快篩呼叫端沒守、r3 g1 新案例誤紅與 b1 合併基準呼叫端沒守),端到端靠真實睡眠的形狀換成攔截呼叫斷言參數;來源同上三個網址。使用者 2026-11-24 裁「再開第四輪」。
- PRIOR-ART:重估平均(b2、c1)——內部覆蓋缺口,補一個耗時不等(例 1 秒與 3 秒)的案例即可分辨平均與其他統計量,沒有外部做法要查。
- 其他組(條款綁定、筆記線索)是本 repo 內部一致性問題,沒有對應的外部做法要查。

## 處置

- 全部 7 條折入(r3 已到上限,使用者裁再開一輪,修補在 r4 由全新席審)。
