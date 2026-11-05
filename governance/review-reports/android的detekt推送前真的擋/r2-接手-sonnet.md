severity: blocker

我讀完 r2 快照、r1 兩份收貨檔,並對照 `scripts/lumos`、`.github/workflows/ci.yml`、`kotlin-idioms/SKILL.md`、`linter精選目錄.md`、`android.yml` 與六個附加節點逐條查過。沒有實際跑 Gradle 或 detekt,所以撞牆步驟都是從程式碼與文字推出來的。

### 撞牆 finding

**1. 消費專案的 CI 沒有型別參數檔,新規定會讓每次 push 的 CI 都紅,而且連「工具沒裝就放行」也被蓋掉**
severity: blocker
blocking: 是
判準:消費專案照 doctor 給的 CI 範本接上後,每次 push 都被擋,而且 spec 沒給 CI 這邊的出口。
引句:「就不跑、擋下,訊息給重新產生的指令」
引句:「第一個詞找不到執行檔時照舊算環境類、自動放行(工具沒裝)」
引句:「本 repo 的 CI 加一步,下載釘版本的 detekt-cli 1.23.8 與 kotlinx-coroutines-core-jvm jar」
- 撞牆步驟:
  1. 消費專案(Android)照 `.github/workflows/ci.yml` 的「code-loop gate」那步抄進自己的 CI,lint.json 照新樣板宣告。
  2. push 後 CI 跑 `lumos code-loop check`。這條路一定會走新增告警閘,沒有 CI 例外。
  3. CI 的 checkout 沒有 `build/lumos/detekt-typeinfo.args`(`build/` 不進版控),所以判成 `typeinfo-missing` 擋下。
  4. 訊息叫人跑 `./gradlew -I … lumosDetektTypeinfo`,但 CI 沒有 Android SDK,而且這個任務還要先編譯所有模組。
- 現況是 detekt 沒裝就算環境問題放行。spec 說參數檔檢查在「跑之前」,所以 CI 沒裝 detekt 時走哪一邊,spec 沒講(S12 沒覆蓋)。
- spec 範圍 8 只處理本 repo 自己的 CI。
- file: `scripts/lumos:68031`——`_codeloop_lint_new_step` 在 `code-loop check` 裡不看 tier、不看是否在 CI。
- file: `scripts/lumos:226`——判 CI 的 helper 存在,但新增告警閘沒用它。

**2. 訊息叫人「改用 `{LINT_FILES_CSV}`」,人照做後被 probe-missing 擋下,訊息卻沒說要加 `@參數檔`**
severity: major
blocking: 是
判準:spec 自己給的修法會把使用者帶進一個照訊息做也出不來的迴圈。
引句:「帶舊 `{LINT_FILES}` 的 detekt 指令列,P2 的文字改成」
引句:「命令用 `@<路徑>` 讀參數檔、而那個檔(相對專案根)不存在 → 提醒先跑初始化腳本,附指令。」
引句:「印產生型別參數檔的指令與放行指令」
- 撞牆步驟:
  1. 舊宣告是 `detekt --input {LINT_FILES} -cp … --jdk-home …`(或根本沒型別參數),`lumos lint-check` 印 P2「改用 `{LINT_FILES_CSV}`」。
  2. 人只把佔位符換掉。命令帶逗號佔位符,所以算「型別宣告命令」,推送時探針加進輸入。
  3. 命令沒有 `@build/lumos/…`,探針規則不響,判 `probe-missing`。
  4. 訊息只印「產生型別參數檔的指令與放行指令」。人跑了 Gradle,命令仍然沒讀它,下次還是被擋。
- 範圍 7 的「`@` 檔不存在」提醒只在命令已經有 `@` 時才出現。
- 只想用不要型別的 GlobalCoroutineUsage、本來就不想接型別的專案,也被迫逐條放行四條探針規則。

**3. 「訊息附 detekt 錯誤輸出最後幾行」做不到:現行執行函式把 stderr 丟掉,回傳值也分不出失敗種類**
severity: major
blocking: 否
判準:spec 的 S12 要求的行為,在 spec 範圍裡沒有列出要改的那支函式。
引句:「擋下,訊息附 detekt 錯誤輸出的最後幾行」
- 撞牆步驟:
  1. 例如 `brew upgrade detekt` 升到 2.x,或 `--jvm-target` 超出範圍,命令跑完沒有結果檔。
  2. 判 `typeinfo-broken`。訊息「最後幾行」是空的,因為 `_lint_run_and_parse` 把 stdout 與 stderr 都導到 DEVNULL。
  3. 修法只剩「重產參數檔」,而重產沒用。
- 同一個函式只回 `(claims, ok)`。逾時、沒結果、工具缺這三種現在都是 `ok=False`,到 `_lint_new_verdict` 一律寫成 `kind: env`,所以 spec 要的五個新類別沒有通道傳出來。
- file: `scripts/lumos:38393`——stdout 與 stderr 導到 DEVNULL(那行的上方註解寫明是為了不污染 `--json`)。
- file: `scripts/lumos:39137`——`ok` 為假時固定寫成 `{"kind": "env", …}`。
- 範圍 1~9 都沒提要改 `_lint_run_and_parse` 的回傳形狀與 stderr 處理。

**4. `typeinfo-missing`、`typeinfo-broken`、`timeout` 沒有針對性的出口,唯一的出路是關掉整道閘**
severity: major
blocking: 否
判準:`separator-path` 與探針都有放行鍵,這三類沒有,但它們最容易在 Gradle 建不起來時觸發。
引句:「宣告了要型別資訊,就不能因為型別資訊壞了而安靜放行」
- 撞牆步驟:
  1. 分支裡某個模組暫時編不過、機器上沒有 Android SDK,或離線。
  2. `lumosDetektTypeinfo` 要先依賴編譯任務,所以跑不出參數檔。
  3. push 被 `typeinfo-missing` 擋下。
  4. 唯一能做的是 `LUMOS_SKIP_LINT_NEW=1` 或把 `lint_new` 設成 off。那會同時關掉同專案其他 linter(ktlint、eslint 等)的新增告警檢查。專案規則禁止 `--no-verify`。
- 前例:`android-e2e-acceptance` 節點有 PITFALL,記載出口排在讀設定之後,導致照訊息設環境變數照樣被擋。這案一樣沒定義出口。

**5. 變體預設是 `debug`,有 product flavor 的專案會得到殘缺的 classpath,而 spec 的檢查全都過得了**
severity: major
blocking: 否
判準:沒有 `debug` 變體的模組被悄悄略過,探針與路徑存在檢查都驗不出來,最後只是規則漏報。
引句:「每個套了 Android 外掛的模組取指定變體(預設 debug,可用 `-PlumosDetektVariant=<變體>` 換)的編譯 classpath」
- 撞牆步驟:
  1. app 模組有 flavor,變體叫 `prodDebug`,沒有叫 `debug` 的變體,但 library 模組有 `debug`。
  2. 初始化腳本只收到 library 模組的類別,app 自己的輸出與 Compose 相關依賴不在 classpath。
  3. 參數檔非空、路徑都存在,探針只靠標準庫與 JDK,所以通過。
  4. `ForbiddenMethodCall` 禁 `collectAsState` 對 app 的檔悄悄不響,也沒有任何訊息指向 `-PlumosDetektVariant`。
- 天花板 2 只說「少一個不相干的套件照樣過」,沒提變體對不上這種整個模組缺席的情況。

**6. 新工作樹每次都要完整編譯一輪,而 spec 沒給較輕的路,參數檔也不可搬**
severity: major
blocking: 否
判準:全域規則要求每個任務開獨立工作樹,所以這個成本每個任務都付一次。
引句:「新工作樹與 clean 之後必擋」
引句:「任務先依賴這些編譯任務」
- 撞牆步驟:
  1. `git worktree add ../x -b x`,改一支 kt 檔,push。
  2. `typeinfo-missing` 擋下。
  3. 跑重產指令,等於把全部 Android 模組冷編譯一輪才印得出 classpath(傾印依賴本身不需要這步)。
  4. 若從別的工作樹把參數檔抄過來,檔裡寫的是那一棵 `build/` 的絕對路徑,路徑存在檢查會過,但 detekt 解析的是另一棵樹的舊編譯輸出,沒有任何警示。
- 實務隱患只寫「刻意的」,沒有成本估計,也沒有只放依賴 jar 的輕量選項。

**7. 訊息裡的重產指令怎麼算出 gradle 目錄與腳本路徑,spec 沒定義**
severity: minor
blocking: 否
判準:monorepo 或自訂參數檔路徑時,訊息印出的指令會是不存在的檔。
引句:「預設 `build/lumos/detekt-typeinfo.args`(相對 Gradle 根)」
- 撞牆步驟:
  1. Gradle 根在 `android/` 子目錄(範圍 7、S5、S12 都要求印重產指令)。
  2. 訊息若印 `./gradlew -I … lumosDetektTypeinfo`,在 git 根執行會找不到 `gradlew`。
  3. 命令裡的 `@` 路徑若不是預設值,lumos 反推不出 gradle 目錄。
- 初始化腳本路徑也一樣:`scripts/lumos` 目前沒有任何取得 `configs/detekt` 路徑的 helper。`LUMOS_HOME` 若自訂,訊息印預設的 `$HOME/harness/…` 會導向不存在的腳本(`scripts/lumos:31884` 只在安裝流程裡解析來源路徑)。
- 判準:⚠(未見 spec 規定算法,實作可能剛好處理)

**8. 落地後兩份文件仍會互相矛盾**
severity: minor
blocking: 否
判準:範圍 9 只列了樣板與〈型別資訊〉一節,其餘仍寫「只記錄不擋」的句子沒被點名。
引句:「kotlin-idioms 慣例文件〈型別資訊〉一節改寫」
- 撞牆步驟:有人讀 `skills/kotlin-idioms/SKILL.md` 第 12 行與機檢接線段,看到「所有 detekt 規則推送前的新增告警檢查目前都只記錄、不擋」,而〈型別資訊〉說會擋。
- 還有這些沒被點名:
  - `linter精選目錄.md` 的 KEY(第 20 行)與表格(第 52 行)。
  - `configs/detekt/android.yml` 開頭的第②點與用法示範行(範圍 7 只提了第①點)。
  - `Android的detekt規則說實話_計劃` 的判定表。`scripts/lumos:37724` 的註解稱它是單一來源,但 P1、P2、T1 的語意都要改,範圍 9 沒列。
- 其中 kotlin-idioms 與 linter精選目錄各有一條綁在 `status=done` 的 REVISIT,到那次推送會被機械點名;android.yml 與判定表沒有這種機制。

**9. 設定快取(configuration cache)開著的專案,初始化腳本可能直接失敗**
severity: minor
blocking: 否
判準:⚠ spec 完全沒提,沒有實測。
- 撞牆步驟:專案設 `org.gradle.configuration-cache=true` 且 problems 為 fail,跑 `./gradlew -I <腳本> lumosDetektTypeinfo`。若任務動作在執行期讀 `project` 或 AGP 變體物件,會被擋。
- S11 只驗「多模組、AGP 8.x」,沒有這個維度。

### 實務隱患逐類

- **金流:**無。不碰付款或點數,跟 spec 的排除一致。
- **對外送出:**無。只在本機與 CI 跑 detekt 與 Gradle。CI 那步下載 jar 且比對 sha256,是下載不是送出。
- **不可逆:**無。新增檔與佔位符,退提交即回原狀。
- **資安:**無。只讀建置設定、寫 `build/lumos/` 與符號連結。
- **併發與多會談:**有,見 finding 6(工作樹間參數檔不可搬)。`.lumos/lintbase-<隨機>/` 沿用既有隨機目錄,沒有新的碰撞。
- **效能與資源:**有,見 finding 6(冷編譯)。另外 `budget_sec` 預設 300 秒是整道閘共用,基準版與現在版各跑一次帶型別的 detekt 後逾時會擋,spec 只寫「教人調」,沒有調整預設值。
- **版本相容:**有,見 finding 3。`brew install detekt` 沒釘版本,spec 的 `@參數檔` 與 `--jvm-target` 行為是 1.23.8 專屬,升版後沒有檢查,也看不到 stderr。
- **CI 差異:**有,見 finding 1。
- **暫存清理:**無新問題。探針複製進既有的 `.lumos/lintbase-*`,由 `finally` 的 `shutil.rmtree` 清掉。

### 附加節點逐條判

- `Issues/推送閘對Android的detekt只記錄不擋`:不影響。spec 的修法對應它的「什麼條件算修好」,結案寫在範圍 9。
- `Systems/pitfalls-lint-adapter`:不影響。無宣告的 regex-only 不變,「全部降級就判沒被檢查」不變。第 87 行 detekt 例外那句會過時,屬 finding 8 同類。
- `Systems/linter精選目錄`:無合約。樣板與說明要改,見 finding 8。
- `Systems/android-e2e-acceptance`:不影響。它否決的是「把值加 shell 引號換進佔位符」。逗號佔位符走既有 `{LINT_FILES}` 同一個引號慣例,疊兩層用格式檢查擋,理由成立。它的 PITFALL(出口排在讀設定之後被擋)是 finding 4 的前例。
- `Systems/pitfalls-code-loop`:不影響行為合約,但新增的擋下類別會經過 `_codeloop_lint_new_step`,而這一步在 CI 也跑,見 finding 1。
- `Systems/lint-declaration-health`:不影響。範圍 1 已把「只准一處替換」的白名單守衛列入。doctor [F] 與 lint-check 共用靜態驗證,所以引號包住逗號佔位符會讓 `doctor --ci` 變紅,這是預期行為。

### 各節

- 頂部 frontmatter、白話、PRIOR-ART、RETIRE-IF:已讀,無 finding。
- 用詞:見 finding 1、2、3、5、7。
- 範圍:見 finding 2、3、8。
- 不做:已讀,無 finding。
- 驗收條款:見 finding 1(S12)與 3(S12)。S11 是 manual 條款,缺 flavor 與 config cache 的情境(finding 5、9)。
- 回退、天花板、REVISIT、審計修正紀錄:已讀,無 finding。

總結:最嚴重 blocker,blocking 共 2 條(finding 1、2)。
