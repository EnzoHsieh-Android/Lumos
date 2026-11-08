severity: minor

甲包 16 條規則裡沒有 major 或 blocker。會擋的 `kt-webview-mixed-content-always` 沒找到會讓推送閘誤報的輸入,混合內容那條在 `rules/api.yml` 的位置也跟計劃一致。我只找到一個測試覆蓋不足的 minor。

我把規則複製到 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查甲-sonnet/`(含 `--shared` clone 的 `repo/`)用 ast-grep 0.51.1 實跑。基準是 `t_kotlin_rulepack_security_rules` 135 項全過、`t_kotlin_rulepack_samples` 27 項全過。

**1. 混合內容那條:`setMixedContentMode(…ALWAYS_ALLOW)` 這一支被拿掉,測試照綠**
severity: minor
blocking: 否

- file: `configs/ast-grep/kotlin-android/rules/api.yml:259-266`(`always-allow` 的 any 清單)
- 引句:「- matches: always-const」
- 失敗場景:
  - 我把 setter 的 `any` 清單裡 `matches: always-const` 那行刪掉,只留 `zero-lit`,結果 `t_kotlin_rulepack_security_rules` 仍是 135 passed、0 failed。`t_kotlin_rulepack_samples` 這次沒對這個改壞版跑。
  - 改壞後 `webView.settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)` 不再被報,而這是計劃範圍 4 明寫會擋的形式。
  - 原因是預期值表 S1 的 setter 只有 `setMixedContentMode(0)` 與 `resolve(0, 1)` 兩列(C53、C54),setter 加常數沒有案例。
  - 壞例樣本雖有這一行,但那份樣本只要求同一規則至少命中 2 處,賦值那幾行已經湊滿,所以抓不到。
  - 其餘寫法拿掉也都照綠:
    - 賦值右邊不帶套件名的裸常數(`apply { mixedContentMode = MIXED_CONTENT_ALWAYS_ALLOW }`)
    - `getSettings()` 接收者
    - `?.`、`!!` 容許
    - `$X?.setMixedContentMode($M)` 與不帶接收者的 setter
  - 這幾項我都只跑了 `t_kotlin_rulepack_security_rules` 一份測試。
- 建議:在 `_KTSEC_CASES` 補一列 `setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW)` 預期報一次;`getSettings()!!` 與裸常數各補一列。
- 佐證:file: `scripts/test_lumos.py:126848-126856`(混合內容案例 C48~C55)
- 因為被保護的不是預期值表上的驗收列,只是覆蓋不夠完整,所以評 minor。

**審查鏡頭逐項結論(沒有 finding)**
- **混合內容那條的誤報與漏報**:
  - 報(正確):`settings.mixedContentMode = 0`、`webView.settings?.mixedContentMode = 0`、`wv?.settings!!.mixedContentMode = 0`、分行的 `.settings\n.mixedContentMode = 0`、具名參數 `setMixedContentMode(mode = 0)`、`requireNotNull(wv).settings.setMixedContentMode(0)`。
  - 不報(正確):`resolve(0,1)`、`cfg.mixedContentMode = 0`、`cfg.settingsX.…`、`if (BuildConfig.DEBUG)` 加或不加大括號、`when` 的除錯分支。
  - 報(正確):`if (DEBUG) {} else {…}` 的 else 那支。
  - 計劃寫明的漏報:`apply`、`with`、先存變數再給(`val s = webView.settings; s.mixedContentMode = 0`)、`0x0`、`if`/elvis 包住的值、`00` 都漏報。
  - 預期值表 8 列都對得上。
- **接收者放寬成 `\w*[sS]ettings`**:
  - `cfg.settings.mixedContentMode = 0`、`cfg.proxySettings.mixedContentMode = 0` 會報,這符合計劃寫的「以 settings 或 Settings 結尾」,不算違規。
  - 唯一能誤報的是非 WebView 物件既叫 `*Settings` 又有 `mixedContentMode` 屬性,實務上很少見。
  - `settings.mixedContentMode += 0` 也會報(複合賦值也是 assignment 節點),寫法罕見,不提 finding。
  - 放寬後的版本沒重量樣本外語料,實驗的 273 命中、誤報 2 是用只認 `settings` 的版本量的。
- **除錯分支與路徑排除**:
  - 16 條都有 `in-debug-only-branch`,`ignores` 全是規則包既有八項那一組。
  - 混合內容那條拿掉除錯排除後,`t_kotlin_rulepack_samples` 會紅(好例誤報 1 處),所以由樣本測試把關。
- **指令執行那條**:跟計劃寫的收窄一致。
  - 報:`exec` 單一參數的串接、`String.format`、字串樣板,以及 `-c` 後接非字面值(`arrayOf`、`listOf`、`ProcessBuilder`)。
  - 不報:`exec("ls")`、`exec(arrayOf("ls","-l"))`、`"ls " + "-l"`、`-c` 後接字面值、`exec` 多參數的樣板。
  - `ProcessBuilder().command("sh","-c",cmd)` 漏報,計劃形狀沒要求涵蓋。
- **不接閘那 15 條**:預期值表對得上,沒有違反計劃形狀,其餘發現都不到值得標的程度。
  - `kt-loadurl-external`:`"…?t=$v"` 字串樣板漏報,但串接寫法會報;`u.startsWith("https://…")` 算誤報。
  - `kt-weak-cipher-suite` 等其餘條目沒查到違反計劃形狀的地方。
  - 好例樣本沒有被會擋的規則誤命中。
  - 新的 `kt-webview-file-access` 會命中第一批好例 `samples/good/kt-webview-file-url-access/…:9` 那行 `allowFileAccess = true // GOOD`。
- **圖譜鏡頭**:派工詞沒附固定席節點,這一項略過。
- **暫存**:臨時目錄 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查甲-sonnet/` 依指示留著。測試留下的 `gctl-run-xb5gjcuz` 已用字面路徑刪掉。

總結:最高等級 minor,共 1 條,blocking 0 條。
