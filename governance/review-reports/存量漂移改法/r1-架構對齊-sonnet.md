severity: major

# 架構對齊審查(r1,sonnet 席)

三問結論先講:
1. 分層與依賴方向:`drift fix` 放在 drift 區、c1 往下呼叫 guard 區的 `_guard_settle_rewrite`,方向跟現況一致(drift 區已經在呼叫 `_guard_formal_line`、`_guard_planned_prose`,見 scripts/lumos:26132、26142),無跨層直呼 finding。
2. 命名與錯誤處理:大方向對(「擋下:」加 rc 2、`--dry-run`、鎖內原子寫),但有幾處跟鄰居不一致,見 F5–F10。
3. 第二種做法:有 4 處(F1–F4)。
4. 落點:見文末「落點」段。

## F1 新的修復帳沒有進簿記檔白名單,表態檔當年進了
severity: major
blocking: 是 — 不改,實作者會照字面新增一本帳卻漏掉白名單,之後修完筆記再提交帳時,代碼審留痕會被判失效、來源髒帳合併會被擋人
引句:「修復帳:每改一筆,往 `governance/drift-fixes.jsonl` 追加一行」
file: `scripts/lumos:21205`
1. 專案已有「工具自己寫的帳」的單一登記處 `_BOOKKEEPING_FILES`(scripts/lumos:21205–21211);表態檔 `governance/drift-acks.jsonl` 就是為了同一個理由被特地加進去(註解寫「跟判定檔一樣是人對發現的回應,不是程式改動」,出自存量漂移防線 [S3])。
2. 這份 spec 的修復帳是同一類東西(跟表態檔「同一種寫法」),但整份只講借 `_jsonl_append_verified`,沒有一處提到要登記進 `_BOOKKEEPING_FILES`。
3. 消費者不只一個:scripts/lumos:6542、17632–17633、28628–28629、28641、28728 都靠它判「這支檔不算程式改動」。漏掉的後果=`drift fix` 之後提交帳檔,會被當成一支程式檔改動(代碼審留痕失效);pull 來源只髒這本帳時不走聯集合併。
4. 這是「同一件事(簿記帳)兩處各登記一份、沒有機械守一致」的形狀;白名單本身就是為了避免它而存在。〈條款〉[S9] 也沒有任何一條測試釘住「新帳在白名單裡」。

## F2 c4 的「只換一項」說要新寫寫入路徑,但既有的 `_set_conditions_locked` 已經處理三種寫法
severity: major
blocking: 是 — 不改,實作者會在 `drift fix` 裡再寫一套 valid_under 欄位改寫(單行/清單/多行區塊),跟 `set` 那套並存,之後兩套各自漂移
引句:「清單只換含那三個詞的那一項(有好幾項含就擋下,要人指定),單行與多行區塊整欄換」
file: `scripts/lumos:14863`
1. spec 同一段自己承認「現有寫入路徑 `_set_conditions_locked` 只會整欄換,『只換一項』要新寫」。但「新」的只有「挑出哪一項、算出新的整欄值」;把整欄值寫回去,`_set_conditions_locked(env, rel, "valid_under", 新的項目清單)` 已經一次處理單行、清單、空的、多行區塊四種寫法(scripts/lumos:14863–14895,`fm_structure` 加 `atomic_write_verify`,COND_KEYS 含 valid_under,scripts/lumos:14356)。
2. 照 spec 字面「要新寫」實作,就會多出第二個改 frontmatter 條件欄的寫入者;該函式的 docstring 就是為了收斂「四種寫法並存」才立的。
3. 讀的一側也有既有做法:`_conds`(scripts/lumos:13524)把多行區塊按換行拆成一條一條。spec 說「多行區塊整欄換」,但按 `_conds` 的語意,區塊裡每一行是一項、跟「清單」沒有分別;spec 的三分法(單行/清單/區塊)跟專案既有的讀法對不上。⚠ 我沒法判定哪一邊該改,但兩邊只能留一種。
4. 寫入端還要注意 `_set_conditions_locked` 自己會印「✓ set …」並擋含換行的值——spec 沒說 `--dry-run`、修復帳、「寫完再跑同一支判定」怎麼跟它接;要嘛包一層要嘛把它拆成「算值」與「寫」,spec 沒選。

## F3 git 呼叫做法:`git log -S` 說「本檔沒有先例」是錯的,c4 的證據①也已有現成函式
severity: major
blocking: 是 — 不改,實作者會為 c1 日期與 c4 證據各自再刻一套 subprocess 呼叫,而這支檔已經有三種 git 呼叫寫法,drift 區只用其中一種
引句:「`git log -S` 本檔沒有先例,新寫;repo 是 shallow(`_git_is_shallow`)或推不出來就擋下、要人給 `--date`」
file: `scripts/lumos:23860`
1. 先例存在:`_nodehome_golive`(scripts/lumos:23856–23864)就是 `_nodehome_git(repo_root, "log", "--reverse", "--format=%H", f"-S{mark}", tip, "--", hook)`,取最舊一筆。spec 的「取 -S 列出的提交(舊到新)」是同一個形狀。
2. drift 區的 git 都走 `_nodehome_git`、`_nodehome_list`、`_nodehome_cat_blobs`(有逾時、失敗回 None、位元組無損解碼;drift 區 25970–27520 唯一的裸 subprocess 是算空樹那一處)。spec〈做法〉第 2 節「逐一讀那個提交的家節點」沒點名這些,「新寫」二字會把實作者往裸 `subprocess.run` 帶。
3. c4 證據①「第一次被提交的提交編號與日期(`git log --diff-filter=A`)」:`_plan_first_commit`(scripts/lumos:5843–5851)已經是「某檔第一次進 git 歷史的提交」,註解還寫了為什麼不能信 frontmatter 的 created。spec 沒提它,又是同功能第二支。
4. 結論:spec 要改成「用 `_nodehome_git` 那一組、沿用 `_nodehome_golive` 的取最舊寫法、c4 證據①借 `_plan_first_commit`」,並刪掉「沒有先例」的說法(這句本身是關於現況的錯誤宣稱,會讓下一個讀者以為不用找)。

## F4 〈做法〉第 5 節的 Issue 結案列出,沒有指定用 `_revisit_split`,而現行決定是全庫只有一支「這行是不是 REVISIT」的判定
severity: major
blocking: 是 — 不改,實作者會為「列出還留著的回頭條件」自己寫一個 REVISIT 行正則,變成第四處各自判(E5、筆記形狀擋、筆記內容審已共用一支)
引句:「改完之後,這篇正文與摘要裡還有日期式或條件式回頭條件就逐行列出(行號加原文)」
file: `scripts/lumos:26331`
1. 既有決定(存量漂移防線 [S11],寫在 Systems/存量漂移守衛 的〈條件式回頭條件〉段):判定只有 `_revisit_split` 一支,三處餵的還是同一版文字(`_strip_inline_markup` 剝過);乙代碼審 r1 就是因為 E5 餵的東西不同而出過事(scripts/lumos:2221–2224 的註解)。
2. 這份 spec 在 E5 標記那一節(第 5 節第一點)是改 E5 現成迴圈,天然沿用;但第二點(`lumos set` 列出)是全新的一條掃描路徑,而且 spec 用「日期式或條件式」這種自己的分類語言描述,沒有寫「用 `_revisit_split` 加 `_search_visible_lines`(跳過圍欄與行內程式碼)」。字面實作最省事的做法就是自己 grep `REVISIT:`。
3. 〈條款〉[S7] 也只驗「列出它還留著的回頭條件行」,不驗跟 E5 判定一致(例:行內程式碼裡的範例 REVISIT、表格行不該列)。
4. 要補的是一句「同一支判定、同一版輸入」,並在 [S7] 測試加一個 E5 不列的行也不列的案例。

## F5 Issue 結案列出要「新加 Issue 的分支」進 `_drift_plan_followups`,但那支函式的合約是「計劃連著哪些別的筆記」
severity: minor
blocking: 否 — 結構方向對(接在 main 分派處、只印不擋),但放進去會讓 exam 與輸出標題語意錯位,改了也只是換個函式名
引句:「`_drift_plan_followups` 對非計劃回空,所以要新加 Issue 的分支」
file: `scripts/lumos:26149`
1. `_drift_plan_followups` 回 `[(種類, 別篇路徑, 說明)]`,語意是「這份計劃收尾了,連著它的別篇」;`_drift_print_followups`(scripts/lumos:26193–26200)印的標題就是「連帶待辦(這份計劃收尾了,下面 N 篇連著它…)」。
2. Issue 的待辦是「同一篇裡的哪幾行」,項目形狀(行號加原文)與「別篇路徑」不同,標題文字也不成立。
3. 另有第二個呼叫端:drift exam 的 status_replay 用同一支(scripts/lumos:27497),它只餵計劃路徑,加 Issue 分支不會壞,但把不同語意塞進同名函式,之後改 exam 的人要猜。
4. 鄰居的做法是「每種連帶待辦一支函式、main 分派處各自呼叫」(`_drift_print_followups` 就是那一個);對齊的寫法是另立同層一支(例如列 Issue 回頭條件的函式),在 `lumos set` 分派處並列呼叫。⚠ 專案沒有兩種語意共用一支的先例,也沒有反例,我只能標這個不一致。

## F6 c3 的合法狀態清單寫死一份,而「類型狀態表」是 `cmd_lint` 內的區域變數,spec 沒說怎麼共用
severity: minor
blocking: 否 — 結構對(只收四個值),但會多出一份無機械守一致的狀態表
引句:「`--status pass|stale|superseded|abandoned`(必填,驗證紀錄的合法狀態扣掉 pending,見 `lumos lint` 的類型狀態表)」
file: `scripts/lumos:5244`
1. 「類型狀態表」`_STATUS_ENUM` 定義在 `cmd_lint` 函式裡面(scripts/lumos:5136 起、5244 行縮排 4 格),不是模組層常數,drift 區 import 不到。
2. spec 同一句既寫死四個值、又說「見 lint 的表」,實作者只能抄一份;lint 之後加狀態,c3 不會跟上,也沒有測試守。
3. 對齊做法二選一:把表提到模組層再 `- {"pending"}`,或在 [S4] 測試加「c3 允許集合 = lint 表的 verification 集合扣 pending」的斷言。spec 兩個都沒寫。

## F7 修復帳的欄位與事件慣例沒跟表態檔對齊
severity: minor
blocking: 否 — 帳能寫、能讀回,只是命名與治理事件跟鄰居(`drift ack`)不一致,補幾句就對齊
引句:「借 `_jsonl_append_verified`,跟表態檔同一種寫法):id、路徑、當時行號、種類、改前那幾行、改後那幾行、日期」
file: `scripts/lumos:27128`
1. `cmd_drift_ack`(scripts/lumos:27101–27146)的做法:路徑常數 `_DRIFT_ACKS`(scripts/lumos:25983)、id 用 `"DACK-" + secrets.token_hex(4)`、鍵欄位傳 `"id"`、寫完呼叫 `_gate_event_or_warn(root, "drift-check", "acked", …)` 進治理帳、印「表態記下了」與要不要提交的提示。
2. spec 只寫「id」,沒有前綴、沒有 `_DRIFT_FIXES` 常數、沒有治理事件。CLAUDE.md 也要求指令結果進治理帳;`drift fix` 是會改筆記內容的寫入指令,比 `drift ack` 更該留事件,卻沒提。
3. `guard settle` 等鄰居沒有 `_gate_event_or_warn`(grep 看不到),所以「不留事件」不算錯,只是跟 `drift` 家族最近的鄰居不一致。⚠ 鄰居本身分兩派。
4. 建議寫進 spec:常數名、id 前綴(如 DFIX-)、是否記 gate 事件、提示要不要提交帳檔(與 F1 相連)。

## F8 〈實務隱患〉還留著 fixed.txt,跟〈做法〉的修復帳是兩個「找回來」的來源
severity: minor
blocking: 否 — 純文件內部不一致,實作不受影響,但讀者會以為還有第二本帳
引句:「不可逆(碰到,可還原):改的是版控裡的筆記,git 還原得回來;照 fixed.txt 可整批找出」
1. 〈做法〉第 1 節明講「不靠人記得留 fixed.txt」,改用 `governance/drift-fixes.jsonl`;〈回退〉節也只講修復帳。整份 spec 裡 fixed.txt 沒有定義,程式碼(`grep fixed.txt scripts/lumos`)也沒有這支檔。
2. 應改成照修復帳找。這條是 spec 內部不一致,程式碼無對應。

## F9 c2/c3 表態的 `related` 路徑慣例跟同一筆紀錄的 `path` 不一樣,而且沒說 ack 怎麼拿到「當時那筆發現」
severity: minor
blocking: 否 — 比對端(發現物的 `related` 本來就是圖譜內相對路徑)能對上,但同一筆紀錄兩種路徑寫法、寫入端取值來源沒寫清
引句:「跟發現物一樣存圖譜內相對路徑,不加 vault 前綴」
file: `scripts/lumos:27124`
1. 表態紀錄的 `path` 存 `f"{vault_rel}/{rel}"`(帶 vault 前綴;scripts/lumos:27124–27127),`_drift_split_acked` 比對時自己補前綴(scripts/lumos:27079–27086)。同一筆紀錄的 `related` 卻不帶前綴,讀的人要記兩種寫法。
2. `cmd_drift_ack(env, node, line, kind, reason)` 現在完全不查那一行是不是發現,只驗行存在且非空(scripts/lumos:27101–27120)。要記 `related` 就得在 ack 裡跑 `_drift_state_findings` 找同行的發現;spec 沒說找不到(例如 kind 給 c2 但那行現在不是 c2)時怎麼辦:是照舊寫沒有 `related` 的舊式表態,還是擋下。這個選擇會決定新寫的表態能不能被放寬比對放行(〈實務隱患〉自我治理那一條靠「新寫的一律帶清單」)。
3. 對齊建議:`related` 也存帶 vault 前綴的路徑(比對時同樣用 `pre +`),或在 spec 明寫為什麼這欄例外;並寫明「找不到對應發現時擋下」。

## F10 `drift fix` 的寫入失敗處理沒寫,鄰居 settle 有
severity: minor
blocking: 否 — 只是錯誤輸出方式,實作者照 `_guard_settle_record` 的樣子補即可
引句:「寫入一律拿筆記庫寫入鎖(`_vault_write_lock`,可重入)、用 `atomic_write_verify` 寫」
file: `scripts/lumos:12310`
1. `atomic_write_verify` 失敗丟 `ValueError`/`RuntimeError`。`_guard_settle_record`(scripts/lumos:12296–12318)接住後印「擋下:…寫不進去」加補救指令、回 2;`set` 的主分派處也接(scripts/lumos:37046 附近)。drift 分派處(scripts/lumos:37030 起)沒有任何 try/except。
2. spec 的 [S9] 只驗成功路徑(寫完重讀確認那筆發現不在),沒寫「自驗失敗或重跑判定仍在時」印什麼、rc 是多少、修復帳寫不寫。照字面實作,失敗會直接噴例外堆疊。
3. 對齊:失敗一律「擋下:…」加 rc 2、不寫帳(帳只記真的成功的);重跑判定仍在時同樣擋下並點名是哪一筆。

## 已看,無 finding 的部分
- 分層與依賴方向(第 1 問):「c1 用 `_guard_settle_rewrite` 與 `_guard_formal_line`」——drift 區往 guard 區呼叫本來就有(scripts/lumos:26132、26142),`guard settle` 與 `drift fix` 共用同一支也沒有 guard 反過來呼叫 drift。引句:「用 `_guard_settle_rewrite`(回 (改寫後的行, 找不到的句型))改整篇」
- 寫入鎖與原子寫(第 2 問):「拿筆記庫寫入鎖、`atomic_write_verify`、`_jsonl_append_verified`」——跟 `cmd_drift_ack`(27139–27141)、`cmd_guard_settle`(12204)一致。引句:「先用跟 `drift scan` 同一支判定(`_drift_state_findings`,c1 在 `_drift_guard_findings`)確認」
- `--dry-run` 命名:專案已有多支用 `--dry-run`(scripts/lumos:35872、35879、36298),一致。
- `--kind` 沿用 `_DRIFT_KINDS`(scripts/lumos:36536):與 `drift ack` 一致。
- 〈做法〉第 6 節「不能借 `_drift_old_reason`」:已核對它確實在原路徑還在時就跳過(scripts/lumos:27089–27098),spec 的判斷正確。
- 「已收尾」兩個集合:spec 已明講 `_DRIFT_CLOSED`(scripts/lumos:25974)與 `QUERY_CLOSED_STATUSES`(scripts/lumos:13702)不同,不混用,沒有第二種做法。

## 落點(第 4 問)
- lands_in 列 Systems/存量漂移守衛 與 Systems/guard-kill:`guard settle` 改動落 guard-kill、drift 家族落存量漂移守衛,方向合理;E5 標記與 `set` 的連帶待辦上一輪(存量漂移防線 [S6])也是落在存量漂移守衛,對齊。
- ⚠ 兩處判不準:(a) c4 的 `--replace` 寫的是 `valid_under`,該欄的寫入合約在 Systems/lumos-cli-write(WHY 2026-09-26 那條)——若 F2 改成呼叫 `_set_conditions_locked`,那篇要加一句「drift fix c4 也走它」,現在 lands_in 沒有它;(b) doctor E5 沒有專屬的家節點(只在存量漂移守衛 第 57 行附近被提到),專案沒有既有做法可對。
- 新開一篇不需要:改動都在既有家的職責內。

不對齊共 10 條,其中判為第二種做法或漏合約的有 4 條,blocking 共 4 條;最嚴重等級:高。
