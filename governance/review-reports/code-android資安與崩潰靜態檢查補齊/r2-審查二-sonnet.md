severity: major

審查範圍:修補差異 `906204244` 對 `c7bf5c638`,逐 hunk 讀完,並在兩版各自的 clone 上實跑 ast-grep 0.51.1 與測試。臨時目錄已刪。

## Finding 1
severity: major
blocking: 是

會擋那條 `kt-webview-file-url-access` 新加的 `not.inside` 區塊裡,「else 分支要排除」和「when 分支要排除」兩段都沒有測試守。拿掉任一段,`-k kotlin_rulepack_security` 仍是 `40 passed, 0 failed`。

引句:「                  regex: ^else$」

引句:「寫在條件恰好是 BuildConfig.DEBUG 的 if 成立那一支或 when 分支裡不報」

最小重現(在 `after` 的臨時 clone 上做變異):
- 刪掉 `not: follows: regex: ^else$` 這一段:測試 40 通過。`if (BuildConfig.DEBUG) {…} else { w.settings.allowFileAccessFromFileURLs = true }` 的命中數從 1 變 0。結果是正式版分支的檔案網址跨來源存取被靜默放行。
- 刪掉整個 `inside: kind: when_entry` 分支:測試 40 通過。
- 把整個 `not` 刪掉:C23 才紅。所以新測試只釘得住「有沒有這個 `not`」,釘不住裡面兩個子條件。

這是會擋規則(`rules/api.yml`,error 級)的安全漏報守衛,計劃〈預期值表〉只補了 C23(DEBUG 成立)與 C24(`!DEBUG`),沒有 else 列與 when 列。我實跑確認現行行為是對的:
- `if (DEBUG) {} else { A }` 會報。
- `when { DEBUG -> A }` 不報。
- `when { else -> A }` 會報。

缺的只是釘住這些行為的案例。被保護的是會擋規則的守衛,測試抓不住改壞,依嚴重度定義判 major,故 blocking 為是。

歸因:未判定。這是修補新增程式自帶的覆蓋缺口,不是行為回歸。修前沒有這段 `not`,所以無從比較。

## Finding 2
severity: minor
blocking: 否

不帶接收者的 `setAllowFileAccessFromFileURLs(true)` 沒有案例守。C21 只用 Universal 那個名字。刪掉 `- pattern: setAllowFileAccessFromFileURLs(true)` 後測試仍是 40 通過。刪掉 Universal 那條則 C21 紅。

引句:「("src/main/kotlin/C21.kt", "with(webView.settings) { setAllowUniversalAccessFromFileURLs(true) }」

歸因:有證據的原有漏查。規則本來就有這條 pattern,修補補的案例只覆蓋一半。

## Finding 3
severity: minor
blocking: 否

`kt-insecure-tls-version` 的 `setEnabledProtocols` 分支漏掉等價的 Kotlin 寫法。這條在 `rules-unwired/`,不接閘。plan 明寫的 `webview` 規則認 `?.`,這條沒寫,所以只是覆蓋不一致。

引句:「+            - pattern: $S.setEnabledProtocols(arrayOf($$$))」

各案例實跑結果(樣本內容不含 "TLSv1.2" 單獨存在的情形):
- `s?.setEnabledProtocols(arrayOf("SSLv3"))`:不報。
- `s.setEnabledProtocols(arrayOf<String>("SSLv3"))`:不報。
- `s.enabledProtocols = arrayOf("SSLv3")`(Kotlin 合成屬性):不報。
- `s.apply { setEnabledProtocols(arrayOf("SSLv3")) }`:報。
- `s.setEnabledProtocols(arrayOf("TLSv1.2", x.getFoo("TLSv1")))`:報(誤報,很牽強)。

歸因:有證據的原有漏查。這條規則在修前就有,修補只加了 C22 案例。

另外,docstring 寫「拿掉 setEnabledProtocols → C22 紅」,這個我沒有做變異驗證,未驗。

## 三問

**① 修補宣稱的行為證據**
- **load_rules 讀 ignores,測試改用它:** 實跑 `S4 … 路徑排除恰好是八項` 四條都綠。
- **訊息上限讀 MSG_MAX:** `message_problems` 本來就用 `MSG_MAX`,測試改成同一個常數,對得上。
- **會擋規則認 BuildConfig.DEBUG 成立那一支:** C23 不報、C24 報,實跑正確。拿掉整個 `not` 後 C23 紅,所以這條有效。但 else 與 when 兩段沒守,見 finding 1。
- **補 with 區塊案例:** C21 有效,拿掉不帶接收者的 Universal 呼叫會紅。File 版沒守,見 finding 2。
- **補 setEnabledProtocols 案例:** C22 綠,規則本身修前就有。

**② 修補處的鄰近路徑**
- **load_rules 其他呼叫者:** 共 8 處,都只讀原有鍵,多一個 `ignores` 鍵沒有影響。型錄自檢 `check.py --sg …` 實跑「規則 211 條,問題 0 個」。
- **ignores 的寫法:**
  - 雙引號可讀。
  - 沒寫 `ignores` 的規則得到空清單。
  - 多行 `ignores:` 目前有 4 處 `ignores:` 不是單行(`rules/data.yml`、`perf.yml`、`state.yml` 等),會靜默得到 `[]`。
  - 單行但行尾帶註解也會得到 `[]`。
  - 目前只有那四條新規則被測試拿去比對,且比對不符會紅(大聲失敗),所以暫無問題。
- **除錯判斷的相鄰寫法**,實跑結果:
  - `else` 分支:報。
  - `!DEBUG`:報。
  - `DEBUG || x`:報。
  - `DEBUG && x`:報,這是保守誤報,與 API-19 風格一致,不標 finding。
  - `else if (DEBUG)` 分支:不報。
  - 巢狀 lambda 在 DEBUG 分支裡:不報。
  - `when` 的 DEBUG 分支:不報;`when` 的 else 分支:報。
  - 完整套件名 `com.x.BuildConfig.DEBUG`:報,保守誤報。

**③ 同一案例修前與修後**
同一組輸入,第一個數字是修前,第二個是修後:

| 輸入 | 修前 | 修後 |
|---|---|---|
| `if (DEBUG) { allowFileAccessFromFileURLs = true }` | 1 | 0 |
| 帶 `apply` 的賦值,在 DEBUG 分支裡 | 1 | 0 |
| `if (DEBUG) {A} else {A}` | 2 | 1 |
| `if (DEBUG) {} else {A}` | 1 | 1 |
| `if (!DEBUG) {A}` | 1 | 1 |
| `with(...) { setAllowUniversalAccessFromFileURLs(true) }` | 1 | 1 |

沒有發現修前正確、修後出錯的案例,所以沒有行為回歸。

**未驗範圍:** 型錄〈統計〉數字與主表對帳。修補差異沒動型錄,我只跑了型錄自檢通過,沒逐數重算。先前提交的 41 列併 3 列我沒逐列讀。也沒查 `C22` 的 docstring 翻紅宣稱。

總結:檔級最高等級為 major(Finding 1,blocking 為是);Finding 2、3 為 minor。
