severity: major

審查席:邊界-sonnet(設計審第 2 輪,邊界與輸入鏡頭)。實驗都在 `--shared` 複本與自建玩具 repo 跑,沒動被審 repo。實驗腳本在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/tb4-r2-work-邊界-sonnet/`(exp1 到 exp8)。

## F1 第②道拿整個名稱去 grep,「類別.方法」寫法第①道判過、第②道必判找不到,合法綁定全被擋
severity: major
blocking: 是
引句:「第②道問被檢查的版本裡那個平台的測試檔整字找不找得到」
file: `scripts/lumos:40263`(`_classify_test_refs`:`real = method in mset or ("." in method and method.rsplit(".", 1)[-1] in mset)`,只拿最後一段比)
file: `scripts/lumos:41252`(`_dispositions_check_test` 現在靠 `name not in methods_for(plat)` 先把 `Class.Method` 擋掉,所以 41270 那行 `git grep -w -F -e name` 從沒收過帶點的名字;抽出 `_test_in_tree` 只抽 grep 那段,這道前置就沒了)
1. 輸入:C# 玩具 repo,`Tests/FooTests.cs` 有 `[Fact] public void Bar()`,已提交;筆記摘要行 `PITFALL: x [test:FooTests.Bar]`,這次推送碰到那篇。
2. 第①道:`_classify_test_refs("[test:FooTests.Bar]", …)` 實跑回 `('n','csharp-xunit','FooTests.Bar','real')`(exp1)。
3. 第②道:把整個名稱拿去 `git grep -w -F -q -e FooTests.Bar HEAD -- ':(glob)**/*.cs'` 實跑,`rc=1`(找不到);同一個 repo 拿 `Bar` 去搜 `rc=0`。檔裡從來沒有字面的 `FooTests.Bar`。
4. 照字面:第①道過、第②道找不到 → 「指不到」→ 擋。所有 `類別.方法` 寫法(C#、Java、Kotlin、`TestX.test_y`)的真測試一律被擋,而計劃明寫「類別.方法都已處理」。本 repo 的筆記裡就有 `[test:TestRetry.test_cap]`、`[test:Pay.t_refund]` 這種寫法(`grep -rhoE` 查得到 5 處,多半是範例)。
5. 實驗:exp1.py 的輸出 `test:FooTests.Bar (False, "測試 'FooTests.Bar' 在平台 … 工作樹掃不到…")` 是現行表態閘的前置在擋;去掉前置後 grep 部分就是上面 rc=1。計劃沒寫第②道該搜哪一段(整名或最後一段),也沒有條款鎖「類別.方法」。

## F2 `_test_in_tree` 的「判不了」沒有判定法;照現有 grep 段字面抽出,子模組與逾時都回「找不到」,而 S24 又要求行為不變
severity: major
blocking: 是
引句:「它回三種:找得到、找不到、判不了(git 出錯或逾時、平台根在 repo 外、平台根是子模組)」
引句:「當表態閘改用抽出的 `_test_in_tree` 後,表態證據的判定應跟原本一樣」
file: `scripts/lumos:41270`(`git grep … at_sha -- :(glob)<rel>/**/*<ext>`,rc 1 直接回 `False, "整字 grep 不到"`)
file: `scripts/lumos:41262`(`root.relative_to(rr)` 只擋根在 repo 外;子模組沒有任何偵測)
1. 輸入:主 repo 把平台根 `sub` 當子模組(git submodule add),測試在 `sub/tests/test_a.py`,子模組已推。
2. 實驗(exp 內 sm/ 目錄):`git grep -w -F -q -e test_a HEAD -- ':(glob)sub/**/*.py'` 回 `submodule-rc=1`;改成 `-- 'sub'` 也是 `rc2=1`。也就是 git 把子模組當成 gitlink 不下鑽,回的是「找不到」不是錯誤。
3. 照字面抽出後,子模組的測試在第②道變成「找不到」→「指不到」→ 擋,跟 S14「平台根是子模組 → 判不了、不擋」正面衝突。計劃沒說怎麼偵測子模組(要 `git ls-tree` 看路徑或祖先是不是 160000,且平台根可能在子模組更深處),也沒說「根在樹裡根本不存在」(`:(glob)nodir/**` 回 rc 1)算找不到還是判不了。
4. 另一個方向:S24 要表態閘「行為不變」。表態閘現在 rc≠0 回 False 並用 rc 當訊息;三態化後,「判不了」在表態閘該回 True 還是 False 沒定義——任一種都改了表態閘行為(回 True 會讓逾時放行表態證據)。
5. repo 外的根實測:`git grep … -- ../zzz` 回 `rc=128`、`fatal: outside repository`;`TimeoutExpired` 是例外不是 rc,現有段沒接。這兩種計劃要歸「判不了」,抽出時要自己加 try;計劃只在 S14 的測試名裡列,沒寫成實作義務。

## F3 「碰到」把開頭欄位其他欄(`updated:`、`status:`、tags)的新行也算進來,翻個狀態或改個日期就整篇要乾淨
severity: major
blocking: 是
引句:「新寫的行照筆記內容閘既有定義(提交時是這次暫存新增的行;推送時是範圍裡逐提交新增、終點還在的行」
引句:「它把向 `_notelines_new` 要到的 rows 放進去」
file: `scripts/lumos:28408`(`_note_shape_eval` 呼叫 `_notelines_new(..., keep_other=True, ...)`,是無條件的)
file: `scripts/lumos:27418`(`_notelines_rows`:`keep_other` 時 `other` 區塊的新行照收)
1. 計劃的碰到定義拿 `_notelines_new` 的 rows。那支在本 repo 的唯一呼叫是 `keep_other=True`(為存量漂移防線而開),所以 `other` 區塊(開頭欄位除 summary、decisions 以外的行:`status:`、`updated:`、`tags:`、`about_code:`)的新增行都在 rows 裡。既有各規則靠 `if reg != "other"` 自己濾掉,新規則若只取路徑集合就沒人濾。
2. 實驗(exp8.py):玩具 repo 一個提交只把 `status: doing` 改 `done`、`updated:` 改日期,`_notelines_new(...keep_other=True)` 回 `[('docs/kg-knowledge/Systems/A.md', [(3,'status: done','other'), (5,'updated: 2026-10-02','other')])]`;staged 模式同樣(只改 `updated:` 就有一列 `other`)。
3. 後果:`lumos set <節點> status done`、更新 `updated:`、補 `about_code` 這種每天都有的動作,會讓那篇整篇進「要乾淨」。例:rtb 一篇有 57 個指不到名字的計劃只是翻 `status: done` 收尾,推送被擋、被迫整篇改。計劃〈名詞〉說「有新寫的行」且自述開頭欄位「只看 summary」,但碰到判定沒濾區塊;RETIRE-IF 第二條(被迫修舊帳放棄推)正是這個。
4. 計劃沒寫「碰到只算 body/summary/decisions 的新行」,也沒有條款鎖「只動 `updated:` 的筆記不算碰到」。

## F4 rows_out 回來的筆記清單包含「新行為零」的筆記(純改名、新增行後來被刪),照「從 rows 取出筆記路徑集合」會把沒寫任何一行的筆記算碰到
severity: major
blocking: 是
引句:「只是被主線合進來、自己沒寫任何一行的筆記不算碰到。」
引句:「這組從 rows 取出筆記路徑集合」
file: `scripts/lumos:27380`(`notes.append((p, text, _notelines_rows(...)))`,rows 可能是空串列也照 append)
1. rows 本身(`(行號, 行文字, 區塊)`)不帶路徑,路徑只能從 `notes` 的 `(p, text, rows)` 取;計劃沒說要不要濾掉 `rows == []` 的那幾篇。
2. 實驗(exp2.py、exp7.py):①同一範圍先提交新增一行再提交刪掉那行 → 回 `('…/A.md', [])`;②只做 `git mv A.md A2.md` 的提交 → 回 `('…/A2.md', [])`。兩種都在 `notes` 裡、rows 為空。(對照:新增後改名會跟到新路徑並保留那一行;新增後刪檔不出現。)
3. 照〈做法〉1 取 notes 的路徑,這兩種筆記都被當「碰到」;純改名一個節點(`lumos` 的改名、搬資料夾)會讓被搬的每一篇整篇要乾淨,違反〈名詞〉「自己沒寫任何一行的不算碰到」。S3 只鎖主線合併那一種,沒鎖這兩種。

## F5 計劃要求「HTML 註解裡的不算」,但它引用的兩個共用零件都明寫「不偵測 HTML 註解」(偵測本身曾被證明是洞),註解的處理沒有現成零件也沒有條款
severity: major
blocking: 是
引句:「程式碼圍欄裡的不算(`_visible_lines`)、HTML 註解裡的不算」
file: `scripts/lumos:4182`(`_visible_lines`:「★不偵測 HTML 註解★(-b r3 單reviewer 兩條 blocker:`-->  <!--` 先關再開會把後面整份藏掉)」)
file: `scripts/lumos:372`(`_strip_inline_markup`:「★不碰 HTML 註解★…偵測註解本身就是洞(先關再開、註解正則不認反引號邊界)」)
file: `scripts/lumos:6616`(`clause_bindings` 同樣寫「HTML 註解不特別處理」)
1. 實驗(exp5.py):`_visible_lines` 對 `['<!--','舊寫法 [test:t_old_gone]','-->','行內 <!-- [test:t_inline] --> 後面',…]` 回傳的可見行包含第 3 行與第 5 行;`_strip_inline_markup("行內 <!-- [test:t_inline] --> 後面 …")` 原樣回傳、旗標 False。
2. 兩種實作走向都出錯:①只用 PRIOR-ART 列的零件 → 註解裡的 `[test:舊名]` 照算,被當指不到擋下(跟〈名詞〉相反);②另寫註解剝除 → 重走前兩輪證明有洞的路:`-->  <!--` 先關再開把後面的 `[test:]` 整段藏掉(漏網),或本 repo 筆記在反引號裡寫的 `<!-- LUMOS-SLIM:START/END -->` 這類範例把註解當成開著、吃掉同一行後面的綁定(`Systems/slim-install-安裝器.md` 第 19、21 行就有「反引號裡的註解 + 後面還有 `[test:]`」的實例,grep 查得到)。
3. 計劃的 25 條條款裡沒有註解那一條(S11 只鎖圍欄),所以綠燈不會揭露實作選了哪一邊。

## F6 條款定義行整個不驗存在,而現有檢查在推送時對「懸空」只提醒、只擋風險低的 doing 計劃,所以動機證據(計劃正文 57 個指不到)大半擋不到
severity: major
blocking: 是
⚠ 嚴重度請編排者判:我沒有 rtb 的資料,不能確認那 57 個裡有幾個落在條款定義行;下面只依本 repo 的程式與計劃自述。
引句:「這兩種行上的測試名本案不驗存在;但標了作廢還掛活測試時照樣算」
引句:「不做:合約行與條款定義行的存在檢查(各有檢查)」
file: `scripts/lumos:6569`(`_clause_check` 說明:「懸空只提醒不擋」)
file: `scripts/lumos:6430`(`_clause_check_twoway`:只有「風險低」門才擋懸空)
file: `scripts/lumos:7096`(`_spec_gate_push_candidates`:推送時查的只有碰到的、或落點被碰到的 `status: doing` 計劃)
1. 〈依據〉自述「計劃正文還有 57 個指不到的(42 個是測試在 rtb 的提交 b2fc512 被刪)」。計劃的 `[test:]` 本來就多數寫在條款定義行上。
2. 條款行被這組規則排除;「各有檢查」的那個檢查,對風險高的計劃只印提醒,對 `done` 的計劃推送時根本不跑(候選只收 `doing`)。所以一份已收尾的計劃條款綁到被刪的測試,這組規則不擋、條款檢查也不擋。
3. 這正是〈白話〉開頭描述的「讀的人會以為有守衛」,條款行落在三不管。若這是刻意取捨,〈不做〉的理由「各有檢查」跟程式不符,至少要改寫成「只在 doctor S5 提醒」。

## F7 保險的第二個條件按「副檔名」算,任何無關的已追蹤 .py/.cs/.kt 有未提交修改就整組降成提醒
severity: minor
blocking: 否
引句:「已追蹤的測試檔(各平台 profile 的測試副檔名,排除 `docs/`、`governance/`)有沒提交的修改或刪除」
file: `scripts/lumos:41261`(同一段用副檔名組 pathspec,不套 profile 的 `file_name_match`,例如 python 的 `test_*.py`)
1. 字面是「測試檔」,實作手上只有副檔名清單,沒有「這是不是測試檔」的判法;若照副檔名,本 repo(python profile,`.py`)只要任何一支 `scripts/*.py` 或 `src` 的 `.py` 有未提交修改,整組只提醒。全域規則提醒同一個 repo 常有別的會談在做事,所以「工作目錄髒」是常態,擋常常自動失效而只留提醒。
2. 未實測 git 指令的輸出;依據是讀碼。計劃應寫明用副檔名還是 profile 的檔名錨,並說是否也算已暫存未提交。

## F8 20 秒上限用完後「剩下的名稱不查」,但沒說順序;名稱去重的鍵沒說含不含平台
severity: minor
blocking: 否
引句:「整組共用一個 20 秒上限,用完剩下的名稱這次不查、印一行」
1. 實測單次 `git grep` 約 0.05 秒(本 repo、exp 計時 5 次共 0.27 秒),約 400 個第②道名稱就用完 20 秒;一次推送碰到很多篇、或一篇綁上千個測試(rtb 計劃量級)時,沒查的是哪些取決於走訪順序。計劃寫了「名稱去重」卻沒定義順序與鍵;若用 `set`,字串雜湊每次程序不同,同一次推送可能這次擋、下次放(閘不穩)。
2. 去重鍵若只用名稱,兩個平台的同名測試(`web:t_a`、`api:t_a`)只查其中一個。
3. 另:第①道 `_classify_test_refs` 對每個沒命中的名稱做 4MB 以上的 haystack 子字串比對(本 repo 實測 1000 個不存在的名稱 2.8 秒;exp3),不在名稱迴圈的 20 秒檢查裡,而計劃判定 `fake`/`dangling` 都算指不到,haystack 是白做的。這點不是判錯,只影響上限的意義。

## 已讀,無 finding
- 〈做法〉2「讀內容」:非 UTF-8 的筆記在 `_notelines_new` 進 `errs` 不進 `notes`(exp7 實測 `non-utf8: ([], ['…B.md:這篇筆記不是 UTF-8 文字…'])`),新規則不會讀到壞資料;原本的 errs 路徑照舊擋。刪檔後 reader 回 None 被略過(exp7「edit then delete」回空)。新增後改名會跟到新路徑(exp7 「edit then rename」回 A2.md 並保留那一行)。
- 〈做法〉10 doctor S20 的位置:`[S]`(`scripts/lumos:1736`)到 `[E1]`(`scripts/lumos:2110`)是既有截斷測試視窗,S19(`scripts/lumos:2538`)在視窗外,接在 S19 後不會踩到。
- 〈做法〉9 格子鍵 `test-gone`:`slot_parse` 對 `[test-gone:…]` 在登記前回空欄位、登記後才是欄位(exp5),與回退節「舊讀端把它當核心句文字」一致;`TEST_REF_RE`(`\[test:`)不會誤抓 `[test-gone:`。
- 單行寫法 summary、區塊寫法、`>-` 折行、CRLF:`_ns_summary_logical` 對區塊寫法與折行、CRLF 正確(exp4);單行寫法回 `{}`,計劃已自述要另處理(S12),現有 `_note_summary_entries`(`scripts/lumos:3513`)已有一版單行處理但要求前綴、且吃的是解析後的筆記物件不是全文,實作時要注意別拿錯零件。
- `slot_parse` 對 `[test:]`、`[test: ]`(空值)、`[test:a,,b]`、全形冒號、大寫鍵、成對反引號內的標記(exp5)行為與〈名詞〉描述一致。

最高等級:major,blocking 共 6 條
