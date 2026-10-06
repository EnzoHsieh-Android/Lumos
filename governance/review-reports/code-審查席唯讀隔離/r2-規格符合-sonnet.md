severity: minor

### F1 既有測試「市集只列一個外掛」沒照規格改
severity: minor
blocking: 否 — 規格要的「市集列出的外掛恰好是清單那幾支」已有測試守著(換了位置),所以條款 S10 字面仍成立。
引句:「既有測試 `t_ledger_plugin_files_valid` 的「市集只列一個外掛」改成「市集列出的外掛恰好是清單那幾支」。」
裁定:縮水(輕微)。`t_ledger_plugin_files_valid`(`/Users/enzo/harness/lumos-toolchain-seat-guard/scripts/test_lumos.py` 第 70176 行起)仍保留「S9 市集列出 lumos-ledger 恰好一次,`len(plugins)==1`」,它是先篩出 lumos-ledger 再數,不是「恰好是清單」。「恰好是 `_LUMOS_PLUGINS`」的比對改放進新測試 `t_guard_plugin_files_valid`。意圖有覆蓋,但沒有改規格指名的那支測試。

### F2 Glob 的 pattern 固定段含 `..` 也擋(規格沒寫)
severity: minor
blocking: 否 — 只會多擋,不會放出任何東西;屬保守的多做。
引句:「`path` 是相對路徑就以這席的工作目錄補全,含 `..` 段 → 擋,沒給就是工作目錄。」
裁定:多做。`register.ts` 的 `searchBase`,`if (segs.some(s => s === '..')) return null`,也就是 `Glob` 的 `pattern` 固定段含 `..` 時直接擋。規格只寫 `path` 含 `..` 要擋,沒說 `pattern` 固定段。另外 `bashBlock` 對非字串指令回「指令不是字串」擋下,規格也沒寫,但這是 fail-closed,同方向。

### F3 ⚠ 存對照表的寫法可能蓋掉熱重載前存下的席(交編排者判斷)
severity: minor
blocking: 否 — 我只能確認規格字面,不確定它算不算「縮水」;這比較像實作行為問題,留給編排者決定。
引句:「外掛熱重載後(對照表從 `$.state` 讀回)執行中的審查席與它派的子代理應照擋」
裁定:⚠。`createGuard` 的 `save()` 寫的是 `Object.fromEntries(seats)`,也就是只有記憶體裡的表。熱重載後記憶體是空的,有新審查席登記時,`$.state` 裡舊席可能被覆蓋掉,除非它們先被 `lookup` 讀回過。`end()` 也是同一套寫法,所以「`$.state` 一併拿掉這場的席」靠的是整張表重存,而不是只刪那場的席。條款 S7 的測試只測「熱重載後讀回」,沒測「熱重載後又登記新席再讀舊席」。

### 逐條裁定

〈做法〉一 認出審查席(以下全數核對 `register.ts`)
- 繼承發起方標記,cwd 取輸入的 `cwd`、沒給就沿用發起方的:已實作。`spawn` 裡 `seat = { ...parent, cwd: typeof e?.cwd === 'string' ? e.cwd : parent.cwd }`。
- 第一個非空行、BOM 與全形空白、`\r`:已實作。`firstLine` 用 `trim()`,JS 的 `\s` 含這些字元。
- `^LUMOS-SEAT:\s*(\S+)$`、恰好三段、每段非空、不是 `.` 或 `..`、不含 `\`、空白與控制字元:已實作。`SEAT_RE` 與 `parseMarker`。
- 寫壞標記的判準:已實作且一字對上。`SEAT_LOOSE_RE = /^[#>*_`\s]*lumos-seats?\s*[:：]/i`,對應規格的「去掉開頭 `#`、`>`、`*`、`_`、反引號,不分大小寫,`lumos-seat` 或 `lumos-seats` 接冒號(含全形)」。沒接冒號的提及回 `none`,不擋。
- 回 `{ deny }` 擋派工、理由說哪裡寫壞:已實作。
- 登記時 `$.state` 同寫、不跑外部指令、`finally` 裡 `release`:已實作。
- `tool.call` 每登記一席就重查、5 秒、逾時放行加 `lumos-guard 逾時放行:` 提示:已實作。`release` 呼叫 `wake`,`call` 用 `Promise.race`。
- `session.end` 清表、叫醒等待者、清 `$.state`:已實作(見 F3 的 ⚠)。

〈做法〉二 工具規則
- 二·1 白名單:已實作。`TOOLS_OK` 與規格清單一致,`Task` 與 `Agent` 兩個名字都認;`Skill`、`SendMessage`、`mcp__*` 等都不在清單裡,所以被擋。`isolation` 任何非空值擋;`subagent_type` 只准 `general-purpose`、`Explore`、`Plan`。
- 二·2 寫檔:已實作。欄位名分 `file_path` 與 `notebook_path`;不是字串、不是絕對路徑、有空段或 `.` 或 `..` 段就擋;最深已存在的上層取真實路徑,`realPath` 缺(含懸空連結)就擋;大小寫折疊加 NFC;只有自己的席位工作資料夾放行;4096 字、256 段上限(`PATH_MAX`、`SEGS_MAX`)。
- 二·3 暫存處:已實作。`Read` 看不懂一律擋、落在暫存處擋;`Grep` 只看 `path`;`Glob` 接 `pattern` 第一個萬用字元前的固定段,絕對 pattern 直接用它;相對 `path` 以席位 cwd 補全、含 `..` 擋;祖孫關係用 `inStaging || aboveStaging`。`Glob` 的 `pattern` 含 `..` 也擋是多做(F2)。
- 二·4 Bash 粗擋:已實作且與設計回寫逐字相符。
  - 切詞符號 `/[\s'"`;|&(){}<>$\\]+/` 涵蓋規格列的 `; | & ( ) { } < > $ \` 加反引號,另含空白與引號,不切斜線。
  - 先轉小寫。
  - `gh`、`hub`、`glab`、`claude` 看整詞,或 `/`、`./`、`../`、`~/` 開頭的執行路徑最後一段。
  - `git` 配 `push`、`send-pack`、`send-email`。
  - `api.github.com`、`uploads.github.com`、`lumos-seat-staging` 字串。
  - 超過 1MB 擋、判斷出錯擋。
  - 理由文字教用 Read 讀檔、避開字、分成兩條指令,沒叫人改用 Grep。
- 二·5 三段式與固定開頭:已實作。`why()` 三段式;派工、工具、寫檔、暫存處、Bash 五種固定開頭。
- 二·6 出錯時擋誰:已實作。`call` 內 `checkTool` 出錯時,Bash 擋、其他放行;外層 `catch` 用 `seatishOf`(已登記或有審查席派工啟動中,`guard` 為 null 也算);`onCallFailed` 在工具已跑過時交回 `next(e)`,否則只擋審查席的 Bash。主會談(沒有 `agentId`)一律放行。唯一差異:`seatish` 只查記憶體,不查 `$.state`(F3 同一類邊界)。

〈做法〉三 安裝流程
- `_LUMOS_PLUGINS` 兩支、`_ledger_*` 改 `_lumos_plugin_*`、既有測試名不改並寫理由:已實作。
- 逐支「沒裝就裝」並用列表確認、第一次查詢出錯交給等待重查、不在判該支 failed:已實作。
- 市集檔沒列的那支回 no-source 略過:已實作,`_lumos_plugin_listed` 加 `_sync_claude_plugin`。
- 不跑 `marketplace update`:已實作。`scripts/lumos` 只有一行註解提到它,沒有呼叫。
- 回傳取最差,failed > no-source > absent > ok:已實作,`_PLUGIN_RANK`。
- 移除:已實作。外掛逐支獨立移除;全部成功才移除市集;任一支失敗保留市集,手動補做只列失敗的那幾支。市集歸屬三種情況與規格一致:確定是我們的就列移除市集;判不出來(查詢出錯)就列並附「先確認來源」那句;確定不是我們的就不列。
- `t_ledger_plugin_files_valid` 改動:見 F1。

〈範圍〉
- 範圍 1:已實作。`.claude-plugin/marketplace.json` 列兩支,`hooks.json` 與 `plugin.json` 齊。
- 範圍 4:已實作。事件帳 `spawnFields` 取 `e?.parentAgentId`,`spawnEvent` 一次給齊整組參數,`onSpawn` 只轉交。
- 範圍 5:已實作。`templates.md` 新增 §0;§1、§3、§7.6、§7.8 第一行都是 `LUMOS-SEAT: {loop}/{rN}/{席名}`,第二行指向 `/tmp/lumos-seat-work/{loop}/{席名}/`;編排者須知寫明收齊前不寫到硬碟與收貨時自己 `git status`;設計審與代碼審 SKILL 的「先存檔放著」已改;使用者記憶 `seat-reports-outside-repo-while-running.md` 已改。
- 〈不做〉各項:沒有越界。沒有事後查 repo、沒有逐詞解析 git、沒有 `$.process`,見 S10 測試的禁用清單。
- 落點:已實作。有 `Systems/lumos-guard` 新節點,另有 `lumos-cli-lifecycle`、`lumos事件帳` 的補句。

〈條款〉
- S1:已實作。`guard.test.ts` 有 S1 測試。
- S2:已實作。含相對、`.`、空段、過長、`/private/tmp`、Glob 固定段。
- S3:已實作。規格列的應擋與應過案例,測試標題都對得上(含 `cat mods/claude/x.ts`、`git log --grep=push`、`GH`、`/usr/bin/gh`)。
- S4:已實作。
- S5:已實作。含 markdown 修飾、全形冒號、一般派工提及 lumos-seat 不擋。
- S6:已實作。含「繼承時寫壞的標記不擋派工」。
- S7:已實作,F3 另有 ⚠。
- S8:已實作。
- S9:已實作。`t_lumos_plugin_install_review_fixes` 與 `t_install_registers_guard_plugin` 都存在。
- S10:已實作。`t_guard_plugin_files_valid` 含市集恰好是清單、禁用 `$.process`、不賦值事件欄位、`next` 只交 `e`,以及本機有 claude 時驗兩個掛鉤都掛 `.catch`。
- S11:已實作。`t_seat_templates_carry_marker`。
- S12:已實作。「同一支純函式給齊」由 `spawnEvent` 提供。
- S13:`[manual]` 條款,實作側無程式碼可對。驗證紀錄節點存在,我沒實跑。

總結:最嚴重 minor,blocking 0 條;縮水+未實作共 1 條
