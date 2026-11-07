severity: major

我讀了整份 spec,逐條核對了引用的程式、函式和測試名。我把 `draft-rules.yml.txt` 複製到 `/tmp/lumos-seat-work/android資安與崩潰靜態檢查補齊/通才-sonnet/` 用 ast-grep 實跑了壞例。

**finding 1**
severity: major
blocking: 是(實測有直接寫法漏報,而且 spec 的實驗、預期值表、天花板都沒抓到,屬設計缺口)
- spec 段落:範範圍 4「WebView 開檔案網址跨來源存取」、實驗表第一列、S3 預期值表最後一列。
- 問題:規則的屬性寫法 `$X.allowUniversalAccessFromFileURLs = true` 對多層接收者不命中。壞例是 `webView.settings.allowUniversalAccessFromFileURLs = true`,這是 Android 最常見的寫法。
- 場景:使用者寫 `webView.settings.allowFileAccessFromFileURLs = true`,規則不報,推送前放行。
- 預期值表只測單層的 `settings.x = true`,實驗只量命中裡的誤報、不量漏報,所以這個洞兩邊都抓不到。
- 引句:「`allowUniversalAccessFromFileURLs = true`、`allowFileAccessFromFileURLs = true`」
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/governance/review-reports/android資安與崩潰靜態檢查補齊/experiment/draft-rules.yml.txt:10`
  - 這是 `$X.` 前綴那條屬性 pattern,第 11 行同形。我實跑五行:`settings.allow... = true` 命中,`w.settings.…`、`webView.settings.…`、`binding.web.settings.…` 三種多層接收者全沒報。
  - 只有 `apply {}` 內的裸寫法(第 12、13 行那兩條)和 `setAllow...(true)` 呼叫形式會中。
- 建議:改成用 kind 比對屬性賦值,或明列多層接收者的壞例進樣本。

**finding 2**
severity: major
blocking: 是(漏掉最典型的違規形狀,spec 只承認放過旗標名類)
- spec 段落:範圍 4 的除錯模式與舊版 TLS、〈實務隱患〉「自寫規則的 if 判斷會放過真問題」。
- 問題:規則認 if 祖先,只看條件字串是不是單純的 SDK_INT 比較,完全不看 true 分支還是 else 分支、也不看否定。「只在正式版開啟」這個 MASTG 要抓的形狀,正好被當成有開關放行。
- 實測:`if (!BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) }` 不報。`if (BuildConfig.DEBUG) { } else { WebView.setWebContentsDebuggingEnabled(true) }` 也不報。
- 〈實務隱患〉只舉 `isBeta`、`isXposedHooked` 這類旗標,沒提否定和 else,實驗放過的 4 處也沒分這幾種。
- 同一邏輯套在舊版 TLS 上:`if (x) { SSLContext.getInstance("TLSv1") }` 也被放行。
- 引句:「往外找到的任何一層 if,條件只要不是單純比 `Build.VERSION.SDK_INT` 就不報」
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/governance/review-reports/android資安與崩潰靜態檢查補齊/experiment/draft-rules.yml.txt:38`
  - 第 38 到 45 行的 `not: inside: stopBy: end kind: if_expression not: has field: condition regex`。
- 建議:至少把 `!` 開頭的條件和 else 分支從放行集合拿掉,並寫進壞例。

**finding 3**
severity: major
blocking: 是(驗收條款綁的測試守不住條款內容)
- spec 段落:驗收條款 S3、S4。
- 問題:S3 綁 `t_kotlin_rulepack_samples`。這支測試只檢查「每條規則壞例命中至少 2 處、好例零命中且至少兩段」,以及載入條數和祖先目錄那類通用項。
- 場景:實作者漏寫 `SDK_INT < 23` 那個該報的壞例,或漏寫 `src/debug` 與 `ComptibleTLS.cipherSuites` 好例,只要仍有 2 處壞例、2 段好例,測試照綠。S3 列的具體好例壞例都不在測試斷言裡。
- S4 綁的 `t_kotlin_rulepack_security_rules_placement`、S1 綁的 `t_linter_catalog_android_security_lint` 在 `test_lumos.py` 都不存在。S4 又沒列規則 id,測試要斷言什麼無從寫起。
- 另外 `kt-` 開頭的 id 沒定,新型錄列編號沒定,但訊息要以列編號開頭。
- 引句:「壞例 應 各自命中;好例 應 不報:除錯模式包在 `if (BuildConfig.DEBUG)` 或任何非 SDK 版本比較的 if 裡」
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/scripts/test_lumos.py:126344`
  - 既有測試 `t_kotlin_rulepack_samples` 的 docstring 和內容只有上述通用檢查。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/configs/ast-grep/kotlin-android/check.py:825`
  - 樣本閘只判「壞例 n<2」「好例有命中」「好例 <2 段」。
- 建議:S3 每一格預期值都要有可執行的逐例斷言;規則 id 先在 spec 定死。

**finding 4**
severity: minor
blocking: 否(誤報面,spec 已認誤報預算一成以內)
- spec 段落:範圍 4 寫死金鑰與除錯模式。
- 問題:兩處會誤報。
  - `SecretKeySpec(byteArrayOf(*parts), "AES")` 這種由變數展開組出的金鑰會被報,實測命中。
  - 除錯模式只認 `if`,`when { BuildConfig.DEBUG -> setWebContentsDebuggingEnabled(true) }` 沒排除,實測命中。
- 這兩個形狀都沒在好例清單裡。
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/governance/review-reports/android資安與崩潰靜態檢查補齊/experiment/draft-rules.yml.txt:103`
  - `pattern: SecretKeySpec(byteArrayOf($$$), $$$)` 沒排除 spread 運算子。

**各節結論**
- 範圍 1(範本加資安規則包)
  - 已讀,無 finding。
  - 我抓了官方 README,`com.android.security.lint:lint` 的安裝語法和 spec 引的一樣。
  - spec 引的九個資安包檢查 id,README 都列得到。
- 範圍 2(型錄登記)
  - 已讀,無 finding。
  - 型錄現有主表的最大列編號,和 `_MAIN_ROW_RE` 的九類相符。
- 範圍 3(`_B4_LINT` 認 `資安包:`)
  - 已讀,無 finding。
  - `check.py:107` 的正則確實沒有 `資安包`,切段符號是 `;` 和 `、`,和 spec 描述一致。
  - 資安包的檢查 id 都是大寫開頭,會被正則接住。
- 〈實驗〉、〈回退〉、〈天花板〉
  - 已讀,無 finding。
  - 實驗只量命中內的誤報,漏報已寫在天花板 1;但 finding 1 和 2 的漏報不是量不到,是設計內建的。
- 圖譜節點
  - `Systems/kotlin規則包`:不破壞宣稱的行為,新規則走既有 `rules/` 與樣本閘機制,樣本閘 `check.py:825` 的行為不變。
  - `Systems/linter精選目錄`:不破壞宣稱的行為,只加一行依賴進範本第 1 步;`warningsAsErrors` 那行原樣保留。
  - 副作用:該節點第 184 行的「先產基準線再開 `warningsAsErrors`」會讓新接的資安包也繼承,spec 第 1 點已寫這件事。
- 實務隱患鏡頭
  - 守衛面:有隱患,見 finding 1 到 4。
  - 金流:無,不碰付款。
  - 對外送出:無,規則與型錄是本機讀檔,範本依賴由人照抄。
  - 不可逆:無,退提交即回原狀。

最嚴重 severity: major,blocking 共 3 條。
