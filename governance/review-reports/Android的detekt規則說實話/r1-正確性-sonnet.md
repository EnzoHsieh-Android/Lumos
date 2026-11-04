severity: major

審查對象:`governance/review-reports/Android的detekt規則說實話/r1-snapshot.md`(一份外部投稿的設計 spec)。判定表我用 Python 3.14 的 shlex、本機 detekt 1.23.8 和一份複製出來的測試實跑過。臨時檔在 `/tmp/lumos-seat-work/Android的detekt規則說實話/正確性-sonnet/`,由編排者收貨後刪。

## 〈判定表〉與〈範圍〉

**F1. 判定函式要檢查 `{LINT_FILES}`(P1、P2),會讓現有的「佔位符只准一處替換」守衛測試變紅,spec 沒提要改它。**
引句:「任何 detekt 宣告(指令列或 Gradle),整條命令沒有 `{LINT_FILES}`」
- 佐證 file: `scripts/test_lumos.py:17108` 的 `t_lint_files_substitution_has_one_implementation`。
- 佐證 file: `scripts/test_lumos.py:17138` 的 `ALLOWED` 白名單只收 6 支函式。
- 佐證 file: `scripts/test_lumos.py:17154` 的斷言:名單外的函式只要提到 `"{LINT_FILES}"` 字面或 `_LINT_NEW_FILES_TOKEN` 就紅。
- 重現:我把 `scripts/lumos` 和 `scripts/test_lumos.py` 複製到臨時目錄,加一支只寫 `"{LINT_FILES}" not in cmd` 的 `_lint_detekt_advice`,再跑 `python3.14 test_lumos.py -k t_lint_files_substitution_has_one_implementation`。結果是 `✗ 名單外碰到它的:['_lint_detekt_advice']`,整個測試 FAILED。
- spec 的〈範圍〉、〈驗收條款〉、〈回退〉都沒提要改這份白名單。
- 白名單在 `scripts/test_lumos.py` 裡,改它得走測試檔簽名流程。
- 照 spec 實作會在推送閘當場紅,spec 沒給出解法:是改白名單、還是不寫佔位符字面(例如拿 `_lint_cmd_with_files(cmd, ["x"]) != cmd` 偵測)。

severity: major
blocking: 是。照 spec 實作必然讓既有守衛測試紅,而且改法牽涉測試檔簽名,不能留給實作者自己猜。

**F2. 拆詞只寫「shlex、posix 模式、標點拆開」,沒寫實作必須的設定。照字面實作會在含中文路徑時失準。**
引句:「每條命令用 shlex 以 posix 模式、標點拆開切成詞」
- 要拆出 `;` `&&` `|`,只能用 `shlex.shlex(..., punctuation_chars=True)`,`shlex.split` 沒這個參數。
- 沒設 `whitespace_split=True` 時,實跑結果:
  - `/Users/enzo/測試/detekt --input src` 拆成 `['/Users/enzo/','測','試','/detekt',…]`,段首認不出 detekt。
  - 設了才是 `['/Users/enzo/測試/detekt','--input','src']`。
  - `./gradlew :app:detekt` 未設時拆成 `':'`、`'app'`、`':'`、`'detekt'`。
- 另外 `shlex.shlex` 預設 `commenters='#'`,`-Pa=b#c` 會被截成 `-Pa=b`,`--input src # x -cp a` 後面整段消失。真 shell 的 `#` 在字中是字面字元。
- 換行被當空白:`detekt --input x\n./gradlew detekt` 併成一段。行尾 `\`+換行會產生一個 `'\n'` 詞,擋在段首就讓整條漏判。
- PRIOR-ART 說「本 repo 拆掛鉤命令時用過 shlex」。實際只有 `scripts/lumos:35464` 的 `_shlex.split(cmd)`,它不含標點拆分,不能當同款先例。

severity: minor
blocking: 否。S1 的列舉案例大多仍會過(`:app:detekt` 因為每個詞各自比對也剛好成立),只有含中文路徑、`#`、換行的命令會漏判或誤判;spec 補一句「`whitespace_split=True`、`commenters=''`」即可。

**F3. 「含 `$(` 的段不判」在 shlex 拆詞後無法用詞比對實作。**
引句:「含 `$(`、反引號命令替換的段不判」
- 未加引號的 `$(git ls-files)` 拆成 `['$','(','git','ls-files',')']`,沒有任何一個詞含 `$(`。反引號因為不是標點字元,還留在詞裡。
- 加雙引號的 `"$(ls | head)"` 反而是單一詞 `'$(ls | head)'`,詞比對抓得到。
- 替換裡有 `&&`、`;`、`|` 時,替換內容會被切到下一段:`$(a; b)` 變成 `...$ ( a` 與 `b )` 兩段。
- 失敗情境:`detekt --input src $(cat extra-args)`。若用詞比對,`$` 和 `(` 分開,這段不會被跳過,印出「沒有 `-cp`」的 T1,但 extra-args 內容可能就帶了 `-cp`。
- spec 要寫明是對原始字串、還是相鄰詞 `$`+`(` 判。

severity: minor
blocking: 否。S1 明列「命令替換」,實作者跑測試會發現,只是 spec 的判準寫法有缺口。

**F4. 包裝詞列了 `nice`、`env`、`time`,但這些包裝詞的選項沒處理,帶選項的寫法會漏判。**
引句:「每段先去掉開頭的環境變數設定(`名稱=值` 形狀的詞)與包裝詞 `env`、`exec`、`time`、`nice`、`nohup`、`command`」
- `nice -n 10 detekt` 拆成 `['nice','-n','10','detekt']`,去掉 `nice` 後段首是 `-n`。
- `env -i detekt`、`time -p detekt` 同理。
- 只會漏報,不會誤報。
- 同一種寫法也沒規定 `env FOO=1 detekt` 與 `FOO=1 env detekt` 要交錯去除。

severity: minor
blocking: 否。表外不判是 spec 允許的,但這幾個明列的包裝詞對常見寫法無效。

**F5. Gradle 判定列有兩個缺口。**
引句:「某個不以 `-` 開頭的詞,取最後一個 `:` 之後的名字恰好是 `detekt`」
- (a) 優先序沒寫。`detektBaselineDebug` 同時符合「`detekt` 開頭、`Debug` 結尾 → 有型別任務」與「`detektBaseline` 開頭 → 不是跑檢查的任務,不判」。外掛確實有 `detektBaseline<Variant>`(見下方來源)。S1 對這個名字的期望值不明。
- (b) 選項的值或被排除的任務會被誤認。`./gradlew check -x detekt` 的 `detekt` 不以 `-` 開頭,被判成在跑 detekt,會誤印 G1 與 P1。`./gradlew -p detekt build` 的專案目錄名也一樣。

severity: minor
blocking: 否。誤判只多印一則提醒,不影響退出碼。

**F6. T1 判準與 T2 的說明對不同寫法的描述不準。**
引句:「SleepInsteadOfDelay(只要 JDK)」
- 實跑:只給 `--jdk-home`、沒有 `--classpath` 時,SleepInsteadOfDelay 和所有要型別的規則都不響。它還需要一個非空的 classpath,不是「只要 JDK」。
- 此時 T1 會印出「補法是帶 `--classpath` 與 `--jdk-home`」,但使用者已經帶了 `--jdk-home`。
- 實務隱患那節還有一句:
  引句:「classpath 指到不存在的檔時,判定表判成有型別(T1 不出),實際規則全不跑」
  這句與實跑不符。`--classpath /nonexistent.jar --jdk-home <JDK>` 時,SleepInsteadOfDelay 和 RedundantSuspendModifier 仍然會響,只有需要協程或標準庫型別的規則不響。結論「看字面抓不到」仍成立,但「全不跑」這個事實要改。

severity: minor
blocking: 否。

**F7. 吞取消訊號規則的版本邊界,實測比 spec 更窄,T1 的補法沒有出口。**
引句:「吞取消訊號(SuspendFunSwallowedCancellation)只在 stdlib 2.0.21 下響,換 2.3.21 不響,其他版本沒逐一測」
- 我用本機 Gradle 快取逐一測了所有可得版本(coroutines 1.8.1 與 1.10.2 結果相同):
  - stdlib 1.8.20、1.8.21、1.9.0、1.9.20、2.0.21、2.1.21 會響。
  - stdlib 2.2.0、2.2.10、2.2.20、2.2.21、2.3.20、2.3.21、2.4.21 全部不響。
  - 邊界在 2.1.21 與 2.2.0 之間。
- 2.2.0 以上時,連 `kotlin.io.println` 的 ForbiddenMethodCall 都不響。
- 但 `androidx.compose.runtime.collectAsState` 的 ForbiddenMethodCall 在 stdlib 2.3.21 下仍然響(已實測)。
- Kotlin 2.2 以上的 Android 專案照 T1「補法是帶 `--classpath`」做完,吞取消訊號規則仍然安靜失效。〈天花板〉沒有這條,表上也沒有對應提醒。

severity: minor
blocking: 否。spec 已承認這個限制;實作時應把邊界與「補了也不響」補進天花板。

**F8. 共用設定的 `ForbiddenMethodCall` 方法清單,spec 只寫簡名,簡名不會生效。**
引句:「ForbiddenMethodCall 原本沒寫在共用設定裡(detekt 預設關),新增成開、方法清單只放 collectAsState」
- 實測:`methods: ['collectAsState']` 完全不響,`methods: ['androidx.compose.runtime.collectAsState']` 才響。連 `println` 簡名也不響。
- 此規則屬於 `style:` 規則集,放錯規則集 detekt 會整個拒跑(同類驗證:`CoroutineLaunchedInTestWithoutRunTest` 放進 `coroutines:` 回 rc=3「Property … is misspelled or does not exist」,spec 這點說對了)。
- spec 沒寫全名與規則集位置,S4 是 manual 才會被抓到。

severity: minor
blocking: 否。

**F9. 其他事實性斷言,逐項核對。**
已讀,無 finding:
- T3:`--input=x`、`-i=x`、`--report=…`、`--classpath=…`、`--jvm-target=17`、`--parallel=true` 全部 rc=1「Was passed main parameter」,不產結果,與 spec 一致。
- P2:`--input a.kt b.kt` rc=1,`a.kt,b.kt` rc=2 有結果。空 SARIF 在 `scripts/lumos` 的 `_lint_run_and_parse` 回 `ok=False`,被記成環境類放行,與 spec 一致。
- P1:`scripts/lumos` 的 `_lint_new_verdict` 把沒有 `{LINT_FILES}` 的命令放進 `report_only` 且不跑,與 spec 一致。
- G1:Gradle 外掛的 `detekt` 任務無型別解析,`detekt<Variant>` 有,與 detekt 官方型別解析文件一致。
- 版本限制:`SuspendFunInFinallySection` 與 `CoroutineLaunchedInTestWithoutRunTest` 在 1.23.8 寫進設定整個拒跑,屬實。
- 規則範圍:`SuspendFunSwallowedCancellation` 只抓 `runCatching` 裡的 suspend 呼叫,`try/catch(e: Exception)` 不抓,屬實。
- 有無型別的分類:
  - `GlobalCoroutineUsage`、`ForEachOnRange` 不用型別就響。
  - `CouldBeSequence`、`ArrayPrimitive` 只要 classpath(stdlib)就響,不需要 JDK。
  - `SuspendFunWithCoroutineScopeReceiver` 預設關,補開後才響。
- `$HOME` 之類環境變數展開不含 `$(`,不被跳過。
- 以 `warn([])` 呈現的做法會讓 `--ci` 退出碼不變,且現有 doctor 測試用的 `detekt {LINT_SARIF_OUT}` 宣告仍通過。
- lint-check 的 JSON 現有格式固定為 `{problems, declared}`,新增 `advisories` 欄不破壞既有測試。
- 補一點:`warn([])` 只印標題與建議,不印逐條。多個提醒要塞進同一個標題或建議字串;若實作者改成逐條傳入,issues 會增加,`--ci` 變紅。S3 的測試能抓到,spec 可以寫明。

severity: clean
blocking: 否。

## 圖譜鏡頭(計劃連結的節點)

- 附帶的 5 個節點(推送閘對 Android 的 detekt 只記錄不擋、`Systems/lint-declaration-health`、`Systems/linter精選目錄`、`Systems/效能檢核目錄`、`Systems/pitfalls-lint-adapter`):我 grep 過,沒有 ★INVARIANT★、★IRREVERSIBLE★、★CHECKPOINT★ 或 `RULE:` 合約行。這份設計沒有破壞節點宣稱的行為。
- `lint-declaration-health` 有一行 KEY 講「`{LINT_FILES}` 佔位符只准有一處替換」。這份設計只做存在判斷、不做替換,不破壞「只有一處替換」本身,但會觸發同一行 KEY 綁定的白名單守衛測試,詳見 F1。
- `pitfalls-lint-adapter` 的 KEY「無 `.lumos/lint.json` → 輸出不變」:設計明寫沒宣告時不加欄位,不影響。
- `lint-declaration-health` 的 KEY 說健檢 F 段「壞=紅擋 CI」:新增的提醒用空清單,不改 issues 計數,不影響。

## 實務隱患鏡頭

- 資安:無。新函式只拆詞判讀、不執行命令,輸入是 repo 自己的 `lint.json`。
- 金流、對外送出、不可逆:無。與 spec 自己的排除一致。
- 效能:無。每條命令是短字串的線性拆詞。
- 相容:無。`--json` 只加欄位,回退時 spec 已註明。
- 例外防護:spec 已寫要自己防型別,F 段沒有包例外;`shlex` 的 `ValueError` 要在拆詞處接住,spec 已寫「拆詞失敗就不判」。

## 順手帶到

我跑 `test_lumos.py` 兩次,留下 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 底下的 `gctl-run-*` 現場。第一次的 `gctl-run-0n_gkksx` 已刪。第二次那份沒顯示目錄名,我認為是 `gctl-run-ft4rbd6g`(21:21 建、只有 `home` 子目錄),但同一目錄下還有其他會談的 `gctl-run-*`,我不確定,所以沒刪。

來源:detekt Gradle 外掛的 `detektBaseline<Variant>` 任務,出自 [detekt.dev Gradle 文件](https://detekt.dev/docs/next/gettingstarted/gradle/)。

最嚴重 severity:major,blocking 共 1 條(F1)。
