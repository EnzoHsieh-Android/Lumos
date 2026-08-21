C1. 卸載入口為 `curl -fsSL <raw-url>/uninstall.sh | bash`，或裝好後直接跑 `~/.lumos-slim/uninstall.sh` | 預期驗證點: slim/uninstall.sh 檔案存在且可作為入口腳本

C2. 五個清理步驟（①bin ②skill目錄 ③~/.lumos-slim ④CLAUDE.md sentinel ⑤manifest）各自獨立判斷/執行、互不阻擋，不再用 `exit` 讓某一步中止其餘步驟 | 預期驗證點: slim/uninstall.py 各步驟函式呼叫處無提前 exit/return 中止全流程；t_slim_uninstall_bin_refusal_does_not_block_claude_md_restore

C3. 步驟①移除 `~/.local/bin/lumos` 前，比對基準優先讀取 install.sh 寫入的 `~/.local/share/lumos-slim/manifest.json` 的 `bin_sha256` 欄位；manifest 給不出參照才退回讀 `~/.lumos-slim/scripts/lumos` 做比對 | 預期驗證點: slim/uninstall.py 讀取 manifest.json 的 bin_sha256 邏輯與 fallback 至 ~/.lumos-slim/scripts/lumos 的邏輯；t_slim_uninstall_refuses_foreign_bin

C4. 步驟②移除 `~/.claude/skills/lumos-project-notes/` 前，先 `mv` 成 `.bak.<timestamp>` 備份，不得直接 `rm -rf` | 預期驗證點: slim/uninstall.py 對 SKILL 路徑的處理呼叫 mv/rename 而非 rm -rf；t_slim_uninstall_backs_up_and_preserves_custom_files

C5. 步驟③移除 `~/.lumos-slim` 前需確認其內含 `scripts/lumos` 與 `install.sh` 兩個檔案才判定為本包裝、才 `rm -rf`，否則保留並印警告 | 預期驗證點: slim/uninstall.py 對 PKG 路徑的結構特徵檢查（scripts/lumos + install.sh 是否存在）

C6. 步驟④讀取執行目錄下 `CLAUDE.md` 中的 `<!-- LUMOS-SLIM:START -->`/`<!-- LUMOS-SLIM:END -->` sentinel 區塊；找不到視同未安裝放行；找到後檢查區塊內建的 `FULL-BACKUP` 標記，值為 BASE64 時 base64 解碼並位元組級還原該區塊回原位置，值為 NONE 時單純挖掉精簡版區塊本體 | 預期驗證點: slim/uninstall.py 中 `_restore_claude_md()` 函式對 FULL-BACKUP 標記的分支處理；t_slim_uninstall_removes_claude_md_block, t_slim_uninstall_direct_install_restores_claude_md

C7. CLAUDE.md 挖除/還原後若整檔內容變空，連同檔案本身一併刪除（還原成「本來沒這個檔案」的狀態），而不是留下一個空檔 | 預期驗證點: slim/uninstall.py `_restore_claude_md()` 對變空後的 unlink 分支

C8. 步驟⑤移除身分證 manifest 本身（`~/.local/share/lumos-slim/manifest.json`）與清空後的 `lumos-slim/` 父目錄；唯一資料相依：①/①b 任一份 bin 檔案因安全考量未被移除時，manifest 必須保留（不刪除）並印出保留原因 | 預期驗證點: slim/uninstall.py 步驟⑤邏輯；t_slim_uninstall_removes_manifest_when_bin_cleared, t_slim_uninstall_keeps_manifest_when_bin_refused

C9. 步驟⑤是否保留 manifest 的判斷必須查檔案系統實況 `dst_script.exists() or dst_script.is_symlink() or dst_shim.exists()`，不得用分支簿記（手動旗標）；且 shim（`lumos.cmd`）檢查僅在 `IS_WIN` 為真時才納入判斷 | 預期驗證點: slim/uninstall.py 中該實況查詢語句與 IS_WIN 條件；t_slim_uninstall_keeps_manifest_when_shim_remains, t_slim_uninstall_manifest_ignores_stray_cmd_on_posix, t_slim_uninstall_keeps_manifest_when_shim_is_broken_symlink

C10. manifest 父目錄（`lumos-slim/`）的清理是選配收尾，必須用獨立的 try/except 包裹，與 `unlink()` manifest 本身分開；`rmdir` 失敗只印一句警告、不升級 rc | 預期驗證點: slim/uninstall.py 中 manifest unlink 與父目錄 rmdir 分屬不同 try 區塊；t_slim_uninstall_manifest_parent_cleanup_is_best_effort

C11. `~/.local/bin/lumos.cmd`（Windows shim）的移除與 `~/.local/bin/lumos` 各自獨立判斷、各自執行，不巢狀在後者的 if 區塊內；shim 安全性判斷改用「內容是否符合 install.py 產生的固定樣板」（`SHIM_TEXT_RE` 正則），符合視為本包裝、可安全移除，不符合則拒絕移除（需 `--force`） | 預期驗證點: slim/uninstall.py 中 SHIM_TEXT_RE 定義與比對邏輯，讀取方式為 `read_bytes().decode()` 而非 `read_text()`；t_slim_uninstall_windows_orphan_cmd_shim_removed, t_slim_uninstall_windows_orphan_cmd_shim_foreign_content_needs_force

C12. rc 語意三段式：0=每一步都完成或本來就沒裝（含冪等 no-op）；1=至少一步基於安全考量主動跳過（bin 比對不符/基準缺失、~/.lumos-slim 內容不像本包）；2=真正的錯誤（sha256 工具缺失、CLAUDE.md 多個 sentinel、FULL-BACKUP base64/utf-8 解碼失敗、未捕捉例外炸穿等） | 預期驗證點: slim/uninstall.py 彙總報告與 rc 決定邏輯；t_slim_uninstall_bin_refusal_does_not_block_claude_md_restore 斷言 rc==1

C13. `_restore_claude_md()` 對 CLAUDE.md 的檔案系統寫入與讀取都必須各自包 `try/except`：寫入側包 `except OSError`，讀取側需將 `except OSError` 與 `except UnicodeDecodeError` 分開接（`UnicodeDecodeError` 繼承 `ValueError` 不是 `OSError` 子類，不會被 `except OSError` 攔到），任一步驟例外都不應阻擋後續步驟⑤（manifest）執行 | 預期驗證點: slim/uninstall.py `_restore_claude_md()` 中 try/except OSError 與 try/except UnicodeDecodeError 的分離寫法；t_slim_uninstall_claude_md_write_failure_does_not_abort_remaining_steps, t_slim_uninstall_claude_md_read_failure_does_not_abort_remaining_steps

C14. sha256 比對邏輯：優先用 `command -v sha256sum`（Linux），否則退回 `shasum -a 256`（macOS），兩者都不可用時視同無法安全驗證、rc=2，但不中止其餘步驟（此為 bash 版行為；Python 版改用 stdlib `hashlib`，不再保留此分支） | 預期驗證點: 舊版 slim/uninstall.sh 中 sha256sum/shasum 判斷邏輯；新版 slim/uninstall.py 使用 hashlib 模組取代

C15. `slim/uninstall.sh` 已改版為僅 ~30 行的定位套件目錄＋挑直譯器＋轉發參數的殼，全部邏輯搬進 `slim/uninstall.py`（stdlib only）；另新增 `slim/uninstall.ps1` 承擔相同轉發角色，其中 `$ErrorActionPreference = "Stop"` 被搬進 `Invoke-Uninstall` 函式內部第一行，`Write-Error` 呼叫需加 `-ErrorAction Continue` 明確覆寫終止語意，收尾用 `$global:LASTEXITCODE = $LASTEXITCODE` 取代裸 `exit $LASTEXITCODE`（避免透過 `&` 呼叫鏈關閉呼叫端 session） | 預期驗證點: slim/uninstall.sh 行數與內容；slim/uninstall.py 存在且承載完整邏輯；slim/uninstall.ps1 中 Invoke-Uninstall 函式定義、Write-Error -ErrorAction Continue 用法、$global:LASTEXITCODE 賦值而非 exit；t_slim_ps1_write_error_noterminating_under_stop_preference, t_slim_ps1_scripts_avoid_session_killing_trailing_exit

C16. 卸載腳本全程只動 `$HOME` 下的 BIN（~/.local/bin/lumos、lumos.cmd）、SKILL（~/.claude/skills/lumos-project-notes/）、PKG（~/.lumos-slim）三個路徑，加上 `~/.local/share/lumos-slim/manifest.json` 與執行目錄下的 CLAUDE.md；絕不觸碰任何其他專案目錄/repo、`~/.claude/settings.json`、`~/.claude/hooks/`、除 lumos-project-notes 外的任何其他 skill | 預期驗證點: slim/uninstall.py 全檔案中出現的路徑常數與檔案系統操作對象清單，逐一比對是否僅限上述範圍
