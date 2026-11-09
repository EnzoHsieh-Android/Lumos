severity: minor

整體判斷:這份 diff 大致沿用專案既有的做法,只有一處寫法跟鄰居不一致。

**問 1:放的位置對不對?**
對。
- `CROSS_PREFIX` 緊貼 `REVIEW_FP_PREFIX` 宣告(`check.py` 的 22 行前後,diff 中 `+CROSS_PREFIX = "cross-"` 那行)。
- 跨規則檢查接在 `check()` 既有的 `hits` 迴圈裡,用同一份 `(owner, msg)` 的 `problems` 元組。
- `good_cases` 改成 `startswith((REVIEW_FP_PREFIX, CROSS_PREFIX))`,沒有另開第二條路。
- 新測試 `t_kotlin_rulepack_good_cross_rule`(`scripts/test_lumos.py:126668`)和 `t_kotlin_rulepack_samples`(`126728`)、`t_kotlin_rulepack_unwired_dir`(`126911`)並排,用同一組 `_ktpack`、`_ktpack_sg` 輔助函式。
- 沒有 ast-grep 時先跑靜態那半,再印「本機沒有 ast-grep」,和 `126749` 的寫法一致。
- 家筆記的 WHY 寫進 `Systems/kotlin規則包.md`。
- Issue 的修好紀錄加在原 Issue 檔,REVISIT 用 `[closed:…]` 收尾,和鄰居 `Systems/kotlin規則包.md` 的 REVISIT 收尾格式一致。

**問 2:命名與寫法跟鄰居一樣嗎?**
大致一樣。
- `cross-` 檔名前綴對應 `review-fp-`。
- 測試名、`★改壞★` / `★對照★` 標記、`print("  ✓ …")` 結尾,都和 `127372` 等鄰居一致。
- 不一致的只有 A1:規則 yml 裡新增了「容易誤報:」註解。我查過 `rules/`、`rules-review/`、`rules-unwired/` 底下所有 yml,沒有任何一條規則用這個前綴。這個前綴是好例樣本檔的慣例(`samples/good` 下 106 個檔有)。規則 yml 既有的寫法有兩種:
  - 檔頭註解,用 `[[Projects/…]]` 連結加「不接閘(樣本外 N 處誤報…)」,例如 `rules-unwired/compose.yml:1`。
  - 規則內的行內註解,尾端附「(日期 實測誤報)」,例如 `rules/compose.yml:14`。

**問 3:有沒有引入專案原本沒有的做法?**
- 「略過檔名前綴」的機制是照 `REVIEW_FP_PREFIX` 複製的,不算第二種做法。
- 「規則 yml 內記已知誤報」本身專案已有。新增的只是把樣本側的「容易誤報:」前綴搬進規則 yml,見 A1。
- 沒有發現其他新做法。

A1
severity: minor
blocking: 否
引句:「# 容易誤報:收集的是有限流(例 flowOf(1, 2))時一般 launch 會自己結束、不會卡住,這條照樣報」
file: `configs/ast-grep/kotlin-android/rules-unwired/compose.yml:1`

補充:這條在規則 yml 內放獨立一行的整行註解,位置在 `# T16` 與 `id:` 之間,結構上放得下。它只是沒有沿用規則 yml 既有的檔頭連結加量測數字寫法,或行內註解尾端附日期的寫法。

不對齊共 1 條,其中 major 0 條
