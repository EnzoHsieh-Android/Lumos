severity: minor

整體結構跟鄰居對得上:設定讀法、退出碼、擋下訊息、`_stack_changed_ok` 的排除、`node_home.ignore` 的用法都沿用既有做法。不一致處有兩條 minor,另有一條 ⚠(YAML 與表格解析重寫),我判 minor 而不是 major。

## 問 1:分層與依賴方向

大致一致。

- **獨立檔放在 `configs/` 下,測試動態載入它。** 這跟既有的 `scripts/scenario_probe.py` 一樣:測試用 `spec_from_file_location` 載入一支獨立 Python 檔。
  - file: `scripts/test_lumos.py:884`、`scripts/test_lumos.py:966`、`scripts/test_lumos.py:1065`,都是這種載入法。
  - 新碼 `_ktpack()` 沿用同一種載入方式,不算第二種做法。
- **依賴方向單向。** `check.py` 零依賴(標準庫),不回頭 import `scripts/lumos`。`scripts/lumos` 只新增 `_RULEPACK_SAMPLE_RE`、`include_test_paths` 與 `_LINT_MSG_SHOW`,沒有跨層直呼 `check.py`。
- **新增告警閘改動沿用既有管道。** `_lint_new_tools` 把 `cfg["include_test_paths"]` 傳進 `_stack_changed_ok(..., keep_test_ext=...)`。其他呼叫端不給參數,維持舊行為。
- **每支檔有家的略過走既有機制。** 新增的 `node_home.ignore` 項目由 `_cochange_excluded` 消費。
  - file: `scripts/lumos:44327`(`_nodehome_config` 本來就有 `ignore` 欄位)。
  - file: `scripts/lumos:59772`(`_cochange_excluded` 的定義)。
- **CI 補裝步驟寫法與既有步驟相同。** 新步驟 `python -m pip install --quiet ast-grep-cli==0.51.1` 跟既有的 `ruff==0.16.7` 同格式。
  - file: `.github/workflows/ci.yml:73`。
- **共用設定檢查的位置不同。** 鄰居 detekt 的共用設定檢查函式 `_detekt_config_problems` 寫在 `scripts/test_lumos.py`,自檢邏輯放在測試檔裡。
  - file: `scripts/test_lumos.py:37384`。
  - 規則包把自檢做成 `configs/` 下 289 行的獨立可執行檔(`check.py`,有 CLI 旗標、有退出碼)。
  - 這是專案內第一支放在 `configs/` 的 Python,但載入方式有先例,而且 `--catalog-only` 與 `--sg` 有獨立使用場景,所以只提醒、不列入條數。

## 問 2:命名與錯誤處理

結構對,兩處小不一致。

- **命名一致。**
  - 測試函式用 `t_` 前綴,並重用 `_lng_module`、`_lng_repo`、`_lng_declare`、`_lng_fake_linter` 等 lint-new 測試輔助函式。
  - 常數用 `_UPPER` 前綴,跟 `_LINT_NEW_*` 同風格。
- **設定壞值的處理一致。** 壞值就「照沒設處理並放進 `cfg["warnings"]`」。
  - file: `scripts/lumos:39486` 前後的 `budget_sec` 等鍵用的就是這個模式。
  - 新鍵 `include_test_paths` 同樣如此。
- **退出碼一致。** `check.py` 用 0 / 1 / 2,與 `scripts/scenario_probe.py` 的 `return 2`(`scripts/scenario_probe.py:1434`)和 `scripts/merge-claude-settings.py` 的 `sys.exit(2)`(`scripts/merge-claude-settings.py:32`)同風格。

**finding 1:本機沒裝工具時的略過寫法,跟鄰居不一樣。**
severity: minor
blocking: 否
引句:「print("  ⊘ 本機沒裝 ast-grep,略過(CI 會跑)")」
file: `scripts/test_lumos.py:37437`
- 鄰居 detekt 測試在本機缺工具時的做法是:先把靜態那半跑完,再印一行 `(本機沒有 detekt,只跑了靜態那半;...)`。
- 其他略過提示也都用括號行(`scripts/test_lumos.py:24750`、`scripts/test_lumos.py:30161`)。
- 新碼用了專案其他地方沒有的 `⊘` 符號,並且 `t_kotlin_rulepack_samples` 與 `t_lint_new_astgrep_kotlin_two_files` 在缺 ast-grep 時整支提早 `return`,連不需要 ast-grep 的靜態檢查也沒跑。
- 靜態檢查(`message_problems`、`catalog_problems`)另外有 S2、S3 兩支測試跑,所以實際覆蓋沒掉,只是寫法不同。

**finding 2:CI 判定方式在專案裡是新做法。**
severity: minor
blocking: 否
引句:「if not sg and _os.environ.get("CI"):」
file: `scripts/test_lumos.py:20866`
- `scripts/test_lumos.py:20866` 與 `scripts/test_lumos.py:20926` 的慣例,是把 `CI` 當成要從環境剝掉的變數,測試不依 `CI` 分流。
- 新輔助函式 `_ktpack_sg` 開了「CI 上缺工具就判紅、本機缺就略過」的分流,且新增 `LUMOS_AST_GREP` 環境變數。
- 這在 detekt 鄰居不存在:detekt 缺工具時不論 CI 與否都略過。
- 用意是正當的(`.github/workflows/ci.yml` 已釘版本安裝),但屬於命名與錯誤處理上的不一致,不是結構問題。

## 問 3:第二種做法

⚠ 判不準,我標 minor。

**finding 3:⚠ `check.py` 自寫了一套 YAML 規則檔與 markdown 表格的解析。**
severity: minor
blocking: 否
引句:「_CELL_RE = re.compile(r'(?<!\\)\|(?=(?:[^`]*`[^`]*`)*[^`]*$)')   # 反引號裡的直線不算欄位分隔」
file: `scripts/lumos:38942`
file: `scripts/lumos:51741`

- **YAML 讀法:**
  - 專案已有 `_RULE_ID_LINE_RE` 與 `_rules_ids_from_yaml_text`,它們也是「沒有零依賴 YAML 解析器所以用行級比對」,專案裡已有這個註解當先例。
  - `check.py` 的 `load_rules` 另用 `re.split(r"^---\s*$")` 加 `^id:` / `^severity:` / `^message:` 的行級正則,屬於同一做法的另一份實作。
  - 它還要抽 `severity`、`message`、`files`,`_rules_ids_from_yaml_text` 只回 id,不能直接沿用。
  - `check.py` 是零依賴獨立檔,不 import 單檔的 `scripts/lumos`,所以沒有現成介面可以共用。
- **markdown 表格切格:**
  - 專案已有 `ln.strip().strip("|").split("|")`(`scripts/lumos:27707`、`scripts/lumos:51741`)。
  - `check.py` 另寫了 `_CELL_RE`,多處理「反引號裡的直線不算分隔」。這是為型錄儲存格含 `` `a|b` `` 而加的,既有的簡單切法處理不了。
  - 屬於同功能的第二份實作。
- **為什麼不判 major:**
  - 這不是引進新的設定讀法,而是在新獨立檔裡重複既有的啟發式做法。
  - 既有版本的能力不夠用,需要的功能(多文件分隔、反引號內直線)確實不同。
  - 沒有跨層直呼。
- 若審查方認為「專案已有同功能」應直接升 major,請以此條為準。

## 另外確認過、對齊的點(不計條數)

- 把 `include_test_paths` 這個副檔名清單轉成 `frozenset` 並正規化(去前導點、轉小寫),跟其他鍵的整數驗證形狀不同,但屬於清單型設定,合理。
- 擋下訊息截斷從 70 改成 `_LINT_MSG_SHOW = 120`,註解寫明跟 `_lint_run_and_parse` 解析 SARIF 時的截斷同數,對齊。
- `_stack_changed_ok` 新增 `_RULEPACK_SAMPLE_RE`,跟既有的 `governance/review-reports/` 排除放在同一個函式、同一種寫法(都是審計或教材證物不當產品碼)。這是 `_stack_changed_ok` 既有排除的擴充。

不對齊共 3 條,其中 major 0 條
