severity: major

審查範圍:spec `r1-snapshot.md` 全文,對照 `scripts/lumos`(`_lint_run_and_parse`、`_lint_new_verdict`、`_lint_new_classify`、`_lint_cmd_with_files`、`_lintcheck_smoke_cmd`、`cmd_rule_check`、`_detekt_cli_codes`、`_pitfall_diff_collect`)、`scripts/test_lumos.py` 與本機 detekt 1.23.8。實驗在 `/tmp/lumos-seat-work/android的detekt推送前真的擋/通才-sonnet/e1/` 做,已刪。

## Findings

**1. 型別參數檔裡只要有一個路徑含空白,detekt 整條拒跑,閘照環境問題放行**
severity: major
blocking: 是(核心目標「不再安靜放行」在常見環境落空,屬 major)
- spec 段落:〈用詞〉型別參數檔與初始化腳本(`--classpath`、`--jdk-home` 各佔一行)。
- 引句:「內容是 detekt 指令列參數,一行一個:`--classpath`、組好的 classpath、`--jdk-home`、JDK 路徑、`--jvm-target`、目標版本。」
- 重現:
  - 把 `--jdk-home` 的值換成含空白的路徑(例 `…/jdk sp/h`,模擬 macOS 上 Android Studio 內建 JDK 的 `/Applications/Android Studio.app/…`)。
  - 跑 `detekt @args --input src/P.kt --build-upon-default-config --config android.yml --report sarif:o.sarif`。
  - 實測印出 `Was passed main parameter 'sp/h' but no main parameter was defined in your arg class` 加用法說明,不產 SARIF。
  - 給路徑加雙引號沒用,錯誤變成 `'sp/h"'`,引號被當成字元。
  - 家目錄含空白、classpath 任何一個 jar 路徑含空白,結果相同。
- 後果:file: `scripts/lumos:38383` 沒有 SARIF 就回 `([], False)`,file: `scripts/lumos:39147` 記成 `kind: "env"`,`_lint_new_classify` 對 env 設 `autopass`。這條命令被靜默放行。
- spec 沒要求初始化腳本在寫檔時偵測或拒絕含空白的路徑,也沒說這種情形怎麼處理。

**2. 型別參數檔缺失、`--jvm-target` 超出範圍、逾時這幾種失敗也全走「跑不出結果」自動放行,探針只管「有產出但規則沒響」**
severity: major
blocking: 是(同一個「不再安靜放行」缺口,而且是最常見的失敗)
- spec 段落:
  - 引句:「探針那次 detekt 沒產出可解析的結果時,沿用既有判定:整條命令記成「跑不出結果」;這種情況不再判探針」
  - 引句:「不給型別參數檔時 應 因型別資訊沒接上而擋;沒裝 detekt 時測試印略過」(S10)
- 實測與程式佐證:
  - 命令寫 `@build/lumos/detekt-typeinfo.args` 而檔不存在:detekt 印 `Could not read file nonexist` 加用法說明,不產 SARIF。
  - 這個檔在 `./gradlew clean`(清掉 `build/`)後、在乾淨 worktree 或新 clone 裡都不存在。記憶「從乾淨 worktree 推」也是現行慣例。
  - `--jvm-target 24` 時 detekt 1.23.8 丟 `Invalid value (24) passed to --jvm-target, must be one of [1.6 … 22]`,不產 SARIF。spec 完全沒寫「目標版本」從哪取、要不要夾在 detekt 支援範圍內。
  - 型別化 detekt 要在同一個 300 秒預算內跑基準版與現在版各一次。逾時時 `_lint_run_and_parse` 回 `([], False)`,同樣記成 env。
- 這四種都不經過探針,全部 autopass。S10 的「不給型別參數檔 → 擋」只有在命令字面根本沒有 `@…` 時才成立。真實的「檔不見了」情境仍是 fail-open,而且正是 Issue 要消滅的那種靜默放行。
- 缺口是:閘在跑命令前沒有檢查 `@<路徑>` 檔是否存在,逾時與拒跑也沒有歸為擋的類別。

**3. `--input` 也用 `;` 切分,含 `;` 的檔名走 env 放行,spec 只處理逗號**
severity: minor
blocking: 否(罕見檔名,但是同一個靜默放行路徑)
- spec 段落:範圍第 2 條,只定義 `comma-path`。
- 重現:`detekt --input 'semi/a;b.kt' …` 丟 `ParameterException: Provided path 'semi/a' does not exist!`,不產 SARIF,所以走 env 放行。

**4. 基本探針只證明「有給 `--classpath` 與 `--jdk-home`」,不證明 classpath 內容是真的,spec 的說法偏強**
severity: minor
blocking: 否(天花板第 2 條已承認一部分,但實測更弱)
- spec 段落:
  - 引句:「基本探針(只靠 Kotlin 標準庫與 JDK):觸發 RedundantSuspendModifier(suspend 函式裡沒有任何掛起呼叫)」
  - 引句:「探針證明「型別資訊夠讓標準庫與協程那幾條規則跑」,不證明 classpath 齊全」
- 實測:`--classpath /nonexistent.jar --jdk-home <JDK>`(沒有任何真 jar)時,RedundantSuspendModifier 與 SleepInsteadOfDelay 兩條照樣響。標準庫由 detekt 自帶,不靠 classpath。
- 後果:初始化腳本在 AGP 版本變動時產出只含不存在或空的路徑,基本探針照過。只有協程探針用得到真 jar,而它只在變更檔含 `kotlinx.coroutines` 字樣時才要求。
- android.yml 實際開的 `ForbiddenMethodCall`、`CouldBeSequence`、`SuspendFunSwallowedCancellation`、`SuspendFunWithCoroutineScopeReceiver` 都沒有對應探針。

**5. S10 與 S6 互相牴觸**
severity: minor
blocking: 否(測試設計問題)
- S10:「只給標準庫加 JDK 的型別參數檔,對一次改了兩支 kt 檔的提交…擋下新增的 GlobalScope 裸用、探針判定通過」。
- S6:任何一支變更檔含 `kotlinx.coroutines` 字樣就要求協程探針,而協程探針需要 coroutines jar。
- 一支可編譯的 GlobalScope 範例必然有 `import kotlinx.coroutines.GlobalScope`。S10 的 fixture 只有刻意省略 import 才不會被判 probe-missing。spec 沒講這個前提。

**6. 唯一動真 detekt 的測試 S10 在 CI 不會跑,`@參數檔`、逗號 `--input` 的行為在 CI 沒有任何驗證**
severity: minor
blocking: 否
- file: `scripts/test_lumos.py:36369` 的既有慣例是 `shutil.which("detekt")` 找不到就印略過。`.github` 底下沒有安裝 detekt 的步驟。
- S1 到 S9 都用假工具,S11 是手動。spec 的最大賭注都押在 detekt 1.23.8 的行為上,卻沒有 CI 層的釘子,REVISIT 也只檢查 2.0。

**7. 替換函式「相對命令執行目錄」的算法沒講清楚,容易寫成錯的**
severity: minor
blocking: 否
- spec 段落:〈用詞〉逗號佔位符,「替換函式多收一個「命令執行目錄」參數」。
- 現況:`_lint_cmd_with_files(cmd, files)` 的呼叫端有三種輸入。
  - 新增告警閘:絕對路徑。
  - 冒煙與風險分級:已相對於 repo_root 的字串。
  - file: `scripts/lumos:38228` 的 `cmd_rule_check`:`str(sp)` 絕對路徑。
- 若直接對所有輸入做 `os.path.relpath(p, cwd)`,相對輸入會被當成相對於行程目前目錄而算錯。`lumos … --repo X` 從別處執行時,冒煙與風險分級會壞。
- spec 的範圍 1 只列規則索引的形狀檢查,沒列 `cmd_rule_check` 的替換呼叫要傳該參數。
- 該參數需要預設值,因為 file: `scripts/test_lumos.py:17184` 的既有測試是兩個引數呼叫。
- S1 的「換成一個加了引號的參數」也不精確。`shlex.quote('a/X.kt,b/Y.kt')` 不加引號,只有特殊字元才加。

**8. 說實話那套文字與判定函式的簽名牽連面沒列**
severity: minor
blocking: 否
- `_DETEKT_ADVICE_TEXT["T1"]` 現寫「Android 專案的依賴散在建置快取,目前沒有現成取法」,本案上線後就是錯的。範圍 6 與 7 沒列它,android.yml 標頭的 G1 說明「接不進推送前檢查」也一樣。
- 「`@` 檔不存在」提醒要看檔案系統。但 `_lint_detekt_codes(cmd)`、`_detekt_command_codes`、`_detekt_cli_codes` 都只收命令字串,docstring 明講「只看字面,不執行」,且 file: `scripts/test_lumos.py:36135` 的表格測試以單一引數呼叫。要傳入 repo_root,spec 沒寫。
- `_detekt_cli_codes` 的 `opaque` 判斷遇到 `@` 開頭就整段不判 T1/T2。這是對的,但表示 `@` 檔內容缺 `--classpath` 只能靠探針抓,而探針失效時見 finding 2。

**9. `comma-path` 的出口只有「改檔名」或整道關閉**
severity: minor
blocking: 否
- spec 段落:範圍第 2 條,「說明改檔名或用既有的整道關閉環境變數 `LUMOS_SKIP_LINT_NEW=1` 推這一次」。
- file: `scripts/lumos:39050` 設了環境變數就回 `off`,連 Python 與 TS 等其他語言的檢查也一起關。且不記 fail-open 帳:`_codeloop_lint_new_step` 只在 `autopass` 時記。
- probe-missing 有放行鍵,comma-path 沒有。

**10. 初始化腳本的規格有缺口**
severity: minor
blocking: 否
- 只涵蓋「套了 Android 外掛的模組」,純 Kotlin/JVM 模組(Clean Architecture 的 `:domain` 很常見)的檔,其 `implementation` 依賴與自身輸出不在聯集裡。
- 未指定任務註冊位置。若註冊在 allprojects,多個模組會各寫一次同一個檔。
- 未指定 `build/lumos/` 相對 Gradle 根還是 git 根。monorepo 子目錄的 Android 專案,兩者不同,命令在 repo_root 找不到檔。
- 「目標版本」沒指定來源,見 finding 2。
- ⚠ 「變體的編譯 classpath、bootClasspath」所用的舊變體 API,AGP 9 是否仍可用我沒能在離線環境查證。spec 沒寫支援的 AGP 範圍,S11 只用一個專案手動驗。

**11. 冒煙加探針的落點沒定義**
severity: minor
blocking: 否
- spec 段落:範圍第 4 條與 S8。
- 閘的探針寫在 `lintbase-<隨機>/probe/` 的暫存目錄。`_lintcheck_smoke_cmd(cmd, stack, repo_root)` 只回命令字串,沒有暫存與清理的位置。
- 冒煙取 `git ls-files` 前 3 支檔,不做逗號路徑判斷。取到含逗號的檔會被報成「冒煙失敗」。
- S8 的「全響」只提基本探針,沒說冒煙是否也驗協程探針。

## 逐節

- frontmatter、白話、PRIOR-ART、RETIRE-IF:已讀,無 finding。外部文件宣稱(detekt.dev、DetektAndroid.kt、discussion #6550)我沒能離線核對,不列。
- 〈用詞〉:基準版/現在版、P1/P2、沒跑到、探針 的定義與程式一致。`{LINT_FILES}` 不是 `{LINT_FILES_CSV}` 的子字串,所以現有的 `in` 判斷不會誤中,已驗。finding 1 到 5、7 出在這一節。
- 範圍 1:守衛測試 `t_lint_files_substitution_has_one_implementation` 是白名單制。新增的探針與逗號檢查函式若提到 `{LINT_FILES_CSV}` 字面或常數,必須加進 ALLOWED。spec 只說兩個佔位符各一處,沒提這件事,但改測試時會當場紅,不列 finding。
- 範圍 2、3、4、5、6、7:findings 見上。
- 〈實務隱患〉:已讀,findings 見上。
- 〈驗收條款〉、〈回退〉、〈天花板〉:findings 見上。其餘已讀無 finding。

## 固定席節點逐條判

- `Systems/pitfalls-lint-adapter`:不影響。本案只改新增告警閘的替換與探針,不動該節點宣稱的「環境不可用不當乾淨」的行為,但 finding 2 提醒新增的失敗路徑仍歸環境類。
- `Systems/linter精選目錄`:不影響合約。該節點沒有合約行,範圍 7 的樣板改寫即可。
- `Systems/lint-declaration-health`:不影響,而且與它「冒煙探針實跑驗規則改到本案做」的否決紀錄同向。需留意該節點「提醒只提醒不改退出碼」,與範圍 6 的「引號包住算格式問題、退出碼 1」是兩條不同通道,不衝突。
- `Systems/android-e2e-acceptance`:不影響。它否決的是 e2e 的 `{{TEST}}` 佔位符,本案是 lint 這邊既有的 `{LINT_FILES}` 同慣例。`shlex.quote` 對一般路徑不加引號,疊兩層的風險只在特殊字元檔名才出現,範圍 6 的格式檢查已擋明顯情形。
- `Issues/推送閘對Android的detekt只記錄不擋`:本案修了「多檔拒跑」這一半。「沒有任何寫法擋得住」在 finding 1、2 的情形下仍成立,結案條件要等這兩個缺口補完。

## 實務隱患逐類

- 登入、權限、付款、個資:無。不碰這些資料。
- 上傳、對外呼叫:無。只在本機跑 detekt 與 Gradle,spec 的「已排除」成立。
- 命令注入與路徑:檔名經 `shlex.quote`,無新增注入面。含 `;` 或 `,` 的檔名是正確性問題,見 findings 3 與 9。
- 執行外部程式碼:`./gradlew -I <腳本>` 在消費專案執行本 repo 分發的 Groovy,屬使用者自己手動跑,不是推送閘自動執行,風險低。
- 資源與時間:型別化 detekt 跑兩次,逾時一律放行,見 finding 2。
- 並行:推送時只讀 `build/lumos/*.args`,不寫。無。
- 不可逆:新增檔、退提交即可,與 spec 一致。

最嚴重 severity 是 major,blocking 共 2 條(findings 1、2)。
