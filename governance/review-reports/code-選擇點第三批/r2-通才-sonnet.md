severity: minor

## g1 C-38/C-39 的「立刻 .await()/.join() 不算子協程」排除範圍過寬,漏掉先併發再等待的作用域
severity: minor
blocking: 否

引句:「建立後同一個運算式就 .await()/.join() 的不算(做完才開下一支,兩種作用域必然等價;同 C-50 只看直接接在後面那一層,包在別的呼叫引數裡的照算;代碼審 r1 g1)」

- 輸入:`supervisorScope { launch { g() }; val a = async { f() }.await() }`,以及把 `supervisorScope` 換成 `coroutineScope` 的版本。
- 走到的行:`child-co` 新增的 `not: inside: navigation_expression has navigation_suffix .await|.join`。`async { f() }.await()` 被排除,作用域內只剩 `launch { g() }` 一個子協程,`many-co`(要兩個以上)不成立,所以不命中。
- 為什麼這算錯:`launch { g() }` 先開、不等,會和後面那支一起跑,所以「必然等價」只在被等的那支排在前面時成立。這個輸入裡 `g()` 失敗時,`coroutineScope` 會取消 `f()`,`supervisorScope` 不會,兩種作用域的行為並不相同,正是 C-38、C-39 要問的那個需求問題。
- 對照 `supervisorScope { val a = async { f() }.await(); launch { g() } }`(等完才開下一支):這個才是真等價,不命中是對的。排除條件沒有分先後。
- 歸因:有證據的修復回歸。
- 查證:用 ast-grep 對同一個 4 行檔分別掃 763081c(修前)與 926c720(修後)的 `configs/ast-grep/kotlin-choice/sgconfig.yml`。
  - 修前:C-39 第 3 行、C-38 第 2 行、C-38 第 4 行都命中。
  - 修後:C-38、C-39 全部沒有命中。
  - 第 2、3 行是不該丟的命中,第 4 行丟掉才對。
- 附帶:新增的樣本和測試只覆蓋「等完才開下一支」的順序,沒有「先開不等、再等一支」的反例,所以現有測試抓不到這個回歸。
- 重現:未能當場翻紅(沒有現成測試會紅),但上述指令可重現規則行為差異,因此降為 minor。

## 已驗主張與未驗範圍

- **已驗,測試全綠**:在 926c720 的獨立 worktree 跑 `python3.14 scripts/test_lumos.py -k` 六組。
  - `choice_scope_rule_output`:14 passed,
  - `choice_samples_batch3`:40 passed,
  - `choice_points_batch3`:37 passed,
  - `choice_points_nul`:12 passed,
  - `choice_points_compose`:7 passed,
  - `choice_points_batch2`:8 passed。
- **`_cb_points` 取代 `_cb2_points`、`_cb3_points`**:
  - 沒裝 ast-grep 時,第二批照舊回 None,第三批用 `skip=` 照舊 raise `_SrcOnly`。
  - 暫存目錄改用 `TemporaryDirectory`,原本不清暫存,現在會清,是改善。
  - grep 確認 926c720 的 `scripts/test_lumos.py` 裡已無舊名稱的殘留呼叫。
- **`_CB3_S7_PIN`**:用 `ast.literal_eval` 比對,和 `_CB2_S7_PIN` 逐筆相同(82 對 82)。
- **`_choice_err_start`**:行為和原本寫在行內的條件式等價。
- **「方法名」錨點改用 `_CHOICE_CALL_NAME_RE.match(b, s, e)`**:取回的位移是整份檔案的絕對位置,和舊寫法 `hit["s"] + m.start(2)` 結果相同。
- **C-48 的 `zero-int` 與 SUSPEND 排除**:沒發現其他問題。
- 未驗:C-48 的 `(0)` 括號寫法(作者已寫明不認)、`onBufferOverflow` 給變數的保守排除、其他 CLAUDE.md 慣例。
- 臨時 worktree 與目錄已刪。

總結:最高嚴重度 minor,blocking 共 0 條
