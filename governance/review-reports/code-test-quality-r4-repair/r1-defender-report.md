severity: major

## A1 — HIT，維持 major

severity: major
blocking: true
引句:「if proc is not None:」
file: `governance/eval/test_quality_handbook.py:249`

`scripts/test_quality.py` 仍只在 `proc.returncode is None` 時清理程序群。launcher 已退出並留下同群 worker 時，`proc.wait()` 已把 return code 設成 1，finally 因此跳過 `killpg`。這是既定產品責任內的 bug：可信測試 runner 正常使用 worker 不等於惡意逃逸。最小可驗收修法是讓 `terminate_group()` 不論 launcher return code 都先嘗試 `killpg(proc.pid, SIGKILL)`，再等待 launcher；新增 CLI 控制驗證 rc1 launcher 留下的同群、關閉管線 worker 會在返回前停止。

## SEC-R4-1 — MISS major；觀察成立，但不構成所報安全缺陷

severity: clean
blocking: false
引句:「`os.killpg(proc.pid, signal.SIGKILL)`」
file: `governance/eval/test_quality_handbook.py:251`

descendant 自己以 `start_new_session=True` 建立新 session 後確實可離開原程序群，但這不違反現有保證。圖譜明定清理「自己建立的 POSIX 程序群」，且不宣稱一般 Python 沙盒。主動 setsid 逃逸後，父程序無法只靠可攜 POSIX process-group API 保證追殺全部後代；需要 cgroup、job object、subreaper 或平台專用程序樹機制，超出現有產品合約。報告所稱 PermissionError 未能重現。

總結：最嚴重 severity 為 major，blocking 1 條。
