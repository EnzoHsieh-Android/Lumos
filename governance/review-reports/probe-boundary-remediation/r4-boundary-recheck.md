severity: major
# r4 邊界席原三條續驗報告

續驗版本：`1b9d8fe1`；只複查原席自己提出的三條，不作全新一輪廣審。

原 Finding 1（舊 schema 事故檔重用）：修補已折入。舊 `skills_health_bad` 與逐場 `fatal` 兩種實際格式均得到 `loaded=0、needed=1、merged_n=0、poisoned=True`。已讀，無 finding。

原 Finding 2（已知 fatal 檔先補跑、後掃描）：修補已折入。相同重現得到 `jobs=[]、rc=3`，未呼叫 `run_job`。已讀，無 finding。

原 Finding 3：語法完整但缺健康欄位的部分輸出仍被當成有效結果。修補只驗頂層可下標、`results` 是 list、列元素是 dict，沒有要求本版 producer 必寫的 `fatal`、`inconclusive`、`skills_health_bad` 至少提供可證明健康檢查完成的訊號；新增測試的 `valid` fixture 也正好省略全部三欄，將此行為鎖成綠燈。`run_job` 呼叫的是同 checkout 的當前 producer，因此這裡不需要為舊輸出格式放寬。

severity: major

blocking: 是。

引句：「if not isinstance(d, dict) or not isinstance(rows, list) or not all(isinstance(x, dict) for x in rows):」

file: `governance/eval/ablation_lumos_first.py:182`、`governance/eval/ablation_lumos_first.py:187`、`scripts/test_lumos.py:37624`。

最小重現：stub 子程序回 `returncode=1`，寫入合法 JSON `{"arm":"with","results":[{"id":"a","passed":false,"reason":"ordinary failure"}]}`，不帶三個批次健康欄位；真 `run_job` 實測 `stop=False`，狀態為 `rc=1 有效 1/1`。同樣 rc=1 的缺檔與截斷 JSON 已會 `stop=True`，所以剩餘破口只在「語法完整、schema 不完整」這一型。

驗證：`python3.14 scripts/test_lumos.py -k probe_boundary_review4` 為 9 passed、0 failed；其中前兩條確實轉綠，第三條的 incomplete-schema 反例未被覆蓋。

總結：最嚴重 severity major，blocking 1 條。
