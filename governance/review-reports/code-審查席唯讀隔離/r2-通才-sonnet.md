severity: major

圖譜牽連摘要:牽連清單共 12 檔,主要碰到 `lumos-cli-lifecycle`、`lumos事件帳`、`lumos-cli-read` 三篇的 ★INVARIANT★,另有三篇事故 Issue 被固定席帶出;本輪改動沒有直接違反其中任何一條合約行。

實測有跑:`claude plugin validate mods/claude/lumos-guard --json` 為 success,`types ./types/index.d.ts` 被引擎認得,`lumos-guard.seats` 的讀寫都被列出。`claude plugin test mods/claude/lumos-guard` 為 49 支全綠。我另把外掛複製到 `/tmp/lumos-seat-work/code-審查席唯讀隔離/通才-sonnet/p`,補了重現測試,下面兩條 major 都在那邊翻紅。

### F1 對照表整份覆寫,熱重載後只要登記一席新的,舊席就從 `$.state` 消失
severity: major
blocking: 是 — 上輪 r1p2(熱重載後執行中的審查席脫離白名單)的修法只在「重載後先呼叫過那一席」時成立,實際會讓審查席脫離白名單
引句:「try { await io.saveSeats(Object.fromEntries(seats)) } catch { /* 存不進去:這場仍在記憶體裡擋 */ }」
說明:`save()` 寫的是記憶體 `seats` 的整份快照。重載後記憶體是空的,`lookup` 只會把「被問到的那一個 id」讀回來。所以重載後的第一次 `spawn` 或 `end` 會把 `$.state` 覆寫成只剩新席,其他舊席被抹掉。`end(session)` 的 `void save()` 也一樣:重載後 `bySession` 是空的,既清不掉自己那場的席,又會把別場的席一起抹掉。
新測試「熱重載後…照擋」之所以綠,是因為它先 `g2.call(a1)` 把 a1 載進記憶體,才做後面的事,走不到這個分支。
最小重現(我加進複製版 guard.test.ts,兩支都紅):
```
const f = fakeIo()
const g1 = createGuard(f.io)
await g1.spawn('S','/repo',{prompt:'LUMOS-SEAT: L/r1/s'}, async()=>({agentId:'a1'}))
const g2 = createGuard(fakeIo(f.store).io)          // 模擬熱重載
await g2.spawn('S','/repo',{prompt:'LUMOS-SEAT: L/r1/t'}, async()=>({agentId:'b1'}))
expect(await g2.call('S',{tool:'Write',file_path:'/repo/a.md',agentId:'a1'})).toContain('lumos-guard 寫檔')  // 實際回 null,放行
```
第二支把 `spawn` 換成 `g2.end('S2')`(別的會談),結果相同。
建議:save 前先對 `$.state` 做 read-merge,用 `ifVersion` 防覆寫;`end` 只刪該場的 id。

### F2 Bash 粗擋改成「不切斜線」後,`$HOME/...`、相對路徑的 gh 與 claude 反而放行
severity: major
blocking: 是 — 上一版(以非英數字元切詞)會擋、這版放行,是 fix 引入的退步
引句:「const last = /^(\/|\.\.?\/|~\/)/.test(t) ? t.slice(t.lastIndexOf('/') + 1) : t」
說明:最後一段只在 token 以 `/`、`./`、`../`、`~/` 開頭時才取。`$` 是切詞符號,`$HOME/.local/bin/claude` 切出來的 token 是 `home/.local/bin/claude`,不符合前綴,整個 token 不在 `BASH_WORDS` 裡。`bin/gh`、`node_modules/.bin/claude` 這類相對路徑也一樣。這台機器的 claude 就裝在 `~/.local/bin/claude`,被誘導寫成 `$HOME/.local/bin/claude -p …` 是很自然的寫法。`~/bin/claude` 有測、`${HOME}/bin/gh` 因為大括號被切開而被擋,唯獨不帶大括號的 `$HOME/…` 漏掉。
重現:在複製版測試裡,`bashBlock` 對 `'$HOME/.local/bin/claude -p x'`、`'bin/gh pr create'`、`'node_modules/.bin/claude -p x'` 都回 null(預期要擋);`'${HOME}/bin/gh pr create'` 正確回非 null。
建議:token 只要含 `/` 就一律取最後一段比對。這樣 `mods/claude/x.ts` 的最後一段是 `x.ts`,不會誤擋,而 `docs/claude-notes.md` 也不受影響。

### F3 新的 `$.state` 接線完全沒被測試走過,出錯時靜默失效
severity: minor
blocking: 否 — 目前拿不出會翻紅的失敗場景,只是測試覆蓋的缺口
引句:「loadSeats: async () => (await $.state.get({ plugin: 'lumos-guard', key: 'seats' })).value ?? {},」
說明:`fakeIo` 在 `Io` 層就直接回 `{...store.seats}`,真實的 `$.state.get` 回 `{value, version}` 這層對應、`$.state.set` 的呼叫都沒被跑到。`lookup` 與 `save` 的 catch 都是靜默吞掉,沒有 toast。如果引擎端的 `state` 行為跟假的不同(例如 `set` 被拒),熱重載保護會無聲地關掉。Verification 筆記也寫了熱重載沒跑真機。
另外,`seatishOf`、`onCall` 的 catch 分支接線只測了純函式 `onCallFailed`,沒有測 `register` 裡 `seatishOf(st, e)` 那行。

### 前輪修復驗收
- r1c1、r1e1、r1s1、r1f3(Read 看不懂的路徑放行):已守住。`.`、`//`、`..`、相對路徑、超長路徑都擋,測試綠。
- r1e4(超長路徑平方級):已守住,`PATH_MAX` 與 `SEGS_MAX` 先判。
- r1s2(Bash 分大小寫):已守住,指令先轉小寫再比。
- r1e2、r1g2(`cat mods/claude/x.ts` 誤擋):已解,但修法引入 F2。
- r1g1、r1e2 後半(Bash 讀暫存處):依決策 d5 整類移出外層,屬流程性處置,外掛層面沒有守衛。
- r1e3、r1g3(標記加 markdown 修飾、`Lumos-seating plan` 誤擋):已守住。`- LUMOS-SEAT:`、引號、`1.` 這類包裝仍判 none,但舊版也是 none,不算退步,我也沒有具體失敗場景,不標。
- r1g4、r1s4、r1c2(onCall 吞錯、主會談 Bash 被擋):已守住。主會談與非審查席放行,審查席擋。
- r1p1(等整批才放行):已守住,每登記一席就喚醒等待者重查。
- r1p2(熱重載對照表歸零):未完整守住,見 F1。
- r1k1(事件帳 S12 接線):已守住,`spawnEvent` 把整組參數一次給齊,測試鎖在純函式上。
- r1k4(S10 只靠 `next({`):已加嚴,新增欄位賦值與 `next(` 非 `e` 的兩條正規式。
- r1p3、r1a1、r1c3、r1e5(安裝流程四處):已守住,有 `t_lumos_plugin_install_review_fixes` 對應。
- r1k2、r1k3、r1k6、r1f 系列(文字與計劃):已守住。
- r1s3(外掛原始碼在可被審查席改的 repo 裡):已誠實界線化並綁 REVISIT。

總結:最嚴重 major,blocking 2 條
