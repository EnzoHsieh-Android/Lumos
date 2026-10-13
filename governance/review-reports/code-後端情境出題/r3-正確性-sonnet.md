severity: major

**審查範圍與方法**:我把修前(112ad15f)與修後(46bc93c3)兩版用 `git archive` 展開到 `/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet/{before,after}`。我用自己寫的探針(同目錄 `probe.py`、`p2.py`、`p3.py`)對兩版跑同一批輸入,指令是 `python3.14 <探針> <before|after>`。

我另外在 repo 根目錄用 `python3.14 scripts/test_lumos.py -k` 跑了 backend_qo、kotlin_spring、qo_ablation、scenario_probe_collect、rollback、spec_gate、stack_question,全綠(72、28、1、1、5、115、112 通過)。`-k pitfalls_stage` 選中 0 個測試,被腳本視為失敗,因為沒有這個名字的測試,不是測試紅。

## Finding 1:阻塞旗標寫成全形括號仍然靜默放行規格閘(題號 無;非 API 或授權題)

severity: major
blocking: 是
歸因:有證據的原有漏查(修前同樣放行;修補宣稱收掉這一類,但只收到兩種括號)

引句:「阻塞旗標只認 [阻塞]、[不可逆],寫成 [阻塞 ]、【阻塞】這類變體算看不懂」

file: `scripts/lumos:6920`。`_PQ_FLAG_LOOSE_RE` 只認 ASCII 的 `[` 和 `【`,不認全形 `［阻塞］`、`〔阻塞〕`,也不認 `(阻塞)`。

- **最小重現**(`W=/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet`):
  - 在 `p2.py` 裡,輸入 `## 待決問題\n- [Q1] 訂單 [類:需求][階段:需求][狀態:待人]［阻塞］\n`
  - 跑 `python3.14 $W/p2.py $W/after`,輸出 `'［阻塞］' gate False [(False, None)]`。同一行對 `〔阻塞〕`、`(阻塞)` 也是 `gate False`。
  - 修前版本結果相同。對照組 `[ 阻塞 ]` 在修前是 `gate False`,修後是 `gate True`。
- **走到哪一行**:
  - 這一行不含任何 ASCII `[阻塞]`。`_pq_parse_line` 的 loose 檢查沒匹配,`_PQ_TAG_RE` 的 group 3 也沒匹配,所以 `blocking=False`。
  - `bad` 為 None,`pending_questions_blocking_gate` 的 `held()` 在 `not q["blocking"]` 處回 False。
  - 結果是一題需求階段、待人、作者本意是阻塞的題,規格閘放行,lint 也不報。這正是這個閘要擋的東西。
- **為什麼算 major**:這是第二輪同一類(阻塞旗標變體)的補丁,結果仍是靠列舉括號種類,沒有改成「整行含『阻塞』『不可逆』字樣卻沒解析成旗標就擋」的統一規則。這符合「同類兩輪要換形狀」的情況。

## Finding 2:未關圍欄的偵測用「最後一行長得像圍欄」判斷,最後一行本身是圍欄開頭時反而放行

severity: minor
blocking: 否
歸因:有證據的原有漏查(修前整段都看不到;新增的看門只涵蓋最後一行不是圍欄標記的情形)

引句:「被沒關的圍欄藏住(檔尾整段看不見、最後一行不是圍欄標記)」

file: `scripts/lumos:6938`。`unclosed` 只看最後一個非空行是否符合 `^\s*(```|~~~)`,不看圍欄的實際開關狀態。

- **輸入**:`# p\n\n```\n- [Q1] a [類:需求][階段:需求][狀態:待人][阻塞]\n```python\n`(圍欄沒關,最後一行是 ` ```python `)。
- **結果**:`p3.py` 兩版都回 `None GATE False`,規格閘放行,被藏起來的阻塞題沒被抓到。
- **對照**:最後一行是普通文字(`prose`)時,修後回 `[(None, True)] GATE True`,有擋到。
- 同族還有「四個反引號開、三個反引號收」,結果一樣是放行。
- 觸發條件窄,所以只標 minor。

## Finding 3:筆記宣稱「沒有〈待決問題〉一節的計劃判定不變」與修後行為不一致

severity: minor
blocking: 否
歸因:有證據的修復回歸(修補自己引入;修前回 None,修後回 bad 並擋閘)

引句:「沒有〈待決問題〉一節的計劃判定與輸出不變」(見 `Systems/規格閘.md`、`Systems/情境出題.md`)

file: `scripts/lumos:6986`。`parse_pending_questions` 現在在 `sec is None` 時,只要 `_pq_unreachable` 找到題目形狀的行就不回 None。

- **輸入**:`# p\n\n## 背景\n1. Q1 [狀態:待人] 說明\n`,計劃沒有待決問題一節。
- **結果**:修前回 None、閘不擋;修後回 `[(None, True)]`、`GATE True`,規格閘回 1。
- 「寧可擋」的方向合理,但文件這句話要改成「沒有該節且沒有題目形狀的行」。
- 我掃了 repo 的 `docs/` 下所有筆記,兩版都是 0 份有 bad 項目,所以沒有現存計劃被誤擋。

## Finding 4:重複寫標記而被擋的題,規格閘印出的原因會誤導

severity: minor
blocking: 否
歸因:有證據的修復回歸(新增的 `dup_tags` 擋法沒配新的訊息分支)

引句:「認不得或重複寫(用哪一個都是猜)就當沒結」

file: `scripts/lumos:7946-7952`。`held()` 因 `dup_tags` 回 True 時,狀態和階段都是合法值,印字落入最後的 else。

- **輸入**:`[階段:需求][階段:實作][狀態:待人][阻塞]`。
- **結果**:輸出 `(第 N 行,狀態 待人)`,表頭卻說「還沒決定」,使用者看不出是標記重複造成。
- 只靠最後那句「寫法問題用 lumos lint 看細節」才找得到原因。

## 三問答覆

**①原問題的修復效果,有行為證據的部分(同一案例兩版對照)**
- 未關圍欄藏住阻塞題:`~~~` 開頭沒關、最後一行是普通文字時,修前 `GATE False`,修後 `GATE True`。
- 標題寫成「三、待決問題」、粗體、寫在節外:修前不擋,修後擋(`probe.py` 與新測試 `t_backend_qo_unreadable_questions_fail_closed`)。
- `[ 阻塞]`、`[ 阻塞 ]` 這類 ASCII 變體:修前放行,修後擋。
- 重複狀態或階段加阻塞:修前放行,修後擋;不阻塞的重複標記仍不擋(`GATE False`,與修前一致)。
- 標記寫在行首時題目文字變空:修後取標記之後的文字(測試 ⑥)。
- 全形括號旗標沒有修復,見 Finding 1。

**②修補處的正常與相鄰路徑**
- 正常的 `- [Q1] ... [阻塞]` 兩版同為 `GATE True`。
- 關好的圍欄(含檔尾的 ``` 和 `~~~`、縮排收尾、圍欄後有空行)裡的範例兩版都不誤擋。
- CRLF 檔案兩版相同。
- `_h2_section_lines` 的 `nested=False` 路徑在回退節、實務隱患節沿用原邏輯,rollback 5 個測試和 spec_gate 115 個測試全綠。
- 長行效能:6 萬空白、4 萬個 `Q1 [階段`、20 萬個 `x` 前綴、`1.` 重複 10 萬次、200 行各含 5000 個 `[ ` 的輸入,最慢 0.1 秒。
- 我掃了 repo `docs/` 下所有筆記,0 份產生 bad 項目。
- 計分器 `_result_row`、`_valid`、`_load_runs` 的壞檔路徑,新測試涵蓋 null、`[]`、`results:[1]`、`calls:null`。
- `scenario_probe._run_scenario` 的接線路徑也已確認。

**抓錯證據(突變)**:我在 `/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet/mut` 對修後樹做了兩處突變。
- 把 `cmd_packets` 的 `old.unlink()` 改成 `pass`:`test_packets_rerun_clears_stale_packets` 翻紅。
- 把 `_run_scenario` 的 codex 分支拿掉 `**extra`:`test_answer_max_reaches_codex_runner_and_cli_wiring` 翻紅,訊息是 `None != 4321 : codex`。

**③新發現的同一案例在修前與修後**
- Finding 1:修前與修後都是 `gate False`。
- Finding 2:修前與修後都是 `GATE False`。
- Finding 3:修前 `None`,修後 `[(None, True)]`、`GATE True`。
- Finding 4:修前與修後都是 `GATE True`(都被擋),訊息誤導是修後新增的分支才有的。

**其他已驗**
- 文件的場次數字與卷證一致:`results` 有 36 場、`results-mini` 有 18 場,合計 54 場;兩份 `mapping.json` 各 36 筆。
- 盲評遮罩:`arm_a`、`arm-b`、`甲組成員` 現在都會遮,修補有效。
- 角色卡:
  - be-api-compat:`pitfalls --stage --json` 新增 `unreadable` 鍵,是純新增欄位;沒帶 `--stage` 的輸出沒有改動。
  - be-authz:本次改動不涉及端點或資料授權,不適用。

**未驗範圍**
- 沒跑全套 3700+ 測試,也沒跑推送前的閘。
- 沒驗 `lumos lint` 的整合輸出(只驗到解析函式層)。
- 沒實跑 `lumos spec-gate` 命令列的完整輸出,只確認解析和擋閘判定。
- Kotlin 觸發詞只確認新增與既有測試綠,沒有逐字對 Android 專案實檔做誤亮度量。

總結:最嚴重 major;blocking 共 1 條。
