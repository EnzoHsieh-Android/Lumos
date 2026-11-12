severity: minor

鎖檔 `…02.json.warming` 不存在(cat 回「No such file」),所以沒有鎖可處理。派工時 hook 只附了「這次沒附固定席節點」的備援段,我改讀 `lens-r3.txt` 當固定席。

**圖譜鏡頭(固定席逐條判)**
- `Systems/kotlin規則包.md` 是 check.py、scripts/lumos、test_lumos.py 的家。diff 只動 check.py 與 test_lumos.py,新增的 WHY 行與現況相符。沒有破壞它宣稱的行為。
- `pitfalls-code-loop`、`lumos-cli-read`(INVARIANT:search 預設排除 superseded)、`bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle` 都只因為牽連 scripts/lumos 而被點到。這份 diff 沒改 scripts/lumos,各條 INVARIANT 都不受影響。
- `bound-tests-gate` 要真跑合約綁的測試。我跑了 `kt_catalog_bad_snippets_reach`(47 過)、`kt_catalog_evidence_patterns`(11 過)、`template_fence_parity`(22 過)、`check.py --catalog-only`(0 問題),全綠。

## Findings

### 1. 註記行跳過規則收窄,有些整行註記不再被跳過
severity: minor
blocking: 否
引句:「_ANNOTATION_ONLY_RE = re.compile(r"^\s*(?:@[\w.:]+(?:\([^()]*\))?\s*)+$")」
file: `configs/ast-grep/kotlin-android/check.py:1127`(`nxt = next(...)` 那行用它);修前版 `startswith("@")` 在 `594f97e95:configs/ast-grep/kotlin-android/check.py`。
- **失敗情境:** `// BAD` 的下一行是整行註記但參數有巢狀括號、泛型或換行,例如 `@Foo(bar(1))`、`@Foo<Int>`、`@[Foo Bar]`、`@Foo(` 換行接參數。新碼不把它當註記,`// BAD` 就標到註記行本身,而不是它修飾的函式。
- **後果:** 片段(例如 `fun z`)對不上註記行,自檢報「片段沒落在標了 // BAD 的行」。這會大聲失敗,不會悄悄放過。
- **為什麼仍列:** 計劃與 docstring 寫的是「整行只有 @ 註記的行跳過」,實作比這句話窄。
- **現況影響:** 我掃了 `samples/bad/` 全部規則,修前修後共 536 筆 (檔, 行, 程式) 一模一樣,真樣本沒受影響。
- 兩版重現(同一支探針,載入 check.py 與 check_before.py,`_bad_lines(lm, 暫存目錄, "kt-x")`):
  - 輸入 `"// BAD\n@Foo(bar(1))\nfun z() = 3\n"`,修前 `[(3,'fun z() = 3')]`,修後 `[(2,'@Foo(bar(1))')]`。
  - 輸入 `@Foo<Int>`、`@[Foo Bar]`、多行 `@Foo(`,修前都標到第 3 行函式,修後都標到第 2 行註記。
  - 簡單的 `@Foo`、`@Foo("a(b")`、`@get:JvmName("x")`、`@A @B(1)`,修前修後都標到第 3 行函式。
- 歸因:有證據的修復回歸(僅限這幾種註記形狀,修前版 `startswith("@")` 會跳過它們)。測試只覆蓋 `@Foo` 與 `@Composable fun`,沒覆蓋這幾種。

### 2. 「三份行數對不上」的分支沒有測試也造不出輸入
severity: minor
blocking: 否
引句:「probs.append(f"壞例檔 {f.name} 去註解後行數對不上,判不了哪幾行標了 // BAD")」
file: `scripts/lumos:6869`(`_strip_c_comments(kotlin=True)` 的填法 `_strip_fill` 用 `x.count("\n")` 保行數)。
- **失敗情境:** 這個分支守的是三份行數一致。`_strip_fill` 對註解與字串區段都只換成同樣多的 `\n`,`raw` 與 `code`、`kept` 的行數沒有對不上的路徑。
- **後果:** 我試過未收尾字串、巢狀區塊註解、三引號字串,行數都一致。test_lumos.py 沒有讓這個分支執行的案例,上輪的案例清單 G2 卻列了「三份行數不一致回問題」。它守的是未來有人改 `_strip_fill` 的情況,現在沒有測試鎖住。
- ⚠ 沒找到能走到這個分支的輸入,無法證明它是死碼。
- 歸因:有證據的原有漏查。這個分支是這次修補新加的,不是修前就有。

## 三問的答案

**① 原問題的修復效果,行為證據**
- **換頁字元(G2):** 輸入 `"val s = 1 // a\x0cb\nval x = bar() // BAD\n…"`,修前版 `_bad_lines` 直接丟 `IndexError: list index out of range`,修後標到第 2 行 `val x = bar()`。
- **同檔其他案例,修後輸出** `[(2,'val x = bar()'), (5,'@Composable fun A(vm: Vm = viewModel()) { }'), (7,'val w = ""')]`:
  - 字串裡的 `// BAD`(第 3 行)不算標記。
  - `@Composable fun …` 標到同一行。
  - 行內 U+2028 後的行尾 `// BAD` 照認。
- **三引號字串(G2 相關):** 字串內單獨一行的 `// BAD`,修前標到 `"""` 收尾行 `(4,'"""')`,修後 `[]`。
- **沒關的圍欄(G3):** `"a\n```kotlin\n## T1 x\nb"` 在 keep_fenced=True 時,修後保留 `['a','## T1 x','b']`,最後一行 `b` 不再被丟,同 scripts/lumos 的 `_visible_lines`。對照測試 22 過,兩條路都比。
- **證據樣式測試(G1):** 11 過。決策表列數改只數〈情境決策表〉那一節。
- **G4 與 D-4 例外:** 只在測試與 `--catalog-only`(0 問題)層面確認,我沒另外造輸入跑修前修後。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- **正常:** 行尾 `// BAD`、`//BAD`、CRLF、無結尾換行、`/* // BAD */`、`// BADGE` 都跟修前一致。
- **相鄰:** 真樣本 536 筆零差異。keep_fenced=False 的圍欄判定,對照測試仍全綠。
- **有變化:** 發現 1 的註記形狀。

**③ 新發現的同一案例,修前與修後**
- 發現 1:修前跳過註記、標到函式,修後標到註記行,見上。
- 發現 2:修前沒有此分支,修後沒有案例觸發。

**未驗範圍**
- 全套測試。
- `--sg` 真 ast-grep 模式(我沒裝 0.51.1)。
- `kt_situation` 整組 145 與 `kt_catalog_stats_consistent`,沒重跑。
- 修前版的 G1、G3、G4 逐案輸出,沒跑。
- D-4 例外的實際推送前提醒行為,沒驗。

清理:我建立的 worktree 與暫存目錄已刪除,repo 根沒動。

總結:最高等級 minor,共 2 條
