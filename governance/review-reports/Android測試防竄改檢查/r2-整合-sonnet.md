severity: major

## 逐節結果

- 問題與最小解、名詞、回退:已讀,無 finding。回退節沒列文件與測試的還原項,併入下面 F3、F5、F7。
- 做法一(比對工具):F3、F12。
- 做法二(併進新增告警閘):F1、F2、F4、F5、F6、F11。
- 做法三(Semgrep):F8、F9。
- 做法四(標準改寫):F7。
- 做法五(六條小問題):已讀,無 finding。三條回頭條件確實掛在 `test_quality.py`,而 `Systems/test-quality-cli.md:37` 等三行都在。
- 做法六(考場)、第二批、驗收條款:已讀,無 finding(先前舊計劃的 REVISIT 六條在第二批有承接)。
- 引用的研讀結論抽查:3.5–6.5 倍、約 8 倍(137.69 / 16.46)、63%、四分之一、jqwik 反 AI 條款、PIT 2022-03-02 結案、arcmutate 仍是 beta、`failOnPassedAfterRetry` 預設 false,都對得上報告原文。`ViewModelScenario.recreate()` 在 2.9.0 起是真的,我用官方發行說明核過。但這條不在研讀報告裡,只在計劃自己的來源清單,不算報告結論。唯一對不上的是 F9。
- 實務隱患:已讀。其中「消費專案要等 `lumos update`」成立,但適用範圍講窄了,見 F10。

## findings

### F1 warn 與「AI 放行待看」的輸出,在推送掛鉤上會被濾掉,看不到
severity: major
blocking: 是(實作後 r1 的 C2/I10 修補在實際推送時等於沒有效果,屬 major)
引句:「設成 warn 時,新增告警(含比對候選)逐條印出來,小結寫」
file: `scripts/hooks/pre-push:637` 放行路徑只轉印 `grep -E '提醒|受波及合約測試|表態閘|安全證據'`。
- 新增告警閘的小結行以 `  新增告警閘:` 開頭(`scripts/lumos:68967` 起的 `_cl_say_ok_extras`),裡面沒有這四個詞,今天就被濾掉。
- 計劃要新增的「逐條印出」「只報不擋,有 N 條」「AI 放行還沒人看過」三類輸出,同樣不含這四個詞,推送時看不到。
- Android 端到端驗收的同類輸出都以 `提醒:` 開頭(`scripts/lumos:68925`),所以過得了這個濾網。
- 計劃沒說要改掛鉤或給這些行加 `提醒` 前綴。
- 計劃的「做法二」和 S14 只測 `_lint_new_verdict` 與印出函式,沒有任何條款測掛鉤。
- 我沒有實跑掛鉤。這條是讀 `pre-push:637` 與 `scripts/lumos:68967` 起的 `_cl_say_ok_extras` 得出的。

### F2 `lint_new.gate` 改成從 git 讀,會打破既有測試與對外文件,計劃都沒列
severity: major
blocking: 是(照計劃做完,`t_lint_gate_modes` 會紅,對外文件會變成假的)
引句:「從 git 讀兩端的 `.lumos/config.json` 的 `lint_new.gate`(不讀工作目錄)」
file: `scripts/test_lumos.py:72232-72241` 的 `t_lint_gate_modes`(S13)只把 `{"lint_new":{"gate":"warn"}}` 與 `off` 寫進工作目錄、沒提交,就呼叫 `_lint_new_verdict` 並期待 `status == "warn"` 和 `"off"`。改成讀 git 後,這兩個期望都會變成預設的 block,測試轉紅。
file: `docs/指令參考.md:162` 和 `docs/command-reference.md:162` 明寫「`lint_new`、`stack_questions` 讀工作目錄那份(只改沒提交時,本機照新值、CI 照提交裡的舊值)」。計劃改完後這句就是假的。
- `docs/指令參考.md:174` 和 `docs/command-reference.md:174` 的 `lint_new.gate` 說明只寫「新增的 linter 告警」,也要補上比對候選。
- 這些都沒進計劃的同步清單。
- 同一個函式裡 `budget_sec` 等其他鍵仍讀工作目錄(`scripts/lumos:67954` 起的 `_codeloop_lint_new_step` 就這樣取預算)。計劃沒說清楚是只有 `gate` 改源、其他鍵不改。

### F3 新頂層指令 `lumos test-guard` 的同步點完全沒列,會讓既有測試紅
severity: major
blocking: 是(計劃缺一份實作者必須照做的同步清單,全套測試會因此紅)
引句:「在主程式加一支比對工具 `lumos test-guard`」
file: `scripts/test_lumos.py:39562-39598` 的 `t_docs_command_count`。
- 命令數取自 `--help`,現在是 97,加了就是 98。
- 文件寫死的數字有 `ARCHITECTURE.md:108,112,142` 和 `skills/lumos-project-notes/reference.md:118,1265`,要全部改成 98。
- `skills/lumos-project-notes/reference.md:118` 的子命令全覽也要補 `test-guard` 的歸類。
file: `scripts/test_lumos.py:11245-11275` 的 `t_command_index_complete`。每個頂層子指令都要在 `skills/lumos-project-notes/commands/*.md` 的語料裡出現 `lumos test-guard`,例如 `06-代碼審與推送.md` 和 `INDEX.md`。Room 守衛有對應的 `t_room_guard_registered` 釘這幾處。
file: `scripts/lumos:69606` 一帶的 `HELP_WHEN` 說明表要加一句「什麼時候用」,`argparse` 要加 subparser 與 `main` 分派。
- 掛鉤不用接:計劃走 `code-loop check` 內呼叫,這一點成立。`README.md` 和 `docs/指令參考.md` 沒列 `room-guard`,所以不必列,有前例。
- `ARCHITECTURE.md` 與 `reference.md` 的命令數在 `t_docs_command_count` 的 `skip` 名單之外,必須同步。
- 計劃的回退節也沒列這些文件。

### F4 「舊紀錄沒有 `by` 欄的當人放的」的前提是錯的,現有紀錄全都有 `by`
severity: major
blocking: 是(遷移規則建立在錯誤事實上,實作者照字面做會把全部舊放行當成待看或誤判)
引句:「舊紀錄沒有 `by` 欄的當人放的」
file: `scripts/lumos:38707-38722` 的 `_lint_waivers_add` 一直寫 `"by": who`,`who` 是 `$USER`。
- 本 repo 的 `.lumos/lint-waivers.json` 共 352 筆,`by` 的分佈是 `enzo` 347、`unknown` 5,沒有任何一筆缺 `by`。
- 計劃要把 `by` 改成 `human` 或 `ai`,等於重用一個已經有別的意思的欄位。
- 計劃沒定義「`by` 是使用者名」這種舊值怎麼歸類。若實作成「非 `human` 即待看」,352 筆舊放行都會被健檢列成「AI 放的,還沒人看過」;若實作成「只有 `ai` 才算」,名叫 `ai` 的使用者會被誤判。
- 改成 `human` 後,原本記在 `by` 的「誰放的」資訊消失,計劃也沒補 `who` 這類欄位。端到端驗收的紀錄是 `by`、`who`、`acked` 三欄。
- 回退節說「`by` 欄被舊版忽略」,漏了新舊版對同一欄意義不同這件事。

### F5 放行理由至少 10 字,與既有測試及對外文件不合,計劃沒列
severity: major
blocking: 是(`t_lint_waive_cli_records_rule_and_file` 會紅)
引句:「`lint-waive` 的理由至少 10 個字而且有實字」
file: `scripts/test_lumos.py:72267-72300` 的 `t_lint_waive_cli_records_rule_and_file`,用 `--note "誤報"`(2 個字)走真實命令列,期待回傳碼 0。改版後會被拒絕。
- 這支測試用 `subprocess.run` 沒隔離標準輸入。加了 `_confirm_tty(..., stdin_timeout=True)` 之後,開發者在終端機裡跑測試,每次呼叫最多等 30 秒。端到端驗收的測試用 `LUMOS_TTY=/nonexistent-tty` 與 pty 隔離,見 `scripts/test_lumos.py:21190` 起的 `t_android_e2e_waive`。S15 與這支舊測試都得照辦。
- `docs/指令參考.md:139`、`docs/command-reference.md:139` 的 `lint-waive` 說明、`skills/lumos-project-notes/commands/06-代碼審與推送.md:14` 都沒有 `--ack`、理由門檻、`--list` 的新標記。
- 這個理由門檻是套到全部新增告警閘的放行,會影響所有消費專案,不只 `tq/` 候選。升級說明沒寫。

### F6 「照搬 `_e2e_waive_cmd`」與實際差別在「答 n」
severity: minor
blocking: 否(語意差異需要明說,不阻擋實作)
引句:「沒有互動終端、讀不到回答或答 n 都記 `by: ai`」
file: `scripts/lumos:42681` 起的 `_e2e_waive_cmd`:答 n(`ans is False`)回 1、不寫入;只有 `None` 才記 `ai`。測試 `scripts/test_lumos.py:21215` 也釘「終端答 n→回 1、不寫」。
- 計劃卻寫成「照搬」並讓答 n 也寫入,只是標成 AI。
- 人在終端按 n 想取消,放行卻已寫進要提交的檔。
- 提問措辭「這筆放行是你本人確認的嗎」讓 n 可以讀成「不是我」,這是可辯護的設計,但「照搬」這個說法對不上,應改成明寫的偏離。

### F7 標準改寫要保住的測試字串,少列了釘住結構的測試
severity: minor
blocking: 否(實作時全套測試會抓到,不會漏進主線)
引句:「改寫時保住兩支既有測試釘的字串」
file: `scripts/test_lumos.py:120086-120110` 的 `t_test_quality_standard_android_unit_section`(S1)釘:
- `### Android 本機單元測試的驗收標準` 必須緊接在 `### C#、Android、iOS 的原生收證接入` 之後;
- 三段粗體依序:**要有哪些**、**怎麼寫才算數**、**什麼證據才算過**;
- 關鍵詞與單源連結。
- 計劃要「新增〈推送前的防竄改檢查〉一節」,卻沒說放哪裡。放在原生收證之後就會讓 S1 轉紅。
- `t_test_quality_standard_android_room_section` 與網頁前端那支測試也各釘一節。
- `skills/lumos-project-notes/commands/03-寫回圖譜.md` 的〈實作測試品質〉被 CLAUDE.md 稱為單一來源,末段有指向標準各節的導覽句。計劃新增〈推送前的防竄改檢查〉與答案表先行,卻沒要求在 03 補導覽。讀 03 的人不會知道新節存在。

### F8 Semgrep 新增的五條樣式只驗過一條
severity: minor
blocking: 否(S17 與考場實跑會暴露,但屬風險)
引句:「與 Hamcrest 的 `assertThat($X, equalTo($X))`、`assertThat($X, is($X))`」
file: `scripts/test_quality_semgrep.py:61` 把所有樣式放進同一條規則的 `pattern-either`,並用 `--strict` 執行。
- 計劃自述只實測了第一條,S17 也只驗兩種寫法。
- Kotlin 的 `is` 是保留字,`assertThat($X, is($X))` 在 Kotlin 樣式語法下可能解析失敗。我沒有 Semgrep 可跑,但這條不能當成「已驗」。
- 一旦其中一條樣式解析失敗,整條規則(含既有的 `assertEquals`)就整個掃不出來。
- 計劃應把樣式逐條實跑列為 S17 的前置條件,或把 Kotlin 的 Hamcrest `is` 拿掉。

### F9 「Sonar 都沒有現成規則」說得太寬
severity: minor
blocking: 否(措辭不影響實作,但引用與報告不一致)
引句:「detekt、Konsist、Android Lint、Sonar 都沒有現成規則抓這兩種(Android Lint 只有 `IgnoreWithoutReason`)」
file: `governance/eval/results/ai-test-verification-research-20261102/smells.md:451` 的表頭寫的是「Sonar Kotlin」,並說 S2699(沒有斷言)只有 Java、C# 等語言版。
- 計劃的比對工具同時掃 `.java` 測試檔,Java 有現成的 S2699。
- 「沒有現成工具」這句只對 Kotlin 成立。

### F10 消費專案升級後的行為變化,不只是 Android
severity: minor
blocking: 否(屬 `lumos update` 的說明缺漏)
引句:「原本「沒宣告檢查工具就不判」的 Android 專案,只要改到 Kotlin 或 Java 測試、建置檔、呼叫 Gradle 的 CI 行就可能被擋」
- 觸發條件只看副檔名與路徑,沒有 Android 判斷。任何 JVM 後端專案(例如本會談所在的 Backend_improve 這類 Java/Kotlin 專案)升級後,新增 `@Ignore`、`@Disabled`、`ignoreFailures`,或動到 `*.gradle`,都會被擋。
- 路徑裡有 `screenshots` 或 `snapshots` 的圖檔,不分棧都會觸發 `tq/snapshot-changed`。
- `.lumos/config.json` 被改動也會觸發比對(`tq/gate-config`)。
- 實務隱患只寫 Android,升級說明與關閉方式(`gate: warn` 或 `off`)沒有對一般消費專案講。
- 這個範圍是刻意還是意外,計劃應先說清楚。
- 另外 `docs/.governance-log.jsonl` 在 `_GOV_LOCAL_PAIRS` 白名單之外,`lint-new` 的 `warned`、`skipped`、`skipped-env` 都會寫進版控帳。warn 模式每次推送都可能弄髒追蹤檔。這與其他閘同款,不算新問題,但計劃說「沒有新的共用寫入點」略漏了這一點。

### F11 放行檔讀不了時,擋下訊息教人做的事做不到,帳也自相矛盾
severity: minor
blocking: 否(僅影響壞檔這個少見情境)
引句:「放行檔讀不了時,既有的檢查工具那半照舊自動放行並記帳;比對候選照判,放行視為空」
file: `scripts/lumos:38707` 起的 `_lint_waivers_add` 在檔壞掉時回「放行檔讀不了」,所以擋下訊息印出的 `lumos lint-waive <指紋>` 指令一定失敗。
- 計劃沒定義這個情境的訊息要怎麼寫,唯一出口是 warn、off 或環境變數。
- 同一次判定還會同時出現 `autopass` 與 `blocked`:`_codeloop_lint_new_step` 會先寫 fail-open 帳,再擋下推送。

### F12 S16 說 Room 守衛方法擷取「不變」,但擴充 `=` 後接大括號的處理會改變 DAO 的 span
severity: minor
blocking: 否(實作者會被 Room 守衛既有測試抓到,但條款自相矛盾)
引句:「而 Room 守衛既有的方法擷取行為不變」
file: `scripts/lumos:47735-47752` 的 `_rg_method_end` 遇到 `=` 就收在該行行尾。
- 計劃要改成配到對應的右大括號。
- Room 的 `@Transaction open fun x() = db.withTransaction { … }` 是常見寫法,它的 span 會因此變大,Room 守衛判定的「改到的 DAO 方法」範圍也跟著變。
- 這是修正,不是「不變」。S16 與「擴充時補 Room 守衛那邊的回歸測試」兩句要改成明寫行為變化。

### F13 改了配套指紋,相依的驗證紀錄的重驗條件被觸發,計劃沒提
severity: minor
blocking: 否(重驗條件未處理)
引句:「改了 `test_quality_semgrep.py` 要重算配套指紋表裡它那一格」
file: `docs/lumos-toolchain-knowledge/Verification/測試品質第四輪修補驗證.md:6` 的 `revalidate_when` 寫「…bundle digest 或 Semgrep finding 轉換時」。
- 這次同時改了指紋表與 Semgrep 規則,等於觸發這條重驗,計劃的「六條小修」與「回退」都沒處理這篇驗證紀錄。

## 固定席節點逐條判

- `Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject 不動 sentinel 之外的內容):不影響。計劃不碰 CLAUDE.md 注入,新增的只是主程式內的函式與指令。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):不破壞。計劃的「逐條改壞一次確認會紅」方向相符,但新測試 `t_tq_guard_*` 與 S19 實作時要各自帶「現場成立」的前置斷言,計劃沒明寫,提醒而已。
- `Issues/deinit整夾刪使用者檔`:不影響。沒有新增被 vendored 進消費專案的檔,`deinit` 刪除範圍不變。
- `Verification/測試品質第四輪修補驗證`:見 F13。
- `Systems/test-quality-cli` 的三條 `when-file:scripts/test_quality.py` 回頭條件:不被觸發,因為計劃不改 `scripts/test_quality.py`,只改 `scripts/test_quality_semgrep.py`。

## 風險類逐類答

- 既有測試期望被打破:會。`t_lint_gate_modes`(F2)、`t_lint_waive_cli_records_rule_and_file`(F5)、`t_docs_command_count`、`t_command_index_complete`(F3)。標準的 S1 若節位置放錯也會紅(F7)。新增告警閘狀態與訊息的測試用假判定,多半不受影響。
- 新指令同步:缺 `HELP_WHEN`、命令數文件、commands 語料(F3)。不需要掛鉤接線,也不需要改 CI。
- 筆記、標準、skill 文字對不上而計劃沒列:`docs/指令參考.md` 和 `docs/command-reference.md` 的 162、174、139 行、`06-代碼審與推送.md:14`、03 的導覽句、`reference.md`、`ARCHITECTURE.md`(F2、F3、F5、F7)。
- 配套指紋:重算那一格這點成立。漏的是 F13。
- 消費專案升級:範圍不只 Android(F10);理由門檻與 `by` 欄會一起影響既有放行檔(F4、F5)。

總結:最嚴重等級 major,blocking 共 5 條(F1、F2、F3、F4、F5)
