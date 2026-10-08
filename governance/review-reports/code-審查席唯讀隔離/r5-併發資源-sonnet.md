severity: minor

範圍:r4 修正差異(`mods/claude/lumos-guard/hooks/register.ts` 的 `save` / `release` / `end` / `onEnd`、測試與筆記)。唯讀審查;實驗在 /tmp/lumos-seat-work/code-審查席唯讀隔離/r5s/ 的臨時複本。
repo 現況核對: `mods/claude/lumos-guard/hooks/register.ts:265-280`、`:340-356`、`:392-410`。

### F1 存回的時間上限改成逐格後,排隊的派工等「格數 x SAVE_MS」,「存回卡住時派工照常回傳」只在單一派工時成立
severity: minor
blocking: 否 — 只在 `$.state` 存回卡住(慢或不回)時才發生,延遲有上限(格數 x 2 秒),沒有放行或誤擋;但跟條款 S7 寫的「存回卡住時派工照常回傳」不符。
引句:「saving = saving.then(() => Promise.race([job(), io.sleep(SAVE_MS)]))」
引句:「          await save()」

時序:
1. 存回壞掉(`io.saveSeats` 永不回)。
2. 編排者同時派 N 席審查席(通常一批 4 到 8 席)。每席 `next(e)` 回來後各自 `await save()`,而 `save()` 回傳的是共用的 `saving` 鏈尾。
3. 每一格最多佔 SAVE_MS(2 秒),所以第 k 席的 `onSpawn` 要等 k x 2 秒才回傳。r3 的寫法是每個派工自己 `Promise.race([save(), io.sleep(SAVE_MS)])`,每席最多等 2 秒;r4 把上限搬進鏈裡,這個性質變成「鏈尾累加」。
4. 連帶:`release(session, p)` 在 `finally`,要等 `await save()` 回來才跑,所以子代理在這段時間的工具呼叫要等 `call()` 自己的 WAIT_MS(5 秒)逾時,才從記憶體 `seats.get(id)` 撈到席(撈得到,不會放行,但每次呼叫多等到 5 秒)。`session.end` 的 `onEnd` 也 await 同一條鏈,在「結束共用一個短時限」的 `session.end` 裡會被整條鏈拖長。

最小重現(臨時複本,SAVE_MS 縮成 200ms,鏈的寫法與 diff 相同,job 永不回):
```
node /tmp/lumos-seat-work/code-審查席唯讀隔離/r5s/sim.mjs
spawn 1 returned at 201 ms
spawn 2 returned at 405 ms
spawn 3 returned at 607 ms
spawn 4 returned at 808 ms
```
這是鏈寫法的簡化模擬,不是跑真外掛測試(本機沒用 `claude plugin test`);判準:要在 guard.test.ts 加「saveSeats 永不回、同時 3 個 spawn,第 3 個在約 SAVE_MS 內回傳」才會對症狀翻紅。現有 S7「存回卡住時會談結束照樣回來」只測單一派工 + 一次 end,看不到疊加。
建議方向:派工那頭保留自己的 `Promise.race([save(), io.sleep(SAVE_MS)])`(鏈裡的逐格上限留著),兩層都要。

### F2 逾時的那一格沒被取消,卡住的存回留在背景繼續跑、與下一格並行
severity: minor
blocking: 否 — 寫入交錯由 `ifVersion` 比對版本擋住(我逐個時序推過,見下),剩下是資源與重複提示;前提是引擎真的照型別檔實作 `ifVersion`(型別檔寫明 `isSet` 在別人先寫時為 false)。
引句:「saving = saving.then(() => Promise.race([job(), io.sleep(SAVE_MS)]))」

時序與結論:
- `Promise.race` 贏的是 sleep 時,`job()` 沒有被取消:它還在 `loadVersioned` 或 `saveSeats` 裡等,最多再跑 SAVE_TRIES 圈。下一格已經開跑,兩個 job 同時在讀、合併、寫。
- 交錯寫入安全嗎:job k 慢、job k+1 是 `end(drop S)`。k+1 讀 v1、去掉 S 的席、寫成 v2。之後 k 才回來,帶的是舊讀到的 v1(其中含 S 的席,合併時會從 saved 撈回來,因為 drop 是 undefined),`saveSeats(merged, 1)` 被 `ifVersion` 擋下回 false,下一圈重讀 v2、記憶體裡 S 已被 `end` 刪掉,收斂。我沒找到會復活 S 的路徑,前提是 CAS 有效。`version ?? 0`:型別檔 `StateRead.version` 是 number,不會缺值,這個補丁在真引擎上是死碼,不傷害。
- 剩下的壞處:(a) 存回持續卡住時,背景活著的 job 隨派工數線性累積(每個握著 merged 的複本與閉包,永不結束);我的模擬 4 格留下 4 個活 job。(b) 每個放棄的 job 各自跳一次「存回撞版 3 次放棄」提示,會重複;更糟的是被 race 丟掉的 job 之後若走到「撞版 3 次」才提示,而它的格早就算做完,提示時機與那一次派工無關。
- 熱重載兩份實例:各自一條 `saving` 鏈,只靠 `ifVersion` 協調,結論同上;沒發現新洞。
建議方向:job 帶一個「已被丟棄」旗標,逾時時設旗標,迴圈每圈與 `saveSeats` 前檢查(不必真取消 I/O);或把「卡住」的狀態記起來,卡住期間新存回直接跳過並合併成一次。

### 其他逐項判過、未立為發現
- `/clear`、接續(`keep`)時 `end` 變成完全不動:在途派工回來因 `endGen` 沒變而登記,`pending` 保留,時序成立;`pending` 只在該會談的派工全回來或之後真正結束時清。代價(舊會談席只增不減)筆記已列入誠實界線與回頭條件,不重複立項。若在途 `next(e)` 永不回,該會談 `pending` 永遠在,未知子代理每次工具呼叫多等到 5 秒才放行,屬既有性質。
- 同編號新舊派工交錯:`release(session, p)` 用派工自己那份 `p`,且只在 `pending.get(session) === p` 時刪;`end` 之後舊派工回來扣的是已脫離的舊物件,新派工計數不受影響。時序成立,測試也守住。
- `io.sleep` 沒帶 `signal`,依型別檔只有 abort 才會 reject,所以 `saving` 鏈不會被 sleep 弄成永久 rejected;未見問題(⚠ 引擎在外掛卸載時是否另行 reject sleep,型別檔沒寫)。
- `SAVE_TRIES` 圈內 `return` 與 `catch` 的結構:放棄提示在 `try` 內,`io.toast` 自己有 try/catch,不會把鏈弄 reject。

### 圖譜鏡頭
LUMOS-IMPACT 機械反查三格皆空(受影響測試 0、共改 0、呼叫者 0),沒有釘到的席筆記可逐條判,無條目。
- 計劃與 `Systems/lumos-guard` 筆記新增 S7 句子「存回卡住時派工照常回傳」「存回每一格都有時間上限」:F1 顯示後者成立、前者在多派工疊加時不成立,屬筆記寫得比實作強;不影響其他節點。
- 表態記錄 `py-eventloop na`(整支沒有 async def)針對的是 Python 探針,與本差異的 TS 外掛無關,判不影響。

總結:最嚴重 minor,blocking 0 條
