severity: major

我把 spec 逐節讀完,並對照了程式碼、pre-push 掛鉤、樣本與 ast-grep 0.51.1 的實跑結果。

交叉引用全部核對過,都存在:
- `Systems/kotlin規則包`、`Systems/pitfalls-code-loop`、`Projects/進度從提交推導_計劃`、`Projects/Lumos定位_程式碼為主脈絡為輔_計劃`。
- 三個先紅測試名,以及 `_pitfall_tier`、`_diff_range_ends`、`lumos lint-waive <指紋> --note`、`spec-gate --push-check`、`loop next`。

實驗臨時目錄在 `/tmp/lumos-seat-work/簡報審查抓到的機制缺口/邊界-sonnet/`,請編排者收貨後刪。repo 沒動。

## 發現

**1. 範圍 2 與〈實務隱患〉「讀不到提交就不升」:空樹起點不會讓 git 失敗,會讀整段歷史**

severity: major
blocking: 是,spec 對 git 行為的宣稱是錯的,實作照字面做會在常見形狀誤升 high。

- 引句:「起點不是一個提交(例如新分支首推、範圍起點是空樹)、git 讀不出訊息時,分級照原本算」
- 實測:`git log 4b825dc642cb6eb9a060e54bf8d69288fbee4904..HEAD` 回 rc=0。在這個 repo 回 3400 個提交、約 1.5MB 的訊息,不會報錯。
- 掛鉤會真的送出這種起點。`pp_range_for` 在遠端舊值是全零或本機沒有該物件(force-push 後、淺層 clone)時,產出 `$_EMPTY_TREE..$_lsha`。`push-range` 算不出來時也退回空樹。
  - file: `scripts/hooks/pre-push:54`
  - file: `scripts/hooks/pre-push:67`
- 具體輸入:標籤推送,或 force-push 後舊頂端本機找不到。實作用 `git log 起點..終點` 讀訊息,會掃整段歷史。歷史裡任何一個提交(含落地本功能、訊息必然寫到 Lumos-Risk 的那個)都會讓這類推送永遠 high。
- spec 這一條寫的是「不升」,實際行為是「全歷史掃描、幾乎必升」。〈預期值表〉和 `t_pitfall_tier_human_high` 都沒有空樹案例。
- 補法:要嘛明寫「起點是空樹時不讀訊息」並加測試,要嘛承認要掃整段歷史。

**2. 範圍 2:訊息解碼與例外處理沒定義,一個壞編碼的提交訊息會讓整道分級 fail-open**

severity: major
blocking: 是,這是「高風險要先審查」整個消失的 fail-open 路徑,先例在同檔就有。

- 具體輸入:範圍內有一個提交,訊息是原始的非 UTF-8 位元組。用 `git hash-object -t commit -w --literally` 造出訊息 `fix \xa4\xa4 Lumos-Risk: high`。
- `git log --format=%B` 原樣吐出 `\244\244`。`subprocess.run(..., text=True)` 立刻拋 `UnicodeDecodeError`(我實跑重現了)。`_pitfall_tier` 沒接例外,`pitfalls` 回非零。
- `_codeloop_pitfalls_tier` 把非零一律當 fail-open,回 `tier: "unknown"`、`blocked: False`。不只人工標記讀不到,連本來會命中的 `claims` 高風險也一併消失。
  - file: `scripts/lumos:75193`
  - file: `scripts/lumos:75203`
- 掛鉤那頭的 `pitfalls ... || true` 也一樣吞掉。
  - file: `scripts/hooks/pre-push:567`
- 同檔已有同形事故的教訓:
  - file: `scripts/lumos:65029`
- spec 只寫「git 讀不出訊息時,分級照原本算」。逾時、解碼錯誤、`git log` 回非零是否都算「讀不出」?`errors="replace"` 有沒有用?這些都沒定。
- 〈天花板〉第二點的描述也跟程式不符:「算不出推送起點 → 當 standard」。實際上 pitfalls 失敗是 `unknown` 加 fail-open,不是 standard。
  - 引句:「推送閘在兩種情況不跑 pitfalls、直接當 standard(推送起點等於現在、算不出推送起點)」
  - 程式裡回 standard 的是「頂端已在主線上」;全零或本機找不到的起點,`_lens_push_base` 是退到分岔點,再不行才用空樹。

**3. 範圍 2 與 PRIOR-ART ②:「空白都不拘」與正規式不符,有格式寫錯會靜默沒作用**

severity: major
blocking: 是,這直接推翻方案「寫錯格式會多審、不會靜默」的核心論點。

- 引句:「大小寫、連字號、底線、空白都不拘」
- 引句:「任何一行出現 `Lumos-Risk` 字樣(正規式 `lumos[-_ ]?risk`,不分大小寫)就判 high」
- 正規式的 `[-_ ]?` 只吃一個 ASCII 字元。實測下列輸入都不命中,結果是靜默不升:
  - `Lumos  Risk: high`(兩個空白)
  - `Lumos<Tab>Risk`
  - `Lumos　Risk`(U+3000 全形空白,中文使用者很常打)
  - `Lumos‑Risk`(U+2011)、`Lumos–Risk`(en dash,macOS 智慧標點會自動換出來)
  - 編輯器在 72 欄折行成 `Lumos-` 換行 `Risk: high`
- 沒有字邊界,反過來誤中:`lumos riskscore`、`Merge branch 'feat/lumos-risk-marker'`。後者屬於已承認的取捨,但前面幾種靜默失效沒被承認。
- 補法:正規式改成 `lumos[\s\-_\u2010-\u2015\u3000]*risk`,或把宣稱收窄成「只認單一 `-`、`_`、空白」。

**4. 範圍 2「這次範圍」:單一版本範圍(終點為 None)沒定義**

severity: minor
blocking: 否,影響限於手動 `pitfalls --diff` 與推送結果不一致。

- `_diff_range_ends("HEAD~2")` 回 `("HEAD~2", None)`。spec 寫的是 `git log 起點..終點`。
- 照字面組字串會得到 `HEAD~2..None`。實測 git 回 `fatal: ambiguous argument`,結果是標記不升。
- 具體輸入:`lumos pitfalls --diff main`(拿 main 比工作目錄)。人工標記在 HEAD 的訊息裡,輸出仍是 standard,但推送閘對同一批提交會是 high。
- 要明寫「終點 None 視為 HEAD」,或明寫此形狀不讀訊息。

**5. 範圍 2、〈實務隱患〉「順手提到也算」:放大器比 spec 承認的多**

severity: minor
blocking: 否,方向是多審,已被刻意接受;但會讓 `RETIRE-IF ②` 的觸發計數被污染。

- 現有分支再推時,掛鉤範圍是 `rsha..lsha`。分支合過主線後,主線上的提交訊息會進範圍,這是既有的「合過主線會多算」問題。
  - file: `scripts/hooks/pre-push:511`
- 本功能落地後,主線上必然有訊息提到 Lumos-Risk 的提交,以及 `Merge pull request #N from .../lumos-risk-...` 這種含分支名的合併訊息。
- 具體輸入:另一條分支合入含這些提交的 main 後第一次推送,會被判 high。
- spec 只承認「實作本功能的提交本身」。

**6. 範圍 2「生效處」:標記升 high 還會產生 spec 沒列的副作用**

severity: minor
blocking: 否,這跟自然 high 同一套行為,但「生效處」清單不完整,讀者會以為只多一道留痕。

- 掛鉤只在 `tier != high` 時才帶 `--bound-tests-advisory`。人工標記升 high 後,原本只提醒的受波及合約測試變成紅就擋。
  - file: `scripts/hooks/pre-push:634`
  - file: `scripts/lumos:75327`
- 〈預期值表〉「只改 Markdown + 標記 → high」會讓純文件推送也被迫跑非 advisory 的合約測試。
- 掛鉤會印「程式碼裡有高風險寫法…命中的地方列在下面」,但標記造成的 high 沒有命中清單。
  - file: `scripts/hooks/pre-push:577`
- 另外 `code-loop` 留痕只存 `head_sha`、`status`、`note`、`ts`,不記迴圈分級。輕量迴圈 pass 也能滿足被標記升高的 high。
  - file: `scripts/lumos:72233`
- spec 已承認「不生效處」,但沒有說明這一點:標記保證的是「要有一筆 pass 或 skip」,不是「要過 high 的席位編制」。

**7. 範圍 3:ruff 的 `noqa` 是大小寫不分,對照表沒說,`# NOQA` 直接繞過**

severity: major
blocking: 是,這是 S3 要補的洞本身,而且是最常見的拼法。

- 引句:「ruff→`noqa`;eslint→`eslint-disable`」
- 實測 ruff 0.16.7:`import os  # NOQA: F401`、`# NoQA`、`#noqa` 都會被 ruff 當成抑制,`ruff check --select F401` 回「All checks passed」。
- S2 的正規式明寫不分大小寫,S3 沒寫。字面比對照預設大小寫區分時,`# NOQA: F401`(flake8 官方文件拼法)數出 0 條,閘完全看不到。
- 補法:ruff 項用不分大小寫比對,並加 `# NOQA` 的測試。

**8. 範圍 3:對照表漏掉 detekt 實際會認的標準寫法**

severity: minor
blocking: 否,〈天花板〉承認「只認對照表」,但漏的不是冷門語法。

- 實測 detekt:
  ```kotlin
  @get:Suppress("MagicNumber") val x: Int get() = 42
  ```
  不報 MagicNumber。同檔另一個沒標的 `43` 才報。
- 這種寫法有 `@get:Suppress`、`@field:Suppress`、`@param:Suppress`、`@kotlin.Suppress(`。
- 表只有 `@Suppress(`、`@file:Suppress(`、`@SuppressWarnings(`,所以 `@get:Suppress(` 數出 0 條。
- 引句:「detekt→`@Suppress(`、`@file:Suppress(`、`@SuppressWarnings(`」

**9. 範圍 3:「整條命令字串用正規式找工具名」會被路徑中的工具名誤認**

severity: minor
blocking: 否,後果是多擋一條且可放行。

- 具體輸入:py 棧宣告 `ast-grep scan --config $HOME/harness/ruff-rules/sgconfig.yml {LINT_FILES} > {LINT_SARIF_OUT}`。
- `ruff-rules` 的 `-` 是非字元,所以 `\bruff\b` 命中。這條命令被同時認成 ast-grep 與 ruff,卻根本沒跑 ruff。
- `.py` 檔新增一行 `# noqa` 會被當成新增告警擋下。
- 同理 `semgrep --config p/eslint-...` 之類。
- 引句:「整條命令字串用正規式找工具名」
- 建議限定在「第一個詞,或 `npx`、`uv run`、`python -m` 之後的詞」,而不是整串。

**10. 範圍 3、〈實務隱患〉:實作提交會被自己的閘擋下,spec 沒講**

severity: minor
blocking: 否。

- 對照表本身要進 `scripts/lumos`。`scripts/lumos` 靠 shebang 被認成 py,被宣告的 ruff 命令掃到。
  - file: `.lumos/lint.json:1`
- 現在 `scripts/lumos` 只有 1 行 `noqa`(`scripts/lumos:39047`)。表格、docstring 每多一行含 `noqa` 的字面,推送時就是一條新增告警。
- 〈實務隱患〉只講了「之後新加 `# noqa`」,沒講本提交要先逐條 `lint-waive`。每條放行的指紋綁行內容,之後改那行又要重放行。

**11. 驗收條款 S1 與預期值表:「同一支檔」的 Fragment 沒有被測到**

severity: major
blocking: 是,測試殺不死一個合理的錯誤實作。

- 引句:「同一支檔裡 Fragment 的收集 應 照報」
- 已提交的先紅樣本,壞例檔只有 Fragment、沒有 Service。
  - file: `configs/ast-grep/kotlin-android/samples/bad/kt-lifecycle-collect-without-repeat/src/main/kotlin/kt-lifecycle-collect-without-repeat.kt:15`
- 好例檔只有 Service 與 Application。`check.py` 對壞例、好例各自掃目錄,從來沒有同時含 Service 和 Fragment 的檔。
- 我造了「檔層級例外」突變規則:只要檔裡任何地方有 `LifecycleService`、`MediaSessionService`、`MediaLibraryService` 的 `delegation_specifier` 就整檔豁免。
  - 已提交的壞例:4 處命中,過。
  - 已提交的好例:0 命中,過。
  - 混合檔(Service 加 Fragment 各一個 collect):0 命中。Fragment 被靜默放掉。
- 壞例檔裡「Service 檔案裡的 Fragment」那行註解,實際檔案裡沒有 Service。
- 補法:壞例檔裡放一個 Service 加 Fragment 的混合檔。

**12. 範圍 1:「只看那一層類別,不看裡面的內部類別」有歧義,兩種讀法的行為相反**

severity: minor
blocking: 否。

- 引句:「認法:類別宣告的直接繼承清單裡有這三個名字之一,只看那一層類別,不看裡面的內部類別」
- 壞例檔的註解寫的是「例外只看外層類別」。
- 用自然的寫法 `not: inside: {kind: class_declaration, has: delegation_specifier ^(三名)\b, stopBy: end}` 實測:
  - A:`class SyncService : LifecycleService() { class UiFragment : Fragment() { fun f() { lifecycleScope.launch { vm.c.collect { } } } } }` 回 0 命中。Service 裡的巢狀 Fragment 被豁免。「只看最近一層類別」的讀法會要求報。
  - B:`class Outer : AppCompatActivity() { inner class Svc : LifecycleService() {…collect…} }` 回 0 命中。「只看外層類別」的讀法會要求報。
- 兩種都沒有測試,也沒有預期值列。要明寫選哪一種。

**13. 範圍 1:「名字之一」會把實作 Service 巢狀介面的非 Service 類別也豁免**

severity: minor
blocking: 否。

- 實測 `\b` 結尾的比對:
  ```kotlin
  class Q4 : Fragment(), MediaSessionService.Listener { … lifecycleScope.launch { vm.h.collect { } } }
  ```
  回 0 命中。
- `class Q5 : Foo(), LifecycleService.Callback by impl` 同樣 0 命中。
- Media3 的 `MediaLibraryService.MediaLibrarySession.Callback` 常由獨立 helper 類別實作,那種類別不是 Service,卻會被豁免。
- 反面:`androidx.lifecycle.LifecycleService()`(全名)用 `^` 錨定時不豁免。
- 要明寫「constructor 呼叫形式 `Name(` 才算」,並決定全名要不要認。

**14. 範圍 1 與 S1:ProcessLifecycleOwner 的例外只覆蓋樣本裡那兩種寫法**

severity: minor
blocking: 否,殘留的是誤報,可放行。

- 實測:
  - `ProcessLifecycleOwner.get().lifecycleScope.launch(Dispatchers.IO) { flow.collect { } }`:1 命中,仍被報。
  - `val owner = ProcessLifecycleOwner.get(); owner.lifecycleScope.launch { … collect … }`:1 命中,仍被報。
- 原規則的 `inside` 本來就有 `launch { }` 與 `launch(...) { }` 兩種。樣本只有 `launch {`,只實作單一形式也能過 S1。
- 反向:`ProcessLifecycleOwner…launch { viewLifecycleOwner.lifecycleScope.launch { x.collect {} } }` 在 Fragment 裡 0 命中,UI 收集被漏。
- 補一列 `launch(Dispatchers.IO)` 的樣本,並說明別名與巢狀怎麼處理。

**15. 〈回退〉:仍寫 trailer 與文字殘缺**

severity: minor
blocking: 否。

- 引句:「拿掉分級函式讀 trailer 那一段;已寫進提交訊息的 trailer 不影響任何東西。」
- 這份計劃已經改成「不照 trailer 格式認」,回退沒跟上。
- 引句:「拿掉新增告警閘多數忽略註解那一行」
- 「多數」是病句,大概是「數」。

**16. RETIRE-IF ② 與 REVISIT:撤除條件現在量不出來**

severity: minor
blocking: 否,但按專案規則「寫不出撤除條件就是還沒想清楚」,現在是量不出的。

- 引句:「半年內沒有任何一次推送讀到 Lumos-Risk 標記」
- spec 沒有在標記命中時寫任何治理帳事件。`tier_reason` 只印在輸出,擋下事件是泛用的「tier=high 且…」,分不出是標記還是自然 high。半年後無從統計。
- 引句:「查新增告警放行紀錄裡 lumos-inline-suppression 的筆數與誤認比例」
- 放行紀錄有 `rule` 欄所以筆數可數,但「誤認」沒有欄位,只能人工逐條讀 `note`。
- 要補一個標記命中的帳事件,以及放行時區分誤認的欄位。

**17. 〈依據來源〉:兩處引用站不住**

severity: minor
blocking: 否。

- S4 與範圍 4 寫「Haiku 4.5」。唯一的引用來源 `Projects/Lumos定位_程式碼為主脈絡為輔_計劃` 只寫「Haiku」,全篇沒有版本號。
  - file: `docs/lumos-toolchain-knowledge/Projects/Lumos定位_程式碼為主脈絡為輔_計劃.md:28`
  - S4 的 `[manual: 逐字核對]` 對不出 ".5"。README 目前已寫「Haiku 4.5」,版本號出處需要補或拿掉。
- 方案引的決策 d7 在筆記裡是 `valid: false`,`superseded_by: d8`,而 d8 又被 d10 取代。
  - file: `docs/lumos-toolchain-knowledge/Projects/進度從提交推導_計劃.md:77`
  - 引用的那句話(trailer 寫錯等於沒寫)確實在 d7 的 `why_chosen` 裡,但來源本身已被翻案,spec 沒說明。

## 已讀、無 finding 的段落

- 用詞(除上面第 3、4 點已提到的)、〈不做〉。
- 範圍 4 / S4:HEAD 的 README 兩版第 450 行與計劃原文的 20/25、12/25、25/25、「筆記正確時還沒量」一致。版本號問題見第 17 點。
- S3 的 `lint-waive` 流程:`cmd_lint_waive` 的指紋與 `--note` 都在。
- 效能與記憶體:`git log` 3400 個提交、1.5MB 的訊息只要 0.05 秒,沒問題。超大檔案已被 `_lint_new_oversize`(5MB 或 6 萬行)在跑命令前彈掉,所以〈實務隱患〉說的「受既有上限管」成立。
- 併發沿用既有鎖、不可逆、金流、對外送出,spec 已排除,我同意。外來文字回顯的資安面,依 lumos 單人威脅模型放行,不列。

## 實務隱患鏡頭

- fail-open 類:有,見第 2 點。
- 範圍與歷史讀取類:有,見第 1、4、5 點。
- 規則誤報與漏報類:有,見第 3、7、8、9、11 至 14 點。
- 其餘風險類:無。上面已逐項說明為什麼。

最嚴重 severity: major,blocking 共 5 條(第 1、2、3、7、11 點)。
