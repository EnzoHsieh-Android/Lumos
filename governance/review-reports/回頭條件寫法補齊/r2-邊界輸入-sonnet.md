severity: major

審查對象:/tmp/回頭條件寫法補齊-r2.md(第 2 版)。對照 repo:scratchpad/rw。方法:逐節讀完;用 python3.14 載入 scripts/lumos 實跑 `_revisit_split`、`_probe_parse`、`_probe_lines`、`_revisit_lines`;掃 docs/ 全部筆記量存量形狀。第 1 輪已修好的項目(日期比今天、`[by:]` 夾中間、非 REVISIT 行的 `[closed:`、E5 搬 Z 段、開頭欄位行首形狀)不重報。

**B1 Z 段「寫在不評估的地方」既有計數行會被句中 REVISIT 灌水,而且跟新增那行重複計**
severity: major
blocking: 是 — 照字面實作,既有的一行語意被改掉、同一批位置在 Z 段出現兩次,驗收 S5 描述的呈現做不出來。
引句:「`_probe_lines` 回傳的「寫在不評估的地方」清單多收一種「REVISIT 寫在句中」」

1. 位置:做法 第 1 節第 3 點。
2. 問題:`_drift_doctor_lines` 現況對 `_probe_lines` 的第二個回傳值只做 `n_dead += len(dead)`,然後印「條件式回頭條件 {n_rows} 條…;寫在不評估的地方 {n_dead} 處」。spec 把句中 REVISIT 塞進同一份 `dead`,又要求「另起一行」印「寫在句中的 REVISIT N 處」。`dead` 的元素只有 `(行號, 原文, 原因)` 三欄,沒有種類欄,兩種之間只能靠比對原因字串分開;spec 沒寫要怎麼分,也沒要求改既有那一行的計數。
3. 例子:圖譜有 0 條條件式、0 條條件標記寫錯地方、68 行句中 REVISIT。照字面實作:既有那行變成「條件式回頭條件 0 條(由 lumos drift scan 評估);寫在不評估的地方 68 處」(語意是「條件標記寫錯位置」,現在摻進日期式的句中),下面再來一行「寫在句中的 REVISIT 68 處」。同一批位置被數兩次,上一行還講成條件標記的問題。既有測試若釘著那行的計數也會紅。
4. 佐證:file: `scripts/lumos:34804-34814`(`n_dead += len(dead)` 與那一行的組句);file: `scripts/lumos:31843-31863`(`dead` 三元組,無種類欄)。其他讀 `dead` 的只有這一處(`grep` `_probe_lines(`:31547、32302、32414、32501 都只取 `[0]`),所以改法是「不共用 `dead`」或「`dead` 加種類欄並讓既有行只數原種類」,spec 兩者都沒選。

**B2 一行裡第二個以後的 REVISIT 完全不被看見(只要行首已經是合法 REVISIT)**
severity: major
blocking: 是 — 這正是本案要消滅的「寫了卻沒人知道是死的」,而且挑中的判定條件(`_revisit_split` 回 None 才看)把它整類漏掉。
引句:「`_revisit_split` 判這行**不是** REVISIT 行(回 None),而且文字裡有 `REVISIT:` 後面」

1. 位置:做法 第 1 節第 1、2 點(只在 `_revisit_split` 回 None 時才呼叫 `_revisit_misplaced`)。
2. 問題:行首是合法 REVISIT 時 `_revisit_split` 回 `date`/`cond`/`bad`,不是 None,句中判定根本不執行;E5、`_probe_lines`、`_revisit_lines` 也只取每行一個。所以同一行後面的第二個、第三個 REVISIT(日期式或條件式)既不被評估、不被擋、Z 段也不列。
3. 例子(已實跑 `_revisit_split`):`REVISIT:2026-10-05 先做 A;REVISIT:[when-file:a.py][by:2026-12-31] 再做 B` → 回 `('date', '2026-10-05 先做 A;REVISIT:[when-file:a.py]…')`;第一層走 `kind == "date"` 分支直接 `return []`,提交放行;第二個條件式永遠不被 `drift scan` 或推送判定抽到(`_probe_lines` 只在 `kind == "cond"` 才抽)。摘要續行、列表項裡把兩個回頭條件寫成一行是很自然的寫法(「一行好幾個 REVISIT」)。
4. 佐證:file: `scripts/lumos:31700-31718`(`_revisit_split` 只解析第一個 `REVISIT:`);file: `scripts/lumos:27923-27934`(`date` 種類直接 `return []`);file: `scripts/lumos:31856-31860`(只有 `kind == "cond"` 才抽)。

**B3 「前面緊鄰的字元不是開引號」把範例句的誤擋留在大量存量上,而且多個 REVISIT: 同行時沒說看哪個**
severity: minor
blocking: 否 — 是誤擋與判定歧義,有單次跳過出口,不造成靜默漏網。
引句:「那個 `REVISIT:` 前面緊鄰的字元不是開引號(`「`、`『`、`"`、`“`、`'`)→ 真」

1. 位置:做法 第 1 節第 1 點、實務隱患 繞過。
2. 問題:(a) 「那個 `REVISIT:`」在一行有兩個以上時指誰沒定義:第一個被引號框住、第二個是真的(`寫法像「REVISIT:2026-10-05 x」,實際要 REVISIT:2026-12-01 y`)用 `re.search` 取第一個會放過;全部都要查才對。(b) 引號與標記之間有空白、粗體或星號(`「 REVISIT:…`、`「**REVISIT:…**」`)、或用括號/書名號(`(例:REVISIT:2026-10-05 x)`、`《…》`)包住的範例句都不算「緊鄰開引號」,會被擋。(c) 我用 `_search_visible_lines`+`_strip_inline_markup` 掃全部 docs 筆記(扣掉行首合法 REVISIT),剛好「前面是 `REVISIT:` 後接日期或 `[when-`」的非 REVISIT 行共 68 行,前一字元分布:`。` 40、`;` 13、空白 7、`,` 4、`~` 1、`「` 1、`:` 1、`★` 1。其中空白那 7 行裡有純在講規則的句子,例:全repo審視_計劃第 189 行「…改成獨立一行 REVISIT:2026-11-19(doctor 的到期掃描只認獨立 REVISIT 行…)」——是在談寫法、帶真日期、沒包反引號;這類以後被改寫(包含改名工具改連結)就被擋,出路只有「補反引號或引號」。
3. 影響:誤擋成本由作者承擔(spec 已選擇不追),但判定規則要把(a)寫清楚,否則兩種實作對同一行結果不同。
4. 佐證:`docs/lumos-toolchain-knowledge/Projects/全repo審視_計劃.md:189`(repo rw 內)。

**B4 句中判定認「YYYY-MM-DD 形狀」,行首判定認 `date.fromisoformat`,結案日期用哪個沒寫;三處形狀不一致**
severity: minor
blocking: 否 — 寬鬆方向只讓少數寫法漏過或放行,沒有新的靜音路徑超出 spec 已承認的天花板。
引句:「緊接 `YYYY-MM-DD` 形狀的日期或 `[when-`」

1. 位置:做法 第 1 節第 1 點;第 2 節第 1 點「先一個 `YYYY-MM-DD`,空白,再理由」。
2. 問題:行首 REVISIT 的日期靠 `date.fromisoformat`,Python 3.14 接受 `20261005` 與 `2026-W41-3`(已實跑:皆回合法日期),所以 `REVISIT:20261005 x` 是合法日期式、E5 會唸;但句中的 `x REVISIT:20261005 y` 不符「YYYY-MM-DD 形狀」,句中判定放過,又落進 B2 同款的靜默死條件。結案標記同理:若 `_revisit_closed` 用 `fromisoformat` 驗,`[closed:20261003 理由理由]` 合格;若用 `\d{4}-\d{2}-\d{2}` 形狀,`[closed:2026-13-45 理由理由]` 合格——spec 只說「日期壞」會錯,沒說用哪支驗。
3. 例子:兩種實作對 S8「結案標記日期不合格」的結果不同,測試與實作容易各寫一套。
4. 佐證:file: `scripts/lumos:31711-31718`(`fromisoformat`);實跑 `python3.14 -c "datetime.date.fromisoformat('20261003')"` 回 2026-10-03。

**B5 結案標記寫在 spec 規定以外的位置,第一層不報、也不生效,作者沒有回饋**
severity: minor
blocking: 否 — 失敗方向是「繼續唸」(安全側),E5 照唸會讓作者看到;只是第一層擋不到,違背本案「寫錯位置要讓人知道」的精神。
引句:「其他位置的 `[closed:…]` 不認,當普通文字」

1. 位置:做法 第 2 節第 1 點、第 4 點。
2. 問題:第 4 點只在 `_revisit_closed` 回 `errs` 時報;位置不對(放在待辦後面)、日期後兩個空白或 Tab、全形括號 `［closed:…］`、沒收 `]` 的 `[closed:2026-10-03 理由`,都是「根本沒認到」,不產生 `errs`,所以提交放行。
3. 例子(已實跑):`REVISIT:2026-10-05\t[closed:x]` → `_revisit_split` 回 `('bad', …)`,本來就報格式不合,OK;但 `REVISIT:2026-10-05  [closed:2026-10-03 已改用新閘道] x`(兩個空白)→ `('date', '2026-10-05  [closed:…] x')`,規格說「日期之後隔一個空白」,兩個空白算不算沒定;條件式寫成 `REVISIT:[when-file:a.py] 待辦 [closed:…]` 同樣放行但條件成立時推送照擋,作者才發現白寫。
4. 佐證:file: `scripts/lumos:31700-31718`、`:31804-31840`(`_probe_parse` 遇到不認得的標記就停、不報錯)。

**B6 工具代寫文字也走同一支第一層,spec 沒列這條平行路徑**
severity: minor
blocking: 否 — 屬遺漏的平行路徑,影響範圍小。
引句:「推送前與 CI 的 `note-shape --diff` 走同一支,一樣擋。」

1. 位置:做法 第 1 節第 2 點、實務隱患 相容。
2. 問題:`_ns_revisit_violations` 還有第三個呼叫端 `_drift_fix_shape_err`(`drift fix` 要寫進筆記的文字先過同一支判定,`visible` 固定 True)。新增的兩條規則會讓它也拒絕;spec 只談提交、推送、CI,沒說 `drift fix` 寫入的文字含 `REVISIT:日期` 的提法時怎麼辦,而改法提示是針對筆記寫作者寫的(「搬成獨立一行」),對工具使用者不通。
3. 佐證:file: `scripts/lumos:33358-33376`(`_drift_fix_shape_err`)、`:33507`(呼叫端)。

已讀,無 finding:範圍、依據、PRIOR-ART/RETIRE-IF、回退、天花板 1–4、審計修正紀錄(引用的 `[[…]]` 節點與 `t_graph_discipline_negation_revisit`、`scripts/graph-rename.sh`、`skills/lumos-project-notes/commands/03-寫回圖譜.md` 皆存在)。

極端輸入逐項答覆(其餘項目無 finding):
- 空行/只有標記沒有文字:`REVISIT:` 回 `bad`(已實跑),沿用既有格式不合規則;`REVISIT:2026-10-05 [closed:]`、`[closed:2026-10-03]` 走第 2 節第 1 點的 errs,無 finding。
- CRLF:`_revisit_split` 先 `strip()`,行尾 `\r` 不影響種類判定(已實跑 `'REVISIT:2026-10-05\r'` 回 `date`);結案值切法 `[^\]\n]*` 不跨行,行尾 `\r` 在 `]` 之後,無 finding。
- 全形符號:`REVISIT：`、`［closed:］` 屬 spec 天花板 1 承認的認不到;`line.strip()` 會剝全形空白與 NBSP,行首情況正常。僅 B5 的位置/括號類回饋缺口列為 finding。
- 列表/引用記號:`> > REVISIT:…`、`- - REVISIT:…` 回 None(只剝一層),會被當句中而擋,與改法字串「前面最多一層」一致,無 finding。
- 圍欄與行內程式碼交錯:呼叫端已排除圍欄;未閉合反引號後面的內容看不見,spec 天花板 5 只對 `[closed:` 承認,對句中 REVISIT 同樣是靜默漏網(同既有條件標記的行為),屬已知、不另列。
- 摘要續行:區塊照 `_notelines_regions`,續行與首行同為 summary 區,無 finding。
- 超長行:新增的正則皆線性(`REVISIT:` 後的空白吃一次、`[^\]\n]*` 無巢狀量詞),無 finding。
- 存量寫法:刪除線、加粗/星號、`KEY:REVISIT:` 皆判句中,存量量測的 68 行形狀分布見 B3;`~~…~~` 的改法字串已寫完整結案寫法,無 finding。

實務隱患逐類:
- 併發:無 — 純讀文字、不寫檔、不新增治理帳事件(spec 已述,與程式一致)。
- 效能:無 — 新增皆線性正則;doctor Z 段原本每篇跑一次 `_probe_lines`,多一次判定。順帶:`drift check` 路徑也會跑到 `_probe_lines` 的句中判定(取 `[0]` 時白跑),成本同量級,可忽略。
- 回滾:無 — 還原單一提交;寫過的 `[closed:]` 是普通文字。
- 誤擋與繞過:有 — B3(誤擋)、B2(漏網)、B5(寫錯無回饋)。
- 守衛面(關掉提醒的口子):`[closed:]` 靠日期與理由留痕,`abcd` 也算 4 字是 spec 已承認的天花板 3,無新 finding。

最嚴重 severity 是 major,blocking 共 2 條(B1、B2)。
