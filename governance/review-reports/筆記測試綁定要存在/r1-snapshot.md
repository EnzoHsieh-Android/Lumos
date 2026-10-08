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
  - Systems/check-t-sentinel
related:
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Projects/筆記格子寫法與過期檢查_計劃]]"
  - "[[Systems/筆記內容閘]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/bound-tests-gate]]"
---
# 筆記測試綁定要存在_計劃

白話:筆記裡寫 `[test:測試名]` 是在說「這件事有這支測試守著」。現在只有合約行(★INVARIANT★)與計劃的驗收條款會核對那支測試真的存在;摘要裡的 WHY、PITFALL、RULE 和正文裡的 `[test:]` 寫錯名字、或測試後來被刪了,沒有任何地方發現,讀的人會以為有守衛。這份計劃做兩件事:①新加進筆記的測試名指不到真測試就擋(全庫既有的只在健康檢查提醒);②已經標成作廢的行還掛著活的測試就擋——那支測試守的是已經不成立的事,常常還是相反的事。

依據:
- 路線圖 1b(所有筆記的測試名要驗存在)、1c(撤除的東西不准再掛活測試)([[Projects/漂移防治路線圖_計劃]]);Enzo 2026-10-01 裁順序,2026-10-02 裁三件:推送擋新寫的、全庫只提醒;新寫的 `[test:待補]` 不准、改寫防回歸無;1c 同一案。
- rtb(另一個用 lumos 的消費專案)2026-10-01 全圖譜巡檢:懸空 `[test:]` 56 個、至少 3 個從沒存在過;撤除條款仍掛活 `[test:]` 12 條、3 條綁的是斷言反面的測試(在 rtb 的 repo 裡:提交 a7b3b2d 的 governance/audits/2026-10-01-drift-sweep/findings.md)。
- 2026-10-02 用最新 lumos 對 rtb 的唯讀副本(rtb 的提交 ef9ae20)量測:計劃正文還有 57 個指不到的(42 個是測試在 rtb 的提交 b2fc512 被刪)、摘要 1 個。本 repo 合約以外帶 `[test:]` 的摘要行 373 行,指不到的 26 個:4 個 `待補` 佔位、12 個文件裡的範例寫法(平台前綴沒定義,判成名稱不合法)、7 個其他「只出現在程式文字裡」、3 個哪裡都沒有。
- [[Projects/筆記格子寫法與過期檢查_計劃]] 天花板 3:格子只驗 `[test:]` 有寫,存在交給本案。

PRIOR-ART: 全部沿用既有零件——判測試存在用推送前合約測試閘那一支 `_classify_test_refs`(多平台、分 real/fake/dangling/bad-name;本案是它第三個呼叫者,不另寫判法);測試索引 `_platform_test_index`;新寫的行用筆記內容閘既有的抽取(提交時 `_notelines_new`、推送時 `_notelines_range_added`);圍欄用 `_visible_lines`、反引號用 `_strip_inline_markup`;作廢用 `_ns_superseded`;規則自己一組開關、自己的違規清單與帳本欄位,照筆記格子規則(`note_shape.slots`)的形狀;`[test-gone:]` 的提交檢查照 `_pin_commit`(在分支歷史上,不只物件存在);全庫提醒照 doctor S17–S19 的寫法(不寫帳)。世界解:文件連結檢查工具(如 lychee、Sphinx linkcheck)也是「新寫的擋、存量另列」;`[test-gone:]` 沿用 rtb 2026-10-01 標籤提案。
RETIRE-IF: 上線滿 8 週,抽查帳上 20 筆這條規則擋下的測試名,其實存在、是索引沒認出的超過一半 → 規則改回只提醒;或滿 8 週全部專案零擋下、doctor 這段也沒列出任何新的 → 擋留著、doctor 段降到 `--verbose` 才印。
REVISIT:2026-12-01 照帳上 note-shape 事件的 `test_refs` 欄位數擋下次數與名稱,抽 20 筆判 RETIRE-IF;順便看單次跳過時記下的 `test_refs` 條數。

## 名詞

- **note-shape / 筆記內容閘**:`lumos note-shape` 指令,提交前掛鉤跑 `--staged`、推送前與 CI 跑 `--diff 起點..終點`;節點 [[Systems/筆記內容閘]] 管它。**單次跳過**:環境變數 `LUMOS_SKIP_NOTE_SHAPE=1`,整道跳過一次並記帳。**治理帳**:`docs/.governance-log.jsonl`,各道閘的事件。
- **測試名**:筆記任一行裡 `[test:名稱]` 的名稱(同一個方括號可用逗號列多支;設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱)。程式碼圍欄(``` 圍住的)與反引號裡的不算——那是範例;反引號沒閉合時,那之後的整行都不算(寧可少認)。
- **指得到真測試**:`_classify_test_refs` 判 `real`。`fake`(名字只出現在程式文字裡、不是測試方法;短名容易這樣)、`dangling`(哪裡都沒有)、`bad-name`(平台前綴沒定義或名稱不合法)都算指不到。
- **新加的測試名**:這次提交或推送的新寫行裡出現、而同一篇筆記在起點版本裡沒出現過的測試名(同名出現幾次就比幾次)。改到舊行時,舊行原本就有的名字不算新加。
- **合約行**:摘要裡 `KEY:★INVARIANT★` 開頭的行,已由 doctor Check T(合約有沒有綁到真的測試)驗存在,波及到的另由推送前合約測試閘真跑。**條款定義行**:計劃(type: project)裡行首是 `[SN]` 的驗收條款,由條款綁定管(spec-trace 列狀態、doctor S5 提醒)。這兩種行本案不查。正文裡的 `KEY:★INVARIANT★`、非計劃筆記裡行首 `[SN]` 的行不是這兩種,照查。
- **明標刪除**:`[test-gone:名稱@提交]`——這支測試在那個提交被刪。不驗名稱存在,只驗寫法與提交(至少 12 碼、在某個分支的歷史上;淺層 clone 判不了就略過那一筆)。
- **作廢的行**:帶 `[status:superseded]` 的行(`_ns_superseded`;筆記格子規定這種行另必帶 `[被取代:]`)。只有 `[被取代:]` 沒有 status 的行不算作廢。**活測試**:指得到真測試的測試名。
- **佔位字**:測試名整個是 `待補`、`待定`、`TODO`、`TBD`(不分大小寫)其中之一。

## 範圍

- 做:note-shape 多一組規則「新加的測試名要指得到」與「作廢的行不准掛活測試」(提交與推送都跑);認得 `[test-gone:]` 並登記成格子鍵;doctor 多一段全庫提醒(含散文撤除的候選);設定 `note_shape.test_refs`。
- 不做:合約行與條款定義行(各有檢查);不真跑測試;不自動把指不到的改成 `[test-gone:]`(要人判刪了、改名還是寫錯);不清 rtb 或本 repo 既有的(各自清,見路線圖的循環);散文寫的撤除(rtb 那 12 條的寫法)不擋,只在 doctor 列候選——判不準,詳〈實務隱患〉。

## 做法

1. **抽取**:`_note_test_refs(line)` 對一行(先經 `_strip_inline_markup`)抽出 `[test:…]` 與 `[test-gone:…]`;圍欄內的行由呼叫端用 `_visible_lines` 略過。合約行(摘要裡、`INVARIANT_RE`)與計劃裡的條款定義行(行首 `[SN]`)略過。
2. **新加的判定**:起點版本那篇筆記(提交時是 HEAD、推送時是範圍起點;新檔就是空)用同一支抽取得到名稱多重集合;新寫行裡的名稱扣掉它,剩下的才查。
3. **判存在**:有要查的名稱時才 `_platform_test_index` 一次;每一行(去反引號後的整段)交給 `_classify_test_refs`。平台前綴沒定義時它整段只回一筆,訊息照印它的錯誤字串。索引建不起來(設定壞丟例外)→ 這組規則這次跳過、印一行原因(note-shape 本來就 fail-open)。
4. **違規**(這組自己的清單,跟其他 note-shape 規則分開收):
   - 新加的測試名指不到 → 印筆記、行號、名稱、判定與改法:改成真的測試名;測試已刪就寫 `[test-gone:名稱@提交]`;沒有測試就拿掉——PITFALL 改寫 `[防回歸:無 理由]` 或 `[repro:指令]`,其他前綴直接拿掉。
   - 新加的是佔位字 → 同上,訊息照前綴給改法(不靠判定種類:`待補` 在某些 repo 會判成 fake)。
   - 新寫行裡的 `[test-gone:]` 寫法不對(沒有 `@`、提交不到 12 碼、不在任何分支歷史上)→ 違規。
   - (1c)新寫的作廢行掛著活測試 → 違規:改成 `[test-gone:]`,或把綁定移到接手的那一行(`[被取代:]` 指的那裡)。
5. **開關與總開關**:`note_shape.test_refs: block`(預設)| `warn` | `off`,寫壞照 `block` 並提醒一句(同 `note_shape.slots`);總開關 `note_shape.gate` 是 `off` 整組不跑、是 `warn` 這組也只提醒。新寫一支 `_note_shape_test_refs_parse`(子鍵各有自己的解析,是既有前例)。
6. **測試索引從哪裡讀**:筆記與 `note_shape.*` 照 note-shape 讀被檢查的版本;測試索引(`platforms` 與測試檔)讀工作目錄,跟推送前合約測試閘一樣。工作目錄裡有沒提交的改動落在各平台的測試檔上時(新寫一支小函式用 `git status --porcelain` 對平台根判),兩邊可能不一致——這次這組只提醒不擋,訊息講原因。
7. **帳本**:這組有違規時,note-shape 的事件多帶 `test_refs` 欄位(條數與前 20 個名稱、各自判定);單次跳過時也先算一次記進去(照格子的 `_ns_skip_slot_extra`)。RETIRE-IF 靠這欄抽查。
8. **格子鍵**(2026-10-02 跟筆記格子那邊的會談對齊,它同意形狀):
   - `test-gone` 登記進 `_SLOT_KEYS` 與 `_SLOT_REPEATABLE`;**不進** `_SLOT_NEW_ONLY`(新文法才有的鍵)——舊寫法的 PITFALL 改寫成 `[test-gone:]` 時不該因此被當成新文法、被要求補齊新格子(rtb 有 42 處舊行要這樣改)。
   - PITFALL 的三選一改成四選一(`test`、`test-gone`、`repro`、`防回歸`);「三選一」是寫死的字,三處一起改成照組員數寫:程式組必有鍵說明那行、測試裡解析範本表的 helper(只認「三選一」)、紀律範本的格子表(寫成「`test`、`test-gone`、`repro`、`防回歸` 四選一」);`t_slots_single_table` 釘兩邊一致。
   - 格子規則的 `slot_check` 是純函式(提交時與 lint 共用),只驗 `[test-gone:]` 的形狀:名稱非空、`@` 後至少 12 碼十六進位;「在分支歷史上」那一半要跑 git,放在本案自己的檢查(〈做法〉4)。已作廢的行格子規則照慣例跳過,跟本案 1c 不衝突(1c 是本案自己這組規則查)。
   - 筆記格子那篇計劃一起改:〈格子規格〉PITFALL 那列、〈範本寫法〉的「三選一」寫法、提到 test/repro/防回歸 的條款改成四選一並註明出處是本案;天花板 3 改指到本案。
9. **全庫提醒**:doctor 新一段(提醒,不擋;照 S17–S19 不寫帳,同一批每次重唸會灌水)列出所有筆記指不到的測試名、寫法不對的 `[test-gone:]`、作廢的行掛活測試;另列散文撤除的候選:計劃裡條款定義行仍有 `[test:]`,而它下一層子項含「撤除」且不含「保留」。每類預設印 3 條、`--verbose` 全列。

## 條款

- [S1] 當新加的測試名(合約行與條款定義行除外)指不到真測試時,note-shape 應回 1 並列出筆記、行號、名稱與判定 [test:t_note_shape_test_refs_new_names]
- [S2] 當指不到真測試的名稱是舊行原本就有、這次只改了那一行的其他字時,note-shape 應不擋 [test:t_note_shape_test_refs_new_names]
- [S3] 當新加的測試名是佔位字而行首是 PITFALL 時,擋下訊息應給 `[防回歸:無 理由]` 與 `[repro:]` 兩種改法 [test:t_note_shape_test_refs_placeholder]
- [S4] 當新加的測試名是佔位字而行首不是 PITFALL 時,擋下訊息應叫人拿掉或改成真名、不給防回歸改法 [test:t_note_shape_test_refs_placeholder]
- [S5] 當行上 `[test-gone:名稱@提交]` 的提交在分支歷史上時,note-shape 應不驗那支測試存在 [test:t_note_shape_test_gone_marker]
- [S6] 當新寫行的 `[test-gone:]` 缺 `@`、提交不到 12 碼或不在任何分支歷史上時,note-shape 應回 1 [test:t_note_shape_test_gone_marker]
- [S7] 當 `[test:]` 只出現在程式碼圍欄或反引號裡時,note-shape 應不查它 [test:t_note_shape_test_refs_skip_examples]
- [S8] 當新寫的行帶 `[status:superseded]` 又掛著指得到的 `[test:]` 時,note-shape 應回 1 並建議改成 `[test-gone:]` 或移到接手的那一行 [test:t_note_shape_retired_line_live_test]
- [S9] 當工作目錄有沒提交的改動落在測試檔上時,這組規則應只提醒不擋並說原因 [test:t_note_shape_test_refs_dirty_tests_warn]
- [S10] 當測試索引建不起來時,這組規則應跳過並印一行原因、note-shape 照其他規則判 [test:t_note_shape_test_refs_index_fail_open]
- [S11] 當 doctor 跑時,doctor 應另一段列出全庫指不到的測試名、寫法不對的 `[test-gone:]`、作廢的行掛活測試與散文撤除的候選,並且不影響回傳碼 [test:t_doctor_note_test_refs]
- [S12] 當 `note_shape.test_refs` 是 `warn` 或總開關 `note_shape.gate` 是 `warn` 時,這組規則應只提醒不擋 [test:t_note_shape_test_refs_config]
- [S13] 當 `note_shape.test_refs` 或總開關是 `off` 時,這組規則應不跑 [test:t_note_shape_test_refs_config]
- [S14] 當這組規則擋下或被單次跳過時,治理帳那筆事件應帶 `test_refs` 欄位(條數與名稱) [test:t_note_shape_test_refs_ledger]
- [S15] 當 PITFALL 行只寫 `[test-gone:]` 而沒有 `[test:]`、`[repro:]`、`[防回歸:]` 時,格子規則應算它滿足防回歸那一格 [test:t_slots_pitfall_test_gone]

## 回退

- revert 實作提交即可。已寫進筆記的 `[test-gone:]` 留著:revert 後格子規則不認得這個鍵,會把它當核心句文字;PITFALL 只靠它滿足三選一的行會在下一次改到時被格子規則擋,要改寫成 `[防回歸:無 …]`。帳上多出的 `test_refs` 欄位舊讀端忽略。
- 只想先停擋:`note_shape.test_refs: warn` 或 `off`。

## 實務隱患

- **誤擋**:索引沒認出的測試寫法(參數化名稱、類別裡的方法)會被判指不到;短名可能被判 fake。緩解:用合約測試閘同一支判法;`warn` 可退;RETIRE-IF 抽查帳上名稱。
- **散文撤除擋不到**:rtb 那 12 條撤除是「條款下一層寫一段撤除裁定」的散文,不帶 `[status:superseded]`,規則擋不到,只會進 doctor 候選(關鍵字判,會有「保留……舊斷言撤除」這種假候選,所以排除含「保留」的)。要擋得住得在撤除時補標記——列進 rtb 清理的回傳要求。
- **兩邊讀的版本不同**:筆記讀被檢查的版本、測試索引讀工作目錄;靠「測試檔有沒提交的改動就只提醒」收斂,剩下的差異(測試檔已提交、但被檢查的版本比工作目錄舊)在推送時可能出現:終點提交之後工作目錄又刪了一支測試,推送時會誤擋。發生時用單次跳過,帳上看得到。
- **時間**:只在有要查的名稱時才建索引;本 repo 測試總檔約 6 萬行,遇到指不到的名稱還要建一次程式文字全文(分 fake 與 dangling)。實作時量一次提交與推送各多幾秒,寫進〈實作紀錄〉。doctor 這段每次全掃,CI 的 doctor 也會多這一次。
- **相容**:消費專案 `lumos update` 後,新加壞名字會被擋——本案本意;既有的不擋。升級前寫好、升級後才推的提交,只有真的新加了壞名字才擋。
- **跟筆記格子的接點**:動格子鍵表與 PITFALL 三選一,先跟那邊的會談對齊。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀筆記與測試檔,不連網
- 已排除:不可逆:只擋提交與推送、只印提醒,revert 回得去
- 守衛面:新增一組提交與推送時的擋,有 `warn`/`off` 與單次跳過可退,單次跳過照記帳。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- 前掃(2026-10-02):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/筆記測試綁定要存在/r1-intake.md`。動到做法的:判「新」的單位從「新寫的行」改成「新加的測試名」(舊行改字原本會被擋);規則自己一組開關與帳本欄位(照格子規則,否則量不到 RETIRE-IF);作廢只認 `[status:superseded]`;`[test-gone:]` 提交照 `_pin_commit` 判在分支歷史上;doctor 段不寫帳;`[test-gone:]` 進格子鍵表與 PITFALL 三選一。
