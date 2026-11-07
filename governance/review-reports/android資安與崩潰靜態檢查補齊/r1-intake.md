preflight-4: ran

# r1 收貨紀錄(android資安與崩潰靜態檢查補齊)

## 首輪前掃(便宜代理,四類)

①未定義的詞、②壞引用、③範圍矛盾與存在類命中直接修真檔、不算 findings。④語意類命中修真檔並留痕如下(修改前 → 後);沒有動到核心裁定的,不升級成正式 finding。

| 編號 | 修改前 | 修改後 | 依據 |
|---|---|---|---|
| P1 | S2「沒標批四 應 報問題」 | S2 改成「通電批次寫了批四時,標錯值才報」;天花板加第 3 條「漏寫批四那一段自檢不報」 | `check.py` 那行只對通電批次含「批四」的列呼叫 `batch4_expected_tags`(前掃代理讀碼) |
| P2 | S4 綁 t_kotlin_rulepack_messages_cite_catalog 驗目錄 | S4 改綁新測試 t_kotlin_rulepack_security_rules_placement | 既有測試只驗訊息格式與等級對目錄,不驗哪條在哪 |
| P3 | 範圍 4:除錯模式「不在條件含 debug 字樣的 if 裡」、TLS 參數含 SSL | 照〈實驗〉定案寫:任何非 SDK 版本比較的 if 都不報、拿掉 SSL、TLS 同套 if 判斷 | 實驗改形狀後的規則(卷證 experiment/draft-rules.yml.txt) |
| P4 | 提示級放 rules-hints/、語意覆核級放 rules-review/ | 兩條都放 rules-unwired/ | 規則包 WHY「rules-unwired/ 也收還沒在真專案量過誤報的新規則」;兩條沒逐筆量 |
| P5 | 「沿用規則包既有的測試路徑清單」 | 點名 rules/state.yml 那份七項加 src/debug* | rules/*.yml 至少三種排除清單寫法 |
| P6 | 「有關的檢查 id 補進那列」 | 點名只有 DataExtractionRules 併進 DATA-13,其餘另開 | 前掃指出沒寫哪個併哪列 |
| P7 | 沒寫實測狀態欄與〈統計〉 | 範圍 2 補上 | 規則包操作第 4 條;型錄〈統計〉節 |

## 收貨

四席(通才、邊界、整合、架構對齊)全數交回後一次寫進卷證;席報告由編排者從子代理逐字稿取最後一則回答原樣存檔(完成通知會把角括號跳脫,不從通知抄)。四份 report-normalize 不用改、quote-check 全數錨定。審查席在 `/tmp/lumos-seat-work/android資安與崩潰靜態檢查補齊/` 留了實驗樣本,repo 工作目錄沒被動過(只有本輪派工單、快照與報告未追蹤)。

編號:通才 G1–G4、邊界 B1–B7、整合 I1–I12、架構對齊 A1–A4,共 27 條;major 9 條(G1 G2 G3 B1 B2 B3 I1 I2 I3),其餘 minor。

## 根因分組

| 組 | 成員 | 根因 |
|---|---|---|
| 甲 規則形狀用一個中介變數配整串屬性 | G1 B1 | `$X.prop = true` 的 `$X` 只吃單一節點,多層接收者整條漏 |
| 乙 除錯開關判法 | G2 B3 B4 A4 I5 的 0227 部分 G4 的 when 部分 | 自創「非 SDK 比較的 if 都算開關」,跟既有 API-19 不同口徑,又不分 then/else、否定 |
| 丙 呼叫鏈與參數靠整串正規式 | B2 B5 B7 | `tlsVersions` 與 `getInstance` 靠文字正規式比對整條鏈 |
| 丁 寫死金鑰參數沒限制 | B6 G4 的金鑰部分 | `byteArrayOf($$$)` 不限參數;第二版又把限制掛在錯的節點(實測整條規則零命中,本輪編排者自己抓到) |
| 戊 誤報量測樣本內 | I1 | 形狀照同一批語料調,分母小,規則包要求量過才升 |
| 己 型錄分類與欄位 | I2 I4 I6 I7 I9 A2 | 新列的情境怎麼認、併入列、重複列、實測狀態欄與統計口徑沒定 |
| 庚 資安包整包 | I3 I12 I10 | 包裡 24 條檢查只登記 9 條;建置版本與基準線重產沒寫;預設開不開沒核 |
| 辛 條款綁通用測試 | G3 I8 | 樣本測試只數壞例 ≥2、好例 0,守不住逐例 |
| 壬 檔案位置 | A1 I11 A3 | 新開 security.yml 跟按型錄主題分檔不一;src/debug 排除只有新規則有 |
| 癸 MASTG 引用 | I5 | 0252/0250/0337 的判準跟規則形狀對不上 |

## 先查世界

- PRIOR-ART:甲丙丁:MobSF mobsfscan 的 Kotlin 規則(https://github.com/MobSF/mobsfscan ,`mobsfscan/rules/semgrep/kotlin/webview.yaml`、`network.yaml`)用 semgrep 的 `$S.allowFileAccessFromFileURLs = true`、`SSLContext.getInstance("TLSv1")`、`$S.setEnabledProtocols(arrayOf(..., "TLSv1", ...))`,semgrep 的中介變數吃任意運算式;ast-grep 的中介變數在賦值左邊只吃單一節點(邊界席 `--debug-query` 實測),所以改用節點種類比對(賦值的左邊整段以屬性名結尾、右邊是 true;`tlsVersions` 看呼叫的參數節點;金鑰看第一個參數節點)。採用,第二版逐例樣本實跑(卷證 experiment/v2-*.kt.txt)。
- PRIOR-ART:乙:mobsfscan 對 `setWebContentsDebuggingEnabled(true)` 完全不看外層判斷,一律報;Android 官方建議的寫法是把 `BuildConfig.DEBUG` 或 `ApplicationInfo.FLAG_DEBUGGABLE` 直接當參數傳(不寫字面 true),MASTG-TEST-0227 也寫要看有沒有檢查 FLAG_DEBUGGABLE。採用:對齊規則包既有 API-19(只認含 `BuildConfig.DEBUG` 的判斷),再收窄成只認條件恰好是 `BuildConfig.DEBUG` 的 if 成立那一支與 when 那一條;否定、else、`||` 照報。排除:自創的「任何非 SDK 比較的 if 都算開關」(架構對齊席點名第二種判法、通才席實測漏掉正式版才開的形狀)。
- PRIOR-ART:戊:規則包操作第 1 條與 REVISIT 要求新規則先放不接閘、拿新的真專案量過才升;Google Tricorder 一成門檻。這輪另撈 250 支沒拿來調形狀的 repo 檔(排除前兩批出現過的 repo)當樣本外語料:檔案網址存取 80 處全真、除錯模式 42 處誤報 16(38%,別名除錯旗標 8、直接判 FLAG_DEBUGGABLE 6、BuildType 1、debug 變體目錄 1)、寫死金鑰只撈到 3 處(全真,分母太小)。採用:只有檔案網址存取放 `rules/`,其他三條放 `rules-unwired/`,升級條件寫死。
- PRIOR-ART:庚:資安包官方 README 列 24 條檢查;建置檔 `build.gradle`(最後改於 2024-08-07,1.0.4 於 2025-11-13 發版前未再改)寫 `lintVersion = '31.5.1'`,照範本既有 Slack 外掛的同一條規則(建置用 lint 版本不高於專案 lint = AGP+23)換算 AGP 8.5.1 以上。採用。
- PRIOR-ART:癸:MASTG-TEST-0252 判準要 JavaScript、檔案存取、FileURL 三者同時成立才失敗;規則只抓 FileURL 那一半,來源欄改寫成「0252 的必要條件之一」;0250 是 content 存取,不再引;0337 講 Intent extras 與 Bundle,不是 `ObjectInputStream`,這條規則與型錄列拿掉。

## 重現

| id | 編排者重現 | 結果 |
|---|---|---|
| G1 | 草稿規則掃 `webView.settings.allowFileAccessFromFileURLs = true` | HIT:不報 |
| B1 | 同 G1,另 `binding.webview.settings.…`、`this.settings.…` | HIT:不報 |
| G2 | `if (!BuildConfig.DEBUG) { WebView.setWebContentsDebuggingEnabled(true) }` | HIT:不報 |
| B2 | 分行 `.tlsVersions(TlsVersion.TLS_1_0)` | HIT:不報 |
| B3 | 邊界席樣本 s2/B.kt 第 15、21、24–27 行 | HIT:草稿全報;第二版只認恰好 BuildConfig.DEBUG,early return 與 let 仍報(樣本外語料 0 筆 early return) |
| I1 | 樣本外語料除錯模式誤報 | HIT:42 處誤報 16 |
| I2 | `check.py` 語意類要表態對程式、盲判席、決策表收列 | HIT |
| I3 | 資安包 README 檢查 id 數 | HIT:24 條 |
| G3 | `t_kotlin_rulepack_samples` 判準 | HIT:只數壞例 ≥2、好例 0 |
| 其餘 minor | 讀碼對照 | HIT |
