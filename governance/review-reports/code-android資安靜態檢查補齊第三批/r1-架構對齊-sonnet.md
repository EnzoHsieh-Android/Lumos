severity: minor

## 1. 分層與依賴方向

對齊。
- 新規則放的位置跟第一、二批同一套:會擋的放 `rules/`,不接閘的放 `rules-unwired/`。`kt-jackson-default-typing` 放 `configs/ast-grep/kotlin-android/rules-unwired/data.yml`,跟 `kt-rsa-no-oaep`(同檔)並排。
- `kt-compose-password-keyboard` 放 `rules/compose.yml`。這是依主題放的,第二批會擋的規則是放 `rules/api.yml`(`configs/ast-grep/kotlin-android/rules/api.yml:272-280`),所以沒有新增層。規則包節點那條 WHY 也同步補了第三批的放置。
- 新測試 `t_kt_catalog_security_lint_batch3` 的依賴方向跟第二批一樣:經 `_ktpack()` 取得 check.py 模組,再呼叫它的 `m.main_rows()`、`m.dt_table()`、`m.situation_dir()`、`m.catalog_problems()`。對照 `scripts/test_lumos.py:129439-129455` 的第二批,以及 `scripts/test_lumos.py:130922` 已有的 `kp.dt_table` 用法。
- 沒看到跨層直呼,也沒有測試自己重讀型錄或規則檔。

## 2. 命名與錯誤處理

大體對齊,有兩條不一致。

- 對齊的部分:
  - 規則 id 全用 `kt-` 加連字號。
  - 訊息格式是 `[UI-112]…;改用…`,跟 `[DATA-98]…;改用 …` 一樣(`configs/ast-grep/kotlin-android/rules-unwired/data.yml:515-519`)。
  - `ignores` 用單行 `[...]`,跟 `rules/api.yml:253,280` 一致。
  - 樣本檔路徑、`// BAD`、`// GOOD` 註解寫法,跟 `kt-rsa-no-oaep` 一樣。
  - 測試輔助函式 `_kt_batch3_catalog_problems` 的命名與回傳「問題清單」的做法,跟 `_kt_batch2_catalog_problems` 一樣。

- 不對齊 A:`_KTSEC_CASES` 新增的 22 列用單引號字串。
  - 該表既有列(`scripts/test_lumos.py:126829` 起,C01~C94)全是雙引號。
  - 結構沒變,只是字面不一致。
  - 這比較接近風格偏好,但同一張表裡兩種引號會讓之後的人猜該跟哪種。
severity: minor
  blocking: 否
  引句:「('src/main/kotlin/C95.kt', 'TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())'」

- 不對齊 B:`t_kotlin_rulepack_security_rules` 的 docstring 沒有補第三批。
  - 第一批、第二批各自在 docstring 裡寫了「翻紅釘」清單(`scripts/test_lumos.py:127036` 起的「第二批(…)混合內容 setter 改回 stopBy: end → C53 紅…」)。
  - 這批只動了程式,docstring 的 hunk 沒有列 C95~C116 對應哪些改壞動作。
  - 只有 `_KTSEC_CASES` 上方的一行註解提到 C100、C110~C112 與 C116。
severity: minor
  blocking: 否
  引句:「第三批([[Projects/Android資安靜態檢查補齊第三批_計劃]] 預期值表 S1 逐列;C100、C110~C112 是桌面四項排除各一例」

## 3. 第二種做法

整體沒有引入第二套讀型錄或讀規則的方式。讀規則走 `load_rules`(沿用 `got = set((r or {}).get("ignores", []))`,該行有代碼審 r1 架構對齊 F1 的備註)。讀型錄走 `main_rows` 與 `dt_table`。有一處需要注意。

- 不對齊:`_KTSEC_PLACE` 的值變成「長度不定」。
  - 原本全是 3 元組 `(目錄, 檔, 編號)`。
  - 這批只有密碼欄多帶第 4 個元素 `"desktop"`,迴圈改成 `(d, fname, cat, *extra)`,再用 `extra == ["desktop"]` 選期望的排除清單。
  - 結構上沒有另寫一套表,但同一張表裡出現兩種形狀,用字串旗標切換,不是在值裡直接放期望的排除清單。
  - 計劃寫的是「期望值寫在 `_KTSEC_PLACE` 各條的值裡」,這個做法算照計劃。
  - 但鄰居的慣例是每條值形狀一致,所以我標 minor,不判 major。
  - ⚠ 交編排者:專案裡沒有既有的「某條規則排除清單不同」的先例可對,無法判這是不是第二種做法,我不硬判成 major。
severity: minor
  blocking: 否
  引句:「"kt-compose-password-keyboard": ("rules", "compose.yml", "UI-112", "desktop"),」

- 對齊的部分:
  - `_KT_BATCH3_ROWS` 是 id 到元組的 dict,加上 `_kt_batch3_catalog_problems` 與測試函式,跟 `_KT_BATCH2_ROWS`(`scripts/test_lumos.py:129351`)同一個形狀。元組多了一格「通電批次」,是擴充不是另一套。
  - `_KT_STATS_LINES` 只改數字,沒改結構。
  - 型錄新列 UI-112、DATA-99、DATA-100 的欄位順序與接電寫法,跟 DATA-96~98 與 UI-111 的語意列一致。
  - D-57 比照 D-56 的格式(證據樣式 `(無)` 兩段、對應檢查、來源網址)。
  - 樣本目錄結構與命名跟 `samples/{bad,good}/kt-rsa-no-oaep/src/main/kotlin/` 一致。

我自己建的路徑:無(沒有在 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/架構對齊-sonnet/` 底下建任何東西)。

不對齊共 3 條,其中 major 0 條
