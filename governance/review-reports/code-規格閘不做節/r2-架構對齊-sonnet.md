severity: major

severity: major
blocking: 是 — 專案已有一支縮排寬度函式 `_ns_indent`(tab 照 4 欄展開),而且它的說明寫明「兩處判續行都用這一支」。這份修補另開 `_nogo_width`,多了第二套縮排計算。
引句:「def _nogo_width(s):」
對照:file: `scripts/lumos:33875`(`_ns_indent`,`ln.expandtabs(4)` 後取縮排寬度)
判定理由:兩支函式的 tab 規則一樣,差別只在全形空白 U+3000 算 2 欄。`_ns_indent` 沒做這件事,但直接擴充它,或給它加一個參數就能做到,用不著另寫一支。目前 `_ns_indent` 的呼叫端是否受影響,我沒有逐一確認。兩套並存,日後改其中一套的規則,另一套會悄悄漂掉。這正是 `_ns_indent` 的說明當初想避免的事。`_nogo_width` 還被拿去算 `ln[:m.end() - 1]`,那是「標記加空白」的前綴寬度,不是縮排,語意也和函式名稱不符。

severity: minor
blocking: 否 — 專案裡本來就有好幾份各用各的否定字表,新增一份不算引入第二種做法,只是缺理由說明。
引句:「_NOGO_NEG_RE = re.compile(r"不|沒有|無|排除|暫緩|非本期|\bout of scope\b|\bnot\b", re.I)」
對照:file: `scripts/lumos:33043`(`_NS_NEG_NARROW_ZH` 上方有註解,寫明「不共用 NEG_LEXICONS、不共用 _DRIFT_M1_HIST_WORDS」的原因);file: `scripts/lumos:19351`(`_REJ_NOGO_RE` 是舊否決清單,用途是找否決提案,和這裡的「項目含否定字樣才跳過」不同題)
判定理由:專案慣例是一個用途一份字表,並在旁邊寫明為什麼不共用。`_NOGO_NEG_RE` 跟 `_REJ_NOGO_RE` 用途不同,分開沒問題,但上方的註解只講了為什麼要加,沒講為什麼不借 `NEG_LEXICONS` 或筆記形狀那組字表。補一句註解就夠。

severity: minor
blocking: 否 — 做法沿用專案「版本號加釘值測試」的路線,只是多一層;兩層之間有機械連動,不算跨層直呼。
引句:「_NOGO_SKIP_LOGIC_VERSION = 1   # 不做清單判斷邏輯」
對照:file: `scripts/test_lumos.py:59802`(`t_door_rule_version_pin` 釘的是執行時算出的輸入指紋);file: `scripts/lumos:7910`(`_DOOR_RULE_VERSION`)
判定理由:新增的版本號加原始碼雜湊釘值,放到 `t_nogo_skip_logic_version_pin`,屬於同一路線。`_NOGO_SKIP_LOGIC_VERSION` 進入 `_door_rule_fingerprint`,所以邏輯一改,會依序觸發兩支測試翻紅,逼你先升內層版本、再升 `_DOOR_RULE_VERSION`。這比原本執行時 `inspect.getsource` 更好,也避開了凍結打包讀不到原始碼的問題。缺點是多了一層人工維護:`_DOOR_RULE_VERSION` 只靠「指紋變了測試紅」間接被逼升版,不是直接綁原始碼。這只算維護成本,不算對不齊。

不對齊共 3 條,major 1 條。`_nogo_skip_lines` 改用既有的 `_h2_section_lines` 取候選行,這點是對齊的,沒有另寫一套找節邏輯。
