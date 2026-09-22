severity: major

## F1 機械守衛本身用逐行正則掃呼叫點,跟同檔(甚至同一份 patch)已經確立的「語法剖析」做法不一致
severity: major
blocking: yes

觀察到什麼:這份 patch 新增的守衛測試 `t_platform_index_consumers_all_unpack_same_arity`,判斷「哪些行在解構 `_platform_test_index` 的回傳值、解了幾個」用的是逐行正則:
引句:「mm = _re.match(r"^\s*([\w, ]+?)\s*=\s*(?:m\.)?_platform_test_index\(", ln)」

但同一份 patch 裡,新增的 `_py_declared_methods`(生產碼,同樣是「掃原始碼找出真宣告」的問題)明確拒絕了正則,理由寫在它自己的 docstring 裡:
引句:「★不要用放寬的正則去掃★(代碼審 r2 通才席 blocker):Python 的掃描刻意不剝字串,」
(該函式接著解釋:放寬的正則會把 docstring/字串裡「長得像宣告」的內容當真,實測本 repo 自己的測試檔多算 148 個;改用 `ast.parse` 才靠語法樹分辨字串跟真宣告。)

`scripts/test_lumos.py` 本身也已經有現成、更精確的先例可以直接借:
- `t_nodehome_foreign_ref_uses_impact_extraction`(`scripts/test_lumos.py:11141` 起)用 `ast.parse`+`ast.walk` 逐函式收集呼叫的名字集合,拿來驗證多個呼叫端都走同一支共用抽取函式——跟這支新守衛「驗證多個呼叫端有沒有用同一種方式處理 `_platform_test_index`」是同一類問題。
- `_text_git_calls_missing_errors`(`scripts/test_lumos.py:11133` 起)更進一步:用 `ast.Assign` 追蹤變數在同一函式內被賦值成什麼、支援串接、迴圈目標等,並且明講「看不出來就當成可能是 git,一樣要帶」——遇到剖不清楚的情況選保守(當成可疑),而不是悄悄跳過。

新守衛完全沒有用 `ast`,而是逐行套正則比對賦值目標字串。這造成的具體盲點(跟這輪派工單第 29 行點名的攻擊方向逐一對上):
- **多行解構**:`(split, default,\n methods_for, ...) = _platform_test_index(rr)` 這種把 target 拆成兩行的寫法,`^\s*([\w, ]+?)\s*=\s*` 是逐行 match、且是 `re.match`(錨在行首),第一行只會比對到 `(split, default,` 這串,而它前面帶了左括號 `(`,不在 `[\w, ]` 字元類裡,整條直接不 match——這支解構會被靜默漏檢。
- **括號包起來的 tuple target**:`(pdata, split, default, methods_for, hay_for, loose_for) = _platform_test_index(rr)` 同理,開頭的 `(` 讓 `[\w, ]+?` 群組配不到,整行被跳過,不會被算進 `bad`。
- **`*rest` 星號解構**:`*` 也不在 `[\w, ]` 字元類裡,同樣會讓整行比對失敗而被跳過,不是被「抓到但誤判支數」,是完全不出現在 `bad` 清單裡。
- **`a, b = c = 索引(...)`(連鎖賦值)**:`[\w, ]+?` 不含 `=`,引擎只能把 `a, b ` 當成第一段候選,之後必須緊接 `_platform_test_index(`,但實際緊接的是 `c`,匹配失敗;`re.match` 又錨死在行首,不會再往右找到 `c = _platform_test_index(`,整行同樣悄悄漏掉。
- **存進 dict/list 再取用**、**lambda 或 f-string 裡呼叫**:都不是「某一行等號左邊直接是逗號分隔的識別字清單」這個形狀,天生在這支逐行正則的偵測範圍外。

重現方式:在 `scripts/lumos` 隨便找一個目前用 `_, split, default, methods_for, hay_for, loose_for = _platform_test_index(rr)` 的呼叫點,手動改寫成上述任一形狀(例如加括號,或拆成兩行)並且只解出 5 個值(漏掉 `loose_for`)——因為那一行從一開始就配不到 `holders`/直接解構兩條正則的任何一條,`bad` 不會收到任何記錄,`check("② 每一處解構的個數都對得上", bad == [], ...)` 照樣綠燈。

為什麼是 bug 而不是風格:這支守衛存在的唯一理由就是這份 patch 自己講的——同一族的「加欄位漏改消費點」錯誤已經連冒三次,要讓機器接手記。但它選的偵測手法在同一份 diff、同一個檔案裡,已經有更精確、經過代碼審驗證過的 ast 做法可以直接照抄,卻改用一種連基本的多行/括號/連鎖賦值都會漏檢的逐行正則。這不是「兩種寫法都合理、挑了比較差的一種」的風格問題,而是這份 patch 自己的推理(★不要用放寬的正則去掃★)沒有被套用到它自己新增的守衛測試上——守衛本身正好會重蹈它試圖防止的那個假綠模式(規則存在,但寫法本身留了洞讓它掃不到)。

## F2 守衛只掃兩份寫死的來源(scripts/lumos + test_lumos.py),沒有走本檔已有的「全 repo 掃描」機制
severity: major
blocking: no

觀察到什麼:
引句:「    for label, text in (("主程式", src), ("測試檔", tst)):」

`src`/`tst` 是分別對 `GRAPHCTL`(`scripts/lumos`)與 `__file__`(`scripts/test_lumos.py`)各自 `read_text` 出來的兩份字串,守衛只走這兩個 label。目前 repo 內確實只有這兩支檔案呼叫 `_platform_test_index`(用 `grep -rn "_platform_test_index"` 核對過,除了這兩支檔沒有第三處),所以現況下不會漏檢。

但這是寫死的兩份「來源列表」,而不是像本檔既有的多檔一致性守衛那樣走一個可重用、可擴充的掃描面:例如 `t_metric_criteria_drift_guard`(`scripts/test_lumos.py:32889`)的「引用點漂移」段落是先定義一個 `ALLOWED` 集合再走一個共用的 `_scannable()` helper 去掃,新增允許的來源檔只要加進集合;`t_precommit_whitelist_drift_guard`(`scripts/test_lumos.py:3594`)同樣是對照多份清單、且註解明講「三份清單」要逐一對齊,不是寫死兩個變數名。這份 patch 自己在生產碼裡也才剛加了 `_walk_test_files`(★走檔只有這一份★,見同份 patch 的 `+def _walk_test_files`)這個原則——理由正是「兩邊各寫一份 os.walk,哪天檔案篩選改了只改一邊,兩份看到的檔就不一樣,而差異沒有東西會翻紅」——這條原則同樣適用在這支守衛上:若未來有第三個消費者(例如 governance/ 底下的腳本,或另一支 hook)直接 import `scripts/lumos` 並呼叫 `_platform_test_index`,這支守衛看不到那支檔,漏改照樣悄悄放行。

為什麼是 bug 而不是風格:這正是派工單第 30 行點名的攻擊方向(「守衛只掃兩個檔，漏掉別的檔會怎樣」)。目前沒有第三個消費者,所以不會立即翻紅或誤判,故不列 blocking;但架構上跟本檔既有「消費面清單要能擴充、不要散落硬編碼兩個變數」的慣例不一致,建議至少留一行註解說明「目前只有這兩支消費它,新增消費者要記得把這支守衛也拉進來掃」,或比照 `t_metric_criteria_drift_guard` 的 `ALLOWED` 集合寫法做成可擴充清單。

## F3 測試命名沒有沿用本檔既有的「漂移守衛」命名慣例
severity: minor
blocking: no

觀察到什麼:
引句:「def t_platform_index_consumers_all_unpack_same_arity():」

本檔同一類「自己掃原始碼、驗跨呼叫點/跨檔一致性」的守衛測試,一律用 `_drift` 或 `_drift_guard` 當名字尾綴,例如 `t_status_tag_drift_guard`(`scripts/test_lumos.py:2213`)、`t_precommit_whitelist_drift_guard`(`scripts/test_lumos.py:3594`)、`t_gov_stats_gate_drift`(`scripts/test_lumos.py:6193`)、`t_fold_value_drift`(`scripts/test_lumos.py:9801`)、`t_docs_enumeration_drift`(`scripts/test_lumos.py:24366`)、`t_metric_criteria_drift_guard`(`scripts/test_lumos.py:32889`)。這個慣例不只是命名習慣,圖譜筆記裡也是照這個名字模式在互相指涉的,例如 `docs/lumos-toolchain-knowledge/Systems/delguard.md:25` 寫「漂移由 t_precommit_whitelist_drift_guard 釘第三份清單」、`docs/lumos-toolchain-knowledge/Projects/loop數據收集_計劃.md:127` 寫「漂移守衛測試(名=`t_metric_criteria_drift_guard`)」。

新守衛做的事(掃原始碼、驗「加欄位時每個消費點都要解到一樣多個值」這個結構不變量)跟上述測試是同一類,卻取名 `t_platform_index_consumers_all_unpack_same_arity`,不含 `drift` 或 `guard`。這會讓未來要用 `grep _drift_guard` 或在圖譜筆記裡按這個名字模式找「這裡有哪些漂移守衛」的人漏看這一支。

為什麼是 bug 而不是風格:CLAUDE.md 的紀律要求「每支檔有家」「開頭欄位用指令改」等機械化慣例,本檔對這類守衛測試也已經形成了可被查詢、可被圖譜筆記引用的命名模式;破格命名會削弱這個可查詢性,但不影響這支測試本身的判定邏輯是否正確,故列 minor、不擋。

---

## 審過但沒發現問題的路徑(供收貨核對)
- 前三輪折入內容在這輪是否被改壞:核對了 `_spec_gate_verdict` 的 `declared == 1` 分支(patch 第 241-251 行區塊),邏輯與行為在這輪只是把 `if/else` 收成一行 `and declared != 1`,語意沒變;`_platform_test_index` 從五個值擴成六個值後,所有既有呼叫點(`run_doctor`、`_clause_bindings_for`、`classify_invariants`、`cmd_archive`、`_bound_tests_for_diff`、`_dispositions_check_test`、`_spec_gate_prepare`/`_spec_gate_push_scan`)在這份 patch 裡都已同步改成六值解構,沒有發現漏改的呼叫點(這點本身也正是這支新守衛想機械化驗證的東西,但我是用 `grep -n "_platform_test_index("` 全檔核對後人工過一遍確認的,不是只信任這支守衛)。
- 這輪相對第三輪的三項改動(補漏改點、新增守衛、修守衛第一版行尾錨死的假綠)都能在 patch 裡對到:`t_python_profile_multiplatform` 補了 `_, _, _, methods_for, _, _loose = m._platform_test_index(root)`(第 643 行);守衛測試在第 732-768 行;守衛裡「行尾允許有註解」的 `(?:#.*)?$` 在第 755/763 行都已經存在。
