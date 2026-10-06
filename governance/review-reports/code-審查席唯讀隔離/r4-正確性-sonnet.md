severity: minor

審查範圍:/tmp/code-審查席唯讀隔離-r4.patch 全 1230 行。本機 `claude plugin test mods/claude/lumos-guard` 79 支全綠;`t_guard_plugin_files_valid`、`t_ledger_plugin_files_valid`、`t_seat_templates_carry_marker` 全綠。以下重現都在臨時複本 /tmp/lumos-seat-work/code-審查席唯讀隔離/r4-正確性-sonnet/c/hooks/x.test.ts,repo 未動。

先答鏡頭一點名的幾項(判不出問題的寫一句為什麼):
- 重試迴圈結束條件:`for (let i = 0; i < SAVE_TRIES; i++)` 三次撞版後落出迴圈、不丟錯、不存,席只留在記憶體。有界,不無窮。判不出問題。
- 版本號 undefined:型別檔 `state.get` 寫明「從沒寫過的值是 undefined、版本 0」,所以真引擎給的是 0;`undefined` 只在引擎少給 version 時發生,此時 `saveSeats` 退成無條件寫(兩份實例同時看到空檔時後寫蓋先寫)。條件是引擎違約,不標。
- 存回逾時後佇列的狀態:見 F1。
- NFKC 後比對跟原文比對:`firstLine` 回原文、`parseMarker` 用 `clean(line)` 只判「想不想寫標記」,合格與否仍用原文 `SEAT_RE`。開頭零寬字元、全形冒號、全形 LUMOS 都落到 bad(測試涵蓋)。兩邊一致。誤擋面見 F4。
- Glob 大括號:`\{([^{}]*)\}` 對巢狀大括號會抓到最內層,內層的絕對路徑或 `..` 仍擋;無閉括號的長字串是線性掃描,沒有效能問題。判不出問題。
- `/.vol/` 與資料卷別名、段數差一(先 pop 結尾斜線再數):走過 255、256、257 段與有無結尾斜線,正確。
- 新擋下分支誤擋正常工作:讀不到 `$.state` 時,任何有子代理編號者的寫檔被擋(不只審查席)。這是計劃明寫的取捨(判不出是不是審查席寧可擋),且只在 `$.state.get` 丟錯時發生,不標。

### F1 存回卡住後佇列永久卡死:會談結束的 `end` 不回、之後每次派工多等 2 秒、之後的席都存不進
severity: minor
blocking: 否 — 觸發需要 `$.state.set` 本身永不回傳,且引擎對 `session.end` 有 1.5 秒總上限,不會真的把會談結束拖死;影響是保護面縮小與派工變慢
引句:「await Promise.race([save(), io.sleep(SAVE_MS)])」
位置:`register.ts` 的 `save()`(`saving = saving.then(...)` 串行鏈)與 `spawn`、`end`。
走法:`saveSeats` 永不 resolve → 第一次 `save()` 的那一格 `.then` 永遠不結束 → `saving` 之後所有 `save()` 都排在它後面。`spawn` 靠 `Promise.race` 脫身,所以每次派工固定多等 `SAVE_MS`(2 秒),而且之後的席再也寫不進 `$.state`(熱重載後這些席不受保護)。`end` 非 keep 分支 `return save(session)` 沒有 race,`onEnd` 的 `await` 永遠不回。計劃條款 S7 只測了「派工不被拖住」,沒測 `end`。
重現:臨時複本 x.test.ts 的 A 測試(`saveSeats: () => new Promise(() => {})`,spawn 後 `onEnd` 300ms 內不回)紅:Expected "done" / Received "hang"。
建議方向:`end` 同樣對存回做逾時(或讓卡住的那一格有逾時後放掉),不要讓一次卡住毒化整條鏈。

### F2 /clear 時還在派工途中的審查席,回來後不登記,整席沒保護
severity: minor
blocking: 否 — 要同時撞上 /clear 與派工回傳的短窗口,影響限於那一席;但跟「/clear 不刪席、背景審查席照擋」的意圖相反
引句:「if (r && typeof r.agentId === 'string' && (endGen.get(session) ?? 0) === gen) {」
位置:`spawn` 的登記判斷與 `end(session, keep)`。
走法:`end` 一進來就 `endGen.set(session, +1)`,keep 分支也一樣;keep 的目的是讓背景審查席繼續被擋,但在飛的派工回來時 `endGen` 已變,`seats.set` 被整段跳過 → 這一席既不在記憶體也不在 `$.state`,之後工具呼叫查不到、放行。keep 時「結束前開始、結束後才登記完」的席該登記(只有非 keep 才該丟)。
重現:x.test.ts 的 B 測試(`g.end('S', true)` 後才 `fin({ agentId: 'a1' })`)紅:`_state.seat('a1')` 是 undefined。

### F3 會談結束後,舊派工的 release 會扣掉結束後新派工的啟動中計數
severity: minor
blocking: 否 — 只在「結束與新派工與舊派工回傳」交錯時發生,後果是新派工那一席登記前的第一批工具呼叫不等待就放行,窗口很小
引句:「if (p.n <= 0) pending.delete(session)」
位置:`end` 內 `pending.delete(session)` 與 `release(session)` 以會談編號為鍵。
走法:舊派工 A 在飛 → `end(S)` 刪掉 pending → 同編號新派工 B 建新的 `Pend{n:1}` → A 回來 `release(S)` 扣到 B 的計數 → n 變 0、`pending` 被刪,B 還沒登記。B 的子代理這時呼叫工具:`seat` 查不到且 `pending.has` 為假,直接放行。本輪新增的「結束後同一個編號再派」測試正好走這種同編號情境,卻沒涵蓋舊派工在飛。
重現:x.test.ts 的 C 測試紅:Expected 1 / Received 0。
建議方向:`release` 用派工開始時拿到的 `Pend` 物件扣,不用編號再查一次。

### F4 標記判準加了「空白也算連字號」後,第一行是散文的一般派工會被擋下
severity: minor
blocking: 否 — 理由文字教人「不是審查席就拿掉這行」,代價是一次派工重寫;但本 repo 自己的工作主題就叫 lumos seat,撞到機率不低
引句:「const SEAT_LOOSE_RE = /^lumos[-_\s‐-―]?seats?(?![a-z0-9_-])/i」
位置:`register.ts` 的 `SEAT_LOOSE_RE`,與 `parseMarker`。
走法:第一行 `Lumos seat guard 的 r4 修正`、`lumos seats are listed below`、`lumos-seat中文` 都判 bad 並回 `{ deny }`(後面接的是空白或中日文字,而 lookahead 只排除 ASCII 英數、底線、連字號)。分隔符可有可無(`?`)連 `lumosseat` 也算。測試只驗了 `Lumos seating plan` 這種接英文字母的 none。
重現:x.test.ts 的 D 測試印出三者皆 `kind:"bad"`。
⚠ 這是 r3 設計明寫要擋的方向(計劃:連字號寫成空白也算),只是把誤擋面標出來,是否接受由編排者裁。

### F5 只有 reason 為 clear 才保留席;resume 同樣是「行程繼續、換會談編號」
severity: minor
blocking: 否 — 沒能在單元層重現,取決於引擎在 resume 時背景子代理是否還活著
引句:「await st.guard?.end(e.sessionId, e?.reason === 'clear')」
位置:`onEnd`。
型別檔 SessionEndInput 寫:「after a /clear or a resume the process goes on under another」。若 /resume 時背景審查席仍在跑,走非 keep 分支會刪掉它們的席,跟 clear 同一個理由卻處理不同。計劃的誠實界線寫了 `--resume` 沒實測,但沒寫 in-process resume 這條。未能重現,自降為 minor。

圖譜鏡頭:
- 圖譜沒有釘到節點,「受影響測試、共改、呼叫者」三格皆空,備援段不逐條答。
- 表態記錄 py-eventloop na(整支沒有 async def):本次差異動的是 scripts/test_lumos.py 的測試函式與 TS 外掛,沒有往那支探針腳本加 async def;宣稱不受影響。
- 筆記一致性:`Systems/lumos-guard.md` 的 PITFALL 行寫「兩個掛鉤都掛 .catch」而 S10 現在寫「三個掛鉤只轉交給受測函式」,兩者講的是不同面向,不衝突。計劃〈誠實界線〉寫「對照表在一場會談內只增不減」,與 F1 的「存回卡住後連 end 的刪除也存不進」是同方向的殘留,可併入 REVISIT:2026-11-06 的觀察。

總結:最嚴重 minor,blocking 0 條
