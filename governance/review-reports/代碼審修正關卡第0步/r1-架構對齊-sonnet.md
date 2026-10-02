severity: major

# 架構對齊審查(架構對齊-sonnet)

## 四問總答

1. 分層與依賴方向:大體對齊。fix-check 放在 `loop` 子指令底下、由指令層呼叫 `_bound_tests_check`(推送閘的判法函式),跟 pitfalls 指令層直接呼叫它同一個方向。file: `scripts/lumos:39659`、`scripts/lumos:39697`。治理帳讀端用 `_drift_jsonl_parse` 整批解析,跟 `cmd_gov` 同一個做法。file: `scripts/lumos:7623-7630`。沒有發現下層反呼上層。兩處不對齊(F1、F2)是「共用函式抽得不全」。
2. 命名與錯誤處理:閘名 `fix-check`、kind `passed`/`warned`/`skipped-env`、`hard=False`、`LUMOS_SKIP_FIX_CHECK`、`--record-template`、回傳碼 1(沒過)/2(輸入壞)、`--repo`,都跟鄰居一致。file: `scripts/lumos:25830`(passed/warned 用字)、`scripts/lumos:30901`(`LUMOS_SKIP_DRIFT_CHECK` 同型)、`scripts/lumos:41109`(`--repo`)。`LOOP_NOT_CLOSE_EVENTS` 守衛只掃 `design-loop`/`code-loop` 兩個閘名,fix-check 是獨立閘名,不會踩到。file: `scripts/test_lumos.py` 的 `t_loop_close_kinds_classified`。不一致處見 F4、F5(minor)。
3. 第二種做法:有兩處(F1 第三份判法、F2 存在判法另寫一份),另有 F3(派工單讀法)、F6(殘骸清理)兩處較輕。
4. 落點:新開 `Systems/代碼審修正關卡` 合理(鄰居 `bound-tests-gate`、`規格閘` 也是一閘一篇)。缺一篇家,見 F7。

## F1 規格閘的「跑一批再逐支判」其實有三份,抽共用函式只收了兩份
severity: major
blocking: 是
引句:「規格閘的條款測試與相依回歸兩處,都是」
佐證行:file: `scripts/lumos:7045-7056`(`_spec_gate_push_one` 第三份:`_run_bound_tests` → `_ran_count` → `_spec_gate_declared` → `_spec_gate_verdict`)、file: `scripts/lumos:6628-6642`、file: `scripts/lumos:6664-6680`
1. 快照說手寫了兩份,要抽成 `_spec_gate_judge_items`。實際 `_spec_gate_push_one`(推送前讀風險低留痕、重跑留痕裡的測試)是第三份同形狀的程式,用同一組呼叫順序,`per_prof` 寫成 `(plats.get(pl) or {}).get("profile_name")` 內聯。
2. 照字面實作:抽完後專案裡會有「共用函式(規格閘兩處+fix-check)」與「推送前那份手寫判法」兩種做法並存。這正是本計劃要消除的重複;之後 `_spec_gate_verdict` 或 `_ran_count` 的呼叫約定一改,推送閘與 fix-check 的綠判法會分歧(fix-check 說綠、推送閘說弱證據,或反過來)。
3. 範圍欄與 S12 的「規格閘印出來的字面不變」也都只提條款測試與相依回歸,沒列推送前那份;實作者照字面不會去動它。
4. 未實測,依據是讀碼(`grep -n "_spec_gate_verdict(" scripts/lumos` 回 6635、6670、7051 三處)。

## F2 修正關卡第 3 項「測試存在」的判法另寫一份,沒有抽共用
severity: major
blocking: 是
引句:「每支測試名包成 `[test:名]` 交給 `resolve_test_refs`」
佐證行:file: `scripts/lumos:38425-38441`(`_bound_tests_for_diff` 內聯的 resolve → `_KILL_METHOD_OK_RE` → `methods_for` 含 `Class.Method` 處理 → real/fake/dangling)、file: `scripts/lumos:6620-6623`(`_spec_gate_items` 只有 `method in methods_for` 的簡化版)、file: `scripts/lumos:7044`(`_spec_gate_push_one` 同簡化版)、file: `scripts/lumos:38620-38626`(`_run_bound_tests` 已會把 dangling/fake/bad-name 的項目直接判紅)
1. 快照說「判法跟推送前合約測試閘算受波及測試時同一套」,但做法是在 fix-check 裡手寫一遍 `resolve_test_refs` + 白名單 + 索引查找,而不是把 `_bound_tests_for_diff` 裡那段抽出來。同一份計劃為了避免重複正在抽兩支共用函式,這支卻新增第四份「名稱 → real/dangling」的分類程式。
2. 現況已有兩種寫法在漂:`_bound_tests_for_diff` 會處理 `Class.Method`,規格閘的兩份不會。fix-check 第 3 項(含 `Class.Method`)與第 4 項(要把這些測試交給規格閘判法跑)吃的是不同口徑,同一支測試名可能第 3 項判存在、卻被另一邊當 dangling。
3. 把分類抽成一支 `(repo_root 或索引, [test:..] 文字) → items[(id, plat, method, status)]` 並讓 `_bound_tests_for_diff` 與 fix-check 共用,結構才一致。
4. ⚠ 交編排者:若決定接受「專案本來就內聯多份」的現況,可降 minor;但本計劃自己的理由(抽共用避免漂移)套在這裡一樣成立。未實測,依據是讀碼。

## F3 讀派工單 base_commit 的規則跟既有兩處讀派工單的做法不同
severity: minor
blocking: 否
引句:「只讀字面那一份 `<輪>-dispatch.json`(同一輪另外的 `<輪>-dispatch-*.json` 不看)」
佐證行:file: `scripts/lumos:11149`(`loop_dir.glob(f"{rid}-dispatch*.json")`)、file: `scripts/lumos:11224`(`*-dispatch*.json`)、file: `scripts/lumos:11144-11165`(三種形狀:單席物件、`seats`、頂層陣列)
1. 既有兩處讀派工單都用 `rN-dispatch*.json` 通配,並把三種形狀都認;fix-check 是第三個派工單讀者,規則刻意收窄成只讀字面檔、頂層陣列當沒有。
2. 結構沒壞(多一欄不影響既有讀者),但同一種檔案現在有兩套「哪些檔算這一輪的派工單」。建議共用一支定位函式或在快照寫明為何不用通配。

## F4 `--regression-set` 的 none 判法跟最相似的 `--refuted-set` 不同
severity: minor
blocking: 否
引句:「只認小寫 `none`」
佐證行:file: `scripts/lumos:8610`(`str(refuted_set).strip().lower() != "none"`,大小寫不拘)、file: `scripts/lumos:8614`(空項的擋下訊息)
1. 快照寫「`--folded-set` 沒有 `none` 這個值,這裡要自己認」,但帳上最像的「可寫 none」的集合旗標是 `--refuted-set`,它用去空白、轉小寫比對。新旗標改成只認小寫,同一個 CLI 兩個 `none` 規則;使用者敲 `--regression-set None` 會被擋,敲 `--refuted-set None` 卻放行。
2. 對齊鄰居:照 `--refuted-set` 的 none 判法與空項訊息。

## F5 理由夠不夠的判法有現成函式,快照沒指名
severity: minor
blocking: 否
引句:「去掉前後空白後至少 `_MANUAL_MIN_CHARS`(4)個字、至少含一個不是標點也不是底線的字」
佐證行:file: `scripts/lumos:8282-8286`(`_escape_reason_ok`,已是「同 `[manual:]` 判法」的單一函式)、file: `scripts/lumos:8620`(`--refuted-set` 內聯同一判法)
1. 快照把判法用文字再寫一遍並說「同 `--refuted-set`」,而 `--refuted-set` 自己是內聯的;實作者很可能再內聯第三份。
2. 結構上應指名重用 `_escape_reason_ok`。

## F6 殘骸清理「寫法照 `_lint_new_clean_stale`」其實是三種不同做法的混搭
severity: minor
blocking: 否
引句:「系統暫存資料夾裡修正關卡前綴、超過一天的殘骸(寫法照 `_lint_new_clean_stale`」
佐證行:file: `scripts/lumos:23798-23812`(只掃 repo 底下 `.lumos/lintbase-*`、只 `rmtree`、不碰 git worktree)、file: `scripts/lumos:14202`(guard kill 用系統暫存 `lumos-kill-` 前綴、沒有任何殘骸清理)、file: `scripts/lumos:23942`(lint-new 的暫存放 repo `.lumos/` 底下)
1. 快照要掃系統暫存資料夾並先 `worktree remove --force`,這在 lint-new 那支裡沒有;而且清理只掛在 fix-check 呼叫端,不在新抽的共用隔離工作樹函式裡,guard kill 的 `lumos-kill-` 殘骸仍沒人清。
2. 結構建議:殘骸清理放進共用函式(按前綴參數),兩個呼叫端同享;否則專案裡會有「有清理的樹」與「沒清理的樹」兩種管法。

## F7 落點:治理帳讀端與 `_KNOWN_GATES` 的家沒進 lands_in
severity: minor
blocking: 否
引句:「治理帳讀端(`cmd_gov` 的轉換)對 `fix-check` 事件吐出 `token` 與上面這些欄位」
佐證行:file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md`(全 Systems 裡唯一提到 `_KNOWN_GATES`、`_GOV_FIELD_TYPES` 的筆記;`about_code` 含 `scripts/lumos`)
1. 本計劃改 `_KNOWN_GATES`、`_GOV_FIELD_TYPES`、`cmd_gov` 轉換,這些的家是 `Systems/reversibility-governance-ledger`,但 lands_in 與〈要同步的文件〉都沒列它;實作者會把讀端欄位說明寫進新節點,日後查治理帳欄位的人在家筆記找不到。
2. 其餘四篇(`guard-kill`、`規格閘`、`loop-convergence-recording`、`finding-refute`)與新開 `Systems/代碼審修正關卡` 的落點對得上各自負責的程式區塊。`Systems/bound-tests-gate` 只在 related、不動,合理。

## 已讀無 finding
- 〈修正紀錄〉形狀與 `--record-template` 的輸出約定:對得上 `pitfalls --dispositions-template`(JSON 走標準輸出、提示走標準錯誤)。引句:「骨架 JSON 印到標準輸出、提示印到標準錯誤,不寫檔」。
- 治理帳事件欄位與 `_gate_event_or_warn` 用法:回傳 `None`(沒 `docs/`)不印、`False` 才印警告,跟函式現況相符。file: `scripts/lumos:1234-1241`。
- `loop next` 提醒用 `_codeloop_record_valid_ex` 判「之後只動簿記檔」:`governance/review-reports/` 已在 `_BOOKKEEPING_DIRS`,沿用是對的。file: `scripts/lumos:22681`。

不對齊共 7 條,其中 major 2 條

最高等級:major,blocking 共 2 條
