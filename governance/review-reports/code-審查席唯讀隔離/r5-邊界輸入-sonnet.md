severity: minor

# 代碼審 r5 邊界輸入席(sonnet)審查報告

範圍:r4 修正差異(`/tmp/code-審查席唯讀隔離-r5.patch`),在臨時複本 `/tmp/r5x-seat/repo` 以 `node --experimental-strip-types` 直接 import `register.ts` 的 `parseMarker`、`checkTool` 試輸入。實驗腳本:`/tmp/r5x-seat/t.ts`(標記)、`/tmp/r5x-seat/g.ts`(Glob 41 組)、`/tmp/r5x-seat/p.ts`(效能)。Python 端 `python3.14 scripts/test_lumos.py -k guard_plugin_files_valid` 25 過 0 敗、`-k seat_templates` 19 過 0 敗;`guard.test.ts` 的 `test(` 計 90 支,與 Systems 筆記、驗證紀錄寫的 90 相符。未跑 `claude plugin test`(沒碰引擎)。

總評:r4 的修正在邊界上大致站得住。一般中英混寫第一行(`Lumos seat 的修正`、`Lumos seat guard 的 r4 修正`、`lumos seats are listed below`、`lumos-seat-work 目錄`、`lumos-seatx:`)全判 none 不誤擋;`Lumos seat:` 帶冒號、`LUMOS_SEAT:`、全形冒號、全形橫線等寫壞形狀判 bad;只剩格式字元的行(U+200E、U+00AD、U+180E、U+200B)當空行跳過,標記在後面照認;U+2028/2029 分行正確。Glob 一般 pattern(`**/*.md`、`src/**/*.{ts,tsx}`、`**/foo..bar.ts`、`docs/v1..v2/*.md`、`..hidden/*`、`**/...`、`{src,test}/**/*.ts`、`**/{a,b}/{c,d}/*.ts`、`**/file{1,2}.{ts,js}`、`\{a\}/*.ts`、`**/*.[jt]s`、`!(a|b)/**`)全放行;`../x`、`x/../y`、`*/..`、`{{a}}`、巢狀大括號、`/tmp/**` 照擋。效能:1000 萬字元的全空行、全零寬行、單一超長行、1000 萬空白接 lumos、1000 萬前綴標點,`parseMarker` 各在 1.1 秒內(最慢是 500 萬行零寬/空行,約 1 秒,線性);Glob 的新正則在大括號密集輸入下是線性,沒有災難性回溯。

以下都是邊角,沒有 blocker/major。

### F1 標記值裡的格式字元不判寫壞,跟筆記寫的規則對不上
severity: minor

blocking: 否 — 只發生在派工詞自己把格式字元夾進值或接在值尾,結果是席位名帶看不見的字元(寫檔目錄對不上、被自己擋),不是放出權限。

引句:「只剩格式字元的行當空行跳過;格式字元在標記那一行裡就判寫壞(代碼審 r3、r4)」

實測(`/tmp/r5x-seat/t.ts`,第 1 到 3 行):值尾接零寬空白、值中間一段夾零寬空白、值尾接 U+0085 控制字元,`parseMarker` 都回 `seat`,不是 `bad`。原因:`SEAT_RE` 的 `\S+` 吃得進這些字元,`segOk` 只擋 `\u0000-\u001f\u007f` 與空白。標記「前面」夾格式字元確實判 bad(已確認),所以只有「在值裡面或尾端」這一類漏掉;類型是漏擋判壞(該判寫壞卻放成合格席),不是誤擋。後果:登記的席名帶看不見字元,`workDir` 變成編排者看不見的怪名字,審查員按派工詞寫自己的工作資料夾反而被擋;權限沒有放大。修法方向:`segOk` 也拒 `\p{Cf}` 與 C1 控制字元(U+0080–U+009F),或筆記把「格式字元」那句改成只含標記前綴。

### F2 連字號寫法不接冒號,後面接中文或標點就判寫壞(誤擋一般首行)
severity: minor

blocking: 否 — 有明確的設計取捨(測試釘住 `lumos-seat中文` 為 bad),且擋下理由已教改寫第一行,可一次修好重派。

引句:「const SEAT_LOOSE_RE = /^lumos[-‐-―]seats?(?![a-z0-9_-])|^lumos[_\s]*seats?\s*[:：]/i」

實測:`lumos-seat 說明文件`、`lumos-seat。`、`lumos-seats are` 都回 bad。r4 只把底線與空白寫法收窄到要接冒號,連字號寫法仍「有沒有冒號都算」。誤擋面:任何以 `lumos-seat` 或 `lumos-seats` 起頭、後面不是英數底線連字號的一般派工第一行(例如談這個機制本身的調研派工)。筆記「一般中英混寫的派工詞第一行不誤擋」對連字號首詞不成立。這是一個要不要把連字號寫法也改成要接冒號的取捨,若維持現狀,建議在條款 S5 明寫「連字號首詞不論有無冒號都算」。

### F3 不可見但不是格式字元的開頭行讓真標記被忽略(靜默漏擋);無冒號的空白寫法同
severity: minor

blocking: 否 — 不是 r4 退步(r4 前同樣沒有隔離),需要派工詞第一行真的是這類字元或漏冒號,編排者範本不會產生。

引句:「const FORMAT_CHARS = /\p{Cf}/gu // 所有格式字元(零寬、方向標記、軟連字號……),不另列清單(代碼審 r4)」

實測:第一行只有 U+2800(點字空白)、U+3164(韓文填充)、U+034F(結合用字元連接符)這類「看不見但不屬 Cf」的字元,`clean()` 之後不為空,被當成第一個非空行,第二行的合格標記不看,結果 `none`,整席放行無隔離。類型:漏擋,靜默。另外 `LUMOS SEAT L/r1/s`(空白分隔又漏冒號)也是 `none`,這是 r4 刻意的放寬代價(想寫標記但漏冒號的空白寫法放行),誠實界線「漏寫不會被擋」大致涵蓋,但筆記沒點名這一形狀。建議:跳空行的判準加 `\p{Mn}` 與 `\p{Zs}`、`\p{Lo}` 中的填充字元太寬不建議;較務實是把這兩種形狀寫進誠實界線。

### F4 Glob 新判準的兩個罕見誤擋形狀
severity: minor

blocking: 否 — 兩種都極少見,擋下理由可讀,審查員可改寫 pattern。

引句:「if (pat.split(/[/,{}]/).includes('..') || /\{[^{}]*\{/.test(pat)) return null」

實測(`/tmp/r5x-seat/g.ts`):(a) `{a,b}..{c,d}`、`**/*.{a,b}..` 被擋,因為 `}` 也當分隔符,`}` 後面緊接的 `..` 被當成一整段;檔名真的以兩個點結尾或接在大括號後(罕見)才碰得到。(b) `a\{b\{c` 這種含兩個跳脫大括號(字面 `{`)的 pattern 被當巢狀擋;`\{a\}/*.ts`、`**/*.\{ts\}`、`**/*.{ts,\}js}` 都照常放行,所以一般跳脫大括號沒事。類型:誤擋。另一邊的漏擋沒有發現(`[..]/x` 放行,這不是穿越寫法)。⚠ 反斜線跳脫的 `\.\./x`:外掛不認它是 `..` 段(放行),要看引擎的 Glob 是否把 `\.` 當成字面點才知道有沒有穿越,我沒有引擎可測,未能重現。

### F5 ⚠ 存回改成讀不到版本時一律帶 ifVersion 0,引擎對「從沒寫過的鍵」的行為沒實測
severity: minor

blocking: 否 — 只影響熱重載後的保護,失敗時會跳提示(r4 新增),會談內仍在記憶體擋。

引句:「if (await io.saveSeats(merged, version ?? 0)) return」

`makeIo.loadVersioned` 對沒寫過的鍵回 `version: undefined`,r4 起這一路從「無條件寫」改成「`ifVersion: 0` 條件寫」。單元測試只驗了「帶 0」,沒驗引擎收不收。若引擎對不存在的鍵不認 0(要的是 get 回過的版本),那第一次存回每次都撞版、重試三次、跳「存回撞版」提示,而且每場會談一開始都會中。我在已裝的 claude 2.1.291 二進位裡只看到「ifVersion is a version `$.state.get` answered (a whole number)」,沒能確認缺鍵時 get 回什麼,未能重現。建議用 S13 那種真機跑一次首次存回看會不會跳提示。

## 圖譜鏡頭(LUMOS-IMPACT 逐條判)

機械反查三格皆空(受影響測試 0、共改 0、呼叫者 0),我另手動核對:
- `Systems/lumos-guard`:TEST 行「90 支」與 `guard.test.ts` 實數 90 相符;型別檔那段加的 REVISIT 與 `types/index.d.ts` 註解一致。影響:無新矛盾。
- `Projects/審查席唯讀隔離_計劃` S5 條款「底線、空白或沒有分隔的寫法要接冒號才算」:對照程式屬實,但「連字號寫法不接冒號也算」只在做法一節寫了、條款 S5 沒寫,見 F2;S5「剝所有格式字元」的說法與 F1、F3 的邊角對不上(筆記該句應限定在標記行前綴)。
- `Projects/審查席唯讀隔離_計劃` S2 條款:Glob 的 `..`、巢狀、大括號放絕對路徑與程式相符;`\{a\}`、`*.{ts,js}` 實測放行,與條款一致。
- `Verification/2026-10-06_審查席隔離實作`:79→90 數字相符。
- 計劃 REVISIT 與誠實界線新增的兩條(熱重載、`/clear` 席無上限):不碰這輪邊界,判不影響;`/clear` 與 `resume` 以外的結束原因仍走真結束,`keep` 時不叫醒等待者無害。
- `scripts/test_lumos.py` 的 `t_guard_plugin_files_valid`:去註解後比對掛鉤接線;`reg = live[live.find("export const register"):]` 找不到時 `find` 回 -1 會變成取最後一字元,三項 `count == 1` 全紅(大聲失敗,不會靜默放行)。判不影響。

總結:最嚴重 minor,blocking 0 條
