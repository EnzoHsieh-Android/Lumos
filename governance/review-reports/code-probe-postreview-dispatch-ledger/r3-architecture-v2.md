severity: major

severity: major

blocking: 是

引句:「for p in _result_json_files(out_dir):」

file: `governance/eval/ablation_lumos_first.py:218`

finding: 五小時額度只以已升格的正式 JSON 為權威來源；子程序異常退出時，父程序把正式檔改寫成沒有逐場紀錄的 tombstone，而實際嘗試數只留在候選檔。依既定恢復流程歸檔 fatal、candidate、pending 後，這些嘗試便從窗口帳消失。下一批重新取得完整額度，形成另一套「可採信結果帳」兼任「用量帳」的錯誤權威來源，違反 S18 的實際呼叫消耗額度要求。

最小重現（已執行）：

1. 模擬子程序執行三次模型，候選列含兩筆 `retry_attempts`，最後回傳 rc=3。
2. `run_job(..., max_per_window=5)` 留下 fatal JSON、candidate、pending；此時 `runs_in_window()` 已回傳 `0`。
3. 按 marker 的恢復政策歸檔三檔後再次呼叫 `run_job`，新子程序收到的仍是 `--max-attempts 5`，預期應只剩 `2`。

實際輸出：
```text
first_max_attempts 5
first_window_count 0
first_health_count 3
after_archive_health_count 0
second_max_attempts 5
```

修正方向：由父層另存不可因事故歸檔而消失的嘗試額度帳；若拿不到可信的實際次數，異常退出至少保守扣除本次授予子程序的完整額度。正式計分結果不可同時充當窗口用量的唯一來源。

候選檔升格與同層原子寫入慣例：已讀，無 finding。

探針與派工器的其餘分層、S11–S17：已讀，無 finding。

錯誤處理與既有工具寫法：已讀，無 finding。

總結：最嚴重 severity major，blocking 1 條。
