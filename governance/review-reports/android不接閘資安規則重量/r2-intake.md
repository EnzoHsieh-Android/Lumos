# r2 收貨紀錄(android不接閘資安規則重量)

## 收貨

- 四席(通才二、出處二、實驗可信二、架構對齊二)全部交回後一次從逐字稿存檔;四份都已是正規化格式。quote-check:實驗可信二、架構對齊二全數錨定;出處二把網頁原文寫成引句格式(引句只收凍結快照原文)、通才二有一句引型錄原文,這幾句錨不到,下表逐條機械重現後採信。收貨時 git status 沒有席位造成的 repo 改動;通才二說可能誤寫的 /tmp/lumos-seat-work/x.kt 不存在。
- 臨時目錄 /tmp/lumos-seat-work/android不接閘資安規則重量/ 收貨後刪。

## 編號與處置

編號:通才二 t1–t4、出處二 s1–s5、實驗可信二 x1–x6、架構對齊二 a1–a6(照報告順序)。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| t1 | 型錄情境欄殘留:TEST-31 還寫用文字找、TEST-33 還寫沒有 @Config、ARCH-3 還寫 currentDestination | HIT:讀型錄三列第 8 欄;testing.yml 那條規則只比對 @LooperMode(LEGACY) | 折:三列情境欄改寫 |
| t2 | 保留規則的通電批次寫「誤報超過一成或量不夠」,但它們沒量過 | HIT:FLOW-14 等列沒有實測數字 | 折:改成「還沒在真專案量過誤報」 |
| t3 | ARCH-3 訊息與後果寫「重複導航」,原文只支持「轉場開始後還處理點擊」 | HIT:dropUnlessResumed KDoc 原文 | 折:訊息與後果照原文改 |
| t4 | 回退條數對不上;API-14 收窄的依據是推論;d1 的 DATA-12 沒解釋 | HIT:實際改了 7 條訊息;議題 #1493 脈絡是 GlobalScope | 折:回退逐項列;收窄理由改寫成「IntelliJ 只講同 scope,別的 scope 沒原文」;d2 寫明 DATA-12 那半不受影響 |
| s1 | TEST-16 出處只點名 Clock.System,規則抓的 JDK、Android API 原文沒提 | HIT:testing.yml 規則樣式 9 個、Kotlin Clock 頁只講 Clock.System | 折:另派代理專查;Oracle Clock javadoc 與 Sonar S8692 涵蓋 java.time now()、Date()、currentTimeMillis,nanoTime 與 SystemClock 找不到;規則收窄、型錄改寫 |
| s2 | TEST-31 索引那半:codelab 那句講的是除錯編號、不是取索引 | HIT:codelab 原句上下文;專查也找不到 | 折:規則移除,TEST-31 維持出處不全 |
| s3 | STATE-9 後果要靠推論接起來、5 秒寫得像唯一解 | HIT:KDoc 與 codelab 原文 | 折:後果寫成兩句原文並列,標準寫法註明官方範例用 5 秒,訊息同步 |
| s4 | ARCH-3 把重複點擊接到例外是推論 | HIT:NavController 參考頁只說找不到目的地 | 折:同 t3 |
| s5 | FLOW-14 後果比原文寬(會暫停的 collect 本來就檢查取消) | HIT:flow.md 原文講的是 busy loop | 折:壞例註明不暫停、後果與訊息加「不暫停時」 |
| x1 | 第二份語料的抽樣與去重重現不出來 | HIT:卷證沒有 v2 命中檔與程式 | 折:存 hits-loadurl-v2.json 與 sample-loadurl-v2.py.txt,重跑抽樣一致 |
| x2 | 排除教材漏了兩處掃描器固件 | HIT:序號 13、39 的路徑 | 折:〈實驗〉寫明,排掉後 78.9%;關鍵字補 fixtures、masaudit |
| x3 | 敏感度 3/37 算不出來 | HIT:席位照卷證算出 4/37 | 折:改用腳本重算(C 算法 3/35、8.6%),並寫明席位另一種判法的 4/37 |
| x4 | 敏感度的排除清單沒存、口徑只套一條 | HIT:卷證沒有清單 | 折:存 sensitivity.py.txt 與結果,三種算法套五條 |
| x5 | 「沒對外開放=誤報」沒處理轉送路徑 | MISS:席位自己也沒逐一追溯,只是盲區 | 折:〈天花板〉寫明,加 REVISIT 抽 10 處查轉送 |
| x6 | 回頭條件:命中 20 標準比資料庫那條寬、讀 manifest 那條有永遠成立的出口、v2 沒給區間、缺方向論證 | HIT:讀 REVISIT 原文 | 折:改成獨立 repo 至少 20、改成評估並寫結論、補區間與方向論證 |
| a1 | 樣本「不報:」前綴跟鄰居不同 | HIT:全樣本 138 處「容易誤報:」 | 折:改成「容易誤報:」 |
| a2 | API-36、UI-103 通電批次是新句子 | HIT:型錄只有三種寫法 | 折:改成既有的「還沒有規則」 |
| a3 | 逐列查證計劃那條重查 API-14、TEST-31 的回頭條件沒結案 | HIT:那份計劃第 104 行 | 折:加 [closed:] 寫實際結果 |
| a4 | 規則包節點還有過期句子 | HIT:第 51、76 行 | 折:兩行補更正 |
| a5 | 「停放或移除」的取捨沒進節點 WHY | HIT:第 52 行 WHY 只講停放 | 折:補一條 WHY |
| a6 | 建議拆成兩篇計劃 | HIT:標題只講重量 | 放行:第二批計劃有新規則與重量同篇的先例,兩件事同一批規則同一輪做;拆開要多開一個迴圈,可找性靠逐列查證計劃與規則包節點連回本篇補 |

--refuted-set none。--regression-set:s1、s2 是上一輪折入時判得太寬造成的(第一次再查把「講到相關原則」當成支持);其餘是原有漏查或新增段落的措辭。

## 先查世界

- PRIOR-ART:s1、s2(出處要講到判定的寫法)——另派代理專查 Oracle javadoc、Kotlin 官方、Sonar、detekt、PMD、Error Prone 規則庫;Sonar S8692 的規則頁 404,改讀 SonarSource/sonar-java 官方原始碼的規則說明與檢查程式。
- PRIOR-ART:x2、x4(教材與基準語料排除)——照第二批「排除資安教材與規則樣本 repo」做法,關鍵字補 fixtures、masaudit、swe-gen、harbor-datagen。
- PRIOR-ART:a1、a2(寫法跟鄰居)——照型錄與樣本既有寫法,沒有要另查的。
