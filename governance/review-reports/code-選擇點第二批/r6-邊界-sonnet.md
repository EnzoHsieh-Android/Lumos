severity: clean

我在臨時副本(修後 8333987a、修前 c261a154 各一份)逐項跑過,沒有找到會做出錯行為的 finding。以下是已驗主張與證據;臨時目錄已用字面絕對路徑刪除。

## 已驗主張(claim / input / expected / before / after / comparison)

**P1 修復:標註加常數(`@Suppress("x") 1`)不再被當成非常數 key**
- input:`LaunchedEffect(@Suppress("x") 1) { }`,用 `ast-grep scan -r rules-choice/api.yml` 掃。
- expected:不命中 C-36。
- before:命中。after:不命中。
- comparison:同一份探針檔掃兩版,只有這行翻轉。`LaunchedEffect(@Suppress("x") k)` 兩版都命中,正向不被打壞。

**P2 `-k + 1`、`-k`、`!k`、`++k`、`k++`、`-1, k` 仍命中;`-1`、`+2`、`- 1`、`-1.5f` 仍不命中**
- before 與 after 在這幾條的結果一致。

**P3 測試能抓到改壞,而且各自獨立**
- 把 `kind: prefix_expression` 換回 `{kind: prefix_expression, regex: '^[-+]'}`:`t_choice_samples_batch2` 紅,指出 `choice-batch2.kt` 第 119 行(`@Suppress` 那行)MISS 卻命中。
- 拿掉 `kind: prefix_expression`:紅,指出第 112、118 行(`-k + 1` 與 `k + 1`)HIT 沒中。
- `nthChild: {position: 1, reverse: true}` 去掉 `reverse`:紅,指出第 88、119 行。
- 三種改壞各自對應到不同的樣本行,每次都是 32 passed、1 failed,不是全套都紅。

**P4 `C-0`、`A-0` 報「列號要寫成…」**
- before 與 after 的 `choice_tables` 對 `C-0` 行為一致(都報)。這次只補了測試,沒改程式。補的測試對得上現有行為。
- 其他列號輸入,before 與 after 結果一致:
  - `C-00`、`C-١`、`C-０`:報寫法不對。
  - `C-1000` 與 22 位數:照認。
  - `C-` 與 `C-40`+零寬空白(U+200B):被 `_CHOICE_ROW_RE` 靜默略過,兩版相同。這是第一版就有的行為,不是這次修補造成。
- 已撤列號那一行:`C-0`、全形逗號、零寬字元都報看不懂;`C-40,C-41`、`C-40、C-40`、全形空白分隔都照認。

**P5 樣本檔與 CRLF**
- 把 `choice-batch2.kt` 整檔改成 CRLF 後跑 `-k choice_samples_batch2`:33 passed。
- ast-grep 在本機是 0.51.2,CI 是 0.51.1,版本差異我沒有跑。
- 新增的十四行都在 `choice-batch2.kt`。其他樣本檔沒動,S7 的 `_CB2_S7_PIN` 釘的是 `arid.kt` 等舊檔,指紋不受影響。

**P6 `gov --stats` 依列號(不在這次修補範圍,順帶驗)**
- 缺欄位、`row` 非字串(計入「沒有列號的放行」)、同 ts(後讀到的贏,與註解一致)、混時區(08:00+08:00 對 03:00Z 比出正確的新舊)都沒有丟例外。
- `row` 是 5000 位數字的字串時排序不崩。

## 未覆蓋與已知殘留(不算 finding)

- `@Suppress("x") -1`、`--1`、`+-1`、`-(1)`、`!true` 仍會命中 C-36,這是把常數當成選擇點。這種寫法在實務上幾乎不會出現,兩版行為相同(不是這次修補造成),後果只是多一個等價壞法。第三輪已放行括號包常數的同類案例。
- 統計帳的 `ck_waive.file` 若是 list 會讓 `_gov_choice_counts` 丟 TypeError(unhashable)。我只用手造的帳測到;帳只由 lumos 自己寫,不屬於這個 repo 的威脅範圍,所以不標 finding。
- C-35 `^` 頭錨點對 `navigation_suffix` 是冗餘的:節點文字一定以 `.` 或 `?.` 開頭,拿掉它不會讓行為改變,是等價變異,不是漏測。
- 我沒有驗 `r6-repair-docs.patch` 的內容與實作的一致性,只掃過一遍。
- 沒有跑 `gov` 真實帳本。

## 圖譜鏡頭

- `Systems/kotlin規則包.md`(家):牽連 `api.yml`、`check.py`、測試。這次只動 `api.yml` 的 literal-arg 與樣本、測試,沒有改該節點宣稱的行為。以程式與測試為準,C-36、C-37 兩份 literal-arg 仍一字不差(`t_choice_samples_batch2` 的比對通過)。
- `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`測試假綠形態`、`lumos-cli-read` 的 INVARIANT:這次沒改 `scripts/lumos` 與 hook 行為,只改了 `test_lumos.py` 的測試案例,不影響它們。
- `check.py` 的程式碼這次沒動,所以「列號只認半形數字」的合約沒被改變。
- 殘留段:算不出來(鏡頭計算超時),我沒有看到「這次新增的殘留」的明細。我沒讀 `residual-index.json`,殘留問答是否換號或改字重問,我未判定。

最嚴重:clean;blocking 共 0 條
