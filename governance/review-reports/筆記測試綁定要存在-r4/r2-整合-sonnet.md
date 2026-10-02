severity: major

# 設計審 r2 整合-sonnet 席報告(整合與接手鏡頭)

做法:把〈做法〉1–11 與 S1–S25 當實作單,逐步對 `scripts/lumos` 與 `scripts/test_lumos.py` 真碼接一次,實驗全在我自己的 `--shared` clone 與探針腳本裡跑(沒動被審 repo)。交叉引用已核:`Projects/漂移防治路線圖_計劃`、`Projects/筆記格子寫法與過期檢查_計劃`、五篇 Systems 節點、skill 指令速查 03/04/05/06、`reference.md`、`scripts/lumos` 的說明字典(`:42701` 那張閘說明表)都存在;doctor S17–S19 在 `[S]..[E1]` 截斷視窗之外(`scripts/test_lumos.py:7545`),S20 接在 S19 後不會落進去。

## F1 單行寫法的 summary 無法用計劃指名的零件抽到,S12 造不出來
severity: major
blocking: 是
引句:「摘要裡一個前綴條目接回續行後的整條(`_ns_summary_logical`;單行寫法的 summary 整個值算一條)」
file: `scripts/lumos:28148`(`_ns_summary_logical`)、`scripts/lumos:27152`(`_notelines_regions`)
1. 〈名詞〉把「單行寫法的 summary」掛在 `_ns_summary_logical` 名下,S12 也要求「summary 是單行寫法」照樣抽到並查。
2. 實測(我的探針):`summary: "WHY:foo [test:t_x]"` 與 `summary: WHY:foo [test:t_x] 後面` 兩種單行寫法,`_notelines_regions` 把整個 `summary:` 行判成 `other`(鍵行本身一律 `other`,第 `:27170` 附近 `out[i] = "other"; continue`),`_ns_summary_logical` 回 `{}`。也就是照字面「用 `_ns_summary_logical`」實作,單行 summary 裡的 `[test:]` 一個都抽不到,規則靜默放行。
3. 連帶:`summary: >` 折疊寫法若續行縮排跟前綴行一樣深(`  WHY:foo` 下一行 `  [test:t_x]`),`ind > last_ind` 不成立,第二行被丟掉,同樣漏。
4. 要實作 S12 的人得自己另寫「從 frontmatter 取 summary 整個值」的抽取(要不要剝引號、沒前綴的單行值算不算一條、`>` 折疊怎麼接),計劃沒定;不同猜法在 S12 夾具(引號包的 / 不包的 / 沒前綴的)上會分岔。
5. 重現:`/opt/homebrew/bin/python3` 以 `SourceFileLoader` 載入 `scripts/lumos`,對上述兩個字串呼叫 `_notelines_regions` 與 `_ns_summary_logical`,輸出 `['other','other','other','other','body','body'] {}`。

## F2 `_test_in_tree` 只回三態,表態閘「行為不變」(S24)接不回去
severity: major
blocking: 是
引句:「它回三種:找得到、找不到、判不了(git 出錯或逾時、平台根在 repo 外、平台根是子模組)」
file: `scripts/lumos:41244`(`_dispositions_check_test`)、`scripts/lumos:41386`(呼叫端 `_ev`)、`scripts/test_lumos.py:41455`(`③git show 卡住…無法驗證`)、`scripts/test_lumos.py:41504`(`grep 不到`)
1. 現行表態閘對這四種結果的處置各不相同:平台根在 repo 外 → `return True, ""`(只做第①道,放行);`git grep` rc=1 → `False` + 「grep 不到」訊息;rc 其他值 → `False` + 「無法對推送版本的樹驗證」訊息;逾時 → `TimeoutExpired` 往上丟,由每題的 except 轉成「無法驗證」(測試 `:41458` 釘住,斷言字樣是「無法驗證」,而 rc≠0 那句是「無法對…驗證」,兩句不同)。
2. 計劃把「平台根在 repo 外」與「git 出錯或逾時」併成同一個「判不了」。表態閘包裝若照 note-shape 的語意把「判不了」一律映成 `False`,跨 repo 平台的表態證據從放行變成擋下,S24 與既有跨 repo 行為翻;若映成 `True`,git 出錯會從擋下變放行(fail-closed 變 fail-open)。兩種映射都改了行為,要「行為不變」只能讓 `_test_in_tree` 回帶原因的結果(至少區分外根、git 非 0/1 rc、逾時、找不到),或讓外根判斷留在包裝層、不進抽出的函式——計劃兩邊都沒講,而且 S14 的「判不了」三種來源跟 S24 的「原本一樣」互相要求不同的函式界面。
3. 另:子模組「判不了」是新行為(現行碼沒有任何子模組判斷,`git grep` 對 gitlink 路徑只會回 rc=1 當「找不到」),不是「抽出」,S24 夾具要排除這條或說明表態閘是否同步改用。
4. 未實測表態閘跨 repo 夾具(現有 `t_codeloop_dispositions_*` 有沒有涵蓋外根我沒逐支核),依據是讀碼。

## F3 第②道對 `Class.Method` 寫法會把第①道判 real 的名稱判成找不到
severity: major
blocking: 是
引句:「第②道問被檢查的版本裡那個平台的測試檔整字找不找得到」
file: `scripts/lumos:40248`(`_classify_test_refs`)、`scripts/lumos:41244`(`_dispositions_check_test` 的 `git grep -w -F -e name`)
1. 第①道對 `Class.Method` 的處理是「取最後一段比對方法集合」:`real = method in mset or ("." in method and method.rsplit(".",1)[-1] in mset)`,回傳的 `method` 欄位仍是完整的 `FooTests.Bar`。
2. 第②道照抽出來的原樣做 `git grep -w -F -e <name>`;原始碼裡不會出現字面 `FooTests.Bar`(類別與方法是分開宣告的)。
3. 實測:fixture 倉庫 `tests/FooTests.cs`(`class FooTests { [Fact] public void Bar() {} }`)、`csharp-xunit`:`_classify_test_refs("[test:FooTests.Bar]")` → `real`;`git grep -w -F -q -e FooTests.Bar HEAD -- ':(glob)**/*.cs'` → rc=1;`-e Bar` → rc=0。照字面把①回的名稱原樣餵②,每個已提交、真實存在的 `類別.方法` 綁定都被判成「指不到」,在 block 設定下擋推送(第②道「找不到」算指不到)。
4. 同時,現行 `_dispositions_check_test` 對這種名稱根本在 `name not in methods_for(plat)` 就回 False(實測 `('FooTests.Bar')` → 「工作樹掃不到」),所以抽出來的段落從沒處理過點號名稱;計劃說「類別.方法都已處理」只對第①道成立。
5. 沒有 S 條款覆蓋這個夾具(S1/S15 都是裸名稱),造不出紅燈就會上線。

## F4 「HTML 註解裡的不算」沒有任何可用的既有零件支持,指名的兩支都明講不處理註解
severity: major
blocking: 是
引句:「程式碼圍欄裡的不算(`_visible_lines`)、HTML 註解裡的不算」
file: `scripts/lumos:4157`(`_visible_lines` 內註解「★不偵測 HTML 註解★」)、`scripts/lumos:4768` 附近(`_strip_inline_markup` docstring「★不碰 HTML 註解★」)
1. 計劃的 PRIOR-ART 說抽取沿用 `_visible_lines`(圍欄)與 `slot_parse`;這兩支以及 `_strip_inline_markup` 都在碼裡白紙黑字寫明不認 HTML 註解(`-b r3` 兩席證明「偵測註解本身就是洞:先關再開」)。
2. 實測(探針,`_ns_summary_logical` + `slot_parse` + `_visible_lines`):摘要行 `WHY:x <!-- [test:t_in_comment] --> 後` 抽出 `('test','t_in_comment')`;正文跨行 `<!--\n- 舊 [test:t_multi_line_comment]\n-->` 抽出 `('test','t_multi_line_comment')`。
3. 照字面「用既有零件」實作 → 註解裡的名稱被當名稱查,在 block 下被擋;要真的不算就得新寫註解偵測,正好是 repo 已有判例證明有洞的那條路,計劃沒給判法、也沒有 S 條款或夾具(S11 只覆蓋圍欄)。
4. 實作者在「照字面不處理」與「自寫註解偵測」之間必須猜一邊,兩邊對註解夾具的結果相反。

## F5 「碰到的筆記」從 rows 取路徑集合,三種讀法結果不同
severity: major
blocking: 是
引句:「這組從 rows 取出筆記路徑集合。不另呼叫第二次 `_notelines_new`。」
file: `scripts/lumos:27344`(`_notelines_new`,以 `keep_other=True` 呼叫)、`scripts/lumos:28025` 附近 `_notelines_rows`
1. `_note_shape_eval` 以 `keep_other=True` 呼叫 `_notelines_new`,回的 `notes=[(路徑, 全文, rows)]`。實測(我造兩個提交:A 只在 `Systems/筆記內容閘.md` 結尾加空行、B 只把 `check-t-sentinel.md` 的 `updated:` 改日期):A 回 `(path, 全文, [])`(rows 為空,但路徑還在 notes 裡)、B 回 `rows=[(5,'other')]`。
2. 〈名詞〉定義「碰到」=「有新寫的行」,但「從 rows 取出筆記路徑集合」可以是:①`notes` 裡全部路徑(含 rows 為空的:只加空行、或新增的行後來被後面的提交刪掉);②`rows` 非空的路徑;③rows 排除 `other`(只改開頭欄位不算)。三種對同一個推送給不同的 touched 集合。
3. 具體後果:`lumos set` / `append` 這類工具改開頭欄位(如 `updated:`、`status:`)的提交,在讀法②③成立時要把整篇舊壞名字修完才推得上去(讀法②),或不要求(讀法③);只加空行的提交在讀法①成立。S2 夾具(「這次沒有新寫行的筆記」)選哪種,實作與夾具必須同一個猜法才綠。
4. 另:`notes` 的第二個元素本來就是被檢查版本的全文(`reader(p)` 讀的),〈做法〉2「再用 note-shape 讀終點的同一個讀檔零件讀一次」是多餘的第二次讀取,而且 staged 模式下要讀的是 index 版本,計劃沒講 `tip_where="index"` 怎麼走。
5. 重現:探針 `../probe1.py`(在我的臨時目錄 `tb4-r2-work-整合-sonnet/`),輸出 `…筆記內容閘.md 0 []` 與 `…check-t-sentinel.md 1 [(5, 'other')]`。

## F6 測試名正規化:`slot_parse` 值保留反引號,第①道直接判 bad-name
severity: minor
blocking: 否
引句:「反引號與大小寫、全形冒號照 `slot_parse` 的規矩。」
file: `scripts/lumos:3764`(`slot_parse`)、`scripts/lumos:5416`(`discover_test_methods` 取方法名時 `strip("`")`)
1. 實測 `_classify_test_refs("[test:`Bar`]")` → `bad-name`(`_KILL_METHOD_OK_RE` 不收反引號);而索引端(Kotlin 反引號測試名)是去掉反引號收進集合的。`slot_parse` 的值不去反引號。
2. 照字面實作,Kotlin 風格 `[test:`名稱`]` 一律「指不到」。現行合約路徑(`TEST_REF_RE`)也是同一行為,所以只算一致性提醒,但計劃把「照 slot_parse 的規矩」寫成名稱解析規格,實作者無從知道要不要先去反引號。
3. 同理:全形逗號切分後交給 `resolve_test_refs` 時,`平台：名`(全形冒號)不會被當前綴(只認 ASCII `:`),落成 bad-name。

## F7 自舉:本 repo 改動範圍裡的筆記自己會被這條規則擋,上線順序沒寫
severity: minor
blocking: 否
引句:「[[Systems/bound-tests-gate]](第①道借它那支)、[[Systems/棧別提問表態閘]](`_test_in_tree` 從它抽出)」
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:17`
1. 〈做法〉11 要求同步 `Systems/bound-tests-gate`;該篇摘要第 17、18 行(WHY、FLOW)正文是散文引用 `[test:] → …`,方括號沒有名稱。〈做法〉3.2 只豁免「正文裡」散文的 `[test:]`,摘要條目一律違規。我的原型(摘要用 `_ns_summary_logical`+`slot_parse`、正文用 `_visible_lines`)對這篇列出 `(17,'WHY','<empty>')`、`(18,'FLOW','<empty>')`。
2. 本 repo 設定讀的是被推版本(tip)的 `.lumos/config.json`:實作提交若同一推送內帶 `note_shape.test_refs: block` 與改了 `bound-tests-gate`,推送會被自己的規則擋下;計劃只說「本 repo 開 block」,沒定順序(先清舊壞名字、config 最後一個提交)。
3. 〈實務隱患〉「誤擋:本案本意」成立,但〈實作紀錄〉要有這一步,否則第一次推送就卡。

## F8 子模組判不了的判法沒給,且「根不是子模組但倉庫裡有子模組」會誤判找不到
severity: minor
blocking: 否
引句:「當第②道判不了(git 出錯或逾時、平台根在 repo 外、平台根是子模組)時,那個名稱應不擋並印一行」
file: `scripts/lumos:41244`(`_dispositions_check_test`,沒有任何子模組判斷)
1. 抽出的原段落沒有子模組判斷;`git grep` 不加 `--recurse-submodules` 對 gitlink 路徑只回 rc=1。「平台根是子模組」要自己加一步(例如對 tip 做 `git ls-tree`、看 mode 160000),計劃沒說用哪個指令、對平台根本身還是對路徑任一祖先判。
2. 單平台 legacy(本 repo 型:`root=repo_root`)而子模組裡有測試檔時,第①道的 `os.walk` 掃得到子模組內容、第②道的 `git grep` 掃不到 → 判「找不到」而非「判不了」,誤擋;S14 夾具(根本身是子模組)抓不到這種。
3. `_disp_git_timeout()` 單次 8 秒,與〈做法〉4「整組 20 秒上限」沒有串:一次 grep 可超出剩餘預算最多 8 秒,實作者要決定把剩餘預算傳進去還是接受超出。

## F9 單次跳過的 `test_refs` 帳,照抄既有函式會被兩個條件擋掉
severity: minor
blocking: 否
引句:「提交時被單次跳過時,先用 `rows_out` 算一次記進去;推送時的單次跳過在讀範圍之前就返回,不搬位置,那筆沒有 `test_refs`。」
file: `scripts/lumos:28572`、`scripts/lumos:28089`(`_ns_skip_slot_extra`)
1. 現行跳過分支是 `extra = _ns_skip_slot_extra(root) if (staged and slots_flag) else None`,而 `_ns_skip_slot_extra` 在格子子開關為 `off` 時也提早回 `None`。照這形狀擴充,S21 的「提交時被單次跳過」只有在掛鉤帶 `--slots` 且 `note_shape.slots` 不是 off 時才帶 `test_refs`;計劃沒說 test_refs 是否也要綁這兩個條件(它跟格子是不同開關)。
2. 擋下事件的 `nodes` 與 `count` 字串也沒講:現行 `nodes=` 只收 viol 與 sviol 的路徑,`count` 是「新違規 N 條、格子缺漏…」。只有 test_refs 違規時 `count` 會寫「新違規 0 條」、`nodes` 為空,`lumos gov <節點>` 查不到。
3. `check` 欄在只有 test_refs 時留空(`_ns_slot_extra` 才設 `check`),跟「這組的有無只看 `extra.test_refs`」一致,但 `lumos gov` 去重鍵含 `check`,同一提交、同一組空 `nodes` 的 blocked 與別種 blocked 會被折成一筆。

## F10 條款定義行「抽成共用」是整檔有狀態的函式,而且名稱解析有兩套
severity: minor
blocking: 否
引句:「實作時把它判定義行的那段抽成共用」
file: `scripts/lumos:6613`(`clause_bindings`)
1. 「定義行」不是逐行純判斷:`clause_bindings` 用 `defined/dup/listlike_extra/fallback` 跨整篇累積,第二次出現在行首的同編號是 `duplicate`、出現在像清單的認不得行是 `shadowed`。抽出來的函式要回哪些行號沒說:只回第一次行首那行,則第二次的「重複定義行」會被當正文行檢查名稱;全部 `lead` 命中的行都算,則 shadowed 的另當。
2. `clause_bindings` 讀 `[test:]` 用 `invariant_test_refs`(`TEST_REF_RE`,小寫、ASCII 冒號),本規則其他處用 `slot_parse`(大寫鍵、全形冒號)。「作廢+活測試」對條款行與合約行要取名稱時,選哪一個?S12 的寬鬆寫法夾具在條款行上兩種答案不同。
3. 條款定義行只在 `type: project` 計劃適用,計劃沒寫 `type` 怎麼從被檢查版本全文取(`split_frontmatter` 即可),但沒寫。

## F11 S25 條款在 `_note_shape_eval` 這一層不會翻紅
severity: minor
blocking: 否
引句:「當 `_note_shape_eval` 傳了 `rows_out` 而沒傳 `slots` 時,格子規則應不跑」
file: `scripts/lumos:28378`(`_note_shape_eval`)、`scripts/lumos:28628`(`cmd_note_shape` 由 `_ns_slots_prepare` 決定格子跑不跑)
1. `_note_shape_eval` 本身從不跑格子規則:格子違規由 `cmd_note_shape` 在 eval 之後呼叫 `_ns_slots_collected` 算,`slots` 容器只是被塞 `notes/old_by`、並讓內部多收一遍 mark2 逐提交文字。傳不傳 `slots` 對回傳的 `viol` 沒有差別,所以 `t_note_shape_eval_rows_out` 只呼叫 `_note_shape_eval` 無法分辨「不連帶開格子」是真的還是假的。
2. 真正要守的是 `cmd_note_shape` 在沒帶 `--slots`(舊掛鉤)時,新增的 test_refs 路徑不會順手去呼叫 `_ns_slots_*`;夾具要走 CLI、看有無 `slots_lines` 帳欄。

## F12 〈做法〉5「保險」沒給具體偵測,S16 夾具有分岔
severity: minor
blocking: 否
引句:「已追蹤的測試檔(各平台 profile 的測試副檔名,排除 `docs/`、`governance/`)有沒提交的修改或刪除」
file: `scripts/lumos:41244`(第②道 pathspec 的組法可借)
1. 沒說用哪個 git 指令(`git diff --name-only HEAD` 含暫存?`git status --porcelain`?),也沒說「已暫存但沒提交」算不算修改、平台根在 repo 外時怎麼辦、多平台時各根各副檔名怎麼組 pathspec(第②道那段 pathspec 組法可借,但沒指名)。
2. 「目前簽出的提交不是推送終點」要拿 `_lens_full_sha(root,'HEAD')` 比 `tip`;worktree/CI detached HEAD 的情況沒提,CI 常是 detached 且等於終點,應不誤觸發——沒寫。

## F13 作廢 PITFALL 照〈做法〉3.4 拿掉測試後,格子規則可能再唸三選一
severity: minor
blocking: 否
引句:「改法:摘要條目把綁定移到接手的那一條(`[被取代:]` 指的那裡),或拿掉」
file: `scripts/lumos:28290` 附近(`_ns_slot_line_problems`)、`scripts/lumos:3750`(`_SLOT_ONE_OF`)
1. 舊 PITFALL 行若已是新文法(有出處與根因)並把 `[test:X]` 拿掉,`_ns_slot_key` 的核心句沒變 → 判舊行,只查 `[被取代:]`,不會唸三選一;但新寫的作廢 PITFALL(同一提交寫好 `[status:superseded]` 又沒有測試)走完整檢查,會唸缺 test/repro/防回歸。改法文字沒講作廢的 PITFALL 該補哪一個,實作者只能在擋下訊息裡猜。低風險,列為提示。

## 其他已讀、無 finding
- 〈做法〉6 設定:`_note_shape_config`(`:27131`)遇 `note_shape` 為物件且沒有 `gate` 鍵照 block;本 repo `.lumos/config.json` 目前沒有 `note_shape` 鍵,加 `{"note_shape":{"test_refs":"block"}}` 不改 gate 判定;`_note_shape_slots_parse` 的壞值處理形狀可直接照抄。已有 `t_note_shape_*` 19 支測試的夾具裡都沒有 `[test:` 字樣(我 grep 過),預設 warn 不會讓既有測試翻紅。
- 〈做法〉9 `test-gone` 鍵:`_SLOT_KEY_RE` 允許 1–12 字且不含 `:`,`test-gone`(9 字)可通過;不進 `_SLOT_NEW_ONLY` 時 `_ns_slot_key` 的核心句會把 `[test-gone:X]` 當欄位剝掉,S23 成立(`[test:X]`→`[test-gone:X]` 核心句不變,判舊行)。
- 〈做法〉10 doctor S20 位置:S17–S19 之後、S8 之前,在 `[S]..[E1]` 視窗外;`warn_soft` 不計問題數。全庫索引時間量測:`_platform_test_index` 與 `methods_for` 合計約 0.12 秒、`hay_for` 約 0.07 秒、單次 `git grep` 約 0.12 秒,20 秒上限充裕。
- 治理帳:`note-shape` 在 `_KNOWN_GATES`;新 `extra` 鍵 `test_refs` 不在 `_GOV_FIELD_TYPES`,不會被當型別錯誤跳過;`lumos gov` 的 mapper 只挑指定欄位,新鍵被忽略,與〈回退〉說法一致。

最高等級:major,blocking 共 5 條
