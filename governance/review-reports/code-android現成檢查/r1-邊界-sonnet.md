severity: major

以下用 Python 直接呼叫函式,並用真實 repo 跑 `lint-check --json` 實測。另外跑了 `-k kt_catalog_batch4`(12 passed)和 `-k lint_android_ci`(38 passed),所以這些洞都是現有測試沒蓋到的。

**F1**
severity: major
blocking: 是
file: `scripts/lumos` 的 `_android_ci_has_lint_task`(diff 第 275–278 行)只逐行判斷,一行裡沒有 `gradlew` 就跳過。
引句:「if not re.search(r"gradlew|\bgradle[ \t]|\barguments:", line):」
輸入:`.github/workflows/ci.yml` 寫成 YAML 常見的反斜線續行:
```
- run: |
    ./gradlew \
      --no-daemon \
      lintDebug
```
再加 `build.gradle.kts` 裡的 `id("com.android.application")`。
實際輸出:`lint-check --repo <dir> --json` 的 advisories 帶 `[CI] A1:專案是 Android,但 CI 設定檔…裡找不到 Android Lint 任務`。續行的 `lintDebug` 那一行沒有 `gradlew`,被略過。在 cwd=/ 和 cwd=repo 各跑一次,結果相同。
同類寫法也會誤報,函式直接回 False:`arguments: |` 換行後才寫 `lintDebug`,以及 `./gradlew assembleDebug \` 下一行接 `:app:lintDebug`。
影響:最常見的多行 CI 寫法會誤報「沒接 Android Lint」,使用者會去補一個已經存在的步驟。

**F2**
severity: minor
blocking: 否
file: `scripts/lumos`(diff 第 279–285 行)切詞後只比對詞本身,不看前後脈絡。
引句:「for tok in re.split(r"[\s'\"`,;&|()\[\]{}=]+", line):」
輸入與實際輸出(皆回傳 True,也就是判成有接):
- `./gradlew check -x lint` 和 `./gradlew build -x lint`:明確排除 lint 卻被判成有接,A1 漏報。
- `./gradlew -Pci=lint test`:`=` 後面的 `lint` 被當成任務。
- `./gradlew test --info # check`:註解裡的詞被計入。
- `# ./gradlew lintDebug`:整行被註解掉卻判成有接。
- `./gradlew clean assemble && cd build`:`cd build` 的 `build` 被算成任務。
影響:這些是少見寫法,結果是漏報。

**F3**
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_lint_android_ci_advisories`(diff 第 333–336 行)用目前工作目錄判斷檔案在不在。
引句:「if not Path(pth).is_file():」
輸入:宣告為 `detekt --input {LINT_FILES_CSV} --plugins tools/p.jar …`,`tools/p.jar` 存在於 repo 根目錄。
實際輸出:
- 從 cwd=repo 執行:不印 A3。
- 從 cwd=/ 執行 `lint-check --repo <dir>`:印 A3。
命令實際是用 `cwd=repo_root` 跑的(`scripts/lumos:39714`)。
同一支函式還有兩個小洞:
- `$XDG_DATA_HOME/x.jar` 這類 `$HOME` 以外的環境變數不展開,會被當成不存在而誤印 A3。
- `sh -c 'detekt --plugins $HOME/x.jar'` 這種包裝寫法,`_android_plugin_paths` 回空清單,A3 漏報;但專案本來就接受 `sh -c` 包裝。

**F4**
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_android_build_texts`(diff 第 244–269 行)只掃建置檔、`.toml` 和 `settings.gradle*`。
引句:「"""專案根目錄往下最多 max_depth 層的建置檔(`_KT_BUILD_FILES`、settings.gradle(.kts))與 gradle/libs.versions.toml 的文字。」
輸入:根 `build.gradle.kts` 有 `compose = true`,而 `build-logic/convention/src/main/kotlin/AndroidCompose.kt` 寫了 `lintChecks("com.slack.lint.compose:compose-lint-checks:1.6.1")`。
實際輸出:仍印 A2「Compose 規則哪裡都沒接」,因為 convention plugin 的 `.kt` 沒被掃。
相反方向:建置檔裡只要有 `// TODO add compose-lint-checks` 這種註解,A2 就被抑制,字面比對不排除註解。`// com.android.application` 的註解也會被當成 Android 專案。

**F5**
severity: minor
blocking: 否
file: `scripts/test_lumos.py` 的 `_KT_B4_LINT`(diff 第 667 行)只認 `androidx`、`內建`、`slack` 三種前綴。
引句:「_KT_B4_LINT = r"(?:androidx(?:\.[\w.]+)?|內建|slack):\s*([A-Z][A-Za-z0-9]+)"」
輸入:`skills/kotlin-idioms/checks-catalog.md` 中現成規則欄寫成 `Android Lint:CommitPrefEdits;…` 的列。
實際輸出:至少 19 列沒被標成第四批「CI 範本:Android Lint」,仍是「批四(現成規則)」,例如 DATA-4、5、6、25、28、29、31、32、33、45–51、76、78 和 TEST-24、25、26。這些都是字面寫明 Android Lint 的列,正是 A1 提醒要保護的對象。
測試與口徑文字互相吻合,所以測試是綠的,但口徑本身漏了這個前綴。另外 `dagger-lint:` 的 ARCH-63 也停在「批四(現成規則)」,判斷方式相同。
其餘你點名的 S4 邊界(全形分號、規則碼前有空白、`androidx` 後接中文、同段同時有「待查」與真規則碼)我沒找到會誤判的真實列。

**邊界逐項結果(沒問題的)**
- **函式不丟例外**:`kt` 是字串、非清單、清單含 None 或數字、`kt: []`、`repo_root` 不存在、命令含 NUL 或 5000 字元,全部不丟例外。
- **`--plugins` 解析**:
  - 最後一個詞沒值回 `[]`。
  - `--plugins=` 回 `[]`。
  - 逗號串兩支、含空白加引號、`~`、`$HOME`、`${HOME}` 都正確展開。
  - 非 detekt 命令的 `-p` 被忽略。
- **建置檔掃描**:
  - 第 3 層會掃、第 4 層不掃。
  - 隱藏資料夾和 `build/` 不掃。
  - 資料夾符號連結不跟、檔案符號連結會讀。
  - 超過 1MB 的檔案只讀前 1MB。
  - 非 UTF-8 位元組照判不出錯。
  - `pom.xml` 與 `libs.versions.toml` 單獨存在也能判成 Android。
  - 單引號 Groovy 的 `apply plugin: 'com.android.application'` 會認成 Android。
  - `settings.gradle.kts` 只有 `include(":app")` 不算。
- **CI 設定檔**:`.github/workflows` 是檔案時回空清單、`.YML` 會讀、子資料夾不讀(GitHub 本來也不支援)。

**manifest(1 條)**
`scripts/lumos:38995` 的 `open\s*\(` 判為誤報。該行是 `with open(root / rp, "rb") as fh:`,在 `with` 裡確定關閉,且有 `except OSError`。

**圖譜鏡頭**
範圍 `87c82567..cafcd3ec` 在 shearwater 專案算不出來,所以改讀 `docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md`、`linter精選目錄.md`、`kotlin規則包.md`。
- **`lint-declaration-health.md`**:不破壞它的合約。
  - 該筆記第 31 行宣稱「只提醒不改退出碼」,新增的 A1–A3 只進 `advisories` 清單和 `warn([], …)`,不進 `problems`,退出碼不變。
  - 第 33 行已記載「A 系列另起一則」,程式也是另起一則。
  - T4 改用共用讀檔函式後,判定範圍仍只看 `.github/workflows/`(`github_only=True`),測試已涵蓋。
- **`linter精選目錄.md`**:不破壞它的合約。
  - 第 181 行寫「只看字面,不驗 CI 真的跑」,和實作一致。
  - 第 143 行的 `--build-upon-default-config` 與 `--disable-default-rulesets` 在範本中都有。
  - F1、F2 的誤報和漏報不違反這句話,但「沒接才印」的前提在多行 `run` 下會失效。
- **`kotlin規則包.md`**:這份變更沒碰規則包,不影響。

總結:最嚴重是 major,會擋 1 條(F1)。
