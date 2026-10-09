severity: major

ID: B1
severity: major
blocking: true
引句:「CLI capture 與 handbook model runner 都建立獨立 POSIX 程序群，必須採同一項返回前清理政策」
file: `scripts/test_quality_semgrep.py:72`

Semgrep 是外部可執行程序，但仍用 `subprocess.run`，沒有建立獨立 POSIX 程序群，也沒有返回前清理 descendants。launcher 啟動繼承 stdout/stderr 的 worker 後退出或逾時時，Python 只停止直屬程序；worker 仍可存活，且會讓已退出的 launcher 被誤判成 timeout。最小重現以 fake Semgrep 啟動長跑 worker、寫 pidfile、輸出合法 JSON 後退出；縮短 timeout 後 `scan` 回 timeout 且 worker 仍存活。修復應沿既有 runner 使用 Popen/start_new_session，讓各出口統一清理。

已知 global --vault cwd 問題未重報；其餘程序、JSON、行號與 executable 邊界已讀，無 finding。

總結最嚴重 severity: major；blocking: 1。
