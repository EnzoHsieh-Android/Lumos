severity: minor

我沒有找到會做出錯行為的洞,只有兩條 minor,都不阻擋。三個修補我都用修前、修後兩版範本各跑一次同一批輸入。邊界輸入我造假表跑了約 25 種,另外把 clone 在 `46773fe6` 的樹上各改壞一次,看測試會不會翻紅。實驗目錄 `/tmp/lumos-seat-work/code-android-ui-kind/邊界-sonnet/` 已用字面絕對路徑刪除。

## Finding 1:沒收尾的中間區段,名稱只出現一次時,它底下已收尾的子樹整段消失
severity: minor
blocking: 否
引句:「    FROM (SELECT DISTINCT name FROM main)」
file: `scripts/templates/android-ui-attribution.sql:47`
歸因:有證據的原有漏查(修前修後輸出相同,不是修補回歸)
- **原因:** `names` 只從 `main`(`dur >= 0`)取名稱,`tree` 卻直接走原始 `slice` 表。沒收尾的區段(dur=-1)名稱若沒在別處以收尾形式出現過,`JOIN names` 接不上。
- **失敗場景:** 幀 10ms 底下掛 `("measure", -1, [("Compose:a", 3)])`。
  - 修前和修後輸出都一樣:compose=0、pipeline=0、other=10。
  - Compose:a 的 3ms 被丟掉,不是算給 Compose。
  - 它的父區段 self 也沒扣掉這一段,所以多層時四類加總會超過幀長。
- **根因:** 跟 r1 修掉的 NULL 名稱是同一族(名稱接不上就整段消失)。這次修補只改了 `=` 變 `IS`,沒有掃同族的另一個入口。
- **⚠ 真實性存疑:** 合法的 trace 裡,收尾的 doFrame 底下不太會有沒收尾的後代,因為父區段會比子區段晚收尾。所以我不升級。

## Finding 2:收據重跑腳本寫暫存查詢檔沒指定編碼,範本現在帶中文註解
severity: minor
blocking: 否
引句:「    with tempfile.NamedTemporaryFile('w', suffix='.sql', delete=False) as f:」
file: `scripts/templates/android-receipt-rerun.sh:52`
歸因:有證據的原有漏查(修前修後這一行相同;只是新範本讓非 ASCII 內容變成必然)
- **重現:** 把範本整份貼進 `queries.sql`,用 `LC_ALL=C PYTHONCOERCECLOCALE=0 PYTHONUTF8=0` 跑 `rerun.sh`。結果丟 `UnicodeEncodeError: 'ascii' codec can't encode characters`。
- **預設環境:** 預設的 UTF-8 環境我跑過,回 0。
- **後果:** 寫暫存檔那一步 Python 直接崩潰,是大聲失敗不是假綠,但 rc=1 的意思是「比對不符」,讀的人會誤判成量測不符。
- **建議:** 加上 `encoding='utf-8'`。

## 三問
1. **原問題修復的行為證據**,三個修補都成立:
   - NULL 名稱:兩版跑同一批輸入,修後 `(None,6,[measure 3])` 得 compose=3、pipeline=5(NULL 這層跟祖先、底下的 measure 照算);修前 pipeline=2、other=2,整段消失。
   - 名稱 `draw*` 太寬:修後 `drawable`、`draws`、App 的 `drawChart` 都跟祖先;修前全被吸進管線。
   - 負數:子區段超過父區段時,修前 pipeline=-4,修後 0。
   - 收據截斷:`LC_ALL` 預設環境下,範本整份貼進 `queries.sql`,第一個以分號結尾的行就是最後的 `ORDER BY f.ts;`。我把一行註解尾巴改成分號,`t_android_ui_attribution_receipt_rerun` 翻紅。
   - 授權守衛:`.sql` 第 2 行改成 `# SPDX` 翻紅;`.sh` 拿掉 SPDX 行,或把它的 `#` 改成 `--`,都翻紅。
2. **修補處的正常、錯誤與相鄰路徑**,都仍成立,邊界輸入的結果如下:
   - **名稱邊界:** `draw` 和 `draw-VRI` 算管線;`draw-VRIx` 因為是 `draw-VRI*` 前綴也算管線,這是設計,不算洞。`drawable`、`draws`、`RV`、`Recomposer`(沒冒號)算其他;`RV `、`Compose:`、`compose:` 分別算 XML、Compose、Compose;空字串名稱跟祖先、不崩。
   - **沒有子區段、幀長 0:** 每類都是 0、不崩。
   - **App 區段夾在框架區段之間:** 跟最近能分類的祖先。
   - **函式區段形狀:** java 檔、括號裡不是數字、兩個括號的名稱都不算 Compose 函式。
   - **深巢狀與大量:** 在 sqlite3 假表上,68000 個區段約 0.2 秒;深度 3000 約 0.01 秒。
   - **授權守衛的檔名邊界:** 大寫 `.SQL` 或副檔名不是 `.sql`,都落到 `#` 規則,方向是多報不是漏報。
   - **保留下來的語意:** 子區段超過父區段時取 0,負數被藏起來,但四類加總會超過幀長(例:幀 10ms 的 traversal 5、measure 9、Compose 9,加總 14)。程式裡有註解說明,不構成 finding。
3. **新發現的同一案例在修前、修後各是什麼結果:** 這份報告的兩條 finding 在兩版結果相同,都是原有問題,沒有一條是修補造成的。

## 收據重跑測試與 pitfalls manifest
- **假分析工具會不會在不該過時過:** 測試用的假工具只在收到的查詢檔同時含 `WITH RECURSIVE` 和 `ORDER BY f.ts;` 時才輸出。查詢被截斷就會兩者都缺,上面的改壞實驗確實翻紅,所以不會假綠。
- **pitfalls manifest:** `source:"pitfalls-builtin"` 五條(第 31、47、52、65、75 行,N+1 型樣)全是誤報。它們都是同一個查詢裡的 CTE 內 `SELECT`,沒有迴圈。

## 圖譜鏡頭(固定席逐條)
- **lumos-cli-read 的 `search` 預設排除 superseded:** 不受影響,這份改動沒碰到。
- **測試假綠形態的「前置斷言」:** 沒被破壞,新測試都帶「前置:範本檔在」或「前置:複製清單裡有 .sql」。
- **design-loop(處置閘第五步):** 不受影響,這份改動不涉及設計審。
- **bound-tests-gate(固定席綁定測試逐支真跑):** 不受影響,綁定測試 `t_license_headers_travel_with_vendored_files` 在 clone 上 8 passed。
- **guard-kill(rc 優先序、`--json`):** 不受影響,這份改動沒碰到。
- **lumos-cli-lifecycle(re-inject 只動 sentinel 之間):** 不受影響。
- **授權與歸屬,第一條(授權檔不得進 `_VENDORED_TOOLKIT`):** 不受影響,`.sql` 加在 `_VENDORED_TREE_FILES`。
- **授權與歸屬,第二條(每支被複製的檔至少有 SPDX 註解行):** 沒破壞。只有 `.sql` 認 `--`,其餘仍只認 `#`;`.sh` 缺標示或寫成 `--` 都會紅。
- **pitfalls-code-loop 的 `★RISK★` 與其餘「超出上限,只列名」的節點:** 沒有看到牽連。

總結:最高嚴重度 minor
