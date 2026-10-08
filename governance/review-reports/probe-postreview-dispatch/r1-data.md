severity: major

finding 1：啟動例外只留在會被覆寫、又被預掃刻意排除的 `summary.json`；下一次 `--merge-only` 或重跑會把事故洗成乾淨結果。  
severity: major  
blocking: 是  
引句:「整批應停止下一題、留下失效 summary 並退出 3；不能讓例外略過批次收尾。」  
file: `governance/review-reports/probe-postreview-dispatch/r1-snapshot.md:97`  
file: `governance/eval/ablation_lumos_first.py:117`  
file: `governance/eval/ablation_lumos_first.py:351`  
file: `governance/eval/ablation_lumos_first.py:361`  
原因：失效且沒有結果檔時，唯一事故標記是記在 summary 的合成 `poisoned`；但 `collect_skills_health` 明確跳過 summary，而下一次執行又直接覆寫 summary。這違反檔頭宣告的「輸出一檔一次嘗試、永不覆蓋」資料追溯語意，也讓 merge-only 把事故歷史消失。修法需為每次失敗留下不可覆寫、可被預掃辨識的 attempt tombstone，或讓預掃納入並保留前次失效摘要。  
最小重現：以 monkeypatch 令第一次 probe 回 `rc=1` 且不產生結果檔，`main()` 得到 `rc=3`、summary 有 `skills_health_poisoned`；同一 out-dir 第二次成功重跑時，實測得到 `rc=0`、`skills_health_poisoned=[]`，目錄只剩第二次的正常 attempt JSON。把第二次改成 `--merge-only` 也會由相同排除路徑覆寫事故摘要。

finding 2：S9 只規定拒絕 `workers > 1`，沒有拒絕零或負數，也沒有要求在改寫 meta/summary 前驗參數；無效輸入可崩潰並留下看似有效的舊摘要。  
severity: major  
blocking: 是  
引句:「缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕，預設僅開一路。」  
file: `governance/review-reports/probe-postreview-dispatch/r1-snapshot.md:98`  
file: `governance/eval/ablation_lumos_first.py:299`  
file: `governance/eval/ablation_lumos_first.py:313`  
file: `governance/eval/ablation_lumos_first.py:322`  
file: `governance/eval/ablation_lumos_first.py:339`  
file: `scripts/test_lumos.py:37718`  
原因：`argparse` 接受任意整數；`ThreadPoolExecutor(0)` 才拋 `ValueError`，此時 `meta.json` 已經改寫，而既有 summary 原封不動。現有新增測試只驗 `workers=2`、新目錄及 runner 未啟動，抓不到零值與「拒絕前已污染輸出」；若把拒絕放在現有 meta 寫入之後，同樣會留下 meta/summary 世代不一致。dispatch 模式應只接受 `workers == 1`，並在建立或改寫 out-dir 內容前驗證；`--merge-only` 不會派工，應另有相容性測試，避免被這條限制誤擋。  
最小重現：先在暫存 out-dir 寫入 `summary.json={"old":"clean"}`，執行 `ablation_lumos_first.py --workers 0 --runs 1 --arms with ...`；實測退出碼 1、拋 `ValueError: max_workers must be greater than 0`，舊的 clean summary 仍存在，而 meta 已被新執行改寫。

S8 將 `OSError`／未來的 `TimeoutExpired` 收成批次失效，以及 S9 採單路派工並保留恢復並行的競速驗證條件：已讀，無其他 finding。Issue 對直接寫檔可能留下半檔的風險、官方依據與重驗入口：已讀，無獨立新增 finding；但 finding 1 表示 summary 目前不能兼任唯一事故憑證。

總結最嚴重 severity: major；blocking: 2 條。
