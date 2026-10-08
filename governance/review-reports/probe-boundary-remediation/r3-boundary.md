severity: major

Finding 1 — runner 拋錯跳過當場健康檢查

severity: major
blocking: 是
引句:「health = global_skills_health()」
file: `scripts/scenario_probe.py:1027`
file: `scripts/scenario_probe.py:1031`
模型執行後若 runner 在逐字稿讀取或結果解析拋例外，流程直接跳到外層 except，未執行當場 `global_skills_health()`。若模型已損壞全域 skills，下一題可先開始，直到較後的健康檢查才發現污染。

最小重現：臨時 Git repo 放 a、b 兩題，a runner 模擬模型後解析例外，健康檢查回報壞連結。實跑 `runner_calls=["a","b"]`、最後 rc3；第二題已在檢出損壞前呼叫。每次模型嘗試後的健康檢查須不受 runner 成敗影響，且在下一題前完成。

Git worktree 外指、Git 身分／trace、模型可寫來源、拒絕與副本清理：已讀，除上述外無 finding。
