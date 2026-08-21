C1. `slim/install.sh` 用 `$(cd "$(dirname "$0")" && pwd)` 定位交付包，並先手捲 symlink 解析迴圈（macOS 無 `readlink -f`，逐層 readlink 接回所在目錄再判斷是否還是 symlink） | 預期驗證點: slim/install.sh 開頭定位邏輯

C2. 安裝流程檢查 `scripts/lumos` 與 `skills/lumos-project-notes` 存在，找不到即 rc=2 | 預期驗證點: slim/install.sh（或 Python 版 slim/install.py）套件完整性檢查段

C3. 2026-08-01 Task 11 新增「注入目標守衛」，動手前先過兩層檢查：①不像專案根（無 `.git`、無 `docs/*-knowledge/`、無既有 `CLAUDE.md`，或 `$(pwd)`==`$HOME`，用 `pwd -P`/`cd -P` 解 symlink 後比對）→拒絕；②目標同時具備 `skills/lumos-project-notes/`+`scripts/lumos`+`scripts/templates/graph-discipline.md` 三件套→拒絕；兩者皆 rc=2 且不建目錄不動任何檔案 | 預期驗證點: t_slim_install_guard_rejects_empty_dir, t_slim_install_guard_rejects_home_dir, t_slim_install_guard_rejects_source_repo

C4. `--here` 旗標可繞過守衛第①②層，但第③層（印出目標絕對路徑與將修改路徑）一律照印、不受影響 | 預期驗證點: t_slim_install_guard_here_bypasses

C5. 安裝時把 bin 的 sha256 寫入身分證 manifest `~/.local/share/lumos-slim/manifest.json`（含 `bin_sha256` 欄位），且不依賴 `~/.lumos-slim` 是否存在 | 預期驗證點: t_slim_uninstall_direct_install_restores_claude_md（manifest 提供比對基準）

C6. `skills/lumos-project-notes` 是用 `cp -R` 實體複製到 `~/.claude/skills/`，而非 symlink | 預期驗證點: slim/install.sh（或 install.py）skill 複製段

C7. CLAUDE.md 注入使用 sentinel 標記 `<!-- LUMOS-SLIM:START/END -->`；若專案已有完整版 `LUMOS:GRAPH-DISCIPLINE` 區塊，原地整段取代且 sentinel 以外既有內容必須 byte-equal 保留；沒有完整版區塊則插在檔首「# 標題」之後（無標題插最前面）；CLAUDE.md 不存在則直接建立 | 預期驗證點: t_slim_install_no_project_touch, t_slim_install_replaces_full_discipline_block_in_place

C8. CLAUDE.md 注入是冪等的：重跑安裝器只更新自己 sentinel 之間內容，不疊出第二塊，備份標記（FULL-BACKUP）不會被重新編碼或洗成 NONE | 預期驗證點: t_slim_install_claude_md_idempotent, t_slim_install_backup_survives_idempotent_reinstall

C9. 完整版區塊被取代前，原文（含其自身 sentinel）先以 base64 編碼備份進精簡版區塊的 HTML 註解 `<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->`，解碼後須與原文逐位元組相同 | 預期驗證點: t_slim_install_replaces_full_discipline_block_in_place

C10. bin/skill 目標已存在且未帶 `--force` 時 rc=2 拒絕；帶 `--force` 時 bin 直接覆寫（manifest 仍照寫），skill 目錄先備份成 `.bak.<timestamp>` 才覆寫 | 預期驗證點: slim/install.sh（或 install.py）碰撞語意段落

C11. `install` 的 `main()` 採「遇錯早退」語意（`rc != 0` 就 return），與 `uninstall.sh`「各步互不阻擋」刻意相反；`_main_guarded()` 只在最外層接 `OSError` 印可行動訊息 + rc=2，控制流不變 | 預期驗證點: t_slim_install_filesystem_error_reports_cleanly_without_traceback

C12. `_merge_claude_md_text()` 讀取非合法 utf-8 的既有 CLAUDE.md 時會拋 `UnicodeDecodeError`（繼承自 `ValueError`），已補獨立 except 分支處理並斷言該檔案位元組原封不動 | 預期驗證點: t_slim_install_non_utf8_claude_md_reports_cleanly

C13. Task 13 將 `slim/install.sh` 全部邏輯（原 293 行純 bash）改寫成 `slim/install.py`（Python stdlib only），`install.sh` 改版後僅約 35 行，只做①手捲 symlink 解析定位套件目錄 ②挑 `python3`/`python` 轉發參數執行 `install.py`；同時新增 `slim/install.ps1` 作為 Windows 對應薄殼 | 預期驗證點: slim/install.sh, slim/install.py, slim/install.ps1 行數與職責分工

C14. Windows shim 呼叫的直譯器名稱不得寫死字面 `python`，需用 `_pick_windows_interpreter()`（依序 `shutil.which("python3")`/`shutil.which("python")`）偵測寫進 `.cmd` shim，兩者都找不到才退回 `"python"` | 預期驗證點: t_slim_install_windows_shim_does_not_hardcode_python_when_only_python3_available

C15. Windows 路徑下全域指令的碰撞偵測必須同時檢查 `lumos`（`dst_script`）與 `lumos.cmd`（`dst_shim`）兩者是否存在，僅看前者會導致單獨殘留的 `lumos.cmd` 在非 `--force` 重裝時被無聲覆寫 | 預期驗證點: t_slim_install_windows_collision_detects_orphan_cmd_shim

C16. 測試套件宣稱 225 checks 全綠，指令為 `python3 scripts/test_lumos.py -k slim` | 預期驗證點: scripts/test_lumos.py -k slim 執行結果
