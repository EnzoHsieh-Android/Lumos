severity: minor

審查範圍是 r2-snapshot.patch,我在自己的複本(scratchpad/rv,由 repo 的 HEAD 48a2739b clone 出來)重跑和驗證。複本上 `-k events` 100 筆、`-k ledger` 173 筆、`-k runner_isolates` 8 筆全綠;`lumos lint Systems/lumos事件帳` 0 問題,`lumos doctor` 0 issues。我沒有發現 blocker 或 major。下面四條都是 minor。

### F1 --prune --days 輸入全形或上標數字時仍噴 Traceback
severity: minor
blocking: 否 — 在任何刪除動作之前就崩,沒有刪任何東西,只是同一類 Traceback 沒收乾淨。

出處:`cmd_events` 的 prune 分支。
問題:r1 修了 `9`×400 的 OverflowError,但數字檢查用 `str.isdigit()`。`'²'`、`'①'` 這類字元 `isdigit()` 為真,`int()` 卻會丟 ValueError,所以前面的檢查擋不住。
具體情境:使用者貼上帶上標數字的天數,例如 `lumos events --prune --days ²`。
佐證:在複本重現,結果是 `ValueError: invalid literal for int() with base 10: '²'`,出自 `cmd_events`。阿拉伯數字 `٣` 則被正常擋下並回 2。`t_events_prune_edge_cases` 只測 `9`×400 與 36501,沒有這個形狀。這和 r1 F7 是同一個崩潰族(Traceback),r1 把整類當成已修,實際沒掃完。
引句:「天數超大或超過上限回 2 不噴 Traceback」
file: `scripts/lumos:23621`

### F2 teardown 移除端沒跟上 r1 F5 的範圍判斷,只有專案範圍那份時誤報失敗並跳過市集
severity: minor
blocking: 否 — 只影響拆除的訊息與市集殘留,不會多刪或誤刪。

出處:計劃做法 4「移除流程」(外掛有列出才移除)。r1 F5 的修法讓安裝端只算 `scope=user` 的那份,移除端沒對稱處理。
問題:`_teardown_claude_plugin` 用 `any(x.get("id") == _LEDGER_PLUGIN ...)` 判斷「有裝」,不看 scope。
具體情境:使用者只在某專案裝過 `lumos-ledger`(`--scope project`),然後跑 `lumos uninstall` 或 `teardown`。
佐證:我用真 claude 在隔離設定目錄重現。`plugin list --json` 列出一筆 `"scope": "project"`,接著 `claude plugin uninstall lumos-ledger@lumos-toolchain` 回 rc=1,訊息是 `Plugin ... is installed in project scope, not user. Use --scope project to uninstall.`。所以移除端會印「移除失敗」並附兩個手動指令,而那兩個指令照樣會失敗。外層 try 在 uninstall 那步就中斷,後面的市集移除也被跳過。測試的假 claude 沒有 scope 不符時失敗的行為,所以測不到。
引句:「移除 lumos-ledger 外掛與我們的市集。沒有 claude、兩者都沒有就安靜略過」
file: `scripts/lumos:21790`

### F3 enforcement 那一列的主 checkout 解析,逾時是 20 秒,不是計劃寫的 3 秒
severity: minor
blocking: 否 — 只在 git 卡住時才有差別,而且開場鉤子本身有內層預算兜底。

出處:計劃做法 3 寫的是用既有的 `_testmap_git(root, [...], timeout=3)`;`_events_root` 實際呼叫 `_lens_git(root, "rev-parse", ...)`,沒傳 timeout。
問題:`_lens_git` 預設 `timeout=20`,所以計劃的 3 秒上限實作成了 20 秒。`lumos enforcement --json` 由 `lumos-entry-hook.py` 在每個 session 開場呼叫,該呼叫自己的預算是 `_inner_budget(default=10)`。git 一卡住,整支 enforcement 先被外層殺掉,所有層的提醒一起消失(鉤子 fail-open),而不是只讓這一列退回 root。計劃與 Systems/lumos事件帳的 RULE 都把「開場不拖慢」當理由,程式沒守住這個前提。這個逾時沒有任何測試覆蓋。
引句:「git-common-dir 是名叫 .git 的資料夾時取上一層;git 失敗、逾時、找不到都退回 root。」
file: `scripts/lumos:41812`、`scripts/hooks/claude/lumos-entry-hook.py:256`

### F4 r1 的修補沒寫回圖譜:驗證紀錄、計劃、筆記的測試與規則都還停在修補之前
severity: minor
blocking: 否 — 只是文件落後;三個月後接手的人會照舊敘述判斷現況。

出處:r1 收貨紀錄已承認補了三支新測試與數項行為,但寫回的筆記沒跟上。
問題與佐證,逐項核對:
- `Verification/2026-10-05_事件帳Python段實作` 的條款表和相關測試數字都停在修補前:沒提 `t_events_session_name_and_repo_validation`、`t_events_reader_edge_lines`、`t_events_prune_edge_cases`、`t_ledger_plugin_bad_json_and_races`、`t_ledger_plugin_messages_and_bootstrap`。「沒驗的」一節也沒更新。
- 同一篇的程式規則檢查段寫「修掉 21 條、保留 1 條」。r1 之後新增的程式行沒有重算,新增行裡已有一處 `noqa: BLE001`。
- `Projects/Lumos事件帳_計劃` 的審計修正紀錄與實作進度沒有代碼審 r1 的紀錄。條款 S11 只寫「N 不是 1 以上的整數時回 2」,沒寫新增的 36500 上限與 `_events_path_safe`。做法 3 沒寫 `--session` 的名稱規則。計劃全文也沒有 36500 這個數字。
- `Systems/lumos-cli-read` 寫 prune 的規矩「寫在 Systems/lumos事件帳」。但那篇的 TEST 清單與正文沒有 prune 的天數範圍、24 小時保護、符號連結與路徑檢查,指標落空。
- `Systems/lumos事件帳` 與 `Systems/lumos-cli-read` 的 `TEST:` 清單沒列 r1 新增的測試,所以 session 名稱、控制字元剝除、版本只認整數、prune 邊界這些筆記裡寫的行為沒有綁定測試。
引句:「bootstrap --lumos-home 要傳進安裝子行程;teardown 確認清單列外掛」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-05_事件帳Python段實作.md`

### 前輪修復驗收

r1 合約席的七條,我在複本對照程式與測試逐條驗過:

- F1 bootstrap 傳 `LUMOS_HOME`:已修。`cmd_bootstrap` 的子行程帶 `env=dict(os.environ, LUMOS_HOME=str(home))`,測試用假 claude 驗到 marketplace add。
- F2 teardown 確認清單與開關略過訊息:已修。確認清單有列外掛與市集,`_teardown_claude_plugin` 在開關打開時印一行。我把確認清單那行拿掉,測試會翻紅。
- F3 指令索引過度宣稱:已修。01 子檔改成「實際模型只在 `--json` 原始事件」,07 補了外掛安裝與移除。不過寫入端的 mod 還不存在,所以該欄位是否真的有值仍無從驗證,算已知界線,不列新問題。
- F4 `--session` 路徑跳脫與連結:已修。名稱規則是 `[A-Za-z0-9][A-Za-z0-9._-]*`,連結一律回 2,測試涵蓋 7 種輸入。
- F5 專案範圍裝過就跳過使用者層:安裝端已修,測試也在;移除端的不對稱是新問題,見 F2。
- F6 enforcement 的 RULE 與測試不符:已修。RULE 字面改成除了 `git rev-parse` 之外不呼叫外部指令,0.9 秒有出處,弱斷言「缺」已拿掉。
- F7 `--days` 極大值與清理競態:大部分已修(超長、上限、`OSError` 蒐集、上層符號連結),但 `isdigit()` 漏網,見 F1。

修補自己引進的新問題:F1、F2、F3。F1、F2 屬於 r1 修補本身留下的洞,F3 是實作與計劃的出入。

### 固定席逐條

三個月後接手的立場下,每條節點:

- Issues/code-loop守衛main-direct盲區:這份 diff 沒碰推送閘或 main-direct 路徑,不影響。
- Systems/lumos-cli-read ★INVARIANT★(search 預設排除 superseded、不排除 stale):`search` 沒被碰,diff 只新增 `events` 指令。`-k search_forget_superseded` 在 r1 席已跑綠,我不重複;判不影響。
- Systems/lumos-cli-lifecycle ★INVARIANT★(re-inject 只覆蓋 sentinel 之間):diff 沒碰 re-inject。`cmd_uninstall`、`cmd_bootstrap`、`_sync_global_hooks` 新增的外掛步驟不經過紀律區塊注入,不影響。
- Systems/design-loop ★INVARIANT★(處置閘第五步,審材必須是 .md 計劃):本 diff 沒碰處置閘與審材判斷,不影響。這一輪的審材本身是 .patch,屬於 code- 開頭的代碼審,不受該條約束。
- Systems/每支檔有家、筆記內容閘、loop-convergence-recording、pitfalls-code-loop:`scripts/lumos` 的新函式落在 lumos事件帳、lumos-cli-lifecycle、lumos-cli-read 三個家的 about_code 內,lint 與 doctor 0 問題。沒碰推送閘或收斂記帳邏輯,不影響。
- Systems/bound-tests-gate、測試假綠形態:新增的 `[test:]` 綁定都是真實存在、且在複本上綠的測試。外掛移除改成真跑 `lumos uninstall` 子行程,不是呼叫內部函式。確認清單那條只做文字比對,但我拿掉那行確實會翻紅,不構成假綠。
- Systems/授權與歸屬、節點範圍與索引守衛、lumos-deinit、slim 安裝與卸載:diff 沒碰 SPDX 檔頭、索引判準、slim 腳本。`cmd_uninstall` 新增了使用者層的 Claude 外掛移除,確認清單已揭露,不影響 deinit 的對稱性。
- 其餘列名的節點(guard-kill、canary-audit、judge-severity-gate、anchor-integrity、check-r-guard、check-t-sentinel、cochange-guard、lumos-refcheck、reversibility-governance-ledger、core-invariant-baseline、doctor-irreversible-hint 等,以及兩篇計劃):判不在 events、外掛安裝移除、enforcement 新列、測試執行器隔離的程式路徑上,不影響。

另外表態記錄寫 py-eventloop 為 na。這份 diff 的 `scripts/lumos` 沒有新增任何 async def,與該表態的前提一致,我沒有反駁它。

總結:最嚴重 minor,blocking 0 條
