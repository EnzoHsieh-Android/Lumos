severity: major

**a1** 把 `?:` 加進共用的 `_CHOICE_OP_RE`,會讓既有 ROR/AOR 等列在運算元含 `?:` 時當掉
severity: major
- 計劃的設計:範圍 3 寫「`_CHOICE_OP_RE` 最前面加 `?:`」,〈用詞〉另說「第一版各列的運算子位置不會變成 `?:`」。
- 引句:「`_CHOICE_OP_RE` 最前面加 `?:`。」
- 既有寫法:這個常數不只給 `_choice_anchor` 用。
  - file: `scripts/lumos:77184` 的 `_choice_top_prec` 也用它。這支函式對表外運算子(含 `?:`)的設計是「回 0、一律加括號」(`scripts/lumos:77176` 的 docstring 寫明)。
  - file: `scripts/lumos:77185` 的 `_CHOICE_PREC[m.group(0).decode("utf-8")]` 是直接查表。
  - `_CHOICE_PREC`(`scripts/lumos:76875`)沒有 `?:` 這個鍵。
- 差在哪:加進去之後,頂層含 `?:` 的運算元一進 `_choice_top_prec` 就 KeyError。
  - 例子:`a ?: b > c` 的 `$A` 是 `a ?: b`,Kotlin 裡 `?:` 比比較運算子結合得緊。
  - 這發生在 `_choice_swap_edits`(`scripts/lumos:77293` 起)算優先層級時,也就是第一版 ROR/AOR/LCR 的既有路徑。
  - S7 只釘「不含 `?:` 的行」,抓不到這個回歸。
- 現成可用的做法:「`?:` 錨點」另用一支專用的運算子正規式,或同時把 `?:` 的層級補進 `_CHOICE_PREC` 並補一條含 `?:` 運算元的測試。
- blocking: 是。判準:改動共用常數的語意,會讓既有列的路徑當掉,屬於跨用途的第二種語意。

**a2** 放行接列號的做法,另寫了一套歸屬規則,沒用既有帳事件已帶的 `row`
severity: major
- 計劃的設計:範圍 5 的放行段,每筆放行用 (檔, 行指紋) 去接「放行之前最近一筆存活事件」,列號取存活事件的 `row`;接不上的另計「沒接上」。
- 既有寫法:
  - file: `scripts/lumos:18425` 的 `ck_waive` 已經帶 `label, row, decl, file, fp` 五個欄位。
  - file: `scripts/lumos:17906` 到 `17910` 的 `_gov_choice_counts` 已經直接用 `w["row"]` 當放行的列號(乾節點候選的 `shape` 計數就是這樣算的)。
- 差在哪:同一份「放行屬於哪一列」的資料,現行段用放行事件自己的 `row`,計劃另造一套「回頭接存活事件」的歸屬。
  - 計劃沒說明放行事件自己的 `row` 為什麼不能用。
  - 兩段(乾節點候選與依列號)可能把同一筆放行算進不同列。
  - 「沒接上」這一類也是新發明的,既有算法裡不存在。
- 要補的內容:計劃要先講清楚 `ck_waive.row` 哪裡不夠。講不出來就直接用它,「沒接上」可以整個拿掉。
- blocking: 是。判準:同一件事既有帳欄位現成可用,卻另寫第二種歸屬做法。

**a3** 「依列號」的計數沒指定落在既有的計數函式,事件欄位的擴充也沒寫
severity: minor
- 計劃的設計:範圍 5 寫「吃已去重的統計列(`_render_gov_choice` 收到的那份)」,壞法以 (檔, 行指紋, `new_sha`) 為單位,列號取事件帶的 `row`。
- 既有寫法:
  - file: `scripts/lumos:18423` 的事件欄位白名單,`ck` 只留 `file, fp, killing_test, changed, mutant_lines, secs, reasons`,沒有 `new_sha`。`row` 在上一行是頂層欄位。
  - 既有的計數是 `_gov_choice_counts` 與 `_gov_choice_count_verdict`(`scripts/lumos:17896` 與 `17940`)這一條線,印出在 `_render_gov_choice`。
- 差在哪:
  - 計劃沒寫要把 `new_sha` 補進這份白名單。不補的話,「以壞法雜湊為單位」做不出來。
  - 計劃也沒寫計數落在 `_gov_choice_counts` 這條線裡,只說「加一小節」。實作者可能再開一個獨立迴圈。
  - 去重鍵(`scripts/lumos:18486` 起)是 (commit, nodes, gate, kind, token, check)。同一提交內「先存活後被殺」的兩筆事件,有可能在去重階段就被併掉,計劃的「取時間最新那筆當終態」不一定看得到兩筆。
- 建議寫法:在範圍 5 明講「擴充 `_gov_choice_counts` 與事件白名單」,並對 S8 補一個同提交先存活後殺掉的案例。
- blocking: 否。判準:方向對、只是落點與欄位沒寫明,屬於可補的規格缺口,不是已確定的第二種做法。

**a4** 錨點「引數」的選行邏輯放在 `_choice_file_points`,繞過 `_choice_anchor` 這個唯一的錨點分派
severity: minor
- 計劃的設計:範圍 3 的選行段,「引數」列由 `_choice_file_points` 檢查節點範圍內任一行是否被改到,錨點行取範圍內第一個改動行;其他錨點照舊。
- 既有寫法:file: `scripts/lumos:77118` 的 `_choice_anchor(b, hit, row)` 是「命中節點到錨點位移」的單一分派處。`scripts/lumos:77470` 起的 `_choice_file_points` 只用 `line_of(anchor) in want` 判斷。
- 差在哪:兩條錨點路徑並存,一條在 `_choice_anchor`,一條在選行處。
  - `_choice_pick` 排序用的 `n["anchor"]` 可能與實際選行用的不同。
  - 計劃裡也沒說 `n["anchor"]` 在「引數」列要存哪一個值。
- 建議做法:把 `lines_changed` 傳進 `_choice_anchor`(或回傳起迄行),讓錨點只有一個出處。
- blocking: 否。判準:偏離程度小、可在實作時收斂,但要在計劃裡寫明 `anchor` 欄位的值。

**不影響的部分(對照過、判乾淨)**
- 規則檔格式:`nul.yml` 與 `api.yml` 補列,沿用「一個類別一個檔」、id 等於列號、用 `not:` 排除等價寫法(對照 `configs/ast-grep/kotlin-choice/rules-choice/api.yml` 與 `sbr.yml` 的 C-18 先例),沒有引入第二種規則格式。
- `check.py`:`CHOICE_CATEGORIES` 與 `CHOICE_ANCHORS`(`configs/ast-grep/kotlin-android/check.py:1392` 與 `1393`)仍是唯一白名單,lumos 讀表經 `choice_tables`,做法一致。
- `_choice_edits` 補三個分支:
  - 「安全呼叫符」與「引數」兩個新分支是按錨點欄分派,跟既有的方法名分支同形。
  - `$A!!` 沿用 `_choice_atomic` 與 `_choice_ctx_safe`。
  - `(刪掉)` 沿用 `tpl == "delete"` 最前面那條。
- 型錄列與決策表互指:D-5、D-6、D-32 都存在(`skills/kotlin-idioms/checks-catalog.md:744`、`745`、`771`),格式沿用 C-31 列。
- 圖譜固定席節點(`Systems/規格閘`、`Systems/kotlin規則包`):兩篇都掛 0 條合約。
  - 計劃不改處置鍵 (檔, 行指紋),不改殺傷力判定與推送前那一道,所以不破壞它們宣稱的行為。
  - 規格閘的 20 行 KEY 與計劃的新增項(依列號統計、新列)沒有衝突。
  - 計劃已要求同步改兩篇的說明。

最嚴重 severity: major,blocking 共 2 條(a1、a2)。
