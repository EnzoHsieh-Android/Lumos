severity: major

## i1 推送前那一道的「主線 ref」沒有接線,推主線時會讓閘整個失效
severity: major
blocking: 是——照字面實作,推主線時改動範圍會算成空,閘什麼都不擋;推功能分支時主線若過期,會把別人的點算進來而誤擋。
- 段落:範圍 4「範圍」。
- 引句:「主線照 pre-push 的遠端主線 ref;算不出分岔點時退回推送範圍本身」
- 問題一,沒有介面可傳:`--push-check` 只收 `RANGE` 與 `--repo`,見 `scripts/lumos:79332`。
  - 掛鉤呼叫它時只帶 `"$_brange"`,不帶遠端名、被推 ref、主線 ref,見 `scripts/hooks/pre-push:592`。
  - 帶 `--pushed-ref` 的只有 `pitfalls` 那條,見 `scripts/hooks/pre-push:566`。
  - `_spec_gate_push_check(env, git_range, repo)` 的簽名也沒有這些參數,見 `scripts/lumos:17387`。
  - 所以「照 pre-push 的遠端主線 ref」目前沒有東西可以實作,spec 沒寫要新增哪個旗標。
- 問題二,有兩套主線算法,spec 沒選。
  - `_mainline_ref` 是本地 `main@{upstream}`,沒設就退本地 `main`,見 `scripts/lumos:69521`。
  - `_push_mainlines` 另外讀遠端 HEAD、遠端 main/master,並跳過被推的那條,見 `scripts/lumos:69071`。docstring 明說兩套並存。
  - spec 引用的 `_codeloop_disp_range` 屬前一套,見 `scripts/lumos:75325`。
- 具體例一,推主線:本地 `main` 就是 B,又沒設 upstream。
  - `_mainline_ref` 退回本地 `main`,`merge-base(main, B)` 等於 B。
  - 這是「算得出分岔點」,不會走 spec 的退路,範圍變成 `B..B` 的空集合,Kotlin 選擇點一個都不查。
  - `_codeloop_disp_range` 靠 `marker_branch != ml[0]` 才避開這一點,而 `--push-check` 沒有分支名可比。
- 具體例二,推功能分支:`origin/main` 沒 fetch、已經過期。
  - 分岔點會比真正的分岔點更舊,別人已合進主線的 Kotlin 改動算進範圍。
  - 這些點在 B 的帳上沒紀錄,整批誤擋。
- 另外,掛鉤算出的 `_brange` 本身就不是「主線分岔點..B」。更新既有分支時是 `rsha..lsha`,新分支首推是 `push-range` 算的起點,見 `scripts/hooks/pre-push:516`。
  - spec 說的「跟 `choice-points` 不帶 `--diff` 時算出的同一個範圍」因此不成立。
  - `choice-points` 沒給 `--diff` 時,`_codeloop_disp_range` 在目前分支就是主線時回傳 `diff_range=None`,也沒有範圍。

## i2 `no_result` 被擋卻沒有任何有效處置,表的雜訊會造成推不出去的死路
severity: major
blocking: 是——字面實作下,一個編不過的壞法會讓推送永遠被擋,唯一的出口要改工具鏈型錄,或對該點說假話判 `equivalent`。
- 段落:〈用詞〉選擇點、有效處置;範圍 4;範圍 3。
- 引句:「識別字成員照整字比對(同 `_kt_trigger_re` 的邊界)」
- 引句:「缺紀錄、最新 `survived`、`no_result`、不唯一、過期 → 擋」
- 引句:「最新一筆是 `survived`、`no_result` 不算,重跑會再跑。」
- 問題一,比對太寬:`_kt_trigger_re` 只擋英數底線邊界,見 `scripts/lumos:39345`。
  - `first`、`last`、`all`、`any`、`none`、`take`、`drop`、`filter` 這些字當成屬性或具名參數出現時也會中,不限 `.first()` 呼叫。
  - 例:`val x = pair.first`。`first`↔`last` 的壞法是 `pair.last`,`Pair` 沒有 `last`,編不過,判 `no_result`。
- 問題二,出口只有改表:`no_result` 不是有效處置,範圍 4 擋它。
  - 範圍 3 的出口只有「規格沒寫」「測試太弱」「`--judge` 判 `equivalent` 或 `not-requirement`」「拿掉程式」。
  - 實務隱患那節說「多半要改表而不是要人處置」,但表在工具鏈的 `skills/kotlin-idioms/checks-catalog.md`。消費專案的作者推不動,只能把「編不過」謊報成等價。
- 問題三,還有別的 `no_result` 來源,都跟程式寫法無關。
  - `cmd_guard_kill` 的 `weak` 把「run_cmd 沒有 `{method}`(整套一起跑)」與「計劃筆記有未提交改動」都算進去,見 `scripts/lumos:28145`。
  - 範圍 2 的前置檢查只講 Android 檢查,沒要求 `{method}`,也沒講為什麼 `no_result` 該擋推送。
- 建議:`--judge` 加 `--as not-compilable`(要留帳、可重審),或把 `no_result` 納入有效處置。

## i3 與情境題那道:同一行被要求兩次,事件互相看不見,還會污染情境題統計
severity: minor
blocking: 否——不會做錯行為,但會重複跑 Gradle,並讓情境題的撤除度量失真。
- 段落:範圍 3「規格沒寫」、範圍 5。
- 重複要求:決策表 D-4(`flatMapLatest`)、D-8、D-9(`coroutineScope`、`supervisorScope`)、D-16(`conflate`)、D-26(`firstOrNull`)的觸發字,跟選擇點表的成員重疊,見 `skills/kotlin-idioms/checks-catalog.md:732`。
  - 同一行會同時被 code-loop 的 kt-situation 題要求表態,又被推送前的選擇點要求處置。
  - 情境題人裁在 kill-log 與治理帳留的是 (seg, row),選擇點的身分是 (file, old, new),兩邊不互認。同一組換寫法會再跑一次 Gradle。
- 矛盾無人偵測:情境題表態「適用且引到規格 S3」,選擇點卻被人判 `not-requirement`。spec 沒有任何一處比對這兩種紀錄。
- 統計污染:`--point` 路徑照原本流程寫的 situation-rule 事件,`seg` 與 `row` 會是空的,spec 沒要求加 `via` 或 `point` 欄位。
  - `_gov_situation_spec_counts` 把每一筆 `(situation-rule, situation-rule)` 都算成「情境題人裁」,見 `scripts/lumos:17860`。
  - 選擇點的寫回因此會灌進情境題計劃自己的 RETIRE-IF 分子。
- 引句:「冪等鍵從 (seg, row) 換成 (file, old, new) 的集合。寫回成功同時記組裡每一點的 `choice-kill` killed(`via: situation-rule`)。」

## i4 紀錄怎麼進到 B 沒說清楚,跟代碼審留痕的先後也沒排
severity: minor
blocking: 否——作者會被卡住,但 spec 沒有做錯,只是漏講步驟。
- 段落:範圍 2「記」、範圍 4「讀哪一版」。
- 引句:「記:每點跑完當場寫一筆治理帳 gate `choice-kill`、kind `choice-kill`」
- 事件寫在工作目錄的 `docs/.governance-log.jsonl`,推送前卻只讀 B 的那份。
  - 沒提交進 B 的紀錄,推送閘看不到。
  - situation-rule 做完會印「下一步提交計劃與治理帳」,見 `scripts/lumos:76525`,choice-kill 與 blocked 訊息沒要求同樣的提示。
- 順序:範圍 3 的補救會改計劃檔(`situation-rule` 寫條款)或測試檔,動到的不是只有帳本。
  - 代碼審通過後「只准再提交帳本」,所以補救會讓已通過的留痕失效。
  - spec 沒說 `choice-kill` 該在代碼審通過之前還是之後跑。
  - 範圍 6 只說 lumos-code-loop 手冊要補一段,沒有排序。

## i5 `blocked` 事件沒有 token,重複推送在 gov 去重裡被折成一筆
severity: minor
blocking: 否——只讓統計失真。
- 段落:範圍 4 最後一條(記 `blocked`)、範圍 5(`_gov_row`)。
- 引句:「`_gov_row` 對 `choice-kill` 取 `token` 並帶出 `verdict`、`group`、`attempt`、`reason`、`as`、`style`、`via`」
- `cmd_gov` 去重鍵是 (commit, nodes, gate, kind, token, check),見 `scripts/lumos:18357`。
  - 範圍 2 列了 `killed`、`judged` 等事件的 `token` 欄位,範圍 4 的 `blocked` 事件沒有。
  - 同一個 HEAD 重推兩次、帳上各有一筆 `blocked`,gov 只算一筆。
- `--stats` 的「被擋筆數」與「過期占比」,以及 RETIRE-IF ③,都是從去重後的列算的,會被低估。
- 另外 spec 沒寫 `hard` 的值。`gov --stats` 的「硬擋」統計對所有 `kind == "blocked"` 的列都計,不看 `hard`,見 `scripts/lumos:18084`。

## i6 版控治理帳的量:一點一筆、帶 `old` 與 `new`,而且帳已經超過 doctor 的上限
severity: minor
blocking: 否——是長期成本,沒有立即做錯。
- 段落:範圍 2「記」、範圍 5。
- 現況:`docs/.governance-log.jsonl` 約 22.5MB、12.5 萬行。doctor 的 `_LEDGER_MB_CAP` 是 5,另有近 7 日是前 7 日 2 倍的成長警告,見 `scripts/lumos:2862`。
- `choice-kill` 不在 `_GOV_LOCAL_PAIRS`,見 `scripts/lumos:1639`。
  - 事件會進版控帳,而且每點每次跑一筆。
  - 一筆有 `old`(最多 500 字)、`new`、`test_blobs`、`clauses`、`plans`,很容易超過 `_gate_event_fit` 的 4096 位元組政策值,見 `scripts/lumos:1860`。
- 大分支在 doctor 的 `ledger-growth` 會一次跳警告,每次推送還要整本 `git show` B 版帳。
- spec 的 RETIRE-IF ② 只量耗時,沒量帳量。
- 建議:`killed` 與 `survived` 這類逐點執行紀錄寫本機帳,只有 `judged`、`split`、`unsuppress`、`blocked` 進版控帳。

## i7 `situation-rule --group` 的寫回不在兩段式收尾裡,多計劃時 node 也沒定
severity: minor
blocking: 否——可靠重跑補救,只是多花一輪 Gradle。
- 段落:範圍 3「規格沒寫」、〈用詞〉守的測試、範圍 2「共用」。
- `_situation_rule_commit` 把「寫計劃加記一筆治理帳」做成兩段式訊號收尾,中斷時會印補記事件,見 `scripts/lumos:76180`。
  - `--group` 要「同時記組裡每一點 killed」,多出 N 筆帳在這個協議外。
  - 條款寫了、其中幾筆沒記到時,沒有補記辦法。能補的只有重跑 `choice-kill`,而那又是一輪 Gradle。
- `cmd_guard_kill(env, node, …)` 只有一個 `node`,它同時決定 kill-log 的 `node`、`recipe_id`,以及 `node_dirty` 這個弱證據判定。
  - 「守的測試取範圍碰到的所有進行中計劃」時,spec 沒說 `node` 取哪一份計劃。
  - 引句:「共用:人裁的 `_situation_rule_kill` 改成只回 (結果列或 None, 狀態 `ok`/`interrupted`/`no_rows`)」

## i8 改 `_situation_rule_kill` 的回傳形狀會讓既有測試翻紅
severity: minor
blocking: 否——要求先改測試並簽核,不是行為錯。
- 段落:範圍 2「共用」。
- 引句:「共用:人裁的 `_situation_rule_kill` 改成只回 (結果列或 None, 狀態 `ok`/`interrupted`/`no_rows`)」
- 現況是回 `(r0, rc)`。`scripts/test_lumos.py:134707` 與 `scripts/test_lumos.py:135218` 直接解包這個回傳值,`scripts/test_lumos.py:135331` 把它換成回 `(…, None)` 的 lambda。
- spec 說「行為不變」,卻沒列要改的既有測試。改 `test_lumos.py` 要先簽名,這件事影響交付順序。

## i9 型錄新增〈選擇點表〉:現有型錄檢查沒涵蓋,section 不存在時的行為也沒定
severity: minor
blocking: 否——都是接線細節,spec 裡補一句即可。
- 段落:〈用詞〉選擇點表、範圍 6。
- 引句:「型錄照 `_kt_catalog_path()` 讀(工具鏈來源那份,不隨被推送版本變;測試用 `LUMOS_KT_CATALOG`)」
- 情境決策表的解析實際在 `configs/ast-grep/kotlin-android/check.py` 的 `dt_table`,從 `\n## 情境決策表` 切到下一個 `\n## `。spec 說「新增一份解析」,沒說放哪。
- `catalog_problems` 把 `情境決策表` 到 `待查證` 之間整段當決策表,見 `check.py:473`。〈統計〉節的手寫數字也是靠重數校驗的,見 `check.py:628`。
  - 新節放哪、要不要接進 `catalog_problems` 與〈統計〉,spec 都沒寫。
  - 不接的話,「缺欄、組號重複、壞法不在成員範圍」只在推送時才發現。
- `C-<n>` 與現有編號家族(`API-`、`CO-`、`D-` 等)沒有衝突,已查證。
- `_kt_catalog_missing` 只判檔案或 `check.py` 不在。檔在、但沒有〈選擇點表〉節,到底算缺檔只提醒還是表壞要擋,spec 沒寫。

## i10 spec 內部的小矛盾與對規格閘既有裁定的衝突
severity: minor
blocking: 否——都是文字或表格的對不上,實作不會因此做錯。
- S7 的預期值表第一列「計劃檔有未提交改動」比條款「當工作目錄不乾淨」窄。〈範圍〉2 寫的是「工作目錄除簿記檔外乾淨」,三處口徑不一致。
  - 引句:「當工作目錄不乾淨、沒有守的測試、或 --import 沒配 --only,choice-kill 應 回 2 不跑」
- S15 的預期值表自相矛盾。
  - 引句:「帳上 attempt 1:killed 3(其中 via situation-rule 1)、survived 1、no_result 1」
  - 走 situation-rule 寫回的那一點,依範圍 3 一定是先有 `survived` 才補救,它的 `attempt` 至少是 2,不該落在「attempt 1」的分母裡。第一次跑殺掉率 3/5 因此算不出來。
- S12 的 `[manual:]` 全部條款的計劃,在規格閘裡是已裁定的做法:Enzo 裁小改動不必綁測試,`manual_only` 的風險低計劃推送時印 `light`,見 `Systems/規格閘.md:32`、`Systems/規格閘.md:36`。
  - 引句:「碰到進行中計劃,但條款全是 `[manual:]`」
  - spec 讓這種計劃下的每個 Kotlin 改動都要逐點 `--judge`,但沒有翻案紀錄(〈舊否決比對〉沒列),也沒說 light 分級與這個擋下並存時的輸出。

## 逐節與交叉引用核對
- 〈白話〉〈不做〉〈回退〉〈天花板〉:已讀,無 finding。
- 交叉引用:範圍 N、S1 到 S20、預期值表各列、〈用詞〉各詞的目標都存在、前後一致(S17 排在最後,是 manual 條款)。
- 〈用詞〉剝註解那段:`_strip_c_comments(..., blank_strings=True, kotlin=True, keep_length=True)` 的字串樣板 `${…}` 內程式碼保留、反引號識別字照留,與 spec 說法一致,見 `scripts/lumos:6869`。
- 已查證且沒問題的假設:
  - `_spec_gate_push_scan` 裡的 `_live` 確實是巢狀函式,見 `scripts/lumos:17254`。
  - `_gov_rows_at`、`_kt_sit_read_many` 的簽名與回傳形狀都符合 spec 用法。
  - `_backing_kill_rows` 目前只跳過 `source == situation-rule`,改成「非空就跳過」不影響其他讀者,見 `scripts/lumos:77491`。
  - `LOOP_NOT_CLOSE_EVENTS` 的守衛 `t_loop_close_kinds_classified` 只看 `design-loop` 與 `code-loop` 兩個閘,所以 spec 說「守衛不強制」正確。
  - `_KNOWN_GATES` 要加 `choice-kill`,否則 `_gate_event` 會拒寫,見 `scripts/lumos:1815`。

## 固定席節點判定
- `Systems/guard-kill`,INVARIANT「rc 優先序」:不影響。`choice-kill` 讀 `result_out` 的列,不讀 rc,`cmd_guard_kill` 的 rc 判定與 `weak`/`killed_unattributed`/`timed_out_weak` 的弱證據不放行都沒動。
  - 新增選用參數 `source` 不改預設行為。
  - 副作用只有:同一點有多支測試、一支殺掉另一支存活時,仍會印「✗ 有配方 SURVIVED」到 stderr,是雜訊,不是破壞。
- `Systems/guard-kill`,INVARIANT「`--json` 成功跑完時 stdout 恰一行 JSON」:不影響。`choice-kill` 不走 `as_json`,不碰那條路。
- `Systems/規格閘` 的 KEY:不影響既有行為,但有兩處需要補翻案說明。
  - 見 i10:`[manual:]` 條款的小改動裁定,以及 light 分級。
  - 見 i1:新增的那圈會在 `_spec_gate_push_check` 內另起,它的範圍參數需要新旗標才能接上。

最嚴重:major;blocking 共 2 條
