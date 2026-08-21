C1. 生成器的 root 集合計算同時保留兩類函式：①保留指令 dispatch 分支呼叫的函式 ②module-level 語句/class body 呼叫的函式；若只算 dispatch 分支會誤砍 module-level helper（如 `_SKILLS = _skills_list()` 這種賦值呼叫的函式）。 | 預期驗證點: scripts/lumos 內生成器計算 root 集合的程式碼，比對 `_SKILLS = _skills_list()` 是否存在且未被視為 dispatch 分支呼叫

C2. 移除謂詞是「保留指令 dispatch 的 AST 可達性閉包之補集」，不是用 `cmd_` 前綴字面比對；例證是 lint-watch 的實作函式名為 `_lint_watch_mode`、保留的 doctor 實作函式名為 `run_doctor`，兩者都不符合 `cmd_` 前綴規則。 | 預期驗證點: scripts/lumos 中函式 `_lint_watch_mode`、`run_doctor` 的實際命名；生成器判斷保留/移除邏輯是否依賴可達性閉包而非字串前綴

C3. removed_cmds 的真值來源＝掃描全部 subparser 註冊語句（涵蓋 Assign/Expr/迴圈三種型態）得到的指令全集，減去 `DEFAULT_KEEP`（24 支保留指令），不是硬編寫死的移除清單。 | 預期驗證點: scripts/lumos 生成器程式碼中 `DEFAULT_KEEP` 常數定義（元素數應為 24）與掃描 subparser 註冊的實作

C4. 產物採「行級刪除」對原始文字做手術，而非用 `ast.unparse` 重建；理由是 `ast.unparse` 實測會把 686 行事故脈絡註解全部剝光、格式全重排。唯一允許重排的例外是「混合保留與移除指令的迴圈註冊」小塊（2-3 行）。 | 預期驗證點: scripts/lumos 生成器程式碼中是否呼叫 `ast.unparse`（應該不呼叫，或僅在極小範圍呼叫）；主體刪除邏輯是否為對原始行文字的切片/刪除操作

C5. 產物自我驗證有雙保險：①`ast.parse(new_text)` 失敗即以 return code 1 中止 ②`--emit-manifest` 旗標會印出 `keep_funcs`/`drop_funcs`/`removed_cmds`/`kept_comment_lines` 供測試/人工核對。 | 預期驗證點: scripts/lumos 生成器程式碼中 `ast.parse` 呼叫點與失敗後的 `sys.exit(1)`（或等效 rc1）處理；`--emit-manifest` 參數定義與其輸出的四個欄位名稱

C6. `_is_registration_loop` 函式判斷「迴圈註冊」須檢查 receiver 是否為頂層 subparsers 變數 `top_var`；2026-07-31 審查以合成 fixture（`otherkeep` 巢狀註冊 `removeme`/`x2`）示範重現：修復前該函式只看 for 迴圈 body 有沒有 `X.add_parser(迴圈變數,...)`，未查 receiver `X` 是否等於 `top_var`，導致保留指令自建的巢狀子指令註冊迴圈（如 `osub = p2.add_subparsers(...)` 後 `osub.add_parser(n,help=h)`）會被誤判為頂層迴圈、整段砍空。 | 預期驗證點: scripts/lumos 中 `_is_registration_loop` 函式簽名是否含 `top_var` 參數，並在函式體內比對 receiver 是否等於 `top_var`

C7. `collect_edits()` 與 `main()` 印診斷用的 `allc` 掃描，兩處呼叫 `_is_registration_loop` 都須傳入 `top_var`；前一位實作者曾誤判「main() 的 allc 掃描沒限定 receiver、collect_edits() 是安全的、屬於超出範圍的純診斷雜訊」，經審查追碼確認兩邊其實是同一段未防護邏輯，該定調已不採用（decisions d2，valid: true）。 | 預期驗證點: scripts/lumos 中 `collect_edits()` 函式與 `main()` 函式內，兩處對 `_is_registration_loop(...)` 的呼叫是否皆帶 `top_var` 引數

C8. `collect_edits()` 對 `main.body` 區塊追蹤已修正：nested for 迴圈（receiver ≠ top_var）不再被無條件剝離出來單獨處理，而是併入所在區塊、隨該區塊一起留下或一起刪除；此修正是為避免「巢狀迴圈屬於已整塊移除的群組指令（如 code-loop 底下的 pass/skip/check）」時反向退化成漏刪、產出 NameError。 | 預期驗證點: scripts/lumos `collect_edits()` 中 main.body 的區塊追蹤邏輯，對 nested for 迴圈（receiver≠top_var）的處理方式是否為「併入所屬區塊」而非「單獨剝離」

C9. 交付包組包清單（`main()` 尾段）曾遺漏 `slim/get.sh` 與 `slim/uninstall.sh`，只複製 `install.sh`/`README.md`/`skills`，實測 `dist/` 只剩 `install.sh`/`README.md`/`scripts/lumos`；修復後組包清單加入 `get.sh`/`uninstall.sh`，且三支 `.sh`（install/get/uninstall）都補上 `chmod 0o755`（原本只對 install.sh 補執行位元）。 | 預期驗證點: scripts/lumos 生成器 `main()` 尾段組包清單程式碼中是否含 `get.sh`、`uninstall.sh`，以及對三支 `.sh` 做 `chmod` 的迴圈邏輯

C10. Task 9 新增的 `slim/claude-block.md`（CLAUDE.md 注入內容外部靜態範本，取代原本腳本內嵌 heredoc）在新增檔案當下即同步加進組包清單 `for item in (..., "claude-block.md", "skills")`，`t_slim_gen_dist_ships_entrypoints` 的 expected 清單同步加了這一項。 | 預期驗證點: scripts/lumos 組包清單的 `for item in (...)` tuple 是否含 `"claude-block.md"`；scripts/test_lumos.py 中 `t_slim_gen_dist_ships_entrypoints` 函式的 expected 清單是否含此項

C11. Task 13 新增 `slim/install.py`/`slim/uninstall.py`（真正邏輯所在，`.sh` 只是薄殼）與 Windows 入口 `slim/install.ps1`/`slim/uninstall.ps1`/`slim/get.ps1`，共 5 個新檔，於 `main()` 尾段組包清單的 `for item in (...)` 迴圈當下同步加入；`.py`/`.ps1` 不進「補 chmod 0o755」的迴圈（`.py` 一律經薄殼 `python <path>` 呼叫、`.ps1` 執行權限由 Windows 執行原則管），只有 `.sh` 三支需要可執行位元。 | 預期驗證點: scripts/lumos 組包清單是否含 `install.py`/`uninstall.py`/`install.ps1`/`uninstall.ps1`/`get.ps1`；chmod 0o755 迴圈是否僅對 `.sh` 副檔名生效

C12. `t_slim_gen_dist_ships_entrypoints` 的 expected 檔案清單已擴充到 12 項，並更新其 docstring（對應 [test:t_slim_gen_dist_ships_entrypoints]）。 | 預期驗證點: scripts/test_lumos.py 中 `t_slim_gen_dist_ships_entrypoints` 函式的 expected 清單元素數量是否為 12，docstring 是否有相應更新

C13. `python3 scripts/test_lumos.py -k slim_gen` 應 25 個 checks 全綠，涵蓋：真檔生成驗證（`--help` 顯示保留 24 支指令、`py_compile` 產生 0 個 SyntaxWarning、dangling handler 數為 0）+ 合成 fixture 驗證迴圈註冊真的被砍 + 巢狀迴圈合成 fixture `t_slim_gen_nested_loop_registration` + 註解密度守衛 + 交付包完整性守衛 `t_slim_gen_dist_ships_entrypoints`。 | 預期驗證點: 執行指令 `python3 scripts/test_lumos.py -k slim_gen`，確認輸出的 checks 總數為 25 且全數通過

C14. 註解密度守衛：產物註解密度不得低於原檔的 90%；此守衛取代原本「保住 N% 註解」的門檻（N 曾從 60% 下修到 50%）。實測數字：原檔 11999 行 / 686 行註解 = 5.7%，產物 6203 行 / 379 行註解 = 6.1%，未下降（decisions d1，valid: true）。 | 預期驗證點: scripts/test_lumos.py 中 `t_slim_gen_keeps_comments` 函式的密度計算與 90% 門檻斷言；對 scripts/lumos 原檔與生成產物實際跑行數/註解行數統計，核對 11999/686 與 6203/379 這組數字

C15. `t_slim_gen_dist_ships_entrypoints` 斷言 `dist/` 目錄內存在 `get.sh`/`uninstall.sh`/`install.sh`/`README.md`/`scripts/lumos`/`skills/lumos-project-notes/SKILL.md`，且三支 `.sh` 皆具備可執行位元。 | 預期驗證點: scripts/test_lumos.py 中 `t_slim_gen_dist_ships_entrypoints` 函式的斷言內容；實際執行生成器後檢查 `dist/` 目錄下述路徑是否存在及其檔案權限
