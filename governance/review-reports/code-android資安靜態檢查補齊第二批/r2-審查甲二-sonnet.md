severity: major

審查範圍:甲包 16 條規則加樣本(`r2-snapshot-甲.patch`),以及 C72~C86 修補差異(`r2-repair.patch`)。逐項實跑 ast-grep 0.51.1,另在 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查甲二-sonnet/` 做了 11 次單點改壞。臨時目錄留著沒刪。

## Findings

### 1. 會擋的混合內容規則:「賦值 0」分支的左邊名稱條件被拿掉時,測試和樣本自檢都照綠

severity: major
blocking: 是

file: `configs/ast-grep/kotlin-android/rules/api.yml:319`

失敗場景:規則在「字面值 0」分支裡,用兩條條件限定它只管混合內容。一條是接收者鏈要有 settings 字樣(第 316 行),另一條是左邊要以 `.mixedContentMode` 結尾(第 319 行)。第 319 行這條沒有任何案例保護。把它整條刪掉,`_KTSEC_CASES` 全部 C01~C86 仍然綠。我另外用 `check.py --sg` 跑樣本自檢,也是綠的,只剩環境缺 `scripts/lumos` 的兩條提示。

刪掉之後,下面這兩行會被這條「會擋」的規則報出來,而規則原本一次都不報:
- `webView.settings.textZoom = 0`
- `webView.settings.cacheMode = 0`

這兩行都是正常的 WebView 設定,但會直接擋住推送。被保護的是推送閘的誤報守衛。計劃預期值表只列了 `cfg.mixedContentMode = 0` 不報,沒列 `settings.<別的屬性> = 0` 不報。修補的 docstring 逐條列了「改壞→哪個案例紅」,獨缺這一條。

重現:
1. 複製 `rules/api.yml`,在 `kt-webview-mixed-content-always` 區塊刪掉下面這三行。
```
- has:
    kind: directly_assignable_expression
    regex: '\.\s*mixedContentMode$'
```
2. 用我的 harness 跑 C01~C86,輸出 `red count 0`。
3. 對含 `webView.settings.textZoom = 0` 與 `webView.settings.cacheMode = 0` 的 `.kt` 跑 `scan --filter kt-webview-mixed-content-always`,命中 2 筆。未改版本命中 0 筆。

建議補一個案例,例如 `webView.settings.textZoom = 0` 預期 0 次。

引句:「regex: '\.\s*mixedContentMode$'」

佐證:file: `configs/ast-grep/kotlin-android/rules/api.yml:316-322`

### 2. 混合內容 setter 的 `?.` 與不帶接收者兩種形狀完全沒有案例

severity: minor
blocking: 否

file: `configs/ast-grep/kotlin-android/rules/api.yml:296-297`

失敗場景:刪掉 `$X?.setMixedContentMode($M)` 或 `setMixedContentMode($M)` 這兩個 pattern,C01~C86 都照綠。

影響:
- `webView.settings?.setMixedContentMode(0)` 會漏報。
- `webView.settings.apply { setMixedContentMode(0) }` 會漏報,這是 Kotlin 常見寫法。

我實測目前規則會報這兩行,所以只是覆蓋缺口,不是現行錯誤。賦值那段的 `(\?|!!)?`,實測只有 `!!` 被 C73 保護,`?.` 單獨被拿掉也綠。

引句:「- pattern: $X?.setMixedContentMode($M)」

## 逐項查過,沒有問題

**混合內容規則的等價寫法(會擋那條)**
- 具名參數:`setMixedContentMode(mode = 0)` 報,正確。
- `?.` 與分行呼叫鏈:`webView.settings?.setMixedContentMode(0)`、`webView.settings\n.setMixedContentMode(...)` 都報。
- 完整套件名常數:`android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW` 報。
- `with(settings){ mixedContentMode = CONST }` 報。
- 內層呼叫與條件式:`setMixedContentMode(if (x) 0 else 1)` 不報。`resolve(0,1)` 不報,計劃明列。
- 分行賦值 `=\n 0` 報。
- 除錯分支:`if (!BuildConfig.DEBUG)` 報,`DEBUG` 的 if-else 只報 else 一次,正確。
- 計劃已記載的漏報:`= (0)`、`apply { mixedContentMode = 0 }`,實測如計劃所述,都不報。
- 計劃不禁止的寬鬆處:`userSettings.mixedContentMode = 0` 與 `prefs.settings.mixedContentMode = 0` 會報,屬計劃「名字以 settings 結尾」的取捨。`p.setMixedContentMode(0)` 沒有接收者條件也會報,計劃的 setter 本來就不限接收者。
- 引句:「webView.settings.setMixedContentMode(resolve(0, 1)) // GOOD 0 是內層呼叫的參數」

**指令執行(ARCH-90)對上 Semgrep 收窄形狀**
- 實測 15 條都符合計劃:串接、樣板插值、`String.format` 報。
- `arrayOf("sh","-c",cmd)`、`ProcessBuilder("sh","-c",cmd)`、`listOf` 包裝、`.waitFor()` 後綴都報。
- `"ls" + " -l"`、`arrayOf("sh","-c","ls")` 不報。
- 多參數的 `exec(cmd, null, dir)` 不報,對上計劃的「單一字串參數」。
- 引句:「Runtime.getRuntime().exec(arrayOf("sh", "-c", cmd)) // BAD exec 的陣列參數」

**其他 14 條不接閘規則**
- 把 loadUrl 等規則逐項實跑 15 個輸入,行為都合註解宣稱的形狀。
- 已知漏報(`"…$u"` 樣板、二次轉手變數)只屬 minor,而且這些規則不接閘。
- 引句:「val target = intent.dataString ?: return」

**好例與壞例**
- 16 組 good 樣本對 4 份 sgconfig 實掃,沒有任何一組命中自己那條規則,也沒有命中混合內容那條會擋的規則。
- 唯一的交叉命中是第一批好例 `kt-webview-file-url-access` 第 10 行命中新規則 `kt-webview-file-access`。那是舊規則刻意留著 `allowFileAccess = true` 的好例,屬預期。
- 壞例的隱患代表性都成立。
- 引句:「val c = Cipher.getInstance("RSA/ECB/NoPadding") // BAD 無填充」

**修補差異 C72~C86**
- 15 個案例對照規則實跑,預期次數全部吻合,基線 `red count 0`。
- 抽驗下列改壞,測試都有紅:setter 改回 `stopBy: end`(C53 紅)、常數前綴錨定(C48、C72、C74 紅)、小寫 `settings`(C50 紅)、拿掉 `getSettings()` 與拿掉 `(\?|!!)?`(C73 紅)。
- 其餘改壞見上面第 1、2 條。
- 引句:「("src/main/kotlin/C73.kt", "webView.getSettings()!!.mixedContentMode = 0", "kt-webview-mixed-content-always", 1),」

**圖譜鏡頭**
- 派工沒附固定席節點。就甲包和修補差異本身,看不出它破壞計劃〈範圍〉4 或〈預期值表〉的哪一條合約,只有上面第 1 條是測試守不住的缺口。

## 總結

最高等級 major,blocking 1 條(第 1 條),minor 1 條(第 2 條)。
