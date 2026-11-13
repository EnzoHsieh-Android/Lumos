severity: minor

審查範圍:修前 8cd6d3c → 修後 594f97e。我把兩版各用 `git archive` 解到 `/tmp/lumos-seat-work/code-情境決策點窮舉/合約-sonnet/{before,after}`,沒動 repo。沒有 ast-grep,所以完整 `--sg` 模式沒跑。

修後版我實跑了這些:`check.py --catalog-only` 回 0 個問題;`-k api_decision_points` 38 過;`-k bad_snippets_reach` 41 過;`-k evidence_samples` 25 過;`-k stats_consistent` 128 過;`-k api_family_e2e` 4 過。修前版只跑了 `--catalog-only`,也是 0 個問題。

派工詞沒附固定席節點,範圍計算超時。我已讀 `/tmp/lumos-seat-work/code-情境決策點窮舉/lens-r2.txt` 的位置,但派工詞說照審即可,沒另外補算。

## findings

1. D-4 例外寫法加了 flatMapConcat,搜尋框用它並答「例外」時不再收到提醒
severity: minor
blocking: 否
引句:「// === bad main 搜尋框用 flatMapConcat、沒有 debounce(觸發字只能靠操作符本身;只對標準寫法算錯)」
file: `skills/kotlin-idioms/checks-catalog.md:743`(D-4 證據樣式例外欄多了 `\bflatMapConcat\b`)、`scripts/lumos:73706`(`_kt_sit_row_verdict` 只拿作者宣告的那個 variant 的樣式核對)
具體失敗場景:
- 搜尋框寫 `query.debounce(300).flatMapConcat { repo.search(it) }`,這是 API-8 點名的壞寫法。
- 作者把 variant 答成 alt,例外樣式現在對得上,不提醒。修前這行對不上,會提醒。
- 這條 flatMapConcat 樣本原本對 main、alt 兩邊都算反例,現在只對 main 算,alt 那邊的守衛是修補自己拿掉的。
- 計劃(第 92 行與 S5/S2 列)和 `Systems/kotlin規則包.md` 的 PITFALL 都只寫「主寫法加 mapLatest、transformLatest」「反例補兩段」,沒記下例外樣式放寬這個取捨。
重現(修前→修後):對 `line='val results = query.debounce(300).flatMapConcat { repo.search(it) }'` 逐條 `re.search` D-4 的證據樣式。
- 修前:`{'main': [False], 'alt': [False]}`
- 修後:`{'main': [False], 'alt': [True]}`
歸因:有證據的修復回歸。

2. 驗證紀錄的測試案例數只改了一個,另兩個是舊數字
severity: minor
blocking: 否
引句:「`kt_catalog_stats_consistent` 128、`kotlin_rulepack_samples`(帶 LUMOS_AST_GREP)28,全過」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-12_情境決策點窮舉實作驗證.md:25`
具體失敗場景:
- 同一行還寫著 `api_decision_points` 28、`bad_snippets_reach` 22,但修補新增了測試。
- 我實跑 `-k api_decision_points` 是 38 過,`-k bad_snippets_reach` 是 41 過。
- 三個月後的人拿這行數字當基準,會誤判案例被刪。
歸因:有證據的修復回歸(修補只改了 stats_consistent 的 106→128,其餘沒跟著改)。

3. `Default` 指向 CO-39,但 CO-39 管的是共享集合,不是選調度器
severity: minor
blocking: 否
引句:「Default | 決策不問 CO-39 | 選 CPU 執行緒池;CO-39 的壞寫法片段 async(Default) 用的就是這個調度器」
file: `skills/kotlin-idioms/checks-catalog.md:1190`;對照 `:1202`(`Dispatchers`→CO-1)、`:1290`(`IO`→CO-1)
具體失敗場景:
- 照表判 `withContext(Dispatchers.Default)` 是否寫死調度器,`Default` 這列把人導到 CO-39(協程裡改非執行緒安全集合)。
- 同類的 `IO` 指向 CO-1(可注入調度器),CO-1 才是管這件事的列。
- 指向 CO-39 只是因為自檢要求被指的列的壞寫法片段含整字 `Default`,而 CO-1 的片段只寫 `Dispatchers.IO`。
- 理由改寫成「用的就是這個調度器」,把遷就機械判法的指向包裝成語意理由。
歸因:有證據的原有漏查(`:1187` 修前就指 CO-39,理由是「太常見不當觸發字」);修補把理由改寫,指向沒改。

4. `_bad_lines` 用兩種切行法,遇到 `\x0c` 或 U+2028 會錯行
severity: minor
blocking: 否
引句:「code = lumos._strip_c_comments(text, blank_strings=True, keep_newlines=True, kotlin=True).split("\n")」
file: `configs/ast-grep/kotlin-android/check.py` 的 `_bad_lines`(同函式 `raw = text.splitlines()`)
具體失敗場景:
- `raw` 用 `splitlines()`,`code` 用 `split("\n")`,遇到壞例檔含 `\x0c` 或 U+2028 時兩邊行數不一致。
- 實測 `'val a = 1\x0c\nval b = 2 // BAD\n'`:`raw` 有 3 行、`code` 只有 2 行,`code[2]` 取到空字串,這個 `// BAD` 被當成單獨一行標記,找不到下一個語句,整個被丟掉,`_bad_lines` 回 `([], [])`。
- 實測 `'val a = 1\u2028val b = 2 // BAD\n'` 同樣回 `([], [])`。
- 結果是該規則的 `規則` 改由報「片段不在 // BAD 行」,病因藏在行數對不齊。
- 行號用 `splitlines` 算,也會跟 ast-grep 的行號對不上。
- 實際壞例檔出現這種字元的機率很低。
歸因:有證據的修復回歸(修前只有 `splitlines` 一個行來源)。

5. `_visible_lines(keep_fenced=True)` 在圍欄沒關時丟掉最後一行,跟 scripts/lumos 不同
severity: minor
blocking: 否
引句:「hidden.update({a, end} if keep_fenced else range(a, end + 1))」
file: `scripts/lumos:5407`(`if i == start or i == end or not keep_fenced`,沒關的圍欄 end 是 None,最後一行保留);check.py 的 `_visible_lines` docstring 寫「同 scripts/lumos 的 keep_fenced」
具體失敗場景:
- check.py 把沒關的圍欄的 `end` 設成 `len(lines) - 1`,於是最後一行被當標記行丟掉。
- 實測範本 `"## T2 x\n### 壞寫法:API-8 y\n```kotlin\nval a = 1\nval last = 2"` 丟給 `_fence_body`:
  - 修前回 `'val a = 1\nval last = 2'`
  - 修後回 `'val a = 1'`
- 範本檔尾圍欄沒關時,`範本 T<n>` 改由會漏掉檔尾那行,可能判成「片段不在範本」。
- 現在型錄裡範本改由是 0 個,所以目前沒人踩到;docstring 已經不實。
歸因:有證據的修復回歸。

6. JVM 專屬的 6 個型別收了,但它們的成員沒收
severity: minor
blocking: 否
引句:「ThreadContextElement | public abstract interface class kotlinx/coroutines/ThreadContextElement」
file: `configs/ast-grep/kotlin-android/coroutines-api/jvm-only.txt:23`;JVM 清單 `kotlinx-coroutines-core-1.10.2.api` 的 ThreadContextElement 區塊
具體失敗場景:
- 我拿 `_api_names` 的 434 個名稱對 JVM 清單比對。公開型別都有了,只剩 `DefaultImpls`、`Key`、`Companion`、`Factory` 這類不寫的。
- 但這幾個 JVM 專屬型別的公開成員不在表上:`updateThreadContext`、`restoreThreadContext`、`copyForChild`、`mergeForChild`、`executor`(`ExecutorCoroutineDispatcher`)、`id`(`CoroutineId`)。
- 型別名列了、成員沒列,「公開名稱每個恰好一列」對 JVM 專屬部分只做了一半。
- 檔頭只寫「公開類別減掉 klib 名稱,6 個」,沒交代成員不收。
- 這些成員大多不帶情境決策,影響小。
歸因:有證據的原有漏查(r1 補型別時就沒處理成員)。

7. D-4「不適用時」文字沒說 flatMapMerge 算不算「每一次都要做完」
severity: minor
blocking: 否
引句:「用 `collect`、`flatMapConcat` 依序做完,或排隊(`Channel` + 單一消費者),不要 `collectLatest`/`flatMapLatest`/`mapLatest`/`transformLatest`」
file: `skills/kotlin-idioms/checks-catalog.md:743`;API 表 `:1244` 寫 flatMapMerge「新值來時舊的不取消、並行跑」
具體失敗場景:
- 上傳這類必須全部做完的需求,用 `flatMapMerge`(並行、不取消、不保序)其實也做得完。
- D-4 的例外文字和例外樣式都只認 `collect`、`Channel`、`flatMapConcat`。
- 接手者判 `flatMapMerge` 的上傳寫法,例外樣式對不上,收到「證據樣式對不上」提醒,文字又沒說它可不可以。
- 樣本只有「搜尋框用 flatMapMerge」這個反例,沒有它當例外的正例。
歸因:有證據的原有漏查(D-4 的 flatMapMerge 觸發字是上一輪補的,修補只補了 flatMapConcat 的例外,flatMapMerge 沒處理)。

8. 〈叫不出的壞寫法〉的理由是套版,有些跟實情不符
severity: minor
blocking: 否
引句:「的觸發字抓不到這種寫法(字面太常見或沒有專一的字)」
file: `skills/kotlin-idioms/checks-catalog.md:1565`(D-13 STATE-20 `savedStateHandle[…]`)
具體失敗場景:
- 整張表的「代碼審」列都用同一句理由,自檢只要求理由不空白。
- D-13 的觸發字其實有 `SavedStateHandle`,片段 `savedStateHandle[…]` 叫不出是因為首字母大小寫不同。
- 接手者讀理由會誤以為「這個字太常見所以沒法當觸發字」。
- 修補把句尾改成「代碼審看是不是犯了 <列>「名稱」」,只修了句尾,前半句沒動。
歸因:有證據的原有漏查(前半句修前就是這樣)。

## 三問

① 原問題的修復效果:
- 同名異義出口在 `last` 上有效:`last` 標「決策不問 代碼審」並以「同名異義:」開頭,通過;測試另有「沒寫同名異義就報」的反向案例。
- D-4 補了 flatMapMerge、flatMapConcat、mapLatest、transformLatest 的觸發字,`-k api_family_e2e` 4 過、`-k evidence_samples` 25 過。
- 〈統計〉的 434 / 62 / 4 / 18 / 95 / 266 我用程式重數,跟表一致:434 列,D-n 62、撞名 4、主表列 18、代碼審 95、無決策 266。
- 修後 `--catalog-only` 回 0 個問題。
- 壞例檔 233 支、有標記的 199 支,新舊正規式數出來相同,計劃寫的 199 沒變。
- 修前逐案原始輸出沒保存,只比對了上面幾項。

② 修補處的正常、錯誤、相鄰路徑:
- 正常路徑成立:`stats_consistent`、`bad_snippets_reach`、`api_decision_points` 都過。
- 錯誤路徑:非 UTF-8 壞例檔回問題不崩(測試有案例)。
- 相鄰路徑有破口:finding 1(D-4 例外放寬)、4(切行不一致)、5(沒關的圍欄丟最後一行)。
- D-4 的 D-38 排除測試不是空轉:D-38 獨佔 DATA-68,把停用列算進引用就會翻紅。

③ 新發現的同一案例修前、修後:
- finding 1:修前 alt 對 flatMapConcat 搜尋框是 False,修後是 True(上面實測)。
- finding 5:修前回兩行,修後回一行(上面實測)。
- finding 4:修前沒有雙來源切行,所以沒有這個行為;修後輸出已列。
- finding 2、3、6、7、8 是修前就有的問題,修補沒引入。
- finding 2 屬修補沒改乾淨,3、6、7、8 是修前就存在的原有漏查。

未驗範圍:
- 完整 `--sg` 模式(沒有 ast-grep),所以「規則」改由的起訖行涵蓋沒實跑。
- `scripts/test_lumos.py` 其他子集。
- `Systems/kotlin規則包.md` 的 `[test:]` 綁定是否齊全,我沒查。
- `TickerMode` 兩個列舉值的語意說明沒對官方文件,「消費慢時會補送」措辭沒查證。
- 臨時目錄 `/tmp/lumos-seat-work/code-情境決策點窮舉/合約-sonnet/` 還在,內有 `before`、`after`、`t1`、`t2`,我沒清,等收貨後處理。

總結:最高等級 minor,共 8 條
