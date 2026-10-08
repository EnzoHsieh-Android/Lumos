severity: major

固定席筆記:hook 沒有在這份派工詞尾端附任何固定席筆記,所以沒有逐條判。

我只讀了程式碼,沒有跑 git 實驗。程式碼位置以 `scripts/lumos` 為準,路徑相對於 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw`。

**K1 退場條件 `[retire:事件 <[[節點]] 狀態=值>…]` 照現行解析器會被截斷,規格的「值裡不能有 `]`」自己就違反**
severity: major
blocking: 是 — 照字面實作,新文法要求的 RULE `[retire:]` 形狀,既有解析器讀出來是被截斷的半截,S2 與 S8 都會做錯。
- 輸入:新寫的 `RULE:… [retire:事件 <[[Systems/某節點]] 狀態=done>]`。走到:格子規格的 D 條與 S2,以及「`RULE` 欄位沿用 `parse_rule_fields`」。
- `RETIRE_REF_RE` 是 `\[retire:\s*([^\]]*)\]`,讀到第一個 `]` 就停。上例讀出來是 `事件 <[[Systems/某節點`。
- 既有的 `rule_field_truncated` 對這種寫法的反應是警告「被截斷」。
- 所以 S2 要求的「形狀合格的 `[retire:]`」,有一種合法形狀一寫就被截斷,檢查看不到尾巴。S8 的「`[retire:事件 …]` 從不成立變成立」也無從判斷。
- 規格同時主張「回頭條件探針的轉變判定」可沿用。但探針只認 REVISIT 行開頭的 `[when-file|symbol|test|status:…][by:日期]`,由 `_probe_parse` 解析。`[retire:事件 …]` 是另一套文法,必須新寫解析器。
- 回退面:新寫進筆記的 `[retire:事件 <[[…]]…>]` 在舊程式下(退回第 1 步之後)全是被截斷的值,而規格說「舊程式不認得的記號只是文字」。
引句:「值裡不能有 `]`(既有限制,真要寫就放正文)」
佐證:`scripts/lumos:3314`、`scripts/lumos:3331`、`scripts/lumos:28505`、`scripts/lumos:28615`

**K2 新文法沒有自己的上線點,在途的舊寫法提交推送時會被當新違規擋,「舊行不查」沒有機制撐住**
severity: major
blocking: 是 — 實作者沿用既有上線標記,消費專案更新後分支上、舊文法寫好還沒推的行,推送和 CI 都會被擋。這與規格的「舊行不查」承諾直接矛盾。
- 輸入:消費專案裡一條功能分支,在 `lumos update` 前用舊文法(`WHY:[日期 出處]…`)提交了筆記,更新後才推送。
- 走到:〈擋〉「掛在筆記形狀檢查…上線點截斷」。
- `cmd_note_shape` 的 `--diff` 路徑呼叫 `_nodehome_clamp_base(root, base, tip, _NOTE_SHAPE_GOLIVE_MARK)`,而標記是寫死的 `"note-shape --staged"`(提交前掛鉤第一次出現這串的提交)。
- 這個提交是舊檢查很久以前上線的,在 slots 之前很多。夾在 base 與 tip 之間的所有新增行都會用新的必有格子表檢查,包含更新前就寫好的。
- 規格沒有為 slots 另開一個標記,也沒說上線點寫在哪。
- 回退時也是同一個洞。還原再重上時沒有「第二次上線點」,已經用新文法寫的行會被當舊行還是新行,規格沒定義。
引句:「**舊行**:上線點之前寫好的行一律不查,也不轉換。」
佐證:`scripts/lumos:25443`、`scripts/lumos:26404`、`scripts/lumos:24933`

**K3 `note_shape.slots` 與 `note_shape.gate` 的組合沒定義,預設又與引用的先例相反,關掉的逃生口設計得不好用**
severity: major
blocking: 是 — 逃生口(整類降級)是回滾的第一道手段,組合語意不定,實作者會做出兩種相反的行為。
- `cmd_note_shape` 在 `mode == "off"` 時整個提早 return(`gate=off`),後面才評估違規,且整份違規共用一個 `mode` 進 `_note_shape_report`。
- 規格沒說:`gate=warn` 的專案,slots 預設的 `block` 算擋還是算提醒?`gate=off` 且 `slots=block` 呢?
- 引為先例的 `drift_check.old_sentence` 和 `note_shape.negation` 都是預設 warn,並且與 gate「各管各的」。
- slots 預設 block,壞值也照 block。例如打成 `"OFF"` 或 `"off "`,逃生口自己失效,只會多印一句。
- 要降級,還得先把改設定檔的提交推過去。設定檔從被推送的版本讀,所以那個提交本身要先能通過檢查。
引句:「**子開關(新增)**:`note_shape.slots`(`block` 預設 / `warn` / `off`),照 `drift_check.old_sentence` 那種「一道閘底下一個子開關」的先例;壞值照 block 並講一句。」
佐證:`scripts/lumos:26422`、`scripts/lumos:26481`、`scripts/lumos:30316`、`scripts/lumos:26129`

**K4 〈回退〉把 `note_shape.slots: off` 當第 3 步的停擋手段,但第 3 步的擋根本不在那條閘**
severity: major
blocking: 是 — 第 3 步的 `[by:]`、`[retire:事件]` 是推送時擋,若誤判,照規格的回退寫法關不掉,會卡住整個推送。
- 〈格子欄位的過期檢查〉表把兩者掛在「存量漂移檢查(新種類)」,由 `cmd_drift_check` 執行。
- 該閘有自己的開關 `drift_check.gate` 和跳過環境變數 `LUMOS_SKIP_DRIFT_CHECK`。
- `note_shape.slots: off` 只管 `cmd_note_shape` 這條。回退寫「第 3 步、第 2 步、第 1 步:各自還原提交;`note_shape.slots: off` 先停掉擋」,第 3 步的擋依然在。
- 〈實務隱患〉自我治理只列了 `LUMOS_SKIP_NOTE_SHAPE` 和 `note_shape.slots`,沒有列 drift 的。
引句:「第 3 步、第 2 步、第 1 步:各自還原提交;`note_shape.slots: off` 先停掉擋。」
佐證:`scripts/lumos:30378`、`scripts/lumos:28163`

**K5 `SEE` 取代 `DEP` 只加進前綴表,沒處理讀 `DEP:` 的程式,先改範本再開前綴的分期順序還會讓兩步之間的消費專案寫出被打錯字警告的行**
severity: major
blocking: 是 — 計劃連到哪些節點的算法只認 `DEP:` 行。範本改成叫人寫 `SEE:` 之後,這些連結會悄悄消失,風險分級與落點判斷會少看一批節點。
- `_plan_system_links` 只讀摘要裡以 `DEP:` 開頭的行的 `[[連結]]`。相依回歸、門判定訊號 2、推送前「誰的落點被碰到」都走這支。
- 規格說「DEP/FLOW 只放連結:一律改 SEE」,但分期第 2 步只說「搜尋行模式與分類判定者把 LOG 當過程紀錄、SEE 當連結」,沒提這支函式。
- 順序問題:第 0 步先改範本與 `lumos new` 骨架(叫人寫 SEE),第 2 步才把 LOG/SEE 放進前綴表。
- 前綴表是 `SYMBOL_NAMES`,沒有 SEE 和 LOG。`SYMBOLISH_RE` 會把它們當打錯字:「非標準符號行…這行不會被當成摘要」。
- 第 0 步與第 2 步之間,以及第 2 步還原之後,所有照範本寫的 `SEE:` 都是這個狀態。
- 〈回退〉說「已經照新範本寫的行留著無害:舊程式不認得的記號只是文字」,這與上述行為不符。
- 規格的 LOG 也同樣:還原第 2 步後,LOG 行不再算摘要,搜尋找不到。
引句:「已經照新範本寫的行留著無害:舊程式不認得的記號只是文字。」
佐證:`scripts/lumos:6205`、`scripts/lumos:3261`、`scripts/lumos:4932`、`scripts/lumos:5415`

**K6 `lumos guard plan` 自己寫出舊文法的 `WHY:[日期]…`,`guard settle` 還靠這個開頭找行,新舊兩邊都踩雷**
severity: major
blocking: 是 — 工具自己產生的筆記行在新規則下會被擋,若把它改成新文法,`settle` 又找不到。
- 規格說「規範層(紀律範本、skill、骨架提示、筆記形狀檢查)全部換成統一文法」,沒提工具自己寫行的程式。
- `guard plan` 寫出 `WHY:[{today}]預告這條合約但還沒做:…`,沒有 `[出處:]` 和 `[因:]`。這一行是新寫行,commit 時被 S1 擋。
- `_guard_planned_prose` 用 `s.startswith("WHY:[")` 加 `_GUARD_WHY_MID` 認出預告句。一旦為了過檢查改成 `WHY:預告… [出處:…] [因:…]`,`settle` 就找不到,報成找不到。
- 回退面:還原後工具與規則回到一致,但中間已改寫的預告句要手動還原。
引句:「規範層(紀律範本、skill、骨架提示、筆記形狀檢查)全部換成統一文法」
佐證:`scripts/lumos:12008`、`scripts/lumos:12155`、`scripts/lumos:12168`

**K7 範本改了又還原,消費專案的 CLAUDE.md 區塊與擋會互相矛盾,規格沒定回退順序**
severity: major
blocking: 是 — 單獨還原第 0 步(範本)而第 1 步(擋)還在,消費專案區塊叫人寫舊格式、擋卻擋舊格式。
- 工具是 symlink 分發(程式立即全域生效),但紀律範本是注入各專案 CLAUDE.md 的快照,要再跑一次 `lumos update` 才變。
- 規格〈回退〉只寫「範本還原後消費專案要再一輪 `lumos update`」,沒有排順序:第 1 步的擋沒先關,範本就不能先還原。
- 更新前:擋已經上線(程式即時生效)而消費專案區塊還是舊範本,叫人寫 `WHY:[日期 出處]`,正是新寫的行會被擋的舊寫法。
- 規格〈分期〉把範本放第 0 步先上,看似安全,但程式碼是 symlink 即時、範本是人手動 update,兩者上線時間差在消費專案是不可控的。
引句:「第 0 步:範本還原後消費專案要再一輪 `lumos update`(既有行為);骨架提示一起還原。」
佐證:`scripts/lumos:2799`、`scripts/lumos:18188`

**K8 RETIRE-IF 兩個撤除條件用現有治理帳量不出來,回滾的判準沒有資料**
severity: major
blocking: 是 — 上線 8 週後要靠這兩個數字決定撤不撤,數字算不出會憑感覺決定回不回滾。
- 「為了過關硬填空殼超過一半」和「用單次跳過繞過超過三成」,規格的資料源只有治理帳。
- `_note_shape_report` 的 blocked 帳只記「新違規 N 條」和節點清單,不分是 slots 違規還是 FACT/行號違規,也沒存被擋的行。
- 跳過帳 `skipped-env` 在評估之前就寫了,內容只有 `LUMOS_SKIP_NOTE_SHAPE`。那次提交有沒有 slots 違規不知道,分母是被擋次數但分子可能根本沒違規。
- 〈格子欄位的過期檢查〉表裡 doctor 的「觸發次數、跳過次數」兩種指標,目前沒有任何一個會按規則種類分。
- S11 要抽查「被擋下又補好的行」,但帳裡沒有行,只能靠 git 歷史自己重建。
引句:「或擋下後用單次跳過繞過的比例超過三成——規則跟實際寫法不合,回頭改範本。」
佐證:`scripts/lumos:26370`、`scripts/lumos:26496`

**K9 PITFALL 的 `[防回歸:無 理由]` 逃生口與既有 PITFALL 提醒不一致**
severity: minor
blocking: 否 — 只多一條警告,不擋也不會做出壞系統,但新逃生口會被舊 lint 當成沒寫防回歸。
- `context_marker_warnings` 的 PITFALL 規則 `_CTX_REGRESS_RE` 只認 `[test:`、`重現`、`repro`。
- 用了 `[防回歸:無 理由]` 的行,通過新擋,但 lint 仍唸「脈絡標記『PITFALL:』缺防回歸」。
- S12 要求「讀同一張表」,但既有的 `_CONTEXT_MARKER_RULES` 和 `_NOTE_SHAPE_PREFIX_RULES` 沒說要不要併進來。
引句:「PITFALL 真的沒有防回歸可寫 `[防回歸:無 <理由>]`。」
佐證:`scripts/lumos:3270`、`scripts/lumos:3284`

**各節已讀**
- 〈格子規格〉:K1、K5、K6 屬此節。
- 〈擋〉:K2、K3、K8。
- 〈格子欄位的過期檢查〉:K1、K4。
- 〈分期〉:K5、K7。
- 〈回退〉:K4、K5、K7。
- 〈天花板〉〈不做〉〈合約候選〉〈待 Enzo 看〉:已讀,無 finding。
- 〈驗收條款〉:S1 到 S12 對照上面各條,S8 見 K1 與 K4,其餘無額外 finding。
- 內部引用 `[[…]]` 的目標節點全部存在(已核 6 個)。

**實務隱患(回滾視角)**
- 併發:無。新增寫入只有治理帳,沿用既有寫入,不新增同時寫的路徑。
- 相容:有隱患,見 K2、K5、K6、K7。
- 自我治理:有隱患,見 K3、K4、K8。
- 資源與效能:無。必有格子是新增行的字串比對,不新增程序。
- 金流、對外送出、不可逆:無。規格已排除,我核對過擋與過期檢查都只讀筆記與程式文字,不改資料。

最高嚴重度:major,blocking 8 條
