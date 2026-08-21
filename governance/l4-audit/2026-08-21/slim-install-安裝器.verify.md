C1 [✅] install.sh 用 `cd "$(dirname "$0")" && pwd` 同義寫法（自製 `_dirof()` 取代外部 `dirname`）定位套件目錄，並手捲 symlink 解析迴圈（無外部 `readlink -f`） | 證據: slim/install.sh:19-35（`_dirof()` 純 bash 參數展開，`while [ -L "$SOURCE" ]` 逐層 `readlink` 接回所在目錄再判斷）

C2 [✅] 套件完整性檢查 `scripts/lumos`（`is_file`）與 `skills/lumos-project-notes`（`is_dir`）存在，找不到即 rc=2 | 證據: slim/install.py:356-361

C3 [✅] 注入目標守衛兩層，皆 rc=2 且不建目錄不動任何檔案：第一層（`.git`/`docs/*-knowledge/`/既有 CLAUDE.md 皆無，或 `target_dir==home` 用 `Path.cwd().resolve()`/`Path.home().resolve()` 解 symlink 後比對）→拒絕；第二層（`skills/lumos-project-notes`+`scripts/lumos`+`scripts/templates/graph-discipline.md` 三件套齊備）→拒絕 | 證據: slim/install.py:382-414；測試 t_slim_install_guard_rejects_empty_dir (scripts/test_lumos.py:18298)、t_slim_install_guard_rejects_home_dir (:18327)、t_slim_install_guard_rejects_source_repo (:18347) 三支皆存在且斷言 rc=2 與 CLAUDE.md 未建/未動

C4 [✅] `--here` 繞過第一、二層（`if not here and not tool_only:` 整段跳過），第三層印目標路徑（`print(f"目標專案: ...")`/`print(f"將修改: ...")`）在 guard 判斷之前執行、不受 `--here` 影響 | 證據: slim/install.py:376-382（印出邏輯）vs :382（`if not here` 才進 guard）；測試 t_slim_install_guard_here_bypasses (scripts/test_lumos.py:18426) 驗證繞過後 rc=0 且更新成功

C5 [✅] bin 的 sha256（`bin_sha256`）寫入 `~/.local/share/lumos-slim/manifest.json`，manifest 目錄現場 `mkdir(parents=True, exist_ok=True)`，不依賴 `~/.lumos-slim` 是否存在 | 證據: slim/install.py:293-305（`manifest_dir = Path.home()/".local"/"share"/"lumos-slim"`, `bin_sha = _sha256_file(dst_script)`）；測試 t_slim_uninstall_direct_install_restores_claude_md (scripts/test_lumos.py:16850-16909) 明確驗「~/.lumos-slim 確實不存在」情境下 manifest 基準仍可比對成功卸載

C6 [❌] 實際是 Python `shutil.copytree()` 而非文字上的 `cp -R`；行為上確為實體複製（非 symlink），語意一致但機制描述不準（本包已從 bash 全面改寫為 install.py stdlib，不再 shell 出 `cp -R`） | 證據: slim/install.py:338 (`shutil.copytree(src_skill, dst_skill)`)

C7 [✅] sentinel `<!-- LUMOS-SLIM:START -->`/`<!-- LUMOS-SLIM:END -->`；完整版 `LUMOS:GRAPH-DISCIPLINE` 區塊存在時原地整段取代、sentinel 外內容 byte-equal；否則插在檔首「# 」標題之後（無標題插最前）；CLAUDE.md 不存在則 `original=""` 直接建立 | 證據: slim/install.py:91-96 (sentinel 常量), :142-195 (`_merge_claude_md_text` 三分支), :186-190（標題判斷 `original.startswith("# ")`）；測試 t_slim_install_no_project_touch (:16257)、t_slim_install_replaces_full_discipline_block_in_place (:16486) 逐位元組斷言吻合

C8 [✅] 冪等：重跑只更新 sentinel 間內容不疊第二塊，備份標記沿用既有值不重新編碼/不洗成 NONE（`_merge_claude_md_text` 情境②：`bm = BACKUP_RE.search(...); backup_marker = bm.group(0) if bm else BACKUP_NONE`） | 證據: slim/install.py:175-181；測試 t_slim_install_claude_md_idempotent (:16342)、t_slim_install_backup_survives_idempotent_reinstall (:16544) 皆斷言重跑後 byte-equal

C9 [✅] 完整版區塊被取代前，原文（含自身 sentinel，`m.group(0)`）以 base64 編碼進精簡版區塊的 HTML 註解 `<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->` | 證據: slim/install.py:167-173（`full_text = m.group(0)`, `base64.b64encode(full_text.encode("utf-8"))`）；測試 t_slim_install_replaces_full_discipline_block_in_place (:16486) 明確 base64 解碼後與 `full_block`（含 START/END）逐位元組比對相同

C10 [✅] bin/skill 目標已存在且未帶 `--force` 時 rc=2 拒絕；帶 `--force` 時 bin 直接 unlink 後覆寫（manifest 仍照寫）、skill 目錄先 `_skill_backup_path()` 備份成 `.bak.<timestamp>` 才 `copytree` | 證據: slim/install.py:261-276（bin：`collided` 判斷→`return 2`／`dst_script.unlink()` 後 `shutil.copyfile`）, :319-338（skill：先 `dst_skill.rename(bak)` 再 `shutil.copytree`）

C11 [部分✅/需澄清] `main()` 確為「遇錯早退」語意（`rc = _install_cli(...); if rc != 0: return rc` 同款重複），與 uninstall.sh「各步互不阻擋」相反（docstring 明講）；但 `_main_guarded()` 實際除了 `except OSError` 外，還多一支 `except UnicodeDecodeError`（對應 C12 所述），並非「只接 OSError」——若把 C11 讀作「僅在最外層以 try/except 包一層、不逐步吞例外」則成立，若逐字讀「只接 OSError」則與程式碼有出入 | 證據: slim/install.py:419-425（早退）, :459-499（`_main_guarded` 同時 `except UnicodeDecodeError`（:479）與 `except OSError`（:493）两分支）

C12 [✅] `_merge_claude_md_text()` 內部 `target.read_text(encoding="utf-8")` 讀非法 utf-8 會拋 `UnicodeDecodeError`（繼承 `ValueError`），`_main_guarded()` 已補獨立 `except UnicodeDecodeError` 分支且訊息內斷言檔案位元組原封不動 | 證據: slim/install.py:149（讀取點）, :479-492（獨立 except 分支）；測試 t_slim_install_non_utf8_claude_md_reports_cleanly (scripts/test_lumos.py:17389) 斷言 `claude_md.read_bytes() == raw`

C13 [❌] 前半屬實：Task 13 確實把 bash 版 install.sh（293 行，見 commit 7fa0c0c 的 `git show`）改寫成 install.py（現 503 行，stdlib only），install.sh 改版後只做①symlink 解析定位②挑 python3/python 轉發，並新增 install.ps1；但「僅約 35 行」與現況不符——當前 slim/install.sh 實際 51 行（Task 13 剛完成時的 commit 5fa02d2 為 39 行，之後 de1f32b/a2fb322 兩次修正加了 `_dirof()` 與大量註解才漲到 51 行） | 證據: `wc -l slim/install.sh` = 51；`git show 7fa0c0c:slim/install.sh \| wc -l` = 293；`git show 5fa02d2:slim/install.sh \| wc -l` = 39；slim/install.py 共 503 行；slim/install.ps1 共 40 行

C14 [✅] Windows shim 直譯器名稱不寫死字面 `python`，用 `_pick_windows_interpreter()`（依序 `shutil.which("python3")`/`shutil.which("python")`，都找不到才退回 `"python"`）偵測寫進 `.cmd` shim | 證據: slim/install.py:198-237（函式本體）, :278（`_install_cli` 呼叫處：`py_cmd = _pick_windows_interpreter()`）；測試 t_slim_install_windows_shim_does_not_hardcode_python_when_only_python3_available (scripts/test_lumos.py:18879) 用僅含 python3 的假 PATH 精確比對 shim 內直譯器 token

C15 [✅] Windows 路徑碰撞偵測同時檢查 `lumos`（`dst_script`）與 `lumos.cmd`（`dst_shim`），僅看前者會讓孤兒 `lumos.cmd` 被非 `--force` 重裝無聲覆寫 | 證據: slim/install.py:261-263（`collided = dst_script.exists() or dst_script.is_symlink(); if IS_WIN: collided = collided or dst_shim.exists() or dst_shim.is_symlink()`）；測試 t_slim_install_windows_collision_detects_orphan_cmd_shim (scripts/test_lumos.py:18923) 驗證孤兒 `.cmd` 觸發碰撞保護且內容未被覆寫

C16 [❌] 實際執行 `python3 scripts/test_lumos.py -k slim` 結果為 **474 passed, 0 failed**，不是「225 checks」；全綠（0 failed）屬實，但具體數字（225）與現況不符——本次驗證環境現場實跑得到的數字 | 證據: 現場執行 `python3 scripts/test_lumos.py -k slim` 尾行輸出 `474 passed, 0 failed`；repo 內（README/FROZEN.md 等非圖譜檔案）未搜到「225」字樣佐證舊數字來源

✅10 ❌3 ❓0 ⏭0
（C11 併記為部分符合，計入 ❌ 的嚴格判定內；若寬鬆讀法則可視為 ✅，此處採嚴格逐字比對故計入不一致）
