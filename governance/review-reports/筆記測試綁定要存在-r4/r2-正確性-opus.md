severity: major

# 設計審 r2(另開迴圈)— 正確性-opus

審的版本:凍結快照 `筆記測試綁定要存在-r4/r2-snapshot.md`;對照碼:negguard clone(HEAD 1de0537a)。實驗都在 `tb4-r2-work-正確性-opus/` 底下跑,用 SourceFileLoader 把 `scripts/lumos` 載進同一個程序,沒跑全套。

## F1 rows_out 照字面取「notes 裡的路徑」,會把合進來的主線筆記、只刪行的筆記都算成碰到;S3 用首推夾具測時會空轉變綠
severity: major
blocking: 是
引句:「這組從 rows 取出筆記路徑集合」
file: `scripts/lumos:27336`
file: `scripts/lumos:27397`
file: `scripts/lumos:27380`
1. 推送時 `_notelines_new` 的候選篇是「範圍淨差異裡 AMR 的所有 .md」(27336 的 `--diff-filter=AMR base..tip`,27397 原樣變成 cand),而且每一篇都會 append 進 notes(27380),不管它的 rows 有沒有東西。逐提交的新行(排除主線、合併只算自己寫的)只拿來過濾 rows,不會把篇拿掉。
2. 實驗(`mrepo`):init 有 A/B/C 三篇;feat 改 A、刪 C 的一行;主線改 B 並推上去;feat 再 merge origin/main。把 `_notelines_new` 包一層印出 notes:
   - `--diff 0000…0..feat`(首推,起點是合併後的分岔點):`A rows=[(8,'正文 二','body')]`、`C rows=[]`。這時 B 不在。
   - `--diff ca88a22..feat`(分支之前推過一次,這次推「刪 C」加「合主線」):`A rows=[...]`、`B rows=[]`、`C rows=[]`。
3. 〈做法〉1 說 `rows_out` 收的是「向 `_notelines_new` 要到的 rows」,接著「從 rows 取出筆記路徑集合」。實作的人最順手的寫法是 `{p for p, _t, _r in notes}`,這樣 B(只有主線改過)和 C(只刪不加)都會變成「碰到」,整篇要乾淨。結果是主線上別人留下的舊壞名字擋住這次推送,正好違反〈名詞〉「只是被主線合進來、自己沒寫任何一行的筆記不算碰到」和 S3。
4. S3 的夾具如果照「新分支首推」來造,起點會落在合併後的分岔點,B 根本不在淨差異裡,測試照樣綠。真正會出事的是「分支先推過、更新主線後再推」,而這是 PR 流程最常見的形狀。
5. 要明寫的有兩件:碰到 =「rows 非空的那幾篇」;S3 夾具要用「已推過的分支起點」(像上面 `ca88a22..feat` 那種),不能用全 0 起點。

## F2 第②道拿完整的「類別.方法」去整字 grep,一定找不到,第①道判 real 的 Java/Kotlin/C# 測試會被判成指不到而擋下
severity: major
blocking: 是
引句:「第②道問被檢查的版本裡那個平台的測試檔整字找不找得到」
file: `scripts/lumos:40263`
file: `scripts/lumos:41270`
1. 第①道 `_classify_test_refs` 遇到 `Class.Method` 時,用 `rsplit(".")` 取方法名去比扁平的方法集合(40263),所以判 real。第②道照表態閘那段做,是 `git grep -w -F -e <名稱>`(41270),名稱原樣送進去。原始碼裡類別名跟方法名分在兩處,「FooTest.testBar」這串整個找不到。
2. 實驗(`jrepo`,legacy java-junit,`src/test/FooTest.java` 裡有 `class FooTest { @Test public void testBar() {} }`,已提交):
   - `gate1 classify: [('n', 'java-junit', 'FooTest.testBar', 'real')]`
   - `git grep -w -F -q -e FooTest.testBar <sha> -- ':(glob)**/*.java' …` → `rc 1`
   - 照〈名詞〉的組合規則「第①道過、第②道找不到 → 指不到」,一個真測試被擋。
3. 快照自己寫第①道「類別.方法寫法都已處理」,但第②道沒交代要用哪一段名稱。抽 `_test_in_tree` 時要規定:名稱帶 `.` 的,改 grep 最後一段(或類別、方法兩段都要找到)。S14–S17 也沒有一條會抓到這個錯,要補一條「類別.方法」的條款或夾具。

## F3 `_test_in_tree` 只回三種結果,保不住表態閘原本的分流(S24 照字面做不出來);另外平台根「在子模組裡面」時會判成找不到
severity: major
blocking: 是
引句:「它回三種:找得到、找不到、判不了(git 出錯或逾時、平台根在 repo 外、平台根是子模組)」
file: `scripts/lumos:41261`
file: `scripts/lumos:41274`
1. 表態閘現在的寫法:平台根在 repo 外 → `return True, ""`,當作通過(41261);git grep 回 1 和 0 以外的值 → `return False`,擋(41274 起);逾時會丟例外,由每題外層接住當「無法驗證」,也擋。這三種在新函式裡都併成「判不了」。
2. S24 要求「表態證據的判定應跟原本一樣」。表態閘如果把判不了對到 False,跨 repo 平台根原本放行的表態會變成擋;如果對到 True,原本擋下的 git 出錯和逾時會變成放行(表態閘是一道守衛,這樣是放寬)。只有三態、不帶原因,兩種對法都違反 S24。所以 `_test_in_tree` 要另外帶「為什麼判不了」,或把「根在 repo 外」留在呼叫端先判掉。
3. 子模組實驗(`suprepo`,`vendor/app` 是子模組,測試在 `vendor/app/Tests/test_x.py`):
   - `git grep … ':(glob)vendor/app/Tests/**/*.py'` → `rc=1`(就是「找不到」)
   - `git ls-tree <sha> -- vendor/app/Tests` 什麼都不印、`rc=0`;只有 `vendor/app` 本身才印 `160000 commit …`
   - 所以平台根設成 `vendor/app/Tests`(子模組裡面)時,只看「平台根本身是不是 gitlink」判不出來,第②道會回找不到,真測試被判指不到而擋下。判不了的條件要寫成「平台根落在某個 gitlink 底下(含等於它)」。

## F4 作廢的合約行掛活測試時,照擋下訊息給的改法(拿掉,或移到接手那條)會讓這行變成裸合約,doctor --ci 換成在推送前與 CI 擋
severity: major
blocking: 是
引句:「作廢的條目(含條款定義行、合約行)掛著活測試 → 違規」
file: `scripts/lumos:1646`
file: `scripts/lumos:43914`
1. Check T 會把 summary 裡每一條 `★INVARIANT★` 都抽出來,標了 `[status:superseded]` 的也不跳過。只要沒有 `[test:]`,就收進 naked(1646),走 `warn` 加 issues。`doctor --ci` 等於 strict(43914),有 issue 就回 1;推送前掛鉤跑 `doctor --ci`,CI 的「Graph doctor (strict)」也跑。
2. 〈做法〉3 第 4 項的改法只有兩種:條款定義行改寫成 `[manual:…]`;摘要條目「把綁定移到接手的那一條,或拿掉」。合約行屬於摘要條目,照做以後 `[test:]` 沒了,變成裸合約,Check T 讓推送前和 CI 紅。改成 `[test-gone:]` 被同一項明文禁止(測試還在),而且 Check T 只認 `[test:]`,一樣是裸的。S10 要求「給那種行的改法」,合約行目前沒有一條改得通的路。
3. 合約行要另給一種改法:拿掉 `★INVARIANT★` 記號(降成一般條目),或整行刪掉。或者反過來,讓 Check T 跳過作廢的合約行;那樣就是改動另一個系統,要列進 lands_in 與〈做法〉11。未實測,依據是讀碼。

## F5 帳本欄位量不出 REVISIT 和 RETIRE-IF 第②條要的數字
severity: major
blocking: 是
引句:「而推送者放棄推、改用單次跳過 → 改回只擋新加的(另開設計)」
file: `scripts/lumos:28701`
file: `scripts/lumos:28702`
file: `scripts/lumos:28572`
1. REVISIT 寫的是「照帳上 note-shape 事件的 `test_refs` 欄位數擋下次數」,〈做法〉8 又說「這組的有無只看 `extra.test_refs`」。問題是 test_refs 在兩種情況下會跟著別的規則的擋一起寫進帳:(a) 提交時這組一律只提醒,但同一次提交被形狀規則擋下,事件 kind=blocked,extra 裡卻有 test_refs;(b) 推送時這組因為保險只提醒,同一次被形狀規則或格子擋下,也一樣。照 REVISIT 的數法,這兩種都會算成「這組擋下」,次數灌水。帳上要再多一個旗標,記這組自己這次是擋還是提醒,例如 `test_refs.mode`。
2. RETIRE-IF 第②條要分辨「擋下的是碰到舊筆記被迫修的舊帳」,還是新寫的名字。可是帳本只記條數、名稱、原因,不記那個名稱所在的行是不是這次新寫的。推送時的單次跳過,快照自己也說「那筆沒有 `test_refs`」。提交時的單次跳過記的是只提醒的那一側,跟「推送者放棄推」對不上。所以第②條拿現有欄位算不出來。要嘛帳上每個名稱多記一個「在不在這次新寫的行上」(rows 已經有行號,可以直接比),要嘛把第②條改成量得到的指標。
3. 順帶一提:`_note_shape_report` 的 nodes 只從 viol、errs、sviol 收(28701)。只有這組違規時 nodes 是空的,`lumos gov` 依節點查不到這些事件,去重鍵裡的節點集合也變成空集合。〈做法〉8 沒說 nodes 要不要併進這組的筆記。

## F6 rows 也收開頭欄位的其他欄(keep_other),只改 `updated:` 或 `lumos set` 改狀態就算碰到,跟〈名詞〉引的定義不一樣
severity: minor
blocking: 否
引句:「新寫的行照筆記內容閘既有定義」
file: `scripts/lumos:28408`
file: `scripts/lumos:27431`
1. `_note_shape_eval` 呼叫 `_notelines_new` 時帶 `keep_other=True`(28408),開頭欄位 other 區塊的新行只要對得上淨差異,就會進 rows(27431)。`_notelines_new` 的說明寫的既有定義,是只收 body、summary、decisions 三塊。
2. 實驗:在 C.md 的開頭欄位只加一行 `updated: 2026-10-02`,提交後 `--diff HEAD~1..HEAD`,印出 `C.md rows= [(3, 'updated: 2026-10-02', 'other')]`。照 F1 的「rows 非空」來判,這篇算碰到,整篇要乾淨。
3. 這樣一來,`lumos set <節點> status done`、改名連帶改 related 這類工具只動開頭欄位的操作,都會逼那篇修舊帳。要不要算碰到,快照得明寫一句(建議只算 body、summary 兩區)。

## F7 「HTML 註解裡的不算」沒有任何既有零件做得到,而全檔兩支可見性函式都明文拒絕偵測註解
severity: minor
blocking: 否
引句:「HTML 註解裡的不算」
file: `scripts/lumos:4182`
file: `scripts/lumos:372`
1. 快照講到可見性的地方,引的只有 `_visible_lines`(圍欄)和 `slot_parse`(反引號)。`_visible_lines` 寫著「★不偵測 HTML 註解★」,理由是 `-->  <!--` 先關再開會把後面整份藏掉(4182);`_strip_inline_markup` 也寫「★不碰 HTML 註解★」(372)。
2. 照字面實作,就得新寫一套註解偵測,等於重開這兩支已經判定是洞的那條路:一個沒關的 `<!--` 會讓後面所有壞名字都放行。這句要嘛刪掉,改成「註解裡的照算,跟 clause_bindings 一致」;要嘛限定「同一行內成對的 `<!-- … -->`」,並補一條會翻紅的條款。

## F8 本 repo 的測試都寫在已追蹤的 test_lumos.py,所以 S15 說的「測試寫了還沒提交」在本機永遠落進保險、只提醒;保險的量法也沒寫清楚
severity: minor
blocking: 否
引句:「新寫了還沒提交的測試檔不在保險內,照擋」
file: `scripts/lumos:5094`
1. 本 repo 的測試只認 `scripts/test_*.py` 裡 `def t_…`,新測試都是改已追蹤的 `scripts/test_lumos.py`。照〈做法〉5,這是「已追蹤的測試檔有沒提交的修改」,保險啟動,這組只提醒。S15 的字面是「測試寫了還沒提交 … 應回 1」,只有在「新開一支沒追蹤的測試檔」時才成立。條款要改寫成「新檔」,不然夾具照本 repo 的寫法造,會回 0。
2. 「已追蹤」用哪支指令量沒寫。用 `git diff HEAD` 的話,已經 `git add` 的新測試檔會顯示成 A,被算進保險,跟「新寫的照擋」相反;用 `git diff`(工作目錄對索引)又會漏掉已暫存的修改。要明寫成 `git diff HEAD --diff-filter=MD`,或其他等價寫法。
3. 第①道的 `load_platforms` 讀的是工作目錄的 `.lumos/config.json`(5094),note-shape 自己的設定卻從終點讀。設定檔有沒提交的改動(例如 platforms 改了)時,兩邊對不上,保險也沒蓋到。要嘛把設定檔一起列進保險,要嘛寫成已知限制。

## F9 推送前掛鉤與 CI 擋下時印的原因和逃生句只講形狀規則,這組擋下時會叫人把整道 gate 設成 warn
severity: minor
blocking: 否
引句:「skill 指令速查 03、06(note-shape 擋下種類)、04(S20)、INDEX、reference.md」
1. `scripts/hooks/pre-push` 在 note-shape 回 1 之後,寫死一句逃生指示:「行號改成函式名或測試名…;整個專案先只提醒 → note_shape.gate 設成 warn」。`.github/workflows/ci.yml` 第 144 行的 `::error::` 也寫死「筆記新寫了程式行號引用或沒寫來源的現況描述」。
2. 這組上線後,只因為測試名擋下的推送會看到講錯原因的訊息,而且逃生句叫人關掉整道 note-shape,不是只關 `note_shape.test_refs`。〈做法〉11 要同步的清單裡沒有這兩支,也沒有 doctor 給消費專案貼的 CI 那步文字。要把它們加進去,逃生句補上 `note_shape.test_refs: warn`。

## 各節核對
- 開頭欄位、白話段、依據:已讀,無 finding(lands_in 的四篇與 related 的連結都對過真檔)。
- PRIOR-ART、RETIRE-IF、REVISIT:RETIRE-IF 第②條量不出來,見 F5;其他已讀,無 finding。
- 名詞:碰到的筆記見 F1、F6;HTML 註解見 F7;第②道見 F2、F3;其他已讀,無 finding。佔位字、作廢判法、`slot_parse` 對反引號的處理都對過碼(成對反引號裡的方括號不當欄位)。
- 範圍:已讀,無 finding。
- 做法 1:F1。做法 2:已讀,無 finding(notes 裡已經帶終點全文)。做法 3:第 4 項見 F4,其他已讀,無 finding。做法 4:已讀,無 finding(本 repo 索引 0.08 秒,一次 git grep 約 0.09 秒;最多測試名的一篇有 54 個不同的名字,換算約 5 秒,在 20 秒上限內)。做法 5:F8。做法 6:已讀,無 finding。各種開關組合對照 `_ns_slots_mode` 的寫法,造得出來;本 repo 加 `note_shape` 物件不會改到 gate 和 slots 的預設。做法 7:已讀,無 finding。做法 8:F5。做法 9:已讀,無 finding。做法 10:已讀,無 finding。做法 11:F9。
- 條款:S3 見 F1,S10 見 F4,S15 見 F8,S24 見 F3;其他條款照字面造得出來。
- 回退:已讀,無 finding。
- 實務隱患(逐類):
  - 誤擋:F1、F2、F3(子模組裡的平台根)、F4。
  - 漏網:F7(偵測註解反而會藏東西)、F8(本 repo 在本機永遠只提醒,要靠 CI)。
  - 時間:量過,在上限內。
  - 相容:預設 warn,消費專案更新後不會被擋,無問題。
  - 帳本與量測:F5。
  - 對外送出、金流:無。只讀筆記和測試檔,不連網。
  - 不可逆:無。revert 就回得去。

最高等級:major,blocking 共 5 條
