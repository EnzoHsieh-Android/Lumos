severity: major

# r2 通才席審查報告(回頭條件寫法補齊_計劃,第 2 版修訂稿)

審查範圍:全份逐節讀完;對照 `scripts/lumos`(`_revisit_split`、`_revisit_lines`、`_probe_lines`、`_probe_parse`、`_ns_revisit_violations`、`_issue_close_revisits`、doctor E5 與 Z 段、`cmd_drift_ack`、`_drift_probe_scan`)與 `scripts/test_lumos.py`。已另外用腳本核對:spec 自己的非程式碼文字沒有任何一行會被它提的新規則命中(跑過 `_strip_inline_markup` 加 `_revisit_split`)。現況量測:本 repo 圖譜裡不是 REVISIT 行、卻含 `REVISIT:` 接日期或 `[when-` 的可見行,排除緊鄰開引號的後是 67 行、緊鄰開引號的 1 行,跟 spec 說的 68 行吻合。

## 做法 第 1 節 句中的 REVISIT

**U1 Z 段一樣被 warn_soft 的 3 條上限截斷,spec 拿「不被擠掉」當放 Z 段的理由,事實不成立**
severity: minor
blocking: 否 — 清單仍在 `--verbose` 與 `drift scan` 看得到,只是 spec 宣稱的好處對不上程式
引句:「也不受 E5 軟段 3 條上限擠掉到期清單」
1. spec 第 1 節第 3 點用「Z 段不受 3 條上限擠」支持把存量清單放 Z 段不放 E5。
2. 問題:doctor 的 Z 段也是 `warn_soft(_zl, …)`,走同一個 `_SOFT_CAP = 3`,超過的收成「另 N 條」。Z 段現有的行是:條件式回頭條件總計一行、c1 到 c5 最多五行、再加設定提醒行。新加的「寫在句中的 REVISIT」若排在這些後面,任何同時有三條以上其他發現的專案(例如工具鏈自己,c 類加條件式計數很容易到三行)裡,句中 REVISIT 那行被摺進「另 N 條」,看不到。
3. 例子:Z 段已有「條件式回頭條件 …」、`[c2]`、`[c3]` 三行 → 第四行(句中 REVISIT)只剩「…另 1 條(lumos doctor --verbose 看全部)」。S5 的測試用單一 fixture 只有這一種發現,測不出來。
4. spec 沒寫新那行排在 Z 段哪個位置,也沒承認這個上限。
5. 查證:file: `scripts/lumos:1379`(`_SOFT_CAP = 3`)、`scripts/lumos:1383-1395`(`warn_soft` 截斷)、`scripts/lumos:2340-2349`(Z 段走 `warn_soft`)。

**U2 擴充 `_probe_lines` 的「寫在不評估的地方」清單,會同時動到 doctor 既有計數與 `drift scan`,spec 只交代了 `drift check`**
severity: minor
blocking: 否 — 行為由實作者隨手選,但會有雙報與 scan 輸出暴增,屬於被漏列的平行讀取端
引句:「`drift check` 只用 `_probe_lines` 的第一個回傳值,不受影響」
1. spec 做法第 1 節第 3 點把句中 REVISIT 塞進 `_probe_lines` 回傳的第二個清單(dead),然後只確認 `drift check` 不讀第二個值。
2. 還有兩個讀端讀第二個值,spec 沒提:
   - doctor Z 段(`_drift_doctor_lines`):`n_dead += len(dead)`,印出「寫在不評估的地方 {n_dead} 處」。句中 REVISIT 進了同一個清單,就會先被算進這一行,spec 又要求另起一行「寫在句中的 REVISIT N 處」——同一批 67 行雙報一次。要避免就得用原因字串或新欄位把兩種分開,spec 沒寫怎麼分;而且 `if n_rows or n_dead:` 這個條件會讓原本沒有條件式回頭條件的專案多印一行無意義的「條件式回頭條件 0 條」。
   - `lumos drift scan`(`_drift_probe_scan`):`probs += [(p, no, tx, why) for no, tx, why in dead]`,輸出在「回頭條件與撤除條件的問題」下,文字模式與 `--json` 的 `problems` 都會多出 67 筆。標題寫的是「寫錯、沒帶期限、指不到、寫在不評估的地方、判不了」,不含「寫在句中」;S5 也沒涵蓋 scan。
3. 例子:本 repo 套用後,`lumos drift scan` 的 problems 從現況變成 +67 筆,而 spec 沒說這是想要的(它在〈範圍〉說存量只由 doctor Z 段列出)。
4. 查證:file: `scripts/lumos:34806-34811`(`n_dead`)、`scripts/lumos:32514-32515`(scan 收 dead)、`scripts/lumos:34791-34796`(scan 印 probs 的標題)。

## 做法 第 2 節 結案標記

**U3 「`_probe_parse` 多認一個鍵 `closed`」與另立的 `_revisit_closed` 是兩套解析,分工沒寫;照字面只改正則會讓條件式的結案行變成「條件寫錯」並停止評估**
severity: major
blocking: 是 — 條件式結案(S7)的核心解析有兩個互相打架的歸屬,照字面實作會得到與 S6/S7 相反的行為
引句:「`_probe_parse` 的連續標記多認一個鍵 `closed`」
1. spec 第 2 節第 1 點說條件式的 `closed` 是 `_probe_parse` 的連續標記多認一個鍵;第 2 點又說合格與否由獨立的 `_revisit_closed(probe)` 判,回 `{"closed", "errs"}`。兩處都沒說 `_probe_parse` 遇到 closed 時要做什麼(存值?驗值?把錯誤放進自己的 `errs`?),也沒說 `_revisit_closed` 的輸入 `probe` 是整行可見文字還是 `REVISIT:` 後面的 rest(`_revisit_split` 回 rest,`_revisit_misplaced(probe)` 說輸入是整行,兩個 helper 的 probe 同名不同義)。
2. 現行 `_probe_parse` 的分支是:`key == "by"` 一支,其餘全部走 `k = key[len("when-"):]` 再驗。只把 closed 加進 `_PROBE_TOKEN_RE` 的字首選項,`closed` 會被切成 `k = "d"`,得到「不認得的條件鍵 when-d」並把 `bad` 設成真。
3. 兩種後果都違反 spec 自己的規則:
   - 若 closed 的錯誤進了 `_probe_parse` 的 `errs`,第一層會報既有的「條件寫錯」,而不是 spec 第 2 節第 4 點的「結案標記寫錯」,同一個錯誤兩個規則名。
   - 若同時設了 `bad`,check 與 scan 會因為 `bad` 不評估這條條件(`if not pr["conds"] or pr["bad"]: continue`),等於「寫錯的結案標記讓條件被靜音」,而 spec 第 2 節第 2 點明寫寫錯的結案標記要當沒寫、照評估。
4. `_PROBE_LEAD_RE`(同一組連續標記的第二份正規式,`_revisit_lines` 用它剝出摘要)也要同步多認 closed,否則條件式行的摘要欄會帶著 `[closed:…]` 一起顯示在 E5 與 Issue 列出裡。spec 只提了 `_probe_parse`。
5. 具體輸入:`REVISIT:[when-file:a.py][closed:2026-10-03 已改用新閘道][by:2026-12-31] t`。照字面只改 `_PROBE_TOKEN_RE` → `_probe_parse` 回 `bad=True`、`errs=["不認得的條件鍵 when-d"]`,S7 的「標記夾在條件與 `[by:]` 中間時 `[by:]` 應照讀得到」雖然 `by` 讀到了,但整行被標壞損、不評估,跟「結案」的語意相反。
6. 查證:file: `scripts/lumos:31694-31697`(`_PROBE_TOKEN_RE`、`_PROBE_LEAD_RE`)、`scripts/lumos:31804-31840`(`_probe_parse` 分支與 `bad` 旗標)、`scripts/lumos:32301-32305`(`bad` 的行不評估)。

**U4 E5 處理提示改文字後,既有測試會翻紅,spec 沒列要同步改**
severity: minor
blocking: 否 — 實作時一跑測試就會發現,但屬於遺漏的連帶改動
引句:「把該行日期改下一次、刪行,或在日期後面加 `[closed:日期 理由]`」
1. spec 第 2 節第 3 點把 E5 的提示字串改了。
2. 既有測試 `t_doctor_revisit_reminder` 用子字串 `"日期改下一次或刪行" in r.stdout` 釘這句。新句是「日期改下一次、刪行,或…」,子字串「日期改下一次或刪行」不再出現 → 那條檢查翻紅。spec 第 3 節〈說明與同步〉與驗收條款都沒提要改這支測試;S9 只新增了斷言。
3. 查證:file: `scripts/test_lumos.py:35877`、`scripts/lumos:2322`。
4. 同一個問題的鄰居:`t_set_issue_closed_lists_revisits` 釘的是「還留著 3 行回頭條件」(`scripts/test_lumos.py:59146`),提示尾巴改字不影響它,不需另改。

**U5 結案寫法的提示字串一律寫成日期式,對條件式的行(E5 會列、Issue 列出會列、第一層改法也會給)是錯的範本**
severity: minor
blocking: 否 — 照提示做的人會把條件式行改壞,但有第一層擋寫錯
引句:「要結案就寫成 `REVISIT:日期 [closed:日期 理由] 原待辦`」
1. 三個提示都只給日期式:第一層「回頭條件寫在句中」的改法、E5 的「在日期後面加」、Issue 結案列出的「寫成 `REVISIT:日期 [closed:日期 理由] …`」。
2. E5 與 Issue 列出的行本來就含條件式(`_revisit_lines` 回 `cond` 種類,E5 用它的 `[by:]` 判到期)。條件式的結案標記要放在條件標記之後,不是「日期後面」。
3. 例子:句中的 `…。REVISIT:[when-file:a.py][by:2026-12-31] x` 命中第一層,改法叫作者寫成 `REVISIT:日期 [closed:…] 原待辦`,作者若照做就把條件式換成日期式、丟掉條件。E5 對條件式逾期行的提示「在日期後面加」也一樣誤導。
4. 查證:file: `scripts/lumos:31732`(cond 行在 `_revisit_lines` 取 `[by:]` 當日期)、`scripts/lumos:2303-2323`(E5 列 cond 行並用同一句提示)。

**U6 條件式行被 `_probe_lines` 在抽取層跳過後,「拿掉結案標記」的推送判定沒定義,可能把條件早已成立的舊行當成新轉變擋下**
severity: minor
blocking: 否 — 屬於 revert 結案的少見動作,擋下訊息還能解釋;但行為沒寫
引句:「條件式的不評估:`_probe_lines` 不抽它」
1. 推送判定(`_drift_probe_check`)用同一支抽取函式讀起點與終點,「起點沒有同一條」就算新成立。起點那版若這行帶合格的 `[closed:]`,抽取層跳過它 → 起點沒有這條;終點把 `[closed:]` 拿掉後條件早就成立 → 判成「這次推送讓條件從不成立變成立」,擋下。
2. spec 只在 S7(scan)寫了「拿掉結案標記應照列」,第 2 節第 6 點只講「新寫一條已成立的條件同時寫 closed 不擋」,沒講反向(重開)的推送行為。〈實務隱患〉的回滾段也只談還原提交。
3. 這是否想要沒寫:重開一條已結案的條件被擋,訊息是「條件成立了」,作者可能是在改錯字,卻被要求表態或刪掉。照 `_retire_lines` 跳過 superseded 的先例,同樣的重開(把 superseded 拿掉)也會這樣,所以可能是承襲慣例,但 spec 該明講。⚠ 判不準是想要的行為還是漏想。
4. 查證:file: `scripts/lumos:32301-32306`(起點與終點用同一支 extract)、`scripts/lumos:31880`(`_retire_lines` 跳過 superseded 的先例)。

## 做法 第 1 節 第 1、2 點的銜接

**U7 `_revisit_misplaced` 的「前面緊鄰」判定沒說逐個出現還是整行,而且只覆蓋緊貼開引號的寫法**
severity: minor
blocking: 否 — 影響誤擋範圍,有單次跳過出口
引句:「前面緊鄰的字元不是開引號」
1. 同一行出現兩次 `REVISIT:` 接日期(一個在引號裡當範例、一個是真的句中回頭條件)時,文意「那個 `REVISIT:` 前面緊鄰」可以讀成任一個出現命中就真、也可以讀成整行第一個。S3 的測試只放單一出現。
2. 引號範例句不緊貼的寫法照樣被判成死條件:例如 `例如「若 REVISIT:2026-10-05 到了就…」` 這種框住整句、`REVISIT:` 前面是空白的寫法,前面緊鄰的字元不是開引號 → 命中,而〈做法〉第 1 節第 1 點的理由是「引號框起來、沒包反引號的範例句是存量裡常見的提法」。本 repo 實測緊貼開引號的只有 1 行,這個排除規則對存量的實際覆蓋很小;能不能覆蓋這類範例句 spec 沒討論,改法字串又叫作者「用行內程式碼或引號包起來」,引號整句框起來卻會被擋,與改法字串打架。
3. 查證:本 repo 圖譜可見行腳本掃描:67 行未排除、1 行因緊鄰開引號而排除(見檔首說明)。

**U8 第一層規則只寫了「`_revisit_split` 回 None 時呼叫」,但現行 `_ns_revisit_violations` 對正文以外的區塊根本不呼叫 `_revisit_split`**
severity: minor
blocking: 否 — 實作者補得出,但 S2 的「開頭欄位清單項不報」要靠它
引句:「`_ns_revisit_violations` 對新寫的行,在 `_revisit_split` 回 None 的時候呼叫第 1 點」
1. 現行 `_ns_revisit_violations` 的結構是:`reg in ("body", "summary")` 且不是表格列才呼叫 `_revisit_split`;其餘(開頭欄位其他欄、decisions、表格列)直接只看 `_PROBE_ANY_RE`。spec 要求這些區塊也看句中 REVISIT,並且對開頭欄位 `- REVISIT:2026-10-05 x` 判成 REVISIT 行而不報。
2. 照現行結構,這些區塊根本沒呼叫 `_revisit_split`,實作者得在第二個分支補一次呼叫並決定順序(先看 `_PROBE_ANY_RE` 還是先看句中判定,才能做到 spec 說的「已經報了條件寫在不評估的地方的不重報」)。spec 沒給順序;且 `reg == "decisions"` 也屬於這個分支,spec 的清單(正文、摘要、表格行、開頭欄位其他欄)沒明講它。
3. 查證:file: `scripts/lumos:27915-27943`(`_ns_revisit_violations` 的兩個分支)。

## 其餘節

### 範圍
已讀,無 finding。

### 做法 第 3 節 說明與同步
已讀,無 finding。(引用的檔 `skills/lumos-project-notes/commands/03-寫回圖譜.md`、`skills/lumos-project-notes/SKILL.md`、`scripts/templates/graph-discipline.md`、`scripts/graph-rename.sh` 都存在;技能手冊兩處的 REVISIT 說明行在 03 第 49-50 行與 SKILL.md 第 73 行;`[[Projects/舊行尾追加不算新寫_計劃]]`、`[[Projects/回訪掃描_計劃]]`、`[[Projects/漂移防治路線圖_計劃]]`、`[[Projects/筆記格子寫法與過期檢查_計劃]]〈不套格子〉`、`[[Projects/存量漂移防線_計劃]]〈做法〉第 0 節`、`[[Systems/筆記內容閘]]`、`[[Systems/存量漂移守衛]]` 都存在。)

### 回退
已讀,無 finding。

### 天花板
已讀,無 finding。

### 審計修正紀錄
已讀,無 finding。(r1 各修法在本版沒有看到回退的跡象;「實字計數抽共用」所指的 `_excluded_line` 內那段 `re.findall(r"[^\W_]", reason)` 確實存在於 `scripts/lumos:6396-6408`。)

## 實務隱患鏡頭:逐類答

- 併發:無 — 本案不寫檔、不新增治理帳事件(spec 已寫);提交時的規則在既有的暫存行讀取路徑上跑,沒有新的共享狀態。唯一的並行相關點是 U6 的推送判定,已列。
- 效能:無新問題 — 第一層多一個正則加一次結案解析、只對新寫的行跑;doctor Z 段每篇本來就跑一次 `_probe_lines`,多一個正則;E5 的結案解析只在 `_revisit_lines` 回的 REVISIT 行上做。唯一的放大是 U2:`drift scan` 與 doctor 的輸出量(67 行)不是時間成本。
- 回滾:無 — 單一提交可還原;〈實務隱患〉回滾段對「已結案的條件在下一次推送才變成立」的描述正確;U6 是前進方向(重開結案)的行為,不是回滾問題。
- 誤擋與繞過:有,已列 U7(引號範例句沒有被排除的寫法)與 U8(區塊分支的順序);繞過面 spec 自己已列(全形冒號、引號框住、`[closed:]` 靜音),經查程式後沒有新增的繞過路徑。另外 `_drift_fix_shape_err` 把工具要寫的自由文字也過 `_ns_revisit_violations`(`scripts/lumos:33372`),新規則一加,`drift fix` 改寫文字若含句中的 REVISIT 會被自己擋掉;目前工具產生的文字沒有這種形狀,風險低,不另列。
- 金流、對外送出、不可逆:無 — 只讀筆記文字,不碰錢、不連網、還原提交即回。
- 跨環境/時區:無 — r1 的時區問題已用「不比日期先後」解掉,本版沒再引入日期比較。

最嚴重 severity 是 major,blocking 共 1 條(U3)。
