severity: minor

三個問題都大致對齊。有 2 條小的不一致,結構都對,沒有第二種做法或跨層直呼。

**問 1 分層與依賴方向:對齊**
- 新增的 `_unpipe`、`_balanced_end`、`_one_annotation_end`、`_annotation_end`、`_next_statement`、`_bad_lines_in` 都放在 `check.py` 的 `_bad_lines` 之前,是同檔的純函式。
- 只有 `_bad_lines_in(lumos, text)` 用到 scripts/lumos。它沿用原本 `_bad_lines(lumos, …)` 把 `lumos` 當參數傳入、再呼叫 `lumos._strip_c_comments` 的方式(`check.py:1196` 附近)。
- 沒有出現第二種借用方式:沒有新增 import,也沒有全域載入 lumos。
- 新的圍欄檢查直接呼叫同檔的 `_fence_regions`(`check.py:1329`,定義在 `check.py:1409`)。`_visible_lines` 也是這樣呼叫它(`check.py:1439`)。
- 括號配對自寫在 `check.py` 內。`_fence_regions` 的 docstring 說明 `check.py` 零依賴、scripts/lumos 沒有 .py 副檔名而不能 import,這是既有的刻意分工。
- 括號計數式 `depth += (c == op) - (c == cl)` 和 scripts/lumos 的 `_drift_mask_settled` 一樣(`scripts/lumos:57584`、`scripts/lumos:60204`)。scripts/lumos 裡沒有現成可重用的 Kotlin 註記或括號配對函式,所以不算新做法。

**問 2 命名與錯誤處理:大致對齊,有 1 條小差異**
- `_BRACKET_PAIRS`、`_ANNOTATION_NAME_RE` 和既有的 `_BAD_MARK_RE` 同為底線開頭的模組常數。
- `_bad_lines_in` 回 `(清單, 問題或 None)`,和 `check.py:181`、`check.py:228` 的 `(值, 錯誤)` 形狀一致。
- `_next_statement` 找不到時回 None,也一致。
- 失敗哨兵不一致見下方 finding 1。

**問 3 第二種做法:大致對齊,有 1 條小差異**
- 修補只剩一套:
  - 舊的 `_ANNOTATION_ONLY_RE` 已整個刪除,repo 內沒有殘留引用。
  - `check.py` 裡只剩 `_unpipe` 內那一處 `.replace("\\|", "|")`,`_snippets` 和 `_unreach_table` 都改走 `_unpipe`。
  - 測試裡自己切節的程式改走 `kp._section`,沒有新舊並存。
- 測試造假 lumos 的寫法見下方 finding 2。

**1. 註記結尾函式的失敗哨兵和同組函式不同**

severity: minor
blocking: 否
引句:「括號到檔尾都沒關,當成不是註記,回 k。」
file: `configs/ast-grep/kotlin-android/check.py:1113`(`_balanced_end`,括號沒關回 None);同組的 `_one_annotation_end` 也是回 None;`_next_statement` 找不到也回 None。
具體代價:同一組新函式裡,兩支用 None 表示失敗,`_annotation_end` 卻回起始行號 `k`,而 `k` 本身也是合法回傳值(代表「不是註記」)。以後有人把它改成 `if end is None` 風格,就會判錯。

**2. 測試用類別加 `@staticmethod` 假裝 lumos 模組**

severity: minor
blocking: 否
引句:「class _MisLines:   # 去註解後多一行:三份行數對不上要報問題,不能照錯位的行判」
file: `scripts/test_lumos.py:5475` 用 `_ty.SimpleNamespace(run=fake, …)` 換模組成員;`scripts/test_lumos.py:54055` 用 `_types.ModuleType("_hookevent")` 加屬性造假模組。
具體代價:⚠ 判不準,請編排者定奪。`t_kt_catalog_*` 區段(126000~133000 行)沒有造假 lumos 的先例,全檔其他地方有 `SimpleNamespace` 和 `ModuleType` 兩種寫法,也有 `_ClkgFakes` 這種「類別當假物件」(`scripts/test_lumos.py:85144`)。所以「類別充當假模組」不算全新,只是和最近的鄰居寫法不同。我保守標為小問題,不算第二種做法。

總結:不對齊共 2 條,其中重大 0 條,最高等級 minor
