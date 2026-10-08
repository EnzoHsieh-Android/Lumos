severity: major

審的是 `/tmp/slots/r1.md`(格子寫法與過期檢查),對照 repo `scratchpad/rw` 裡的 `scripts/lumos`。

## 1. 分層與依賴方向
大致一致,沒有跨層直呼。
- 擋的部分掛在筆記形狀檢查(`cmd_note_shape` 與 `_note_shape_eval`,`scripts/lumos:26351`、`26185`)。新增行、上線點截斷、`LUMOS_SKIP_NOTE_SHAPE` 都沿用它。
- 過期檢查掛在存量漂移檢查(`_drift_probe_check`,`scripts/lumos:29088`),時間類提醒掛在 doctor。這跟既有「事件類擋推送、時間類只提醒」的分工同向。
- 唯一的結構疑點是必有鍵表的歸屬,見 A1。

## 2. 命名與錯誤處理
結構對,但有三處跟鄰居不一致:`[by:]` 撞名(A3)、跨前綴鍵名(A4)、子開關的先例選擇(A5)。
- 壞值照 block 並講一句,跟 `_note_shape_config`(`scripts/lumos:25483`)一致。
- 單次跳過 `LUMOS_SKIP_NOTE_SHAPE=1`、擋下訊息帶「缺什麼、怎麼補」,跟 `_CONTEXT_MARKER_RULES`(`scripts/lumos:3280`)一致。

## 3. 第二種做法
有兩處:必有鍵表(A1)和事件式撤除條件的語法(A2)。其餘新能力(LOG、SEE、`[觀測:]`、`[recheck:]`、`[repro:]`、度量類提醒)專案原本沒有,依你的指示不算。

## 4. 落點
寫進筆記內容閘(擋)與存量漂移守衛(`[by:]`、`[retire:事件]`)是對的。但還有幾塊沒有歸宿(A6)。

---

**A1** 必有鍵表可能變成第三張前綴表
severity: major
blocking: 是——專案已經有「前綴對應必有項」的表和擴充點,設計若另起一張就是第二種做法;不過 S12 可能就是要併表,所以標 ⚠ 請作者說清楚
引句:「四個前綴的必有鍵檢查 應 讀同一張」
佐證行 file: `scripts/lumos:3280`(`_CONTEXT_MARKER_RULES`:WHY 要出處、PITFALL 要防回歸、FACT 要來源)
佐證行 file: `scripts/lumos:25907`(`_NOTE_SHAPE_PREFIX_RULES`,note-shape 只用 FACT/FLOW/DEP 這一份)
佐證行 file: `scripts/lumos:3399`(`context_marker_warnings(rules=…)` 是現成的換表入口;RULE 另走 `rule_lifecycle_warnings`,`scripts/lumos:3367`)
說明:
- WHY 出處、PITFALL 防回歸、FACT 來源這三項現在已經有人檢查(lint 整篇警告,note-shape 只看新增行)。
- 設計新增的 `[出處:]`、`[test:/repro:/防回歸:]`、`[觀測:]` 與這三項是同一件事的更嚴格版。
- 設計沒寫「取代或擴充 `_CONTEXT_MARKER_RULES` 與 `_NOTE_SHAPE_PREFIX_RULES`」。照字面實作,會是 lint 一張、note-shape 一張、新的一張。
- 應明寫併表:新表取代這兩張,`context_marker_warnings` 與 `rule_lifecycle_warnings` 讀它。

**A2** 事件式撤除條件另寫了一套語法
severity: major
blocking: 是——專案已有「事件成立就觸發」的條件語法,同一件事設計又寫一套
引句:「`[retire:度量 <指標> <比較> <數字>]`、`[retire:事件 <[[節點]] 狀態=值> 或 <檔或符號出現>]`、`[retire:人裁 by:日期]`」
佐證行 file: `scripts/lumos:28505`(`_PROBE_TOKEN_RE`:`[when-…:]` 加 `[by:]`)
佐證行 file: `scripts/lumos:28506`(`_PROBE_KEYS = ("file","symbol","test","status")`)
佐證行 file: `scripts/lumos:28616`(`_probe_parse`,把條件解析成 `(鍵, 值)` 清單)
說明:
- 既有的條件標記已經能表達「檔、符號、測試、節點狀態」,對應設計的「檔或符號出現」和「節點狀態=值」。
- 設計說「沿用轉變判定」,但表面寫法換成 `事件 <…> 或 <…>` 自然語言式,要另寫一個解析器。
- 這是一份筆記裡兩種語法,描述同一種條件。
- 建議 `[retire:事件 …]` 直接收 `[when-file:…]`、`[when-status:…]` 這一組,共用 `_probe_parse`。
- 度量類(`度量`)與人裁(`人裁`)是新能力,不在此列。

**A3** `by` 這個鍵一個名字三種意思
severity: minor
blocking: 否——結構對,只是命名撞名,改名即可
引句:「`[出處:日期 來源]`、`[by:取代者]`、`[applies:路徑]`」
佐證行 file: `scripts/lumos:28505`(`by` 在 REVISIT 行是期限日期)
佐證行 file: `scripts/lumos:28626`(`_probe_parse` 把 `by` 當 `YYYY-MM-DD`)
說明:
- 設計裡 `[by:取代者]` 是指向被取代者或取代者的節點。
- 設計裡 `[retire:人裁 by:日期]` 是值裡再套一個 `by:`,跟「整條筆記只有前綴冒號與 `[鍵:值]` 兩種記號」的說法矛盾。
- 同一個鍵在 REVISIT 行是期限日期,在新格子是節點。這與設計自己寫的「同一個意思只有一種鍵」相反。
- 建議把 `[by:取代者]` 改名(例如 `[取代:]`),人裁期限直接用 `[until:]`(RULE 已有 `[until:]`,`scripts/lumos:3314`)。

**A4** 「同一個意思只有一種鍵」自己沒做到
severity: minor
blocking: 否——可以直接補上對應關係
引句:「| FACT/FLOW/DEP | 現況與數值 | `[來源:部署\|資料庫\|生產\|外部\|人工]` `[觀測:日期]`」
佐證行 file: `scripts/lumos:3295`(`_CTX_SOURCE_RE` 的 `[來源:]` 是既有記號,設計沿用)
佐證行 file: `scripts/lumos:3316`(RULE 的 `[confirmed:]` 與 `_RULE_CONFIRM_STALE_DAYS`,`scripts/lumos:3318`)
說明:
- 「這句話哪來的」在 WHY 叫 `[出處:]`,在 RULE 叫 `[依據:]`,在 FACT 叫 `[來源:]`。
- 「什麼時候確認過」在 RULE 是 `[confirmed:]`,在 FACT 是 `[觀測:]`。
- 其中 `[來源:]` 與 `[confirmed:]` 是專案原有的,新增的 `[出處:]`、`[依據:]`、`[觀測:]` 與它們各自重疊。
- 設計該說明刻意分開的理由,否則就是自己違反「同一個意思一種鍵」。

**A5** 子開關的先例挑了較遠的那個
severity: minor
blocking: 否——旗標名與值域結構對,只是先例引錯,以及跟 `gate` 的關係沒講
引句:「**子開關(新增)**:`note_shape.slots`(`block` 預設 / `warn` / `off`),照 `drift_check.old_sentence` 那種」
佐證行 file: `scripts/lumos:26130`(`_note_shape_negation_parse`:`note_shape.negation`,同一道閘底下的子開關,值域 warn/off,預設 warn)
佐證行 file: `scripts/lumos:30316`(`_drift_old_sentence_config`:`drift_check.old_sentence`,預設 warn)
佐證行 file: `scripts/lumos:25467`(`_note_shape_config`:`note_shape.gate` 預設 block)
說明:
- 同一道閘(note_shape)已經有一個子開關 `negation`,最近的先例是它,而不是別道閘的 `old_sentence`。
- 兩個既有子開關預設都是 warn,設計的 `slots` 預設 block。這是刻意的新擋,可以接受,但該明講。
- 設計沒講 `note_shape.gate=off/warn` 與 `slots` 的優先順序。
- `negation` 的壞值處理是「照 warn、講一句」,`slots` 是「照 block、講一句」。形式一致,方向相反,屬合理。

**A6** `lands_in` 的兩篇接不住所有落點
severity: minor
blocking: 否——只是落點清單不完整,補列即可(⚠ 我只確認了前綴表歸屬、`lumos new` 骨架與 doctor 三處的歸宿,沒逐支檔核對)
引句:「- **DEP/FLOW 只放連結**:一律改 SEE;既有規範、`lumos new` 骨架提示、筆記形狀檢查對只放連結 FLOW/DEP 的放行,一起改掉(C 的代價,本篇負責)。」
佐證行 file: `scripts/lumos:3264`(`SYMBOL_RE` 與前綴名單,LOG、SEE 要加在這裡)
佐證行 file: `scripts/lumos:3425`(`_search_region` 用 `SYMBOL_RE` 標區域,搜尋行模式要跟著認新前綴)
說明:
- 擋(`note_shape.slots`、必有鍵、E、D 的形狀檢查)寫進〈筆記內容閘〉:對。
- `[by:]`、`[retire:事件]` 的過期檢查寫進〈存量漂移守衛〉:對。
- 其餘四塊不屬這兩篇的職責:紀律範本與 skill、`lumos new` 骨架、前綴表與搜尋區域標記、doctor 的時間類提醒。
- 實測 `筆記內容閘` 的 responsibility 只管提交前與推送前的擋,`存量漂移守衛` 不含 doctor 的非漂移提醒。
- 這兩篇的 `about_code` 都沒有紀律範本,`lands_in` 該補上實際管這些檔的 Systems 節點。

---

不對齊共 6 條,其中 major 2 條

補充:這份設計的 `[test:名]` 存在性檢查、`[repro:]`、LOG/SEE、度量類提醒都是專案原本沒有的能力,依你的指示沒有標成不對齊。
