C1. 兩層分工:`install`/`uninstall`/`bootstrap` 屬機器層,只動 `~/.local/bin`(全域 lumos)+ `~/.claude`(user-scope skills、hooks);`init`/`update`/`deinit` 屬專案層,只動本 repo(`docs/<slug>-knowledge/`、`scripts/` vendored、`CLAUDE.md` 注入、`git core.hooksPath`) | 預期驗證點: scripts/lumos cmd_install/cmd_uninstall/cmd_bootstrap vs cmd_init/cmd_update/cmd_deinit 各自的檔案系統寫入路徑

C2. `install [--force]` 在 Unix 用 symlink、Windows 用 `lumos.cmd` shim 建全域指令,並連帶安裝 user-scope skills,且會檢查 `~/.local/bin` 是否在 PATH | 預期驗證點: cmd_install 函式、PATH 檢查邏輯

C3. `uninstall` 對稱移除全域指令與 skills(symlink/junction/複製夾皆清除);junction 移除用 `os.rmdir` 只移除連結本身、不會遞迴進 target 目錄刪除來源內容 | 預期驗證點: cmd_uninstall 函式、os.rmdir 呼叫點

C4. `bootstrap` 支援旗標 `--lumos-url --lumos-home --pull --init`;預設**不會** pull 既有的 Lumos 源 clone,需顯式加 `--pull` 才更新 | 預期驗證點: cmd_bootstrap 參數解析、預設 pull 行為

C5. bootstrap 對專案層採四分流(2026-07-25 起):①已有 vault 且已 vendored → 直接接 hooks ②中間態(有 vault 無 vendored,靠 `_vault_in` 判斷名稱)→ 只提示不自動動作 ③無 vault → 經 `_confirm_tty` 確認(印完整路徑、預設 N,`y`才執行);`--init` 旗標可跳過確認直接執行,且一律以 `force=False, no_pull=True` 呼叫 `cmd_init` ④非 git repo → 只跑機器層,不碰專案層 | 預期驗證點: cmd_bootstrap 內對 vault/vendored 狀態的分流判斷邏輯、_vault_in 函式、對 cmd_init 的呼叫參數

C6. `init [--name --force --no-hooks --no-pull]` 會建立 vault(6 個資料夾 + `.gitignore` + `MOC/index.md` + CLAUDE.md 注入區塊)+ 預設 vendor 工具組 + 安裝 pre-commit/pre-push hooks | 預期驗證點: cmd_init 函式、_INIT_SUBDIRS_FULL 常數(應為 6 個資料夾:Systems、Verification、Projects、Issues、Sessions、MOC)

C7. `update [--source --no-pull]` 只刷新「本專案」的 vendored 工具組(git pull 源 + 重新 vendor),圖譜資料(vault)受 skip 保護不會被動到 | 預期驗證點: cmd_update 函式、與 _scaffold_project 的 vault-skip 邏輯互動

C8. ★INVARIANT★ re-inject 只覆蓋 CLAUDE.md 中 sentinel 標記之間的 body,sentinel 之外的既有內容必須 byte-equal 保留不變 | 預期驗證點: t_reinject_preserves_outside 測試、CLAUDE.md re-inject 相關函式(sentinel 解析與覆寫範圍)

C9. `_confirm_tty` 三階確認機制:①`stdin.isatty()` 為真時用 `input()`,遇 `EOFError` 落入下一階 ②開啟 `/dev/tty` 用低階 fd(`os.open` O_RDWR)+ `os.write` + `select` 逾時 30 秒 + `os.read` ③兩者皆不可行則回傳 None(視為跳過);合法答案嚴格限定 `y`/`yes`,預設一律為 N(拒絕);測試接縫為環境變數 `LUMOS_TTY`/`LUMOS_TTY_TIMEOUT` | 預期驗證點: _confirm_tty 函式實作、上述環境變數讀取點

C10. `teardown` 跨兩層一鍵反安裝,執行順序固定為:全域 hook 清理 → `deinit(keep_graph=True)` → `uninstall`;圖譜文件(docs/knowledge vault)在任何情況下都保留不刪;順序「全域先」是因為 deinit 會刪掉 vendored 的 `merge-claude-settings.py`,而 `_teardown_global_claude` 需要用它來做清理 | 預期驗證點: cmd_teardown 函式呼叫順序、_teardown_global_claude 對 merge-claude-settings.py 的依賴

C11. Windows 上的 `_selfdelete_risk()` pre-flight 檢查:若正在執行的 lumos 是 repo 內 vendored 那份(而非全域 lumos),在 teardown 進行任何 mutation 前即回傳 rc2 拒絕執行;此守衛只在 Windows 生效(用 `LUMOS_SIMULATE_WINDOWS` 環境變數作測試接縫,不影響全域 `_IS_WIN` 判斷);路徑比對改用 `parts` 前綴比對(`len(me) > len(r) and me[:len(r)] == r`)而非 `Path.is_relative_to()`(因該方法為 Python 3.9+ 專屬,本專案宣告支援 ≥3.8);例外處理必須是窄範圍 `except OSError`,不得寫成寬鬆的 `except Exception`;`--dry-run` 情況下不觸發此守衛 | 預期驗證點: _selfdelete_risk 函式、t_selfdelete_risk_python38_compatible_and_dryrun_exempt 測試、except 子句型別

C12. `cmd_init` 決定 vault slug 的優先順序為:①`--name` 旗標 ②既有 vault 資料夾名稱(去除 `-knowledge` 後綴)③repo 的 basename;此順序中②必須先於③,否則在既有 vault 上使用 `--force` 會誤用 basename 建立錯誤的空 vault | 預期驗證點: cmd_init 內 slug 決定邏輯、t_init_force_uses_existing_vault_slug 測試

C13. 來源 repo 自我保護:`update` 與 `deinit` 兩指令偵測到執行目錄 `root == _lumos_src()`(即在 Lumos 源本身 repo 內執行)時,會回傳 rc=2 並拒絕執行,不允許在源 repo 本身跑專案層指令 | 預期驗證點: cmd_update、cmd_deinit 函式內對 _lumos_src() 的比對邏輯

C14. `_VENDORED_TOOLKIT` 白名單固定為 5 個檔案(`scripts/lumos`、`scripts/test_lumos.py`、`scripts/merge-claude-settings.py`、`scripts/graph-rename.sh`、`scripts/fetch-notesmd.sh`)加上 `scripts/hooks/`、`scripts/templates/` 兩個整夾;此常數同時被 `_vendor_toolchain`(安裝端)與 `_deinit_remove_vendored`(移除端)共用,避免兩端白名單各自列舉而漂移 | 預期驗證點: _VENDORED_TOOLKIT 常數定義、_vendor_toolchain 與 _deinit_remove_vendored 是否皆引用同一常數

C15. 2026-08-11 起,來源 pull 改為 fail-closed 政策(收進單一函式 `_pull_source_or_abort`,由專案層 `_vendor_toolchain` 與機器層 `cmd_bootstrap` 共用):若來源 repo 有設定 remote 但 pull 失敗,則在寫入任何檔案之前中止(不留半套);若來源 repo 無 remote(離線 clone),則不視為失敗、照常執行;三個指令(`update`/`init`/`bootstrap`)皆提供 `--allow-stale` 逃生門覆蓋此中止行為 | 預期驗證點: _pull_source_or_abort 函式、t_vendor_pull_failure_aborts / t_vendor_no_remote_skips_pull / t_vendor_allow_stale_overrides_pull_failure / t_bootstrap_pull_failure_aborts 測試

C16. decisions d5(2026-08-20,valid: true):本 repo 與 Citrus_Lumos_Full 鏡像分家——本 repo 不再推送鏡像、不再視其為同步目標;鏡像自帶獨立的安裝入口(get.sh/get.ps1)與更新路線,自此獨立演進,兩邊內容會分岔 | 預期驗證點: git remote 設定(應不再含 Full 鏡像 remote 或不再有推送腳本)、鏡像 repo 的 get.sh/README 是否已改指向自身而非 EnzoHsieh-Android/Lumos

C17. decisions d6(2026-08-20,valid: true):精簡版交付庫 Citrus_Lumos 分家——本 repo 內 `slim/` 目錄凍結(不刪除、不再對外發布新版本),交付庫獨立演進自負更新;`slim/` 內測試照跑但不再由本 repo 人工同步推送 | 預期驗證點: repo 內 slim/ 目錄是否存在 FROZEN 告示檔(FROZEN.md)、slim/ 相關測試是否仍在跑但無新推送紀錄

C18. `_deinit_unbar_gate` 只有在 `git config core.hooksPath` 的值指向本 repo 的 `scripts/hooks` 時才會 unset 它,不會誤刪使用者自訂的 githooks 路徑;`cmd_uninstall` 只移除 `~/.local/bin/lumos` 是 symlink 的情況,若該路徑是一般檔案(同名非連結檔)則不刪除 | 預期驗證點: _deinit_unbar_gate 函式、cmd_uninstall 對 ~/.local/bin/lumos 型別(symlink vs regular file)的判斷分支
