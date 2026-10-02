---
type: project
status: doing
created: 2026-10-02
updated: 2026-10-02
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/筆記內容閘
  - Systems/lumos-cli-read
  - Systems/bound-tests-gate
related:
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Projects/筆記格子寫法與過期檢查_計劃]]"
  - "[[Systems/筆記內容閘]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Systems/lumos-cli-read]]"
---
# 筆記測試綁定要存在_計劃

白話:筆記裡寫 `[test:測試名]` 是在說「這件事有這支測試守著」。現在只有合約行(★INVARIANT★)與計劃的驗收條款會核對那支測試真的存在;摘要裡的 WHY、PITFALL、RULE 和正文裡的 `[test:]` 寫錯名字、或測試後來被刪了,沒有任何地方發現,讀的人會以為有守衛。這份計劃做兩件事:①新加進筆記的測試名指不到真測試就擋(全庫既有的只在健康檢查提醒);②這次新寫的作廢條目還掛著活的測試就擋——那支測試守的是已經不成立的事,常常還是相反的事。

依據:
- 路線圖 1b(所有筆記的測試名要驗存在)、1c(撤除的東西不准再掛活測試)([[Projects/漂移防治路線圖_計劃]]);Enzo 2026-10-01 裁順序,2026-10-02 裁三件:推送擋新寫的、全庫只提醒;新寫的 `[test:待補]` 不准、改寫防回歸無;1c 同一案。
- rtb(另一個用 lumos 的消費專案)2026-10-01 全圖譜巡檢:懸空 `[test:]` 56 個、至少 3 個從沒存在過;撤除條款仍掛活 `[test:]` 12 條、3 條綁的是斷言反面的測試(在 rtb 的 repo 裡:提交 a7b3b2d 的 governance/audits/2026-10-01-drift-sweep/findings.md)。
- 2026-10-02 用最新 lumos 對 rtb 的唯讀副本(rtb 的提交 ef9ae20)量測:計劃正文還有 57 個指不到的(42 個是測試在 rtb 的提交 b2fc512 被刪)、摘要 1 個。本 repo 合約以外帶 `[test:]` 的摘要行 373 行,指不到的 26 個:4 個 `待補` 佔位、12 個文件裡的範例寫法(平台前綴沒定義,判成名稱不合法)、7 個其他「只出現在程式文字裡」、3 個哪裡都沒有。
- [[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3:格子只驗 `[test:]` 有寫,存在交給本案。

PRIOR-ART: 全部沿用既有零件——判測試存在用推送前合約測試閘那一支 `_classify_test_refs`(多平台、分 real/fake/dangling/bad-name;本案是它第三個呼叫者,不另寫判法;一次送一個名稱,同修正關卡的用法);測試索引 `_platform_test_index`;摘要接回續行 `_ns_summary_logical`、圍欄 `_visible_lines`、條款定義行 `_CLAUSE_LEAD_RE`、合約行 `INVARIANT_RE`、作廢 `_ns_superseded`;規則自己一組開關、自己的違規清單、帳本 `extra` 欄的鍵,照筆記格子規則(`note_shape.slots`)的形狀;全庫提醒照 doctor S17–S19 的寫法(不寫帳)。新寫的只有:吃全文的名稱次數抽取、到被檢查版本的測試檔整字複查(`git grep`)。世界解:文件連結檢查工具(如 lychee、Sphinx linkcheck)也是「新寫的擋、存量另列」;`[test-gone:]` 沿用 rtb 2026-10-01 標籤提案,提交編號改成選填。
RETIRE-IF: 上線滿 8 週,抽查帳上 20 筆這條規則擋下的測試名,其實存在、是索引沒認出的超過一半 → 規則改回只提醒;或滿 8 週全部專案零擋下、doctor 這段也沒列出任何新的 → 擋留著、doctor 段降到 `--verbose` 才印。
REVISIT:2026-12-01 照帳上 note-shape 事件的 `test_refs` 欄位數擋下次數與名稱,抽 20 筆判 RETIRE-IF;順便看單次跳過時記下的 `test_refs` 條數。

## 名詞

- **note-shape / 筆記內容閘**:`lumos note-shape` 指令,提交前掛鉤跑 `--staged`、推送前與 CI 跑 `--diff 起點..終點`;節點 [[Systems/筆記內容閘]] 管它。**被檢查的版本**:提交時是提交索引、推送時是範圍終點(note-shape 讀筆記與 `note_shape.*` 設定都從這裡)。**單次跳過**:環境變數 `LUMOS_SKIP_NOTE_SHAPE=1`,整道跳過一次並記帳。**治理帳**:`docs/.governance-log.jsonl`,各道閘的事件。
- **測試名**:筆記裡 `[test:名稱]` 的名稱。認得的寫法跟筆記格子對齊:鍵不分大小寫、半形或全形冒號、方括號內外的空白;同一個方括號可用半形或全形逗號列多支;名稱外圍的反引號拿掉;設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱。整個方括號落在反引號裡(例:寫成程式碼的 `` `[test:t_x]` ``)或程式碼圍欄裡的不算——那是範例;反引號沒閉合時,那之後到行尾不算。
- **一條**:摘要裡一個前綴條目接回續行後的整條(單行寫法的 summary 整個值算一條);正文裡一個實體行。
- **指得到真測試 / 指不到**:名稱逐一(一次一個,不整行)交給 `_classify_test_refs`,再到被檢查版本的測試檔整字找(〈做法〉3)。兩邊都說有才算指得到,兩邊都說沒有才算指不到;兩邊說法不同時算判不了,不擋(寧可少擋)。`_classify_test_refs` 的 `fake`(名字只出現在程式文字裡、不是測試方法)、`dangling`(哪裡都沒有)、`bad-name`(平台前綴沒定義或名稱不合法)都是它那一邊的「沒有」。
- **新加的測試名**:這次改到的筆記(含新增、刪除、改名的兩端)裡,某個名稱在終點版本的總次數多於起點版本的總次數,多出來的那幾次就是新加的。名稱從一篇搬到另一篇、從一行搬到另一行、筆記改名、摘要重排折行,次數不變,都不算新加。
- **合約行**:摘要裡接回後符合 `INVARIANT_RE` 的條目(`extract_contracts` 同一判法),已由 doctor Check T(合約有沒有綁到真的測試)驗存在,波及到的另由推送前合約測試閘真跑。**條款定義行**:計劃(type: project)裡符合 `_CLAUSE_LEAD_RE`、且是那個編號第一次出現的行(`clause_bindings` 同一判法,`- [S1]` 也算),由條款綁定管(spec-trace 列狀態、doctor S5 提醒)。這兩種上的測試名本案不算次數、也不查。
- **明標刪除**:`[test-gone:名稱]` 或 `[test-gone:名稱@提交]`——這支測試已經刪了,提交編號選填(只當追溯線索:不驗它存不存在,格子只驗寫法——有 `@` 時後面至少 7 碼十六進位;同一個提交裡刪測試、或推送前壓提交都寫得出來)。驗的是內容:名稱現在不能是真測試(還指得到就是假話)。它不算 PITFALL 防回歸那一格——測試刪了就是沒有守衛,PITFALL 要另寫 `[防回歸:無 理由]`。
- **作廢的條目**:帶 `[status:superseded]` 的一條(`_ns_superseded`;筆記格子規定另必帶 `[被取代:]`)。只有 `[被取代:]` 沒有 status 的不算。**活測試**:指得到真測試的測試名。
- **佔位字**:去掉平台前綴後名稱整個是 `待補`、`待定`、`TODO`、`TBD`(不分大小寫)其中之一。

## 範圍

- 做:note-shape 多一組規則「新加的測試名要指得到」與「作廢的條目不准掛活測試」(提交與推送都跑);認得 `[test-gone:]` 並登記成格子鍵;doctor 多一段全庫提醒(含散文撤除的候選);設定 `note_shape.test_refs`。
- 跟使用者裁定的差別:Enzo 裁的是「推送時擋」;本計劃讓同一條規則在提交時也跑、也擋(提早回饋,判法與逃生口相同),實作前請 Enzo 確認。
- 不做:合約行與條款定義行(各有檢查);不真跑測試;不自動把指不到的改成 `[test-gone:]`(要人判刪了、改名還是寫錯);不清 rtb 或本 repo 既有的(各自清,見路線圖的循環);散文寫的撤除(rtb 那 12 條的寫法)不擋,只在 doctor 列候選——判不準,詳〈實務隱患〉;不改 PITFALL 的三選一。

## 做法

1. **抽取**:新寫一支吃全文的 `_note_test_name_counts(text, is_plan)`(自己的寬鬆正則,不用合約行那支嚴格的 `TEST_REF_RE`,也不用只吃摘要條目的 `slot_parse`——要同時吃摘要與正文、又要對齊格子認得的寫法);開頭欄位只掃 summary,`decisions` 與其他欄不掃;摘要用 `_ns_summary_logical` 接回續行(單行寫法的 summary 照 `_note_summary_entries` 的補法,實作時抽成吃全文的一支兩邊共用),正文用 `_visible_lines` 略過圍欄;每一條找 `[test…]` 方括號(照〈名詞〉的寬鬆寫法),整個方括號落在反引號裡的略過;合約行與條款定義行略過。回「名稱 → 次數」與「名稱 → 第一次出現在哪篇哪一行」。`[test-gone:]` 另抽。
2. **新加的判定**:這次改到的筆記清單用 `git diff --name-status -z --no-renames 起點 終點 -- 知識庫`(提交時起點是 HEAD、終點是提交索引);起點那一側讀刪除與修改的,終點那一側讀新增與修改的;兩側各自加總次數相減,多出來的才查。起點是空樹時全部算新加。
3. **判存在**:有要查的名稱時才 `_platform_test_index` 一次;每個名稱單獨組成一段 `[test:名稱]` 交給 `_classify_test_refs`(工作目錄那一邊);再到**被檢查的版本**裡,各平台根下的測試檔用 `git grep -w -F`(提交時 `--cached`、推送時對終點)整字找這個名稱(去掉平台前綴)。兩邊都說沒有才算指不到、兩邊都說有才算指得到,說法不同不擋——工作目錄跟被檢查的版本不同(測試檔改了沒暫存、推的分支不是目前簽出的那條)時不會因此誤擋;漏網的交給 CI(CI 的工作目錄就是終點,兩邊一致)。同一套判法也用在「`[test-gone:]` 名稱還在不在」與 1c 的「活測試」。
4. **判不了就跳過**:索引建不起來(設定壞丟例外)、某平台的根不存在或掃不到任何測試方法時,那個平台的名稱這次不查、印一行原因(note-shape 本來就 fail-open)。
5. **違規**(這組自己的清單,跟其他 note-shape 規則分開收):
   - 新加的測試名指不到 → 印筆記、行號(這次新寫行上第一次出現的位置;只是次數變多、找不到新寫行時,報終點裡第一次出現的位置)、名稱、判定與改法:改成真的測試名;測試已刪就寫 `[test-gone:名稱]`——那一條是 PITFALL 時還要另寫 `[防回歸:無 理由]` 或 `[repro:指令]`(`[test-gone:]` 不算防回歸);沒有測試就拿掉,PITFALL 同樣改寫防回歸無或 repro。
   - 新加的是佔位字 → 一律違規,先於判存在(不靠判定種類,也不過複查:`TODO` 常出現在測試檔註解裡);訊息照那一條的前綴給改法。
   - 新加的 `[test:]` 方括號裡沒有任何名稱(`[test:]`、`[test:,]`)→ 違規(格子規則會把它當有寫)。
   - 新加的 `[test-gone:名稱]` 名稱現在指得到真測試 → 違規:測試還在,改回 `[test:]`。
   - (1c)作廢的條目掛著活測試,而且這一條是這次新寫的(接回後的整條在起點那一側——這次改到的所有筆記合起來——找不到一模一樣的,所以搬篇、改名不算新寫)→ 違規:改法是把綁定移到接手的那一條(`[被取代:]` 指的那裡),或拿掉;不建議改成 `[test-gone:]`(測試還在,那是假話)。舊的作廢條目只改了錯字也算新寫,會被擋——碰到了就順手修。
6. **開關與總開關**:`note_shape.test_refs: block`(預設)| `warn` | `off`,寫壞照 `block` 並提醒一句(同 `note_shape.slots`);總開關 `note_shape.gate` 是 `off` 整組不跑、是 `warn` 這組也只提醒。新寫一支 `_note_shape_test_refs_parse`(子鍵各有自己的解析,是既有前例)。
7. **接線與上線**:`_note_shape_eval` 之外另跑這組(它只看這次改到的筆記,不靠新寫行容器,也就不靠格子的 `--slots`)。不另設上線記號(格子規則有 `_SLOTS_GOLIVE_MARK`、要掛鉤帶旗標才開):本案判「新加」是比兩側次數,升級前寫好的提交只有真的新加了壞名字才會被擋,不會把整段歷史當新寫;消費專案 `lumos update` 換到新程式就開始擋,不必改掛鉤範本。`cmd_note_shape` 呼叫 `_note_shape_report` 的條件加上這組違規;報告裡這組另起一段標題「新加的測試名指不到真測試」,收尾句講這組的改法,不沿用「程式碼推得出來」那段。
8. **帳本**:這組有違規時,note-shape 那筆事件的 `extra` 欄多一個 `test_refs` 鍵(條數、前 20 個名稱與各自判定),跟格子那邊的鍵併在同一個 `extra` 字典裡;事件既有的違規種類欄照既有寫法再多列一項 `test_refs`;單次跳過時,提交與推送兩種都先算一次記進去(不靠 `--slots`)。RETIRE-IF 靠這欄抽查。
9. **格子鍵**:`test-gone` 登記進 `_SLOT_KEYS` 與 `_SLOT_REPEATABLE`;**不進** `_SLOT_NEW_ONLY`(舊寫法的行改寫成 `[test-gone:]` 時不該因此被當成新文法、被要求補齊新格子;rtb 有 42 處舊行要這樣改);**不改** PITFALL 的三選一。格子的 `slot_check` 只驗形狀(名稱非空;有 `@` 時後面至少 7 碼十六進位);名稱還在不在由本案這組查,兩邊不重複報同一種錯。紀律範本不動(`t_slots_single_table` 只比必有鍵、選擇題、條件鍵、列舉,選填鍵不在內;不動就不必升版與重注入);`[test-gone:]` 的寫法寫進 skill 指令速查 03-寫回圖譜與 reference.md。2026-10-02 跟筆記格子那邊的會談對齊過鍵表的形狀(它同意;「進四選一」那點本輪改回不進,會再跟它講)。
10. **全庫提醒**:doctor 新一段 S20(接在 S19 之後,實作時確認不落在既有截斷測試的視窗裡;標題含「提醒,不擋」,用 `warn_soft`,不用會擋的 `warn`;照 S17–S19 不寫帳)列出所有筆記指不到的測試名(過了複查還指不到的)、名稱還在的 `[test-gone:]`、作廢的條目掛活測試;另列散文撤除的候選:計劃裡條款定義行仍有 `[test:]`,而它的下一層子項(緊接在後、縮排比條款行深的連續行)裡有一行含「撤除」且不含「保留」。每類預設印 3 條、`--verbose` 全列;`--ci` 也跑(要建一次索引)。
11. **要同步的文件**:[[Systems/筆記內容閘]](這組規則)、[[Systems/lumos-cli-read]](doctor S20)、[[Systems/bound-tests-gate]](`_classify_test_refs` 多一個呼叫者)、[[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3 改指到本案;skill 指令速查 03-寫回圖譜、06-代碼審與推送(note-shape 擋下種類)、04-自檢與健康(S20)、INDEX、reference.md;`scripts/lumos` 的說明字典。

## 條款

- [S1] 當新加的測試名(合約行與條款定義行除外)指不到真測試、複查也找不到時,note-shape 應回 1 並列出筆記、行號、名稱與判定 [test:t_note_shape_test_refs_new_names]
- [S2] 當指不到的名稱是起點版本就有的、這次只是改了那一條的其他字、搬到別行或別篇、或筆記改名時,note-shape 應不擋 [test:t_note_shape_test_refs_new_names]
- [S3] 當同一條裡一個名稱平台前綴寫錯、另一個名稱是新加而且指不到時,note-shape 應把新加的那個單獨列出,不被前綴錯的那個遮住 [test:t_note_shape_test_refs_per_name]
- [S4] 當新加的測試名是佔位字而那一條是 PITFALL 時,擋下訊息應給 `[防回歸:無 理由]` 與 `[repro:]` 兩種改法 [test:t_note_shape_test_refs_placeholder]
- [S5] 當新加的測試名是佔位字而那一條不是 PITFALL 時,擋下訊息應叫人拿掉或改成真名、不給防回歸改法 [test:t_note_shape_test_refs_placeholder]
- [S6] 當新加的 `[test-gone:名稱]` 的名稱現在不是真測試時,note-shape 應放行(帶不帶 `@提交` 都一樣) [test:t_note_shape_test_gone_marker]
- [S7] 當新加的 `[test-gone:名稱]` 的名稱現在指得到真測試時,note-shape 應回 1 並叫人改回 `[test:]` [test:t_note_shape_test_gone_marker]
- [S8] 當方括號整個落在反引號裡或程式碼圍欄裡時,note-shape 應不算它 [test:t_note_shape_test_refs_skip_examples]
- [S9] 當名稱用大寫鍵、全形冒號或全形逗號寫、或名稱外圍包反引號時,note-shape 應照樣抽到並查 [test:t_note_shape_test_refs_lenient_syntax]
- [S10] 當新寫的作廢條目(續行接回後)掛著指得到的 `[test:]` 時,note-shape 應回 1 並建議把綁定移到接手的那一條 [test:t_note_shape_retired_line_live_test]
- [S11] 當工作目錄與被檢查版本的測試檔對一個名稱說法不同(一邊有、一邊沒有)時,note-shape 應不擋那個名稱 [test:t_note_shape_test_refs_checked_version]
- [S12] 當測試索引建不起來、或某平台的根不存在、或掃不到任何測試方法時,那個平台的名稱應跳過並印一行原因,note-shape 照其他規則判 [test:t_note_shape_test_refs_index_fail_open]
- [S13] 當 doctor 跑時,doctor 應在 S20 列出全庫指不到的測試名、名稱還在的 `[test-gone:]`、作廢的條目掛活測試與散文撤除的候選,並且不影響回傳碼 [test:t_doctor_note_test_refs]
- [S14] 當 `note_shape.test_refs` 是 `warn` 或總開關 `note_shape.gate` 是 `warn` 時,這組規則應只提醒不擋 [test:t_note_shape_test_refs_config]
- [S15] 當 `note_shape.test_refs` 或總開關是 `off` 時,這組規則應不跑 [test:t_note_shape_test_refs_config]
- [S16] 當這組規則擋下、或提交或推送時被單次跳過時,治理帳那筆事件的 `extra` 應帶 `test_refs` 鍵(條數與名稱) [test:t_note_shape_test_refs_ledger]
- [S17] 當新加的 `[test:]` 方括號裡沒有任何名稱時,note-shape 應回 1 [test:t_note_shape_test_refs_empty]
- [S18] 當 summary 是單行寫法、或名稱落在摘要條目的續行時,note-shape 應照樣抽到並算次數 [test:t_note_shape_test_refs_summary_forms]
- [S19] 當 `note_shape.test_refs` 寫成不認得的值時,這組規則應照 `block` 跑並印一句提醒 [test:t_note_shape_test_refs_config]
- [S20] 當舊寫法的 PITFALL 行只把 `[test:X]` 改成 `[test-gone:X]` 時,格子規則應不擋那一行,也不把它當新文法要求補齊新格子 [test:t_slots_test_gone_key]

## 回退

- revert 實作提交即可。已寫進筆記的 `[test-gone:]` 留著:revert 後格子規則不認得這個鍵,會把它當核心句文字,不擋;它本來就不算防回歸,PITFALL 不受影響。帳上多出的 `test_refs` 鍵舊讀端忽略。
- 只想先停擋:`note_shape.test_refs: warn` 或 `off`。

## 實務隱患

- **誤擋**:索引沒認出的測試寫法(參數化名稱、類別裡的方法)會被判指不到;複查用被檢查版本的測試檔整字找,找得到就放行,所以只會擋「測試檔裡根本沒有這個字」的名稱。`warn` 可退;RETIRE-IF 抽查帳上名稱。
- **漏網**:複查找得到就放行,名稱只要出現在測試檔裡(註解、字串)就過——寧可少擋;工作目錄有、被檢查的版本沒有的名稱在本機推送時放行,交給 CI。
- **散文撤除擋不到**:rtb 那 12 條撤除是「條款下一層寫一段撤除裁定」的散文,不帶 `[status:superseded]`,規則擋不到,只會進 doctor 候選(關鍵字判,排除含「保留」的)。要擋得住得在撤除時補標記——列進 rtb 清理的回傳要求。
- **時間**:只在有要查的名稱時才建索引與複查;本 repo 測試總檔約 6 萬行。實作時量一次提交與推送各多幾秒,寫進〈實作紀錄〉。doctor S20 每次全掃,CI 的 doctor 也會多這一次。
- **相容**:消費專案 `lumos update` 後,新加壞名字會被擋——本案本意;既有的不擋。升級前寫好、升級後才推的提交,只有真的新加了壞名字才擋。
- **跟筆記格子的接點**:只加一個鍵、不改三選一;動鍵表前跟那邊的會談再對一次。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀筆記與測試檔,不連網
- 已排除:不可逆:只擋提交與推送、只印提醒,revert 回得去
- 守衛面:新增一組提交與推送時的擋,有 `warn`/`off` 與單次跳過可退,單次跳過照記帳。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- r1(2026-10-02,4 席:正確性-opus、邊界-sonnet、整合-sonnet、架構對齊-sonnet):40 條/blocking 25/全折,無放行、無駁回。三席獨立抓到同一組根問題,換三個形狀:①判「新」從新寫行減整篇改成「這次改到的筆記兩側加總次數相減」(改名、搬行、折行、整篇佔次數都收掉),名稱一次送一個判(壞前綴不再吞掉整行);②拿掉「測試檔有改動就只提醒」(平台根常是 repo 根、提交時筆記自己就算改動,規則會永遠不擋),改成指不到的名稱到被檢查版本的測試檔整字複查;③`[test-gone:]` 提交選填、驗內容(名稱現在不能是真測試)、不算防回歸、不改三選一(同一提交刪測試或壓提交原本寫不出來;只驗形狀會讓假話過關)。其餘照補:寬鬆寫法對齊格子、摘要接回與單行 summary、條款行用 `_CLAUSE_LEAD_RE`、索引空的也跳過、帳本併進 extra 且推送時跳過也記、doctor 段給 S20 與子項定義、落點改 lumos-cli-read 與 bound-tests-gate、接線與報告標題。例:同一篇把一行 `[test:x_dead]` 搬到另一行並改一個字 → 修前擋、修後不擋;一行 `[test:bad:a, t_new_missing]` → 修前整行一筆 bad-name、修後 t_new_missing 單獨列出。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- 前掃(2026-10-02;其中「`[test-gone:]` 提交驗在分支歷史上」「進 PITFALL 三選一」兩點已被 r1 改掉):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/筆記測試綁定要存在/r1-intake.md`。動到做法的:判「新」的單位從「新寫的行」改成「新加的測試名」(舊行改字原本會被擋);規則自己一組開關與帳本欄位(照格子規則,否則量不到 RETIRE-IF);作廢只認 `[status:superseded]`;`[test-gone:]` 提交照 `_pin_commit` 判在分支歷史上;doctor 段不寫帳;`[test-gone:]` 進格子鍵表與 PITFALL 三選一。
