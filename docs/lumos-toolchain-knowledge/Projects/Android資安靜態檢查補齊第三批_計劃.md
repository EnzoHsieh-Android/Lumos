---
type: project
status: done
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/done
  - scope/stack-knowledge
  - risk/守衛面
related:
  - "[[Projects/Android資安靜態檢查補齊第二批_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---
# Android資安靜態檢查補齊第三批_計劃

> 白話:第二批留了三件「找不到權威出處或形狀分不出」的隱患回頭再查。2026-11-08 重查,其中三件找到了 OWASP MASTG 或官方文件的出處:Compose 密碼欄只用遮字、沒設密碼鍵盤,鍵盤會記住輸入(MASTG-TEST-0258);Jackson 開全域預設型別,外部 JSON 能指定要建的類別(Jackson 官方文件);通知裡放 OTP、帳號這類敏感資料(MASTG-TEST-0315、MASWE-0037)。前兩件寫成 ast-grep 規則、在 GitHub 語料量誤報(密碼欄第三版在一份全新樣本外單獨過升級條件、放會擋;Jackson 誤報太高只能不接閘),第三件要看內容敏不敏感,寫成語意類的列,交表態與盲判。

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
2. **規則**(密碼欄形狀照卷證 `experiment/draft-rules-v3-pwd.yml.txt`、逐例在 `experiment/pwd-v3-cases.kt.txt`;Jackson 照 `experiment/draft-rules.yml.txt`):
   - **會擋**(`rules/compose.yml`)`kt-compose-password-keyboard`:呼叫名是 TextField、OutlinedTextField、BasicTextField 或 BasicTextField2(Material3 的 SecureTextField、OutlinedSecureTextField 沒有 `visualTransformation` 參數、預設就是密碼鍵盤,不列),參數裡有 `visualTransformation = …PasswordVisualTransformation(…)`(含 `if (…) VisualTransformation.None else PasswordVisualTransformation()`),而且符合下面任一:①這個呼叫完全沒有 `keyboardOptions =` 參數;②`keyboardOptions` 的值是字面的 `KeyboardOptions.Default` 或 `KeyboardOptions(…)`(括號裡沒有再呼叫函式),裡面沒有 `KeyboardType.Password`、`KeyboardType.NumberPassword`,而且沒寫 `keyboardType =` 或寫的是 `KeyboardType.<名字>` 這種字面值。值是變數(`opts`)、`.copy(…)`、括號裡有函式呼叫、`keyboardType` 是變數的,看不出最後設了什麼,不報;寫成完整套件名的呼叫(`androidx.compose.material3.TextField(`)不認(漏報,寫進〈天花板〉)。severity error。路徑排除:既有八項,另加 Compose 多平台的桌面原始碼四項 `**/src/desktopMain/**`、`**/src/jvmMain/**`、`**/desktop*/src/**`、`**/*-desktop/src/**`,照 `rules-unwired/data.yml` 的寫法排成單行一個 `ignores: [...]`、八項在前四項在後(compose.yml 現有那處三項的多行寫法不跟;桌面沒有手機鍵盤快取;第一份樣本外 3 筆桌面誤報只有 1 筆落在這四項裡,另兩筆從路徑看不出是桌面,排除只擋得到照多平台慣例放的桌面碼)。測試 `t_kotlin_rulepack_security_rules` 對每條規則的路徑排除改成逐條期望值(這條是 12 項,其他照舊 8 項),期望值寫在 `_KTSEC_PLACE` 各條的值裡。形狀凍結在卷證 `experiment/pwd-v3-frozen.sha.txt`(第三版規則檔的雜湊),進 repo 的規則只准改訊息與排版。
   - **不接閘**(`rules-unwired/data.yml`)`kt-jackson-default-typing`:呼叫的被呼叫端是 `.activateDefaultTyping`、`.enableDefaultTyping`、`.activateDefaultTypingAsProperty`、`.enableDefaultTypingAsProperty`;severity error(同其他不接閘的資安規則);路徑排除既有八項。放不接閘的理由:樣本外誤報 83%(幾乎全是後端拿 Redis 當快取,兩端可信)。
   - **訊息**:照規則包 WHY 與型錄自檢 `message_problems` 的硬要求:以 `[型錄編號]` 開頭、連前綴不超過 120 字、含分號、含「改用」或「改成」、不含 `$`(卷證初稿的訊息不合,進 repo 時重寫)。
   - **樣本**:每條 `samples/bad/<id>/` 至少兩處命中、`samples/good/<id>/` 至少兩段。
3. **語意列 DATA-100 與情境決策表 D-57**:
   - 主表:壞寫法 `NotificationCompat.Builder(ctx, ch).setContentText("驗證碼 $otp")`、`setContentTitle("餘額 $balance")`,以及 `setVisibility(NotificationCompat.VISIBILITY_PUBLIC)` 配敏感內容;標準寫法:通知只說「有一則新訊息」、細節進 App 認證後才看,敏感的設 `VISIBILITY_PRIVATE` 加 `setPublicVersion(<遮掉內容的版本>)` 或 `VISIBILITY_SECRET`;情境「語意:要看通知內容敏不敏感」;接電方式「表態對程式、盲判席」,通電批次「表態對程式=批三;盲判席=批三」。
   - D-57:情境「要發通知」;觸發字 `setContentText`、`setContentTitle`、`NotificationCompat.Builder`;證據樣式主、例外都寫 `(無)`(標準寫法的第一種「通知只說有一則新訊息」寫不出字面特徵,型錄證據樣式的規定是同一段裡有寫不出特徵的寫法就寫 `(無)`;另一種 `setPublicVersion(`、`VISIBILITY_SECRET` 雖然寫得出,單寫它會讓第一種每次都被提醒);不適用時「通知內容不含敏感資料(例:下載完成、提醒事項)→ 照一般寫法,不必設可見度」;對應檢查 DATA-100。
   - 不放情境樣本檔:證據樣式兩段都 `(無)` 的列放了樣本,型錄自檢 `situation_sample_problems` 會報「樣本沒有作用」。
4. **型錄手寫節**:〈統計〉由 `stats_problems` 核對的數照程式重數(總列數、各主題、各級、情境、規則包條數與不接閘、被會擋的規則守到的列數、逐列查證);測試 `_KT_STATS_LINES` 寫死的同一批數一起改成新值(那支測試的改壞動作是把型錄裡的這些字樣換成別的數,型錄換了新數而測試還寫舊數,改壞套不上、整支紅);情境決策表列數那行 `stats_problems` 不核對,照手數改成 57,括號裡的證據樣式分項改成用 check.py 的 dt_table 程式數(實作時數到舊值 8、31、5 在這批之前就已過期,57 列是 15、34、11);〈待查證〉不用改(三列都不含待查)。
5. **規則包節點**([[Systems/kotlin規則包]]):資安自寫規則放哪一級那條 WHY 補第三批(密碼欄放 `rules/compose.yml`、Jackson 放 `rules-unwired/data.yml` 與理由),不另開新行。
6. **第二批計劃的回頭條件**:第 96 行(通知那一半已做、LocalServerSocket 與 XOR 照舊)、第 99 行(Compose 那半已做、版面 XML 照舊)、第 100 行(Jackson 已量)各改寫或結案;〈不做〉那兩句「鍵盤快取規則包掃不到」「Jackson 語料撈不到」照這次結果更正。
7. 不做:版面 XML 的 `android:inputType`(規則包不掃 XML);Jackson 形狀第二版(例:排除 Redis 快取設定裡的 mapper)——要等有新語料才能量,寫成回頭條件;LocalServerSocket、自寫 XOR。

## 實驗

2026-11-08,ast-grep 0.51.1,規則初稿在暫存區跑(卷證 `governance/review-reports/android資安靜態檢查補齊第三批/experiment/`)。語料用 GitHub 程式搜尋撈 Kotlin 檔,排除第二批出現過的 repo;repo 以種子 20261109(任意選的固定數,讓切法可重現)隨機對半切成樣本內外,各抽 40 處由判讀代理打開前後 20 行判(判讀準則 `judge-*.md`)。

| 規則 | 樣本內 命中/抽判/誤報/判不準 | 樣本外 命中/抽判/誤報/判不準 | 放哪 |
|---|---|---|---|
| kt-jackson-default-typing | 125/40/37/1 | 121/40/33/3 | `rules-unwired/`(樣本外誤報 83%) |
| kt-compose-password-keyboard 第一版 | 236/40/2/1 | 239/40/7/0(17.5%,其中 3 筆是 Compose Desktop) | — |
| kt-compose-password-keyboard 第二版(加排除桌面四項) | — | 另撈 404 個 repo(排除前兩份):172/40/0/0 | —(兩份樣本外都用來調過形狀,改當樣本內) |
| kt-compose-password-keyboard 第三版(凍結,見下) | 前三份 | 第三份:846/40/3/0(7.5%,Wilson 95% 上界約 20%) | `rules/compose.yml` |

第二版跟第一版只差路徑排除,第二份樣本外的 0 誤報主要是語料組成不同,不是排除那四項的功勞。前兩份樣本外都在看過之後改過形狀(第一份之後加桌面排除、設計審之後加「字面 KeyboardOptions 沒設密碼鍵盤也報」),對第三版來說都是樣本內,不拿來判升級;第一、二批的升級條件也是一份樣本外單獨判、沒有合計的先例。

第三版的量法(2026-11-08):
- 形狀先凍結:規則檔(含 12 項排除)的 sha256 寫在 `experiment/pwd-v3-frozen.sha.txt`,跑語料前核對過一致。
- 語料:查詢只用 `PasswordVisualTransformation language:Kotlin`、不帶 `keyboardType`,按檔案大小切八片(同一組查詢 GitHub 只回前 1000 筆,前 1000 筆的 repo 在第一份就用掉了;大小跟有沒有設鍵盤無關),排除前三份出現過的 1266 個 repo;撈到 1587 個 repo 的 1691 支檔(`experiment/corpus-pwd3.tsv`)。
- 抽判:種子 20261110,每個 repo 最多抽一處(避免同 repo 多筆不獨立),40 處由乾淨的判讀代理照 `experiment/judge-pwd-v3.md` 判(範例碼只看路徑與 repo 名兩樣客觀特徵);判讀結果原文在 `experiment/pwd-oos3-judge.md`,TP 39、FP 1。
- 編排者機械重核:逐 repo 查有沒有 `AndroidManifest.xml`、建置檔有沒有 `compose.desktop`(`experiment/pwd-oos3-platform.tsv`);兩處是純 Compose 桌面專案(沒有 manifest、建置檔是 desktop),判讀代理判成 TP,改判 FP(桌面沒有手機鍵盤快取);三個沒有 manifest 的 repo 只上傳了 Android 原始碼(有 MainActivity、Firebase),維持 TP;三個多平台 repo 的命中在 commonMain 或手機模組,維持 TP。最後 FP 3(作業 repo 1、純桌面 2)/40 = 7.5%,過升級條件(命中 ≥20、誤報 ≤10%)。

## 實務隱患

- 密碼欄規則擋到消費專案既有寫法:新增告警閘只擋這次新增的告警,既有的不擋;誤報走 lint-waive 留帳。
- 非敏感的遮字欄位(例:遮住的非秘密文字)會誤報:三份樣本外判讀都沒見到,照實寫在〈天花板〉。
- 外層用共用元件把 keyboardOptions 從參數帶進來:值是變數就不報,規則只在呼叫本身沒有 keyboardOptions、或字面寫了卻沒設密碼鍵盤時報。
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
- [S3] 當真型錄跑型錄自檢時,問題數 應 是 0,〈統計〉由 stats_problems 核對的數 應 等於重數,而且測試寫死的〈統計〉值 應 每個都在真型錄裡找得到 [test:t_kt_catalog_stats_consistent]
- [S4] 當讀真型錄時,UI-112、DATA-99、DATA-100 應 各在主表、名稱與通電批次照範圍 1 的表,D-57 應 在情境決策表、對應檢查是 DATA-100、證據樣式兩段都是 `(無)`,D-57 應 沒有情境樣本檔,型錄自檢與情境樣本自檢 應 都是 0 個問題 [test:t_kt_catalog_security_lint_batch3]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())` | 報 | MASTG-KNOW-0055 |
| S1 | `OutlinedTextField(value = p, onValueChange = {}, visualTransformation = if (show) VisualTransformation.None else PasswordVisualTransformation())` | 報 | 同上:可切換顯示的密碼欄 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password))` | 不報 | MASTG-KNOW-0055 的正確寫法 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = opts)` | 不報 | 範圍 2:帶了 keyboardOptions 就不報 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done))` | 報 | 範圍 2 ②:字面的 KeyboardOptions 沒設密碼鍵盤 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions.Default)` | 報 | 範圍 2 ② |
| S1 | `OutlinedTextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text))` | 報 | 範圍 2 ②:字面鍵盤類型不是密碼 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword, imeAction = ImeAction.Done))` | 不報 | PIN 欄的正確寫法 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = kt))` | 不報 | 範圍 2:鍵盤類型是變數,看不出來 |
| S1 | `TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions.Default.copy(keyboardType = KeyboardType.Password))` | 不報 | 範圍 2:`.copy(…)` 不判 |
| S1 | `BasicTextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())` | 報 | 範圍 2:呼叫名單的 BasicTextField |
| S1 | `BasicTextField2(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())` | 報 | 範圍 2:呼叫名單的 BasicTextField2 |
| S1 | `SecureTextField(state = s)` | 不報 | Material3 的密碼元件預設就是密碼鍵盤 |
| S1 | `TextField(value = p, onValueChange = {})` | 不報 | 範圍 2:沒有遮字就不是密碼欄 |
| S1 | 放在 `src/desktopMain/kotlin/` 底下的第一列寫法 | 不報 | 範圍 2:桌面沒有手機鍵盤快取 |
| S1 | `mapper.activateDefaultTyping(mapper.polymorphicTypeValidator, ObjectMapper.DefaultTyping.NON_FINAL)` | 報(不接閘那條) | Jackson 官方文件 |
| S1 | `JsonMapper.builder().activateDefaultTyping(ptv).build()` | 報一次(不接閘那條) | 同上;鏈式寫法只報 activateDefaultTyping 那一層 |
| S1 | `mapper.registerModule(KotlinModule())` | 不報 | 沒開預設型別 |
| S1 | `ObjectMapper().apply { activateDefaultTyping(ptv) }` | 不報 | 〈天花板〉:隱含接收者不認(釘住現行行為,免得以為有報) |
| S1 | `TextField(…, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text, imeAction = ImeAction.Done))` | 報 | 範圍 2 ②:字面鍵盤類型後面還有參數 |
| S1 | `mapper.activateDefaultTypingAsProperty(ptv, ObjectMapper.DefaultTyping.NON_FINAL, "@class")` | 報(不接閘那條) | 範圍 2:AsProperty 版本 |
| S1 | `mapper.enableDefaultTypingAsProperty(ObjectMapper.DefaultTyping.NON_FINAL, "@class")` | 報(不接閘那條) | 範圍 2:舊 API 的 AsProperty 版本 |
| S1 | 字面 `KeyboardOptions(imeAction = ImeAction.Done, // TODO KeyboardType.Password` 換行 `)` | 不報 | 〈天花板〉:註解裡寫到密碼鍵盤也當成已設(釘住現行行為) |
| S1 | `MyTextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())` | 不報 | 〈天花板〉:自訂元件名不認 |
| S1 | `androidx.compose.material3.TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation())` | 不報 | 〈天花板〉:完整套件名不認 |
| S1 | `KeyboardOptions(keyboardType = KeyboardType.Text, imeAction = if (x) ImeAction.Done else ImeAction.Next)` | 不報 | 〈天花板〉:括號裡再有括號就不判 |
| S2 | 列舉規則包 | 兩條照範圍 2 的檔、等級、路徑排除,訊息 ≤120 字且以型錄編號開頭 | 本計劃範圍 2 |
| S3 | 真型錄 | 型錄自檢 0 個問題 | 本計劃範圍 4 |
| S4 | 真型錄 | 三列在主表、D-57 對應 DATA-100 且兩段 `(無)`、沒有 D-57 樣本檔、兩種自檢 0 個問題 | 本計劃範圍 1、3 |
| S4 | 真型錄的 UI-112 那列刪掉 | 紅 | 改壞:新列不在主表 |
| S4 | 多放一支 `samples/situation/D-57.kt.txt` | 紅 | 改壞:兩段 `(無)` 的列有樣本 |

## 回退

退回本計劃的提交:兩條規則與樣本、型錄三列與 D-57、〈統計〉改動與測試寫死的統計值、第二批計劃那三條回頭條件與兩句更正、測試擴充、Systems/kotlin規則包 那幾行。卷證留著。

## 天花板

- 密碼欄第三份樣本外誤報 7.5% 是 40 處抽判的點估計,Wilson 95% 上界約 20%;升級條件照第一、二批用點估計判。
- 純 Compose 桌面專案的原始碼目錄跟 Android 一樣(`app/src/main/kotlin`),路徑排除擋不到;規則包只跑在 Android 消費專案,實際影響小。
- 會漏報的寫法:寫成完整套件名的呼叫(`androidx.compose.material3.TextField(`);遮字值放變數再傳(`val vt = PasswordVisualTransformation()` 之後 `visualTransformation = vt`);帶型別參數的 `TextField<String>(`;自訂元件名(`MyTextField(`);`keyboardOptions` 是變數、`.copy(…)`、字面 `KeyboardOptions(…)` 的括號裡再出現任何一對括號(函式呼叫、`if (x) … else …`、`when (…)`、註解裡的括號都算),或 `keyboardType` 是變數;字面 `KeyboardOptions(…)` 裡的註解寫到 `KeyboardType.Password`(規則比對整段原文,註解也算)。
- 誤報只量了命中裡的比例,漏報沒量。
- Jackson 那條只認帶 `.` 的呼叫:`ObjectMapper().apply { activateDefaultTyping(ptv) }` 這種隱含接收者、沒有接收者的 `activateDefaultTyping(ptv)` 不報;同一條鏈呼叫兩次(`mapper.activateDefaultTyping(a).activateDefaultTyping(b)`)會在同一行報兩次。semgrep、Sonar 的對應規則是在 ObjectMapper 上呼叫就報、不分寫法,這條還是不接閘,等第二版形狀一起改。
- 通知那列靠表態與盲判,規則包不判通知內容敏不敏感。

REVISIT:2027-05-08 用新一批語料重量 kt-compose-password-keyboard(形狀照凍結雜湊、排除前四份 repo),樣本外誤報超過一成就降回不接閘
REVISIT:2027-05-08 密碼欄量一次漏報:在一份新語料裡找有 PasswordVisualTransformation 卻沒被規則報的呼叫,逐處判是不是〈天花板〉列的那幾種寫法,漏報多就補形狀
REVISIT:2027-05-08 判讀代理逐檔往外找「已防護」的做法抽查一次:從第三份 TP 裡挑共用元件那幾處,到原 repo 找呼叫端有沒有另外設密碼鍵盤,找到就把那幾處改判、重算誤報率
REVISIT:2027-01-08 在各消費專案跑 `lumos lint-waive --list --json`,數 kt-compose-password-keyboard 被放行的筆數、對照推送前這條擋下的筆數,超過三成照 RETIRE-IF 降回不接閘
REVISIT:2027-01-08 讓型錄自檢 `stats_problems` 也核對〈統計〉情境決策表那行的列數與三個證據樣式分項(這行不核對,第三批之前就過期過一次)
REVISIT:2027-05-08 Jackson 試第二版形狀(排除同函式把 mapper 交給 Redis 序列化器或快取設定的寫法),用新語料重量,過升級條件才升

## 審計修正紀錄

- r1(2026-11-08,四席):13 條/blocking 2/密碼欄改成凍結第三版形狀、另撈第三份樣本外單獨判(7.5%,放會擋);字面 KeyboardOptions 沒設密碼鍵盤改成報;統計測試寫死值一起改;D-57 證據樣式兩段 (無)、不放樣本;S3/S4 改綁專屬型錄測試。
- 席報告與收貨紀錄:`governance/review-reports/android資安靜態檢查補齊第三批/`(r1-*.md、r1-intake.md)。
- 實作(2026-11-08):統計那行的舊值 8、31、5 早已過期(三種口徑都數不出),改成程式數的 15、34、11,設計審時兩席照舊值說 31→32 也一併更正;第二批計劃那條同主題回頭條件結案。
- 代碼審 r1(2026-11-08,兩席):5 條/blocking 0/補四例(逗號分支、Jackson 兩個 AsProperty 名字、註解裡寫到密碼鍵盤的天花板),〈天花板〉補註解那種漏報;測試的新案例改雙引號、放置表第四格直接放排除清單、測試說明補第三批改壞清單。卷證 `governance/review-reports/code-android資安靜態檢查補齊第三批/`。
- 代碼審 r2(2026-11-08,兩席):2 條/blocking 0/補三例釘住天花板(自訂元件名、完整套件名、括號裡再有括號),〈天花板〉那句改成「括號裡再出現任何一對括號」;架構對齊 0 條。
