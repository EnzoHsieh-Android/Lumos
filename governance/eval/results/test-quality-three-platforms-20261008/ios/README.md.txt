# ios 原生測試品質消費專案

需求與界線見 [REQUIREMENTS.md](REQUIREMENTS.md)、重跑入口見 [實驗手冊](../README.md)。

由根目錄執行 `python3 run_experiment.py ios`；加 `--semgrep /absolute/path/to/semgrep` 執行選配靜態候選掃描。

請先按手冊準備固定SDK與平台；原生報告與退出碼保留在每次 artifacts/run-*/各phase/native。Counterexamples 是故意不當的對照，不由綠燈授予品質。
