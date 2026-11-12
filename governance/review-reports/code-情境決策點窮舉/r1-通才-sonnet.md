severity: minor

審查範圍是 r1-code.patch 的三支程式。我逐 hunk 讀完,並追了 `scripts/lumos` 的 `_kt_sit_text_segments`、`_kt_sit_rows_rx`、`_kt_trigger_re`、`_stack_changed_ok`,以及 `check.py` 的 `_cells`、`_fence_regions`、`template_sections`、`load_lumos`。

本機實測:
- `-k kt_catalog_api_decision` 28 過 0 敗。
- `-k bad_snippets_reach` 22 過 0 敗。
- 對真型錄跑 `_reachable` 195 個反查單位約 0.1 秒,效能沒問題。
- 單獨一個 `"`、`{`、`/*`、`"""` 當片段,都乾淨地判成「叫不出」,沒有拖垮切段。

我沒找到 blocker 或 major。

**重用與簡化類**
- `_kt_sit_path_ok` 的抽出與原本兩處內聯條件等價:`not cur or PAT.search(cur) or not ok` 等於 `not cur or not path_ok`。
- 推送端兩個呼叫點(`scripts/lumos:39969`、`scripts/lumos:69407`)和 `check.py:1064` 都改叫它,沒有重做既有東西。
- `scan` 保留三元組介面,改成包 `scan_ranges`,舊呼叫端沒有被弄壞。

**固定席(LUMOS-LENS 這次沒附節點,我自行判斷)**
- 影響範圍:`_kt_sit_path_ok` 抽出後行為不變,推送前的情境段和鏡頭計算兩條路徑都沒變,對既有合約不影響。
- 新增的兩道自檢只在 `check.py` 與 `--catalog-only` 裡跑,不進推送路徑。

**Finding 1**

severity: minor
blocking: 否

〈叫不出的壞寫法〉表上若有兩列完全相同(情境列、對應檢查、片段都一樣),`check.py` 不會報。
- 原因:`bad_snippet_reach_problems` 用 `listed = {(r, c, s): (route, why) ...}` 把重複列併成一筆。
- 對照:〈API 決策點〉對同名重複有報「同一個名稱出現兩列」,這邊沒有對等的檢查。
- 我複製了一列叫不出的列,`bad_snippet_reach_problems` 仍回 `[]`。
- 代價:兩列的改由欄可以互相矛盾(一列「規則」、一列「代碼審」),後面那列的驗證被吞掉,表也會比統計行多一列。
- file: `configs/ast-grep/kotlin-android/check.py:484`

引句:「listed = {(r, c, s): (route, why) for r, c, s, route, why in table}」

**Finding 2**

severity: minor
blocking: 否

「規則」改由的起訖行核對只比「同一檔、同一規則,有沒有任何一個節點涵蓋任何一條符合片段的 `// BAD` 行」。
- 規則報的是涵蓋整個函式或類別的大節點時,該檔其他不相干的 `// BAD` 行也會被涵蓋,所以判成通過。
- 這道守衛擋不住「規則其實沒報到片段那一行,只是報了同一個大節點」。
- 這是弱化,不是失效;現行 5 條規則列沒有證據顯示出事。
- file: `configs/ast-grep/kotlin-android/check.py:506`

引句:「if isinstance(idx, dict) and not any(a <= no <= b for f, no in hits for a, b in idx.get((rule_id, f), ())):」

**Finding 3**

severity: minor
blocking: 否

`check()` 裡後面的 `problems.append(("<reach>", "要載入 scripts/lumos:" + why))` 用的 `why`,可能不是載入 lumos 失敗的原因。
- 原因:同函式中間的 SARIF 迴圈有 `got, why = sarif_gate_rule_ids(...)`,把 `why` 覆蓋了。
- 目前兩邊載入失敗的原因字串相同,不會真的出錯。但 SARIF 回傳形狀一變,訊息就會錯,甚至在 `why` 是 None 時組字串丟 TypeError。
- 這是同名變數重用的維護風險;`lumos, why` 與 SARIF 的 `why` 應分開命名。
- file: `configs/ast-grep/kotlin-android/check.py:1522`

引句:「problems.append(("<reach>", "要載入 scripts/lumos:" + why))」

總結:max severity minor,blocking 0 條。
