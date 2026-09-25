severity: major

## Q1 分層與依賴方向

新碼全部留在 `_report_findings_missing_severity` 內部,呼叫的還是同一層現成的原語:`_visible_lines`、`_SEV_DECL_LINE_RE`、`_FINDING_VERIFIED_WORDS`,沒有跨層直呼上層(`cmd_*`)或下層 I/O。這點跟鄰居一致。
引句:「mh = re.match(r"^\s*(#{1,6})\s", ln)」(scripts/lumos:7255,對照 `_report_normalize_issues` 同層取值方式 scripts/lumos:7211 `_mt = _SEV_DECL_LINE_RE.fullmatch(lines[i])`)

## Q2 命名與錯誤處理

變數命名(`out`、`cur`、新增的 `cur_lv`)延續同函式既有的 `out, cur = [], None` 模式只是多開一個追蹤層級用的變數,`re.match(..., re.I)` 的旗標寫法也跟同檔其他處(scripts/lumos:2091 `re.search(..., re.I)`、scripts/lumos:5389 `_KEEPS_VARIANT_RE = re.compile(..., re.I)`)一致;沒有新造錯誤回傳格式,仍是 `(no, 訊息, ln)` tuple 塞進 `out`/`issues`,跟 `_report_normalize_issues` 既有的 `issues.append((no, "...", ln))` 同一種寫法(scripts/lumos:7215)。測試也延續同一支 `t_report_normalize_flags_finding_without_severity` 用 ①②③…的圈碼編號繼續往下編,沒有另開新函式。
引句:「小寫 f1 標題、沒 severity → 也要抓」(scripts/test_lumos.py,`t_report_normalize_flags_finding_without_severity` 內新增的 check ⑤,對照既有 check ①②③④同一支測試函式)

## Q3 第二種做法

## F1 自己手刻一套「標題層級決定段落邊界」的邏輯,沒有沿用 `_h2_section_lines`——而那支函式的docstring 明白寫著「找節邏輯不准長出第三套」
severity: major
blocking: yes
這份 patch 為了讓「F 段被子標題切斷」翻案,新增了 `cur_lv` 並自己比較 `lv > cur_lv` 來判斷要不要把目前這個標題當作段落結束,等於重新發明了一套「由標題層級決定段落起訖」的演算法。但同檔案 5298 行已經有 `_h2_section_lines(text, h2_re)`,是「回退節」與「實務隱患節」兩處共用的同款邏輯(到下一個同層或更高層標題為止、fence 內不算),而且它的 docstring 已經記著上一輪架構對齊審查留下的鐵則,明講這條找節邏輯只准一套、不准再長出第三套。這份 patch 沒有嘗試把 `_h2_section_lines` 擴充成可重複找多個 `F\d+` 段落再重用,而是直接在 `_report_findings_missing_severity` 裡再刻一份自己的層級比對,正是三問裡「自創的工具函式而鄰居已有同功能」——引入了第二種做法。
引句:「out, cur, cur_lv = [], None, 0」
佐證:scripts/lumos:7253(新刻的段落邊界迴圈起點) 對照 scripts/lumos:5298-5300(`_h2_section_lines` 定義與「找節邏輯不准長出第三套」的既有裁定)

不對齊共 1 條,其中 major 1 條
