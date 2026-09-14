# code-dart-sarif r2 收貨紀錄(2026-09-14)

兩席收齊才動樹。`report-normalize` 兩份都已是正規格式;修正差異席 `quote-check` 全錨定,資安席 clean。

| id | 席 / 原編號 | 等級 | 內容 | 編排者重現 | 處置 |
|---|---|---|---|---|---|
| k1 | 修正差異 F1 | major | 丟掉整個 COMPILE_TIME_ERROR 類,連參數個數錯、型別不符、未定義名字這些真 bug 也丟,閘判乾淨 | HIT:真 dart 3.13.3,三種真 bug 都是 COMPILE_TIME_ERROR | 折(spec):向 Enzo 攤三個選項(維持不收講明/補整份原始碼/逐檔判斷),附量測「帶 pubspec 與 .dart_tool 連結只解得開外部套件、專案自己的引用照樣找不到」;**Enzo 裁維持不收、文件講明**。程式註解、兩篇筆記、README.en 都寫明「這道閘對 Dart 抓不到編譯錯誤、要靠建置與 CI」,附事件回頭條件與 REVISIT |
| k2 | 修正差異 F2 | major | 冒煙換檔只認 git 追蹤檔,還沒 git add 的新檔又變回誤報 | HIT(席附重現,讀碼確認 ls-files 預設只列索引) | 折:ls-files 加 --cached --others --exclude-standard;新增未追蹤檔測試,拆掉修正會紅 |

資安席:clean。refuted:none。accepted:none。
