severity: minor

## A11 樣板填字沿用載入函式卻另寫一套嚴格的佔位字替換
severity: minor
blocking: 否
引句:「text = _note_template_fill(root, _ARCH_TPL_ANDROID, {})」
file: `scripts/lumos:48551`

說明:專案原本就有 `_note_template_fill`,載入範本、剝掉 SPDX 與開頭註解、用 `_NOTE_TEMPLATE_SLOT_RE` 一次掃描替換,表外佔位字原樣留著。新碼借它的載入,但傳空表讓替換變成空操作,再用 `_arch_tpl_fill` 自己掃一次、表外佔位字就擋下。結構上是借用了同一支載入函式和同一個正規式,只是把替換拆成第二份。要用條件塊再填字,所以嚴格版有存在理由。為什麼判 minor:它沒有繞開載入函式。為什麼不是 major:是否算第二種做法有爭議。判不準,交編排者(⚠)。

## 三問

**1. 分層與依賴方向:對齊**
- 新碼放在 arch 區塊 `_arch_target_vault_rel` 之後,屬於同一層的純函式加一個 `cmd_`。
- 它向下呼叫 `_arch_targets_config`(`scripts/lumos:57316`)、`_arch_code_file`(`scripts/lumos:57489`)、`_config_glob_error`(`scripts/lumos:57306`)、`_lens_git`、`_note_template_fill`、`_path_special_chars`、`nfc`。方向和鄰居一致,沒有跨層直呼。
- 本輪兩處修補都改成呼叫鄰居函式:
  - `_arch_tpl_scope_error` 先呼叫 `_config_glob_error`,它和 `review_roles`、`arch_targets` 本來共用同一支,所以這裡沒有再多出一種做法。
  - `_arch_tpl_legacy` 改用 `_arch_code_file`,和 `_arch_target_rule_index`(`scripts/lumos:57498`)用的是同一支判定。
- 找 repo 根的寫法是 `_lens_git(Path.cwd(), "rev-parse", "--show-toplevel")`,和 `cmd_spec_freeze`(`scripts/lumos:65454`)一樣。
- `git ls-files -z` 的呼叫方式和 `_arch_target_doctor_lines`(`scripts/lumos:57572`)一樣。
- 工具自帶檔清單登記在 `_VENDORED_TREE_FILES`(`scripts/lumos:31980` 附近)。
- 範本檔頭用 SPDX 加 `<!-- -->` 註解,和 `scripts/templates/note-audit-reread.md:1` 一樣。
- ⚠ 判不準:`_arch_tpl_scopes` 用 `f.startswith(s + "/")` 決定範圍內有哪些檔。鄰居的做法是 `_arch_target_rule_index` 加 `_glob_first_match`(`scripts/lumos:56737`)。範圍已禁萬用字元,所以兩邊結果應該相同。這是第二份「檔在不在範圍內」的判定。我沒有判成 finding。

**2. 命名與錯誤處理:對齊**
- 函式用 `_arch_tpl_*` 前綴,常數用 `_ARCH_TPL_*`,和 `_arch_legacy_*`、`_ARCH_LEGACY_REL` 的做法一致。
- 擋下訊息格式是 `print(f"擋下:…", file=sys.stderr)` 加 rc 2,和 `dispatch-lens` 的擋下訊息一致。`spec-freeze` 用的前綴是 `spec-freeze:`,屬於另一種格式,兩種在專案裡並存。
- 函式內 `import json as _j` 是專案常見寫法,全檔有 82 處。
- argparse 的 `dest` 用子命令前綴(`at_`),和 `freeze_`、`lens_` 同型。
- `HELP_WHEN` 的條目已補,和鄰居一樣是白話敘述加指令。
- 範本的日誌方式是只讀、印到終端,沒有寫檔,和 `spec-freeze` 不帶 `--out` 的行為同型。

**3. 第二種做法:大致沒有**
- 本輪修補沒有引入新的第二種做法,反而收斂到鄰居的共用函式。
- 唯一的疑點是 A11。範圍判定那點見上面的 ⚠。
- 產出的 Kotlin 和 `ArchitectureRulesTest.kt` 的差異如下。檔對照 `/Users/enzo/orca/workspaces/macrobench-lab-arch/app/src/test/java/com/example/mblab/arch/ArchitectureRulesTest.kt:1`。
  - 新增 `scopeDirs`、`repoRoot`、`legacyFiles`。
  - `layersDependOnlyInward` 從 `assertArchitecture` 改成比對 import。範本註解已寫明原因:`assertArchitecture` 在某一層沒有任何檔時整支失敗。
  - 手寫的舊檔清單解析器,註解說明是不為一個清單加 JSON 函式庫,符合專案零依賴的家規。
  - 測試名稱與沒有 DDD、用例省略時的規則文字,都是從舊範本拆開成按開關選用,命名一致。
- 這些差異都有註解交代理由,不是無理由的第二種寫法。
- 讀清單的逗號判定(結尾多逗號就讓測試紅)和 Python 端 `_arch_legacy_at` 的讀不懂就算 unreadable 方向一致。

總結:不對齊共 1 條,其中 major 0 條。
