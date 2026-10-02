severity: major

# r3 架構對齊-sonnet

審查對象:`Projects/筆記測試綁定要存在_計劃.md` 的凍結快照 r3-snapshot。對照 repo 根:`scratchpad/negguard`(下文 `lumos` 指它的 `scripts/lumos`)。慣例 skill:python-idioms。

## 四問結論

**1. 分層與依賴方向。** note-shape 這一帶(`lumos:27100-28700`)現在不呼叫任何 `_drift_*` 或 `_dispositions_*`;方向是反的:存量漂移那一段(`lumos:30374` 起)大量吃 note-shape 的零件(`_ns_summary_logical`、`_ns_superseded`、`_notelines_regions`,例 `lumos:30899-30900`)。計劃要 note-shape 反過來呼叫 drift 私有的 `_drift_tree_env`(F2),形成 note-shape 與 drift 互相依賴。借 `_dispositions_check_test` 也是閘對閘私有呼叫,但它不吃 note-shape,方向沒反,只是少了鄰居的例外包法(F5)。

**2. 命名與錯誤處理。** 開關那支 `_note_shape_test_refs_parse` 照 `_note_shape_slots_parse`(`lumos:28113`)的形狀,對齊。不對齊的是:鄰居每一組附加規則在 cmd_note_shape 裡都包例外、fail-open 印一句(`_ns_slots_collected` `lumos:28030`),計劃沒寫;`_dispositions_check_test` 的呼叫端鄰居一律包例外(`lumos:41386` 起),計劃沒寫(F5);帳本欄位鄰居用扁平計數,計劃用巢狀名稱清單,印出的筆記字串也沒提跳脫(F8)。

**3. 第二種做法。** 查到四處新冒出的第二種做法:①「舊行比對」另用 `_ns_text_key` 單鍵,不用鄰居 `_ns_old_keys`/`_ns_is_old`(它帶「舊行有沒有標作廢」旗標),會讓 1c 的主要場景放行(F1,有實測);②note-shape 同一趟內再呼叫一次 `_notelines_new`,鄰居(否定現況句、標籤提示、格子)都掛在 `_note_shape_eval` 那一趟的容器上收 rows(F3);③上線點:鄰居每組新規則各有自己的掛鉤記號、「找不到記號=整段不跑」(`lumos:27990-27993`),計劃改用 note-shape 的舊記號(F4);④「類別.方法」規則第三次內嵌,而不是抽共用(F6)。r2 換進來的 `slot_parse`、`_notelines_new`、`_ns_summary_logical`、`_visible_lines` 本身借法跟鄰居一致。

**4. 落點。** 引用的 doctor S20 放進 lumos-cli-read、規則放筆記內容閘,跟 S17–S19 與格子規則的家一致;位置紀律(S19 之後、避開截斷視窗)也照鄰居。缺的是:被改的 `_dispositions_check_test` 的家在 `Systems/棧別提問表態閘`(該篇已寫它的 test: 驗法),計劃的 lands_in 與要同步清單卻列 bound-tests-gate、另寫「實作時找家」(F7)。

## F1 1c 的「舊行」比對鍵用錯,把「舊行改標作廢」這個主要場景放行
severity: major
blocking: 是
引句:「(1c)新寫的作廢條目掛著活測試,而且這一條用 `_ns_text_key` 正規化後在起點那一版整個知識庫找不到一樣的(只重排折行的不算新寫)→ 違規」
file: `scripts/lumos:28194-28215`(`_ns_old_keys` 存 `(連結集合, _ns_superseded(ln))`,`_ns_is_old` 回「對上的舊行有沒有標作廢」)
file: `scripts/lumos:28243-28247`(`_ns_slot_line_problems`:舊行這次才加上作廢,照樣當要查的)
file: `scripts/lumos:28168-28190`(`_ns_slot_key` 用 `slot_parse(...)["core"]` 才進 `_ns_text_key`,欄位已被剝掉)
1. 輸入:一條既有的活 RULE(帶 `[test:t_a]`),這次推送只在行尾加 `[status:superseded] [被取代:無 理由]`,`[test:t_a]` 留著。這正是 rtb 那種「撤除條款仍掛活測試」的標準寫法。
2. 走到:這行是新寫的行(進得了 `_notelines_new`),再走 1c 的「起點整庫找不到一樣的」判。`_ns_text_key` 吃的是 `slot_parse` 的核心句,`[status:]`、`[被取代:]`、`[test:]` 都是格子鍵、都被剝掉,新舊兩版文字鍵相同。
3. 壞在:起點版找得到「一樣的」,這條被當舊行放過,1c 不擋。只有「全新寫一條就是作廢的」才擋,而作廢幾乎都是改舊行做的(`lumos:28212` 註解已寫明)。
4. 最小實驗(已跑,在我的 shared clone 裡):
   舊行 `[test:t_a] 舊限制… [依據:人] [since:…] [retire:人裁] [until:…]`,新行同上加 `[status:superseded] [被取代:無 不需要了]`
   `_ns_text_key(core)` 新舊相等:`True`(值 `舊限制要有測試守著`);`_ns_is_old(新, _ns_old_keys([舊]))` 回 `(True, False)`,後一個 False 就是「舊行沒標作廢」,鄰居靠它判出「這次才作廢」。
5. 對齊做法:1c 的「是不是新寫」改用 `_ns_old_keys` 與 `_ns_is_old` 的 `old_sup` 旗標(舊行已作廢才算舊),不另用 `_ns_text_key` 單鍵;S11 要補「舊行改標作廢」這個案例,S12 才不會只測到折行。

## F2 note-shape 反向呼叫 drift 私有的 `_drift_tree_env`,依賴方向反了
severity: major
blocking: 是
引句:「起點知識庫批次讀 `_drift_tree_env`;每條的鍵用格子的 `slot_parse`」
file: `scripts/lumos:30601-30627`(`_drift_tree_env` 在 drift 區段,靠 `_drift_list` 與 `_DRIFT_LS_CACHE`)
file: `scripts/lumos:30899-30900`(drift 區段呼叫 note-shape 的 `_ns_summary_logical`、`_ns_superseded`)
file: `scripts/lumos:30521`(drift 呼叫 `_notelines_regions`)
1. 現況:note-shape 區段(`lumos:27100-28700`)沒有任何 `_drift_*` 呼叫(我用 awk 掃過);drift 區段有 14 處吃 note-shape 的 `_ns_*`/`_notelines_*`。依賴是 drift 到 note-shape 單向。
2. 計劃讓 `_note_test_refs` 與起點集合這條路從 note-shape 呼叫 `_drift_tree_env`,而 drift 區段本來就依賴 note-shape,變成雙向。鄰居裡「兩個閘共用」的零件(`_notes_status_flipped` 註明筆記內容審與存量漂移共用、`_doctor_cfg_bytes` 的 docstring 寫「原本三段各抄一份,抽成這一支」)都是抽到中性位置才共用,沒有閘直接伸手拿別的閘私有函式。
3. 要用起點整庫文字,對齊做法是把 `_drift_tree_env`(連同 `_drift_list`、`_drift_cat`)提到 `_nodehome_*` 那一層的中性位置,drift 與 note-shape 都從那裡拿;或不借它,用 note-shape 自己已有的 `_nodehome_reader(root, base)` 加 `_nodehome_list`。計劃兩者都沒講,PRIOR-ART 還把它寫成「全部沿用既有零件」。

## F3 同一趟 note-shape 再呼叫第二次 `_notelines_new`,不走鄰居共用 rows 的容器
severity: major
blocking: 是
引句:「這組不靠格子的 `--slots` 容器,自己向 `_notelines_new` 要 rows。」
file: `scripts/lumos:28406-28418`(`_note_shape_eval` 一趟呼叫 `_notelines_new`,rows 分給 `hints`、`tags`、`slots` 各路收集)
file: `scripts/lumos:28608-28618`(cmd_note_shape 把 `hints`、`tags`、`slots` 傳進同一趟 eval)
file: `scripts/lumos:27344-27364`(`_notelines_new` 推送時逐提交掃掛鉤歷史,是整段最貴的一步)
1. 鄰居:否定現況句(`_ns_negation_collect`)、標籤提示(`_ns_tag_hints_collect`)、格子(`slots["notes"], slots["old_by"]`)全部掛在 `_note_shape_eval` 那一次的 rows 上;整支 cmd_note_shape 只呼叫一次 `_notelines_new`。
2. 計劃的步驟 2 與步驟 7:`_note_shape_eval` 之後「另跑這組」、「自己向 `_notelines_new` 要 rows」。字面實作 = 同一次推送內第二次逐提交掃、第二次 `git diff`;而 PRIOR-ART 與步驟 2 都說「不另跑 git diff」,字面上互相矛盾。
3. 步驟 8 的單次跳過又要再多一趟(`_ns_skip_slot_extra` 本身就會再跑一次 `_note_shape_eval`,見 F8),同一個命令最多三次讀同一批 rows。
4. 對齊做法:這組做成跟 hints/tags 同形的收集器,掛在 eval 那一趟的 rows 上,eval 後只做判定與印出。

## F4 上線點用 note-shape 的舊記號,跟鄰居「每組新規則自己一個記號、找不到就不跑」不同
severity: major
blocking: 是
引句:「上線點沿用 note-shape 既有的(`_notelines_new` 已經處理),不另設記號:消費專案 `lumos update` 換到新程式就開始擋,不必改掛鉤範本。」
file: `scripts/lumos:27990-27993`(格子註解:「找不到記號=整段不跑」,「既有上線點找不到是不過濾、全查,格子不能照抄」)
file: `scripts/lumos:28007-28027`(`_ns_slots_prepare` 推送與 CI 看自己的 `_SLOTS_GOLIVE_MARK`,找不到就不跑)
file: `scripts/lumos:28718`、`29671`、`30374`(筆記內容審、重讀、存量漂移也各有自己的 `*_GOLIVE_MARK`)
1. 鄰居慣例:凡是會新擋的規則組,各有一個只出現在掛鉤呼叫行的記號,推送與 CI 在終點的掛鉤歷史找不到那個記號就整組不跑,doctor 另有一段講「這組沒在跑」(`_ns_slots_doctor_lines`)。
2. 計劃用 note-shape 的舊記號,代表任何已經裝了 note-shape 的消費專案,`lumos update` 一換程式,所有還沒推出去的、更新前寫的提交都變成這組規則的檢查對象。計劃用「起點那一版出現過的名稱不算新加」緩了一部分,但更新前寫、尚未推送的新名稱仍被擋,而且這是計劃自己寫的本意(「相容」一節),沒有退路,只有 `test_refs: warn` 這種事後逃生口。
3. 對齊做法:這組自己一個記號與 `mark2`/sink 路徑,或明講為什麼這組可以不照格子的先例,並在計劃寫出對「更新前寫、尚未推送的提交」的處理。

## F5 呼叫 `_dispositions_check_test` 沒包例外,逾時會變成假擋(⚠ 嚴重度請編排者裁)
severity: minor
blocking: 否
引句:「索引建不起來、或某平台的根不存在、掃不到任何測試方法 → 那個平台這次不查、印一行原因。」
file: `scripts/lumos:41244-41290`(`_dispositions_check_test` 內 `_sp.run(..., timeout=_disp_git_timeout())` 沒接 `TimeoutExpired`、`pdata["platforms"][plat]["root"]` 沒接 `KeyError`)
file: `scripts/lumos:41386-41440`(鄰居的呼叫端用 try/except 把任何例外接成「無法驗證」;docstring `lumos:41391` 寫明「任何例外都由呼叫端接成無法驗證」)
file: `scripts/lumos:28030-28044`(`_ns_slots_collected`:格子整段包 try/except,印一句、當作沒有)
1. 計劃只列了「索引建不起來、平台根不存在、掃不到方法」三種 fail-open;對每個名稱呼叫 `_dispositions_check_test` 時的例外(`git grep` 逾時預設 8 秒 `LUMOS_DISP_GIT_TIMEOUT`)與 cmd_note_shape 的整組例外沒有任何規定。
2. 字面實作:某名稱的 `git grep` 逾時,`TimeoutExpired` 一路往上沒人接,Python 以 exit 1 結束,跟 note-shape 的「擋下」同一個回傳碼,推送被擋而且沒有違規清單。
3. 結構對(借對了函式),錯誤處理跟鄰居不一致,依分級錨標 minor;但按共同規則「擋錯」字面可到 major,請編排者裁。對齊做法:整組仿 `_ns_slots_collected` 包例外 fail-open 印一句,每個名稱的判存在仿 `_one` 的「無法驗證」處理並寫進 S14。

## F6 「類別.方法」規則第三次內嵌,不抽共用;doctor 同一份輸出裡兩種指不到的判法
severity: minor
blocking: 否
引句:「寫法照 `_classify_test_refs` 的規矩補進第①道(只認方法名那段),第②道用方法名找。」
file: `scripts/lumos:40248-40275`(`_classify_test_refs` 內嵌 `method.rsplit(".", 1)[-1] in mset`)
file: `scripts/lumos:12923-12943`(`_classify_one` 沒有這條)
file: `scripts/lumos:1656-1690`(doctor Check T 內嵌自己的判法,也沒有這條;另分 fake 與 dangling)
1. 已經有三種判法:`_classify_one`、Check T 內嵌、`_classify_test_refs`,只有最後一種認「類別.方法」。計劃補成第四份(`_dispositions_check_test` 內再抄一次)。
2. doctor 因此同一次輸出裡:Check T 對合約行用 Check T 的判法,S20 對其他行用表態閘的判法;同一個 `Class.Method` 字串,合約行與非合約行得到不同判定。
3. 另外 `_dispositions_split_test`(`lumos:40910-40924`)的 legacy 單平台遇冒號回「沒開多平台」,`resolve_test_refs`(`lumos:5169-5190`)是整串配預設平台;docstring 寫「規則同 resolve_test_refs」但不同,計劃 S25 的「平台前綴沒定義」提示要靠比對原因字串(鄰居 `_ev_msg` 有比字串開頭的先例,故只列入此條)。
4. 對齊做法:把「方法名是否在平台集合」抽成一支共用小函式讓四處都用,並在計劃寫出 legacy 遇冒號的判法。

## F7 被改的 `_dispositions_check_test` 的家已經可查,計劃卻留到實作時找、lands_in 也列錯
severity: minor
blocking: 否
引句:「管 `_dispositions_check_test` 的那篇(實作時用 `lumos impact --file` 找家)」
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:31`(寫了表態 `test:` 名在平台索引掃不到、`git grep -w` 不到就擋)
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:39`(寫了 test: 證據只掃測試副檔名、排除 docs 與 governance)
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:31`(這篇的主題是受波及合約測試真跑閘與掛接)
1. 計劃的 `lands_in` 與要同步清單列 bound-tests-gate 並寫「說明兩支的分工」,但 `_dispositions_check_test` 本身(含這次補的「類別.方法」)的行為記載在棧別提問表態閘;家規(每支檔有家、改了程式寫進改到那支檔的家)要求寫進那篇。
2. 計劃另借 `_drift_tree_env`(家在存量漂移守衛),`lands_in` 沒有。
3. 對齊做法:`lands_in` 改成 筆記內容閘、lumos-cli-read、棧別提問表態閘(必要時加存量漂移守衛),bound-tests-gate 只留一句分工連結。

## F8 帳本欄位形狀與單次跳過路徑跟格子不同,印出的筆記字串沒提跳脫
severity: minor
blocking: 否
引句:「提交時被單次跳過,照格子的 `_ns_skip_slot_extra` 先算一次記進去(不靠 `--slots`)」
file: `scripts/lumos:28089-28110`(`_ns_skip_slot_extra`:格子模式 off 或 MERGE_HEAD 就回 None,跳過帳什麼都不帶;它自己會再跑一次 `_note_shape_eval`)
file: `scripts/lumos:28368-28375`(`_ns_slot_extra`:扁平欄位 `check`、`slots_lines`、`slots_missing`,只放計數)
file: `scripts/lumos:28685-28707`(報告印出路徑、片段一律 `_esc_clean`;注解說片段是筆記原文)
1. 「照 `_ns_skip_slot_extra`」沒說是擴充同一支還是另寫一支;若另寫,跳過路徑裡有兩支各自跑 eval 的函式(見 F3),且 `check` 欄位要合併成第三種值。若直接擴充,它在格子 off 時直接回 None,`test_refs` 就帶不進帳,S19 的「單次跳過時應帶 test_refs」落空。
2. 計劃的 `test_refs` 是巢狀字典,內含「前 20 個名稱與各自原因」(筆記原文與 `_dispositions_check_test` 的原因字串);鄰居的 extra 只放計數與格名。名稱是任意筆記字串,報告與帳本寫入沒寫要經 `_esc_clean`,而鄰居的報告對路徑與片段都跳脫。
3. 對齊做法:擴充 `_ns_skip_slot_extra` 一支回兩組鍵、不受格子模式限制;帳本 extra 放計數與種類,名稱只印不記或記前先過 `_esc_clean`。

## F9 起點版的圖譜路徑與「沒有起點」沒照 `_drift_tree_env` 鄰居的用法處理
severity: minor
blocking: 否
引句:「起點那一版整個知識庫的名稱集合用 `_drift_tree_env` 一次批次讀(有時間上限,超過就這組這次跳過、印一行)」
file: `scripts/lumos:31450-31462`(鄰居讀起點:`if not base: return`、`_drift_vault_rel(root, base) or vault_rel`、`benv is None` 印一句)
file: `scripts/lumos:28606-28608`(note-shape 的 `base_where` 在整庫第一次推送時是 `None`)
1. 鄰居三件事:沒起點直接當沒有;起點那一版的圖譜資料夾用 `_drift_vault_rel(root, base)` 另算(圖譜改名、搬家時終點的 vault_rel 在起點是空的);讀不出就印原因。
2. 計劃只寫了逾時。字面實作:圖譜資料夾在這次推送中改名,拿終點的 `vault_rel` 去讀起點,起點集合是空的,每個既有測試名都被當成新加、全部被判一次存在,可能大量誤擋;`base_where` 為 `None` 時 `_drift_tree_env(root, None, …)` 的行為計劃沒定。
3. 對齊做法:照 `lumos:31450` 那三步寫進步驟 3,並補一條測試。

## 其他
- 抽取用 `slot_parse`、摘要條目用 `_ns_summary_logical`、圍欄用 `_visible_lines`、條款行用 `_CLAUSE_LEAD_RE`、doctor 位置與「不寫帳、不計入問題數」都跟 S16–S19 一致:已讀,無 finding。
- 開關讀法 `note_shape.test_refs` 仿 `note_shape.slots`,壞值照 block 並提醒:已讀,無 finding。

不對齊共 9 條,其中 major 4 條
最高等級:major,blocking 共 4 條
