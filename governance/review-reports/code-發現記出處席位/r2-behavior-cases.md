# r2 待驗案例(修前 746df1cbd → 修後 fa213fad1)

案例只是待驗範圍,不是「已修好」的證據;新席自己跑兩版核對,可補案例。測試指令一律 `python3.14 scripts/test_lumos.py -k <關鍵字>`;修前版本用 `git -C <臨時目錄> worktree` 或 `git show 746df1cbd:scripts/lumos` 取。

| 組 | 角色 | 待驗行為 | 出處 | 選例依據 |
|---|---|---|---|---|
| G1 | repair | `gov --stats` 逐席段:`外家-gemini-2-flash` 與 `外家-gemini-3-flash` 分兩列;`外家codex-gpt-5.6-terra` 原樣;`外家finder2-codex` 併成 `外家finder-codex` | 計劃〈做法〉統計「不同模型不合併」 | 席位報告的反例加真帳寫法 |
| G1 | preserve | `架構對齊r2-sonnet`、`架構對齊-r2-sonnet`、`架構對齊2-sonnet` 照舊併成 `架構對齊-sonnet` | 計劃〈預期值表〉S8 | 修前就通過的既有斷言 |
| G2 | repair | 同一迴圈首筆在生效前、第二筆在生效後,載體不帶 `--finding-seat` → rc0 | 計劃〈做法〉必填條件「首筆=時間最小」 | 席位指出 min 改 max 測試照綠 |
| G2 | preserve | 空帳、本筆時間早於生效日 → rc0;首筆不早於生效日 → rc2 | 計劃 S1、S6 | 既有斷言 |
| G3 | repair | 不帶 `--loop`、帶 `--finding-seat c1=亂寫` → rc2、帳不變 | 計劃〈做法〉值「席名要是同輪帳上的 auditor」 | 席位實跑反例 |
| G3 | preserve | 不帶 `--loop`、不帶 `--finding-seat` 的載體照舊能記(不是本功能要擋的) | 計劃〈範圍〉不做:不改其他記帳規則 | 相鄰呼叫路徑 |
| G4 | repair | `LUMOS_FINDING_SEAT_SINCE=2000-01-01`(純日期)生效;覆寫把照常數該填的推遲時 stderr 有提醒 | 席位報告;鄰居 `_choice_since` 收純日期 | 席位反例 |
| G4 | preserve | 帶時區的覆寫值照舊生效;沒設覆寫時用常數 | 計劃〈做法〉生效日 | 既有測試 `_fs_since` 用法 |
| G5 | repair | 首筆時間讀不動 → rc2、訊息含「補帶 --finding-seat」、治理帳多 `finding-seat-badts`;列出的同輪席名有引號 | 席位報告 | 席位反例 |
| G5 | preserve | `finding-seat-missing`、`finding-seat-unknown` 事件照舊各多一筆;S3 訊息照舊列出同輪席名、含「載體最後記」 | 計劃 S1、S3 | 既有斷言 |
| G6 | repair | standard 代碼審 `loop next --json` 的 `hints` 有一條含 `--finding-seat` 與「載體最後記」 | 席位報告 | 席位反例 |
| G6 | preserve | high 代碼審照舊印資安包與 `--finding-source` 兩條;設計審不印這條;非派工階段不印 hints | 既有測試 t_loop_next_high_code_security_hints | 既有斷言 |
| G7 | repair | `_fs_blocked_n` 只讀 `docs/.governance-log.jsonl` | 鄰居測試寫法 | 席位指出 |
| G7 | preserve | 兩種事件計數斷言照舊成立 | 計劃 S1、S3 | 既有斷言 |

文件類(c3、i1、i2、i5)沒有產品案例:核對 reference.md、templates.md §0、06 速查、SKILL.md、系統筆記的說法跟程式行為一致即可。
