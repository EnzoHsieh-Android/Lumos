severity: major

以下所有重現都在 `--shared` clone 檢出的修前 000fc1463 與修後 4dfd6f7db 各跑一次(ast-grep 0.51.1,絕對路徑 `--config <包>/sgconfig.yml`)。臨時目錄已刪。

## Findings

### F1 共用除錯判斷的條件正規式把常見的除錯限定寫法判成會報,修前不報的現在報
severity: major
blocking: 是
歸因:有證據的修復回歸(API-19、DATA-16),API-40、API-41 不受影響
引句:「regex: ^(BuildConfig\.DEBUG|BuildConfig\.DEBUG\s*&&[^|]*|[^|!]*&&\s*BuildConfig\.DEBUG)$」

第三個分支 `[^|!]*&&\s*BuildConfig\.DEBUG` 排除了 `!`,結果 `!=` 和 `!x` 都被擋掉。這兩種寫法實際上都只在除錯版執行,卻報了。

| 輸入 | 規則 | 修前 | 修後 |
|---|---|---|---|
| `level = if (x != null && BuildConfig.DEBUG) Level.BODY else Level.NONE` | API-19 | 不報 | 報 |
| `level = if (!x && BuildConfig.DEBUG) Level.BODY else Level.NONE` | API-19 | 不報 | 報 |
| `if (a != b && BuildConfig.DEBUG) { builder.fallbackToDestructiveMigration() }` | DATA-16 | 不報 | 報 |
| `if (!BuildConfig.DEBUG) { } else { builder.fallbackToDestructiveMigration() }` | DATA-16 | 不報 | 報 |
| `level = if (BuildConfig.DEBUG && (a \|\| b)) Level.BODY else Level.NONE` | API-19 | 不報 | 報 |

- 第 4 列是「非除錯走遷移、除錯才走破壞性」的寫法,else 那一支只在除錯版執行。
- 最後一列的 `[^|]*` 讓括號裡的 `||` 也被排除,是同一個正規式的限制。
- 這兩條規則在 `rules/`,會擋人。
- API-40 在修前就對 `x != null && DEBUG` 報,修後行為不變。

### F2 共用判斷的「X 且 BuildConfig.DEBUG」那個分支完全沒有測試,拿掉或放寬都照綠
severity: major
blocking: 是
歸因:有證據的修復回歸(新分支與新測試表都是這次修補加的)
引句:「("src/main/kotlin/C27.kt", "if (BuildConfig.DEBUG && s != null) { webView.settings.allowFileAccessFromFileURLs = true }",」

C25 到 C35 只有 DEBUG 在 `&&` 左邊(C27)。DEBUG 在 `&&` 右邊的寫法沒有案例。我在改動後 clone 的副本上做了兩個變異,各跑 `-k kotlin_rulepack_security_rules`:

- 整個拿掉 `|[^|!]*&&\s*BuildConfig\.DEBUG` 分支:51 passed, 0 failed。
- 把 `[^|!]*` 改成 `.*`:51 passed, 0 failed。這樣 `if (a || b && BuildConfig.DEBUG) { webView.settings.allowFileAccessFromFileURLs = true }` 會被放行。a 為真時這行在正式版照跑,會擋人的 API-40 就此漏報,測試卻綠。

對照組:拿掉 else 排除、讓 `!BuildConfig.DEBUG` 被接受、把 `&&` 分支改成也吃 `||`,測試都會紅(分別是 C07/C25/C32、C06/C24/C34、C28)。這幾個子條件有守住,沒守住的只有 `X && DEBUG` 分支與它排除 `!` 的作用,所以 F1 的誤報也沒被抓到。

### F3 舊版 TLS 新增的屬性賦值寫法在多層接收者、`!!`、`apply` 區塊、`arrayOf<String>` 時仍然漏報
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前這些屬性寫法全不報,修後只補一部分)
引句:「+            - pattern: $S.enabledProtocols = arrayOf($$$)」

| 輸入 | 修後 |
|---|---|
| `a.b.enabledProtocols = arrayOf("SSLv3")` | 不報 |
| `socket!!.enabledProtocols = arrayOf("SSLv3")` | 不報 |
| `socket.apply { enabledProtocols = arrayOf("SSLv3") }` | 不報 |
| `socket.enabledProtocols = arrayOf<String>("SSLv3")` | 不報 |
| `sock?.setEnabledProtocols(arrayOf<String>("SSLv3"))` | 不報 |

這和 r1 為 API-40 指出的毛病同族:賦值左邊的接收者用單一節點樣式配,多層接收者會漏。API-40 已改成用節點種類比對,這裡沒套同一招。只有 `socket.enabledProtocols`、`socket?.enabledProtocols` 與單層方法呼叫會報。這條規則在 `rules-unwired/`,不擋人,所以只算 minor。

### F4 共用判斷對帶套件名的 BuildConfig.DEBUG 與 `when (BuildConfig.DEBUG)` 主詞寫法不認
severity: minor
blocking: 否
歸因:帶套件名那個是有證據的原有漏查;`when` 主詞寫法對 API-19 是有證據的修復回歸(修前不報、修後報)
引句:「regex: ^BuildConfig\.DEBUG$」

- `level = if (com.foo.BuildConfig.DEBUG) Level.BODY else Level.NONE`:修前、修後都報。多模組專案有多個 BuildConfig 時常這樣寫。
- `when (BuildConfig.DEBUG) { true -> level = Level.BODY; false -> level = Level.NONE }`:API-19 修前不報、修後報,因為 when_condition 是 `true`,不是 DEBUG。

## 三問回答

**① 修補宣稱修好的有何行為證據**
- 共用判斷、else、when、且、或各子條件確實有效,修前修後對照如下:
  - DATA-16 的 else 分支(`if (DEBUG) {x} else {fallbackToDestructiveMigration()}`)、`!DEBUG`、`DEBUG && x || y` 都變成報,符合計劃宣稱。
  - DATA-16 的 `when { DEBUG -> fallback }` 修前誤報、修後不報。
  - API-19 的 `if (DEBUG) NONE else if (y) BODY` 修後正確報。
  - 多行條件 `DEBUG &&\n x` 不報,正確。
- 舊版 TLS 的 `?.setEnabledProtocols`、`socket.enabledProtocols`、`socket?.enabledProtocols` 修前全不報、修後報。其餘寫法見 F3。
- load_rules 讀多行 `ignores`:現有 rules 的多行寫法是縮排的 `  - '…'`,新正規式讀得到。但 `ignores` 欄位只被 `t_kotlin_rulepack_security_rules` 的 S4 讀,而那四條規則都是單行寫法,所以多行讀法沒有測試。我沒找到實際會失敗的場景,所以不列 finding。
- 我在改動後 clone 上跑了 `-k kotlin_rulepack`(99 passed, 0 failed)與 `-k kt_catalog`(48 passed, 0 failed)。

**② 修補處的相鄰路徑**
- 修前不報、修後報:F1 的五列、F4 的 `when (DEBUG)` 主詞寫法。
- 修前報、修後不報:DATA-16 的 `when { BuildConfig.DEBUG -> fallback }`(原本誤報)。
- 修後仍會漏報的保護缺口:見 F2 的 `a || b && DEBUG` 放行變異。
- utilDirs 在消費專案用絕對路徑 `--config <包>/sgconfig.yml` 時找得到 utils。我在另一個 cwd 的專案目錄實跑,`matches: kt-in-debug-only-branch` 正常解析,四份 sgconfig 都掛了。
- 共用判斷對括號、多行、帶套件名的判法:
  - `if (BuildConfig.DEBUG)`:不報。
  - `if (com.x.BuildConfig.DEBUG)`:報。
  - `DEBUG &&\n x` 跨行:不報。
  - `(a || b) && DEBUG`、`DEBUG && (a || b)`:報(F1)。

**③ 同一案例修前修後**
F1 到 F4 每個案例的修前、修後結果都附在各 finding 裡,逐一在兩個檢出版本各跑一次。

**未驗範圍**
- 型錄 41 列與 check.py 批四口徑的內容正確性。
- 不同版本 ast-grep 對 `utilDirs` 的支援。
- 圖譜固定席:派工詞說鏡頭計算超時,不必補算,我沒做。
- 角色卡 be-api-compat、be-authz:本次是靜態規則包,沒有對外 API 或端點,沒有命中題。

臨時工作目錄 `/tmp/lumos-seat-work/code-android資安與崩潰靜態檢查補齊/審查三-sonnet/` 已刪除。
