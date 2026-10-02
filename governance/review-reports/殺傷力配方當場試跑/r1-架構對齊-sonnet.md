severity: minor

席名:架構對齊-sonnet。對照的程式碼是 negguard 副本(下文 `scripts/lumos:行號` 都指那份)。

## 四問總答

1. 分層與依賴方向:一致,無跨層直呼。
   - kill-add 在同一行程呼叫 guard kill:同檔先例是 cmd 呼叫 cmd。file: `scripts/lumos:7262`(cmd_signoff 呼叫 cmd_set)、file: `scripts/lumos:12522`(loop 內呼叫 cmd_loop_status)。kill-add 本身也已有「鎖內寫、鎖外做慢事」的分層,file: `scripts/lumos:14279-14289`(鎖外才跑 `_kill_add_warn`)。`--try` 放在鎖外、提醒之後,方向相同。
   - doctor 讀殺傷力帳本:doctor 呼叫計算函式、自己印,file: `scripts/lumos:2954`(`_kill_p2_scan` 回 dict、doctor 組 warn_soft 與 gov_events)。`_backing_kill_rows` 已被「寫表態」這個非 doctor 的呼叫端使用,file: `scripts/lumos:41160`。doctor 多一個讀者不改方向。
   - 修正關卡掃配方:fix-check 本來就跨領域呼叫 `_classify_test_refs`、`_bound_tests_check`、`_spec_gate_judge_items`,file: `scripts/lumos:12060-12115`。再呼叫 `_kill_*` 同性質。取筆記用 `env.notes`,file: `scripts/lumos:654`。
2. 命名與錯誤處理:結構對、命名與細節有 5 處跟鄰居不同(F1、F2、F6、F8、F9),都是 minor。
3. 第二種做法:「取最新一筆」「判檔有沒有改過」都沒有另起爐灶到 major 的程度,但各有一處值得註記(F4、F5)。「把結果交回呼叫端」專案已有慣例(out 參數),本份沿用但改了名字與型別(F1)。
4. 落點:合理。`Systems/guard-kill` 管 kill-add、guard kill、doctor P2(file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:35,71,103`),`Systems/代碼審修正關卡` 管 `loop fix-check` 提醒(file: `docs/lumos-toolchain-knowledge/Systems/代碼審修正關卡.md:1-12`,responsibility 欄)。兩篇都存在、about_code 都含 `scripts/lumos`。「要同步的文件」裡的指令速查第 06 子檔不是 Systems 節點,不用進 lands_in。落點見 F7 的連帶要改的舊句。

## F1 交回結果的參數名與型別跟既有先例不同
severity: minor
blocking: 否
引句:「與 `results_out`(呼叫端給一個清單,跑完把每條的判定、證據弱、短身分放進去)」
file: `scripts/lumos:21511`(`_loop_status_disposal(..., result_out=None)`)
file: `scripts/lumos:21802-21804`(`result_out["rid"] = rid`、`result_out["fails"] = list(fails)`)
file: `scripts/lumos:928`、`scripts/lumos:942`、`scripts/lumos:1091`(呼叫端傳 `result_out=out`)
1. 專案已有「cmd 函式回傳碼固定是整數、結果用選用 out 參數交回」的先例,先例叫單數 `result_out`、型別是 dict、呼叫端傳空 dict。
2. 本份取名複數 `results_out`、型別是清單。做法本身(選用 out 參數)是對的,不算第二種做法。
3. 名字與型別跟先例不一致,日後讀 code 的人會當成兩套約定。

## F2 `check-p2` 用新 kind `survived` 區分兩種提醒,鄰居是用不同 gate 名
severity: minor
blocking: 否
引句:「每篇涉及的筆記各記一筆 `check-p2` 事件,kind 用 `survived`(跟原文對不上的 `warned` 分開)」
file: `scripts/lumos:1748`(check-s)、`scripts/lumos:1802`(check-s2)、`scripts/lumos:1833`(check-s3)、`scripts/lumos:1857`(check-s4)
file: `scripts/lumos:3496`(`_SLOT_METRIC_KINDS = ("blocked", "warned", "skipped-env", "hinted", "acked")`)
file: `scripts/lumos:7303`(已知 gate 名清單,`check-p2` 在其中)
1. doctor 各段全部寫 `kind: "warned", hard: False`;同一類的兩種軟提醒分開時,先例是另開 gate 名(check-s、check-s2、check-s3、check-s4),不是在同一個 gate 換 kind。
2. kind 的既有詞彙是「這個關卡做了什麼動作」(blocked、warned、skipped-env、hinted、acked),`survived` 是 guard kill 的判定詞,屬於另一種語意。
3. 度量欄 `度量 <gate>.<kind>` 只認那五個 kind(`scripts/lumos:3566-3567`),`check-p2.survived` 之後無法被度量引用。
4. 結構(軟提醒、不擋、落帳)是對的,只是區分方式跟鄰居不同。⚠ 若編排者認為 kind 擴充算「第二種做法」,可升 major;我判 minor 因為沒有哪個消費端會因此壞。

## F3 修正關卡新增的配方掃描讀主工作目錄的設定,鄰居讀樹裡那份
severity: minor
blocking: 否
引句:「配方平台的 repo 最上層要等於修正關卡的 repo 最上層(不同 repo 的跳過,免得同名路徑誤報)」
file: `scripts/lumos:14908-14911`(`_kill_check_ctx` 以 `repo_root` 讀設定)
file: `scripts/lumos:12012-12016`(fix-check 以 `tree / ".lumos" / "config.json"` 讀「提交裡那份」設定,並在設定有未提交改動時提醒)
file: `scripts/lumos:12047`(`pdata = load_platforms(tree)`)
1. `cmd_loop_fix_check` 其他每一項都讀隔離工作樹裡的設定(r3 已明講「設定讀樹裡那份」),並對沒提交的設定改動加提醒。
2. 本份用 `_kill_plat_top` 需要 `_kill_check_ctx(repo_root)`,那是以主工作目錄讀設定、讀不到才報錯,跟 fix-check 已建好的 `pdata`/`plats` 是兩份。
3. 同一個指令裡「平台根在哪」會有兩個來源,可能互相不一致(主工作目錄設定有未提交改動時)。設計沒講要用哪份,也沒講跟鄰居不同的理由。

## F4 「檔有沒有改過」另寫一支 git 呼叫,而且 PRIOR-ART 仍寫沿用 `_codeloop_record_valid_ex`
severity: minor
blocking: 否
引句:「判法:用配方平台的 repo 最上層(`_kill_plat_top`)跑 `git diff --quiet <head_sha> HEAD -- <file>`;非 0 或出錯都算改過」
file: `scripts/lumos:40384`(`_codeloop_record_valid_ex`:同類問題「這筆紀錄之後有沒有動代碼」的既有做法)
file: `scripts/lumos:31453`(`_lens_git(root, "--literal-pathspecs", "diff", "--no-ext-diff", "--no-textconv", "--quiet", "HEAD", "--", gp)`:單一檔 diff --quiet 的既有寫法)
file: `scripts/lumos:41010-41030`(`_backing_valid_rows`:同一份帳本、同樣的 cache 與 deadline 寫法)
1. 「判單一檔從某版本到 HEAD 有沒有改」專案裡有一個現成寫法(`_lens_git` 帶 `--literal-pathspecs --no-ext-diff --no-textconv`,理由寫在註解:檔名含 `*` 不當萬用字元)。設計寫的 `git diff --quiet <head_sha> HEAD -- <file>` 沒帶這些旗標,等於另寫一份;配方的 `file` 是人手寫的欄位,含萬用字元時行為會跟鄰居不同。
2. 計劃開頭 PRIOR-ART 一行仍把 `_codeloop_record_valid_ex` 寫成「之後只動簿記檔」判法的沿用對象,但〈做法〉已改成不用它。兩處說法對不上,下一個讀者會以為有沿用。
3. 語意上不同(整版有沒有動代碼 vs 單檔有沒有改)所以不另起第二種做法到 major,但要在計劃裡寫明為什麼不用既有零件,並沿用 `_lens_git` 的旗標。

## F5 「每條配方取最後一筆」在計劃裡新寫一份,沒抽共用
severity: minor
blocking: 否
引句:「每條配方取**檔內順序最後一筆**(跟合約背書 `_backing_judge_groups` 一致,不比 `ts`)」
file: `scripts/lumos:41034-41040`(`_backing_judge_groups` 內部先 `groups.setdefault(r["recipe_id"], []).append(r)` 再取 `groups[rid][-1]`)
file: `scripts/lumos:13833-13836`(`_kill_recipe_key` 註解:「三處都用這一支(別各寫一份比對)」,是本專案對這類同義邏輯的既有態度)
1. 語意(檔內順序最後一筆、不比 `ts`)跟鄰居一致,這是好的。
2. 但 `_backing_judge_groups` 是把分組內嵌在判題函式裡,設計沒說要把「分組取最後」抽出來,等於 P2 新寫一份同語意的程式。日後有人改一邊(例如改成比 `ts`)另一邊不會跟著動。
3. 需要在計劃裡二選一:抽一支共用的「按配方身分取最後一筆」,或寫明兩邊刻意各寫一份並綁一條對照測試。

## F6 `_kill_p2_skips` 的名字與範圍:三處新用,舊的內嵌複本仍在
severity: minor
blocking: 否
引句:「抽成 `_kill_p2_skips(note)`,P2、survived 清單、修正關卡提醒三處共用,行為不變」
file: `scripts/lumos:2910-2911`(doctor P 段內嵌同一個 verification 型、superseded、stale 判斷)
file: `scripts/lumos:2390`、`scripts/lumos:2450`、`scripts/lumos:2488`(同一句 `status ... in ("superseded", "stale")`)
file: `scripts/lumos:14186-14190`(`_kill_p2_scan` 內嵌那份;註解寫「跳過的節點逐字照 P 段」)
1. 這條規則在專案裡已經內嵌了 5 份,P2 註解還特別寫「逐字照 P 段」。本份只抽 P2 這一份,P 段與其他段維持內嵌,結果是「照 P 段」變成兩處不同寫法(一個函式、一個內嵌)。
2. `_kill_p2_skips` 還多一條「沒有 `kill_recipes` 欄」,P 段沒有,所以不能直接說行為同 P 段。
3. 名字帶 `p2`,但要被修正關卡呼叫;鄰居的 `_kill_*` 家族有 `_kill_list_cell`、`_kill_rel` 這種不帶 p2 的通用名。結構沒壞,只是命名範圍與註解的「逐字照 P 段」要同步改。

## F7 動 `cmd_guard_kill` 跟姊妹計劃「不改它」的既有立場相反,舊句沒列入要同步的文件
severity: minor
blocking: 否
引句:「判法、回傳碼、kill-log、`--json` 都不變」
file: `scripts/lumos:13857`(「★判法逐項對齊 cmd_guard_kill,但不改它★」)
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:35`(「guard kill 本身一行不改,判斷函式重演它的走法」)
file: `scripts/lumos:14823-14824`(`cmd_guard_kill` 現行簽名只有 `invariant_substr, platform_override, as_json, keep_worktree`)
1. 前一份計劃(殺傷力配方失配提醒)刻意不動 `cmd_guard_kill`,理由是它的圍欄與回傳碼有既有合約與測試。本份加了兩個選用參數與一個過濾,新參數不給時行為不變,這個做法沒問題。
2. 但那兩句「不改它」會變成過時的說法,而〈要同步的文件〉只列了 CLI 一節補 `--id`、`--try`,沒列這兩句。
3. 過濾位置「合約片段過濾之後」跟既有 `invariant_substr` 過濾同處(`scripts/lumos:14842-14843`),落點與鄰居一致。

## F8 新旗標的 argparse 命名跟鄰居的 dest 前綴慣例不同
severity: minor
blocking: 否
引句:「帶 `--try`:寫入成功(含只更新 covers)後」
file: `scripts/lumos:42403-42418`(kill-add:`--platform` 的 dest 是 `gk_platform`;kill-rm:`--id` 的 dest 是 `gkr_id`)
file: `scripts/lumos:42419-42424`(kill:`--json` 的 dest 是 `gk_json`)
引句:「新旗標 `--id`(可重複,也收逗號分隔)」
1. 這組子命令的旗標一律帶子命令前綴的 dest(`gk_`、`gkr_`),避免 `args.` 屬性撞名。`--try` 的 `try` 是 Python 關鍵字,`args.try` 語法就不合法,一定要給 dest;設計沒講。
2. guard kill 的 `--id` 若不帶前綴 dest 會跟 kill-rm 的 `gkr_id` 命名不對稱;設計也沒講 `--id` 的 dest(`action="append"` 加逗號拆分在這一組沒有先例,kill-rm 只收單一值)。
3. 只是命名,但規格沒寫,實作者會各猜各的。

## F9 「經 warn_box 帶完整身分」跟 warn_box 現況不符
severity: minor
blocking: 否
引句:「寫入鎖裡已經算出這條的完整身分(判重用的那把),經既有的 `warn_box` 帶到鎖外再取前 12 碼」
file: `scripts/lumos:14354`(`warn_box.append(recipe)`:放進去的是配方 dict,不是身分)
file: `scripts/lumos:14289`(鎖外 `for rec in warn_box ... _kill_add_warn(env, rel, rec)`)
file: `scripts/lumos:13859-13868`(`_kill_recipe_id(node, elem)` 是 P2、kill-add 提醒、kill-rm 共用的身分函式)
1. 現有 `warn_box` 帶的是這次實際寫進去(或只更新 covers 時指到的既有)那一條配方 dict,鎖內判重算的是 `_kill_recipe_key`,沒有存下來。
2. 照鄰居的做法,鎖外拿到 `rec` 後直接呼叫 `_kill_recipe_id(str(rel), rec)` 即可,不用改 `warn_box` 的內容。設計寫成「帶身分」會讓實作者去改 `warn_box` 的元素型別,動到 `_kill_add_warn` 的現有簽名。
3. 純說法不精確,結構對得上(沿用既有 out 容器、沿用共用身分函式)。

不對齊共 9 條,其中 major 0 條
最高等級:minor,blocking 共 0 條
