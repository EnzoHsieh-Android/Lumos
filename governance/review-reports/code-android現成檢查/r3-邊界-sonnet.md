severity: major

(測試總檔 `-k android` 120 秒內沒跑完,轉到背景,我沒等結果,以下全是直接造輸入跑函式得到的。臨時檔放在 `/tmp/lumos-seat-work/code-android現成檢查/邊界-sonnet/`。)

**F1 — `build`/`check` 只要是整個「詞」就算跡象,只要檔裡出現 gradle 字樣,`needs: build`、`name: build` 這類非 lint 的詞就讓提醒消失(漏報)**
severity: major
blocking: 是
file: `scripts/lumos:39026`(`_android_ci_lint_evidence`)
引句:「                if gradle and _ANDROID_UMBRELLA_WORD.fullmatch(w):」
- 輸入:Android 專案(`build.gradle.kts` 有 `com.android.application`),`.github/workflows/ci.yml` 沒有任何 lint:
  ```
  jobs:
    build:
      steps:
        - uses: actions/setup-java@v4
          with:
            cache: gradle
        - run: ./gradlew assembleDebug
    release:
      needs: build
      steps:
        - run: echo done
  ```
- 實際輸出:`_lint_android_ci_advisories` 回 `[]`,A1 沒印。
- 另外三種寫法同樣讓提醒消失:`name: build`、`name: "build"`、`run: test -f check`(各搭一行 `./gradlew assembleDebug`)。
- 原因:判斷單位是整檔的「詞」,不是「gradlew 那一行的任務」。`needs: build`、`cache: gradle` 在 GitHub Actions 非常常見,所以沒接 lint 的專案常被判成有跡象。
- 計劃承認寫了卻沒跑會少印,但那指的是 `-x lint` 這類 lint 字樣。這裡是完全不相干的詞。
- 修法:`check`/`build` 只在含 gradle 字樣的同一行(或續行合併後的同一邏輯行)才算,不要整檔。
- 未改成這樣前,`needs`/`name` 這類非命令欄位的值要排除。

**F2 — `name: lint` 這類 job 或 workflow 名稱的 `lint`,在只有 kotlinter 的專案也算跡象(漏報)**
severity: minor
blocking: 否
file: `scripts/lumos:39024`
引句:「                if _ANDROID_LINT_WORD.fullmatch(w) and not _ANDROID_LINT_NONCHECK.fullmatch(w.rsplit(":", 1)[-1]):」
- 輸入:`jobs:\n  j:\n    name: lint\n    steps:\n      - run: ./gradlew lintKotlin\n`
- 實際輸出:A1 不印。`lintKotlin` 本身已被 NONCHECK 排除,是 `name: lint` 這個詞救了它。
- 這是計劃已承認的取捨(job 名也算),所以只標 minor。
- `./gradlew ktlintCheck --info lint` 同樣不印。

**F3 — 建置檔 `lint { }` 偵測錯過同一行或點號寫法;有 lint 設定卻被提醒(誤報)**
severity: minor
blocking: 否
file: `scripts/lumos`(`_ANDROID_LINT_CONFIG`)
引句:「+_ANDROID_LINT_CONFIG = re.compile(r"^[ \t]*(?:lint|lintOptions)[ \t]*\{", re.M)」
- 輸入:
  - `app/build.gradle`:`android { lint { abortOnError false } }`
  - `app/build.gradle.kts`:`android { lint.abortOnError = false }`
  - 把 lint 設定放在 `build-logic/convention/.../*.kt`(只掃 build.gradle 類的檔,掃不到)
- 實際輸出:三個都印 A1(其餘條件皆無跡象時)。
- 屬少見寫法。`lint-baseline.xml` 與 `lint {` 獨立成行的寫法都正確。

**F4 — CI 設定檔只認固定檔名,composite action 與 GitLab `include:` 的檔讀不到(誤報)**
severity: minor
blocking: 否
file: `scripts/lumos`(`_ci_config_paths`、`_CI_OTHER_CONFIG_FILES`)
引句:「 _CI_OTHER_CONFIG_FILES = (".gitlab-ci.yml", "bitrise.yml", ".circleci/config.yml", "Jenkinsfile", "azure-pipelines.yml")」
- 輸入一:`.github/workflows/ci.yml` 只有 `uses: ./.github/actions/lint`,`.github/actions/lint/action.yml` 內是 `run: ./gradlew lintDebug`。
- 輸入二:`.gitlab-ci.yml` 只有 `include: - local: ci/lint.yml`,`ci/lint.yml` 內是 `./gradlew lintDebug`。
- 實際輸出:兩種都印 A1。
- A1 文字已寫「CI 在別的系統或任務藏在腳本裡也會印」,有自述限制,所以只標 minor。

**F5 — A3 的外掛相對路徑一律以 repo 根解析,命令自己 `cd` 後的相對路徑被誤判不存在(誤報)**
severity: minor
blocking: 否
file: `scripts/lumos`(`_android_plugin_missing`)
引句:「            pp = Path(repo_root) / pp」
- 輸入:repo 根下有 `tools/x.jar`,命令 `cd tools && detekt-cli --plugins x.jar`,或 `(cd tools; detekt-cli --plugins x.jar)`。
- 實際輸出:`_android_plugin_missing` 回 True,印 A3(實際檔案在)。
- 另有一例:`FOO=tools detekt-cli --plugins $FOO/x.jar`,而 shell 環境剛好也有 `FOO=zzz`,同樣回 True。命令前綴被剝掉後,用的是環境裡的值。
- 這類寫法少見。

**F6 — 建置檔掃描上限(200 支、1MB)截斷後,後面的 lint 區塊讀不到(誤報)**
severity: minor
blocking: 否
file: `scripts/lumos`(`_android_build_texts`)
引句:「    取前 max_files 支、每支讀前 max_bytes。」
- 輸入一:250 個 `mNNN/build.gradle.kts`,只有 `m249` 有 `android { lint { } }`。
- 輸入二:一支 `app/build.gradle.kts` 前面有一行 1MB 的註解,`lint { }` 在後面。
- 實際輸出:兩個都印 A1。
- 排序是 (層數, 路徑),根目錄的檔先讀,所以根模組不會被擠掉。
- 觸發條件極少見。

**F7 — Jenkinsfile 行尾 `//` 註解裡的 lint 字樣被當跡象(漏報)**
severity: minor
blocking: 否
file: `scripts/lumos`(`_android_ci_lint_evidence`)
引句:「        lines = [ln for ln in lines if not ln.lstrip().startswith("//")]」
- 輸入:Jenkinsfile 內容 `sh './gradlew assembleDebug' // lint later`
- 實際輸出:有跡象,A1 不印。
- 只略過「`//` 開頭的整行」,行尾 `//` 沒處理;`/* */` 區塊也沒處理。
- 偏向少印,符合證據模型的取向。

**逐條驗收結果,沒問題的**
- 該算跡象的都正確:
  - GitHub Actions、GitLab、Circle、Azure 的 `lint`、`lintDebug`、`:app:lintRelease`、`gradle lint`、`gradlew.bat lint`。
  - Bitrise 的 `android-lint@`、多行續行 `\`、YAML `|` 區塊。
  - Jenkins 的單引號與雙引號 sh。
  - 帶 gradle 字樣檔裡的 `build`。
  - `lintAnalyzeDebug`、`lintFixtureDebug`。
- 不該算的都正確:
  - `lintKotlin`、`lintKotlinMain`。
  - `ktlintCheck`、`detekt`、`spotlessCheck`。
  - 未展開的 `${{ matrix.task }}`。
  - 純 `-Plint-baseline`。
  - Jenkins 整行 `//` 註解。
  - `lint:` 這種 job 鍵(帶冒號)。
- `_ci_strip_comment` 對 `echo "#" && ./gradlew lint` 與 `http://x/#a` 都沒壞。
- A3 展開與判斷,這些都正確:
  - `$(pwd)`、反引號、`${HOME:-/x}`、`$` 殘留、引號包住的空白路徑。
  - 符號連結指向存在的檔(不報)、懸空連結(報)、指到資料夾(報)。
  - `--plugins=`、`-p`、逗號分隔多支。
  - `sh -c '…'` 內層。
  - 傳入 `None`、整數、list 都不丟例外。
- 建置檔掃描:
  - Groovy 字串裡的 `//`(`url 'https://…'`)沒把後面的 `com.android.application` 吃掉。
  - TOML 字串裡的 ` #`(`"a #b"`)被引號保護。
  - TOML 行尾 `# c` 註解被剝掉。
  - 根模組排序優先。
- 效能:`_detekt_walk_segments` 對單一逗號串(約 16000 支外掛)耗時超線性(16000 支 0.65 秒),20 萬支約 99 秒。這是既有的切段程式,不是本輪修補引入,現實輸入不會碰到。
- 圖譜鏡頭:範圍在這個 repo 算不出固定席,我改讀 `Systems/lint-declaration-health.md` 與 `Systems/linter精選目錄.md` 的修補差異。新增的 WHY 行與目錄文字和程式行為一致。唯一落差是 F1 的「提到 gradle 的設定裡的 check 或 build」這句,寫的是整檔詞,程式也確實是整檔詞,但這個語意本身就是 F1 的來源,不是圖譜寫錯。

總結:最嚴重是 F1(`needs: build`、`name: build` 加 `cache: gradle` 讓沒接 lint 的專案不被提醒),會擋 1 條;其餘 F2 到 F7 皆為罕見寫法或計劃已承認取捨的 minor,不擋。
