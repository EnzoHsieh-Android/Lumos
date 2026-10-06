severity: major

審查範圍是合約與圖譜一致,來源是 `/tmp/code-審查席唯讀隔離-r1.patch`。所有實驗都在 `/tmp/lumos-seat-work/code-審查席唯讀隔離/合約圖譜-sonnet/rv` 這份 `--shared` 複本裡做,原 repo 沒動。

先講已驗證為真的宣稱:
- 外掛測試實跑 `claude plugin test mods/claude/lumos-guard`,結果 33 支全綠,與筆記寫的「33 支」相符。
- ledger 外掛測試共 24 支,也相符。
- 三篇筆記加一篇 Verification,`lumos lint` 都是 0 問題,`lumos doctor` 為 0 issues。
- Python 子集 `-k guard_plugin`、`ledger_plugin`、`seat_templates`、`install_registers`、`teardown_removes`、`runner_isolates` 全綠。
- 兩條 ★INVARIANT★ 綁定測試 `t_reinject_preserves_outside`、`t_search_forget_superseded` 都綠。
- 我另外對安裝流程做了 P1、P2、P4、P5、P6 五處改壞,都翻紅。範本標記拿掉兩段也翻紅。這幾處與筆記宣稱一致。

### F1 S12 的測試守不住當初出事的那一行接線
severity: major
blocking: 是 — 條款 S12 的測試對「把修正退回原狀」仍綠燈,錯誤會無聲回來
引句:「  await record(st, $, f.agent, 'spawn', f.extra)」
重現:在複本把 `mods/claude/lumos-ledger/hooks/register.ts` 的 `onSpawn` 裡 `f.agent` 改回 `e.agentId`(也就是原本的 bug 寫法),跑 `claude plugin test mods/claude/lumos-ledger`,結果是 24 pass、0 fail。
說明:新測試只呼叫純函式 `spawnFields`,沒有測 `onSpawn` 把 `f.agent` 傳進 `record` 這一步。`Systems/lumos事件帳` 新增的 PITFALL 寫 `[repro:claude plugin test mods/claude/lumos-ledger 的 S12 測試]`,Verification 也寫「S12 先看到紅才修」。實際上這支測試守不住接線,所以 S12 條款的 manual 綁定只驗到半句。
file: `mods/claude/lumos-ledger/hooks/register.ts:312-340`

### F2 改過行為的地方,別處還寫著舊說法
severity: minor
blocking: 否 — 只是文字落後,不會做出錯的行為
引句:「外掛步驟自己回 ok / absent(找不到 claude 或測試開關)/ no-source(來源 repo 沒有市集檔)/ failed,自己印一行」
說明:
- `Systems/lumos-cli-lifecycle` 的〈狀態〉這一條沒跟上。現在是每支外掛各印一行,`no-source` 也多了「市集檔沒列那支」的意思。
- 同篇的〈測試隔離〉列出的測試名沒改。計劃 d2 寫了「對應測試名跟著改」,而 r3 架構席也當成已改過。實際上 `t_install_registers_ledger_plugin`、`t_teardown_removes_ledger_plugin` 都還是舊名。
- 使用者看得到的安裝說明還寫「裝 Claude 事件帳外掛 `lumos-ledger`」,沒提 `lumos-guard`。
- `Systems/lumos-deinit` 的移除說明也只提事件帳外掛。
- `t_teardown_removes_ledger_plugin` 的 docstring 還寫「失敗附兩個手動指令」,實際是「只列失敗那幾支加市集」。
file: `skills/lumos-project-notes/commands/07-安裝維運.md:7`
file: `docs/lumos-toolchain-knowledge/Systems/lumos-deinit.md:53`
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md:102`
file: `scripts/test_lumos.py:69562`

### F3 S9 條款字面的 `marketplace update` 半句既沒實作也沒驗,計劃沒更新
severity: minor
blocking: 否 — 實作方向有依據,只是條款字面與實作不一致
引句:「隔離的 Claude 設定資料夾實測,資料夾型市集新增外掛後不跑 `marketplace update` 也裝得上,所以安裝流程沒加這一步」
說明:計劃 S9 條款仍寫「`marketplace update` 非零只警告」,第 103 行的做法也還寫要跑。這一步已經拿掉,但條款與做法都沒改成「不做」。所以 `t_install_registers_guard_plugin` 綁的 S9 字面有一句沒對象。那次實測也沒留任何可重跑的證據(沒有測試,也沒有指令),只有一句話。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md:120`

### F4 S10「不改寫任何輸入或結果」只被一條正規式綁住
severity: minor
blocking: 否 — 漏驗的是半句條款,目前原始碼沒有違反
引句:「("改寫事件後交下去", r"next\(\{")」
說明:這條正規式只擋字面 `next({`。`e.prompt = ''; return next(e)` 或 `next(rewrite(e))` 都會過。RULE 行的 `[test:t_guard_plugin_files_valid]` 與 S5 的「不改輸入與結果」因此只被弱綁定。
file: `mods/claude/lumos-guard/hooks/register.ts:857-863`

### F5 幾處規則改壞後測試仍綠,而 Verification 寫「每一處」都翻紅
severity: minor
blocking: 否 — 沒有失敗場景,只是守衛有空洞
引句:「每一處都至少讓一支測試翻紅」
重現(都在複本跑 `claude plugin test mods/claude/lumos-guard`,結果都是 33 pass、0 fail):
- 把 `ROOTS` 裡的 `'/private/var/tmp'` 與 `'/var/tmp'` 拿掉。程式碼是 `const ROOTS = ['/private/tmp', '/private/var/tmp', '/tmp', '/var/tmp']`。測試的 `EXISTS` 與 `LINKS` 備了 `/var/tmp`,但沒有任何案例用到。
- 把 `fold` 的 `normalize('NFC')` 去掉。
- 把 `end()` 裡 `for (const w of p?.waiters ?? []) w()` 刪掉。
說明:Verification 列的 25 處我沒有逐一驗。上面這三處不在它列的清單裡,所以那句「每一處」只對它列出的那批成立。另外 `PLUGIN_RANK` 的優先序(`failed` 大於 `no-source` 大於 `absent`)也沒有混合案例。把 `no-source` 提到 `failed` 之上,`install_registers` 與 `teardown` 子集仍是 22 passed 與 41 passed。

### F6 新 WHY 行的出處指向已被取代的決策
severity: minor
blocking: 否 — 筆記內部不一致,不影響行為
引句:「WHY:審查席改用白名單,不用黑名單 [出處:Projects/審查席唯讀隔離_計劃 決策 d2]」
說明:`Systems/lumos-guard` 的 WHY 行引 d2 與 d3 當出處,但計劃裡 d1 到 d3 都是 `valid: false`,現行的是 d4。d4 才把 Bash 粗擋與「外掛不跑外部指令」的結論保留下來。照這個出處去查的人,會讀到含已拿掉的「事後查 repo」那版內容。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md:20-34`

### 固定席逐條
**Systems/lumos-cli-lifecycle**
- ★INVARIANT★「re-inject 只覆蓋 sentinel 之間 body」:這個 diff 沒碰 re-inject 路徑。綁定測試 `t_reinject_preserves_outside` 實跑 3 passed,不受影響。
- ★DEBT★ 兩條(版本戳不是正確性守衛、pull 來源髒仍會 vendor):都沒碰到,仍成立。
- 這次改動的〈Claude 外掛〉節與程式大致對得上。逐支裝、回傳取最差、列表確認、任一支移除失敗就保留市集,我都用改壞實驗驗過。對不上的只有 F2 列的幾處。

**Systems/lumos-cli-read**
- ★INVARIANT★「search 預設排除 superseded」:diff 沒碰 search。`t_search_forget_superseded` 實跑 19 passed,不受影響。

**Systems/lumos事件帳**
- 沒有登記合約。新增的 PITFALL(spawn 的 agent 欄記成空的)描述屬實,但見 F1:它引的 repro 守不住接線。
- 新加的一句「市集檔也列審查席隔離外掛」屬實。
- 這篇的 frontmatter `updated` 仍是 2026-10-05,可順手更新。

**Systems/lumos-guard**
- 沒有登記合約。
- 33 支與 `[test:]` 指到的三支測試都存在。
- RULE 行綁的 `t_guard_plugin_files_valid` 能擋 `$.process`、`prompt.*` 事件、`$.fs.write`,也能擋少掛 `.catch`,但守不住「不改寫輸入或結果」的全部寫法(見 F4)。
- 出處引用見 F6。
- PITFALL「掛鉤自己丟錯時引擎直接跳過它」的 `.catch` 修法,在複本上用 `claude plugin validate` 的測試確認過。我沒有重跑 S13 真機驗收。

**其餘固定席(分組摘要)**
- 安裝移除類(`slim-*`、`lumos-deinit`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`測試假綠形態`):只動到 `_sync_claude_plugin` 與 `_teardown_claude_plugin` 及測試期望。既有測試實跑全綠,沒有發現新的衝突。
- 風險與守衛面節點(`pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`、`check-*`、`cochange-guard`、`lumos-refcheck`、`judge-severity-gate`、`core-invariant-baseline`、`doctor-irreversible-hint`):diff 沒碰它們的行為,只因同在 `scripts/lumos` 與 `scripts/test_lumos.py` 才被牽連。
- 計劃類(`Lumos事件帳_計劃`、`公開精簡版`、`code側刪除傳播守衛`、`逃生自動記` 等):沒有發現被推翻的條款。
- 既有測試期望被改的兩處:(a) 外掛移除失敗時保留市集,改得對,有新增的 S9 測試正反雙向驗。(b) `t_ledger_plugin_files_valid` 的「市集只列一個外掛」放寬成「列出恰好一次」,改得對,「恰好是清單那幾支」由 `t_guard_plugin_files_valid` 接手。兩處之外,舊行為殘留的位置見 F2。

總結:最嚴重 major,blocking 1 條
