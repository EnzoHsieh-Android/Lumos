severity: blocker

(第 2 輪審查,通才席。r1 已解決的項目不重報。)

**1. 型別宣告命令的判準只看「是 detekt 加逗號佔位符」,沒帶型別資訊的命令也被探針擋,而 P2 新文字正好叫舊用戶改用逗號**
引句:「那套字面判定認成 detekt 指令列、而且帶逗號佔位符的命令。」
引句:「當命令不是 detekt 指令列(含 Gradle 任務接法)或只帶舊 `{LINT_FILES}` 時,新增告警檢查 應 不加探針」
- 重現:`.lumos/lint.json` 寫 `detekt --input {LINT_FILES_CSV} --build-upon-default-config --report sarif:{LINT_SARIF_OUT}`(沒有 `@`、沒有 `--classpath`),推送。
- 這條命令依判準就是型別宣告命令。基本探針的 RedundantSuspendModifier 與 SleepInsteadOfDelay 沒有型別資訊不會響(r1 席位已實測),所以每次推送都 `probe-missing` 擋下。
- 範圍 7 又把帶舊 `{LINT_FILES}` 的 P2 文字改成叫人換成 `{LINT_FILES_CSV}`。照做的人本來沒有型別資訊,換了反而每次被擋,而且被要求先上型別資訊。
- 這與用詞寫的「宣告了要型別資訊,就不能因為型別資訊壞了而安靜放行」自相矛盾。
- 沒有型別參數的逗號命令只想解決多檔拒跑,卻被迫上整套型別資訊,或對探針規則逐條放行。逐條放行會把探針守衛一起關掉。
severity: major
blocking: 是
判準:新規則會誤擋一種合法且被自家提醒文字引導出來的設定。

**2. 「第一個詞找得到執行檔」沒定義怎麼判,對 `$HOME/...`、環境變數前綴、`sh -c` 包裝都判錯**
引句:「跑了但沒產出結果,而且命令第一個詞找得到執行檔(工具有裝)」
- file: `scripts/lumos:37796` 的 `_detekt_strip_prefix` 與 `_detekt_segment_codes` 已把 `FOO=1 detekt …`、`env`、`nice` 等包裝詞和 `sh -c '…'` 都認成 detekt 宣告。判「找得到」若只拿 token 0 去 `shutil.which`,有三種失敗:
  - `JAVA_HOME=/x detekt @… --input {LINT_FILES_CSV}`:token 0 是 `JAVA_HOME=/x`,找不到,判成工具沒裝,自動放行。型別資訊壞了仍然安靜放行,本案要堵的洞原樣保留。
  - `$HOME/bin/detekt …` 或 `~/bin/detekt`:`shutil.which` 不展開變數,判成沒裝,結果同上。
  - `sh -c 'detekt …'`:token 0 是 `sh`,永遠找得到。detekt 真的沒裝時 rc 127、沒有 SARIF,被判 `typeinfo-broken` 擋下,與「工具沒裝照舊放行」相反。
  - `java -jar detekt-cli.jar` 同理,jar 不存在也被判擋。
- `shutil.which` 看的是 lumos 行程的當前目錄與 PATH,命令實際在 `repo_root` 跑。`./detekt` 這類相對寫法會算錯。
- S12 只測「找得到」與「找不到」兩個正例,這些寫法沒有條款。
severity: major
blocking: 是
判準:新分類邊界在已被工具認得的寫法上與 fail-closed 的目標相反。

**3. 路徑含空白的修法在家目錄有空白時失效,且只提到 JDK**
引句:「路徑含空白(例如 Android Studio 內建 JDK、家目錄有空白)時,在 `build/lumos/links/` 建一個不含空白的符號連結指過去,參數檔寫連結」
- 連結放在 Gradle 根底下。家目錄有空白時,專案通常就在那底下。例如 `/Users/John Smith/proj/build/lumos/links/jdk` 本身仍含空白。
- 參數檔寫相對路徑只在 detekt 的當前目錄剛好是 Gradle 根時成立。閘固定在 git 根跑,Gradle 根在子目錄時就不成立。
- 家目錄有空白時,`~/.gradle/caches/...` 下的每個 classpath 項目都有空白,不只 JDK。文字只講一個連結,沒說 classpath 要逐項建、也沒說連結名怎麼避免撞名。AAR 解出來的檔幾乎全叫 `classes.jar`。
- `typeinfo-missing` 對任何含空白的行都擋,這些專案永遠重產永遠被擋。
severity: major
blocking: 是
判準:該修法在文字自己舉的情境(家目錄有空白)下做不到,結果是永久擋下。

**4. 初始化腳本對有 flavor 的模組、AGP 9.x 等沒有輸出,而 `typeinfo-*` 沒有單命令放行,只剩關整道閘**
引句:「每個套了 Android 外掛的模組取指定變體(預設 debug,可用 `-PlumosDetektVariant=<變體>` 換)的編譯 classpath」
引句:「支援範圍:Android Gradle 外掛 8.x(用舊的變體介面,跟 detekt 1.23.8 外掛同一套);9.x 要改用新的變體介面,見回頭條件。」
- 有 productFlavors 的 app 沒有名叫 `debug` 的變體(是 `freeDebug` 之類)。文字沒說模組沒有該變體時怎麼辦:
  - 靜默跳過該模組,classpath 缺了 app 的依賴,但探針靠別的模組的標準庫與協程仍可能過。這正是本案要堵的靜默失效。
  - 全部跳過時參數檔沒有 classpath,永遠 `typeinfo-missing`。
- 今天是 2026-11-05。AGP 9.x 用戶腳本直接失敗,回頭條件到 2027-04 才查。
  - ⚠ 我沒能離線核實 9.x 是否已拿掉舊介面。
- ⚠ 開 Gradle configuration cache 的專案,任務在執行期取 `project.configurations` 可能失敗。文字沒要求印出的指令帶 `--no-configuration-cache`。
- 逃生門:只有 `separator-path` 與 `probe-missing` 有放行鍵。`typeinfo-missing`、`typeinfo-broken`、`timeout` 的出口只剩重產參數檔,或關整道閘(`LUMOS_SKIP_LINT_NEW` 或 `lint_new.gate`),後者連 ruff 等其他命令一起關。
severity: major
blocking: 是
判準:無法修的前提(flavor、AGP 9、空白)讓 fail-closed 變成無單命令出口的永久擋,出口只剩關掉整道閘。

**5. 新增 `scripts/templates/detekt-probe/*.kt` 會被複製進每個消費專案,並被消費專案自己的新增告警閘掃到**
引句:「兩支故意寫錯的 Kotlin 原始碼檔,放在 `scripts/templates/detekt-probe/`(新增;跟既有 `.sql`、`.sh` 範本一樣把別的語言的內容放成檔」
- file: `scripts/lumos:31971`:`_VENDORED_TREE_DIRS = ("scripts/hooks", "scripts/templates")`,安裝時整夾複製進消費專案。
- file: `scripts/test_lumos.py:15314`:`t_vendored_file_list_matches_what_install_ships` 逐檔比對 `_VENDORED_TREE_FILES`。新檔沒登記就紅,計劃的範圍與 lands_in 沒提這張表。
- file: `scripts/lumos:39076`:`_lint_new_verdict` 算 `code_pairs` 時 `_stack_changed_ok(a)` 沒傳 `skip`,不套 `_vendored_skip`。
- 重現:消費專案宣告 `kt` 的 detekt 命令,跑 `lumos update` 把兩支探針 `.kt` 帶進一個提交,推送。這兩支是新增檔、刻意觸發多條規則,在該專案自己的新增告警閘下全算新增告警,更新提交被擋。`.sql`、`.sh` 範本不會被 Kotlin 命令掃到,所以「跟既有範本一樣」的類比不成立。
- 探針是否要隨 `lumos update` 發到消費專案、發了怎麼跳過,計劃都沒決定。
- 另外 `.kt` 在 `scripts/lumos` 的 `_NODEHOME_CODE_EXTS`,是要有家的程式檔。範圍 6 只替初始化腳本登記 about_code,探針檔沒有家,提交前會擋。
severity: major
blocking: 是
判準:新增檔直接讓既有「工具自裝檔清單」測試翻紅,並對消費專案的既有閘產生新的誤擋。

**6. CI 下載步驟與測試對不上**
引句:「下載釘版本的 detekt-cli 1.23.8 與 kotlinx-coroutines-core-jvm jar(從官方發布處,比對寫死的 sha256,不符就讓那一步失敗),放進快取」
- file: `scripts/test_lumos.py:36369`:`t_detekt_shared_config_valid` 與 S10 都用 `shutil.which("detekt")`。步驟只說下載 jar,沒說在 PATH 放名叫 `detekt` 的啟動器。照字面做,S10 在 CI 仍略過,條款寫的「CI 一定有這兩樣,不略過」不成立。
- 本機實測:官方發布處同時有 `detekt-cli-1.23.8-all.jar` 與 `detekt-cli-1.23.8.zip`。`-all.jar` 沒有獨立的 kotlin-stdlib 檔,而 S10 的型別參數檔需要「標準庫加協程 jar 加 JDK」。
- 步驟沒列標準庫 jar,協程 jar 的版本也沒釘。
- S10 目前靠「本機 Gradle 快取」找協程 jar,CI 沒有那個快取。步驟下載到哪、測試怎麼找,沒有寫。
- JDK 路徑若沿用 macOS 的 `/usr/libexec/java_home`,在 ubuntu 上不存在。
- CI 分 prep、shards、gates 數個工作,各自一台機器。步驟加在哪些工作沒寫,沒加的工作 S10 照樣略過。
- 快取命中時若跳過下載步驟,寫死的 sha256 就不再驗證。
severity: minor
blocking: 否
判準:條款宣稱 CI 必跑,但步驟照字面做不到;不破壞既有行為。

**7. 要區分逾時、無輸出並附錯誤輸出,但 `_lint_run_and_parse` 的介面與輸出處理沒改**
引句:「擋下,訊息附 detekt 錯誤輸出的最後幾行。」
- file: `scripts/lumos:38388`、`scripts/lumos:38393`:`_lint_run_and_parse` 把 stdout 與 stderr 都導到 DEVNULL,逾時與無結果都回 `([], False)`。函式註解寫明有兩個既有呼叫點加七處測試依賴這個回傳形狀。
- 另有 `scripts/lumos:59087` 的風險分級路徑也呼叫它。
- 計劃沒說怎麼把「原因、錯誤末幾行」帶出來,也沒說 stderr 要抓回來。`typeinfo-broken` 與 `timeout` 兩類因此沒有實作路徑。
- 抓 stderr 與 stdout 目前被明寫為「不可洩漏」,新做法要重新註明。
severity: minor
blocking: 否
判準:新類別所需資訊在現有函式簽名上拿不到;屬實作缺口,不改變設計語意。

**8. 分批:切分不穩、混用兩種佔位符會重複算、64 KB 的單位未定**
引句:「逗號串超過 64 KB 時,新增告警閘把檔清單切成多批各跑一次、合併結果;探針只放第一批。」
- 同批內的檔互相看得到宣告。base 與 head 各自分批,新增或刪除檔會讓兩邊切點不同。
  - 一個檔在 head 與依賴它的 suspend 呼叫同批、在 base 不同批時,型別規則只在 head 響。這些舊告警被當成新增擋下。
  - 前提是 CSV 超過 64 KB,約數百支檔,屬大型改名。
- 同一條命令同時有兩種佔位符(S1 明列此情形)時,「只對逗號佔位符分批」表示 `{LINT_FILES}` 那份每批都換成完整清單,那個工具的告警被每批重複一次。head 批數比 base 多一批時,舊告警每條多算一次,被當成新增。
- 「64 KB」未說明是字元還是位元組。路徑含中文時一個字 3 位元組,64K 字元可到約 192 KB,超過 Linux 單一參數上限。
  - 而 `scripts/lumos:38388` 的 `Popen` 不在 try 裡,E2BIG 的 OSError 會把整道閘變成 traceback。
  - ⚠ 此項取決於實作怎麼量。
severity: minor
blocking: 否
判準:誤擋與崩潰只在超大差異時出現,放行鍵可繞。

**9. `--jvm-target` 的值怎麼寫沒定義**
引句:「`--jvm-target` 取專案設定的 Kotlin/Java 目標版本,夾在 detekt 1.23.8 支援的 1.8 到 22 之間」
- 本機實測 detekt 1.23.8:`1.8`、`11`、`22` 接受。`8`、`7`、`1.7`、`23` 都得 rc 1、無 SARIF。
- 用 Java 的 majorVersion 寫出 `8` 的腳本,對最常見的 Java 8 專案產出無效參數檔,每次推送 `typeinfo-broken`。
- 只說夾範圍,沒說 `8` 轉 `1.8`、`1.7` 與 `7` 要往上夾到 `1.8`。
severity: minor
blocking: 否
判準:正規化規則缺漏,最常見值就會讓腳本產出壞檔。

**10. 引號格式檢查與 `sh -c` 包裝衝突**
引句:「逗號佔位符被包在引號裡」
- file: `scripts/lumos:37802` 一帶的判定把 `sh -c '…'` 視為合法的 detekt 宣告。包裝寫法裡佔位符本來就在引號內。若檢查是找引號內的 `{LINT_FILES_CSV}`,這種寫法被 lint-check 判成格式問題(退出碼 1)。
- 替換結果若含空白,引號內再出現 `'…'` 會把包裝字串切壞。
- 文字沒說檢查怎麼斷詞。
- ⚠ 檢查實作若只比對獨立 token,就不會誤報。
severity: minor
blocking: 否
判準:格式檢查對一種被其他判定認可的寫法有誤報風險。

**11. 型別宣告命令的逾時與無輸出改成擋,和既有決策 d7、資源鏡頭規則字面抵觸,沒登記例外**
引句:「`timeout`:逾時。一般命令逾時照舊算環境類;型別宣告命令逾時算擋。」
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:125`:d7 的 trade_offs 寫「環境不可用(工具沒裝、逾時、拉不到規則)走自動放行」。同檔 :200 同文。
- 計劃的範圍 9 只說把新類別與放行鍵寫進 pitfalls-code-loop,沒有 `decision-add` 或註記 d7 的例外。
- 同檔 :60 的 RULE 資源鏡頭要求審「逾時誤擋」。基準版與現在版共用同一個 `budget_end`,基準版跑去 280 秒時,現在版只剩 20 秒就逾時,新規則下變成硬擋。
- 原本是自動放行。
severity: minor
blocking: 否
判準:決策紀錄與新行為對不上,逾時誤擋路徑已有實證前提。

**逐條判附帶節點**
- `Issues/推送閘對Android的detekt只記錄不擋`:本案就是它的修法,不影響其記載。
- `Systems/pitfalls-lint-adapter`:adapter 的「讀不懂就 rc2、不寫結果檔、閘視為跑不動」只涉及 dart/sqlfluff/stylelint 轉接。新分類只套逗號型別宣告命令,不影響。
- `Systems/linter精選目錄`:about_code 加入初始化腳本沒問題。標準接法樣板與「只記錄不擋」的說明按範圍 9 同步,與其他發現無關。
- `Systems/android-e2e-acceptance`:否決把值加 shell 引號的理由是使用者可能已自己包引號。本案沿用 `shlex.quote`,並以範圍 7 的格式檢查把雙重引號擋在宣告階段。除 #10 的 `sh -c` 情形外不影響。
- `Systems/pitfalls-code-loop`:見 #11。
- `Systems/lint-declaration-health`:佔位符替換只准一處的守衛,範圍 1 已列要改寫。「沒有修法所以不擋」的 WHY 因本案提供修法而不矛盾。不影響。

**實務隱患逐類**(依本功能碰到的風險類)
- 逾時誤擋與資源耗用:見 #11 與 #8。基準版與現在版共用預算,命令行長度與分批單位也有缺口。
- 工具自裝檔與消費專案:見 #5。
- 安裝來源與外部下載:見 #6,sha256 比對本身合理。
- 資安、金流、對外送出、不可逆:無。計劃已排除,初始化腳本只讀建置設定,探針是固定檔,退回提交即恢復。

已讀,無 finding 的節:〈用詞〉的「基準版、現在版」「P1、P2」「沒跑到」「逗號佔位符」「型別參數檔」;〈範圍〉第 3、4、8 以外(其餘已在上列涵蓋)、〈不做〉、〈回退〉、〈天花板〉、REVISIT 三行。

總結:最嚴重 severity 為 major(無 blocker),blocking 共 5 條(#1、#2、#3、#4、#5)。
