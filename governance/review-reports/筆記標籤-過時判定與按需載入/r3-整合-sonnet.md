severity: major

審查範圍:逐節讀完 `/tmp/tags/r3.md`,對照 `scripts/lumos`、`scripts/test_lumos.py`、`scripts/hooks/`、`scripts/templates/`、`skills/lumos-project-notes/` 實際查證。我的鏡頭是整合與知識同步。沒有固定席筆記附在尾端,所以那一項不適用。

## 固定席逐條判定

沒有固定席筆記附在尾端,此項不適用。

## Findings

**R3I1**
severity: major
blocking: 是——照字面實作會讓既有測試翻紅,並逆轉一個有出處的決定(單一來源),不改會做出壞系統。
- 輸入:〈分類規格〉最後一段要把分類規格的單一來源搬進 skill 的「寫回圖譜」子檔,範本只留一行指路。
- 壞在哪:目前的單一來源正好相反,而且有測試釘著。
  - `skills/lumos-project-notes/SKILL.md:59`、`skills/lumos-project-notes/commands/03-寫回圖譜.md:30` 都明寫「唯一來源是紀律範本」。
  - `scripts/test_lumos.py:18980` 的 `t_note_convention_single_source` 會檢查三件事:skill 兩檔不准出現 `| \`WHY:\` |` 這種分類表列(`:19000`)、必須含「唯一來源是紀律範本」(`:19011`)、範本〈寫筆記時〉必須還留著 WHY:/RULE:/PITFALL:/FACT:。
  - 該測試的 docstring 說明這是 2026-09-21 同一天被三種手法繞過後,才改成「不准有第二份定義」的形狀。
  - spec 的分類表(定義、必帶、線索、易混淆)放進 skill 就是第二份定義,實作者照字面做,這支測試必紅。
- 同一條規則兩份說法:範本現有的 WHY/RULE/PITFALL/FACT 表(`scripts/templates/graph-discipline.md:38-45`)不會消失,所以範本和 skill 會各有一張表。
- 還有一個代價:範本會被注入每個專案的 CLAUDE.md,動筆時本來就在眼前;skill 子檔只有觸發 skill 才載入。這個取捨 spec 沒講。
- spec 沒列要改的檔:SKILL.md:59、03-寫回圖譜.md:30、`commands/INDEX.md:43`、`t_note_convention_single_source`。
- 要二選一:規格留在範本(搬回「過了瘦身基線」的代價),或明列逆轉決定並改測試與三份指路頁。
引句:「規格的單一來源寫在 lumos-project-notes skill 的」

**R3I2**
severity: major
blocking: 是——H1 的提醒會跟 lumos 自己教的、骨架自己產的寫法互相打架。
- 輸入:H1 對「只放連結的 DEP 行」提醒「寫進 related,不是外部依賴」。
- 壞在哪:既有文件、骨架、程式都把「DEP 只放連結」當正規寫法,不是錯寫。
  - `skills/lumos-project-notes/reference.md:404` 的 FLOW 範例是 `見 [[Systems/付款流程]]`。
  - `reference.md:425` 與 `:434`:「FLOW/DEP 只寫指針」。
  - `reference.md:408` 之後的符號表:DEP「依賴指路(只放 wikilink…)」,範例 `[[Billing]][[Inventory]]`。
  - `lumos new` 骨架提示 `DEP:[[依賴模組]]`(`scripts/lumos:16769`)。
  - 筆記形狀擋刻意放行只放連結的 FLOW/DEP(`scripts/lumos:25264` 的 `_NS_POINTER_ONLY_RE`、`:25314` 的 skip,註明代碼審 r1、r2)。
  - DEP 行的連結還被 `_plan_system_links`(`scripts/lumos:6176`)當「計劃連到誰」的訊號用。
- spec〈現況〉說「文件自己有四處對不上」,而分期第 0 步只修那四處。H1 上線後會多出第五處:文件教 DEP 指針、提交時卻被唸。
- 〈分類規格〉FACT/FLOW/DEP 那列的「易混淆」格已經寫了「DEP 只放連結是『相關筆記』,寫進 related,不寫 DEP」。要的話必須同時改 reference.md 的 DEP/FLOW 列、骨架提示、`_NS_POINTER_ONLY_RE` 的放行理由,spec 一條都沒列。
引句:「新寫的 DEP 行除了 `[[連結]]` 沒有別的字 → 提醒」

**R3I3**
severity: major
blocking: 是——判定者的紀錄格式裝不下 spec 要求它做的事。
- 輸入:〈分類檢查〉要判定者「先把混合句拆成單類句子再判」,每行判定多一欄前綴。
- 壞在哪:
  - 現有派工詞的輸出是每個內容編號一列 `<id> | <class> | <evidence> | <reason>`(`scripts/templates/note-audit-judge.md` 輸出段),而且同編號取最重(規則 7)。
  - 實驗量到混合句有 20 條拆兩段、9 條拆三段(`classify-toolchain-rtb.md`),也就是一行常有兩三個前綴。
  - 單欄「前綴」只能放一個值。判定者拆完能表達的只有「該拆」,看不出拆成哪幾個前綴;spec 又說「該拆」要列給人改,但沒有欄位存拆分結果。
  - 結構上沒說多個判定者或申訴對同一編號給不同前綴時怎麼折。`_note_audit_fold`(`scripts/lumos:26229`)只折 class,`_note_audit_parse_verdict`(`:26188`)只驗 class。
  - 沒講欄位放哪。`_note_audit_parse_report`(`:26475`)用位置取 `cells[2]`、`cells[3]`,插在中間會打壞舊報告;必須在尾端附加。
  - 這是紀錄格式與折疊規則的設計缺口,不是措辭。
引句:「派工詞照上面的分類規格(定義加線索加易混淆),判定者先把混合句拆成單類句子再判」

**R3I4**
severity: major
blocking: 是——第 2 步的出口沒有可執行的上線點,「只提醒」也沒有輸出位置。
- 輸入:〈不溯及既往〉與〈分類檢查〉都說「沿用筆記內容審既有的上線點」。
- 壞在哪:
  - 筆記內容審的上線點是 `_NOTE_AUDIT_GOLIVE_MARK = "note-audit check"`(`scripts/lumos:25913` 附近),要求推送前掛鉤裡有這串。
  - 實際 `scripts/hooks/pre-push` 只有 `reread-check`(`:497-504`),沒有 `note-audit check`;CI 同樣只有 reread-check(`.github/workflows/ci.yml:196`)。
  - 〈現況〉自己承認「還沒接進推送前掛鉤」,接線留給另一份計劃 REVISIT 2026-10-12。
  - 結果:第 2 步做完,多一欄前綴只在人手動跑 `prepare/record` 時才有。
  - 「出口只提醒」的位置也沒定義。`record` 只印「還沒被涵蓋的行」(CODE/MIXED,`scripts/lumos:26745` 附近),`check` 只回 rc。「前綴判錯、該拆、是過程紀錄」沒有任何現成出口。
  - 分期沒把「筆記內容審先接進掛鉤」列為第 2 步的前置條件,S11、S15 與 RETIRE-IF 也沒說接線前怎麼量。
引句:「前綴判錯、該拆、是過程紀錄、是程式推得出——都只列出來讓人改,不擋」

**R3I5**
severity: major
blocking: 是——S12 的驗收門檻照字面跑不動,S15 的比較基準口徑不同。
- 輸入:S12「用去識別化題庫加原 68 句重跑,前綴判對率至少 70%」;S15「高於上線前的 75%」。
- 壞在哪:
  - 原 68 句的答案檔是 `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_key.json`,欄位是 `verdict: 成立/無法判定…`,沒有任何前綴標籤,算不出「前綴判對率」。
  - 150 句(含標籤)只在 `/tmp/ctxsplit/`,不在 repo。`git ls-files governance/audits/2026-10-01-tagdrift` 只有 5 份 md。
  - 會員系統 250 句依 `classify-member-system.md`「不進 repo」,所以 75% 的語料取不回來。
  - 75% 是會員系統 80 句、八類(含「其他」「程式推得出」)、sonnet 子代理量的;筆記內容審的判定者是 opus(`scripts/lumos:25927` 的 `_note_audit_judge_model`),spec 的判定者列舉只有六個值。
  - 70% 的門檻與 75% 的基準不在同一份題庫上,也沒有人先在 opus 加新派工詞上量過一次。
  - 標註者與判定者同為 Claude 家族(〈天花板〉1 已承認),這裡仍未補約束。
  - 實作者得先自行補標 68 句、決定 150 句怎麼存;spec 只在第 1 步一句帶過「題庫存進」。
引句:「前綴判對率低於 70% 就不接」

**R3I6**
severity: major
blocking: 是——預設呼叫在本 repo 最常改的檔上會倒出大量文字,違背「按需載入」的目的。
- 輸入:`lumos search --about <檔> --prefix …`(行模式不截斷、`--top` 預設 0 全給)。
- 壞在哪:
  - `--about` 用的家對照表(`_home_map_from_notes`,`scripts/lumos:24010`)沒有大檔門檻。
  - 改檔前提示那邊刻意有:家 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)就不當入口(`_impact_confirmed_homes`,`scripts/lumos:34597` 附近),理由是「巨檔上家沒有鑑別力」。
  - 本 repo 的 `scripts/lumos` 在 `Systems/` 下有 39 個 status 為 doing/done/stale 的家。我用 frontmatter 解析數,摘要裡 RULE/PITFALL/WHY 共 159 行、約 43,500 字元,全部不截斷輸出。
  - `lumos context` 在輸出超過 20 KB 時就會提醒佔注意力(`scripts/lumos:40166` 附近)。
  - 〈改程式時的分類檢查清單〉要 AI 改每支檔前都跑這條,最常改的主程式拉出 43K。spec 沒設巨檔處理,也沒給摘要或上限。
引句:「`--about <檔>`:那支檔的家筆記」

**R3I7**
severity: major
blocking: 是——清單要檢查的欄位(如 `[confirmed:]`)會被既有格式截掉。
- 輸入:〈搜尋行模式〉說輸出「沿用既有逐行片段格式」。
- 壞在哪:
  - 既有格式(`scripts/lumos:4004-4010`、`:4042-4046`)是篇名一行,底下縮排列「行號 [區域]: 前 90 字…」,超過 90 字就截成「…」。篇名不是每行都帶,S13 要求的「每行帶篇名」也與它不同。
  - 〈改程式時的分類檢查清單〉要逐類看 `[confirmed:]` 是否超過半年、`[until:]`、`[retire:]`。本 repo 的 RULE/PITFALL 行常超過 90 字(R3I6 的 159 行平均約 270 字),欄位會被截掉。
  - 判不了「這次改動有沒有違反它」,AI 只能再 `lumos show` 全文,而行模式本來就是為了不用讀全文。
  - spec 要明定行模式輸出是否不截斷、格式是否每行 `篇名:行號: 全文`。
引句:「輸出沿用既有逐行片段格式,每行帶篇名;`--json` 在行模式多一個片段文字欄位」

**R3I8**
severity: major
blocking: 是——清單漏掉合約與舊寫法,還會讓 AI 以為沒有東西要查。
- 輸入:〈改程式時的分類檢查清單〉只列 WHY/RULE/PITFALL/FACT 四列,取行指令是 `--prefix RULE,PITFALL,WHY`(沒有 FACT)。
- 壞在哪:
  - 紀律範本和 CLAUDE.md 都說能挑戰程式碼的有 `decisions:`、★INVARIANT★ 合約行、Issues、Verification;這四類清單沒有對應列。
  - 本 repo `Systems/*.md` 摘要行:KEY 637、DECISION 4、WHY 84、PITFALL 75、RULE 12、FACT 2、FLOW 67、DEP 77(我用 grep 逐前綴數的)。〈不溯及既往〉保證舊 KEY 不補標,所以對多數專案(如 rtb)`--prefix` 取行會空或很少。
  - 空結果看起來像「沒有脈絡要查」,實際是舊筆記沒標前綴。spec 沒說空結果要提醒「KEY 與 ★INVARIANT★ 不在此」,也沒要求搭配 `lumos contracts`。
  - 命令與表格不一致:表格有 FACT 列,命令沒有 FACT。
  - 這是 CLAUDE.md 鐵則要求「動手前別漏合約」的缺口。
引句:「lumos search --about <檔> --prefix RULE,PITFALL,WHY」

**R3I9**
severity: minor
blocking: 否——只是提醒,且給得出具體誤判,但不會讓實作做出壞系統。
- 輸入:H3 過程紀錄提醒與〈分類規格〉的 WHY 線索詞。
- 壞在哪:H3 的豁免條件是「沒有 WHY、PITFALL 的線索」,而 WHY 線索詞表含「改成」。H3 的動作詞清單(折入、改成、完成)也含「改成」。因此用「改成」描述動作的過程紀錄,被 WHY 線索豁免掉。
- 另一邊:WHY 規定出處要放在行首(`WHY:[2026-09-27 設計審 r1 三席]…`,本 repo 現行寫法),H3 的「以日期或審查輪次開頭」沒說前綴後面的算不算,實作者要自己猜。
- 兩份線索詞表(WHY 線索、H3 動作詞)要先去重。
引句:「新寫的摘要行以日期或審查輪次開頭」

**R3I10**
severity: minor
blocking: 否——是同一句話內的自相矛盾,不影響其他行為。
- 輸入:〈結構性提醒〉最後一條。
- 壞在哪:「提醒全部印出、不設上限(同否定現況句提醒)」與同句後半「超過 10 行時只印前 10 行加總數」直接衝突。
- 否定現況句先例是全部印出(`_ns_negation_format`,`scripts/lumos:25512` 附近)。實作者不知道依哪一半;S4、S7 到 S10 也沒有測試守這個上限。
引句:「提醒全部印出、不設上限(同否定現況句提醒),但同一次提交同一條規則超過 10 行時只印前 10 行加總數」

**R3I11**
severity: minor
blocking: 否——訊息精度與 vestigial 欄位問題,實作者查得出。
- 輸入:W4、S5 與「已作廢沿用 `[status:superseded]`」。
- 壞在哪:
  - S5 的新訊息對所有 superseded RULE 一律出現,連已經「留著並加連結」的也唸;而同一條 WHY/PITFALL 的規則(S10)是「沒連結才提醒」。RULE 沒對齊。
  - `rule_lifecycle_warnings`(`scripts/lumos:3336`)目前也是無條件唸。lint 每次都唸,對照 spec 說的「留著並加連結」會永遠有噪音。
  - 實際上 `STATUS_REF_RE` 只被 `parse_rule_fields` 用,沒有其他消費端:drift scan、`impact`、reread 都不看這個標記。「沿用」只沿用了標記名稱。
  - 搜尋行模式隱藏是新增的唯一消費者。標了 superseded 的 WHY 在存量漂移的舊句檢查、否定現況提醒下仍會被評估,spec 沒講要不要一起略過。
引句:「已作廢沿用 RULE 既有的 `[status:superseded]`」

**R3I12**
severity: minor
blocking: 否——是重疊與落地清單的遺漏,不改也不會做出錯誤行為。
- 輸入:〈改程式時的分類檢查清單〉與已上線的「回頭重讀」。
- 壞在哪:
  - 回頭重讀(`scripts/templates/note-audit-reread.md`)已經在推送時用判定者問「這個 diff 讓這篇家筆記哪幾行不成立」,並明寫 RULE/PITFALL/WHY 的現況部分一律檢查。
  - spec 的 `related` 列了守檔筆記對照改動計劃,正文完全沒說明新清單與它的分工,是兩道「改程式後回頭查脈絡」的機制各說各的。
  - 清單〈天花板〉3 承認「靠 AI 照做」,卻不提回頭重讀已有判定者做同一類事。
  - 落地清單另外沒列:分期第 0、1 步動紀律範本,必然要同步本 repo 的 CLAUDE.md、AGENTS.md 注入區塊,否則 Check D 報漂移(`scripts/lumos:2790-2830`);也沒提 `CHANGELOG.md`。
  - 〈依賴欄位〉那份計劃的表格第 37 行也宣稱「擴到 WHY、PITFALL 行」,與本篇「已作廢擴大」重複認領同一條規則。
引句:「紀律範本兩處 RULE 效力說法對齊成」

**R3I13**
severity: minor
blocking: 否——是驗收條款跨步驟的排程問題。
- 輸入:S4 驗收「`note_shape.tag_hints` 是 off 時,W4、H1、H2、H3 與已作廢缺連結的提醒都不出現」。
- 壞在哪:
  - 子開關在第 0 步上線,但 H1、H2、H3 與缺連結提醒在第 3 步才做;每步各自過代碼審,第 0 步無法讓 S4 全綠。要在 S4 標明按步驟分段驗。
  - 否定現況句的先例還有 doctor 一行(開關關掉或壞值要看得見,`_ns_negation_doctor_lines`,`scripts/lumos:25581`)。tag_hints 沒有對應 doctor 提示,關掉後靜默。
  - 〈分類規格〉REVISIT 列寫「日期或 `[when-*]` 條件」,實際條件式還必須帶 `[by:]`,否則 note-shape 會擋(`scripts/lumos:25326-25340` 的「沒帶期限」)。
引句:「照 `note_shape.negation` 的先例」

## 逐節已讀

- 前言與摘要、依據、PRIOR-ART:已讀,無 finding。
- 〈現況〉四處文件矛盾我逐項核對,屬實:
  - `reference.md:408` 的 RULE 範例不是欄位寫法。
  - `reference.md:438-441` 舊精簡表的 FLOW/FACT 與新規範相反。
  - 範本兩處 RULE 效力說法不一致:`graph-discipline.md:28` 寫三欄加半年內確認,`:42` 表格那行可讀成兩欄。
  - RETIRE-IF 不在 `SYMBOL_NAMES`(`scripts/lumos:3222`)。
- 加進 `SYMBOL_NAMES` 的副作用我也查了:`t_symbol_names*` 測試與 `SYMBOLISH_RE` 只依賴該集合,沒有其他破壞。
- 〈設計原則〉:已讀,無 finding。
- 〈分類規格〉:見 R3I1、R3I9。另外表格只有 7 列,判定者列舉 6 個值,現有 `SYMBOL_NAMES` 還有 PRIOR-ART、DECISION、TEST、VERIFY、AUTH、FLAG、CORE。這幾種前綴的行,判定者沒有對應標籤,「前綴對不對」對它們無意義,實作要決定歸「其他」。
- 〈分類檢查(AI 判定者)〉:見 R3I3、R3I4、R3I5。
- 〈改程式時的分類檢查清單〉:見 R3I6、R3I8、R3I12。
- 〈搜尋行模式〉:見 R3I6、R3I7。其餘我驗過屬實:
  - `--top` 預設 0(`scripts/lumos:40184`)。
  - 現有 `--include-superseded` 是節點層,語意不變(`:40186`)。
  - `--path` 已存在,與新 `--prefix` 不衝突。
- 〈結構性提醒〉:見 R3I2、R3I9、R3I10、R3I11、R3I13。
  - 否定現況句先例的 plumbing 只在 `--staged` 才算(`scripts/lumos:25837`),tag_hints 沿用即可。但那條 hints 結構是 negation 專用(`items/error/seen`、emit 文字與 `hinted` 帳),新提醒要不要共用該結構 spec 沒說,屬實作細節。
- 〈健康檢查補一段〉:已核對。doctor 的 L 段只收 `_lint_collect` 的 errs(`scripts/lumos:1546`),warns 不進 doctor,所以過期 RULE 目前確實不會出現,spec 的缺口判斷正確。無 finding。範圍(含 Archive 與 superseded 節點)沒講,不構成 finding。
- 〈不溯及既往〉、〈分期〉、〈已裁〉、〈天花板〉、〈不做〉:已讀,無 finding(分期的前置條件問題併入 R3I4)。
- 〈驗收條款〉、〈回退〉、〈合約候選〉、〈審計修正紀錄〉:已讀,問題併入上列 R3I1、R3I4、R3I5、R3I13。

## 實務隱患

- 併發:無,因為新寫入只有既有治理帳與判定檔,沿用既有原子寫入。
- 效能:有——R3I6 的行模式不截斷會一次倒出約 43K 字元。其餘結構性提醒是新增行字串比對,同量級。
- 資源:無,不開程序、不加連線。
- 回滾:第 1 步回退只還原 skill 與範本一行,但 R3I1 說明單一來源已被測試釘住,回退順序要連測試一起考量。
- 相容:R3I2 與 R3I3 有。H1 與既有文件互相抵觸,判定者紀錄多一欄要放在尾端才不打壞舊報告解析。
- 注入:無新增面。判定者讀筆記文字,沿用「筆記是資料」規則。
- 自我治理:提醒可用 `note_shape.tag_hints` 關,但 R3I13 指出關掉後 doctor 不講。
- 金流、對外送出、不可逆:無,理由同 spec 〈已排除〉。

最高嚴重度:major,blocking 8 條
