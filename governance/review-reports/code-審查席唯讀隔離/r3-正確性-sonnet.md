severity: major

審查範圍:d0b24391..HEAD(patch 1494 行)。本機跑 `claude plugin test mods/claude/lumos-guard` 63 全綠;`python3.14 scripts/test_lumos.py -k guard_plugin` 24 綠、`-k install_registers` 25 綠。三支外掛合併處(`_LUMOS_PLUGINS`、市集檔、teardown 文字、測試)沒找到問題。圖譜鏡頭:尾端是「圖譜沒有釘到節點」備援段,不逐條答;角色卡沒附,略過。

### F1 會談結束後同一個會談編號再出現,審查席不再登記,隔離整個失效
severity: major
blocking: 是 — 守衛靜默失效(放行)且測試沒覆蓋;但「引擎會重用同一個會談編號」這個前提我沒能在真引擎驗到(⚠)

1. 觸發:同一個 guard 實例(同一行程、沒熱重載)裡,先 `session.end`(例如 `/clear` 之後又 `/resume` 回舊會談,型別檔說 resume 會讓行程換 id,回到舊會談時 id 可能是原本那個),之後該 id 又派審查席。
2. 路徑:`end()` 做了 `ended.add(session)`,而且從不移除;`spawn` 裡 `if (r && typeof r.agentId === 'string' && !ended.has(session))` 條件為假,席位不進 `seats`、不進 `$.state`;`call()` 的 `lookup` 查不到、`pending` 也已釋放 → `if (!seat) return null` 放行。結果:該席可以寫 repo、跑 `gh`。
3. 重現:臨時複本 `/tmp/lumos-seat-work/code-審查席唯讀隔離/r3-copy/mods/claude/lumos-guard/hooks/probe.test.ts` 的 P1(`createGuard`→`end('S')`→`spawn('S', LUMOS-SEAT)`→`call` 寫 `/repo/a.md`),`claude plugin test` 結果 紅(Expected 含 "lumos-guard",Received null)。
4. 位置:`ended` 的設計目的只是擋「會談結束後才回來的在途派工」。可改成 spawn 開始時記下當時的世代(或在新的 spawn 進來時 `ended.delete(session)`),只擋「結束前就開始、結束後才完成」的那批。

引句:「if (r && typeof r.agentId === 'string' && !ended.has(session)) {」

### F2 寫檔路徑解析:最深已存在上層的判斷把「stat 丟錯」一律當「不存在」,懸空連結在真引擎的行為未驗
severity: minor
blocking: 否 — 沒能重現(降一級);測試假件把懸空連結建模成 `undefined`,真引擎可能是丟 ENOENT

1. 輸入:工作資料夾裡有一條指向「尚不存在的 repo 路徑」的符號連結(`dang`),Write 它。
2. 路徑:`realOf` 對 `.../s/dang` 呼叫 `io.real`;`makeIo.real` 直接回 `(await $.fs.stat(path,{resolve:true})).realPath`。型別檔說 `stat` 對缺檔 reject ENOENT、懸空連結則 `realPath` 缺。若引擎對懸空連結是 reject 而非回無 realPath,`catch { continue }` 會往上走到 `.../s`(存在),接上 `dang` 判成在工作資料夾內放行,而實際寫入會穿過連結建出外面的檔。假件(`fakeReal` 回 `undefined`)與真引擎行為是否一致沒人驗。
3. 沒有真引擎可跑 `$.fs.stat`,未能重現。建議在測試或手動對真引擎驗一次懸空連結的回應;若是 reject,改成先判 `isLink` 或對「catch 之後往上走」的那一層再 stat 一次末段是否為連結。

引句:「real: async path => (await $.fs.stat(path, { resolve: true })).realPath,」

總結:最嚴重 major,blocking 1 條
