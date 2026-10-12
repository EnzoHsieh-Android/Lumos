severity: minor

我這區審了計分器 `qo_ablation.py`、探針 `scenario_probe.py` 的 `--answer-max` 改成照參數傳,以及自主迴圈測試檔裡對應的測試。沒有 blocker 或 major,有三條 minor。所有重現都在我自己的臨時目錄跑,修前版本用你給的乾淨副本。

## Finding 1:壞結果檔「列成無效場」的修補只涵蓋寫到一半的檔,結構錯但語法合法的 JSON 仍讓整批崩潰

severity: minor
blocking: 否
歸因:有證據的原有漏查(修補把壞檔入口補到一半,沒引入新錯)
引句:「壞檔照列成無效場,不讓整批算不出來(代碼審 r1 併發席)」
file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:140-150`(`_valid` 只接 `OSError, ValueError, KeyError, IndexError`,沒接 `TypeError` 和 `AttributeError`)
file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:154-170`(`_load_runs`)

- **走一遍的路徑**:結果檔內容是 `null`、`[]`、`{"results":[1]}`,或 `"calls":null`。
  - `_valid` 裡的 `json.loads(...)["results"][0]` 對 `null` 和 `[]` 丟 `TypeError`。
  - `{"results":[1]}` 在 `r.get(...)` 丟 `AttributeError`。
  - 這些例外沒被接住,`_load_runs` 的 `try` 在後面,輪不到它。
  - 連 `valid_only=False`(`score` 子命令的路徑)也崩,因為 `"valid": _valid(p)` 與 `r.get("calls")` 照樣丟例外。
- **重現**:我把四種內容各寫成 `x/a/qo-P1-r1.json`,呼叫 `_load_runs`,工作目錄 `/tmp/lumos-seat-work/code-後端情境出題/併發資源-sonnet`,用 `python3.14 t.py <檔>`。

| 輸入 | 修前 `valid_only=True` | 修前 `valid_only=False` | 修後 `valid_only=True` | 修後 `valid_only=False` |
|---|---|---|---|---|
| 截斷 JSON `{"results":[{"ans` | OK(空) | JSONDecodeError | OK(空) | OK(`valid=False`) |
| 空檔 | OK(空) | JSONDecodeError | OK(空) | OK(`valid=False`) |
| `{"results":{}}` | OK(空) | KeyError | OK(空) | OK(`valid=False`) |
| `null` | TypeError | TypeError | TypeError | TypeError |
| `[]` | TypeError | TypeError | TypeError | TypeError |
| `{"results":[1]}` | AttributeError | AttributeError | AttributeError | AttributeError |
| `"calls":null` | TypeError | TypeError | TypeError | TypeError |

- 修補確實修好了寫到一半的檔(前三列修前崩、修後不崩);後四列修前修後完全相同。
- 這個計分器已註明只用來重算,實際會遇到的壞檔多半是寫到一半,所以降為 minor。

## Finding 2:`--answer-max` 傳到 Codex 場次這條新接線沒有任何測試守

severity: minor
blocking: 否
歸因:有證據的修復回歸(修補新增了一條沒被測試覆蓋的路徑;程式本身接對了)
引句:「"answer": _answer_field(final, source_token, answer_max)[0], "answer_len": _answer_field(final, source_token, answer_max)[1], "arm": arm, "ever_lumos": ever」
file: `scripts/scenario_probe.py:1005`(`run_one_codex`)

- **走一遍的路徑**:
  - 修前由 `main()` 設全域 `ANSWER_MAX`,Codex 與 Claude 兩條路徑都吃得到。
  - 修後兩個執行器各自收 `answer_max`,新測試 `test_answer_max_flows_as_argument_not_global` 只呼叫 `run_one`,沒碰 `run_one_codex`。
  - 若有人改成 `_answer_field(final, source_token)`(漏傳),`--runner codex --answer-max 20000` 會悄悄只存 1500 字,`answer_len` 與存檔長度不等,計分器 `_valid` 會把整場判成被截斷。
- **破壞驗證**:
  - 我在 `/tmp/lumos-seat-work/code-後端情境出題/併發資源-sonnet/mut`(從 112ad15f `git clone --shared`)把 1005 行的 `answer_max` 拿掉。
  - 該區 63 支測試(`python3.14 -m unittest scripts.test_autonomous_loop.TestScenarioProbeAblation scripts.test_autonomous_loop.TestQoAblation`)連跑兩次都 OK。
  - `python3.14 scripts/test_lumos.py -k scenario_probe` 的 3 支也全綠。
  - 第一次跑有一個 `test_attempt_ledger_two_parent_race_retains_loser_candidate` 紅,還原後和破壞後再跑都綠,判定是併發測試的偶發紅,與這個破壞無關。
  - 所以這個變異沒有被抓到。
- **未能重現的部分**:Codex 這條路徑實際出錯的場景,我只做了測試層驗證,沒有真跑 Codex。

## Finding 3:`packets` 重跑時不清舊評分包,檔數變少會留下孤兒包

severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後相同,修補沒碰這段)
引句:「for i in range(0, len(packets), a.batch):」
file: `governance/eval/qo-ablation-2026-10/qo_ablation.py:210-213`(`cmd_packets`)

- **輸入**:同一個 `--dest`,先用 `--batch 2 --seed 1` 產 5 包,再用 `--batch 8 --seed 2` 重產。
- **走到哪一行**:只覆寫 `packet-01.json`、`packet-02.json`,`packet-03` 到 `packet-05` 不刪。
- **結果**:`ls w/pk` 還有 5 個檔;包內 blind_id 共 16 個,對照表只有 10 個。修前修後輸出完全一樣。
- **為何只列 minor**:
  - 多出的 id 會讓 `check_labels` 報「多 …」而大聲失敗。
  - `adj-pack` 會 glob 讀整個目錄,舊包內容會混進仲裁包。
  - 檔數沒變少時是整批覆寫,不留孤兒。
  - 原檔頭註明盲評包已產完,只有重產才踩到。

## 三問的回答

**① 原問題的修復效果有何行為證據?**
- 壞結果檔列無效:對截斷、空檔、`results` 為 dict 三種輸入,兩版對照見 Finding 1 的表,修前崩、修後不崩。結構錯但語法合法的輸入沒修到,見 Finding 1。
- 上限改成照參數傳(Claude 路徑):
  - `python3.14 -m unittest scripts.test_autonomous_loop.TestScenarioProbeAblation scripts.test_autonomous_loop.TestQoAblation` 在 112ad15f 為 63 支 OK。
  - `python3.14 scripts/test_lumos.py -k probe` 為 431 passed、0 failed。
  - 在修前副本,新測試呼叫 `run_one(..., answer_max=2000)` 會因為沒有這個參數而不通過,此項依簽名推斷,我沒有在修前副本實際執行。
- Codex 路徑的修復效果未判定,理由見 Finding 2。
- `collect_only` 省略 `expect` 時評分不崩:我沒有在修前副本實際執行,只確認修後測試 `test_collect_only_without_expect_key_grades_without_crash` 綠。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- **正常路徑**(合法結果檔、旗標預設值)仍成立。
  - 合法結果檔在兩版都得到 `valid=True`。
  - 預設上限仍是 1500,測試 `assertEqual(len(dflt["answer"]), 1500)` 綠。
  - `-k ablation` 5 支、`-k attempt` 23 支、`-k source_probe` 58 支全綠,都是在 `scripts/` 與 HEAD 無差異的工作目錄跑的。
- **錯誤路徑**只有部分成立,缺口見 Finding 1。
- **相鄰路徑**:`_run_kwargs` 現在一律帶 `answer_max`,我只搜出 `scripts` 與 `governance/eval` 裡呼叫 `run_one`、`run_one_codex` 的地方,其中 `test_lumos.py` 用 `patch.object(mod, "run_one", side_effect=...)` 的案例在 `-k probe` 全綠,沒有看到簽名不合的問題。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- Finding 1:見上表。
- Finding 2:修前由全域變數涵蓋,沒有「漏傳」這種失誤形狀,所以沒有可比的修前結果。
- Finding 3:修前修後同為孤兒 5 檔、blind_id 16 對 10。

## 圖譜鏡頭

- `Systems/codex-harness`、`Systems/測試假綠形態`:`scenario_probe.py` 的改動沒有破壞既有行為合約。測試假綠形態要求「還原翻紅釘」配前置斷言,新增的 `test_answer_max_flows_as_argument_not_global` 前半(`len(row["answer"])==2000`)確實執行到 `run_one`,但沒涵蓋 Codex,見 Finding 2。
- `Systems/bound-tests-gate`:這次沒有改 `scripts/lumos` 以外的合約綁定測試,Codex 路徑的變異沒被抓到屬於測試品質,不是合約破壞。
- `Systems/lumos-cli-read`、`Systems/design-loop`、`Systems/guard-kill`、`Systems/lumos-cli-lifecycle`、`Systems/授權與歸屬`:我這區(`qo_ablation.py`、`scenario_probe.py` 的上限傳遞、`test_autonomous_loop.py`)沒有碰這幾個合約的對象,判不影響。
- 超出上限、只列名的節點:未逐一審。

## 未驗範圍

- 沒真跑 Codex 或 Claude 執行器,只做 mock 層測試。
- 沒驗證 `qo_ablation.py` 的 `final` 與 `merge` 在真實卷證標註上的結果,我沒拿卷證做完整重算。
- 沒驗 `packets`、`mapping` 在寫入中途被打斷時的狀態,這種打斷窗口很小,我判定不值得標。
- 沒驗 `--expect-runs` 預設為 0 時漏場次的行為,只讀程式碼,沒有行為證據。

總結:最嚴重 minor;blocking 共 0 條。
