severity: minor

## F1 補忽略行遇到不動的情況完全無聲,doctor 卻叫人跑 lumos update,跑了也不會好
severity: minor
blocking: 否
引句:「if gi.is_symlink() or not gi.is_file() or gi.stat().st_nlink > 1:」
file: `/home/user/Lumos/scripts/lumos:21044`(`_init_additive_setup` 呼叫 `_ensure_docs_gitignore` 的那一行,回傳值整個被丟掉)
file: `/home/user/Lumos/scripts/lumos:2415`(doctor 的提示文字寫「帳在 docs/ 的跑一次 lumos update 補忽略規則」)
失敗場景:
1. 消費專案的 docs/.gitignore 是捷徑(例如 monorepo 共用一份)、硬連結、唯讀或非 UTF-8。
2. 使用者升級工具後跑 lumos update:`_ensure_docs_gitignore` 走到上面那行直接 return [],沒印任何一個字。
3. docs/.governance-local.jsonl 在下一次提交就出現,是未追蹤檔;doctor 的軟提醒叫他再跑 lumos update,他再跑一次仍然是無聲的什麼都沒發生。提示指向的修法對這群人永遠無效,真正要做的(手動往那份檔加兩行)只出現在函式 docstring 裡,使用者看不到。
4. 這群人此時若 git add -A,本機帳就被提交進版控,之後兩台機器各自追加同一個 jsonl,pull 時合併衝突(忽略規則對已追蹤檔無效;doctor 只會提醒 git rm --cached,歷史已進去)。
回滾面:不涉及不可逆動作,是「回得去但沒人告訴你怎麼回」。計劃〈做法〉5 寫了「交給 doctor 提醒」,但 doctor 的提醒文字沒分這四種情況。
未能重現為整條流程(沒有在對話裡裝出捷徑版 docs/.gitignore 跑 doctor);delta 測試 `t_gov_split_review_r1_fixes` 已證實捷徑情況回 [] 且不動檔,提示文字不分情況是讀程式所得。

## F2 新舊版本交界:專案還沒跑 lumos update 時,本機帳可被一個 git add -A 永久帶進版控,沒有提交前的攔阻
severity: minor
blocking: 否
引句:「docs/" + GOV_LOCAL_LOG_NAME, "docs/" + USAGE_LOCAL_LOG_NAME,」
file: `/home/user/Lumos/scripts/lumos:24373`(只把兩個新檔名加進 `_BOOKKEEPING_FILES`,讓代碼審留痕不失效;沒有任何地方在提交前拒絕或自動退出暫存這兩個檔)
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:74`(計劃承認「全域工具更新後到專案跑 lumos update 之前,本機帳會以未追蹤檔出現」,只說偏吵)
失敗場景:
1. 消費專案的全域工具先更新、專案的 docs/.gitignore 還沒補行(或是 F1 那四種不補的情況)。
2. 這時第一次 pre-commit / pre-push 就會往 docs/.governance-local.jsonl 寫,成為未追蹤檔。
3. 使用者(或雲端工作階段)下一次 git add -A,檔進版控、之後忽略規則對它無效。
4. 兩台機器各自往同一個 jsonl 尾端追加,pull / rebase 時每次都衝突;還原本案提交也不會把它從歷史拿掉。_BOOKKEEPING_FILES 只保證代碼審留痕不因此失效,保不了這件事。
回滾面:這個「已被追蹤」的狀態只有 `git rm --cached` 能退,doctor 有提醒(`_local_ledger_doctor_msgs` 的 tracked 分支),所以可救、不是資料遺失,故列 minor。

## 圖譜鏡頭(LUMOS-IMPACT 固定席,分組摘要)
- 帳檔與回滾直接相關的席:Systems/reversibility-governance-ledger(RISK 守衛面)、Systems/lumos-cli-read(usage-local 改名)——筆記已更新到七來源與 usage-local,count 標記與程式 `load(` 行一致,與程式現況相符;判定類讀者(`_codeloop_read_from_ledger`、`_codeloop_read_dispositions`、`_fix_check_events`、`_loop_close_stamps`、`_escape_released_loops`、cmd_loop_rewrite 血緣、replay_weekly.py)我逐一讀過,都只讀版控帳且只認 code-loop、fix-check、design-loop 的事件,這三個閘不在 `_GOV_LOCAL_PAIRS`,守衛面沒被破壞。
- Systems/pitfalls-code-loop(RISK 守衛面,簿記白名單 KEY 行 33、36):程式已把兩個新檔名加進 `_BOOKKEEPING_FILES` 與 cochange 排除表;該筆記的 KEY 行仍只列「治理帳/usage-log/ci-log…」未提新檔名,屬文字落後(新檔被忽略,實際只在 F2 的情況才會被掃到),不影響行為。
- Systems/lumos-cli-lifecycle:★DEBT★ 行 31 說來源 repo 的 docs/.governance-log.jsonl 等簿記檔「恆髒」——分流後例行寫入不再弄髒它,該句描述已部分過期(程式 `_pull_source_or_abort` 的聯集合併清單沒動,仍涵蓋舊帳,行為安全)。以程式碼為準,不影響結論。
- Systems/lumos-deinit(RISK 不可逆):deinit 程式對 docs/ 下的帳檔與 docs/.gitignore 沒有逐檔處理;新本機帳與補的兩行 ignore 在 deinit 後留在原地,無害也不被誤刪,與本案無衝突。
- Systems/bound-tests-gate(INVARIANT)、canary-audit、design-loop、loop-convergence-recording、guard-kill、授權與歸屬、測試假綠形態、slim-* 與其餘固定席:本 diff 沒碰它們的寫入點;bound-tests 事件全數留在版控帳(計劃與程式 `_GOV_LOCAL_PAIRS` 一致,沒有 bound-tests 條目),canary 與 kill 帳沒動,無牽連。

## 已走過沒問題的範圍
- 分流判定 `_gov_routes_local`:gate、kind 非字串、hard 非恰好 False 都回 False 進版控帳;`_gate_event_build` 的 hard 一定是 bool,extra 蓋欄位的呼叫點沒看到會蓋 gate/kind/hard 的。
- 本機帳寫不進去:`_append_governance_log` 兩本各自 try、`_gate_event` 回 False,版控帳不受牽連。
- 回滾(〈回退〉與〈實務隱患〉):還原提交會讓根 .gitignore 兩行消失,計劃已要求先移走兩本本機帳,每個 worktree 與機器各做一次,與程式現況一致;舊版 `_usage_log` 會回頭寫已凍結的 .usage-log.jsonl,不衝突;消費專案 docs/.gitignore 多出的兩行無害。
- 新舊版混用:判定類讀者在新舊版讀的是同一本版控帳、讀的事件種類沒被分流,CI 版本不同不會導致 code-loop 留痕或修正關卡判定不一致;只有統計類(--nags、S18)會因舊版看不到本機帳而少報或多報「該撤」,計劃已寫明且 S18 是軟提醒。
- S18 暖機:本機帳不在、剛建、或被刪都不判;第一筆取法與 `_gov_ts` 的出界擋掉我讀過沒有溢位路徑;新增白名單組合時兩本事件合併計數,不會少算。
- `_ensure_docs_gitignore`:追加不替換、CRLF 與缺尾換行處理、硬連結與捷徑不動、O_EXCL 新建;鎖用 `~/.cache/lumos/vault-lock/`,正常路徑不在使用者 docs/ 留殘檔(退路才落到 docs/ 內,屬既有共用寫法)。
- 讀者只讀一般檔案(管線、特殊裝置檔不讀)、`_usage_log` 與兩支寫入器不跟捷徑寫。

總結:沒有不可逆動作與判定面的新舊不一致,回退步驟與程式現況相符;剩下兩個邊角是補忽略行在不動的情況下提示無效、以及未補忽略行期間本機帳可被誤提交,皆可用 git rm --cached 救回。
