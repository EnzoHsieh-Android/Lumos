---
type: project
status: todo
created: 2026-10-15
updated: 2026-10-15
tags:
  - type/project
  - status/todo
  - scope/guards-gates
lands_in:
  - Systems/lumos-cli-write
  - Systems/lumos-cli-read
  - Systems/筆記內容閘
  - Systems/lumos-refcheck
  - Systems/每支檔有家
  - Systems/規格閘
  - Systems/test-profile-multiplatform
related:
  - "[[Projects/改摘要單行的指令_計劃]]"
  - "[[Projects/雙向門放行_計劃]]"
  - "[[Projects/回頭條件寫下時就成立_計劃]]"
  - "[[Projects/回頭條件消失式與生來成立_計劃]]"
  - "[[Projects/否定現況句配回頭條件_計劃]]"
  - "[[Projects/示範回饋小修_計劃]]"
decisions:
  - content: 加 lumos summary-add <節點> "<一行>" 新增摘要行,寫入前跑提交時同一套筆記形狀與格子檢查;推翻 Projects/改摘要單行的指令_計劃 的「不做插行」,紀律範本與 skill 的「開頭欄位用指令改」跟著列出新指令
    id: d1
    context: web 示範的前端與後端代理都要往摘要加 RULE 行,只能手改開頭欄位,跟紀律「開頭欄位用指令改」打架;2026-10-06 那份因 rtb 那輪插行 0 次而不做
    why_chosen: 使用者 2026-10-15 裁定;兩個代理在同一次示範各踩一次,原本「要時再加」的條件已出現;寫前跑同一套形狀檢查,不會多一個繞過提交檢查的入口
    decided: 2026-10-15
    valid: true
  - content: 規格閘實作後才跑走輕量版:已有條款指紋相同的風險低留痕就不用重跑;沒有就照舊擋並在訊息裡教人把實作檔暫時換回實作前的版本、在同一個工作目錄補跑;不做 --red-at 暫時工作樹
    id: d2
    context: Q1:實作後才跑規格閘必擋,示範代理把新檔搬走跑紅再搬回;候選是工具內建 --red-at 在實作前的提交開暫時工作樹跑紅,或只改訊息教手動補跑
    why_chosen: 編排者 2026-10-15 裁定:使用者說先不用過度設計,暫時工作樹是新的複雜度與新的出錯點(中斷殘留、測試輔助檔要不要一起蓋);手動補跑保留同一份紅的證據、留痕照一般流程寫進目前的帳
    decided: 2026-10-15
    valid: true
pending_questions:
  - id: Q1
    text: 規格閘實作後才跑:要做 --red-at(在實作前的提交開暫時工作樹、蓋上現在的測試檔跑紅),還是只做「已有留痕不用重跑」加訊息教人手動在實作前版本跑?
    class: 範圍
    stage: 架構
    status: 已決
    decision: "#d2"
---
# 筆記指令健檢與規格閘小修_計劃

白話:一次前端示範(order-web)與一次後端補件,踩到筆記指令、健檢與規格閘的一串小毛病——摘要不能加一行只好手改開頭欄位、`set` 說明沒列欄位、`lands_in` 寫錯照收、條件句被當成會過期的現況句、寫下就成立的回頭條件到推送才被擋、計劃裡要新建的路徑被當成不存在、`home check` 不帶參數就擋、實作後才跑規格閘會擋、乾淨 clone 推送時規格閘留痕不見而靜默放行。這份把 F、G、H 三組 17 個編號收成 11 節,能用一條規則收的就不逐點補,拆成 7 個小提交。

依據:2026-10-15 一次 React 前端示範(order-web)與一次後端補件時記下的缺口清單(編排者的比對表,不在圖譜裡;編號只是那份清單的代號,意思逐一寫在下面〈名詞〉),每條在 2026-10-15 對 `scripts/lumos` 現況重讀過(以程式碼為準);使用者 2026-10-15 裁定加新增摘要行的指令(決策 d1,推翻 [[Projects/改摘要單行的指令_計劃]] 的「不做插行」)。

名詞:
- 缺口編號(本篇各節標題括號裡的代號):F8、B6、W8=摘要不能用指令新增一行;B7=`set` 說明沒列可改欄位;F14=`append` 的落點寫成 `[[連結]]` 照收;F17、W9=否定現況句提醒把畫面狀態與時序句當成會過期的現況;F29=寫下就成立的回頭條件到推送才被擋;F6=寫錯格式的「已排除」行 lint 不唸;F9=計劃裡要新建的路徑被判不存在;W5=健檢路徑檢查把「檔名加參數」整串當檔名、被忽略的執行期檔判不存在;B8=只改歸屬或負責範圍仍被說「家沒動」;B9=`home check` 不帶參數就擋;W6=健檢「每支檔有家」看不到還沒提交的節點;B1、B11=實作後才跑規格閘會擋、健檢的規格閘欄一直顯示紅;B2=計劃改成 done 後推送閘不再跑它的測試;B3=規格閘留痕在乾淨 clone 不見;W10=規格閘同一句警告印三次;F15=條款句式兩道閘判法疑似不一致。
- 帳:**審查帳**=`docs/.canary-log.jsonl`(審查席與規格閘留痕;消費專案裡 `lumos init` 在 docs 底下產的 .gitignore 把它當**本機帳**忽略、不進版控,工具鏈自己的 repo 有進版控);**治理帳**=`docs/.governance-log.jsonl`(進版控,CI 唯一讀得到的帳,代碼審通過的留痕在這裡)。
- 健檢段名:`lumos doctor` 輸出的段落代號——P 段=筆記提到的程式檔路徑還在不在;S8=每支程式檔有沒有家;S9=節點有沒有用反引號寫別人的檔;S10=管很多檔的節點有沒有寫負責範圍;S14=風險低計劃放行統計。
- 每支檔有家的條款:「S13、S13b」指 [[Projects/每支檔有家_計劃]] 的驗收條款(寫回落點要是改動檔的家、有寫回時每支改動檔都要有家),不是本篇的條款,也不是健檢段名。

PRIOR-ART: 全部借 repo 裡既有的零件,不新建機制:摘要定位與寫入照 `summary-line`(`_summary_line_hits`、`_summary_line_pick_err`、`atomic_write_verify`、寫入鎖);寫前形狀檢查照 `drift fix` 已有的 `_drift_fix_shape_err`(工具要寫的自由文字先跑筆記形狀擋同一支判定)與格子的 `_ns_slot_line_problems`;落點格式照 `_lands_in_bad`;已排除行照 `_excluded_line`(規格閘判定與證明共用的那一支);回頭條件文法照 `_probe_parse`;推送閘讀的留痕放進版控的治理帳,照代碼審留痕的先例(治理帳是 CI 唯一讀得到的帳,[[Projects/治理帳例行紀錄分流_計劃]] 的裁定);被忽略的執行期檔照 `git check-ignore --stdin`。
RETIRE-IF: summary-add 上線 8 週,各專案治理帳與 git 歷史裡手改摘要區的次數沒有下降(還是手改)就撤指令;否定現況句 v4 規則在第 8 週人工抽樣的準度比 v3 低就退回 v3;其他各節是錯誤訊息與判定修正,撤法是還原那個提交。

## 範圍與提交拆法

| 提交 | 編號 | 節 | 落點 |
|---|---|---|---|
| ① feat: 摘要可以用指令新增一行 | F8、B6、W8 | 1 | Systems/lumos-cli-write |
| ② fix: set 說明列出可改欄位、append 的落點寫成連結時自動改純字串 | B7、F14 | 2、3 | Systems/lumos-cli-write |
| ③ fix: 否定現況句提醒不再唸條件與時序子句 | F17、W9 | 4 | Systems/筆記內容閘 |
| ④ feat: lint 先唸寫下就成立的回頭條件與寫錯格式的已排除行 | F29、F6 | 5、6 | Systems/lumos-cli-read |
| ⑤ fix: 路徑檢查認得要新建的路徑、指令參數與被忽略的執行期檔 | F9、W5 | 7、8 | Systems/lumos-refcheck、Systems/lumos-cli-read |
| ⑥ fix: 每支檔有家的提醒與預設範圍 | B8、B9、W6 | 9 | Systems/每支檔有家、Systems/筆記內容閘 |
| ⑦ fix: 規格閘實作後重跑、乾淨 clone 推送與健檢欄位 | B1、B11、B2、B3、W10 | 10 | Systems/規格閘、Systems/test-profile-multiplatform |
| 不做 | F15 | 11 | — |

各提交互不依賴,可以分開推;⑦ 碰推送閘,代碼審會判 high,其他多半 standard。

## 做法

### 1. 新增摘要行的指令(F8、B6、W8)

現況:`summary-line` 只能換或刪一行裡的一段,新片段不准含換行;新開節點的骨架只有四個空前綴行,要多寫幾條 RULE 只能手改開頭欄位,跟紀律「開頭欄位用指令改」打架。2026-10-06 那份計劃因「rtb 那輪插行 0 次」不做插行;這次示範兩個代理都踩到,使用者裁定加(d1)。

做法:新子命令 `lumos summary-add <節點> "<一行>" [--after "<片段>"] [--nth N] [--dry-run]`,函式 `cmd_summary_add`,跟 `cmd_summary_line` 同一支檔、同一把寫入鎖。

1. 輸入:新行去頭尾空白後不得是空的、不得含 `str.splitlines` 認得的換行類字元(同 summary-line 那條檢查,抽成一支共用);摘要寫成單行值 `summary: 一句`、或這篇沒有摘要欄 → 擋(rc2),講要先改成區塊寫法(同 summary-line 不支援單行值)。
2. 去重:摘要區裡已有一行去頭尾空白後跟新行一字不差 → 印「已經有」、rc0、檔案不動(同 append 的去重語意)。
3. 位置:預設接在摘要區最後一個實體行之後;帶 `--after` 時用 summary-line 同一支定位(找不到、對到多處就擋並列候選,`--nth` 指定),插在那一條之後——那一條有續行(`_ns_summary_logical` 認得的)就插在整條之後。縮排照摘要區第一個實體行的前導空白。
4. 寫前形狀檢查(跟提交時同一套):呼叫 `_drift_fix_shape_err(root, [(新行, "summary")])`——內部就是筆記形狀擋逐行用的 `_ns_check_line` 加 `_ns_revisit_violations`;會被提交擋下的寫法(程式行號引用、沒寫來源的 FACT/FLOW/DEP、SEE 夾句子、回頭條件格式壞)在這裡就 rc2 不寫,印同一句改法。格子缺鍵用 `_ns_slot_line_problems(新行, None, 現在)`,擋不擋照 `_ns_slots_mode` 讀到的專案開關:block 就 rc2 不寫、warn 寫入並印提醒、off 不看。不是 git 專案(或 git 列不出檔案清單)時照 `_drift_fix_shape_err` 現在的行為:它回錯誤字串、呼叫端當擋下,summary-add 同樣 rc2 不寫並印那句原因——不另寫跳過分支(圖譜本來就在 git 專案裡、提交前掛鉤也要 git,單人使用不值得多一條路;跟 `drift fix` 同一個擋法)。
5. 寫入照 `atomic_write_verify`(驗新行在、其他行一字不動),同一次把 `updated:` 改成今天(沿用 `_summary_line_rebuild` 的改法);印新增那一行與它在第幾行,提示 `lumos lint <節點>`。`--dry-run` 只印不寫。
6. 統一規則「工具往摘要寫新句子之前先跑提交時那套形狀檢查」:`summary-line` 換出來的新行也跑第 4 點同一支(新片段給空字串、只是刪掉一段的不跑)。這是 summary-line 行為的收緊:以前寫得進去、提交才擋的,現在寫入時就擋。
7. 文件同步:指令說明字典(「什麼時候用」那張)與 argparse、`skills/lumos-project-notes/commands/03-寫回圖譜.md` 加一列、`commands/INDEX.md` 的指令清單、`skills/lumos-project-notes/SKILL.md` §3 寫回表加「摘要加一行/改一行」、頂層指令數(現在寫 91 的地方:`ARCHITECTURE.md` 第 3 節標題、同節圖裡的根節點、同節結尾那句共三處,`skills/lumos-project-notes/reference.md` 裡子命令全覽那句與介紹 `commands/INDEX.md` 是幾個指令總目錄那句共兩處;`t_docs_command_count` 會掃全部活文件,漏改哪一處它就紅)。紀律範本 `scripts/templates/graph-discipline.md` 鐵則 2 括號改成列出 `lumos set` / `append` / `summary-add` / `summary-line` / `decision-add`;改完在本 repo 跑 `lumos update` 重注入 `CLAUDE.md` 與 `AGENTS.md`(doctor Check D 守兩邊一致),照上次改範本的慣例 bump `LUMOS_VERSION`,消費專案下次 `lumos update` 帶過去。
8. [[Projects/改摘要單行的指令_計劃]] 正文〈範圍〉已補一句指到本篇 d1(2026-10-15 寫計劃時一起補;不改它的摘要與狀態)。

### 2. set 說明列出可改欄位(B7)

現況:`lumos set --help` 只有「什麼時候用」一句與三個位置參數;可改的欄位清單只在打錯時的擋下訊息裡(`_cmd_set_locked` 組 `SCALAR_KEYS` 與 `COND_KEYS`)。

做法:抽一支 `_set_keys_text()` 回「純量欄位:…;整欄換掉:valid_under、revalidate_when」,`set` 的 argparse 把它放進 `key` 參數的 help 與說明尾巴,擋下訊息也改呼叫它——兩處同一份,不另抄。`append` 的 `key` 參數同樣列 `LIST_KEYS`(同一個缺口,一起補)。

### 3. append 的落點寫成連結時自動改純字串(F14)

現況:`_cmd_append_locked` 對 `lands_in` 照收任何值;lint 只提醒(`_nl_rule_lands_in`),處置閘才擋(`_disposal_landing_step`)。

做法:`key == "lands_in"` 時先正規化:去掉外層 `[[ ]]`、去掉結尾 `.md`、去頭尾空白;正規化後用 `_lands_in_bad` 判(lint 與處置閘同一支)——合格就照正規化後的值寫入,有改就印「已改成純字串 Systems/x(lands_in 只收這種寫法)」;仍不合格就 rc2 不寫,印跟處置閘同一句格式說明。統一規則:寫入端跑讀取端同一支判斷。

### 4. 否定現況句提醒不唸條件與時序子句(F17、W9)

現況:`_ns_negation_hits` 的修飾語判定(`_ns_neg_is_modifier`)認「否定字眼後面 9 字內接『時』『前』、而且下一個字是斷句或虛詞」才算條件子句;斷句只認一組固定標點,碰到括號就停。實測(2026-10-15,對 order-web 圖譜與比對表的句子):「載入中(第一次還沒回來)、沒有商品…」「(畫面還沒重繪)」「還沒回來時應顯示」「這時還沒確認環境…」「畫面還沒重繪前…」「若使用者還沒登入,導到登入頁」全部被提醒。2026-09-30 量測報告第三版的留出樣本裡,非真句的大宗本來就是「程式或資料狀態的描述、條件子句」(30 行裡 14 行)。

規則(只認語法記號,不加任何狀態詞的白名單):否定字眼落在「條件或時序子句」裡就不算現況句。子句用三個記號認:
1. 往後找「時」「前」時,收尾括號(`)` `）` `」` `』`)跳過不停。
2. 「時」「前」後面接的字:原本只收固定幾個標點與虛詞,改成任何標點(Unicode 類別 P 開頭,含「…」「—」)、空白、行尾,另加情態詞「應、該、須」(條款寫法「…還沒回來時應顯示」)。「前端」「時間」「時區」這種後面接一般字的照舊不算。
3. 否定字眼所在那一小段(既有 `_ns_neg_segment` 切法)裡、在它前面出現條件或時序開頭詞「若、如果、假如、要是、一旦、等到、只要、這時、此時」。不收「當」(「當前還沒有測試」是現況句)。

先改量測程式再搬進工具(字眼表與規則的既有規矩:`governance/eval/negation-revisit/neg_revisit_measure.py` 抄給工具、`t_note_shape_negation_lexicon_pinned` 逐字比對):量測程式加 `_is_modifier_v4` 與 `classify_v4`,對 2026-09-30 的 150 行人工判定重跑、結果補進同目錄報告新的一節。2026-10-15 先用一支臨時腳本試過:150 行裡被判真(T)的 0 行被丟、被丟的 2 行是 P 與 H(都不是真句);上面 6 句示範句,記號 1–3 收掉「還沒回來時應顯示」「這時還沒確認」「還沒重繪前…」「若…還沒登入」四種,括號裡的狀態說明(「載入中(第一次還沒回來)」「(畫面還沒重繪)」)照舊會唸——它跟「匯出頁(還沒做)」在字面上分不開,不做(見〈不做〉);寫的人把狀態名放進引號、或改寫成「回應到之前」就不唸。這個提醒本來就只提醒、可關(`note_shape.negation`)。

規則改了,[[Projects/否定現況句配回頭條件_計劃]] 的第 8 週人工抽樣(REVISIT 2026-11-25)要照 v4 抽,本篇上線日寫進那篇正文。

### 5. lint 先唸寫下就成立的回頭條件(F29)

現況:推送時已經擋「這次新寫(或改了條件)的回頭條件,條件已經成立」(`_drift_probe_judge` 那條,`t_drift_when_probes_evaluate_and_trigger` ⑨);提交時只有否定現況句提醒那段字樣裡一句「先確定那件事還沒發生」,不評估;`lumos lint` 完全不看。示範的修補代理寫 `REVISIT:[when-file:<已存在的畫面檔>][by:…]` 想表達「下次改到這支檔」,推送才被擋。

歷史:[[Projects/回頭條件消失式與生來成立_計劃]] 三輪設計審都在「往回查歷史找寫下那一版」收不了,拆到 [[Projects/回頭條件寫下時就成立_計劃]] 另做(drift scan 的「寫下時就已成立」標記)。這次只做**寫下當下看條件現在成不成立**,不往回走歷史。

做法:`_lint_collect` 多一條提醒(warn,不影響 rc):
1. 用 `_probe_lines` 與 `_retire_lines` 抽這一篇的條件式回頭條件與 RULE 撤除條件。
2. 只看「這次新寫或改了條件」的:用 `git show HEAD:<這篇>` 讀上一個提交的版本(一次,只這一篇),同樣抽一次;條件組一模一樣(`_drift_probe_old` 比的那個)的算舊行,不唸(那是 drift scan 的範圍)。不是 git、`HEAD` 沒這篇 → 全部算新寫。這是跟上一版比一次,不往回走。
3. 三種不用讀程式內容就判得出的條件:`when-file:<路徑>` 而路徑在提交索引的檔案清單裡(`_nodehome_list(root, "index")`;不是 git 就看磁碟);`when-gone:<路徑>`(只有路徑、不帶 `::字串`)而路徑在清單裡找不到、也不是資料夾;`when-status:<節點>=<值>` 而那篇現在就是那個值。`when-symbol`、`when-test`、帶字串的 `when-gone` 要讀程式內容,不做(交給推送)。
4. 命中就唸:「第 N 行的回頭條件寫下就已成立(when-file 指的檔現在就在)——推送時漂移檢查會擋下。要等『下次改到這支檔』請改用日期 REVISIT:YYYY-MM-DD,或改綁真的還沒發生的事(要建的新檔、守它的測試名)」;撤除條件那條把「回頭條件」換成「RULE 撤除條件」。

### 6. lint 先唸寫錯格式的已排除行(F6)

現況:「已排除:<類>:<理由>」只有規格閘(`_door_exclusions` 呼叫 `_excluded_line`)在判;寫成「已排除:<類>(理由)」時 `_excluded_line` 回 None、規格閘只說「實務隱患節缺已排除行」,lint 不唸。

做法:`_lint_collect` 對 `type: project` 的筆記,在實務隱患節(`_h2_section_lines(text, _HAZARD_H2_RE)`)裡,可見文字去掉列表記號後以「已排除」開頭的行,呼叫同一支 `_excluded_line`:回 None(冒號沒寫對,含括號寫法)、類名不在四類中文名、理由不到 4 個實字,各唸一行並印正確格式 `已排除:<四類之一>:<理由≥4 字>`(四類名照 `_DOOR_CLASS_ZH`)。warn,不影響 rc。判法跟規格閘同一支,不另寫正則。

### 7. 計劃裡要新建的路徑(F9)

現況:`_refcheck_scan` 對不存在的路徑一律 `missing`;doctor P 段同樣列「已不存在」。前端新專案幾乎每個路徑都是新的,每輪派工都要手動說明。

做法:一個寫法、兩處都認——反引號路徑後面緊接半形「(新增)」或全形「（新增）」(中間可有一個空白)就是「這份計劃要新建它」:
- refcheck:路徑不存在時列成 `planned`(文字輸出「○ 將新增」,`--json` 的 status 是 `planned`、頂層多一欄 `planned` 計數),不算 missing、不讓 rc 變 1;路徑已經在就照 ok。
- doctor P 段:只在 `type: project` 的筆記認這個寫法;計劃狀態是 todo/doing 時不列;已 done 而路徑仍不存在時照列,原因寫「計劃已完成,標了新增的路徑還是不存在」。
- 設計審手冊(`skills/lumos-design-loop/SKILL.md` 步驟 2 refcheck 那句)補一句「要新建的路徑標(新增)」。

抽取那段(反引號裡的字串、它在原文的結束位置)兩處各自已有(refcheck 跟 Check P 刻意複製,見 [[Systems/lumos-refcheck]] d1);「後面緊接(新增)」的判斷寫成一支小函式兩處共用。

### 8. doctor 路徑檢查:指令帶參數、被忽略的執行期檔(W5)

現況:doctor P 段與 refcheck 把反引號裡整串當路徑,「scripts/e2e.sh --cleanup」整串查不到就判已不存在;執行期才有、已被 gitignore 的檔(鎖檔、狀態檔)判不存在。另一個 repo 的路徑那一項沒重現,不做。

做法(兩處同一套):
1. 反引號裡含空白、整串又不是存在的路徑時,當成一行指令:只拿第一個以空白分開的詞當路徑核對;第一個詞沒有 `/` 就跳過。refcheck 那邊要替 `_node_code_ref_tokens` 新增一個 `cmdline` 參數(現在沒有)開這個選項——預設關,推筆記與每支檔有家這兩個呼叫端行為不變(那兩處改了會讓既有筆記突然多出「別人的檔」)。
2. 不存在的路徑先整批問一次 `git check-ignore --stdin -z`:被忽略的不算不存在——doctor P 段不列,refcheck 列成 `ignored`(不算 missing)。不是 git 專案就跳過這一步。

### 9. 每支檔有家:提醒與預設範圍(B8、B9、W6)

B8 現況:提交前那句「它的家這次沒動」(`home check` 的家提醒,程式裡叫 nudge)用的是 `content_changed`——只看摘要、決策、正文三欄(`_nodehome_parse_note` 的 sig);about_code 與 responsibility 是簿記,不算。這個定義也決定寫回落點擋不擋([[Projects/每支檔有家_計劃]] 的 S13、S13b),不能動。
做法:只改 nudge 那一處:一支改動檔的家,只要這次 about_code 或 responsibility 有變(兩版的 `about`、`resp` 不同)就算「家有動過」,不印那句提醒;`content_changed` 與 S13、S13b 的擋法不變。「一檔兩聚合只能一個家」:現況 `homesN` 本來就是清單、允許多個家(超過 8 個才改印 nudge-many),不改程式,補一支測試釘住。

B9 現況:`lumos home check` 與 `lumos note-shape` 不帶 `--staged` 或 `--diff` 就 rc2。
做法:兩支同一條規則——都沒帶就照 `--staged` 查,先印一句「沒帶範圍,照 --staged 查這次要提交的內容」。兩個都帶照舊擋。掛鉤都明寫旗標,不受影響。

W6 現況:doctor S8 讀提交索引那一份(`_nodehome_ledger` 用 `_nodehome_side(root, "index", …)`)——已暫存的節點看得到,還沒 `git add` 的新節點、或改了 about_code 還沒暫存的節點看不到,提交前一直唸沒家。
做法:`_nodehome_ledger` 建完索引那份之後,另列圖譜 Systems 底下未追蹤(`git ls-files --others --exclude-standard`)與工作目錄有改(`git diff --name-only`)的 .md,用 `_nodehome_parse_note` 讀工作目錄版本;只靠這些節點才有家的檔,從 S8 的沒家清單拿掉,改印一行「這幾支的家還在工作目錄、沒提交(<節點>);提交時一起加進去」。需要家的檔照舊從索引算;S9、S10 不動;提交前檢查本來就讀索引,不動。

### 10. 規格閘:實作後重跑、乾淨 clone 推送、健檢欄位、重複警告(B1、B11、B2、B3、W10)

設計意圖(讀 [[Projects/雙向門放行_計劃]] 與 [[Systems/bound-tests-gate]] 後確認):風險低不派審,證據是「規格閘時每條新行為的測試各自紅、推送時全綠」兩頭夾住;推送閘是它唯一的閘。下面每一條都不放寬這個證據,只修讓它失效或擋錯的地方。

**B1 實作後才跑會擋**。現況:`cmd_spec_gate` 對風險低在 `_spec_gate_print_twoway` 沒過時直接 rc1,不寫留痕;實作做完再跑,測試都綠,必擋;示範的代理把新檔搬走跑出紅再搬回。
- (a) 重跑:沒過的每一條都只是「測試已綠」(沒有弱證據、沒有找不到),而且審查帳裡這份計劃最後一筆規格閘留痕是風險低、條款指紋(`_clause_block_sha` 同一套輸入)與門判定規則版本都跟現在一樣 → 印「已有 <日期> 的風險低放行留痕、條款沒變;測試現在綠=已做完,不用重跑(推送閘照跑留痕裡的測試)」,rc0,不寫新留痕(原留痕裡的紅證據保留)。
- (b) 第一次就在實作後跑:沒有相符留痕、沒過的條款全是「測試已綠」→ 照舊擋,訊息改講白並教手動補跑:「規格閘要的是『還沒實作時這些測試會紅』的證據,實作後才跑拿不到。補法:先把實作提交(或做一個暫時提交),用 `git restore --source=<實作前的提交> -- <實作的程式檔>` 把實作檔暫時換回實作前的版本(測試檔留現在的),在同一個工作目錄跑 `lumos spec-gate <計劃>` 拿到紅與留痕,再 `git restore -- <實作的程式檔>` 換回來」。訊息列出這次沒過的條款名,讓人知道要看到哪幾支紅。留痕照一般流程寫進目前這份圖譜的帳,不需要工具另外開工作目錄。
- 不做工具內建的「在實作前的提交開暫時工作樹跑紅」(`--red-at`):編排者 2026-10-15 裁走輕量版(決策 d2,待決問題 Q1),理由是使用者說先不要過度設計,暫時工作樹是新的複雜度與新的出錯點(中斷殘留、測試輔助檔要不要一起蓋)。
- 手冊:`skills/lumos-design-loop/SKILL.md`「先判門」那段補一句「實作後才跑會擋;已有相符留痕就不用重跑,沒有就照擋下訊息把實作檔暫時換回實作前的版本補跑一次」。

**B11 健檢欄位只記最後一次**。現況:doctor S14 每列印的「條款 N/紅 N」是那筆留痕寫下時的紅數(規格閘時本來就該紅),失敗的重跑不寫留痕,所以做綠之後一直顯示「紅 2」,提醒句又寫「紅要在推送前做綠」,讀起來像還沒做。做法:每列改成「規格閘當時:條款 N/紅 N(那時該紅)、計劃現在 <狀態>、留痕 <日期>」,提醒句改成「這是規格閘當時的紅數;現在綠不綠由推送閘跑留痕裡的測試」。不新增欄位、不重跑測試。

**B2 改 done 後推送閘不再重跑**。現況:`_spec_gate_push_scan` 只對 `status == "doing"` 的計劃跑留痕裡的測試;照「做完再改狀態」的習慣,把狀態改成 done 跟實作同一次推送,這次推送就跳過唯一的閘。當初只看 doing 是怕放著沒人管的計劃變成擋所有人的地雷(雙向門放行 r2 簡化席)。做法:候選多一種——狀態是 done、而且這次推送範圍改到了計劃檔本身(既有的 `touched_plans`);沒被改到的 done 計劃照舊不查,地雷顧慮不變。

**B3 留痕在被 gitignore 的本機帳**。2026-10-15 實測(暫存目錄造 fixture repo,docs/.gitignore 照 `init` 寫的忽略 .canary-log.jsonl):原 repo 條款測試紅 → 推送閘 rc1 擋;`git clone` 出來的乾淨 clone 同一個範圍 → rc0,一個字都不印(帳不在、`rec` 是 None、整份計劃當沒留痕跳過)。本 repo 的審查帳有進版控,所以工具鏈自己沒中;消費專案(`init` 產的)全中。做法(統一規則:推送閘要讀的留痕一律進版控的治理帳,同代碼審留痕):
- 寫:`_spec_gate_record` 寫審查帳之後,同一筆再寫一筆治理帳事件 `{"gate": "spec-gate", "kind": "spec-gate-record", "nodes": [計劃], "record": <同一筆>}`;確認 `_gov_routes_local` 把它分到進版控那本。
- 讀:`_spec_gate_ledger_index` 先照舊讀審查帳;推送閘有候選計劃在審查帳找不到留痕時,才讀一次治理帳,讀之前先用字串 `"spec-gate-record"` 篩行再解 JSON(本 repo 治理帳約 20MB,代碼審曾抓過「只走輕量審也要整本讀一次」的成本問題),兩邊以 token 去重、取最後一筆。
- 舊留痕(上線前只在本機帳的)不補寫;乾淨 clone 推它們時照舊判沒留痕。為了不再靜默:推送閘對「狀態 doing、門現在重判是風險低、卻找不到任何留痕」的候選印一行「找不到規格閘留痕(本機帳不在?),這份的條款測試這次沒跑」——只印不擋(舊計劃沒有補救路,擋了等於擋所有人)。
- 同一族、不在這次範圍:輕量設計審的紀錄也只在本機審查帳,乾淨 clone 推送時會判沒審而擋下(往嚴的方向錯),另記在 [[Issues/輕量設計審紀錄只在本機帳乾淨clone推送誤擋]]。

**W10 同一句警告印三次**。現況:`load_platforms` 每被呼叫一次就對不存在的 root 印一次「⚠ 平台 'x' 的 root 不存在」,規格閘一次跑會呼叫三次。做法:模組層一個集合記「這次程式執行已經警告過的 (平台, root)」,同一組只印一次;所有呼叫端共用,不逐處去重。

### 11. F15 條款判法不一致:判不出,不做

2026-10-15 重現:示範那句「當頁面載入時應已有一個 aria-live 區塊;之後下單成功或失敗的訊息出現在那個區塊裡,而輪詢失敗的提示不在裡面。」——`_clause_grammar` 判「回應段缺應」(第一個逗號之後那段沒有應);在 fixture repo 跑規格閘同樣擋下「格式看不懂」。兩道閘本來就共用 `_clause_check`,差別只在句式要不要驗的日期旗標,示範那份計劃的首筆帳在旗標日之後,兩邊都會驗。order-web 的治理帳裡規格閘只有兩筆成功紀錄(10-15 12:27、12:52),都在那句被改成合格句式(11:55 的提交)之後;那句只存在 11:54–11:55 之間,帳上找不到規格閘在那時放行它的紀錄。推測是規格閘跑在第一輪折入之前、處置閘跑在折入之後。判不出工具的不一致,不改程式。

## 驗收條款

- [S1] 當 summary-add 收到一行合格的摘要行時,它應接在摘要區最後一條之後寫入、把 updated 改成今天並印出新增的那一行。[test: t_summary_add_appends_at_end]
- [S2] 當 summary-add 帶 --after 而片段在摘要裡恰好對到一條時,它應插在那一條(含續行)之後;對不到或對到多處時應不寫、回 2 並列出候選。[test: t_summary_add_after_locates_entry]
- [S3] 當新行是空的、含換行類字元、或摘要寫成單行值時,summary-add 應不寫並回 2。[test: t_summary_add_rejects_bad_input]
- [S4] 當新行跟摘要裡既有的一行一字不差時,summary-add 應印「已經有」、回 0 且檔案不動。[test: t_summary_add_skips_duplicate]
- [S5] 當新行帶提交時會被筆記形狀擋擋下的寫法(程式行號引用、沒寫來源的 FACT 行)時,summary-add 應不寫、回 2 並印出跟提交時同一句改法。[test: t_summary_add_runs_note_shape_check]
- [S6] 當新行缺了必有的格子時,summary-add 應照專案的格子開關處理:block 時不寫並回 2、warn 時寫入並印提醒。[test: t_summary_add_follows_slot_mode]
- [S7] 當 summary-line 換出來的新行帶提交時會被擋的寫法時,summary-line 應不寫並回 2;只刪掉一段的應照舊寫入。[test: t_summary_line_runs_shape_check]
- [S8] 當讀紀律範本鐵則 2 與 commands/03-寫回圖譜.md 時,兩處應都列出 summary-add 與 summary-line,而且本 repo 的 CLAUDE.md、AGENTS.md 紀律區塊應跟範本一致。[test: t_discipline_lists_summary_commands]
- [S9] 當跑 lumos set --help 時,說明應列出 set 收的每一個欄位(含 responsibility 與整欄換掉的條件欄),而且跟擋下訊息列的是同一份。[test: t_set_help_lists_keys]
- [S10] 當 append 的欄位是 lands_in、值寫成 [[Systems/x]] 或 Systems/x.md 時,append 應改成純字串 Systems/x 寫入並印一句改了什麼;正規化後仍不合格的應不寫並回 2。[test: t_append_lands_in_normalizes]
- [S11] 當新寫的否定字眼落在條件或時序子句裡時,提交前的否定現況句提醒應不列這一行(子句照〈做法〉4 的三個語法記號判);「前端頁面還沒做」「匯出功能尚未實作」這類現況句應照列。[test: t_note_shape_negation_condition_clause]
- [S12] 當量測程式的 v4 規則重跑 2026-09-30 的 150 行人工判定時,被判真(T)的行應一行都不少,而且正式工具應跟量測程式逐行判得一樣。[test: t_note_shape_negation_v4_matches_measure]
- [S13] 當一篇筆記新寫或改了條件的回頭條件(含 RULE 撤除條件)是 when-file 指向提交索引裡已有的檔、when-gone 指向不存在的路徑、或 when-status 指的筆記已是那個狀態時,lumos lint 應印一行提醒講它寫下就已成立、推送會被擋,並給日期式的改法。[test: t_lint_revisit_born_true]
- [S14] 當回頭條件在上一個提交的同一篇裡已經有一模一樣的條件組時,lint 應不為它印寫下就成立的提醒。[test: t_lint_revisit_born_true_skips_old]
- [S15] 當計劃的實務隱患節有以「已排除」開頭、卻不合「已排除:<四類之一>:<理由≥4 字>」的行時,lumos lint 應逐行提醒並印正確格式(括號寫法、類名不在四類、理由太短都要唸)。[test: t_lint_excluded_line_format]
- [S16] 當 refcheck 看到反引號路徑後面緊接「(新增)」而路徑還不存在時,refcheck 應把它列成將新增、不算 missing、不讓回傳碼變 1。[test: t_refcheck_planned_path]
- [S17] 當進行中的計劃正文把不存在的路徑標了「(新增)」時,doctor P 段應不列這一條;計劃已 done 而路徑仍不存在時應照列並講計劃已完成。[test: t_doctor_p_planned_path]
- [S18] 當反引號裡是「路徑加參數」的一行指令時,doctor P 段與 refcheck 應只拿第一個詞當路徑核對,推筆記與每支檔有家的抽取結果應不變。[test: t_ref_path_first_word_of_command]
- [S19] 當反引號路徑不存在、但被 gitignore 忽略時,doctor P 段應不列成已不存在,refcheck 應列成被忽略、不算 missing。[test: t_ref_path_gitignored_runtime]
- [S20] 當這次提交改了某支檔、而它的家只改了 about_code 或負責範圍時,home check 應不印「它的家這次沒動」那句提醒,寫回落點的擋法應不變。[test: t_nodehome_nudge_counts_bookkeeping_edit]
- [S21] 當一支檔同時列在兩篇 Systems 節點的 about_code 時,home check 應兩篇都當它的家、不報沒家。[test: t_nodehome_two_homes_allowed]
- [S22] 當 lumos home check 或 lumos note-shape 沒帶 --staged 也沒帶 --diff 時,它們應照 --staged 查並先印一句講用了預設。[test: t_home_and_note_shape_default_staged]
- [S23] 當新開的節點只在工作目錄(未加進版控)、已把某支檔列進 about_code 時,doctor S8 應不把那支檔列成沒家,改印一行講它的家還沒提交。[test: t_doctor_s8_sees_worktree_home]
- [S24] 當風險低計劃已有條款指紋相同的放行留痕、條款測試現在都綠時,lumos spec-gate 應印已有留痕不用重跑、回 0,而且應不寫新留痕。[test: t_spec_gate_low_rerun_after_impl]
- [S25] 當風險低計劃沒有相符的留痕、沒過的條款全是因為測試已綠時,規格閘應擋下、講實作後才跑拿不到紅的證據,並印出把實作檔暫時換回實作前版本補跑的步驟與這次沒過的條款名。[test: t_spec_gate_low_green_explains_manual_red]
- [S26] 當 doctor S14 列風險低計劃的紅數時,每一列應標明那是規格閘當時的紅數與計劃現在的狀態,提醒句應不再叫人把紅做綠。[test: t_doctor_s14_labels_red_at_gate_time]
- [S27] 當這次推送改到一份已 done 的風險低計劃(例:同一次推送把狀態改成 done)時,推送閘應照 doing 一樣跑留痕裡的測試;沒被改到的 done 計劃應照舊不查。[test: t_prepush_spec_gate_done_in_range]
- [S28] 當規格閘寫留痕時,它應同時在進版控的治理帳寫一筆 spec-gate-record;推送閘在審查帳找不到留痕時應改讀治理帳,兩邊同一筆只算一次。[test: t_spec_gate_record_in_governance_log]
- [S29] 當在沒有本機審查帳的乾淨 clone 推送一份風險低計劃、條款測試是紅的時,推送閘應擋下。[test: t_prepush_spec_gate_clean_clone_blocks]
- [S30] 當推送閘的候選是門重判為風險低的 doing 計劃、兩本帳都找不到它的留痕時,推送閘應印一行講這份的條款測試這次沒跑,回傳碼應不變。[test: t_prepush_spec_gate_missing_record_speaks]
- [S31] 當設定裡某個平台的 root 不存在、規格閘跑一次時,那句警告應只印一次。[test: t_platform_root_warning_once]

## 實務隱患

- **守衛面**(照實寫,不排除):第 1 節讓 summary-line 寫入時多擋一類寫法(以前提交才擋);第 3 節讓 append 寫入端多擋;第 9 節改提交前提醒與預設範圍;第 10 節改規格閘放行(已有相符留痕就回 0)與推送閘的候選(多查改成 done 的、多讀治理帳)。判錯的方向:(a) 判錯成「已有相符留痕」會讓沒紅過的計劃放行——條件綁在條款指紋與規則版本都一樣,指紋輸入跟推送閘判過期是同一套;(b) 手動把實作檔換回舊版補跑時換錯檔、或連測試輔助檔一起換掉而整支跑不起來——跑不起來是弱證據、不算紅,照舊擋,換錯檔的紅會在推送閘全綠那一頭再被夾一次;(c) 推送閘多查 done 計劃可能擋到只改了措辭的 done 計劃——只限這次改到計劃檔本身的,而且條款沒變時指紋不變、照跑測試即可。這幾處都要代碼審(會判 high)。
- **相容**:summary-line 寫入時多擋一類寫法,以前寫得進去、提交才被擋的現在當場擋,呼叫端看到 rc2(訊息照提交時那句);`set --help` 只多文字;append 對 lands_in 會改寫使用者給的值(只拿掉 `[[ ]]` 與 `.md`,印出來);治理帳多一種事件,讀治理帳的既有指令(`lumos gov`、處置閘人裁紀錄)要確認不受影響;`refcheck --json` 多兩種 status(planned、ignored)與一個頂層計數,既有消費端只看 missing/out_of_range,不受影響。
- **效能**:推送閘只在審查帳找不到留痕時才讀治理帳,先用字串篩行;lint 的 F29 每篇多一次 `git show HEAD:<這篇>` 與一次讀索引清單(單篇,毫秒到百毫秒);doctor P 段多一次 `git check-ignore --stdin`;doctor S8 多兩次 git 列檔、只讀有變的節點。
- **併發**:寫入都走既有的圖譜寫入鎖;單人、AI 依序操作,不另處理。
- **跨環境**:淺層 clone 或不是 git 時,F29 的「跟上一版比」與 W5 的忽略檢查照「全部算新寫」「跳過」走。
- 已排除:金流:只改筆記工具的指令、提醒與閘,不碰任何收費流程
- 已排除:對外送出:不呼叫網路、不往外部服務傳任何東西
- 已排除:不可逆:改的都是版控裡的程式與筆記,還原提交就回去;帳本只多寫、不改舊列

## 不做

- 不做括號裡的狀態說明(「載入中(第一次還沒回來)」)的豁免:它跟「匯出頁(還沒做)」在字面上分不開,只能靠狀態詞白名單,使用者明說不要逐詞白名單。
- 不做 F29 的 `when-symbol`、`when-test`、帶字串的 `when-gone` 寫下當下判定(要讀程式內容與測試索引,交給推送時的漂移檢查);不往回查歷史(那是 [[Projects/回頭條件寫下時就成立_計劃]] 的 drift scan 標記)。
- 不做 F29 在提交時擋(推送已經擋,lint 是寫完一篇就跑的那一步,最早說得到)。
- 不做 W5 的「另一個 repo 的路徑」(沒重現)、W6 的設定檔(eslint.config.js 這類)算不算需要家的檔(既有 `node_home.ignore` 可設)。
- 不補寫上線前只在本機審查帳的舊規格閘留痕;不把整本審查帳改成進版控(那是另一個決定,輕量設計審紀錄同一族,見實務隱患)。
- 不做 F15(判不出,見〈做法〉11)。
- 不做規格閘 `--red-at`(工具內建開暫時工作樹在實作前的提交跑紅):決策 d2,改由擋下訊息教人手動補跑。
- 不改新開節點骨架的四個佔位行(有了 summary-add 就能加)。

## 回退

七個提交各自獨立,還原哪一個就回到那一節原本的行為。① 還原後 summary-add 指令消失、summary-line 回到不做寫前檢查,紀律範本照還原後的版本再跑一次 `lumos update` 重注入;⑦ 還原後治理帳裡已寫的 spec-gate-record 事件留著不讀、無害,推送閘回到只看 doing 與本機審查帳。設定與既有帳本格式都沒有改。

## 合約候選

(無。第 10 節碰到 [[Systems/規格閘]] 的放行條件,若該篇已有合約行,代碼審時對照。)

## 審計修正紀錄

