severity: major

驗收  
#5 未通過:稽核鉤子仍漏報 `os.open` 寫入，且允許清單涵蓋 site-packages 與整個 Python prefix。scripts/test_lumos.py:30729

### 6 / major / `os.open` 的數字 flags 可繞過寫入檢查
引句:「open 只准讀 hook 自己的原始碼與標準庫」
位置:scripts/test_lumos.py:30743
為什麼是問題:`os.write(os.open(__file__, os.O_WRONLY), b"X")` 放進 hook 頂層時，audit 的 `open` 參數是 `(path, None, flags)`；探針只檢查 `args[1]`，忽略 `args[2]`，因此把寫入當成 `"r"`，而 hook 路徑又在允許清單內，最終 `events == []`。
建議:依 audit event 的第三個 `flags` 用 `os.O_ACCMODE` 判讀，任何非 `O_RDONLY` 都記為違規。

### 7 / major / 標準庫允許清單實際涵蓋 site-packages 與整個 prefix
引句:「paths.get("purelib"), paths.get("platlib"), sys.base_prefix, sys.prefix」
位置:scripts/test_lumos.py:30729
為什麼是問題:`open(sys.executable, "rb").read(1)` 放進 hook 頂層即可讀標準庫以外的執行檔而不違規；本機 `sys.prefix` 是 Python framework 根目錄，且 `purelib/platlib` 明確是 site-packages，再配合無路徑邊界的 `startswith`，允許面遠大於宣稱。
建議:只允許 realpath 後的 `stdlib/platstdlib`，用 `os.path.commonpath` 驗證目錄邊界，移除 `purelib`、`platlib`、`sys.prefix` 與 `sys.base_prefix`。

總結:#5 尚未折實；同信任域與不動 hook 的範圍刀可以接受，但稽核鎖仍有兩個可直接重現的繞過，且只需修測試探針；實際開過 governance/review-reports/接手視圖/r2-外家codex.md、governance/review-reports/接手視圖/r2-intake.md、governance/review-reports/接手視圖/r3-snapshot.diff、scripts/test_lumos.py、scripts/hooks/claude/check-graph-sync.py、docs/lumos-toolchain-knowledge/Projects/接手視圖_計劃.md、/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md。
