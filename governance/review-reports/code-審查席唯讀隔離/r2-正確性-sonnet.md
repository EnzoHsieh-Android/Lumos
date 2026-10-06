severity: major

## 正確性審查:lumos-guard 第 2 輪

### F1 熱重載後新登記一席,會把還沒被讀回記憶體的舊席從 `$.state` 抹掉,該席隨即不受管
severity: major
blocking: 是 — 審查席脫離白名單後可寫 repo、讀暫存處,這正是 r1p2 要堵的洞,修補本身沒堵住。
引句:「await io.saveSeats(Object.fromEntries(seats)) } catch { /* 存不進去:這場仍在記憶體裡擋 */ }」

走到的程式:
- 熱重載後 `createGuard` 重建,記憶體 `seats` 是空的。
- 審查席 A 還在跑,但還沒呼叫過任何工具,所以 `lookup` 沒把它讀回記憶體。
- 此時同批的審查席 B 派工,`spawn` 走到 `seats.set(B)` 再 `await save()`。
- `save()` 只寫記憶體裡的 `{B}`,整份覆蓋掉 `$.state` 裡的 `{A}`。
- A 下一次呼叫工具時 `lookup(A)` 記憶體查不到、`$.state` 也只剩 `{B}`,於是回 undefined,`call` 回 null 放行。

最小重現(`/tmp/lumos-seat-work/code-審查席唯讀隔離/正確性-sonnet/t1.mts`,用 `node --experimental-strip-types t1.mts` 跑):
- 兩個 guard 共用同一份 store:g1 登記 A,g2 登記 B。
- 輸出 `after B spawn state [ 'B' ]`。
- 接著 g2 對 A 的 `Write /repo/a.md` 回傳 `null`,也就是放行。

現有測試「熱重載後…照擋」只讓 g2 先對 a1 呼叫一次,把它讀進記憶體,才碰到不了這條路徑。

另外 `end()` 也有同形狀:它存的是記憶體的殘缺快照,而不是載入後再去掉本場的結果。後果較輕,因為本場的席都已結束。

修法:`save` 前先 `loadSeats` 再合併,或寫入時以讀到的狀態為底。`end` 也要這樣處理。

file: `mods/claude/lumos-guard/hooks/register.ts`(`createGuard` 內的 `save`、`lookup`)

### F2 出錯時判斷「是不是審查席」只看記憶體,熱重載後 Bash 反而放行
severity: minor
blocking: 否 — 只在掛鉤出錯與熱重載同時發生時才漏,且 F1 修好後影響更小。
引句:「return seats.has(id) || [...pending.values()].some(p => p.n > 0)」

- 走到的程式:重載後 `seats` 是空的,`$.state` 裡有登記的審查席 A,此時 `onCall` 因 `$.session.id()` 丟錯而進 catch。
- `seatishOf` 走 `st.guard.seatish(A)`,回 false,於是回 null,審查席 A 的 Bash 不擋。
- 反方向也有問題:只要任何會談有審查席派工在啟動中,出錯時所有非審查席子代理的 Bash 都會被擋。

### F3 Bash 粗擋「路徑最後一段」讓 repo 內的 `mods/claude` 目錄被誤擋,相對路徑的 `bin/gh` 反而放行
severity: minor
blocking: 否 — 有 Glob 與 Read 可繞,不影響隔離。
引句:「const last = /^(\/|\.\.?\/|~\/)/.test(t) ? t.slice(t.lastIndexOf('/') + 1) : t」

實測結果(同 `t1.mts`):
- `find /Users/x/repo/mods/claude -name "*.ts"` 被擋。
- `ls ./mods/claude` 被擋。
- `cat bin/gh`、`bin/gh pr list` 放行。
- `ls /repo/mods/claude/` 放行,因為結尾斜線讓最後一段變成空字串。

審查員在本 repo 逛 `mods/claude` 目錄是常見動作,所以誤擋有具體場景。含斜線但不以 `/`、`./`、`../`、`~/` 開頭的相對路徑執行檔(舊版會擋)現在成為漏洞,不過要先有那個 gh 執行檔。

### F4 標記寫壞的判準沒涵蓋 markdown 清單前綴,這類派工靜默不受管
severity: minor
blocking: 否 — 是編排者自己寫標記,要踩到才漏。
引句:「const SEAT_LOOSE_RE = /^[#>*_`\s]*lumos-seats?\s*[:：]/i」

實測:`- LUMOS-SEAT: a/b/c`、`1. LUMOS-SEAT: a/b/c`、`[LUMOS-SEAT: a/b/c]` 都回 `none`。派工不被擋,子代理也沒套白名單。這跟 r1e3 同一類(標記加修飾就靜默不認),只是修飾字元集合少了 `-`、數字加點、`[`。

### F5 移除失敗時印出的手動指令行尾帶 `# …` 註解,在 zsh 互動環境會變成多餘參數
severity: minor
blocking: 否 — 只影響失敗路徑的提示文字。
引句:「todo.append(f"{market_cmd}    # 先用 claude plugin marketplace list 確認它的來源是 lumos 的資料夾再刪")」

macOS 預設 zsh 互動模式不把 `#` 當註解(沒開 `interactive_comments`)。使用者整行貼上後,`#`、`先用`…會成為 `claude plugin marketplace remove` 的多餘參數。依 CLI 解析方式,可能報錯,也可能忽略後直接刪掉市集,而那正是這行註解要求先確認的事。建議把確認句另印一行。

### 逐 hunk 確認無問題的部分
- 等待迴圈:受 `timer` 約束一定會出來。`release` 與 `end` 都會叫醒等待者,pending 被刪後也會跳出。5 秒等待在 10 秒的掛鉤預算內。
- `realOf` 的 `PATH_MAX`、`SEGS_MAX` 在逐層 `real` 呼叫之前就擋掉,沒有平方級問題。
- `_lumos_plugin_ensure` 第一次查詢進 try,例外種類與 `_lumos_plugin_wait` 一致。
- `_lumos_plugin_listed` 對 null、數字、BOM 的處理正確。
- `spawnEvent` 直接轉交 `spawnFields` 的整份結果,沒有可選錯的欄位。
- `$.state` 的 `{ plugin, key }` 是字面量,符合型別檔要求;值是純 JSON。

### 圖譜鏡頭
四篇核心節點:
- `Systems/lumos-cli-lifecycle`:其 ★INVARIANT★(re-inject 不動 sentinel 之外)與本次市集檔解析和失敗訊息無關,不破壞。
- `Systems/lumos-cli-read`:本次動的是安裝與移除流程的失敗路徑,不碰 context、search、doctor 路徑,不破壞。
- `Systems/lumos事件帳`:`spawnEvent` 只是把參數整組交出,語意不變,不破壞。這篇 `updated` 已是 2026-10-06。
- `Systems/lumos-guard`:F1 讓筆記裡「熱重載後仍擋」的主張在特定交錯下不成立,需要等 F1 修了才算成立。我只看了程式碼面,沒有逐字核對筆記文字。

其餘牽連項(`lumos-deinit` 等)只列出,未逐篇核對文字:
- `Systems/lumos-deinit`:本次只改了 `_teardown_claude_plugin` 失敗時的提示行,不碰它的 `rmtree` 四重閘。
- 其他分組項(`bound-tests-gate`、`guard-kill` 等):這次改動沒有走到它們的合約面。

### 前輪修復驗收
- r1c1 / r1e1 / r1s1 / r1f3(Read 的 `.`、`//`、`..`、相對路徑):已修。這幾種路徑現在都擋。
- r1e4(超長路徑平方級):已修。
- r1c2 / r1g4 / r1s4(出錯時的 Bash 方向):部分。邏輯已拆開,但見 F2。
- r1p1(等待者要等整批):已修。每登記一席就喚醒等待者重查。
- r1p2(熱重載後對照表歸零):部分。「讀回」有做,「寫」會覆蓋掉舊席,見 F1。
- r1p3(裝完確認的第一次查詢):已修。
- r1c3(移除失敗時手動指令叫人移市集):部分。判別邏輯有了,但見 F5。
- r1e3 / r1g3(標記判準):部分。markdown 修飾已涵蓋,清單前綴沒有,見 F4。
- r1e2 / r1g2(路徑誤擋):部分。相對路徑不再誤擋,但「最後一段」仍誤擋目錄,見 F3。
- r1e5(市集檔 null 或 BOM):已修。

總結:最嚴重 major,blocking 1 條
