severity: minor

## 第一問 分層

規則、型錄、情境樣本、規則包節點的落點都照第二批和既有慣例走,沒有跨層直呼。

- 密碼欄規則放 `rules/compose.yml`。這個檔本來就收會擋的 Compose 規則。檔內只有第一條 `kt-compose-expensive-calc-in-body` 有 `ignores`(三項),其餘 Compose 規則沒寫(`configs/ast-grep/kotlin-android/rules/compose.yml:92`)。
- Jackson 規則放 `rules-unwired/data.yml`。這個檔的既有規則都帶八項排除(`configs/ast-grep/kotlin-android/rules-unwired/data.yml:7`)。
- D-57 的情境樣本放 `samples/situation/D-57.kt.txt`。這個目錄已有 D-16、D-32、D-51(`configs/ast-grep/kotlin-android/samples/situation/D-51.kt.txt`),用 `// === main-ok …` / `// === bad …` 分段,計劃寫的段名一致。
- 手寫節放型錄的統計與決策表,規則包 WHY 放 [[Systems/kotlin規則包]],都對得上第二批。
- 計劃用 `[[Systems/kotlin規則包]]` 當落點,該節點已存在,不必另開新的。

引句:「資安自寫規則放哪一級那條 WHY 補第三批(密碼欄放 `rules/compose.yml`、Jackson 放 `rules-unwired/data.yml` 與理由),不另開新行。」

## 第二問 命名與寫法

大致對齊,有兩點跟鄰居不一致。

- 規則 id 用 `kt-compose-password-keyboard` 和 `kt-jackson-default-typing`,跟既有的 `kt-compose-*`、`kt-webview-*` 命名一致。
- 訊息要求「`[型錄編號]` 開頭、≤120 字」跟 `_KTSEC_PLACE` 的現有檢查一致(`scripts/test_lumos.py:127020`)。
- 型錄列 UI-112、DATA-99、DATA-100 和 D-57 沿用「編號往下接」的做法。證據樣式寫法 `主寫 … 、例外 (無)` 符合型錄的格式說明(`skills/kotlin-idioms/checks-catalog.md:730`)。

minor 一:`kt-compose-password-keyboard` 的 12 項排除寫法沒交代。既有慣例是「單行 `[...]` 八項」。`check.py` 的 `load_rules` 兩種寫法都讀(`configs/ast-grep/kotlin-android/check.py:80`),所以不是結構問題。但 `rules/compose.yml` 全檔只有一處 `ignores`,是三項的多行寫法。計劃沒說這條要照 `data.yml`/`api.yml` 的單行八項加四項的樣子寫,還是照 compose.yml 的多行。這是寫法跟鄰居不一致的風險,不是第二種做法。

引句:「路徑排除:既有八項,另加 Compose 多平台的桌面原始碼四項 `**/src/desktopMain/**`、`**/src/jvmMain/**`、`**/desktop*/src/**`、`**/*-desktop/src/**`」

severity: minor
blocking: 否

## 第三問 第二種做法

路徑排除的逐條期望值沒有另起一套,測試綁法有一處和第二批鄰居不同。

- 現行測試把八項釘成對所有規則通用的常數 `_KTSEC_IGNORES`,並對每條 `_KTSEC_PLACE` 規則比對「恰好是八項」(`scripts/test_lumos.py:127026`)。計劃把它改成逐條期望值(這條 12 項、其他 8 項)。這是同一個測試、同一個讀法(`load_rules`),只是期望值從常數變成逐條取值,不算第二種做法。
- 測試的期望值要放哪裡,計劃也沒寫。我建議擴充 `_KTSEC_PLACE` 的值,這樣最小。
- S3/S4 的綁法有不一致。第二批把型錄內容與統計分別綁到專屬的型錄測試:`t_kt_catalog_security_lint_batch2`(`scripts/test_lumos.py:129408`)和 `t_kt_catalog_stats_consistent`(`scripts/test_lumos.py:129490`)。第三批把 S3 綁到 `t_kotlin_catalog_rows_wired`,那是一般格式測試。S4 要驗「三列在主表、D-57 對應 DATA-100、情境樣本自測過」,卻綁到 `t_kotlin_rulepack_security_rules`,而這個測試只跑 ast-grep 規則和路徑、訊息,現在不讀型錄主表、不看情境樣本。依第二批做法,S4 該有一個類似 `t_kt_catalog_security_lint_batch3` 的專屬測試。沒有專屬測試,S4 要驗的事沒有程式去驗。
- 這不是另起第二套機制。型錄自檢 `catalog_problems + situation_sample_problems`(`scripts/test_lumos.py:129312`)已存在,缺的只是測試要真的呼叫它。所以評為 minor,不是 major。

引句:「[S4] 當讀真型錄時,UI-112、DATA-99、DATA-100 應 各在主表,D-57 應 在情境決策表而且對應檢查是 DATA-100,D-57 的情境樣本 應 通過證據樣式自測 [test:t_kotlin_rulepack_security_rules]」

severity: minor
blocking: 否

不對齊共 2 條,其中 major 0 條
