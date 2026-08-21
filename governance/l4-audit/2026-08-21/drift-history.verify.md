C1 [✅] FLOW 與實作相符：沿 git log 取樣、git show 抽當時圖譜符號、git grep -F 比對當時 code、rows[i]["ghosts"] 交集判偶發/穩態 | 證據: scripts/lumos:2483(cmd_drift_history), 2536-2567(取樣/比對), 2580-2591(persist 交集邏輯)

C2 [✅] --every 預設值確為 60 | 證據: scripts/lumos:14460 `p.add_argument("--every", type=int, default=60, ...)`

C3 [✅] --every/--limit/--json 三旗標皆存在於 argparse | 證據: scripts/lumos:14460-14462

C4 [✅] _git() 輔助函式固定帶 `-c core.quotePath=off` | 證據: scripts/lumos:2525-2527 `def _git(*a): return _sp.run(["git", "-c", "core.quotePath=off", *a], ...)`

C5 [✅] 與 commit message 記載一致：首版用 `.endswith(".md")` 過濾，非 ASCII 檔名被 git 加引號跳脫，25/30 個中文檔名節點被濾掉 | 證據: git commit b425e19 訊息「首版重放腳本用 .endswith(".md") 過濾 git ls-tree,但 git 對非 ASCII 檔名加引號跳脫 → 25/30 個中文檔名節點被濾掉」；現況修法見 scripts/lumos:2496-2498(docstring) 與 2526(quotePath=off)

C6 [✅] 與 commit message 記載一致：結論從「2% 持續三個月」翻轉成「0% 沒問題」 | 證據: git commit b425e19 訊息同段；scripts/lumos:2497 docstring 同樣覆誦

C7 [✅] 首版只取「動過圖譜的 commit」，與 drift 誕生機制同形狀而系統性錯過；後改掃全部 commit | 證據: scripts/lumos:2531-2536 程式碼註解與 `log = _git("log", "--format=%H %ad", ...)`（未過濾路徑，全部 commit）；git commit b425e19 訊息「首版只取「動過圖譜的 commit」取樣...改掃全 commit」

C8 [✅] 取樣範圍 bug 由模擬「code 改名、圖譜沒動」假 repo 的測試翻紅發現 | 證據: scripts/test_lumos.py:5143-5165 `_dh_repo()`（c1 寫 OldAsync 並提交、c2 改名為 NewAsync 但圖譜未動，註解「★code 改名、圖譜沒動 → 幽靈符號誕生★」）；git commit b425e19 訊息「是測試翻紅才發現的」

C9 [✅] 恰好 3 條回歸測試，內容與描述一致：①改名後幽靈符號可見 ②--json 結構正確 ③無 docs 佈局回 rc=2 | 證據: scripts/test_lumos.py:5168-5173(t_drift_history_detects_persisting_ghost)、5176-5187(t_drift_history_json_shape)、5190-5197(t_drift_history_needs_repo_layout，斷言 r.returncode==2)；程式碼端 rc=2 見 scripts/lumos:2505-2507

C10 [✅] 與 commit message 記載一致：GetOrdersForRedeemAsync / ListAvailableAsync 橫跨全部取樣點皆幽靈，期間 2026-05-26→07-15 | 證據: git commit b425e19 訊息「LandmarkMember 實測:GetOrdersForRedeemAsync / ListAvailableAsync 橫跨全部取樣點,2026-05-26→07-15 期間圖譜從 23 篇長到 27 篇...」（註：scripts/lumos:2493-2494 docstring 另寫「橫跨 77 天、21→30 篇」，與同一 commit 之 commit message 數字不一致，屬程式庫內部自身的文字漂移，但不影響本主張與 commit message 的一致性判定）

C11 [✅] 與 commit message 記載一致：篇數 23→27、候選符號 108→149 | 證據: git commit b425e19 訊息同段（見 C10 引文）

C12 [✅] 與 commit message 記載一致：同期 10 個 agent 兩階段交叉審計也沒抓到 | 證據: git commit b425e19 訊息「——同期 10 個 agent 的兩階段交叉審計也沒抓到。規律成立,不是快照過擬合。」

C13 [✅] 判讀規則與 docstring/輸出文字相符（0 幽靈+0 候選→profile 未對上；0 幽靈+候選正常→無此型 drift；持續存在→規律成立/穩態）；惟實作是以單一訊息文字涵蓋前兩種情況、要求人工核對候選數，並非各自獨立的程式分支 | 證據: scripts/lumos:2489-2492(docstring 判讀說明)、2580-2591(persist 分支 + 末段 else 訊息「所有取樣點都 0 幽靈...或 symbol_profile 沒對上你的語言棧(先確認候選數不是 0)」)

C14 [✅] 設計動機（U/Y 為啟發式、換圖譜或語言棧可能靜默失效、不宣稱通用改給每專案自量）與 docstring 相符；且 drift-history 與 Check Y 共用同一 `load_symbol_profile()` | 證據: scripts/lumos:2489-2490(docstring)；1936(def load_symbol_profile)、1172(Check Y 呼叫)、2508(drift-history 呼叫)

C15 [❓] 對應 Verification 節點檔案存在，但內容依審計規則禁止讀取（docs/lumos-toolchain-knowledge/ 為被審計對象），故無法核對內容是否涉及 profile 化與歷史重放兩項修正 | 證據: `ls -la docs/lumos-toolchain-knowledge/Verification/2026-08-12_通用性修正_profile化與歷史重放.md` 顯示檔案存在（3056 bytes, 2026-08-14），內容未讀

✅14 ❌0 ❓1 ⏭0
