severity: minor

通才回歸-sonnet 對乙區第 4 輪修補的審查結果:沒有 blocker 或 major,只有兩條 minor。

## 三問

**① 原問題的修復效果有何行為證據?**
- **`--batch 0/-1`**:修後兩個值都回 2,舊包不動。
  - 命令:`python3.14 scripts/test_autonomous_loop.py TestQoAblation`,在 `/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve` 跑,29 項 OK。
  - 修前的失敗只有修補包自己帶的 `r3-repair-before.txt` 為證(ValueError),我沒有自己重跑修前版。
- **`answer` 為 None、`answer_len` 為字串**:我用自寫探針跑 `score`,修前版(`before4`)與修後版結果如下。
  - `answer=None`:修前 TypeError,修後 rc0、`valid=False`。
  - `answer_len="3"`:修前 TypeError,修後 rc0、`valid=False`。
  - `answer_len` 為 bool 或 float:兩版都 rc0、`valid=False`,沒變。
  - 探針在 `/tmp/lumos-seat-work/code-後端情境出題/通才回歸-sonnet/probe.py`,用 `python3.14 -I` 跑。
- **撤出〈待決問題〉正文解析**:`python3.14 scripts/test_lumos.py -k backend_qo` 共 9 項過、0 失敗,包括 `t_backend_qo_question_section_not_parsed` 與 `t_backend_qo_stage_facets_only`。
- **文件撤出的殘骸**:`grep` 在 `scripts/lumos`、`skills/` 內只找到〈待決問題〉的說明性註解與文件,沒有斷掉的呼叫。舊測試名(`question_line_shape`、`parser_robust`、`gate_fail_closed` 等)在程式與筆記裡都沒有殘留。
- **筆記格式**:`lumos lint` 檢查四篇受影響的筆記,全部 0 問題。
- **原始輸出路徑遮蔽**:我把修前版(`46bc93c3`)兩個 `codex-rater-raw.txt` 的 `/private/tmp/.../scratchpad` 換成 `<會談暫存目錄>`,與修後版(`b187b5e9`)逐位元相同。「只換路徑」成立。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常的計分輸入沒變:`trunc` 案例(答案被截斷)兩版都一樣標為無效並記 `truncated=True`。
- 錯誤輸入現在回無效場,不再崩。
- 相鄰的 `calls` 欄位仍會崩,見下面 finding 1。

**③ 同一案例在修前、修後各是什麼結果?** 見下面各條 finding。

## Finding 1

severity: minor
blocking: 否
歸因:有證據的原有漏查(修前、修後都崩,不是這輪修補造成)

「計分遇到欄位型別錯不崩」只補了 `answer` 與 `answer_len`。同一組結果檔的 `calls` 元素形狀錯,`cmd_score` 還是會崩。

- **哪個輸入、走到哪一行**
  - 結果檔 `calls=[["Bash"]]`(元素長度為 1):`_load_runs` 的 `tuple(c)` 收下它,`valid` 判成 True(`_valid` 只查 `calls` 是不是清單)。`code_start` 的 `for name, summ in calls:` 再解包失敗。
  - 結果檔 `calls=[["Bash",{"command":"touch x"}]]`(第二項是 dict):`_shell_writes_v2` 的 `re.search` 收到 dict,TypeError。
- **兩版證據**:同一支探針,`before4` 與修後樹的輸出都是
  - `calls_short CRASH ValueError not enough values to unpack (expected 2, got 1)`
  - `calls_dict CRASH TypeError expected string or bytes-like object, got 'dict'`
- **新測試的缺口**:`test_score_survives_wrong_field_types` 只列三個欄位組合,沒涵蓋 `calls`。
- **為什麼只算 minor**:真實結果檔的 `calls` 是機器產出的 `[工具名, 摘要字串]`,這個實驗也已跑完,只剩重算用途。

引句:「"answer_len": r.get("answer_len") if isinstance(r.get("answer_len"), int) else None,   # 型別錯照列成無效場,計分不崩(代碼審 r3)」

file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:69-80`、`governance/eval/qo-ablation-2026-10/qo_ablation.py:176-178`

## Finding 2

severity: minor
blocking: 否
歸因:有證據的修復回歸(筆記因這輪撤出而自相矛盾,修前這幾句與程式一致)

〈後端工程提問與證據擴充_計劃〉在 A 塊「設計紀錄」橫幅之外,還有幾處把已撤出的規格閘擋法與 lint 規則寫成現行。同一篇的 d10 與 S1 已經說程式不讀正文,內部不一致。

- **守衛面段**:寫「本案會改規格閘(新加一條擋法)與 lint 規則,誤擋會訓練人繞過」,但現在規格閘與 lint 都沒改。
- **RETIRE-IF 第①條**:寫「撤掉〈待決問題〉的規格閘檢查、lint 規則、`--stage`」,要撤的東西現在不存在。
- **回退節**:寫「回退規格閘那一條擋法、lint 規則」,一樣對不上。
- 這幾處不在橫幅涵蓋的 A 塊內。
- 兩版證據:`git show 46bc93c3:<該計劃>` 與 `git show b187b5e9:<該計劃>` 的這幾句相同,只有修後版多了 d10 與 S1 改寫,所以是這輪撤出後才變得矛盾。我沒有對這個不一致寫翻紅測試。

引句:「本案會改規格閘(新加一條擋法)與 lint 規則,誤擋會訓練人繞過」

file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:229`、`:142`、`:267`

## 測試品質與既有行為

- `t_backend_qo_question_section_not_parsed` 的 ① 只驗 rc 0 加字串不出現,沒有「同一份計劃拿掉這節輸出相同」的對照組。若有人把解析接回去,輸出會多出〈待決問題〉字樣,所以仍會翻紅,但判準偏弱。這條我不單獨報 finding。
- 兩支新增單元測試各自的修前失敗(TypeError、ValueError)我沒有逐支還原實作驗證,只重現了 `answer` 與 `answer_len` 兩條。
- `test_packets_bad_batch_keeps_old_packets` 的修前失敗只有修補包自己帶的證據,我沒有跑修前版。

## 圖譜固定席

- **全部「不影響」**:本次乙區只改文件、計分器的資料載入與參數檢查、`scripts/test_autonomous_loop.py` 的測試,以及原始輸出的路徑遮蔽。我沒有碰 `scripts/lumos`、`scripts/scenario_probe.py` 或 `scripts/test_lumos.py` 的 diff(那屬甲區)。
- **`codex-harness`**:`scripts/test_autonomous_loop.py` 只新增 `TestQoAblation` 兩支測試,沒動探針與執行器。
- **`bound-tests-gate`**:乙區沒改綁定測試閘的程式。
- **`design-loop`**:乙區沒改處置閘的程式。
- **`guard-kill`**:乙區沒改 `guard kill`。
- **`lumos-cli-lifecycle`、`lumos-cli-read`、`授權與歸屬`**:乙區沒碰 `re-inject`、`search` 或授權檔白名單。
- **`測試假綠形態`**:乙區沒新增「修 bug 的還原翻紅釘」類測試。
- **上述結論的限度**:`lumos-skills/*` 與 `INDEX.md` 的文字修改我逐行讀過,沒有指向已刪除的測試名或不存在的指令。

## 未驗範圍

- 甲區(`scripts/lumos`、`scripts/test_lumos.py` 的撤出)。
- 全套 3700 案例。
- 修前版逐支新測試的紅燈,只靠修補包自帶的 `r3-repair-before.txt`。

總結:最嚴重 minor;blocking 共 0 條。
