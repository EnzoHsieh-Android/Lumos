severity: minor

通讀 1230 行差異。路徑判定、版本化存回、讀不到對照表的方向、標記判準、掛鉤接線與範本同步大致銜接得上。以下三條是修正本身或修正銜接處留下的洞,都在 /tmp/lumos-seat-work/code-審查席唯讀隔離/r4x/ 的臨時複本用 node 24 重現過(只轉型別,邏輯沒動)。

圖譜鏡頭逐條:
- 受影響測試、共改、呼叫者三格皆空:機械反查沒有命中,不影響判斷。
- 表態記錄(py-eventloop na):這次差異沒有新增 async def 的 Python 探針,宣稱未被反駁。

### F1 Glob 的 `..` 只擋大括號選項,第一個萬用字元之後的 `..` 仍放行
severity: minor
blocking: 否 — 暫存處讀取保護本來就是盡力而為(誠實界線已寫 Bash 讀得到),且引擎對 `*/..` 的實際解析沒實測。
⚠ 引擎的 Glob 實作會不會真的解開萬用字元後面的 `..` 我判不準。
r3 為同一類「搜尋範圍算不準」補了大括號選項,但同族的 `..` 出現在第一個萬用字元之後的段、或大括號外面,沒有掃完。
引句:「// 大括號選項裡放絕對路徑或 .. :搜尋範圍算不準,當看不懂(代碼審 r3);一般的 *.{ts,js} 照常」
位置:mods/claude/lumos-guard/hooks/register.ts 的 searchBase(Glob 分支)。固定段迴圈在第一個含萬用字元的段就 break,後面的 `..` 不看。
重現(臨時複本 t.mts,假檔案系統):seat.cwd=/repo,Glob pattern 為 `*/../../private/tmp/lumos-seat-staging/**`、`**/../../../…`、`{a,b}/../../…` 三種,checkTool 都回 null(放行);同一路徑寫成絕對路徑則擋。紅綠:放行 3/3,對照擋 1/1。
修法方向:pattern 任何一段是 `..` 就當看不懂,不管在萬用字元前後。

### F2 /clear 時還在派工途中的審查席不會登記
severity: minor
blocking: 否 — 要剛好在 /clear 的那一瞬間派出審查席;但後果是那一席整場沒有隔離,且不跳任何提示。
end(session, keep=true) 一律把 endGen 加一,而派工回來時用 endGen 比對決定登記與否。keep 的本意是「背景審查席還活著、席位不刪」,對「派工還在飛」卻走成丟棄:新席沒進對照表,之後工具呼叫查不到就放行。
引句:「endGen.set(session, (endGen.get(session) ?? 0) + 1)」
位置:register.ts 的 createGuard.end;對應 spawn 內 `(endGen.get(session) ?? 0) === gen` 判斷。
重現(t2.mts):spawn 的 next 先不回,呼叫 g.end('S', true),再回傳 agentId a1;之後 _state.seat('a1') 是 undefined,g.call 對 a1 的 Write 回 null(放行)。紅綠:未登記、放行。
修法方向:keep 時不遞增 endGen(只有真結束才遞增);測試補一條「/clear 當下派工途中的席照常登記」。計劃〈誠實界線〉只寫了熱重載中途,沒寫這個。

### F3 session.end 的 end() 沒有自己的存回上限
severity: minor
blocking: 否 — 引擎的 session.end 有整體時間上限(型別檔:whole chain shares one short wall-clock bound),最壞是拖慢結束、留殘席,不會放行。
r3 只替 spawn 加了 Promise.race 與 SAVE_MS,end 仍直接回傳 save(session);save 是串行鏈,前面任一次存回卡住,end 與之後所有存回都等不到。
引句:「return save(session)」
位置:register.ts 的 createGuard.end 與 save 的串行鏈 `saving = saving.then(...)`。
重現(t2.mts):saveSeats 永不回應,先 spawn 一席再 g.end('S'),500ms 內不回(HANG)。紅綠:掛住。
另外 save 重試 SAVE_TRIES 次都撞版時靜默放棄,drop 也跟著丟,殘席留在 $.state;與上面同屬「存回失敗只在記憶體裡擋」的既有取捨,計劃有寫,只提醒。
修法方向:end 也用 Promise.race([save(session), io.sleep(SAVE_MS)]),並讀 next.budget 的上限。

總結:最嚴重 minor,blocking 0 條
