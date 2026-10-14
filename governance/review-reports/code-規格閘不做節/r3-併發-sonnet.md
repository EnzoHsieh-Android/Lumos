severity: clean

**已讀,無 finding。**

我讀了新正則和 `_nogo_line_says_nogo`、`_nogo_skip_lines`,也在 `spec-gate-nondo` 的 `scripts/lumos` 上實測。實驗檔已刪。

- **回溯**:`_NOGO_NEG_PREFIX_RE`、`_NOGO_NEG_HEADER_RE` 都是行首錨定的固定字串選擇,沒有巢狀量詞。`_NOGO_CLAUSE_SPLIT_RE` 是單一字元類加固定詞的選擇,`_NOGO_REF_TOKEN_RE` 是 `^[A-Za-z]{0,3}\d{1,4}$`,上限很小。四支都是線性。
- **病態單行**:我試了 10 萬到 100 萬字元的單行,內容包括連續逗號、連續 and、連續空白、連續冒號、連續行內標記和連續括號。再加 5 萬字元的未閉合反引號、星號、方括號、`![[`。單行 100 萬字元的耗時在 0.2 秒以內,記憶體約 120MB。放大 4 倍的方括號輸入,耗時沒有跟著平方成長。
- **大清單**:不做清單 5000 行,`_nogo_skip_lines` 約 0.03 秒。加上 `_door_judge` 的整體重判約 0.12 秒,記憶體約 40MB。5000 行續行約 0.02 秒。
- **100KB 單行**:整個 `_door_judge` 約 0.02 秒。1MB 的危險詞單行約 0.19 秒、62MB。
- **推送前重算**:`_door_judge` 在 `scripts/lumos:8745` 和 `scripts/lumos:9082` 各呼叫一次,每份計劃多做一次 `_h2_section_lines` 加一輪線性掃描。每份計劃增加的成本在毫秒級,可以忽略。
- **`nogo_skipped` 大小**:它會進條款指紋。我用 5000 行各帶多類危險詞的清單測,得到 10000 筆,隨行數線性成長。指紋的雜湊成本也是線性,不是問題。

最高等級 clean,blocking 0 條。
