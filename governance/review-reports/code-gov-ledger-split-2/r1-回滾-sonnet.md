severity: major

## F1 〈回退〉寫「還原單一功能提交」,但現況是五個提交,單獨還原功能提交會在程式與帳檔上衝突
severity: major
blocking: 是
引句:「GOV_LOCAL_LOG_NAME = ".governance-local.jsonl"」
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:104`
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:88`
失敗場景(已在臨時 clone 實跑,未動 repo 根):
1. 分支 91f4b29e..HEAD 現有五個提交:c860d399 feat、4daf83b6、063ec29f、35c4ac3d、88e51555 三輪折入的 fix。〈回退〉和〈實務隱患〉回滾寫的是「還原本案提交即可」「還原本案的單一功能提交」。
2. 在 clone 裡 `git checkout 88e51555 && git revert --no-commit c860d399`,衝突清單有 `scripts/lumos`、`scripts/test_lumos.py`、`docs/.governance-log.jsonl`、`governance/anchor-baseline.json`、`reversibility-governance-ledger.md`,另有「治理帳例行紀錄分流_計劃.md」是 UD(修改對刪除)。scripts/lumos 內有 `<<<<<<< HEAD` 標記(1310、1467、1544 行附近),`ast.parse` 直接 SyntaxError。
3. 只有 `git revert 91f4b29e..88e51555` 整段還原才無衝突。但帳檔 `docs/.governance-log.jsonl` 與 `anchor-baseline.json` 是每次提交、推送都會追加的檔,只要主線上本案之後又有任何會寫帳的提交,即使本案壓成一個提交,還原它也會在帳檔尾端衝突(追加行相鄰)。
4. 一旦衝突,救援靠人手動解。誤解成 ours 或 theirs 會吞掉擋人紀錄、代碼審留痕,那正是 CI 唯一權威來源,而且當下沒有機器檢查。
5. 〈回退〉沒有講整段還原的範圍寫法,也沒有講帳檔衝突怎麼解。照字面做會卡在半途。
修法方向:〈回退〉改寫成「還原範圍 + 帳檔衝突取兩邊聯集」,或確認推送前壓成單提交並註明帳檔衝突要聯集解。

## F2 回退前「先刪本機帳」只靠人記得,還原後簿記白名單跟著消失,沒有機器守衛
severity: minor
blocking: 否
引句:「"docs/" + GOV_LOCAL_LOG_NAME, "docs/" + USAGE_LOCAL_LOG_NAME,」
file: `/home/user/Lumos/scripts/lumos:24403`
失敗場景:
1. 還原之後根 `.gitignore` 的兩行與 `_BOOKKEEPING_FILES` 的兩個新檔名一起消失。每個 worktree、每台機器上的本機帳變成未追蹤檔。
2. 舊版程式不認得它們,不會提醒。使用者 `git add -A` 就把它們提交進版控,路徑與節點名這類本機紀錄從此進了 git 歷史。
3. 另外,它們不在還原後的 `_BOOKKEEPING_FILES` 裡,所以在代碼審通過之後提交,會讓代碼審留痕被當成「中間動過非簿記檔」而失效,要重審或重跑。後果是能救回來的(`git rm --cached`、重審),所以只標輕微。
4. 〈回退〉的緩解只有一段文字。這是在回退本身,沒有任何程式守衛。

## F3 讀檔尾改丟錯後,度量暖機起點在「兩筆都夠舊或只剩一筆有效」之外仍有卡死情況(不阻擋)
severity: minor
blocking: 否
引句:「return evs, (two[1] if len(two) == 2 else None)」
file: `/home/user/Lumos/scripts/lumos:3948`
失敗場景:
1. 帳裡只有一筆有效的舊紀錄加一筆 2099 年的壞時間,`nsmallest(2)` 回 [舊, 2099],暖機起點是 2099,護欄永遠不放行,該閘的度量式撤除條件永遠不判。
2. 版控帳是只追加的,那筆壞行刪不掉。
3. 只影響本機 doctor 的軟提醒(`--ci` 不跑 S18),方向偏保守,所以標輕微。
新舊版本並存:舊版取第一筆、新版取第二早,同一本帳在一台新機器和一台舊機器上可以得出不同的「判/不判」。這只會影響軟提醒,不影響擋人。

## 已走過沒問題的範圍
- 判定類讀者(`_fix_check_events` 12503 行附近、`_codeloop_read_dispositions` 43508 行附近、`_loop_close_stamps`、`_escape_released_loops`、`cmd_loop_rewrite` 血緣)都仍讀版控帳字面路徑。本案新增的例行事件不會讓任何擋人判定從擋變放,新舊版本與 CI 版本不同時判定一致。
- `_local_ledger_writable` 三支寫入器共用。本機帳是捷徑或管線時只是不寫,`_gate_event` 回 False 時只印 telemetry-write-failed,不改閘判定。
- `_ensure_docs_gitignore` 只追加、不動使用者已有的行。還原後多出的兩行無害,也不會把另外五本進版控的帳忽略掉(只放本案兩行)。這一步不是不可逆。
- `_gov_tail_bytes` 改丟 OSError 後,兩個呼叫端(2365 行 doctor 帳增速、`_gov_metric_events`)都在外層廣域 except 之內,不會讓 doctor 中斷。
- 舊使用紀錄帳 `.usage-log.jsonl` 凍結不刪,別台機器 pull 不會刪檔。
- 圖譜鏡頭:派工訊息沒有附 LUMOS-IMPACT 固定席筆記尾段,所以無法逐條答固定席。我只照計劃筆記的〈回退〉〈實務隱患〉〈天花板〉對現況代碼核對。三者中〈回退〉的「單一功能提交」與現況不符(F1),其餘照程式現況做得到。〈天花板〉第 2 點(舊版 `--nags` 與 S18 少報、多報)與程式一致。

總結:回退路徑文字與實際提交結構不符,單獨還原功能提交會在程式與帳檔衝突,其餘回滾面可行。
