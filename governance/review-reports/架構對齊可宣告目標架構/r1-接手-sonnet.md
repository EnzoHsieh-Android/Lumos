severity: major

整份 spec 照字面做得出 S1–S4 的程式碼骨架。但三個月後要在 Laravel 舊系統或 Android 新模組啟用它的人，會撞到下面幾面牆。

**HND-1**
severity: major
blocking: 是
引句:「所以範圍寫在版控設定、doctor 與 code-loop check 都會印出來」
審材外佐證 file: `scripts/lumos:26625`
審材外佐證 file: `docs/lumos-toolchain-knowledge/Projects/代碼審前後端角色鏡頭_計劃.md:96`
審材外佐證 file: `scripts/lumos:28856`
- 問題：spec 把「寫在版控」當成防後門，但沒說 `arch_targets` 與目標節點要讀哪個版本。同一個分支可以在同一次推送裡新增 `arch_targets`、或把目標節點的規則改鬆，來決定自己被怎麼審。印出來只能事後看。
- 既有做法有兩種，而且互相不同：
  - `review_roles` 讀改動起點版本，理由明寫「被審的分支不能自己改宣告決定自己拿到哪張卡」。
  - `node_home` 讀被檢查的快照。
- spec 兩種都沒選。
- 逐條貼進派工詞的規則文字是專案自寫的自由文字。讀的若是分支版本，被審者就能往審查席的指令區塞字。
- 判準：S1–S4 要補「讀哪個版本」，並加一條測試，例如分支改 config 但起點沒宣告時，該檔仍走鄰居基準。

**HND-2**
severity: major
blocking: 是
引句:「能寫成架構測試的規則交給該棧現成工具並走既有合約綁定」
審材外佐證 file: `scripts/lumos:7490`
審材外佐證 file: `scripts/lumos:5502`
審材外佐證 file: `scripts/lumos:5634`
- 問題：「走既有合約綁定」在現況不成立。
  - 既有的 `[test:]` 綁定只認兩處：摘要裡的 ★INVARIANT★ 類合約行（`_contract_texts`），以及計劃的 `[S<n>]` 條款。正文〈目標規則〉裡的 `[A<n>]` 沒有解析器，也沒有 doctor 的懸空檢查。
  - S1–S5 沒有任何一條驗 `[A]` 的 `[test:]` 能解析、會被檢查。
- 照 spec 做的人會碰到：
  - **Laravel**：`TEST_PROFILES` 沒有 php。要靠 config 的 `test.exts` / `method_regex` 自訂，但 spec 沒提。連 `lumos init` 的骨架也不會猜 php。
  - **ArchUnit 慣用寫法**：`@ArchTest static final ArchRule` 是欄位不是方法。`JAVA_TEST_RE` 要 `@Test … void`，抓不到，這種規則綁不上。
  - **dependency-cruiser**：是 CLI 加設定檔，不是測試函式。要自己包一支 jest 測試才有名字可綁，spec 沒講。
  - **bound 規則的審查分工**：規則綁了測試以後，審查席還要不要判那條，spec 沒說。要不要把「綁了/懸空」狀態貼給審查席也沒說。linter 目錄 `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:26` 的〈架構 lint〉只列 Konsist、ArchUnitNET、Harmonize，沒有 ArchUnit(Java)，也沒有 PHP 的 Deptrac / PHPat / Pest arch。
- 判準：要嘛新增 `[A]` 行的解析、綁定與懸空檢查並補驗收條款，要嘛改成沿用 `RULE:` 加 `[test:]`（見 HND-9）。每個棧至少要有一個能綁的最小範例。

**HND-3**
severity: major
blocking: 是
引句:「規則內容寫在專案圖譜，不寫進 Lumos 技能」
審材外佐證 file: `docs/lumos-toolchain-knowledge/Systems/arch-alignment-lens.md:40`
審材外佐證 file: `scripts/lumos:41076`
- 問題：照這份做的人拿不到目標架構節點的範本，也沒有一個 DDD 範例。他不知道一條 `[A<n>]` 要寫到什麼程度才「審得動」。
  - 審查席只看到規則文字和 diff。「聚合根守不變規則」「Repository 只存取整包物件」這類句子，沒有判準（什麼算違反、什麼不算）就判不出來。
  - spec 沒給單條規則的長度、數量上限，也沒給好壞對照。
  - 目標節點是「一般 Systems 節點」，新建必須有 `responsibility`。spec 沒講這種不管程式檔的節點要怎麼開，`lumos new system` 的 `--code` 又怎麼處理。
  - `_ARCH_QUESTIONS` 的三問寫死在 `pitfalls` 人讀輸出，spec 沒說目標基準時要換成哪三問，只說派工範本換。
- 判準：計劃要附一份可複製的目標架構節點範例，含 3–5 條 DDD 規則，每條帶「違反長怎樣」。同時說明這份範例放在哪、誰來維護。

**HND-4**
severity: minor
blocking: 否
引句:「已宣告的專案設定欄位會被忽略，不影響其他閘。」
審材外佐證 file: `scripts/lumos:23292`
審材外佐證 file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:30`
- 問題：消費專案怎麼開始用，spec 沒寫。
  - 設定欄位的使用說明在 `commands/06` 那張表（`review_roles` 就寫在那），spec 的 `lands_in` 只列 `Systems/arch-alignment-lens`，不會更新它，也不會碰 `graph-discipline.md` 或 `lumos-code-loop` / `lumos-design-loop` 的 SKILL。
  - 邏輯在 `scripts/lumos`，派工分支在 `templates.md`，兩者分發管道不同。新 skill 配舊腳本，審查席會被指示用目標基準，但 `pitfalls` 沒印；舊 skill 配新腳本，印了目標基準，卻仍用舊三問。這是「忽略」以外的自相矛盾。
  - ⚠ 實際會不會出現版本錯位，取決於各專案是 symlink 還是 vendored，我只確認了 `cmd_update` 會 vendor 整套工具，沒逐一驗兩條路徑的行為。
- 判準：補一份使用者導向的說明和版本錯位時的行為，例如舊腳本遇到 `arch_targets` 時 doctor 提醒。

**HND-5**
severity: major
blocking: 是
引句:「pitfalls 多一次設定讀取與 glob 比對，改動檔數量級，額外成本可忽略。」
審材外佐證 file: `scripts/lumos:41848`
審材外佐證 file: `scripts/lumos:41596`
- 問題：效能宣稱與既有硬約束衝突。
  - `pitfalls --diff` 刻意不載入 vault，實測 0.18s；`Env(vault)` 要 4.7s。程式碼註解明寫它在 pre-push 熱路徑上逐 ref 跑，不能每輪付這筆。
  - spec 的 S3 要驗「節點不存在」「節點沒有任何目標規則」，節點標示 `Systems/<名>` 還要走別名與 NFC 解析，這就要載入 vault，或另寫一套單檔直讀。
  - spec 兩種都沒選，卻斷言成本可忽略。
- 判準：要寫明用單檔直讀（失去別名解析）還是載入 vault。若載入 vault，要說明為什麼可以破壞 vault-free 的約束，並補一條效能測試。

**HND-6**
severity: major
blocking: 是
引句:「pitfalls --diff 應不列該檔的鄰居對照檔，改印目標架構節點與其逐條規則，--json 標 baseline=target 與 target_node。」
審材外佐證 file: `scripts/lumos:41083`
審材外佐證 file: `scripts/lumos:41110`
審材外佐證 file: `scripts/lumos:41450`
- 問題：新開模組的第一支檔是使用者最典型的情境，而現行 `_arch_alignment_hints` 在它身上什麼都不吐。
  - 新資料夾沒有同層檔，`sibs` 為空就被 `continue`。全部檔都沒對照時 `if not out_files: return {}`，整段 `arch_alignment` 為空，下游的候選張力也不跑。
  - 實作者照 S1 字面寫測試，fixture 若放了鄰居檔就會綠，真正的新資料夾反而是空的。S1 沒要求「無鄰居檔也要印目標基準」。
  - `arch["files"]` 現在是 `{檔: [鄰居清單]}`。「每支檔多 baseline 與 target_node」要改成物件，所有讀者（`:41559` 的人讀輸出、`:48117` 的 `tension_candidates`）都得改，spec 沒給 schema。
  - 測試檔與非 code 副檔名會被 skip，目標範圍內的測試檔要不要印基準也沒講。
  - S2 說「與沒有宣告時逐字相同」，但 step 3 又說 `--json` 每支檔多 `baseline: neighbors|target`。這兩句對範圍外的檔互相矛盾。
- 判準：S1 補「範圍內且無任何鄰居檔」的案例，並寫定 JSON 結構，區分「範圍外是否帶 `baseline: neighbors`」。

**HND-7**
severity: major
blocking: 是
引句:「範圍內的寫法跟範圍外鄰居不同，不算 finding。」
審材外佐證 file: `skills/lumos-design-loop/templates.md:324`
審材外佐證 file: `skills/lumos-design-loop/SKILL.md:26`
審材外佐證 file: `scripts/lumos:41135`
- 問題：混合推送沒有定義。
  - 典型的舊系統新模組推送，是同時改範圍內的新 DDD 檔，加範圍外的舊 Controller 去呼叫它。
  - §7.6 範本是單席單份：只有一個鄰居檔清單欄、一套三問。「加目標基準分支」沒說：整個派工單二選一、拆成兩席、還是同一席依檔切換。
  - 切換之後，範圍外的舊檔直接呼叫範圍內模組、繞過聚合根，由誰判？範圍外檔只比鄰居，鄰居看不出這個問題。第三問只涵蓋範圍內往外依賴，反方向沒有。
  - design-loop 也派 §7.6，而且「新開 DDD 模組」的設計審最常發生在實作前。設計審沒有改動檔，目標範圍怎麼決定、第四問「落點」怎麼配，spec 全沒提。
- 判準：S5 補混合推送的派工規則和設計審的規則，並說明範圍外舊檔反向依賴範圍內模組由哪一問負責。

**HND-8**
severity: minor
blocking: 否
引句:「通用不變量（並行、資源、金額、時間）照舊適用」
審材外佐證 file: `scripts/lumos:41135`
審材外佐證 file: `docs/lumos-toolchain-knowledge/Issues/架構對齊席與棧別檢核題可能相反.md:89`
審材外佐證 file: `skills/kotlin-idioms/SKILL.md:159`
- 問題：spec 沒處理它跟張力表態、棧別檢核題的分工。接手者可能兩邊都照做。
  - 目標規則（例如「Repository 載入整包聚合」）和棧別檢核題（N+1、批次載入）很容易同時觸發。
  - 張力候選的判斷依賴 `arch["files"]` 的鄰居檔。範圍內沒有鄰居清單，候選就靜默消失，而且沒有任何地方說「範圍內的 tension 表態，`existing` 欄該指目標規則編號還是別的」。
  - 審查席要查「existing 指的檔真的那樣寫嗎」，範圍內沒有這種檔可開。
  - step 5 要把 8 份慣例 skill 的「當地慣例贏」在範圍內解釋成目標架構。這是改變 skill 語意，但 `lands_in` 沒列這些 skill，寫程式的那一刻讀 skill 的 AI 根本不知道 `arch_targets`。
- 判準：補一小節〈與張力表態、棧別檢核題的關係〉，說清楚範圍內 tension 的欄位怎麼填，以及 step 5 落在哪幾份檔。

**HND-9**
severity: minor
blocking: 否
引句:「沒有可跑測試的照寫散文規則」
審材外佐證 file: `CLAUDE.md:47`
審材外佐證 file: `scripts/lumos:44981`
- 問題：`[A<n>]` 與既有的 `RULE:` 行形成兩套並存的做法。
  - `RULE:` 已經有 `[test:]`、`[applies:]`、`[since:]`、`[retire:]`、`[confirmed:]` 的生命週期欄位，也有「半年內確認過才有挑戰程式碼效力」的規則。
  - `[A]` 是正文行，沒有這些欄位，專案 CLAUDE.md 的前綴表也沒有收錄它。照專案自己的規則，這類沒有結構的正文只是「線索」。
  - 規則廢止、改號沒有慣例，而審查帳會「引規則編號」，改號後舊引用就對不上。
  - 目標節點正文裡很自然會寫例子路徑（`app/Domain/Order/Order.php`）。節點只准用反引號寫自己家的檔，別人的檔會踩 S9 的提醒，新寫的還會被提交前擋下。spec 沒提醒這點。
  - 目標節點描述的是尚未成真的目標。專案的「程式碼為主」原則會把它當成「對不上程式碼的現況描述」，要求立 Issue 記它錯。
- 判準：要嘛 `[A]` 改成 `RULE:` 行加 `[test:]`，要嘛明說為什麼不用，並補上廢止慣例、目標節點的標示方式（避免被當成現況）和路徑寫法。

**HND-10**
severity: major
blocking: 是
引句:「或宣告了但審查席依目標規則提出的發現連續兩季零件被折入（等於沒人用或規則沒產生訊號）時」
審材外佐證 file: `scripts/lumos:9613`
審材外佐證 file: `scripts/lumos:8815`
審材外佐證 file: `scripts/lumos:47504`
- 問題：RETIRE-IF 的兩個條件現況都數不出來。
  - 審查帳的 findings 欄位只有 `--findings-set` 的 id、`--finding-kind`（code/spec/process）和 `--finding-severity`，沒有席位或基準欄位。折入統計只按輪次和 auditor 彙總（`:8815` 一帶）。
  - 治理帳的事件沒有 baseline 欄位。S4 的 `code-loop check` 只「印出」目標節點與命中檔數，不寫帳。「依目標規則提出的發現」只存在於各輪自由文字的席報告裡。
  - 「連續 90 天沒有任何專案宣告」：本 repo 看不到消費專案的 `.lumos/config.json`，沒有任何回傳通道。
  - 「零件」讀不通，像是「零筆」的筆誤，兩季的起算點也沒定義。
- 判準：S4 要同時寫一筆治理帳事件，含 baseline、node、檔數。處置帳要有「發現來自目標基準」的標記，例如依引用的規則編號。否則撤除條件只能靠人記得。

**HND-11**
severity: minor
blocking: 否
引句:「同一支檔只能落在一個範圍；範圍重疊、節點不存在、節點沒有任何規則，都算宣告錯誤。」
審材外佐證 file: `scripts/lumos:40547`
審材外佐證 file: `scripts/lumos:26625`
- 問題：「範圍重疊」只有在針對具體檔案時才判得出。
  - glob 比對沿用 `_glob_first_match`：星號跨斜線、開頭 `**/` 會被去掉再試。兩個樣式是否相交，靜態看不出來。
  - `pitfalls` 只看改動檔，`doctor` 才列得出全部追蹤檔。spec 沒說重疊要用哪個檔集合判斷，所以同一份宣告在 doctor 報錯，在 pitfalls 可能完全看不出來。
  - 「宣告錯誤」只定義了三種。`arch_targets` 本身形狀不對（不是清單、缺鍵、多鍵、路徑以 `./` 或 `/` 開頭、含反斜線）沒有處理。對照 `review_roles`，它們都有明確的路徑檢驗與「壞宣告整份不用」。
  - 「退回鄰居基準」是無聲降級：只印一行警告，沒有任何東西擋。目標檔案改名後，審查席會悄悄回到「跟鄰居不同就是違規」，也就是這份計劃要解決的原問題。
  - 「doctor 應報錯」沒說是軟提醒還是計入 issues。
- 判準：S3 補檔集合、形狀檢查和 doctor 的嚴重度。

**HND-12**
severity: minor
blocking: 否
引句:「並以一份目標範圍內的改動實際派一席，核對它引用規則編號而不是鄰居檔」
審材外佐證 file: `skills/lumos-design-loop/templates.md:324`
- 問題：S5 的 manual 驗法照做不了，也無法重複。
  - 本 repo 沒有任何 `arch_targets` 宣告，也沒有目標架構節點。實際派一席要先在某個消費專案或夾具裡搭出完整設定，spec 沒指定用哪個。
  - 單次派工的結果隨模型而變，之後有人改 §7.6 也不會被偵測到。
  - 這條其實可以機械化：斷言組出的派工詞含 `baseline` 與規則編號、且不含鄰居清單欄位。
- 判準：S5 至少拆出一條可測的子條款（派工文字的組裝），人工那半只留給席位的實際行為。

**HND-13**
severity: minor
blocking: 否
引句:「範圍內新寫的程式彼此一致嗎」
審材外佐證 file: `scripts/lumos:41135`
審材外佐證 file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:44`
- 問題：判斷粒度是整個檔，沒有只看新增行的規定。
  - 舊系統常把範圍宣告在還有舊檔的資料夾（例如 `app/Services/**` 逐步遷移）。改一行舊檔，整檔都被目標規則審。
  - lint-new 閘是因為這個原因才做「新增告警差集」的。
  - 「逐條貼出規則內容」沒有數量上限。對照 impact 的固定席最多 8 篇，50 條規則會撐大每席派工詞。
- 判準：§7.6 目標分支補「只對增行或新檔判違反」的口徑，以及規則貼出數量的上限或截斷說明。

總結最嚴重 severity: major；blocking 共 7 條
