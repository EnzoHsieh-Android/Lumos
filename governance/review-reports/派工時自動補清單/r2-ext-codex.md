# r2 外家否決席報告(Codex, sandbox=read-only, 前景執行)

---

1. `updatedInput` 仍只能列為「待重跑驗證的可行性假說」，不能列為已實測成立的設計前提。r2 承認版控內沒有注入測試輸出，卻仍在摘要與可行性段斷言「做得出來已經實測過」「可改寫派工詞」。在完整腳本、stdin/stdout、子代理回覆與 transcript 雜湊補齊前，合適地位應是 prerequisite／unverified hypothesis；重跑失敗即停止試點，而不是「動工前待辦」。

severity: major  
blocking: 是；核心傳輸機制尚無第三方可重現證物，失敗會使整個試點無法成立。  
引句:「**做得出來已經實測過;有沒有用,要量了才知道。**」  
file: `governance/eval/hook-intercept/README.md:38` 只有省略原輸入的示意 JSON，至 `:48` 仍只是結果敘述。  
file: `governance/eval/hook-intercept/2026-09-03-raw-hook-log.txt:1` 至 `:13` 只有 deny 測試與 SubagentStart 輸入，沒有 updatedInput 追測輸出。

2. r2 新稱「真正的規律是有沒有碰到 `scripts/lumos`」仍不成立。反例全都不含該檔：`67b035e` 只有 `governance/eval/seat-coverage/recount.py`，固定席 1；`84d400c` 三個 code seed，固定席 3；`e0730ff` 五個 code seed，固定席 4。沒有碰 `scripts/lumos` 仍呈 1、3、4 的連續差異，說明真正決定量的是各檔案的圖譜連結與合約密度，不是一支檔案的有無。r2 雖刪掉舊二元假說，卻立刻換上另一個未驗證二元假說。

severity: major  
blocking: 否；此句是錯誤的折入解釋，但試點已有 cap=8，不再直接依賴該規律決定截斷策略。  
引句:「真正的規律是「有沒有碰到 `scripts/lumos` 這支連結密度極高的巨檔」」  
file: `scripts/lumos:16368` 至 `:16413` 顯示固定席由逐檔圖譜結果聯集產生，不是 `scripts/lumos` 存在與否的二元判定。

3. 「沒有機械防篡改」是正確揭露，但沒有處理原安全問題。這支全域 hook 能在子代理執行前改寫任意派工詞；執行副本與 settings 不受 repo anchor、CI 或版本控制保護。把部署縮到作者機器只縮小受影響人口，沒有降低該機器上誤改、安裝漂移或供應鏈竄改的能力。至少試點也需要執行副本雜湊核對、settings 註冊核對，或每次啟動時從受信 source 重同步；否則這仍是未受監督的 prompt-rewrite primitive。

severity: blocker  
blocking: 是；安全邊界仍完全沒有偵測或完整性控制，「已揭露」不能代替風險處理。  
引句:「這是本機實驗,**沒有機械防篡改**;能改到你家目錄的人本來就能做任何事」  
file: `scripts/lumos:11404` 至 `:11410` 的 anchor 清單不含 Claude hook 執行副本。  
file: `scripts/hooks/pre-push:45` 至 `:60` 的 anchor 檢查只在 push/CI 路徑，且可用 `--no-verify` 跳過。

4. r1 的不受信任載荷問題沒有折入。r2 仍把待審分支產生的節點內容貼進派工詞，只規定外框「中性」，沒有將載荷標為不可執行資料、消毒命令式文字或限制可注入欄位。opt-in 只表示編排者同意開通通道，不表示待審 repo 的圖譜文字可信；錨點揭露更與載荷安全無關。

severity: blocker  
blocking: 是；攻擊者控制的 repository 文字仍可自動進入子代理指令面。  
引句:「**措辭**:中性系統附加框架(實測教訓:寫成「暗號是 XXXX」會被子代理拒答並指認為提示注入)。」  
file: `scripts/lumos:16374` 至 `:16383` 顯示 impact 直接依待審 diff 與 repo 圖譜內容計算。  
file: `scripts/lumos:16442` 至 `:16447` 顯示輸出含節點名稱與關聯來源，沒有 prompt-oriented 信任隔離。

5. 新試點的主指標按現行帳務流程從第一天就是空的。實帳共有 885 列，`capture_counts` 102 列，日期只到 2026-08-23；其後 0 列，而 `findings_set` 已持續記到 2026-09-03。r2 只說「得先恢復習慣」，沒有把產生 counts 的步驟、責任人、漏填 fail-closed 或首輪驗收寫進設計。因此若現在照 spec 開跑，實驗列仍只會留下 findings，主指標沒有輸入。

severity: blocker  
blocking: 是；預註冊實驗若主 outcome 無資料，注入組與對照組均無法判讀。  
引句:「★要跑這個實驗,得先恢復填這個欄位的習慣——而那本身就是一個「靠人記得」的步驟。★」  
file: `docs/.canary-log.jsonl:885` 是目前末列，仍無 `capture_counts`。  
file: `governance/eval/seat-coverage/recount.py:24` 至 `:28` 明定無 `capture_counts` 就算不出結果。  
file: `governance/eval/seat-coverage/recount.py:79` 明記該欄由編排者手填。

6. D1 與 D2 按既有帳 schema 都算不出來。`capture_counts` 只是每個相異缺陷被幾席抓到的無 id 次數陣列；`findings_set` 則是 `F01-...` 等助憶 id。兩者沒有 finding→注入節點映射，也沒有保存每輪實際注入的八篇節點。既有重算器甚至明文承認 counts 無法對到 finding id。故不能判斷某個 finding 是否「清單外」，也不能計算八篇中的哪篇被命中。

severity: blocker  
blocking: 是；D1 是 spec 宣告的有效必要條件，D1 不可算即無法依預註冊規則判有效。  
引句:「**D1 清單外發現數**:每輪統計「不在注入清單上的相異缺陷」有幾個。」  
file: `governance/eval/seat-coverage/recount.py:58` 至 `:60` 明寫 `capture_counts` 是無 id 陣列，無法直接對到 `findings_set`。  
file: `docs/.canary-log.jsonl:885` 展示 `findings_set` 只有助憶 id，沒有節點歸屬或注入清單欄位。

7. d9 不能化解「機器注入後仍須手動展開」的 blocker。d9 裁定的是既有 code-loop 編排流程：編排者先取得固定席、手貼 capped 內容，再把超額項降為「列名且不必答」。它裁的是交付責任與 token cap，沒有證明機器注入的八篇足以覆蓋特定 diff，也沒有讓超額節點內容自動可得。r2 把「不必答」誤讀成「不需要知道」，只是取消完整覆蓋要求；這與試點宣稱用機器補足 AI「攤不出來」的價值主張衝突。

severity: major  
blocking: 是；cap=8 的移植缺乏對新通道的覆蓋依據，超額固定席被明確排除後，試點量到的只是前八篇提示效果。  
引句:「**但 d9 裁的正是「超出上限的不必答」**——該批評的前提是「審查員需要完整清單才能做好工作」」  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:114` 至 `:115` 顯示 d9 是 code 迴圈「落成核對 capped 節錄」的裁定。  
file: `docs/lumos-toolchain-knowledge/Projects/一句話層供糧_計劃.md:39` 顯示超額項仍只是列名/L0、全部不必答，並未提供完整內容或覆蓋保證。

最嚴重 severity: blocker；blocking 共 6 條；上輪 8 條 blocking：真修 2 / 未修 6。
tokens used
90,048