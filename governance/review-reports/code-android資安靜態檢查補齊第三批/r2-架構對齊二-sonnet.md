severity: clean

我讀了完整的 r2-snapshot.patch 和 r2-repair-review.patch,也用 `git show b3561e61a:scripts/test_lumos.py` 對照修後版本。比對對象是第一、二批的鄰居檔,結論是沒有發現「第二種做法」,也沒有跨層直呼。

**1. 分層與依賴方向:對齊**
- 兩條規則放的位置跟第二批的邏輯一致。會擋的密碼欄規則放 `rules/compose.yml`(主題相近、會接閘),不接閘的 Jackson 規則放 `rules-unwired/data.yml`。鄰居是 `kt-rsa-no-oaep` 放 `rules-unwired/data.yml`,且 `rules/api.yml` 也只有第一、二批各一條會擋的規則。
- 樣本放在 `samples/{bad,good}/&lt;id&gt;/src/main/kotlin/&lt;id&gt;.kt`,跟 `samples/bad/kt-rsa-no-oaep/src/main/kotlin/kt-rsa-no-oaep.kt` 同形。
- 修補把 `_KTSEC_IGNORES` 與 `_KTSEC_IGNORES_DESKTOP` 搬到 `_KTSEC_PLACE` 前面,讓第四格直接放排除清單。讀規則的方式仍只有 `check.py` 的 `load_rules`,測試裡的註解 `讀法只有 check.py 的 load_rules 一套` 沿用。測試沒有自己另寫一套 YAML 解析。
- 這個搬動前後的兩版我都比對過:`git show 1abb0f2bd` 的 `_KTSEC_IGNORES` 在 `_KTSEC_PLACE` 之後(126994 行),修後 `b3561e61a` 在之前(126998 行,PLACE 在 127003 行)。這是修補自己動的位置,但沒有改變誰呼叫誰。

**2. 命名與錯誤處理:對齊**
- 規則 id 都是 `kt-*`,訊息以 `[UI-112]`、`[DATA-99]` 開頭且不超過 120 字,跟 `[DATA-98]` 同形。file: `configs/ast-grep/kotlin-android/rules-unwired/data.yml:520`
- 新規則的 `ignores` 用單行清單,跟 `rules/api.yml:253` 和 `rules-unwired/data.yml:521` 同寫法。
- 規則上方的註解標題照第二批的寫法:`[[Projects/…_計劃]]` 加理由。
- 修補把新測試案例從單引號改成雙引號,與 `_KTSEC_CASES` 既有的 C48~C94 一致。這是修補去對齊鄰居,不是引入新的不一致。
- 測試函式 `t_kt_catalog_security_lint_batch3`、常數 `_KT_BATCH3_ROWS`、輔助函式 `_kt_batch3_catalog_problems` 的命名與第二批 `_KT_BATCH2_ROWS`、`_kt_batch2_catalog_problems` 同形。
- 錯誤處理一律是回傳問題字串清單,再交給 `check()`,跟第二批同形。

**3. 第二種做法:沒有**
- 型錄新列(UI-112、DATA-99、DATA-100)的欄位數與寫法跟 API-48、DATA-88、DATA-98 同形:現成規則欄寫「無(自寫 ast-grep …)」,實測狀態欄寫「真實語料:樣本內…樣本外…」。
- 〈統計〉各行與 D-57 決策表列沿用同一格式。語意列 DATA-100 的欄位與 UI-111 同形(`表態對程式、盲判席`、`未測`)。
- 改壞實驗用 `_ktpack(copy=True)` 加 `mc.CATALOG.write_text`,跟既有的 `t_kotlin_catalog_rows_wired`、`t_kt_catalog_stats_consistent` 是同一套做法,不是新做法。
- 第二批的 `t_kt_catalog_security_lint_batch2` 本身沒有改壞步驟,第三批多了兩個。這是補強,不是另一種形狀。
- 修補後 `_KTSEC_PLACE` 的第四格是排除清單,取代了修補前的字串 `"desktop"` 標記。這避免了一個只在這裡用的魔術字串,沒有引入新做法。測試裡也沒有別的地方還在比對 `"desktop"`,我用 grep 對照過。
- 一個沒歸入發現的觀察:修補後 `_KTSEC_PLACE` 的結尾 `}` 和 `def t_kotlin_rulepack_security_rules` 之間是 3 行空行,不是慣例的 2 行(`git show b3561e61a:scripts/test_lumos.py` 的 127030~127032 行)。這純屬排版,依規則不列。

不對齊共 0 條,其中 major 0 條

我在 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/架構對齊二-sonnet/ 底下只建了一個檔:`t.py`,是 `b3561e61a` 版 test_lumos.py 的副本。
