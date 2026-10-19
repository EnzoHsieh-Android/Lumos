severity: minor

這份 diff 沒有第二套讀帳、寫帳或 git 呼叫,也沒有跨層直呼。設計審 r1 要求的四項都照做了。另有 7 條小不一致,結構都對,沒有一條擋推。

我是對著已套用 patch 的工作樹 `55da596f` 核對的,所以下面的行號是現行 `scripts/lumos` 的行號。

## 1. 分層與依賴方向

設計審要求的四項:

- **讀治理帳**:`_spec_gate_gov_index` 用 `_gov_vc_gate_events`(`scripts/lumos:15703`)。帳壞的原因照原樣往上傳,推送閘擋下,跟 `_nogo_ctx_gov`(`scripts/lumos:9613`)的 fail-closed 一致。
- **寫治理帳**:`_spec_gate_record` 用 `_gate_event`(`scripts/lumos:1497`)。("spec-gate","spec-gate-record") 不在 `_GOV_LOCAL_PAIRS`(`scripts/lumos:1369`),所以會進版控帳,讀寫兩端對得上。
- **git**:新碼全走 `_lens_git`(`_note_text_at_rev`、`_lint_born_base_text`、`_git_ignored`,後者同 `scripts/lumos:1477` 的 check-ignore 寫法),或鄰居 `_nodehome_git`。沒有新的 `subprocess.run(["git",...])`。
- **lands_in 正規化**:`link_target`(`scripts/lumos:502`)加 `_lands_in_bad`(`scripts/lumos:28543`),跟 lint 和處置閘同一支判斷。

新指令 `summary-add` 的骨架跟 `cmd_summary_line`(`scripts/lumos:22696`)一樣:先檢查參數,再 `env.find` 和 `_node_not_found(write_side=True)`,接著 `_vault_write_lock`,最後 `*_locked`,用 `atomic_write_verify` 寫入。`HELP_WHEN`、`add_parser`、`main()` 分派也都登記在 `summary-line` 旁邊。

兩處值得交編排者看的依賴:

- **lint 新增 git 依賴**:`_lint_collect`(`scripts/lumos:6683`)原本只做單篇文字檢查,現在新增的 `_lint_born_true` 會叫 `_lens_git` 和 `_drift_probe_tree`。這是 lint 第一次依賴 git 和 drift 層。它有「沒有可判條件就直接回、不叫 git」的早退,也有 `_LINT_BORN_TREES` 快取,成本有控。
- **讀磁碟沒擋捷徑**:`_nodehome_worktree_homes` 直接用 `(Path(root)/p).read_bytes()`。同層的 `_nodehome_reader`(`scripts/lumos:33247`)讀磁碟時有 `is_file() and not is_symlink()` 的守衛,這裡沒有。

severity: minor
blocking: 否
引句:「raws = [_nodehome_git(root, "ls-files", "--others", "--exclude-standard", "-z", "--", spec),」
file: `scripts/lumos:33235`(`_nodehome_changed_vs_disk` 已經在做「工作目錄對索引的差異路徑集」,`_nodehome_split_z` 在 `scripts/lumos:33198`)
說明:新函式自己重寫了 diff 清單和切 `\0`,又沒有鄰居的捷徑守衛。`ls-files --others` 是真的新需求,但 diff 那半可以直接用 `_nodehome_changed_vs_disk`。⚠ 小重複,交編排者判。

## 2. 命名與錯誤處理

沿用鄰居的部分:

- 擋下一律是「擋下:… 檔案沒動」加 `return 2`,跟 `summary-line` 和 `cmd_append` 相同。
- `(結果, 擋下訊息)` 的二元組,跟 `_about_code_path`(`scripts/lumos:23093`)相同。
- 治理帳寫不進去只印 stderr,不改判定,符合 `_gate_event` docstring 的約定。
- `[spec-gate]` 前綴也跟鄰居一致。

不一致的地方:

severity: minor
blocking: 否
引句:「if not args.hm_staged and args.hm_diff is None:     # 沒帶範圍照 --staged(〈做法〉9 B9;掛鉤都明寫旗標)」
file: `scripts/lumos:46184`(同族的 `cochange check` 沒給範圍仍然 `擋下 … return 2`)
說明:`home check` 和 `note-shape` 改成沒給範圍就預設 `--staged`,同族的 `cochange check` 還是擋下。「--staged/--diff 沒給」的處理在三個指令間不一致。

severity: minor
blocking: 否
引句:「print("    4. 在同一個工作目錄跑 lumos spec-gate」
file: `scripts/lumos:24778`(鄰居的寫法是 `照原因補:\n    lumos append <節點> about_code …`,指令獨立縮排一行)
說明:`_spec_gate_low_not_red` 的補法把指令夾在編號步驟的句子裡,不是獨立一行。`_spec_gate_push_no_record` 的「跑一次 lumos spec-gate …」也是夾在句中。

severity: minor
blocking: 否
引句:「def _s14_plan_status(env, r):」
file: `scripts/lumos:4155`、`scripts/lumos:4404`(鄰居是 `_doctor_<x>_lines` 和 `_doctor_p2_unbound`)
說明:doctor 段的輔助函式慣例是 `_doctor_` 開頭,放在 doctor 輔助區。這支是唯一的 `_s<數字>_` 開頭,而且放在規格閘函式群裡。

## 3. 第二種做法

沒有 major。沒有發現另一套讀帳或寫帳、另一套 git 呼叫、另一套摘要解析。`_ns_summary_logical`、`_ns_slot_line_problems`、`_ns_old_keys`、`_drift_fix_shape_err`、`_summary_line_hits` 和 `_summary_line_pick_err` 都沿用了既有函式。以下是小重複和讀端分歧:

severity: minor
blocking: 否
引句:「old = {tuple(x[2]["conds"]) for x in _probe_lines(base)[0] + _retire_lines(base)[0]}」
file: `scripts/lumos:42081`(`_drift_probe_old`,函式本體是同樣的 `{tuple(x[2]["conds"]) ...}`;推送閘的轉變判定在 `_drift_probe_judge`)
說明:docstring 說「整組判法跟推送閘同一支」,但「起點有沒有同一條」是在 lint 裡另寫一份,沒有改寫成呼叫 `_drift_probe_old`。⚠ 它只判寫下就成立、比推送閘窄,可以算刻意,但等於兩處各自維護「新寫」的定義。

severity: minor
blocking: 否
引句:「def _fm_touch_updated(lines, e, today):」
file: `scripts/lumos:22784`(`_summary_line_rebuild` 的 updated 迴圈)、`scripts/lumos:23562`(supersede 的 updated 換行)、`scripts/lumos:23483`(`_fmt_decision_value` 裡還留著 `len((str(v) + "x").splitlines()) > 1`)
說明:「把 updated 換成今天」這段迴圈現在有三份相同的邏輯。另外 `_has_line_break` 新抽出來,卻只套用在 summary 兩條路徑,同族的 `_fmt_decision_value`(註解還寫「認法同 summary-line」)沒改用它。

severity: minor
blocking: 否
引句:「gw = _gate_event(_vault_repo_root(env), "spec-gate", "spec-gate-record", f"規格閘留痕 {rec['token']}", nodes=[rel],」
file: `scripts/lumos:1582`(`_gate_event_fit`,舊句檢查、note-shape、note-reread、drift-check 的帶清單事件都用它控制 4096 位元組)
說明:`extra` 帶 `tests`、`exclusions`、`nogo_skipped` 這幾個清單,沒走 `_gate_event_fit`,也沒有註解說明為什麼不裁。若不裁是刻意的(裁掉 `tests` 會讓推送閘少跑測試),要寫進註解。另外手寫的 `gw is False` 警告沒用 `_gate_event_or_warn`(`scripts/lumos:1623`),但 `_gate_event` docstring 允許呼叫端自己講,所以這點不列。⚠ 交編排者。

severity: minor
blocking: 否
引句:「_sg_latest = _spec_gate_latest_records(env)」
file: `scripts/lumos:3244`(doctor S14 仍只讀本機審查帳;`cmd_spec_gate` 在 `scripts/lumos:9213`、推送閘在 `scripts/lumos:9964` 已改讀 `_spec_gate_latest_merged`)
說明:這句不在 diff 新增行裡,而是 diff 上下文;引句是工作樹上同一行。同一份規格閘留痕,現在有「合併兩本帳」和「只讀本機帳」兩種讀法。乾淨 clone 的 doctor S14 會看不到留痕。這條也是 ⚠,因為 S14 是統計用途,可能刻意不改。

不對齊共 7 條,其中 major 0 條

(七條是:`_nodehome_worktree_homes` 重寫差異清單、`home check` 與 `note-shape` 預設 `--staged`、補法指令夾在句中、`_s14_` 命名、`_lint_born_true` 另寫「新寫」判斷、`updated` 迴圈與換行判斷各多一份、`spec-gate` 留痕沒用 `_gate_event_fit` 加 doctor S14 讀端分歧。)
