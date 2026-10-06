severity: minor

審查範圍:/tmp/code-審查席唯讀隔離-r3.patch 全文,重點在 mods/claude/lumos-guard/hooks/register.ts 與 scripts/lumos 的外掛清單。
重現全放在臨時複本 /tmp/lumos-seat-work/code-審查席唯讀隔離/r3c,測試檔 mods/claude/lumos-guard/hooks/r3exp.test.ts(X1–X6)。
`claude plugin test mods/claude/lumos-guard` 結果:原有 65 條全綠;我加的 6 條裡 X1、X2、X3、X4 紅,X5、X6 綠。
紅的是對外掛目前行為的探針,不是原測試壞掉。X5(8 席同時派、登記前就呼叫工具)與 X6(一席丟錯不影響別席的等待者)綠,表示同批登記與逾時以外的等待邏輯扛得住。
圖譜:這份派工沒有釘到節點,「圖譜沒有釘到節點」備援段不逐條答。我對照了設計計劃 `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`:F4 計劃只寫到 $.state 保不保留並排了回頭條件;F1、F2、F3、F5 計劃沒有寫到。

### F1 熱重載時新舊實例各自「先讀後寫」存回,後寫的抹掉先寫的席
severity: minor
blocking: 否 — 只在熱重載交錯的窄窗口出現,而且被抹掉的席要到下一次熱重載才失效,不是當下就放行。
引句:「saving = saving.then(async () => {」
位置:`mods/claude/lumos-guard/hooks/register.ts` 的 `save`(讀 `io.loadSeats()` 到 `await io.saveSeats(merged)` 中間隔著 await)。
時序:
1. 熱重載前的舊實例有一筆 spawn 還在飛,它的 `save` 已讀完 `$.state`、還沒寫。
2. 熱重載後的新實例登記另一席 B 並寫進 `$.state`。
3. 舊實例接著寫,覆寫成它讀到的舊內容加自己的 A,B 從 `$.state` 消失。
原因:`saving` 串行佇列是每個模組實例各一條,擋不住跨實例交錯。型別檔的 `$.state.set` 有 `ifVersion`(`claude-code.d.ts` 約 3312 行),`makeIo` 的 `saveSeats` 沒用。
重現:`r3exp.test.ts` X1,兩個 `createGuard` 共用一份 store、舊實例讀完卡在閘門上。結果紅(`Received: ["A"]`)。
後果:B 還在新實例的記憶體裡,當下照擋;下一次熱重載後 B 查不到,Bash 以外的工具放行(fail-open)。
修法方向:`state.get` 的 version 配 `set` 的 `ifVersion`,撞版就重讀重合併重試;重試要有次數上限。

### F2 熱重載落在「派工途中」:新實例沒有啟動中清單,子代理第一個工具呼叫放行
severity: minor
⚠
blocking: 否 — 要熱重載恰好落在子代理已啟動、登記還沒完成的窗口;窗口通常很短,但那一次是完全放行。判不準,因為不知道引擎熱重載時舊實例在飛的 `next` 會不會先被等完。
引句:「const r = await next(e)」
位置:`createGuard.spawn`:對照表要等 `next(e)` 回來才寫 `seats` 與 `$.state`,在這之前只有記憶體裡的 `pending`。
時序:
1. 舊實例 spawn 進入 `next(e)`,子代理已開始、尚未回 `agentId`。
2. 熱重載。新實例的 `pending` 是空的、`$.state` 裡也還沒有這席。
3. 子代理的第一個 `tool.call` 進新實例,`lookup` 回 undefined、`pending.has(session)` 為假,`call` 回 null 放行。
原因:S7 的熱重載保護只覆蓋「已登記之後」,「啟動中」清單沒有存進 `$.state`。
重現:`r3exp.test.ts` X2,兩個 `createGuard`,g1.spawn 的 next 卡住,g2.call 寫 /repo。結果紅(回 null)。
修法方向:派工一進來就把「啟動中」(會談與計數)寫進 `$.state`,或把登記提前到 `next(e)` 前用佔位記下派工詞推出的席位,回來再補編號。

### F3 存回與 spawn 回傳沒有上限:`$.state` 一卡,整條佇列和 spawn 都跟著卡
severity: minor
blocking: 否 — 要 `$.state.get/set` 本身掛住才會觸發;它在行程內,現實裡很少卡。
引句:「await save()」
位置:`spawn` 內 `await save()` 之後才 `return r`;`save` 內 `await io.saveSeats(merged)`。
時序:某次 `saveSeats` 永不回 → `saving` 這條 Promise 鏈永不結算 → 之後每一次 spawn(含非審查席以外的審查席派工)都卡在 `await save()`、`finally { release }` 跑不到 → `pending` 永遠不釋放 → 同會談其他子代理每次工具呼叫都等滿 5 秒再逾時放行。`call` 的等待有 5 秒上限,但 `save()` 的等待沒有。
重現:`r3exp.test.ts` X3,saveSeats 回永不結算的 Promise,50ms 後 spawn 仍未回傳、`pending('S')` 為 1。結果紅。
修法方向:存回不要擋住 spawn 的回傳與 release(先 release 再背景存,或對存回設逾時);`end` 已有引擎的短上限,這條只缺 spawn 這側。

### F4 會談結束刪掉的席,可能包含還在背景跑的子代理(/clear)
severity: minor
⚠
blocking: 否 — 設計計劃已列「/clear、--resume 之後還擋不擋」為待實測(REVISIT:2026-11-06),但它只寫「$.state 保不保留」,沒寫「外掛主動刪」這條。
引句:「for (const id of bySession.get(session) ?? []) seats.delete(id)」
位置:`createGuard.end`(記憶體刪除)加 `save(session)`(`$.state` 刪除)。
時序:型別檔說 `/clear` 時「行程在新 session id 下繼續」(`claude-code.d.ts` 約 10510 行)。若 /clear 前派出的審查席還在背景跑,`session.end` 一來,它的席就被刪光;之後它的 `tool.call` 查不到表,`call` 回 null 放行。
重現:`r3exp.test.ts` X4:spawn、`end('S')`、再用另一個 session id 呼叫該子代理的 Write 寫 /repo。結果紅(回 null)。
不確定處:背景子代理會不會在 /clear 時被引擎一起收掉,我沒有查到,所以標 ⚠。
修法方向:`end` 時只刪已確定結束的子代理(例如問 `$.agent.list()`),或 reason 為 clear 時保留;驗證紀錄裡補一條會談結束後席位留不留。

### F5 對照表只增不減(單一會談內);已結束標記集合也不清
severity: minor
blocking: 否 — 只是記憶體與 `$.state` 隨會談內派的席數增長,幾十席的量級沒有實際影響。
引句:「const ended = new Set<string>()」
位置:`ended` 加入後從不移除;`seats` 與 `$.state` 裡的席只在 `end` 時刪,子代理自己結束不刪。`save` 每次把整份合併後寫回,所以每次 spawn 的存回成本隨已登記席數線性增長,一場會談累計是平方。
後果:長時間自動迴圈(一個會談派幾百席)會讓每次 spawn 變慢,間接把 F3 的等待放大。
修法方向:`turn.complete` 或 `$.agent.list()` 發現子代理結束就刪;`ended` 只留最近 N 個。

### F6 安裝端:清單變三支後,最壞耗時近三倍;解除安裝時中途失敗的結果是靜默失去守衛
severity: minor
blocking: 否 — 只改了清單常數,逐支邏輯與兩個 install 同時跑的等待重查是既有、有測試的路徑;這條只指出最壞耗時與方向。
引句:「_LUMOS_PLUGINS = ("lumos-ledger@lumos-toolchain", "lumos-context@lumos-toolchain", "lumos-guard@lumos-toolchain")」
位置:`scripts/lumos` 的 `_sync_claude_plugin` 與 `_teardown_claude_plugin` 迴圈。
說明:
- 每支最壞耗時是列表查詢 30 秒、install 30 秒、裝完確認 10 秒、等待重查最多 10 秒的預算;`claude` 卡住時三支串行比以前多一個最壞的一輪。沒有整段上限。
- 兩個 install 同時跑:每支各有最終狀態重查,第三支沒有新風險。我看過代碼,沒有找到會讓第三支特別容易壞的路徑。
- 移除做一半失敗:只移掉前兩支時守衛仍在(安全方向);只移掉守衛時市集保留、手動指令列出失敗那幾支,印出的訊息沒有點出「守衛已被移除、審查席現在不受限制」。
我沒有實測這一條,只讀了碼。

總結:最嚴重 minor,blocking 0 條
