severity: major

ID: SEC-R4-1 程序群清理可被子程序以新 session 逃逸
severity: major
blocking: true
引句:「`os.killpg(proc.pid, signal.SIGKILL)`」
file: `governance/eval/test_quality_handbook.py:251`

最小安全重現：launcher 以 `start_new_session=True` 再啟動長跑 worker 後 rc1；`model_command()` 返回且 `returncode == 1` 時，逃到新 session 的 worker 仍存活。若逃逸 worker 保留原管線，macOS 上 timeout 路徑的 `killpg` 還可能拋出未捕捉的 `PermissionError`，取代原本的結構化 timeout 結果。這會讓模型命令在錯誤或逾時後繼續消耗資源。

symlink／路徑：已讀；來源先讀入私人暫存快照，Semgrep 只接觸快照，無 finding。

外部 Semgrep JSON：已讀；finding 形狀、規則、快照路徑、掃描清單、錯誤、退出碼及行號上下界皆採拒收，無 finding。

bundle digest／TOCTOU：已讀；驗證的是讀入的 `raw`，執行時也直接 `compile(raw)`，未重新從可替換路徑載入，無 finding。

總結: 最嚴重 severity major，blocking 1。
