severity: minor

這份 diff 大致沿用既有做法。我只找到一處跟第二批不一致的地方,屬測試覆蓋形狀,沒有第二套做法或跨層直呼。

**1. 分層與依賴方向:對齊。**
- 新規則放的位置跟第一、二批一樣。會擋的 `kt-compose-password-keyboard` 附加在 `rules/compose.yml` 檔尾,對照 `rules/api.yml` 第 245 至 253 行的 `kt-webview-file-url-access`。不接閘的 `kt-jackson-default-typing` 附加在 `rules-unwired/data.yml` 檔尾,對照同檔第 7、28、565 行。
- 規則檔頭註解的連結寫法(`# [[Projects/…_計劃]]:…`)、`id`、`language`、`severity`、`message` 的順序、`ignores` 用單行清單,都跟 `rules/api.yml` 第 245 至 253 行相同。桌面四項排除是在同一份八項清單後面追加,沒有另開機制。
- `rules/compose.yml` 第 92 行有一條舊規則用多行 `ignores:`,新規則用單行。同檔有兩種寫法,但新規則跟資安規則的寫法一致,不列為不一致。
- 樣本放在 `samples/{bad,good}/&lt;規則 id&gt;/src/main/kotlin/&lt;規則 id&gt;.kt`,跟既有的 `samples/bad/kt-rsa-no-oaep/src/…` 一樣。
- 測試只呼叫 `_ktpack()`、`m.main_rows()`、`m.dt_table()`、`m.situation_dir()`、`m.catalog_problems()`、`m.situation_sample_problems()`。這些都是 `t_kt_catalog_security_lint_batch2` 已在用的 `check.py` 介面,沒有跨層直呼。

**2. 命名與錯誤處理:大致對齊,有一處不齊。**
- 命名對齊:`_KTSEC_IGNORES_DESKTOP`、`_KT_BATCH3_ROWS`、`_kt_batch3_catalog_problems`、`t_kt_catalog_security_lint_batch3` 都照 `_KT_BATCH2_ROWS`、`_kt_batch2_catalog_problems`、`t_kt_catalog_security_lint_batch2` 的名字與 `print` 格式。
- 訊息格式對齊:`[UI-112]…`、`[DATA-99]…` 開頭不空格,與 `[API-40]…` 相同。
- 回傳錯誤的方式對齊:問題清單是字串 list、`probs[:10]` 截斷,跟第二批相同。
- 改壞實驗對齊:`★前置★` 加 `★改壞★`,跟第二批一致。
- 計劃檔〈審計修正紀錄〉的 r2 那行少了卷證路徑。r1 那行已寫了 `governance/review-reports/…` 路徑,r2 這行沒有。第二批計劃是 r1 之後另起一行寫「席報告:…」。這屬於文件寫法細節,我歸在下面那條 minor 一起帶過。

severity: minor
blocking: 否
發現:第三批型錄測試少了第二批的「逐列查證 0 列」檢查。`t_kt_catalog_security_lint_batch2` 有 `unv = m.catalog_unverified()` 與「③ 還沒逐列查證是 0 列」。`t_kt_catalog_security_lint_batch3` 只有 ① 和 ②,沒有 ③。新增的三列都帶〔查證 2026-11-08:…〕,目前不會出事。但第三批的 S4 條款也沒承諾這一項,所以是登記範圍的差異,不是漏寫。
歸因:原有漏查。這是第三批初版就有的形狀,r2 修補(`r3-repair-review.patch`)沒有碰測試的這一段。
我怎麼查的:對照 `scripts/test_lumos.py` 第 129359 行與第 129467 行(`catalog_unverified`),再比對 r3-snapshot.patch 裡 batch3 函式的 ①、②、★前置★、★改壞★。
另外,全域的 `t_kt_catalog_unverified_rows`(`scripts/test_lumos.py` 第 129115 行起)已涵蓋整份真型錄,所以實際沒有漏守,風險很低。
引句:「check("② 真型錄自檢與情境樣本自檢 0 個問題", not selfp, str(selfp[:5]))」

**3. 第二種做法:沒有。**
- 讀型錄:仍走 `m.main_rows()` 和 `m.dt_table()`。判準表寫死在測試檔,不從型錄算,跟 `_KT_BATCH2_ROWS` 一樣。
- 讀規則:仍走 `m.load_rules()` 和 `_KTSEC_PLACE`。
- 資料表形狀:`_KTSEC_PLACE` 的值原本是 3 元組,r2 之前就讓它可帶第 4 個選填元素(`(d, fname, cat, *extra)`),屬於擴充同一張表,不是另一張表。`_KT_BATCH3_ROWS` 多了第三欄「通電批次」,是因為第三批要核對 `c[9]`。這個欄位第二批沒有。這是同形狀的資料表加一欄,不是新做法。
- 修補差異(r2 補的 C121 至 C123 與天花板那句改寫)沿用 `_KTSEC_CASES` 的同一種四元組,沒有引入新結構。
- 天花板與預期值表的寫法沿用第二批計劃的 S1 列式和〈天花板〉條列。

不對齊共 1 條,其中 major 0 條

建過的路徑:無(沒有在 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/架構對齊三-sonnet/` 底下建任何東西,也沒有修改 repo)。
