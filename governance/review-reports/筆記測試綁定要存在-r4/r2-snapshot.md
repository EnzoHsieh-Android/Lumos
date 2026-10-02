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
  - Systems/棧別提問表態閘
related:
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Projects/筆記格子寫法與過期檢查_計劃]]"
  - "[[Systems/筆記內容閘]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Systems/lumos-cli-read]]"
---
# 筆記測試綁定要存在_計劃

白話:筆記裡寫 `[test:測試名]` 是在說「這件事有這支測試守著」。現在只有合約行(★INVARIANT★)與計劃的驗收條款會核對那支測試真的存在;摘要裡的 WHY、PITFALL、RULE 和正文裡的 `[test:]` 寫錯名字、或測試後來被刪了,沒有任何地方發現,讀的人會以為有守衛。這份計劃的做法:推送時,這次碰到(有新寫的行)的筆記整篇要乾淨——測試名都要指得到真測試、標成作廢的條目不准還掛活測試、`[test-gone:]` 不准說假話;舊的壞名字碰到了就順手修。提交時只提醒;沒碰到的筆記只在健康檢查提醒。程式預設只提醒,本 repo 設定開擋。

依據:
- 路線圖 1b(所有筆記的測試名要驗存在)、1c(撤除的東西不准再掛活測試)([[Projects/漂移防治路線圖_計劃]]);Enzo 2026-10-01 裁順序,2026-10-02 裁三件:推送擋新寫的、全庫只提醒;新寫的 `[test:待補]` 不准、改寫防回歸無;1c 同一案。設計審四輪(前一個迴圈三輪到頂、另開一輪)後,問題都在「只擋新加的」要分新舊的接點,Enzo 2026-10-02 裁改成「碰到的筆記整篇要乾淨」。
- rtb(另一個用 lumos 的消費專案)2026-10-01 全圖譜巡檢:懸空 `[test:]` 56 個、至少 3 個從沒存在過;撤除條款仍掛活 `[test:]` 12 條、3 條綁的是斷言反面的測試(在 rtb 的 repo 裡:提交 a7b3b2d 的 governance/audits/2026-10-01-drift-sweep/findings.md)。
- 2026-10-02 用最新 lumos 對 rtb 的唯讀副本(rtb 的提交 ef9ae20)量測:計劃正文還有 57 個指不到的(42 個是測試在 rtb 的提交 b2fc512 被刪)、摘要 1 個。本 repo 合約以外帶 `[test:]` 的摘要行 373 行,指不到的 26 個:4 個 `待補` 佔位、12 個文件裡的範例寫法(平台前綴沒定義,判成名稱不合法)、7 個其他「只出現在程式文字裡」、3 個哪裡都沒有。
- [[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3:格子只驗 `[test:]` 有寫,存在交給本案。

PRIOR-ART: 全部沿用既有零件——判存在第①道用推送前合約測試閘那一支 `_classify_test_refs`(多平台、類別.方法都已處理),第②道把表態閘 `_dispositions_check_test` 裡「在被推的版本找測試檔」那段抽成共用 `_test_in_tree`(只看測試副檔名、排除 docs 與 governance、平台根在 repo 外已處理);碰到的筆記用其他 note-shape 規則同一個入口 `_notelines_new`(經 `_note_shape_eval` 同一趟);每條的鍵用格子的 `slot_parse`;摘要接回 `_ns_summary_logical`、圍欄 `_visible_lines`、條款定義行用 `clause_bindings` 同一判法、合約行 `INVARIANT_RE`、作廢 `_ns_superseded`;規則自己一組開關、違規清單、帳本 `extra` 的鍵,照筆記格子規則的形狀;全庫提醒照 doctor S17–S19(不寫帳)。新寫的只有串起來的抽取與判定、`rows_out` 參數、`_test_in_tree` 的抽出。世界解:「碰到就要整篇乾淨」是童子軍規則(Boy Scout Rule)的機械版;文件連結檢查工具(lychee、Sphinx linkcheck)也是查有改動的文件;`[test-gone:]` 沿用 rtb 2026-10-01 標籤提案。
RETIRE-IF: 本 repo 開擋滿 8 週,抽查帳上 20 筆這條規則擋下的測試名,其實存在、是索引沒認出的超過一半 → 本 repo 改回 `warn`;或擋下的有一半以上是「碰到舊筆記被迫修舊帳」而推送者放棄推、改用單次跳過 → 改回只擋新加的(另開設計);或滿 8 週全部專案零擋下、doctor 這段也沒列出任何新的 → 擋留著、doctor 段降到 `--verbose` 才印。
REVISIT:2026-12-01 照帳上 note-shape 事件的 `test_refs` 欄位數擋下次數與名稱,抽 20 筆判 RETIRE-IF;順便看單次跳過時記下的 `test_refs` 條數。

## 名詞

- **note-shape / 筆記內容閘**:`lumos note-shape` 指令,提交前掛鉤跑 `--staged`、推送前與 CI 跑 `--diff 起點..終點`;節點 [[Systems/筆記內容閘]] 管它。**被檢查的版本**:提交時是提交索引、推送時是範圍終點。**單次跳過**:環境變數 `LUMOS_SKIP_NOTE_SHAPE=1`,整道跳過一次並記帳。**治理帳**:`docs/.governance-log.jsonl`,各道閘的事件。
- **碰到的筆記**:這次有新寫的行的筆記——新寫的行照筆記內容閘既有定義(提交時是這次暫存新增的行;推送時是範圍裡逐提交新增、終點還在的行,已在主線上的提交不重查、合併提交只算它自己多寫的行、上線點之前的不算;入口 `_notelines_new`,跟其他 note-shape 規則同一趟)。只是被主線合進來、自己沒寫任何一行的筆記不算碰到。
- **整篇要乾淨**:碰到的筆記,在被檢查的版本裡整篇(不分新舊行)都要符合〈做法〉3 的規則。舊的壞名字碰到了就要順手修。
- **測試名**:筆記一條裡 `slot_parse` 解出的 `test` 鍵(同一條可寫多次)的值,再用半形或全形逗號切開、去前後空白、去掉空項;設定有 `platforms` 時可帶 `平台:` 前綴(前綴與名稱之間的空白也去掉)。反引號與大小寫、全形冒號照 `slot_parse` 的規矩。程式碼圍欄裡的不算(`_visible_lines`)、HTML 註解裡的不算;縮排四格寫成的程式碼區塊不認(`_visible_lines` 本來就不認,已知限制)。**一條**:摘要裡一個前綴條目接回續行後的整條(`_ns_summary_logical`;單行寫法的 summary 整個值算一條);正文裡一個實體行。開頭欄位只看 summary,`decisions` 與其他欄不看。
- **合約行**:摘要裡接回後符合 `INVARIANT_RE` 的條目,已由 doctor Check T 驗存在、波及到的另由推送前合約測試閘真跑。**條款定義行**:計劃(type: project)裡照 `clause_bindings` 同一判法認的定義行(那個編號第一次寫在行首的那一行;實作時把它判定義行的那段抽成共用)。這兩種行上的測試名本案不驗存在;但標了作廢還掛活測試時照樣算(〈做法〉3 第 4 項;rtb 那 12 條就是計劃條款行)。
- **指得到 / 指不到 / 判不了**(每個名稱):第①道用推送前合約測試閘那一支 `_classify_test_refs`(工作目錄的測試索引;多平台、「類別.方法」寫法都已處理),判 `real` 才過,`fake`/`dangling`/`bad-name` 算指不到;第②道問被檢查的版本裡那個平台的測試檔整字找不找得到(把表態閘 `_dispositions_check_test` 裡做這件事的那段抽成共用小函式 `_test_in_tree`,表態閘改用它、行為不變),它回三種:找得到、找不到、判不了(git 出錯或逾時、平台根在 repo 外、平台根是子模組)。第①道過、第②道找得到 → 指得到;第①道沒過、或第②道找不到 → 指不到(測試寫了沒提交,推上去也沒有守衛,一樣算);第②道判不了 → 判不了,不擋、印一行。提交時與 doctor 沒有被推的版本,只做第①道。
- **明標刪除**:`[test-gone:名稱]` 或 `[test-gone:名稱@提交]`——這支測試已經刪了,提交編號選填(只當追溯線索,不驗;格子只驗寫法——有 `@` 時後面至少 7 碼十六進位)。驗的是內容:名稱不能是空的或佔位字,而且不能指得到真測試(還指得到就是假話)。它不算 PITFALL 防回歸那一格。
- **作廢的條目**:那一條 `slot_parse` 解出 `status` 是 `superseded`(`_ns_superseded` 同一判法,任何前綴、正文行與條款行也適用);只有 `[被取代:]` 沒有 status 的不算。**活測試**:指得到真測試的測試名。
- **佔位字**:去掉平台前綴後名稱整個是 `待補`、`待定`、`TODO`、`TBD`(不分大小寫)其中之一。

## 範圍

- 做:note-shape 多一組規則「碰到的筆記整篇要乾淨」(推送時與 CI 擋、提交時只提醒);`[test-gone:]` 登記成格子鍵;doctor 多一段全庫提醒(同一套判法、不分碰沒碰);設定 `note_shape.test_refs`;把表態閘「在被推的版本找測試」那段抽成共用。
- 不做:合約行與條款定義行的存在檢查(各有檢查);不真跑測試;不自動把指不到的改成 `[test-gone:]`;不清 rtb 或本 repo 既有的(各自清,見路線圖的循環);散文寫的撤除不擋,只在 doctor 列候選;不改 PITFALL 的三選一;不認「檔裡有 `def 名稱(` 但 profile 認不得」的寫法(會把一般函式名也放行,設計審 r4 實測);Python 寫在類別裡、profile 不認得的測試會被判指不到——已知限制,用 `warn` 退。

## 做法

1. **碰到的筆記從哪來**:`_note_shape_eval` 加一個新參數 `rows_out`(呼叫端給容器、它把向 `_notelines_new` 要到的 rows 放進去;不動既有的 `slots` 參數,所以不會連帶打開格子規則),這組從 rows 取出筆記路徑集合。不另呼叫第二次 `_notelines_new`。
2. **讀內容**:碰到的筆記在被檢查的版本裡的全文,用 note-shape 讀終點的同一個讀檔零件(筆記數就是碰到的篇數,不讀整庫、不讀起點與主線)。
3. **規則**(這組自己的違規清單),對碰到的每一篇整篇:
   1. 測試名(合約行與條款定義行除外)指不到 → 違規,印筆記、行號、名稱、原因與改法:改成真的測試名;測試已刪就寫 `[test-gone:名稱]`(PITFALL 另要 `[防回歸:無 理由]` 或 `[repro:指令]`);沒有測試就拿掉,PITFALL 同樣改寫防回歸無或 repro;名稱含 `:` 而平台前綴沒定義、看起來是人工驗證(例如 rtb 的 `[test:browser:…]`)時另提示改用 `[manual:一句怎麼驗]`。
   2. 摘要條目裡有佔位字、或 `[test:]` 方括號裡沒有名稱 → 違規,不判存在;改法照那一條的前綴。正文裡散文提到 `[test:]` 這個標記本身不算;`slot_parse` 對沒收尾的方括號給的錯誤欄位不當名稱。
   3. `[test-gone:]` 名稱是空的、是佔位字、或指得到真測試 → 違規(最後一種:測試還在,改回 `[test:]`)。
   4. 作廢的條目(含條款定義行、合約行)掛著活測試 → 違規。改法:摘要條目把綁定移到接手的那一條(`[被取代:]` 指的那裡),或拿掉;條款定義行改寫成 `[manual:已撤除,見 被取代 指的那裡]`(拿掉會變成「沒標」讓 spec-trace 唸);不建議改成 `[test-gone:]`(測試還在,那是假話)。
   5. PITFALL 條目有 `[test-gone:]`、沒有 `test`、`repro`、`防回歸` 任一 → 違規(格子規則會把只改欄位的舊行放過,這裡補上)。
4. **判存在**:有要查的名稱時才 `_platform_test_index` 一次,名稱去重;每個名稱照〈名詞〉的兩道判;整組共用一個 20 秒上限,用完剩下的名稱這次不查、印一行;索引建不起來、或某平台的根不存在、掃不到任何測試方法 → 那個平台這次不查、印一行;這組任何一步丟例外 → 整組這次不查、印一行(note-shape 本來就 fail-open)。
5. **保險**(推送時,這組只提醒不擋並說原因):目前簽出的提交不是推送終點(推的分支不是目前這條),或已追蹤的測試檔(各平台 profile 的測試副檔名,排除 `docs/`、`governance/`)有沒提交的修改或刪除——這兩種時工作目錄的索引跟被推的版本對不上。新寫了還沒提交的測試檔不在保險內,照擋。
6. **開關**:`note_shape.test_refs: block` | `warn` | `off`,**程式預設 `warn`**、本 repo 的 `.lumos/config.json` 設 `block`;寫壞照 `warn` 並提醒一句;總開關 `note_shape.gate` 是 `off` 整組不跑、是 `warn` 這組也只提醒。新寫一支 `_note_shape_test_refs_parse`。提交時一律只提醒。預設 `warn` 的理由:鄰居(筆記格子)把「程式上線」與「開擋」分開,免得消費專案 `lumos update` 那一刻碰到的舊筆記全被擋;本案用設定分開——消費專案先看 doctor S20 列的清單、清乾淨了再自己設 `block`,不必改掛鉤。
7. **接線**:`cmd_note_shape` 在 `_note_shape_eval` 之後跑這組;呼叫 `_note_shape_report` 的條件加上這組違規;報告裡這組另起一段標題「碰到的筆記裡有指不到真測試的綁定」,收尾句講這組的改法;印的筆記路徑與名稱照既有的跳脫,名稱截到 80 字。
8. **帳本**:這組有違規時,note-shape 那筆事件的 `extra` 字典多一個 `test_refs` 鍵(條數、前 20 個名稱與各自原因),跟格子那邊的鍵併在同一個字典。`check` 欄是單值、也是同日去重的鍵:這組的違規照既有寫法併進同一筆事件,`check` 照既有判法不變,這組的有無只看 `extra.test_refs`。提交時被單次跳過時,先用 `rows_out` 算一次記進去;推送時的單次跳過在讀範圍之前就返回,不搬位置,那筆沒有 `test_refs`。
9. **格子鍵**:`test-gone` 登記進 `_SLOT_KEYS` 與 `_SLOT_REPEATABLE`;不進 `_SLOT_NEW_ONLY`;不改 PITFALL 的三選一。`slot_check` 只驗形狀。紀律範本不動;`[test-gone:]` 的寫法寫進 skill 指令速查 03-寫回圖譜與 reference.md。
10. **全庫提醒**:doctor 新一段 S20(接在 S19 之後、不落在既有截斷測試的視窗;標題含「提醒,不擋」,用 `warn_soft`;不寫帳),對全庫每一篇做〈做法〉3 的五項,判存在只做第①道;另列散文撤除的候選:計劃裡條款定義行仍有 `[test:]`,而它的下一層子項(緊接在後、縮排比條款行深的連續行)裡有一行含「撤除」且不含「保留」。每類預設印 3 條、`--verbose` 全列;索引建不起來時這段只印一行原因。抽取用同一支吃全文的函式(doctor 從筆記路徑讀全文)。
11. **要同步的文件**:[[Systems/筆記內容閘]](這組規則)、[[Systems/lumos-cli-read]](doctor S20)、[[Systems/bound-tests-gate]](第①道借它那支)、[[Systems/棧別提問表態閘]](`_test_in_tree` 從它抽出)、[[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3 改指到本案;skill 指令速查 03、06(note-shape 擋下種類)、04(S20)、INDEX、reference.md;`scripts/lumos` 的說明字典。

## 條款

- [S1] 當推送時碰到的筆記裡有測試名(合約行與條款定義行除外)指不到真測試時,note-shape 應回 1 並列出筆記、行號、名稱與原因,舊行上的也算 [test:t_note_shape_test_refs_touched_note]
- [S2] 當指不到的名稱在一篇這次沒有新寫行的筆記裡時,note-shape 應不擋 [test:t_note_shape_test_refs_touched_note]
- [S3] 當推送範圍合過主線、主線那段改了某篇筆記而這次推送自己沒寫那篇時,note-shape 應不把那篇當碰到 [test:t_note_shape_test_refs_mainline_merge]
- [S4] 當摘要條目是 PITFALL 而有佔位字時,擋下訊息應給 `[防回歸:無 理由]` 與 `[repro:]` 兩種改法 [test:t_note_shape_test_refs_placeholder]
- [S5] 當摘要條目不是 PITFALL 而有佔位字時,擋下訊息應叫人拿掉或改成真名、不給防回歸改法 [test:t_note_shape_test_refs_placeholder]
- [S6] 當摘要條目的 `[test:]` 方括號沒有任何名稱時,note-shape 應回 1;正文散文裡出現不算 [test:t_note_shape_test_refs_empty]
- [S7] 當 `[test-gone:名稱]` 的名稱指不到真測試時,note-shape 應放行(帶不帶 `@提交` 都一樣) [test:t_note_shape_test_gone_marker]
- [S8] 當 `[test-gone:名稱]` 的名稱指得到真測試、或是空的或佔位字時,note-shape 應回 1 [test:t_note_shape_test_gone_marker]
- [S9] 當 PITFALL 條目有 `[test-gone:]` 而沒有 test、repro、防回歸任一時,note-shape 應回 1 [test:t_note_shape_test_gone_pitfall]
- [S10] 當作廢的條目(摘要條目、計劃條款定義行或合約行)掛著活測試時,note-shape 應回 1 並給那種行的改法 [test:t_note_shape_retired_line_live_test]
- [S11] 當名稱只出現在程式碼圍欄裡時,note-shape 應不算它 [test:t_note_shape_test_refs_skip_examples]
- [S12] 當名稱用大寫鍵、全形冒號或全形逗號寫、或落在摘要條目的續行、或 summary 是單行寫法時,note-shape 應照樣抽到並查 [test:t_note_shape_test_refs_lenient_syntax]
- [S13] 當計劃的條款編號先在行內被提到、後面才寫在行首時,note-shape 應把後面那行當條款定義行、不驗它的測試名 [test:t_note_shape_test_refs_clause_def]
- [S14] 當第②道判不了(git 出錯或逾時、平台根在 repo 外、平台根是子模組)時,那個名稱應不擋並印一行 [test:t_note_shape_test_refs_undecidable]
- [S15] 當測試寫了還沒提交、筆記已經綁它而推送時,note-shape 應回 1 [test:t_note_shape_test_refs_uncommitted_test]
- [S16] 當推送時目前簽出的提交不是推送終點、或已追蹤的測試檔有沒提交的修改或刪除時,這組規則應只提醒不擋並說原因 [test:t_note_shape_test_refs_checked_version]
- [S17] 當測試索引建不起來、或某平台的根不存在、或掃不到任何測試方法、或這組丟例外時,應跳過並印一行原因,note-shape 照其他規則判 [test:t_note_shape_test_refs_index_fail_open]
- [S18] 當提交時這組規則有違規時,note-shape 應只提醒、回傳碼照其他規則 [test:t_note_shape_test_refs_commit_warns]
- [S19] 當沒寫 `note_shape.test_refs` 時,這組規則應只提醒不擋;寫 `block` 時才擋 [test:t_note_shape_test_refs_config]
- [S20] 當 `note_shape.test_refs` 或總開關是 `off` 時,這組規則應不跑;總開關是 `warn` 時應只提醒;寫成不認得的值時應照 `warn` 跑並印一句提醒 [test:t_note_shape_test_refs_config]
- [S21] 當這組規則擋下、或提交時被單次跳過時,治理帳那筆事件的 `extra` 應帶 `test_refs` 鍵(條數與名稱),`check` 欄照既有判法 [test:t_note_shape_test_refs_ledger]
- [S22] 當 doctor 跑時,doctor 應在 S20 段列出全庫指不到的測試名、寫法或內容不對的 `[test-gone:]`、作廢的條目掛活測試、佔位字與散文撤除的候選,並且不影響回傳碼 [test:t_doctor_note_test_refs]
- [S23] 當舊寫法的 PITFALL 行只把 `[test:X]` 改成 `[test-gone:X]` 時,格子規則應不把它當新文法要求補齊新格子 [test:t_slots_test_gone_key]
- [S24] 當表態閘改用抽出的 `_test_in_tree` 後,表態證據的判定應跟原本一樣 [test:t_dispositions_test_in_tree_unchanged]
- [S25] 當 `_note_shape_eval` 傳了 `rows_out` 而沒傳 `slots` 時,格子規則應不跑 [test:t_note_shape_eval_rows_out]

## 回退

- revert 實作提交即可。已寫進筆記的 `[test-gone:]` 留著:revert 後格子規則不認得這個鍵,會把它當核心句文字,不擋;它本來就不算防回歸。帳上多出的 `test_refs` 鍵舊讀端忽略。`_test_in_tree` 抽出一起還原,表態閘回到原寫法(行為本來就一樣)。
- 只想先停擋:`note_shape.test_refs: warn` 或 `off`。

## 實務隱患

- **誤擋**:碰到的舊筆記有舊的壞名字,要順手修才推得上去——本案本意。Python 寫在類別裡、profile 不認得的測試會被判指不到,`warn` 可退。測試寫了沒提交就推送筆記會被擋(第②道),這是本意。
- **漏網**:推的分支不是目前簽出那條、或已追蹤的測試檔有沒提交的改動時只提醒,交給 CI(CI 的工作目錄就是終點);第②道判不了的不擋;沒碰到的筆記不擋,只在 doctor S20 列出。
- **散文撤除擋不到**:rtb 那 12 條撤除若只寫成「條款下一層一段撤除裁定」、不帶 `[status:superseded]`,規則擋不到,只會進 doctor 候選(排除含「保留」的)。要擋得住得在撤除時補標記——列進 rtb 清理的回傳要求。
- **lint 的提醒**:舊寫法的 PITFALL 照改法加 `[防回歸:無 …]` 之後,lint 會因為這行出現新文法的鍵而唸缺出處與根因——只提醒、不擋。
- **時間**:只讀碰到的筆記;有要查的名稱才建索引;第②道每個名稱一次 `git grep`(本 repo 約 0.2 秒),碰到的筆記若綁了很多測試會花幾秒,整組 20 秒上限。實作時量一次推送多幾秒,寫進〈實作紀錄〉。doctor S20 全庫只做第①道(全庫抽取約 0.3 秒,索引另計)。
- **相容**:程式預設只提醒,消費專案 `lumos update` 後不會被擋;要擋得自己設 `block`。
- **跟筆記格子的接點**:只加一個鍵、不改三選一;`_note_shape_eval` 加 `rows_out` 參數。動之前跟那邊的會談再對一次。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀筆記與測試檔,不連網
- 已排除:不可逆:只擋推送、只印提醒,revert 回得去
- 守衛面:新增一組推送時的擋,預設只提醒、本 repo 開擋;有 `warn`/`off` 與單次跳過可退,提交時的單次跳過照記帳。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- 另開迴圈 `筆記測試綁定要存在-r4` r1(2026-10-02,4 席同編制):35 條/blocking 21/全折。四席獨立在「分新舊」的接點找到新錯:借格子舊行判定推送時新行比對到自己(rtb 那 12 條照樣放行)、條款行永遠判新寫、逐篇讀起點與主線各 14–17 秒超過 20 秒上限、主線那一版在 CI 等於終點(永遠不擋)、表態閘那支的 git 出錯與子模組回「找不到」而非例外、「檔裡有 def 就判不了」把一般函式名放行。Enzo 裁換方向:推送時「碰到的筆記整篇要乾淨」——不分新舊、不讀起點與主線、不用舊行判定;判存在第①道改用 `_classify_test_refs`、第②道抽出 `_test_in_tree` 回三態;拿掉 def 判法(Python 類別測試列為已知限制);程式預設 `warn`、本 repo 開 `block`(上線與開擋用設定分開);`_note_shape_eval` 加 `rows_out` 參數(既有容器參數會連帶開格子)。條款重編為 S1–S25。席報告在 `governance/review-reports/筆記測試綁定要存在-r4/`。
- r3(2026-10-02,4 席同編制,上限輪):33 條/blocking 16/全折(Enzo 裁「折入後另開一輪審完整版」)。最大的一條三席獨立實測一致:1c 用 `_ns_text_key` 比核心句,在舊條目補 `[status:superseded]`、測試照留時核心句沒變 → 放行,正好是 rtb 那 12 條的寫法 → 改用格子的舊行判定 `_ns_is_old`(它回「起點那條有沒有已標作廢」)。其他:佔位字與空名稱不再跟起點比(起點已有 4 個待補、49 個空的)、只看新寫的摘要條目;條款定義行改用 `clause_bindings` 同一判法(先在行內提到、後寫在行首的有 17 份 38 條);判存在加「判不了」(git 出錯、逾時、子模組、Python 類別裡的測試),路徑含方括號要跳脫;保險只在推的分支不是目前簽出那條時啟動(測試沒提交照擋);新寫行跟 `_note_shape_eval` 同一趟拿、帶 keep_other;起點用 note-shape 自己的讀檔零件(不跨去用漂移那支)、另加主線那一版、讀不出的筆記不判;整組 20 秒上限、名稱去重;decisions 明寫不掃;不另設上線記號的理由寫明。例:舊條目 `PITFALL:x [test:t_live]` 改成 `PITFALL:x [test:t_live] [status:superseded] [被取代:[[Y]]]` → 修前放行、修後擋。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- r2(2026-10-02,4 席同編制):33 條/blocking 14/全折,無放行、無駁回。r1 換的三個形狀裡有兩個同類再出 major(判新加、判存在),照「同類兩輪換形狀」整類改用外層既有的機制,不再補條件:判新加改用 note-shape 既有的新寫行入口 `_notelines_new`(排除主線、合併只算自己寫的、有上線點;r1 的兩側相減會把合進來的主線算成這次新加),再扣掉起點那一版整個知識庫出現過的名稱;判存在拿掉自寫的 `git grep` 複查(會搜到筆記自己、測試檔呼叫過函式就放行、類別.方法對不上),改用表態閘那支 `_dispositions_check_test`(兩道都過才算、已排除 docs 與 governance)並補類別.方法;抽取改用 `slot_parse`(自寫寬鬆正則是第二套)。另外:擋改回只在推送時(提交時提醒)——Enzo 原裁就是推送,且提交時擋會卡分兩個提交做的中間那個;`[test-gone:]` 補內容檢查(空、佔位字、PITFALL 只剩它沒有防回歸);1c 比對用 `_ns_text_key`(只重排折行不算新寫);推送時單次跳過不記 test_refs(跳過分支在讀範圍前返回,搬了會改既有回傳碼)。例:分支合進主線後推送,主線新增的壞名字 → 修前算這次新加擋下、修後不算;`[test:cmd_note_shape]`(函式名不是測試)→ 修前 grep 在測試檔找到放行、修後第①道判不是測試方法擋下。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- r1(2026-10-02,4 席:正確性-opus、邊界-sonnet、整合-sonnet、架構對齊-sonnet):40 條/blocking 25/全折,無放行、無駁回。三席獨立抓到同一組根問題,換三個形狀:①判「新」從新寫行減整篇改成「這次改到的筆記兩側加總次數相減」(改名、搬行、折行、整篇佔次數都收掉),名稱一次送一個判(壞前綴不再吞掉整行);②拿掉「測試檔有改動就只提醒」(平台根常是 repo 根、提交時筆記自己就算改動,規則會永遠不擋),改成指不到的名稱到被檢查版本的測試檔整字複查;③`[test-gone:]` 提交選填、驗內容(名稱現在不能是真測試)、不算防回歸、不改三選一(同一提交刪測試或壓提交原本寫不出來;只驗形狀會讓假話過關)。其餘照補:寬鬆寫法對齊格子、摘要接回與單行 summary、條款行用 `_CLAUSE_LEAD_RE`、索引空的也跳過、帳本併進 extra 且推送時跳過也記、doctor 段給 S20 與子項定義、落點改 lumos-cli-read 與 bound-tests-gate、接線與報告標題。例:同一篇把一行 `[test:x_dead]` 搬到另一行並改一個字 → 修前擋、修後不擋;一行 `[test:bad:a, t_new_missing]` → 修前整行一筆 bad-name、修後 t_new_missing 單獨列出。席報告在 `governance/review-reports/筆記測試綁定要存在/`。
- 前掃(2026-10-02;其中「`[test-gone:]` 提交驗在分支歷史上」「進 PITFALL 三選一」兩點已被 r1 改掉):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/筆記測試綁定要存在/r1-intake.md`。動到做法的:判「新」的單位從「新寫的行」改成「新加的測試名」(舊行改字原本會被擋);規則自己一組開關與帳本欄位(照格子規則,否則量不到 RETIRE-IF);作廢只認 `[status:superseded]`;`[test-gone:]` 提交照 `_pin_commit` 判在分支歷史上;doctor 段不寫帳;`[test-gone:]` 進格子鍵表與 PITFALL 三選一。
