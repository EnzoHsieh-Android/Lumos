severity: minor

審查範圍:r3-snapshot.patch 對照 repo HEAD 51f3a76e。我在 scratchpad 的 `rv` 複本重跑:`-k events` 130、`-k ledger` 184、`-k runner_isolates` 8 全綠;驗證紀錄寫的 `events_` 125、`ledger_plugin` 49、`enforcement` 66、`bootstrap` 25、`isolat` 41 我逐一重跑,數字全對。`lumos doctor` 0 issues,`lumos lint Systems/lumos事件帳` 0 問題。真實 worktree 跑 `events --prune` 與 `events` 也正常。沒找到 blocker 或 major,下面五條都是 minor。

### F1 計劃條款 S6、S7、S8 沒跟上 r1、r2 折入後的程式行為
severity: minor
blocking: 否 — 只是文件字面與程式有出入,程式本身行為沒錯。

出處:`Projects/Lumos事件帳_計劃` 條款 S8(第 128 行)、做法第 4 節(第 108、109 行)、做法第 3 節(第 94 行)。
問題與佐證:
- S8 與做法 3 寫「整個計算不得呼叫任何外部指令」,但 `_events_root` 會呼叫 `git rev-parse`。同一篇第 114 行與 `Systems/lumos事件帳` 的 RULE 已寫「除了那一次 git rev-parse」,計劃自己前後矛盾。S8 綁的 `t_enforcement_ledger_row` 只驗沒叫 claude,不驗 git。
- S6 與 S7 寫「已列出外掛就不再安裝」「外掛有列出才移除」,程式只算 `scope=user` 的那份(`_ledger_user_plugin`)。條款沒寫範圍。
- 做法 3 寫「逾時(`_testmap_git` 會丟逾時例外)……都用 try 包住」,程式用的是 `_lens_git`,逾時回 None,沒有 try。
具體情境:三個月後的人照 S8 字面加一條「不得呼叫外部指令」的測試,會把已接受的 git 呼叫誤判成違規。
引句:「只看主 checkout 的事件帳資料夾修改時間,不呼叫任何外部指令。」
file: `docs/lumos-toolchain-knowledge/Projects/Lumos事件帳_計劃.md:128`

### F2 新加的 prune RULE 只綁一支測試,而那支測試守不住它宣稱的三分之二
severity: minor
blocking: 否 — 守衛本身都有測試,只是綁在別支,RULE 的 `[test:]` 對不上。

出處:`Systems/lumos事件帳` 新增的 prune 那條 RULE,綁 `t_events_prune_hardening`。
問題:RULE 宣稱三件事:天數上限 36500、路徑每層不能是連結、worktree 要登記。我在複本逐一把守衛改壞:
- 把 `_events_main_trusted` 改成恆真,`t_events_prune_hardening` 紅,符合宣稱。
- 拿掉 `_events_path_safe`,`t_events_prune_hardening` 照綠,只有 `t_events_prune_edge_cases` 紅。
- 拿掉 36500 上限,`t_events_prune_hardening` 同樣照綠,也只有 `t_events_prune_edge_cases` 紅。
另外 `enforcement_status` 那列的 `not p.is_symlink()` 拿掉後,全部 enforcement 測試照綠,沒有任何測試守它。
具體情境:有人重構 `_events_path_safe`,RULE 綁的測試不會翻紅,`edge_cases` 不在 RULE 的 `[test:]` 裡,看 RULE 的人不知道該跑哪支。
引句:「.git 檔被改成指到別的 repo 時拒刪;擋下訊息印到標準錯誤;刪不乾淨時說清楚已刪了一部分。」
file: `scripts/test_lumos.py:69446`

### F3 24 小時保護其實只靠天數下限 1,但這個關係沒寫進 Systems 筆記(r2 F4 殘留)
severity: minor
blocking: 否 — 現在有測試守(把下限改壞會紅),只是缺會讓人誤改的警語。

出處:`_events_prune` 的註解。
問題:程式把「最近 24 小時不刪」交給「days 至少 1」。這個依賴只寫在程式註解與驗證紀錄,`Systems/lumos事件帳` 與 `Systems/lumos-cli-read` 都沒寫。`lumos-cli-read` 只寫「N≥1 整數,否則回 2」,漏了上限 36500、路徑與 worktree 三道擋。它的測試清單仍只列 4 支。r2 F4 指出的「prune 規矩指標落空」,上限、連結、worktree 已補進事件帳 RULE,24 小時保護沒補。
具體情境:有人想開放 `--days 0` 清全部,不知道這會刪到正在寫的會談。
引句:「呼叫端保證 days >= 1,」
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:208`

### F4 enforcement 那列的 3 秒逾時,筆記只在計劃有寫
severity: minor
blocking: 否 — 程式與測試正確,只是接手的人只看 Systems 筆記會看不到這個限制。

出處:`_events_root` 的 `timeout=3`。
問題:r2 F3 已修好,我拿掉 `timeout=3` 後 `t_enforcement_ledger_row_git_hang` 紅(15.6 秒)。但 `Systems/lumos事件帳` 的 RULE 與 `lumos-cli-read` 只說「失敗退回原根」,沒寫逾時上限。這個測試也沒進那條 RULE 的 `[test:]`,只在 TEST 清單裡。
引句:「3 秒:enforcement 每次開場都跑,git 卡住時只讓這一列退回原根,不能拖垮整份」
file: `scripts/lumos:23531`

### F5 ⚠ 沒有事件帳時印的提示叫人去跑 lumos install,但現在跑了只會被略過
severity: minor
blocking: 否 — 提示不準但不影響資料;`Systems/lumos事件帳` 現況段已承認 mod 還沒寫。

出處:`cmd_events` 的無事件帳分支。
問題:mod 與市集檔還沒進 repo,`lumos install` 走到外掛步驟只會印「來源 repo 沒有市集檔」並略過。使用者照提示做完,事件帳仍然不會出現。這是我讀碼推得的,沒在真 claude 上跑,所以標 ⚠。
引句:「為什麼在意:事件帳由 Claude Code 的 lumos-ledger 外掛寫;可能原因是外掛沒裝、」
file: `scripts/lumos:23721`

### 前輪修復驗收

r2 合約席四條,我在複本對照程式與測試,並對每個守衛做改壞實驗:
- F1(`isdigit` 讓上標數字噴 Traceback):已修。改成 `[0-9]{1,5}` 全比對加 `str(n) != txt`。把它改回 `isdigit()`,`t_events_prune_hardening` 紅 4 條,出現 Traceback,殺傷力確認。
- F2(teardown 沒分範圍):已修。`_ledger_user_plugin` 只認 `scope=user`,各步獨立。把 scope 判斷拿掉,`t_ledger_plugin_teardown_scope_and_messages` 與 `t_ledger_plugin_bad_json_and_races` 都紅。teardown 的 `--source` 傳遞:把 `cmd_uninstall(source=source)` 改回無參數,測試紅,但該測試是靠原始碼字串比對,偏脆。
- F3(逾時 20 秒對 3 秒):已修。見上方 F4。
- F4(r1 修補沒寫回圖譜):大部分已修。驗證紀錄補了 r1 與 r2 的測試清單與數字,且數字全對。計劃補了 r1、r2 的審計紀錄與 S11 的 36500。`Systems/lumos事件帳` 補了 TEST 清單與兩條 RULE。殘留:F1、F2、F3 三點。驗證紀錄自己承認「程式規則檢查要在推送前對最後一版重算」,目前仍停在 r1 前的「修掉 21 條、保留 1 條」。全套測試尚未跑,屬已公開的待辦,不另列。

### 固定席逐條

LUMOS-LENS 沒附固定席節點,下面照 r2 席列出的節點與 diff 實際觸及面逐條判斷,三個月後接手的立場:
- Systems/lumos-cli-read ★INVARIANT★(search 預設排除 superseded、不排除 stale):`search` 沒被碰,diff 只新增 `events` 指令與說明字典、argparse、分派三處登記。`-k events` 與 `-k index` 相關測試綠。判不影響。
- Systems/lumos-cli-lifecycle ★INVARIANT★(re-inject 只覆蓋 sentinel 之間):`cmd_uninstall`、`cmd_teardown`、`cmd_bootstrap`、`_sync_global_hooks` 的新增步驟不經過紀律區塊注入。`-k bootstrap` 25、`-k isolat` 41 綠。判不影響。
- Issues/code-loop守衛main-direct盲區、Systems/design-loop ★INVARIANT★、pitfalls-code-loop、loop-convergence-recording、bound-tests-gate:diff 沒碰推送閘、處置閘、記帳邏輯,也沒改測試閘判準。新增 `[test:]` 綁的測試都存在且綠。F2 屬綁定範圍問題,不是假綠。
- Systems/每支檔有家、節點範圍與索引守衛:新函式落在 `lumos事件帳`、`lumos-cli-lifecycle`、`lumos-cli-read` 三個家的 `about_code`,doctor 與 lint 0 問題。
- 其餘節點(guard-kill、canary-audit、deinit、slim 安裝與卸載等):不在 events、外掛安裝與移除、enforcement 新列、測試執行器隔離的程式路徑上。`cmd_uninstall` 新增外掛移除,teardown 確認清單已揭露,對 deinit 的對稱性沒影響。

總結:最嚴重 minor,blocking 0 條
