severity: minor

## A21 目前目錄找 repo 根的做法在新子命令裡又寫了一遍
severity: minor
blocking: 否
引句:「r = _lens_git(Path.cwd(), "rev-parse", "--show-toplevel")」
file: `scripts/lumos:63469`(既有的 `_lens_repo_root(repo)` 就是同一件事:`_lens_git(start, "rev-parse", "--show-toplevel")`,取不到回 None;新碼在 `scripts/lumos:57994-57998` 自己內聯了五行)

## A22 判斷哪些路徑算測試原始碼集,新增了第三套寫法
severity: minor
blocking: 否
引句:「_ARCH_TPL_KONSIST_TEST_RE = re.compile(r"(?:^|/)src/[^/]*test[^/]*/", re.I)」
file: `scripts/lumos:46997`(`_rg_is_test_path` 也是用 `src/<名稱>/` 判測試原始碼集,規則是以 test、androidTest 開頭或以 Test 結尾;`scripts/lumos:40736` 的 `_e2e_default_excluded` 是第二套)

**1. 分層與依賴方向:對齊,A22 為 ⚠ 待編排者判。**
- 新碼全放在 `_arch_*` 家族旁邊(`scripts/lumos:57755` 到 `57770`)。
- 呼叫鏈和鄰居一致,沒有跨層直呼:
  - 讀檔走 `_note_template_fill`(`scripts/lumos:48551`)。
  - 讀宣告走 `_arch_targets_config`(`scripts/lumos:57312`)。
  - 範圍檢查走 `_config_glob_error`(`scripts/lumos:57306`)。
  - 檔案判定走 `_arch_code_file`(`scripts/lumos:57489`)。
  - 特殊字元判定走 `_path_special_chars`(`scripts/lumos:49134`)。
  - 路徑正規化走 `nfc`。
- 本輪修補沿用 `_arch_code_file`,再疊 Konsist 規則。沒有改走另一條呼叫路徑,這部分沒有新做法。
- `_VENDORED_TREE_FILES`、`HELP_WHEN`、argparse 的 `at_` 前綴(對照 `freeze_`、`lens_` 前綴)、`main()` 的分派都照鄰居寫,沒有偏離。
- A22 判不準:Konsist 的規則是「原始碼集名稱轉小寫後含 test」,和 `_rg_is_test_path` 的「開頭或結尾」確實不同,另寫一條有理由。但專案裡因此有了三套「src/ 下哪段算測試」的判定。產出的 Kotlin 讀清單改用兩條正規式,也沒碰這件事。

**2. 命名與錯誤處理:大致對齊,有 A21 一條。**
- 命名:`_arch_tpl_*` 前綴、全大寫常數、`cmd_` 前綴,都和鄰居一致。
- 錯誤處理:擋下訊息用 `擋下:…` 寫到 stderr,回傳 rc 2,和 `cmd_spec_freeze`、`cmd_dispatch_lens_spec` 一致。
- 日誌:只讀、印到終端,沒有另造日誌方式。
- 函式內 `import json as _j`、`import datetime as _dt` 是全檔既有寫法(分別 82 處、49 處)。
- 取本機日期的 `_dt.datetime.now(_dt.timezone.utc).astimezone().date()` 照 `scripts/lumos:4349` 的寫法。
- 差異只有 A21:`cmd_spec_freeze` 內聯是因為要帶 `_SPEC_FREEZE_GIT_C` 參數,新碼沒有這個理由。

**3. 第二種做法:A21、A22 兩條,結構都對,沒有跨層直呼。**
- `_arch_tpl_fill` 另寫一輪佔位字替換,只是為了表外佔位字要拒絕而不是原樣留著。它沿用 `_NOTE_TEMPLATE_SLOT_RE`,第一輪也走 `_note_template_fill`,行為有差別,所以不列。
- `_arch_tpl_until` 沒有既有的一年後日期輔助函式可用(grep 沒找到),不算重複。
- 舊檔清單收檔用 `_arch_tpl_legacy_file` 疊在 `_arch_code_file` 上,是延伸而不是另寫一套。

總結:不對齊共 2 條。
