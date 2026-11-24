# r4 收貨紀錄(code-選擇點變異加速)

## 派工與收貨

- 2026-11-24 派七席(正確性、資源、邊界、整合、通才、架構對齊、資安),都是 sonnet 全新代理;修補鏡頭:修前 744f7b6d6 → 修後 100d3851c。六席主審修補差異 r4-repair.patch(250 行),資安席讀整份 r4-snapshot.patch(2866 行);派工依 r4-dispatch.json。這一輪是 r3 到上限後使用者裁「再開第四輪」加開的(cap-decision extra-round、cap-retro.json 已記)。
- 七席收齊才落地,報告從子代理逐字稿存檔。
- 收貨三道:report-normalize 七份都已是正規化格式;quote-check 第一次架構對齊席 2 句、資源席 1 句錨不到(引句跨多行,比對逐行),純格式退回原席只改成單行引句、結論不動,重交後七份全數錨定;refcheck 全對得上。
- 修正關卡 r3:全部通過(r3-fix-check.txt)。

## 重現表

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| g1 | 通才 #1(major) | 編排者在 100d3851c 暫存工作樹把重估的 `sum(measured) / len(measured) * left` 換成 `min(measured) * left`、`measured[0] * left`,`-k t_choice_kill_merge`:兩種都 136 passed、0 failed | HIT,折入 |
| b1 | 邊界 #1 | 同 g1 的 `min(measured)` 重現(同一缺口,邊界席判 minor) | HIT,折入 |
| b2 | 邊界 #2 | 合併基準呼叫端 `max(mg.remaining(), 1.0)` 換成 `mg.remaining()`,`-k t_choice_kill_merge` 136 passed、0 failed | HIT,折入 |
| b3 | 邊界 #3 | 單支基準 `cap = min(full, max(mg.remaining(), 1.0))` 換成 `min(full, mg.remaining())`,`-k t_choice_kill_merge` 136 passed、0 failed | HIT,折入 |
| in1 | 整合 #1 | 席位在 after 版把 `_kill_merge_emit` 的存活列加帶 `judged`,ledger_counts/all_survive/new_params/no_lane_chunk 四支全綠;讀碼確認 ledger_counts 用假的 cmd_guard_kill、S12 的「列不帶 judged」只在 merge=None 時跑 | HIT,折入 |

## 修補因果(--regression-set)

- g1、b1:r3 修補加的耗時不等案例(1、3、1 秒)分得出總和、最後一筆、最大值,分不出最小值與第一支;修前案例(全部 2 秒)同樣分不出 → 原有漏查,不是修補造成。
- b2、b3:產品碼四輪都沒動,「最少 1 秒」的保底從來沒有測試 → 原有漏查。
- in1:r3 修補新加的 guard-kill PITFALL 把它登記成有測試守,但測試本來就守不到 → 原有漏查(修補只是讓缺口被看見)。
- 判過,沒有修補造成的回歸 → none。

## 先查世界

- PRIOR-ART:時限與重估的測試缺口(g1、b1、b2、b3)——延續 r3 已查的方向(攔截呼叫斷言傳入的值、不用真實睡眠;來源 https://gitlab.torproject.org/tpo/core/arti/-/issues/240 、https://testing-library.com/docs/using-fake-timers),這輪補的是同一形狀下漏掉的輸入值:選一組讓平均跟最小值、第一支算出不同決定的耗時(1、5、1 秒),以及剩下時限已用完(負數)時「最少 1 秒」的保底。變異測試的做法是對每個存活變異挑一個能區分它的輸入(https://nwyin.github.io/irradiate/guide/surviving-mutants/)。
- 方向:對 — r3 換的形狀(攔截呼叫)這輪四席都驗過能抓呼叫端改壞;剩下的是輸入值沒挑齊,不是形狀錯;來源同上。
- PRIOR-ART:in1 是本 repo 內部的測試覆蓋問題,沒有外部做法要查。

## 處置

- 全部 5 條折入。r4 是加開輪,使用者睡前授權「重現仍有 major 可自行修補、跑 r5 一輪,r5 再有 major 就停」(2026-11-24)。
