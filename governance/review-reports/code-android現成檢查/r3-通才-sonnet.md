severity: major

**F1**
引句:「只有 `lintKotlin`、`lintFix`、`lintVitalRelease`、`lintAnalyzeDebug`、`updateLintBaseline` 應 照印」
file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:81`
這是驗收條款 S1,綁了測試 `t_lint_android_ci_advice`。這輪的程式和測試把 `lintAnalyze` 從排除名單拿掉,測試也刪掉 `lintAnalyzeDebug` 那一例。但 S1 條款原文仍要求「只有 `lintAnalyzeDebug` 時照印 A1」。
重現:CI 檔只寫 `run: ./gradlew lintAnalyzeDebug`,A1 不印。實測回傳 `[]`,條款說該印。
條款與行為互相矛盾,而且這條是帶測試綁定的合約文字。修法有兩種:改條款,或把這例列為「不印」。
severity: major
blocking: 是

**F2**
引句:「③建置檔有 `lint { }` 或 `lintOptions { }` 區塊,或專案往下三層內有 `lint-baseline.xml`(範本第 1、2 步的痕跡)」
範本的步驟順序是「先產基準線、提交,再加 CI 步驟」。照做到第 2 步、還沒做第 3 步的專案,正是 A1 該提醒的對象。它因為有 `lint-baseline.xml` 或 `lint { baseline = … }` 反而不印。
重現:Android 專案、沒有任何 CI 檔、只有 `app/lint-baseline.xml`,`_lint_android_ci_advisories` 回 `[]`。只有 `android { lint { … } }` 區塊、沒有 CI 檔時也回 `[]`。
範本自己的第 1、2 步痕跡,把範本第 3 步缺漏的提醒關掉了。很多舊專案為了 `abortOnError false` 本來就有 `lintOptions { }`,同樣不會被提醒。
severity: major
blocking: 是

**F3**
引句:「②那支 CI 設定檔提到 gradle(大小寫不拘)而且有一個詞是 `check` 或 `build`」
`check`、`build` 這兩個詞,在 GitLab 的 `stage: build`、GitHub 的 `needs: build`、`name: build` 都會出現。「提到 gradle」又只要檔裡任何地方有一個字,`gradle/actions/setup-gradle` 或 `image: gradle:8` 就夠了。
重現(實測都回 `[]`):
- 只有 `./gradlew assembleDebug` 加一個 `needs: build` 的 workflow,A1 不印。
- `.gitlab-ci.yml` 只有 `stage: lint` 搭 `./gradlew assemble`,A1 也不印。
上一輪限在 gradlew 那一行,這輪放寬到整份檔,等於 CI 只要有 gradle 加任一 job 名,A1 就靜默。計劃把「job 名稱叫 build」寫成接受的代價,但 `stage: lint` 與 `needs:` 比單一 `name:` 常見得多,證據門檻低到失去鑑別力。
建議:第②類改成只認 `run:`、`script:`、`arguments:`、`tasks:` 這類命令欄位,或要求 `check`、`build` 跟在 gradlew、gradle 後面。
severity: minor
blocking: 否

**F4**
引句:「建置檔有 `lint { }` 或舊寫法 `lintOptions { }` 區塊,或專案根目錄往下三層內有 lint-baseline.xml」
`_android_lint_config_evidence` 在 `_android_build_texts` 之後又自己 `os.walk` 一遍,目錄跳過條件(`_stack_scan_skip`、隱藏資料夾、深度 3)是第三份複本。這個走訪沒有 200 支的上限,卻要判斷 `lint-baseline.xml`。前一輪才為同類問題抽了 `_detekt_walk_segments`,走訪器這次又複製一份。
建議:讓 `_android_build_texts` 順手回報有沒有 `lint-baseline.xml`,或把兩個走訪合併。
severity: minor
blocking: 否

**F5**
引句:「`/`、`.` 不切,路徑 `app/build/outputs` 與 `-Dkotlin.build.x` 是一個詞、不算」
`/* … */` 這種 Groovy 區塊註解(Jenkinsfile)沒有處理,只處理了 `//` 行。
重現:Jenkinsfile 內容是 `/*\n sh './gradlew lint'\n*/\nsh './gradlew assemble'`,A1 不印,被註解掉的 lint 被當成跡象。
這是上一輪二邊3 的同族,只補了 `//` 一半。方向是少印,所以影響小。
severity: minor
blocking: 否

**F6**
引句:「AGP 9.4 以上用 1.6.1(lint 32.4.1);AGP 9.3 用 1.5.5(lint 32.3.2);AGP 8.7 到 8.x 用 1.4.2(lint 31.7.1);更舊的照發行說明挑」
`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md` 與計劃都有同樣的版本表。AGP 9.0 到 9.2 沒有列,也不屬於「更舊」。照這份表,這幾個版本的專案不知道該挑哪一版。依照規則「建置用 lint 不高於專案 lint」,應該是 1.4.2。
建議:把表補成「AGP 8.7 到 9.2 用 1.4.2」,或明講 9.0 到 9.2 沿用 1.4.2。
severity: minor
blocking: 否

**F7**
引句:「`WHY:Android 現成檢查的三則提醒(A1 CI 設定檔沒有 Android Lint 任務、A2 用 Compose」
`docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md:33` 的這行還在說 A1 是「CI 設定檔沒有 Android Lint 任務」。新增的下一行 WHY 才說 A1 是證據模型,看建置檔和 CI 設定檔。同一個節點裡兩行對 A1 的定義不一致。另外 `_android_ci_lint_evidence` 的 docstring 寫「跡象有兩種」,計劃與 A1 提醒文字寫三種(建置檔那一種在別的函式裡),也沒對齊。
severity: minor
blocking: 否

**F8**
引句:「`ci_dir = Path(tempfile.mkdtemp(prefix="gctl-andci-ci-"))`」
測試新建了暫存目錄,每次跑都留下一份,沒有刪。`~/.claude/CLAUDE.md` 的〈暫存清理〉寫「自己跑的測試或實驗:跑完…之後,刪掉它留下的暫存」。這輪才新增的 `gctl-andci-ci-` 沒人清,既有的 `gctl-andci-home-` 也一樣。不確定測試框架會不會統一清掃,所以只列為慣例違反。
severity: minor
blocking: 否

總結:最嚴重是 S1 驗收條款與新行為互相矛盾(F1),以及證據模型把範本第 1、2 步的痕跡當成已接上而關掉 A1(F2),會擋 2 條。A3 共用 `_detekt_walk_segments`、T4 改回直接讀檔、`_detekt_command_codes` 的呼叫端這幾處,我沒找到破壞點。
