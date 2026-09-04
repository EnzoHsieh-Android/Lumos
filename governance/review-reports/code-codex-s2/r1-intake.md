preflight-4: ran

# r1 收貨紀錄(code-codex-s2,standard)

## 前掃
- 代碼迴圈無四類前掃;patch 只含 scripts/lumos、test、skills(圖譜筆記不入審材)。

## 外家否決(Codex)10 條(6 major 4 minor;引句 9/10 錨定,#4 錨不到不入 set、內容仍折)
- #1 disposal_cmd 漏旗標 HIT:折入(所有 {_tier_flag} 模板統一補 {_orch_flag},定義搬到 _tier_flag 旁)。
- #2 舊帳可被 --orchestrator codex 改分家 HIT:折入 loop next 擋「舊帳視為 claude,要用 codex 開新編號」。
- #3 帳面兩筆不同編排者無人報 HIT:折入 `_loop_orchestrators` 集合;loop next rc2、roster 印「編排者不一致」異常。
- #4 --orchestrator 沒 --loop 孤兒欄(minor)HIT:折入 rc2。
- #5 零記錄無 tier 測試被新守衛先擋(minor)HIT:該測試補旗標,讓 tier 守衛真的被測。
- #6/#7 測試覆蓋(disposal_cmd/light/舊帳 roster)HIT:折入 `t_codex_s2_r1_fixes`。
- #8/#9/#10 skill 把 `model: sonnet` 與 spawn_agent 綁一句 HIT(實驗 3/4 看到 spawn_agent 只有 task_name/message/fork_turns):四處改寫「不能逐席指定模型,由 codex 設定 agents.default_subagent_model 決定;升 opus 只在 Claude 適用」。
## 架構對齊 7 條(1 major 6 minor)
- major `_loop_records` 與 cmd_loop_next 內既有讀帳迴圈逐行重複 HIT:折入 cmd_loop_next 改用 `_loop_records(strict=True)`(OSError 由呼叫端印,行為不變)。
- minor:`_ORCHESTRATORS`→`LOOP_ORCHESTRATORS`(對齊 LOOP_TIERS);值域訊息補「之一」;reference.md「舊頭版全文」凍結段誤插 Codex 字句 → 還原;skill 註記三種措辭 → SKILL 級加「Codex 對照單源=templates.md §3 ④」指標(reference 級統一短標 `(Codex:spawn_agent)`);`_roster_family` 字串沿用=有意識偏離(席判 clean);d4 字面「record 缺=擋」vs 實作「record 定錨後不一致才擋、首輪必帶在 loop next」→ 折入:計劃 S2 文字改成實作語意(比照 --tier 選配慣例)。
## 單reviewer 6 條(3 major 3 minor;引句 6/6、行號 16/16;席用 git stash 隔離到 patch 狀態重現,工作樹事後核對完好)
- F1(major)舊帳 record 端第一個旗標會回溯改分家 HIT(席實跑翻掉一輪外家判定):折入 cmd_canary 同一刀(舊帳+非 claude → rc2)。F2(major)`loop next --json` roster.family 字面不相對 HIT:折入 roster JSON 加 `relative_family` 與 `orchestrator`(不改 family 欄契約;None 分支守住)。F3=外家 #5(已折)。F4=外家 #1、F5=外家 #4(已折)。F6(minor)席名提示多輪洗版 HIT:折入每 loop 每名字一次。
- 派工鏡頭:席回報尾端有「lumos 自動附加」固定席段(這輪 base 用 Lumos/main)。
