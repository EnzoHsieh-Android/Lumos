severity: major

severity: major  
blocking: 是  
引句:「or any(x.get("id") != qid for x in rows) or len(rows) > n」  
file: `governance/eval/ablation_lumos_first.py:273`  
S11 違規且綁定測試假綠：驗證只拒絕 `len(rows) > n`，成功退出但少列仍於 `pending.unlink()` 移除未完成標記。最小重現：mock `subprocess.run` 在要求 `n=2` 時只寫一列並回 rc=0；實測得到 `pending=0 health=[] accepted=1`。加入 `len(rows) != n` 斷言即可在現版翻紅。影響是截斷或漏寫的成功外觀結果被下次合併採信，不再保持整批失效；現有 `t_probe_boundary_formal_dispatch_fail_closed` 21 項全綠但未覆蓋 rc0 部分輸出。

severity: major  
blocking: 是  
引句:「if d.get("fatal") or any(isinstance(r, dict) and r.get("fatal") for r in rows)」  
file: `governance/eval/ablation_lumos_first.py:139`  
S13 違規：舊檔 `fatal` 只用 truthiness，未驗證精確布林型別。最小重現：寫入 `{"arm":"with","results":[{"id":"a","passed":true}],"fatal":0,"inconclusive":false,"skills_health_bad":[]}`；實測 `collect_skills_health=[]` 且 `load_results()["with"]` 接受一列。斷言該檔必須被標失效並拒絕計分會在現版翻紅。現有測試只測 `passed`、`n_calls`、`answer_content_ok`、`limit_hit` 的錯型，漏掉頂層健康欄位。

severity: minor  
blocking: 否  
引句:「if not isinstance(meta, dict):」  
file: `governance/eval/ablation_lumos_first.py:396`  
S14 未完整落實：merge-only 只驗 meta 頂層是 dict，空字典仍被視為可用來源。最小重現：`meta.json` 寫 `{}` 後純合併，實測標題為「記錄日期 None;當次 Claude CLI ?」，沒有規格要求的「來源日期未知／來源版本未知」。現有測試只覆蓋完整歷史 meta 的保留，未覆蓋缺欄或錯型欄位。

總結：最嚴重 severity major，blocking 2 條。
