severity: minor

審查範圍:r1-snapshot.patch 全部,並對照 `/Users/enzo/orca/workspaces/lumos-toolchain/kt-rulepack-followups` 的現況檔。沒有讀圖譜節點,三問都是用程式碼對照。

### 1. 分層與依賴方向

對齊,沒有跨層直呼。

- test-guard 的 `_tg_kind` 和 room-guard 的 `_rg_grep`、`_rg_hunks`、`_rg_triggered`,新加的四處略過都重用同一個既有判定 `_RULEPACK_SAMPLE_RE`。沒有另寫比對。
- 這個 regex 是 `_stack_changed_ok` 早就在用的同一支:`scripts/lumos:61551` 定義,`scripts/lumos:61571` 在 `_stack_changed_ok` 裡使用。
- 對照 `_stack_changed_ok` 另一條略過 `governance/review-reports/` 的寫法(`scripts/lumos:61570`)。新碼是同樣的「函式開頭或過濾處先 `.match` 就略過」,形狀一致。
- 回傳值也和既有做法一致:`_tg_kind` 對不該看的路徑回 `None`,和同函式建置檔回 `None` 的寫法相同(`scripts/lumos:49697`、`scripts/lumos:49706`)。
- `check.py` 只改自己檔內的函式,沒有新增對 `scripts/lumos` 的依賴。
- `coroutines.yml` 新增的 `any` 分支,擺在 `coroutines.yml:133` 既有的加法分支旁邊,結構一樣。

### 2. 命名與錯誤處理

對齊。

- `scan` 解析失敗後回 `None`,由呼叫端報「跑不起來」。這和同函式既有的 `TimeoutExpired`、`OSError` 路徑一致:`check.py:247`、`check.py:250`、`check.py:253`。例外型別 `(ValueError, KeyError, TypeError)` 是常見寫法。
- 新註解的格式「(代碼審 r4 通才席 Finding 2)」,和 `coroutines.yml:133`、`rules/api.yml:193` 的既有引註格式相同。
- 新函式 `_strip_yaml_comment` 用底線開頭加動詞開頭,和 `check.py` 內其他輔助函式一致。
- 全形逗號修正與 `d` 改 `_d` 都屬於局部修正,不涉及慣例。
- 兩處無害的空行與排版差異,不列入。

### 3. 第二種做法

有一處近似重複,見 F1。除此之外沒有自創的工具函式。

### F1 `_strip_yaml_comment` 與 scripts/lumos 的 `_ci_strip_comment` 幾乎同一支

severity: minor
blocking: 否
引句:「def _strip_yaml_comment(ln):」

佐證行:`scripts/lumos:59925` 的 `_ci_strip_comment`(對照 `configs/ast-grep/kotlin-android/check.py:36`)

說明:

- 專案裡已經有「去掉不在引號裡的行尾 `#` 註解」的函式 `_ci_strip_comment`(`scripts/lumos:59925`)。
- 新函式的引號狀態機、`" \t"` 判斷、`rstrip` 都和它一模一樣。
- 唯一差別是新函式允許 `#` 在行首(`i == 0`)。因為 `_files_block_is_test_only` 原本靠整行註解被刪來處理,這是有意的差別。
- 這屬於同功能的第二份實作,但我不確定該判 major。理由有兩個:
  - `check.py` 是 `configs/` 底下獨立、零依賴的規則包自檢工具,現況沒有 import `scripts/lumos`(`check.py:11-17`)。
  - `scripts/lumos` 沒有 `.py` 副檔名,而且有幾萬行,從 `check.py` 直接 import 不自然。
- ⚠ 交編排者:要不要把「獨立工具不依賴 `scripts/lumos`」當成既有做法,由你裁。
  - 若當成既有做法,這條就是純 minor,建議在函式註解裡指向 `_ci_strip_comment`,避免日後兩份各自漂移。
  - 若認為該共用,就升 major。

不對齊共 1 條,其中 major 0 條
