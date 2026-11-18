severity: minor

兩條 finding 都是規則漏判或多判。兩條都沒有破壞資料或合約,所以最高是 minor。我的臨時副本(clone 與 before worktree)已用字面絕對路徑刪除。

## c1 `.let` 的 C-34 只擋住單層沒大括號分支,`else if` 與巢狀 if/when 裡的陳述式 `.let` 仍命中
severity: minor
blocking: 否 — 假命中產生等價壞法,可用放行標「等價」處理,不損壞資料。
鏡頭題號:無(後端與前端卡都不涉及)。

- 輸入:`if (a) go() else if (b) x.let { show(it) }`,陳述式、回傳值沒人用。同樣會命中的還有 `for (i in list) if (i > 0) x.let {…}`、`if (a) if (b) x.let {…}`、`if (a) when (c) { true -> x.let {…}; else -> go() }`。
- 路徑:`value-used` 的第 3、4 支規則是 `inside control_structure_body inside if_expression, matches: value-pos`。這裡的 `value-pos` 是 sbr.yml 那份保守定義「父節點不是 statements 就算值」。內層 `if_expression` 自己掛在外層的 `control_structure_body` 底下,所以 `value-pos` 判為真,`.let` 被當成值被用到。
- 預期:規格與樣本註解寫「只有 if/when 本身當值用時才算」,這幾行應不命中。實際:都命中 C-34。
- 實測:`ast-grep scan` 對該檔,第 2、3、4、5 行都有 C-34。接著跑 `_choice_scan` 加 `_choice_file_points`,第 2 行挑出壞法 `if (a) go() else if (b) x.also { show(it) }`(等價壞法)。第 4 行同樣。
- 修前 eebb8459 對同一檔的結果完全相同(命中集合與壞法一樣)。這是原有漏查,修補只擋了單層分支。
- 樣本 `choice-batch2.kt` 的 MISS 只有單層分支,沒有 `else if` 或巢狀,測試抓不到。
- 引句:「      - inside: {kind: control_structure_body, inside: {kind: if_expression, matches: value-pos}}」
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(`value-used` 區塊)
- 歸因:有證據的原有漏查。修前、修後各跑一次,結果相同。

## c2 負數字面值判法 `^[-+]\s*[0-9]` 把 `-1.plus(k)` 這類「數字開頭的鏈式呼叫」也當常數,C-36、C-37 漏命中
severity: minor
blocking: 否 — 只漏掉一個壞法,不影響其他列。

- 輸入:`LaunchedEffect(-1.plus(k)) { x() }`、`remember(-1.coerceAtLeast(offset)) { 1 }`。key 隨 `k` 或 `offset` 變動。
- 路徑:新增的字面值分支 `{kind: prefix_expression, regex: '^[-+]\s*[0-9]'}` 只看文字開頭。`-1.plus(k)` 在語法樹整段是一個 `prefix_expression`,開頭 `-1` 符合,整個引數被當成字面值,`value_arguments` 不命中。
- 實測:修前 eebb8459 命中 `C-36 3 '(-1.plus(k))'`、`C-37 4 '(-1.coerceAtLeast(offset))'`;修後這兩行都不命中。`-k.toInt()`、`-1 * k`、`-(1 + k)` 仍命中,沒有誤傷。
- 此輸入少見(數字字面值後面直接接方法呼叫)。
- 引句:「        - {kind: prefix_expression, regex: '^[-+]\s*[0-9]'}」
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-36 與 C-37 的 `literal-arg`)
- 歸因:有證據的修復回歸。修前命中、修後不命中,輸入與命令相同。

## 圖譜鏡頭(固定席)
- `Systems/kotlin規則包.md`:新增的 WHY 與 PITFALL 行,與程式一致。雙重否定改寫在我造的 C-33 到 C-37 對照檔上,命中集合與修前相同,差異只有 C-36、C-37 的負數與字元字面值。不影響,但 c1 是這篇「只有 if/when 本身當值用時才算」一句的例外。
- `Systems/bound-tests-gate.md`、`guard-kill.md`、`lumos-cli-lifecycle.md`、`lumos-cli-read.md`、`測試假綠形態.md`:這次的程式改動是規則 yml、`check.py` 的撤列號判讀、`_gov_choice_counts` 的時間比較與排序,與這些合約宣稱的行為無交集。不影響。
- `Systems/pitfalls-code-loop.md`、`loop-convergence-recording.md`(RISK):改動只經 `_loop_ts_newer` 這個既有純函式,沒有動它。不影響。
- 「這次新增的殘留」段:派工鏡頭只印出「算不出來」,沒有任何殘留問答可對。那份提示問的是殘留問答的編號、判定、checker、ts 有沒有被換編號或改字。這次改動沒有碰 `residual-index.json`,我也沒有讀它,所以這題只能答「未判定」。

## 修補鏡頭三問
1. 原問題的修復效果:
   - `.let` 單層沒大括號分支:修後 `if (c) x.let` 與 `for`、`while`、`else`、`when` 單層都不命中;修前都命中。測試改版後,用舊 api.yml 跑 `-k choice_samples_batch2` 會 2 條紅(原樣本沒有這些 MISS 行,新增的 MISS 才抓得到)。
   - 放行時區:`_loop_ts_newer` 比 UTC 秒數,測試用混時區的兩筆放行,用字串比較會選錯。
   - 全形冒號與多寫一行:新守衛會報;舊正規式不認全形冒號、多寫一行時只看第一行。
   - 負數與字元字面值:已排除,但引入 c2。
2. 修補處的正常、錯誤與相鄰呼叫路徑:
   - 規則端:修補後 C-33、C-35 在 `?.` 鏈、註解與 `combine` 輸入上的命中集合,與修前一致(對照檔 b.kt、a.kt 的 diff 只有 C-36、C-37 與 C-34 預期內的差)。
   - `?.` 錨點:`?.` 前有中文字、`!!` 位置照位元組算,在修前就正確,修補只加了測試。
   - 引數錨點:只改右括號那一行時,修前就能挑到,修補只加了測試。
   - 其他測試:`gov_stats_choice_by_row`、`choice_table_batch2`、`choice_points_compose`、`choice_points_nul_safecall`、`choice_points_batch2_stable`、`choice_samples_batch2` 在修後版本全綠。
   - 未發現的相鄰缺口(未驗):列號帶超長 ASCII 數字時 `int()` 可能超出位數上限而丟例外。帳上的列號來自型錄,我判為範圍外,沒有實測。
3. 新發現的同一案例修前修後:c1 修前修後相同(都命中、都挑出壞法);c2 修前命中、修後不命中。

## 已驗主張的證據
- claim:`?.` 前有中文字時 `!!` 位置正確。
  - input:`val é = "價格"; val u = r` 換行 `?.n`,改第二行。
  - expected:`r!!` 接在 r 後,續行 `.n`。
  - before 與 after:兩版輸出皆為 `        val é = "價格"; val u = r!!\n            .n`。
  - comparison:一致。這是修前就對,不是修補造成。
- claim:`?.` 前有註解不命中(行註解與區塊註解)。
  - input:註解接在 `?.` 前的各種寫法。
  - 實測:都不命中;下一個 `?.` 仍會被挑中(例如 `?.z?.w` 挑到 `w`)。
  - comparison:符合規格,修前行為相同。

## 未驗範圍
- 沒有跑任何不帶 `-k` 的全套測試。
- G5 輸出量:我只量了 300 層巢狀與 1500 個 `?.` 的輸出位元組(修前 28MB、修後 15MB 等),沒有做線性成長判定。
- 沒有對新測試逐道做變異。唯一的變異實驗是用修前的 api.yml 驗證樣本測試會紅。

最嚴重:minor;blocking 共 0 條
