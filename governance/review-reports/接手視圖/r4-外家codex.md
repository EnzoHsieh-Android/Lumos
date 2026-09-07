severity: blocker

驗收  
#6 通過:`is_write` 同時檢查字串 mode 與數字 flags，且 fd 路徑保守記違規；四個指定案例皆會被記錄。scripts/test_lumos.py:30743  
#7 通過:允許域只取 realpath 後的 stdlib/platstdlib 並以 commonpath 驗邊界；`sys.executable`、site-packages、`python3.14-foo` 鄰居皆不放行。scripts/test_lumos.py:30730

### 8 / blocker / `os.stat` 可讀取外部檔案中繼資料而完全不留稽核事件
引句:「★匯入 hook 沒有任何外部動作:不開程序、不連網、不讀 hook 與標準庫以外的檔、不改檔系統★」
位置:scripts/test_lumos.py:30811
為什麼是問題:把 `os.stat("/etc/passwd")` 放進 hook 頂層即可觀察外部檔案；實測 Python audit hook 收到零事件，因此 `events == []`，探針判綠。
建議:匯入期間包裝 `os.stat` 等無 audit event 的檔案系統讀取原語，對非 hook／stdlib 路徑記違規。

總結:#6、#7 已折實，但新發現一條可重現的外部讀取繞過；實際開過 governance/review-reports/接手視圖/r3-外家codex.md、governance/review-reports/接手視圖/r3-intake.md、governance/review-reports/接手視圖/r4-snapshot.diff、scripts/test_lumos.py、scripts/hooks/claude/check-graph-sync.py、docs/lumos-toolchain-knowledge/Projects/接手視圖_計劃.md、/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md。
