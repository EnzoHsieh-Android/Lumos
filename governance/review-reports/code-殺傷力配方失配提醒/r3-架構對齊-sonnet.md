severity: clean

# 架構對齊席(sonnet)第 3 輪報告

對照結果(沒有引進第二種做法、沒有跨層直呼,不湊 finding):

1. 暫存索引(GIT_INDEX_FILE + read-tree):專案內沒有既有同類 helper。file: `scripts/lumos:13118` 是唯一出處;其他 git 包裝(`_nodehome_git`、`_testmap_git`、`_lens_git`)都是對真索引或 ls-tree 問,沒有「從 HEAD 讀出暫存索引」的做法,所以不是重複造輪。同檔 `_kill_tree` 的 `git ls-tree` 與新函式同樣直接 `subprocess.run(["git","-C",key,...], timeout=_KILL_GIT_TIMEOUT)`,風格一致。
2. 暫存資料夾與清理:`_kill_fs_fold` 用 mkdtemp + finally rmtree,與 cmd_guard_kill(file: `scripts/lumos:13926`)同款;`_kill_restorable` 的索引要跨多次呼叫存活所以改 atexit(專案內 atexit 只此一處,但沒有既有慣例可對,且生命週期不同,不算第二種做法)。
3. `_kill_fs_fold` 量檔案系統特性:專案內只有 `_drift_c4_dir_key` 之類「一律 nfc+casefold」的比對鍵(file: `scripts/lumos:30086`),沒有量測式做法;此處要貼合 guard kill 暫存資料夾的實際行為,量測合理,且沿用共用的 `nfc`(file: `scripts/lumos:387`)。
4. `_kill_esc` / `_kill_rel` / 佔位字:類別集合走共用的 `_PATH_SPECIAL_CATS`、判斷走 `_path_special_chars`(file: `scripts/lumos:27572`),沒有另立類別表。與 `_note_reread_show`(換成空格)、`_esc_clean`(換空格、不含 Cf)輸出形式不同(此處換成可見的 \uXXXX,需要讓人看出原樣),屬不同需求,不是同一件事做兩種。
5. 測試 spy:`t_kill_recipe_check_fs_and_git` 的「存 real_run、換 subprocess.run、finally 還原、spy 內只記 git 呼叫」與既有慣例一致(file: `scripts/test_lumos.py:42469` 的 `real_run = m.subprocess.run` ... `finally: m.subprocess.run = real_run`)。

最高等級:clean
