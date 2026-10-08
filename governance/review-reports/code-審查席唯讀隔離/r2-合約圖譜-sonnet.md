severity: major

本輪驗過的環境:在 `git clone --shared` 複本 `/tmp/lumos-seat-work/code-審查席唯讀隔離/合約圖譜-sonnet/c` 改壞,repo 本身沒動。`claude plugin test mods/claude/lumos-guard` 是 49 支、`lumos-ledger` 是 25 支,都全綠。四支 Python 測試的條數全部對得上(11、10、16、10)。`lumos lint` 與 `lumos doctor` 都是 0 問題。`claude plugin validate` 過,有警告。驗證紀錄裡的「不跑 marketplace update」重跑指令,我實跑成功(兩支都 Successfully installed,約 2 秒,不是寫的 30 秒)。

### F1 事件帳 S12 的接線改壞照綠,上一輪 r1k1 沒真正收掉
severity: major
blocking: 是 — 上一輪 major 指的「改回 e.agentId 照綠」仍能重現,且筆記宣稱已經不可能
引句:「接線那行沒有欄位可選錯」
引句:「await record(st, $, agent, ev, extra)」
file: `mods/claude/lumos-ledger/hooks/register.ts:339`
- 重現:在複本把 `await record(st, $, agent, ev, extra)` 改成 `await record(st, $, e.agentId ?? null, ev, extra)`,跑 `claude plugin test mods/claude/lumos-ledger`,結果 25 pass 0 fail。
- 原因:`onSpawn` 把 `spawnEvent` 的回傳拆成三個變數,再以位置參數傳給 `record`。發起方那個參數仍然可以接錯,新測試只驗純函式 `spawnEvent` 的回傳值。
- 影響:事件帳筆記寫「沒有欄位可選錯」是不實的。r1 收貨表記的「onSpawn 直接把 spawnFields 的結果整份交給 record」也沒做到。
- 建議做法:改成 `record(st, $, ...spawnEvent(e, r))`,或測試走真的 `onSpawn`。

### F2 熱重載後下一次 spawn 或 session.end 會把 `$.state` 裡的其他審查席洗掉
severity: major
blocking: 是 — 筆記宣稱熱重載後執行中的席「照擋」,實際上只撐到下一次存檔
引句:「外掛熱重載後對照表從 `$.state` 讀回」
引句:「記憶體查不到時讀回,代碼審 r1」
file: `mods/claude/lumos-guard/hooks/register.ts:231`
file: `mods/claude/lumos-guard/hooks/register.ts:303`
- 原因:`save()` 一律寫 `Object.fromEntries(seats)`,也就是只含記憶體裡的席。重載後 `seats` 是空的,只有「被查過一次」的席才會被 `lookup` 讀進來。
- 重現:把下面兩支測試貼到 `guard.test.ts` 末尾,跑 `claude plugin test mods/claude/lumos-guard`,結果 49 pass 2 fail,兩支都紅。
  - 第一支:g1 登記 a1 與 b1;g2 以同一份 store 重建,再 spawn c1;g3 再重建,`g3.call(... agentId:'b1' ...)` 預期被擋,實際放行,因為 store 只剩 c1。
  - 第二支:g1 在會談 S 登記 a1、在會談 T 登記 b1;g2 重建後 `end('S')`,store 預期只剩 `['b1']`。`bySession` 重載後是空的,`save()` 寫進空的 `seats`,b1 也被洗掉。
- 為什麼測試沒抓到:`S7 熱重載後` 測試只做「重載、讀回、再派子代理」一次,沒測重載後的第二次存檔。
- 建議做法:`save()` 改成先讀 `$.state` 再合併,`end()` 只刪本場的 id。

### F3 d5 還有兩份手冊寫舊做法,計劃卻宣稱已改
severity: major
blocking: 是 — 收貨編排者照 reference.md 做就會違反 d5,且沒有任何測試守這件事
引句:「先到的席報告先存檔放著」
file: `skills/lumos-code-loop/reference.md:574`
file: `skills/lumos-design-loop/reference.md:514`
- 重現:`grep -n "先到的席報告先存檔放著" skills/*/reference.md` 命中 2 行,兩份都沒進這次差異。
- 計劃做法 5 寫「設計審與代碼審手冊『先到的席報告先存檔放著』那句改成收齊前不落地」。實際只改了兩份 `SKILL.md` 與 `templates.md`,「先存檔放著」這句只存在於 `reference.md`。
- `t_seat_templates_carry_marker` 只讀 `templates.md`。把 `SKILL.md` 改回舊句,或不碰 `reference.md`,都不會有測試翻紅。

### F4 SKILL 裡「收席報告第一個動作是 ls」與「報告不寫到硬碟」互相矛盾
severity: minor
blocking: 否 — 屬文字內部矛盾,不改變程式行為
引句:「收席報告第一個動作是 `ls` 確認檔真的在」
- 兩份 `SKILL.md` 的同一段先寫「先到的席報告先留在對話裡、不寫到硬碟」,下一句仍叫人 `ls` 確認檔在。
- 使用者記憶 `seat-report-intake-discipline.md` 仍寫「每一席回來立刻存檔」,跟已改的 `seat-reports-outside-repo-while-running.md` 互相打架。它在 repo 外,只提醒不算 repo 缺陷。

### F5 本輪新增的行為有三處沒測試,改壞照綠
severity: minor
blocking: 否 — 每處現況都是對的,只是守不住
引句:「工作目錄取輸入的 `cwd`,沒給就沿用發起方的」
引句:「判不出來照列並附一句先確認來源」
引句:「轉小寫,再以空白、引號與 shell 符號」
- 子代理 cwd 繼承:把 `register.ts` 的 `: parent.cwd }` 改成 `: sessionCwd }`,49 pass 0 fail。測試只覆蓋頂層席的 `cwd: '/tmp/scratch'`。
- 移除時「判不出來照列並附一句」:把 `elif ours is None:` 改成 `elif False:`,11 與 10 條都全綠。只有「是我們的」與「確定不是」兩條被測。
- Bash 切詞裡的反斜線:把切詞字元集拿掉 `\\`,49 pass 0 fail。拿掉後 `\gh pr create` 這種跳脫別名寫法就會放行。

### F6 S10 的「不賦值事件欄位」只認 `e.x =` 一種寫法
severity: minor
blocking: 否 — 屬靜態守衛的涵蓋範圍,不是現有缺陷
引句:「不賦值事件欄位、`next` 只交 `e`」
- 我拿目前的規則(正規式 `\be\??\.[A-Za-z_]\w*\s*(=(?!=)|\+=|-=)`)試了幾種寫法,下列都不會被抓到:
  - `e['tool'] = 'x'`
  - `Object.assign(e, {...})`
  - `e.cwd ||= '/x'`
  - `delete e.command`
  - `e = { ...e, tool: 'x' }`
- 反過來,`next( e )` 這種多了空白的寫法會被誤判成「把 e 以外的東西交下去」。

### F7 效能數字不是最壞情況
severity: minor
blocking: 否 — 數字量級有誤,但不影響行為
引句:「5MB 派工詞 7 毫秒」
引句:「接近 1MB 的 Bash 指令最慢 62 毫秒」
- 我在 `claude plugin test` 的執行環境量到:
  - 5MB 全是換行的派工詞,`parseMarker` 約 125 毫秒;5MB 全是空白行約 77 毫秒。
  - 1MB 左右的 Bash 指令,`bashBlock` 最慢的形狀(`'a '` 重複約 50 萬次)約 115 毫秒;`a;b ` 重複約 107 毫秒。
- 機器不同數字會不同,但派工詞差了 10 倍以上,應標明量的是哪種形狀,或改成量最壞形狀。「多用 15MB」我量不到(測試環境沒有 `process`)。

### F8 `lumos-guard` 筆記與計劃回退節有兩處沒跟上改動
severity: minor
blocking: 否 — 是舊句子沒跟著改,不會讓程式做錯事
引句:「沒跑過 Bash 擋、其他放行」
引句:「外掛不寫任何檔,沒有資料要清」
file: `mods/claude/lumos-guard/hooks/register.ts:371`
- 第一句在 `lumos-guard.md` 的 PITFALL 修法裡。現行 `onCallFailed` 只擋「審查席的 Bash」,主會談的 Bash 放行,計劃 S8 也這樣寫,所以筆記那句寫得太粗。
- 第二句在計劃回退節。現在外掛會往 `$.state` 寫 `lumos-guard.seats`,`claude plugin validate` 也列出 state writes。拿掉外掛後這份資料要不要清,回退節沒說。

### 固定席逐條
- **第 1 項,宣稱逐句驗證**:
  - 測試支數:外掛 49 支、事件帳 25 支、Python 11、10、16、10 條,全對。
  - 改壞「再改壞 17 處」:我只抽驗 14 處(外掛 12、Python 5 裡扣掉語法失敗那處,共約 17 次實驗),其中 F5 列的三處與 `aboveStaging` 的祖先判斷(`ROOTS.some(r => r === p || r.startsWith(p + '/'))` 改掉,0 紅)沒翻紅。「全翻紅」的說法對這幾處不成立。
  - 效能:見 F7。
  - 可重跑指令:有效(見檔首)。
- **第 2 項,最可能假綠的五處改壞**:
  - 事件帳接線(F1):假綠。
  - 子代理 cwd 繼承、反斜線切詞(F5):假綠。
  - 熱重載後存回(F2):測試沒涵蓋這個情境。
  - `utf-8-sig` 與 `isinstance(..., str)`:前者翻紅;後者(`name` 不是字串)沒翻紅,但影響很小,不另列。
  - 其餘 12 處(`SEAT_LOOSE_RE` 兩處、`SEGS_MAX`、`PATH_MAX`、`called`、`seatish`、`toLowerCase`、`~/`、最後一段、release 喚醒、存檔、`end` 寫狀態等)都翻紅,守得住。
- **第 3 項,d5 散落位置**:
  - 一致的地方:範本 §0、兩份 `SKILL.md`、計劃名詞與誠實界線、`lumos-guard.md`、記憶檔。
  - 沒改的地方:兩份 `reference.md`(F3)。
  - 內部矛盾:`ls` 一句(F4)。
  - 程式碼這一頭:擋讀暫存處的行為與 d5「留著當多一層保護」一致。
- **第 4 項,四篇圖譜**:
  - `lumos-cli-lifecycle`:多支外掛、不跑 update、測試清單三處與 `_sync_claude_plugin`、`_teardown_claude_plugin` 一致,未發現矛盾。唯一的 ★INVARIANT★(re-inject)不在這次牽連範圍。
  - `lumos-cli-read`:唯一提到外掛的是 `events` 一段,沒有被這次改動打破。它的 ★INVARIANT★(search 排除 superseded)與這次無關。
  - `lumos事件帳`:`updated` 已更新;S12 的「沒有欄位可選錯」不實(F1);TEST 清單沒列新測試名,屬非阻擋的疏漏。
  - `lumos-guard`:F2、F8。它的 RULE(不呼叫 `$.process`、只掛三個事件)與程式碼一致,`lumos lint` 0 問題。

### 前輪修復驗收
- 已修且我實測守得住:
  - 讀檔看不懂的路徑一律擋。
  - Bash 轉小寫且路徑裡含 `claude` 不誤擋。
  - 寫壞標記的判準。
  - 出錯時只擋審查席的 Bash。
  - 每登記一席就喚醒等待者。
  - 市集檔 BOM 與 `plugins` 欄位怪值。
  - 裝完確認的第一次查詢丟錯。
  - 移除時判市集歸屬(「確定不是我們的」那支)。
- 未真正修好:r1k1(事件帳接線,見 F1)、r1p2(對照表存 `$.state`,見 F2),r1f 組筆記裡「手冊先存檔放著」那句(見 F3)。

總結:最嚴重 major,blocking 3 條
