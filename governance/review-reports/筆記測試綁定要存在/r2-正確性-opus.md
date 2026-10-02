severity: major

# 設計審 r2 正確性-opus:筆記測試綁定要存在_計劃

實驗都在 `tb-r2-work-正確性-opus/` 底下做(clone 與 g1–g4 小 repo),只讀 negguard,沒有改它。

## F1 推送時用「起點、終點兩端相減」,合過主線或 rebase 後強推時,主線上的提交會被當成這次新加的而擋下

severity: major
blocking: 是
引句:「這次改到的筆記清單用 `git diff --name-status -z --no-renames 起點 終點 -- 知識庫`(提交時起點是 HEAD、終點是提交索引)」
file: `scripts/hooks/pre-push:334`
file: `scripts/lumos:27265`
file: `scripts/lumos:27327`
file: `scripts/lumos:28578`
file: `scripts/lumos:28606`
file: `scripts/lumos:38546`
file: `scripts/lumos:38564`

1. 推送前掛鉤傳給 note-shape 的範圍是「遠端分支舊頂端..本機頂端」(`_hrange="$_rsha..$_lsha"`)。舊頂端在本機找得到時,`_lens_push_base` 直接拿它當起點,不檢查它是不是終點的祖先。
2. 既有的 note-shape 會逐個提交看,並用 `exclude_remote` 排除已經在主線上的提交(`rev-list … --not <主線>`),合併提交只算它自己多寫的行(`_merge_new_lines`)。這些保護就是為了這種範圍。本案改成只比兩端次數,這兩層保護都沒有了。`_lens_push_base` 的說明也寫了它「在合過主線…會算錯」。
3. 重現(g3 小 repo):主線上先有一個提交「筆記 B 加 `[test:t_mainline]`,同時加這支測試」,再有一個提交「刪掉 t_mainline 測試,不碰筆記」。按全庫只提醒的設計,刪測試不會被擋。功能分支先推過一次(遠端頂端 R),之後 `git merge main` 得到 T。
   ```
   == 推送範圍 R..T 的改到筆記
   A	docs/x-knowledge/Systems/B.md
   == 起點/終點 t_mainline 次數
   0
   1
   == 終點測試檔有沒有
   rc=1
   == 現有機制排除主線後的提交
   c3082c32…   (只剩那個合併提交)
   ```
   照計劃字面做:t_mainline 多了 1 次,工作目錄和終點兩邊都找不到,所以會判成指不到並擋下。可是使用者只做了合併,沒有寫任何筆記。`git rebase main` 後強推也一樣:舊頂端還在本機,`git diff 舊頂端 新頂端` 會把主線這段時間的筆記改動都算進來。
4. 另一種情形:找不到主線時起點是空樹,`_nodehome_clamp_base` 再把起點截到 note-shape 自己的上線點(`_NOTE_SHAPE_GOLIVE_MARK`),不是這組規則的上線點。結果是 note-shape 上線以來所有寫進筆記、現在指不到的名稱都算新加。這跟〈做法〉7 說的「不會把整段歷史當新寫」以及〈實務隱患〉相容那一條都對不上。
5. 1c 判新寫也用「起點那一側」,同樣會把主線帶進來的作廢條目當成這次新寫的。
6. 提交時合併提交整個跳過(MERGE_HEAD),理由是「推送前只查合併自己多寫的行」。但這組規則在推送時用兩端相減,並不只查合併自己多寫的行,這個前提對這組不成立。
7. 方向(不是唯一解):推送時起點側的次數除了起點版本,也要把範圍裡「已在主線上的提交」與「合併自己沒寫的行」排除。可以沿用 `_notelines_range_added` 的逐提交集合,把它當成起點側的補充;或者改用存量漂移那支 `_push_range_start` 算起點。另外要補一條測試:既有遠端分支合過主線後再推,不擋。

## F2 複查拿整個名稱去 grep,跟 `_classify_test_refs` 比對的單位不一樣:`類別.方法` 寫法的作廢檢查與 test-gone 檢查永遠不會觸發,而 Python 類別方法的真測試會被誤擋

severity: major
blocking: 是
引句:「索引沒認出的測試寫法(參數化名稱、類別裡的方法)會被判指不到;複查用被檢查版本的測試檔整字找,找得到就放行」
file: `scripts/lumos:40263`
file: `scripts/lumos:4820`

1. `_classify_test_refs` 對帶點的名稱,只要最後一段在方法集合裡就判 real(`method.rsplit(".", 1)[-1] in mset`)。這是推送前合約測試閘為了 C# `Class.Method` 寫法特地補的(見 Verification/2026-08-22_受波及合約測試真跑閘落地)。複查卻是拿整串名稱做 `git grep -w -F`,而測試檔裡從來不會出現 `類別.方法` 這樣連在一起的字。
2. 實驗 g1(C#,預設 csharp-xunit):
   ```
   'LoginTests.Login_fails_after_three_tries' → real
   git grep -w -F -e "LoginTests.Login_fails_after_three_tries" → rc=1
   git grep -w -F -q -e "Login_fails_after_three_tries"        → rc=0
   ```
   兩邊說法永遠不同,規則一律「判不了、不擋」:
   - [S7] 寫 `[test-gone:LoginTests.X]`,而 X 其實還在,不會擋。
   - [S10] 作廢條目掛 `[test:LoginTests.X]` 這支活測試,不會擋。
   所以用這種寫法時,S7 和 S10 是構造不出來的。
3. 反過來還有誤擋。實驗 g4(python profile):Python 的測試樣式錨在行首(`PYTHON_TEST_RE` 是 `^def`),所以類別裡的測試方法不在集合裡。
   ```
   'TestRetry.test_cap' → dangling
   git grep -w -F -e TestRetry.test_cap → rc=1
   ```
   `test_cap` 是真的 pytest 類別方法,但兩邊都說沒有,新加 `[test:TestRetry.test_cap]` 會被擋。這正是引句說「找得到就放行」的那一類,計劃的說法不成立。
4. 方向:複查用的字串要跟 classify 拆名稱的方式一致。帶點的就 grep 最後一段(或兩段都試)。並且補一條測試:`類別.方法` 寫法下 S7、S10 擋得住,Python 類別方法不誤擋。

## F3 複查「各平台根下的測試檔」沒講清楚是哪個根、哪些檔:照字面掃所有平台根,會讓綁錯平台的新名稱放行;根在 repo 外時 grep 直接出錯

severity: major
blocking: 是
引句:「各平台根下的測試檔用 `git grep -w -F`(提交時 `--cached`、推送時對終點)整字找這個名稱(去掉平台前綴)」
file: `scripts/lumos:41261`
file: `scripts/lumos:41269`

1. 實驗 g2:設兩個平台,ios 底下有 `testLoginLockout`,android 底下沒有,default_platform 是 android。
   ```
   'android:testLoginLockout' → dangling
   'testLoginLockout'         → dangling(沒寫前綴就歸到預設平台 android)
   git grep -w -F -e testLoginLockout HEAD -- ios android → 命中 ios,rc=0
   ```
   引句寫的是「各平台根」加「去掉平台前綴」,照字面就是掃全部平台根。結果是:新加的 `[test:testLoginLockout]` 或 `[test:android:testLoginLockout]` 綁錯了平台,兩邊說法不同,不擋。多平台專案兩邊常有同名測試,「沒寫前綴就落到預設平台」又是最常見的寫錯,1b 要抓的正是這種錯,這裡卻會放過。
2. 平台前綴沒定義(bad-name)的名稱要 grep 哪個根,計劃沒寫。
3. 平台根在 repo 外(多平台可以跨 repo)時,`git grep` 回 128:
   ```
   fatal: ../other: '../other' is outside repository … rc=128
   ```
   計劃沒說 grep 出錯算「有」、「沒有」還是「判不了」。照「兩邊都有才算有」,這種平台的 S7、S10 永遠不會觸發。
4. 「測試檔」怎麼從 profile 換成 pathspec(副檔名、`file_name_match`、`file_must_match`)也沒寫。如果實作沒照副檔名篩,平台根是 repo 根(單平台預設)時,這篇筆記自己就含這個名稱,grep 永遠說有,S1 就失效。
5. 既有的 `_dispositions_check_test` 已經處理過這幾件事:只掃那個平台自己的根、根在 repo 外只做工作樹那一道、只掃該 profile 的副檔名、排除 `docs/**` 與 `governance/**`(那是另一輪審查查出治理帳含測試名後補的)。〈PRIOR-ART〉卻把 `git grep` 列成「新寫的」,沒有指到這支。
6. 方向:寫明只 grep「那個名稱解析出來的平台」的根;前綴沒定義的名稱只靠 classify 判;跨 repo 的根當判不了並印原因;pathspec 照抄 `_dispositions_check_test`,或直接共用它。

## F4 把 `test-gone` 登記成格子鍵以後,新文法 PITFALL 只把 `[test:X]` 改成 `[test-gone:X]`,會從「缺三選一被擋」變成放行

severity: major
blocking: 是
引句:「它不算 PITFALL 防回歸那一格——測試刪了就是沒有守衛,PITFALL 要另寫 `[防回歸:無 理由]`。」
file: `scripts/lumos:28231`
file: `scripts/lumos:28223`

1. `_ns_slot_line_problems` 判斷舊行時,用的是「去掉白名單欄位後的核心句與連結」(`_ns_slot_key`)。判成舊行就整行不套必有鍵,只有「這次才加作廢」的情況例外。
2. 實驗(直接呼叫現有函式,登記鍵的部分用暫時改 `_SLOT_KEYS`/`_SLOT_CANON` 模擬):
   ```
   舊行:PITFALL: 重試沒設上限會打爆下游 [出處:abc1234] [根因:迴圈沒上限] [test:t_retry_cap]
   新行:同一行,只把 [test:t_retry_cap] 改成 [test-gone:t_retry_cap]
   現況(test-gone 不是鍵): [(('test/repro/防回歸',), '缺 test、repro、防回歸 三選一')]
   照計劃登記成鍵後: []
   對照:整個新寫(沒有舊行): [(('test/repro/防回歸',), '缺 test、repro、防回歸 三選一')]
   ```
   登記成鍵以後,`[test-gone:…]` 從核心句裡剝掉,文字鍵跟舊行一樣,這行就被當成舊行放行。現在的程式反而擋得住。
3. 本案這組規則也不會補上這個洞:`[test:]` 的次數變少,不觸發「新加」;`[test-gone:]` 的名稱確實已經不是測試,S6 放行。結果是一條新文法 PITFALL 從有守衛變成完全沒守衛,沒有任何一道擋下,引句要求「要另寫 `[防回歸:無 理由]`」等於沒人管。
4. S20 只顧到舊寫法的行,不受影響。要修的是新文法的行:在 `_ns_slot_line_problems` 判成舊行那一支,比照 `[被取代:]` 的例外,「舊行有 `test`、新行拿掉 `test` 而 PITFALL 三選一都沒有」時照樣查三選一。並補一條測試。

## F5 `[test-gone:]` 方括號是空的或寫佔位字時,沒有任何一道檢查;空方括號用「名稱次數」本身也判不出新加

severity: minor
blocking: 否
引句:「格子的 `slot_check` 只驗形狀(名稱非空;有 `@` 時後面至少 7 碼十六進位);名稱還在不在由本案這組查,兩邊不重複報同一種錯。」
file: `scripts/lumos:28223`

1. 格子檢查只看前綴在 `_SLOT_REQUIRED` 裡的摘要條目。正文行、`KEY:`/`SEE:` 條目裡的 `[test-gone:]`、`[test-gone:@abc1234]`(名稱是空的)或 `[test-gone:待補]`,格子都不會看到。
2. 本案這組對佔位字和空方括號的規定只寫給 `[test:]`。`[test-gone:待補]` 送進 classify 一定是「沒有」,所以 S6 放行。
3. 實驗:`_classify_test_refs("[test:]")` 回空清單,不是任何一種判定。〈做法〉2 用「名稱 → 次數」判新加,空方括號沒有名稱可以當鍵,S17 的「新加的 `[test:]`」得另外拿「空」當一把鍵來算,計劃沒寫。
4. 這裡風險低:`[test-gone:]` 不算防回歸,所以只標 minor。補法是把佔位字和空名稱的規則一起套到 `[test-gone:]`,並寫明空方括號的次數鍵。

## F6 1c 用「一模一樣」判新寫,中文摘要只是換個地方折行,就會被當成新寫的作廢條目

severity: minor
blocking: 否
引句:「接回後的整條在起點那一側——這次改到的所有筆記合起來——找不到一模一樣的,所以搬篇、改名不算新寫」
file: `scripts/lumos:28164`

1. `_ns_summary_logical` 用一個空白把續行接回去。中文句子只是換個地方折行,接回後的整條就多一格或少一格。
2. 實驗:
   ```
   'WHY: 舊做法是逐筆重試直到成功 [status:superseded] … [test:t_live]'
   'WHY: 舊做法是逐筆重試 直到成功 [status:superseded] … [test:t_live]'
   一模一樣? False | _ns_text_key 相同? True
   ```
3. 〈名詞〉說「摘要重排折行……不算新加」,1c 卻把重新折行算成新寫,兩邊對不上。格子規則已經有專門處理這件事的 `_ns_text_key`(中文旁邊的空白不算)。被擋的確實是一條掛著活測試的舊作廢條目,所以只標 minor。補法是改用 `_ns_slot_key` 比對。

## F7 「這次新寫行」從哪裡來沒有定義:推送時不用新寫行容器,摘要續行上的名稱也只能報到那一條的第一行

severity: minor
blocking: 否
引句:「印筆記、行號(這次新寫行上第一次出現的位置;只是次數變多、找不到新寫行時,報終點裡第一次出現的位置)」
file: `scripts/lumos:28164`

1. 〈做法〉7 寫明這組「不靠新寫行容器」,可是報行號又要用「新寫行」。推送時該拿淨差異的新增行號(像 `_NotelinesNet`)還是逐提交的文字,計劃沒說。
2. `_ns_summary_logical` 的鍵是一條的第一行。名稱新加在續行上時,報出來的是第一行,而第一行未必是這次寫的。
3. 退回「終點裡第一次出現的位置」時,如果同名的舊寫法出現在另一篇也有改到的筆記裡,會指到那篇的舊行。

## F8 提交時也擋,會擋到「之後的提交才補齊」的中間狀態,而逃生口一次跳過整道 note-shape

severity: minor
blocking: 否
引句:「本計劃讓同一條規則在提交時也跑、也擋(提早回饋,判法與逃生口相同),實作前請 Enzo 確認。」

1. 先在一個提交裡把筆記改成 `[test-gone:X]`,下一個提交才刪 X:第一個提交時 X 兩邊都還在,S7 擋下。推送時看的是最終狀態,本來會放行。
2. 摘要先寫 `[test:t_new]`,t_new 下一個提交才寫,而且工作目錄裡也還沒有:提交時兩邊都說沒有,擋下。條款定義行不受影響,因為那種行不算。
3. 專案慣例是「做到一半的本機提交,推之前壓成一個」,這種中間提交是常態。唯一的逃生口 `LUMOS_SKIP_NOTE_SHAPE=1` 會連同一次的其他 note-shape 規則一起跳過。給 Enzo 裁的時候,建議把這個代價寫進〈範圍〉那一句。

## 各節核對

- 開頭欄位與依據:已讀,無 finding。lands_in 與 related 指到的六篇都存在;筆記格子計劃第 142 行確實寫「天花板 3」。
- 名詞:已讀。內容問題已併進 F2、F3、F6。
- 範圍:已讀。提交時也擋的代價見 F8。
- 做法 1–11:問題見 F1–F7。另外核對過的事實:`_SLOT_KEY_RE` 認得 `test-gone`(只能是 1 到 12 字,不能有空白或冒號);`_ns_skip_slot_extra` 只在提交時加 `--slots` 才算;doctor 現在沒有 S20(測試總檔裡的 S20 都是別的計劃的條款編號)。這三點都對。
- 條款:已讀。照本來的意思,S1、S6、S11、S17 都能在測試夾具裡造出來;S7、S10 用 `類別.方法` 寫法或根在 repo 外時造不出來(F2、F3);S2 在合過主線的推送範圍下不成立(F1)。
- 回退:已讀,無 finding。
- 實務隱患:已讀。「只會擋測試檔裡根本沒有這個字的名稱」這句不成立(F2)。
- 實作紀錄、審計修正紀錄:已讀,無 finding。

## 實務隱患鏡頭

- 誤擋:F1(合過主線、rebase 強推、空樹起點)、F2(Python 類別方法)。
- 漏網:F2、F3(`類別.方法`、綁錯平台、跨 repo 根)、F4(PITFALL 守衛被拿掉也沒人擋)、F5。
- 時間:F1 的補法如果改成逐提交收集,會多跑一次 rev-list 和逐提交 diff。既有 note-shape 本來就跑這一套,可以共用同一趟結果,不必另算。
- 相容:F1 讓消費專案 `lumos update` 之後,已經推過、又合過主線的分支被主線的舊帳擋下,跟〈實務隱患〉相容那一條矛盾。
- 資安:無。只讀筆記與測試檔。`git grep` 用 `-F -e` 帶名稱,不經過殼層,沒有注入面。
- 金流、對外送出、不可逆:無。理由同快照〈已排除〉三條,讀程式碼確認過。

最高等級:major,blocking 共 4 條
