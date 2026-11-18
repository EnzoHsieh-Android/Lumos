severity: clean

這次修補只動兩支檔(`configs/ast-grep/kotlin-choice/rules-choice/api.yml` 與 `configs/ast-grep/kotlin-choice/samples/choice-batch2.kt`),沒有碰 `scripts/lumos`,所以派工詞列的 `_choice_*`、`_gov_choice_counts`、`_render_gov_choice` 這類 Python 對照組都沒被動到。以下三問只對 YAML 規則與樣本回答。

**1. 分層與依賴方向:對齊。**
- 改動留在原本負責的規則檔,規則還是只用既有的 `kind` / `has` / `nthChild` 結構判斷,沒有新函式、沒有跨層呼叫。
- C-36 與 C-37 的 `literal-arg` 區塊還是各一份。我用腳本比對這兩段,逐字相同(輸出 `2 True`),符合規則檔上方寫的「兩份要一字不差」。
- 同族對照是 `configs/ast-grep/kotlin-android/rules-review/state.yml:55` 與 `configs/ast-grep/kotlin-android/utils/debug-only.yml:37`。它們用 `kind: prefix_expression` 搭 `regex` 是因為要比對前綴文字。這次拿掉 `regex: '^[-+]'` 改成純結構判斷,是這支規則本身的取捨,不是改變全專案的寫法。

**2. 命名與錯誤處理:對齊。**
- 註解引用審查輪次的寫法是「代碼審 r5 c3」。同一支檔裡 `api.yml:238` 已經有「代碼審 r2 b1 c2」這種短寫法,新註解跟它一樣。
- 樣本的標記格式沿用既有的 `// HIT C-xx` 和 `// MISS C-xx`,沒有新增標記種類。
- 這次不涉及回傳碼、錯誤訊息與帳本事件。

**3. 有沒有第二種做法:沒有。**
- 沒有新的讀帳方式、放行檔格式、隔離工作樹或工具函式。

**已驗主張的證據**

| 項目 | 內容 |
|---|---|
| claim | `LaunchedEffect(@Suppress("x") 1)` 以前被誤判為會觸發 C-36,修後不會;`-k + 1` 仍會觸發 |
| input | 臨時檔三行:`LaunchedEffect(@Suppress("x") 1)`、`LaunchedEffect(-k + 1)`、`LaunchedEffect(-1)` |
| expected | 只有 `-k + 1` 那行命中 C-36 |
| before(c261a154) | 命中第 3 行與第 4 行,也就是 `@Suppress("x") 1` 誤判 |
| after(8333987a) | 只命中第 4 行 |
| comparison | 誤判消失,真命中與 `-1` 的不命中都沒變 |
| 全套樣本測試 | `python3.14 scripts/test_lumos.py -k choice_samples` 共 33 項通過,含「第二批樣本:每個 HIT 都中、每個 MISS 都沒中」 |

**歸因:** 有證據的修復效果。兩版都用 `ast-grep scan` 跑過同一個檔。

**未驗範圍:** 新增的 C-34、C-35 樣本我只用既有樣本測試的通過結果支撐,沒有逐行用修前版本重跑。這次 patch 沒改 C-34、C-35 的規則,所以我沒判它們的修前後差異。

**圖譜鏡頭:** `lens-r6.txt` 我沒讀。派工詞說明鏡頭是備份,而這次改動的產品碼只有 YAML 規則與樣本,我判不影響圖譜鏡頭的固定席。

臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/架構對齊-sonnet` 已用字面絕對路徑刪除。

最嚴重:clean;blocking 共 0 條;不對齊共 0 條,其中 major 0 條
