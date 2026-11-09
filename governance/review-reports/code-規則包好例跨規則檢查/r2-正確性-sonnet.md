severity: clean

總結:最高嚴重度 clean。沒有發現需要列為 F 編號的缺陷。

**證據**
- 真規則包自檢:`check.py --sg <ast-grep>` 輸出「規則 228 條,問題 0 個」。
- 測試 `t_kotlin_rulepack_good_cross_rule`:
  - 有 `LUMOS_AST_GREP` 時 7 條斷言全綠。
  - 沒有 ast-grep 時只剩 1 條斷言(cross- 檔宣告不算段數),不再是零斷言。
- 我在臨時副本逐項改壞 `check.py`,再跑這支測試,結果如下:

| 改壞方式 | 翻紅的斷言 |
|---|---|
| review-fp- 檔對會擋規則一律豁免 | 「review-fp- 檔被別條會擋規則命中也照報」 |
| cross- 檔也照報(拿掉 `elif`) | 「★對照★ 同樣的別條壞寫法放進 cross- 檔就不報」 |
| 拿掉「cross- 沒被命中」檢查 | 「cross- 檔沒被別條規則命中要報」 |
| `good_cases` 不略過 `cross-` | 「cross- 檔的宣告不算好例段數」兩條(不靠 ast-grep 與靠 ast-grep 各一) |
| 拿掉「好例被會擋規則命中」報告迴圈 | 「好例被別條會擋規則命中要報」與 review-fp 那條 |
| 整個跨規則判斷 `and False` | 「好例被別條會擋規則命中要報」、review-fp、對照三條 |

- 邊界輸入走查(都在臨時副本):
  - 放在 `kotlin/sub/` 子目錄的 cross- 檔,正常通過。
  - 大寫的 `Cross-x.kt` 不當 cross- 檔,照報(符合設計)。
  - 同時被兩條規則命中的 cross- 檔,不報。
  - review-fp- 檔裝會擋規則的壞寫法,報。
  - review-fp- 檔裝覆核級規則的壞寫法,不報(原行為)。
- 三份測試複本各用獨立的 `mkdtemp`,不會互相干擾。
- 清理:`rmtree` 在 `finally` 內。我在副本改壞時留下的 `gctl-run-*` 與臨時目錄已用字面路徑刪掉。

**修補三問**
1. 原問題的修復效果:review-fp- 檔被會擋規則命中,修前沒有測試釘住,修後有專屬複本斷言,改成一律豁免就會紅(見上表第一列)。沒有 ast-grep 的環境,修前直接 return 零斷言,修後至少跑 `good_cases` 的 cross- 略過那條(拿掉略過會得到 4 而不是 1)。
2. 修補處的正常、錯誤與相鄰路徑仍成立:對照組(cross- 放別條壞寫法不報)、cross- 沒被命中要報、cross- 命中自己的規則算誤報、不算段數,都仍成立。
3. 同一案例修前、修後:review-fp- 放會擋規則壞寫法,在 `check.py` 程式邏輯上修前就會報(本輪修補沒動 `check.py`),差別只在修前沒有測試。歸因:有證據的原有漏查(測試缺口),不是修復回歸。查證命令:`LUMOS_AST_GREP=<sg> python3.14 scripts/test_lumos.py -k kotlin_rulepack_good_cross_rule`,修前 f712af3 沒有 review-fp 那條斷言,修後 0764d33 有且綠。

**待驗**
- ①:通過(見上)。
- ②:通過。
- ③:通過。用 ast-grep 對 `launch { flowOf(1, 2).toList(values) }` 放在 `src/test` 實掃,`kt-test-tolist-not-background` 確實命中。`testing.yml` 的「容易誤報」註解與 Issue 紀錄寫的是同一件事。
- ④:通過,0 問題。
- ⑤:通過,四道檢查各有測試會紅。

**附帶觀察,不列為缺陷**
測試複本沒有複製 `scripts/lumos`,所以 `ta`、`tb`、`tc` 的前面會固定出現「找不到 scripts/lumos」兩行雜訊。斷言本身用 `in` 比對全文,結果不受影響。只是斷言紅的時候,失敗訊息 `[:400]` 會被這兩行佔掉,不容易看出真正的問題。

relevant file:
- `/Users/enzo/orca/workspaces/lumos-toolchain/goodsample-fix/configs/ast-grep/kotlin-android/check.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/goodsample-fix/scripts/test_lumos.py`
