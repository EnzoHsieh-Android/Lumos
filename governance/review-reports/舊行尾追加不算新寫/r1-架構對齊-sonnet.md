severity: major

## 問一:分層與依賴方向

配對放在 notelines 那一層、給兩層共用,方向對。第一層 `_note_shape_eval` 和第二層 `_note_audit_items` 本來就都靠下層的 `_notelines_new` 取新行(`scripts/lumos:28407`、`scripts/lumos:28947`),配對再往下放一格不會造成反向依賴。第二層只多一個 `appended` 欄位、第一層只多算 N/O 計數,各層的判定仍留在各層。

有兩處對不上,見 A1 和 A3。

**A1**
severity: major
blocking: 是 — 同一份 `git diff -U0` 輸出會有兩套解析器,規格沒說明為什麼不改成一套
引句:「新寫一支解析器 `_notelines_parse_hunks`:同一份 `git diff -U0` 輸出」
- `_notelines_parse_added` 做的就是解析 `git diff -U0`,新解析器是它的超集:多保留被刪行和舊起點。
- 規格自己指出舊解析器的缺陷:內容行 `++ x` 會被當成檔頭。照規格做,兩套會並存,而且對同樣的輸入行為不同。
- 較一致的做法是只留一套:`_notelines_parse_added` 改成從 hunks 取被加的行,同時修掉檔頭誤判。
- 佐證:`scripts/lumos:27178`(`_notelines_parse_added`,第 27181 行用 `startswith("+++ ")` 判檔頭)
- 佐證:`scripts/lumos:27400`(`_NotelinesNet.lines` 也是靠 `_notelines_parse_added` 解析)

**A3**
severity: minor
blocking: 是 — 規格說的「共用同一次 diff」照現有結構做不到,動手前要改寫這句
引句:「推送前那次範圍淨差異跟既有的 `_NotelinesNet` 共用同一次 diff(不多跑第二次)。」
- `_NotelinesNet` 只存解析後的行號集合,不留原始輸出或 hunks。
- 它是懶算的:只有 `keep_other` 時才建(`scripts/lumos:27396`),第二層走 `keep_other=False`,根本沒有 Net。
- 它的註解明說要「用到才算」,這是併發審查席的要求。要共用就得改它的存放內容和建立時機,等於改動既有契約。
- 提交前(staged)那一路另外跑 `_ns_diff("--cached")`(`scripts/lumos:27353`),`_notelines_append_pairs` 又是獨立函式,所以提交前還是多一次 diff。
- 規格「效能」段寫的「提交前本來就跑那支 diff」不成立,這兩處要一併改。
- 要真的共用一次 diff,較貼近現有做法是照 `sink` 的傳法,由 `_notelines_new` 一併交出 hunks。
- 佐證:`scripts/lumos:27400`、`scripts/lumos:27396`、`scripts/lumos:27353`

## 問二:命名與錯誤處理

命名沿用現有混用:函式用 `_notelines_`,常數用 `_NS_`(例如 `scripts/lumos` 裡的 `_NS_STRUCT_KEY_RE` 與 `_NOTELINES_HEADING_RE` 並存),不另列。放寬帳用的 `hints`/`tags`/`slots` 式有預設值的容器參數,也和 `_note_shape_eval` 簽名(`scripts/lumos:28378`)一致。

**A4**
severity: minor
blocking: 否 — 結構沒問題,只是回傳約定要寫清楚
引句:「整批回 None(git 失敗、路徑含換行)就這次全不配對。」
- 現有慣例是 git 失敗回 `None`,呼叫端自己 fail-open。例子:`_ns_slots_old_lines` 回 `None`(`scripts/lumos:28272`),`_NotelinesNet` 用 `failed` 旗標。
- 規格同時又寫「整支包在 try 裡,任何例外都當沒有配對」(第 42 行)。
- 這樣出現兩種失敗出口:`None` 和 `{}`。兩者呼叫端是否同樣處理,規格沒講。
- 否定收集器那段吞例外有先例,但範圍窄;這裡包住整支函式,範圍大很多。
- 建議寫明:`None`、`{}`、例外三種情形,呼叫端都落到「整行查」。
- 佐證:`scripts/lumos:28240`(`_ns_deleted_summary_lines` 的 git 失敗約定)

**A5**
severity: minor
blocking: 否 — 抽共用的方向對,但現有函式有寫死的地方,要先講怎麼拆
引句:「量法借舊句檢查帳的 `_drift_m1_fit`(用 `_gate_event_build` 組完整事件、量 JSON 一行的位元組、從尾端丟;拆成共用的一支)」
- `_drift_m1_fit` 把閘名寫死成 `"drift-check"`,又綁定 `rows`、`nodes` 的語意(`scripts/lumos:33635`)。
- 放寬帳要裁的是 `[路徑, 行號]` 清單,閘名是 `note-shape`。
- 拆成共用時要把閘名和被裁的鍵當參數,不然就是複製出第二份。
- 這是借用,不是第二種做法。
- 佐證:`scripts/lumos:33635`、`scripts/lumos:1234`(寫帳走 `_gate_event_or_warn`,規格說走既有寫入器是對的)

## 問三:第二種做法

**A2**
severity: minor
blocking: 否 — 兩者問的問題不同,沒有重複實作的疑慮,但規格要講清楚為什麼不能併
引句:「本案的「同一個改動區塊裡被刪、被接字的那一行」(問:只多了尾巴嗎)」
- 結論:`_notelines_parse_hunks` 不算 `_ns_deleted_summary_lines` 的第二套。
- 後者只收「像摘要前綴的被刪行」,把縮排更深的續行接回去,而且用 `--no-renames`。前者要保留區塊邊界,並用 `-M`。
- 兩者的 git 旗標不同:`_ns_deleted_summary_lines` 自己組一份 git 參數(`scripts/lumos:28245`),新解析器走 `_ns_diff`(`scripts/lumos:27207`)。
- 規格沒寫為什麼不併。
- 建議在規格補一句「刪除行這邊要的是整行文字加續行合併,所以不併」。
- 佐證:`scripts/lumos:28240`、`scripts/lumos:27207`

**A6**
severity: minor
blocking: 否 — 這是規格第 6 條的文字問題,不是設計問題
引句:「**三種「舊行」各問各的**:本案的「同一個改動區塊裡被刪、被接字的那一行」(問:只多了尾巴嗎)」
- 三種舊行並存的理由成立,各自回答不同的問題:是否只多了尾巴、程式端是否變了、欄位是否補齊。
- 第 6 條的文字重複又混亂:「不動的」、喚醒那一路、筆記格子的舊行判定各出現兩次,結尾還掛著「`_notelines_new` 交出的 rows。存量漂移檢查。」兩個沒接上句子的片段。
- 讀起來像改稿殘留,AI 讀者容易誤判哪幾種舊行會被動到。
- 建議重寫成三條並列的清單。
- 佐證:`scripts/lumos:28272`(`_ns_slots_old_lines` 的格子舊行來源,是三種之一)

不對齊共 6 條,其中 major 1 條
