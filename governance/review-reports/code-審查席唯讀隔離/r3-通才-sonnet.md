severity: major

# r3 通才審查(sonnet)

範圍:全份 diff 逐 hunk(lumos-guard 外掛、事件帳 spawnFields/spawnEvent、scripts/lumos 外掛清單、測試)。
外掛清單合併三支的改動(`_LUMOS_PLUGINS`、marketplace.json、測試期望)互相一致,沒找到洞。型別檔核對:`$.fs.stat` 對不存在丟 ENOENT、懸空連結 realPath 缺席,與 `realOf` 的假設一致;`agent.spawn` 的 `next` 在子代理啟動後就回(非等它跑完),所以 7 的等待機制成立。

### F1 macOS 資料卷別名路徑繞過暫存處判斷
severity: major
blocking: 否 — 只在知道別名路徑時才繞得過,守衛本身(連結、大小寫、/tmp 別名)其他路徑都守住了;⚠ 嚴重度取決於是否把「有心繞」算進威脅
類別:路徑別名未正規化(跟「/tmp 是連結」同一族,但實際路徑解析不折疊它)。
位置:`mods/claude/lumos-guard/hooks/register.ts` 的 `rootOf` / `ROOTS` / `FOLDERS_ROOT`(S2 的 Read、Grep、Glob 都靠它)。
引句:「const ROOTS = ['/private/tmp', '/private/var/tmp', '/tmp', '/var/tmp']」
說明:macOS 的資料卷在 `/System/Volumes/Data/private/tmp/...` 也看得到同一批檔案,該路徑 realpath 後仍是自己(本機實測 `/System/Volumes/Data/private/tmp` 存在,node `fs.realpathSync` 回傳原樣,`rootOf` 比對結果 null/undefined),所以 `inStaging` 回 false、`aboveStaging` 也不認(搜尋範圍 `/System/Volumes/Data` 或其下 `private` 不在祖先判斷內)。Read 該別名下的 lumos-seat-staging、或 Grep/Glob 指到 `/System/Volumes/Data/private` 都放行。型別檔自己也警告「a hard link or a case alias keeps its own」。寫檔那側因 `rootOf` 回 null 反而擋(安全方向),不受影響。
最小重現(翻紅):guard.test.ts 的 `EXISTS` 加 `/System/Volumes/Data/private/tmp/lumos-seat-staging/L/r1-x.md` 與其各層上層,再加
`expect(await chk({ tool: 'Read', file_path: '/System/Volumes/Data/private/tmp/lumos-seat-staging/L/r1-x.md' })).toContain('lumos-guard 暫存處')` → 目前回 null,紅。(我只在 /tmp 複本驗了前提:別名存在、realpath 不折疊;沒有跑完整外掛測試。)
建議:realOf 之後先剝掉 `/system/volumes/data` 前綴再比;或把它加進 ROOTS 與 aboveStaging。

### F2 `ended` 只增不減:同一個會談編號重現時,之後的審查席不登記
severity: minor
blocking: 否 — 需要 /resume 回到同行程內已結束過的會談編號,型別檔沒保證會或不會;⚠ 判不準
類別:狀態生命週期。
位置:`createGuard` 的 `ended` 集合與 spawn 內判斷。
引句:「if (r && typeof r.agentId === 'string' && !ended.has(session)) {」
說明:`end(session)` 把會談編號永久放進 `ended`。型別檔說 /clear 後換新編號(安全),但 resume 是「另一個會談取代它」,若同行程內 resume 回已結束過的編號,之後該會談所有審查席派工都不進對照表,`call` 查不到席就放行——整席無隔離且沒有任何提示(沒有 toast)。同行程重載 guard 也會讓 `ended` 歸零,行為不一致。
重現:未能重現(需要真引擎的 resume 行為);單元層可寫:`g.end('S'); await g.spawn('S',…LUMOS-SEAT…, async()=>({agentId:'a1'}))` 後 `g._state.seat('a1')` 為 undefined,即現行設計,是否合理要看引擎。
建議:會談再次出現 spawn/call 時把它從 `ended` 移除,或只在「end 發生時仍在途」的派工上標記作廢,而不是整個會談編號永久封存。

### F3 派工側讀不到 $.state 時,孫代理失去隔離(跟 call 側「Bash 擋」方向不一致)
severity: minor
blocking: 否 — 需要熱重載後記憶體空且 $.state 讀取丟錯,兩個條件同時成立
類別:fail-open 與 fail-closed 方向不一致。
位置:`createGuard.spawn` 開頭。
引句:「const parent = found === 'error' ? undefined : found」
說明:`call` 在 lookup 回 'error' 時對 Bash 擋(`BASH_ERROR`),但 `spawn` 在同一狀況把發起方當成「查無」,孫代理派工詞沒標記就 `next(e)` 直接放行,且不登記。該孫代理之後的工具呼叫又因 lookup 查不到而放行(若此時 state 恢復讀取仍查不到)。
重現:`fakeIo` 的 loadSeats 丟錯,`g.spawn('S','/repo',{prompt:'無標記',parentAgentId:'unknown'},next)` → 走 `next(e)`,孫代理不受限;以現有測試風格寫即可翻紅(期望 deny 或登記為審查席)。
建議:'error' 時有 parentAgentId 就比照 `seatish` 的保守方向(當審查席繼承或擋下派工),至少 toast 一次。

### 其他核對(判不成立,不標)
- 事件帳 `spawnEvent`:發起方改 `parentAgentId`,接線只轉交整組,測試鎖形狀,沒有洞。
- `onCallFailed`:`next.called` 為真時回 `next(e)` 不重跑,與型別檔 Caught 語意一致。
- 席名大小寫(fold 小寫)造成同迴圈下只差大小寫的席共用工作資料夾,屬可接受的碰撞,沒有失敗場景對應威脅,不標。
- 圖譜鏡頭:三格皆空,無固定席筆記可逐條答;改動檔在 base 樹無測試與呼叫者,不影響既有路徑。

總結:最嚴重 major,blocking 0 條
