severity: major

# r3 正確性-opus(鏡頭:正確性與邏輯)

實驗環境:`git clone --shared` 到 `fg-r3-work-正確性-opus/repo`;另寫一支照快照字面重組的判法腳本 `fg-r3-work-正確性-opus/exp.py`(紅樹=對修正後建工作樹、只把 `fixed` 檔 `git checkout <base> --` 換回,`base` 沒有就刪;判法=`_run_bound_tests(樹, items, tails)` → `_ran_count` → `_spec_gate_declared(method, loose_for(plat))` → `_spec_gate_verdict`,再加快照第 4 項新規則「讀得出支數的棧沒逾時卻讀不到支數 → 判不過」)。以下「重現」指令都在 `fg-r3-work-正確性-opus/` 底下跑;測試指令用有 pytest 的 `/usr/bin/python3 -m pytest -p no:cacheprovider tests -k {method}`,`LUMOS_TEST_TIMEOUT=8`。

派工詞列的情境,實測結果先總列(`/opt/homebrew/bin/python3 exp.py`):

| 情境 | 期望 | 實際 |
|---|---|---|
| good:真修正+好測試 | 過 | PASS ✓ |
| weak:弱測試(沒驗修正) | 不過 | FAIL ✓ |
| collide:`test_fcdemo` 撞 `test_fcdemo_strip` | 不過 | FAIL ✓(弱證據「篩選匹配到 2 支」) |
| param:參數化 3 組 | 過 | PASS ✓(n=3、declared=1) |
| hang:修卡死,紅樹逾時 | 過 | PASS ✓(逾時算紅) |
| **weak_import**:弱測試(`assert True`),測試檔頂端 import 修正新增的名字 | 不過 | **PASS ✗**(F2) |
| **missing_file**:修正動 a.py+b.py,紀錄只列 a.py,測試沒驗修正 | 不過 | **PASS ✗**(F2) |
| **crash**:修正前深層輸入讓直譯器崩潰,好測試 | 過 | **FAIL ✗**(F3) |
| **two_paths**:文字、JSON 兩條路徑都列 `fixed`,唯一測試只走文字 | 不過 | **PASS ✗**(F4) |
| **shared_red**:一組純測試補強(`no_red_reason`)+一組真修正,測試同檔 | 過 | **FAIL ✗**(F1) |
| **untracked_cfg**:`.lumos/config.json` 沒進版控 | 過 | **FAIL ✗**(F6) |

## F1 所有組共用一棵紅樹:純測試組列為 `fixed` 的測試檔被換回,同檔其他組新寫的測試在紅樹裡消失,好修正判不過
severity: major
blocking: 是
引句:「把這輪修正紀錄所有 `fixed` 路徑的檔,在紅樹裡用 `git checkout <base> -- <檔>` 換回 `base` 的內容」
file: `scripts/test_lumos.py:31758`(本 repo 所有 `t_` 測試都在這一支檔裡,`main()` 從 `globals()` 收)
1. 輸入:同一輪兩組。G1 修 `lib.py`,新測試 `test_norm` 寫進 `tests/test_lib.py`;G2 是「測試沒釘住」類,只把同一支 `tests/test_lib.py` 裡的 `test_old` 補斷言,寫 `no_red_reason`。照第 1 項「每組至少一條 `fixed` 路徑、`fixed` 的檔有改動」,G2 唯一能列的 `fixed` 就是 `tests/test_lib.py`。
2. 照引句,紅樹把這一輪**所有** `fixed` 檔換回 `base`,包括 G2 的測試檔(快照沒有把「寫了 `no_red_reason` 的組」的 `fixed` 檔排除在紅樹之外)→ G1 的 `test_norm` 在紅樹裡不存在。
3. 重現(`exp.py` 的 `mkrepo/fixcheck`,情境 shared_red):只換回 `lib.py` → `PASS`;照快照換回 `lib.py`+`tests/test_lib.py` → `FAIL`,紅樹輸出 `collected 1 item / 1 deselected / 0 selected`、`n=None`、`declared=0`,判「修之前選不到這支測試」。
4. 本 repo 的所有測試都在 `scripts/test_lumos.py` 一支檔,所以只要某輪有一組「測試沒釘住」的純測試補強,同輪其他每一組都會被判不過——結構性誤擋,不是邊角。程式與測試同檔的棧(〈實務隱患〉自己提的 Rust)也一樣,而且是整輪連坐,不只那一組。
5. 要改的地方:紅樹只換回「沒寫 `no_red_reason` 的組」的 `fixed` 檔;條款 S4 補一個「一組純測試補強+一組真修正、測試同檔 → 真修正那組照過」的情境。

## F2 紅樹被「部分換回」弄壞(匯入錯、收集錯、編譯錯)也算紅:弱測試照過,漏列修正檔時失敗方向不是擋
severity: major
blocking: 是
引句:「修正其實動了三支檔、紀錄只列一支時,紅樹還帶著另外兩支的修正」
file: `scripts/lumos:6584`(`_spec_gate_verdict`:`verdict == "red"` 且 n 不是 0 就回 red,不分失敗是斷言還是匯入/收集錯)
file: `scripts/lumos:38495`(`_PYTEST_SUMMARY_RE` 把 `error` 跟 `failed` 一起加進 n)
1. 輸入 A(weak_import):修正在 `lib.py` 修 `norm` 並順手新增 `helper`;測試檔頂端 `from lib import norm, helper`,紀錄列的測試是 `def test_weak2(): assert True`。紅樹 `lib.py` 換回 → 測試檔收集時 ImportError → pytest `1 error ... Interrupted: 1 error during collection`、rc=2 → `_ran_count` n=3、`declared=1` → `_spec_gate_verdict` 判 red → 第 4 項 **PASS**。一支什麼都沒驗的測試過了先紅後綠。
2. 輸入 B(missing_file):修正動 `a.py`(新增 `clean`)與 `b.py`(改成呼叫 `clean`),紀錄只列 `a.py`;測試 `test_run_ok` 只驗 `run('a') == 'a'`(沒驗修正)。紅樹 `a.py` 換回、`b.py` 留修正後 → `from a import x, clean` 失敗 → 收集錯 → 判 red → **PASS**。快照引句那段說漏列「多半判修之前就通過,失敗方向是擋」,只對「漏列的是呼叫端」成立;漏列的是「被呼叫端以外那一支」(或修正刪掉的檔——第 87 行要求 `at` 的檔在修正後的提交裡,被刪的檔根本列不進 `fixed`、紅樹也還原不回來)時,紅樹是壞的、任何碰到那個模組的測試都紅,方向是放。
3. 重現:`/opt/homebrew/bin/python3 exp.py weak_import missing_file` → 兩行都是 `第4項 PASS`,紅樹 tail 都是 `Interrupted: 1 error during collection`。
4. 編譯型的棧更嚴重(未實測,依據是讀碼):swift/kotlin/C#/java/dart 的 `_ran_count` 讀不出支數(`count_re` 只有 python 有,`scripts/lumos:38487`),`_spec_gate_verdict(None, …, "red")` 照退出碼判 red;只要同一個測試 target 裡有任何一支測試引用修正新增的名字,紅樹整個 target 編譯失敗,紀錄列的**每一支**測試(含 `XCTAssertTrue(true)` 這種)都判紅、過。
5. 要改的地方(擇一,要寫進第 4 項):python 紅那邊要求摘要裡有 `failed`(收集錯 `error` 不算紅、判不過「修之前測試跑不起來,判不出是不是因為修正」);讀不出支數的棧照實標「紅可能是編譯失敗」並在輸出印紅樹 tail 讓人判;〈實務隱患〉「修正紀錄漏列檔」那段改寫成兩個方向都會發生。S4 補「弱測試+測試檔匯入修正新增的名字 → 回 1」。

## F3 新規則把「修正前會讓行程崩潰」的好修正判不過(`nesting`、`perf-memory` 兩類的典型症狀)
severity: major
blocking: 是
引句:「但讀得出支數的棧(像 python)在沒逾時卻讀不到支數時,當成」
file: `scripts/lumos:13976`(`_kill_run`:被訊號殺掉時 rc 是負數,例 -11)
1. 輸入(crash):`base` 的 `parse(depth)` 深度超過 1000 時在 C 層崩潰(實驗用 `ctypes.string_at(0)` 模擬 C 擴充 segfault;OOM 被系統 SIGKILL、`os._exit` 同型);修正改成丟 `ValueError`,測試 `with pytest.raises(ValueError): parse(5000)`——好修正、好測試。
2. 紅樹:pytest 行程 rc=-11 死掉,沒有摘要行 → `_ran_count` 回 `(None, False)`、沒逾時 → 照引句判「修之前選不到這支測試」→ 第 4 項 **FAIL**。
3. 重現:`/opt/homebrew/bin/python3 exp.py crash` → `第4項 FAIL`,紅樹 `rc_verdict: red`、`n: null`、`v: fail-nocount`;另跑 `_run_bound_tests` 直接看到 detail `rc=-11`。
4. 快照第 29 行的動機實例就有「修補造成深層巢狀當機」,固定類別清單也有 `nesting`、`perf-memory`;修卡死的「逾時算紅」補了,修崩潰的同一個形狀沒補。本 repo 自家 runner 先印「lumos 測試(N 案例)」再跑,所以本 repo 不中;中的是 pytest/unittest 消費專案(rtb 兩個工作樹都是 pytest)。
5. 要改的地方:比照逾時,紅樹 rc 是負數(被訊號砍)或 ≥128 時判紅、輸出標「崩潰算紅」;條款 S4 補這個情境。

## F4 同組多條 `fixed` 路徑共用一棵紅樹與同一支測試:只走其中一條路徑的測試也讓整組過——正是動機裡「JSON 輸出路徑繞過修補」那種
severity: major
blocking: 是
引句:「路徑狀態兩種:`fixed`=這條路徑這次修了,要列守著它的測試」
1. 輸入(two_paths):`output-path` 類一組,`paths` 兩條:`out_text.py:render`(fixed,tests `[test_text_escape]`)、`out_json.py:render`(fixed,tests `[test_text_escape]`);`test_text_escape` 只呼叫文字輸出。
2. 紅樹把兩支一起換回 → 測試因文字路徑紅 → 綠樹綠 → **PASS**。JSON 路徑沒有任何測試守著,紀錄卻說它有。
3. 重現:`/opt/homebrew/bin/python3 exp.py two_paths` → `第4項 PASS`。
4. 動機(第 29 行)第一個實例是「JSON 輸出路徑繞過修補」,全域規則也是「每組替所有相似的程式路徑各寫一支先紅的測試」;紀錄格式把測試掛在每條路徑底下,判法卻只驗「所有修正一起拿掉時測試紅」,每條路徑跟它的測試之間的對應沒有任何一步驗。同理也會跨組:G1 的弱測試因 G2 的修正被換回而紅。
5. 要改的地方:逐條 `fixed` 路徑驗——只換回「那條路徑的檔」(同檔多條路徑時至少逐檔)的紅樹裡,它列的測試要紅;成本是紅樹數=不同 `fixed` 檔數,寫進〈實務隱患〉的時間估計。做不到就把這個天花板寫明,S4 加反向情境。

## F5 `no_red_reason` 沒有任何機械前提:真修程式的組寫四個字就跳過紅那邊
severity: major
blocking: 是
引句:「拿掉修正就等於拿掉測試時寫(至少四個字、要有實字);寫了這組的測試只跑綠那邊、不跑紅那邊」
1. 輸入:一組 `fixed` 是 `scripts/lumos:_kill_run`,tests `[t_weak]`(弱測試),寫 `"no_red_reason": "測試補強"`。快照只驗字數與實字,不驗「這組的修正全在測試裡」→ 只跑綠那邊 → 第 4 項過。F2、F4 那幾道防線對這組全部失效,只剩事後統計。
2. 有一條不靠猜路徑、純機械的前提可以加:寫了 `no_red_reason` 的組,每條 `fixed` 路徑 `at` 的函式段必須就是這組 `tests` 裡的某一支(「修正就是測試本身」),否則第 1 項不過。本 repo 的情境(`scripts/test_lumos.py:t_old` 補斷言、tests `[t_old]`)照過;上面的輸入被擋。
3. S4 現在只寫「寫了 `no_red_reason` 的組只跑綠那邊」,沒有反向情境;補上述前提與「程式路徑+`no_red_reason` → 回 1」。

## F6 兩棵樹讀的是提交裡的 `.lumos/config.json`:設定檔沒進版控的專案永遠不過;設定從哪讀也沒寫
severity: major
blocking: 是
引句:「主工作目錄只讀審查帳、治理帳與修正紀錄」
file: `scripts/lumos:38606`(`_run_bound_tests` 第一行 `load_platforms(repo_root)`,讀 `repo_root/.lumos/config.json`)
file: `scripts/lumos:4811`(`load_platforms`:沒有設定檔 → legacy `csharp-xunit`、`run_cmd` None)
1. `_run_bound_tests(綠樹, …)`、`_platform_test_index(綠樹)`、`_bound_tests_check(綠樹, …)` 全部從**工作樹裡**讀設定。設定檔沒進版控 → 樹裡沒有 → `run_cmd` None → `_run_bound_tests` 回 `(None, "這個專案沒設測試指令…")`,第 5 項回 `no-config`。快照第 4 項只寫了每支結果怎麼判,沒寫 `_run_bound_tests` 整個回 None 時怎麼判;實作只能判不過 → 每次 `warned`。
2. 重現:`/opt/homebrew/bin/python3 exp.py untracked_cfg`(設定檔放進 `.git/info/exclude`)→ `第4項 FAIL(_run_bound_tests 回 None)`,兩棵樹的 err 都是「這個專案沒設測試指令」。
3. 實際分布:本機 18 個有 `.lumos/config.json` 的專案裡,`~/JennyOnePlus`、`~/Stockify_BackEnd` 兩個沒進版控(`git ls-files --error-unmatch` 查)。guard kill(`scripts/lumos:14132` 從主 repo `load_platforms`)、推送前合約測試閘都讀主工作目錄的設定,所以這兩個專案現在跑得動,接入修正關卡才會壞。
4. 同一份設定被拆兩處讀:`fix_check.budget_sec`、`link_dirs`、平台根先決條件(新的設定讀取函式)讀主工作目錄;`run_cmd`、平台、測試索引讀樹。剛改了 `run_cmd` 沒提交時兩邊不一致,快照只說會印提醒。
5. 要改的地方:明寫「平台設定(`load_platforms` 的輸入)一律取主工作目錄那份、平台根換成樹」(`load_platforms` 已經接受 `cfg=` 參數,`_run_bound_tests` 要多開一個傳設定的入口),或明寫要求設定檔進版控、沒進版控回 2 並說明;第 4 項補「`_run_bound_tests` 回 None → 不過並印原因」。

## F7 S13 釘的「guard kill 多平台時測試在平台根跑」不是現況:現在跑在工作樹頂層
severity: major
blocking: 是
引句:「多平台時 guard kill 應在平台所在的 repo 建樹、測試在平台根跑,跟抽函式之前一樣」
file: `scripts/lumos:14206`(`git -C <平台根> worktree add --detach wt`)
file: `scripts/lumos:14227`(`_kill_run(cmd, wt, …)`,cwd 是工作樹頂層,沒接平台根子路徑)
1. 實測:多平台設定 `{"py": {"profile": "python", "root": "sub", "run_cmd": "pwd >> LOG; python3 test_guard.py # {method}"}}`,`sub/` 裡放 `prod.py`、`test_guard.py`,配方 `file: sub/prod.py`。跑 `lumos guard kill Systems/Limit --json` → `pwd.log` 記到 `/private/var/folders/…/lumos-kill-i79sdi8_/wt`(不是 `…/wt/sub`),baseline `can't open file '…/wt/test_guard.py'`、判 `abort`。重現目錄 `fg-r3-work-正確性-opus/gk/`。
2. 所以快照的「先補多平台路徑測試、先綠、抽完照綠」照 S13 字面寫的測試,抽函式之前就是紅的;要嘛改 guard kill 的 cwd(跟「guard kill 行為不變」打架,也會換掉那些照頂層寫 `run_cmd` 的專案的行為),要嘛測試照現況寫、條款文字是錯的。第 137 行「guard kill 傳平台所在 repo 的頂層,照它現在的 `-C`」也不符現況:現在 `-C` 傳的是平台根。
3. 同一個平台設定,`_run_bound_tests` 在「樹+平台根」跑(`scripts/lumos:38635` 的 `root = str(pentry.get("root") or repo_root)`),guard kill 在樹頂層跑——兩者本來就不一樣。S13 要改成釘現況(「測試在工作樹頂層跑」),guard kill 跟平台根不一致另開 Issue;修正關卡第 4 項照 `_run_bound_tests` 的平台根跑,不受影響。

## F8 「讀得出支數卻讀不到 → 判不過」這條新規則沒有條款釘住;拿掉它,紅樹裡根本不存在的測試會被判紅、過
severity: major
blocking: 是
引句:「在綠樹失敗或一支都沒跑到時應回 1」
1. S4 這句只講綠樹。紅那邊的新規則(第 115 行)不在任何條款裡。實作漏了它時,`_spec_gate_verdict` 對「rc≠0、n=None」直接回 red:實測 `L._spec_gate_verdict(None, False, "red", "rc=1 ✗ -k 選中 0 個測試", declared=0)` → `('red', '這棧還讀不出支數,只印有沒有跑過')`。
2. 觸發輸入:本 repo 自家 runner 在 `-k` 選不到測試時印 `✗ -k '…' 選中 0 個測試`、rc=1、沒有「lumos 測試(N 案例)」那行(實測 `scripts/test_lumos.py -k t_zzz_no_such` → `ran_count: (None, False)`)。紅樹裡測試不存在(F1 的情境、或程式跟測試同檔)時,沒有這條規則就是 red → 過。
3. 要改的地方:S4 加「紅樹選不到這支測試(本 repo runner 印選中 0 個、pytest 0 selected)→ 回 1 並寫修之前選不到」,跟 F3 的「崩潰算紅」一起寫成同一條,釘住兩個方向。

## F9 「逾時算紅」不分「測試開始跑之後卡住」與「測試還沒開始就逾時」
severity: minor
blocking: 否
引句:「其中因逾時判紅的(修卡死類的修正,修之前跑不完)照樣算過」
1. 紅樹逾時算紅的條件只看 `_run_bound_tests` 的 detail 是不是「超時」。兩種不是「修卡死」的逾時也會走到這裡:(a)編譯型的棧在全新工作樹冷建置(xcodebuild 的 DerivedData 依專案路徑分,新路徑等於從頭建;guard kill 的 baseline 因此用 `max(600, floor)`,`scripts/lumos:14227`,而 `_run_bound_tests` 每支 180 秒);(b)第 6 項把單支逾時截成「剩下的時間」。(b) 之後剩不到 300 秒會讓第 5 項判不過,整次照樣回 1;(a) 在綠樹也冷建置時綠那邊先不過。⚠ 未實測,交編排者判要不要在輸出裡把「逾時算紅」的 tail 附上(看得出測試有沒有開始跑),讓人自己判。

## F10 `loop next` 只比提交:通過之後工作目錄再改程式(沒提交)不會提醒
severity: minor
blocking: 否
引句:「事件的 `head_sha` 跟現在的 `HEAD` 之間沒有簿記檔以外的檔案改動」
1. 派工詞問的「拿掉乾淨先決條件後,沒提交的修正能不能被判過」:`fix-check` 本身沒有這條路——修正沒提交時,`fixed` 的檔在 `base..修正後` 沒改動(第 1 項不過),或綠樹沒有修正(綠那邊不過);新測試沒提交時第 3 項不過。實驗與讀碼都對得上。
2. 剩下的窗口在 `loop next`:C1 跑 `fix-check` 通過 → 工作目錄再改程式、沒提交 → `loop next` 比 `C1..HEAD` 沒差、不提醒。凍結材料也是 `merge-base..HEAD`(手冊第 1 步),下一輪審的跟修正關卡驗的同一份,所以一般輪次沒有漏;漏在快照自己強調的「到上限要推之前」——人改完直接提交推送,沒人再跑 `loop next`。可以在 `loop next` 的提醒條件外加一行只印、不算狀態的「工作目錄有簿記檔以外沒提交的改動,通過紀錄不涵蓋它們」(同一個 `git status --porcelain -z` 判法,`fix-check` 已經有)。

## F11 `run_cmd` 自己就會回到主工作目錄的虛擬環境,「依賴資料夾預設不連」擋不到這條路
severity: minor
blocking: 否
引句:「依賴資料夾預設不連:`.lumos/config.json` 的 `fix_check.link_dirs`」
1. rtb 兩個工作樹的 `run_cmd` 是 `"$(git rev-parse --git-common-dir)/../.venv/bin/python" -m pytest tests -k {method} -q`;在隔離工作樹裡 `--git-common-dir` 指回主 repo 的 `.git`,用的是主工作目錄的 `.venv`。那個 venv 裡要是有專案的可編輯安裝,紅樹就載到主工作目錄修正後的程式(第 2 輪審查實測過的那個失真),`link_dirs` 設不設都一樣。
2. 現在不中:rtb 的 `.venv` 沒有 `.pth`/可編輯安裝,pytest 用 `pythonpath = ["src"]`(相對工作樹)。〈實務隱患〉「依賴資料夾」那段只把風險掛在 `link_dirs` 上,補一句「測試指令自己回到主工作目錄找依賴的也一樣」,回頭條件照那段的「第一個宣告的專案接入時實測一次紅樹載到哪一份」。

## 逐節核對

- frontmatter/白話/依據/PRIOR-ART/RETIRE-IF/REVISIT:已讀,無 finding(依據第 29 行的實例被 F3、F4 引用)。引用的函式 `_gate_event_or_warn`、`_KNOWN_GATES`、`_GOV_FIELD_TYPES`、`_drift_jsonl_parse`、`_panel_retired_for`、`_drift_config`、`_lint_link_deps`、`_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 在 clone 裡都找得到。
- 名詞:「一支測試的判法」與程式對得上(`scripts/lumos:6564`、`6584`、`38498`、`38606`);放寬宣告集從 `_platform_test_index(樹)` 的 `loose_for` → `_loose_declared_methods(平台根, profile)` 來,本 repo 的 `test.method_regex` 錨在行首、`.py` → 走 `_py_declared_methods`,在樹上算,對得上。
- 範圍:已讀,無 finding。
- 修正紀錄:F1、F2、F4、F5。
- `fix-check`:F1–F3、F6、F8、F9。平台根:legacy 時 `root = repo_root`(傳樹就是樹),多平台時 `(樹 / root).resolve()`,都在樹裡,對得上。本 repo runner 先印「lumos 測試(N 案例)」再跑,逾時、崩潰、斷言錯都讀得到 n=1;只有「選中 0 個」讀不到(F8 要釘住的那條)。
- 中斷與殘骸:已讀,無 finding。
- 共用的隔離工作樹:F7。
- `loop next`:F10;狀態集合 `plant-canary`/`gate-pending`/`converged`/`cap-reached`/`escalate` 在 `cmd_loop_next` 裡都找得到,`converged` 回 0、其餘回 1。
- `canary record --regression-set`、第 2 步、上線、跟提案不同、回退:已讀,無 finding。
- 條款:S4 缺 F1、F2、F3、F5、F8 的情境;S13 文字跟現況相反(F7)。其餘條款跟做法對得上。
- 實務隱患:F2(「漏列修正檔」的方向寫錯)、F11。

## 實務隱患鏡頭

- 正確性/假綠假紅:F1–F5、F8(本報告主體)。
- 設定與環境:F6、F11。
- 時間:F9;其他照快照的估計,沒有新發現。
- 並行會談:全部在樹裡跑,主工作目錄只讀;F10 是唯一剩下的窗口。
- 資料完整性(帳本):讀端去重鍵確實含 `token`(`scripts/lumos:7699`),治理帳轉換現在只對 canary/blocked 與 code-loop 表態吐 token(`scripts/lumos:7649`),快照要補 `fix-check` 這一支,對得上。
- 金流、對外送出、不可逆:無——只在本機建樹跑測試、只追加帳本。

最高等級:major,blocking 共 8 條
