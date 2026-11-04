severity: major

審查範圍:逐節讀完整份 spec,對照 `scripts/lumos`、`scripts/test_lumos.py` 與本機 detekt 1.23.8 實跑。實驗放在 `/tmp/lumos-seat-work/detekt協程規則真的在跑/正確性-sonnet/p/`,由編排者收貨後刪。

## Findings

### F1 探針比對的規則 ID 形狀 spec 沒定義,照字面寫會讓每次真跑都判成「五條全缺」
- spec 段落:驗收條款 S1、範圍第一點。
- 問題:S1 與用詞只寫裸名 `GlobalCoroutineUsage` 等,沒說怎麼跟 SARIF 的 `ruleId` 比對。detekt 1.23.8 實際輸出是 `detekt.coroutines.GlobalCoroutineUsage` 這種「detekt.規則集.規則名」。照字面用 `==` 或 `in {五個裸名}` 比對,真 detekt 下永遠比不中。
  - 結果是五條全被判缺,smoke 一律 rc1。
  - 用假 detekt 腳本吐裸名 `ruleId` 的測試 `t_lintcheck_smoke_detekt_probe` 會照樣綠,所以測試抓不到。
- 重現:帶齊型別參數跑探針,SARIF 裡 `ruleId` 全是 `detekt.coroutines.*`,沒有一個是裸名。
- 佐證:
  - file: `scripts/lumos:38242` `_lint_run_and_parse` 把 `ruleId` 原樣放進 claim 的 `rule`,沒有剝前綴。
  - 實跑 `detekt --input src --report sarif:o2.sarif ...`,規則集合為 `['detekt.coroutines.GlobalCoroutineUsage','detekt.coroutines.InjectDispatcher','detekt.coroutines.SleepInsteadOfDelay','detekt.coroutines.SuspendFunWithCoroutineScopeReceiver','detekt.coroutines.SuspendFunWithFlowReturnType', ...]`。
- 引句:「探針結果缺 GlobalCoroutineUsage、InjectDispatcher、SleepInsteadOfDelay、SuspendFunWithFlowReturnType、SuspendFunWithCoroutineScopeReceiver 任一條時」
severity: major
- blocking: 是。比對規則是判定邏輯本體,spec 沒定義,照字面實作必錯。

### F2 探針那次 detekt 根本沒產出 SARIF 時,要記成問題還是提醒,spec 沒定義
- spec 段落:S1–S3、實務隱患第三點。
- 問題:spec 只定義兩種結果:規則缺 → 問題 rc1;沒有 `--input` 可換 → 提醒。但「換了 `--input` 之後那次 detekt 沒產出可解析 SARIF」是第三種狀態,spec 沒講。
  - 既有冒煙的慣用寫法 `if not ok: problems.append("冒煙失敗…")` 一旦照抄,就跟實務隱患的「換不到就照實說、不記成問題」衝突。
  - 反過來若當作「五條全缺」,訊息會說「補型別參數」,是錯的診斷。
- 重現輸入:`detekt --input $(git rev-parse --show-toplevel)/app/src --report sarif:{LINT_SARIF_OUT} ...`,`$(...)` 沒加引號。
  - 用空白切詞會把 `$(git` 當成 `--input` 的值,換完剩下 `rev-parse --show-toplevel)/app/src` 變成 shell 語法錯誤,detekt 沒跑,沒有 SARIF。
  - 主冒煙那次(原指令)是綠的,只有探針那次壞,所以這就是「主冒煙過、探針沒產出」的真實情境。
  - 第二個成因:第二次 detekt 撞到 `LINT_CMD_TIMEOUT`(180 秒)。
- 佐證:
  - file: `scripts/lumos:38172-38188` 逾時、檔空、JSON 壞都回 `([], False)`,上層分不出是換壞了還是 detekt 真的沒響。
  - file: `scripts/lumos:37789-37791` 既有 `ok=False` 一律記成問題。
  - 實測 `detekt --config=cfg.yml` 這類壞參數會 usage 退出、不寫 SARIF。
- 引句:「指令字串是 shell 字串,換 `--input` 要處理引號與 `--input=x` 寫法」
severity: major
- blocking: 是。「缺哪條算問題、哪條只提醒」的分類漏了一個會真實發生的格子。

### F3 探針的四條型別規則要求消費專案 classpath 裡有 kotlinx-coroutines,沒有的專案會被誤判成「型別資訊沒給」
- spec 段落:用詞「探針驗的五條」、不做清單、S1。
- 問題:spec 為了避開 Compose 誤判,不驗 collectAsState。但同一個邏輯沒套用在協程函式庫上。
  - 探針的 `InjectDispatcher`、`SuspendFunWithFlowReturnType`、`SuspendFunWithCoroutineScopeReceiver` 需要 classpath 裡解析得到 kotlinx.coroutines 型別。
  - 共用設定是「Android 專案標準」,但 Android 專案不一定依賴 kotlinx.coroutines(例如用 RxJava 或 callback 的專案)。
- 重現:
  - classpath 只給 kotlin-stdlib 加 `--jdk-home`,探針結果為 `['GlobalCoroutineUsage','RedundantSuspendModifier','SleepInsteadOfDelay']`。
  - `InjectDispatcher`、`SuspendFunWithFlowReturnType`、`SuspendFunWithCoroutineScopeReceiver` 三條全部沒響。
  - 這種專案 classpath 其實給對了,但 `lint-check --smoke` 會 rc1。訊息點名缺三條並叫人「補型別參數」,補不了:這個專案根本沒有協程函式庫,要補的是依賴,而且它也不需要這些規則。
- 佐證:
  - 實跑 `detekt --input src ... --classpath kotlin-stdlib-2.2.21.jar --jdk-home <JDK17>`,輸出如上。
  - 同一組探針加上 `kotlinx-coroutines-core-jvm-1.9.0.jar` 後,這三條與 `SleepInsteadOfDelay` 都響。
- 引句:「探針不驗 collectAsState(要消費專案的型別資訊裡有 Compose runtime,沒用 Compose 的 Android 專案會被誤判成」
severity: major
- blocking: 是。spec 自己認定的「依賴缺失=誤判」風險,在協程這一條沒處理,會讓合格專案的 smoke 永遠紅。

### F4 靜態提醒的「是不是 detekt 指令列」「有沒有 classpath」判法沒定義,幾種常見命令形狀各自誤判
- spec 段落:範圍第二點、S4。
- 問題:spec 只給兩個結果:Gradle 不提醒、已帶 classpath 不提醒,沒定義怎麼從 shell 字串認出 detekt 指令列、怎麼認 classpath。本機現況有以下形狀:
  1. `cd android && ./gradlew detekt -Pout={LINT_SARIF_OUT}`。這是既有測試固定樣本(`scripts/test_lumos.py:36067`)。含 detekt 這個字、沒有 `--classpath`,用字詞比對會被判成要提醒。但它是 Gradle 接法,S4 要求不提醒。
  2. `./gradlew detektMain`(KDS 的真實宣告,見 `scripts/test_lumos.py:36071` 與 `scripts/lumos:37761`)。字詞比對 `\bdetekt\b` 比不中,子字串比對才中,兩種寫法結果相反。
  3. `java -jar /tmp/detekt-dist/...detekt-cli.jar --report ...` 是 KDS 真實宣告形狀(見 `Systems/lint-declaration-health` 第 26 行)。用「第一個 token 是 detekt」判斷會漏,目錄名含 detekt 的 `java -jar` 路徑則看判法而定。
  4. `java -cp detekt-cli.jar io.gitlab.arturbosch.detekt.cli.Runner --input src ...` 這個 `-cp` 是 JVM 的 classpath,不是 detekt 分析用的 `--classpath`。spec 把 `-cp` 當「有型別資訊」會誤判成有,應該提醒卻不提醒。
  5. `--classpath=x` 的等號寫法:detekt 1.23.8 的 JCommander 根本不收,會整個 usage 退出。對這種寫法的判法沒意義,但也沒說怎麼處理。
- 佐證:實跑 `detekt --input=src ...` 與 `detekt ... --config=cfg.yml` 都得到 `Was passed main parameter '--input=src' but no main parameter was defined in your arg class` 然後退出,detekt 1.23.8 只認空白分隔。
- 引句:「命令走 Gradle 或已帶 classpath 時兩處都 應 不提醒」
severity: major
- blocking: 是。判定函式沒寫清楚,上述 1/2/4 各有確切輸入會輸出與 S4 相反的結果。

### F5 健檢 F 段新判斷要「不管格式有沒有問題」就判,會對非 dict、非 list、非字串的合法 JSON 崩潰
- spec 段落:範圍第二點(健檢那段)。
- 問題:`_lint_load_and_validate` 在格式有問題時仍把解析後的 `config` 原樣放進回傳(`scripts/lumos:37731-37733`),所以 F 段拿得到「壞形狀」的資料,spec 要求這種情況也要判。
- 重現:`.lumos/lint.json` 內容是 `[1,2]` 或 `null`,`config` 不是 dict,新判斷若呼叫 `config.get("kt")` 就 AttributeError。內容是 `{"kt":[5]}` 時,把整數丟進 `shlex.split` 也會 TypeError。
  - 這兩種輸入在既有測試裡都有人餵過:`scripts/test_lumos.py:36070` 餵 `_lintcheck_validate([1,2])`,`scripts/test_lumos.py:8955` 餵 `{"kt":"not-a-list"}` 走 doctor `--ci`,預期受控 rc1。
  - doctor 的 F 段是 `if True:` 區塊、沒包 try(`scripts/lumos:4099`),traceback 會打斷整支健檢,連其他段都看不到。
- 佐證:`_lint_stacks_for_diff` 對 `config.get(ext)` 有 `isinstance(..., list)` 守衛,但對 `config` 本身沒有(`scripts/lumos:37684`),可見這個坑已經存在,新程式沒有現成工具可借。
- 引句:「健檢那段放在 F 段既有分支之後,只要宣告讀得出來(合法 JSON)就判,不管格式有沒有問題。」
severity: major
- blocking: 是。有具體輸入會讓 doctor 崩潰,而且是 spec 明文要求的路徑。

### F6 提醒的輸出位置沒定,problems 非空與 `--json` 兩條路徑會丟掉或汙染
- spec 段落:S2、S3、S4。
- 問題:`cmd_lint_check` 只有在 `not problems` 分支才會印 `skipped_stacks` 那類提醒(`scripts/lumos:37795-37801`)。`problems` 非空時走 `✗` 分支只列問題。
  - `--json` 分支更早 `return`(`scripts/lumos:37792-37794`),只印一行 JSON。
  - spec 說 lint-check「印一段提醒而退出碼照舊」,沒說這兩條路徑要不要印、印到 stdout 還是 stderr。照字面在 `--json` 下印到 stdout 會汙染 JSON(既有測試 `scripts/test_lumos.py:17002` 會解析 stdout);在 problems 分支不印則提醒被吞。
- 引句:「`lumos lint-check`(不帶冒煙)應印型別資訊提醒而退出碼照舊」
severity: minor
- blocking: 否。不影響合法路徑的判定正確性,是實作時要補的接口細節。

### F7 探針其實要驗六條,spec 前後只寫五條
- spec 段落:用詞第三點、範圍第一點、S2。
- 問題:用詞與範圍都說「探針五條」,S2 卻要求「五條都響、只缺吞取消那條」時 rc0 並印提醒。這代表探針原始碼必須另含 `runCatching { suspend 呼叫 }`,實作也要偵測第六條 `SuspendFunSwallowedCancellation`。「探針原始碼包含哪些違規範例」只靠 S2 暗示。
- 佐證:實跑確認這條在 stdlib 1.9.0 + 協程 1.7.1/1.9.0 下會響,在 stdlib 2.2.21 + 協程 1.9.0 下不響(o2 輸出無此條),spec 的版本限制描述屬實。
- 引句:「當探針五條都響、只缺吞取消訊號那條時,`lumos lint-check --smoke` 應 退出碼 0 並印提醒」
severity: minor
- blocking: 否。一處文字補齊就能消除,不影響判定方向。

### F8 引用共用設定卻沒帶 `--build-upon-default-config` 時,訊息的修法是錯的
- spec 段落:S1、實務隱患第一點。
- 問題:觸發探針的條件只看「引用共用 Android 設定」,沒要求 `--build-upon-default-config`。
  - 沒帶這個旗標時,即使型別參數齊全,只有設定檔明寫 `active: true` 的 `GlobalCoroutineUsage` 與 `SuspendFunWithCoroutineScopeReceiver` 會響。
  - 預設開的 `InjectDispatcher`、`SleepInsteadOfDelay`、`SuspendFunWithFlowReturnType` 不響。smoke 判缺三條並說「補型別參數」,補了也沒用。
- 重現:`detekt --input src --report sarif:o4.sarif --config cfg.yml --classpath <coroutines+stdlib> --jvm-target 17 --jdk-home <JDK17>`(沒有 `--build-upon-default-config`),結果 `['GlobalCoroutineUsage','SuspendFunWithCoroutineScopeReceiver']`。
- 引句:「訊息點名缺的規則並給補型別參數的修法」
severity: minor
- blocking: 否。紅燈本身是對的(那三條確實沒在跑),只是建議的修法有時指錯。

### F9 替換對象與引號規則沒指定,且可能撞到 `{LINT_FILES}` 的白名單守衛測試
- spec 段落:範圍第一點、實務隱患最後一點。
- 問題:
  - 新替換是對 `cmd` 做,還是對 `_lintcheck_smoke_cmd` 換完檔案清單的 `ready` 做,spec 沒說。若對 `ready` 做,`--input` 後面可能是三個以空白分隔的路徑(`scripts/lumos:37752` 取前三支),「整段值」的邊界不清楚。
  - 探針目錄要不要 `shlex.quote` 沒定。不加引號,TMPDIR 含空白就壞;加引號,需要跟「連同原本外面的引號一併換掉」配合,spec 只寫了前半。
  - `t_lint_files_substitution_has_one_implementation` 的白名單(`scripts/test_lumos.py:17108` 起,`ALLOWED`)規定名單外函式不准在原始碼裡提到 `_LINT_NEW_FILES_TOKEN` 或 `"{LINT_FILES}"`。新寫的換參數函式若為了處理 `--input {LINT_FILES}` 而提到這個 token,測試就紅。spec 沒提需要把函式加進白名單,也沒說避開。
  - `--input=x` 寫法在 detekt 1.23.8 根本不被接受(見 F4 佐證),實務隱患要求處理它是多餘的。
- 引句:「這段換參數的程式是新寫的,既有冒煙只會換 `{LINT_FILES}` 佔位符。」
severity: minor
- blocking: 否。都是實作時可以當場決定的細節,但最好在 spec 裡一次寫死。

### F10 靜態提醒只看 classpath,但用詞定義了三個參數
- spec 段落:用詞第一點、S4。
- 問題:用詞把 `--classpath`、`--jvm-target`、`--jdk-home` 都算型別資訊,S4 的靜態提醒只檢查 classpath。
- 重現:`--classpath` 帶齊但沒有 `--jdk-home` 時,`SleepInsteadOfDelay` 不響,靜態提醒不會出聲。
  - 實跑只有 classpath(含 jvm-target)時,`SleepInsteadOfDelay` 不在輸出裡。
  - 加上 `--jdk-home` 後它才響。
  - 只給 `--jvm-target` 不夠。
- 另外:只有探針能抓到這個情況,而探針只對「引用共用設定且帶 `--input`」的命令跑。
- 引句:「detekt 指令列的 `--classpath`(或 `-cp`)、`--jvm-target`、`--jdk-home` 三個參數」
severity: minor
- blocking: 否。缺口有探針後備,且不影響已定義路徑的正確性。

### F11 標準接法樣板「改帶型別參數」缺少產生 classpath 的辦法
- spec 段落:範圍第三點、第四點。
- 問題:spec 要把 `Systems/linter精選目錄` 樣板與 `configs/detekt/android.yml` 開頭用法改成帶型別參數,但 `--classpath` 的值對 Android 專案是專案特有(依賴的 jar 與 AAR 解出的 classes.jar,通常得靠 Gradle 任務印出),spec 沒說樣板用什麼佔位、讀者怎麼取得。樣板寫成 `<classpath>` 這類佔位,消費專案抄過去仍會是 F3 那種不完整的 classpath。
- 佐證:`docs/lumos-toolchain-knowledge/Projects/Android協程與API協同機械審_調研.md` 第 57 行自己寫「Android 專案要嘛用 Gradle 外掛的 `detekt<Variant>` 任務(自帶型別),要嘛 CLI 帶 `--classpath` 與 `--jvm-target`」,CLI 路線的取得方法沒有記。
- 引句:「設定開頭的用法改成帶型別參數的標準接法。」
severity: minor
- blocking: 否。屬於文件落地時要補的執行細節。

## 其餘節

- 範圍、不做、回退、天花板、REVISIT:已讀,無 finding。
  - 交叉引用目標都存在:`Projects/Android協程與API協同機械審_調研`、`Projects/社群規則第二批_計劃`、`Systems/lint-declaration-health`、`Systems/linter精選目錄`、`Systems/android-e2e-acceptance`。
  - `t_lintcheck_cli` 存在於 `scripts/test_lumos.py:36086`;S1–S4 綁的新測試名是待寫的,不是壞引用。
- spec 對 detekt 的現況斷言我查證過的:
  - 1.23.8 的設定驗證確實會拒絕不存在的屬性(`Run failed with 1 invalid config property`),所以「寫進 `CoroutineLaunchedInTestWithoutRunTest` 會讓 detekt 整個拒跑」成立。
  - `ForbiddenMethodCall` 的 `methods` 設定可被 1.23.8 載入。
  - `GlobalCoroutineUsage` 不需要 classpath 就會響,用它確認設定有被讀到成立。

## 圖譜節點逐條判

- `Systems/lint-declaration-health`:不影響宣稱的行為。
  - spec 新增的探針是在 smoke 之內多跑一次,不改「smoke 維持手動」「靜態層恆跑、有宣告才驗」。
  - 靜態提醒走 `warn([])` 也不動 `issues`。
  - 唯一牽連是該節點第 19–21 行的守衛:替換 `{LINT_FILES}` 的白名單測試(見 F9)。新函式若提到這個 token,測試會紅。
- `Systems/linter精選目錄`:不影響,但有一處文字要跟著改。節點寫的「開預設關的三條」與 `--build-upon-default-config` 的描述,補開兩條後要同步。
- `Systems/android-e2e-acceptance`:不影響。該節點的 WHY 否決了對使用者指令加 shell 引號的做法。本案不是換佔位符,是整段替換 `--input 值`,spec 的區分成立,但 F9 的引號細節要寫清楚,否則會踩到同一個理由。

## 實務隱患鏡頭

- 命令注入與 shell 字串解析:有隱患,見 F2、F4。
  - 探針在使用者的 shell 字串上做詞切分替換,`$(…)`、`&&`、環境變數前綴都不是 shlex 能完整處理的。
  - 替換失敗的後果被 spec 定義得不夠清楚(F2)。
- 子行程與暫存檔:探針暫存目錄「跑完即刪」,但沒說探針中途被 `LINT_CMD_TIMEOUT` 殺掉時的清理責任。
  - `_lint_run_and_parse` 的暫存 SARIF 有 `finally` 清理,探針目錄沒有等價的保證。
  - 輕微,與 F2 一起處理即可。
- 時間成本:每個 detekt 宣告 smoke 時間約加倍(主跑一次加探針一次,各受 180 秒逾時限制)。這點與 `Systems/lint-declaration-health` 已承認的「smoke 慢」同向,屬已知代價。
- 持續提醒無出口:靜態提醒對刻意不帶 classpath 的專案(例如只用不需型別資訊的規則)會永遠出現在每次 doctor 與 lint-check 上,spec 沒提關掉的方法。這是 spec 刻意選擇的「提醒不擋」,無額外風險。
- 版本相容:共用設定加進 `SuspendFunWithCoroutineScopeReceiver`。spec 全篇只講 1.23.8,沒說消費專案裝更舊的 detekt 時,這個設定屬性會被拒絕、整個 detekt 不跑。我沒有找到可驗證的版本邊界,不標,留給編排者判斷。
- 權限、個資、金流、網路:無。功能只讀本機宣告、在本機臨時目錄跑 detekt,不碰這幾類。

最嚴重 severity 是 major,blocking 共 5 條(F1、F2、F3、F4、F5)。
