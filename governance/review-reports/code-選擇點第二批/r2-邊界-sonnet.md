severity: minor

## b1 C-36/C-37 的負數字面值判法把「`-1.` 開頭、後面還接呼叫」的 key 當常數,修後整個漏掉
severity: minor
blocking: 否(漏掉的是該收的選擇點,不是做出錯的壞法;只影響少見寫法,且不損壞資料)

- 輸入:`LaunchedEffect(-1.coerceAtLeast(k)) { load() }` 與 `remember(-1.0.coerceAtLeast(k)) { 3 }`。tree-sitter 把 `-1.coerceAtLeast(k)` 解成 `-(1.coerceAtLeast(k))`,屬於 `prefix_expression`。新加的 literal-arg 分支 `{kind: prefix_expression, regex: '^[-+]\s*[0-9]'}` 只看文字開頭,把它當字面值排除。它其實依賴 `k`。
- 預期:C-36、C-37 命中,因為 key 隨 k 變。
- 實際:0 命中。
- 引句:「- {kind: prefix_expression, regex: '^[-+]\s*[0-9]'}」
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-36、C-37 兩份 literal-arg)
- 歸因:有證據的修復回歸。
  - 指令:`ast-grep scan -r <版本>/configs/ast-grep/kotlin-choice/rules-choice/api.yml --json=compact p4.kt`
  - 修前(eebb8459):`LaunchedEffect(-1.coerceAtLeast(k))` 與 `remember(-1.0.coerceAtLeast(k))` 都命中,共 3 筆(含 `remember(-1)` 這筆舊的誤命中)。
  - 修後(6cc9ad8c):0 命中。
- 範圍:單人自用、這種寫法罕見,所以只標 minor。`-1.coerceAtLeast(k)` 這類寫法會被靜默漏掉。

## b2 `gov --stats` 依列號排序遇到超過 4300 位的數字列號會丟 ValueError
severity: minor
blocking: 否(帳上列號都由型錄 `C-<n>` 產生,正常寫法碰不到;只是「怪列號不讓整段當掉」這句宣稱沒涵蓋全部)

- 輸入:帳上 `row = "C-" + "9"*5000` 的一筆 choice-kill 事件,走 `m._render_gov_choice([...])`。
- 走到:`_render_gov_choice` 的 `sorted(... key=lambda x: int(x[2:]) ...)`。修補加了 `isascii() and isdecimal()`,擋住了 `C-²`,但 `int()` 仍有 4300 位字串上限。
- 預期:照印或排最後。實際:`ValueError: Exceeds the limit (4300 digits) for integer string conversion`。
- 引句:「for row in sorted(by_row, key=lambda x: (int(x[2:]) if x[:2] == "C-" and x[2:].isascii() and x[2:].isdecimal() else 10 ** 9, x)):」
- file: `scripts/lumos`(`_render_gov_choice` 的 sorted 那行)
- 歸因:有證據的原有漏查。修前與修後跑同一輸入,結果都是 ValueError(修前用的是 `isdigit`,同樣會丟)。
- 另測 `C-٣`、`C-`、`C-0032`、row 為 None 或整數,修前修後都正常不當掉。

## 已驗的修復與正常路徑(每項附 claim / input / expected / before / after / comparison)

**G1 C-34(.let→also)**
- claim:沒大括號的 if/for/while/else/when 分支裡的 `.let` 不命中。
- input:`p1.kt` 與樣本檔 `choice-batch2.kt`。
- expected:`if (c) x.let{}` 這類不命中;`val z = if (c) x.let{1} else 0` 與 `fun h() = if (c) x.let{1} else 2` 命中。
- before:未重跑修前規則,只看到測試案例新增。
- after:新樣本行全部符合標記。我另外造了 17 行探針,命中位置合理,包括 else-if 鏈、`return x.let{}`、try/catch、一般 `val` 指派。
- comparison:`t_choice_samples_batch2` 25 項全過,跑的是真 ast-grep 0.51.2,CI 釘的是 0.51.1。
- 過度命中(修前就有,非本次):`x ?: x.let{1}` 與 `(x.let{1})` 當陳述句時也命中。這些命中的壞法是等價的,只多一次存活噪音。

**G1 C-36/C-37 負數與字元常數**
- claim:`-1`、`'c'` 不命中。
- 結果:達成,見 b1 的副作用。

**G2 依列號統計**
- claim:混時區放行取 UTC 較晚者;列號照數字排序;`C-²` 不丟例外。
- 變異驗證:把 `not _loop_ts_newer(...)` 換回 `ts >= ...`,`t_gov_stats_choice_by_row` 會紅(4 過 1 敗),測試抓得到。
- 時間打平:`_loop_ts_newer` 為偽時,後讀到的那筆贏;缺 ts 視為最舊。`ts=None`、`ts=12345` 的探針不當掉。
- after:`t_gov_stats_choice_by_row` 5 項全過。

**G3 `?.` 錨點**
- claim:`!!` 位置照位元組算。
- 結果:`t_choice_points_nul_safecall` 5 項全過,含多位元組那條真 ast-grep 測試。
- 探針:`p3.kt` 造了 `a.b(1) // c`、`a!! // c`、`(a) // c`、`l[0] // c`、`a.b{1} // c`、`/* c */`、多註解與 `a.b(1)/**/?.c` 共 11 種前導註解。全部正確不命中,只有 `) ?.c`(註解在括號內)命中。
- C-33 的雙重否定改寫(輸出平方成長那條),命中集合在 `p2.kt` 探針上與預期一致,包括字串樣板 `"${a?.b}"`。
- 引數錨點:右括號行的案例 `{8}` 已補測。程式碼本體在修前就已經正確,這次只補了測試。

**G4 已撤列號守衛**
- 全形冒號、`- ` 開頭、粗體、多寫一行,都報看不懂;`:(無)` 不報;撤掉的列號再出現照擋。
- `t_choice_table_batch2` 12 項全過。
- 測試缺口(非 major):把「頂格才認」的 `lines[0] == lines[0].lstrip()` 條件拿掉後,這支測試仍是 12 項全過,因為沒有縮排行的案例。該條件拿掉後只是更寬鬆,守衛仍會生效,不會靜默失效,所以只算 minor 的測試缺口。

**G5 輸出量**
- 沒有自動測試守輸出量,我也沒重跑 300 層巢狀的量測。**未驗**。
- 派工詞只准用最多 20GB 以下的實驗,我沒造大檔。

## 圖譜鏡頭(固定席)
備份檔 `/tmp/lumos-seat-work/code-選擇點第二批/lens-r2.txt` 的「這次新增的殘留」段寫「算不出來(時間預算用完)」,殘留逐條題我無法答,標 ⚠ 未判定。

- `Systems/kotlin規則包`:這次改的正是它的家,規則、check.py 與測試行為依筆記宣稱做事,沒看到破壞。
- `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`lumos-cli-read` 的 INVARIANT:不影響。這次沒動 code-loop 綁測試判定、`guard kill`、re-inject 或 search 排除邏輯。
- `測試假綠形態` INVARIANT(還原翻紅釘須有前置斷言):不影響。新測試都先用 `_cb2_points` 或 `_choice_anchor` 取得現場值再比對。
- `pitfalls-code-loop`、`loop-convergence-recording`(RISK):不影響。`scripts/lumos` 只動 `gov --stats` 的選擇點統計段。

## 三問
1. 原問題修復效果:G1 的 C-34 和 G2、G3、G4 的案例都有同一輸入的測試或探針證據。C-36/37 的負數修復成立但引入 b1。G5 的輸出量只靠作者手動量測,我沒驗證。
2. 修補處正常、錯誤與相鄰路徑是否仍成立:成立,但 C-36/37 的 `prefix_expression` 判法把相鄰的「負數開頭的非常數運算式」也排除了(b1)。
3. 新發現的同一案例修前修後:b1 修前命中、修後漏掉;b2 兩版都會丟例外,見上。

最嚴重:minor;blocking 共 0 條
