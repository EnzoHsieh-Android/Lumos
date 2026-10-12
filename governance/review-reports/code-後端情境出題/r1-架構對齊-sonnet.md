severity: major

審查範圍是 `/tmp/code-後端情境出題-r1.patch`。我找到 4 條不對齊,其中 3 條是 major。

**問 1:分層與依賴方向**

沒有跨層直呼,也沒有新的依賴方向。
- `_nl_rule_pending_questions` 掛進 `_lint_new_rules`,規則寫成「一條規則一支小函式」,跟 `_nl_rule_lands_in` 一樣。
- 規格閘的呼叫點 `_spec_gate_front` 在 `_spec_gate_clause_part` 之前,放在鄰居同一層。
- `cmd_pitfalls` 的 `stage` 分支是在函式開頭提早返回,跟既有的 `--diff` 檢查寫法相同。

不一致的地方不在分層,在「讀筆記文字」和「抽條款」。這兩處都是第二種做法,見問 3。

**問 2:命名與錯誤處理**

整體對齊鄰居。
- `cmd_pitfalls` 新增的三個參數錯誤都印 `擋下:` 到 stderr 並回 rc2,跟 `--diff` 以 `-` 開頭那條一致。
- `qo_ablation.py` 用 `✗ … ` 加 `file=sys.stderr` 並回 rc2,跟 `scenario_probe.py` 的 `✗ --runs 至少 1` 一致。
- `scenario_probe.py` 的 `--answer-max` 檢查用 `ap.error`,跟 `ablation_lumos_first.py` 的 `ap.error("--max-per-window 不可為負")` 一致。

一條 minor:

severity: minor
blocking: 否
引句:「print(f"讀不到 {md}:{e}", file=sys.stderr)」
`_pitfalls_stage` 的讀檔失敗訊息沒有 `擋下:` 前綴,同一個函式 `cmd_pitfalls` 的參數錯誤都帶。結構上沒問題,只是前綴不一致。審材外對照:`scripts/lumos` 的 `cmd_pitfalls` 內 `--diff` 檢查(約 `scripts/lumos:43019` 附近)。⚠ 行號沒逐行核對。

**問 3:第二種做法**

severity: major
blocking: 是
引句:「def _env_note_text(env, rel):」
原有 `env_text(env, rel)`(`scripts/lumos:761`)做的是同一件事:Env 是記憶體版就讀 `_texts`,否則讀磁碟。兩者唯一差別是例外處理。`env_text` 同時攔 `OSError` 和 `UnicodeDecodeError`,新函式只攔 `OSError`,所以遇到壞編碼的筆記會直接丟例外。同檔還有多處既有呼叫,例如 `scripts/lumos:4192`、`scripts/lumos:33314`。其中 `scripts/lumos:33314` 的註解正是「記憶體 Env 也讀得到(代碼審 r1 架構對齊席 F2)」。這就是你點名的 `_env_note_text` 情形。

severity: major
blocking: 是
引句:「def _pq_clause_tests(text):」
這支函式自己逐行用 `SPEC_CLAUSE_RE.search` 加 `TEST_REF_RE` 抽「條款綁的測試名」。既有做法是 `clause_bindings`(`scripts/lumos:7516`),它走 `_visible_lines` 和 `_strip_inline_markup`,會略過圍欄、反引號和註解,並且有「不開第二套引擎」的明文。
- 新函式不略過圍欄和反引號,範例裡的 `[S1] … [test:x]` 也會被算成條款測試。
- 它也沒用既有的測試名切分器 `_test_names_of`(`scripts/lumos:32858`),後者處理全形逗號、反引號和平台前綴。新函式只用 `split(",")` 和 `split(":")`。

同一個問題也在 `parse_pending_questions`:它逐行掃原文,不經 `_visible_lines`,所以圍欄裡寫的範例 `## 待決問題` 會被當成真的。這條我只從讀碼判斷,沒實跑,標 ⚠。

severity: major
blocking: 是
引句:「def cmd_run(a):」
`qo_ablation.py` 是第二套實驗執行器,而 `governance/eval/ablation_lumos_first.py` 已經有一套,而且它還 import 並重用 `scenario_probe` 的單一實作(該檔 `:29`,註解寫「單一實作來源」)。重複的部分:
- **有效場判定**:新的 `_valid` 對照既有的 `is_valid`(`ablation_lumos_first.py:78`)。
- **版本紀錄**:新的 `_cli_version` 對照既有的 claude 版本取得(`ablation_lumos_first.py:448`)。
- **逐場派工**:`subprocess.run` 呼叫 PROBE,對照 `ablation_lumos_first.py:239`。
- **跳過已有有效結果**:同上。
- **統計**:`kappa`、`sign_flip_p`、`delivery_rate` 是新增統計,repo 其他地方找不到同名實作,所以統計本身不算重複。

另有一處與既有做法不同:既有執行器用共用用量帳(`--max-per-window` 加 `--attempt-ledger`)管額度,新的 `cmd_run` 完全沒有,只傳 `--wait-on-limit`。

我判這是 major 的依據有兩點:新增了第二套執行器,並且繞過了既有的額度帳。但它是一次性對照實驗,預先登記了自己的算法。若你們認定實驗碼不受「單一執行器」約束,可降 minor。⚠

severity: minor
blocking: 否
引句:「global ANSWER_MAX」
`scenario_probe.py` 新增「模組全域變數由 `main()` 設定」的做法。這檔原本的模組常數(`GRADER_VERSION`、`LIMIT_RE` 等)都不在 main 裡被改寫,結果函式也沒有這種全域改寫。審材外對照:`scripts/scenario_probe.py:218`、`scripts/scenario_probe.py:1207`。`scripts/lumos` 裡雖有 `global _TESTMAP_DIR_RE` 這類先例(`scripts/lumos:29422`),但那是快取,不是命令列參數。本專案已有這個形狀,所以只列 minor。另外 `_answer_field` 在 `run_one` 的回傳字典裡被呼叫兩次,是小重複,不影響對不對齊。

**表態記錄對照**
- 表態記錄只有 `py-*` 題,沒有 `tension` 紀錄,所以不需要查四欄真假。
- `py-external` 答 satisfied,證據是 `qo_ablation.py:207`。那一行是 `subprocess.run([exe,"--version"], …, timeout=60)`,逾時確實有帶。
- 但同檔 `cmd_run` 內的 `subprocess.run(cmd, cwd=str(REPO))` 沒有 `timeout`。它外呼的探針自己有 `--timeout`,但父程序沒有。這跟「對應題答了 satisfied」有出入,屬於外部呼叫逾時題而非架構對齊題。我只提醒,不列為對齊 finding。

按你要的張力形狀,表態沒有被反駁的一題,其他只列這一組:
- 既有 X:`env_text` 與 `clause_bindings`。
- 隱患 Y:壞編碼筆記會讓 lint 丟例外,圍欄範例被當成真題或真條款測試。
- 這次 Z:新寫了 `_env_note_text`、`_pq_clause_tests`、`parse_pending_questions`。
- 不一致 N:3 處。

總結:不對齊共 5 條,其中 major 3 條。
