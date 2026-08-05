- **major** — `governance/eval/canary_calibration.py:64`  
  具體失敗場景：校準帳超過 500 行後，即使使用 `--no-log` 試跑，也會先以 `write_text()` 原地截斷為最近 400 行，違反 `--no-log` 不寫入與 append-only 合約；若另一程序在 `read_text()` 後、`write_text()` 前追加紀錄，新紀錄也會被覆寫遺失。此寫法沒有 tmp→自驗→atomic，程序中斷時還可能留下截斷或半寫檔。  
  引句：「# dsp_log_compact: 累積帳超過 500 筆自動壓實(保留最近 400,防無限長胖)」

max severity: major
