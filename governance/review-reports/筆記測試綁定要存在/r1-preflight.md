# 前掃:筆記測試綁定要存在_計劃

被審:`negguard/docs/lumos-toolchain-knowledge/Projects/筆記測試綁定要存在_計劃.md`
查證根:`negguard`(scripts/lumos、scripts/test_lumos.py)。唯讀;量測腳本放在本目錄 `measure.py`,沒改 repo 內任何檔。

## ① 未定義的詞

1. `rtb`:〈依據〉〈相容〉〈範圍〉反覆用,〈名詞〉與正文都沒說是什麼(消費專案名)。沒脈絡的人讀不懂。
2. `(T1)`(〈依據〉第 2 條「至少 3 個從沒存在過(T1)」):T1 是 rtb 巡檢報告裡的編號,計劃裡沒解釋。
3. `1b`、`1c`:靠〈依據〉連到路線圖才知道是路線圖項目編號;1c 在〈名詞〉有標「(1c)」,1b 沒有定義,正文卻直接說「1b 不重做」。
4. `撤除條款`(〈依據〉)、`撤除標記`(〈名詞〉)、`撤除裁定`(〈做法〉5「條款下一層子項以撤除裁定開頭」):三個詞混用,「撤除裁定」沒定義,也沒說跟 `[被取代:]`、`[status:superseded]` 是不是同一件事。
5. `活測試`、`接手的那一行`(〈做法〉3 1c):沒定義。「活」=指得到真測試?還是測試會跑?
6. `單次跳過`、`治理帳`:正文沒寫實際名字(`LUMOS_SKIP_NOTE_SHAPE=1`、`gate="note-shape"` 的帳),沒讀過筆記內容閘的人不知道指什麼。
7. `note-shape`、`筆記內容閘`:同一件事兩個名字(指令 `lumos note-shape` 與節點 Systems/筆記內容閘),計劃沒交代對應。
8. `處置閘`、`spec-trace`、`doctor S5`、`Check T`:〈名詞〉直接用,沒一句解釋。
9. `[防回歸:無 理由]`、`[repro:指令]`:只有 PITFALL 前綴才有這個三選一(`_SLOT_ONE_OF`);計劃沒說這是格子鍵、也沒說只對 PITFALL 成立,但 S3 對所有前綴都要求給這兩種改法。
10. 平台前綴 `平台:`(〈名詞〉):只有 `.lumos/config.json` 有 `platforms` 時才有意義(legacy 單平台整串含冒號不切分,會變 bad-name);計劃沒說。
11. 「測試檔有沒提交或沒暫存的改動」(〈做法〉4、S8):哪些檔算「測試檔」(各平台 root 下 profile 認的檔?)、怎麼偵測,沒定義。
12. 「既有新增行抽取的區塊判定」(〈做法〉1「程式碼區塊由呼叫端照…略過」):指哪個東西沒說。見 ④-5。
13. 「誤擋比例」(RETIRE-IF):誤擋怎麼數(誰來標「測試其實存在」)沒定義。見 ④-14。
14. 〈依據〉裡的提交編號 `a7b3b2d`、`ef9ae20`、`b2fc512` 是 rtb 的,不是本 repo 的;沒標「rtb 的提交」,讀者會拿去本 repo 查。(已標 rtb 的只有 a7b3b2d。)

## ② 壞引用

逐項在 repo 查過:

存在、名字對:`_classify_test_refs`(scripts/lumos:40248)、`_platform_test_index`(12856)、`extract_contracts`(4719)、`cmd_note_shape`(28551)、`[test:]`/`TEST_REF_RE`(4736)、`clause_bindings`(6613)、doctor S5(2365)、Check T(1626)、`_ns_superseded`(28189)、`_KILL_METHOD_OK_RE`(14110);筆記 `Projects/漂移防治路線圖_計劃`、`Projects/筆記格子寫法與過期檢查_計劃`、`Systems/筆記內容閘`、`Systems/check-t-sentinel`、`Systems/bound-tests-gate` 都在;路線圖 1b/1c 列在 42、43 行;格子計劃〈天花板〉第 3 條在 165 行,內容與計劃引用一致;路線圖的「循環」在 26 行。
鍵 `[防回歸:]`、`[repro:]`、`[被取代:]`、`[status:]` 都在 `_SLOT_KEYS`(3745)。

有問題:
1. **`[test-gone:]` 不是現有鍵**:`_SLOT_KEYS`(3745)沒有它,`slot_parse` 會把它當核心句文字。計劃〈實務隱患〉有講要登記進鍵表,算已知;但沒講也要進 `_SLOT_REPEATABLE`、紀律範本表(`t_slots_single_table` 釘範本與程式)、以及 PITFALL 三選一(見 ③-2)。
2. **治理帳的閘名**:〈做法〉5「`--ci` 記事件」要新閘名(照 S16/S5 的 `check-sNN`),必須加進 `_KNOWN_GATES`(7537)與 spec 說明表;計劃沒提。(不是壞引用,是漏列的必改點。)
3. **測試名前綴**:計劃八支測試都叫 `t_ns_…`,repo 內 note-shape 現有測試一律 `t_note_shape_…`(test_lumos.py:50155 起);`t_ns_` 這個前綴現在 0 支。不是錯,但跟鄰居命名不同;八支都還不存在(條款內 `[test:t_…]` 不算)。
4. 〈依據〉的量測數字:我用 `_classify_test_refs` 對本 repo 筆記重跑(摘要行、非合約行、帶 `[test:` 的行):**總數 373 成立**;指不到 **26 成立**(未剝反引號時)。但拆分對不上:`待補` 在摘要行只有 **4** 個(計劃寫 11)、真 dangling 3 個(成立)、bad-name 12、fake(非待補)7。11/12/3 的拆法我重現不出來(可能含正文行,摘要行範圍沒寫清楚)。另外剝掉反引號後有 10 行整行消失。
5. rtb 的數字(56 個、57 個、42 個、12 條、3 條)是外部倉庫,這邊查不到,未驗。

## ③ 範圍自相矛盾

1. **〈做法〉3「新寫的行」vs S2/〈相容〉「既有的不擋」**:程式裡「新寫」=diff 加到的行(`_notelines_parse_added`,27230),不是「語意上新」。動到舊行任何字(改錯字、補欄位)就整行算新寫,舊行上原本就指不到的 `[test:]` 會被擋。格子規則為此做了舊行豁免(`_ns_is_old`,28205),本計劃沒有,S2 只講「舊行上」,沒說被改過的舊行。
2. **修法「測試已刪就寫 `[test-gone:]`」vs PITFALL 三選一**:PITFALL 必須有 `test`/`repro`/`防回歸` 其一(`_SLOT_ONE_OF`,3753),`test-gone` 不在內;格子規則開著時(掛鉤帶 `--slots`),PITFALL 照指示改成 `[test-gone:]` 就會因缺三選一再被擋。計劃沒說 `test-gone` 算不算滿足三選一。
3. **S3 的兩種改法只適用 PITFALL**:WHY、RULE、一般行掛 `[test:待補]` 時,`[防回歸:無]` 在格子表裡不存在於它們的前綴(WHY/RULE 沒有這個鍵)。〈做法〉3 第 1 條有分「PITFALL 改寫…」,第 2 條(佔位字)與 S3 卻對所有行一律給這兩種改法。
4. **〈做法〉6 `note_shape.test_refs` 與總開關 `note_shape.gate`**:沒講優先序。程式前例(`_ns_slots_mode`,28135):gate=off 整道不跑、gate=warn 子規則也只提醒、其他才看子開關。計劃 S10/S11 只測自己的鍵。若 gate=warn 而 test_refs=block,結果沒定義。
5. **「一條規則」vs 治理帳沒有規則欄位**:〈做法〉3 說「違規清單、擋下、單次跳過、治理帳照既有」,RETIRE-IF 與 REVISIT 卻要「數這條規則的擋下與單次跳過事件」。既有帳只寫 `gate="note-shape"` + 「新違規 N 條」字串(28708),slots 才有額外欄位(`extra`);單次跳過 `LUMOS_SKIP_NOTE_SHAPE=1` 是整道閘跳過(28571),分不出是哪條規則。〈回退〉寫「沒有寫入新的帳本欄位以外的資料」,字面是「新帳本欄位」存在還是不存在,讀不出來。
6. **〈做法〉4「只提醒不擋」vs S8 與〈做法〉3**:〈做法〉3 說「提交與推送都跑、擋下」,〈做法〉4 又說「測試檔有未提交改動時只提醒」。提交時索引(暫存)與工作目錄不同是常態(測試檔改了沒 add);推送時終點提交與工作目錄不同也是常態。這兩種情形下規則多半只提醒,擋的範圍實際比〈做法〉3 寫的窄多少沒量化。
7. **〈範圍〉不做「合約行與條款定義行(各有檢查)」vs 檢查實況**:條款綁定懸空是「只提醒不擋」(`_clause_check`,`_CLAUSE_HANG_STATES`;doctor S5 標題寫「提醒,不擋」),且 S5 只看 `type: project` 非 superseded/stale 的筆記。「各有檢查」成立,但不是「擋」;而且〈做法〉1 要連非計劃筆記裡的 `[SN]` 開頭行也略過,那種行沒有任何檢查。
8. **〈範圍〉做:「doctor 多一段全庫提醒(含 1c 的關鍵字候選)」vs 〈名詞〉撤除標記只認標記**:rtb 那 12 條撤除條款是散文式「撤除裁定」小節,不帶 `[被取代:]`/`[status:superseded]`;規則(擋)抓不到它們,只有 doctor 關鍵字候選會列。依據裡的「12 條、3 條反面」與規則實際能擋的集合幾乎不重疊,計劃沒講這點。
9. **`[被取代:]` 單獨出現算不算撤除標記**:〈名詞〉寫「`[被取代:…]` 或 RULE 的 `[status:superseded]`」兩者並列;程式裡 `[被取代:]` 是 `[status:superseded]` 的附屬值(格子規格:標了 status 就必須有被取代,3925),單有 `[被取代:]` 沒有 status 的行,`_ns_superseded`(28189)判為沒作廢、doctor S17 也不看。見 ④-9。

## ④ 機械宣稱驗語意

格式:原句 → 程式實際(函式+行號)→ 成立/不成立/部分成立。

1. 「判測試存在用…`_classify_test_refs`(多平台、能分 real/fake/dangling/bad-name)」→ 成立。`_classify_test_refs(text,node,split,default,methods_for,hay_for)` 40248:`resolve_test_refs` 丟 ValueError → 一筆 bad-name;名稱過不了 `_KILL_METHOD_OK_RE` → bad-name;在 `methods_for(plat)`(含 `Class.Method`)→ real;只在 `hay_for` 子字串 → fake;都沒有 → dangling。
   - 補充(影響訊息):未定義平台前綴時整段文字只回**一筆** bad-name,名稱欄是錯誤訊息前 60 字(`"?"` 平台),同一行其他 ref 不再單獨判;計劃「印哪個名稱、判成哪種」在這種情形印的是錯誤字串不是名稱。
   - 補充:`[test:待補]` 在本 repo 判成 **fake**(「待補」二字在測試檔的程式文字裡出現),不是 dangling;其他專案可能是 dangling。S3 要靠字面比對單獨處理,不能靠判定種類。
   - 補充:fake 是子字串比對,`a`、`x`、`X` 這種短名會判 fake,見本 repo 的範例行。
2. 「`_platform_test_index` 讀的是工作目錄」(〈做法〉4)→ 成立。`_platform_test_index(repo_root)`(12856)呼叫 `load_platforms(repo_root)` 讀 `repo_root/.lumos/config.json`(5084,讀磁碟)與 `discover_test_methods(root, profile)` 掃磁碟上的測試檔(5416);沒有任何「某個版本」的參數。推送前合約測試閘(`_bound_tests_for_diff`,40305)用同一個、也是 `repo_root`(工作目錄)。**但**:note-shape 本身的設定(`note_shape.*`)與筆記內容是從被檢查的版本讀(提交=索引、推送=終點提交,見 `cmd_note_shape` 28618 docstring);所以同一次檢查裡,筆記與 `note_shape.test_refs` 讀版本、`platforms`/測試檔讀工作目錄,兩邊設定來源不同。
   - 另:`load_platforms` 設定壞(兩個平台沒 default 等)會丟 ValueError;`_bound_tests_for_diff` 吞成 `no-config`(fail-open),Check T 也吞。計劃沒寫索引建不起來時 note-shape 要怎樣(note-shape 整體立場是 fail-open,28557)。→ 計劃缺這一條。
3. 「`_classify_test_refs` 的參數」:計劃只說「每個 `[test:]` 交給它」。實況:它收的是一**段文字**(內含 `[test:…]`),不是單一 ref;餘下四個參數是 `_platform_test_index` 回傳的 split、default、methods_for、hay_for(回傳是六值,第 6 值 `loose_for` 不用)→ 部分成立(「每個交給它」其實是整行/去反引號後的整段文字交給它,一次判該行全部 ref)。
4. 「note-shape 提交時與推送時從哪裡讀內容」→ 計劃〈做法〉4 只講測試索引。實況:`cmd_note_shape`(28551):提交 `staged` → `base_where=HEAD, tip_where="index"`,內容與 `.lumos/config.json` 都用 `_nodehome_reader(root, tip_where)` 讀索引;推送 `--diff A..B` → `tip_where=終點 sha`,內容與設定讀終點提交。新增行:提交 = `git diff --cached` 的新增行(`_notelines_new` 27344);推送 = 範圍逐提交各自新增的行(`_notelines_range_added` 27250),排除主線已有、排除「寫的時候掛鉤還沒帶 `note-shape --staged` 記號」的提交,且「終點版本裡還在」才算。→ 〈名詞〉「新寫的行:這次提交或推送範圍裡新增、終點還在」成立。
5. 「程式碼區塊由呼叫端照既有新增行抽取的區塊判定略過」(〈做法〉1)→ **不成立(說法不準)**。`_notelines_new`/`_notelines_regions`(27131 起)的「區塊」是 body/summary/decisions/other 四種版面區,**沒有 fence 概念**;被丟掉的是 `other`(開頭欄位其他欄)。圍欄判定在 `_note_shape_eval` 另算:`vis = {no for no,_ in _visible_lines(...)}`(28422),目前只給 `_ns_revisit_violations` 用(`_ns_check_line` 還用 `keep_fences=True` 連圍欄內都掃)。要略過圍欄得新用 `vis`;要略過反引號得用 `_strip_inline_markup`(368)——它「未閉合反引號之後一律不信」,會把同一行未閉合反引號後的真 `[test:]` 也略過(寧可少認),計劃〈名詞〉寫「反引號裡的不算」沒提這個後果。
6. 「合約行:摘要裡 `KEY:★INVARIANT★` 開頭的行(`extract_contracts` 抽得到的)」→ 成立但有細節。`extract_contracts(note)`(4719)吃的是 note 物件,只掃 `fields["summary"]` 的每個**實體行** `strip()` 後比 `INVARIANT_RE`(4689:`^KEY:\s*(?:\([^)]*\)\s*)?★INVARIANT★`),同時回 `★DEBT★`;**不抽** `★CHECKPOINT★`、`★IRREVERSIBLE★`(它們有各自的 RE,4777 附近)。計劃的 `_note_test_refs(line)` 只有一行文字,要略過合約行得自己用 `INVARIANT_RE`,且不能分辨該行是不是在 summary(body 裡的 `KEY:★INVARIANT★` 不是合約,也不會被 Check T 看)。DEBT 行有 `[test:]` 也不被略過。
7. 「合約行…已由 doctor Check T 與推送前合約測試閘驗存在並真跑」→ **部分成立**。Check T(1626)只驗存在(doctor 不執行測試,見 `discover_test_methods` docstring 與 5419),不真跑;推送前合約測試閘 `_bound_tests_for_diff`(40262)只處理「這次 diff 波及到、且釘住的節點」的合約行(`pins`),不是全庫;真跑是另一支測試跑閘。所以全庫合約行靠 Check T 驗存在,「真跑」只對波及節點成立。
8. 「條款定義行:計劃裡 `[SN]` 開頭的驗收條款,已由條款綁定(spec-trace、doctor S5、處置閘)管」→ **部分成立**。`clause_bindings`(6613):定義行 = 該 id **第一次**出現在行首(`_CLAUSE_LEAD_RE`,6161,去列表符號/標題/粗體)的那一行,只看 `_visible_lines`+`_strip_inline_markup` 後看得見的字;只有計劃(doctor S5 限 `type: project`、非 superseded/stale)。測試懸空只**提醒不擋**(處置閘 `_clause_check`:`hang` 只印「只提醒不擋」;風險低門 `door=low` 才要求測試存在)。「定義行」要看整份文字(第一次出現、同編號重複),單行函式 `_note_test_refs(line)` 判不出;只能近似成「行首是 `[SN]`」。
9. 「撤除標記:筆記格子的作廢鍵 `[被取代:…]`,或 RULE 的 `[status:superseded]`」→ **部分成立/說法與程式不一致**。程式裡「作廢」只由 `[status:superseded]` 決定:`_ns_superseded(line)`(28189)= `slot_parse` 的欄位裡有 `status=superseded`(任何前綴、不限 RULE,且 `slot_parse` 對整串 `[鍵:值]` 掃,與前綴無關)。`[被取代:]` 只是作廢行必帶的接手說明(`_slot_check_values` 3925:status=superseded 才檢查被取代;反方向沒有檢查)。doctor S17(`_doctor_replacement_lines`,3573)也是先 `_ns_superseded` 才看被取代。→ 單有 `[被取代:]`、沒 status 的行,現有程式不視為作廢;計劃若要抓這種行是新判定,不是「既有的」。RULE 的 status 另有 RULE 專用解析:`parse_rule_fields`(3382:新文法走 `slot_parse`,舊寫法走逐鍵正則 `_RULE_FIELD_RES`)→ `rule_lifecycle_warnings`(3703)。所以「由哪支解析」有兩支:RULE 生命週期用 `parse_rule_fields`;筆記格子/note-shape/doctor S17 用 `_ns_superseded`(同 `slot_parse`)。舊寫法的 RULE 行:`parse_rule_fields` 的正則版與 `slot_parse` 對「值裡有 `]`」的切法不同,同一行兩支可能得出不同 status(沒實測,未驗)。
10. 「新寫的行用筆記內容閘既有的…抽取與擋下、單次跳過、治理帳流程(note-shape)」→ 部分成立。擋下流程 `_note_shape_report`(28685):違規元組 `(路徑, 行號, 規則, 片段, 改法)`,`gate=block` rc1、`warn` rc0,記 `blocked`/`warned` 帳;單次跳過 `LUMOS_SKIP_NOTE_SHAPE=1` 在 `cmd_note_shape` 開頭整道跳過、記 `skipped-env`(28571)。但:**違規是一個全域模式**——想讓 `test_refs` 與其他規則各自 block/warn,既有前例是**另開一組**(slots:`_note_shape_slots_parse` 28113 + `_ns_slots_mode` 28135 + 自己的收集/報告,`_note_shape_report` 的 `slot=` 參數),不是往同一個 `viol` 加規則;往 `viol` 加就只受 `note_shape.gate` 管,`warn`/`off` 子鍵要自己接。另外,推送時的「還沒上線的提交不查」用 note-shape 的掛鉤記號(`_NOTE_SHAPE_GOLIVE_MARK`,27107);格子為了「新規則比 note-shape 晚上線」另設 `mark2`(`--slots`),本計劃沒有第二個記號,於是消費專案升級後、推送範圍內升級前寫的提交,若其行掛壞 `[test:]`,推送時會被當新寫擋。
11. 「`note_shape` 設定怎麼讀(有沒有每條規則的子鍵前例)」→ 有前例,計劃說「跟 note-shape 其他規則同一處讀」**部分成立**:`note_shape.gate`(`_note_shape_config`,27131,回 `(mode, warnings)`,兩處以二值解包呼叫,註解明說不要擴充它)、`note_shape.negation`(27825,warn/off)、`note_shape.tag_hints`(27888,warn/off)、`note_shape.slots`(28113,block/warn/off,壞值照 block 並提醒一句)。每個子鍵各有自己的 `_…_parse` 函式、都讀同一份 `.lumos/config.json`(被檢查版本),壞值語意各寫各的。計劃的 `block|warn|off` 與 slots 同形;但沒寫壞值(例如大寫、非字串)怎麼辦、也沒寫要不要新寫第五支 `_note_shape_test_refs_parse`。
12. 「doctor 既有提醒段的寫法」「提醒、不擋、`--ci` 記事件」(〈做法〉5)→ 部分成立。doctor 段寫法:`section("Sxx", …)` + `warn_soft(lines, head, advice)`(1354):不動 `issues`,不影響 rc(S9「不影響回傳碼」成立);預設每段只印 3 條、`--verbose` 或 `--ci` 全列(`_verbose = verbose or ci`,1349)。`--ci` 才落帳:`gov_events.append({"gate":"check-sNN",...})`,於 3272 的 `if ci:` 區塊一次 `_append_governance_log`(S16 前例,2502)。注意:(a)格子的 S17/S18/S19 刻意**不寫帳**(註解 2509-2512:同批每次重唸會灌水),本計劃要寫就是跟最近三段相反;(b)新閘名要先登記 `_KNOWN_GATES`(7537),且要 `check-` 開頭才被 `doctor-run` 統計(3276);(c)S17 `[被取代:]` 一跳只在完整 doctor 跑、`--ci` 不跑,是因為它「不讀 git」;本計劃那段要建測試索引(掃磁碟測試檔),`--ci` 也要跑,成本在 CI 的 doctor 裡多一次全掃。
13. 「doctor 全庫提醒:列出所有筆記(不分新舊)指不到的 `[test:]`」→ 部分成立。doctor 讀的是 Env 內存的筆記全文;可行,但要自行抽取每一行(含正文)。注意 Check T(1626)用的是**自己的內嵌迴圈**,不呼叫 `_classify_test_refs`;計劃〈依據〉稱「另外三份同類判法不再新增第四份」,repo 內確有:Check T 內嵌迴圈、`_classify_one`(12896,clause_bindings 與 guard list 用)、`_classify_test_refs`(40248,推送前合約閘與修正關卡用)。三份之說大致成立;新規則用 `_classify_test_refs` 是第三個呼叫者而不是第四份。
14. 「RETIRE-IF:擋下事件裡超過一半是誤擋;REVISIT:數 note-shape 這條規則的擋下與單次跳過事件」→ **不成立(量不到)**。見 ③-5:帳只有閘級事件,無規則欄位;誤擋(「測試其實存在、索引沒認出」)沒有任何機制標記,帳裡沒有「誤擋」事件種類(`_SLOT_METRIC_KINDS`:blocked/warned/skipped-env/hinted/acked)。要依 RETIRE-IF 判斷得先加欄位或另設標記,計劃沒列。
15. 「測試索引…整次檢查建一次」「只在範圍裡有帶 `[test:]` 的新寫行時才建」(〈做法〉2、〈實務隱患〉時間)→ 部分成立。`methods_for`/`hay_for` 是惰性、每平台各算一次並快取(12871),成立;但 `_platform_test_index` 本身一呼叫就 `load_platforms`(讀設定),且 `discover_test_methods` 對本 repo 的 test_lumos.py(約 63k 行)是整檔掃、`hay_for` 還要整個 root 的程式文字(`build_code_haystack`),只要有任一個 ref 不是 real 就會觸發 haystack 的建立(fake/dangling 的分辨用)。「幾秒」我沒量,未驗。
16. 「`[test-gone:名稱@提交]`…只驗寫法與那個提交在 repo 裡」(〈名詞〉)→ 不是現有判定,是新寫。現有的最接近的是 `_ns_pin_ok`(27551,先 `_pin_commit` 要至少 12 位、在某個分支歷史上,再驗那個提交裡那支檔那一行)。節點 筆記內容閘 的 PITFALL(35 行)記過「只查提交物件存在會被 `git commit-tree` 在本機捏造的提交繞過」;計劃寫「提交在 repo 裡」沒講用哪一種(物件存在 vs 在分支歷史上),也沒講淺層 clone 的 CI(`cmd_note_shape` 28585 淺層直接跳過,doctor 也不保證有歷史)上找不到提交會怎樣。→ 不成立的是「沿用既有」之說;這是新判定,且前人踩過的坑沒帶進來。
17. 「S9…doctor 應…不影響回傳碼 [test:t_doctor_note_test_refs]」→ 成立(warn_soft 不動 issues,1354)。
18. 「S8 當測試檔有沒提交或沒暫存的改動時…」→ 現有程式沒有可直接用的「平台 root 下測試檔是否 dirty」函式(我搜了 `git status`/`diff --quiet` 相關,沒有針對平台測試根的現成);要新寫。計劃〈做法〉4 沒標明是新寫還是借用。
19. 「S4/S5:`[test-gone:]` 提交在 repo 裡」→ 同 ④-16。
20. 「2026-10-02 …本 repo 合約以外帶 `[test:]` 的摘要行 373 行」→ 成立(我重算 373);「指不到的 26 個」成立;拆分(11 待補/12 範例/3 真錯)我重現得 4 待補 + 12 bad-name + 7 fake(非待補)+ 3 dangling,見 ②-4。

## 順手記錄(不是設計建議)
- 我跑量測時 `negguard` 的 `docs/.canary-log.jsonl`、`docs/.governance-log.jsonl` 是已修改狀態,修改時間(22:17)早於我開始量測的時間;不是我寫的,應是那邊另一個會談。
