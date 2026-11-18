severity: major

## c1 C-34 的 catch 區塊「確定是值」判法沒有任何測試守住
severity: major
blocking: 是——測試抓不住具體、合理的改壞,被保護的是 S6 的 C-34 條款(只收確定是值的位置)。

- 改壞:把 `catch_block` 那一行的 `value-direct` 改回 `value-pos`,這正是修補前的寫法,也是 r2 g1 c1 要修的那一類。
- 輸入:`if (c) try { go() } catch (e: Exception) { x.let { show(it) } }`,也就是 if 掛在另一個分支底下、不是值,let 的回傳值沒人用。
- 走到哪:`api.yml` C-34 的 `value-used` 第 4 條 `catch_block … try_expression, matches: value-direct`。改壞後,try 的父節點是 `control_structure_body`,不在 `statements` 裡,於是 `value-pos` 成立,規則誤命中這個 let。
- 樣本檔只有 `if (c) try { x.let {…} } catch (e: Exception) { go() }`,let 在 try 本體,沒有一行把 let 放在 catch 裡,所以改壞也不會紅。
- 預期:`for (i in 1..2) try {…} catch … { x.let{…} }` 兩行都不命中。改壞後這兩行都命中。
- 實測(臨時副本,改壞後跑兩個測試子集):
  - `-k choice_samples_batch2`:33 passed, 0 failed。
  - `-k choice_points`:105 passed, 0 failed。
- 修補前版本 `6cc9ad8c` 同一輸入也會命中,因為本來就是 `value-pos`。
- 歸因:有證據的原有漏查,只是這次修補補測試時漏了這一支;修補本身對這輸入的行為正確。
- 兩版查證:修後 `ast-grep scan -r api.yml` 對 `c.kt` 只回第 5 行(`val v = try … x.let { 1 }`,正確);改壞後回 2、3、5。修前未另跑這支輸入。

引句:「- inside: {kind: catch_block, inside: {kind: try_expression, matches: value-direct}}」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`

## c2 帶號數字的運算元清單,Long/十六進位/二進位/無號四種沒有測試
severity: major
blocking: 是——能指出具體改壞而測試照綠,被保護的是 S6 字面值定義;依列號統計與其他行為不受影響。

- 改壞:`LaunchedEffect` 與 `remember` 兩份規則的運算元清單 `any: [integer_literal, real_literal, long_literal, hex_literal, bin_literal, unsigned_literal]`,任一份漏抄一種。
- 走過的輸入:`LaunchedEffect(-1L)`、`(-0x1)`、`(-0b1)`、`(-1u)`,預期都不命中,因為 key 是常數。
- 逐種拿掉再跑,`choice_samples_batch2` 都是 33 passed:
  - 拿掉 `long_literal`、`hex_literal`、`unsigned_literal`、`bin_literal` 任一種,對應那行就變成誤命中,測試照綠。
  - 這四種都另跑過 `choice_points`,同樣全綠(105 passed)。
  - 只有拿掉 `real_literal`(`+2.5` 有樣本)與整段退回舊 regex 才會紅。
- 修補前版本用 regex `^[-+]\s*[0-9]`,這四種都不命中,所以是對的;修補把它改成清單,新增了「清單漏項」這種改壞方式。
- 歸因:有證據的修復回歸風險。修補後行為正確,但新的結構判法沒有被測試守住。
- 兩版查證:修後 `-1L`、`-0x1`、`-0b1`、`-1u` 都不命中;改壞對應那一種後,該行命中。

引句:「- has: {nthChild: {position: 1, reverse: true}, any: [{kind: integer_literal}, {kind: real_literal}, {kind: long_literal}, {kind: hex_literal}, {kind: bin_literal}, {kind: unsigned_literal}]}」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`

## c3 括號包住的常數(`-(1)`、`-(-1)`)被當成非常數而命中
severity: minor
blocking: 否——只造成存活的等價壞法,要人放行一次,不損壞資料。

- 輸入:`LaunchedEffect(-(1)) { a() }` 與 `LaunchedEffect(-(-1)) { a() }`。
- 走到:帶號數字那條判法,最後一個子節點是括號運算式,不是數字常數,所以判成「引數不全是字面值」而命中。
- 結果:key 換成 `Unit` 與原本同樣是常數,必然等價。實測修後這兩行命中,修前也命中,不是修補造成。
- 歸因:有證據的原有漏查。計劃只說「看結構,運算元本身要是數字常數」,沒有承諾括號,屬極少見寫法,所以只報 minor。

引句:「LaunchedEffect(-1.coerceAtLeast(k)) { load() } // HIT C-36」
file: `configs/ast-grep/kotlin-choice/samples/choice-batch2.kt`

## 圖譜鏡頭
派工詞沒附固定席節點,我也沒讀備份檔 `lens-r3.txt`,所以逐條判固定席沒做,未判定。這次改動只動 `api.yml`、樣本、`gov --stats` 的排序鍵與測試,沒碰筆記宣稱的挑法、行指紋與乾節點,沒有看到會破壞合約的地方。

## 三問回答與已驗主張證據
①原問題的修復效果:G1 與 G2 都有修前紅、修後綠的行為證據。
- G1:樣本第 29 到 35 行的 `else if` 鏈、巢狀 if、for 裡的 if、if 裡的 when 或 try,修前 C-34 誤命中,修後不命中。
- G2:`-1.coerceAtLeast(k)` 與 `-1.0.coerceAtLeast(k)` 修前漏抓,修後命中。這兩個修前結果是拿修後的樣本檔對修前規則跑出來的。
- G3:5000 位數字的列號排序,只讀了程式與測試,沒另跑修前版本。

②正常與相鄰路徑:
- 先前就能抓的寫法修後都還抓得到,走過的輸入有:`return x.let`、引數、字串樣板、elvis 右邊、具名引數、lambda 最後一行、屬性 getter、`val t = try … catch`、`=when{…}` 的區塊分支。
- 陳述位置都沒被誤抓,走過的有:while、do-while、try/catch/finally 當陳述、標籤 for、init 區塊、`when` 陳述。
- 已知刻意漏抓:`fun y(c) = if (c) { if (c) x.let{1} else 2 } else 3` 這種外層又掛在分支底下的寫法不收,計劃明文認。
- 帶號數字:`-1L`、`-0x1`、`-1u`、`- 1`(中間空白)、`-1.5f`、`-1e3`、`-0b1`、`-1_000` 都不命中,`-k`、`-1 + k`、`-1.coerceAtLeast(k)`、`-(1)`、`-(-1)` 都命中。
- 依列號排序:`C-²`、空編號、超長編號都不會讓 `int()` 丟例外,程式碼走一遍結論如此。

③新發現的同一案例修前與修後:c1 與 c2 修前沒有對應測試,修後結論見各條。c3 兩版結果相同。

未驗範圍:
- `nul.yml` 與第一批的 `?:`、`?.` 新編輯,以及行列換算、多位元組字元,本席沒走。
- 全套測試與第二批其他列的單元測試沒跑。
- 修前版本的測試套件沒另跑。

最嚴重:major;blocking 共 2 條
