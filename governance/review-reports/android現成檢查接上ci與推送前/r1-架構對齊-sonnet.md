severity: major

我只讀了快照和既有程式,沒改任何檔。對照過的既有檔:`scripts/lumos`、`.github/workflows/ci.yml`、`configs/detekt/android.yml`、`Systems/linter精選目錄.md`、`Systems/lint-declaration-health.md`、`Systems/kotlin規則包.md`。

## 1. 分層與依賴方向

新函式 `_lint_android_ci_advisories(config, repo_root)` 的位置和呼叫方式跟 detekt 提醒同形。它新增在 `scripts/lumos` 的提醒區旁。呼叫端是 lint-check(`scripts/lumos:39114`)和 doctor [F] 段(`scripts/lumos:4172`)。它只讀本機檔,不碰別的層。沒有跨層直呼。

但它要自己判斷「是不是 Android 專案」,而這件事 repo 裡已經有一套做法。

### F1
severity: major
blocking: 是
引句:「掃的檔:專案根目錄與下一層資料夾的上述建置檔與 `gradle/libs.versions.toml`,每支最多讀 1 MB」
對照:`scripts/lumos:38116-38118`(`_KT_BUILD_FILES`、`_KT_BUILD_ANDROID`)、`scripts/lumos:38132-38135`(`_kt_build_candidates`)、`scripts/lumos:38157`(用 `_KT_BUILD_ANDROID.search` 判 android)
- 既有的 Android 認定,是由 `_kt_build_candidates` 從某支 `.kt` 檔往上找建置檔,再用 `_KT_BUILD_ANDROID` 比對。比對的字樣是 `com\.android\.`、`libs\.plugins\.android` 和 `android {` 區塊。
- 計劃另外定義了一套:只掃根目錄加下一層,多讀 `libs.versions.toml`,字樣是 `com.android.application/library` 和別名。它還自帶 1 MB 與 200 支的上限。
- 計劃沒有提到既有那套,也沒說明為什麼不能重用或抽共用函式。同一個「Android 專案」概念會有兩個判準,日後會漂移。
- ⚠ 兩套的語意不完全相同:既有的含 `android {` 區塊,計劃的只認 application/library 外掛。判斷是否「第二種做法」要看編排者認不認這個差異是刻意的。我判 major,因為計劃沒有交代理由。

## 2. 命名與錯誤處理

提醒代號、文字表、`--json`、doctor 提醒的大方向跟鄰居一致:
- 代號用 A1、A2,沿用 T/G/P 的「字母加數字」。
- 文字表自帶,對應 `_DETEKT_ADVICE_ORDER` 和 `_DETEKT_ADVICE_TEXT`(`scripts/lumos:38798-38799`)。
- `--json` 放進同一個 `advisories` 清單,對應 `scripts/lumos:39116`。
- doctor [F] 另起一則提醒,對應 `scripts/lumos:4172-4178`。
- 讀不了的檔當沒有,對應 `scripts/lumos:38926-38929` 的 `except OSError: continue`。
- 不改退出碼,對應 `scripts/lumos:39114` 的註解。

有兩處沒寫清楚。

### F2
severity: minor
blocking: 否
引句:「lint-check 的文字與 `--json` 的 `advisories` 清單接在 detekt 提醒之後」
對照:`scripts/lumos:39133-39142`(`_lint_detekt_print` 標題寫死「detekt 宣告實際會怎樣」)、`scripts/lumos:39025-39027`(條目格式 `[副檔名 第 N 條] 代號:一句` 與 `[CI] T4:`)
- 現有的 `_lint_detekt_print` 標題、「為什麼在意」和「細節去哪看」都是寫死 detekt 的。計劃要另起標題,但沒說是新增一支印出函式,還是把現有的泛化。
- A1、A2 條目的前綴格式(`[CI] A1:` 還是別的)也沒定。
- 結構是對的,只是格式規格缺了,實作時容易各寫各的。

### F3
severity: minor
blocking: 否
引句:「workflow 檔沿用 T4 的讀法(不設上限,同 `_detekt_ci_has_typed_task`)」
對照:`scripts/lumos:38915-38931`
- 計劃說「沿用讀法」,沒說是呼叫共用 helper,還是在新函式裡複製一份 `iterdir` 加 `suffix` 判斷加 `read_text` 的迴圈。
- 既有的 `_detekt_ci_has_typed_task` 是寫死 detekt 比對的,不能直接共用。複製迴圈就多一份 workflow 讀取。
- 建議在計劃裡寫明抽一支共用的 `_ci_workflow_texts(repo_root)`。

## 3. 第二種做法

除了 F1,還有一個。

### F4
severity: major
blocking: 是
引句:「(本機目錄,新增慣例、不進 repo)」
對照:`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:124`(「外部工具一律裝進套件管理器,嚴禁易失位置」)、`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:130`(既有命令引用 `$HOME/harness/lumos-toolchain/configs/...`)
- 既有慣例有兩條:外部工具走 `brew install detekt`,共用設定走 clone 下來的 repo 路徑。
- 計劃要人手動下載外掛 jar,放進 `$HOME/.local/share/lumos/detekt-plugins/`,這是第三種來源:既不是套件管理器,也不是 repo 路徑。計劃自己也承認是「新增慣例」。
- 沒說明為什麼不能放在 repo 的 `configs/` 隨 clone 分發,或為什麼沒有 brew 之類的管理法。
- 沒說外掛升版由誰盯。`Systems/lint-version-watch` 現有的盯版機制沒被提到。
- 外掛 jar 沒有套件管理器可用,新位置有它的理由。但它是新慣例,應該在計劃裡寫成有決策紀錄的設計,而不是順帶一句。
- ci.yml 那邊「下載加比對 sha256」沿用既有做法(`.github/workflows/ci.yml:150-165`),這部分一致,不算第二種。

## 4. 落點

三篇 lands_in 都已存在,且各自管到要改的檔,不需要另開新篇。

| 要改的檔 | 家 | 在 lands_in 裡 |
|---|---|---|
| `scripts/lumos` | `lint-declaration-health`(about_code 列 `scripts/lumos`,`lint-declaration-health.md:36`) | 是 |
| `configs/detekt/android.yml` | `linter精選目錄` | 是 |
| `skills/kotlin-idioms/checks-catalog.md` | `kotlin規則包` | 是 |
| `.github/workflows/ci.yml` | `安全證據閘`、`筆記內容閘`、`存量漂移守衛`、`bound-tests-gate` | 否 |

### F5
severity: minor
blocking: 否
引句:「本 repo 的 CI(`.github/workflows/ci.yml` 裝 detekt 那一步)照 detekt 的做法多下載 compose-rules 0.4.28 外掛並比對同一個 sha256」
對照:`.github/workflows/ci.yml:150-165`
- `ci.yml` 的家是上表那四篇,沒有一篇在 lands_in。
- 專案規則是「改到的每支檔都得先有家」,而且說明要寫進該檔的家。這一步的說明沒有落點。
- 建議在 lands_in 補上 `ci.yml` 實際的家,或在計劃寫明這一步的說明寫進哪一篇。
- `kotlin規則包` 的負責範圍寫了「不負責 detekt 共用設定」,所以 compose-rules 的 detekt 面不該落在它那邊。目前計劃只讓它承接 `checks-catalog.md`,沒有問題。

⚠ 交編排者:型錄通電批次改由「一次性腳本」依欄位內容判,而且「腳本不進 repo」。`configs/ast-grep/kotlin-android/check.py:91,161` 對通電批次欄只驗非空。口徑只寫在〈輸入與口徑〉的文字裡,沒有機器守衛。型錄裡確實有程式撈欄位的前例(〈待查證〉一節)。我判不準這算不算第二種做法,所以不列為 finding。

不對齊共 5 條,其中 major 2 條
