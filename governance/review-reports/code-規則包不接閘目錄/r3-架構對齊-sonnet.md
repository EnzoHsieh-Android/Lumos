severity: clean

這份 diff 沒有引入第二種做法或跨層直呼。三問都對得上既有寫法,所以沒有 F 條目。我只讀了 diff 與 repo 的對照處,沒有重跑測試。

## 1. 分層與依賴方向
- 新的 `sarif_gate_rule_ids` 借用 `scripts/lumos` 的 `_lint_run_and_parse`,走的是既有的 `load_lumos()` 動態載入,沒有新增 import 路徑。
  - 對照:`check.py` 的 `load_lumos` 在 `configs/ast-grep/kotlin-android/check.py:432`,既有借用 `lm._kt_sit_row_check` 在 `check.py:459`,`lumos._kt_sit_text_segments` 在 `check.py:500`。這幾處同樣呼叫底線開頭的函式,方向一致。
  - 新呼叫在 `check.py:728`。
- 新增的 `rules-unwired` 目錄靠 `CONFIGS`、`_DIR_SEVERITY` 兩張表接入,`load_rules`、`loaded_count`、`scan` 都沒加特例。
  - 對照:`rules-hints` 與 `rules-review` 的接法在 `check.py:25` 前後。
  - 我在 repo 內查了 `rules-hints` 與 `sgconfig-hints` 的出現處,程式端只有 `check.py` 與 `test_lumos.py`,沒有別的硬編目錄清單需要跟著補。

## 2. 命名與錯誤處理
- `sgconfig-unwired.yml` 與 `rules-unwired/` 的命名和 `sgconfig-hints.yml`、`rules-hints/` 同形。
- 錯誤處理沿用既有寫法:回傳 `(None, 原因)` 而不丟例外,問題以 `("<pack>", 訊息)` 元組收集,並用 `_TIMED_OUT` 做逾時短路。
  - 對照:`check.py:682` 與 `check.py:740`。
- 載入失敗的訊息寫法和情境題自測的 `證據樣式自測要載入 scripts/lumos:` 同形(`check.py:477`)。
- `sarif_gate_rule_ids` 內的 `import time` 是函式內區域 import。`load_lumos` 內的 `importlib` 也是這樣寫(`check.py:434`),有先例。
- 新測試的暫存目錄用 `tempfile.mkdtemp(prefix="gctl-ktsg-")`,前綴與同函式既有的 `wrap`、`slow`、`junk` 一致(`scripts/test_lumos.py:126412` 起)。
  - 新測試比既有的多做了 `shutil.rmtree` 清理,符合全域暫存清理規則,算改善。
  - 區域 `import shutil` 在檔內也有先例:`scripts/test_lumos.py:3699` 用 `import shutil`,其他地方用 `as _sh`,兩種並存。

## 3. 第二種做法
- 「出處不全只准放 rules-unwired」改寫了 `catalog_problems` 裡原本的 hint 判斷(`check.py:~396`),是在原處改規則,沒有另開一套檢查。
- 新測試 `t_kotlin_rulepack_unwired_dir` 的寫法與既有 `t_kotlin_rulepack_messages_cite_catalog` 同形:假規則字典、`check()` 斷言、預期值來自造的資料。
- SARIF 探針的測試也是用假 `sg` 腳本(含 `--format sarif` 分支)包住真 `sg`,和同函式內既有的 `junk`、`slow` 假 `sg` 做法相同。

不對齊共 0 條
