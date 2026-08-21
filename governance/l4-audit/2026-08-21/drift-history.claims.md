C1. FLOW：沿 git 歷史取樣，每個取樣點用 git grep 比對「當時的 code」與「當時圖譜提到的符號」，輸出幽靈符號時間序列，據以判斷「偶發 vs 穩態」 | 預期驗證點: lumos drift-history 指令實作（腳本主流程）
C2. 預設取樣頻率為每 60 個 commit 取樣一次（`lumos drift-history` 不帶參數時的預設行為） | 預期驗證點: drift-history 腳本中 --every 的預設值（應為 60）
C3. CLI 支援旗標 `--every <N>`（稀疏取樣）、`--limit <N>`（只看最近 N 個取樣點）、`--json`（結構化輸出） | 預期驗證點: drift-history 腳本的 argparse/參數解析區塊
C4. 實作固定帶 `-c core.quotePath=off` 執行 git 指令，以避免 git 對非 ASCII 檔名加引號跳脫 | 預期驗證點: grep 腳本原始碼中是否有 "quotePath=off" 字串，且用於呼叫 git 的位置
C5. 首版腳本用 `.md` 尾綴字串比對（`.endswith(".md")`）過濾 `git ls-tree` 輸出的檔名，但因非 ASCII 檔名被 git 加引號跳脫，導致 25/30 個中文檔名節點被濾掉 | 預期驗證點: git log 中該腳本早期版本 diff（過濾邏輯變更前後）
C6. 上述過濾 bug 使結論從「2%、持續三個月」翻轉成「0%、完全沒問題」——即 bug 導致系統性低估/隱藏 drift | 預期驗證點: 該 bug 修復前後兩次執行 lumos drift-history 的輸出差異／對應 commit message
C7. 首版取樣只挑「動過圖譜（docs）的 commit」，因與 drift 的誕生機制（只改 code、沒改圖譜）同形狀，系統性錯過 drift 出生那一刻；後改為掃描全部 commit | 預期驗證點: drift-history 腳本的取樣點選取邏輯（是否過濾 commit 是否觸及 docs 路徑）
C8. 上述取樣範圍 bug 是由一則造出「code 改名、圖譜沒動」假 repo 的測試翻紅才發現的 | 預期驗證點: drift-history 測試目錄中是否存在模擬「code renamed but graph untouched」情境的測試案例
C9. 該功能綁有 3 條回歸測試：①改名後幽靈符號可見、②--json 輸出結構正確、③無 docs 佈局時回傳 rc=2 | 預期驗證點: drift-history 對應測試檔案（測試數量與斷言內容，尤其 exit code == 2 的情境）
C10. LandmarkMember 專案首次執行（2026-08-12）結果：`GetOrdersForRedeemAsync` 與 `ListAvailableAsync` 兩個符號橫跨全部取樣點皆為幽靈符號，取樣期間為 2026-05-26 至 2026-07-15 | 預期驗證點: 該次 lumos drift-history 執行輸出／記錄（若有存檔的 --json 輸出或 Verification 節點）
C11. 同一期間（2026-05-26 至 2026-07-15）該專案圖譜篇數從 23 篇長到 27 篇，候選符號數從 108 長到 149 | 預期驗證點: 對應時間點的圖譜節點檔案計數與 drift-history 候選符號計數
C12. `GetOrdersForRedeemAsync` / `ListAvailableAsync` 這兩個幽靈符號，同期由 10 個 agent 執行的兩階段交叉審計也沒有抓到 | 預期驗證點: 該次兩階段交叉審計的產出記錄（是否涵蓋這兩個符號名）
C13. 判讀規則：曲線一直為 0 且候選數也為 0 → 判定為 symbol_profile 未對上該專案語言棧（而非「沒有 drift」）；曲線一直為 0 但候選數正常 → 判定為「此專案沒有這型 drift」；曲線橫跨全部取樣點都在 → 判定為「規律成立、屬穩態」 | 預期驗證點: drift-history 腳本或其文件中對應的候選數/曲線判讀邏輯與輸出訊息
C14. 該工具設計動機明列為 Check U（靠中文詞表）與 Check Y（靠命名慣例）皆為啟發式，換一份圖譜或語言棧可能靜默失效，故不宣稱通用、改為「給每個專案一把尺自己量」 | 預期驗證點: check-y-symbol-existence 與 drift-history 之間的依賴關係節點 [[Systems/check-y-symbol-existence]]，以及兩者是否共用同一套符號比對機制
C15. 本節點的驗證記錄為 [[Verification/2026-08-12_通用性修正_profile化與歷史重放]]，內容應涉及 profile 化與歷史重放兩項修正 | 預期驗證點: docs/lumos-toolchain-knowledge/Verification/2026-08-12_通用性修正_profile化與歷史重放.md 是否存在且內容對應
