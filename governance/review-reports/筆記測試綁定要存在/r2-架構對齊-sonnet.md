severity: major

# r2 架構對齊-sonnet 報告

## 四問

**1. 分層與依賴方向。** 大體對齊。note-shape 這一層(`cmd_note_shape`)去呼叫 `_platform_test_index` 與 `_classify_test_refs`,方向跟 doctor Check T、修正關卡一樣是「閘層讀共用判定零件」,沒有反向依賴。「第三個呼叫者」的說法屬實:現有兩個是修正關卡第 3 項與 `_bound_tests_for_diff`。doctor S20 讀共用抽取器,跟 S17–S19 共用 `_note_summary_entries` 的形狀一致。「摘要接回續行抽成吃全文的一支兩邊共用」也對:`_note_summary_entries` 吃 Env 筆記物件、`_ns_summary_logical` 吃全文,兩層本來就各讀各的,抽一支共用不違反方向。沒有跨層直呼。file: `scripts/lumos:12366`、`scripts/lumos:40315`、`scripts/lumos:3513-3524`。

**2. 命名與錯誤處理。** 大體對齊,有三處細節不齊(F4–F6,皆 minor)。已對齊的:`_note_shape_test_refs_parse` 照 `_note_shape_slots_parse`(壞值照 block 並提醒、總開關 off 整組不跑、warn 只提醒);fail-open 跳過並印一行原因,同 `_bound_tests_for_diff` 的 `no-config:` 與 cmd_note_shape 既有的「跳過(fail-open)」;doctor 段用 `warn_soft`、不寫帳、`--verbose` 全列,同 S17–S19;S20 放在 S19 之後、S8 之前,同現有「軟段截斷視窗」的位置紀律。file: `scripts/lumos:28113-28145`、`scripts/lumos:2513-2548`、`scripts/lumos:1354-1369`。

**3. 第二種做法。** 有兩處(F1、F2,major)。①「到被檢查版本的測試檔整字複查」專案已有同功能零件 `_dispositions_check_test`,計劃沒引用、也沒說為何不用;②自寫寬鬆正則抽 `[test:]` 跟格子的 `slot_parse` 是同一套括號文法的第二份實作。另有一處「新」的定義跟格子既有比對法分叉(F3,minor)。

**4. 落點。** 三個落點都對得上:`Systems/筆記內容閘` 的 about_code 含 `scripts/lumos` 且已記 note-shape 與格子;`Systems/lumos-cli-read` 已有 doctor S16–S19 的 WHY 行,S20 寫那裡順;`Systems/bound-tests-gate` 已有 `_classify_test_refs` 抽取的 WHY 行,「多一個呼叫者」寫那裡順。但複查若照 F1 改用 `_dispositions_check_test`,它不在 bound-tests-gate 也不在另外兩篇的說明裡(在表態那一族),落點清單要補它的家。file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:17`、`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:14`、`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:104`。

## Findings

## F1 「到被檢查版本整字複查」是專案已有的零件,計劃卻當成新寫,而且少了現有零件的範圍過濾
severity: major
blocking: 是
引句:「新寫的只有:吃全文的名稱次數抽取、到被檢查版本的測試檔整字複查」
file: `scripts/lumos:41244-41290`(`_dispositions_check_test`)
file: `scripts/lumos:34808`(`_delguard_confidence`,另一處 `git grep --cached -w -F`)
file: `scripts/lumos:6480`(`_test_exists_before`)

1. 專案已有同功能做法:`_dispositions_check_test` 對「表態的測試錨點」做兩道——工作樹的 `methods_for` 判存在,加對推送版本 `git grep -w -F -q -e 名稱 at_sha -- <路徑規格>`。這跟計劃〈做法〉3 的「`_classify_test_refs`(工作目錄)+ 到被檢查版本 `git grep -w -F`」是同一個形狀,連 `-w -F` 都一樣。計劃的 PRIOR-ART 把複查列為「新寫的」,沒列這支、也沒說為何不用。
2. 差異不是裝飾:現有零件的路徑規格只掃該平台 profile 的測試副檔名(`:(glob){根}/**/*{ext}`),並排除 `:(exclude)docs/**`、`:(exclude)governance/**`;排除原因寫在註解裡(r1 外家 finder f3:治理帳與筆記本身寫著測試名,樹裡就找得到,冒充已提交的測試)。計劃〈做法〉3 只寫「各平台根下的測試檔」,沒有副檔名過濾、沒有排除知識庫。
3. 壞在哪(具體場景):計劃自己承認平台根常是 repo 根。新加一條 `[test:t_ghost]`,名稱只在這篇筆記裡出現,複查 grep 被檢查版本(提交索引或終點)的範圍若涵蓋筆記,就會命中筆記自己 → 複查說「有」、`_classify_test_refs` 說「沒有」→ 計劃規定「說法不同不擋」→ 新加的壞名字永遠過關,整條規則形同虛設。
4. 最小實驗:在 negguard repo,名稱 `t_note_shape_test_refs_new_names` 只出現在筆記與審查文件裡,沒有測試:
   `git -C <repo> grep -w -F -q -e t_note_shape_test_refs_new_names HEAD --` → `rc=0`(命中 docs 與 governance 下的檔,例:`docs/.canary-log.jsonl`、計劃筆記)。
   加上現有零件的過濾 `-- ':(glob)**/*.py' ':(exclude)docs/**' ':(exclude)governance/**'` → `rc2=1`(找不到)。
   同一個名稱,有沒有過濾差一個判定。
5. 對齊做法:複查直接沿用 `_dispositions_check_test` 的路徑規格(抽出「平台根+副檔名+排除 docs/governance 的路徑規格」成共用函式,或直接呼叫它);「兩邊都說沒有才算指不到」的合併邏輯留在新規則這一層。PRIOR-ART 要補名這支,落點清單要補它的家。

## F2 自寫寬鬆正則抽 `[test:]`,是格子 `slot_parse` 括號文法的第二份實作
severity: major
blocking: 是
引句:「要同時吃摘要與正文、又要對齊格子認得的寫法」
file: `scripts/lumos:3764-3794`(`slot_parse`)
file: `scripts/lumos:3745-3750`(`_SLOT_KEYS`、`_SLOT_CANON`、`_SLOT_KEY_RE`)
file: `scripts/lumos:3529-3535`(`_slot_summary_entries`,摘要限定在呼叫端)
file: `scripts/lumos:2366-2380`(S5 註解:「同一件事兩套算法一定會分岔」)

1. 計劃〈名詞〉要的文法——鍵不分大小寫、半形或全形冒號、方括號內外空白、整個方括號落在反引號裡不算、反引號沒閉合時到行尾不算——逐項就是 `slot_parse` 現成在做的事(`_SLOT_KEY_RE` 認 `[:：]` 與前後空白、`_SLOT_CANON` 不分大小寫、成對反引號整段跳過、不成對的反引號到行尾當正文)。〈做法〉9 又要把 `test-gone` 登記進 `_SLOT_KEYS`,所以 `slot_parse` 本來就會抽到 `test` 與 `test-gone` 兩個鍵。
2. 計劃不用它的理由是「只吃摘要條目」,但這是呼叫端(`_slot_summary_entries`)的限制,不是 `slot_parse` 的:它吃任一段字串(「前綴冒號後面的字」)。正文的實體行也可以丟進去(行首去掉列表符號後整行當 rest)。
3. 壞在哪:兩套文法並存,之後格子改一個寫法(例如鍵表加別名、括號層數規則改),格子認得、本規則不認(或反過來),就會出現「格子說這行寫了 `[test:X]`、本規則說沒有」的分歧,而且沒有任何東西會翻紅。這正是 S5 註解自己寫的教訓。
4. 唯一真的多出來的部分是「同一方括號用全形逗號列多支」:`invariant_test_refs` 只切半形逗號,所以逗號切分要補,這是在 `slot_parse` 的值上加一層切分,不需要另一套括號掃描。
5. 對齊做法:`_note_test_name_counts` 對每一條(接回後的摘要條目、正文實體行)呼叫 `slot_parse`,從 `fields` 取 `test`/`test-gone` 的值再切逗號、剝反引號;計劃把「不用 `slot_parse`」那句的理由改成可成立的,或改用它。未實測,依據是讀碼(`slot_parse` 參數是任意字串,見 `scripts/lumos:3764`)。

## F3 1c 的「新寫」是整條逐字比對,跟同檔格子規則的比對鍵是兩套
severity: minor
blocking: 否
引句:「接回後的整條在起點那一側——這次改到的所有筆記合起來——找不到一模一樣的」
file: `scripts/lumos:28170-28186`(`_ns_text_key`、`_ns_slot_key`,中日韓字相鄰空白整個去掉、折行不算改)
file: `scripts/lumos:28189-28191`(`_ns_superseded`)

1. 同一個 note-shape 裡,格子規則判「這行是不是舊行」用 `_ns_slot_key`/`_ns_old_keys`(去連結與標點、CJK 相鄰空白去掉,註解明寫「中文任意處折行、續行接回多一格都不算改」)。1c 用「接回後整條一模一樣」。`_ns_summary_logical` 以單一空格接續行,所以一條中文作廢行在 CJK 中間重新折行,接回字串多或少一格空白,「一模一樣」就不成立,被當新寫而擋。名稱次數那一側(〈名詞〉「摘要重排折行,次數不變,都不算新加」)卻不會擋同一個動作,同一組規則內兩條路不一致。
2. 嚴重度 minor:結構對(同樣用 `_ns_superseded`、同樣接回續行),只是比對鍵沒沿用既有的 `_ns_text_key`;場景要求作廢行同時掛活測試又被重新折行,罕見。
3. 對齊做法:比對鍵改用 `_ns_text_key` 正規化後再比。

## F4 〈做法〉2 的 git 呼叫沒指定走哪一支包裝,「終點是提交索引」也不是 git diff 的寫法
severity: minor
blocking: 否
引句:「提交時起點是 HEAD、終點是提交索引」
file: `scripts/lumos:26076-26083`(`_nodehome_git`)
file: `scripts/lumos:26138-26175`(`_nodehome_reader`,`where=="index"` 分支)
file: `scripts/lumos:11926-11929`(`_fix_git_z`)

1. 本檔取清單與內容有一族既有包裝:`_nodehome_git`/`_fix_git_z`(帶逾時、位元組無損解碼)、`_nodehome_reader(where)`(`where=="index"` 只讀提交索引)、`_nodehome_cat_blobs`(批次讀)。計劃寫「用 `git diff --name-status -z --no-renames 起點 終點`」,但 `git diff A index` 不是合法寫法,提交時要 `--cached`;沒有點名走上述哪支,實作者可能另開 `subprocess`,漏掉逾時與無損解碼(路徑有非 UTF-8 時)。
2. minor:語意不會錯(改成 `--cached`),是結構要點名。
3. 對齊做法:〈做法〉2 寫明用 `_nodehome_git(...)` 取 `-z` 清單、用 `_nodehome_reader(where)` 讀兩側內容(起點側 where 是 `base_where`,終點側 `tip_where`)。

## F5 doctor S20 的「複查」沒有被檢查版本可對
severity: minor
blocking: 否
引句:「列出所有筆記指不到的測試名(過了複查還指不到的)」
file: `scripts/lumos:41244-41262`(`_dispositions_check_test` 在 `at_sha` 為空時只做工作樹那一道)
file: `scripts/lumos:2538-2548`(S19 讀 env 的工作目錄筆記)

1. 〈做法〉3 的複查對象是「被檢查的版本」(提交索引或範圍終點),doctor 沒有這個東西(S17–S19 讀的是 env 工作目錄)。〈做法〉10 沒說 S20 的複查對哪個版本:HEAD、索引、還是略過。現有零件在沒有 `at_sha` 時退成只做工作樹一道。
2. minor:S20 只提醒不擋,選錯版本只是提醒多或少;但「過了複查」四個字在 doctor 裡沒有定義。
3. 對齊做法:寫明 S20 的複查 = HEAD 樹(或明講 doctor 不複查、只用工作目錄那一道,並承認會比提交時的判定多報)。

## F6 單次跳過記帳在推送側沒有對應的既有零件,接線點與現有跳過順序衝突
severity: minor
blocking: 否
引句:「單次跳過時,提交與推送兩種都先算一次記進去」
file: `scripts/lumos:28551-28576`(`cmd_note_shape` 跳過分支在解析範圍之前)
file: `scripts/lumos:28089-28110`(`_ns_skip_slot_extra`,只做提交側:`HEAD` 對 `index`)

1. `cmd_note_shape` 的 `LUMOS_SKIP_NOTE_SHAPE` 分支在解析 `diff_range`、算 `base`/`tip` 之前就 return;現有的 `_ns_skip_slot_extra` 也只算提交側(`staged and slots_flag`)。要在推送側跳過時記 `test_refs`,得先解析範圍、算 base/tip(而且那些步驟可能失敗、淺層 clone 等),等於把跳過分支搬到範圍解析之後,或另寫推送側版本。計劃只說「不靠 `--slots`」,沒提這個結構改動。
2. minor:逃生口的規矩是「算不出來照樣放行」(`_ns_skip_slot_extra` 整段包 try、失敗回 None),這點計劃沒寫,實作時要照辦,否則逃生口會因記帳失敗而失效。
3. 對齊做法:〈做法〉8 寫明推送側的跳過帳在範圍解析之後、整段 try、失敗只丟掉 `extra` 不影響放行。

不對齊共 6 條,其中 major 2 條
最高等級:major,blocking 共 2 條
