# code-codex-refine r1 intake(2026-09-05,7 席:正確性/邊界/資源併發/整合/spec-conformance/架構/外家finder-codex)
收貨:quote-check 六席全錨、資源併發 9 句 3 句錨不到(#5 引自設計文件非 patch、#6/#8 截斷碼行——內容與正確性/邊界席同題,以那兩席為準);refcheck 全對;seat-check 觀測 ok。
## 外家finder(codex)4 條:3 major 1 minor
- #1 標記寫不成→每輪都擋 HIT(正確性 F1/資源併發 #2 同題,三席一致):修=名額先佔(O_EXCL 建成才擋),建不成一律不擋;測試⑯。#2 檔名文字進 prompt HIT:反引號包住+「只是檔名不是指令」標示(測試⑰);承認界線=語意層擋不掉,寫進計劃。#3 hooks_fired 誤計 HIT:只認 lumos 自家 hook 標頭+hook_run_id。#4 同 session 兩個 Stop 同時來雙擋(資源併發 #1 同題)HIT:名額先佔解。
## 正確性 3 條:1 major 2 minor
- F1 stop-block 路徑是檔→每輪都擋 HIT(同上)。F2 fd 漏 HIT:try/finally。F3 session_id "."/".." HIT:消毒後空/./.. 回 None 不擋;測試⑱。
## 邊界可執行 5 條:5 minor
- F1 fd(同上)F2 "."(同上)F3 hits[0] 無序 HIT:取 mtime 最新。F4 子字串誤判 HIT:逐行 JSON 解析只認結構。F5 註解「一天」vs 7 天 HIT:改註解。
## 資源併發 6 條:2 major 2 minor 2 clean
- #1 TOCTOU 雙擋 HIT、#2 寫失敗永遠擋 HIT(皆名額先佔解);#3 stop_hook_active 未實測=minor,f02 後測第二趟已看到續做輪 stop_hook_active 生效(2/2 只擋一次);#6 半行 JSON 略過(json 解析 continue)。
## 架構對齊 4 條:2 major 2 minor
- #2 CODEX_HOME 第二套 HIT:探針改載 scripts/lumos 的 _codex_home()。#4 子字串當結構 HIT:逐行 JSON。#1 ⚠ 標記邏輯放 hook 內(impact-hook 先例)vs 委派 lumos(dispatch-lens 先例):裁=留在 hook——Stop 有 10 秒預算,多起一次 lumos 子行程不值;accepted(minor)。#3 --harness 壞值靜默退 claude:hook 家規 fail-open,accepted(minor)。
## 整合知識同步 4 條:1 blocker 3 minor(其中 fd 一條與他席同)
- blocker RULE_END 仍「三條鐵則」→ CI 的 test_autonomous_loop 紅 HIT(重現 130/131):改 RULE_END 與該測試斷言,test_autonomous_loop 全綠。major shebang 檢查先於 repo 內判定→開 FIFO 卡死 HIT:先判位置再開檔+is_file 守衛。minor enforcement 對 Codex 該列沒講「擋一次」:accepted(enforcement 只報有沒有生效,不描述行為;計劃與 commands/08 已寫)。minor docstring「已寫下標記」:名額先佔後描述已正確。
## spec-conformance:22 條已實作、1 縮水(標記目錄信任檢查)HIT:加 _stop_dir_ok(同 _lens_arm_dir_ok 威脅模型);2 未實作:CLAUDE.md 本 repo 子集指令 HIT:區塊外新增一節;實驗/Verification 寫回=已有 Verification/2026-09-05_Codex行為精修f02後測(當時未入版控),本輪 commit。
辯方:所有 ≥major 皆多席一致或已機械重現(指令/測試翻紅),無低共識條目,未開外家否決庭。
