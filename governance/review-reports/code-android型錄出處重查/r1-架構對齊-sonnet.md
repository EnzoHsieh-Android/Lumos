severity: minor

我只讀了凍結 patch 與倉庫裡的鄰居檔,沒有改任何檔,也沒有跑測試。

**1. 分層與依賴方向**
- 內容大致放對層。型錄列和〈統計〉在 `skills/kotlin-idioms/checks-catalog.md`。決策記在計劃的 `decisions:`。回頭條件用 REVISIT 與 `[closed:]`。細節放 Verification。測試輔助函式放在 `scripts/test_lumos.py` 型錄統計區。
- 新驗證紀錄的 frontmatter 與 `plan_refs`、`system_refs` 結構,跟鄰居 `docs/lumos-toolchain-knowledge/Verification/2026-11-09_Android型錄待查證列逐列核對.md:1-17` 一致。
- `Systems/kotlin規則包.md` 的 `verified_by` 也補上了新紀錄。
- CERT 算權威來源的決策 d4 放在 `Android不接閘資安規則重量_計劃`,和它所關的 REVISIT 同檔,也對。
- 沒有發現放錯層。

**2. 命名與寫法**
- 〔查證 2026-11-09:網址〕的寫法,跟原有的〔查證 2026-11-07:…〕完全相同,對得上 `checks-catalog.md:13` 的口徑。
- D-58、D-59 的欄位順序、「主:(無);例外:(無)」和網址以空白分隔,都跟 D-57 一致。D-57 見 `checks-catalog.md:408`,D-55 的網址用「 ; 」分隔,所以兩種寫法本來就並存。
- 決策 d1、d4 的欄位(content、id、context、why_chosen、decided、valid)和該檔原有決策一致。
- `[closed:2026-11-09 決策 d1:…]` 沿用既有的 `[closed:日期 …]` 形狀。
- 劃掉撤除條件用 `~~…~~(日期 決策 d1 劃掉:理由)`。同 repo 的 `必要合約清單_計劃.md:117` 和 `:187` 也用 `~~` 加理由,所以算有先例。這也照該計劃 REVISIT 自己寫的「把 RETIRE-IF 前半段劃掉並寫理由」做。
- 輔助函式 `_kt_pend_seed`、`_KT_PEND_HEAD`、`_KT_PEND_ROW` 的前綴跟 `_kt_line_sub`、`_kt_drop_line`、`_kt_bump`、`_KT_STATS_MUTATIONS` 一致。`_kt_pend_seed` 也呼叫了同檔的 `_kt_line_sub`。
- 只有一處跟鄰居不一致:

A1
severity: minor
blocking: 否
引句:「API-14、API-36、UI-103、TEST-31 查不到或跟官方相反,維持出處不全,五條規則移出規則包」
file: `skills/kotlin-idioms/checks-catalog.md:1084`
說明:這次改動讓 API-36 依 CERT 拿掉出處不全,同一個 diff 裡 API-36 的型錄列也改成「2026-11-09 改以 CERT ERR51-J 為出處」。但〈統計〉「逐列查證」這行的歷史句子沒同步,仍寫它「維持出處不全」。這行是疊歷史的寫法,所以可能是刻意留舊紀錄。但同一行只改了數字,沒補 API-36 已翻案,讀的人會看到前後相反,判不準,標 ⚠。

**3. 第二種做法**
- 測試改壞的種子:以前每條改壞都寫死用真型錄的 CO-3 那一行(長字串)。現在改成 `_kt_pend_seed` 先造一個一致的待查狀態,再只動一處。這是因為 CO-3 的待查已解決、真型錄沒有待查列了,屬於被迫改法,而且加了前置檢查 ①b(`seed != text` 且自檢數量不變)。測試裡本來就有「前置:有套上」的紀律,所以不算第二種做法。
- 決策表補列、出處不全加〔查證〕、`[closed:]` 加新 REVISIT、新驗證紀錄,全都是既有機制。我沒看到新機制或新格式。

不對齊共 1 條,其中 major 0 條
