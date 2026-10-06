severity: major

## 1. 分層與依賴方向
事件帳外掛不匯入審查席隔離外掛,兩支各自獨立,方向本身乾淨。toolExtra、spawnFields 加欄位也合既有做法。問題在「認標記」這件事:事件帳另寫了一個 seatOf,只複製了 SEAT_RE 那一條,沒有複製守衛判定標記的整套流程。
對照 `mods/claude/lumos-guard/hooks/register.ts:70`(parseMarker 先用 firstLine 以 \n、 、  切行,並先 NFKC 與剝格式字元判空行,再三段與 segOk 驗證)與 `mods/claude/lumos-ledger/hooks/register.ts:92`(seatOf 只以 \n 切、只 trim、沒有三段驗證)。
兩邊對「第一個非空行」「合格」的判定已經不同。例:第一行是零寬字元時守衛跳過、事件帳記 null;值寫成 a/b 兩段時守衛判 bad 擋下、事件帳照記 seat。測試只釘 SEAT_RE 那行字,釘不到這些差異。

## 2. 命名與錯誤處理
- 命名沿用 toolExtra、spawnFields、cmd 風格,seatOf 與 parseMarker 命名習慣相近,無不一致。
- 型別不符記 null 或不記,與既有 `typeof ... === 'string'` 寫法一致。
- output_mode 截 40 字,計劃與條款只寫「output_mode」、沒定 40,屬計劃與程式不一致。
- 守衛用 firstLine/clean 防零寬與分行字元,事件帳沒有,防護強度不同。

## 3. 第二種做法
- 既有「兩端各寫一份」做法(`scripts/test_lumos.py` t_ledger_rules_match_reader)是兩端共用同一組案例檔 rules-fixture.ts、各自跑行為。新測試 t_ledger_seat_re_matches_guard 改成只抽正規式字串比對,是另一種較弱的釘法:只釘一行,不釘行為。
- 抽取正規式與既有 t_seat_templates_carry_marker 不同:既有用 `^const SEAT_RE = /(.+)/$`,新的用 `(/.+/[a-z]*)` 含旗標,同一件事兩種寫法。
- 事件帳另寫一份認標記的函式,正是題目點名的「第二種做法」。
- 截斷長度 200 與既有 cmd 的 500 同為 slice 寫法,一致,不列。

### F1 事件帳另寫一份認標記的函式,判定與守衛的 parseMarker 已分岔
severity: major
blocking: 是 — 引入第二種做法(第二份標記判定),且兩份行為已可舉出分歧的輸入
引句:「const SEAT_RE = /^LUMOS-SEAT:\s*(\S+)$/」

### F2 守衛釘法只比正規式字串,不像既有做法共用案例跑行為
severity: major
blocking: 是 — 與既有 rules-fixture 共用案例的釘法不同,另開了較弱的第二種釘法,釘不到 firstLine 與三段驗證的分歧
引句:「pat = _re.compile(r"^const SEAT_RE = (/.+/[a-z]*)$", _re.M)」

### F3 抽取 SEAT_RE 的正規式與既有測試寫法不一致
severity: minor
blocking: 否 — 結構對,只是同一件事兩種抽法
引句:「check(f"S4 {name} 原始碼裡抽得到 SEAT_RE", m is not None, "")」

### F4 output_mode 截 40 字,計劃條款未定義
severity: minor
blocking: 否 — 命名與規格不一致,結構不變
引句:「if (typeof e?.output_mode === 'string') extra.output_mode = e.output_mode.slice(0, 40)」

總結:不對齊共 4 條,其中 major 2 條
