severity: minor

重點:修補把判準搬進 `check.py`,測試只呼叫 `catalog_problems`,分層和鄰居一致。沒有第二種讀表或判法,也沒有跨層直呼,所以沒有 major。剩下 5 條 minor,都是命名、docstring 或改壞做法的小差異。

## 問 1 分層與依賴方向

對得上。改寫後的測試不重寫判準,直接呼叫自檢函式。
引句:「mine = [p for p in base if p[0] == "<統計>" or "待查證" in p[1]]」
- 鄰居 `t_kt_catalog_batch4_wiring` 也是呼叫 `ck.catalog_problems(ck.load_rules())`,再用訊息字樣篩出自己那一類。對照 `scripts/test_lumos.py:129078`。
- 判準住在 `check.py`:`pending_problems`、`stats_problems` 都重用 `_cells` 和 `_MAIN_ROW_RE`,並接在 `catalog_problems` 後面。鄰居的口徑也住在那支檔,見 `configs/ast-grep/kotlin-android/check.py:120`(`batch4_expected_tags`)和 `:359`。
- `_kt_batch2_b4_problems` 呼叫 `m.batch4_expected_tags`,沒有在測試裡另寫口徑。

## 問 2 命名與錯誤處理

結構對,有 4 條 minor。

**finding 1**
severity: minor
blocking: 否
引句:「_kt_batch2_b4_problems」旁的 `elif "批四(" + ";".join(want) + ")" not in cell(rid, 9):`
- 測試把「批四(...)」的標籤格式又拼了一次,和 `check.py:361` 是同一個字串。
- 鄰居改用 `check.py` 暴露的常數:`f"批四({lint})"` 搭配 `ck.B4_TAG_LINT`,見 `scripts/test_lumos.py:129078`。
- 口徑沒有分叉,所以只算 minor。

**finding 2**
severity: minor
blocking: 否
引句:「型錄 → 第二批 S3 的問題清單(空=全過);m 是 _ktpack() 載入的模組(改壞實驗給複本)。判準全部寫死在本檔」
- 這句 docstring 沒跟著改。`_kt_batch2_catalog_problems` 現在多呼叫了 `m.batch4_expected_tags`,所以「全部寫死在本檔、不從型錄或規則包算」不再成立。
- `t_kt_catalog_security_lint_batch2` 的翻紅釘也沒提新增的批四那道。
- 鄰居 `t_kt_catalog_batch4_wiring` 的 docstring 有寫「口徑住在 check.py」,見 `scripts/test_lumos.py:129078`。

**finding 4**
severity: minor
blocking: 否
引句:「_STAT_TOPICS = ("API", "FLOW", "STATE", "CO", "UI", "ARCH", "DATA", "TEST", "PERF")」
- 主題清單在 `check.py:98` 的 `_MAIN_ROW_RE` 已有一份,這裡再列一份,兩處要手動同步。
- 同一支檔裡沒有先例。
- 只是常數重複,判法沒有重複,所以算 minor。

**finding 5**
severity: minor
blocking: 否
引句:「return [("<catalog>", "找不到〈統計〉節")]」
- 同一個函式 `stats_problems` 的錯誤代號混用兩種:節不存在用 `<catalog>`,數字不符用 `("<統計>", f"{label} 寫 {got},重數是 {n}")`。
- `check.py:396` 既有的全域問題代號只用 `<catalog>`。
- 測試因此要寫成 `p[0] == "<統計>" or "待查證" in p[1]`,比鄰居用單一字樣篩選多一層。

docstring 條款標記:新測試首行用 `[[Projects/...]] S4:`,和 `t_kt_catalog_batch4_wiring` 一致。有判準來源、翻紅釘,格式和鄰居相同。⚠ 鄰居自己混用 `[S1]` 這種寫法(如 `t_kotlin_rulepack_samples`),請編排者裁示,我不算它不一致。

## 問 3 第二種做法

沒有重抄讀表、判法或口徑。舊測試檔裡抄的 `_kt_stats_problems`、`_kt_stats_extra_problems`、`_kt_pending_problems` 三份已整段刪除,改走 `check.py`。

改壞實驗的做法有一處不同。

**finding 3**
severity: minor
blocking: 否
引句:「tmp = Path(tempfile.mkdtemp(prefix="kt-stats-"))」
- 新測試在沒有複本的 `_ktpack()` 上,自己建暫存目錄,再把 `m.CATALOG` 改指過去。
- 鄰居每次改壞都走 `_ktpack(copy=True)`,再寫 `cp.CATALOG`,見 `scripts/test_lumos.py:126509`、`:129108`、`:127862`。
- 兩邊用的機制相同(模組屬性加暫存檔),所以我定為 minor。差別只在沒有重用 `_ktpack` 的複本輔助,暫存目錄前綴是 `kt-stats-` 而不是 `gctl-ktpack-`,另外多了 `finally` 加 `rmtree` 清理。
- 清理那段比鄰居好,符合全域暫存清理規則。但 `m.HERE`、`m.TEMPLATES` 沒有跟著改指,只有 `CATALOG` 指向暫存檔。
- 其餘做法和鄰居一致:改壞字串照真型錄寫死,並有「★前置★ 有套上」的檢查(`mut != text`)。⚠ 請編排者裁示:要不要改回 `_ktpack(copy=True)`,或接受這個較省複製的版本。

筆記沒有另開行。`Systems/kotlin規則包.md` 裡沒有舊的統計守衛 WHY,所以新增的那行是新主題。
引句:「WHY:型錄〈統計〉〈待查證〉兩節是手寫的,判準住在 check.py 的 stats_problems」
- 格式有 `[出處:]`、`[因:]`、`[不選:]`、`[test:]`,和相鄰 WHY 行一致。
- 兩批資安規則那條 WHY 是改既有行,沒有另開新行,符合計劃範圍 5。
- 型錄〈待查證〉、〈統計〉的說明句沿用「手寫(沒有程式產生,改主表時一起改):…」句式,和既有節一致。

不對齊共 5 條,其中 major 0 條
