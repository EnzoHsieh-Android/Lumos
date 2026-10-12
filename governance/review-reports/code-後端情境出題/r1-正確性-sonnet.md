severity: minor

沒有 blocker 或 major。我逐 hunk 走過一遍,找到 7 條 minor,都不阻擋。規格閘的位置、`pitfalls` 不帶 `--stage` 時的輸出、lint 在 `warn` 與 `on` 下的行為,三項核對無誤,詳見文末。下面的重現都在 `/tmp/lumos-seat-work/code-後端情境出題/正確性-sonnet/` 跑過。

**一、逐 hunk 發現**

severity: minor
blocking: 否
規格閘對格式寫壞的阻塞題會放行。輸入 `- [Q1] 問題 [阻塞][類:a][階段:需求][狀態:待査]`(「査」是錯字),或只寫 `[阻塞][階段:需求]` 沒寫狀態,走到 `pending_questions_blocking_gate` 的 `q["status"] in PQ_OPEN` 為假,回 `[]`,規格閘不擋。能補這個洞的只有 lint,但 lint 要等提交或推送才跑。
引句:「if q["blocking"] and q["stage"] in ("需求", "架構") and q["status"] in PQ_OPEN」
file: `scripts/lumos:6998`。重現:`parse_pending_questions` 配 `pending_questions_blocking_gate` 的輸出為 `[]`。

severity: minor
blocking: 否
`parse_pending_questions` 不認程式碼圍欄,也只認第一個 `## 待決問題`。圍欄內的示範如 "```\n## 待決問題\n- [Q1] x [阻塞][類:a][階段:需求][狀態:待查]\n```" 會被當成真題,該計劃的規格閘會永遠回 1。文件後面真正的第二個同名節完全不被解析,那裡的阻塞題不會擋。
引句:「start = next((i for i, ln in enumerate(lines) if _PQ_HEAD_RE.match(ln)), None)」
file: `scripts/lumos:6924`。重現:圍欄樣本解出 1 題,`blocking=True`、`status=待查`。

severity: minor
blocking: 否
欄位正則會在題目行內的 " 理由:" 處切斷「出處」欄,測試名也會帶著結尾標點。輸入 `出處:看 理由:這是理由 的 說明` 解出 `source='看'`,長度 1 小於 4,lint 在 gate=on 時誤報「自答卻沒附出處」。輸入 `測試:t_foo。` 解出 `test='t_foo。'`,對不上條款裡的 `t_foo`,誤報「不在任何一條驗收條款」。
引句:「_PQ_FIELD_RE = re.compile(r"(出處|理由|測試):\s*(.*?)(?=\s+(?:出處|理由|測試):|$)")」
file: `scripts/lumos:6920`。

severity: minor
blocking: 否
`pitfalls --stage` 讀到非 UTF-8 的檔會直接丟 Python 追蹤訊息。`_pitfalls_stage` 只接 `OSError`;同一份計劃走 `_spec_gate_load` 時會接 `UnicodeDecodeError` 並印出原因。
引句:「text = Path(md).read_text(encoding="utf-8")」
file: `scripts/lumos:43032` 起的 `_pitfalls_stage`。重現:`printf '## 待決問題\n\xff\n' > bad.md; lumos pitfalls bad.md --stage 需求`,輸出 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff`。

**二、實驗計分器 `qo_ablation.py`**

severity: minor
blocking: 否
`code_start` 的重新導向正則會把引號裡的 `>` 當成寫檔,對只讀的 grep 誤判。跑 `code_start([("Bash","grep -rn '=> handler' src/")])` 得 True,`grep -rn "a -> b" .` 也是 True。`>` 後面接的字被當檔名,又抽不出路徑,所以保守判成寫碼。這個誤判會讓判決條件 `code_b > code_a` 灌水,v2 只修了 gradle 字樣那一種,這裡是同一類。
引句:「r"(?<![0-9&])>>?\s*(?!/dev/null)[\w./-]+|"」
file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:35`。

severity: minor
blocking: 否 ⚠
`cmd_agree` 只在題 P1、P2、P3、P6 比對亂問數的分歧,`merge` 卻對所有題都判差大於 1。若兩位評分員在其他題給的亂問數差大於 1(例如 3 對 0),`merge` 丟出「亂問數差 >1 卻沒有仲裁」,但 `adj-pack` 從沒為它產生過仲裁列,無法修復。評分員說明寫只判這四題,實際會不會填非零值我判不準,所以標 ⚠。
引句:「if _scenario_of(mapping[bid]) in NOISE_SCENARIOS and abs(la[bid]["noise"] - lb[bid]["noise"]) > 1:」
file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:328` 與 `:376`。

**三、測試獨立判準**(對照〈實作測試品質〉)

severity: minor
blocking: 否
三處測試過鬆,各自抓不到一種已知的壞法。
- `t_backend_qo_stage_order_and_cap` 的 ⑤ 拿新程式碼跑兩次互相比對,抓不到「不帶 `--stage` 的輸出被改掉」。基準要改成寫死的字串,或對 `git show HEAD:scripts/lumos` 的舊版輸出比。
- `test_answer_max_flag_parses...` 只驗退出碼。把 `scripts/scenario_probe.py:1208` 的 `ANSWER_MAX = a.answer_max` 刪掉,所有測試照綠,實驗卻會全場判截斷無效。
- `t_backend_qo_question_line_shape` 只 grep 標準輸出,沒驗 gate=on 時 rc 為 1、warn 時為 0,也沒驗 doctor 那條路。
引句:「plain_before.stdout == plain_after.stdout and "[Q3]" not in plain_after.stdout」
file: `scripts/test_lumos.py:56086`。

**四、pitfalls manifest**
- 併發題指的 `scripts/scenario_probe.py:1207` `global ANSWER_MAX`,判誤報。它在 `main()` 解析參數後賦值一次,之後全是讀取,沒有共享寫入。
- 表態 py-external 引的 `qo_ablation.py:207` 是傳給子程序的 `--timeout`,不是 `subprocess.run` 的逾時。外層 `subprocess.run(cmd, cwd=str(REPO))` 沒設逾時,但子程序內部有逾時,所以不成立缺陷。
- py-eventloop、py-parallel、py-memory、py-hotpath 的 na 與我看到的一致:同步程式、無 async、無無界快取。

**五、本案特定鏡頭**
- **規格閘位置**:核對無誤。新擋法在 `_spec_gate_print_rejections` 之後、`_spec_gate_clause_part` 與 `prep is None` 的提早結束之前,也在 `--no-run` 的處理之前,所以只有待決問題、沒有條款的計劃也會被擋。副作用:提前回 1 時不寫 `_spec_gate_record` 與治理帳,先前的 PASS 留痕仍在。
- **lint 在 gate 兩種值下**:`_lint_new_rules` 由 `cmd_lint` 依 `note_lint.gate` 分流,`on` 進 errs 回 1,`warn` 進 warns 回 0;doctor 那條路有 try 包住。邏輯正確,只是測試沒覆蓋(見第三節)。
- **`--stage` 不帶時**:`cmd_pitfalls` 只多了 `if stage is not None` 一段,其餘路徑不變,輸出逐位元不變。`--diff` 的 JSON 因 kt 題組多了兩個 shape_only 題,`stack_questions_meta` 會多兩項,`stack_questions` 整組清單不變。
- **`parse_pending_questions` 回 None**:`_nl_rule_pending_questions` 用 `not qs` 接住,規格閘走 `or []` 接住,`_pitfalls_stage` 走 `pending_questions_for_stage` 的 `qs or []` 接住,三處都接住。`env.resolve` 回 None 時 `_pq_decision_state` 回 `"missing"`。frontmatter 沒有 `decisions` 時也是 `"missing"`。`[[X|別名]]#d1` 的正則可解析。
- **新舊互讀**:舊版 lumos 不認得這一節,不會因它擋。新計分器讀舊結果檔缺 `answer_len` 時判無效,且 `_meta_ok` 失敗會回 2 要人移走舊檔。

**六、圖譜鏡頭(固定席,逐條判)**
- `codex-harness`:`scenario_probe.py` 只多了 `answer_len`、`--answer-max`、空 expect 的 `judge`,不改 Codex 流程,不影響。
- `lumos-cli-read`(search 排除 superseded):沒碰 search,不影響。
- `bound-tests-gate`:只新增測試、未改閘邏輯,不影響。
- `design-loop`(處置閘第五步):`_clause_check` 與審材格式規則未動,不影響。
- `guard-kill`:rc 優先序與 `--json` 純度未動,不影響。
- `lumos-cli-lifecycle`(re-inject):未動,不影響。
- `授權與歸屬`:`governance/eval/` 不在 `_VENDORED_TOOLKIT` 或 `_VENDORED_TREE_FILES`,所以新檔 `qo_ablation.py` 沒有 SPDX 不違規;`scripts/lumos` 檔頭未動,不影響。
- `測試假綠形態`(還原翻紅釘需配前置斷言):新測試有翻紅釘,但上面第三節指出的 ⑤ 與 `--answer-max` 兩處抓不到對應的壞法,屬於同類顧慮。
- 超限只列名的節點(`pitfalls-code-loop`、`規格閘` 等):這份 diff 沒有任何一處改到它們宣稱的行為。

**七、角色卡**
- `be-api-compat`:CLI 對外輸出的新增都是加法(`answer_len`、JSON 多出 meta 項、`--stage` 是新旗標),舊讀者讀得懂。
- `be-authz`:沒有新增端點或資料存取,不適用。

總結:最嚴重 minor;blocking 共 0 條
