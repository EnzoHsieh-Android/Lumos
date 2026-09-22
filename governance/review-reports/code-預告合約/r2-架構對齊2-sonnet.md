severity: major

## F1 新抽出的 extract_planned 打破了同區塊「抽取函式跟自己的正則放一起」的既有慣例

severity: major
blocking: yes

觀察到什麼:這次把 r1 寫在 `cmd_context` 輸出層裡的預告掃描迴圈,抽成一支獨立函式 `extract_planned`,刻意放在 `extract_contracts` 正上方(`scripts/lumos:3672`),docstring 明講理由:

引句:「跟 extract_contracts 成對:那支只認正式合約記號(刻意撈不到預告),這支只認預告記號。」

引句:「★兩支都放這裡★(代碼審 r1 架構席):第一版把掃描迴圈寫在輸出層,等於同一件事兩個地方各做一次。」

`cmd_context` 那邊呼叫端也把理由講白了:

引句:「所以另外有一支 extract_planned;兩支都放在合約抽取那一區,不散在輸出層。」

但 `extract_planned` 真正依賴的正則 `PLANNED_RE`,定義在 `scripts/lumos:10560`——離它的呼叫處 6800 多行,而且是跟 `cmd_guard_plan`、`GUARD_MARK_FIELD` 這些 guard 指令實作混在一起的區塊,不是「合約抽取那一區」。

怎麼重現:對照這個檔案裡真正的同層慣例——`extract_reversibility`(`scripts/lumos:4257`)是這次要成對的 `extract_planned`/`extract_contracts` 之外,檔案裡另一支同類型的「從 summary KEY 行抽標記」函式,它用到的四個正則 `CHECKPOINT_RE`/`IRREVERSIBLE_RE`/`ROLLBACK_REF_RE`/`GUARD_REF_RE` 全部定義在 `scripts/lumos:4170-4173`,就在它自己正上方 80 幾行,跟 `INVARIANT_RE`/`DEBT_RE`(`scripts/lumos:3668-3669`,`extract_contracts` 正上方)、`TEST_REF_RE`/`AUDIT_REF_RE`/`INV_TAG_RE`/`KILL_REF_RE` 等全部落在 `scripts/lumos:3668-4181` 這同一個群集裡。也就是說,這個檔案裡每一支「合約抽取」函式的正則常數,一律緊貼在函式旁邊、同一個群集區塊——`extract_planned` 是這個群集裡唯一一支正則遠在天邊的。

為什麼是 bug 而不是風格:作者自己在兩處註解都明講了意圖是「不要讓同一件事分散在兩個地方」「兩支都放在合約抽取那一區」,但只搬動了函式本體,沒有一併把 `PLANNED_RE` 挪過來(或另立一個群集內的別名/轉發)。結果是:讀 `extract_contracts`/`extract_reversibility` 能就地看懂它們用哪個正則,但讀 `extract_planned` 看不到 `PLANNED_RE` 定義在哪,得往下翻 6800 行、翻進一段完全不相關的 guard 指令實作才找得到。這正是這次 r1 之所以會生出「同一件事兩個地方各做一次」這個問題的同一種根因(散落、找不到既有東西在哪),這次的修正只解決了「函式本體重複」的表面,沒解決「正則跟函式脫鉤散落」的裡層,跟同層對照函式(`extract_reversibility`)的慣例相反。

## F2 新增的 frontmatter 鍵名清單註解改成區塊上方多行,跟同一份清單裡前三次新增的行內註解寫法不一致

severity: minor
blocking: no

觀察到什麼:`_KNOWN_FRONTMATTER_KEYS`(`scripts/lumos:4585`)這個 tuple 裡,之前兩次新增鍵名都是「鍵名 + 同一行行內註解(日期＋事由)」:

引句:「"responsibility", "lands_in",   # 2026-09-11 每支檔有家:Systems 的負責範圍、計劃的落點」

引句:「"plan_risk", "door",   # 2026-09-17 計劃風險(作者只能往嚴標 high);door 是舊寫法,讀得懂但提醒改」

這次新增的四個鍵名改成註解寫在鍵名清單「上方」獨立兩行,鍵名本身那行完全沒有行內註解:

引句:「# 2026-09-22 預告合約(必要合約清單_計劃):守衛節點的四個欄位。不登記的話,」

怎麼重現:直接看 diff(patch 第 203-206 行)就能比對出三種寫法混在同一個 tuple 裡——前兩筆是「值 + 行內註解」,新的這筆是「註解獨立成上方兩行 + 值」。

為什麼是 bug 而不是風格:這條清單的既有慣例本身就是拿「行內註解」當索引在用——往後任何人要查「這個鍵名是哪次加的、為什麼」,習慣是掃該行尾端的 `#`,新這筆按同一套掃法會被跳過(得往上多看兩行才找得到脈絡)。不算它是機械會出錯的 bug,列為 minor、不擋:純粹是同一份清單裡格式不統一造成之後維護時的認知負擔,不影響任何行為。

---

審過的路徑(佐證,非 patch 內容):
- `scripts/lumos:3668-4181`(合約抽取正則群集:INVARIANT_RE/DEBT_RE/TEST_REF_RE/AUDIT_REF_RE/INV_TAG_RE/KILL_REF_RE/CHECKPOINT_RE/IRREVERSIBLE_RE/ROLLBACK_REF_RE/GUARD_REF_RE)
- `scripts/lumos:3672`(extract_planned 定義處)
- `scripts/lumos:4257`(extract_reversibility,同層對照函式)
- `scripts/lumos:10560-10562`(PLANNED_RE/WATCH_REF_RE/DUE_REF_RE,遠在 guard 指令實作區)
- `scripts/lumos:4585-4596`(_KNOWN_FRONTMATTER_KEYS 全貌與三次新增的註解寫法)
- `scripts/lumos:10720`、`scripts/lumos:10781`、`scripts/lumos:10848`(`_guard_planned_line` 簽名從 3-tuple 改 4-tuple,兩處呼叫端都同步更新,未見漏改——查過但不算發現)
- `scripts/lumos:4711`(lint「沒見過的鍵」訊息格式,核對新測試 `t_guard_plan_node_passes_lint_clean` 的字串比對確實對得上實際輸出)

已驗過但沒問題的路徑(排除項,不列進發現):
- 測試寫法的翻紅釘慣例:`scripts/test_lumos.py` 全檔 254 處都是「docstring 裡寫『翻紅釘:…→ 第 N 條翻紅』」,這次新增的三支測試(`t_guard_plan_node_passes_lint_clean`、`t_guard_plan_hostile_claims`、`t_guard_abandon_wrong_home_blocks`)寫法一致,沒有偏離。
- 「整段輸出搜字串」這種寬鬆斷言(如 `"很重要的真合約" in gl.stdout`):在既有測試裡本來就大量使用(緊鄰的 `t_abandoned_excluded_and_marker_kept` 就有 `"棄了的" not in out`),不是這批新引入的寫法,不算偏離。
- `_guard_plan_slug` 與 `guards:` 欄位的實際寫入格式(`scripts/lumos:10620-10622`)跟新測試 `t_guard_abandon_wrong_home_blocks` 裡用字串取代模擬手改(`"  - Systems/Pay"`)的假設一致,沒有對不上。
