severity: major

審查範圍:`r1-snapshot.patch` 對照計劃做法 3–5 與條款 S4–S8、S10–S12。實驗都在我自己的臨時複本(`/private/tmp/claude-501/rv/`)做,沒有動 repo。八組綁定測試在複本上全綠。S12、S7、S6 各做一次故意改壞,對應測試都翻紅,所以驗證紀錄「故意改壞會紅」站得住。

### F1 bootstrap 的 `--lumos-home` 沒傳進安裝子行程,外掛被悄悄略過
severity: major
blocking: 是 — 計劃明定要做的行為沒做,而且筆記與進度宣稱 Python 段已完成,與實況不符。

出處:計劃做法 4「位置」段與回退第 2 步(都列出「bootstrap 傳 `LUMOS_HOME` 的那一行」);diff 完全沒碰 `cmd_bootstrap`。
問題:`cmd_bootstrap` 用 `subprocess.run([... "install", "--force"])` 起子行程,沒有把 `LUMOS_HOME` 放進環境。子行程裡 `_sync_claude_plugin` 呼叫 `_lumos_src()`,退回預設的 `~/harness/lumos-toolchain`。
具體情境:使用者跑 `lumos bootstrap --lumos-home /x/lh`。外掛步驟去找預設路徑,找不到市集檔就印「略過」。裝好的來源明明是 `/x/lh`,外掛卻沒裝。
重現:假家目錄加假 `claude`,在非 git 目錄跑 `bootstrap --lumos-home $T/lh`。`$T/lh` 是帶市集檔的 clone。輸出是 `(略過 Claude 事件帳外掛:...沒有 .claude-plugin/marketplace.json——/private/tmp/claude-501/rv/bs/home/harness/lumos-toolchain)`,假 claude 的呼叫紀錄檔根本沒產生。
佐證:筆記 Systems/lumos-cli-lifecycle 寫「`bootstrap` ... 都會確保外掛在」。計劃〈實作進度〉寫「Python 段完成」。驗證紀錄「沒驗的」一節沒有列出這一項。
引句:「    src = _lumos_src(source)」
file: `scripts/lumos:19061`

### F2 teardown 確認清單沒加外掛那一行;開關略過時移除端靜默
severity: minor
blocking: 否 — 只影響揭露文字,移除功能本身正確。

出處:計劃做法 4「移除流程」末句「`teardown` 的確認清單加一行『Claude 外掛 lumos-ledger 與市集 lumos-toolchain』」;開關段「兩邊都整段略過並印一行」。
問題:diff 沒改 `cmd_teardown` 的確認文字,所以互動確認只列「~/.claude 全域 hooks」,沒提外掛與市集會被移除。`_teardown_claude_plugin` 在 `LUMOS_SKIP_CLAUDE_PLUGIN=1` 時不印任何訊息,和計劃的「印一行」不符。
引句:「# teardown 第三步也經過這裡」
file: `scripts/lumos:17075`

### F3 指令索引說明多寫了讀取端做不到的事,安裝維運索引沒跟上
severity: minor
blocking: 否 — 只是文件過度宣稱。

出處:01-進場查脈絡.md 新增的一列。
問題:該列寫「子代理與實際模型」。`cmd_events` 文字輸出只印 `tool`、`reason`、`origin`、`agent_type`,不印模型。`_events_sessions` 的摘要列也沒有模型欄。要看模型只能靠 `--json` 的原始事件,而寫入端尚未存在,欄位是否存在無從驗證。另外 `install` / `uninstall` 現在會改使用者層的 Claude 設定(加市集、裝外掛),`07-安裝維運.md` 沒更新,仍只寫「symlink 到 ~/.local/bin」。
引句:「回合、工具呼叫(含失敗)、子代理與實際模型;在 worktree 裡跑讀的是主 checkout 那份」
file: `skills/lumos-project-notes/commands/07-安裝維運.md:7`

### F4 `--session` 沒擋路徑跳脫,符號連結資料夾的行為前後不一
severity: minor
blocking: 否 — 唯讀、只會讀到 `*.jsonl`,實際危害有限。

問題一:`--session` 直接拼進路徑。`events --session ../../..(接外部路徑)` 會讀 events 以外任意資料夾的 `*.jsonl`。重現:我放在 `/private/tmp/claude-501/rv/outside/a.jsonl` 的檔被印出來。計劃與 S11 強調「不碰 events 以外的路徑」,只對 prune 做到。
問題二:`cmd_events` 用 `d.is_dir()`,`_events_read` 卻對符號連結資料夾回空。結果是 `--session LNK` 回 0 並印「0 筆事件」,不是「找不到」的回 2。
引句:「    d = _events_root(root) / _EVENTS_REL / session」
file: `scripts/lumos:18785`

### F5 `plugin list` 不分範圍,別的範圍裝過就跳過使用者層安裝
severity: minor
blocking: 否 — 要使用者手動在專案範圍裝過同名外掛才會觸發。

重現:用 claude 2.1.289 在隔離設定目錄,以 `--scope project` 裝 `lumos-ledger@lumos-toolchain`,再到別的 cwd 跑 `claude plugin list --json`,仍列出 `"scope": "project"`。`_sync_claude_plugin` 只比對 `id`,會判成已裝而不裝使用者層那份。
引句:「listed = any(isinstance(x, dict) and x.get("id") == _LEDGER_PLUGIN」
file: `scripts/lumos:18818`

### F6 enforcement 那條 RULE 與綁定測試不完全對得上
severity: minor
blocking: 否 — 行為正確,只是筆記宣稱比程式與測試強。

問題:Systems/lumos事件帳的 RULE 寫「整個計算不得呼叫任何外部指令」,並綁 `t_enforcement_ledger_row`。程式實際會呼叫 `git rev-parse`(經 `_events_root`),測試只用假 `claude` 的標記檔證明沒叫 claude。計劃自己允許 git,所以該 RULE 的字面是錯的。同一句的「每次開場多約 0.9 秒」沒有出處或重現指令。
另有一處弱測試:S4 的「子代理只有 turn_end 不當錯誤」用 `"缺" not in stdout` 檢查,程式裡沒有任何會印「缺」的分支,這條斷言不可能翻紅。
引句:「check("S8 整個 enforcement 計算沒有呼叫 claude 指令", not marker.exists())」
file: `scripts/lumos:20771`

### F7 `--prune --days` 極大值會噴 traceback;清理過程遇競態會崩
severity: minor
blocking: 否 — 只影響輸入異常或競態時的體驗,不會多刪檔。

重現:`events --prune --days $(python3.14 -c "print('9'*400)")` 丟出 `OverflowError: int too large to convert to float`。`str(n) != str(days).strip()` 這道檢查擋不住它。
另外 `_events_prune` 對 `f.stat()` 與 `shutil.rmtree` 沒有包例外。寫入端同時在寫,檔案消失就會中途崩,留下刪一半的結果。
引句:「        newest = max([d.stat().st_mtime] + [f.stat().st_mtime for f in d.iterdir() if not f.is_symlink()])」
file: `scripts/lumos:19049`

### 固定席逐條(impact 自行跑 `lumos impact --diff 2db51cc4..HEAD`,hook 沒附筆記)
- Systems/lumos-cli-lifecycle:唯一 INVARIANT 是 re-inject 不動 sentinel 以外內容。本 diff 沒碰 re-inject,不影響。`t_reinject_preserves_outside` 3 支綠。
- Systems/lumos-cli-read:INVARIANT 是 search 預設排除 superseded。本 diff 只新增 `events`,沒碰 search,不影響。`-k search_forget_superseded` 19 支綠。
- Systems/slim-install-安裝器 與 slim-uninstall-一行卸載:兩篇的 INVARIANT 都綁 slim 安裝器 / 卸載腳本的 CLAUDE.md 注入、備份、獨立步驟。diff 沒碰 slim 腳本。`-k slim_install` 101 支、`-k slim_uninstall` 124 支全綠,不影響。
- Systems/bound-tests-gate:INVARIANT 是推送閘逐支真跑綁定測試。本 diff 沒碰閘邏輯,`t_bound_tests_gate` 16 支綠。新增的 `[test:]` 綁定都是真實存在的測試函式,不影響。
- Systems/測試假綠形態:INVARIANT 是翻紅釘要有前置斷言。新測試 S12 有前置斷言(worktree 建得起來、worktree 本身沒有事件帳)。我把 `_events_root` 改成恆回 `root`,S12 翻紅,不違反。S4 的 `"缺" not in stdout` 是弱斷言,見 F6,但它不是翻紅釘。
- Systems/授權與歸屬:`scripts/lumos` 檔頭要帶 SPDX 與 MIT。diff 不動檔頭;`-k license` 11 支、`-k deinit_never` 4 支綠,不影響。
- Systems/節點範圍與索引守衛:INVARIANT 在於索引與範圍判準,diff 沒碰;`-k doctor_s5` 7 支、`-k doctor_s6` 11 支綠,`t_command_index_complete` 也綠,不影響。
- Systems/lumos-deinit:標「RISK·不可逆」但沒有合約行。`cmd_uninstall` 現在會移除使用者層的 Claude 外掛與市集,確認清單沒有揭露,見 F2。
- 其餘固定席節點(design-loop、guard-kill、pitfalls-code-loop、canary-audit 等)的 INVARIANT 與 RISK 都不在 `events`、外掛安裝、enforcement 新列、測試執行器隔離的程式路徑上,判不影響。

最嚴重 severity:major;blocking 條數:1(F1)。
