severity: major

### F1 Read 擋暫存處時,路徑含 `.`、`..`、`//` 或是相對路徑就整個放行
severity: major
blocking: 是 — 外掛要防的就是「審查席讀到別席報告」,Read 這條路用一個斜線的小變化就繞得過。
引句:「return real !== null && inStaging(real)」
引句:「if (parts.some(s => s === '' || s === '.' || s === '..')) return null」

白話:`realOf` 看到路徑裡有 `.`、`..`、空段(`//`)或不是絕對路徑,會回 `null`,意思是「看不懂」。Write、Grep、Glob 遇到 `null` 都改成擋下。Read 這條相反,`null` 被當成「不在暫存處」放行。

哪個輸入、走到哪一行:
- 審查席呼叫 `Read` 時帶 `file_path: '/tmp/./lumos-seat-staging/L/r1-x.md'`。
- 同理 `'/tmp//lumos-seat-staging/…'`、`'/Users/../tmp/lumos-seat-staging/…'`,或相對路徑 `'lumos-seat-staging/L/r1-x.md'`。
- 走到 `checkTool` 的 Read 分支,`realOf` 在 `.`、`..`、空段那行回 `null`。
- 條件 `real !== null && inStaging(real)` 為假,回 `null` 放行。
- Claude Code 的 Read 會先把路徑正規化或照 cwd 解讀,所以真的讀得到暫存處的檔。
- `guard.test.ts` 的 S2 只測了乾淨的絕對路徑(行 96–98),沒有任何一支 Read 帶這些拼法的測試。

最小重現(放在我的工作資料夾 `/tmp/lumos-seat-work/code-審查席唯讀隔離/正確性-sonnet/`):
- 把 `register.ts` 複製成 `reg.mts`。
- `io.real` 用 `fs.realpath`,對 `checkTool` 餵 `{tool:'Read', file_path:<各種拼法>}`。
- 指令:`cd "$W" && node t1.mts`
- 輸出:
  - `"/tmp/lumos-seat-staging/Lx/r1-x.md" => 擋下(lumos-guard 暫存處)…`
  - `"/tmp/./lumos-seat-staging/Lx/r1-x.md" => ALLOW`
  - `"/tmp//lumos-seat-staging/Lx/r1-x.md" => ALLOW`
  - `"/Users/../tmp/lumos-seat-staging/Lx/r1-x.md" => ALLOW`
  - `"lumos-seat-staging/Lx/r1-x.md" => ALLOW`
- 同一個檔用 `cat /tmp/./lumos-seat-staging/Lx/r1-x.md` 讀得到內容。
- 重現用的測試檔 `Lx/` 我已刪掉,staging 原有內容沒動。

修法方向:Read 遇到 `real === null` 也擋,跟 Write、Grep、Glob 同一條規則(不在暫存處的路徑才放行)。這是同一個根因,應該統一規則,不要只補 Read 一處。

file: `mods/claude/lumos-guard/hooks/register.ts:171`
file: `mods/claude/lumos-guard/hooks/register.ts:86`

### F2 掛鉤出錯時,主會談自己的 Bash 也被擋
severity: minor
blocking: 否 — 只在掛鉤本身逾時或回傳不合規時發生,而且擋的是編排者自己的指令,不是漏擋。
引句:「return e?.tool === 'Bash' ? { deny: BASH_ERROR } : next(e)」

`onCallFailed` 沒看 `e.agentId`。tool.call 掛鉤逾時或誤回傳,而且 `next.called === false` 時,主會談(沒有 `agentId`)的 Bash 也回 `{ deny: BASH_ERROR }`。外掛設計上只管審查席,主會談應該放行。

測試 S8 的 `onCallFailed({ tool: 'Bash' }, …)` 剛好拿沒有 `agentId` 的事件斷言「擋」,等於把這個行為釘死了。

我沒能造出引擎讓掛鉤逾時的場景,所以只算 minor。`onCall` 內部已經吞掉所有例外,`.catch` 實際只會在逾時或誤回傳時走到。

file: `mods/claude/lumos-guard/hooks/register.ts:320`

### F3 外掛移除失敗時,手動指令無條件列出「移除市集」,不管市集是不是我們的
severity: minor
blocking: 否 — 只是印出的建議不精確,不會自己動到別人的東西,但照抄會刪到使用者自己的同名市集。
引句:「todo.append(market_cmd)」

輸入:使用者自己加了同名市集 `lumos-toolchain`(`source` 是 github,不是本機資料夾),或市集根本不存在,而且有一支外掛 `uninstall` 失敗。

走到的行:`if errors:` 分支。它不看 `_same_local_path`,也不看市集存不存在,就把「移除市集」放進手動指令。舊版只有「市集那一步自己失敗」才會印這行,而那一步有檢查市集是不是我們的。使用者照抄就會刪掉自己的市集,或跑一條必定報錯的指令。

file: `scripts/lumos:22076`

### 固定席逐條

- **Systems/lumos-cli-lifecycle(★INVARIANT★ re-inject 只覆蓋 sentinel 之間 body、sentinel 外 byte-equal,綁 `t_reinject_preserves_outside`)**
  - 不影響。diff 只動外掛安裝與移除函式、teardown 確認文案和測試,沒碰 CLAUDE.md 注入或 sentinel 的程式。
  - 兩條 DEBT 也沒碰。
  - 筆記更新與程式一致:回傳取最差、各支獨立、未列的那支略過、全部成功才移除市集、裝完列表確認。
  - 一處筆記沒跟上:〈狀態〉那行仍把 `no-source` 定義成「來源 repo 沒有市集檔」。現在市集檔沒列某一支也會回 `no-source`。屬筆記精度問題,不影響合約。
- **Systems/lumos-cli-read(★INVARIANT★ search 預設排除 superseded,綁 `t_search_forget_superseded`)**
  - 不影響。search 的篩選路徑沒動。
  - 唯一牽連是 `lumos events` 顯示 `[agent]` 前綴(行 23866)。巢狀 spawn 事件的 agent 欄從空變成發起方,讀取端用 `e.get("agent")` 判斷,行為相容。
- **Systems/lumos事件帳(無合約)**
  - 不破壞它的 RULE。enforcement 那列仍不呼叫 claude,事件帳路徑與消毒規則沒動。
  - `spawnFields` 沒有 `deny:`(帶冒號)或 `next({`,`t_ledger_plugin_files_valid` 的禁用樣式不會誤中。
  - 「兩支一起裝、一起移除」符合程式,移除時只要有一支失敗就保留市集。
  - 新增的 PITFALL(spawn 的 agent 欄記成空)與 `spawnFields` 修法一致。
- **Systems/lumos-guard(無合約;RULE 帶 since、retire、confirmed 齊全,有挑戰程式碼的效力)**
  - RULE「不呼叫 `$.process`、不改寫輸入或結果、只掛三個事件」:程式符合,`deny` 是拒絕不是改寫。
  - `responsibility` 與摘要宣稱「擋讀席報告暫存處」:被 F1 破壞。Read 在路徑含 `.`、`..`、`//` 或相對路徑時放行,這條宣稱目前只對乾淨的絕對路徑成立。
  - 同一篇寫「寫檔只准 `/tmp/lumos-seat-work/…`」,程式實際也放行 `/var/tmp` 與 `$TMPDIR` 底下同名資料夾。筆記要補,但沒有安全影響。
- **其餘固定席(分組摘要)**
  - 安裝與分發 INVARIANT:bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、canary-audit、slim-get、slim-install、slim-uninstall。
    - diff 沒改這些檔,也沒改它們綁的測試語意。
    - 我只用 grep 確認 repo 內沒有別處寫死單一 `lumos-ledger` 外掛的移除邏輯,沒有逐篇驗合約行。
  - RISK 守衛面:pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger、check-t-sentinel、doctor-irreversible-hint、check-r-guard、cochange-guard、lumos-refcheck、judge-severity-gate、core-invariant-baseline、存量漂移守衛。
    - 只因 `scripts/lumos` 與測試檔改動而列入,diff 沒碰它們的程式。
  - 不可逆:Systems/lumos-deinit。
    - 只有 teardown 的確認文案加了 lumos-guard 一詞。deinit 與專案層反安裝邏輯沒動。
    - 外掛移除只在機器全域那層,F3 是印出建議的問題,不是動作本身。
  - design-loop:diff 只在 SKILL.md 與 templates.md 加標記與暫存處說明。範本 §2、§4(辯方)與 §5、§6(SDD)沒加標記,屬設計取捨。
  - 筆記沒同步:`skills/lumos-project-notes/commands/07-安裝維運.md` 第 7 行仍寫「裝 Claude 事件帳外掛 `lumos-ledger`」,沒提 lumos-guard。diff 沒改這份。

### 本案特定鏡頭結論
- **`.catch` 與 `Caught`**:`onCallFailed` 先看 `next.called`,已呼叫就 `next(e)` 取回原結果,符合型別檔「replay-safe、不重跑」。`agent.spawn` 的 `.catch` 同理。唯一缺口是 F2。
- **5 秒等待與登記競態**:`pending` 先加後 `next`,`seats.set` 在 `release` 之前,所以子代理的早到工具呼叫會等到登記完成。
  - 有並行的別席時,醒來要等到全部啟動中的派工都結束,或 5 秒逾時。
  - 逾時後會重讀 `seats.get(id)`,自己的登記若已完成仍會被擋。
  - 只有自己的登記超過 5 秒才放行,並跳逾時提示。
  - 這一帶我沒找到會出錯的輸入。
- **`_sync_claude_plugin` 回傳值**:`max(..., key=_PLUGIN_RANK)` 取最差,各支獨立。
  - 舊市集檔只列一支時,guard 走 `no-source`、ledger 照裝,不整段失敗。
  - 市集已登記在同一路徑時不跑 `marketplace update`;這個前提我沒有獨立驗證,採信驗證卷證的隔離設定實測。
- **`_teardown_claude_plugin` 保留市集的條件**:任一支 `uninstall` 或列表出錯就保留市集,手動指令只列失敗的那幾支加市集,符合筆記。唯一問題是 F3 的無條件印出。

總結:最嚴重 major,blocking 1 條
