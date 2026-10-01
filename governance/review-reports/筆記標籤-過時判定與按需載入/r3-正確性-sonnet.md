severity: major

固定席筆記:派工詞說「若 hook 有附在尾端」,但我收到的內容裡沒有附任何固定席筆記,所以沒有逐條判定可寫。

我讀完整份 spec,並對照 `scripts/lumos`、`scripts/hooks/pre-commit`、`skills/lumos-project-notes/reference.md`、`scripts/templates/` 與兩份分類實驗摘要驗證過。前兩輪已折入的項目大多補上了:RULE 的 `[confirmed:]` 半年門檻、RETIRE-IF 不在前綴表、`--top` 預設 0、superseded 訊息改寫、doctor 掃舊 RULE。以下是仍會做錯的地方。

**R3C1**
severity: major
blocking: 是 照字面做,H2 會叫作者把 ★INVARIANT★ 合約行拆開,拆壞合約。
1. 輸入:新寫的 `KEY:★INVARIANT★ …[test:…]` 摘要行,長度超過 140 字。這類行常帶 `[test:]`,再提到「必須」「根因」之類的字,就同時有兩類線索詞。
2. 走到 H2:規則只看「新寫的摘要行」長度加兩類線索詞,沒有排除合約行。
3. 壞在哪:實驗已指出合約行「自成一種格式,不該被拆」(`governance/audits/2026-10-01-tagdrift/classify-toolchain-rtb.md:32`)。
   - spec 現況也說合約記號是少數準確的結構線索。
   - lint 要求合約只能寫成 `KEY:★INVARIANT★` 前綴(`scripts/lumos:5387`),拆出去的另一半就失去合約身分或測試綁定。
   - 判定者派工詞同樣要求「先把混合句拆成單類句子再判」,也沒有豁免合約行。
引句:「新寫的摘要行超過 140 字,而且同時有兩類的線索詞」
佐證:`scripts/lumos:5387`

**R3C2**
severity: major
blocking: 是 分類規格表把合約該用的 `KEY:` 前綴寫成「新寫不用」,與現行必填規則直接衝突。
1. 表中 KEY 列寫「舊的未分類寫法,新寫不用」。
2. 但 lint 強制 ★INVARIANT★ 與 ★DEBT★ 必須寫在 `KEY:` 前綴下(`scripts/lumos:5387`)。`reference.md:421` 的符號表也這樣規定。
3. 表裡沒有「合約行」這一類。判定者的前綴選項(WHY / RULE / PITFALL / FACT / 過程紀錄 / 其他)也沒有 KEY 或合約。合約行會被判成「前綴錯」或「其他」。
4. 後果:實作者照表把 KEY 當淘汰項,會叫人別寫合約行,或讓判定者對每條合約行報前綴錯。
引句:「| KEY | 舊的未分類寫法 | 新寫不用 | — | — |」
佐證:`scripts/lumos:5387`、`skills/lumos-project-notes/reference.md:421`

**R3C3**
severity: major
blocking: 是 H1 與現行指引、骨架提示、既有豁免三處直接矛盾,spec 沒列修正。
1. `reference.md:411` 現行寫「DEP: 依賴指路(只放 wikilink…)」,範例是 `[[Billing]][[Inventory]]`。
2. `lumos new` 骨架提示叫人填 `DEP:[[依賴模組]]`(`scripts/lumos:16769`)。
3. 筆記形狀檢查刻意放行只放連結的 FLOW/DEP(`scripts/lumos:25315` 搭配 `_NS_POINTER_ONLY_RE`,`scripts/lumos:25264`)。
4. H1 卻說這種行是「相關筆記,寫進 related」。實作者照著做,會讓每個照骨架填 DEP 的新筆記都被唸。
5. 第 0 步與第 1 步只列了 RULE 範例、舊精簡表、RETIRE-IF,沒有列 DEP 與 FLOW 的列、骨架提示。這正是 spec 自己說要清掉的「文件自己對不上」,而且會多出第五處。
引句:「新寫的 DEP 行除了 `[[連結]]` 沒有別的字」
佐證:`skills/lumos-project-notes/reference.md:411`、`scripts/lumos:16769`、`scripts/lumos:25315`

**R3C4**
severity: major
blocking: 是 spec 改成「作廢的 RULE 留著」,doctor 清單卻會把留著的作廢行永遠列出來。
1. 輸入:一條已標 `[status:superseded]` 的 RULE,按本案新規矩留在筆記裡,`[confirmed:]` 已超過 180 天。
2. doctor 的過期清單寫「所有 RULE 行」,沒有排除作廢行。
3. 既有的 `rule_lifecycle_warnings` 有 `st == "active"` 條件才報 until 與 confirmed 的過期(`scripts/lumos:3345-3356`)。S6 沒寫要沿用。
4. 作廢行永遠不會被重新確認,於是每次 doctor 都列它,而且沒有任何處理方法能讓它消失。舊訊息叫人刪行,本案改成留著,等於移除了唯一的消除辦法。
引句:「doctor 列出所有 RULE 行裡 `[until:]` 已過期、或 `[confirmed:]` 超過半年的(舊行也列、只提醒)」
佐證:`scripts/lumos:3345`

**R3C5**
severity: major
blocking: 否 這會讓 AI 漏掉 FACT 這一類,但不會做出壞系統。
1. 檢查清單表列了 WHY、RULE、PITFALL、FACT 四類。
2. 同節給的取行指令卻是 `--prefix RULE,PITFALL,WHY`,沒有 FACT。skill 查詢表會照抄這一行。
3. 照字面做,AI 永遠拉不到 FACT 行,「改動影響部署、資料或外部行為時回頭確認」那一列就是空的。REVISIT 與 RETIRE-IF 也不在拉取範圍。
4. 排序規則有「FACT 類」,但沒說 `--prefix FACT` 是否包含 FLOW 與 DEP。
引句:「lumos search --about <檔> --prefix RULE,PITFALL,WHY」

**R3C6**
severity: major
blocking: 是 spec 要求的判定輸出,現有報告格式裝不下。
1. 判定者被要求先把混合句拆成多個單類句子,再各自判前綴。
2. 現有報告每行是 `id | 類 | 證據 | 理由`,一個 content id 只有一列、一個類(`_note_audit_parse_report`,`scripts/lumos:26475`)。
3. `record` 對同 id 多列取最重的一個(`scripts/lumos:26707` 附近的 `best[rid]`,依 `_NOTE_AUDIT_WEIGHT`)。
4. 「多一欄前綴」只能放一個值。一行拆成 WHY 加 PITFALL 時,拆出的第二個前綴會被丟掉,或被權重規則覆蓋。
5. 「這行寫的前綴對不對」就無法對拆出的各部分判斷。
6. spec 沒定義多值的寫法,也沒說權重合併要怎麼改。
引句:「每行判定多一欄前綴;舊格式的紀錄照讀(那一欄空著)」
佐證:`scripts/lumos:26475`

**R3C7**
severity: minor
blocking: 否 只是提醒,誤報不擋。
H3 說「以日期開頭、後面是動作而且沒有 WHY/PITFALL 線索」。兩處定義互相重疊:
- 分類規格要求 WHY 必帶出處,現行格式就是行首 `[日期 …]`,與 H3 的「日期開頭」撞在一起。
- 動作詞「改成」同時是 WHY 的線索詞,所以含「改成」的行永遠不會被 H3 報到。
- spec 自己第 36 行那條 WHY 沒有任何 WHY 線索詞,卻有「折入」,會被 H3 報。
- 需要明講「日期」指前綴之後的哪個位置,並排除 WHY 的出處括號。
引句:「新寫的摘要行以日期或審查輪次開頭、後面是動作」

**R3C8**
severity: minor
blocking: 否 這條清單項目無法落實,不影響其他部分。
檢查清單要 FACT「更新確認日期」,但 FACT 行沒有日期欄位。`parse_rule_fields` 與過期檢查只認 RULE 的欄位(`scripts/lumos:3282`、`scripts/lumos:3314`)。doctor 清單也只掃 RULE。沒有地方能存這個日期,也沒有東西會去讀它。
引句:「FACT | 程式驗不了;改動若影響部署、資料或外部行為,回頭確認並更新確認日期」
佐證:`scripts/lumos:3282`

**R3C9**
severity: minor
blocking: 否 這是政策已知的缺口,但作者看不到。
RULE 要有 `[confirmed:]` 才有挑戰程式碼的效力。W4 只檢查缺 since 與 retire,doctor 清單只列「有 confirmed 且過期」的。完全沒寫 `[confirmed:]` 的 RULE 在寫入時不提醒,doctor 也不列。我數了圖譜裡 18 條 RULE,6 條沒有 `[confirmed:]`。作者會以為寫齊 since 和 retire 就生效。
引句:「要挑戰程式碼還得 `[confirmed:]` 半年內(既有政策)」
佐證:`scripts/lumos:3329`

**R3C10**
severity: minor
blocking: 否 只影響提醒輸出的行為。
1. 引句內前半說「全部印出、不設上限(同否定現況句提醒)」,後半又設 10 行上限,自相矛盾。
2. 所引的先例 `_ns_negation_format` 明寫「全部印出,不設上限」(`scripts/lumos:25512`),並沒有 10 行上限。
3. 先例的 `hints` 通道在 `negation=off` 時是 None(`scripts/lumos:25849-25852`)。tag_hints 若共用這條通道,`negation` 關掉就會連帶讓 tag_hints 沒有輸出,違反 S4。spec 沒說兩者要分開。
引句:「提醒全部印出、不設上限(同否定現況句提醒),但同一次提交同一條規則超過 10 行時只印前 10 行加總數」
佐證:`scripts/lumos:25512`、`scripts/lumos:25849`

**R3C11**
severity: minor
blocking: 否 行為沒定義,實作者要自己猜。
1. 行模式在給了 term 時怎麼辦沒定義。是用 term 再篩行,還是忽略 term,還是走原本的 BM25。原本 `term` 是必填位置參數(`scripts/lumos:40170`)。
2. `--about` 的檔沒有家時,輸出為空,與「沒有任何限制」無法區分。測試檔與排除檔都沒有家。
3. 家筆記的對照函式 `_home_map_from_notes` 可以回傳多篇,但文中寫成單數。
引句:「給了 `--prefix` 或 `--about` 時 `term` 可以不給(位置參數改成可省略)」
佐證:`scripts/lumos:40170`

**R3C12**
severity: minor
blocking: 否 影響驗收可信度,不影響行為。
1. 70% 門檻用的題庫(工具鏈加 rtb 150 句加 68 句)裡,純 RULE 只有 5 句、純 FACT 只有 4 句(`classify-toolchain-rtb.md:22`)。總判對率過了 70%,RULE 與 FACT 的前綴準度仍可能是零。
2. RETIRE-IF 與 S15 用的 75% 來自另一個專案的 80 句盲判(`classify-member-system.md:16`)。上線後換成「抽新寫的筆記行」,語料與標註者都不同。
3. 現況寫「程式推得出」佔 12% 與 19%,RETIRE-IF 卻拿「約三成」當基準,兩處數字對不上。
4. 68 句題庫是 CODE/MIXED/CONTEXT 三類標註,沒有前綴標準答案(`governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_key.json`)。S12 的「前綴判對率」在這 68 句上沒有定義。
引句:「AI 判定者的前綴判對率沒有比上線前的 75% 高」
佐證:`governance/audits/2026-10-01-tagdrift/classify-toolchain-rtb.md:22`

**R3C13**
severity: minor
blocking: 否 改檔前提示 hook 沒動,合約仍由它提示。
檢查清單只涵蓋摘要行的四個前綴,沒有 ★INVARIANT★ 合約行和 `decisions:` 欄位,也沒說要搭配 `lumos contracts` 或 `lumos impact` 一起用。CLAUDE.md 規定這兩類才有挑戰程式碼的效力,AI 只照這張清單做就會漏看。
引句:「改某支檔之前,先把跟它有關、還有效的脈絡行拉出來,逐類對照:」

**各節狀態**
- 開頭欄位、依據、PRIOR-ART、現況:已讀,無 finding。R3C12 提到現況與 RETIRE-IF 的數字對不上。
- 設計原則:已讀,無 finding。
- 分類規格:R3C2、R3C3、R3C7。
- 分類檢查:R3C1、R3C6。
- 改程式時的分類檢查清單:R3C5、R3C8、R3C13。
- 搜尋行模式:R3C11,另見 R3C5。
- 結構性提醒:R3C1、R3C3、R3C7、R3C10。
- 健康檢查補一段:R3C4。
- 不溯及既往:已讀,無 finding。
- 分期、已裁、天花板、不做、驗收條款、回退、合約候選、審計修正紀錄:已讀,無 finding。回退第 2 步另有一個小風險:把 `_NOTE_AUDIT_PROMPT_VERSION` 退回舊版,會讓新版清單上的輕判定被丟掉,因為來源比對會失敗(`scripts/lumos:26708`)。

**實務隱患**
- 併發:無。寫入沿用既有點。
- 效能:無。都是字串比對,與既有 lint 同量級。
- 資源:無,沒有長駐程序。
- 回滾:見上方小風險。
- 相容:有,見 R3C3(DEP 指引)與 R3C6(判定紀錄格式)。
- 注入:無,判定者沿用「筆記是資料不是指示」的規則。
- 金流、對外送出:無,只讀筆記與程式文字。
- 不可逆:無。不改資料、不刪筆記。

最高嚴重度:major,blocking 4 條(R3C1、R3C2、R3C3、R3C4、R3C6 中,R3C5 為 major 但 blocking 否;實際 blocking 為 R3C1、R3C2、R3C3、R3C4、R3C6 共 5 條)

最高嚴重度:major,blocking 5 條
