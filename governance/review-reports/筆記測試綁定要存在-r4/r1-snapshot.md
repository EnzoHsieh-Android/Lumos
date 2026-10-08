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

白話:筆記裡寫 `[test:測試名]` 是在說「這件事有這支測試守著」。現在只有合約行(★INVARIANT★)與計劃的驗收條款會核對那支測試真的存在;摘要裡的 WHY、PITFALL、RULE 和正文裡的 `[test:]` 寫錯名字、或測試後來被刪了,沒有任何地方發現,讀的人會以為有守衛。這份計劃做兩件事:①推送時,新加進筆記的測試名指不到真測試就擋(提交時只提醒;全庫既有的只在健康檢查提醒);②這次新寫的作廢條目還掛著活的測試就擋——那支測試守的是已經不成立的事,常常還是相反的事。

依據:
- 路線圖 1b(所有筆記的測試名要驗存在)、1c(撤除的東西不准再掛活測試)([[Projects/漂移防治路線圖_計劃]]);Enzo 2026-10-01 裁順序,2026-10-02 裁三件:推送擋新寫的、全庫只提醒;新寫的 `[test:待補]` 不准、改寫防回歸無;1c 同一案。
- rtb(另一個用 lumos 的消費專案)2026-10-01 全圖譜巡檢:懸空 `[test:]` 56 個、至少 3 個從沒存在過;撤除條款仍掛活 `[test:]` 12 條、3 條綁的是斷言反面的測試(在 rtb 的 repo 裡:提交 a7b3b2d 的 governance/audits/2026-10-01-drift-sweep/findings.md)。
- 2026-10-02 用最新 lumos 對 rtb 的唯讀副本(rtb 的提交 ef9ae20)量測:計劃正文還有 57 個指不到的(42 個是測試在 rtb 的提交 b2fc512 被刪)、摘要 1 個。本 repo 合約以外帶 `[test:]` 的摘要行 373 行,指不到的 26 個:4 個 `待補` 佔位、12 個文件裡的範例寫法(平台前綴沒定義,判成名稱不合法)、7 個其他「只出現在程式文字裡」、3 個哪裡都沒有。
- [[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3:格子只驗 `[test:]` 有寫,存在交給本案。

PRIOR-ART: 全部沿用既有零件——判存在用表態閘驗測試證據那一支 `_dispositions_check_test`(工作目錄索引加被檢查版本的測試檔整字找,兩道都過才算;已處理平台根在 repo 外、只看測試副檔名、排除 docs 與 governance),只補「類別.方法」寫法與根路徑跳脫;新寫的行用其他 note-shape 規則同一個入口 `_notelines_new`(已排除主線、合併只算自己寫的、有上線點);起點與主線那一版用 note-shape 自己的讀檔零件 `_nodehome_list`/`_nodehome_reader`;每條的鍵用格子的 `slot_parse`;摘要接回 `_ns_summary_logical`、圍欄 `_visible_lines`、條款定義行 `_CLAUSE_LEAD_RE`、合約行 `INVARIANT_RE`、作廢 `_ns_superseded`、1c 判舊條目用格子的 `_ns_is_old`;條款定義行用 `clause_bindings` 同一判法;規則自己一組開關、違規清單、帳本 `extra` 的鍵,照筆記格子規則(`note_shape.slots`)的形狀;全庫提醒照 doctor S17–S19(不寫帳)。新寫的只有:把上面這些串起來的抽取與判定。世界解:文件連結檢查工具(如 lychee、Sphinx linkcheck)也是「新寫的擋、存量另列」;`[test-gone:]` 沿用 rtb 2026-10-01 標籤提案,提交編號改成選填。
RETIRE-IF: 上線滿 8 週,抽查帳上 20 筆這條規則擋下的測試名,其實存在、是索引沒認出的超過一半 → 規則改回只提醒;或滿 8 週全部專案零擋下、doctor 這段也沒列出任何新的 → 擋留著、doctor 段降到 `--verbose` 才印。
REVISIT:2026-12-01 照帳上 note-shape 事件的 `test_refs` 欄位數擋下次數與名稱,抽 20 筆判 RETIRE-IF;順便看單次跳過時記下的 `test_refs` 條數。

## 名詞

- **note-shape / 筆記內容閘**:`lumos note-shape` 指令,提交前掛鉤跑 `--staged`、推送前與 CI 跑 `--diff 起點..終點`;節點 [[Systems/筆記內容閘]] 管它。**被檢查的版本**:提交時是提交索引、推送時是範圍終點。**單次跳過**:環境變數 `LUMOS_SKIP_NOTE_SHAPE=1`,整道跳過一次並記帳。**治理帳**:`docs/.governance-log.jsonl`,各道閘的事件。
- **測試名**:筆記一條裡 `slot_parse` 解出的 `test` 鍵(同一條可寫多次)的值,再用半形或全形逗號切開、去前後空白;設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱。反引號與大小寫、全形冒號照 `slot_parse` 的規矩(跟筆記格子認得的寫法一致)。程式碼圍欄裡的不算。
- **一條**:摘要裡一個前綴條目接回續行後的整條(單行寫法的 summary 整個值算一條);正文裡一個實體行。
- **新寫的行**:筆記內容閘既有定義——提交時是這次暫存新增的行,推送時是範圍裡逐提交新增、終點還在的行;已在主線上的提交不重查、合併提交只算它自己多寫的行、上線點之前的提交不算(其他 note-shape 規則同一個入口 `_notelines_new`)。
- **新加的測試名**:出現在新寫的行(摘要條目只要有一行是新寫的就整條算)上、而且「起點集合」裡沒有的名稱。起點集合 = 起點那一版整個知識庫出現過的名稱,再加上主線現在那一版知識庫的名稱(找得到主線時;推送者改到主線剛合進來的那一條時,主線的名稱不算在他頭上)。起點:提交時是 HEAD,推送時是 note-shape 算出的範圍起點。名稱搬行、搬篇、筆記改名、改舊行其他字、摘要重排折行都不算新加。起點那一版讀不出來(不是 UTF-8 等)的筆記,它在終點那一版的名稱這次一律當舊的,不判。
- **指得到 / 指不到 / 判不了**:用表態閘驗測試證據那一支 `_dispositions_check_test` 判(平台前綴照 `_dispositions_split_test`):第①道工作目錄的測試索引有這個名稱、第②道被檢查版本的該平台測試檔(只看那個平台 profile 的測試副檔名、排除 `docs/` 與 `governance/`)整字找得到,兩道都過才算指得到;第①道沒過、或第②道 grep 不到才算指不到(測試寫了沒提交,推上去也沒有守衛,一樣算指不到)。判不了(不擋、印一行):git 出錯或逾時、平台根在 repo 外或是子模組(只做第①道,第①道過就算指得到)、第①道沒過但測試檔裡有 `def 名稱(` 這種 profile 認不得的寫法(條款綁定既有的「設定認不到」,Python 寫在類別裡的測試就是這樣)。「類別.方法」寫法照 `_classify_test_refs` 的規矩補進第①道(只認方法名那段),第②道用方法名找;平台根路徑含 `[` `]` `*` `?` 時第②道的路徑要跳脫(兩項都補在 `_dispositions_check_test`,表態閘一起受益)。
- **合約行**:摘要裡接回後符合 `INVARIANT_RE` 的條目,已由 doctor Check T(合約有沒有綁到真的測試)驗存在,波及到的另由推送前合約測試閘真跑。**條款定義行**:計劃(type: project)裡、照條款綁定 `clause_bindings` 同一判法認的定義行——那個編號第一次寫在行首(`_CLAUSE_LEAD_RE`)的那一行;只在行內被提到不算(實作時把 `clause_bindings` 判定義行的那段抽成共用,兩邊同一支)。這兩種上的測試名本案不驗存在;但它們標了作廢還掛活測試時照樣算 1c(rtb 那 12 條就是計劃條款行)。
- **明標刪除**:`[test-gone:名稱]` 或 `[test-gone:名稱@提交]`——這支測試已經刪了,提交編號選填(只當追溯線索:不驗它存不存在,格子只驗寫法——有 `@` 時後面至少 7 碼十六進位;同一個提交裡刪測試、或推送前壓提交都寫得出來)。驗的是內容:名稱不能是空的或佔位字,而且現在不能指得到真測試(還指得到就是假話)。它不算 PITFALL 防回歸那一格——測試刪了就是沒有守衛。
- **作廢的條目**:帶 `[status:superseded]` 的一條(`_ns_superseded`;筆記格子規定另必帶 `[被取代:]`)。只有 `[被取代:]` 沒有 status 的不算。**活測試**:指得到真測試的測試名。
- **佔位字**:去掉平台前綴後名稱整個是 `待補`、`待定`、`TODO`、`TBD`(不分大小寫)其中之一。

## 範圍

- 做:note-shape 多一組規則「新加的測試名要指得到」「`[test-gone:]` 不准說假話」「新寫的作廢條目不准掛活測試」——推送時與 CI 擋,提交時只提醒(Enzo 2026-10-02 裁的是推送時擋;設計審 r2 也指出提交時就擋會卡住分兩個提交做的中間那個、而唯一逃生口會連其他規則一起跳過);認得 `[test-gone:]` 並登記成格子鍵;doctor 多一段全庫提醒(含散文撤除的候選);設定 `note_shape.test_refs`;`_dispositions_check_test` 補「類別.方法」寫法。
- 不做:合約行與條款定義行(各有檢查);開頭欄位只掃 summary,`decisions` 區與其他欄裡的 `[test:]` 不掃(本 repo decisions 裡有 14 行,由決策自己的欄位管);不真跑測試;不自動把指不到的改成 `[test-gone:]`;不清 rtb 或本 repo 既有的(各自清,見路線圖的循環);散文寫的撤除(rtb 那 12 條的寫法)不擋,只在 doctor 列候選;不改 PITFALL 的三選一。

## 做法

1. **抽取**:新寫一支吃全文的 `_note_test_refs(text, is_plan, rows)`,只拿新寫的行所在的條目:摘要用 `_ns_summary_logical`(帶 `cont` 把續行對回它的條目,同格子規則;單行寫法的 summary 照 `_note_summary_entries` 的補法,實作時抽成吃全文的一支兩邊共用),正文用 `_visible_lines` 略過圍欄;每一條丟給 `slot_parse` 取 `test`、`test-gone` 鍵,值再切逗號;合約行與條款定義行在判存在時略過、在 1c 照查。回每個名稱與它出現的筆記、行號(新寫的那一行)、所在條目的前綴、是否作廢。
2. **新寫的行從哪來**:跟其他 note-shape 規則同一趟——`_note_shape_eval` 本來就接受一個容器把它向 `_notelines_new` 要到的 rows 交出(格子規則就是這樣拿),這組傳自己的容器、帶 `keep_other` 讓單行寫法的 summary 也進來;不另呼叫第二次 `_notelines_new`、不另跑 `git diff`、不靠格子的 `--slots`。
3. **新加的判定**:起點那一版整個知識庫用 note-shape 自己的讀檔零件(`_nodehome_list` 列檔、`_nodehome_reader` 讀內容,跟 note-shape 讀終點同一套;不跨去用漂移檢查的 `_drift_tree_env`)讀一次,同一支抽取(不限新寫行)算出起點集合;主線那一版同樣讀一次(`_mainline_ref` 找得到才讀)。只在第 1 步有候選名稱時才讀;第 1 步的名稱扣掉起點集合,剩下的是新加的。
4. **判存在**:有要查的名稱時才 `_platform_test_index` 一次,名稱去重後每個交給 `_dispositions_check_test`(推送時第②道對終點、提交時不給 at_sha 只做第①道),外面包例外——丟例外(含 git 逾時)算判不了。保險只有一種:推送時目前簽出的提交不是推送終點(推的分支不是目前這條)→ 工作目錄的索引跟被推的版本對不上,這組這次只提醒不擋;測試寫了沒提交不在保險內,照擋。索引建不起來、或某平台的根不存在、掃不到任何測試方法 → 那個平台這次不查、印一行原因。整組(讀起點、判存在)共用一個 20 秒上限,用完剩下的名稱這次不查、印一行。
5. **違規**(這組自己的清單):
   - 新加的測試名指不到 → 印筆記、行號、名稱、`_dispositions_check_test` 給的原因與改法(平台前綴沒定義、看起來是人工驗證時,例如 rtb 的 `[test:browser:…]`,另提示改用條款既有的 `[manual:一句怎麼驗]`):改成真的測試名;測試已刪就寫 `[test-gone:名稱]`(PITFALL 另要 `[防回歸:無 理由]` 或 `[repro:指令]`);沒有測試就拿掉,PITFALL 同樣改寫防回歸無或 repro。
   - 新寫的摘要條目(用格子的舊行判定 `_ns_is_old` 判不是舊條目的)裡有佔位字、或 `[test:]` 方括號裡沒有名稱 → 一律違規,不跟起點集合比(起點已經有 4 個 `待補`、49 個空的,比了就永遠擋不到),先於判存在;訊息照那一條的前綴給改法。只看摘要條目,正文散文裡提到 `[test:]` 這個標記本身(本 repo 約 6%)不算;`slot_parse` 對沒收尾的方括號給的錯誤欄位不當名稱。
   - 新寫的行上的 `[test-gone:]` 名稱是空的、是佔位字、或現在指得到真測試 → 違規(最後一種:測試還在,改回 `[test:]`)。
   - 新寫的 PITFALL 條目只剩 `[test-gone:]`、沒有 `test`、`repro`、`防回歸` 任一 → 違規(格子規則會把只改欄位的舊行放過,這裡補上)。
   - (1c)作廢的條目掛著活測試,而且這次才變成作廢:用格子的舊行判定 `_ns_is_old`(它回「算不算舊條目、對上的舊條目有沒有標作廢」)——不是舊條目(新寫的),或是舊條目但起點那條還沒標作廢(這次才在舊行補上 `[status:superseded]`,rtb 那 12 條的寫法)→ 違規;起點那條就已標作廢(只重排折行、或碰到舊帳)不算。改法:摘要條目把綁定移到接手的那一條(`[被取代:]` 指的那裡),或拿掉;條款定義行拿掉會變成「沒標」讓 spec-trace 唸,改寫成 `[manual:已撤除,見 被取代 指的那裡]`;不建議改成 `[test-gone:]`(測試還在,那是假話)。
6. **開關與總開關**:`note_shape.test_refs: block`(預設)| `warn` | `off`,寫壞照 `block` 並提醒一句(同 `note_shape.slots`);總開關 `note_shape.gate` 是 `off` 整組不跑、是 `warn` 這組也只提醒。新寫一支 `_note_shape_test_refs_parse`。提交時一律只提醒。
7. **接線與上線**:`cmd_note_shape` 在 `_note_shape_eval` 之後跑這組(rows 是同一趟拿到的);呼叫 `_note_shape_report` 的條件加上這組違規;報告裡這組另起一段標題「新加的測試名指不到真測試」,收尾句講這組的改法,印的筆記路徑照既有的跳脫。上線點沿用 note-shape 既有的(`_notelines_new` 已經處理),不另設記號——格子規則另設記號,是因為它擋的是「寫法」,上線前合法的寫法上線後變不合法;本案擋的是「名稱指不到真測試」,上線前寫的壞名稱本來就是錯的。代價:`lumos update` 之前寫、還沒推的提交裡若新加了壞名稱,推送時會被擋(用單次跳過或改掉)。
8. **帳本**:這組有違規時,note-shape 那筆事件的 `extra` 字典多一個 `test_refs` 鍵(條數、前 20 個名稱與各自原因),跟格子那邊的鍵併在同一個字典;`extra` 裡既有的違規種類欄照既有寫法再多列一項。提交時被單次跳過,照格子的 `_ns_skip_slot_extra` 先算一次記進去(不靠 `--slots`);推送時的單次跳過在讀範圍之前就返回,不搬位置(搬了會改變既有的回傳碼),所以推送時跳過那筆沒有 `test_refs`——RETIRE-IF 以擋下事件為主,跳過只當參考。
9. **格子鍵**:`test-gone` 登記進 `_SLOT_KEYS` 與 `_SLOT_REPEATABLE`;不進 `_SLOT_NEW_ONLY`;不改 PITFALL 的三選一。`slot_check` 只驗形狀(名稱非空;有 `@` 時後面至少 7 碼十六進位);內容由本案這組查。紀律範本不動(`t_slots_single_table` 只比必有鍵、選擇題、條件鍵、列舉);`[test-gone:]` 的寫法寫進 skill 指令速查 03-寫回圖譜與 reference.md。2026-10-02 跟筆記格子那邊的會談對齊過(它同意不改三選一)。
10. **全庫提醒**:doctor 新一段(段名 S20,接在 S19 之後,實作時確認不落在既有截斷測試的視窗裡;標題含「提醒,不擋」,用 `warn_soft`;照 S17–S19 不寫帳)用同一支抽取掃全庫(不限新寫行),`_dispositions_check_test` 只做第①道(doctor 沒有被檢查版本,讀的就是工作目錄),列出指不到的測試名、名稱還指得到的 `[test-gone:]`、作廢的條目掛活測試;另列散文撤除的候選:計劃裡條款定義行仍有 `[test:]`,而它的下一層子項(緊接在後、縮排比條款行深的連續行)裡有一行含「撤除」且不含「保留」。每類預設印 3 條、`--verbose` 全列;索引建不起來時這段只印一行原因。
11. **要同步的文件**:[[Systems/筆記內容閘]](這組規則)、[[Systems/lumos-cli-read]](doctor S20)、[[Systems/bound-tests-gate]](判存在借的是表態閘那支,說明兩支的分工)、管 `_dispositions_check_test` 的那篇(實作時用 `lumos impact --file` 找家)、[[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3 改指到本案;skill 指令速查 03-寫回圖譜、06-代碼審與推送(note-shape 擋下種類)、04-自檢與健康(S20)、INDEX、reference.md;`scripts/lumos` 的說明字典。

## 條款

- [S1] 當推送時新加的測試名(合約行與條款定義行除外)指不到真測試時,note-shape 應回 1 並列出筆記、行號、名稱與原因 [test:t_note_shape_test_refs_new_names]
- [S2] 當指不到的名稱在起點那一版的知識庫就有(這次只是改了那一條的其他字、搬到別行或別篇、或筆記改名)時,note-shape 應不擋 [test:t_note_shape_test_refs_new_names]
- [S3] 當推送範圍合過主線、主線那段新加了指不到的名稱時,note-shape 應不把它算在這次推送 [test:t_note_shape_test_refs_mainline_merge]
- [S4] 當新加的測試名是佔位字而那一條是 PITFALL 時,擋下訊息應給 `[防回歸:無 理由]` 與 `[repro:]` 兩種改法 [test:t_note_shape_test_refs_placeholder]
- [S5] 當新加的測試名是佔位字而那一條不是 PITFALL 時,擋下訊息應叫人拿掉或改成真名、不給防回歸改法 [test:t_note_shape_test_refs_placeholder]
- [S6] 當新寫的 `[test-gone:名稱]` 的名稱現在指不到真測試時,note-shape 應放行(帶不帶 `@提交` 都一樣) [test:t_note_shape_test_gone_marker]
- [S7] 當新寫的 `[test-gone:名稱]` 的名稱現在指得到真測試、或是空的或佔位字時,note-shape 應回 1 [test:t_note_shape_test_gone_marker]
- [S8] 當新寫的 PITFALL 條目只剩 `[test-gone:]`、沒有 test、repro、防回歸任一時,note-shape 應回 1 [test:t_note_shape_test_gone_pitfall]
- [S9] 當名稱只出現在程式碼圍欄裡時,note-shape 應不算它 [test:t_note_shape_test_refs_skip_examples]
- [S10] 當名稱用大寫鍵、全形冒號或全形逗號寫時,note-shape 應照樣抽到並查 [test:t_note_shape_test_refs_lenient_syntax]
- [S11] 當這次才在舊條目上補 `[status:superseded]`、`[test:]` 照留而且指得到時,note-shape 應回 1 並建議把綁定移到接手的那一條 [test:t_note_shape_retired_line_live_test]
- [S12] 當作廢條目在起點就已標作廢、這次只是重排折行或改了別的字時,note-shape 應不擋 [test:t_note_shape_retired_line_live_test]
- [S13] 當推送時目前簽出的提交不是推送終點時,這組規則應只提醒不擋並說原因 [test:t_note_shape_test_refs_checked_version]
- [S14] 當測試索引建不起來、或某平台的根不存在、或掃不到任何測試方法時,那個平台的名稱應跳過並印一行原因,note-shape 照其他規則判 [test:t_note_shape_test_refs_index_fail_open]
- [S15] 當提交時這組規則有違規時,note-shape 應只提醒、回傳碼照其他規則 [test:t_note_shape_test_refs_commit_warns]
- [S16] 當 doctor 跑時,doctor 應在 S20 段列出全庫指不到的測試名、名稱還指得到的 `[test-gone:]`、作廢的條目掛活測試與散文撤除的候選,並且不影響回傳碼 [test:t_doctor_note_test_refs]
- [S17] 當 `note_shape.test_refs` 是 `warn` 或總開關 `note_shape.gate` 是 `warn` 時,這組規則應只提醒不擋;寫成不認得的值時應照 `block` 跑並印一句提醒 [test:t_note_shape_test_refs_config]
- [S18] 當 `note_shape.test_refs` 或總開關是 `off` 時,這組規則應不跑 [test:t_note_shape_test_refs_config]
- [S19] 當這組規則擋下、或提交時被單次跳過時,治理帳那筆事件的 `extra` 應帶 `test_refs` 鍵(條數與名稱) [test:t_note_shape_test_refs_ledger]
- [S20] 當新寫的摘要條目裡 `[test:]` 方括號沒有任何名稱時,note-shape 應回 1;正文散文裡出現不算 [test:t_note_shape_test_refs_empty]
- [S21] 當 summary 是單行寫法、或名稱落在摘要條目的續行時,note-shape 應照樣抽到 [test:t_note_shape_test_refs_summary_forms]
- [S22] 當舊寫法的 PITFALL 行只把 `[test:X]` 改成 `[test-gone:X]` 時,格子規則應不把它當新文法要求補齊新格子 [test:t_slots_test_gone_key]
- [S23] 當表態證據寫成「類別.方法」而工作目錄的測試索引有那個方法時,`_dispositions_check_test` 應判第①道過 [test:t_dispositions_test_class_method]
- [S24] 當新寫的作廢條目是計劃的條款定義行或合約行、而且掛著活測試時,note-shape 應照 1c 回 1 [test:t_note_shape_retired_line_live_test]
- [S25] 當新加的測試名含 `:` 而 `_dispositions_split_test` 判不出平台時,擋下訊息應另提示人工驗證改用 `[manual:…]` [test:t_note_shape_test_refs_new_names]
- [S26] 當 `_dispositions_check_test` 丟例外、git 出錯或逾時、平台根是子模組時,那個名稱應算判不了、不擋並印一行 [test:t_note_shape_test_refs_undecidable]
- [S27] 當計劃的條款編號先在行內被提到、後面才寫在行首時,note-shape 應把後面那行當條款定義行、不驗它的測試名 [test:t_note_shape_test_refs_clause_def]
- [S28] 當起點已經有 `[test:待補]`、這次又新寫一條帶 `[test:待補]` 的摘要條目時,note-shape 應擋 [test:t_note_shape_test_refs_placeholder]
- [S29] 當推送者改到主線剛合進來的那一條、那條的名稱在主線現在那一版就有時,note-shape 應不算它新加 [test:t_note_shape_test_refs_mainline_merge]
- [S30] 當 Python 測試寫在類別裡(檔裡有 `def 名稱(` 但 profile 認不得)時,那個名稱應算判不了、不擋 [test:t_note_shape_test_refs_undecidable]
- [S31] 當平台根路徑含 `[` `]` 時,`_dispositions_check_test` 的第②道應照樣找得到真測試 [test:t_dispositions_test_glob_root]

## 回退

- revert 實作提交即可。已寫進筆記的 `[test-gone:]` 留著:revert 後格子規則不認得這個鍵,會把它當核心句文字,不擋;它本來就不算防回歸。帳上多出的 `test_refs` 鍵舊讀端忽略。`_dispositions_check_test` 的「類別.方法」補法一起還原,表態證據寫成這種的回到判不過。
- 只想先停擋:`note_shape.test_refs: warn` 或 `off`。

## 實務隱患

- **誤擋**:測試寫了沒提交就推送筆記,會被擋(第②道);這是本意(推上去沒有守衛)。索引沒認出的寫法(參數化名稱)會被判指不到,`warn` 可退;RETIRE-IF 抽查帳上名稱。
- **漏網**:推的分支不是目前簽出那條時只提醒,這時新加的壞名字不擋,交給 CI;判不了的名稱(git 出錯、逾時、子模組、Python 類別裡的測試)也不擋(CI 的工作目錄就是終點,兩邊一致)。起點那一版整個知識庫就有的名稱一律不算新加——把既有的壞名字複製到新的一行不會被擋,只在 doctor S20 列出。
- **散文撤除擋不到**:rtb 那 12 條撤除是「條款下一層寫一段撤除裁定」的散文,不帶 `[status:superseded]`,規則擋不到,只會進 doctor 候選(關鍵字判,排除含「保留」的)。要擋得住得在撤除時補標記——列進 rtb 清理的回傳要求。
- **lint 的提醒**:舊寫法的 PITFALL 照改法加 `[防回歸:無 …]` 之後,lint 會因為這行出現新文法的鍵而唸缺出處與根因——只提醒、不擋。
- **時間**:推送時多一次起點知識庫批次讀(有上限)、有要查的名稱才建索引;每個要查的名稱一次 `git grep`(本 repo 量過一次約 0.2 秒),新加的名稱通常個位數。實作時量一次推送多幾秒,寫進〈實作紀錄〉。doctor S20 每次全掃,CI 的 doctor 也會多這一次。
- **相容**:消費專案 `lumos update` 後,推送時新加壞名字會被擋——本案本意;既有的不擋。
- **跟筆記格子的接點**:只加一個鍵、不改三選一;動鍵表前跟那邊的會談再對一次。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀筆記與測試檔,不連網
- 已排除:不可逆:只擋推送、只印提醒,revert 回得去
- 守衛面:新增一組推送時的擋,有 `warn`/`off` 與單次跳過可退,提交時的單次跳過照記帳。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- r3(2026-10-02,4 席同編制,上限輪):33 條/blocking 16/全折(Enzo 裁「折入後另開一輪審完整版」)。最大的一條三席獨立實測一致:1c 用 `_ns_text_key` 比核心句,在舊條目補 `[status:superseded]`、測試照留時核心句沒變 → 放行,正好是 rtb 那 12 條的寫法 → 改用格子的舊行判定 `_ns_is_old`(它回「起點那條有沒有已標作廢」)。其他:佔位字與空名稱不再跟起點比(起點已有 4 個待補、49 個空的)、只看新寫的摘要條目;條款定義行改用 `clause_bindings` 同一判法(先在行內提到、後寫在行首的有 17 份 38 條);判存在加「判不了」(git 出錯、逾時、子模組、Python 類別裡的測試),路徑含方括號要跳脫;保險只在推的分支不是目前簽出那條時啟動(測試沒提交照擋);新寫行跟 `_note_shape_eval` 同一趟拿、帶 keep_other;起點用 note-shape 自己的讀檔零件(不跨去用漂移那支)、另加主線那一版、讀不出的筆記不判;整組 20 秒上限、名稱去重;decisions 明寫不掃;不另設上線記號的理由寫明。例:舊條目 `PITFALL:x [test:t_live]` 改成 `PITFALL:x [test:t_live] [status:superseded] [被取代:[[Y]]]` → 修前放行、修後擋。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- r2(2026-10-02,4 席同編制):33 條/blocking 14/全折,無放行、無駁回。r1 換的三個形狀裡有兩個同類再出 major(判新加、判存在),照「同類兩輪換形狀」整類改用外層既有的機制,不再補條件:判新加改用 note-shape 既有的新寫行入口 `_notelines_new`(排除主線、合併只算自己寫的、有上線點;r1 的兩側相減會把合進來的主線算成這次新加),再扣掉起點那一版整個知識庫出現過的名稱;判存在拿掉自寫的 `git grep` 複查(會搜到筆記自己、測試檔呼叫過函式就放行、類別.方法對不上),改用表態閘那支 `_dispositions_check_test`(兩道都過才算、已排除 docs 與 governance)並補類別.方法;抽取改用 `slot_parse`(自寫寬鬆正則是第二套)。另外:擋改回只在推送時(提交時提醒)——Enzo 原裁就是推送,且提交時擋會卡分兩個提交做的中間那個;`[test-gone:]` 補內容檢查(空、佔位字、PITFALL 只剩它沒有防回歸);1c 比對用 `_ns_text_key`(只重排折行不算新寫);推送時單次跳過不記 test_refs(跳過分支在讀範圍前返回,搬了會改既有回傳碼)。例:分支合進主線後推送,主線新增的壞名字 → 修前算這次新加擋下、修後不算;`[test:cmd_note_shape]`(函式名不是測試)→ 修前 grep 在測試檔找到放行、修後第①道判不是測試方法擋下。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- r1(2026-10-02,4 席:正確性-opus、邊界-sonnet、整合-sonnet、架構對齊-sonnet):40 條/blocking 25/全折,無放行、無駁回。三席獨立抓到同一組根問題,換三個形狀:①判「新」從新寫行減整篇改成「這次改到的筆記兩側加總次數相減」(改名、搬行、折行、整篇佔次數都收掉),名稱一次送一個判(壞前綴不再吞掉整行);②拿掉「測試檔有改動就只提醒」(平台根常是 repo 根、提交時筆記自己就算改動,規則會永遠不擋),改成指不到的名稱到被檢查版本的測試檔整字複查;③`[test-gone:]` 提交選填、驗內容(名稱現在不能是真測試)、不算防回歸、不改三選一(同一提交刪測試或壓提交原本寫不出來;只驗形狀會讓假話過關)。其餘照補:寬鬆寫法對齊格子、摘要接回與單行 summary、條款行用 `_CLAUSE_LEAD_RE`、索引空的也跳過、帳本併進 extra 且推送時跳過也記、doctor 段給 S20 與子項定義、落點改 lumos-cli-read 與 bound-tests-gate、接線與報告標題。例:同一篇把一行 `[test:x_dead]` 搬到另一行並改一個字 → 修前擋、修後不擋;一行 `[test:bad:a, t_new_missing]` → 修前整行一筆 bad-name、修後 t_new_missing 單獨列出。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- 前掃(2026-10-02;其中「`[test-gone:]` 提交驗在分支歷史上」「進 PITFALL 三選一」兩點已被 r1 改掉):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/筆記測試綁定要存在/r1-intake.md`。動到做法的:判「新」的單位從「新寫的行」改成「新加的測試名」(舊行改字原本會被擋);規則自己一組開關與帳本欄位(照格子規則,否則量不到 RETIRE-IF);作廢只認 `[status:superseded]`;`[test-gone:]` 提交照 `_pin_commit` 判在分支歷史上;doctor 段不寫帳;`[test-gone:]` 進格子鍵表與 PITFALL 三選一。
