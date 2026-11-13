severity: minor

## 1. 註記行的括號只認一層,常見的多層註記會讓 `// BAD` 標到註記行本身
severity: minor
blocking: 否
引句:「+_ANNOTATION_ONLY_RE = re.compile(r"^\s*(?:@[\w.:]+(?:\([^()]*\))?\s*)+$")   # 整行只有註記(可帶一層括號參數)」
file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py:1112`(`_bad_lines` 裡 `nxt = next(...)` 那行用它判斷要不要跳過)
- 輸入與走法:單獨一行 `// BAD` 後面接 `@Preview(name = stringResource(R.string.a))`、`@Foo(x = bar())`,或跨行的 `@Foo(` 加 `  1)`。
- 這些行不符合 `[^()]*`,所以不再被當成「整行只有註記」,`// BAD` 就標到註記行。
- 錯成什麼:標記對到註記行,不是它修飾的 `fun`。片段是 `fun` 內文的規則單位會被誤報成「片段不在 BAD 行」。
- 只要註記行有 `bar()` 之類的字,片段 `bar()` 又可能誤中註記行。
- 實測,修前與修後的 `_bad_lines` 輸出:
  - `@Foo(x = bar())`:修前 `[(3,'fun z() = 3')]`,修後 `[(2,'@Foo(x = bar())')]`。
  - `@Foo(` 跨行:修前 `[(3,'1)')]`,修後 `[(2,'@Foo(')]`。
- 修前跳過所有 `@` 開頭的行,所以修後對這類註記是行為改變,對 `@Composable fun A() {}` 這種同行接程式的才是真修復。
- 範圍:228 支真壞例檔修前修後輸出逐檔相同,目前沒有真實受害樣本。
- 計劃與 docstring 已寫明「一層括號」,所以這是已知限制,不是文件與程式不符。
- 測試:沒有案例涵蓋巢狀括號註記。
歸因:有證據的修復回歸(上述兩輸入修前走 `startswith("@")` 跳過、修後不跳;指令:用 `/tmp/lumos-seat-work/code-情境決策點窮舉/邊界-sonnet/cmp.py` 載入 `594f97e` 版 check.py 與工作目錄版,對同一份輸入各跑一次 `_bad_lines`)

## 2. 〈叫不出〉片段格非整格的分支,`\|` 還原沒有測試守
severity: minor
blocking: 否
引句:「+        rows.append((c[0], c[1], sn[0] if whole else c[2].replace("\\|", "|"), c[3], c[4]))」
file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py:1081`
- 在副本(我自己複製出來的目錄,不是 repo)把 `c[2].replace("\\|", "|")` 改成 `c[2]`,跑 `-k bad_snippets_reach`,結果 47 passed、0 failed,沒有任何案例變紅。
- 新案例只驗了 `` `a` 垃圾 `` 保持原樣,沒有含 `\|` 的非整格(如 ``x `a\|b` y``、``` `a\|b` `c` ```)。docstring 與 diff 說明都宣稱「兩種都做 \| 還原」,這半句沒有測試保護。
- 行為本身是對的(修前 ``x `a\|b` y`` 保留 `\|`,修後還原成 `|`)。被保護的只是錯誤訊息與比對的字面,所以只算覆蓋面。
- 另外 `if not len(raw) == len(code) == len(kept)` 的問題分支也沒有測試。我把它換成 `if False` 後測試照綠。
- 用 30000 筆隨機 Kotlin 片段(含 `\r`、U+2028、未閉合字串與區塊註解)跑三份行數,沒有一筆不一致,所以這是防禦碼,不是會誤報的路徑。
歸因:有證據的原有漏查(新增的碼本身沒有對應案例)

## 3. 範本小節的圍欄沒關時,內文與組界一路外洩到檔尾
severity: minor
blocking: 否
引句:「+                hidden.update({a} if b is None else {a, b})」
file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py:1166`(`_fence_body` 取組界的 `b` 用 `template_sections`,只認圍欄外的 `## T` 標題)
- 輸入:T2 的 `### 壞寫法:API-1` 圍欄沒關,後面還有 `### 壞寫法:API-9` 與 `## T3`。
- 走法:CommonMark 把這些後續標題都當圍欄內文,`_fence_body(t,"T2","API-1")` 回傳 `val a = 1\n### 壞寫法:API-9 z\nval secret = 2\n## T3 q\n### 壞寫法:API-1 w\n...`。
- 錯成什麼:T2 的內文含到 T3 的程式。只出現在 T3 或其他編號的片段會被判成落在 T2 的 API-1 小節,「範本 T2」這種改由會誤過。T3 自己的 `_fence_body` 回傳空字串,反而報問題。
- 影響:這個修補讓最後一行不再被丟,方向正確,但沒處理沒關圍欄之後的外洩。
- 目前型錄沒有任何「範本」改由單位(統計為 0),實際影響為零,所以只算 minor。⚠ 這是不是該擋沒關圍欄的範本檔(而不是容忍),屬設計取捨,我判不準。
歸因:有證據的原有漏查(修前同樣讓後續內容外洩,只是少算最後一行)

## 已驗主張與證據

1. 原問題的修復效果:
   - 換頁字元、U+0085、U+2028、VT 在 `//` 註解中:修前 `[]`,修後 `[(2,'val x=1')]`,對到正確的行。
   - 字串裡的 `// BAD`(`val q = "see // BAD"`)不再算標記,同一行字串和註解各一個仍認註解。
   - 多行 raw string 內獨立一行 `// BAD` 不算標記。修前 `raw_then_bad` 會多出 `(1,'val s = """')`,修後只剩第 2 行。
   - `@Composable fun A(vm: Vm = viewModel()) { }` 標到該行,不再跳過。
   - 圍欄沒關時 `keep_fenced=True` 保留到檔尾。我拿 20000 組隨機圍欄排列(``` / ~~~ / 縮排 / 標題行)對 `scripts/lumos` 的 `_visible_lines`,keep 兩個值各比一次,差異 0。
   - 非整格的片段格不再吞尾巴:`` `a` 垃圾 `` 保持原文。
2. 修補處的正常、錯誤與相鄰呼叫路徑:
   - 空檔、只有一行 `// BAD`、檔尾沒換行、CRLF、純 `\r`、BOM 開頭、標記在最後一行、`/* // BAD */`、巢狀區塊註解、`@Foo // 說明`、多註記疊行,結果與修前相同或更正確,沒有崩潰。
   - 區塊註解 `/* // BAD */` 內的標記仍算標記,與修前一致,符合「要在註解裡」。
   - `--catalog-only` 0 個問題。測試結果:`bad_snippets_reach` 47 過,`kt_catalog_evidence_patterns` 11 過,`template_fence_parity` 22 過。
   - 228 支真壞例檔的 `_bad_lines` 輸出修前修後逐檔相同。
3. 同一案例修前修後(請見 finding 1 的對照)。不同案例的證據都在上面各條。
4. 測試是不是「只有該修補會擋」,在副本逐項改回舊寫法後的結果:
   - 還原成 `splitlines()`:變紅,主要因為真型錄多出「行數對不上」。
   - 把「標記數多於只去註解版本」改成只看 `search(ln)`:字串內標記案例變紅。
   - 把註記判斷改回 `startswith("@")`:「@ 註記加同行程式」案例變紅。
   - 把整格判斷改回 `startswith("`")`:變紅。
   - `keep_fenced` 改回舊寫法:`template_fence_parity` 變紅。
   - 兩個沒變紅的見 finding 2。
5. 固定席:hook 沒附上席節點,我改讀 `lens-r3.txt`。該檔列出 `kotlin規則包` 家節點與 `bound-tests-gate`、`pitfalls-code-loop` 等 INVARIANT。這份 diff 只動 check.py、一份樣本、型錄文字和 jvm-only 註解,不碰 `scripts/lumos` 與這些合約的程式路徑,所以我判不影響。純文字行(WHY、依據來源)不改行為。

未驗範圍:
- `--sg` 實跑 ast-grep 的起訖行涵蓋。
- 完整 `kt_situation` 組(145 案)與 `kt_catalog_stats_consistent`。
- 修前逐案原始輸出沒保存,所以修前行為是我拿 `594f97e` 版 check.py 重跑得來。
- 純 `\r` 檔與 ast-grep 的行號對不對沒有驗。
- 一百萬字元級的輸入只量到 `// BAD` 連續行是 O(n²)(2 萬行約 5.8 秒),修前修後相同,不是這次引入。

總結:最高等級 minor,共 3 條
