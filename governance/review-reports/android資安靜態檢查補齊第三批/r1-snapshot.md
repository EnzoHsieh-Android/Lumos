---
type: project
status: doing
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
  - risk/守衛面
related:
  - "[[Projects/Android資安靜態檢查補齊第二批_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---
# Android資安靜態檢查補齊第三批_計劃

> 白話:第二批留了三件「找不到權威出處或形狀分不出」的隱患回頭再查。2026-11-08 重查,其中三件找到了 OWASP MASTG 或官方文件的出處:Compose 密碼欄只用遮字、沒設密碼鍵盤,鍵盤會記住輸入(MASTG-TEST-0258);Jackson 開全域預設型別,外部 JSON 能指定要建的類別(Jackson 官方文件);通知裡放 OTP、帳號這類敏感資料(MASTG-TEST-0315、MASWE-0037)。前兩件寫成 ast-grep 規則、在 GitHub 語料量誤報(密碼欄量到會擋、Jackson 誤報太高只能不接閘),第三件要看內容敏不敏感,寫成語意類的列,交表態與盲判。

PRIOR-ART: ①密碼欄:MASTG-KNOW-0055 給的 Compose 寫法就是 `visualTransformation = PasswordVisualTransformation()` 配 `keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)`,MASTG-TEST-0258 的判定是「處理敏感資料的欄位沒用不快取的輸入類型就不過」;CodeQL 有對應的版面 XML 查詢(java/android/sensitive-keyboard-cache,https://codeql.github.com/codeql-query-help/java/java-android-sensitive-keyboard-cache/),版面 XML 規則包不掃,只做 Compose 這半。②Jackson:官方文件(https://github.com/FasterXML/jackson-docs/wiki/JacksonPolymorphicDeserialization)寫明內容來源不可信時不建議用預設型別、兩端可信時可以;規則只能看到呼叫,看不到 mapper 拿去解什麼,誤報靠量。③通知:MASTG-TEST-0315 的做法就是用靜態分析找出 setContentTitle、setContentText 的位置再人判內容(MASTG-DEMO-0078 用 semgrep 找位置),跟型錄語意類的「表態對程式 + 盲判席」同一個分工。排除:LocalServerSocket(仍只有低權威部落格,Android 參考頁沒寫風險)、自寫 XOR 加密(MASTG 只有提案階段的議題,沒有正式測試頁),照舊留在第二批計劃的回頭條件。
RETIRE-IF: 密碼欄那條在消費專案推送前一個月內被放行(lint-waive)超過三成 → 降回不接閘重量;Android Lint、compose-rules 或 Slack compose-lints 出了同一種檢查 → 自寫規則撤掉、型錄改指現成檢查。

## 用詞

- **規則包**:`configs/ast-grep/kotlin-android/`,`rules/` 會擋(error 在推送前擋)、`rules-unwired/` 只登記不接閘;**型錄**:`skills/kotlin-idioms/checks-catalog.md`。
- **樣本內、樣本外**:同第二批——樣本內是調規則形狀時看過的語料,樣本外是形狀定案之後另撈、排除前面出現過的 repo 的語料,誤報率以樣本外為準。**升級條件**:樣本外命中 ≥20、誤報 ≤10%(同第一、二批)。
- **判不準**:判讀表的 UNSURE(判讀代理看完判不出的),算誤報比例時留在分母。判讀代理=派去逐處打開前後文判 TP/FP 的子代理。
- **既有八項路徑排除**:規則包自寫規則共用的測試碼排除清單(測試 `_KTSEC_IGNORES` 那八個 glob:`**/src/test*/**`、`**/src/androidTest*/**`、`**/src/testFixtures/**`、`**/src/*Test/**`、`**/src/sharedTest/**`、`**/*-test/src/**`、`**/*testing/src/**`、`**/src/debug*/**`)。
- **通電批次、批一、批三**:型錄每列寫這列由哪一批接上機械檢查;批一=規則包會擋的規則已上線;批三=語意類的「表態對程式」與「盲判席」(推送前讓 AI 表態、另派一席不看程式脈絡的判讀)。**情境決策表**:型錄裡語意類情境「看到這個 → 預設這樣寫 → 什麼時候例外」的表,列編號 D-n;**證據樣式**:那一列用來在程式裡找「照標準寫法寫了」的正規式。
- **新增告警閘**:推送前只擋這次新增的告警、既有的不擋;**lint-waive**:對一筆告警留帳放行的指令。**規則包 WHY**:[[Systems/kotlin規則包]] 裡訊息寫法那條(「[型錄編號] 錯在哪;改用 <最短修法>」)。

## 範圍

1. **型錄新列**(編號照現有最大號往下):

   | 型錄列 | 內容 | 管它的 |
   |---|---|---|
   | UI-112 | Compose 密碼欄只遮字沒設密碼鍵盤 | `kt-compose-password-keyboard`(會擋);級 B、接電方式「告警帶寫法」、通電批次「告警帶寫法=批一」 |
   | DATA-99 | Jackson 開全域預設型別 | `kt-jackson-default-typing`(不接閘);級 B、接電方式「告警帶寫法」、通電批次「告警帶寫法=未接(規則在 rules-unwired/:樣本外誤報超過一成或量不夠)」 |
   | DATA-100 | 通知放敏感資料 | 語意類;級 D、接電方式「表態對程式、盲判席」、通電批次「表態對程式=批三;盲判席=批三」;情境決策表 D-57 |

   來源欄帶〔查證 2026-11-08:網址〕;實測狀態寫樣本內外命中與誤報。三列現成規則欄都沒有 Android Lint 或 compose-rules 的候選,〈接電證據〉不用加判定。
2. **規則**(形狀照卷證 `experiment/draft-rules.yml.txt`):
   - **會擋**(`rules/compose.yml`)`kt-compose-password-keyboard`:呼叫名是 TextField、OutlinedTextField、SecureTextField、OutlinedSecureTextField、BasicTextField 或 BasicTextField2,參數裡有 `visualTransformation = …PasswordVisualTransformation(…)`(含 `if (…) VisualTransformation.None else PasswordVisualTransformation()`),而且這個呼叫完全沒有 `keyboardOptions =` 參數。帶了 `keyboardOptions`(不管值是字面還是變數)不報;寫成完整套件名的呼叫(`androidx.compose.material3.TextField(`)不認(漏報,寫進〈天花板〉)。severity error。路徑排除:既有八項,另加 Compose 多平台的桌面原始碼四項 `**/src/desktopMain/**`、`**/src/jvmMain/**`、`**/desktop*/src/**`、`**/*-desktop/src/**`(桌面沒有手機鍵盤快取;第一份樣本外 3 筆桌面誤報只有 1 筆落在這四項裡,另兩筆從路徑看不出是桌面,排除只擋得到照多平台慣例放的桌面碼)。測試 `t_kotlin_rulepack_security_rules` 對每條規則的路徑排除改成逐條期望值(這條是 12 項,其他照舊 8 項)。
   - **不接閘**(`rules-unwired/data.yml`)`kt-jackson-default-typing`:呼叫的被呼叫端是 `.activateDefaultTyping`、`.enableDefaultTyping`、`.activateDefaultTypingAsProperty`、`.enableDefaultTypingAsProperty`;severity error(同其他不接閘的資安規則);路徑排除既有八項。放不接閘的理由:樣本外誤報 83%(幾乎全是後端拿 Redis 當快取,兩端可信)。
   - **訊息**:照規則包 WHY 與型錄自檢 `message_problems` 的硬要求:以 `[型錄編號]` 開頭、連前綴不超過 120 字、含分號、含「改用」或「改成」、不含 `$`(卷證初稿的訊息不合,進 repo 時重寫)。
   - **樣本**:每條 `samples/bad/<id>/` 至少兩處命中、`samples/good/<id>/` 至少兩段。
3. **語意列 DATA-100 與情境決策表 D-57**:
   - 主表:壞寫法 `NotificationCompat.Builder(ctx, ch).setContentText("驗證碼 $otp")`、`setContentTitle("餘額 $balance")`,以及 `setVisibility(NotificationCompat.VISIBILITY_PUBLIC)` 配敏感內容;標準寫法:通知只說「有一則新訊息」、細節進 App 認證後才看,敏感的設 `VISIBILITY_PRIVATE` 加 `setPublicVersion(<遮掉內容的版本>)` 或 `VISIBILITY_SECRET`;情境「語意:要看通知內容敏不敏感」;接電方式「表態對程式、盲判席」,通電批次「表態對程式=批三;盲判席=批三」。
   - D-57:情境「要發通知」;觸發字 `setContentText`、`setContentTitle`、`NotificationCompat.Builder`;證據樣式主寫 `setPublicVersion\(|VISIBILITY_SECRET`(VISIBILITY_PRIVATE 是預設值,單寫它不算照做;要附遮掉內容的版本或整則藏起來)、例外 `(無)`;不適用時「通知內容不含敏感資料(例:下載完成、提醒事項)→ 照一般寫法,不必設可見度」;對應檢查 DATA-100。
   - 情境樣本 `samples/situation/D-57.kt.txt`:`main-ok` 一段(VISIBILITY_PRIVATE 加 setPublicVersion)、`bad` 一段(VISIBILITY_PUBLIC 配驗證碼),照型錄自檢既有的情境樣本格式。
4. **型錄手寫節**:〈統計〉由 `stats_problems` 核對的數照程式重數(總列數、各主題、各級、情境、規則包條數與不接閘、被會擋的規則守到的列數、逐列查證);情境決策表列數那行 `stats_problems` 不核對,照手數改成 57;〈待查證〉不用改(三列都不含待查)。
5. **規則包節點**([[Systems/kotlin規則包]]):資安自寫規則放哪一級那條 WHY 補第三批(密碼欄放 `rules/compose.yml`、Jackson 放 `rules-unwired/data.yml` 與理由),不另開新行。
6. **第二批計劃的回頭條件**:第 96 行(通知那一半已做、LocalServerSocket 與 XOR 照舊)、第 99 行(Compose 那半已做、版面 XML 照舊)、第 100 行(Jackson 已量)各改寫或結案;〈不做〉那兩句「鍵盤快取規則包掃不到」「Jackson 語料撈不到」照這次結果更正。
7. 不做:版面 XML 的 `android:inputType`(規則包不掃 XML);Jackson 形狀第二版(例:排除 Redis 快取設定裡的 mapper)——要等有新語料才能量,寫成回頭條件;LocalServerSocket、自寫 XOR。

## 實驗

2026-11-08,ast-grep 0.51.1,規則初稿在暫存區跑(卷證 `governance/review-reports/android資安靜態檢查補齊第三批/experiment/`)。語料用 GitHub 程式搜尋撈 Kotlin 檔,排除第二批出現過的 repo;repo 以種子 20261109(任意選的固定數,讓切法可重現)隨機對半切成樣本內外,各抽 40 處由判讀代理打開前後 20 行判(判讀準則 `judge-*.md`)。

| 規則 | 樣本內 命中/抽判/誤報/判不準 | 樣本外 命中/抽判/誤報/判不準 | 放哪 |
|---|---|---|---|
| kt-jackson-default-typing | 125/40/37/1 | 121/40/33/3 | `rules-unwired/`(樣本外誤報 83%) |
| kt-compose-password-keyboard 第一版 | 236/40/2/1 | 239/40/7/0(17.5%,其中 3 筆是 Compose Desktop) | — |
| kt-compose-password-keyboard 第二版(加排除桌面四項) | — | 另撈 404 個 repo(排除前兩份):172/40/0/0 | `rules/compose.yml` |

第二版跟第一版只差路徑排除,第二份樣本外的 0 誤報主要是語料組成不同,不是排除那四項的功勞。兩份樣本外合起來 80 處誤報 7 處(8.75%),在升級條件的一成以內但很勉強;照兩份合計判,放 `rules/`。

第二版的樣本外語料用了兩組查詢(`PasswordVisualTransformation keyboardType`、`PasswordVisualTransformation OutlinedTextField`);第一組撈到的檔在別處提過鍵盤類型,這種檔的作者可能比較常設鍵盤,誤報率可能被低估,寫進〈天花板〉。

## 實務隱患

- 密碼欄規則擋到消費專案既有寫法:新增告警閘只擋這次新增的告警,既有的不擋;誤報走 lint-waive 留帳。
- 非敏感的遮字欄位(例:遮住的非秘密文字)會誤報:語料 120 處裡沒見到,照實寫在〈天花板〉。
- 外層用共用元件把 keyboardOptions 從參數帶進來:帶了參數就不報,規則只在呼叫本身完全沒有 keyboardOptions 時報。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。
- 已排除:金流:只改型錄、規則包與測試,不碰付款。
- 已排除:對外送出:不寄信、不呼叫外部服務。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 密碼欄要用不快取的輸入類型 | MASTG-TEST-0258 | https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0258/ |
| Compose 密碼欄的正確寫法 | MASTG-KNOW-0055 | https://mas.owasp.org/MASTG/knowledge/android/MASVS-STORAGE/MASTG-KNOW-0055/ |
| 預設型別在來源不可信時不建議用 | Jackson 官方文件 | https://github.com/FasterXML/jackson-docs/wiki/JacksonPolymorphicDeserialization |
| 通知不放敏感資料 | MASTG-TEST-0315 | https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0315/ |
| 通知要設可見度遮掉敏感內容 | MASWE-0037 | https://mas.owasp.org/MASWE/MASVS-PLATFORM/MASWE-0037/ |
| 三種鎖定畫面可見度 | Android 官方通知文件 | https://developer.android.com/develop/ui/views/notifications/build-notification |

## 驗收條款

- [S1] 當逐例測試對預期值表每一列 S1 的寫法各跑一次規則包時,該報的 應 恰好被那條規則報一次、不該報的 應 不被它報 [test:t_kotlin_rulepack_security_rules]
- [S2] 當列舉規則包時,kt-compose-password-keyboard 應 在 `rules/compose.yml`、severity 是 error、路徑排除是既有八項加桌面四項,kt-jackson-default-typing 應 在 `rules-unwired/data.yml`、路徑排除是既有八項,兩條訊息 應 以型錄列編號開頭、連前綴不超過 120 字 [test:t_kotlin_rulepack_security_rules]
- [S3] 當真型錄跑型錄自檢時,問題數 應 是 0,〈統計〉由 stats_problems 核對的數 應 等於重數 [test:t_kotlin_catalog_rows_wired]
- [S4] 當讀真型錄時,UI-112、DATA-99、DATA-100 應 各在主表,D-57 應 在情境決策表而且對應檢查是 DATA-100,D-57 的情境樣本 應 通過證據樣式自測 [test:t_kotlin_rulepack_security_rules]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())` | 報 | MASTG-KNOW-0055 |
| S1 | `OutlinedTextField(value = p, onValueChange = {}, visualTransformation = if (show) VisualTransformation.None else PasswordVisualTransformation())` | 報 | 同上:可切換顯示的密碼欄 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password))` | 不報 | MASTG-KNOW-0055 的正確寫法 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = opts)` | 不報 | 範圍 2:帶了 keyboardOptions 就不報 |
| S1 | `TextField(value = p, onValueChange = {})` | 不報 | 範圍 2:沒有遮字就不是密碼欄 |
| S1 | 放在 `src/desktopMain/kotlin/` 底下的第一列寫法 | 不報 | 範圍 2:桌面沒有手機鍵盤快取 |
| S1 | `mapper.activateDefaultTyping(mapper.polymorphicTypeValidator, ObjectMapper.DefaultTyping.NON_FINAL)` | 報(不接閘那條) | Jackson 官方文件 |
| S1 | `JsonMapper.builder().activateDefaultTyping(ptv).build()` | 報一次(不接閘那條) | 同上;鏈式寫法只報 activateDefaultTyping 那一層 |
| S1 | `mapper.registerModule(KotlinModule())` | 不報 | 沒開預設型別 |
| S2 | 列舉規則包 | 兩條照範圍 2 的檔、等級、路徑排除,訊息 ≤120 字且以型錄編號開頭 | 本計劃範圍 2 |
| S3 | 真型錄 | 型錄自檢 0 個問題 | 本計劃範圍 4 |
| S4 | 真型錄 | 三列在主表、D-57 對應 DATA-100、情境樣本自測過 | 本計劃範圍 1、3 |

## 回退

退回本計劃的提交:兩條規則與樣本、型錄三列與 D-57、情境樣本、〈統計〉改動、第二批計劃那三條回頭條件與兩句更正、測試擴充、Systems/kotlin規則包 那幾行。卷證留著。

## 天花板

- 密碼欄兩份樣本外合計 80 處誤報 8.75%,離一成很近;第二份還有一組查詢偏向「別處提過鍵盤類型」的檔,誤報率可能被低估。
- 寫成完整套件名的呼叫不認,會漏報。
- 判讀只看了呼叫本身與共用元件的參數,沒有逐檔找外層用別的方式設密碼鍵盤的寫法。
- 通知那列靠表態與盲判,規則包不判通知內容敏不敏感。

REVISIT:2027-05-08 用新一批語料重量 kt-compose-password-keyboard(查詢不帶 keyboardType),樣本外誤報超過一成就降回不接閘
REVISIT:2027-05-08 Jackson 試第二版形狀(排除同函式把 mapper 交給 Redis 序列化器或快取設定的寫法),用新語料重量,過升級條件才升

## 審計修正紀錄
