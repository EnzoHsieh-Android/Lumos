severity: major  
blocking: 是  
引句:「return not r.get("limit_hit") and not str(r.get("reason", "")).startswith("儀器例外")」  
file: `governance/eval/ablation_lumos_first.py:106`  
finding: 舊結果驗證未檢查 `reason` 型別，卻在計分時先轉成字串。攻擊者可注入 `reason: ["儀器例外: injected"]`，繞過儀器例外排除並把偽造的 `passed: true` 算成有效通過，違反 S13。falsey 的錯型 `fatal: []`、`skills_health_bad: {}` 以及任意型別 `inconclusive` 也會通過驗證。  
最小重現: 對該列呼叫 `invalid_batch_evidence(d, "with")` 實得 `[]`，`is_valid(backfill_limit(row))` 實得 `True`，`_arm_stats([row], ["a"], 1)` 實得 M1 `1/1`；加入 `assert invalid_batch_evidence(d, "with")` 即翻紅。  
影響: 損壞或刻意製作的舊 JSON 可污染純合併報表，偽造通過率並抵掉缺場。

severity: minor  
blocking: 否  
引句:「or any(ord(ch) < 32 or ord(ch) == 127 for ch in qid))」  
file: `governance/eval/ablation_lumos_first.py:69`  
file: `scripts/scenario_probe.py:954`  
finding: 題號驗證只拒絕 ASCII C0 與 DEL，仍接受 C1 控制字元及 Unicode 格式控制字元，未完整符合 S12。這些值之後會原樣印到終端與報表，可造成顯示或方向偽裝。  
最小重現: `a\u0085spoof` 與 `a\u202espoof` 對現行判式均得 `rejected=False`，但 `str.isprintable()` 均為 `False`。

S11、S14及路徑、符號連結、檔案權限、越界與鎖繞過：已讀，無凍結差異 finding。  
LUMOS-IMPACT: `2db51cc4..HEAD`  
總結：最嚴重 severity major；blocking 1 條。
