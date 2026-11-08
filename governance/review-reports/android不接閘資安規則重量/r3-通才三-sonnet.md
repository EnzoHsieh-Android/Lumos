severity: major

## Finding 1
severity: major
blocking: 是
判準:驗收條款 S4 與預期值表宣稱「報」的輸入,實際要報;spec 的〈範圍 5〉說 kt-prod-reads-system-clock「加上 Clock.System.now()」。
引句:「| S4 | `fun stampKt() = kotlin.time.Clock.System.now()` | 報 | Kotlin Clock 文件 |」
問題:照 spec 做出來的規則不報這一列。
- 規則樣式是 `Clock.System.now()`。ast-grep 要求接收者剛好是 `Clock.System`,所以帶套件前綴的 `kotlin.time.Clock.System.now()` 與 `kotlinx.datetime.Clock.System.now()` 都比對不到。
- 壞例樣本裡那行標了 `// BAD`,規則其實沒報它。
- 綁定的 S4 測試 `t_kotlin_rulepack_samples` 只驗每條規則的壞例目錄至少報一處。該目錄的其他三處(currentTimeMillis、Instant.now、LocalDate.now)都有報,所以測試綠燈。
- 把 `Clock.System.now()` 這個樣式整個刪掉,這個測試也不會紅。r2 的 s1 折入的就是這個新樣式,它沒有任何機械守衛。
- 預期值表同一列的另一個說法(不帶前綴時會報)是對的。問題只在 spec 挑了帶前綴的形式當「報」的證據。
佐證:
- 實跑:在規則包樣本目錄 samples/bad/kt-prod-reads-system-clock 用 sgconfig-unwired.yml 掃,只報第 5、8、12 行,第 10 行 stampKt 沒報。
- 我另寫的臨時檔 /tmp/lumos-seat-work/android不接閘資安規則重量/通才三-sonnet/t/src/main/kotlin/a.kt 結果相同:不帶前綴的 `Clock.System.now()` 有報,兩種帶前綴的沒報。
- file: `configs/ast-grep/kotlin-android/rules-unwired/testing.yml:13`
- file: `configs/ast-grep/kotlin-android/samples/bad/kt-prod-reads-system-clock/src/main/kotlin/kt-prod-reads-system-clock.kt:10`
修法方向:規則補上帶前綴的樣式(例如接收者用 `$$$.Clock.System`),或把壞例與預期值改成不帶前綴的形式。再讓測試逐行核對 `// BAD`。

## Finding 2
severity: minor
blocking: 否
判準:同一份 spec 內數字要一致。
引句:「只登記那一級少 3 條、2 條收窄形狀,消費專案推送前的行為不變」
問題:〈實務隱患〉寫少 3 條、2 條收窄。其他地方寫的是移出 4 條、收窄 3 條,包括白話、d2、範圍 5、回退、預期值表。
佐證:
- 規則包不接閘目錄從 30 條變 26 條(`_KT_STATS_LINES` 與 `rules-unwired/` 實數),少 4 條。
- 收窄的是 async、導航、系統時鐘三條。
- file: `scripts/test_lumos.py:129618`

## Finding 3
severity: minor
blocking: 否
判準:拿掉樣式的補丁要連帶檢查它旁邊的條件還有沒有守衛。
引句:「kt-click-navigate-unguarded 拿掉 View 的 setOnClickListener 兩個樣式」
問題:規則仍帶「外層有 `currentDestination` 就不報」的排除,這原本是 View 防護的寫法。
- 唯一測這個排除的好例是 `// case: currentDestination-guard`,它現在寫在 View 的 `setOnClickListener` 裡。規則已不比對 View,好例本來就不會報,所以排除子句被拿掉也不會紅。
- 型錄的形狀欄只寫「外層沒包 dropUnlessResumed」,沒提這個排除。r2 的 t1 把情境欄的 currentDestination 字樣改掉了,規則卻沒跟著動。
- 這個排除沒有出處,也沒有 Compose 版的測試。
佐證:
- file: `configs/ast-grep/kotlin-android/rules-unwired/architecture.yml:11`
- file: `configs/ast-grep/kotlin-android/samples/good/kt-click-navigate-unguarded/src/main/kotlin/kt-click-navigate-unguarded.kt:11`

## Finding 4
severity: minor
blocking: 否
判準:決策紀錄的取代鏈要指到仍有效的那一筆。
引句:「舊決策 DATA-12 改成人裁列那半不受影響」
問題:兩處對不上。
- 逐列查證計劃的 d1 把 DATA-12 的取捨提醒和 API-14、TEST-31 標出處不全放在同一筆決策。這一筆整筆被標成 `valid: false`,取代者指向本計劃的 `#d1`。但本計劃的 d1 自己也已 `valid: false`,有效的是 d2。
- d2 又說 DATA-12 那半不受影響。結果 DATA-12 那半現在沒有任何有效決策可查。
佐證:
- file: `docs/lumos-toolchain-knowledge/Projects/Android寫法型錄逐列查證_計劃.md:21`
- `lumos lint` 對兩篇都回 0 問題,所以這個缺口機器沒抓到。

## Finding 5
severity: minor
blocking: 否
判準:出處補查要求「出處直接講到規則判定的那個寫法」;補進來的句子不能多講原文沒有的事。
引句:「IntelliJ 內建檢查講的是同一個 scope 的 async{…}.await()」
問題:型錄引用的 IntelliJ 資源檔只有 `inspection.redundant.async.display.name=Redundant 'async' call` 與 `Redundant ''async'' call may be reduced to ''{0}''` 兩行。原文沒有任何「同一個 scope」的限定,這是 spec 自己的推論。
- 另一半依據是議題 #1493 維護者的一句話,脈絡是 GlobalScope 加 NonCancellable。收貨檔 source-recheck-a 自己標它「不在權威來源範圍,只能算近權威」。
- 型錄 API-14 的來源欄仍寫 `SC CONCUR_003:detekt SequentialAsyncAwait`,而同一份 source-recheck-a 說在 detekt 原始碼搜不到這個名字。
- 這比被降級的 TEST-31 證據強,但判法並不一致。規則收窄成保守形狀本身無害。
佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:166`
- file: `governance/review-reports/android不接閘資安規則重量/experiment/source-recheck-a.md:14`

## Finding 6
severity: minor
blocking: 否
判準:出處說明要交代對規則範圍有影響的限制。
引句:「各有 Oracle Clock javadoc 或 Sonar S8692 的原文」
問題:source-recheck-c 查到兩個限制,spec 都沒寫。
- S8692 的標題與設定是「測試碼」範圍。
- 它的檢查程式其實不比對 `System.currentTimeMillis()`,只有說明文字提到。
- 所以 `currentTimeMillis` 只有說明文字支持,不是 Oracle 加 Sonar 雙重支持。
另外,規則會報 `class Svc2(private val now: () -&gt; Instant = { Clock.System.now() })` 這種「建構子帶預設值」的注入寫法。這正是訊息建議的做法,實測會誤報,好例沒有「容易誤報:」註記它。
佐證:
- file: `governance/review-reports/android不接閘資安規則重量/experiment/source-recheck-c.md:33`
- 我的臨時檔 a.kt 第 12 行實測有報。

## 修補驗收結果與沒問題的節
**r1 與 r2 收貨紀錄的折入處置,逐條到 repo 核對:**
- r1 的 g1 到 g7、n1 到 n5、e1 到 e6、a1 到 a3:都落實。
  - 〈用詞〉、去重位置數與 Provider 去重後 8/20 都在,重算確認那筆重複判的是 TP。
  - 敏感度腳本與結果、v2 判準雜湊(sha256 重算一致)、天花板與 REVISIT 的對應、回退清單都在,v2 抽樣腳本與命中檔也在。
  - 型錄 7 列的數字逐列對卷證重數一致。TLS 11 處誤報分項 4、3、2、1、1,指令執行 22 加 5,Provider 的 7 處「已防護」都對。
  - 命中數、去重位置數、repo 數與 hits 檔重算一致。Wilson 區間 62 到 88%、6 到 35% 重算一致。
- r2 的 t1 到 t4、s1 到 s5、x1 到 x6、a1 到 a6:除下列例外都落實。
  - 訊息改寫、七條訊息的回退逐項、通電批次寫法、TEST-31 的 `~索引` 改寫都在,「容易誤報:」前綴也在。
  - API-36 與 UI-103 寫「還沒有規則」。逐列查證計劃的 REVISIT 有 `[closed:]`。
  - 例外:s1 的 Clock.System 樣式沒有守衛(Finding 1),t1 對 ARCH-3 的處理只改了型錄沒改規則(Finding 3)。
- 型錄統計:規則包 225 條、不接閘 26 條、出處不全 28 列、查證 525 列,與測試寫死值一致。
- 規則與型錄的對應:非不接閘的規則掛的型錄列都沒有出處不全且都有查證網址。
- 四條移出的規則:除計劃與規則包節點外,沒有殘留引用。`rules-unwired/compose.yml` 已刪。
- S4 其餘四列(別的 scope 的 async 不報、同 scope 報、View 點擊不報、SystemClock 不報)實測成立。
- 引用來源核對:Kotlin Clock 文件那句、dropUnlessResumed 的 KDoc 原文、Sonar PR #5611 網址(回 200)都屬實。
- 本機測試:`-k t_kotlin_rulepack_unwired_dir` 11 過、`-k t_kotlin_rulepack_samples` 27 過、`-k t_kotlin_catalog_rows_wired` 20 過、`-k kotlin_rulepack` 245 過。`scripts/lumos lint` 對計劃與規則包節點都是 0 問題。

**固定席(Systems/kotlin規則包):不影響合約。**
- 該節點 0 條 KEY、0 條合約。
- 兩條相關 WHY 仍成立:「出處不全列的規則只准放 rules-unwired/」(現在零條)與新補的「查不到就移出」,兩者不互相打架。
- 唯一小殘留:節點第 77 行描述 `rules-unwired/` 時仍寫「引用型錄出處不全列的規則」,現況已無這類規則。

**實務隱患逐類:**
- 金流、對外送出、不可逆、守衛面:無。改動只在不接閘目錄、型錄、測試與圖譜,`rules/` 沒動,退回提交即還原,spec 的排除理由成立。
- 併發:無,單人依序操作。
- 隱私與資料:無。卷證只收公開 repo 的路徑清單與判讀文字,沒有個資。
- 相容性:無新增。移出的四條規則在別處沒有引用,消費專案若有針對它們的抑制註解,留著也不會出錯。

建過的路徑:
- /tmp/lumos-seat-work/android不接閘資安規則重量/通才三-sonnet/
- /tmp/lumos-seat-work/android不接閘資安規則重量/通才三-sonnet/t/
- /tmp/lumos-seat-work/android不接閘資安規則重量/通才三-sonnet/t/src/main/kotlin/a.kt
- /tmp/lumos-seat-work/android不接閘資安規則重量/通才三-sonnet/t/sg.yml

最高等級 major;blocking 1 條
