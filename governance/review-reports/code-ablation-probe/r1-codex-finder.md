severity: major

- `major` — `governance/eval/ablation_lumos_first.py:149`：答案內容完全正確、但先用了 `Grep` 再敲 lumos 時，`run_one()` 的 `passed` 已因 M1 順序失敗而為假，M4 仍用它計數，故所謂「答案正確率」實際混入了工具順序。逐字引句：`"m4_answers_passed": sum(1 for r in ans if r.get("passed"))`

- `major` — `scripts/scenario_probe.py:115`：例如 Bash 呼叫 `rg 'lumos search' CLAUDE.md` 只是在搜尋規則文字，正則仍會從引號後的 `lumos search` 命中，將未執行 lumos 的場次灌入 M2/M3；同類誤判也包含 `echo "lumos doctor"`。逐字引句：`LUMOS_CALL_RE = re.compile(r"(?:^|[\s;&|(`'\"/])lumos\s+[a-z]")`

- `major` — `governance/eval/ablation_lumos_first.py:106`：窗口已有 49 場、兩個 worker 同時啟動各含 3 runs 的工作時，兩者都會在任何新結果落地前讀到 49 並放行，最後跑到 55 場；檢查既沒有鎖／reservation，也沒有判斷 `current + n`。逐字引句：`if max_per_window and runs_in_window(out_dir) >= max_per_window:`

- `major` — `governance/eval/ablation_lumos_first.py:57`：舊結果若只保存前 12 個 calls、原始 `ever_lumos=True` 來自第 13 個呼叫，backfill 會無條件覆寫成 `False`；雖標了 `calls_truncated`，`is_valid()` 和統計仍照常納入，直接壓低 M2 並把該場排除於 M3。逐字引句：`r["ever_lumos"], r["first_lumos_idx"] = ever, idx`
