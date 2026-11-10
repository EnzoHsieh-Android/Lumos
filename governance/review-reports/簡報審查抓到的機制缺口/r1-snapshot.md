---
type: project
status: doing
created: 2026-11-09
updated: 2026-11-09
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/kotlin規則包
  - Systems/pitfalls-code-loop
related:
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/pitfalls-code-loop]]"
---
# 簡報審查抓到的機制缺口_計劃

> 白話:面試簡報請 Codex 以面試官角度逐頁審,回頭查 Lumos 實際怎麼處理時,查出三個機制缺口和一句不準確的說法:Service 裡合理的背景收集被規則誤擋、人沒辦法把某次改動的風險調高、行內忽略註解可以不留紀錄地繞過新增告警閘,以及 README 的實驗句把比較組講錯。這份計劃一次補完四件。

PRIOR-ART: ①規則例外照官方對 repeatOnLifecycle 的適用範圍收窄:官方說它是為了「只在 UI 顯示在畫面上時處理」,所以非畫面的生命週期擁有者(Service、整個 App 程序)不在規則該管的範圍。②人工調高風險寫在提交訊息裡(跟 Signed-off-by、Reviewed-by 這類寫在訊息裡的標記同一種慣例),但**不照 git trailer 的格式認**:本 repo 先前 [[Projects/進度從提交推導_計劃]] 用過 trailer,後來翻案(d7),理由是「trailer 寫錯的輸出跟沒寫一樣,會靜默失敗」。所以這裡改成訊息裡任何地方出現 `Lumos-Risk` 字樣(大小寫、連字號、底線、空白都不拘)就算,寫錯格式的結果是多審,不是悄悄沒作用;只准往上調,不准往下。③行內忽略要留痕借 SonarQube 追蹤 NOSONAR 與 @SuppressWarnings 的做法(把忽略註解本身當成要處理的問題),以及 ESLint 社群規則 require-description(忽略要寫理由);Lumos 已有「新增告警要附理由放行」的流程,把新加的忽略註解當成一條新增告警送進同一條路,不另做一套。
RETIRE-IF: ①Android Lint 或 compose-rules 出了同一種只管畫面收集的檢查 → 自寫規則撤掉、型錄改指現成檢查。②半年內沒有任何一次推送讀到 Lumos-Risk 標記 → 檢討是否改成別的人工入口或拿掉。③忽略註解告警的放行紀錄裡,誤認(忽略字樣出現在字串常數或說明文字裡)的筆數多過真的忽略 → 改成解析各工具的抑制結果,不再用字面比對。

## 用詞

- **行內忽略註解**:寫在程式碼行裡、讓檢查工具略過那一行的註解,例如 `// ast-grep-ignore`、`# noqa`、`eslint-disable`、Kotlin 的 `@Suppress(…)`。
- **人工標記高風險**:提交訊息裡出現 `Lumos-Risk` 字樣的那一行,建議寫成 `Lumos-Risk: high <一句理由>`;字樣後面剩下的字當理由。
- **這次範圍**:分級函式收到的差異範圍,兩點(`A..B`)或三點(`A...B`,起點取共同祖先)都先用 `_diff_range_ends` 拆成起點與終點,再讀「起點之後、終點以前」的提交(`git log 起點..終點`)。

## 範圍

1. **規則例外**:`kt-lifecycle-collect-without-repeat`(型錄 STATE-5)規則的兩個分支(`lifecycleScope.launch { … collect … }` 與 `.launchIn(lifecycleScope)`)都不再報兩種非畫面的生命週期擁有者:①類別直接繼承 `LifecycleService`、`MediaSessionService`、`MediaLibraryService` 時,類別本體裡的收集(認法:類別宣告的直接繼承清單裡有這三個名字之一,只看那一層類別,不看裡面的內部類別);②`ProcessLifecycleOwner.get().lifecycleScope` 的收集。型錄 STATE-5 那列補一句適用範圍。
2. **人工調高風險**:分級函式 `_pitfall_tier` 最先讀這次範圍內每個提交的完整訊息,任何一行出現 `Lumos-Risk` 字樣(正規式 `lumos[-_ ]?risk`,不分大小寫)就判 high,理由寫「人工標記高風險」加那一行字樣後面的字;值寫什麼都一樣(寫 low 也照 high,因為不准往下調),只改改動文件也照 high。生效處:`pitfalls --diff` 的輸出與推送閘的 `code-loop check`(它開子程序跑 pitfalls 取 tier)。不生效處:`loop next` 的分級由編排者照 pitfalls 輸出帶,已經定錨的審查迴圈不會被事後升級;`spec-gate --push-check` 印的「改動風險分級:light」是另一套判斷,不受影響,推送時以 `code-loop check` 為準。
3. **行內忽略註解進新增告警閘**:新增告警閘每跑一條檢查命令,就在改動前、改動後兩份快照上,各數一次「這個工具認得的忽略寫法」出現在哪幾行,當成規則名 `lumos-inline-suppression` 的告警,跟工具本身的告警一起比差;新加的就照新增告警擋,走 `lumos lint-waive <指紋> --note` 附理由放行、留紀錄。掛點在每條命令真的跑完、記進已跑清單之後(沒跑的、只報不擋的命令不數)。認工具的方法:整條命令字串用正規式找工具名(`ast-grep` 或獨立的 `sg`、`ruff`、`eslint`、`stylelint`、`detekt`、`semgrep`、`swiftlint`,前後要是字的邊界),一條命令可以同時認到多個。工具與寫法的對照:ast-grep→`ast-grep-ignore`;ruff→`noqa`;eslint→`eslint-disable`;stylelint→`stylelint-disable`;detekt→`@Suppress(`、`@file:Suppress(`、`@SuppressWarnings(`;semgrep→`nosemgrep`;swiftlint→`swiftlint:disable`。
4. **README 實驗句**:中英兩版改成照原始紀錄寫:比較的是「只看程式碼」和「讀到故意寫錯的筆記」、單位是 25 場、只在 Haiku 4.5 出現(Opus 四組都 25/25),並補上「在筆記旁標明以程式碼為準後回到 20/25」與「筆記正確時的表現還沒量」。

## 不做

- 已經存在的忽略註解不追溯,只看這次新加的。
- 人工標記不能把分級往下調。
- 自寫基底類別間接繼承 Service 的情況認不出,照舊報,走放行。
- Android Lint 的 Gradle 任務不經新增告警閘,它的 `@SuppressLint`、`tools:ignore` 不在這次範圍。

## 實務隱患

- **字面比對會誤認**:字串常數或說明文字裡出現對照表裡的忽略字樣(例如 `"# noqa"` 這個字串),也會被當成忽略註解。誤認的結果是多擋一條、走放行,不是漏擋。
- **標記誰都能加**:工具分不出是人還是 AI 加的;但只准往上調,被濫用的方向是多審,不是少審。
- **順手提到也算**:提交訊息裡只是提到 Lumos-Risk 這個詞(例如實作這個功能的提交本身),也會被判 high;這是刻意的取捨:格式不嚴格,換來寫錯不會靜默失效。
- **讀不到提交就不升**:起點不是一個提交(例如新分支首推、範圍起點是空樹)、git 讀不出訊息時,分級照原本算,不會因為人工標記升級。
- **改一行就算新增**:新增告警閘的指紋用「規則+檔名+那一行的內容」,同一行改了別的字但留著 `# noqa`,會被算成新加的一條,要再放行一次;這跟工具本身的告警同一套口徑。
- **靠命令字面認工具**:命令包在自己寫的腳本裡、看不到 ruff、ast-grep 這些字時,那條命令不數忽略註解。
- **本 repo 也用 ruff**:之後新加 `# noqa` 要附理由放行;2026-09 以來 scripts/lumos 新加過 3 處,量小。
- 併發沿用放行檔讀改寫已上鎖的做法;效能是每條命令多讀一次改動檔的文字,檔數受既有大小上限管;不動任何既有帳。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:不送任何資料到外部
- 已排除:不可逆:只改判定與文件,整段還原就回到原狀
- 碰到守衛面:三件都改推送閘或規則的判定,照守衛面處理(要過代碼審)。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 規則只管畫面的收集 | 官方說 repeatOnLifecycle 是為了「只在 UI 顯示在畫面上時處理」(This approach processes the flow emissions only when the UI is visible on the screen),2026-11-09 讀 | https://developer.android.com/topic/libraries/architecture/views/coroutines-views |
| Service 不是畫面 | 「A Service that is also a LifecycleOwner」,已知子類別 MediaSessionService、間接子類別 MediaLibraryService,2026-11-09 讀 | https://developer.android.com/reference/androidx/lifecycle/LifecycleService |
| ProcessLifecycleOwner 不是畫面 | 「Class that provides lifecycle for the whole application process」,2026-11-09 讀 | https://developer.android.com/reference/androidx/lifecycle/ProcessLifecycleOwner |
| 人工標記不照 trailer 格式認 | 本 repo 先前用 trailer 承載工作項,翻案理由是「trailer 寫錯的輸出跟沒寫一樣(靜默)」(d7);所以改成字樣出現就算,寫錯只會多審 | [[Projects/進度從提交推導_計劃]] |
| 行內忽略要留痕 | SonarQube 把 NOSONAR 與 @SuppressWarnings 的使用當成要追蹤的問題 | https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-quality-gates/tracking-inline-comments |
| README 實驗句 | 原文「Haiku 有圖譜 12/25 vs 只看程式碼 20/25」「筆記正確時的表現尚未量」 | [[Projects/Lumos定位_程式碼為主脈絡為輔_計劃]] |

## 驗收條款

- [S1] 當規則包樣本自測跑到 kt-lifecycle-collect-without-repeat 時,LifecycleService 與 MediaSessionService 子類別裡、ProcessLifecycleOwner 的收集(含 launch 裡 collect 與 launchIn 兩種)應 不報,同一支檔裡 Fragment 的收集 應 照報 [test:t_kotlin_rulepack_samples]
- [S2] 當這次範圍內有提交訊息出現 `Lumos-Risk` 字樣時,分級 應 是 high 並寫明人工標記與那行的理由(寫 low、寫在內文段落、大小寫或連字號不同、只改文件都一樣);範圍外的提交、沒有這個字樣 應 不改分級 [test:t_pitfall_tier_human_high]
- [S3] 當改動新加一行那條命令的工具認得的行內忽略註解時,新增告警閘 應 多出一條 lumos-inline-suppression 告警;原樣留著的、別的工具的寫法 應 不算 [test:t_lint_new_inline_suppression]
- [S4] 當讀 README 中英兩版那句實驗時,應 寫明比較組是「只看程式碼」對「讀到故意寫錯的筆記」、單位是場、只在 Haiku 出現、標明以程式碼為準後回到 20/25、筆記正確時還沒量 [manual:對照 Projects/Lumos定位_程式碼為主脈絡為輔_計劃 原文逐字核對中英兩版的數字與比較組]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `class SyncService : LifecycleService()` 裡 `lifecycleScope.launch { flow.collect {} }` | 不報 | LifecycleService 官方說明是 Service,不是畫面;repeatOnLifecycle 官方適用範圍是 UI 在畫面上 |
| S1 | `ProcessLifecycleOwner.get().lifecycleScope.launch { flow.collect {} }` | 不報 | ProcessLifecycleOwner 官方說明:整個 App 程序的生命週期 |
| S1 | `repo.pings.onEach { }.launchIn(lifecycleScope)` 在 LifecycleService 子類別裡 | 不報 | 同上兩列 |
| S1 | 同一支檔裡 `class SettingsFragment : Fragment()` 的 `lifecycleScope.launch { collect }` | 照報 | repeatOnLifecycle 官方範例就是 Fragment |
| S2 | 範圍內提交訊息尾 `Lumos-Risk: high 改到登入流程`,改一支程式檔 | high,理由含「人工標記」與「改到登入流程」 | 本計劃範圍 2 |
| S2 | 訊息尾 `Lumos-Risk: low`,改一支程式檔 | high(寫什麼值都照 high,不准往下調) | 本計劃範圍 2 |
| S2 | 內文段落寫 `lumos_risk 升高`,最後一段是一般文字 | high(不照 trailer 格式認) | [[Projects/進度從提交推導_計劃]] d7:trailer 寫錯會靜默失效 |
| S2 | 只改一篇 Markdown 文件、訊息帶 `Lumos-Risk: high` | high(不再判 light) | 本計劃範圍 2 |
| S2 | 標記在範圍起點之前的提交 | 照原本算(standard) | 本計劃用詞〈這次範圍〉 |
| S3 | ast-grep 命令,改動前一行 `// ast-grep-ignore: kt-x`,改動後多一行 `bar() // ast-grep-ignore` | 新增 1 條,在新加那行 | 本計劃範圍 3 |
| S3 | ruff 命令掃 .kt 檔裡的 `ast-grep-ignore` | 0 條 | 本計劃範圍 3 的對照表 |
| S3 | ruff 命令掃 `import os  # noqa: F401` | 1 條 | Ruff 的行內忽略寫法 |
| S4 | 讀 README.md 與 README.en.md 第 450 行那句實驗 | 兩版都寫「只看程式碼答對 20 場、讀到故意寫錯的筆記剩 12 場、標明以程式碼為準後回到 20 場、Opus 四組都 25 場全對、筆記正確時還沒量」 | [[Projects/Lumos定位_程式碼為主脈絡為輔_計劃]] 原文 |

## 回退

- 規則例外:還原 state.yml 那條規則、兩個樣本檔與型錄 STATE-5 那列。
- README:還原中英兩版那一句。
- 人工調高風險:拿掉分級函式讀 trailer 那一段;已寫進提交訊息的 trailer 不影響任何東西。
- 忽略註解:拿掉新增告警閘多數忽略註解那一行;已寫的放行紀錄留著無害。

## 天花板

- 人工標記只解決「人能調高」,不解決「工具算低了而沒人發現」。
- 推送閘在兩種情況不跑 pitfalls、直接當 standard(推送起點等於現在、算不出推送起點),這時人工標記也讀不到。
- 忽略註解只認對照表裡的工具與寫法;換一種寫法(例如包進巨集、或工具新增的抑制語法)就認不出。
- 規則例外只認直接繼承;判斷不了「這段收集在需求上該不該在背景跑」。

REVISIT:2027-05-09 查新增告警放行紀錄裡 lumos-inline-suppression 的筆數與誤認比例,決定要不要照 RETIRE-IF ③ 改做法
