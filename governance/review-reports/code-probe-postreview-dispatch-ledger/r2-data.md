severity: major

severity: major  
blocking: 是  
引句:「if (type(n_calls) is not int or n_calls < 0 or (calls is not None and not isinstance(calls, list))」  
file: `governance/eval/ablation_lumos_first.py:132`  
file: `governance/eval/ablation_lumos_first.py:106`  
重現: 寫入 `{"arm":"with","results":[{"id":"a","passed":true,"reason":["儀器例外: timeout"],"n_calls":0,"calls":[]}],"fatal":false,"inconclusive":false,"skills_health_bad":[]}` 後呼叫 `collect_skills_health`、`load_results`、`_arm_stats`；實測得到 `health=[]`、`n=1`、`m1_passed=1`、`missing=0`。翻紅斷言應要求健康掃描有錯且有效分母為 0。  
影響: `reason` 是決定儀器例外是否排除的計分欄位，但新增 schema 檢查未限制其型別；`is_valid` 又先轉成字串，錯型舊資料會被當成有效成功列，污染 M1/M4、缺場與補跑判定，違反 S13。

總結: 最嚴重 severity: major；blocking: 1
