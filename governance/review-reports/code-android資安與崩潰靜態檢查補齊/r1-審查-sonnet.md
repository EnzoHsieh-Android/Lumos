severity: minor

整份 diff 逐 hunk 讀完,只有 3 條 minor。

**型錄抽查:** 我用 curl 抓了 65 個檢查頁(24 條資安包加 41 個內建與併進既有列的 id),每個 id 都對一次。
- 每個 id 的提供者都對得上:資安包的 Vendor 是 Google - Android 3P Vulnerability Research,內建的是 Android Open Source Project。
- 沒有任何一頁寫 disabled by default。我另外 grep 了 DisabledAllSafeBrowsing 頁,那個字是檢查名稱本身,不是預設關。
- README 的 24 個 id 與 `_ASL_README_IDS` 一致,刪除線那條也確實被排除。
- Google Maven 最新版確實是 1.0.4。
- 統計節的數字我用程式重算,全部對上:514 列、各類列數、級的組合、規則 211 條(error 34、hint 50)、批一守到 129 列、查證 500 列。

**測試結果:** 我跑了 `-k kotlin_rulepack`(84 條通過)、`-k kt_catalog`(48 條通過),另外單跑新增的三支與 `t_kt_catalog_batch4_wiring`,全過。`check.py --catalog-only` 回報 0 個問題。

**改壞實驗(在我自己的複本裡做,已刪):**
- 刪掉 `linter精選目錄` 的「已經照範本接過 CI」那句,或把 AGP 8.5.1 改成 8.0,`t_linter_catalog_android_security_lint` 會翻紅。這支測試守得住。
- 另外兩個改壞測試抓不到,見 finding 1、2。

**1.**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/rules/api.yml`(新增的 `kt-webview-file-url-access`)
情境:計劃〈範圍〉4 明列四種寫法,其中一種是 `apply`/`with` 區塊裡不帶接收者的 `setAllowUniversalAccessFromFileURLs(true)`。我把兩條裸呼叫的 pattern 刪掉(`pattern: setAllowUniversalAccessFromFileURLs(true)` 與 `pattern: setAllowFileAccessFromFileURLs(true)`),結果 `python3.14 scripts/test_lumos.py -k t_kotlin_rulepack_security_rules` 仍是 36 條全過,`check.py --sg` 也是 0 個問題。
原因:`_KTSEC_CASES` 的 C01 到 C03、C20 都走賦值、`$X.`、`$X?.` 這幾條。`check.py` 對壞例樣本只要求至少命中兩處,不核對每一行 `// BAD`。`with(webView.settings) { setAllowUniversalAccessFromFileURLs(true) }` 實際會漏報,但沒有測試抓得到。這是會擋的規則,所以值得補一個 `with(...) { setAllow...(true) }` 的案例。
引句:「    - pattern: setAllowUniversalAccessFromFileURLs(true)」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/configs/ast-grep/kotlin-android/check.py`(只算命中數,不逐行對 BAD)

**2.**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/rules-unwired/api.yml`(`kt-insecure-tls-version`)
情境:計劃〈實作紀錄〉特別寫「舊版 TLS 規則照範圍 4 補 `setEnabledProtocols`(草稿沒有)」,但這個分支沒有任何測試守著。我把整個 `setEnabledProtocols(arrayOf(...))` 分支刪掉,`t_kotlin_rulepack_security_rules` 仍是 36 條全過,`check.py --sg` 也是 0 個問題。
原因:`_KTSEC_CASES` 的 C10 到 C14 完全沒有 `setEnabledProtocols`。壞例樣本裡其他 BAD 行讓「至少兩處」的門檻照樣過。這條規則不接閘,所以影響有限。
引句:「    socket.setEnabledProtocols(arrayOf("TLSv1", "TLSv1.2")) // BAD 陣列裡有舊版本」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/scripts/test_lumos.py`(`_KTSEC_CASES` 沒有此案例)

**3.**
severity: minor
blocking: 否
file: `configs/ast-grep/kotlin-android/rules/api.yml`(`kt-webview-file-url-access`)
情境:`if (BuildConfig.DEBUG) { webView.settings.allowFileAccessFromFileURLs = true }` 在 `src/main` 會被這條會擋的規則報成 error。我實跑 `ast-grep scan -c sgconfig.yml` 確認有報,訊息是 `[API-40]…`。
原因:這條規則只靠路徑排除 `src/debug*`,不像姊妹規則 `kt-webview-debugging-enabled` 認 `BuildConfig.DEBUG`。計劃自己的〈用詞〉與〈實務隱患〉沒提這個誤擋情境,預期值表也沒有這一列。除錯旗標包住的寫法會讓推送被擋,只能靠 `lint-waive` 放行。樣本外 80 處誤報 0,所以頻率低,但「樣本外真實寫法」確實有這個缺口。
引句:「# 與左邊以這兩個屬性名結尾、右邊是 true 的賦值(用節點種類比對;中介變數在賦值左邊只吃單一節點,多層接收者會漏)」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint/configs/ast-grep/kotlin-android/rules/api.yml`

**會擋那條在樣本外寫法下的行為:** 我另外寫了 `!!`、分行賦值、`apply { this.x = true }`、`let { it.x = true }`、`?.` 賦值、`= false`、變數賦值這些寫法實跑。
- 前五種該報的有報。
- `= false` 與變數賦值不報。
- 括號 `(true)`、具名參數 `value = true`、`java.lang.Boolean.TRUE` 會漏報。這是計劃已承認的「只認字面 true」,只漏報、不誤擋。

**角色卡:** be-api-compat 與 be-authz 都不適用。這份 diff 沒有端點、欄位或對外 API,只動規則包、型錄與筆記。

**圖譜鏡頭:** 派工詞說鏡頭計算超時、沒附固定席節點,所以我沒逐條答。我只確認:`check.py` 新口徑讀舊型錄不會變(只是多認一個前綴),型錄自檢讀新列、舊列都是 0 個問題。

最大嚴重度 minor,blocking 0 條(共 3 條)。
