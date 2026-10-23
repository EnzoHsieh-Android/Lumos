severity: clean

資源鏡頭沒有找到會讓機器卡住的問題。

我用 python3 的 sqlite3 把範本 `android-ui-attribution.sql`(取自 f96ffe70)跑在大量假資料上,做法是照 diff 的 `_ui_attr` 建四張表。表上沒有 `parent_id` 索引,SQLite 自動建索引,所以每個數字都是無索引下量的。每幀 42 個區段,一部分巢狀、一部分掛在 doFrame 底下:

| 幀數 | 區段數 | 耗時 |
|---|---|---|
| 3,000 | 12.9 萬 | 0.74 秒 |
| 10,000 | 43 萬 | 2.65 秒 |
| 30,000 | 129 萬 | 8.31 秒 |
| 100 幀,每幀 3,000 區段 | 30 萬 | 1.74 秒 |

幀數增加 3 倍,耗時也約 3 倍,成長是線性的。計劃 PITFALL 說的「12.6 萬區段 234 秒」那個平方級問題沒有重現。每幀 3,000 個區段的深層巢狀也只要 1.74 秒。我沒有 trace_processor,所以真實 Trace 上的成本沒量到,上面全是 SQLite 的數字。

## 三問逐條走過

1. **子程序與執行緒殘留**:diff 沒有新增任何子程序、執行緒或背景工作。範本是純 SQL,測試只用記憶體內的 sqlite3,沒有殘留的東西要收。
2. **時間預算**:新測試的資料只有幾幀、幾個區段,執行時間可忽略。上表顯示 12.9 萬區段不到 1 秒、129 萬區段也只要 8 秒,沒有大輸入把正常操作擋下的路徑。
3. **記憶體與二次方工作**:遞迴 CTE `tree` 的每一步直接查 `slice s ON s.parent_id = t.id`。`names` 只對不重複的區段名算一次,`kids` 先 GROUP BY。我沒有找到二次方的路徑。最大那組 129 萬列的記憶體用量是線性的,範本沒有讓輸入翻倍的結構。
   - 引句:「SELECT s.id, t.frame_id, COALESCE(n.own, t.fam)」
   - file: `scripts/templates/android-ui-attribution.sql:262`

## skill 新步驟

「分 XML / Compose」每次只對基準與候選各跑一次查詢。沒有截圖,也沒有每列迴圈。composition tracing 只在「專案沒開」時請專案重跑同一個情境一次,是單次成本。裝置時間沒有暴增。

## 圖譜鏡頭(固定席)

各節點宣稱的合約和這份 diff 都不衝突:

- **lumos-cli-read**:search 的 superseded 篩選。diff 在 `scripts/lumos` 只改了 `_VENDORED_TREE_FILES` 加一行,不影響。
- **測試假綠形態**:修 bug 的還原翻紅釘要配前置斷言。diff 沒有改動這條規則的測試,新測試還各自帶了「前置:範本檔在 scripts/templates/」的斷言。
- **pitfalls-code-loop**:diff 沒有碰 `pitfalls` 的程式路徑,不影響。
- **design-loop**:處置閘第五步。diff 沒動 loop 或閘邏輯,不影響。
- **bound-tests-gate**:code-loop check 對固定席合約綁的測試逐支真跑。`test_lumos.py` 只新增測試,沒改既有測試,不影響。
- **guard-kill**:diff 完全沒碰 guard kill 的程式,不影響。
- **lumos-cli-lifecycle**:re-inject 保留 sentinel 之外的內容。diff 沒動 re-inject,不影響。
- **授權與歸屬**:範本檔頭有 SPDX 兩行,符合「被複製的檔至少要有 SPDX 註解行」。範本沒有加進 `_VENDORED_TOOLKIT`,也不是授權檔,不違反「授權檔永遠不得出現在 `_VENDORED_TOOLKIT`」。
- **其餘「超出上限只列名」的節點**:不逐條答。

我的暫存目錄已刪除。

總結:最高嚴重度 clean
