severity: minor

## F1 新增的判定分支用 `pass` 當空分支續接,跟本檔既有的 `pass` 用法(只用在 except 吞例外)不一致

severity: minor
blocking: no

觀察到什麼:`_spec_gate_verdict` 新增的判斷式寫成

引句:「        if declared == 1:」

引句:「            pass」

也就是「n>=2 時,若 declared==1 就用 pass 空過、否則才 return weak」。查了全檔(`scripts/lumos`)所有 56 處 `pass`,抽樣前 10 處(559/654/842/971/1553/1607/1649/2231/4337/4663 行)全部是 `except ...: pass`(靜默吞例外的既有慣例),沒有一處是像這裡這樣,在一般判定邏輯的 `if` 分支裡用 `pass` 當「不做事、續往下走」的寫法。`_spec_gate_verdict` 本身原本(以及新增後的其餘部分)全是扁平的 `if 條件: return ...` 鏈(第 75、77、79、81、82 行),沒有巢狀 if/else。這處新增是全檔唯一一個「`if cond: pass else: return`」形狀,跟鄰近程式碼、也跟全檔 `pass` 的既有用法都不一樣。

怎麼重現:讀 `scripts/lumos` 第 5649-5661 行(`_spec_gate_verdict`)即可看到,不需要跑起來重現,是靜態寫法比對。

為什麼是 bug 而不是風格:這條本身不影響行為正確性(邏輯等價於把條件收斂成 `if n is not None and n >= 2 and declared != 1:` 才 return weak),純屬「跟既有慣例不一致」——這正是本鏡頭要抓的東西,不是功能缺陷,歸類 minor、不擋。

## 其餘已驗過、判定一致,沒有發現

- **三個呼叫點取 `methods_for` 的來源一致**:`cmd_spec_gate`(`scripts/lumos:5842`)、`_spec_gate_regress`(`scripts/lumos:5715` 簽章不變,原本就收 `methods_for`)、`_spec_gate_push_one`(`scripts/lumos:6098` 由 `idx` 拆出)三處的 `methods_for` 全部同源自 `_platform_test_index()`(`scripts/lumos:10381-10403`),用 `grep -n "methods_for" scripts/lumos` 逐一追過,三處都間接指回同一支函式,沒有「有的用 methods_for、有的用別的來源」的情況。
- **新參數不破壞既有呼叫端相容性**:`_spec_gate_verdict` 新參數 `declared=None` 是有預設值的 keyword,舊呼叫寫法不用改也能跑;`_spec_gate_run_clauses` 雖然是新增「必填」位置參數 `methods_for`,但用 `grep -n "_spec_gate_run_clauses" scripts/lumos` 查過,全檔唯一呼叫點在 `cmd_spec_gate`(`scripts/lumos:5842`),同一個 diff 裡已經一起改好,沒有漏改的第二個呼叫點;另外用 `grep -rn "_spec_gate_run_clauses\|_spec_gate_verdict(" --include="*.py" .`(排除 scripts/lumos、scripts/test_lumos.py 本身)查過 repo 全部 .py,沒有第三方白箱直呼這兩支函式。
- **測試 fixture 改動沒有動到既有測試的語意**:`_mk_spec_gate_repo` 補了 `t_multi_extra`(名字含 `t_multi`)後,既有測試 `t_spec_gate_multi_ran_is_weak`(`scripts/test_lumos.py:44586-44590`)驗的仍是「篩選匹配到 2 支 → 印測試名要唯一」,而且是「兩支都是真的宣告的測試」而不是像改動前那樣單靠假 runner 回報數字、程式裡其實只有一支——這處補的第二支測試讓「匹配到兩支」名副其實,語意沒有被沖淡,反而更貼近它的敘述。`t_spec_gate_twoway_weak_blocks`(`scripts/test_lumos.py:44984-44993`)也還是用 `t_multi` 驗弱證據(現在 declared=2,不等於 1,照舊落入「測試名要唯一」→ weak → 印「弱證據」),沒被新邏輯改變判定結果。三支相關測試(`t_spec_gate_multi_ran_is_weak`、`t_spec_gate_parametrized_is_not_weak`、`t_spec_gate_twoway_weak_blocks`)已用 `python3 scripts/test_lumos.py -k <關鍵字>` 實際跑過,全綠(分別 1/2/4 passed, 0 failed)。
- **新函式命名/位置**:`_spec_gate_declared` 沿用全檔 `_spec_gate_*` 前綴慣例,插在 `_spec_gate_load` 之後、`_spec_gate_verdict` 之前(它的計算結果餵給 `_spec_gate_verdict`),跟檔案裡「小判定 helper 緊鄰在它服務的判定函式前面」的排列方式一致。
- **註解密度**:`_spec_gate_declared` 的 docstring 帶 ★…★ 標記、引用回報日期與出處(2026-09-22),乍看比鄰近函式(多半一行)密。但用 `grep -n '2026-0[0-9]-[0-9][0-9]'` 掃過全檔,找到多處既有函式也是這種「帶日期、帶代碼審輪次/回報出處的多行敘事型 docstring」(例如 `scripts/lumos:3177`「兩段式讀法(2026-09-16 代碼審 r2)」、`scripts/lumos:3262`「★為什麼需要★(2026-09-07 代碼審 r1 通才席實測)」、`scripts/lumos:3327`「黏成一串沒斷開就幾乎必定 0 筆(Landmark 2026-08-11 實測…)」),這種密度其實是本檔對「有踩坑出處」函式的既有寫法,不是新引入的風格。
