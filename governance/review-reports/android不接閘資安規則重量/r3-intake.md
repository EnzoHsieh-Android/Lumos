# r3 收貨紀錄(android不接閘資安規則重量)

## 收貨

- 四席(通才三、出處三、實驗可信三、架構對齊三)全部交回後,一次從逐字稿存檔。四份都已是正規化格式,quote-check 全數錨定。
- 收貨時 git status 沒有席位造成的 repo 改動。
- 席位臨時目錄 /tmp/lumos-seat-work/android不接閘資安規則重量/ 收貨後刪除。

## 編號與處置

編號照報告順序:通才三 g1–g6、出處三 p1–p6、實驗可信三 e1–e5、架構對齊三 c1–c2。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| g1 | 系統時鐘規則新加的 `Clock.System.now()` 樣式比對不到帶 `kotlin.time.` 前綴的寫法;壞例那行標 BAD 卻沒報,樣本自測只驗目錄至少報一處所以綠 | HIT:用 sgconfig-unwired.yml 掃壞例,只報第 5、8、12 行,第 10 行沒報 | 折:規則補 `kotlin.time.Clock.System.now()`、`kotlinx.datetime.Clock.System.now()` 樣式;逐例表補 C124(帶前綴要報),拿掉前綴樣式時 C124 翻紅 |
| g2 | 〈實務隱患〉寫少 3 條、2 條收窄,跟其他段對不上 | HIT:讀計劃原文 | 折:照最終結果改成少 5 條、2 條收窄 |
| g3 | 導航規則拿掉 View 樣式後,「外層有 currentDestination 就不報」的排除沒有出處,也沒有測試守 | HIT:architecture.yml 有那條 not;唯一測它的好例寫在 View 的 setOnClickListener 裡 | 折:拿掉那條排除,型錄與訊息不提它 |
| g4 | 逐列查證計劃 d1 的取代者指向本計劃已失效的 d1;DATA-12 那半沒有有效決策可查 | HIT:讀兩篇的 decisions 欄 | 折:本計劃記 d3(最終結果),d2 標成被 d3 取代;逐列查證計劃 d1 的取代者改指 d3,另記 d2 寫明 DATA-12 那半照舊有效 |
| g5 | API-14 說「IntelliJ 講的是同一個 scope」是推論;detekt SequentialAsyncAwait 在原始碼搜不到 | HIT:同 p2 | 折:同 p2 |
| g6 | 系統時鐘出處沒交代 Sonar S8692 是測試碼範圍;規則會報建構子參數預設值給 `Clock.System.now()` 的注入寫法 | HIT:前半同 p1;後半用 `class Svc2(private val now: () -> Instant = { Clock.System.now() })` 實跑,第 3 行有報 | 前半折(同 p1);後半放行:這是訊息建議的注入寫法,規則在 rules-unwired/ 不擋;計劃〈天花板〉寫明這個過寬處,REVISIT 2027-05-08 排除參數預設值或在型錄寫明 |
| p1 | TEST-16 的 `System.currentTimeMillis()`、`Date()` 只出現在 Sonar S8692 的說明文字,而 S8692 是測試碼範圍規則;Oracle Clock javadoc 只講 now() | HIT:source-recheck-c 第 33 行記了 S8692 scope 是 Tests、檢查程式不比對 currentTimeMillis | 折:規則拿掉這兩個樣式,好例補「容易誤報:」;逐例表補 C125(currentTimeMillis 不報);型錄壞寫法、情境欄、來源欄改寫 |
| p2 | API-14 沒有一份講到這個寫法的主要出處:IntelliJ 只有名稱與訊息字串,議題 #1493 只是留言 | HIT:IntelliJ KotlinBundle 那行沒有判定條件;議題留言照判法只算佐證 | 折:kt-async-await-immediately 移出規則包,API-14 名稱標(出處不全),通電批次改成「還沒有規則」,測試第 ⑧⑨ 道跟著改 |
| p3 | FLOW-14 規則接收者什麼都收,來源只舉 IntRange,其他型別的依據是 Builders.kt 但沒列 | HIT:Builders.kt 1.9.0 各型別 asFlow 都用 unsafeFlow | 折:型錄來源欄補 Builders.kt 網址 |
| p4 | 導航規則的 `navigate` 不限定接收者;NavController 例外那句是型錄自己串的 | HIT:architecture.yml 用 `$N.navigate($$$)` | 放行:核心(Compose 點擊內 navigate 用 dropUnlessResumed 包)有 KDoc 直接支持,規則在 rules-unwired/ 不擋;〈天花板〉寫明過寬,REVISIT 2027-05-08 收窄接收者 |
| p5 | Mutex 規則的巢狀判斷會穿過子協程 lambda,那不是同一協程重入 | HIT:coroutines.yml 的 has 帶 stopBy: end | 放行:主要寫法(同協程巢狀 withLock)有 KDoc 逐字支持,規則不擋;〈天花板〉寫明,REVISIT 2027-05-08 停在 launch/async 的 lambda |
| p6 | STATE-9 後果把兩段話接起來;TEST-33「PAUSED 預設」的出處網址沒列 | HIT:codelab 與 LooperMode.html 原文 | 折:STATE-9 後果只寫 KDoc 原文;TEST-33 來源補 LooperMode.html |
| e1 | 第一份語料的 Wilson 區間現在就能算,REVISIT 觸發條件不明確 | HIT:照標準公式重算,數字跟席位一致 | 折:〈實驗〉補五條區間;REVISIT 觸發改成「下一次重量任一條時」 |
| e2 | 「代理讀網頁會判寬」沒有複核回頭條件;Provider 對外開放沒有專屬回頭條件 | HIT:七條 REVISIT 逐條對照 | 折:加出處抽查複核的 REVISIT;Provider 抓 manifest 重判併進第一條 REVISIT |
| e3 | TLS 合成同源後是 9/30=30%,不是 31% | HIT:judge-tls.md 9 筆 HttpHelper 全是 TP | 折:改成 9/30(30%) |
| e4 | 第二份語料原檔與 manifest 不在卷證,重現要先照 blob sha 重抓,計劃沒寫 | HIT:corpus-loadurl-v2.tsv 有 blob sha;卷證沒有原檔 | 折:〈實驗〉寫明重現前提;〈天花板〉補一句並加 REVISIT 評估存檔或放重抓腳本 |
| e5 | 轉送路徑全改判也只到 17.5%,可寫進去讓結論不靠那條 REVISIT | HIT:7/40 | 折:〈實驗〉補界限 |
| c1 | 決策取代指向要指到仍有效的那筆 | HIT:同 g4 | 折:同 g4 |
| c2 | 規則包節點不接閘目錄那行仍以現在式寫「出處不全的規則放這裡」 | HIT:Systems/kotlin規則包 那行 | 折:改成 25 條、列出移除的五條,原句改寫成歷史說法 |

- --refuted-set none。
- 修補因果:g1、p1 是上一輪折 s1 時造成的(s1 收窄系統時鐘時,把「只出現在測試碼規則說明文字」也當成直接出處,新加的 Clock.System 樣式又沒逐例守);g3 是上一輪拿掉 View 樣式時沒連帶檢查旁邊的排除;g4、c1 是上一輪記 d2 時沒回頭改逐列查證計劃的取代指向;c2 是上一輪 a4 只改了一行。p2、g5 是 r1 就有的判寬(把「講到相關原則」當支持),r2 沒抓到。其餘是新增段落的措辭或原有漏寫。
- 驗證:規則包測試子集 `-k kotlin_` 639 項、`-k kt_` 535 項全過。三種改壞各自翻紅後還原:拿掉前綴樣式 → C124 紅;加回 currentTimeMillis → C125 紅;拿掉 API-14 的(出處不全) → 第 ⑧ 道紅。

## 先查世界

- PRIOR-ART:p1、g6(時鐘出處)——重讀 Oracle java.time.Clock javadoc、SonarSource/sonar-java 的 S8692 規則 json 與 SystemClockCheck.java。S8692 的 scope 是 Tests,不能當正式碼的直接出處。所以只留 java.time now() 與 Kotlin 官方點名的 Clock.System。
- PRIOR-ART:p2、g5(async 立刻 await)——讀 IntelliJ KotlinBundle 與 kotlinx.coroutines 議題 #1493;detekt 原始碼搜 SequentialAsyncAwait 無結果(source-recheck-a)。官方文件、KDoc、規則頁都沒有直接講到這個寫法,照判法移出。
- PRIOR-ART:g1(樣式比不到帶前綴寫法)——ast-grep 的 pattern 照語法樹比對,接收者 `Clock.System` 與 `kotlin.time.Clock.System` 是不同節點。採用最小解:多列兩個帶前綴的樣式,不改成 regex。
- PRIOR-ART:e1(區間)——Wilson score interval 標準公式,同第三批計劃的算法。
