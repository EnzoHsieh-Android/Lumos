severity: major

### F1 save() 用記憶體子集覆寫整份 $.state,熱重載後新派一席會抹掉其他執行中的席
severity: major
blocking: 是 — 守衛失效(fail-open):熱重載後仍在跑的審查席,在有人新派一席後脫離白名單。這正是 r1 修熱重載要堵的洞,修補本身又開了一條。
引句:「try { await io.saveSeats(Object.fromEntries(seats)) } catch { /* 存不進去:這場仍在記憶體裡擋 */ }」
時序:
1. 熱重載後模組變數歸零,`seats` 是空的,`$.state` 裡還有 A、B。`lookup` 是按需讀回,只在 A 或 B 自己下一次呼叫工具時才會把它載進記憶體。
2. 這時編排者派新席 C。`spawn` 登記 C 之後呼叫 `save()`,寫進去的是 `{C}`,A 和 B 從 `$.state` 消失。
3. A 或 B 還沒讀回就呼叫工具:記憶體沒有,`lookup` 讀到的 state 也沒有,回 undefined,`call` 回 null 放行。
4. 席位閒置(等模型回應、等長工具)正好落在第 1 步到第 2 步之間時,就會中招。

重現:我在 `/tmp/lumos-seat-work/code-審查席唯讀隔離/併發資源-sonnet/t.mts` 用 node 24 直接載入 `register.ts`,注入假 io。state 預置 `{A,B}`,新建 guard,`spawn` 一個回 `agentId: 'C'` 的席,再對 A 呼叫 `Write /repo/x`。實測輸出:
- `T1 state keys after C registered: [ 'C' ]`
- `T1 A tool call (Write /repo/x): null`(應該是擋下)

同根的交錯寫入:`save()` 取快照是同步的,但 `$.state.set` 是非同步,也沒用 `ifVersion`。兩席同時登記時,先取快照的那次若較晚落地,就蓋掉後取快照的那次。同一支假 io 讓第一次寫入慢 50ms、第二次快,最後 state 只剩 `[ 'A' ]`(`T3 state keys`),B 丟失。真引擎是否保證 `$.state.set` 依呼叫順序落地,型別檔沒寫,所以這一半我標「未能在真引擎重現」,只在假 io 下成立。
建議:不要寫整份記憶體。改成先 `$.state.get` 拿到 `{value, version}`,合併後用 `ifVersion` 寫,失敗就重讀重試。或在 `lookup` 之外,於 `save` 前先把 state 整份讀進 `seats`。

### F2 end() 之後才登記完成的派工會把已結束會談的席重新放回對照表與 $.state
severity: minor
blocking: 否 — 只造成殘留與洩漏,不影響擋人。
引句:「for (const id of bySession.get(session) ?? []) seats.delete(id)」
時序:
1. 派工 `next(e)` 還沒回來。
2. `session.end` 觸發 `end()`:刪掉該會談的席,`pending.delete`,`void save()`。
3. `next` 才回來,`spawn` 接著執行 `seats.set`、重建 `bySession`、再 `save()`。

這一席之後沒有任何 `end` 會清它,而且寫進了 `$.state`。重現同上檔的 T2:`T2 leaked seat after end: true [ 'C' ]`。
另外,熱重載後經 `lookup` 讀回的席只進 `seats`、不進 `bySession`,`end()` 同樣刪不掉它們。

### F3 Python 端裝完確認的總預算沒有把前面的查詢與 install 算進去
severity: minor
blocking: 否 — 只在 claude 卡住時拉長等待,功能不錯。
引句:「    if not (seen or _lumos_plugin_wait(lambda: _lumos_plugin_user(claude, pid))):」
場景:`claude plugin list` 掛住時,每支外掛最壞要累計 `install` 30 秒、第一次 `_lumos_plugin_user` 30 秒、`_lumos_plugin_wait` 的 1 秒加上一次 30 秒查詢,約 91 秒。兩支外掛加市集操作可能超過 3 分鐘且沒有輸出。`budget=10.0` 只約束 wait 自己開新一次的時機,不是整個函式的總預算。

### 前輪修復驗收
- 等待迴圈:我沒有找到漏醒。`waiters.push` 與 `seats.get` 檢查在同一個同步段內,`wake` 清空陣列後等待者會重查並重新登記。`release` 讓 `n<=0` 的 `Pend` 被刪除後,迴圈靠 `pending.has` 結束。`end()` 喚醒後等待者會靜默放行(沒有逾時提示),可接受。
- 共用一個 5 秒計時器:每次登記都喚醒重查,不會空轉。
- 預算:`$.clock.sleep` 的 5 秒算進 10 秒預算,`lookup` 的 `$.state.get` 與 `$.fs.stat` 不算,所以沒超。
- 登記後、喚醒前 `await save()` 會延後喚醒,但只影響「比 `seats.set` 還早到的呼叫」。我用假 io 讓 `saveSeats` 卡 6 秒,席已在記憶體時 `call` 直接擋下,所以不是問題。
- `lookup` 讀 state 後寫回記憶體本身正確,問題在 F1 的寫回方向。
- `void save()` 內部有 try/catch,不會有未處理的 rejection。
- `_lumos_plugin_ensure` 第一次查詢的例外改走等待重查,方向正確。
- 上一輪「熱重載後對照表歸零」只修了讀的一半,寫的一半見 F1。

總結:最嚴重 major,blocking 1 條
