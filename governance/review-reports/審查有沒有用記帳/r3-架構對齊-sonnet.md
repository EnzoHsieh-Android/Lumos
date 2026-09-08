severity: major

LUMOS-SPEC: docs/lumos-toolchain-knowledge/Projects/審查有沒有用記帳_計劃.md

# r3 架構對齊(sonnet)——審查有沒有用記帳_計劃(上限輪,驗收 r2 major 折入)

被審(凍結):`governance/review-reports/審查有沒有用記帳/r3-snapshot.md`。方法:讀 `git show HEAD:scripts/lumos` 現況(存 `/tmp/lumos_head.py` 逐行核對),不找 bug、不評風格,只判折入後的設計跟專案既有做法一不一致。

## 問一:拒收偵測與檔案掃描邊界(對照①②)

[S1] 這輪新加兩塊直接動到「哪些字看得見/怎麼判斷格式壞」的掃描邏輯:一支「拒收偵測正則」(放在 `_report_severities` 旁,只用來拒不用來數),和一條「檔首規則」(跳過開頭的 HTML 註解與空行,取第一個非空行當檔級 severity)。這兩塊要分開判——一塊有先例撐得住,一塊正對著專案明文否決過的做法。

**①拒收偵測正則**:`_report_severities` 自己 docstring 只稱自己是「★單一 parse 實作★」(`scripts/lumos:4816`);真正「不得自寫第二份」的明文鐵則寫在另一篇既有計劃筆記——「嚴重度 parse 必須複用 _report_severities...不得自寫第二份★(自寫會出現「正規化器認得、寫側不認」的漂移,家裡為此立過鐵則)」(`docs/lumos-toolchain-knowledge/Projects/全repo審視_計劃.md:390`)。這條鐵則鎖的是「解析」——把文字變成一個 severity 值;[S1] 的拒收正則明寫「只用來拒、不用來數」,不產出任何 severity 值,不是第二份 parser。專案已經有這個形狀的先例:`_quote_rows` 除了抽引句的主正則(`scripts/lumos:13433`-`13435`),另用 `n_markers` 這支伴生正則(`scripts/lumos:13438`)專抓「有引句標籤開頭、卻抽不出合法引句」的殘缺格式,只用來標 `malformed: True`(`scripts/lumos:13454`),不進正式抽取結果——跟 [S1]「伴生正則只拒不數」是同一種分工。判:已對齊。

**②檔首跳過 HTML 註解**:專案對「偵測 HTML 註解」這件事有三筆獨立、帶著真實事故的明文否決,不是沒交代過的空白地帶。`_visible_lines`(全檔唯一的 fence 判定)原始碼旁註:「★不偵測 HTML 註解★(-b r3 單reviewer 兩條 blocker:`-->  <!--` 先關再開會把後面整份藏掉;曾短暫加過,同日拿掉)」(`scripts/lumos:2530`);它的行內層級搭檔 `_strip_inline_markup` 同款重申:「★不碰 HTML 註解★:-b r3 兩席證明「偵測註解」本身就是洞(先關再開、註解正則不認反引號邊界),註解裡的 [SN] 一律走「認不得→擋」」(`scripts/lumos:170`);`clause_bindings` 第三次重申「HTML 註解不特別處理」(`scripts/lumos:4089`)。三處都是同一個決定:偵測註解本身會製造新的靜默吃字洞,寧可讓看不懂的內容直接被擋,不特別繞過。這正好對照題目點名的 `_intake_declared`——它「先剝 fenced 圍欄再掃」(`scripts/lumos:4790`-`4791`),但同樣沒有、也從沒有處理過 HTML 註解;全檔搜尋確認沒有任何既有函式做「跳過開頭 HTML 註解」這件事。[S1] 的「檔首(跳過開頭的 HTML 註解與空行)」是專案裡第一支要去偵測 HTML 註解邊界的新程式碼,而且正好是曾經因為這個形狀出過兩條 blocker、當天就被拔掉的那個做法。判:仍不對齊——量級是「重犯已明文否決的第二種做法」,不是命名或錯誤處理細節。

severity: clean
blocking: 否
引句:「放在 `_report_severities` 旁,只用來拒、不用來數」
file: `scripts/lumos:4816`(`_report_severities` docstring「★單一 parse 實作★」)、`docs/lumos-toolchain-knowledge/Projects/全repo審視_計劃.md:390`(「嚴重度 parse 必須複用 _report_severities...不得自寫第二份」鐵則鎖的是解析,不是拒收)
file: `scripts/lumos:13433`-`13435`、`:13438`、`:13454`(`_quote_rows` 的 `n_markers` 伴生正則:只標 malformed、不進抽取結果——「拒不數」的既有先例)

severity: major
blocking: 是
引句:「①檔首(跳過開頭的 HTML 註解與空行)第一個非空行必須是檔級」
file: `scripts/lumos:2530`(`_visible_lines`「★不偵測 HTML 註解★」+ 兩條 blocker 事故記錄)
file: `scripts/lumos:170`(`_strip_inline_markup`「★不碰 HTML 註解★」,同一決定的第二處)、`scripts/lumos:4089`(`clause_bindings`「HTML 註解不特別處理」,第三處)
file: `scripts/lumos:4790`-`4791`(`_intake_declared` 只剝 fenced 圍欄,同樣不處理 HTML 註解——題目引的對照組本身也沒有這個做法)

## 問二:refuted id 對 intake 的整字比對(前輪 major 折入驗收,對照③)

r2 這一席的 major 是「refuted id 對 intake 驗是子字串比對(`a1` 會被 `a10` 命中),沒有沿用專案唯一的文字錨定實作 `_quote_norm`/`_QUOTE_MIN_NORM_LEN`」。這輪折入後的寫法是「前後不是英數」的整字比對,再加上要求同一列同時出現 `HIT`/`MISS` 字樣。

先核對題目給的對照物:逐字讀 `SYMBOL_RE`(`scripts/lumos:2320`)和 `_CLAUSE_LISTLIKE_RE`(`scripts/lumos:4077`)——兩支正則其實都沒有用 `\b`;`SYMBOL_RE` 靠冒號緊跟關鍵字後面天然排除「KEYS:」這種前綴誤判,`_CLAUSE_LISTLIKE_RE` 靠 `[S(\d+)\]` 的方括號邊界。但「整字比對(前後不是英數)」這個慣例本身在專案裡確實存在,只是先例在別的地方:`scripts/lumos:489`、`:8650`、`:15957`、`:15981`-`15982` 都是 `re.compile(r"\b" + re.escape(x) + r"\b", re.ASCII)` 這種寫法,而且專案自己記過為什麼一定要帶 `re.ASCII`——「re.ASCII:方法名是 ASCII 識別字;否則 Python \b 視 CJK 為 \w,「守衛Pay跑」(中文緊貼方法名無空格)→ \b 不成立 → 漏護(under-protection,更危險)」(`scripts/lumos:11539`-`11541`)。這正是關鍵:Python 預設(非 ASCII)模式下 `\b` 把 CJK 字元也算進 `\w`,ASCII id 緊貼中文散文時邊界根本不會觸發,反而漏判。[S2] 的措辭是「前後不是英數」,不是空泛的「word boundary」——這個講法直接對應 `(?<![0-9A-Za-z])id(?![0-9A-Za-z])` 這種顯式排除英數字元的寫法,天生不會踩到 `\b` 那個 CJK 鄰接漏判的坑,比專案既有那幾處單純套 `\b`+`re.ASCII` 還更貼著問題本身。r2 抓到的具體症狀(`a1` 被 `a10` 命中)是「id 右邊緊接數字」,整字比對直接堵死這條路。判:r2 這條 major 已對齊——不只折入,寫法比既有先例更精準地避開了同一批既有先例才踩過的鄰接漏判陷阱。

`HIT`/`MISS` 也不是這輪發明的新詞彙:它是 `rN-intake.md` 機械重現表既有的欄位慣例,`docs/lumos-toolchain-knowledge/Systems/design-loop.md:38` 記著「編排者機械重現留痕 rN-intake.md(命令+輸出+HIT/MISS,MISS=佐證不採信退回該席)」,`docs/lumos-toolchain-knowledge/Projects/迴圈摩擦三修_計劃.md:29` 是這個格式的原始決策記錄。[S2] 只是要求「駁回 id 要對到這張既有表格的那一列」,沒有另開一套新的重現記錄格式。

severity: clean
blocking: 否
引句:「前後不是英數:`a1` 不因 `a10` 命中」
file: `scripts/lumos:11539`-`11541`(既有 `\b`+`re.ASCII` 整字比對慣例,附「中文緊貼方法名時 \b 失效漏命中」的明文教訓——[S2]「前後不是英數」的措辭正是這個教訓的顯式修法)
file: `scripts/lumos:489`、`:8650`、`:15957`、`:15981`-`15982`(同款 `\b`+`re.ASCII` 整字比對先例)
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:38`(`rN-intake.md` 的 `HIT`/`MISS` 欄位是既有格式,非新造)

## 問三:讀側推導值印法(對照④)

[S3] 要印「存活多於席位報的 S 條」,算法是 `S = max(0, M+R−N)`——這是推導值(從三個欄位算出來的),不是直接讀帳面上某個欄位。題目問 `_render_gov_stats` 有沒有先例,還是一律只印原始計數。

讀完整支函式(`scripts/lumos:4345`-`4490`),docstring 自稱「純數字報表」(`scripts/lumos:4346`),但函式本體其實已經在印推導值,不是只印原始計數:finding_kinds 那段印「程式缺陷 {fk['code']}({fk['code']/tot:.0%})...」(`scripts/lumos:4401`),design-loop 結案那段印「人裁放行率 {capped / len(by):.0%}」(`scripts/lumos:4430`)——都是拿原始計數做除法算出比率再印出來。所以「推導值可以印」這件事本身在 `_render_gov_stats` 裡已有先例,不是 [S3] 第一個這樣做。

差別在於 [S3] 自己明文要求這段新增內容「不印比率」(段首固定第二句:「這段內部也不印比率、別自己算 Σ折/Σ報 當『審查有用率』」),而 `S = max(0, M+R−N)` 是減法加下限夾,不是除法比率,兩者不衝突——[S3] 避開的是「比率」這個特定形狀,不是「所有推導值」。`max(0, X−Y)`「算出還缺/還剩多少」的夾法本身在專案別處也是既有慣例:impact 篩選裡「補 need=max(0, N−count) 席」(`scripts/lumos:18525`,`18532` 是實作)、另一處直接寫明「同 _rescue_n 的 max(0,…) 慣例;負切片語意是「砍尾」不是上限」(`scripts/lumos:18547`)。判:已對齊——`_render_gov_stats` 本身就印推導值(比率),`S` 這種減法夾值的形狀也在專案別處有先例,[S3] 只是換了個推導公式,沒有走出「這張報表只准印原始計數」的界線(因為那條界線在現有碼裡本來就不存在)。

severity: clean
blocking: 否
引句:「存活多於席位報的 S 條(編排者自找或漏併)」
file: `scripts/lumos:4401`、`:4430`(`_render_gov_stats` 既有的比率型推導值印法)
file: `scripts/lumos:18525`、`:18532`、`:18547`(`max(0, N−count)` 減法夾值的既有慣例,`S` 的算法同一形狀)

不對齊共 1 條,其中 major 1 條
