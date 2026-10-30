severity: minor

## A1 --scope 的合法性檢查另寫一套,沒有呼叫專案共用的 `_config_glob_error`
severity: minor
blocking: 否
引句:「if scope.startswith(("./", "/")):」
file: `scripts/lumos:57306`

`_config_glob_error` 的 docstring 寫明是 review_roles 與 arch_targets 共用的同一支。它檢查空白、`./` 或 `/` 開頭、反斜線。新碼的 `_arch_tpl_scope_error` 把這三項又各寫了一遍,另外加了萬用字元、空段、少於兩段等新檢查。

結構是對的:最後產出的宣告仍交給 `_arch_targets_config` 讀一次(`_arch_tpl_targets`),讀出的條數不同就拒絕。差別只在前面那段把共用的三項重寫了一份,所以才列 minor。若日後 `_config_glob_error` 的規則改了,這裡不會跟著動。

## 三問

**1. 分層與依賴方向:對齊。**
- 新碼放在 `scripts/lumos` 的 arch 區塊,緊接 `_arch_target_vault_rel` 之後,跟既有的 `_arch_targets_config`、`_arch_legacy_at` 同一區(`scripts/lumos:57754` 附近)。
- 讀範本走 `_note_template_fill`(`scripts/lumos:48551`):專案自己的優先,退回工具安裝樹。這跟 `_NOTE_AUDIT_TEMPLATE`、`_NOTE_REREAD_TEMPLATE` 一樣。
- 工具自帶檔清單 `_VENDORED_TREE_FILES` 已補上新資料檔。
- 找 repo 根用 `_lens_git(Path.cwd(), "rev-parse", "--show-toplevel")`,跟 `scripts/lumos:57990` 相同。
- 路徑字元檢查用 `_path_special_chars`,NFC 轉換用 `nfc`。
- 宣告讀回用 `_arch_targets_config`。
- 舊檔清單的 `{"files": [...]}` 形狀跟讀端 `_arch_legacy_at`(`scripts/lumos:57424`)一致。
- 沒有跨層直呼。`cmd_arch_template` 只讀不寫,輸出走 `sys.stdout`。
- 子命令註冊(`sub.add_parser`、`HELP_WHEN`、`main` 分派)跟 `spec-freeze` 同形(`scripts/lumos:69211`、`70144`、`70644`)。
- argparse 的 dest 加前綴(`at_*`),跟 `freeze_*`、`lens_*` 的做法一致。

**2. 命名與錯誤處理:對齊,只有 A1 一處小差異。**
- 函式命名 `_arch_tpl_*` 沿用 `_arch_*` 家族。
- 錯誤一律 stderr 加 `擋下:` 再回 rc 2。這個前綴在 `scripts/lumos` 裡出現約 700 次,是專案慣例。
- `cmd_spec_freeze` 的前綴是 `spec-freeze:`,另帶 `--json` 與代碼表;新命令只印終端,沒有 `--json`,跟它「只印到終端」的定位相符。
- 函式內 `import json as _j` 的寫法跟 `cmd_spec_freeze` 的 `import stat as _st` 同風格。
- 沒有日誌,鄰居的只讀命令也沒有。
- 測試用 `_role_git_repo`、`_load_lumos_inproc`、`check`、`mkvault`,檔內 `os.chdir` 已有 34 處,做法一致。
- 舊測試 `t_arch_target_android_template_*` 保留原名,改測產生器的產出。

**3. 第二種做法:大致沒有,有兩處標 ⚠ 交編排者。**
- ⚠ 同一個「目標架構範本」家族現在有兩種機制。DDD 與前端範本還是技能文件裡抄貼的範本(`skills/lumos-project-notes/commands/target-arch-frontend-template.md` 的「採用步驟」一到四),Android 改成由 `lumos arch-template android` 產生。
  - 計劃明寫了這個改法,也有開關帶來的組合變化當理由。
  - 但專案裡沒有既有的「範本產生器」可對,我判不準算不算第二種做法,所以不硬判。
- ⚠ `_arch_tpl_fill` 另寫了佔位字替換,用的是同一個 `_NOTE_TEMPLATE_SLOT_RE`。
  - 載入仍走 `_note_template_fill`,傳空表讓佔位字原樣留下,再由 `_arch_tpl_fill` 替換。
  - 不同點是遇到表外佔位字就拒絕,而 `_note_template_fill` 是原樣留著。行為需求確實不同,但沒有擴充既有函式,而是在它旁邊疊一層。我傾向不算第二種做法,請編排者定。

總結:不對齊共 1 條,其中 major 0 條。
