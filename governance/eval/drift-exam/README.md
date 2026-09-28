# 存量漂移考卷(rtb,2026-09-28)

給 [[Projects/存量漂移防線_計劃]] 量三道防線用:每道做完各考一次,看抓到幾題、誤報幾題。

- 來源:`governance/audits/2026-09-28-rtb-drift-rootcause/rootcause.md`(rtb 會談的根因稽核)§1 的 33 題抽樣與 §2.2 的逐處追溯。
- 被考的 repo:`/Users/enzo/rtb-mainwt`,稽核當時的主線 `067f005`;考試在它的 clone 上跑,不動原 repo。
- 33 題:漂移 20(機制① 9、② 5、③ 6)、屬實非漂移 10、不成立 3(A9 稽核判「邊界」,這裡記成不成立並在 notes 說明)。
- 每題的 `note`/`line`/`text` 是在 `067f005` 上逐題 `git grep -F` 找到、再用 `git show 067f005:<路徑>` 取第 `line` 行機械比對過,0 處不符(2026-09-28 本會談重驗一次)。
- 1.6(總索引漏列)與 1.7(引用已推翻決策)稽核沒點名抽的是哪 3 處,I1–I3、R1–R3 是整理時從它描述的母體裡挑的,各題 `sample_note` 有寫怎麼挑、怎麼確認。
- `mechanism` 與 `invalidating_commits` 照稽核 §2.2/§2.3;非漂移題為 null/空。
- `exam_event`:考法見 [[Projects/存量漂移防線_計劃]]〈做法〉第 3 節(`commit`、`status_replay`、`probe`、`current_state`);機制①的題標 `mechanism1_experiment`,給 [[Projects/舊句偵測實驗_計劃]]。

## 更正紀錄

- 2026-09-28 設計審 r1 正確性席查出:A5、A6、E1 三題的失效提交寫錯(A5 是 1eace79、A6 是 16136d6、E1 是 ef10bc7——把計劃 status 改成 done 的那個);A4、A5 的筆記在失效那時還是長檔名(之後 e8ea7d0 才改短),另加 `note_at_event` 欄記當時路徑(A4 的失效提交本來就對)。整理時只核對了原文、沒核對失效提交,這次用 `git log -G '^status:'` 逐題對過。
- 2026-09-28 設計審 r2 查出:B3 的失效提交也寫錯(b9c7496、8ff8c95 前後 Phase 12 計劃都已是 doing;讓「開工」成立的是 f183cd8,已改);D6 的 code_evidence 方向寫反(短名從來不存在,已改);`exam_event` 改成跟計劃〈做法〉第 3 節四種考法一致:`commit`(A4–A6、E3)、`status_replay`(E1、E2)、`probe`(A7、B1–B5,事件以 `rtb-2026-09-28-probes.json` 的 `event_commit` 為準)、`current_state`(非漂移題),機制①那 9 題標 `mechanism1_experiment`。
- 2026-09-28 設計審 r3 查出:B5 原文是「到 2026-12-31 時看有沒有啟動程式決定怎麼做」,日期才是觸發,改寫成純條件式會把它提早到 8ff8c95 擋人、改掉原意——從改寫檔拿掉,考法改成 `current_state`(照留日期式);B1、B2 原文是「事件或到某天」,改寫補上 `[by:2026-12-31]` 期限;E1、E2 加 `status_targets`(E2 的 7413936 同時把 Phase11B 與 Phase8 兩份計劃改成 done,兩份都要重放)。
- 考卷只適用於甲(狀態連帶)、乙(回頭條件)兩道防線;機制①那 9 題留給舊句偵測實驗([[Projects/舊句偵測實驗_計劃]])。
