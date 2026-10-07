severity: minor

審查範圍:/tmp/code-事件帳補記-r1.patch 全部 hunk;對照真代碼 mods/claude/lumos-guard/hooks/register.ts、scripts/lumos 讀取端。實驗在 /tmp/seatchk.js(node 直接跑兩邊的切行邏輯)。

### F1 seatOf 的切行與「第一個非空行」判準跟審查席隔離外掛不一致,守衛放行的標記事件帳記成 null
severity: minor
blocking: 否 — 只是漏記 seat 欄,不影響守衛、也不影響讀取端正確性;但直接削弱本篇目的(對出哪個子代理是哪一席)。
引句:「for (const raw of prompt.split('\n')) {」
實驗(node,兩邊邏輯逐字照抄):
- 派工詞 `U+200B\nLUMOS-SEAT: a/r1/b`:守衛 firstLine 用 clean() 剝格式字元後判空,跳過第一行,回 `a/r1/b`;事件帳只用 trim()(U+200B 不是 JS 空白),第一行判非空,SEAT_RE 對不上,記 null。
- 派工詞 `LUMOS-SEAT: a/r1/b` 後接 U+2028 再接「請審查」:守衛按 `\n| | ` 切,第一行就是標記,回 `a/r1/b`;事件帳只按 `\n` 切,整行 `\S+$` 吃不下後面的字,記 null。
- `\r\n`、開頭 U+2028、純 `\n` 兩邊一致。
根因:計劃與 `t_ledger_seat_re_matches_guard` 只釘正規式一字不差,沒釘切行與判空邏輯;patch 第 207 行附近(seatOf 的 split 與 `if (!line) continue`)跟守衛 firstLine 不同。
file: `mods/claude/lumos-guard/hooks/register.ts:54-60`
修法建議:seatOf 用同一個 firstLine(含 U+2028/2029 與 clean 判空),或把 firstLine 也納入 Python 釘住的範圍。補一條測試涵蓋上面兩個輸入(現有 S3 測試只測 \n 與空白開頭)。

### F2 「只記合格標記」與實作不符:守衛判寫壞的值事件帳照記
severity: minor
blocking: 否 — 只多記一個值,守衛照常擋;事件帳不影響判定。
引句:「return m ? m[1].slice(0, 200) : null」
SEAT_RE 只驗 `\S+`,守衛之後還要求三段、每段 segOk(`parseMarker`)。實驗:`LUMOS-SEAT: a/b`(兩段)、`LUMOS-SEAT: a/r1/b` 尾接 U+200B,事件帳都記成非 null 的 seat,守衛卻判 bad 而擋派工(spawn 事件的 denied 為 true)。計劃文字說「seat:合格審查席標記」,讀的人會把 seat 非 null 當成合格席位。
file: `mods/claude/lumos-guard/hooks/register.ts:69-82`
建議:要嘛計劃與筆記改寫成「記第一行標記值,不保證合格,看 denied」,要嘛讀取端核對時以 denied 與三段格式再驗一次。

### F3 Grep/Glob 的欄位名在附的型別檔裡查不到,只由測試自己造輸入「證明」
severity: minor
blocking: 否 — 欄位名對錯只讓新欄位漏記,不會讓寫入出錯。
⚠ 判不準。
引句:「for (const k of ['pattern', 'glob'] as const) if (typeof e?.[k] === 'string') extra[k] = e[k].slice(0, 200)」
型別檔 BuiltinToolInputs(15203 行起)列了 Agent、Bash、Read…,但搜不到 Grep、Glob、output_mode;所以 `pattern`、`glob`、`output_mode` 是否就是引擎 tool.call 事件上的扁平欄位,型別檔無法證實(Bash 的 `command` 同樣是扁平讀,這點與既有寫法一致)。補記 S1 測試用 `toolExtra({ tool: 'Grep', pattern: ... })` 自造輸入,真實引擎給的欄位若名稱不同(例如包在 input 裡)會全綠但新欄位永遠不記。建議上線後用真實事件帳抽一筆 Grep 確認有 pattern。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:15203`

## 其他走過、判無問題
- 事件行長度:新增欄位 pattern/glob 各 200 字、output_mode 40 字、seat 200 字、cmd_len 數字;JSON 跳脫最壞約 6 倍仍遠低於讀取端 `_EVENTS_MAX_LINE = 64 * 1024`(`scripts/lumos:25175`)。cwd 沒截斷,但受系統路徑上限約束,不構成實際風險。
- 欄位撞名:事件頂層鍵是 v、ts、session、agent、worktree、ev(register.ts 的 base),新欄位 cwd、seat、pattern、glob、output_mode、cmd_len 都不撞,`...extra` 不會蓋掉頂層。
- 非字串:pattern/glob/output_mode/cwd/prompt 非字串都走 typeof 擋住;測試涵蓋 5、null、{}、42、undefined。
- 新舊互讀:讀取端 `_events_take_line` 只驗 v 與深度,對未知欄位照單全收,文字輸出只取 tool/reason/origin/agent_type(`scripts/lumos:25395`),舊讀取端讀新事件、新讀取端讀舊事件(缺 cwd/seat)都不會壞;cmd_len 缺席代表舊事件。
- slice 在代理對中間切(emoji 剛好跨第 200 字)會留孤立代理字元,JSON.stringify 會跳脫成 \ud83d,不致壞行;與既有 cmd 的 500 字截法同一種,不另標。
- 圖譜鏡頭:派工詞寫明這次沒附固定席筆記(鏡頭計算超時),未逐條判。
- 角色鏡頭:未附卡,略過。

總結:最嚴重 minor,blocking 0 條
