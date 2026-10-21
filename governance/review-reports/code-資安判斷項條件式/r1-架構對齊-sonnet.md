severity: minor

A1 新條件式判斷與既有 manual_check_scope 的來源分在兩處
severity: minor
blocking: 否
引句:「need_judgments = _secev_control_table(rec, ctx, out) | _secev_format_judgments(rec)」
file: `scripts/lumos:10540` manual_check_scope 的額外判斷是 `_secev_control_table` 裡由 `_secev_min_kinds` 帶出 extra_j,再回傳給 `_secev_control_layer`。
新條件式判斷改在 `_secev_control_layer` 用 `|` 補上第二個來源。
兩條路最後都進同一個 need_judgments,再交給 `_secev_control_kinds`。
`_SECEV_CONDITIONAL_JUDGMENTS` 也是同一份旗標。所以這是同一套機制,沒有第二種做法。
放法比較貼近既有的是把 `_secev_format_judgments` 併進 `_secev_control_table`,讓「條件式判斷由 table 層回傳」只有一個出口。
現在的拆法會讓日後讀者以為有兩套條件式機制。

A2 新增一張鏡像表,但條件的來源是正確的
severity: minor
blocking: 否
引句:「_SECEV_JUDGMENT_FORMATS = {"threshold_meaningful": "k6_summary", "calibration_representative": "sarif"}」
file: `scripts/lumos:8474` 條件是從既有的 `_SECEV_KIND_FORMATS` 推得,沒有另列種類清單,與計劃寫的「不另列清單」一致。
唯一的小分歧是這個判斷表不放進 `_SECEV_JUDGMENTS` 或類別表,而是獨立一張。
放進類別表會動到威脅類別表版本,所以獨立一張可以接受,不算 major。
另外 concurrency 的允許格式含 junit。只要必要種類有 concurrency,就會要求 threshold_meaningful,即使實際證據是 junit。
這是保守方向,d20 的 trade_offs 只寫了反方向的風險,沒提到這點。

A3 新測試沿用既有夾具,無偏離
severity: minor
blocking: 否
引句:「r.extra_fence_items = [r.review_item(reviewer="另一個 AI 會談", reviewer_kind="ai", judgments=ai_j)]」
file: `scripts/test_lumos.py:106420` 同一檔已有同樣的 `extra_fence_items` 與 `review_item` 寫法。
新測試用 `_SgRepo`、`_sg_eval`、`_sg_codes`、`_sg_kind`,沒有自造夾具,與既有做法一致。
S62 條款、決策 d20 與 REVISIT 的 `[closed:日期 理由]` 都符合專案慣例。
條款一行一條並綁 `[test:]`,REVISIT 的寫法與 `scripts/lumos:47549` 的 `_REVISIT_CLOSED_RE` 相符。
這條沒有要修的問題。

最嚴重 severity:minor,blocking 共 0 條
