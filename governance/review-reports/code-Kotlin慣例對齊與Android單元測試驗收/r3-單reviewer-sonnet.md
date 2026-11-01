severity: minor

第 3 輪審查的結論是沒有 blocker 或 major,共 3 條 minor。

**歸因與環境**
- 修補差異 `r3-repair.patch` 只有 `governance/anchor-baseline.json` 一支檔。壓提交前後,其餘檔案內容一字不差:`git diff --stat 3562f6c9..98a346717` 排除審查卷證、帳本和 `governance/` 後為空。
- 所以下面三條 finding 都不是這次修補造成的,修前修後的行為相同。
- 實驗在 `/tmp/lumos-seat-work/code-Kotlin慣例對齊與Android單元測試驗收/單reviewer-sonnet/` 的 clone 裡做,已用字面絕對路徑刪除。

## Finding

### H1
severity: minor
blocking: no
file: `skills/lumos-project-notes/commands/test-quality-standard.md:102` 與 `:109`;`scripts/test_lumos.py` 的 `t_test_quality_standard_android_unit_section`
引句:「資料庫照前面的〈Android 資料層(Room)〉節,裝置上的畫面與流程照 lumos-android-evidence 的端到端驗收。」

失敗場景:r2 修補要求新節指 Room 節時寫明節名,不寫「上一節」(上一節其實是原生收證)。這個修補沒有任何測試守住。
- 把 `:102` 和 `:109` 兩處的 Room 指路改成「照上一節」,`t_test_quality_standard_android_unit_section` 仍是 `10 passed, 0 failed`,rc=0。
- 守衛測試只驗節位置、三段順序、關鍵詞、單源指標、03 的指路。
- 之後有人改回「上一節」,讀者會被導到原生收證節,找不到 Room 的做法。

歸因:有證據的原有漏查。
- 修前 3562f6c9 與修後 98a346717 的這兩處文字相同,測試也都沒守。
- 命令:在 clone 裡做 `str.replace` 後跑 `python3.14 scripts/test_lumos.py -k t_test_quality_standard_android_unit_section`,兩版結果相同。

### H2
severity: minor
blocking: no
file: `skills/lumos-project-notes/commands/test-quality-standard.md:956`(來源行);計劃 `Projects/Android本機單元測試驗收標準_計劃.md` 的 S2 條款
引句:「[Hilt 測試](https://developer.android.com/training/dependency-injection/hilt-testing)、[Gradle 測試篩選](https://docs.gradle.org/current/kotlin-dsl/gradle/org.gradle.api.tasks.testing/-test-filter/is-fail-on-no-matching-tests.html)、[程式碼涵蓋率](https://developer.android.com/studio/test/coverage-report)」

失敗場景:新節開頭寫「各頁當天的更新日期列在最後」,S2 條款也要求官方頁「帶核對日期」。但來源行裡這三個官方連結沒有日期,其餘十個都有。
- Hilt 測試和程式碼涵蓋率是 `developer.android.com` 頁面,應該有可抓的更新日期。
- 讀的人無法判斷這三條的核對日期,S2 的人工核對也對不上這三條。

歸因:有證據的原有漏查。修前修後來源行相同。
- 命令:`grep -n 'Hilt 測試' skills/lumos-project-notes/commands/test-quality-standard.md`,兩版輸出相同。

### H3
severity: minor
blocking: no
file: `skills/lumos-project-notes/commands/test-quality-standard.md`(新節 Flow 小段,Turbine 那條);`Projects/Kotlin慣例對齊Android官方與本機detekt_計劃.md` 做法 3 的 R21
引句:「社群:用 Turbine 時,每個發出的值都要收掉,或用 `cancelAndIgnoreRemainingEvents()` 明講不管;錯誤用 `awaitError()` 收;不要用 `runCurrent()` 去推 Turbine。」

失敗場景(兩處措辭與依據對不上):
1. Turbine README 的原文是「Use them everywhere, and you might never need `runCurrent()` again」,以及「instead of using tools like `runCurrent()` to "push" an asynchronous flow along」。README 說的是「不必」,沒有禁止。手冊寫成「不要」,語氣比出處重。這條已標「社群」,所以只是措辭精度。
2. 計劃做法 3 的 R21 寫「用開發者選項「不保留活動」測」,實際交付的 R21 沒有這句。實作端沒有問題,「不保留活動」只模擬 Activity 被銷毀、不是程序被殺。計劃筆記寫成「做法」卻沒反映實際內容,日後可能被誤當 R21 該有的內容。

歸因:有證據的原有漏查。兩處修前修後文字相同。
- 查證:WebFetch 取 `https://github.com/cashapp/turbine`;`grep -n '不保留活動' docs/lumos-toolchain-knowledge/Projects/Kotlin慣例對齊Android官方與本機detekt_計劃.md skills/kotlin-idioms/SKILL.md`,只在計劃筆記命中。

## 配對案例(分開報)

### repair 案例
所有案例都是前後對比:
- 修前是 3562f6c9a86a0b424206fb12cc644df70a8d4427,修後是 98a346717ddf558b779415285e92be33a7af91a7。
- case_source 是派工單列的配對案例;突變輸入由我獨立造。

| 主張 | 修前 | 修後 | 歸因 |
|---|---|---|---|
| `anchor verify` 應 rc0 | `3562f6c9` 的 `anchor-baseline.json` 對 `scripts/test_lumos.py` 不符(我用 sha256 逐檔比對,命中 `MISMATCH scripts/test_lumos.py`) | `python3.14 scripts/lumos anchor verify` 印出「13 個驗證器檔案都跟基準線一致」,rc=0 | 有證據的修復效果:`r3-repair.patch` 把基準 sha 由 `56a111ab…` 改為 `46c64b8e…` |
| 三個功能提交各自的基準與該提交的測試檔一致 | 不適用(修前是另一組提交) | `1f9a03359` 和 `3e62aa422` 的基準都是 `d44a9ead…`,測試檔 sha256 也都是 `d44a9ead…`;`98a346717` 兩邊都是 `46c64b8e…`。三個提交各自 13 個錨點檔逐一比對,0 個不符 | 修後成立 |
| `t_kotlin_idioms_android_official_rules` 在標題或依據行被動時紅 | 內容相同,未另行判定 | 突變全部紅(1 failed):「五、Android 特有」標題改字;R19、R20、R21、R22 各自刪掉依據行;審查鏡頭改回 R1–R18 | 修後有行為證據 |
| `t_test_quality_standard_android_unit_section` 在單源指標被拿掉時紅 | 內容相同 | 突變全部紅(9 passed, 1 failed):單源指標改成「單源=無」;「什麼證據才算過」改名;03 的指路改成別的字;新節搬到「共用證據格式」前面 | 修後有行為證據 |
| 新節指 Room 時寫明節名 | 內容相同 | 文字成立:`:102`、`:109` 寫〈Android 資料層(Room)〉節,Room 節確實在原生收證前(`:66`)。但沒有測試守住,見 H1 | 文字成立,守衛缺口是原有漏查 |

### preserve 案例
- 六支指定測試修後全綠,各自 `-k` 跑結果依序如下;三問(行為證據、相鄰路徑、同案例前後)在這裡一併回答。
  - `t_kt_flow_question_events_as_state`:4 passed。
  - `t_kt_leaks_question_viewmodel_context`:2 passed。
  - `t_kotlin_idioms_android_official_rules`:11 passed。
  - `t_kotlin_idioms_detekt_snippet_runs`:4 passed(0.9 秒)。
  - `t_test_quality_standard_android_unit_section`:10 passed。
  - `t_test_quality_standard_android_room_section`:9 passed。
- detekt 範例那支的突變:
  - 少一個右括號:退出碼 1,測試 2 failed。
  - 加入不存在的規則:退出碼 3,測試 2 failed。
  - `GlobalCoroutineUsage` 改成 `active: false`:測試 2 failed。
- 相鄰測試(clone 在 HEAD 98a346717):
  - `-k idioms` 18、`-k stack_question` 120、`-k kotlin` 53、`-k kt_` 69、`-k test_quality_standard` 21、`-k skill` 65,全綠。
  - `lumos lint` 對六篇改動筆記都是 0 問題。
  - `lumos doctor` 為「圖譜健康 — 0 issues」。

## 三問

**1. 原問題的修復效果有何行為證據?**
- 錨點基準:修前 sha 不符,修後 `anchor verify` rc0,三個提交各自的基準也都一致。
- r1、r2 加強的守衛:上面的突變全部翻紅。
- 只見測試通過不能證明問題解決,所以我另外做了突變。

**2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 修補只動基準檔。正常路徑(`anchor verify`)成立。
- 錯誤路徑(基準與檔案不符)在修前版本也能重現,我用 sha 比對證實,所以 `anchor verify` 能擋這種不符。
- 相鄰測試和文件健檢都沒壞。
- 沒裝 detekt 的路徑只印警告並 return。這是計劃明文接受的,沒有在別處驗到。

**3. 新發現的同一案例在修前、修後各是什麼結果?**
- H1、H2、H3 的文字或守衛行為在 3562f6c9 與 98a346717 相同,都是原有漏查。
- H1 在 clone 做同一個突變,結果都是綠;H2、H3 的文字用 grep 比對,兩版相同。

## 已驗的正向主張

**官方文件與引用的官方頁一致**,逐頁用 WebFetch 對照:
- 架構建議(2026-10-05):「不要從 ViewModel 送事件給 UI」和「ViewModel 不持生命週期型別/Context」是 Strongly recommended,「不用 AndroidViewModel」是 Recommended,假實作優於 mock 是 Strongly recommended。
- UI 事件頁(2026-05-18):Channel 不保證送達;導覽那一例的返回堆疊旗標用 `rememberSaveable`。
- 狀態還原頁(2026-10-07):R21 的三欄存活表與官方一致。
- Flow 測試(2026-09-24):R22 範例的 `backgroundScope.launch(UnconfinedTestDispatcher(testScheduler))` 逐字相符。
- 協程測試(2026-09-22):`MainDispatcherRule` 要先宣告;測併發優先用 `StandardTestDispatcher`。
- 其餘頁的更新日期與關鍵主張:本機單元測試(2026-10-23)、Robolectric(2026-03-05)、測試策略(2026-10-08)、要測什麼(2026-03-05)、命令列測試(2026-10-15)、測試替身(2026-03-05)、截圖測試(2026-10-08)。
- 唯一對不上的是 H3 的 Turbine 措辭。

**detekt 實測**:detekt 1.23.8 在 `/Users/enzo/.gradle` 的 coroutines 1.8.1 與 stdlib 1.9.20 jar、JBR 17 下重跑。
- 只給 `--input`:零報 `SuspendFunSwallowedCancellation`、`SleepInsteadOfDelay`、`InjectDispatcher`、`ForbiddenMethodCall`、`CouldBeSequence`。
- 帶 `--classpath` 與 `--jdk-home`:`SleepInsteadOfDelay`、`InjectDispatcher`、`ForbiddenMethodCall`、`CouldBeSequence` 都報。`SuspendFunSwallowedCancellation` 只報 `runCatching` 那行(第 13 行),`try/catch(Exception)` 那行(第 9 行)不報。
- `ForbiddenImport` 只給 `--input` 就抓得到 `runBlocking` 與 `collectAsState` 的 import。完整套件名的 `kotlinx.coroutines.GlobalScope.launch` 不報。
- `--generate-config` 的預設開關和手冊寫的一致,`CoroutineLaunchedInTestWithoutRunTest` 不存在。

**圖譜鏡頭**(固定席逐條):
- `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`授權與歸屬`:`scripts/lumos` 只改 `_STACK_QUESTION_SPECS` 兩題的文字,不碰搜尋、guard kill、re-inject 與授權白名單,不影響。
- `bound-tests-gate`、`design-loop`:新增的條款都有綁定測試且方法名合法,迴圈 id 以 `code-` 開頭,不走設計審的處置閘。
- `測試假綠形態`:新測試帶前置斷言(條號連續、找得到 Channel 那一列、找得到〈機檢接線〉段與 yaml 區塊)。唯一的靜默路徑是沒裝 detekt 時 return,計劃明文接受。
- `linter精選目錄`(`android.yml` 的家):只改註解與文字,實測事實正確。
- 超出上限只列名的節點:
  - 查了 `test-quality-handbook` 與 kt-flow/kt-leaks 的其他引用,沒有過期內容,其餘只列名未逐篇讀。
  - `scripts/lumos` 裡沒有第二份「事件=SharedFlow」。

**其他**:
- 臨時目錄在例外或提早 return 時的清理成立:`mkdtemp` 在 `try` 之前,沒裝 detekt 的 return 在 `mkdtemp` 之前。
- 測試對 `GRAPHCTL` 已 resolve,不受 symlink 影響。
- 用 `Path(GRAPHCTL).parent.parent` 的七處都在已 resolve 的 `GRAPHCTL` 之上。

## 未驗範圍
- 全套測試約 8 分鐘,沒跑;只跑了上面列的子集。
- detekt 2.x 與 Linux/Windows 的輸出格式沒驗,只在 macOS + 1.23.8 驗。
- 沒裝 Gradle detekt 外掛的消費專案實跑 SARIF,仍是文件記載的 REVISIT(2026-12-15)。
- Turbine 以外的社群連結(Pitest issue、Now in Android wiki)沒逐條核對。

總結:最高等級 minor
