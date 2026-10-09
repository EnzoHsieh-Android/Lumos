severity: major

B1: HIT

severity: major
blocking: true
引句:「cwd=root, env=env, capture_output=True, text=True, timeout=40」
file: `scripts/test_quality_semgrep.py:72`

縮短 timeout 的重現確認三種路徑都會留下同群 worker：launcher 真逾時；launcher 已退出但 worker 繼承管線時誤報 timeout；launcher 已退出且 worker 關閉管線時回 scanned 但 worker 仍存活。現況沒有 start_new_session，無法安全用 launcher PID 殺群。這屬既有可信 backend 責任，因 worker 未主動 setsid 逃逸。最小修法是改用 Popen/start_new_session，所有出口 finally 清群；parent 已退出但 descendant 持管線時要先判 parent 狀態，避免誤報 timeout。

必要控制涵蓋成功退出的繼承/關閉管線 worker、真 timeout 與非零退出。

總結最嚴重 severity: major；blocking: 1。
