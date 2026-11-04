severity: major

# 審稿報告:detekt協程規則真的在跑_計劃(r1,邊界席)

我替極端輸入發聲。以下全部在 detekt 1.23.8、macOS 實跑,或讀 `scripts/lumos` 得來。實驗檔在 `/tmp/lumos-seat-work/detekt協程規則真的在跑/邊界-sonnet/`,留給編排者收貨後刪。

## 逐節結論

- 前言、PRIOR-ART、RETIRE-IF:已讀,無 finding。反引號宣稱 0 條。內部交叉引用目標都存在:`Projects/社群規則第二批_計劃`、`Projects/Android協程與API協同機械審_調研`、`Systems/android-e2e-acceptance`、`Systems/lint-declaration-health`、`Systems/linter精選目錄`。`lands_in` 兩篇也存在。
- 用詞:見 finding 5、6。
- 範圍:見 finding 1、2、3、7、8。
- 實務隱患:見 finding 1、4、7。
- 驗收條款:見 finding 2、3、5、6、7。
- 回退:見 finding 8、9。
- 天花板與 REVISIT:已讀,無 finding。

## Finding

### 1. 新增告警閘「會被擋」這句,對 detekt 指令列做不到

- spec 段落:實務隱患第 4 條;範圍第 3 條。
- 引句:「之後新寫的 collectAsState 或掛在 CoroutineScope 上的 suspend 函式會被擋」
- 問題:
  - 標準樣板是 `--input <src 目錄>`,不帶 `{LINT_FILES}`。這種命令在新增告警閘裡直接降成 report_only,從不擋。
  - 改寫成 `--input {LINT_FILES}` 也不行。`{LINT_FILES}` 會被展開成「每個路徑各自跳脫、空白相接」。detekt 1.23.8 不收空白分隔的多個路徑。
  - 我實測 `detekt --input 'p1/Probe.kt' 'other/Z.kt' ...` 得 rc=1,訊息 `Was passed main parameter 'other/Z.kt' but no main parameter was defined in your arg class`,沒有產出 SARIF。
  - 所以改動兩支以上 kt 時,該命令被記成 env 類未完成,閘自動放行。
  - 結果:新補開的 ForbiddenMethodCall 和 SuspendFunWithCoroutineScopeReceiver,在 detekt 指令列宣告下,推送時從不真正擋人。spec 寫「這是本案要的效果」,效果實際上落空。
  - 連帶影響:既有冒煙 `_lintcheck_smoke_cmd` 取 3 支檔展開。專案有 2 支以上 kt 時,`--input {LINT_FILES}` 的宣告,冒煙會被誤判「跑不出可解析 SARIF」。spec 的 S1、S3 完全沒講這種 `--input {LINT_FILES}` 的形狀。
- 佐證:
  - file: `scripts/lumos:38888`(`_LINT_NEW_FILES_TOKEN not in cmd` 時 `out["report_only"].append(cmd)` 並 continue)。
  - file: `scripts/lumos:38788`(`_lint_new_classify` 的 not-checked 分支)。
  - file: `scripts/lumos:38305`(`_lint_cmd_with_files` 逐檔跳脫空白相接)。
  - file: `scripts/lumos:37737`(`_lintcheck_smoke_cmd`,sample=3)。
severity: major
- blocking: 是。載重宣稱(新增的規則會擋人)與程式現況相反,spec 要先改寫這句,並明講 `--input {LINT_FILES}` 的處置。

### 2. 探針命令怎麼組、探針跑不出結果怎麼判,spec 沒定義

- spec 段落:範圍第 1 條;S1、S3。
- 引句:「把那個參數的值(連同外面的引號)整段換成探針暫存目錄再跑一次」
- 問題:S1、S3 只定義了「缺規則」和「沒有 `--input` 可換」兩支。以下輸入沒有歸宿:
  - (a) 探針那次 `_lint_run_and_parse` 回 `([], False)`,即沒產出 SARIF。成因有:
    - 逾時(180 秒);
    - consumer 設定有 detekt 拒絕的鍵;
    - `--input=x` 換完仍是 `--input=`(finding 3);
    - 命令別處還有 `{LINT_FILES}` 殘留,例如 `--input src --includes {LINT_FILES}`。`_lint_run_and_parse` 見到佔位符會直接回 `([], False)`。
    這時該記成問題、略過,還是當成「五條全缺」?spec 一句「不能假裝驗過」不足以決定 rc。
  - (b) 先換 `--input` 再展開 `{LINT_FILES}`,還是反過來?先展開的話,`--input` 的值已是多個 token,「整段換」就換不乾淨(見 finding 1)。
  - (c) `_lintcheck_smoke_cmd` 回 None(專案還沒有 kt 檔)時,探針跑不跑?探針其實不需要專案檔,但既有分支是 `continue` 略過整條。
  - 另外,新增告警閘的程式與測試守著「整支程式只准有一處替換 `{LINT_FILES}`」。探針命令必須重用 `_lint_cmd_with_files`,不能再手寫一處 `.replace`。spec 沒提。
- 佐證:
  - file: `scripts/lumos:38157`(佔位符未換就 `return [], False`)。
  - file: `scripts/lumos:37786`(smoke 無檔分支)。
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:21`(只准一處替換佔位符的守衛)。
severity: major
- blocking: 是。有 rc 後果的分支沒定義,實作者各自裁量會得到不同的退出碼。

### 3. 「detekt 指令列」的判定式沒定義,正反例在本 repo 文件裡就有

- spec 段落:範圍第 1、2 條;S3、S4。
- 引句:「命令不是 detekt 或沒引用共用設定時 應 完全不跑探針」
- 問題:
  - 本 repo 文件記載的真實宣告有 `java -jar /tmp/detekt-dist/detekt-cli-1.23.7-all.jar --input ...`,執行檔不叫 detekt。
  - 另有 Gradle 形,`./gradlew detektMain`。
  - 「是 detekt 指令列」、「走 Gradle」若用子字串或詞界比對,結果不同:
    - 比對 `detekt`,會把 `./gradlew detektMain` 當 CLI,而它沒有 `--classpath`,於是印假提醒,違反 S4「走 Gradle 不提醒」。
    - 比對詞界 `detekt` 或執行檔名,則 java -jar 形漏判,S4 提醒不會印。
  - S4 的「走 Gradle」測試因此無法確定地寫出來。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:55`(jar 形宣告)。
  - file: `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:26`(KDS detektMain 案例)。
severity: major
- blocking: 是。S3、S4 的負面分支依賴這個判定,需補定義(執行檔 token 規則、是否含 `java -jar ...detekt-cli`、`gradlew` 排除)。

### 4. `--input=x` 在 detekt 1.23.8 根本不合法,spec 要求「處理」是死分支

- spec 段落:實務隱患第 3 條。
- 引句:「換 `--input` 要處理引號與 `--input=x` 寫法」
- 問題:
  - 實測 `detekt --input=p1 ...` 得 rc=1,訊息 `Was passed main parameter '--input=p1' but no main parameter was defined`。
  - 這種宣告的真命令冒煙本來就失敗。
  - 若探針換成 `--input=<探針目錄>` 照跑,探針也會失敗,落進 finding 2(a)。
  - 若測試用假 detekt 腳本驗這支,假腳本若接受 `--input=`,測試綠但與真 detekt 不符。
  - 同時 `-i p1` 與逗號清單 `--input other,p1` 都實測可用。`-i` 路徑 spec 有涵蓋。
- 佐證:detekt 1.23.8 實跑輸出,見上。
severity: minor
- blocking: 否。spec 應刪掉這條要求,或改成「`--input=` 直接視為套不上」。

### 5. 缺規則的修法訊息一律講「補型別參數」,但缺的成因不只這個

- spec 段落:S1;實務隱患第 1、2 條。
- 引句:「訊息點名缺的規則並給補型別參數的修法」
- 問題:實測以下情形,五條規則會缺而與型別資訊無關。
  - consumer 命令帶 `--excludes '**/Probe.kt'`:五條全缺,rc=0,連 GlobalCoroutineUsage 也缺。spec 自己說 GlobalCoroutineUsage 是「確認共用設定有被讀到」。
  - 探針檔被 `--baseline` 吃掉:我拿同一份探針建 baseline 再跑,結果為空。
  - 共用設定是舊版(缺新補的 SuspendFunWithCoroutineScopeReceiver):這一條缺,與型別資訊無關。
  - 這時「補型別參數」是錯誤指引。
  - 另外,「吞取消訊號」提醒寫死「detekt 1.23.8」。這條缺,也可能是 consumer 自己關了,此時該句不實。
- 佐證:實測 `--excludes '**/Probe.kt'` 與 `--baseline` 皆得空結果,見上。
severity: minor
- blocking: 否。建議的判準:GlobalCoroutineUsage 缺 → 先講「共用設定沒讀到或探針被濾掉」,不給型別參數修法。這條 spec 應補。

### 6. 型別資訊定義三個參數,但 S4 只查 classpath

- spec 段落:用詞;範圍第 2 條;S4。
- 引句:「沒帶 `--classpath` 或 `-cp` 時」
- 問題:
  - 實測只給 `--classpath`、不給 `--jdk-home`/`--jvm-target`,得 `['GlobalCoroutineUsage','InjectDispatcher','SuspendFunWithFlowReturnType']`,SleepInsteadOfDelay 消失。
  - 給齊三個參數則四條皆響。
  - 所以只帶 classpath 的命令,S4 不提醒,SleepInsteadOfDelay 靜默不跑。只有冒煙探針才抓得到。
  - 「已帶 classpath 時不提醒」與用詞「三個參數」不一致。
  - `-cp` 簡寫在 1.23.8 實測可用,無問題。
severity: minor
- blocking: 否。

### 7. 探針第二次執行會改寫 consumer 命令裡的其他報告檔,與回退宣稱衝突

- spec 段落:回退。
- 引句:「沒有寫入任何消費專案的檔」
- 問題:
  - 命令常帶 `--report txt:...`、`html:...`,或 `--create-baseline --baseline x.xml`。探針在 cwd=repo_root 再跑一次,同一個報告路徑會被改成探針結果。
  - 實測 `-r txt:rep.txt`,舊內容 `old` 被換成探針的 InjectDispatcher 等條目。
  - 真命令先跑、探針後跑,最終留在 repo 裡的是探針內容。
  - 這影響範圍包含 `--create-baseline` 的 baseline 檔。
- 佐證:
  - file: `scripts/lumos:38163`(`cwd=repo_root` 執行,stdout/stderr 轉 DEVNULL)。
  - 上述實測。
severity: minor
- blocking: 否。spec 需改回退句,或明講探針會被忽略/抑制其他 report。

### 8. 靜態提醒「不管格式有沒有問題」會餵不合法的結構給新判斷

- spec 段落:範圍第 2 條。
- 引句:「只要宣告讀得出來(合法 JSON)就判,不管格式有沒有問題」
- 問題:
  - 輸入 `{"kt": 5}`、`{"kt": "detekt ..."}`、`{"kt": [null]}`、頂層為 `[]`,都是合法 JSON。
  - `_lintcheck_validate` 會擋,新判斷在問題路徑上也要跑,必須自己防型別,否則 doctor 以 traceback 結束。
  - 「lint-check 也印提醒」與 `--json` 衝突。`--json` 模式只印一行 JSON(`scripts/lumos:37792-37794`),測試 `scripts/test_lumos.py:17002` 就在解析它。提醒若 print 到 stdout 會污染。spec 沒講 `--json` 時提醒走哪。
  - `lint-check` 進入點提早 `return 1` 的 problems 分支(`scripts/lumos:37802`),提醒是否仍印,也沒講。
severity: minor
- blocking: 否。

### 9. 暫存目錄的清除只寫「跑完即刪」,沒說異常路徑

- spec 段落:用詞(探針);回退。
- 引句:「探針用的暫存目錄跑完即刪」
- 問題:
  - `_lint_run_and_parse` 只捕 `TimeoutExpired`(`scripts/lumos:38173`),沒捕 `KeyboardInterrupt`。
  - Popen 用 `start_new_session=True`。Ctrl-C 只打到 lumos,不打到 detekt JVM,JVM 孤兒仍在讀探針目錄。
  - 若探針目錄用 `mkdtemp` 而不放進 `try/finally`(或 `TemporaryDirectory`),Ctrl-C 或例外會殘留。
  - 新增告警閘有 `_LINT_NEW_STALE_SEC` 殘骸清掃(`scripts/lumos:38285`),探針沒有等價機制。
  - 冒煙多一次 `LINT_CMD_TIMEOUT=180`,spec 沒交代探針逾時預算與對 `lumos doctor` 慢速說明的影響。
severity: minor
- blocking: 否。spec 補一句「用 `with TemporaryDirectory`/finally 清」即可。

### 10. 規則比對鍵與符號連結:spec 用裸規則名,SARIF 實際是帶規則集前綴

- spec 段落:用詞(探針驗的五條);S1。
- 問題:
  - SARIF 的 ruleId 實測為 `detekt.coroutines.InjectDispatcher`,不是 `InjectDispatcher`。
  - 檔案 uri 在 macOS 是 `file:///private/tmp/...`,即使 cwd 寫 `/tmp`。`/var` 同理會變 `/private/var`。
  - 比對只靠規則名尾段就沒事。若實作順手按「檔案落在探針目錄」過濾,字面比對會落空,因為字面算不進 repo_root 還要靠 realpath 補救(`scripts/lumos:38229-38236`)。
  - spec 沒指定比對鍵。
- 佐證:SARIF 實測輸出,見上。
severity: minor
- blocking: 否。

### 11. `&&` 串兩個 detekt、多次 `--input` 的處理沒講

- spec 段落:範圍第 1 條。
- 問題:
  - 同一條命令 `detekt --input a ... --report sarif:{LINT_SARIF_OUT} && detekt --input b ... --report sarif:{LINT_SARIF_OUT}`,兩個 `{LINT_SARIF_OUT}` 被換成同一個檔,後者覆蓋前者。
  - spec 寫「那個參數」是單數。只換第一個,探針 SARIF 會被第二個真執行蓋掉,結果五條全缺,被誤報成問題。
  - 同一個 detekt 兩個 `--input` 則 detekt 自己拒絕(`Can only specify option --input once`,rc=1),真命令就失敗,此路徑歸 finding 2(a)。
  - spec 需規定:全部出現處都換,或命令含多個 detekt 呼叫就算「探針套不上」。
severity: minor
- blocking: 否。

## 固定席節點(逐條判)

- `Systems/lint-declaration-health`:不影響合約。其 KEY 說 smoke 是「每 linter 一次完整 run」,探針會加倍,屬描述需更新,不破壞行為。但該節點釘住「只准一處替換 `{LINT_FILES}`」(測試 `t_lint_files_substitution_has_one_implementation`)。探針實作若新增第二處替換就會紅,見 finding 2。
- `Systems/linter精選目錄`:不影響。0 條合約。改標準接法樣板屬文件。但 `--input <src 目錄>` 樣板是 report_only,見 finding 1。
- `Systems/android-e2e-acceptance`:不影響。其 WHY 否決的是 `{{TEST}}` 佔位符的 shell 引號包裹。本案替換的是使用者自己的 `--input` 值,機制不同。spec 說「只有一層引號,不會疊」成立。前提是實作真的用 shell tokenizer 解析引號,而不是 regex 假設單一種引號,這是實作要守的。

## 實務隱患鏡頭

- 指令字串解析:finding 3、4、11,另見 finding 2(b)。`-i`、逗號清單、含空白目錄 `'dir with space'` 皆實測可用,無問題。
- 退出碼與錯誤訊息:finding 2、5。
- 對 consumer repo 的副作用:finding 7。
- 清理與逾時:finding 9。
- 平台(macOS 符號連結):finding 10。
- 效能:探針檔小,第二次執行主要成本是 JVM 啟動加載入 classpath,我只在 1 個小 classpath 下實跑,沒有量大型 Android classpath 的耗時,無數據可據以標。
- 資安:無。命令本來就是 consumer 自己宣告的 shell 字串,探針沒有新增外部輸入面。
- 併發:無。冒煙是人手動序列執行。

最嚴重 severity 是 major,blocking 共 3 條(finding 1、2、3)。
