severity: major

快照核對：SHA-256 與指定值 `3a253f007fafa2d6ebff87d479de5312d3c71a495c6a958b8c6de2a1ef6437e3` 一致，共 154 行。

前言／PRIOR-ART／RETIRE-IF：已讀；見 finding F2、F3。  
範圍與條款：已讀；見 finding F1、F3。  
2026-10-04 收斂性診斷與最小調整：已讀；見 finding F3。  
落點：已讀；見 finding F5。  
試行登記與回顧入口：已讀；見 finding F1、F2、F4、F5。

finding F1

severity: major  
blocking: 是  
引句:「已領號後才改成探針相依或中止，仍保留該格並標範圍偏離／中止，不能事後從五案分母抹去難案。」

設計只規定中止案保留名額，沒有規定它在各項統計中的結果值與分母：三輪內通過率究竟算失敗、未知，還是排除；沒有發生修復的案件在「修復引入缺陷／根因修復組」中如何入分母，也沒有定義。現行工具只判單一 loop 是否通過，不會替試行聚合分母；試行本身又明定沒有新機械閘。

具體失敗場景：第2、3案領號後分別因範圍轉成探針相依及無法建立隔離 worktree 而中止，第4、5案均通過。回顧者可報「完成案 2/2 通過」或「領號案 2/4 通過」；兩者都保留了中止列，卻得到 100% 與 50% 的相反結論。

file: `skills/lumos-code-loop/reference.md:124`  
file: `skills/lumos-code-loop/SKILL.md:62`

finding F2

severity: major  
blocking: 是  
引句:「歷史第1案與四件新工作分列，不合併聲稱因果改善率。」

禁止混用是正確的，但遵守後只剩一個異質的歷史哨兵案與四件前瞻新案；另取最近五件歷史對照又只是「若取」的選配。第1案跑到例外第4輪，而現行正常上限是3輪，因此不能作新四案的基準。若不強制建立可比基準，試行只能陳列四件新案結果，無法回答「是否比較容易收斂」。

具體失敗場景：新四案全部在兩輪內通過。若和第1案四輪FAIL合算，得到4/5；若正確分列，得到新案4/4、歷史案0/1；若又沒有採選配歷史對照，就完全沒有「改善前」分布。三種報法對改善方向的暗示不同。

file: `skills/lumos-code-loop/SKILL.md:60`  
file: `docs/.canary-log.jsonl:2285`  
file: `governance/review-reports/code-repair-pilot-01/r4-gate.txt:13`

finding F3

severity: major  
blocking: 是  
引句:「五案不足以證明因果，不以三輪通過率單獨決定成效。」

計劃正確限制因果宣稱，但沒有預先定義「收斂改善」的主要結果與判定規則。現行 skill 對收斂已有明確語意：一輪內所有 finding 都有處置而使處置閘通過；計劃卻改用多項原始數量與耗時，未指定何者優先、修復引入缺陷是否除以根因組數、是否按 severity 分層，或什麼結果只算不確定。結果可在看到資料後任選最有利指標。

具體失敗場景：新四案全部三輪內通過，但新增步驟耗時增加40%；修復引入缺陷由2件降至1件，根因修復組卻由2組增至10組。可分別宣稱「通過率改善」、「成本惡化」或「每根因缺陷率改善」，快照沒有規則決定哪個才是試行結論。

file: `skills/lumos-code-loop/SKILL.md:62`  
file: `skills/lumos-code-loop/SKILL.md:48`

finding F4

severity: minor  
blocking: 否  
引句:「首次派工前在本計劃該案逐案紀錄寫帶時區的開始時間。」

總耗時定義從「首次派工」起算，但記事要求是在派工前寫一個泛稱「開始時間」的值，沒有要求抄錄派工單的實際 `started` 時刻。現行流程在真正派工前還有凍結材料及表態等步驟，因此兩個時點可能不同。

具體失敗場景：協調者10:00寫開始時間，完成表態及材料整理後10:30才派工，11:00問閘。依定義應為30分鐘，依記事會算成60分鐘；另一案若直接採派工單時間，兩案就不是同一時鐘。

file: `skills/lumos-code-loop/SKILL.md:19`  
file: `skills/lumos-code-loop/SKILL.md:25`  
file: `governance/review-reports/code-repair-pilot-01/r4-dispatch.json:6`

finding F5

severity: major  
blocking: 是  
引句:「每次開工與收尾由 skill 入口導向本表，第五次收尾觸發回顧。」

生效條件只要求新設計迴圈PASS、Verification、快照雜湊與生效時刻，沒有要求確認實際載入的全域 skill 已包含試行入口。目前 repo 分支版已有入口，但實際安裝於 `/Users/enzo/.agents/skills/` 的版本從 testmap 項目直接進入「一輪怎麼跑」，沒有五案試行提示。由於計劃又明說新增欄位全靠人工、沒有機械檢查，這會直接漏登樣本與時鐘。

具體失敗場景：本設計審PASS後立即把 Verification 改成PASS並記生效時間，但尚未合併／同步 skill；下一個新 session 讀目前安裝版 skill，照正常 code-loop 開工而未領第2案、未打時間。事後才發現時，候選順序與第一派工時刻都無法可靠重建。

file: `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md:15`  
file: `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md:17`  
file: `skills/lumos-code-loop/SKILL.md:16`  
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:5`

缺資料／放行後觀測窗／到期回顧：已讀，無 finding；缺值記未知、不補零，14天未成熟案件排除比較，以及 `REVISIT:2026-11-03` 到期即回顧均有明文。  
實務隱患：已讀，無 finding。  
回退：已讀，無 finding。  
審計修正紀錄：已讀，無 finding。  
第1案逐案紀錄與例外續修：已讀；除 finding F2 所述不可作新四案比較基準外，未見新增 finding。

總結：最高 severity major；blocking 4 件。