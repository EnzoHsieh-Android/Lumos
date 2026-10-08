severity: major
# r4 邊界席原報告

凍結快照 SHA-256：`aba46af10824bc3bf4f9f1a49ed81c8971be92012aba4d63da5541e4f9b5eb42`。

Finding 1：舊 schema 的事故檔仍會抵掉缺場並進統計。r4 只用新頂層 `fatal` 排除整檔；真實舊格式只有 `skills_health_bad`，或只有 `inconclusive` 加逐場 `fatal`。前者仍被 `load_results` 收入，後者甚至不會被 `collect_skills_health` 標記。

severity: major
blocking: 是。

引句：「整批 fatal 的檔案即使逐場 reason=ok 也不可計分或抵掉缺場。」

file: `governance/eval/ablation_lumos_first.py:91`、`governance/eval/ablation_lumos_first.py:112`。

最小重現：建立舊格式檔 `{"arm":"with","results":[{"id":"a","passed":true,"reason":"ok"}],"inconclusive":true,"skills_health_bad":[["broken","/tmp/..."]]}`，不放頂層 `fatal`；真函式輸出 `loaded=1, needed(a)=0, merged_n=1, poisoned=True`。另一個舊清理失敗檔含先前成功列、逐場 `fatal:true`、頂層 `inconclusive:true`、空 `skills_health_bad`，實測 `needed(a)=0, merged_n=1, poisoned=[]`。兩種都違反整批事故不得重用。

Finding 2：已有 fatal 檔時，補跑先啟動，失效掃描後執行。`load_results` 排掉 fatal 後讓 `needed` 產生工作，但 `collect_skills_health` 要等 executor 全部完成才呼叫，因此已知健康或清理不可判的輸出目錄仍會先跑模型。

severity: major
blocking: 是。

引句：「這裡不管走不走 merge_only 都掃 out_dir 一次。」

file: `governance/eval/ablation_lumos_first.py:301`、`governance/eval/ablation_lumos_first.py:323`。

最小重現：輸出目錄先放 `fatal:true, inconclusive:true, results:[a 成功]`，以一題、一次、`arms=with` 呼叫真 `main`，只 stub `run_job` 記錄呼叫。實測在掃出 poison 前已排入 `jobs_started=[("with","a",1)]`，最後才得到 `skills_health_poisoned`，且回傳碼仍為 0。

Finding 3：`run_job` 對缺檔、部分 JSON 或異常退出碼不會停批；未知健康狀態下仍放行後續工作。它只對 rc=3 或成功解析出的旗標設 `stop`，而 producer 若在最終健康檢查或寫檔前非預期崩潰，會是 rc=1／訊號退出並留下缺檔或半檔。

severity: major
blocking: 是。

引句：「探針回 3 或結果檔標了 skills 事故:設停止旗標,其餘 worker 與後續工作不再派」

file: `governance/eval/ablation_lumos_first.py:164`、`governance/eval/ablation_lumos_first.py:172`。

最小重現：stub `subprocess.run` 回 `returncode=1`，分別不產出結果檔及只寫 `{"results":[`，傳入真 `threading.Event` 呼叫 `run_job`。兩次皆得到 `stop=False`、狀態 `rc=1 有效 0/1`；executor 的下一個工作因此仍會執行。

runner 拋錯後立即健康檢查、健康檢查拋錯轉 fatal、逐場清理失敗及批次基線清理後再做最終健康檢查：已讀，無 finding。

總結：最嚴重 severity major，blocking 3 條。
