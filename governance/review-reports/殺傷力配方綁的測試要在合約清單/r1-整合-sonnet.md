severity: major

整合與知識同步鏡頭。對照程式碼:/Users/enzo/harness/lumos-d3(唯讀,未改檔、未跑測試套)。派工時沒有附上計劃牽連的合約或事故節點,所以只能自己查 Systems/guard-kill 的合約行,結果在最後一節。

## F1 新閘名 check-p2t 要登記的地方有兩處,spec 一處都沒寫
severity: major
blocking: 是——不補這兩處,新增的提醒不是記不進治理帳,就是悄悄寫進版控帳,spec 的 S2 條款又沒有任何一句會讓這件事變紅。
spec 段落:「範圍」第二條「gov_events 記 `check-p2t`」。
引句:「gov_events 記 `check-p2t`;自己一個例外保護。不跑 git。」
問題:閘名要登記在兩個名單,兩邊的失敗方式不同。
- `_KNOWN_GATES`(`scripts/lumos:7993`)。寫入器 `scripts/lumos:1486` 看到不在名單上的閘名就不寫,只在 stderr 印一句「不在 _KNOWN_GATES 名單上」。結果是每次 `doctor --ci` 都多印一句警告,而且記不進帳。另有漂移釘 t_gov_stats_gate_drift(`scripts/test_lumos.py:6538`)掃全檔 `"gate": "字面值"`,忘了登記它會紅,這一處有機械守衛。
- `_GOV_LOCAL_PAIRS`(`scripts/lumos:1320-1329`)。doctor 各段的 warned 事件走白名單分流到本機帳,名單上現有 `check-p2`、`check-p2s`。新閘名不加進去,事件就照舊寫進版控帳 `.governance-log.jsonl`,每次 `doctor --ci` 讓版控檔多幾行。這正是「治理帳例行紀錄分流」要避免的事。守衛測試 t_gov_split_pairs_drift(`scripts/test_lumos.py:6741`)只檢查「名單上的每一對有寫入點」,沒檢查「寫入點的閘名在名單上」,所以漏加這一處沒有任何測試會紅。
具體例:實作者照 spec 寫 `gov_events.append({"gate": "check-p2t", "kind": "warned", "hard": False, ...})` 並把 check-p2t 加進 `_KNOWN_GATES`、不碰 `_GOV_LOCAL_PAIRS` → 全部測試綠,可是 rtb 每次 `doctor --ci` 後版控帳都多一筆。
`gov --stats` 的消費面:`scripts/lumos:8081` 把「在 `_KNOWN_GATES` 但帳裡沒出現」的閘列進「未出現」清單,這是正常行為,不會因為多一個閘名而認不得。週報沒有另外硬編閘名(我在 scripts/、governance/*.py、mods/ 搜 check-p2 只命中 `scripts/lumos` 與測試)。
要補進 spec:兩個名單都要改;S2 加一條讀本機帳驗 `check-p2t/warned` 的斷言,寫法照 `scripts/test_lumos.py:66747-66750` 對 check-p2s 的做法(含 `_KNOWN_GATES.count == 1`);另加一支測試釘「`_GOV_LOCAL_PAIRS` 包含 doctor 寫的每個 check-* warned」,不然漏加沒人知道。

## F2 「沒帶 --test 一定取自清單,不會觸發」與程式不符
severity: major
blocking: 是——spec 自己的範圍句和比對規則互相矛盾,且會對「測試明明在清單上」的情形印出「不在清單」的錯話。
spec 段落:「範圍」第一條。
引句:「沒帶 `--test` 時配方的測試一定取自清單,不會觸發。」
問題與具體例:有兩條路會讓這句話不成立。
1. 多平台、清單寫 `[test:ios:Foo]`、kill-add 不帶 `--test` 也不帶 `--platform`。`_guard_kill_add_locked`(`scripts/lumos:15259` 起)取 `refs[0]` 原樣當配方 test,即 `"ios:Foo"`,配方沒有 platform 欄。guard kill 實際跑 `_kill_method_name("ios:Foo", True)` 得 `Foo`,平台取預設平台(`scripts/lumos:14650`、`15814` 起的分組 `r.get("platform") or platform_override or default_plat`)。spec 要求「照 guard kill 實際的跑法」比,所以配方算 (預設平台, Foo),清單解析出 (ios, Foo),兩邊不等 → kill-add 提醒「不在清單」。可是這支測試明明就是從清單來的。這個提醒其實揭露了一個真實問題(殺傷力在預設平台跑、合約綁的是 ios),但 spec 規定的訊息是「推送前跑的是清單上那幾支」,對使用者是錯話,doctor 那一則同理。
2. 「只更新 covers」路徑。spec 把它算進範圍(`recipe = r` 沿用既有配方),此時 `test_arg` 是 None,配方的 test 是很久以前寫的、可能早就不在清單上。每次補 covers 都會再印一次,而這時並沒有帶 `--test`。
預期 vs 實際:spec 說這兩種情形不觸發,規則推出來會觸發。
要補進 spec:決定「平台前綴 + 無 platform 欄」這種存法要不要提醒、提醒什麼話(建議另開一句講「配方會在預設平台跑」),並把第一條裡那句改成只講「帶 --test 時」,covers-only 路徑要不要印、印幾次寫明白。S1 的測試要補這兩格。

## F3 提醒裡的 `lumos guard bind` 建議,對兩類測試跑不起來,對一類會弄壞後續 kill-add
severity: major
blocking: 是——提醒給的是照做會失敗或造成新卡關的指令,而 spec 的 S1/S2 只驗「提醒裡有 lumos guard bind」這幾個字。
spec 段落:「範圍」第一、二條(提醒文字)、「驗收條款」S1。
引句:「清單有東西時講「推送前跑的是清單上那幾支,要讓這支也被推送閘守就 `lumos guard bind`」」
問題與具體例(程式驗證):
1. `cmd_guard_bind`(`scripts/lumos:14552`)開頭用 `IDENT_RE` 擋掉不是純識別字的方法名;guard kill 的白名單 `_KILL_METHOD_OK_RE`(`scripts/lumos:14617` 之後)卻允許含空格與點的名字(Kotlin 反引號拆殼後)。配方 test 是 `` `foo bar` `` 或 `a.b` 時,提醒叫人 bind,bind 回「不是合法的方法名」rc2。
2. 配方 test 帶平台前綴(`ios:Foo`、無 platform 欄)時,bind 要的是 `Foo --platform ios`,不是整串。spec 只說「附指令形狀」,沒說平台怎麼拆。
3. bind 是附加不是取代(`scripts/lumos` 的 `refs.append(ref)`)。清單有 1 支時再 bind 一支變 2 支,之後 `kill-add` 不帶 `--test` 會被 `_guard_kill_add_locked` 擋下(「這條合約綁了好幾條測試…用 --test 指明」,`scripts/lumos:15259` 之後 `len(refs) > 1` 那段)。也就是照提醒做會讓這條合約以後的 kill-add 每次都要帶 `--test`。提醒應該講這個代價,或改建議「不綁,改把配方的 test 換成清單上那支」。
4. bind 比對合約行用 `TEST_REF_RE.sub`,kill-add 定位合約行用 `INV_TAG_RE.sub`(去 test/audit/kill/src/git 標記);提醒裡的「<KEY子字串>」若取自配方的 invariant 欄(kill-add 存的是使用者給的片段),通常兩邊都找得到,但 spec 沒說提醒印的片段從哪來,doctor 那一則印的是「合約前 30 字」,不是可貼的片段,貼過去 bind 可能對到多行被擋。
要補進 spec:提醒的指令範本從哪取欄位、test 名不合 IDENT 時改講什麼、平台前綴怎麼拆;S1/S2 至少各一格斷言指令真的跑得過 bind(rc0)。

## F4 doctor 第三則在設定檔讀不了、第一則例外、平台不在設定三種情形的行為沒定義
severity: major
blocking: 是——既有測試 t_doctor_kill_recipe_drift 專門走這三條路,實作者無從得知該印什麼,也無法判斷既有斷言會不會被新行打破。
spec 段落:「範圍」第二條、「實務隱患」第二點、PRIOR-ART 第一句。
引句:「用既有 `resolve_test_refs(合約行, 平台表, 預設平台)` 解析成 (平台, 方法) 對」
問題:`resolve_test_refs` 需要平台表與預設平台,這兩個來自 `load_platforms`/`_kill_cfg_load`。
- 設定檔讀不了(壞 JSON、`load_platforms` 丟例外):P2 第一則走 `cfg_err` 分支(`scripts/lumos:3365-3373`)。第三則拿不到平台表,不能比。spec 沒說跳過、沒說印什麼。既有測試 ⑩/⑩b/⑩c/⑩d(`scripts/test_lumos.py:67201-67215` 附近)對這種情形各有斷言,例如「這一段算不出來」不得出現。
- `_p2` 在第一個 try 裡丟例外時是 None(第二則 `_kill_p2_survived` 已經處理 `p2=None`,`scripts/lumos:15085` 附近);第三則若依賴 `_p2["ctx"]` 取設定就會跟著壞,若自己重讀設定就多一次讀取。spec 說「自己一個例外保護」,沒說依賴什麼。
- 平台不在設定裡(測試 ① 的 `platform="zz"` 配方):配方是 (zz, TestLimitFive),清單是 (預設, TestLimitFive),必然「不在清單」,被列進第三則;第一則已因為「平台 zz 不在設定裡,沒驗」列過它。同一條配方被兩則各列一次,而且第三則的理由(測試不在清單)是假的,真因是平台寫錯。同理 `{"invariant": "上限恆為5", "file": 5, "old": "x"}` 這種缺 test 欄的配方,test 當空字串,也會被列成「不在清單」。
- 合約行沒有 `[test:]`(測試 ⑩ 用的 `inv_lines`):清單空,所有配方都對不上,第三則整篇列出,與第一則「設定檔讀不了」疊在一起。
- 既有斷言風險:測試 ②(`scripts/test_lumos.py:67151` 附近)用 `--id <短身分>` 在 P2 段找出恰好一行;第三則若也帶 `--id` 就會讓 `len(line) == 1` 翻紅;另一格斷言 `"::" not in s`,第三則若把 (平台, 方法) 印成「平台::方法」就紅。spec 的列出格式(節點、合約前 30 字、配方的測試、bind 指令形狀)沒帶 `--id`,所以不用擔心前者,但沒有固定後者的格式。
要補進 spec:cfg_err 時第三則的行為(建議整則跳過、不記帳);平台不在設定或缺 test 欄的配方歸入「對不回/沒比對」而不是「不在清單」;第三則是否自行讀設定。

## F5 「另有 N 條」那行:印不印、放哪、算不算上限,三處不清,且「沒有任何檢查管」不實
severity: minor
blocking: 否——是輸出形狀的缺口,實作者選哪種都能過 S2,但會與既有 3 條上限互相踩。
spec 段落:「範圍」第三條。
引句:「在同一則提醒的開頭另印一行筆數(「另有 N 條配方對不回合約行,沒比對」),不逐條列」
問題:`warn_soft`(`scripts/lumos:1669-1681`)的格式是「標題行 + 最多 3 條 • 行 + 『另 K 條』行 + 建議」。(a) 筆數放進 head 就影響標題;放進 lines 第一格就吃掉 3 條上限的一格(`_SOFT_CAP = 3`),真正的問題項只剩 2 條可見。(b) 沒有任何一條配方「不在清單」、只有 N 條對不回時,整則要不要印?S2 寫「只算進另有 N 條那一行」,但沒說在零筆不在清單時這一行會不會單獨出現;若不出現,「至少讓人看得到」就落空;若出現,既有測試 ① 的 Mix 篇(含 2 條格式壞配方)會讓 P2 段多一則,影響 ⑪ 的 `plines` 計數(該測試目前只靠平台根找不到那一條)。(c) 「目前沒有任何檢查管這種情況」不完全對:`_kill_rm_rewrite`(`scripts/lumos:15562-15580`)已有一份「去標記後含 invariant 片段」的比對來決定要不要拿掉 `[kill:recipes]`,kill-add 定位合約行也有一份(`scripts/lumos:15259` 起),spec 的第三份比對應該抽共用函式,不要再抄一次(跟 Systems/guard-kill 已記的「同一個判斷只寫一次」同一精神)。
要補進 spec:筆數行放在 lines 還是 head、零筆不在清單時印不印、比對抽成共用函式並讓 kill-rm 與 kill-add 改用。

## F6 kill-add 的鎖外提醒:合約行從哪來、與既有「恰好一行」文字的關係
severity: minor
blocking: 否——是實作細節缺口與文件要改的句子,不是行為矛盾;沒有既有測試會因此紅。
spec 段落:PRIOR-ART 末句與「範圍」第一條。
引句:「kill-add 的提醒接在既有的鎖外提醒 `_kill_add_after_lock`/`_kill_add_warn` 旁。」
問題:
1. 合約行文字在鎖內的 `_guard_kill_add_locked` 才有(`line`、`refs`),`warn_box` 只放配方(`warn_box.append(recipe)`)。spec 沒說怎麼傳出來;若在鎖外重讀筆記,會多一次讀檔、且與別的會談的 `lumos set` 有時間差(讀到的清單可能已不同),重讀失敗也沒說怎麼辦。最簡單的做法是把 `refs` 與設定一併放進 warn_box,spec 要寫明。
2. 平台表與預設平台要另讀設定(`_kill_cfg_load`)。`_kill_add_warn` 已經建 `_kill_check_ctx` 一次;第二個提醒應共用同一個 ctx,不然每條配方讀兩次設定。
3. 既有文字:`_kill_add_warn` 的 docstring(「印恰好一行提醒」)、`Systems/guard-kill.md:103`(「多印恰好一行」)、測試 t_guard_kill_add_warns_drifted_recipe 的說明與斷言(`scripts/test_lumos.py:66973`,數的是失配那一行 `base_err + 1`)。新增後,一條失配又不在清單的配方會印兩行。既有測試都不帶 `--test`(我 grep 了 `kill-add` 相關呼叫,沒有一處帶 `--test`),所以不會翻紅,但句子要改成「各至多一行」,並說兩行的先後。
4. 順序:`_kill_add_after_lock` 裡 `for rec in warn_box: _kill_add_warn(...)` 之後才接 `--try` 的試跑輸出(`scripts/lumos:15217` 起)。新提醒印在試跑前還是後沒定義,試跑輸出很長時,放後面會被蓋掉。
要補進 spec:warn_box 多帶欄位、共用 ctx、與失配提醒的先後、`--try` 之前印。

## F7 RETIRE-IF 的兩個條件都量不到
severity: minor
blocking: 否——是撤除條件的可執行性問題,不影響功能。
spec 段落:RETIRE-IF 行。
引句:「連續 60 天 doctor 這一則提醒在本工具鏈與 rtb 都是 0 筆、而且 kill-add 沒印過這個提醒」
問題:(a) kill-add 的提醒不寫治理帳(`_kill_add_warn` 只 `print` 到 stderr),沒有任何地方記得「印過沒」,第二個條件無法機械判定。(b) 第一個條件若要寫成機器式 `[retire:度量 check-p2t.warned == 0 近N週]`,閘名必須先在 `_KNOWN_GATES`(`scripts/lumos:4263` 的檢查)且走本機帳時看本機帳的暖機起點(`scripts/lumos:4056`),所以又回到 F1。(c) 「在 rtb 也是 0 筆」要讀別的 repo 的帳,工具鏈本身讀不到。
要補進 spec:把 RETIRE-IF 拆成可量的一半(doctor 的 check-p2t 筆數,度量式)與人裁的一半(kill-add 提醒),後者要嘛讓 kill-add 也記一筆(但要走 F1 同樣的登記),要嘛明寫「人裁」。

## F8 落地要改的句子與檔案沒列全
severity: minor
blocking: 否——是知識同步清單的缺漏,沒有機械守衛會抓,所以列出來。
spec 段落:front matter `lands_in`。
引句:「Systems/guard-kill」
問題:`lands_in` 只列一篇。三個月後的人要同步的位置(我逐一查過):
- `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`:第 35 行「三處補上」的敘述、第 103 行 kill-add 段「多印恰好一行」、第 107 行 doctor P2 段的第一則描述與「每條、每篇、整段各自包例外保護」、第 109 行「同一段第二個提醒」之後要接第三個、第 117 行的函式清單(新增的函式與 `_kill_note_skipped` 的引用)、frontmatter 的 WHY 行要加一行(照既有格式寫 `[出處:]` `[因:]`)並把新測試名寫進 `[test:]`。
- `skills/lumos-project-notes/reference.md:63`:健康巡檢那一列講「P2 殺傷力配方的原文還對不對得上程式」,要補第三則。
- `skills/lumos-project-notes/commands/04-自檢與健康.md:23`:講 P2 列哪兩類,要補第三類。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md:25-26`:每個 P2 提醒各有一列「看到這行怎麼辦」,第三則需要自己的一列(指令、看哪裡、為什麼)。
- `scripts/lumos` 的 `_KNOWN_GATES` 與 `_GOV_LOCAL_PAIRS` 註解(F1)。
- 守衛面:`guard audit` 只寫 `[audit:]` 留痕(`scripts/lumos:16153`),`guard trace` 只列「合約 → 測試 → Verification」(`scripts/lumos:16211`),兩者都不比對配方,不需同步,也不會被本案破壞。
要補進 spec:把以上寫成「落地清單」一節,勿只靠 `lands_in` 一個節點。

## 已排除與已讀無 finding
- 既有測試會不會翻紅:我檢查了 `_mk_kill_env`/`_kr_note`/`_kr_recipe`(預設合約 `[test:TestLimitFive]`、預設配方 `test="TestLimitFive"`,兩邊一致),跑 kill-add 的測試沒有一支帶 `--test`,所以 S1 範圍的新提醒不會讓它們翻紅。P2 的風險集中在 F4、F5 列的幾格;我沒有實際跑測試套(唯讀、也不在這個工作目錄跑),所以這是靜態判斷,不是跑出來的結果。
- doctor 軟提醒上限:`_SOFT_CAP = 3`(`scripts/lumos:1665`),`--verbose` 全列。新增第三則本身不受影響;受影響的只有「另有 N 條」那一行(F5)。`doctor-run` 事件的 note 會記 `soft=N`(`scripts/lumos:3661`),段數多一則會讓這個數字變大,沒有測試釘它的具體值。
- 合約行對 guard kill 的 INVARIANT:Systems/guard-kill 兩條 ★INVARIANT★(rc 優先序;`--json` 成功時 stdout 恰一行 JSON,`guard-kill.md:21-22`)。本案只在 kill-add 的 stderr 與 doctor 多印,不碰 `cmd_guard_kill`,不影響這兩條:前者只看判定結果、後者只管 `--json` 的 stdout。
- 「實務隱患」四項「已排除」:金流、對外送出、不可逆、守衛面——查過,新增只是提醒、不寫新檔(F1 的本機帳除外,那是例行紀錄)、不改任何閘的判定,成立。
- 「回退」與「天花板」兩節:已讀,無 finding。

總結:最嚴重 major,blocking 4 條(F1、F2、F3、F4),minor 4 條(F5、F6、F7、F8)。
