severity: major

整體判斷:新規則、樣本、型錄列、測試的放置與命名都照鄰居。有一處引入第二種做法:BuildConfig.DEBUG 的判法。另有一條 minor。

**問 1 分層與依賴方向**

規則放置與鄰居一致。
- 新規則照主題放進既有的 `api.yml`、`data.yml`,不另開檔。會擋的那條在 `rules/api.yml`,其餘三條在 `rules-unwired/`。`rules-unwired/` 的 `api.yml` 原本就有 `kt-error-by-message-string`,在 `configs/ast-grep/kotlin-android/rules-unwired/api.yml:1`。
- 樣本目錄是 `samples/{bad,good}/<規則id>/src/main/kotlin/<規則id>.kt`,跟 `samples/bad/kt-http-logging-body-unguarded/src/main/kotlin/kt-http-logging-body-unguarded.kt` 一樣。
- 呼叫方向對。測試只呼叫 `check.py` 的 `load_rules`,不繞過它。修補把測試自己讀 `ignores` 的那段刪掉(原本約 5 行 `re.split`),改讀 `r["ignores"]`,讀法收成一套。
- 型錄列和 `_B4_LINT` 只多認一個 `資安包` 前綴,放在原本認 `內建`、`slack` 的位置,結構沒變。

**問 2 命名與錯誤處理**

命名一致:
- 規則 id 都是 `kt-` 加 kebab。
- 訊息是 `[型錄編號]錯在哪;改用…`,用單引號包起來,跟 `configs/ast-grep/kotlin-android/rules/api.yml:49` 同格式。
- 測試名是 `t_kotlin_rulepack_*`、`t_kt_catalog_*`,docstring 帶 `[S3]`、翻紅釘。
- 測試的訊息上限改讀 `m.MSG_MAX`,對齊 `check.py:30`,不再寫死 120。

F1 是 minor。
severity: minor
blocking: 否
`load_rules` 新增的 `ignores` 欄位只吃單行 `ignores: [...]`。專案裡有鄰居用多行清單寫法:`rules/state.yml:250` 和 `rules/data.yml:41`。這兩條讀出來會靜默得到空清單,而不是報錯或照樣解析。docstring 有寫「單行」,所以不算隱瞞。但回傳欄位叫 `ignores`,讀者會以為涵蓋所有寫法。目前四條新規則都是單行,沒有實際誤判。
引句:「ignores 是那份文件單行 `ignores: [...]` 裡用引號括住的路徑清單(沒寫就是空清單)。」
佐證 file:`configs/ast-grep/kotlin-android/rules/state.yml:250`、`configs/ast-grep/kotlin-android/rules/data.yml:41`

**問 3 第二種做法**

F2 是 major,另標 ⚠ 交編排者。
severity: major
blocking: 是
包裡原本判「有沒有包在 DEBUG 裡」的做法,是 API-19 那條。它用 `inside: any: [if_expression, when_expression]`,再 `has: pattern: BuildConfig.DEBUG, stopBy: end`,見 `configs/ast-grep/kotlin-android/rules/api.yml:49-60`。這次新增的是另一套判法:`control_structure_body`、`follows: ^else$`、`has field: condition regex ^BuildConfig\.DEBUG$`、`when_entry` 加 `when_condition`。同一段 20 行判法還在兩條規則各抄一份,一份在 `rules/api.yml`,一份在 `rules-unwired/api.yml`。修補把它貼進 `kt-webview-file-url-access`,這份重複就是修補造成的。
- 該條規則自己的註解寫著「同 kt-webview-debugging-enabled 的判法」,等於承認是手抄同步。
- 兩份落在不同的 sgconfig 目錄,`utils:` 在同一檔內才共用。要共用得另設共用目錄,所以不能直接說「應該用 utils」。
- 計劃〈不做〉明寫「不改既有 API-19 的除錯判法(…同族問題另記)」,所以這是有記錄的取捨,不是疏漏。
- 派工詞點名的就是這種形狀(同一個除錯判斷在多條規則各寫一份,而包裡原本是另一種寫法),所以我照錨標 major。是否放行請編排者判斷。
引句:「寫在條件恰好是 BuildConfig.DEBUG 的 if 成立那一支或 when 分支裡不報(同 kt-webview-debugging-enabled 的判法,代碼審 r1)」
佐證 file:`configs/ast-grep/kotlin-android/rules/api.yml:49`(既有判法);新判法在 `rules/api.yml:290-306` 與 `rules-unwired/api.yml:38-55`。

測試方面沒有第二種做法:
- 找檔路徑用 `Path(GRAPHCTL).resolve().parents[1]`,`scripts/test_lumos.py` 裡有 20 處同寫法。計劃已記錄「兩種並存放行」。
- 批四前綴的測試沿用同檔 `t_kt_catalog_batch4_wiring` 的 `tags` 與 `ck._cells` 做法。
- 掃描沿用 `_ktpack_sg` 和 `m.scan`,沒有另抄一份。

不對齊共 2 條,其中 major 1 條。檔級等級為 major。
