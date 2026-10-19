severity: clean

這輪修補我逐 hunk 看過,沒找到能利用的洞,三類都已看,無發現。

**① 提示注入:已看,無。** 這輪新增的字串都是固定的訊息文字(`_TEST_NAME_RULE_ZH`、撞名訊息、`_anchor_migration_hint`)。其中會帶進外來字串的有兩處:檔名經 `_kill_esc` 轉義,配方的 test 名經 `_kill_show` 顯示。兩者都沒有接進給 AI 的派工詞或 hook 附加段。

**② 讀寫與執行越界:已看,無。**
- **正規式跳脫與 shell。** `_name_filter_escape` 的 regex_tail 改成 `\s` + 跳脫後的名字 + `(?:\s@\S+)*$`。跳脫集合 `.*+?^${}()|[]\/` 涵蓋了所有會影響正規式的字元。字串開頭是 `\s`,不會被當選項,而 `_test_name_ok` 本來就擋以 `-` 開頭的名字。
- **shell 引號。** 名字交給 shell 時走既有的 `_run_cmd_expand` 引號。Windows 上 `_WIN_CMD_SPECIAL` 擋掉 `& | < > ^ % " !`,上一輪拿掉的 `^`、`|`、`<` 也不在新的 regex 裡。
- **git grep 的 `--`。** 我查了 `scripts/lumos` 現有各處 `git grep` 呼叫,都用 `-e` 或 `-f` 傳樣式,並在 `--` 前結束參數。這輪的修補沒有新增 grep 呼叫。
- **`file_name_match` 越界讀取。** `_walk_test_files` 的檔名錨只用 `fnmatch` 比檔案的 basename,走訪根是 `repo_root`,`os.walk` 不跟隨目錄捷徑。設定覆蓋後,掃描讀不到 repo 外。
- **`_anchor_migration_hint` 快取。** 這支新加的快取只以平台根、profile 名、檔名錨為鍵,讀的範圍和原本相同,沒有新的讀寫面。
- **密鑰與信箱。** 測試補丁裡沒有看起來能用的憑證或信箱。我搜了 `subprocess`、`shell`、`environ`、`token`、`password`,只對到 `import subprocess` 與 `sys.platform == "win32"` 兩行。

**③ 非刻意走過守衛:已看,無。**
- **被跳過的綁定測試判綠。** 撞名判定新增了 describe 加測試拼名、`@tag` 剝除、「自己那一支只由種類是測試的第一個佔用」。這些都讓撞名判得更嚴(寧可多數)。要把「被跳過的綁定測試」判綠,得靠更鬆的判定,而這幾處沒有放鬆。
- **標題頭尾空白。** `_test_name_of_match` 對字串標題頭尾有空白的名字回 None。這讓綁定更少被收進來,守衛不會因此被走過。
- **`_bind_name_problem` 改用 `_split_test_ref_ex`。** 寫入端現在和讀取端判同一套規則,而且 `platform is None` 時一律檢查。比上一版(只在名稱含冒號時才檢查)多擋,沒有放寬。
- **`lenient` 路徑。** 只用於殺傷力配方,剝前綴後仍要過 `_test_name_ok`(`cmd_guard_kill` 與 `_kill_recipe_judge` 都有)。
- **剝註解的多行字串。** `_C_STRIP_RE` 新增三引號與 `@"..."` 的處理,把這類字串內的 `/*` 認成字串,測試不再被整段吞掉。這是修補,不是繞過。

我另外看到幾處潛在的效能問題:`_PW_TAG_TAIL_RE` 掃很長且重複的標題時接近二次方,`_C_STRIP_RE` 的未閉合三引號會吃到檔尾。這些歸資源席,依規定不報。

最嚴重 severity:clean,blocking 共 0 條。
