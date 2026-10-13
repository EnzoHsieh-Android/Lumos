severity: minor

審查結果:併發與資源鏡頭。沒有 blocker 或 major。`qo_ablation.py run` 的中斷續跑、半成品判斷都站得住,但有 4 個資源與錯誤路徑的缺口。

**續跑與半成品判斷(不成問題)**
- 探針寫 `--out` 是原子寫入(`scripts/scenario_probe.py` 的 `_atomic_write_text`),所以不會留下寫一半的結果檔。
- `.meta.json` 先寫、結果後到:Ctrl-C 後只剩 meta 沒結果時,`out.exists()` 為假,續跑照常重跑。
- `_valid` 對 `answer_len != len(answer)`、`limit_hit`、`fatal` 都判無效,半成品不會被當有效。

severity: minor
blocking: 否
`cmd_run` 呼叫探針的 `subprocess.run(cmd, cwd=str(REPO))` 沒帶逾時,與同檔註解「外呼一律帶逾時」不符。探針的 `--timeout` 只管單場,管不到沙盒建立或 hook 卡住。探針一旦卡死,整個 run 會一直等到人按 Ctrl-C。表態記錄 `py-external satisfied — qo_ablation.py:207` 指到的是 `if _valid(out):`,不是任何子程序呼叫;帶逾時的只有 `_cli_version` 那一處。
引句:「        subprocess.run(cmd, cwd=str(REPO))」

severity: minor
blocking: 否
探針的退出碼被丟掉,`cmd_run` 一律回 0,也沒有鎖。兩種後果:
- 探針立刻失敗(旗標錯、用量上限用完)時,迴圈會連續空轉剩下的場次,最後仍回 0。
- 同一個 `--out-dir` 同時開兩個 run 時,兩邊都判「尚無有效結果」,各自寫 meta、各自啟動探針,重複燒額度,後寫的覆蓋先寫的。

我沒另外重現,只是讀碼推得。
引句:「        print(f"[{a.runner}] {sid} r{k} 組{arm}", flush=True)」

severity: minor
blocking: 否
`_load_runs(valid_only=False)` 讀結果檔沒有防壞檔,`score` 會整個崩潰。重現:`mkdir -p o/claude/a; echo '{"results": []}' > o/claude/a/qo-P1-r1.json; qo_ablation.py score --out-dir o --gold g.json --dest d.json`,結果是 `IndexError: list index out of range`。`_valid` 自己有接 `IndexError`、`KeyError`、`ValueError`,但 `_load_runs` 第 231 行沒接。因此任何一個格式不對的結果檔都會讓 `score` 整批算不出來。⚠ 目前探針正常不會寫出空 `results`,所以我只給 minor。
引句:「        r = json.loads(p.read_text(encoding="utf-8"))["results"][0]」

severity: minor
blocking: 否
`pitfalls --stage` 讀計劃檔只接 `OSError`。非 UTF-8 的計劃檔會直接丟 Python 追蹤訊息,不走既有的「擋下」格式與 rc2。重現:`printf '\xff\xfe## x\n' > bad.md; lumos pitfalls bad.md --stage 需求`,結果是 `UnicodeDecodeError`。同檔的 `_spec_gate_load` 已經接了 `(OSError, UnicodeDecodeError)`,這裡漏了。
引句:「        text = Path(md).read_text(encoding="utf-8")」

**ANSWER_MAX 全域變數**
- 被 import 當模組時,沒走 `main` 的路徑維持預設 1500,行為不變。
- 同一程序重複呼叫 `main` 不會殘留,因為每次都用 `a.answer_max` 重設(預設 1500)。
- 只有「先跑過 `main(--answer-max N)`、再直接呼叫 `run_one`」這種混用才會殘留,目前沒有這種呼叫者。
- 這是設計取捨,不算缺陷。

**lumos 大圖譜成本**
- `_nl_rule_pending_questions` 只對 `type=project` 的筆記多讀一次檔,圖譜裡約 333 篇計劃,成本是毫秒級。
- 非 UTF-8 的筆記在 `load_vault` 就被建成空欄位筆記,規則在 `type != project` 提早回傳,不會崩。
- `_env_note_text` 重複了既有的 `env_text`(`scripts/lumos:761`),而且少接 `UnicodeDecodeError`。目前走不到,因為上述提早回傳擋住了,所以不另列 finding。

**固定席節點對照**(逐條判斷,皆不影響)
- `codex-harness`:`answer_len` 是新增欄位,`--answer-max` 預設 1500,既有輸出不變。
- `lumos-cli-read` ★INVARIANT★:search 的 superseded 篩選沒被碰。
- `bound-tests-gate`:改動沒動到閘的邏輯。
- `design-loop`:規格閘新增的「待決問題」擋法放在「沒有條款就提早結束」與 `--no-run` 之前,不是處置閘第五步;不碰「計劃有 [SN] 時任一條款要 [綁定測試:有]」那條。
- `guard-kill`、`lumos-cli-lifecycle`、`授權與歸屬`、`測試假綠形態`:都沒有碰到。`授權與歸屬` 要求主程式帶 SPDX 與 MIT 全文,這份 diff 沒動檔頭。

總結:最嚴重 minor;blocking 共 0 條
