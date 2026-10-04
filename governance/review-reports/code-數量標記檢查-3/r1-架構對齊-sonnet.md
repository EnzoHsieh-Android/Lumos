severity: minor

## Z1 _strip_inline_markup 說明仍自稱唯一本體,與新的 _inline_mask 並列兩處「唯一」宣稱
severity: minor
blocking: 否
引句:「_strip_inline_markup 與 _inline_visible_mask 都從這裡導出」
file: `scripts/lumos:384`

收斂本身是對的:全檔已沒有第二份遮罩邏輯(grep 剩下的 INLINE_CODE_RE.sub 在 4439、22758、23463、37627 都是刻意「搜尋寧可多看見」的 probe,原說明已交代)。但 `_strip_inline_markup`(368 行)的說明仍寫「★全檔唯一★」且完全沒提它現在只是 `_inline_mask`(384 行)的薄包裝;`_inline_mask` 又寫「★唯一本體★」。下一個讀者會看到兩個「唯一」,而且定義順序是包裝在前、本體在後、再接一個只為 count 一個呼叫端(`_count_rewrite`,34319)存在的 `_inline_visible_mask`。結構沒錯,只是 `_strip_inline_markup` 說明該補一句「本體在 _inline_mask」,不然下一輪有人讀到第一個 docstring 會以為邏輯在這裡。另外 `_inline_mask` 結尾直接接 `WIKILINK_RE`(393 行)沒空行,此點原檔就如此,不列。

## Z2 _count_rewrite 命名屬 _count_ 群,位置卻落在 _drift_fix_ 群
severity: minor
blocking: 否
引句:「def _count_rewrite(line, old, new):」
file: `scripts/lumos:34313`

其餘 `_count_*`(`_count_parse`、`_count_lines`、`_count_members`、`_count_enum`、`_count_changed`、`_count_eval`、`_count_actual`)集中在 33084–33250 一帶;`_count_rewrite` 與 `_drift_fix_count` 一起放在 34313,夾在 `_drift_fix_c5`(34284)與 `_drift_fix_shape_err` 之間,前綴卻不是 `_drift_fix_`。drift fix 區塊的其他輔助函式一律 `_drift_fix_*` 命名(33906–34468)。要嘛改名 `_drift_fix_count_rewrite`,要嘛搬進 `_count_*` 群;現況是兩邊的慣例各取一半。判不準是否算 major,但不引入第二種做法,故 minor。

## 三問總答

1 分層與依賴方向:對照 `scripts/lumos:368-392`、`33193-33222`、`34313-34338`。`_inline_mask` 在最底層的文字工具區,`_count_rewrite` 與 `_count_lines`(33110)都往下呼叫 `_strip_inline_markup` 或 `_inline_visible_mask`,沒有跨層直呼、沒有反向依賴。`_count_changed` 只吃已解析的 tree,不碰 I/O,與 `_count_eval` 的分工同鄰居一致。

2 命名與錯誤處理:對照 `scripts/lumos:33193-33222`、`34313`。`_count_changed` 的簽名拿掉 hit 參數,與 `_count_eval` 呼叫端(33243)一致;回傳「(值, 原因)」或 True/False 的形狀與鄰居相同。`import ast` 在 `_count_*` 群裡一律用函式內 `import ast`,與同檔 5552 一致;`_drift_py_names` 系列用 `_ast` 別名,屬檔內既有兩派,不列。命名不齊的點見 Z2。

3 第二種做法:對照 `scripts/lumos:5558`、`32329`、`32374`、`33202`。行內遮罩已收斂到單一本體(a:無遺留第二份)。`_count_changed` 用 `ast.walk` 加 `ast.iter_fields` 找「某識別字所有出現位置」:專案內沒有既有的通用識別字出現位置走訪(`_drift_py_names` 只回名稱集合、`_drift_m1_assigns` 只收模組層與類別層指派目標、5558 只收函式名),語意不同、不可共用,所以不算第二種做法(b:無該共用的)。`ast.walk` 本身是專案慣用寫法。

總結:不對齊共 2 條,其中 major 0 條;最高等級 minor
