---
type: project
status: doing
created: 2026-11-04
updated: 2026-11-04
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/lint-declaration-health
  - Systems/linter精選目錄
related:
  - "[[Projects/detekt協程規則真的在跑_計劃]]"
  - "[[Issues/推送閘對Android的detekt只記錄不擋]]"
  - "[[Projects/Android的detekt推送前真的擋_計劃]]"
  - "[[Projects/Android協程與API協同機械審_調研]]"
  - "[[Systems/lint-declaration-health]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/效能檢核目錄]]"
---
# Android的detekt規則說實話_計劃

> 白話:Android 專案的 detekt 現在有兩件事跟大家以為的不一樣:①共用設定開的協程規則,照標準接法跑多半沒在跑(要型別資訊,沒給就安靜跳過);②推送前的新增告警檢查對 detekt 從來不擋。這案不修這兩件事(修法在 [[Projects/Android的detekt推送前真的擋_計劃]]),只做到「工具自己講實話」:lint-check 與健檢看到 detekt 宣告時,照一張窮舉的判定表印出它實際會怎樣;文件與圖譜裡「已開」的說法全部改成「已開,但要型別資訊才跑、推送時不擋」。順手補開兩條規則、改掉文件裡 detekt 1.23.8 不存在的規則名。出身:已作廢的 [[Projects/detekt協程規則真的在跑_計劃]] 第一輪設計審。

PRIOR-ART: ①提醒形狀用健檢 F 段既有「有 eslint 設定但沒接」那則的同一個形狀(提醒函式帶空清單:不計問題、不讓 CI 變紅),在 F 段新加一個判斷。②指令拆詞用 Python 標準庫 shlex(posix 模式、標點拆開),不自寫引號解析;本 repo 拆掛鉤命令時用過 shlex 拆詞,lint 命令本身照舊交給 shell 執行,這裡只拆來判讀、不改命令。③判定依據全部來自 detekt 1.23.8 自己的說明(`detekt --help` 的參數表)與 2026-11-04 本機實測(見〈判定依據〉),detekt 官方型別解析文件明寫沒有型別解析時要型別的規則「不會跑」。不新建機制、不加設定鍵。
RETIRE-IF: [[Projects/Android的detekt推送前真的擋_計劃]] 落地、而且 detekt 本身在缺型別資訊時會警告——那時提醒裡「不擋」與「沒在跑」兩句都不再成立,整張判定表改寫或拿掉。

## 用詞

- **型別資訊**:detekt 指令列的 `--classpath`(簡寫 `-cp`)與 `--jdk-home`。前者給依賴的型別,後者給 JDK 的型別(Thread.sleep 這類)。`--jvm-target` 實測不影響規則響不響,不算進來。
- **共用設定**:本 repo 分發的 detekt 設定檔(configs 底下 detekt 資料夾的 android.yml,家是 [[Systems/linter精選目錄]])。消費專案的宣告用絕對路徑指向安裝在本機的這份檔,所以這裡改了,消費專案下次更新工具鏈就跟著變,不用改它們的檔。
- **要型別資訊的規則**(detekt 預設開、共用設定開、或本案補開的,實測確認):InjectDispatcher、SuspendFunSwallowedCancellation、SuspendFunWithFlowReturnType、SuspendFunWithCoroutineScopeReceiver、RedundantSuspendModifier、SleepInsteadOfDelay(只要 JDK)、CouldBeSequence、ArrayPrimitive、ForbiddenMethodCall。不用型別資訊就會響的:GlobalCoroutineUsage、ForEachOnRange。
- **detekt 宣告**:`.lumos/lint.json` 裡任一副檔名底下、照下面判定表認得出是 detekt 的那條命令。
- **新增告警檢查**:推送前在合併基準與這次改動上各跑一次 linter、只擋新增告警的那道檢查,家是 [[Systems/pitfalls-lint-adapter]]。

## 判定表(窮舉;表外的寫法一律不判、不提醒)

**拆詞**:每條命令用 shlex 以 posix 模式、標點拆開切成詞;拆詞失敗(引號沒配對)就整條不判。遇到只由 `;` `&` `|` 組成的詞就切成下一段,每段各自判。每段先去掉開頭的環境變數設定(`名稱=值` 形狀的詞)與包裝詞 `env`、`exec`、`time`、`nice`、`nohup`、`command`;段首是 `sh`、`bash`、`zsh` 且帶 `-c` 時,對 `-c` 後面那一個詞遞迴套同一張表(最多一層)。含 `$(`、反引號命令替換的段不判。

**認出是誰**(看段首詞去掉路徑後的檔名):

| 段首 | 條件 | 判成 | 參數從哪開始看 |
|---|---|---|---|
| `detekt`、`detekt-cli` | — | detekt 指令列 | 段首之後 |
| `java` | 有 `-jar`,後面那個詞的檔名以 `detekt-cli` 開頭、`.jar` 結尾 | detekt 指令列 | 那個 jar 之後(之前的 `-cp` 是給 JVM 的,不算) |
| `java` | 某個詞是 `io.gitlab.arturbosch.detekt.cli.Main` | detekt 指令列 | 那個類別名之後 |
| `gradlew`、`gradlew.bat`、`gradle` | 某個不以 `-` 開頭的詞,取最後一個 `:` 之後的名字恰好是 `detekt` | Gradle 沒型別任務 | — |
| 同上 | 名字是 `detektMain`、`detektTest`,或 `detekt` 開頭且以 `Debug`、`Release`、`UnitTest`、`AndroidTest` 結尾(外掛依建置變體自動產生的任務) | Gradle 有型別任務 | — |
| 同上 | 名字以 `detektBaseline`、`detektProjectBaseline`、`detektGenerateConfig` 開頭 | 不是跑檢查的任務,不判 | — |
| 同上 | 其他 `detekt` 開頭的名字(例如自訂的 `detektAll`) | Gradle 認不得的任務 | — |
| 其他 | — | 不是 detekt,不判 | — |

**判出來之後印什麼**(一條命令可以同時中好幾種;同一條命令同一種只印一次):

| 代號 | 條件 | 提醒在講什麼 |
|---|---|---|
| T1 | detekt 指令列,參數裡沒有獨立的 `--classpath` 或 `-cp` 詞 | 要型別資訊的規則(列出用詞那幾條的名字)不會跑,也不會報錯;補法是帶 `--classpath` 與 `--jdk-home`;Android 專案的依賴沒有穩定路徑,目前沒有現成取法 |
| T2 | detekt 指令列,有 classpath、沒有獨立的 `--jdk-home` 詞 | SleepInsteadOfDelay 這類要 JDK 型別的規則不會跑 |
| T3 | detekt 指令列,有詞是「detekt 參數表裡任一個長或短參數名,緊接 `=`」(例 `--classpath=`、`-cp=`、`--input=`、`-i=`) | detekt 1.23.8 不收等號寫法,整條會拒跑、不產結果;改成空白分隔 |
| G1 | Gradle 沒型別任務 | 純 `detekt` 任務沒有型別解析,同 T1 那批規則不會跑;要型別改用 `detekt<變體>` 任務 |
| G2 | Gradle 認不得的任務 | 判不出這個任務有沒有設 classpath;自訂任務沒設的話,同 T1 那批規則不會跑 |
| P1 | 任何 detekt 宣告(指令列或 Gradle),整條命令沒有 `{LINT_FILES}` | 推送前的新增告警檢查對這條只記錄、不擋 |
| P2 | detekt 指令列,整條命令有 `{LINT_FILES}` | 這次改動有兩支以上檔時,檢查把檔名用空白串起來、detekt 只收逗號分隔,會拒跑,檢查照環境問題放行 |

**宣告格式壞掉時**:逐項判,頂層不是物件就整份不判;某個值不是清單、清單裡某項不是字串,只跳過那一項,同一份宣告裡其他合法的 detekt 命令照判照印。都不出錯(格式問題由既有的格式檢查報)。宣告不是合法 JSON 時不判(lint-check 照舊回 2)。

## 判定依據(2026-11-04 本機 detekt 1.23.8 實測)

- 參數表(`detekt --help`):`--classpath, -cp`、`--input, -i`、`--jdk-home`、`--jvm-target` 等;沒有等號寫法。
- 吞取消訊號(SuspendFunSwallowedCancellation)只在 stdlib 2.0.21 下響,換 2.3.21 不響,其他版本沒逐一測;推測是 detekt 1.23.8 內建的 Kotlin 編譯器讀不懂較新標準庫。下面「六條都響」是 2.0.21 的結果。
- 探針檔帶 coroutines 與 stdlib 2.0.21:有 classpath 加 `--jdk-home` → 協程六條都響;只有 classpath → 少 SleepInsteadOfDelay;`-cp` 簡寫與長寫同結果;`--classpath=值` → 沒產結果;classpath 指到不存在的檔 → 不報錯、要型別的規則全不響。
- 效能檔:沒型別只響 ForEachOnRange;帶 stdlib 與 JDK 再多響 CouldBeSequence、ArrayPrimitive。
- 多檔:`--input a.kt b.kt` → rc=1 拒跑;`--input a.kt,b.kt` → 有結果。

## 範圍

- 判定表寫成一支函式,lint-check 與健檢 F 段共用(不留兩份)。
  - lint-check:人讀輸出在既有結果之後印提醒,健康與有問題兩條分支都印;`--json` 時不另外印字,有宣告且讀得出來時輸出物件一律帶 `advisories` 欄(字串清單,沒提醒就是空清單);沒宣告那條路徑的輸出照舊、不加欄位;退出碼照舊。
  - 健檢 F 段:既有分支之後,宣告讀得出來(合法 JSON)就判;有提醒時印一段,提醒函式帶空清單,不計入問題、`--ci` 退出碼不變(結尾「提醒段數」會多算一段,這是預期)。
- 共用 detekt 設定新增兩段:SuspendFunWithCoroutineScopeReceiver 設成開;ForbiddenMethodCall 原本沒寫在共用設定裡(detekt 預設關),新增成開、方法清單只放 collectAsState。設定開頭的用法說明照判定表講實話。
- 知識同步(逐處列出,做完逐處勾):
  - [[Systems/效能檢核目錄]] 協程 scope、結構化並發、大集合、primitive array 四列:「共用 config 已開」改成「已開,要型別資訊才跑;推送時不擋」;SuspendFunSwallowedCancellation 的描述改成「runCatching 裡呼叫 suspend 函式」。
  - [[Systems/linter精選目錄]] Kotlin 那行 KEY 與 detekt 標準接法樣板:補「有開≠有跑」與判定表的 T1、P1。
  - [[Systems/lint-declaration-health]]:補 F 段多了 detekt 判定那一段。
  - kotlin-idioms 慣例文件:R6、R9、R10、R11、R12、R13 的機檢欄標「要型別資訊」;R12 的 CoroutineLaunchedInTestWithoutRunTest 標「detekt 2.0 才有,1.23.8 寫進設定會整個拒跑」;runBlocking 不全面禁(理由見不做);R10 加吞取消訊號的版本限制,並註明 SuspendFunSwallowedCancellation 只抓「runCatching 裡呼叫 suspend」,R10 壞例那種 `try { } catch (e: Exception)` 它不抓(世界解查證,detekt 1.23.8 官方規則頁);機檢接線段照改;開頭的核對邊界改成「2026-11-04 用 detekt 1.23.8 核對過協程與效能兩組」。
  - [[Projects/Android協程與API協同機械審_調研]] 現況表那幾列。

**不做**:不做冒煙探針(改到推送前真的擋那案再設計);不改新增告警檢查;不碰任何消費專案的宣告;不加 runBlocking 全面禁用(OkHttp Authenticator 這類同步介面裡橋接 suspend 是正當用法,ForbiddenMethodCall 分不出在不在 suspend 裡);判定表外的寫法(Makefile 目標、npx、自寫腳本包一層)不判。

## 實務隱患

- 提醒對 Android 消費專案目前沒有出口(T1、P1 都修不了),每次健檢都會出現。這是本案要的「講實話」,出口在推送前真的擋那案;提醒文字要寫明「目前沒有現成修法」,不讓人白找。
- classpath 指到不存在的檔時,判定表判成有型別(T1 不出),實際規則全不跑——只看字面抓不到,寫進天花板。
- 共用設定補開的兩條,在消費專案補上型別資訊之前不會響;補上之後,只要推送前真的擋那案還沒落地,也只記錄不擋。
- 宣告格式壞掉時新判斷要自己防型別,健檢 F 段沒有包例外,一出錯整支健檢就斷。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只印本機輸出,不呼叫外部服務
- 已排除:不可逆:只加提醒與改文件,退提交即回原狀

## 驗收條款

- [S1] 當判定表函式拿到上表每一種段首寫法、每一種參數組合(含 java -jar 之前的 -cp、Gradle 的 detektMain 與 :app:detekt、sh -c 包一層、&& 串兩段、引號沒配對、命令替換)時,應 回傳表上對應的提醒代號集合,表外寫法與格式壞掉的項目 應 回空集合且不丟例外 [test:t_lint_detekt_advice_table]
- [S2] 當 `.lumos/lint.json` 有 detekt 宣告時,`lumos lint-check` 應 在健康與有問題兩條分支都印出對應提醒且退出碼與沒有提醒時相同;加 `--json` 時 應 只輸出一個 JSON 物件、提醒放在 `advisories` 欄 [test:t_lintcheck_detekt_advice_output]
- [S3] 當 `.lumos/lint.json` 有 detekt 宣告時,`lumos doctor` 的 F 段 應 印同一批提醒,`--ci` 的退出碼與問題數 應 跟拿掉這批提醒時一樣;宣告是頂層清單、值不是清單、清單裡有數字時 應 不出錯 [test:t_doctor_lint_detekt_advice]
- [S4] 當用 detekt 1.23.8 搭共用設定、帶 coroutines 與 stdlib 2.0.21 的 classpath 與 `--jdk-home` 跑一支含 `suspend fun CoroutineScope.g()` 與 `collectAsState()` 的檔(classpath 另加 Compose runtime 的 classes.jar)時,設定驗證應通過、兩條各自響 [manual:照〈判定依據〉的做法實跑一次,把指令與輸出貼進實作紀錄]
- [S5] 當知識同步清單逐處改完時,清單裡每一處 應 不再出現沒講要型別資訊的「已開」或「預設開」 [manual:對清單裡每支檔 grep「已開」與「預設開」,逐行確認旁邊有要型別資訊或不擋的說明]

## 回退

退回本案的提交即可:lint-check 與健檢不再印 detekt 提醒、`--json` 少一個欄位(讀它的程式要容許欄位不存在);共用設定拿掉新增的兩段、回到 detekt 預設(兩條都關);文件回到舊說法。沒有寫入任何消費專案的檔。

## 天花板

1. 只看指令字面:classpath 指到不存在或過期的檔、`--input` 指錯目錄、consumer 自己的設定關掉規則,判定表都看不出來。
2. 表外寫法不判,不代表那些寫法沒問題。

REVISIT:2027-03-01 查 detekt 2.0 出正式版沒;出了就重跑〈判定依據〉的實測,確認吞取消訊號那條在新版 Kotlin 標準庫下恢復,並評估補開 2.0 才有的 SuspendFunInFinallySection 與 CoroutineLaunchedInTestWithoutRunTest。
