severity: clean

這份 diff 跟專案既有做法對得齊,沒有引入第二種做法,也沒有跨層直呼。有一處小差異(`_batch4_problems` 的命名,見問 2)是鄰居本身不一致,我沒列成不對齊,標 ⚠ 交編排者。

**問 1:分層與依賴方向**

`_batch4_problems` 放在 `catalog_problems` 正上方,跟前面的 `_dt_row_lint` 同一帶,是前綴底線的單列私有輔助函式,由 `catalog_problems` 在迴圈裡呼叫。

- 回傳形狀:`_batch4_problems` 回字串清單,由呼叫端包成 `(rid, p)`。`_dt_row_lint` 也是這樣做的,所以不算不一致。
  - 引句:「        problems += [(rid, p) for p in _batch4_problems(c[5], batch)]」
  - 對照:`configs/ast-grep/kotlin-android/check.py:398` 的 `problems += [(did, p) for p in _dt_row_lint(...)]`;函式本體在 `check.py:326`。
- 沒有前綴底線的 `template_problems`(`check.py:749`)、`pending_problems`(`check.py:445`)、`stats_problems`(`check.py:504`)吃整張表、回 `(rid, msg)` 元組。它們處理的單位是整張表,跟逐列輔助函式不同層,所以沒拿它們當對照。
- 依賴方向:`_batch4_problems` 只呼叫 `batch4_expected_tags` 和 `B4_TAG_*`,沒有跨層直呼。口徑仍然只住在 `check.py:122`。

**問 2:命名與寫法**

- 函式命名與 docstring:前綴底線加 `_problems` 後綴,docstring 先講輸入輸出,再講判法與理由。
  - 引句:「def _batch4_problems(rule_col, batch):」
  - ⚠ 同層逐列輔助函式 `_dt_row_lint` 用 `_lint` 後綴,表層函式用 `_problems` 後綴,鄰居本身不一致,所以不列成 finding,交編排者判是否要統一。
- 型錄 11 列的標籤寫法:跟既有寫法一致。
  - 引句:「告警帶寫法=批一、批四(CI 範本:Android Lint)」
  - 對照:`skills/kotlin-idioms/checks-catalog.md:566` 的 DATA-27 寫成「告警帶寫法=批一、批四(CI 範本:Android Lint)」。
  - UI-10 和 TEST-23 沿用「批一(只有提示級規則,預設不接)、批四(…)」這種既有形式。我用 `git show HEAD:skills/kotlin-idioms/checks-catalog.md` 查過,已有兩列這樣寫。
  - UI-10、UI-16 的雙標籤寫成「CI 範本:Android Lint;推送前:detekt 外掛 compose-rules」,用的是 `check.py:122` 的 `batch4_expected_tags` 回傳順序和「;」分隔。
- 測試改壞例子:沿用既有的 `(name, idx, a, b)` 元組加 `_ktpack(copy=True)` 複本,跟前兩例同一寫法,第三例直接併進同一個迴圈。
  - 引句:「("批一的列拿掉批四", i_b1, f"告警帶寫法=批一、批四({lint})", "告警帶寫法=批一")」
  - 對照:`scripts/test_lumos.py:129155`。
- 筆記 WHY 行:新開一行是對的。`Systems/kotlin規則包.md:54` 那行談的是資安包前綴和 `B4_DEFAULT_OFF`,不是「第四批標籤不論批幾都判」這個決策。檔內沒有別行講「只判已寫批四的列」,所以沒有該改的既有行。
  - 引句:「WHY:型錄自檢的第四批標籤不論那列原本標批幾都判」
  - 欄位齊全:`[出處:]`、`[因:]`、`[不選:]`、`[test:t_kt_catalog_batch4_wiring]`。

**問 3:第二種做法**

沒有另寫一套判法或讀表。

- 判法:`batch4_expected_tags` 仍是口徑的單一處。我 grep 過 `scripts` 和 `configs`,`check.py:346` 的 `_batch4_problems` 是唯一的生產端使用者,測試端只讀它。
- 讀表:主表仍走 `main_rows`,`_batch4_problems` 只收 `c[5]` 和 `c[9]`,沒有自己重新讀型錄。
  - 引句:「    want = batch4_expected_tags(rule_col)」
- 改動內容:原本內嵌在迴圈裡的 `want`/`have` 兩個分支逐字搬進函式,只拿掉 `if "批四" in batch else []` 這個門檻。判法沒有分叉,也沒有兩個版本並存。

不對齊共 0 條,其中 major 0 條。(⚠ 1 項交編排者:`_batch4_problems` 與 `_dt_row_lint` 的後綴命名不一致,鄰居本身就不一致。)
