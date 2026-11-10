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
  - Systems/pitfalls-lint-adapter
related:
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/pitfalls-code-loop]]"
---
# 簡報審查抓到的機制缺口_計劃

> 白話:面試簡報請 Codex 以面試官角度逐頁審,回頭查 Lumos 實際怎麼處理時,查出三個機制缺口和一句不準確的說法:Service 裡合理的背景收集被規則誤擋、人沒辦法指定「改到這些地方就要嚴審」、行內忽略註解可以不留紀錄地繞過新增告警閘,以及 README 的實驗句把比較組講錯。這份計劃一次補完四件。

PRIOR-ART: ①規則例外照官方對 repeatOnLifecycle 的適用範圍收窄:官方說它是為了「只在 UI 顯示在畫面上時處理」,Service 不是畫面。②人工調高風險借 CODEOWNERS 的形狀:專案在設定裡列出敏感路徑,改到就要嚴審;路徑比對沿用本 repo 實機驗收 shared_paths 那套(`_e2e_norm`、`_e2e_under`),不另寫比對。不用「提交訊息裡寫標記」:設計審 r1 四席實測它會被合併主線的提交、新分支首推的空樹起點、壞編碼訊息、壓提交弄丟標記這四種情況打穿;本 repo 先前 [[Projects/進度從提交推導_計劃]] 也因為「提交訊息裡的標記寫錯會靜默失效」放棄過(d7,那篇後來再翻成 d8、d10,但這條理由沒被推翻)。③行內忽略要留痕借 SonarQube 追蹤 NOSONAR 與 @SuppressWarnings 的做法(把忽略註解本身當成要處理的問題);Lumos 已有「新增告警要附理由放行」的流程,把新加的忽略註解當成一條新增告警送進同一條路,不另做放行流程。
RETIRE-IF: ①Android Lint 或 compose-rules 出了同一種只管畫面收集的檢查 → 自寫規則撤掉、型錄改指現成檢查。②有宣告 risk_high_paths 的專案,一年內那些路徑一次都沒被改到(用 git log --name-only 離線算)→ 檢討清單是否過時。③放行紀錄裡 rule 是 lumos/inline-suppression 的筆數,人工抽查理由後誤認(不是真的忽略註解)多過真的忽略 → 改成解析各工具的抑制結果,不再用字面比對。

## 用詞

- **行內忽略註解**:寫在程式碼裡、讓檢查工具略過那一行或那一段的註解或註記,例如 `// ast-grep-ignore`、`# noqa`、`eslint-disable`、Kotlin 的 `@Suppress("MagicNumber")`。
- **高風險路徑清單**:`.lumos/config.json` 的新鍵 `risk_high_paths`,字串清單,每項是相對專案根的檔案或目錄。
- **這次範圍**:分級函式收到的差異範圍(`pitfalls --diff` 與推送閘傳進來的那一個)。

## 範圍

1. **規則例外**:`kt-lifecycle-collect-without-repeat`(型錄 STATE-5)兩個分支(`lifecycleScope.launch { … collect … }`、`.launchIn(lifecycleScope)`)都不再報包在 Service 類別裡的收集。認法:任何一層外圍類別的繼承清單裡,有一項是建構子呼叫形式的 `LifecycleService(`、`MediaSessionService(`、`MediaLibraryService(`(可帶 `androidx.lifecycle.` 或 `androidx.media3.session.` 前綴);寫成 `MediaSessionService.Listener` 這種巢狀介面不算。外圍類別任一層是 Service 就豁免,所以 Service 裡的內部類別也豁免、Activity 裡的內部 Service 類別也豁免、Activity 本身照報。型錄 STATE-5 那列補一句適用範圍。
2. **高風險路徑清單**:分級函式 `_pitfall_tier` 在殘留索引那一步之後、風險型樣那一步之前,讀 `risk_high_paths`,這次改到的檔只要有一支等於清單裡的檔、或在清單裡的目錄底下,就判 high。理由寫「改到 risk_high_paths 列的路徑:」加最多 3 支檔名(超過寫「…等 N 支」),檔名經 `_plain_label` 清洗。多個理由並存時照既有寫法用「;」串起來,不互相蓋掉。
   - **讀哪一版設定**:範圍起點那一版與終點那一版(終點是工作目錄時讀工作目錄)的清單取聯集,所以同一次改動拿掉某條路徑不會讓自己降級,新加的當次就生效。
   - **讀不出時**:設定檔不存在或沒有這個鍵 → 不影響。設定檔讀得到但 JSON 解析失敗、或 `risk_high_paths` 不是字串清單、或超過 200 項 → 判 high,理由寫「risk_high_paths 讀不出」,跟殘留索引讀不出的方向一致。
   - **對不到檔的路徑**:清單裡某條路徑在終點那一版一支檔都對不到時,pitfalls 的輸出多印一行「risk_high_paths 這幾條對不到任何檔」,不影響分級;CODEOWNERS 的教訓是寫錯的規則會被靜默略過,這行讓人看得到。
   - **生效處**:`pitfalls --diff` 的輸出、推送閘的 `code-loop check`。判 high 之後跟其他原因的 high 一樣:要一筆代碼審留痕或 `code-loop skip`;受波及合約測試從只提醒變成紅就擋;`stack_questions.gate` 設 high-only 的專案,表態題生效;推送掛鉤印的提醒改成先印 pitfalls 給的理由,不再固定說「程式碼裡有高風險寫法」。
   - **不生效處**:`loop next` 的分級由編排者照 pitfalls 輸出帶;`spec-gate --push-check` 印的 light 是另一套判斷,推送以 `code-loop check` 為準。
3. **行內忽略註解進新增告警閘(只在推送範圍模式)**:新增告警閘的推送範圍模式(`_lint_new_tools`)每跑完一條命令,就在改動前、改動後兩份快照上,找這條命令的工具認得的忽略寫法出現在哪幾行,當成規則名 `lumos/inline-suppression` 的告警,跟工具本身的告警一起比差;新加的就照新增告警擋,走 `lumos lint-waive <指紋> --note` 附理由放行、留紀錄。同一份快照裡,同一支檔同一行只算一次(多條命令都認到同一個工具時不重複)。
   - **認工具**:沿用 detekt 判定那套命令切段(`_detekt_walk_segments` 剝環境變數與包裝詞、展開 `sh -c`),每段取第一個詞的檔名(`_cmd_basename`);第一個詞是 `npx`、`bunx`、`uvx` 時看下一個非選項的詞,`pnpm exec`、`yarn`、`uv run`、`python -m`、`python3 -m` 同理;detekt 的 `java -jar detekt-cli…` 照既有 `_detekt_segment_codes` 認。路徑裡出現工具名不算。
   - **對照表**(正規式,除非註明都不分大小寫):ast-grep 與 sg → `ast-grep-ignore`;ruff → `#\s*noqa`、`#\s*(ruff|flake8)\s*:\s*(noqa|disable|ignore|file-ignore)`;mypy → `#\s*type:\s*ignore`;bandit → `#\s*nosec`;eslint → `eslint-disable`;biome → `biome-ignore`;stylelint → `stylelint-disable`;semgrep → `nosemgrep`;swiftlint → `swiftlint:disable`;detekt 與 ktlint → `@(\w+:)?(kotlin\.)?Suppress(Warnings)?\(`,但括號裡的字串全是全大寫加底線的(例如 `"UNCHECKED_CAST"`,那是 Kotlin 編譯器的警告名,不是檢查工具的規則名)就不算;ktlint 另加 `ktlint-disable`。
   - **訊息**:「新加的行內忽略註解(<工具>)會讓檢查略過這裡:移除它,或用 lumos lint-waive <指紋> --note 寫明為什麼要忽略」,告警的 source 欄寫 `lumos`。
4. **README 實驗句**:中英兩版照原始紀錄寫:Haiku 4.5 只看程式碼答對 20 場、讀到故意寫錯的筆記只剩 12 場;Opus 每組都 25 場全對,實驗對它在天花板;筆記正確時的幫助還沒量。拿掉「標明以程式碼為準後回到 20 場」,原始紀錄對那組有「要打折扣」的保留。
5. **跟著改的文件**:`skills/lumos-code-loop/SKILL.md` 講 light 與 high 來源的那段、`skills/lumos-project-notes/commands/06-代碼審與推送.md` 補「想把某些路徑一律當高風險」那一列、`docs/指令參考.md` 的 pitfalls 與 lint-waive 說明、`cmd_lint_waive` 的說明字串(放行對象不只是誤報)、README 中英兩版「先判風險」那一點、`Systems/pitfalls-code-loop` 的分級 KEY 行(順序寫成:殘留索引、高風險路徑、風險型樣)。

## 不做

- 已經存在的忽略註解不追溯,只看這次新加的。
- 回合結束鉤子用的工作樹模式不數忽略註解:那條路的擋停訊息與白名單規則不同,另外評估。
- 高風險路徑清單不支援萬用字元,只認整段路徑的檔或目錄。
- ProcessLifecycleOwner 不豁免:官方頁說它是所有 Activity 的合成生命週期,沒有說它不是畫面,依據不足。
- 人工不能把分級往下調。
- Android Lint 的 Gradle 任務不經新增告警閘,`@SuppressLint`、`tools:ignore` 不在這次範圍。

## 實務隱患

- **字面比對會誤認**:字串常數或說明文字裡出現對照表的寫法(例如 `"# noqa"` 這個字串)也會被當成忽略註解,結果是多擋一條、走放行。實作本身把對照表寫成正規式字串(`#\s*noqa`),不會被自己的對照表認到。
- **改一行就算新增**:指紋用「規則+檔名+那一行的內容」,同一行改了別的字但留著 `# noqa`,會被算成新加的一條;這跟工具本身的告警同一套口徑。
- **同檔同一行複製貼上只要放行一次**:放行綁指紋,同檔一模一樣的一行第二次出現時,第一次的放行就涵蓋它。這是既有放行規則,工具本身的告警也一樣;另開 [[Issues/放行綁指紋同檔複製貼上的同一行不再擋]] 追蹤。
- **高風險只要求有一筆通過紀錄**:推送閘只看有沒有這一版的通過或 skip 紀錄,不比對那次審查迴圈定錨的分級,輕量迴圈的通過紀錄也算數。這是既有缺口,自然判出的 high 也一樣;另開 [[Issues/高風險改動用輕量審查通過也能推送]] 追蹤。
- **本 repo 也用 ruff**:之後新加 `# noqa` 要附理由放行;2026-09 以來 scripts/lumos 新加過 3 處,量小。
- **Kotlin 專案 `@Suppress` 量大**:只數括號裡有工具規則名的那些;編譯器警告名(全大寫底線)不算。
- 併發沿用放行檔讀改寫已上鎖的做法;效能是每條命令多讀一次改動檔的文字,檔數受既有大小上限管;設定檔多讀起點、終點兩版,每次推送多兩次 git 讀檔。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:不送任何資料到外部
- 已排除:不可逆:只改判定與文件,整段還原就回到原狀
- 碰到守衛面:三件都改推送閘或規則的判定,照守衛面處理(要過代碼審)。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 規則只管畫面的收集 | 官方說 repeatOnLifecycle 是為了「只在 UI 顯示在畫面上時處理」(This approach processes the flow emissions only when the UI is visible on the screen),2026-11-09 讀 | https://developer.android.com/topic/libraries/architecture/views/coroutines-views |
| Service 不是畫面 | 「A Service that is also a LifecycleOwner」,已知子類別 MediaSessionService、間接子類別 MediaLibraryService,2026-11-09 讀 | https://developer.android.com/reference/androidx/lifecycle/LifecycleService |
| 敏感路徑清單 | CODEOWNERS 用路徑指定敏感區要誰審;寫錯的行會被靜默略過,所以要讓對不到的路徑看得見 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners |
| 行內忽略要留痕 | SonarQube 把 NOSONAR 與 @SuppressWarnings 的使用當成要追蹤的問題 | https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-quality-gates/tracking-inline-comments |
| detekt 的抑制寫法 | 規則名放 @Suppress 的字串裡,可帶 detekt: 或規則集前綴,也接受 @SuppressWarnings | https://detekt.dev/docs/introduction/suppressing-rules |
| ruff 的抑制寫法 | `noqa` 不分大小寫、`#` 後可有空白;檔案層級用 `# ruff: noqa` 或 `# flake8: noqa`;另有 `ruff: ignore`、`ruff: file-ignore`、`ruff: disable` 註解,2026-11-09 讀 | https://docs.astral.sh/ruff/linter/#error-suppression |
| 不用提交訊息標記 | 提交訊息裡的標記寫錯會靜默失效(d7 理由) | [[Projects/進度從提交推導_計劃]] |
| README 實驗句 | 被測 claude-haiku-4-5;只看程式碼 20/25、現行 12/25;Opus 四組 25/25「在天花板」;丙組 20 有「要打折扣」的保留 | /Users/enzo/harness/lumos-gvc 工作樹的 Verification/2026-09-19_受控實驗程式碼為主四組對照(未提交);摘要見 [[Projects/Lumos定位_程式碼為主脈絡為輔_計劃]] |

## 驗收條款

- [S1] 當規則包樣本自測跑到 kt-lifecycle-collect-without-repeat 時,包在 LifecycleService、MediaSessionService 子類別裡的收集(launch 裡 collect、launch(Dispatchers.IO) 裡 collect、launchIn 三種)應 不報;同一支壞例檔裡另有 Service 類別時,Fragment、實作 MediaSessionService.Listener 的 Fragment、ProcessLifecycleOwner 的收集 應 照報 [test:t_kotlin_rulepack_samples]
- [S2] 當這次改到的檔在 risk_high_paths 列的檔或目錄底下時,分級 應 是 high 並列出檔名;清單從起點版拿掉的路徑 應 仍算數;設定讀不出 應 判 high;沒改到清單裡的路徑 應 不改分級 [test:t_pitfall_tier_risk_paths]
- [S3] 當推送範圍新加一行那條命令的工具認得的行內忽略註解時,新增告警閘 應 多出一條 lumos/inline-suppression 告警;原樣留著的、別的工具的寫法、編譯器警告名的 @Suppress、路徑裡出現工具名 應 不算;兩條命令認到同一工具 應 只算一次 [test:t_lint_new_inline_suppression]
- [S4] 當讀 README 中英兩版那句實驗時,應 寫明 Haiku 4.5 只看程式碼 20 場、讀到故意寫錯的筆記 12 場、Opus 在天花板、筆記正確時還沒量,且 不 寫加註後回到 20 場 [manual:對照 lumos-gvc 工作樹 Verification/2026-09-19_受控實驗程式碼為主四組對照 逐字核對中英兩版]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `class SyncService : LifecycleService()` 裡 `lifecycleScope.launch { flow.collect {} }` | 不報 | LifecycleService 官方說明是 Service;repeatOnLifecycle 官方適用範圍是 UI 在畫面上 |
| S1 | 同上類別裡 `lifecycleScope.launch(Dispatchers.IO) { flow.collect {} }` | 不報 | 原規則兩種 launch 寫法都認,例外也要兩種都豁免 |
| S1 | `repo.pings.onEach { }.launchIn(lifecycleScope)` 在 MediaSessionService 子類別裡 | 不報 | 同上 |
| S1 | 壞例檔同時有 `class SyncService : LifecycleService()` 與 `class SettingsFragment : Fragment()` 的 collect | Fragment 那處照報 | repeatOnLifecycle 官方範例就是 Fragment |
| S1 | `class Q : Fragment(), MediaSessionService.Listener` 裡的 collect | 照報 | 巢狀介面不是 Service 建構子呼叫 |
| S1 | Fragment 裡 `ProcessLifecycleOwner.get().lifecycleScope.launch { collect }` | 照報 | 本計劃不做:ProcessLifecycleOwner 依據不足 |
| S2 | 清單 `["src/auth"]`,改 `src/auth/Login.kt` | high,理由含 src/auth/Login.kt | 本計劃範圍 2 |
| S2 | 起點版清單有 `src/auth`,這次改動同時改 `src/auth/Login.kt` 並把清單清空 | high | 範圍 2:起點與終點聯集 |
| S2 | 設定檔 JSON 壞掉 | high,理由含讀不出 | 範圍 2:讀不出往 high |
| S2 | 清單 `["src/auth"]`,只改 `src/other.kt` | 照原本算(standard) | 範圍 2 |
| S2 | 清單 `["src/aut"]`,改 `src/auth/Login.kt` | 照原本算(整段路徑比對,aut 不含 auth) | `_e2e_under` 的既有語意 |
| S3 | ast-grep 命令,改動前一行 `// ast-grep-ignore: kt-x`,改動後多一行 `bar() // ast-grep-ignore` | 新增 1 條,在新加那行 | 範圍 3 |
| S3 | ruff 命令掃 `import os  # NOQA: F401` | 1 條 | ruff 文件:noqa 不分大小寫 |
| S3 | ruff 命令掃 .kt 檔裡的 `ast-grep-ignore` | 0 條 | 範圍 3 對照表 |
| S3 | `ast-grep scan --config tools/ruff-rules/sg.yml {LINT_FILES}` 掃 `x = 1  # noqa` | 0 條 | 範圍 3:路徑裡的工具名不算 |
| S3 | detekt 命令掃 `@Suppress("UNCHECKED_CAST")` 與 `@get:Suppress("MagicNumber")` | 只有後者 1 條 | detekt 文件;編譯器警告名不算 |
| S3 | 兩條 detekt 命令都掃同一支檔的同一行 `@Suppress("MagicNumber")` | 1 條 | 範圍 3:同一行只算一次 |
| S4 | 讀 README.md 與 README.en.md 那句實驗 | 兩版都寫 Haiku 4.5 20 場對 12 場、Opus 在天花板、筆記正確時還沒量,沒有「回到 20 場」 | 原始紀錄 Verification/2026-09-19_受控實驗程式碼為主四組對照 |

## 回退

- 規則例外:還原 state.yml 那條規則、兩個樣本檔與型錄 STATE-5 那列。
- 高風險路徑清單:拿掉分級函式讀 `risk_high_paths` 那一段與掛鉤提醒文字的改動;專案設定裡留著的鍵不再有作用。
- 忽略註解:拿掉推送範圍模式數忽略註解那一步;已寫的放行紀錄留著無害。
- README 與跟著改的文件:還原那幾段文字。

## 天花板

- 高風險路徑清單只解決「人能指定哪些地方要嚴審」,不解決單次改動臨時要升級;那種情況要人自己開高風險審查迴圈。
- 推送閘在幾種情況不跑 pitfalls 或拿不到分級(推送起點已在主線上、取不到頂端、pitfalls 失敗),這時高風險路徑也不會生效。
- 忽略註解只認對照表裡的工具與寫法;換一種寫法(例如工具新增的抑制語法)就認不出。
- 規則例外判斷不了「這段收集在需求上該不該在背景跑」;自寫基底類別間接繼承 Service 的情況認不出,照舊報,走放行。

REVISIT:2027-05-09 查放行紀錄裡 lumos/inline-suppression 的筆數,抽查理由裡誤認的比例,決定要不要照 RETIRE-IF ③ 改做法
REVISIT:2027-05-09 對照表跟 Systems/linter精選目錄 的工具菜單核對一次,菜單多了的工具補上它的忽略寫法
