# r1 收貨紀錄(code-選擇點變異加速)

## 派工與收貨

- 2026-11-23 派七席(正確性、資源、邊界、整合、通才、架構對齊、資安),都是 sonnet 全新代理;材料依 r1-dispatch.json,凍結 patch 2594 行超過 1800 行,拆成三包(A:lumos、Systems、skills;B:test_lumos.py 與計劃;C:knowledge、skills、lumos),資安席拿整份。
- 七席收齊才落地,報告從子代理逐字稿存檔。
- 純格式退回:派工範本要求「最後一行總結 max severity」,六席把最後一行寫成 `severity: …` 或 `max severity: …`,收貨工具把它當成多一條發現(正確性席因此多出一條假 major)。六席都退回原席,只改最後一行成「總結:最高嚴重度 X」,發現內容沒動;report-normalize 對七份都回「已是正規化格式」。這個範本衝突記成工具問題待開單。
- 收貨三道:quote-check 除資安席外全數錨定;資安席判 clean、0 條,沒有引句可驗。
- 圖譜鏡頭:資安席回報派工詞尾端沒附固定席節點,資源席回報「計算超時」。可能原因是會談開在 shearwater 工作樹、審查範圍的 base 不在它的主線上(鏡頭照規則改附 LUMOS-LENS 說明或備援段);席位照派工詞讀了真碼查證,結論不受影響。下一輪派工前先暖快取、確認鏡頭附得上。
- 席位臨時目錄 /tmp/lumos-seat-work/code-選擇點變異加速/ 在本輪收尾後刪除。

## 重現表

重現在 orch 複本上做(紀錄:/tmp/lumos-seat-work/code-選擇點變異加速/orch-repro.log;要點抄在下面)。

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| c1 | 正確性 #1(major) | 照席位情境縮小(總時限不夠量齊基準):合併模式 rc2、判出 0 個壞法、只跑了三支基準;同一輸入 `--no-merge` 判出 1 個 | HIT,折入(修正 1) |
| c2 | 正確性 #2 | 讀碼確認:看停止旗標之後、合併程序登記之前收到第一個訊號,回呼找不到要收的程序,整支合併呼叫照跑完;修補後測試修前實測等滿約 60 秒 | HIT,折入(修正 2) |
| rs1 | 資源 #1 | 同 c2 | HIT,折入(修正 2) |
| rs2 | 資源 #2 | 讀碼確認快篩逾時只取 max(合併基準×5, 下限),不看剩餘總時限 | HIT,折入(修正 3) |
| rs3 | 資源 #3 | 同 c1 根因(量齊夠不夠用固定單價估) | HIT,折入(修正 1) |
| rs4 | 資源 #4 | 讀碼確認單支基準沒有合併標記;第一個訊號照既有逐支流程等那一支跑完 | 放行,理由見下 |
| b1 | 邊界 #1(major) | 拿掉合計 64MiB 上限,-k choice_kill_merge 相關 18 支照綠 | HIT,折入(修正 4) |
| b2 | 邊界 #2(major) | 拿掉中斷時的還原,相關 6 支照綠 | HIT,折入(修正 4) |
| b3 | 邊界 #3(major) | 快篩上限改成只用下限,相關 109 支照綠 | HIT,折入(修正 3、4) |
| b4 | 邊界 #4 | 讀碼確認卡線值(45 秒、rc 127/128、剛好等於上限)沒有案例 | HIT,折入(修正 4) |
| b5 | 邊界 #5 | 讀碼確認假 Gradle 的超大輸出模式只寫第一個案例,跟真 Gradle 每支都寫不同 | HIT,折入(修正 4) |
| b6 | 邊界 #6 | 讀碼確認量基準期間總時限到的路徑沒有案例 | HIT,折入(修正 4) |
| in1 | 整合 #1 | 計劃寫「沒啟用合併的原因印到標準錯誤」,程式不印 | HIT,折入(修正 8:計劃改成照程式) |
| in2 | 整合 #2 | 計劃寫 base_secs「沒量齊是 0」,程式量一半也累加 | HIT,折入(修正 8) |
| in3 | 整合 #3 | 讀碼確認 gov --stats 不讀新欄位 | 放行,理由見下 |
| in4 | 整合 #4 | 讀碼確認 on_row 列上的 judged 沒有讀者 | HIT,折入(修正 6) |
| g1 | 通才 #1 | 同 in4,另有 finish 裡的死分支 | HIT,折入(修正 6) |
| g2 | 通才 #2 | 讀碼確認沒有任何一支在合併道裡時照開一次快篩,而且記成 merged | HIT,折入(修正 5) |
| g3 | 通才 #3 | 讀碼確認斷路器只數沒跑乾淨,不數有失敗 | 放行,理由見下 |
| g4 | 通才 #4 | 同 c2 | HIT,折入(修正 2) |
| g5 | 通才 #5 | guard-kill 那條 WHY 帶了複雜度數字 | HIT,折入(修正 9) |
| a1 | 架構對齊 #1 | 讀碼確認合併標記掛在 Popen 物件屬性上 | 放行,理由見下 |
| a2 | 架構對齊 #2 | 讀碼確認 `hk.merge` 在建構後才設 | HIT,折入(修正 7:修正 6 之後已沒有讀者,整個拿掉) |
| a3 | 架構對齊 #3 ⚠ | 讀碼確認模組各段檢查在兩處各寫一份 | HIT,折入(修正 10:抽成共用函式) |

budget 重現原始輸出(c1):

```
merge rc 2 secs 54 judged mutants: 0 run: [(0, 0, 0, False)]
no-merge rc 2 secs 69 judged mutants: 1 run: [(1, 0, 1, False)]
```

## 放行理由

- rs4:第一個訊號照既有逐支流程等那一支跑完,是計劃〈做法〉4 明寫的 `[不選:第一個訊號就收所有測試程序]`;席位自己也寫了前一版就有這個行為。量齊階段把窗口從一支變 N 支是真的,但第二個訊號照既有流程收程序,呼叫端直接 SIGKILL 才留孤兒,單人工具下可接受。不修。
- in3:REVISIT:2026-12-31 本來就寫明要讀治理帳原始欄位判;加 gov --stats 的讀法是新功能,不是缺陷。RETIRE-IF ① 的判法靠 S18 人工抽查寫進驗證紀錄,不靠 gov --stats 的「補測試後殺掉」計數。不修。
- g3:斷路器不數「有失敗」是設計取捨;殺掉率高時合併不划算,已由計劃 RETIRE-IF ②(合併後每個壞法的秒數沒比不合併低三成就拿掉)與 REVISIT:2026-12-31 盯著。再加一條自動關閉是新機制,最小解(現有撤除條件)夠用。不修。
- a1:席位自己判「結構是對的,沒有第二張登記表」;屬性先標再登記,回呼看到時一定帶標記。另開一張表只是搬位置,不改行為。不修。

## 先查世界

- PRIOR-ART:時限與逾時(c1、rs2、rs3、b3)——查 PIT FAQ 與 Stryker、Blinky 的逾時設計:都用「不帶壞法那一輪的實測耗時 × 係數 + 常數」當上限,而不是固定單價;採用:量基準改用第一支實測值重估剩下的支數,快篩上限取 min(max(合併基準×5, 下限), 剩餘時限)。來源:https://pitest.org/faq 、https://stryker-mutator.io/docs/stryker-js/configuration/#timeoutfactor-number
- PRIOR-ART:訊號空窗(c2、rs1、g4)——查 Python signal 文件與 bpo-1975、bpo-47139:在 Popen 前後遮蔽訊號不可靠(子程序繼承遮罩、訊號處理只在主執行緒的位元組碼之間跑);排除遮蔽做法,採用「登記之後再看一次停止旗標,已收到就當場收掉」。來源:https://docs.python.org/3/library/signal.html 、https://bugs.python.org/issue1975 、https://bugs.python.org/issue47139
- 其他組(測試補洞、死欄位、文件對齊、重複函式)是本 repo 內部一致性問題,沒有對應的外部做法要查。

## 修補

- 實作代理提交 8810c9ddf(fix: 合併快篩量基準不再吃光時限、訊號空窗當場收掉合併呼叫);測試檔改動使用者 2026-11-23 回「簽」,簽章提交 02fd3bdf5。
- 新增測試:t_choice_kill_merge_budget_reestimate、t_choice_kill_merge_signal_race、t_choice_kill_merge_screen_cap、t_choice_kill_merge_edges、t_choice_kill_merge_no_lane_chunk;既有 t_choice_kill_merge_interrupt 補還原後內容回到原文的斷言,t_choice_kill_merge_unclean_goes_single 改用每案都寫出的超大輸出。
- 代理改壞 16 處都有測試翻紅(腳本與輸出在會談 scratchpad 的 impl-ck/mutate2.py、mutate2.out)。
- 編排者重跑:-k choice_kill_merge 129 過 0 紅;lint-new 47a37c05..HEAD 狀態 clean。
- 判斷:a2 沒照字面改走建構子,因為修正 6 刪掉 judged 之後 `hk.merge` 已沒有讀者,留著是死碼。
