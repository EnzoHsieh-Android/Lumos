severity: major

## Z1 _count_visible 是行內可見判定的第二份
severity: major
blocking: 是
引句:「s = blank(blank(line, _DOUBLE_BACKTICK_RE), INLINE_CODE_RE)」
file: `scripts/lumos:34310`
`_strip_inline_markup`(scripts/lumos:368-377)的說明明寫「全檔唯一,別在別處自寫第二份」。`_count_visible` 自己重新組了同一套:先雙反引號、再單反引號、再「未閉合反引號之後不信」(34311-34312 對應 374-377)。它的註解還承認「判定同 _strip_inline_markup」,正是兩份各自演化的前兆(上一輪 F4 就是這一份少認了雙反引號才出的)。其他呼叫端(6387、6584、28096、32059、33095、33662 等)全走 `_strip_inline_markup(...)[0]`;只有「位置不動」這點不同。建議把核心抽成一支(例如 `_inline_visible_mask(line)` 回遮罩後同長度字串),`_strip_inline_markup` 與 `_count_visible` 都從它導出(前者去掉 \0、後者保留),判定只剩一處。

## Z2 _count_module_nodes 手寫走訪 ⚠
severity: minor
blocking: 否
引句:「todo.extend(ast.iter_child_nodes(nd))」
file: `scripts/lumos:33187`
全檔 `iter_child_nodes` 只有這一處,既有做法是 `ast.walk`(5543、32314、32359、33201)與 `_drift_m1_assigns`(32340)的 body 遞迴。要的語意(模組層、不進函式/類別/lambda)確實沒有現成函式可借,`_drift_m1_assigns` 只進 If/Try 且收的是指派名,不等價,所以不算 major;但這是專案內第三種「走模組層」的寫法,判不準是否該與 `_drift_m1_assigns` 合併,標 ⚠。另外 `_count_changed` 同一函式裡一半用 `_count_module_nodes`、一半用 `ast.walk`,讀者要自己分辨哪個範圍,註解有講,結構上可接受。

## 三問總答
1 分層與依賴方向:count 這組仍在 drift 區內自成一塊(33060-33270 讀、34305 起寫入修復),`prefetch` 改呼叫 `prefetch_paths`(32552 對 32693,與 33267 的呼叫端一致)是收斂不是新增。沒有跨層直呼。`_count_visible` 放在修復區(34305)而不在 `_strip_inline_markup` 旁,是它成為第二份的結構原因。
2 命名與錯誤處理:`_COUNT_READ_METHODS` 沿用被取代的 `_COUNT_MUTATORS` 的位置(函式前、`_COUNT_` 前綴、frozenset),與鄰居(33060-33066 的 `_COUNT_ENUM_BASES` 等)命名一致;`_count_eval` 補 MemoryError 與 `_drift_py_names`(32310)的接法一致,註解也指明出處;`_count_changed` 取代 `_count_mutated` 命名無衝突。無不一致。
3 第二種做法:見 Z1(行內可見判定第二份,major)與 Z2(模組層走訪,minor ⚠)。

總結:不對齊共 2 條,其中 major 1 條;最高等級 major
