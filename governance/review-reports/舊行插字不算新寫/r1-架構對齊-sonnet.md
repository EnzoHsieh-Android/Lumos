severity: major

**第一問 分層與依賴方向**

設計把「配對舊行並比違規計數」放在 `_note_shape_eval` 前半的逐行迴圈裡,起點版本改用 `_nodehome_cat_blobs` 批次讀。依賴方向沒有倒置:`_note_shape_eval` 呼叫 `_notelines_new` 取新行,再向下呼叫 `_ns_check_line`,本案沒有讓下層回頭呼叫上層。批次讀的做法也照 `_ns_base_summary_lines`(`scripts/lumos:28292`)。

有一個分層小問題:否定現況句與前綴提醒不是在 viol 迴圈裡算,而是走另外兩個收集器,`_ns_negation_collect(hints, p, text, rows)` 和 `_ns_tag_hints_collect(tags, p, text, rows)`(`scripts/lumos:28416-28417`)。它們收的是 `(路徑, 全文, rows)`,拿不到 O。設計第 3 點要求提醒也「N 與 O 照計數比」,卻沒寫配對結果怎麼傳給這兩個收集器。這在 A3 列。

**A1**
severity: major
blocking: 是 — 「這行算不算舊的」已有三套判法,本案又加第四套純插入,而且明文只收斂一半、不整併。
引句:「不改的**:`_note_shape_eval` 後半「新程式檔喚醒舊引用」那一路(它自己有整行相等的舊行判定)」
- 現有判法 1,格子的文字鍵:`_ns_slot_key`、`_ns_old_keys`、`_ns_is_old`,見 `scripts/lumos:28175`、`scripts/lumos:28193`、`scripts/lumos:28208`。
- 現有判法 2,`old_by`(上線前寫的行,按路徑存整行):`scripts/lumos:27279`、`scripts/lumos:27299`。
- 現有判法 3,喚醒那段:`ln.strip() in old or ln.strip() in old_by.get(nfc(p), ())`,見 `scripts/lumos:28453`。
- 本案:用 `SequenceMatcher` 的 opcodes 判純插入,再做「O 與 N 各算一次違規、照計數比」。這是第四套。
- 第 2 點「N 對 O 都算一次」的做法,本質上等於「舊行本來就有的違規不算」。喚醒那一路的整行相等,只是「N 恰好等於 O」的特例,也就是插入長度為 0。
- 設計本可把「找到 O」收成一支共用函式,回傳整行相等或純插入的 O,讓喚醒那一路和新增行那一路都呼叫它。設計卻刻意不動喚醒那一路。
- 格子那套則留到 `REVISIT:2026-10-15`。
- 這些判法一旦分歧,同一行可能在格子、新增行、喚醒三條路得到不同的新舊結論。S1 到 S8 沒有任何一條驗收條款把三者的一致性鎖住。

**第二問 命名與錯誤處理**

設計沿用 `_ns_` 前綴與 `base_where`,方向一致。錯誤處理有兩處有出入,列在下面。

**A2**
severity: minor
blocking: 否 — 只是參數沒寫死,但會直接影響「純插入」的判定結果。
引句:「`SequenceMatcher(None, O, N).get_opcodes()` 只有 `equal` 與 `insert`、至少一段 `insert`」
- 同檔其他處用 `SequenceMatcher` 的寫法不一致。`scripts/lumos:32407` 傳 `autojunk=False`,`scripts/lumos:11654` 和 `scripts/lumos:35090` 沿用預設。
- 預設的 `autojunk=True` 在序列超過 200 個元素時,會把出現過多的字元當垃圾,opcodes 因此不穩。這份設計處理的是長句,中文單行常超過 200 字。
- 設計要寫明用哪一種。我建議照 `scripts/lumos:32407` 的 `autojunk=False`,並把 200 對與 2000 字兩個上限命名成模組常數,風格比照 `_EL_NEAR_THRESHOLD`(`scripts/lumos:11614`)。這點沒有把握:⚠ 不確定 `autojunk` 在實測中是否真的讓純插入判錯。

**A3**
severity: minor
blocking: 否 — 錯誤路徑和資料流沒交代,但實作時補寫即可。
引句:「`base_where` 是空樹、或那篇在起點版本不存在(含範圍內改名)就不配對、照整行查。」
- 既有慣例是批次讀失敗就回 `None`,由呼叫端 fail-open,不當成「沒有舊版」,因為那會把舊行誤擋成新寫。見 `scripts/lumos:28292` 的 docstring,以及 `scripts/lumos:28266` 的說明。
- 設計只講「不存在就整行查」,沒講 `_nodehome_cat_blobs` 整批回 `None` 時怎麼辦。依第 1 點的語意,應該跟 `_ns_slots_old_lines` 一樣 fail-open。這裡的 fail-open 會放寬閘門,方向跟既有慣例一致,但設計沒說,實作時可能照整行查,結果不同。
- 提醒收集器(`_ns_negation_collect`、`_ns_tag_hints_collect`,`scripts/lumos:28416-28417`)只拿 `(p, text, rows)`,設計沒說 O 的配對結果由誰算、怎麼傳進去。建議在 `_note_shape_eval` 算一次配對表,同時傳給 viol 迴圈與兩個收集器,不要各自重算。

**第三問 第二種做法**

結論:是,而且已經是第四套。

- 現有三套判法的粒度各不相同。格子判法的鍵是(前綴, 文字鍵, 連結集合)。`old_by` 判法是整行字串相等。喚醒判法也是整行字串相等,另外還查上線點版本。
- 本案再加一套:行內字元層級的純插入,加上 O 與 N 各跑一次違規函式、照計數比。
- 設計自己承認格子仍然「插字會改到核心一句,格子仍當新寫」,也就是同一次「補更正」會被格子當新寫、被新增行路徑當舊行,兩邊矛盾。REVISIT 把這個矛盾推到 2026-10-15,但沒有機械守衛。第 4 點註明「不改的」,也沒有給出收斂路線。
- 建議收斂成一支 `_ns_find_old_line(N 的區塊, N, 起點版本的行集)`,回傳整行相等、純插入、或沒有。喚醒那一路、新增行那一路和 `old_by` 都改呼叫它,格子判法在 REVISIT 時併入。
- 計數比較(第 2 點)並非第二種做法。它是新能力,既有判法都沒有。
- 逐項違規的比對鍵分「規則加片段」和「只看規則」兩種,是新的鍵設計。它為了抵抗插字改動前 60 字片段而存在,合理。

不對齊共 3 條,其中 major 1 條
