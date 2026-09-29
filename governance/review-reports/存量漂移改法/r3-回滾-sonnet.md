severity: major

# 第 3 輪 回滾席(sonnet)審查報告

## F1 〈回退〉只退指令文件,漏掉同節列的圖譜筆記、被改過的既有測試、以及被撤掉的 10/13 回頭條件
severity: major
blocking: 是 — 照〈回退〉字面退,圖譜筆記與防線計劃會繼續宣稱一個已不存在的指令與「缺口已處理」,原本 10/13 那條決定的回頭條件也不會回來,實作者會留下說謊的筆記
引句:「第 9 節改的指令文件(commands/04、INDEX、06、reference.md)一起改回」
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:247`
1. 〈做法〉第 9 節「同步改的筆記與文件」列了三類東西:五篇 Systems 筆記(存量漂移守衛、guard-kill、lumos-cli-write、lumos-cli-read、reversibility-governance-ledger)、`存量漂移防線_計劃` 的〈修復結果〉標成「已由本計劃處理」並「撤掉那條 10/13 的 REVISIT」、lumos-project-notes 的指令文件。〈回退〉只寫了第三類「一起改回」。
2. 我查了防線計劃第 247 行:`REVISIT:2026-10-13 決定這五項開不開新計劃…`。回退後這條被撤掉、沒有任何句子要求把它放回去;缺口段還寫「已處理」。CLAUDE.md 鐵則 4 說回頭條件要接電,這裡撤了卻不在回退清單。
3. 五篇 Systems 筆記(含將來〈合約候選〉填進去、綁 `[test:t_drift_fix_*]` 的合約行)回退後仍描述 `drift fix`、修復帳、settle 的 `--date`;合約綁的測試若隨程式一起拿掉,會變成懸空綁定(doctor 只提醒,但筆記已與程式不符,下一個 session 的 AI 會照抄)。
4. 第 9 節最後一條要改既有測試 `t_guard_settle_rewrites_planned_prose`、`t_guard_settle_recovers_half_done`(斷言改成新行為)。〈回退〉沒寫要把它們改回;程式退了、測試留新斷言,全套會紅。
5. 修法方向:〈回退〉補一句「第 9 節同步清單的每一項都要反向處理:五篇 Systems 筆記、防線計劃缺口段與 10/13 REVISIT、兩支既有測試」。

## F2 「git 一定退得回去」的前提(先確認沒有未提交改動)有兩個洞:未追蹤的新筆記、鎖外檢查後被插手
severity: major
blocking: 是 — 〈回退〉與〈實務隱患〉的不可逆防法整個押在這一步,兩個洞都讓「一定」不成立,實作者照字面做會給出退不回去的保證
引句:「先確認那一篇在 git 裡沒有未提交的改動(工作目錄與暫存區都乾淨;有就回 2」
file: `scripts/lumos:26078`(`_drift_state_findings` 掃的是磁碟上所有筆記,包含還沒進 git 的)
1. 未追蹤:「工作目錄與暫存區都乾淨」若照字面用 `git diff --quiet` 與 `git diff --cached --quiet` 實作,對從未提交過的新筆記兩者都回 0(我在臨時 repo 實測:新檔 `n.md` 兩條都 rc=0,`git status --porcelain` 才顯示 `?? n.md`,`git checkout -- n.md` 回 rc=1「pathspec did not match」)。也就是新筆記通過第 1 步,修完後沒有任何 git 版本可以退。同一個 session 剛開的 Issue 走 c2 --close、剛開的驗證紀錄走 c3,正是這種情況。spec 沒寫「未追蹤算髒」,也沒寫被 .gitignore 掉的路徑怎麼辦。
2. 鎖外檢查後被插手:這個檢查在第 1 步(鎖外),第 3 步拿鎖後只重載圖譜、重判發現,沒有再檢查一次「還乾淨」。另一個會談(CLAUDE.md 記憶裡「同工作區有別的會談」就是常態)在第 1 步與第 3 步之間對同一篇做了未提交修改:fix 會以那份未提交內容為底寫入,之後 `git checkout` 那一篇會連對方的未提交修改一起沖掉。第 5 步的指紋比對只管「寫入之後」的插手,管不到「寫入之前」。
3. 修法方向:未追蹤(`??`)、intent-to-add、gitignored 一律當髒回 2;第 3 步鎖內再確認一次這篇對 HEAD 沒有差異。

## F3 修復帳「要退靠 git」的說法也套在 `via: guard settle` 的紀錄上,但 settle 那條路沒有乾淨檢查
severity: minor
blocking: 否 — 只影響「照帳退回」的期望,不會做出壞資料;不改,實作者只是誤以為 settle 補改的紀錄也有乾淨前提
引句:「第 1 節第 1 步確認過改之前沒有未提交的改動,所以一定退得回去」
1. 帳的 `via` 欄有 `guard settle`(〈做法〉第 7 節),第 3 節對 pass 補改「鎖的順序跟 fix 一樣」,但乾淨檢查只寫在第 1 節 fix 的第 1 步,settle 沒有。
2. settle 常在人剛手改家節點與守衛紀錄之後跑(未提交),那時補改句子再提交,git 還原那個提交會連人的手改一起退掉;第 7 節那句「一定退得回去」對這類紀錄不成立。
3. 修法方向:第 7 節那句限定「`via: drift fix`」,或 settle 補改也做同一個乾淨檢查。

## F4 〈回退〉沒列共用函式與既有 `drift ack` 的行為改動
severity: minor
blocking: 否 — 留著多半無害,但回退清單不完整,退完後既有指令行為與退之前的版本不同
引句:「順手讓表態檔的寫入也做同一個檢查」
file: `scripts/lumos:8511`(`_jsonl_append_verified`,canary、表態檔、治理帳共用)
1. 第 7 節改了 `_jsonl_append_verified`(追加前補換行,「表態檔、治理帳等共用這支的一起受益」)、表態檔寫入加符號連結檢查;第 8 節讓 `drift ack --kind c2|c3` 拿鎖、鎖內重判、不是那種發現就回 2。〈回退〉只涵蓋 `related` 與「舊表態不再算數」,這三處沒有一條說要不要退。
2. 影響:退掉 fix 後,`drift ack` 仍會因符號連結檢查或「這行現在不是 c2」而回 2,而這些是新指令上線前沒有的行為;沒寫「可以留著、行為不變」也沒寫「要退」,實作者無從判斷。
3. 修法方向:三處各補一句留或退,並註明留著時對既有呼叫者的可見差異。

## F5 符號連結檢查的「上層目錄」沒有界定到哪一層,可能把合法環境全擋掉
severity: minor
blocking: 否 — 只擋新加的檢查所涵蓋的寫入;⚠ 依實作解讀不同,尚未能證明會誤擋
引句:「本身與上層目錄都不是符號連結(是就回 2)」
file: `scripts/lumos:27101`(`cmd_drift_ack` 現況以 `resolve()` 兩邊都解開再比,不擋符號連結)
1. 現況 `cmd_drift_ack` 用 `env.vault.resolve().relative_to(Path(root).resolve())`,能容忍 repo 放在符號連結底下(macOS 的 `/tmp` 就是 `/private/tmp` 的連結)。新檢查「上層目錄都不是符號連結」若查到檔案系統根,就會擋掉這類使用者的既有 `drift ack`(向後相容退步);若只查到 repo 根,要寫明。
2. 「解析後的真實路徑要在 repo 根底下」也沒說 repo 根本身要不要先解析;一邊解析一邊沒解析會在符號連結環境誤判。⚠ 需要實作者釘一個定義。
3. 修法方向:寫明檢查範圍是「repo 根(已解析)到帳檔之間」的每一層,repo 根以上不查;並加一條測試:repo 在符號連結目錄下,`drift ack` 與 `drift fix` 仍能寫。

## F6 c1 寫錯轉正日期之後沒有更正路徑,〈回退〉也沒交代
severity: minor
blocking: 否 — 錯日期是可預期的殘餘風險,已列在誠實界線;缺的只是事後怎麼改,不改不會做出壞系統
引句:「推出來的日子會不對或推不出,這種要人給 `--date`」
1. 誠實界線承認壓提交、改名會讓推出的日期偏差。但 c1 一旦改完,預告句已變成「(日期 已轉正)」等歷史說法,`_drift_guard_findings` 對 pass 紀錄只在還有預告句時才出 c1(scripts/lumos:26129 附近),所以同一篇不會再出現 c1;第 1 節第 3 步「指定的行要還是這一種發現」也會讓 `drift fix --kind c1` 回 2。
2. 結果:寫錯的日期只能手改,修復帳只告訴你改了哪行;〈回退〉的「不用還原」沒提這件事。
3. 修法方向:界線補一句「改錯日期靠手改那一行,帳的 `changed` 給出位置」。

## F7 「沒記 related 的舊表態不再算數」對歷史視角(`drift scan --at`、`drift exam --history`)的影響沒交代
severity: minor
blocking: 否 — 只影響回看舊提交的診斷輸出,不擋推送(c2 到 c5 只列出不擋,已查 `_drift_check_core`)
引句:「取 `ts` 最新的那一筆,它的 `related` 涵蓋現在的清單(現在的是它的子集)才算已表態」
file: `scripts/lumos:27292`
1. `cmd_drift_scan` 用 `_drift_load_acks(root, sha)` 讀某個提交的表態檔再 `_drift_split_acked`。新規則下,舊提交裡所有沒記 related 的 c2/c3 表態都不算數,`drift scan --at <舊提交>` 與逐提交重放會把當時已表態的 c2/c3 全部重新列成「沒表態」,歷史數字(含防線計劃 RETIRE-IF ①要量的「表態照留比例」)口徑跟著變。
2. 修法方向:界線補一句,或歷史視角對沒記 related 的表態沿用舊比對並標註。

## 已讀,無 finding

- 〈回退〉第 4 點(c2/c3 表態的 related 回退)的技術前提「`_drift_load_acks` 整行原樣回傳、下游只取 path、text、kind、reason」:已核對 `scripts/lumos:27051`(整個 dict 原樣回)、`_drift_split_acked`(只取 path/text/kind)、`_drift_old_reason`(只取 text/kind/reason/path),成立;舊版讀新欄位不會壞。
引句:「已寫的欄位留在表態檔裡無害(`_drift_load_acks` 整行原樣回傳、下游只取 path、text、kind、reason)」
- 〈回退〉第 5 點 `_KNOWN_GATES` 的 drift-fix 留著無害:已核對 `scripts/lumos:1154`(只在寫入端檢查閘名)、`scripts/lumos:6981`(只多列在「沒觸發過的閘」),舊版讀到帳上的 drift-fix 事件不會出錯。
引句:「`_KNOWN_GATES` 的 drift-fix 留著無害」
- 〈回退〉第 3 點 E5 標記、`_revisit_lines`、set 列出:純多印,已讀,無 finding。
引句:「純重構加多印,回退就是拿掉印出;`_revisit_lines` 可以留著(行為不變)」
- 舊版 lumos 遇到 `drift fix` 子命令:現況 argparse 對未知子命令直接報錯(`scripts/lumos:36524` 的 `drsub` 只有 check/scan/ack/exam),舊版不會把 fix 當 ack 執行;spec 說的「fix 會被當成 ack」只在加了 fix 子命令而分派沒改時才成立,不影響回退。
引句:「`drift` 子命令現在「不是 scan 就當 ack」」
- 實務隱患逐類:守衛面誤擋漏擋(c2 到 c5 在 check 只列出、不擋,上線時舊表態重列只影響顯示,無);併發(見 F2);效能(一次一篇,無);向後相容(見 F4、F5、F7);不可逆(見 F2、F3、F6)。

最嚴重等級為重大,blocking 共 2 條。
