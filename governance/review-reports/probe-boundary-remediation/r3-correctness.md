severity: major

Finding 1 — 最終健康檢查失敗仍被下游合併為有效樣本

severity: major
blocking: 是
引句:「r2 最終健康檢查讀不到仍寫不可判紀錄」
file: `scripts/scenario_probe.py:1125`
file: `scripts/test_lumos.py:37502`
file: `governance/eval/ablation_lumos_first.py:72`
file: `governance/eval/ablation_lumos_first.py:92`
最終健康檢查拋錯時，探針雖寫 `fatal=true`、`inconclusive=true` 並回 3，卻把 `bad` 設為空、保留每場 `reason="ok"` 與有效分母。下游 `load_results`/`is_valid` 只按逐場 reason，`collect_skills_health` 只按 `skills_health_bad`，於是仍把整批不可判資料合併，且 `needed` 判為無須補跑。

最小重現：兩題 runner 都成功，`global_skills_health` 依序回 `[]`、`[]`、最終拋 `OSError`。輸出 rc3、fatal/inconclusive true，但 `valid_total=2`、兩列 `is_valid=True`、`needed(a)=0`、`collect_skills_health=[]`。新增測試只驗 fatal/inconclusive 和列數，未驗真實消費端合併。

中途健康檢查拋錯的停批：已讀，無 finding。linked worktree、實際提交身分、清理與 keep/重試：已讀，無 finding。表態 `py-eventloop na`：同步 CLI 無事件迴圈，無 finding。`Systems/codex-harness`、`Systems/測試假綠形態` 與計劃：本 finding 命中不可判分母與測試未覆蓋消費端。

驗證：凍結 patch SHA256 `cdbfac731efbea0d59b566865cc2cf1c307954e515f038202c976870274e21e5`；`probe_boundary_` 45 passed，但上述情境仍重現。實驗只用臨時資料。
