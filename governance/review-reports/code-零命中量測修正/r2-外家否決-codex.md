severity: major

1. 引號內的 heredoc 字樣會吞掉後續真搜尋
severity: major
blocking: 是
引句:「m = _HEREDOC_START_RE.search(ln)」
file: `governance/eval/lens-utilization/recount.py:890`
重現：兩行 Bash `printf '%s\n' '<<EOF'`、`python3 scripts/lumos search __CODE_REVIEW_NO_HIT_7F2A__ --json` 實際輸出 `<<EOF` 與 `{"results": [], "candidates": 0, ...}`，但同一指令與輸出交給 `_search_events` 得到 `[]`。掃描器在處理引號前把普通字串誤認成 heredoc 起點，整筆零命中消失。

2. 其他指令印出的整行 JSON 仍會冒充搜尋計數
severity: major
blocking: 是
引句:「evs[0]["verdict"] = _search_verdict(output) if len(counts) <= 1 else "undetermined"」
file: `governance/eval/lens-utilization/recount.py:989`
重現：`printf '%s\n' '{"results": [], "candidates": 0}'; python3 scripts/lumos search README | head -1` 的輸出同時含前述假 JSON 與命中行 `2.243 Systems/slim-readme.md`，但 `_search_events` 回傳 `{'query': 'README', 'verdict': 'zero'}`。只有一行計數時程式仍無法證明其來源，卻直接壓過可見的命中證據。

3. 查詢詞以數字結尾且 `&` 不留空白時不會拆開
severity: major
blocking: 是
引句:「_LONE_AMP_RE = re.compile(r"(?<![&>|\d])&(?![&>])")」
file: `governance/eval/lens-utilization/recount.py:873`
重現：`python3 scripts/lumos search __CODE_REVIEW_NO_HIT_1&python3 scripts/lumos search __CODE_REVIEW_NO_HIT_2; wait` 實際印出兩行 `(共 0 篇候選...)`，但解析結果只有一筆、查詢被黏成 `__CODE_REVIEW_NO_HIT_1&python3 scripts/lumos search __CODE_REVIEW_NO_HIT_2` 且判為 `undetermined`。負向回看排除 `\d` 使這兩次零命中都沒被計入。

4. CLI 接受的長旗標縮寫會把旗標值配進查詢
severity: major
blocking: 是
引句:「_SEARCH_VALUE_FLAGS = ("--path", "--top")」
file: `governance/eval/lens-utilization/recount.py:871`
重現：`python3 scripts/lumos search __CODE_REVIEW_NO_HIT_7F2A__ --pa Systems --json` 被 argparse 接受並輸出 `{"candidates": 0, ...}`，但解析器記成查詢 `__CODE_REVIEW_NO_HIT_7F2A__ Systems`。`--pa` 是 `--path` 的有效縮寫，固定只辨認完整旗標仍會污染查詢字串。

5. 反斜線跳脫的字面 `$` 被誤判成變數查詢
severity: major
blocking: 是
引句:「_VAR_QUERY_RE = re.compile(r"\$(?:\{|\(|[A-Za-z_0-9@*#?])|`")」
file: `governance/eval/lens-utilization/recount.py:869`
重現：`python3 scripts/lumos search \$CODE_REVIEW_NO_HIT_7F2A --json` 實際搜尋字面 `$CODE_REVIEW_NO_HIT_7F2A` 並輸出零候選，解析器卻回傳空查詢、`undetermined`、`zero_unattributed: 1`。程式只豁免單引號，沒有豁免 shell 的反斜線跳脫。

6. 行尾 shell 註解會被併進查詢字串
severity: major
blocking: 是
引句:「elif not w.startswith("-"):」
file: `governance/eval/lens-utilization/recount.py:923`
重現：`python3 scripts/lumos search __CODE_REVIEW_NO_HIT_7F2A__ --json # verify lumos search no hit` 實際輸出零候選，但解析結果的 query 是 `__CODE_REVIEW_NO_HIT_7F2A__ # verify lumos search no hit`。切詞未套用 shell 註解語意，導致本來可歸屬的零命中配到不存在的查詢。

全份最高嚴重度是 major,blocking 共 6 條