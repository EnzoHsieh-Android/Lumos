severity: major

# 設計審 r1 正確性-opus 席:筆記測試綁定要存在_計劃

審查鏡頭:照字面實作會不會判錯。實驗都在 `tb-r1-work-正確性-opus/` 底下做(repo clone、g1–g4 小 git 庫、exp1–exp6 腳本),沒動被審 repo。

## F1 整行交給 `_classify_test_refs`:同一行只要有一個平台前綴寫錯,整行就只剩一筆錯誤字串,分不出哪些名稱是新加的
severity: major
blocking: 是
引句:「平台前綴沒定義時它整段只回一筆,訊息照印它的錯誤字串」
file: `scripts/lumos:40254`
file: `scripts/lumos:5181`
1. `_classify_test_refs` 是先對整段文字跑 `resolve_test_refs`,只要有一段前綴沒定義就丟 ValueError,接著整行只回一筆 `(node, "?", 錯誤字串, "bad-name")`。同一行其他名稱的判定全部丟掉,方法欄放的是錯誤字串,不是名稱。
2. 〈做法〉2 說只查扣掉舊名之後剩下的新名,〈做法〉3 卻說整行交出去。這兩步接不起來。實驗 exp1(多平台設定 py/kt):
   - A:舊名 `[test:zz:t_old]` 已經在那一行上,這次只新加真測試 `[test:py:t_real_a]`。結果只回一筆 bad-name,錯誤字串講的是 t_old。
   - C:舊名 `[test:zz:t_old]` 加上這次新加的錯名 `[test:t_typo]`。結果還是只有那一筆 t_old 的 bad-name,t_typo 完全沒判。
3. 實作的人只有兩條路,兩條都錯:
   - 看到 bad-name 就擋:A 情形等於擋了舊名,違反 S2。
   - 只留「名稱在新加集合裡」的那幾筆:這一筆的名稱欄是錯誤字串,會被濾掉,C 情形的 t_typo 就漏查,違反 S1。
4. 改法:不要整行交出去,而是每個新加名稱各自組成 `[test:名稱]` 再交給 `_classify_test_refs`。一個名稱一次呼叫,前綴錯誤只會落在它自己身上。〈做法〉3 要改成這樣寫,S1/S2 的測試要各加一個「同一行有舊的壞前綴」的夾具。

## F2 起點版本照新路徑去找:筆記改名或搬家又改了一個字,舊名稱會被當成新加的擋下
severity: major
blocking: 是
引句:「起點版本那篇筆記(提交時是 HEAD、推送時是範圍起點;新檔就是空)用同一支抽取得到名稱多重集合」
file: `scripts/lumos:27355`
file: `scripts/lumos:28266`
1. 新寫行是用 `git diff -U0 -M` 抽的。改名時改名偵測會成立,所以只有改過的那一行算新寫。但照計劃,起點版本是拿新路徑去讀,改名前那個路徑上沒有這個檔,於是當成「新檔就是空」。
2. 實驗 g2:筆記 A.md 裡有一行 `- WHY:舊句 [test:t_gone_old]`,另外 30 行沒動。執行 `git mv A.md B.md`,再把「舊句」改成「舊句改字」。結果:
   - diff 只有一行新增:`+- WHY:舊句改字 [test:t_gone_old]`。
   - `git cat-file -e HEAD:docs/k/Systems/B.md` 回 `fatal: ... not in 'HEAD'`。
   - 所以起點集合是空的,t_gone_old 算新加,而且是 dangling,被擋。這違反 S2(只改舊行的其他字不擋)。
3. 小檔或改動多時改名偵測不成立(g1 就是這樣),整篇每一行都算新寫,整篇所有舊的壞名稱一起被擋。
4. 推送時也一樣。`_notelines_range_added` 會把逐提交的文字帶到終點路徑(`_carry`),但「起點版本」這一半計劃沒有說要照改名對回舊路徑。
5. 前例的做法不是這樣:格子規則的「上一版」是「HEAD 版本加上這次 diff 刪掉的行」(`_ns_slots_old_lines`)。刪掉的行在改名時就是舊路徑上的原文,所以格子規則不會被改名騙到。
6. 改法:起點集合改成「起點同路徑版本 + 這次範圍裡被刪掉的行」,照格子前例做;或者照 diff 的改名對照用舊路徑去讀。計劃也要講清楚跨篇搬內容(拆節點、把一段搬到另一篇)算不算新加。照現在字面是算,舊壞名稱搬家就會被擋。

## F3 新寫行減的是起點整篇:沒改的舊行也佔掉額度,同一篇再引用一次既有的壞名稱不會被查
severity: major
blocking: 是
引句:「新寫行裡的名稱扣掉它,剩下的才查」
file: `scripts/lumos:27355`
1. 〈名詞〉說「同名出現幾次就比幾次」,本意是數次數。可是被減數是「新寫行的名稱」,減數是「起點整篇的名稱」。起點裡那一次出現的行如果這次沒動、還留在終點,也照樣把額度用掉。
2. 實驗 g1(第二段):B.md 第 6 行已有 `[test:t_gone_old]`(指不到),這次新增一行 `- 新段落也提到 [test:t_gone_old]`。
   - 新寫行是 {t_gone_old:1},起點整篇也是 {t_gone_old:1},相減為空,所以不查。
   - 但這是一句新寫的引用,而且指向不存在的測試,正是這條規則要擋的東西。
3. 改法:直接比整篇次數,用終點整篇減起點整篇,次數有增加的才算新加,再到新寫行上去報。這樣改舊行(次數不變)、同篇搬行(次數不變)照樣不擋,多引用一次(次數加一)就會擋。S1 要加一個「同篇複製既有壞名」的夾具。

## F4 「工作目錄有沒提交的改動」用 porcelain 對平台根判:提交時幾乎永遠只提醒,本 repo 推送時也是
severity: major
blocking: 是
引句:「新寫一支小函式用 `git status --porcelain` 對平台根判」
file: `scripts/lumos:5111`
file: `scripts/lumos:4993`
1. 沒設 `platforms` 的專案(本 repo 就是,`.lumos/config.json` 只有 `test_profile: python`),平台根就是 repo 根。`git status --porcelain` 也會列出已暫存的檔。實驗 g1(第三段):同一個提交暫存一支新測試和引用它的筆記,porcelain 印出 `M  docs/k/Systems/B.md` 與 `M  scripts/test_x.py`。
2. 照引句字面對平台根判,正在提交的那篇筆記本身就落在根底下,所以提交時一定是「有沒提交的改動」,這組規則永遠只提醒。S1 在提交時根本擋不了。
3. 就算收窄到測試檔(python profile 的 `test_*.py`):專案規矩是程式、測試和筆記同一個提交,而一邊寫新測試一邊在筆記寫 `[test:]`,正是名稱最容易打錯的時候。這種提交裡測試檔一定是已暫存,所以照樣只提醒。
4. 本 repo 的主工作目錄長期有沒提交的檔(會談開頭的 git status 就有 `M docs/.governance-log.jsonl` 等)。用根判的話,從主工作目錄推送也一律只提醒。
5. 「提交時也擋」是計劃自己多加的(使用者裁的是推送擋)。上面這種「索引跟工作目錄不一致」的問題,就是多加了提交時才帶進來的。
6. 改法:
   - 提交時只看「暫存版跟工作目錄不一樣」的測試檔:`git diff --name-only`(不帶 `--cached`)加上未追蹤檔,再用 profile 的 `exts`/`file_name_match` 篩出測試檔。這樣已暫存而且跟工作目錄一致的測試不會讓規則降級。
   - 推送時見 F5。
   - 〈做法〉6 要寫明「測試檔」怎麼認,不要寫「對平台根」。

## F5 推送時終點不是目前簽出的提交:測試索引來自另一條分支,誤擋與漏擋計劃都沒收
severity: major
blocking: 是
引句:「剩下的差異(測試檔已提交、但被檢查的版本比工作目錄舊)在推送時可能出現」
file: `scripts/hooks/pre-push:73`
file: `scripts/hooks/pre-push:359`
1. 推送前掛鉤會對每一條要推的參照各跑一次 `note-shape --diff <起點>..<_lsha>`,但測試索引永遠讀當下的工作目錄。
2. 情境:人在 main 上,執行 `git push origin feat`;feat 加了測試 `t_new`,feat 的筆記也新加了 `[test:t_new]`。
   - 工作目錄是乾淨的 main,所以 F4 的降級不會觸發。
   - 索引裡沒有 t_new,判成 dangling,擋下。
   - 反過來也會出錯:feat 刪了某支測試,又新加一句引用它,main 的工作目錄裡還有這支測試,結果放行。
3. 計劃的實務隱患只講了「終點之後工作目錄又刪了一支測試」這一種,沒講「推的根本不是目前簽出的分支」。同一次推送推多條參照時也一樣。
4. 未實測,依據是讀碼(掛鉤逐參照迴圈,測試索引經 `load_platforms(repo_root)` 走訪工作目錄)。
5. 改法:推送時先比 `git rev-parse HEAD` 跟終點,不同就讓這組只提醒並講原因(便宜而且確定);或者索引改從終點的樹讀。這兩個情境要寫進 S9。

## F6 平台根不存在,或掃不到任何測試時,不會丟例外,所有名稱都判成 dangling 被擋,沒有走 fail-open
severity: major
blocking: 是
引句:「索引建不起來(設定壞丟例外)→ 這組規則這次跳過、印一行原因」
file: `scripts/lumos:5127`
file: `scripts/lumos:40265`
1. `load_platforms` 遇到 root 不存在時只印一句警告,不丟例外。之後 `methods_for` 回空集合,`_classify_test_refs` 就把那個平台每個名稱判成 dangling。
2. 實驗 exp6:設定 `platforms` 有 and(root=android,存在)與 ios(root=ios,不存在)。`_platform_test_index` 正常回傳,沒丟例外;`[test:ios:t_ios_real]` 判成 `dangling`。
3. 會碰到的情境:
   - 多平台專案沒初始化子模組。
   - CI 用 sparse checkout,或某個 job 只簽出一個平台。
   - 測試檔搬了目錄。
   這幾種情形下,那個平台所有新加的名稱都被擋。S10 只涵蓋「丟例外」這一種。
4. 改法:任何一個平台的 root 不存在,或方法集合是空的,就把那個平台的名稱當成「判不了」,只提醒並講原因,不判 dangling。S10 加這個夾具。

## F7 抽取吃不到的拼法照樣滿足格子規則的 PITFALL 那一格,新加的錯名永遠不會被查
severity: major
blocking: 是
引句:「`_note_test_refs(line)` 對一行(先經 `_strip_inline_markup`)抽出 `[test:…]` 與 `[test-gone:…]`」
file: `scripts/lumos:3757`
file: `scripts/lumos:4736`
1. 格子規則的 `slot_parse` 認得的寫法比較寬:鍵名不分大小寫、收全形冒號、`[` 後面可以有空白、值可以用反引號包起來。判測試存在用的 `TEST_REF_RE` 只認半形 `[test:`,而且抽取前會先經 `_strip_inline_markup` 把反引號段剝掉。
2. 實驗 exp1 和 exp5:`PITFALL:坑 [出處:x] [根因:y]` 後面接 `[Test：t_typo]`、`[ test:t_typo]` 或 `[test:` 加反引號包住的 `t_typo` 加 `]`,三種寫法 `slot_check("PITFALL", …)` 都回 `[]`,也就是格子算有 test 這一格;但去反引號之後 `TEST_REF_RE` 抽到 `[]`,`_classify_test_refs` 也回 `[]`。
3. 結果:新寫的 PITFALL 用這幾種寫法掛一個打錯的名稱,格子規則和本案都會放行,讀的人會以為有守衛。這正是計劃白話第一段要堵的事。本案把 PITFALL 改成四選一之後,這個洞也一起延續到 `test-gone`。
4. 改法擇一,並把選擇寫進〈做法〉1:
   - 抽取改用 `slot_parse` 的欄位辨識(鍵名正規化後是 test/test-gone 就收,值照樣去反引號)。
   - 或者讓格子規則只在 `TEST_REF_RE` 認得的寫法下才算滿足 test 那一格。
   S7 要另加一條:反引號包住的名稱在格子規則上也不能算有 test。

## F8 1c 給的改法「改成 `[test-gone:]`」對活測試是一句假話,而 `[test-gone:]` 不驗名稱已經不存在,寫了就過
severity: major
blocking: 是
引句:「(1c)新寫的作廢行掛著活測試 → 違規:改成 `[test-gone:]`,或把綁定移到接手的那一行」
file: `scripts/lumos:27114`
1. 1c 擋的前提是那支測試指得到,也就是還在。可是 `[test-gone:名稱@提交]` 的定義是「這支測試在那個提交被刪」,對一支還在的測試這句話不成立。
2. 〈名詞〉又寫了不驗名稱存在,只驗寫法和提交;而 `_pin_commit` 只確認那個提交在某條分支的歷史上。
3. 實驗 exp3:隨手拿 HEAD 的前 12 碼丟給 `_pin_commit`,回傳完整編號,也就是會過。所以照擋下訊息把作廢行改寫成 `[status:superseded] [test-gone:t_live@<HEAD前12碼>]` 就放行。doctor 那段「寫法不對的 `[test-gone:]`」也不會列出它,筆記從此多了一句沒人會發現的假話。
4. 改法:
   - `[test-gone:]` 的名稱如果判成 real,就算違規(新寫行擋,doctor 也列出)。
   - 1c 的改法只給兩條:把綁定移到接手的那一行;或者真的把測試刪掉,同時拿掉綁定。
   - S8 的建議字樣跟著改。

## F9 同一次推送裡刪掉的測試寫不出真的提交編號,照專案「推之前壓成一個提交」的做法會被 S6 擋
severity: major
blocking: 是
引句:「新寫行裡的 `[test-gone:]` 寫法不對(沒有 `@`、提交不到 12 碼、不在任何分支歷史上)→ 違規」
file: `scripts/lumos:27114`
1. 專案規矩是一個功能一個提交、筆記和程式同一個提交、做到一半的本機提交推之前壓成一個。所以刪測試的那個提交,就是寫 `[test-gone:]` 的那個提交,寫的當下拿不到它自己的編號。
2. 照字面只有兩種做法,兩種都不行:
   - 先提交刪測試(提交前掛鉤會擋「改 code 沒動圖譜」)。
   - 或者先寫中間提交的編號再壓。實驗 exp3:feat 上先提交「刪測試」得到 A,再提交筆記 `[test-gone:t_x@A前12碼]`,然後執行 `git reset --soft main` 再提交一次。`_pin_commit(A)` 回 `None`,A 已經不在任何分支上,推送時那一行是新寫的,S6 擋下。
3. 結果是 `[test-gone:]` 只寫得出「早就在主線上的刪除」,也就是 rtb 那種事後清理。只要是這次推送才刪的測試,就只能改用單次跳過,或寫一個不實的編號(見 F8,任何分支上的提交都會過)。
4. 改法擇一:
   - 允許一個「同次」寫法(例如 `@本次`),推送時驗「終點的樹裡已經沒有這支測試、起點有」。
   - 或者明寫這種情形的正確改法是直接拿掉綁定(PITFALL 改寫成 `[防回歸:無 理由]`),不要指向 test-gone。

## F10 「行首 `[SN]`」照字面不含清單符號,本計劃自己的條款行 `- [S1] …` 不會被略過
severity: minor
blocking: 否
引句:「合約行(摘要裡、`INVARIANT_RE`)與計劃裡的條款定義行(行首 `[SN]`)略過」
file: `scripts/lumos:6161`
1. 這份快照自己的條款都是 `- [S1] …` 開頭。條款綁定認定義行用的是 `_CLAUSE_LEAD_RE`(先去掉 `- * # > 1.` 等前綴),而且只認「這個編號第一次出現在行首」的那一行。
2. 計劃沒點名用哪一支。照字面用 `startswith("[S")` 實作的話,每一篇新計劃在條款上綁還沒寫的測試(spec-gate 要求先綁),提交時都會被當成新加的 dangling 擋下,連這篇自己也一樣。
3. 改法:〈名詞〉和〈做法〉1 寫明用 `_CLAUSE_LEAD_RE`,跟 `clause_bindings` 同一個判法。

## F11 1c 以實體行為單位:作廢標記和 `[test:]` 分在摘要的續行時看不到;只改一個錯字也會擋舊的綁定
severity: minor
blocking: 否
引句:「帶 `[status:superseded]` 的行(`_ns_superseded`;筆記格子規定這種行另必帶 `[被取代:]`)」
file: `scripts/lumos:28189`
1. 實驗 exp4:摘要第 4 行是 `PITFALL:舊坑 … [test:t_live]`,第 5 行是縮排的續行 `續寫 [status:superseded] [被取代:[[Systems/B]]]`。逐實體行看,第 4 行判成沒作廢,第 5 行沒有 test,1c 就漏掉了;接回成邏輯行才會判成 (True, ['t_live'])。格子規則已經用 `_ns_summary_logical` 處理這種情形。
2. 本 repo 現在摘要續行是 0 行,所以只標 minor。
3. 另外,名稱那條規則已經從「新寫的行」改成「新加的名稱」,但 1c 還是用「新寫的作廢行」。對一條舊的作廢行只修一個錯字也會擋,跟 S2 的精神不一致。計劃要明寫這是刻意的,還是改成「這次才變成作廢,或這次才多掛上活測試」。

## F12 佔位字用字面比,帶平台前綴(`[test:py:待補]`)時不相等,改法訊息會給錯
severity: minor
blocking: 否
引句:「測試名整個是 `待補`、`待定`、`TODO`、`TBD`(不分大小寫)其中之一」
file: `scripts/lumos:5169`
1. 測試名是 `invariant_test_refs` 抽出的原始字串,帶著前綴(exp1:`resolve_test_refs("[test:py:待補]")` 拆出來才是 `('py','待補')`)。所以「整個是待補」對 `py:待補` 不成立。
2. 這種寫法照樣會判成 fake 或 dangling 被擋,但吃不到 S3/S4 照前綴給的改法,而且帳上不會算成佔位字。
3. 改法:用拆掉前綴之後的名稱來比。

## F13 單次跳過記帳照 `_ns_skip_slot_extra` 只在提交時、而且掛鉤帶 `--slots` 才算;計劃自己指定的推送誤擋逃生口,帳上會少 `test_refs`
severity: minor
blocking: 否
引句:「單次跳過時也先算一次記進去(照格子的 `_ns_skip_slot_extra`)」
file: `scripts/lumos:28572`
1. 前例的條件是 `if (staged and slots_flag)`,函式裡面也寫死了讀暫存區和 HEAD。
2. 〈實務隱患〉說推送時誤擋要用單次跳過。照前例實作的話,推送時跳過的那一筆不會帶 `test_refs`,REVISIT 要看的「單次跳過時記下的 `test_refs` 條數」會少掉最該看的那一類。
3. 另外,格子的 extra 帶 `check` 鍵,兩組同時出現時欄位要怎麼合併,計劃沒寫。
4. 改法:跳過時兩種模式都算(推送時用同一個範圍),條件不要綁 `--slots`;並寫明 extra 合併的形狀。

## 逐節核對
- 開頭欄位、白話、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀。交叉引用的節點(漂移防治路線圖、筆記格子、筆記內容閘、check-t-sentinel、bound-tests-gate)都存在。「三選一」寫死的地方在 `scripts/templates/graph-discipline.md:43`、`scripts/lumos:3898`、`scripts/test_lumos.py:30301`,跟〈做法〉8 列的三處一致。沒有其他 finding。
- 名詞:F3(多重集合)、F8(test-gone 不驗名稱)、F10(行首)、F12(佔位字)。
- 範圍:已讀,無 finding。散文撤除只提醒,這點已經講明白。
- 做法 1–9:F1、F2、F3、F4、F5、F6、F7、F8、F9、F11、F13。開關的優先順序(〈做法〉5)跟 `_ns_slots_mode` 的語意一致:gate=off 時 `cmd_note_shape` 在一開頭就回傳;gate=warn 時子規則降成提醒。這一節本身無 finding。
- 條款 S1–S15:已讀,缺的夾具已經寫在各 finding 的改法裡。
- 回退:已讀,無 finding。
- 實務隱患(風險類逐類):
  - 誤擋:F2、F5、F6、F9。
  - 漏擋:F1、F3、F7、F8、F11。
  - 一致性(兩邊讀的版本不同):F4、F5。
  - 時間:只在有要查的名稱時才建索引,方向對,無 finding。
  - 相容:升級前寫的提交在推送時會照查,計劃已經承認,無 finding。
  - 金流、對外送出、不可逆:無,理由同計劃(只讀本機檔案,revert 就回得去)。
  - 帳本:F13。

最高等級:major,blocking 共 9 條
