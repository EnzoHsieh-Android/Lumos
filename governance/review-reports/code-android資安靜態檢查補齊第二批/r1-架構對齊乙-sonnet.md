severity: minor

審查的是乙包 patch(型錄、測試、圖譜筆記)。我對照了 `checks-catalog.md` 既有列、`scripts/test_lumos.py` 的鄰居測試、`check.py` 的讀表函式和 `kotlin規則包.md` 既有的 WHY 行。沒有發現第二種做法或跨層直呼,不對齊的三條都是 minor。

## 1. 分層與依賴方向:對齊

- **讀表走 check.py:** 新的 `_kt_batch2_catalog_problems`、`_kt_stats_problems` 讀型錄都走 `m.main_rows()`,不另抄一份讀表。鄰居 `t_kt_catalog_security_lint_ids` 也是這樣(`scripts/test_lumos.py:129102` 一帶),`check.py` 自己註明主表唯一讀法在 `main_rows`(`configs/ast-grep/kotlin-android/check.py:542`)。自檢和查證數則呼叫 `m.catalog_problems`、`m.situation_sample_problems`、`m.catalog_unverified`(`check.py:340`、`472`、`569`)。
- **測試位置與輔助函式:** 新測試放在 `t_kt_catalog_security_lint_ids` 緊接後面,輔助函式放在本檔,和 `_kt_ui39_problems`(`test_lumos.py:127769`)、`_kt_instr_template_problems`(`127378`)同一做法。
- **擴充既有表:** 規則實跑案例是往既有的 `_KTSEC_CASES`、`_KTSEC_PLACE` 追加,沒有另開一張表。擴充的是 `t_kotlin_rulepack_security_rules`。
- **型錄列落點與欄位:**
  - 12 欄格式與鄰居一致,例如 `checks-catalog.md:626` 的 DATA-87。
  - 第一批 API-47 等現成檢查列,用「LINTREF 〔查證 日期:網址〕」記來源;新增的內建檢查列 ARCH-89、DATA-95 照同一寫法。
  - 「內建:」前綴是型錄已有的寫法(例如「內建:SetJavaScriptEnabled」),ARCH-89、DATA-95 沿用,沒有新發明。
  - 自寫規則列也照 DATA-87 的「無(自寫 ast-grep …)」、「告警帶寫法=未接(規則在 rules-unwired/ …)」寫。
  - 新列依主題放進對應的 API、ARCH、DATA 表,沒有放錯節。

## 2. 命名與錯誤處理:三條 minor

**finding 1:新增的 16 筆 `_KTSEC_PLACE` 裡,有 6 條沒有對應的 `_KTSEC_CASES` 實跑案例。**
- 沒案例的是 `kt-weak-cipher-suite`、`kt-provider-openfile-traversal`、`kt-weak-key-size`、`kt-object-input-stream`、`kt-db-on-external-files`、`kt-xxe-documentbuilder`,它們只過目錄和訊息編號那道檢查。
- 鄰居第一批的四條自寫規則,在 `_KTSEC_CASES` 裡每條都有案例(例如 `test_lumos.py:126783` 一帶的 `kt-webview-debugging-enabled`)。
- 第二批的 docstring 又寫「C48~C71 與 _KTSEC_PLACE 後 16 筆」,讀起來像兩邊一一對應。
severity: minor
blocking: 否
引句:「第二批([[Projects/Android資安靜態檢查補齊第二批_計劃]] S1、S2 擴充同一組,C48~C71 與 _KTSEC_PLACE 後 16 筆)」
既有檔佐證:`scripts/test_lumos.py:126783`

**finding 2:新測試的段落標記跟鄰居重複。**
- `t_kt_catalog_security_lint_batch2` 標 `[S3]`,`t_kt_catalog_stats_consistent` 標 `[S4]`。
- `t_kotlin_rulepack_security_rules` 已經用 `[S3][S4]`,同一個 S 編號在不同測試各指不同東西。
- 鄰居 `t_kt_catalog_security_lint_ids` 標的是自己的 `[S5]`。
- 第二批測試的 ②③ 兩道,又把鄰居 ids 測試的 S5 自檢(`catalog_problems`、`catalog_unverified`)原文再跑一次。
severity: minor
blocking: 否
引句:「真型錄自檢 0 個問題、還沒逐列查證 0 列。判準來源:計劃範圍 1~3 原文(寫死在 _KT_BATCH2_ROWS、_KT_BATCH2_LINT)。」
既有檔佐證:`scripts/test_lumos.py:129102`

**finding 3:`_kt_stats_problems` 自己切節、直接讀型錄檔。**
- 它自己用 `m.CATALOG.read_text` 讀檔,再用 `text.find("\n## 統計")`、`"\n## 待查證"` 切節。
- `check.py` 的 `catalog_problems` 也有同樣的找節寫法(`check.py:344` 的 `i_dt, i_pend = text.find(...)`)。
- 讀型錄的函式放在 check.py(`catalog_unverified`、`catalog_problems`),測試只呼叫。這裡統計重數的邏輯整段留在測試檔。
- 主表讀法本身有走 `main_rows`,所以不算第二種讀法;只是節的切法在兩處各寫一份。
- ⚠ 鄰居本身不一致:`_kt_ui39_problems` 這類判準也留在測試檔,交編排者裁。
severity: minor
blocking: 否
引句:「i_st = text.find("\n## 統計")」
既有檔佐證:`configs/ast-grep/kotlin-android/check.py:344`

## 3. 第二種做法:沒有

- **筆記摘要行:** 規則放置的 WHY 是改既有那一行(`-  WHY:資安四條自寫規則只有 kt-webview-file-url-access…` 改成兩批合寫的一行),沒有另開新行。格式是 `[出處:][因:][不選:][test:]`,和 `kotlin規則包.md` 的既有 WHY 行一致。
- **型錄欄位:** 沒有新欄位、新前綴。
- **測試判準:** 判準寫死在 `_KT_BATCH2_ROWS`、`_KT_BATCH2_LINT`,不從型錄或規則包反算。這是 ids 測試 `_ASL_README_IDS` 的同一做法。
- **新開的計劃筆記:** 設計類筆記一律寫成 `Projects/<主題>_計劃`,符合專案規則。

不對齊共 3 條,其中 major 0 條
