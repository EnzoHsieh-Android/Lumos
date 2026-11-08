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

  - 「測試或範例碼」只看兩樣客觀特徵:①檔案路徑有 test、sample、demo、example、tutorial 這類目錄或模組名;②repo 名(owner/名字的「名字」那段)含 sample、demo、example、tutorial、practice、lab、template、starter、course、codelab、exercise、homework、assignment 其中一個字(不分大小寫,可以是字的一部分)。兩樣都沒有就照正式碼判,不因套件名是 com.example、畫面簡單或 README 說是練習而改判。

各規則的 TP 判準:
- kt-insecure-tls-version:App 自己的連線用 TLSv1、TLSv1.1、SSL、SSLv3 或 OkHttp 的 COMPATIBLE_TLS(允許 TLS 1.0、1.1)→ TP;只在 Android 5.0(API 21)以前的舊系統才走這條路(有版本判斷包住)→ FP(寫「FP型:舊系統相容」);連到第三方規定要舊版 TLS 的設備或伺服器、App 改不了 → FP 外部協定強制;把舊版列出來是為了停用 → FP 停用/黑名單。
- kt-loadurl-external:Intent 帶進來的網址沒驗 scheme/host 就 loadUrl → TP(看不到 manifest 是否 exported 就照 TP 判,理由註明「未確認 exported」);有驗證 → FP 已防護。
- kt-provider-openfile-traversal:Uri 路徑一路進到 File 沒做 canonical 檢查 → TP;有 canonicalPath 比對或白名單 → FP 已防護。
- kt-db-on-external-files:App 自己的資料庫檔建在外部儲存 → TP;打開使用者選來匯入/轉檔的別人的資料庫 → FP(寫「FP型:匯入外部資料庫」)。
- kt-command-exec-nonliteral:指令字串的非字面部分可能來自外部(Intent、網路、使用者輸入、外部檔名)而且沒有白名單或跳脫 → TP;非字面部分全是 App 自己的常數、自己的套件名或系統回傳的固定值 → FP 可信來源;App 本身就是讓使用者自己下指令的終端機或 root 工具 → FP(寫「FP型:執行指令是功能本身」)。

輸出:TSV,每處一列,欄位用 tab 分隔:ruleId<TAB>檔(ctx 區塊標頭的路徑)<TAB>行<TAB>判定<TAB>理由。第一列寫表頭 `ruleId	檔	行	判定	理由`。ctx 檔裡每個「#####」區塊都要有一列,不准跳。最後一列寫總計(TP、FP、UNSURE 各幾,FP 各型各幾)。
