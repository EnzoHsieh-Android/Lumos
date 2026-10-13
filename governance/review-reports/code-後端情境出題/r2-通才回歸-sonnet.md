severity: minor

我在 `/tmp/lumos-seat-work/code-後端情境出題/通才回歸-sonnet/` 下用 `git archive` 解出修前(c960f6de)和修後(112ad15f)兩份,自己跑過。沒有 blocker 或 major。三條 minor 都不擋推。

## 固定席節點判讀
- **codex-harness**:不影響。`scenario_probe.py` 只改回答上限的傳遞方式,`collect_only` 缺 `expect` 時改成不崩潰;`run_one_codex` 的簽章是在尾端加選配參數。`test_lumos.py` 裡所有舊呼叫都沒傳 `answer_max`,仍可用。
- **lumos-cli-read、bound-tests-gate、design-loop、guard-kill、lumos-cli-lifecycle、授權與歸屬**:不影響。這份乙區 diff 沒碰 `search` 的過濾、處置閘、`guard kill` 的 rc、re-inject、授權白名單。
- **測試假綠形態**(還原翻紅釘要配前置斷言):下面第 1 條對應這條。`test_answer_max_flows_as_argument_not_global` 的前置斷言只蓋到 `run_one` 和 `_run_kwargs`,沒蓋到 codex 路徑和 `main` 的接線。

## 三問

**① 原問題的修復效果有何行為證據?**
- 回答上限不再靠改寫模組全域值。我在修後版跑 `python3.14 -m unittest scripts.test_autonomous_loop.TestScenarioProbeAblation`,在工作目錄 `after/`,退出碼 0,38 個測試通過。
- 同一個班次用 `answer_max=2000` 得到 `(2000, 3000)`,不給參數得到 1500。
- 修前版是 `main` 設全域值,沒有這個參數路徑。
- 重算結果沒變:拿 `rating/` 的真實評分檔(`labels-rater-claude.json`、`labels-rater-codex.json`、`adjudication.json`)跑修後版 `agree` 再跑 `final`,在 `after/`,退出碼 0。輸出的 `final.json` 與已存檔的 `rating/final.json` 逐位元相同,kappa 0.837,判定 FAIL。
- 新增的 `noise` 規則沒有誤傷實際資料:四筆非零 noise 都落在 P2、P6(R005、R014、R030、R034)。
- 修前版的 `final` 必須帶 `--agree`。我想在修前版用同一份資料重跑對照,但 zsh 沒切開參數,指令報錯、沒跑成,所以這一對照沒做。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- `final` 現在自己重算 kappa,不收 `--agree`。傳 `--agree` 會被 `argparse` 擋下(`SystemExit`),`adj-pack` 仍要 `--agree`,沒被連帶拿掉。
- `_load_runs` 遇到壞檔回傳 `valid=False`,不會整批崩潰。
- `check_labels` 在非亂問題填非零 noise 時會報錯,真實資料不受影響(見上)。
- `run_one_codex` 的簽章只在尾端加選配參數。`test_lumos.py` 的 6 個呼叫點(約 41208、42155、42418、42487、42507、42551 行)都沒有傳 `answer_max`,不受影響。
- `scenario_probe.py` 的 `--answer-max` 預設仍是寫死的 `1500`,沒有引用 `ANSWER_MAX`,兩處要手動同步。這點沒有造成失敗。

**③ 新發現的同一案例在修前、修後各是什麼結果?** 見下面三條。

## Findings

severity: minor
blocking: 否
標題:遮罩改寫後新增漏遮,盲評會洩露組別。
歸因:有證據的修復回歸
引句:「(?<![a-z])(?:codex|claude|openai|sonnet|opus|haiku|anthropic)(?![a-z])」
引句:「\barm[\s_-]?[ab]\b(?!\s+[a-z])|[甲乙]組(?![合織成件裝員])」
- **重現**:跑 `python3.14 .../probe_mask.py`,工作目錄 `/tmp/lumos-seat-work/code-後端情境出題/通才回歸-sonnet/`,退出碼 0,逐字輸出如下。

| 輸入 | 修前 | 修後 |
|---|---|---|
| `甲組成員同意` | `⟨遮罩⟩成員同意` | 原樣 |
| `乙組員` | `⟨遮罩⟩員` | 原樣 |
| `in arm b is better` | `in ⟨遮罩⟩ is better` | 原樣 |
| `arm_a path` | `⟨遮罩⟩ path` | 原樣 |
| `arm-b worktree` | `⟨遮罩⟩ worktree` | 原樣 |

- **路徑**:新增的負向預視 `(?!\s+[a-z])` 和 `(?![合織成件裝員])` 讓這些組別字樣整段不遮。
- **影響**:組別字樣本來就是盲評要隱藏的資訊,修後版重產盲評包時會漏。實驗已跑完、已發的包不受影響。
- **測試缺口**:`test_mask_edge_shapes` 只釘「應該保留」的一側(`can arm a trap`、`甲乙組合`),沒有釘上面這幾種「必須遮」的形狀。
- **反向**:修後版 `CLAUDE_CODE`、`codex2`、`Sonnet4`、`我是Claude` 改成會遮,修前版不遮,這幾個是真改善。

severity: minor
blocking: 否
標題:`answer_max` 在 codex 路徑和 `main` 接線都沒有行為測試守住。
歸因:有證據的原有漏查。修補新增了參數卻只測了一半,修前版同樣沒有測 codex 路徑。
引句:「"answer": _answer_field(final, source_token, answer_max)[0], "answer_len": _answer_field(final, source_token, answer_max)[1], "arm": arm, "ever_lumos": ever」
- **變異一(codex 路徑)**:複本 `mut/`,把 `run_one_codex` 的 `_answer_field(...)` 改回不傳 `answer_max`。跑 `TestScenarioProbeAblation` 得到 38 個測試 OK;`test_lumos.py -k scenario_probe` 得到 3 個通過、0 失敗;`-k codex` 得到 168 個通過、0 失敗。全部沒翻紅。
- **變異二(`main` 接線)**:複本 `mut2/`,讓 `run_at` 的 `extra` 濾掉 `answer_max`。`TestScenarioProbeAblation` 得到 38 個測試 OK,沒翻紅。同時開跑的 `test_lumos.py -k probe` 我沒等到結果,不納入結論。
- **影響**:這個實驗實際用的就是 `--answer-max 20000` 加 codex runner。回到預設 1500 的後果是結果檔被截斷、`_valid` 判無效,資料白燒。
- **修法**:替 `run_one_codex` 補一條和 `run_one` 對稱的測試,並讓測試走 `run_at` 或 `main`。
- **修前對照**:修前版是 `main` 直接設全域值,這個接線同樣沒測。

severity: minor
blocking: 否
標題:預先登記仍把已移除的 `run` 寫成現行步驟。
歸因:有證據的修復回歸
引句:「## 執行(qo_ablation.py run)」
- **證據**:file: `governance/eval/qo-ablation-2026-10/preregistration.md:44`。第 48、49 行還有「結果檔存在 results/ 底下」和「續跑」的說明。
- **壞引用**:修補把 `run` 子命令拿掉了(`main(["run",...])` 現在會 `SystemExit`),這一節還指著它。
- **無法重現**:這是文件引用不一致,屬靜態比對。

## 已驗與未驗範圍
- **已驗**:
  - `final` 用真實評分檔重算,輸出與存檔 `final.json` 逐位元相同。
  - 修後版 `TestQoAblation` 和 `TestScenarioProbeAblation` 共 63 個測試通過。
  - 兩條 codex 與 `main` 接線的變異。
  - 遮罩探針。
- **未驗**:
  - 修前版用同資料重跑 `final`(zsh 參數問題,沒跑成)。
  - `test_lumos.py -k probe` 在變異二下的結果(未等到)。
  - `scenario_probe.py` 的 `collect_only` 缺 `expect` 修補,我只看了 diff 的 `sc.get("expect") or []`,沒另外做變異。
  - 其餘 `test_lumos.py` 綁定測試沒全跑。

總結:最嚴重 minor;blocking 共 0 條。
