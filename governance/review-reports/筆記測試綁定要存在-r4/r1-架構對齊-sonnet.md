severity: major

# 架構對齊審(r1,架構對齊-sonnet)

審查對象:凍結快照 r1-snapshot.md。對照程式碼 repo:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard`(下稱 negguard)。慣例 skill:python-idioms(本案是零依賴單檔 CLI 內的規則接線,沒有並行、金額、時間帶時區的題目,對照鄰居慣例為主)。

## 四問

**問 1 分層與依賴方向。** 本案把新規則掛在 note-shape(筆記內容閘)這一層,判存在卻跨去借表態閘(代碼審層)的 `_dispositions_check_test`,同時鄰居 `clause_bindings`、`_classify_test_refs`(合約與條款綁定層,中性)已有同一題的判法。借用方向有兩處對不上:①判「這次才作廢」借的 `_ns_is_old` 只吃摘要行的鍵,吃不了正文的條款定義行,而條款定義行正是 S24 點名要擋的對象(F1);②主線那一版沒走 note-shape 自己的 `_ns_mainline_refs`(F2)。另外改 `_dispositions_check_test` 會讓表態閘一起受影響,但落點沒把它的家列進 `lands_in`(F8)。判存在的來源見 F3。

**問 2 命名與錯誤處理。** 設定函式 `_note_shape_test_refs_parse` 對得上 `_note_shape_slots_parse`,開關鍵 `note_shape.test_refs` 對得上 `note_shape.slots` / `note_shape.negation`,這部分一致。不一致在:①帳本 `extra` 的形狀,格子是攤平的 `slots_lines`/`slots_missing` 加字串欄 `check`,本案寫成單一巢狀鍵 `test_refs`,又說「違規種類欄再多列一項」,但 `check` 是兩值字串不是清單(F7);②鄰居的組級別失敗處理是整組包例外、印一句「這次沒跑完」後放行(`_ns_slots_collected`、`_note_shape_negation_emit`),本案只寫了逐名稱包例外,抽取、讀起點、算舊行失敗時走哪條沒寫(F7)。

**問 3 第二種做法。** 有四處:判存在的「類別.方法」與「設定認不到」兩段在 `_classify_test_refs`、`clause_bindings` 已有實作,本案另補一份而不是抽共用(F3);上線記號的取捨理由跟鄰居紀錄的理由不是同一個(F4);起點與主線整庫讀取用逐篇 `_nodehome_reader`,同一支 `_note_shape_eval` 裡「整個圖譜一次讀」用的是 `_nodehome_cat_blobs` 批次(F5);同一批條款行與合約行上,`[test:]` 的抽取在 spec-trace 走 `TEST_REF_RE`、在本案走 `slot_parse`(F6)。

**問 4 落點。** `slot_parse`、`_SLOT_KEYS`、doctor S20 的家是 lumos-cli-read(列了),規則本體的家是筆記內容閘(列了),`bound-tests-gate` 管 `_classify_test_refs` 一族(列了)。漏的是 `_dispositions_check_test` 的家:要改它,卻只寫「實作時用 impact 找家」,而且沒進 `lands_in`(F8)。S20 編號沒撞(negguard `scripts/lumos` 只有 S17 到 S19 在 `run_doctor`)。

## F1 `_ns_is_old` 認不得正文條款行,「起點就已作廢」對條款定義行永遠不成立
severity: major
blocking: 是
引句:「(1c)作廢的條目掛著活測試,而且這次才變成作廢:用格子的舊行判定 `_ns_is_old`」
file: `scripts/lumos:28167-28215`(`_ns_slot_key` 要求 `SYMBOL_RE` 前綴,沒有前綴回 `None`;`_ns_is_old` 對 `None` 回 `(False, False)`)
file: `scripts/lumos:28148-28165`(`_ns_summary_logical` 只收 `summary` 區的前綴行,舊行來源 `_ns_slots_old_lines` 也只讀摘要邏輯行)
1. 設計 S24 要求「新寫的作廢條目是計劃的條款定義行」照 1c 判,S12 要求「起點就已標作廢、只重排折行」不擋。條款定義行在正文,長相是 `- [S1] 條款 … [status:superseded] [被取代:…] [test:t]`,沒有 `PITFALL:` 這類前綴。
2. 照字面借 `_ns_is_old`:鍵算不出,回 `(False, False)`,等於「不是舊條目」,走「不是舊條目(新寫的)→ 違規」那一支。起點那版本來就標作廢、只改了折行的條款行,會被當成這次才作廢而擋下,S12 對條款行失效。
3. 最小實驗(在 negguard 以 python 載入 `scripts/lumos`):
   - `m._ns_slot_key("- [S1] 條款一 [status:superseded] [被取代:無 x] [test:t_a]")` 得 `None`
   - `m._ns_is_old(那個鍵, m._ns_old_keys([同一行]))` 得 `(False, False)`
   - 同樣內容換成 `PITFALL:x [test:t_a] [status:superseded] [被取代:無 y]`,鍵是 `('PITFALL','x',frozenset())`,`_ns_is_old` 得 `(True, True)`。
4. 這不是措辭問題:正文行的「舊行判定」要另寫一套(逐篇比起點那版同一條款編號那行有沒有標作廢),等於為條款行冒出第二種舊行判定;或者設計得明講條款定義行用條款編號對起點版比、不借 `_ns_is_old`。目前設計只寫借,沒寫正文怎麼辦。

## F2 主線那一版沒寫要走 `_ns_mainline_refs`(remote_only),推主線與 CI 上起點集合會把整批吃掉
severity: major
blocking: 是
引句:「主線那一版同樣讀一次(`_mainline_ref` 找得到才讀)」
file: `scripts/lumos:38736-38746`(`_mainline_ref` 預設 `remote_only=False` 會退回本地 main/master;docstring 寫明筆記形狀擋「推主線時本地 main 就是要推的頂端,拿它當已在主線上會把整批都排除掉」)
file: `scripts/lumos:27212-27229`(`_ns_mainline_refs` 固定 `remote_only=True`;`_ns_exclusions` 再用 `merge-base --is-ancestor tip ref` 濾掉已包含 tip 的參照,註解寫 CI 上本地 main 追蹤的 origin/main 就是這次推上來的頂端)
1. 鄰居 note-shape 找主線有兩層保護:只認 upstream、再濾掉已包含 tip 的。設計 PRIOR-ART 與步驟 3 都只寫 `_mainline_ref`,沒說傳 `remote_only=True`、也沒說濾 tip。
2. 照字面直接呼叫 `_mainline_ref(repo_root)`:在 main 上直接推(或 CI 跑 `--diff BEFORE..SHA`,本地 main 就是 SHA)時回傳的主線就是被推的終點;主線那一版的測試名全進起點集合,「新加的測試名」恆為空集合,整組規則在最常見的推主線情境永遠不擋。
3. 這不是效能或邊界題:是借用方式跟鄰居不一致、而且鄰居的註解已經把這個坑寫成教訓。改法是明寫借 `_ns_mainline_refs` + `_ns_exclusions`。未實測,依據是讀碼(兩支函式與 docstring)。

## F3 判存在第三套:「類別.方法」與「設定認不到」在鄰居已有實作,本案另補一份;判不了的三態也沒有出處
severity: major
blocking: 是
引句:「「類別.方法」寫法照 `_classify_test_refs` 的規矩補進第①道(只認方法名那段),第②道用方法名找」
引句:「第①道沒過但測試檔裡有 `def 名稱(` 這種 profile 認不得的寫法(條款綁定既有的「設定認不到」,Python 寫在類別裡的測試就是這樣)」
file: `scripts/lumos:40263`(`_classify_test_refs` 內 `real = method in mset or ("." in method and method.rsplit(".", 1)[-1] in mset)`)
file: `scripts/lumos:6696`(`clause_bindings` 內聯的 `re.search(r"^\s*def\s+" + re.escape(n) + r"\s*\(", hay, re.M)` 判 unrecognized)
file: `scripts/lumos:41244-41290`(`_dispositions_check_test` 回 `(bool, 字串)` 二態;git 非 0 非 1 的 rc 也回 `False` 加一段字串,逾時是例外)
file: `scripts/lumos:12856-12898`(`_platform_test_index` 已回 `loose_for`,放寬掃描連縮排與類別裡的宣告都算,本案沒提它)
1. 專案裡「這個測試名存不存在」現在有兩個引擎:`_classify_one`/`_classify_test_refs`(Check T、條款綁定、推送前合約閘、修正關卡共用,檔內註解反覆寫「不開第二套引擎」)與 `_dispositions_check_test`(表態證據,多一道樹內 git grep)。本案挑了後者,合理(只有它有第②道)。但本案需要的另外兩個語意,前者早有:Class.Method(`_classify_test_refs` 40263)與「設定認不到」(`clause_bindings` 6696,內聯正規式、沒抽成函式)。
2. 設計的做法是在 `_dispositions_check_test` 裡再寫一份 Class.Method、再寫一份 `def 名稱(` 的判斷:同一個規則三處各一份,日後鄰居改一邊(例如 `_KILL_METHOD_OK_RE` 的名稱合法檢查,本案沒套)會漂移。設計對「條款定義行判定」就知道要抽共用,對這兩段卻沒有。
3. 判不了的三態沒有機制:`_dispositions_check_test` 的回傳裡「grep 沒中(rc 1)」與「git 出錯(rc 非 0 非 1)」都是 `(False, 文字)`,只差字串;「第①道沒過但有 def」要另掃 haystack。設計只說「補進 `_dispositions_check_test`」兩項(類別.方法、跳脫),三態怎麼拿到沒寫,實作者只能解析訊息字串或改回傳形狀,而它的呼叫端是表態閘(`scripts/lumos:41377`)。
4. 依賴方向:note-shape(筆記層)呼叫表態閘(代碼審層)的函式,並且為了本案去改它(「表態閘一起受益」),表態閘的行為(Class.Method 開始放行、glob 路徑跳脫)也被一併改變,波及面落在另一道閘的合約上。比較乾淨的方向是把兩段共用判斷抽到中性的一層(貼著 `_classify_test_refs` 與 `_platform_test_index`),兩邊都借。

## F4 不另設上線記號的理由,跟鄰居紀錄的理由不是同一個
severity: major
blocking: 是
引句:「上線點沿用 note-shape 既有的(`_notelines_new` 已經處理),不另設記號——格子規則另設記號,是因為它擋的是「寫法」」
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:20`(WHY:格子另設記號的因:「程式與掛鉤同一輪 lumos update 到,不靠旗標分開的話程式一上線就全面開擋;既有上線點找不到是全查」)
file: `docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:33`(程式上線與開擋分開)
file: `scripts/lumos:28007-28027`(`_ns_slots_prepare`:推送與 CI 看自己的上線記號,找不到就不跑)
1. 設計把鄰居另設記號的原因說成「擋的是寫法」。鄰居自己記錄的原因是上線機制:消費專案 `lumos update` 後程式與掛鉤同時換上,新增的擋規則若沒有自己的記號,程式一到就對所有範圍內提交開擋;`_NOTE_SHAPE_GOLIVE_MARK` 只代表「note-shape 這道上線了」,對新加的子規則沒有時間切點。
2. 本案是預設 `block` 的新擋規則,屬於同一類。設計在步驟 7 自己承認後果:「`lumos update` 之前寫、還沒推的提交裡若新加了壞名稱,推送時會被擋」,而 CI 那邊(消費專案的 `note-shape --diff` 直接用新 lumos)更沒有掛鉤時間點可言。這正是鄰居用自己記號、「找不到整段不跑」要避免的情境。
3. 不算 major 以外的退路:本案提交時只提醒,所以「寫的時候檢查在不在」那招(`_notelines_live_sets` 逐提交看掛鉤)也用不上。要嘛照格子的作法另設記號(`--test-refs` 旗標加記號,上線與開擋拆兩步),要嘛把「為什麼這次可以破例」的理由改成鄰居紀錄的那個、並說明為何同一輪上線不會全面開擋。目前的理由等於換了一個鄰居沒用過的原因來做不同的事。

## F5 起點與主線整庫讀取用逐篇 `_nodehome_reader`,同函式裡「整個圖譜一次讀」是批次
severity: minor
blocking: 否
引句:「起點那一版整個知識庫用 note-shape 自己的讀檔零件(`_nodehome_list` 列檔、`_nodehome_reader` 讀內容,跟 note-shape 讀終點同一套」
file: `scripts/lumos:28426-28437`(`_note_shape_eval` 的「新程式檔喚醒」段:被檢查版本所有筆記用 `_nodehome_cat_blobs` 一次批次讀,註解寫另開手段是第二種做法)
file: `scripts/lumos:28290-28305`(`_ns_base_summary_lines` 讀起點版本也是 `_nodehome_cat_blobs`)
file: `scripts/lumos:26196-26200`(`_nodehome_side` 註解:逐篇 git show 65 篇要 2 秒以上,所以另設 share 機制)
1. 設計「時間」一節寫的是「起點知識庫批次讀(有上限)」,做法一節點名的卻是逐篇的 `_nodehome_reader`;起點不是 HEAD 時 `_nodehome_reader` 對每篇都是一次 `git show`。
2. 量級:negguard 約 630 篇筆記,用 `git show` 逐篇讀 200 篇約 4.4 秒(部分含中文路徑在我的實驗裡因轉義失敗,數字只當量級),起點加主線兩份整庫約 20 秒,跟設計的 20 秒上限同量級,超限時「剩下的名稱這次不查」。
3. `_nodehome_side` 只讀 `Systems/`,不能直接拿來讀整庫,所以不是照搬能解的;但批次讀的零件(`_nodehome_cat_blobs`)就在同檔、被同一支 `_note_shape_eval` 用過。⚠ 這條的嚴重度交編排者:我只對照了寫法一致性,沒量實作後的實際秒數。

## F6 `[test:]` 抽取在同一批條款行、合約行上有兩條路
severity: minor
blocking: 否
引句:「每條的鍵用格子的 `slot_parse`」
file: `scripts/lumos:5160-5166`(`invariant_test_refs` 用 `TEST_REF_RE`,小寫 `[test:`,逗號切)
file: `scripts/lumos:6693`(`clause_bindings` 對條款行走 `invariant_test_refs`)
file: `scripts/lumos:3764-3790`(`slot_parse` 認大寫鍵、全形冒號)
1. S10 要求大寫鍵、全形冒號也要抽到。條款定義行與合約行本來由 `TEST_REF_RE` 一路(spec-trace、Check T)看,本案 1c 對它們也要抽 `test`,走的是 `slot_parse`。
2. 同一條 `- [S3] … [status:superseded] [TEST:t_x]`:本案認為掛著測試名(會擋),spec-trace 認為沒有 `[test:]`(untagged)。兩個工具對同一行的「有沒有掛測試」答案不同。
3. 是 r2 刻意換成 `slot_parse` 的決定(摘要行那邊對齊格子),對摘要行站得住;對條款行與合約行,設計沒有說明為何不改走 `invariant_test_refs`。⚠ 嚴重度交編排者。

## F7 治理帳 extra 形狀、單次跳過路徑與組級別失敗處理與鄰居不同
severity: minor
blocking: 否
引句:「`extra` 裡既有的違規種類欄照既有寫法再多列一項」
file: `scripts/lumos:28368-28376`(`_ns_slot_extra`:`check` 是字串 `"slots"` 或 `"shape+slots"`,另有平的 `slots_lines`、`slots_missing`)
file: `scripts/lumos:28089-28110`(`_ns_skip_slot_extra`:整段包例外、只在有格子子開關時才跑,內部自己呼叫一次 `_note_shape_eval`)
file: `scripts/lumos:28030-28044`(`_ns_slots_collected`:算失敗印一句、當作沒有)
1. `check` 是單值字串,「再多列一項」沒有照既有寫法可循;加上本案共有 shape、slots、test_refs 三種,字串組合要重新定義。鄰居的攤平欄位(`slots_lines`)與本案的巢狀 `test_refs` 鍵形狀也不同。
2. 步驟 8 要求提交時單次跳過先算一次 `test_refs` 記帳,但 `_ns_skip_slot_extra` 內部已經呼叫了一次 `_note_shape_eval`(取新寫行),另寫一支同型函式等於跳過路徑跑兩次 `_notelines_new`,跟步驟 2 的「不另呼叫第二次 `_notelines_new`」互相打架;合起來做就得把兩個容器併進同一次 eval。設計沒說怎麼併。
3. 組級別的失敗(讀起點、抽取、算舊行例外)走哪條沒寫:鄰居一律「印一句這次沒跑完、不影響其他檢查」,本案只寫了逐名稱判不了。

## F8 落點:`_dispositions_check_test` 的家沒進 `lands_in`,也沒指名
severity: minor
blocking: 否
引句:「管 `_dispositions_check_test` 的那篇(實作時用 `lumos impact --file` 找家)」
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:44`(DEP 行列了一串 `_dispositions_*` 函式,是這族的家;`about_code` 列 `scripts/lumos`)
1. 計劃 front matter 的 `lands_in` 只列筆記內容閘、lumos-cli-read、bound-tests-gate;同一份計劃要改 `_dispositions_check_test`(Class.Method、路徑跳脫),它的家(表態閘那篇)沒進 `lands_in`,CLAUDE.md 鐵則 5 要求計劃寫 `lands_in`(現況落在哪幾篇)。
2. 「實作時再找」跟鄰居計劃(如筆記格子計劃的 `lands_in`)的作法不同:那邊在設計階段就把受影響的節點列齊。設計階段已能用 grep 找到(上面那篇),不需等到實作。

## 其他已讀,無 finding
- 設定開關 `note_shape.test_refs` 與總開關疊加、壞值照 block 並提醒:對得上 `_note_shape_slots_parse` / `_ns_slots_mode`(`scripts/lumos:28113-28145`)。
- 摘要接回續行、單行 summary 補法:抽共用(`_note_summary_entries` 的補法抽成吃全文),跟鄰居 S16 到 S19 的作法一致(`scripts/lumos:3513-3523` 註解)。
- 全庫提醒 S20 的位置、`warn_soft`、不寫帳、`--ci` 的取捨、索引建不起來只印一行:對得上 S17 到 S19(`scripts/lumos:2513-2545`)。
- 不改 PITFALL 三選一、`test-gone` 進 `_SLOT_KEYS` 與 `_SLOT_REPEATABLE`、不進 `_SLOT_NEW_ONLY`:對得上鍵表現況(`scripts/lumos:3743-3750`)。
- 新寫行入口借 `_note_shape_eval` 的容器、不另跑 `_notelines_new`:對得上 `hints`/`tags`/`slots` 三個既有容器的作法(各自一個參數、各自隔離);只是要加第四個參數(F7 已提到容器與跳過路徑)。

不對齊共 8 條,其中 major 4 條
最高等級:major,blocking 共 4 條
