severity: minor

審查範圍:/tmp/code-gls-r1.patch 全 1355 行逐 hunk 讀完,對照 scripts/lumos 現況與計劃〈回退〉。圖譜鏡頭:派工尾端沒有附 LUMOS-IMPACT 固定席筆記,無逐條可答;改以計劃筆記的三條合約候選(三個判定閘永不入本機名單、hard 恰好 False、兩本各自吞錯)對照程式驗證,見最後一節。

## F1 回退寫的「先刪兩本本機帳」不可逆,且只涵蓋這一份工作目錄
severity: minor
blocking: 否
引句:「# 本機帳:例行觀察與查筆記紀錄,不進版控(Projects/治理帳例行紀錄分流_計劃)」
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:102`
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:104`
失敗場景:
1. 上線後 docs/.governance-local.jsonl 累積 doctor-run、daily-wrapper(stale / watchdog-stale 這類告警)、spec-gate-run 等例行紀錄。這些只在本機,git 裡沒有副本。
2. 要退回時,〈回退〉叫人先刪兩本再 revert。revert 會同時拿掉根 .gitignore 那三行(diff 第 16-18 行加的),不刪就會變成未追蹤檔;刪了就永久丟掉。舊版 `_gov_ledger_rows_by_time` 不存在,舊版 cmd_gov 不讀 .governance-local.jsonl(diff 的 `load(GOV_LOCAL_LOG_NAME, _gov_row)` 是新增),所以留著也看不到。程式沒有提供「把本機帳併回 .governance-log.jsonl」的指令,也沒有匯出路徑。
3. 計劃寫的「本 repo 回退前先刪」只管這一份工作目錄。〈天花板〉自己寫了本機帳每台機器、每個 worktree 各一份。其他 worktree、別台機器 pull 到 revert 提交後,根 .gitignore 失效,本機帳立刻變未追蹤檔。
4. 回退後的舊版 `_BOOKKEEPING_FILES` 沒有這兩個新檔名(diff 在該表新增了 docs/ 加 GOV_LOCAL_LOG_NAME 與 USAGE_LOCAL_LOG_NAME)。其他 worktree 的人若 `git add -A` 把它們帶進提交,舊版會把這個提交當成「改了程式碼」,使已蓋的代碼審留痕失效而擋推。
5. 不是 blocker:資料只是統計用的例行觀察,判定類讀者不受影響(三個判定閘不在名單,我逐筆對過 _GOV_LOCAL_PAIRS)。回退步驟寫得出來,但「刪除」是這次改動裡唯一不可逆的動作,而且步驟列表漏了其他 worktree。
最小重現:未能重現為紅(屬流程缺口,不是程式 bug)。可驗證手法:臨時目錄 git init、放新版根 .gitignore、跑 doctor --ci 產生本機帳、把 .gitignore 還原成舊版,git status 即多出 `?? docs/.governance-local.jsonl`。

## F2 doctor 軟提醒叫人跑 lumos update,但在沒有 docs/ 的佈局 update 補不了
severity: minor
blocking: 否
引句:「沒被忽略的跑一次 lumos update 補忽略規則;太大的可以直接刪,只影響本機統計」
file: `/home/user/Lumos/scripts/lumos:20812`(update 路徑經 _init_additive_setup)
file: `/home/user/Lumos/scripts/lumos:21030`(只呼叫 `_ensure_docs_gitignore(root / "docs")`)
失敗場景:
1. 獨立 vault 佈局:vault 在 repo 根底下(例如 `<root>/kg`),`vault.parent` 就是 repo 根,沒有 docs/ 資料夾。_append_governance_log 寫到 `vault.parent / .governance-local.jsonl`,也就是 repo 根。
2. `_ensure_docs_gitignore(root / "docs")` 在 docs/ 不存在時直接回 [](diff 內明寫「docs/ 不存在:什麼都不做」),所以 update、init 都不會補任何忽略規則。
3. 實測(臨時目錄 /tmp/rbx,git init 加 kg/MOC/idx.md,跑 `lumos --vault kg doctor --ci`):根目錄多出 `.governance-local.jsonl`,`git status` 顯示 `?? .governance-local.jsonl`;再跑 doctor 印出「.governance-local.jsonl 沒被 .gitignore 忽略,會以未追蹤檔出現」,並建議「跑一次 lumos update 補忽略規則」。照做無效,提醒永遠不消失,檔案也可能被 `git add -A` 帶進版控。
4. 影響僅限獨立 vault 佈局的消費專案,不影響本 repo 與 docs/ 底下 vault 的標準佈局。修法方向:忽略規則寫到 `vault.parent / .gitignore`,與帳檔實際落點同一層;或這種佈局下提醒改講手動加哪一行。
最小重現:如上 /tmp/rbx。

## 新舊並存情境(逐一走過,無需動作)
- 同一 repo 兩台機器一新一舊:舊機器仍把例行事件寫進版控帳,新機器寫本機帳。新機器的統計讀者兩本合讀,舊機器的紀錄在版控帳照讀。判定類讀者(`_codeloop_read_from_ledger` 在 scripts/lumos:42482、`_fix_check_events` 在 12482、`_escape_released_loops` 在 11261、`_loop_close_stamps` 在 10313)一行沒改、只讀版控帳,兩邊判定一致。舊機器看不到新機器的例行觀察,統計偏少,計劃〈天花板〉已認。
- 消費專案新工具、舊 hooks:hooks 只呼叫 lumos 子命令,不直接寫帳,不受影響。
- 工具已更新、尚未跑 `lumos update`:本機帳以未追蹤檔出現,doctor 軟提醒有蓋到(`_local_ledger_doctor_msgs`),標準佈局下 update 會補。
- CI 版本與本機不同:CI 是全新 checkout,沒有本機帳。CI 讀的只有版控帳。新版 CI 跑 doctor --ci 寫的本機帳留在 CI 暫存目錄,無副作用。
- 不可逆動作盤點:沒有刪檔、沒有改寫既有帳、沒有 untrack。`.gitignore` 補行是二進位追加,CRLF 與無尾換行都處理(測試 t_gov_split_ignore_rule 涵蓋)。回退後 docs/.gitignore 多出兩行:舊版從不寫這兩個檔名,忽略它們無害。舊 .usage-log.jsonl 原地凍結,沒停止追蹤,別台機器 pull 不會被刪檔。
- 同一秒寫入的排序:ts 是事件當下時間,穩定排序下版控帳在前。spec-gate 同一秒的新舊平手,後寫者勝會偏向本機帳,誤差在秒級,無實害。

## pitfalls manifest 逐條判定
- scripts/test_lumos.py:38466 ruff E702:誤報。該行(`(root / "src" / "m.py").write_text(...); g("add", "-A")`)是 t_delguard_logs_ok_too 的既有 context 行,不在這份 diff 的新增行內。
- scripts/lumos:1454 `open(path, "a")`:誤報。是 `_gate_event` 內 `with open(path, "a", ...)`,離開區塊就關。
- scripts/lumos:1531 `open(path, "a")`:誤報。`_append_governance_log` 迴圈內的 `with open`,例外只吞 OSError,與原行為相同。
- scripts/lumos:21064 `open(gi, "ab")`:誤報。`_ensure_docs_gitignore` 的 `with open(gi, "ab")`。
- tier=high、suite=full 的理由(改到 anchor-baseline.json 之類守衛檔)與本 diff 內容無關,屬機制判定。

## 已走過沒問題的範圍
- 三個判定類閘(code-loop、fix-check、design-loop)不在 _GOV_LOCAL_PAIRS 內,所有判定類讀者仍只讀版控帳。
- `_gov_routes_local` 要求 hard is False 且閘名與種類皆為字串,缺欄位、型別不對、hard 為 0 或字串都進版控帳。
- `_append_governance_log` 兩本各自開檔各自吞 OSError,本機帳壞不連累版控帳事件;`_gate_event` 走本機帳失敗仍回 False。
- `_usage_log` 改寫新檔、舊檔不再寫也不 untrack;`_BOOKKEEPING_FILES` 與 cochange 排除清單同步補了新檔名。
- S18 度量:事件兩本合計、暖機護欄的最舊一筆只看版控帳。
- 測試改動:`_gov_since` 以多重集合差取新事件,避免合併排序後依行數位移,邏輯正確。

總結:這份改動沒有不可逆的資料改寫,判定面的回滾與新舊並存都站得住,只留兩條低嚴重度缺口,一是回退步驟靠刪除且漏掉其他 worktree,二是沒有 docs 資料夾的佈局下忽略提醒無法被它指的指令解掉。
