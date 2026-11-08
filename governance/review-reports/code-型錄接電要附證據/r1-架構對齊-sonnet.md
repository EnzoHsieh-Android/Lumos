severity: minor

## 第一問:分層與依賴方向

新函式都放在 `check.py` 這一層,沒有跨層直呼。讀節的 `_section` 放在讀表函式之上,`wiring_table`、`wiring_problems` 接進 `catalog_problems`,走的是 `pending_problems` 的路。測試端只呼叫 `ck.wiring_problems`、`ck.wiring_table`,沒有在測試裡另寫一套重數。依賴方向跟 `_pending_table`、`situation_dir` 一致。`wiring_dir` 公開,對應既有的 `situation_dir`(`configs/ast-grep/kotlin-android/check.py:633`)。

引句:「    problems += pending_problems(text, rows) + wiring_problems(text, rows) + stats_problems(text, rows, rules)」

## 第二問:命名與寫法

大方向跟鄰居一致。整理後 `pending_problems` 的 `_pending_table` 與 `_abbr_table` 共用 `_section`。`_stats_expected` 的新增列沿用 `("標籤", 正規式, 重數)` 的元組。出處重用 `_VERIFIED_RE`(`check.py:780`)。龜甲括號寫成 `\u3014` 跳脫,跟 `_VERIFIED_RE` 同一招。作廢那行有 `[status:superseded]` 和 `[被取代:]`,跟 `docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md:64` 一致。細節有五處寫法跟鄰居不同,都是 minor。

### 發現 1:列層級的錯誤訊息沒有〈接電證據〉前綴
`pending_problems`(`check.py:547`)的每條訊息都以〈待查證〉開頭。`_wiring_row_problems` 的兩條卻以「通電批次」開頭,計劃 S2 也寫「以〈接電證據〉開頭」。結果是測試被迫把過濾條件放寬成 `startswith(("〈接電證據〉", "通電批次"))`,舊測試原本只要比 `"第四批" in p[1]`(`scripts/test_lumos.py:129148`)。

引句:「        out.append("通電批次的批四標籤跟〈接電證據〉不一致:要寫" + ("「批四(" + ";".join(want) + ")」" if want else "沒有批四"))」

severity: minor
blocking: 否

### 發現 2:`wiring_table` 公開,但新 WHY 沒交代
讀同類節的 `_pending_table`(`check.py:527`)是底線開頭。`t_kt_catalog_private_helpers`(`scripts/test_lumos.py:132560`)和 `Systems/kotlin規則包.md:32` 的 WHY 規定:只在檔內用的輔助要加底線,公開的例外要寫明(`situation_dir` 就有寫)。`wiring_table` 與 `wiring_dir` 因為測試要呼叫而公開,新 WHY 沒說這是刻意的例外。⚠ 公開本身可能合理,不一致只在「沒記」。

引句:「def wiring_table(text):」

severity: minor
blocking: 否

### 發現 3:新 REVISIT 與舊 REVISIT 並存,舊的前提已過時
`Systems/kotlin規則包.md:484` 的舊 REVISIT 還寫「第四批接電靠讀官方檢查頁判」,這個前提已被本次推翻。patch 沒有結案,也沒有照 `Systems/存量漂移守衛.md:49` 的 `[closed:日期 理由]` 寫法處理。計劃裡又新增了日期相同的 REVISIT:2027-02-08,兩條並存。⚠ 舊條仍有「消費專案真跑」的檢查價值,所以只列 minor。

引句:「REVISIT:2027-02-08 有消費專案接上 CI 範本之後,拿〈接電證據〉節每筆「擋得到」的壞例在那個專案真跑一次,沒報的改判擋不到」

severity: minor
blocking: 否

### 發現 4:家節點沒記新樣本目錄
`Systems/kotlin規則包.md:32` 和第 86 行有交代 `samples/situation/` 的位置與「改了就同時改」的步驟。`samples/lint-wiring/` 實際存在,但家節點目前沒有任何一處提到它。patch 只新增了描述判定的 WHY,沒補檔案位置或維護步驟。

引句:「型錄自檢 check.py 的 wiring_problems 雙向比對判定表與通電批次」

severity: minor
blocking: 否

### 發現 5:測試的改壞寫法寫了複本卻不走複本
鄰居 `t_kt_catalog_batch4_wiring`(`scripts/test_lumos.py:129169` 一帶)的寫法是:`_ktpack(copy=True)`、`cp.CATALOG.write_text`、`cp.catalog_problems`。新測試的 `mutate` 也寫了複本,卻把 `new_text` 直接傳給 `wiring_problems`。複本的 `CATALOG` 寫入沒有被讀到,真正被讀的只有 `wiring_dir`。另外 `_ = _re` 是為了消掉未使用的 import 才加的。

引句:「        cp.CATALOG.write_text(new_text, encoding="utf-8")」

severity: minor
blocking: 否

## 第三問:第二種做法

沒有另起一套。讀節用 `_section`,認列用 `_MAIN_ROW_RE` 加 `_cells`,出處用 `_VERIFIED_RE`,候選只住 `batch4_candidates`,`batch4_expected_tags` 改成呼叫它,候選口徑沒有分叉。

⚠ 一處判不準:`_batch4_have` 自己用 `_BATCH4_RE` 解析「告警帶寫法=」那一段,而 `template_problems` 對「行為測試或正向約束=」另有解析。兩個是不同的子段,各一個正規式,還不算第二種讀法。如果之後再多一個子段解析,才該抽共用函式。

引句:「    i = batch.find("告警帶寫法=")」

不對齊共 5 條,其中 major 0 條
