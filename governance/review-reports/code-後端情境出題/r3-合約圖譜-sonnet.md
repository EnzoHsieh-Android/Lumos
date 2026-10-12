severity: minor

三問總結:
- ①原問題的修復效果:在我跑的輸入上有行為證據。圍欄沒關、標題寫法認不得、寫在節外、阻塞旗標變體、重複狀態,修前都放行(gate=0),修後都擋(gate=1)。
- ②修補處的相鄰路徑:正常路徑仍成立。修補也留下 4 個缺口,見下面 finding。
- ③同一案例在兩版的結果:都在 finding 裡。

repair 與 preserve 分開報,最後列未驗範圍。

## Findings

severity: minor
blocking: 否
標題:外層看門判斷「圍欄有沒有關」的方法太粗,圍欄沒關但檔尾恰好像圍欄標記時,阻塞題仍整題消失。
引句:「unclosed = tail < len(lines) and not re.match(r"^\s*(```|~~~)", last)」
- 輸入:`"## 待決問題\n```\n- [Q1] a [類:需求][階段:需求][狀態:待人][阻塞]\n~~~\n"`。開的是 ``` 圍欄,最後一行是 `~~~`。
- 路徑:`_visible_lines` 把第 2 行起整段藏掉,所以 Q1 不在 `vis` 裡。`_pq_unreachable` 的 `last` 是 `~~~`,正規式 `^\s*(```|~~~)` 不分字元、不分長度,把它當成「已關閉」,`unclosed=False`,Q1 沒被列進 lost。
- 同型輸入:``"````\n…題目行…\n```\n"``(4 個反引號開、3 個反引號收,短的關不掉長的)。
- 兩版結果,指令 `python3.14 probe2.py <樹>`,退出碼 0:
  - 修前:`bt_open_tilde_last [] gate=0`。
  - 修後:`bt_open_tilde_last [] gate=0`,`4bt_open_3bt_last [] gate=0`。
  - 對照:最後一行是一般文字時修後 `gate=1`,所以只有「檔尾像圍欄」這個形狀漏。
- 修補測試 `t_backend_qo_unreachable_questions_fail_closed` 的「節內圍欄沒關」案例,最後一行是「退回。」,沒有涵蓋這個形狀。
- 歸因:未判定,偏有證據的原有漏查。修前同樣放行,但修補的設計宣稱「被沒關的圍欄藏住一律擋」,實作只靠檔尾單行猜測。
- 修法:不要猜,直接取 `_visible_lines` 掃完後的圍欄狀態。
- 重現:未能當場翻紅在 repo 測試上。我是用 `scripts/lumos` 的 `parse_pending_questions` 直接重現的,判定規格閘擋不擋用 `pending_questions_blocking_gate`。

severity: minor
blocking: 否
標題:新的「像題目」規則掃全檔、旗標寬鬆規則掃整行,一般敘述文字也會被當看不懂而擋規格閘。
引句:「_PQ_FLAG_LOOSE_RE = re.compile(r"[\[【]\s*(阻塞|不可逆)[^\]】\n]{0,20}[\]】]")」
- 輸入 A:`"## 待決問題\n- [Q1] 看 [阻塞原因] 說明 [類:需求][階段:實作][狀態:待人]\n"`。這是一題階段為實作、沒標阻塞的一般題。
- 輸入 B:`"# p\n## 背景\nQ1 [類別] 之類的說明 [狀態:...]\n"`。`_PQ_DEF_RE` 掃全檔,`[類別]` 命中 `[類`。
- 兩版結果,同上指令,退出碼 0:
  - 修前:A 是 `gate=0`、B 是 `None gate=0`。
  - 修後:A 是 `[(None, True)] gate=1`、B 是 `[(None, True)] gate=1`。
- 這是「寧可擋」的設計取捨。但訊息只說「旗標寫法看不懂」,作者看不出是自己的敘述文字撞到字面。
- 我掃了 repo 現有的 `docs/lumos-toolchain-knowledge` 全部筆記,沒有現行筆記被誤擋,只有 1 篇含此節,在兩版都沒有 bad 行。
- 歸因:有證據的修復回歸,是刻意取捨的副作用。
- 建議:要嘛縮小比對範圍(旗標只認標記區),要嘛在註解與筆記寫明這是已知誤擋。

severity: minor
blocking: 否
標題:計分器「結構錯的結果檔列成無效場」的修補不完整,欄位型別錯時 score 仍崩。
引句:「壞檔一律列成無效場(代碼審 r1、r2 併發席)」
- 輸入:結果檔 `{"results":[{"answer":null,"answer_len":3,"calls":[]}]}`、`answer_len` 是字串 `"3"`、`answer` 是整數 5。
- 路徑:`_result_row` 只驗第一列是物件。`_load_runs(valid_only=False)` 把 `answer` 原樣放進 run,`cmd_score` 的 `_regex_row` 對它跑 `re.search(..., run["answer"])` 與 `(run["answer_len"] or 0) > len(run["answer"])`。
- 兩版結果,`python3.14 p3.py <樹>`:
  - 修前:三個案例都是 `TypeError`(none、str vs int、int)。
  - 修後:三個案例都是同樣的 `TypeError`。
- 歸因:有證據的原有漏查。修補的測試 `test_load_runs_survives_wrong_shape_json` 只測 `_valid` 與 `_load_runs` 不崩,沒走到 `score` 這一步。
- 影響小:實驗已跑完,要有手動損壞的結果檔才會觸發。

severity: minor
blocking: 否
標題:新增的「寧可擋」行為沒有綁到計劃的驗收條款,且規格閘筆記有排版錯字。
引句:「計劃〈待決問題〉裡有有標阻塞、階段是需求或架構、狀態是待查或待人的題」
- 計劃 S1 條款只綁 `t_backend_qo_blocking_question_holds_spec_gate`,規格閘.md 與情境出題.md 只在散文裡說 `t_backend_qo_unreadable_questions_fail_closed` 守「寧可擋」,沒有 `[test:]` 鍵。
- 「有有」是重複字。
- 這是筆記與條款的對應缺口,不是行為錯。
- 歸因:有證據的修復回歸,只限文件。

## 已驗主張

repair:
- 在 `after` 副本跑 `python3.14 scripts/test_lumos.py -k backend_qo`,72 passed、0 failed。`-k kotlin` 是 31 passed。
- 翻紅釘有效,我實測過:
  - 把 `_pq_unreachable` 改成直接 `return []`,`t_backend_qo_unreadable_questions_fail_closed` 的 6 條 ① 斷言翻紅。
  - 把 `if loose:` 改成 `if False:`,3 條 ④ 斷言翻紅,②③ 留綠。
- 各種原本被吞的題目行修後都被擋(修前 gate=0、修後 gate=1)。這是我自己的輸入,不是只看作者測試:
  - `~~~` 圍欄沒關。
  - Setext 標題。
  - `## 待決問題清單`。
  - 4 格縮排的題目行。
  - `[阻塞 ]` 等旗標變體。
  - 題目行後面欄位裡出現旗標變體。

preserve:
- 關好的圍欄裡的範例不算、不擋:`closed` 案例與我的 `fence4` 都是 `gate=0`。
- 精確 `[阻塞]` 的既有擋法、階段是實作的待人題不擋:`normal_nonblock` 是 `gate=0`。
- 標記寫在最前面且後面有文字時,題目文字取標記之後:作者的 ⑥ 斷言通過。我另測了標記寫在最前面且後面沒文字的案例,題目文字是空字串,屬可接受。
- 圖譜固定席與合約:改動只在 `parse_pending_questions` 一帶、`_h2_section_lines` 多一個預設為 False 的參數、Kotlin 觸發詞、探針接線,以及評分器與測試。沒有碰 `search` 排除 superseded、`reinject`、授權檔白名單、`guard kill` 的 rc 優先序、`bound-tests` 等合約的程式路徑,判不影響。
- `_h2_section_lines` 的既有呼叫端(回退節、實務隱患節):`nested=False` 的路徑沒有改動,作者的 `-k rollback`、`-k door` 數字我沒有自己重跑,只做了閱讀判斷。

## 未驗範圍

- Kotlin 新觸發詞只讀了正規式,沒有逐條對抗。已知會漏兩種寫法:`webClient\n.get()` 換行鏈式呼叫,以及 `restTemplate?.exchange(` 的安全呼叫。
- 我沒有重跑探針的 `test_answer_max_reaches_codex_runner_and_cli_wiring` 突變,只讀過測試,接線與抽出 `_run_scenario` 的程式讀起來一致。
- 遮罩 `[甲乙]組` 與 `arm` 的行為只讀了正規式與作者測試,沒有另造輸入。
- 計分器重算兩輪結果「逐位元相同」的主張,我沒有重算,卷證在 `rating/` 與 `rating-mini/`。

總結:最嚴重 minor;blocking 共 0 條。
