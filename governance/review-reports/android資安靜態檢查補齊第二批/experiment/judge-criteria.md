# 判讀準則(所有判讀員共用)

每處命中看前後 20 行(必要時打開 ctx 檔標頭那支原檔看整個檔,原檔都在本機)。判 TP / FP / UNSURE:
- TP:正式版本(非測試、非範例模組)真的有那個風險寫法,而且開發者改得動。
- FP:形狀對上但不是那個風險,理由欄開頭寫「FP型:<型>;」再一句話。常用型:
  - 非資安用途(例:MD5 做快取鍵、檔案檢查碼、去重)
  - 外部協定強制(第三方協定/伺服器規定的寫法,App 改不了:ADB 金鑰簽章、Netease/QQ 等 API 加密、智慧卡 NFC 協定)
  - 可信來源(資料只來自 App 自己寫的私有檔/資源/記憶體內複製,攻擊者碰不到)
  - 已防護(防護寫在別處,例如呼叫端或 helper 已驗)
  - 函式庫原始碼複本(把 OkHttp 等第三方原始碼整份抄進 repo)
  - 測試或範例碼(路徑排除沒擋到的測試、sample/demo 模組、教學練習題)
  - 非秘密(變數名像秘密但值不是:鍵名、檔名、路徑、ID)
  - 停用/黑名單(列出弱套件是為了移除它們)
  - 只檢查不寫檔 / 只產生不解析 等(自己寫明)
- UNSURE:看完還判不出,寫明缺什麼資訊。

各規則的 TP 判準:
- kt-weak-message-digest:MD5/SHA-1 用在資安目的(密碼雜湊、驗證簽章或 token、防竄改完整性、金鑰衍生、憑證比對)才 TP;快取鍵/檢查碼/ID 是 FP 非資安用途;第三方 API 規定的簽名是 FP 外部協定強制。
- kt-rsa-no-oaep:"RSA"(Android 上預設是沒填充的教科書 RSA,JVM 上是 PKCS1,兩者都不是 OAEP)或 NoPadding 用來加密 App 自己的資料就 TP;ADB 認證簽章(手動補 PKCS#1 再做 raw RSA)、NFC 智慧卡、第三方 API 規定 → FP 外部協定強制。
- kt-weak-key-size:正式程式產生 <2048 的 RSA/DSA/DH 或 <128 的對稱金鑰 → TP;測試用假憑證 → FP。
- kt-static-iv:用寫死/全零 IV 加密 App 自己的資料 → TP;重現第三方協定 → FP 外部協定強制;刻意要確定性輸出(例如做雜湊/索引)→ FP 並寫明。
- kt-xxe-documentbuilder:解析的 XML 可能來自外部(網路、使用者匯入檔、其他 App)且沒關 DTD → TP;只解析自己的 assets/建置設定檔/自己寫的檔 → FP 可信來源;只 newDocument() 產生 XML 不 parse → FP 只產生不解析。
- kt-object-input-stream:反序列化的資料攻擊者可能塞(網路、外部儲存、Intent、使用者匯入、剪貼簿、其他 App)→ TP;只讀 App 私有檔/SharedPreferences 自己寫的、內建資源、記憶體內深複製 → FP 可信來源。看不出來源就 UNSURE。
- kt-db-on-external-files:App 自己的資料庫檔建在外部儲存 → TP;打開使用者選來匯入/轉檔的別人的資料庫 → FP(寫「FP型:匯入外部資料庫」)。
- kt-provider-openfile-traversal:Uri 路徑一路進到 File 沒做 canonical 檢查 → TP。
- kt-webview-mixed-content-always:正式 WebView 設成 ALWAYS_ALLOW → TP;sample/demo 模組或教學練習 → FP 測試或範例碼。
- kt-weak-cipher-suite:App 自己啟用弱套件 → TP;函式庫原始碼複本、為了移除而列出 → FP。
- kt-hardcoded-secret-name:真的憑證/API key/密碼寫死 → TP(就算是可公開的前端 key,只要是真的金鑰值也算 TP);值不是秘密 → FP 非秘密;公開的協定常數(例:各家都抄的 Netease EAPI key)→ FP 外部協定強制;明顯範例值 → FP。
- kt-zip-slip:解壓縮項目名稱直接組輸出路徑且沒驗證 → TP;防護在別處 → FP 已防護;名稱只拿來比對/讀取不寫檔 → FP;壓縮檔只來自 App 內建資源 → FP 可信來源。
- kt-loadurl-external:Intent 帶進來的網址沒驗 scheme/host 就 loadUrl → TP(看不到 manifest 是否 exported 就照 TP 判,理由註明「未確認 exported」);有驗證 → FP 已防護。

輸出:TSV,每處一列,欄位用 tab 分隔:ruleId<TAB>檔(ctx 標頭路徑裡 corpus/ 之後那段;語料①的檔用 gap/corpus/ 或 fill/ 之後那段)<TAB>行<TAB>判定<TAB>理由。第一列寫表頭 `ruleId	檔	行	判定	理由`。ctx 檔裡每個「#####」區塊都要有一列,不准跳。
