severity: major

finding K1: 子程序少回結果列仍刪除 pending，違反 S11 的完整驗證要求

severity: major

blocking: 是

引句:「or any(x.get("id") != qid for x in rows) or len(rows) > n」

file: `governance/eval/ablation_lumos_first.py:273`

最小重現（已重現）：mock `subprocess.run` 在收到 `--runs 2` 時只寫一筆合法結果並回傳 rc0，再呼叫 `run_job(..., n=2)`；翻紅斷言為 `pending` 仍存在、`collect_skills_health()` 非空且 `needed(...) == 2`。實際得到 `pending=[]`、`health=[]`、`needed=1`，部分資料被當成健康結果，窗口帳也會少算已派出的場次。

finding K2: 五小時窗口只計最終結果列，完全漏算撞上限後的重試呼叫

severity: major

blocking: 是

引句:「最近 hours 小時內落地的探針場次(含撞上限的):算帳號窗口用掉多少。」

file: `governance/eval/ablation_lumos_first.py:207`

最小重現（已重現）：建立一筆結果，內含兩筆 `retry_attempts` 與一筆最終結果，代表窗口內實際啟動三次模型；翻紅斷言為 `runs_in_window(out_dir) == 3`，實際回傳 `1`。因此即使 `max_per_window=2` 已超額，下一工作仍會得到剩餘額度並再次啟動模型；S12 的窗口限額只限制最終列數，沒有限制 CLI 所承諾「含撞上限」的實際嘗試數。

多進程互斥、父死子活後第二批拒收、相對輸出落點、鎖與檔案描述元釋放：已讀,無 finding。

總結：最嚴重 severity: major；blocking: 2 條。
