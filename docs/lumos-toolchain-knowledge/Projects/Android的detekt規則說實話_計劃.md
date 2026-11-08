---
type: project
status: doing
created: 2026-11-04
updated: 2026-11-08
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/lint-declaration-health
  - Systems/linter精選目錄
  - Systems/效能檢核目錄
  - Systems/pitfalls-lint-adapter
related:
  - "[[Projects/detekt協程規則真的在跑_計劃]]"
  - "[[Issues/推送閘對Android的detekt只記錄不擋]]"
  - "[[Projects/Android的detekt推送前真的擋_計劃]]"
  - "[[Projects/Android協程與API協同機械審_調研]]"
  - "[[Systems/lint-declaration-health]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/pitfalls-lint-adapter]]"
---
# Android的detekt規則說實話_計劃

> 白話:Android 專案的 detekt 現在有兩件事跟大家以為的不一樣:①共用設定開的協程規則,照標準接法跑多半沒在跑(要型別資訊,沒給就安靜跳過);②推送前的新增告警檢查對 detekt 從來不擋。這案不修這兩件事(修法在 [[Projects/Android的detekt推送前真的擋_計劃]]),只做到「工具自己講實話」:lint-check 與健檢看到 detekt 宣告時,照一張窮舉的判定表印出它實際會怎樣;文件與圖譜裡「已開」的說法全部改成「已開,但要型別資訊才跑、推送時不擋」。順手補開兩條規則、改掉文件裡 detekt 1.23.8 不存在的規則名。出身:已作廢的 [[Projects/detekt協程規則真的在跑_計劃]] 第一輪設計審。

PRIOR-ART: ①提醒形狀用健檢 F 段既有「有 eslint 設定但沒接」那則的同一個形狀(提醒函式帶空清單:不計問題、不讓 CI 變紅),在 F 段新加一個判斷。②指令拆詞用 Python 標準庫 shlex(設定見〈判定表〉拆詞那段,照 Python 官方 shlex 文件與本機實測),不自寫引號解析;本 repo 只有掛鉤命令用過 shlex 整串拆詞(沒拆標點),這裡多開標點拆段是第一次;lint 命令本身照舊交給 shell 執行,這裡只拆來判讀、不改命令。③判定依據來自 detekt 1.23.8 自己的說明(`detekt --help` 的參數表)、Gradle 命令列說明、2026-11-04 編排者本機實測與設計審席位實測(見〈判定依據〉,各句標出處),detekt 官方型別解析文件明寫沒有型別解析時要型別的規則「不會跑」。不新建執行機制、不加設定鍵;新增的只有一支判定函式、一支從新增告警檢查抽出的共用小函式、一條共用設定檢查測試與它的對照資料。
RETIRE-IF: [[Projects/Android的detekt推送前真的擋_計劃]] 落地、而且 detekt 本身在缺型別資訊時會警告——那時提醒裡「不擋」與「沒在跑」兩句都不再成立,整張判定表改寫或拿掉。

## 用詞

- **型別資訊**:detekt 指令列的 `--classpath`(簡寫 `-cp`)與 `--jdk-home`。前者給依賴的型別,後者給 JDK 的型別(Thread.sleep 這類);JDK 那批規則要兩者都有才響(只給 `--jdk-home`、沒 classpath 時也不響)。`--jvm-target` 實測不影響規則響不響,不算進來。
- **共用設定**:本 repo 分發的 detekt 設定檔(configs 底下 detekt 資料夾的 android.yml,家是 [[Systems/linter精選目錄]])。消費專案的宣告用絕對路徑指向安裝在本機的這份檔,所以這裡改了,消費專案下次更新工具鏈就跟著變,不用改它們的檔。
- **要型別資訊的規則**(detekt 預設開、共用設定開、或本案補開的,實測確認):InjectDispatcher、SuspendFunSwallowedCancellation、SuspendFunWithFlowReturnType、SuspendFunWithCoroutineScopeReceiver、RedundantSuspendModifier、SleepInsteadOfDelay(要開型別解析加 JDK)、CouldBeSequence、ArrayPrimitive(只要 classpath)、ForbiddenMethodCall。其中 RedundantSuspendModifier 與 SleepInsteadOfDelay 只要開了型別解析(有給 classpath,就算指到不存在的檔)就響,不依賴 classpath 裡真的有哪些 jar;其餘要 classpath 裡真的有對應函式庫。**不用型別資訊就會響的**:GlobalCoroutineUsage、ForEachOnRange——同步文件時這兩條不准標「要型別資訊」。
- **detekt 宣告**:`.lumos/lint.json` 裡任一副檔名底下、照下面判定表認得出是 detekt 的那條命令。
- **新增告警檢查**:推送前在合併基準與這次改動上各跑一次 linter、只擋新增告警的那道檢查,家是 [[Systems/pitfalls-lint-adapter]]。

## 判定表(窮舉;表外的寫法一律不判、不提醒)

**拆詞**:
1. 先把「反斜線緊接換行」換成一個空白(續行),再按換行切成多行,每行各自拆。
2. 每行用 `shlex.shlex(行, posix=True, punctuation_chars=';&|')`,並設 `whitespace_split=True`、`commenters=''`(shell 裡詞中間的 `#` 是普通字元;不設的話中文路徑會被拆碎、`#` 之後整段被吃掉,實測)。拆詞丟 ValueError(引號沒配對、結尾單一反斜線)就整行不判。
3. 遇到只由 `;` `&` `|` 組成的詞就切成下一段,每段各自判;空段跳過。
4. 每段開頭逐詞剝掉:`名稱=值` 形狀的環境變數設定;包裝詞與它們的選項——`env`(連同 `-i`、`-u 名稱`、`--`,以及後面接的 `名稱=值`)、`nice`(連同 `-n 數字`、`-數字`)、`time`(連同 `-p`)、`nohup`、`exec`、`command`(連同 `-p`);兩種可以交錯出現,剝到第一個不是這些的詞為止。剝完是空段就跳過。
5. 段首是 `sh`、`bash`、`zsh` 且下一個詞是 `-c`、再下一個詞存在時,對那個詞遞迴套同一張表(只遞迴一層;第二層以下不判)。`-c` 後面沒有詞就整段不判。
6. **看不到完整參數的段**:段裡有任一詞以 `@` 開頭(detekt 會把 `@檔名` 展開成檔裡的參數,實測)、或含 `$`(變數或命令替換;posix 拆詞後 `$(cat` 會留在同一個詞裡,實測)、或含反引號時,這一段不判「缺參數」那兩種提醒(T1、T2),其他照判。

**取值越界**:表上所有「後面那一個詞」(`-jar` 的下一個、`-c` 的下一個、Gradle 帶值選項的下一個)不存在時,視為沒認出、不判,不准丟例外。

**認出是誰**(看段首詞去掉路徑後的檔名):

| 段首 | 條件 | 判成 | 參數從哪開始看 |
|---|---|---|---|
| `detekt`、`detekt-cli` | — | detekt 指令列 | 段首之後 |
| `java` | 有 `-jar`,後面那個詞的檔名以 `detekt-cli` 開頭、`.jar` 結尾 | detekt 指令列 | 那個 jar 之後(之前的 `-cp` 是給 JVM 的,不算) |
| `java` | 某個詞是 `io.gitlab.arturbosch.detekt.cli.Main` | detekt 指令列 | 那個類別名之後 |
| `gradlew`、`gradlew.bat`、`gradle` | 見下方〈Gradle 任務怎麼取〉與〈Gradle 任務名怎麼分〉 | — | — |
| 其他(含段首檔名剛好叫 detekt 但在專案自己的資料夾裡,例如 `./scripts/detekt`——這種仍判成 detekt 指令列,見天花板 3) | — | 不是 detekt,不判 | — |

**Gradle 任務怎麼取**:段首之後的詞逐一看。以 `-` 開頭的是選項:選項本身含 `=` 就只算一個詞;是下列「帶值選項」且不含 `=` 時,連下一個詞一起跳過(依據 Gradle 命令列說明):`-x` `--exclude-task` `-p` `--project-dir` `-b` `--build-file` `-c` `--settings-file` `-g` `--gradle-user-home` `-I` `--init-script` `-D` `--system-prop` `-P` `--project-prop` `--include-build` `-M` `--write-verification-metadata` `-F` `--dependency-verification` `--priority` `--console` `--warning-mode`。其餘不以 `-` 開頭的詞是任務,取最後一個 `:` 之後的名字。所以 `-x detekt`、`-p detekt` 裡的 detekt 不算任務。

**Gradle 任務名怎麼分**(由上往下,第一個符合的算數):

| 順序 | 名字 | 判成 |
|---|---|---|
| 1 | 以 `detektBaseline`、`detektProjectBaseline`、`detektGenerateConfig` 開頭 | 不是跑檢查的任務,不判(外掛的 `detektBaseline<變體>` 也在這裡) |
| 2 | 恰好是 `detekt` | Gradle 沒型別任務 |
| 3 | `detektMain`、`detektTest`,或 `detekt` 開頭且以 `Debug`、`Release`、`UnitTest`、`AndroidTest` 結尾(外掛依建置變體自動產生的任務) | Gradle 有型別任務 |
| 4 | 其他 `detekt` 開頭(例如自訂的 `detektAll`) | Gradle 認不得的任務 |
| 5 | 不是 `detekt` 開頭 | 不判 |

**判出來之後印什麼**(一條命令可以同時中好幾種;同一條命令同一種只印一次):

| 代號 | 條件 | 提醒在講什麼 |
|---|---|---|
| T1 | detekt 指令列,參數裡沒有獨立的 `--classpath` 或 `-cp` 詞(看不到完整參數的段不判) | 要型別資訊的規則(列出用詞那幾條的名字)不會跑,也不會報錯;推送前只跑改到的檔,要型別資訊的規則照 detekt 官方建議放在 CI 的 Gradle 型別解析任務(`detekt<變體>`)加基準線擋,範本見 linter 目錄;另外 Kotlin 標準庫 2.2 以上時,吞取消訊號那條補了也不響(detekt 1.23.8 限制)(2026-11-06 [[Projects/Android的detekt推送前真的擋_計劃]] 改) |
| T2 | detekt 指令列,有 classpath、沒有獨立的 `--jdk-home` 詞(看不到完整參數的段不判) | SleepInsteadOfDelay 這類要 JDK 型別的規則不會跑 |
| T3 | detekt 指令列,有詞是「detekt 參數表裡任一個長或短參數名,緊接 `=`」(例 `--classpath=`、`-cp=`、`--input=`、`-i=`) | detekt 1.23.8 不收等號寫法,整條會拒跑、不產結果;改成空白分隔 |
| G1 | Gradle 沒型別任務 | 純 `detekt` 任務沒有型別解析,同 T1 那批規則不會跑;要型別改用 `detekt<變體>` 任務 |
| G2 | Gradle 認不得的任務 | 判不出這個任務有沒有設 classpath;自訂任務沒設的話,同 T1 那批規則不會跑 |
| P1 | 任何 detekt 宣告(指令列或 Gradle),而且整條命令沒有檔案佔位符(`{LINT_FILES}` 與 `{LINT_FILES_CSV}` 都沒有) | 推送前的新增告警檢查對這條只記錄、不擋;detekt 指令列改用 `--input {LINT_FILES_CSV}` |
| P2 | detekt 指令列,而且那一段裡有舊的 `{LINT_FILES}`(只看舊佔位符;逗號佔位符 `{LINT_FILES_CSV}` 不印) | 這次改動有兩支以上檔時,檢查把檔名用空白串起來、detekt 只收逗號分隔,會拒跑,檢查照環境問題放行;改用 `--input {LINT_FILES_CSV}` |
| T4 | 整份宣告裡有任何 detekt 宣告,而專案 `.github/workflows/` 底下(`.yml`/`.yaml`)沒有任何一支提到「有型別任務」的 Gradle 任務名(照〈Gradle 任務名怎麼分〉第 3 列,例 `detektDebug`、`detektMain`;`detektBaseline<變體>` 不算)。一個專案一則、標 `[CI]`;只看字面、不執行(2026-11-06 推送前真的擋那案新增;那案字面叫 T3,但 T3 已被等號寫法用掉) | detekt 預設設定與共用設定都開了要型別資訊的規則,推送前只跑不用型別的,型別規則目前哪裡都沒擋;把 CI 型別檢查範本貼進專案的 CI |

P1 看整條命令(新增告警檢查本來就以整條命令為單位決定跑不跑),P2 看 detekt 那一段(佔位符在別段時展開不影響 detekt)。「有沒有佔位符」不在新函式裡自己比字面:改呼叫新增告警檢查判「這條接不接得住」的既有判斷(抽成一支小函式,由新增告警檢查與本判定共用,放進「只准一處碰佔位符」那條守衛的白名單並寫理由),不另寫第二份。

**提醒文字**:代號對應的文字只放在判定函式旁邊同一張表裡,lint-check 與健檢都從那裡取,不各寫一份。文字不回顯使用者命令的內容,只標「哪個副檔名底下第幾條」(例 `[kt 第 1 條]`),所以不需要清洗外來字串。人讀輸出照專案三段式:發生什麼 → 為什麼在意 → 能做什麼(沒有修法的寫「目前沒有現成修法,見工具鏈文件」)。

**宣告格式壞掉時**:逐項判,頂層不是物件就整份不判;某個值不是清單、清單裡某項不是字串,只跳過那一項,同一份宣告裡其他合法的 detekt 命令照判照印。都不出錯(格式問題由既有的格式檢查報)。宣告不是合法 JSON 時不判(lint-check 照舊回 2)。

## 判定依據(2026-11-04 本機 detekt 1.23.8 實測)

- 參數表(`detekt --help`):`--classpath, -cp`、`--input, -i`、`--jdk-home`、`--jvm-target` 等;沒有等號寫法。
- 吞取消訊號(SuspendFunSwallowedCancellation):stdlib 1.8.20 到 2.1.21 會響,2.2.0 以上(測到 2.4.21)全部不響,協程函式庫 1.8.1 與 1.10.2 結果相同(設計審 r1 正確性席逐版實測,編排者對 2.0.21 與 2.3.21 兩點重現過)。2.2 以上連標準庫的 ForbiddenMethodCall(例 println)都不響,但 Compose 的 collectAsState 照響。推測是 detekt 1.23.8 內建的 Kotlin 編譯器讀不懂較新標準庫。下面「六條都響」是 2.0.21 的結果。
- 探針檔帶 coroutines 與 stdlib 2.0.21:有 classpath 加 `--jdk-home` → 協程六條都響;只有 classpath → 少 SleepInsteadOfDelay;只有 `--jdk-home` → 要型別的全不響;`-cp` 簡寫與長寫同結果;`--classpath=值` → 沒產結果;classpath 指到不存在的檔 → 不報錯,要依賴函式庫型別的不響,只要開了型別解析就會響的兩條(SleepInsteadOfDelay、RedundantSuspendModifier)與不靠型別的照響;classpath 裡沒加 `./` 的相對路徑放在第一個以外的位置時,那個 jar 會被靜默忽略(設計審 r1 接手席實測)。
- 效能檔:沒型別只響 ForEachOnRange;帶 stdlib 再多響 CouldBeSequence、ArrayPrimitive(不需要 JDK)。
- 等號寫法:`--input=`、`-i=`、`--classpath=`、`--config=`、`--report=`、`--jvm-target=` 全部 rc=1 不產結果。
- 參數檔:`detekt @檔名` 會把檔裡的內容當參數展開。
- 設定疊加:兩份設定要用逗號合成一個 `--config a.yml,b.yml`(分開寫兩次 `--config` 會拒跑);清單類欄位(例 ForbiddenMethodCall 的 methods)後面那份整份蓋掉前面那份、不合併、不警告。
- ForbiddenMethodCall 的方法要寫完整名稱(`androidx.compose.runtime.collectAsState` 會響;只寫 `collectAsState` 不報錯也不響),而且要放在 `style:` 規則集底下(放錯規則集 detekt 整次拒跑)。
- 多檔:`--input a.kt b.kt` → rc=1 拒跑;`--input a.kt,b.kt` → 有結果。

## 範圍

- 判定表寫成一支函式,lint-check 與健檢 F 段共用(不留兩份)。
  - lint-check:人讀輸出在既有結果之後印提醒,健康與有問題兩條分支都印;`--json` 時不另外印字,有宣告且讀得出來時輸出物件一律帶 `advisories` 欄(字串清單,每條是「`[副檔名 第 N 條] 代號:一句`」,沒提醒就是空清單);沒宣告那條路徑的輸出照舊、不加欄位;退出碼照舊。
  - 健檢 F 段:既有分支之後,宣告讀得出來(合法 JSON)就判;所有提醒合成**一次**提醒函式呼叫(帶空清單,逐條放進建議文字,最多列 20 條、超過的寫「另 N 條」),不計入問題、`--ci` 與 `--strict` 退出碼不變;結尾「提醒段數」多算一段,這是預期。
  - 健檢 F 段既有那句「推送前的新增告警閘會真的執行它們」改成只對含檔案佔位符的命令成立的說法(例:「含檔案佔位符的命令,推送前的新增告警檢查會真的執行;不含的只記錄」),不然會跟 P1 前後打架。
- 共用 detekt 設定新增兩段:`coroutines:` 底下 SuspendFunWithCoroutineScopeReceiver 設成開;`style:` 底下新增 ForbiddenMethodCall 設成開、方法清單只放完整名稱 `androidx.compose.runtime.collectAsState`(原本共用設定沒寫這條,detekt 預設關)。設定開頭的用法說明照判定表講實話;SuspendFunSwallowedCancellation 旁邊那行註解改成「runCatching 裡呼叫 suspend」。
- 共用設定加一道自動檢查(新測試):設定檔裡每條規則都要在一份釘住的「detekt 1.23.8 規則名 → 規則集」對照裡、而且放在對的規則集底下,ForbiddenMethodCall 的每個方法名都要含點(完整名稱);對照取自 `detekt --generate-config` 的輸出,釘進測試資料、附產生指令與版本。本機有 detekt 時另跑一次真的設定驗證(沒有就只跑靜態那半,並在輸出講明沒跑真的)。
- 知識同步(逐處列出,做完逐處勾;下列每處講「已開」都要同時講清楚要不要型別資訊、推送時擋不擋):
  - [[Systems/效能檢核目錄]]:協程 scope 那列(GlobalScope 不要型別,照舊有效;自建 scope 沒跟生命週期仍是人判)、結構化並發那列(SuspendFunSwallowedCancellation 改成「runCatching 裡呼叫 suspend,要型別資訊,Kotlin 2.2 以上不響」)、大集合那列(CouldBeSequence 要型別資訊)、primitive array 那列拆成兩句(ArrayPrimitive 要型別、ForEachOnRange 不用);四列都加「推送時不擋」。
  - [[Systems/linter精選目錄]]:Kotlin 那行 KEY(「開預設關的三條」改成現在的五條,補「有開≠有跑」)、工具分類表裡說 detekt「跑得動」那句、detekt 標準接法那一段(「三條」「裸跑時這三條全不生效」改成判定表 T1 的實話,「接完跑冒煙驗真跑得動」補一句冒煙只驗有沒有產出結果、不驗規則有沒有響),並寫明自有設定要用逗號跟共用設定合成一個 `--config`、清單類欄位後面蓋前面。
  - [[Systems/pitfalls-lint-adapter]]:講 detekt「本來就跑得起來」那句補「但推送時只記錄」。
  - [[Systems/lint-declaration-health]]:FLOW 行與冒煙層描述補 F 段多了 detekt 判定那一段。
  - kotlin-idioms 慣例文件(消費專案讀得到的是這份,所以「型別資訊」的定義與取得方式要寫在它自己裡面,不能只指圖譜):
    - 開頭機檢欄說明補「要型別資訊」的意思與取得方式。
    - R6、R9、R10、R12 的 SleepInsteadOfDelay 與 RedundantSuspendModifier、R13 的機檢欄標「要型別資訊」;R11(GlobalCoroutineUsage)標「不要型別資訊」。
    - R10:吞取消訊號只抓「runCatching 裡呼叫 suspend」、R10 壞例那種 `try { } catch (e: Exception)` 它不抓(detekt 1.23.8 官方規則頁);Kotlin 標準庫 2.2 以上不響。
    - R12:CoroutineLaunchedInTestWithoutRunTest 標「detekt 2.0 才有,1.23.8 寫進設定會整個拒跑」;runBlocking 不全面禁(理由見不做);「寫進 detekt 設定就好」那句改掉。
    - R13:ForbiddenMethodCall 要寫完整名稱、放 `style:`。
    - 機檢接線段:拿掉 1.23.8 不存在的規則;寫明設定疊加用逗號合成一個 `--config`、清單後面蓋前面。
    - 開頭核對邊界:寫成「已核對(2026-11-04,detekt 1.23.8):協程與效能兩組;未核對:其餘(含 R16 的 compose-rules 條數)」,逾期的 2026-10-25 那行回頭條件改成新日期或結案。
  - [[Projects/Android協程與API協同機械審_調研]]:現況表那幾列、把 `--jvm-target` 當必要參數的兩處、「共用設定還沒開的只剩…那條」那句。
- 每處新寫的「推送時不擋」都在同一篇加一行 `REVISIT:[when-status:Projects/Android的detekt推送前真的擋_計劃=done][by:2027-03-01] 推送前真的擋落地了,把這篇「推送時不擋」的說法改掉`(kotlin-idioms 也加,寫法照它既有那行)。

**不做**:不做冒煙探針(改到推送前真的擋那案再設計);不改新增告警檢查的判定與行為(只把它既有的「這條接不接得住」判斷原樣抽成共用小函式,呼叫處行為不變);不碰任何消費專案的宣告;不加 runBlocking 全面禁用(OkHttp Authenticator 這類同步介面裡橋接 suspend 是正當用法,ForbiddenMethodCall 分不出在不在 suspend 裡);判定表外的寫法(Makefile 目標、npx、檔名不叫 detekt 的自寫腳本包一層)不判。

## 實務隱患

- 提醒對 Android 消費專案目前沒有出口(T1、P1 都修不了),每次健檢都會出現。這是本案要的「講實話」,出口在推送前真的擋那案;提醒文字要寫明「目前沒有現成修法」,不讓人白找。
- classpath 指到不存在的檔、或相對路徑放錯位置時,判定表判成有型別(T1 不出),實際要依賴型別的規則不跑——只看字面抓不到,寫進天花板。
- 新判定要知道「這條命令有沒有檔案佔位符」,而「只准一處碰佔位符」那條守衛測試會擋名單外的函式;做法是把新增告警檢查既有的那個判斷抽成一支共用小函式、加進守衛白名單並寫理由。白名單在測試檔裡,改測試檔要先經使用者簽名。
- 同一個「沒有修法」的提醒每次健檢都出現,會被當成噪音而忽略;為此提醒合成一段、最多列 20 條;推送前真的擋那案落地時拿掉 P1、P2 並改文件(REVISIT),detekt 本身也會在缺型別時警告之後整張表拿掉(RETIRE-IF)。
- 已排除:守衛面:不改任何檢查的判定與退出碼;動到的是守衛測試白名單、共用設定、新測試與健檢一句訊息,所以照走設計審
- 共用設定補開的兩條,在消費專案補上型別資訊之前不會響;補上之後,只要推送前真的擋那案還沒落地,也只記錄不擋。
- 宣告格式壞掉時新判斷要自己防型別,健檢 F 段沒有包例外,一出錯整支健檢就斷。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只印本機輸出,不呼叫外部服務
- 已排除:不可逆:只加提醒與改文件,退提交即回原狀

## 驗收條款

- [S1] 當判定表函式拿到上表每一種段首寫法、每一種參數組合(含 java -jar 之前的 -cp、Gradle 的 detektMain、:app:detekt、detektBaselineDebug、-x detekt、-p detekt、sh -c 包一層、&& 串兩段、換行與續行、引號沒配對、`@參數檔`、`$VAR`、沒加引號的 `$(…)`、中文路徑、詞中 `#`、包裝詞帶選項)時,應 回傳表上對應的提醒代號集合;表外寫法、格式壞掉的項目、以及取值越界的退化寫法(`java -jar` 結尾、`sh -c` 結尾、只有環境變數、只有 `env`、開頭或結尾是分隔符、空字串)應 回空集合且不丟例外 [test:t_lint_detekt_advice_table]
- [S2] 當 `.lumos/lint.json` 有 detekt 宣告時,`lumos lint-check` 應 在健康與有問題兩條分支都印出對應提醒且退出碼與沒有提醒時相同;加 `--json` 時 應 只輸出一個 JSON 物件、提醒放在 `advisories` 欄 [test:t_lintcheck_detekt_advice_output]
- [S3] 當 `.lumos/lint.json` 有 detekt 宣告時,`lumos doctor` 的 F 段 應 印同一批提醒合成的一段、而且不再印「會真的執行它們」那句不分佔位符的話,`--ci` 與 `--strict` 的退出碼與問題數 應 跟拿掉這批提醒時一樣;宣告是頂層清單、值不是清單、清單裡有數字時 應 不出錯 [test:t_doctor_lint_detekt_advice]
- [S4] 當共用設定裡任一條規則不在釘住的 detekt 1.23.8 規則對照裡、放錯規則集、或 ForbiddenMethodCall 的方法名不含點時,共用設定檢查 應 失敗 [test:t_detekt_shared_config_valid]
- [S5] 當用 detekt 1.23.8 搭共用設定、帶 coroutines 與 stdlib 2.0.21 的 classpath(絕對路徑)與 `--jdk-home` 跑一支含 `suspend fun CoroutineScope.g()` 與 `collectAsState()` 的檔(classpath 另加 Compose runtime 的 classes.jar)時,設定驗證應通過、兩條各自響 [manual:照〈判定依據〉的做法實跑一次,把指令與輸出貼進實作紀錄]
- [S6] 當知識同步清單逐處改完時,清單裡每一處 應 不再出現沒講清楚型別資訊與推送擋不擋的「已開」「預設開」「還沒開」「三條」「跑得動」 [manual:對清單裡每支檔 grep 這五組字,逐行確認旁邊有要不要型別資訊與推送擋不擋的說明,結果貼進實作紀錄]

## 回退

退回本案的提交即可(程式、測試、白名單、對照資料、共用設定、文件在同一個提交裡,一起退,測試不會因為只退一半而紅):lint-check 與健檢不再印 detekt 提醒、`--json` 少一個欄位(讀它的程式要容許欄位不存在);健檢 F 段那句訊息回到舊說法;抽出的共用小函式併回新增告警檢查、白名單少一個名字;共用設定檢查測試與對照資料一起拿掉;共用設定拿掉新增的兩段、回到 detekt 預設(兩條都關);文件回到舊說法。沒有寫入任何消費專案的檔。

## 天花板

1. 只看指令字面:classpath 指到不存在或過期的檔、相對路徑放錯位置、`--input` 指錯目錄、消費專案自己的設定關掉規則或用清單蓋掉共用設定,判定表都看不出來。
2. 表外寫法不判,不代表那些寫法沒問題;看不到完整參數的段(參數檔、變數、命令替換)不判缺參數。
3. 段首檔名叫 detekt 的自寫腳本會被當成 detekt 指令列,腳本自己補了 classpath 時 T1 會誤報;寫法上建議腳本不要取這個名字。
4. Kotlin 標準庫 2.2 以上時,吞取消訊號那條與標準庫的 ForbiddenMethodCall 補了型別資訊也不響(detekt 1.23.8 限制),判定表不另外提醒,只寫在 T1 的文字與文件裡。

REVISIT:2027-03-01 查 detekt 2.0 出正式版沒;出了就重跑〈判定依據〉的實測,確認吞取消訊號那條在新版 Kotlin 標準庫下恢復,並評估補開 2.0 才有的 SuspendFunInFinallySection 與 CoroutineLaunchedInTestWithoutRunTest。
- 2026-11-08 [[Projects/Android的detekt推送前真的擋_計劃]] 做完後同步過:協程調研的現況表與 [[Systems/效能檢核目錄]] 那幾列改成「不用型別的推送前擋、要型別的由消費專案 CI 擋」;判定表的 P1、P2 沒拿掉——命令沒寫檔案佔位符、或用空白分隔的 `{LINT_FILES}` 時推送前照樣擋不住,程式照舊印這兩則提醒,拿掉反而跟程式對不上。

## 審計修正紀錄

- r1(2026-11-04,四席:正確性、邊界、接手、架構對齊,同一家模型):報 29 條,blocking 8 條;依根因分七組全折——①佔位符守衛白名單(改共用小函式進白名單)②看不到完整參數的段不判缺參數③shlex 設定寫死與換行、包裝詞選項、取值越界④Gradle 帶值選項與任務名優先序⑤知識同步漏列與規則歸類錯、健檢舊訊息打架、會過期的話搬回頭條件⑥共用設定加自動檢查、方法要全名⑦事實修正(版本邊界 2.2.0、只給 JDK 不響、不存在的 classpath 部分照響、相對路徑、設定疊加)。卷證:governance/review-reports 底下 Android的detekt規則說實話 資料夾。

## 合約候選(設計審過了之後列;候選不等於已標,蓋章照 guard 流程與「不確定不標」)

- detekt 提醒只是提醒:lint-check 的退出碼與健檢的問題數、`--ci`/`--strict` 退出碼,不因為有沒有 detekt 提醒而改變(對應 S2、S3)。
- 共用 detekt 設定只准出現 detekt 正式版存在、放在正確規則集底下的規則,ForbiddenMethodCall 的方法要寫全名——違反時所有引用它的消費專案 detekt 會一起拒跑或規則靜默失效(對應 S4)。

## 實作紀錄

- 2026-11-04:先寫 S1–S4 四支測試、各自確認紅(判定函式不存在、lint-check 與健檢沒印、共用設定少兩條),再實作:`_lint_gate_covers` 共用小函式(新增告警閘與風險分級原本各自寫的判斷改呼叫它,守衛白名單 6 支變 5 支,範圍更窄)、判定表一組函式與提醒文字表、lint-check 兩條分支與 `--json` 的 `advisories`、健檢 F 段合成一段的提醒與改寫「會真的執行它們」那句、共用設定補兩段。翻紅:十道檢查逐一改壞(看不到參數照判、P2 看整條、Gradle 帶值選項不跳、副檔名原樣回顯、健檢提醒算問題、健檢只在健康分支判、有問題分支不印、`--json` 外多印字、檢查器不看全名、包裝詞選項不剝),對應測試各自紅。相關既有測試(佔位符守衛、lint-check、格式校驗、健檢 F 段)全綠。
- S1 條款字面與判定表對齊:原寫「開頭或結尾是分隔符…應回空集合」,但 `detekt &&` 的 detekt 那段照表就該判 T1、P1;測試照判定表寫(只有分隔符的才是空集合),條款文字照此理解。
- S5 手動驗收(2026-11-04):`detekt --input <含 suspend fun CoroutineScope.g() 與 collectAsState() 的檔> --classpath <kotlinx-coroutines-core-jvm-1.10.2、kotlin-stdlib-2.0.21、compose runtime 1.9.3 的 classes.jar、junit 4.13.2,全絕對路徑> --jdk-home <JBR 17> --report sarif:… --build-upon-default-config --config <共用設定>` → rc=2(有發現)、沒有設定錯誤;命中 `detekt.coroutines.SuspendFunWithCoroutineScopeReceiver`(第 10 行)與 `detekt.style.ForbiddenMethodCall`(第 14 行)。
- S6 手動驗收(2026-11-04):對清單六支檔 grep「已開|預設開|還沒開|三條|跑得動」並篩 detekt 相關行,逐行確認旁邊有型別資訊與推送擋不擋的說明;kotlin-idioms 在開頭機檢欄說明統一講推送不擋,逐條機檢欄講型別資訊。效能檢核目錄 lambda 穩定性那列的「預設開」是 Compose 編譯器設定,與 detekt 無關。
- 2026-11-04 推送前預檢:新增告警檢查抓到這次帶進的 3 條(健檢兩處用 + 串清單、兩支判定函式複雜度 11 與 16 超過 10)。串清單改展開寫法;函式照原樣拆:包裝詞選項跳過抽成一支、detekt 指令列認參數與配代號各抽一支,行為不變;四支新測試與佔位符守衛重跑全綠。不放行。
