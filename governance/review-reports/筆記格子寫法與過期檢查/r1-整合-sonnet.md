severity: major

固定席筆記:這次沒有 hook 附在尾端,所以沒有逐條判。

**I1**
severity: major
blocking: 是——照字面實作會做出推送擋和既有存量漂移守衛的決定打架的閘,而且新種類沒有修法與登記。
1. 輸入:〈格子欄位的過期檢查〉表的 `[by:…]` 列,加上分期第 3 步。
2. 表上寫「擋(推送)、存量漂移檢查(新種類)」。
3. 但 `Systems/存量漂移守衛` 的 WHY 已定:「推送閘只擋 c1……c2–c5 連的是人寫的連結,連結有時只是參考,擋了會逼人亂結案,所以只列出」。實際程式也只有 c1 進 must,其餘進 listed,見 `scripts/lumos:28484`。
4. `[by:]` 指向的是人寫的連結,擋它等於翻掉這個決定。spec 沒提翻案,也沒說為什麼這種可以擋。
5. 依賴欄位計劃的〈待解問題〉明列:新發現種類要一起登記 `drift ack`、種類名稱表、`drift fix` 提示,現有只認七種。「整份併進本篇」後這些沒被承接。
6. spec 也沒給 `[by:]` 和 `[retire:事件]` 的 `drift fix` 修法。memory 記著「存量漂移五種都有路」是這個守衛的底線。
7. S8 只測「被擋」,沒有 ack、fix、種類名稱的條款。

引句:「| `[by:…]` | 指到的決策或節點不存在、或它自己也作廢了 | 擋(推送) | 存量漂移檢查(新種類) |」

**I2**
severity: major
blocking: 是——必有格子的合格形狀自己就違反格子文法,這個形狀又同時被提交閘擋。
1. 〈格子規格〉規定「值裡不能有 `]`(既有限制,真要寫就放正文)」。
2. 同一節 D 的事件形狀卻是 `[retire:事件 <[[節點]] 狀態=值> …]`,值裡一定有 `]]`。
3. 實測:`parse_rule_fields("x [retire:事件 [[Projects/a]] 狀態=done] [since:…]")` 回 `retire='事件 [[Projects/a'`,被截斷。`rule_lifecycle_warnings` 會唸「值裡有右中括號,會被截斷」。
4. 正則是 `RETIRE_REF_RE = \[retire:\s*([^\]]*)\]`,見 `scripts/lumos:3315`。
5. S2 要求「形狀合格的 `[retire:]`」才不擋,所以寫節點狀態條件的人不可能同時通過 S2 和 S8。
6. spec 沒說要改正則,也沒說節點怎麼寫(不帶括號的名字?)。

引句:「`[retire:事件 <[[節點]] 狀態=值> 或 <檔或符號出現>]`」

**I3**
severity: major
blocking: 是——「沿用」不成立,第 3 步要新寫解析、候選篩選和轉變判定,spec 卻當成現成的。
1. 〈格子欄位的過期檢查〉的 `[retire:事件 …]` 列、PRIOR-ART 都說沿用回頭條件探針的轉變判定。
2. 實際上探針只認 REVISIT 行,`_revisit_split` 要求 `REVISIT:` 開頭(`scripts/lumos:28511`),`_probe_lines` 只掃 body 與 summary 裡的 REVISIT 行(`scripts/lumos:28660`)。
3. 條件文法是 `[when-file|symbol|test|status:…]` 加 `[by:日期]`(`scripts/lumos:28505`),`when-status` 寫成 `<節點>=<值>`。
4. spec 的 `[retire:事件 <[[節點]] 狀態=值>` 和 `<檔或符號出現>` 兩種寫法都不是這套文法。
5. 探針的 `_PROBE_ANY_RE` 只看 `[when-`,RULE 行裡的 `[retire:事件]` 不會被當條件,也不會被「寫在不評估的地方」提醒。
6. `[retire:事件]` 因此有三個缺口:要不要轉成 `when-*`、寫在 RULE 行時誰評估、期限(探針強制 `[by:]`,這裡沒有)。
7. 依賴欄位計劃另記:既有轉變判定是「不成立變成立」,而且判不了的語意要分開寫。

引句:「| `[retire:事件 …]` | 條件從不成立變成立 | 擋(推送) | 存量漂移檢查,沿用回頭條件探針的轉變判定 |」

**I4**
severity: major
blocking: 是——新格子一上線,既有的 WHY/PITFALL 警告就和新範本互相矛盾。
1. spec 說「規範層(紀律範本、skill、骨架提示、筆記形狀檢查)全部換成統一文法」,清單漏了 `lumos lint` 的 `context_marker_warnings` 和 `rule_lifecycle_warnings`。
2. 前者由 `scripts/lumos:5428` 對整篇摘要跑,規則在 `scripts/lumos:3279-3290`。
3. 實測合格的新行會被唸:
   - `PITFALL:… [出處:2026-09-30 事故] [根因:…] [防回歸:無 …]` 得到「缺防回歸」,因為 `_CTX_REGRESS_RE` 只認 `[test:` / 重現 / repro。
   - `WHY:… [出處:Enzo 對話] [因:x]` 得到「缺出處」,因為 `_CTX_SRC_RE` 要日期、#d、[[ 或 sha。
4. 反過來,舊式寫法過 lint 卻被新閘擋,同一行在兩處標準不同。
5. spec 的 S1–S7 只測閘,沒有任何條款管 lint 與閘一致。
6. 分類計劃的 W4 也用 `rule_lifecycle_warnings`(`:127`)。RULE 的 `retire` 在 lint 認任何文字,在閘只認三種形狀,是兩套標準。

引句:「規範層(紀律範本、skill、骨架提示、筆記形狀檢查)全部換成統一文法」

**I5**
severity: major
blocking: 是——LOG 前綴和已定案的分類計劃直接相反,同一條規則(過程紀錄放哪裡)有兩份說法。
1. 分類計劃 `Projects/筆記標籤_過時判定與按需載入_計劃.md:68` 的設計原則 3:「過程紀錄不進筆記:屬於 git 歷史、驗證紀錄與審查卷證」。
2. 同計劃第 0 步(`:144`)要在紀律範本補「過程紀錄不寫進筆記」。判定者第五欄也會把這類行標成「過程紀錄」要人處理。
3. 本篇新增 `LOG:` 前綴專門收「某天做了什麼」,「不檢查、不當依據」。兩份計劃都要寫進同一個〈寫筆記時〉單一來源,實作者只能擇一。
4. spec 沒有說它翻了分類計劃的哪條,也沒有修訂分類計劃的步驟。
5. 分類計劃審了三輪才收斂,它的 RETIRE-IF 還在量「過程紀錄」比例。LOG 讓這個比例的意義變了。

引句:「| LOG(新,B) | 某天做了什麼 | 不檢查、不當依據 | — |」

**I6**
severity: major
blocking: 是——取代鏈和 DEP/FLOW 兩處,本篇和分類計劃各自一套規則,而且分類計劃沒改。
1. 取代鏈:
   - 分類計劃(`:128`)規定 WHY、RULE、PITFALL 帶 `[status:superseded]` 卻沒 `[[連結]]` 只提醒,不進違規清單。
   - 本篇 E 規定任一前綴 `[status:superseded]` 沒有 `[by:]` 就擋(S5)。
   - 兩者可以同時成立:有連結沒 `[by:]` 時,一邊說合格、一邊說擋。
   - 依賴欄位計劃〈不收〉還明說「`[superseded-by:]`……專案已有決策的取代鏈與 `[status:superseded]` 兩套,再開一套是第三種做法」。`[by:]` 正是第三套。
2. DEP/FLOW:
   - 分類計劃〈不做〉(`:175`)「不提醒『DEP 只放連結』」的理由是「要改得另開計劃連那三處一起改」。
   - 本篇確實是那份另開計劃,但沒有指出它是在翻分類計劃這一條。
   - 分類計劃〈分類規格〉表還寫「只放連結的 FLOW/DEP……照舊合法」。
3. 後果:三個月後的人讀兩份計劃會得到相反的寫法規則,而分類計劃已是「設計審三輪收斂」的定案。

引句:「**DEP/FLOW 只放連結**:一律改 SEE;既有規範、`lumos new` 骨架提示、筆記形狀檢查對只放連結 FLOW/DEP 的放行,一起改掉(C 的代價,本篇負責)。」

**I7**
severity: major
blocking: 是——共用同一個上線點會讓上線前寫的舊式行被當新違規,不溯及既往的承諾做不到。
1. 〈擋〉說「掛在筆記形狀檢查……上線點截斷」。
2. 實際上線點只有一個:`_NOTE_SHAPE_GOLIVE_MARK = "note-shape --staged"`(`scripts/lumos:25443`)。`_nodehome_golive` 找的是掛鉤第一次含這串的提交(`scripts/lumos:24922`)。
3. 該提交早已存在(約 2026-09-27)。新規則上線時,上線點到現在之間所有舊文法的 WHY/PITFALL/RULE/FACT 新增行,都落在範圍內。
4. 推送時走 `per_commit=False`,只靠範圍截斷(`scripts/lumos:25661`)。開著的分支一推送就整批被判成新違規。
5. spec 沒說要為格子另開自己的上線標記。程式有先例:`_note_shape_eval(mark=…)` 已經有 `mark` 參數。
6. 本篇計劃檔自己的摘要 WHY 行也是舊文法。

引句:「- **舊行**:上線點之前寫好的行一律不查,也不轉換。」

**I8**
severity: minor
blocking: 否——規則可以照做,只是「舊行不查」的字面承諾會被改過的舊行打破。
1. 「新寫的行」在程式裡是 git 新增行:`_notelines_new`,見 `scripts/lumos:25656`。
2. 只改一個字的舊 WHY 行,在 diff 裡等同新增行,會被要求補 `[出處:]` `[因:]`。
3. 漂移路線圖 #8 鼓勵「改原句不追加」。這兩條會互相頂住。
4. 合約候選第一條把「舊行不受格子檢查影響」當成承諾,但沒說「被改過的舊行」算舊還是新。

引句:「- 舊行不受格子檢查影響(S1 的舊行部分)——不溯及既往的承諾。」

**I9**
severity: major
blocking: 是——步驟 0 清單漏掉會教舊格式的檔,實作完新寫的人照 skill 抄就被自家閘擋。
1. 步驟 0 只列「紀律範本、skill 判斷例子、`lumos new` 骨架提示」。
2. 這些地方仍用舊格式:
   - `skills/lumos-project-notes/reference.md:404-411`:有一張前綴表,範例是 `[d3]改抽樣不全跑…`、`[2026-09-05] 邊跑邊改腳本… [test:…]`、`DEP:[[Billing]]`。這張表也不在單源測試的 `_NOTE_CONVENTION_FILES` 內,表示已經有第二份定義。
   - `reference.md:288-290`:FLOW/DEP 範例。
   - `skills/lumos-project-notes/commands/03-寫回圖譜.md:35-38`:各前綴要求。
   - `commands/INDEX.md:43`:列出會被擋的種類。
   - `scripts/hooks/pre-push:364`:逃生訊息只提 `[來源:…]`。
   - `scripts/lumos:5315`:lint 訊息叫人補 `FLOW:/KEY:/DEP:`。
3. 新舊格式混在 skill 裡,會產生一批合格的舊範例實際上會被擋。

引句:「0. **範本**:紀律範本的前綴表改成格子範本(單一來源);skill 放判斷例子;`lumos new` 骨架提示改用新範本與 SEE。」

**I10**
severity: major
blocking: 是——把 DEP 連結行改成 SEE 會讓計劃相依判斷漏掉連結,且步驟順序讓 SEE 先被教、後被認得。
1. `_plan_system_links` 只讀摘要的 `DEP:` 行取 `[[連結]]`,見 `scripts/lumos:6215`。它是「計劃連到誰」的唯一來源,相依回歸、門判定、推送前落點都靠它。SEE 行不會被讀到。
2. 步驟 0 就改骨架與範本教 SEE,步驟 2 才把 LOG/SEE 加進 `SYMBOL_NAMES`。中間 lint 會對 `SEE:` 唸「非標準符號行……看起來像打錯字,這行不會被當成摘要」(`scripts/lumos:5416`),而 S4 在步驟 1 就要求提醒改用 SEE。
3. 骨架現有空的 `FLOW:` `DEP:` 靠 `not body` 跳過。新的 SEE「至少一個連結」若沒保留這個豁免,`lumos new` 產的骨架第一次提交就被擋。spec 沒寫這一條。

引句:「2. **新前綴**:LOG、SEE 進摘要前綴表;搜尋行模式與分類判定者把 LOG 當過程紀錄、SEE 當連結。」

**I11**
severity: minor
blocking: 否——只是實作者要自己補,不會做出壞系統。
1. PRIOR-ART 寫「RULE 欄位沿用 `parse_rule_fields`」,S12 寫「用既有的行內欄位解析」。
2. 實際上 `parse_rule_fields` 只認 `since/until/confirmed/status/retire/applies` 六個鍵(`_RULE_FIELD_RES`,`scripts/lumos:3317`)。
3. 出處、因、根因、依據、觀測、recheck、repro、by、防回歸都沒有解析器。重複鍵取最後一個,也沒有定義這些新鍵要不要照辦。
4. 沒有測試把「紀律範本表 = 程式裡的必有鍵表」釘在一起。分類計劃對詞表是逐字釘住(`t_note_shape_negation_lexicon_pinned`)。範本與程式各自演化是 memory 裡記過的散落同步問題。

引句:「- [S12] 四個前綴的必有鍵檢查 應 讀同一張「前綴 → 必有鍵」表、用既有的行內欄位解析,不為各前綴另寫判法」

**I12**
severity: minor
blocking: 否——實作者會自己選一種,但選錯的後果可預期。
1. 〈擋〉有兩個開關:`note_shape.gate` 決定擋或提醒,`note_shape.slots` 是 block/warn/off。
2. 組合沒定義:`gate=warn` 時 `slots=block` 擋不擋?`gate=off` 時整道不跑,slots 是否仍適用?
3. 分類計劃說 gate off 時整道檢查不跑,本篇沒複述。
4. doctor 的 `_note_shape_doctor_lines`(`scripts/lumos:26268`)已有「開關不是 block 就講」的先例,spec 沒列要為 `slots` 加一行。
5. S4 說只放連結的 DEP/FLOW「提醒」,但違規清單裡的東西一律由 gate 決定擋或提醒。提醒要自己的容器(像否定現況句那樣),spec 沒寫。

引句:「- **子開關(新增)**:`note_shape.slots`(`block` 預設 / `warn` / `off`),照 `drift_check.old_sentence` 那種「一道閘底下一個子開關」的先例;壞值照 block 並講一句。」

**I13**
severity: minor
blocking: 否——會被擋的人看到訊息就知道,但合格集合定義不全。
1. RULE 的 `[依據:人|外部|審計|法規]`:紀律範本的 RULE 定義是「程式看不到的限制(相容性、法規、要人工核可…)」,「相容性」沒有對應的值。
2. `[retire:度量 <指標> <比較> <數字>]`:指標只說「先做兩種:觸發次數、跳過次數」,沒有名字或讀哪個帳。
3. S2 要擋「形狀不合格」,而「形狀合格」的集合有這兩處沒定義。

引句:「| RULE | 限制 | `[依據:人\|外部\|審計\|法規]` `[since:]` `[retire:三種形狀之一]` | `[confirmed:]`(要挑戰程式碼就必須半年內)`[test:]` `[applies:]` |」

**I14**
severity: minor
blocking: 否——回退時只多出雜訊警告。
1. 〈回退〉說「已經照新範本寫的行留著無害:舊程式不認得的記號只是文字」。
2. 還原第 2 步後,`SEE:` 和 `LOG:` 行會觸發 lint 的「非標準符號行……看起來像打錯字」(`scripts/lumos:5416`)。
3. 所以不是完全無害。

引句:「- 已經照新範本寫的行留著無害:舊程式不認得的記號只是文字。」

**I15**
severity: minor
blocking: 否——是計劃管理漏洞,不影響實作。
1. 依賴欄位計劃(`Projects/依賴欄位_過時判定_計劃.md`)的 frontmatter 還是 `status: todo`,沒有標「併入本篇」。
2. 它自己的 REVISIT(2026-11-26)還要「照〈待解問題〉逐條改設計,再開設計審」。本篇第 4 步也說「再設計」。同一件事有兩個負責人。
3. 本篇 `[test:名]` 列寫「路線圖 1b 那案負責所有筆記」,但那案「另開計劃」尚未存在,分期裡也沒有它。
4. `lands_in` 只列兩篇。這次要改的檔還有紀律範本、skill、`lumos new`、lint、doctor,規則第 5 條要求每支改到的檔都有家,spec 沒列。
5. 步驟 2 要改判定者派工詞(LOG/SEE),`_NOTE_AUDIT_PROMPT_VERSION` 規定改字就升版並重跑小實驗(`scripts/lumos:26509`),分類計劃第 2 步還在量基準。本篇沒列這個依賴。

引句:「依賴欄位那份整份併進本篇,改名為「格子欄位的過期檢查」」

最高嚴重度:major,blocking 8 條
