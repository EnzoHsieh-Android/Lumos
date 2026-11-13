severity: major

## 1. 整行註記判讀只認一層括號,巢狀括號的註記行不再被跳過
severity: major
blocking: 是
引句:「_ANNOTATION_ONLY_RE = re.compile(r"^\s*(?:@[\w.:]+(?:\([^()]*\))?\s*)+$")」
file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py:1107`(patch 約第 52 行);計劃 `/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Projects/情境決策點窮舉與壞寫法要叫得出_計劃.md` 寫「整行只有 `@` 註記的行跳過」。

失敗場景:壞例檔寫成 `// BAD` 下一行 `@Foo(bar = baz())`、再下一行 `fun z() = 3`。註記的括號裡只要再有一層括號或呼叫,`\([^()]*\)` 就配不上,整行判成「有程式」。`// BAD` 因此標到註記行,不標到 `fun z()`。〈叫不出〉的片段在標記行上找不到,自檢會誤報。
同類輸入:`@Preview(device = Devices.of("a"), name = "n")`、`@Foo(a = listOf(1))`、`@Bar` 後面接 `@Foo(x(y))`。多行註記 `@Foo(\n a=1\n)` 會標到 `@Foo(`,但修前也是標錯行(標到 `a = 1`),所以不算新退步。

修前、修後各跑一次,輸入都是 `"// BAD\n@Foo(bar = baz())\nfun z() = 3\n"`,用 `_bad_lines` 比:
- 修前 `594f97e`:標到 `(3, 'fun z() = 3')`
- 修後 `6d53943`:標到 `(2, '@Foo(bar = baz())')`
- `@Preview(device = Devices.of("a"), name = "n")` 同樣是修前標第 3 行、修後標第 2 行。
- 修前版本用 `lstrip().startswith("@")`,所有 `@` 開頭的行都跳過。

我拿這兩版的 `_bad_lines` 跑了現有 228 條規則的全部壞例,結果沒有差異,所以目前不會讓推送閘紅。但任何新壞例只要註記帶巢狀括號,就會被這次修補誤判。

歸因:有證據的修復回歸(修前跳過、修後不跳過,同一輸入兩版輸出不同)。

## 2. 「三份行數對不上」的回報分支與片段格的 `\|` 還原沒有測試守
severity: minor
blocking: 否
引句:「probs.append(f"壞例檔 {f.name} 去註解後行數對不上,判不了哪幾行標了 // BAD")」
file: 測試在 `/Users/enzo/harness/lumos-d4-triggers/scripts/test_lumos.py` 的 `_reach_route_guards`(patch 約第 457 行起),沒有任何案例觸發這個分支。

失敗場景:我在副本逐項改壞,測試只守得住部分修補。
- 把 `if not len(raw) == len(code) == len(kept):` 改成 `if False:`,`-k bad_snippets_reach` 仍是 47 過 0 紅。
- 把 `_unreach_table` 非整格分支的 `.replace("\\|", "|")` 拿掉,同樣 47 過 0 紅。
- 另外五道改回舊寫法都會紅:註記判讀、字串裡的 `// BAD`、`splitlines` 換回、`whole` 判讀、`_visible_lines` 的 keep_fenced。這五道有測試守住。

這兩處沒被守住,而且很難造出會觸發的輸入:`keep_newlines` 讓三份行數天生相等,所以那條分支實際到不了。對 `\|` 還原來說,拿掉後只影響「整格沒有反引號、內含 `\|`」這種寫法,行為差異極小。

歸因:有證據的原有漏查(這兩處是修補一併帶進來的新碼,但行為上沒有可以和修前比較的輸入)。

## 已驗主張與證據

**① 原問題的修復效果**
- 字串裡的 `// BAD`:輸入 `val q = "see // BAD"`,修後不算標記(檔 c.kt 第 3 行不在結果內)。同一行 `val s = "// BAD" // BAD` 仍被認出,內容是 `val s = ""`。
- 換頁字元:前一行有 `\x0c`,`// BAD` 仍對到自己那一行。
- U+2028:同一行字串裡的 U+2028 不斷行,行尾的 `// BAD` 照認。
- `@Composable fun A()` 的「註記加同一行程式」:標到那一行,不跳過。
- 沒關的圍欄:用 20000 組隨機輸入比對 `check.py` 與 `scripts/lumos` 的 `_visible_lines`,keep_fenced 兩種都比,0 筆不一致。
- 範本小節圍欄沒關時,最後一行算進內文(測試過)。
- 片段格:反引號外有字的照整格原文;整格一段反引號的取內文。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- 邊界輸入都在修後版本實跑過,結果合理:
  - 標記在檔案第一行、最後一行、沒有換行的檔尾
  - CRLF
  - 連續兩個標記(兩個都標到同一行,無害)
  - 標記後只剩註解
  - 多行 raw string 裡的 `// BAD`(不算)
  - 行尾 `/* // BAD */`(算,因為在註解裡)
  - 字元常值
- 現有 228 條規則的全部壞例,修前修後 `_bad_lines` 輸出一致(0 筆差異)。
- `--catalog-only` 回報型錄問題 0 個。
- 測試通過:
  - `-k bad_snippets_reach`:47 過
  - `-k evidence_samples`:25 過
  - `-k template_fence_parity`:22 過
  - `-k evidence_patterns`:11 過
  - `-k api_decision_points`:38 過
  - `-k kt_catalog_stats_consistent`:128 過

**③ 同一案例在修前、修後的結果**
- 只有 finding 1 在兩版結果不同,數據見上。
- 其餘修補點修前的逐案輸出編排者沒保存,我只跑了修後;其中字串 `// BAD`、換頁字元、`@Composable` 這幾條,是靠改壞副本(改回舊寫法)看到測試變紅,間接證明修補有效。

**配對案例(repair / preserve)**
- G1(證據樣式測試只數決策表那一節):`_dt0` 和 `_i_dt` 的找法會在標題被改名時讓測試紅,不會悄悄過。型錄「## 情境決策表」之後的下一節是「## 待查證」,中間的 D- 列為 740–799,與〈叫不出的壞寫法〉的 D- 列(1521–1592)分開,所以切節正確。
- G2、G3、G4 和 D-4 例外(含 `flatMapMerge`):對應測試全綠,改壞都紅(只有 finding 2 提到的兩處例外)。
- preserve:`//BAD`、`// BADGE`、`// BAD-NEXT` 續行、整行 `@Foo` 跳過、非 UTF-8 回問題,對應既有案例全綠;`keep_fenced=False` 的圍欄判定與 `lumos` 逐項一致。

**未驗範圍**
- `--sg <ast-grep>` 的完整規則自檢沒跑,本機沒有 ast-grep。
- 整套測試(`kt_situation` 整組 145 等)沒跑。
- 孤立 `\r` 換行:`read_text` 會把它轉成 `\n`,與 docstring 說的「只照 `\n` 切」略有出入。這種檔實際不存在,不報。

**pitfalls 表態**
- 這份 diff 是 Python 自檢腳本加文件,沒有事件迴圈、並行、外呼,答 na 合理。
- 記憶體、熱路徑答 satisfied 也合理:每個壞例檔多掃兩遍,而且逐檔處理。

**圖譜鏡頭**
- hook 沒附固定席節點,範圍計算超時。我也沒讀 `lens-r3.txt`(派工詞指的備援檔)。
- 改到的筆記是 `Systems/kotlin規則包.md` 和計劃筆記。新增的 WHY 行(D-4 例外收 `flatMapMerge`)與程式、型錄一致,沒有破壞宣稱的行為或合約。
- 計劃寫「整行只有 `@` 註記的行跳過」,與 finding 1 的程式行為不符,這是 finding 1 的文件側影響。

**角色鏡頭**
- `be-api-compat`:改動只在自檢與型錄,不碰對外 API,不適用。
- `be-authz`:無端點,不適用。

**暫存清理**
- 我建立的兩個 worktree 和實驗目錄已用字面絕對路徑刪除,測試留下的 6 個 `gctl-run-*` 現場也已刪除。
- 其他 `gctl-run-*` 目錄不是我建立的,沒有動。

總結:最高等級 major,共 2 條
