severity: major

審查範圍:/tmp/slots/r1.md 全文。已對照 `scripts/lumos`(筆記形狀檢查、`parse_rule_fields`、回頭條件探針、`guard plan`、lint)。

**C1 上線點沒有格子專用的記號,舊寫法的提交會被倒溯擋下**
severity: major
blocking: 是——照字面做,「舊行不查」在推送與 CI 路徑上不成立,會誤擋合法的舊寫法。
- spec 說「上線點截斷」「舊行:上線點之前寫好的行一律不查」,但沒有為格子另設上線記號。
- 現有上線點是提交前掛鉤含 `note-shape --staged` 這串。格子只是同一條檢查多幾條規則,掛鉤字串不變。
- 推送時,範圍被夾到那個既有記號第一次出現的提交,逐提交只看該提交的掛鉤有沒有記號。
- 實際情況:一條 PR 分支在 `lumos update` 帶進格子之前,就已經提交了舊寫法 `WHY:[日期 出處]…`。分支要推、或 CI 跑 `--diff` 時,這些行在範圍內,又被當成新行,缺 `[出處:]` 就被擋。
- 舊版 `lumos` 的提交前掛鉤根本不檢查格子,作者沒有被警告過。
- 需要為格子另訂記號,或把格子規則的生效點綁在掛鉤內容版本。
引句:「上線點之前寫好的行一律不查,也不轉換。」
佐證:`scripts/lumos:25443`、`scripts/lumos:25674`、`scripts/lumos:26404`

**C2 改到舊行就變新行:RULE 重確認、錯字修正都會被新格子擋,和「舊的自由文字 retire 照認」衝突**
severity: major
blocking: 是——規範自己要求的維護動作會被閘擋下,使用者只能繞過。
- 閘判「新寫的行」靠 diff 新增行。改動舊行任何一個字,整行都算新增。
- 現行 lint 對過期的 RULE 唸的是「還成立就更新 `[confirmed:]`」(`rule_lifecycle_warnings`)。CLAUDE.md 也規定,`RULE:` 要半年內確認過才有挑戰程式碼的效力。
- 照做就會改到一條舊 RULE 行。這行沒有 `[依據:]`,retire 是自由文字,按 S2 會被擋。
- 作者只能補 `[依據:]` 並重寫 retire,或用 `LUMOS_SKIP_NOTE_SHAPE=1` 繞過。
- 同理,舊 WHY 改一個錯字就被要求補 `[出處:][因:]`。
- spec 的「舊的自由文字 `[retire:…]` 照認」只在沒被碰到時成立。
- 要明定改到舊行時怎麼處理:例如只比對新增的鍵,或只改 `[confirmed:]` 時豁免。
引句:「舊的自由文字 `[retire:…]` 照認,新寫的必須是三種之一。」
佐證:`scripts/lumos:3389`、`scripts/lumos:3394`、`scripts/lumos:25656`

**C3 工具自己寫的 WHY 行,會被新的 WHY 必有鍵擋住**
severity: major
blocking: 是——用 `lumos guard plan` 的人,提交會被自己的工具產物擋下。
- `lumos guard plan` 寫出的預告句是 `WHY:[{today}]預告這條合約但還沒做:…`,沒有 `[出處:]` 也沒有 `[因:]`。
- `guard settle` 轉正時還會改寫那一行,同一行又變成新行。
- 現有的否定現況句提醒有把這種工具樣板豁免(`_NS_NEG_TEMPLATES`)。
- spec 的 S7 只豁免合約行和其他前綴,第 0 步只改範本、skill、骨架提示。這個寫入點沒被列進去。
- 同族還有:任何其他程式生成的 WHY/PITFALL/RULE/FACT 行,spec 沒有掃描過。
引句:「規範層(紀律範本、skill、骨架提示、筆記形狀檢查)全部換成統一文法」
佐證:`scripts/lumos:12008`、`scripts/lumos:12168`、`scripts/lumos:25982`

**C4 事件型 retire 的寫法,裝不進自己規定的「值裡不能有 `]`」文法,也沒有程式會去評估它**
severity: major
blocking: 是——事件型 retire 照字面做不出來,S8 的 retire 部分沒有可實作的解析路徑。
- 格子規格說「值裡不能有 `]`(既有限制)」。D 的事件形狀卻是 `<[[節點]] 狀態=值>`,必然含 `]]`。
- 實測 `RETIRE_REF_RE` 對 `[retire:事件 [[Systems/a]] 狀態=done]` 只取到 `事件 [[Systems/a`,後半被截斷。lint 還會警告值被截斷。
- spec 說「沿用回頭條件探針的轉變判定」,但探針有三個限制:
  - 只從以 `REVISIT:` 開頭的行取條件。
  - 條件語法是 `[when-file|symbol|test|status:…]`,status 寫成 `<節點>=<值>`,不是 `<[[節點]] 狀態=值>`。
  - 抽取、候選篩選、「起點同一條」判定都綁 `REVISIT` 行。
- 內嵌在 RULE 行裡的 `[retire:事件 …]` 沒有抽取器。spec 沒有說要新寫,也沒有給語法如何對上 `when-*`。
引句:「`[retire:事件 <[[節點]] 狀態=值> 或 <檔或符號出現>]`」
佐證:`scripts/lumos:3315`、`scripts/lumos:28506`、`scripts/lumos:28511`、`scripts/lumos:28615`

**C5 spec 自己的範例違反自己的形狀**
severity: major
blocking: 是——範本是使用者照抄的來源,照抄就被自己的閘擋。
- RULE 範例的 retire 是 `[retire:事件 分析行程改由沙箱隔離]`。「分析行程改由沙箱隔離」既不是節點狀態,也不是檔或符號出現,按 D 不合格,會被 S2 擋。
- FACT 範例是 `[recheck:辦大型活動前]`。但 S9 與過期表要拿 `[recheck:]` 當「週期」去算「觀測+週期」。這個值不是週期。
- `[recheck:]` 的格式根本沒定義(幾天?`30d`?)。解析不了時是回退到來源預設,還是丟警告,spec 沒說。
- 同一類:`[觀測:日期]` 在提交時只驗有沒有寫。壞日期(例如 `昨天`)到了 doctor 怎麼處理也沒說。
引句:「RULE:分析行程不准有送提案以外的寫入呼叫 [依據:審計] [since:2026-09-23] [retire:事件 分析行程改由沙箱隔離] [test:t_analyzer_no_write]」

**C6 `[by:]` 沒有值文法,與現有 `[by:日期]` 同鍵兩義,取代鏈延伸時會誤擋**
severity: major
blocking: 是——S5 與 S8 的 `[by:]` 部分,實作者無從決定指向什麼、什麼叫「也作廢了」。
- `[by:取代者]` 的值沒有定義:可以是節點、決策編號,還是某一行?
  - 一行沒有可指的識別字。
  - 「指到的決策或節點不存在、或它自己也作廢了」的存在性與作廢判定也就無從實作。
- 現有 `[by:YYYY-MM-DD]` 在探針裡是期限(`_PROBE_TOKEN_RE`)。`[retire:人裁 by:日期]` 也是期限的意思。
- spec 卻宣稱「同一個意思跨前綴只有一種鍵」。這裡同一個鍵 `by` 有兩個意思,`_probe_parse` 一碰到非日期值就報「期限不是 YYYY-MM-DD」。
- 「它自己也作廢了」就擋推送。逐步取代是正常歷史:A 被 B 取代,後來 B 被 C 取代。
  - 推送「B 標 superseded、by C」時,A 的 `[by:B]` 立刻變成「指到的也作廢」,這次推送被擋。
  - 要擋的是改了 B 的人,卻要逼他改 A,還可能是舊行。
  - 沒說鏈要不要追到最後一個存活者。
- 成環(A by B、B by A)也沒處理。
引句:「| `[by:…]` | 指到的決策或節點不存在、或它自己也作廢了 | 擋(推送) | 存量漂移檢查(新種類) |」
佐證:`scripts/lumos:28509`、`scripts/lumos:28634`

**C7 只放連結的 DEP/FLOW:提醒、擋、放行三處說法互相矛盾**
severity: major
blocking: 是——擋與提醒的分界不一致,實作者只能猜。
- S4:只放連結的 DEP/FLOW「應提醒改用 SEE」。
- 規格〈DEP/FLOW 只放連結〉:「對只放連結 FLOW/DEP 的放行,一起改掉」。
  - 現有程式的「放行」是 `_NS_POINTER_ONLY_RE` 的跳過。
  - 拿掉放行,這類行就走 FACT/FLOW/DEP 的必有鍵,缺 `[來源:]` 和 `[觀測:]` 被擋,不是提醒。
- 兩種解讀會做出不同的系統,而且「提醒」那條路目前沒有程式:格子違規進同一個 `viol`,由 `gate` 統一決定擋或提醒。
- 骨架留的空 `FLOW:`/`DEP:`(`not body` 的豁免)也沒有說保留或取消。
引句:「`DEP/FLOW 只放連結`:一律改 SEE;既有規範、`lumos new` 骨架提示、筆記形狀檢查對只放連結 FLOW/DEP 的放行,一起改掉」
佐證:`scripts/lumos:25856`、`scripts/lumos:25907`、`scripts/lumos:26434`

**C8 度量型 retire 的指標沒有白名單,形狀過關但永遠評估不到**
severity: major
blocking: 是——retire 條件靜默變死,而「寫不出撤除條件的 RULE」正是這份計劃要消滅的問題。
- D 的形狀是 `[retire:度量 <指標> <比較> <數字>]`,指標是任意詞。
- 過期表說只先做「觸發次數、跳過次數」兩種指標,doctor 才讀得到。
- 提交時的形狀檢查若只驗三種形狀,`度量 週活躍 < 5` 會過關,卻永遠不會被量。
- 按字面,閘不驗指標名,也沒有「未知指標」的提醒。
- `人裁 by:日期` 到期也只提醒、沒有後續,這部分是設計取捨,不算漏洞。
引句:「| `[retire:度量 …]` | 量出來符合 | 提醒 | doctor(要讀治理帳,先做兩種指標:觸發次數、跳過次數) |」

**C9 分期順序:第 1 步的提醒叫人寫 SEE,SEE 到第 2 步才被認得**
severity: major
blocking: 是——實作者照分期做,中間版本會對使用者講錯話。
- 現在的前綴表(`SYMBOL_NAMES`)沒有 SEE 與 LOG。
- lint 對未列名的 `XXX:` 摘要行唸「非標準符號行,看起來像打錯字,這行不會被當成摘要」。
- 第 0 步把 `lumos new` 骨架改用 SEE,第 1 步的擋下與 S4 的提醒也叫人改用 SEE。這兩步都要到第 2 步才讓 SEE、LOG 進前綴表。
- 第 0 到第 1 步之間,按範本寫的 `SEE:` 行會被 lint 唸成打錯字,也進不了摘要與檢索。
- 回退段也有相同問題:單獨還原第 2 步後,第 1 步的訊息仍然指向 SEE。
- SEE 與 LOG 的前綴註冊應該排在第 0 步之前,或和第 0 步同提交。
引句:「LOG、SEE 進摘要前綴表;搜尋行模式與分類判定者把 LOG 當過程紀錄、SEE 當連結。」
佐證:`scripts/lumos:3261`、`scripts/lumos:5416`

**C10 S12 說「用既有的行內欄位解析」,但既有解析是 RULE 專用的固定六鍵**
severity: minor
blocking: 否——實作者會自己發現,但可能擴充 `_RULE_FIELD_RES`,連帶改掉 lint 的截斷警告範圍。
- `parse_rule_fields` 只認 since、until、confirmed、status、retire、applies 六個鍵。
- 出處、因、根因、依據、觀測、recheck、repro、防回歸、by、來源、查,都不在裡面。
- `rule_field_truncated` 與 `rule_lifecycle_warnings` 也迴圈用這張表。只擴一張表,連 lint 的行為一起變。
- 值截斷到第一個 `]` 的問題,也會讓 `[repro:指令]` 與 `[查:指令]` 在指令含 `[a-z]` 時被截。doctor 查「指令裡的檔案路徑還在不在」會用截斷後的字串。
- spec 沒說怎麼從自由指令抽路徑。
引句:「四個前綴的必有鍵檢查 應 讀同一張「前綴 → 必有鍵」表、用既有的行內欄位解析」
佐證:`scripts/lumos:3316`、`scripts/lumos:3321`、`scripts/lumos:3345`

**C11 新文法過關的行,會被現有 lint 的脈絡標記規則另外唸**
severity: minor
blocking: 否——只是雜訊與雙重標準,不影響擋或放行,但 spec 沒講這幾條 lint 規則是否一起換。
- PITFALL 的 `[防回歸:無 理由]` 不含 `[test:`、`重現`、`repro`。`_CTX_REGRESS_RE` 會唸「缺防回歸」。
- WHY 的 `[出處:Enzo 口頭]` 沒有日期、編號、`[[`。`_CTX_SRC_RE` 會唸「缺出處」。
- 反過來,新的 `[出處:]` 只驗「有寫」,比舊判準鬆。
- RULE 標了 `[status:superseded]`,`rule_lifecycle_warnings` 永遠唸「確定撤掉就把整行刪掉」,但 E 要求保留並加 `[by:]`。
- 第 0 步沒把 `_CONTEXT_MARKER_RULES` 和 `rule_lifecycle_warnings` 列進要改的規範層。
引句:「規範層(紀律範本、skill、骨架提示、筆記形狀檢查)全部換成統一文法」
佐證:`scripts/lumos:3272`、`scripts/lumos:3276`、`scripts/lumos:3374`

**C12 E「任一前綴」與 S7、S10 的豁免範圍衝突**
severity: minor
blocking: 否——只影響邊角行,實作者選哪邊都不會讓主流程壞掉。
- E 說有 `[status:superseded]` 就必須有 `[by:]`,「任一前綴」。
- S10 說 LOG 行不被任何格子或過期檢查查,S7 說合約行不套格子。LOG 或合約行若標了 superseded,到底查不查?
- 另外,現有 `_ns_check_line` 的 context 規則只在 region 是 summary 時跑。
  - spec 說「新寫的行」,沒說只看摘要區還是連正文區都算。
  - 正文裡的 `WHY:` 行(例如範例區塊外的敘述)是否也要必有鍵?
  - 這影響「新寫行」的範圍,但不屬必然誤判。
引句:「| 已作廢(E,任一前綴) | — | 有 `[status:superseded]` 就必須有 `[by:]` | — |」
佐證:`scripts/lumos:25903`

**C13 `note_shape.slots` 和 `note_shape.gate` 的交互沒說,「照先例」的先例與 spec 做法相反**
severity: minor
blocking: 否——組合行為可以由實作者補定,不會影響主流程的正確性。
- spec 說子開關「照 `drift_check.old_sentence` 那種先例」。但那個先例是預設 warn,壞值也照 warn。
- spec 卻定預設 block、壞值照 block。實際上它抄的是 `_note_shape_config` 的 gate 寫法。
- 沒說的組合:
  - `gate=off` + `slots=block`:現有程式 gate=off 提早 return,連格子一起關,但 spec 沒寫。
  - `gate=warn` + `slots=block`:現有 `_note_shape_report` 對全部違規用同一個 mode。要讓格子獨立於 gate,必須分開兩路,spec 沒要求。
- S6 只測 slots 單獨設定的三個值與壞值。
引句:「**子開關(新增)**:`note_shape.slots`(`block` 預設 / `warn` / `off`),照 `drift_check.old_sentence` 那種「一道閘底下一個子開關」的先例;壞值照 block 並講一句。」
佐證:`scripts/lumos:25467`、`scripts/lumos:30316`、`scripts/lumos:26419`、`scripts/lumos:26481`

各節已讀的結論:
- 格子規格:有 finding(C2、C3、C4、C5、C6、C10)。
- 擋:有 finding(C1、C7、C13)。
- 格子欄位的過期檢查:有 finding(C4、C5、C6、C8)。其中以下兩條已讀,無額外 finding:
  - `[test:名]` 一列:路線圖 1b 排隊中,spec 只借用。
  - 時間到期一律只提醒:各列一致,沒有矛盾。
- 分期:有 finding(C9)。
- 天花板、不做、回退、合約候選:已讀,無 finding。
- 驗收條款:S1 到 S12 的測試名在 spec 外尚未存在,屬後續實作;條款內容的漏洞已併入上列 finding。
- 內部引用:`[[Projects/依賴欄位_過時判定_計劃]]`〈待解問題〉、路線圖 1b 等目標都存在。

實務隱患逐類:
- 併發:無。新增寫入只有治理帳,沿用既有寫法。
- 效能:無。必有格子是新增行字串比對;過期檢查沿用現有候選篩選與預算。
- 資源:無。不開長駐程序。
- 相容:有(C1、C2、C3、C11)。舊寫法、工具產物、lint 並存,各自會在上述場景誤判。
- 自我治理(誤擋逃生口):有(C13)。`slots` 與 `gate` 交互未定。
- 金流、對外送出、不可逆:無。只讀筆記與程式文字,不碰交易、不呼叫外部服務、不改資料。

資料狀態五問:
- 新舊互讀:C1、C2、C3、C11。
- 寫一半:C9。分期中間狀態會對使用者講錯話。
- 衍生資料:C10。解析器與 lint 共用同一張表,擴充會連帶改行為。
- 時間:C5 `[recheck:]` 格式未定、`[觀測:]` 壞值未定;C8 `人裁 by:日期` 到期後無下一步。
- 不可逆:無。擋都能用子開關降級,舊行不改。

最高嚴重度:major,blocking 9 條
