severity: clean

## 固定席段說明

hook 有附固定席段。guard-kill、lumos-cli-read、bound-tests-gate、loop-convergence-recording、pitfalls-code-loop、測試假綠形態、design-loop、lumos-cli-lifecycle 這幾篇我都自己開筆記讀了合約行。其餘只列名的節點(reversibility-governance-ledger 等)我沒逐篇開。我只依 `git diff dd8729f..95977c1` 的檔案範圍判斷,diff 沒碰到它們的行為面。

## 逐節點判定

**guard-kill.md,★INVARIANT★ 兩條。diff 不破壞。**
- rc 優先序(綁 `t_guard_kill_rc_precedence`)。
  - rc 只看 `verdicts`,而 `verdicts` 只來自 `r["verdict"]`。這次 `cmd_guard_kill` 只新增 `if hk.on: res["_ran_solo"] = True`。
  - 先紅順序只改配方交出的順序,不改各判定值。略過列本來就從 rc 排除(`verdicts = [... != "skipped"]`)。
  - 實跑 `-k t_guard_kill_rc_precedence`:4 passed,0 failed。
- `--json` 純度(綁 `t_guard_kill_json_purity`)。
  - 新欄位 `_ran_solo` 已加進 `--json` 的剔除清單。
  - `result_out` 的列和殺傷力帳本 `_kill_log_rows` 都是明列欄位,不會帶出 `_ran_solo`。
  - 新增的診斷印字(`_kill_merge_off`、斷路器那行、合併基準那行)全是 `file=sys.stderr`。
  - 實跑 `-k t_guard_kill_json_purity`:6 passed,0 failed。
  - 另跑 `-k t_choice_guard_kill_new_params`(S12,不傳 merge 時行為不變):5 passed,0 failed。
- guard-kill.md 在這個範圍的 diff 沒動 INVARIANT 行。`lumos lint` 該節點為 0 問題。

**lumos-cli-read.md(search 預設排除 superseded)。不影響。** diff 裡沒有 search、`--include-superseded`、superseded 相關程式。

**bound-tests-gate.md(code-loop check 逐支真跑固定席綁的測試)。不影響。**
- 這次沒碰 `resolve_test_refs`、`_classify_one`,也沒碰閘本體。
- 計劃新增的 8 個 `[test:t_choice_kill_merge_*]` 與 `t_choice_kill_no_merge_unchanged`,在 `scripts/test_lumos.py` 都各恰有一個 `def`,沒有懸空。

**測試假綠形態.md(還原翻紅釘要配前置斷言)。不影響。**
- 該條綁的是 slim_uninstall 和 deinit 兩支測試,diff 沒改它們。
- 新測試是行為案例,不是「還原翻紅釘」。

**design-loop.md(處置閘第五步)。不影響。** diff 沒碰處置閘程式。這次的設計審不屬於此閘的程式路徑,這個範圍內也沒有新增 `[SN]` 子句違規。

**lumos-cli-lifecycle.md(re-inject sentinel)。不影響。** diff 沒有 reinject 相關改動。

**loop-convergence-recording.md、pitfalls-code-loop.md(標 ★RISK★,但本文沒有 ★RISK★ 合約行)。不影響。**
- pitfalls-code-loop.md 只有一條 KEY:`PITFALL_CLASSES` 要與 `difficulty.RISK_CLASSES` 一致、`_PITFALL_BLACKLIST` 要與 `difficulty._BLACKLIST` 一致。
- diff 範圍內搜不到 `PITFALL_CLASSES`、`_PITFALL_BLACKLIST`、`RISK_CLASSES`,零命中。
- loop-convergence-recording.md 的 diff 只涉及 `_GOV_FIELD_TYPES`、`_gov_row` 與 `_choice_event_extra` 的選用欄位。

## 與治理帳型別守衛的相鄰路徑

這條不屬任何固定席合約,是我另外讀到的。

- `_GOV_FIELD_TYPES` 新增 `merge_kind`、`merge_unclean`、`merge_off`(dict)和 `single_runs`(int)。
- `_gov_row` 用 `or {}` 和 `or 0` 把舊帳缺欄讀成預設值。
- `bool` 是 `int` 的子類別,這是型別守衛的常見破口。`single_runs` 只由程式計數寫入,看不到外部可控的路徑。

## 已驗主張

| claim | input | expected | case_source | before | after |
|---|---|---|---|---|---|
| rc 優先序沒被先紅順序與 `_ran_solo` 影響 | `t_guard_kill_rc_precedence` | 4 全綠 | 固定席綁定測試 | 未跑修前版 | 4 passed |
| `--json` 純度沒被新欄位影響 | `t_guard_kill_json_purity` | 6 全綠 | 固定席綁定測試 | 未跑修前版 | 6 passed |
| 不傳選用參數時行為不變 | `t_choice_guard_kill_new_params` | 5 全綠 | S12 條款 | 未跑修前版 | 5 passed |
| 新事件欄位與舊帳讀法 | `t_choice_kill_merge_event_fields`、`t_choice_kill_merge_failure_goes_single` | 全綠 | 計劃 S 條款 | 未跑修前版 | 6 passed、4 passed |

歸因:未判定。本席只做固定席核對,沒有跑修前版對照,也沒有發現需要歸因的缺陷。

## 未驗範圍

- 沒實跑 loop-convergence-recording、pitfalls-code-loop 兩節點的綁定測試,因為它們沒有 ★RISK★ 合約行,diff 也沒碰它們的程式。
- 沒審 `_kill_merge_*` 內部的正確性,那是其他席的鏡頭。
- 只列名的節點沒逐篇開。

總結:最高嚴重度 clean,blocking 0 條。
