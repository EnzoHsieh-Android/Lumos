severity: major

## 第 1 問 分層與依賴方向:大致對齊,有一處自寫

- **放的位置**:對齊。`_superseded_decisions`、`cmd_rejections` 緊貼 `cmd_decisions`(`scripts/lumos:18139`、`18153`),跟鄰居同一帶。規格閘提醒 `_spec_gate_print_rejections`(`:7270`)夾在 `_spec_gate_record` 與 `_spec_gate_print_door`(`:7285`)之間,在 `_spec_gate_front`(`:7702`)緊接 door 行呼叫。方向是規格閘呼叫讀取層,沒有反向,也沒有跨層直呼。
- **共用解析函式**:大部分有用。摘要走 `_slot_summary_entries`(`:4041`,鄰居用法 `:4091`、`:4281`),`slot_parse` / `_slot_vals`(`:4052`)、`_visible_lines`、`split_frontmatter`、`env_text`(`:755`)、`_gist`、`parse_decisions` 都是既有的。`decisions --superseded` 的收集抽成共用函式,這是對的做法。
- **自寫的部分**:
  - 引述遮蔽用了自己的 `_REJ_QUOTED_RE`,見 F1。
  - 正文 WHY 行用了自己的 `_REJ_WHY_RE`,見 F2。
  - 作廢狀態表手寫,見 F3。

## 第 2 問 命名與錯誤處理:大致對齊

- **指令註冊**:對齊。`HELP_WHEN`(`:49404`)與 `main()` 的 `add_parser`、`--json` 的 `dest="rej_json"`(`:49994`)跟 `q_json`、`st_json` 等同一寫法。分派段放在 decisions 之後(`:50944` 附近),跟 `contracts`(`:50788`)同型。
- **空結果訊息**:對齊,`無舊否決(共 0 筆)` 跟 `cmd_query` 的 `無節點符合條件`(`:18500`)同風格。`--json` 先於空判斷輸出,也跟 `cmd_query` 一致。
- **略過行**:`[spec-gate] 舊否決: —(收集失敗:{e};略過)` 跟 `[spec-gate] 跑: —(平台設定讀不動:{e};略過)`(`:7728`)格式一致,同樣走 stdout。
- **只提醒不擋**:規格閘鄰居 `_spec_gate_prepare`(`:7724`)只捕 `(ValueError, OSError)`,新碼捕全部 `Exception`。全檔有 245 處 `except Exception`,`_gist`(`:12610`)也是 fail-open,而且程式註解有交代理由,所以不列 finding。
- **JSON 形狀**:見 F4。
- **文字輸出的節點名**:`superseded-decision` 那段印 `rel`(帶 `.md`),`decisions --superseded` 印 `n.stem`(`:18152`)。`cmd_contracts`(`:6157`)與 `cmd_query` 印 rel,鄰居本身不一致,不判。

## 第 3 問 第二種做法:有 1 處,另有 2 處小的

- 新的 argparse 註冊方式:沒有。
- 新的輸出慣例:沒有(JSON 欄位名見 F4)。
- 測試佈景另起一套:沒有。`_rej_vault` 用 `mkvault` / `write`;規格閘測試用 `_mk_spec_gate_repo`、`_sg_plan2`、`_load_lumos_inproc`(`test_lumos.py:225`);`patch.object(m.sys, "stdout", …)` 在測試檔裡有大量先例。
- 自創引號判定:有,見 F1。

## F1 自寫引述遮蔽,專案已有至少兩份同功能
severity: major
blocking: 是
引句:「_REJ_QUOTED_RE = re.compile(r」
佐證:file: `scripts/lumos:18171`
- 新增的 `_REJ_QUOTED_RE` 要做的事,是把引述舊句子裡的詞當成「只是在提它」而排除。專案已經有兩份做同一件事的:
  - `_drift_mask_quotes` / `_DRIFT_QUOTE_RE`(`scripts/lumos:35366`、`35370`)。它的 docstring 寫「專案慣例『只是在提某個詞就用全形引號包起來』」,意圖完全相同。
  - `_ns_neg_quote_spans` / `_NS_NEG_QUOTES`(`:31251`、`:31268`)。它的四組括號「」『』“”"" 跟新碼前四組一模一樣。
- 這會讓同一件事有第四份實作。新碼還額外加了反引號,但專案裡行內程式碼的遮蔽有全檔唯一的 `_strip_inline_markup`(`:368`)。
- ⚠ 交編排者:既有的兩份、加上 `_REVISIT_QUOTES`(`:35729`),本身已經三處分歧,專案沒有單一標準。我仍按錨判 major,因為「自訂引號剝除而專案已有同功能」是題目明列的情形;編排者若認定專案沒有既有做法,可以降級。

## F2 正文 WHY 行自建前綴辨識,繞開 `SYMBOL_RE`
severity: minor
blocking: 否
引句:「_REJ_WHY_RE = re.compile(r"^(?:[-*]\s+)?WHY:")」
佐證:file: `scripts/lumos:18168`
- 辨識摘要或正文的符號前綴,既有慣例是 `SYMBOL_RE.match(line.strip())` 再取 `m.group(1)`(`:4654`、`:4688`、`:32107`、`:32149`)。`SYMBOL_RE`(`:3835`)由 `SYMBOL_NAMES` 單一來源產生。
- 新碼只為了多認 `- WHY:` 這個列表寫法,就另寫了一支只認 WHY 的正則。結構上可以用 `SYMBOL_RE` 加 bullet 剝除取代。
- 程式註解已寫「同 SYMBOL_RE」,但實作並未共用它。

## F3 作廢狀態表手寫,跟專案的狀態值域不一致
severity: minor
blocking: 否
引句:「_REJ_RETIRED = {"project": ("superseded", "rejected")」
佐證:file: `scripts/lumos:18172`
- 專案已有狀態值域的單一來源 `_STATUS_ENUM`(`:18440`)和 `QUERY_CLOSED_STATUSES`(`:18437`)。
- `_STATUS_ENUM["project"]` 只有 `{todo, doing, done, superseded}`,沒有 `rejected`。新表的 project 那一格含 `rejected`,測試的 `Projects/否決計劃_計劃.md`(`status: rejected`)用的也是這個值。
- 這等於另立一份狀態詞彙,而且有一格對不上專案的合法值。讀 `status` / `type` 的寫法也跟 `status_of`(`:771`)不同,改用 `n.fields.get(...).strip().lower()`;不過 `:4771` 有同型先例,所以這點不單獨算。

## F4 `--json` 頂層欄位名跟最近的兩個列舉鄰居不同
severity: minor
blocking: 否
引句:「print(json.dumps({"total": len(items), "items": items}, ensure_ascii=False, indent=2))」
佐證:file: `scripts/lumos:18235`
- 最近的兩個列舉型指令 `cmd_query`(`:18496`)與 `cmd_search`(`:5318`)的頂層都是 `{"results": [...]}`。全檔沒有任何輸出用 `items` 當結果陣列。
- 項目內的 `node` 欄位(帶 `.md`)與 `cmd_query` 一致。
- ⚠ 交編排者:其他讀取指令的頂層欄位名各異(`rows`、`groups`、`problems`),所以只判 minor。

不對齊共 4 條,其中 major 1 條
