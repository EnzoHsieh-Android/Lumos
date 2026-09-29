severity: major

# 架構對齊審查(r3 快照;對照 clone-ns 的 scripts/lumos)

四問結論(逐問;細節在下面各 finding):
1. 分層與依賴方向:drift 區段呼叫 guard 區段的既有做法(`_drift_guard_findings` 讀 `_guard_planned_prose`、`_guard_formal_line`)方向一致;但 `guard settle` 對 pass 節點改走 drift fix 的 c1 那支(含修復帳),會第一次讓 guard 區段反向依賴 drift 區段,見 F2。
2. 命名與錯誤處理:函式與常數命名(`cmd_drift_fix`、`_DRIFT_FIXES`、`_revisit_lines`、`DFIX-` 8 碼對齊 `DACK-`)與鄰居一致,回 2 加「擋下:」訊息一致;`--why`/`--reason` 混用、`ts` 格式未指定、閘名另開,見 F5、F7、F8。
3. 第二種做法:符號連結防護第三種寫法(F1)、狀態寫入四份手寫(F3)、提示指令文字五處各寫(F4)、git 呼叫兩種風格(F6)、追加寫入兩條路(F10)。
4. 落點:lands_in 五篇對得上主要動到的家,但改到共用寫入原語與簿記名單卻沒列它們的家,見 F9。

## F1 修復帳的符號連結防護是專案裡第三種寫法,而且沒說放在哪一支
severity: major
blocking: 是 — 不指定就是每個接手的人在三套防符號連結的寫法之間猜,而且新一套比舊兩套多擋上層目錄、卻仍是先查再開檔
引句:「寫之前檢查帳檔、以及它解析後的真實路徑要在 repo 根底下、本身與上層目錄都不是符號連結(是就回 2)」
file: `scripts/lumos:7875`
file: `scripts/lumos:15557`
1. 現有做法一:`_escape_log_guard(log)`(7875)在寫逃逸帳前 `log.is_symlink()` 就擋,回 0/2,逃逸帳手動記帳與撤回共用;註解自承「判斷與開檔間競態」。
2. 現有做法二:`_ledger_append`(15557–15567)用 `O_NOFOLLOW` 在開檔那一刻拒絕連結終點,沒有先查再開的空窗。
3. 讀取端還有第三個零碎寫法:`_drift_load_acks`(27058)遇到連結就當沒有檔。
4. spec 這句要求的是第四種組合:`resolve()` 後在 repo 根底下、本身與每一層上層目錄都不是連結,且沒有指定寫成獨立函式、放進 `_jsonl_append_verified`(共 5 個以上呼叫端:canary、逃逸帳、規格閘去重、drift ack)、還是只在 fix 與 ack 兩處各自檢查。「順手讓表態檔的寫入也做同一個檢查」同樣沒說落在 `cmd_drift_ack` 還是共用寫入原語。
5. 判準:這件事專案已有兩種既有寫法,spec 加第三種且不說怎麼收斂,後面的人無法判斷新增第五個帳檔時該抄哪一支。要對齊就得在 spec 裡點名:擴充哪一支既有函式(例如把上層目錄與 resolve 檢查併進 `_escape_log_guard` 那一類、寫入端改 `O_NOFOLLOW`),舊的呼叫端一起受益。

## F2 `guard settle` 對 pass 節點要呼叫 drift fix 的 c1 那支,方向跟現況相反 ⚠
severity: major
blocking: 是 — 這是新的跨區段依賴方向;不指定共用函式放哪,實作者會讓 guard 區段直呼 drift 區段(含寫修復帳與治理事件)
引句:「還有預告句就走第 2 節同一支(前提、日期、不疊、修復帳 `via: guard settle`)」
file: `scripts/lumos:12195`
file: `scripts/lumos:26122`
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:6`
1. 現況方向:drift 區段(26122 的 `_drift_guard_findings`)呼叫 guard 區段的判準;guard 區段(12086–12360)整段沒有任何 `_drift_` 呼叫(我對 11900–12700 行 grep 結果為空)。
2. spec 第 2、3 節要讓 `cmd_guard_settle`(12195)的 pass 分支走「第 2 節同一支」,而那一支要做的事包含:`_drift_state_findings` 重判、修復帳(`via: guard settle`)、治理事件、`_DRIFT_FIXES`——全是 drift 區段的東西。
3. 圖譜也把責任切在這裡:存量漂移守衛的 responsibility 明寫「不負責 guard settle 本身(guard-kill)」。settle 的 pass 分支歸 guard-kill,卻反過來依賴存量漂移守衛家裡的實作,兩個家互相依賴。
4. spec 沒說「同一支」是放在哪個區段、誰呼叫誰。合理的對齊做法是:改句與轉正日期推導(`_guard_settle_rewrite` 系列)留在 guard 區段,drift fix 與 settle 都往下呼叫;寫修復帳的那一步由各入口自己呼叫。⚠ 這是依現況方向推的,spec 若有意讓兩區段互相呼叫,要明寫並在兩個家節點各補一句。

## F3 「改 status 加同步標籤並驗證」會有四份手寫,spec 只點名原語沒點名共用支
severity: minor
blocking: 否 — 結構是對的(用的是鄰居同一組原語),只是差一支共用函式,漂移風險由測試而非機械守
引句:「寫入:status 用 `edit_fm_scalar` + `edit_fm_sync_status_tag`;正文最後加一行,文字依狀態」
file: `scripts/lumos:14846`
file: `scripts/lumos:12297`
1. 現況已有兩份:`_cmd_set_locked`(14841–14857)與 `_guard_settle_record`(12302–12313)各自寫了「`edit_fm_scalar`→`edit_fm_sync_status_tag`→檢查 status 與 `status/*` 標籤一致」的 `_check`/`_ok` 閉包,兩份幾乎逐字相同。
2. spec 再加 c3 一份、c2 `--close` 一份(c5 走 `_guard_settle_record_lines`,算內容那段共用,但 status 檢查閉包仍在寫入端);等於這個檢查閉包出現四到五次。
3. 這是「鄰居本身就這樣」(⚠),但 spec 把它擴成第三、第四份,而且新增的兩份還要加「正文最後一行」的共同規則(c2 明寫「照第 5 節 c3 的規則」),那一塊倒是有共用意圖卻沒點名共用函式名。
4. 對齊做法:抽一支「給舊行、狀態值 → 新 frontmatter 加一致性檢查」與一支「正文最後加一行」的共用支,c2、c3 共用;`_cmd_set_locked` 與 `_guard_settle_record` 是否一併改回收,spec 沒說。

## F4 c1–c5 的指令提示文字在五處各寫一份,沒有單一產生處
severity: minor
blocking: 否 — 結構對(提示只是文字),但指令語法(c2 兩條、c3 帶 `--status <值>`、c1 每篇一條)一改,五處要同步,靠單一測試名守
引句:「訊息應指到 `lumos drift fix` 指令(c1 每篇一條),不再教人手改」
file: `scripts/lumos:27246`
file: `scripts/lumos:26145`
1. 現有提示寫法:`_drift_report_must`(27226 起)自己組「預告句那幾筆」與 `lumos drift ack <節點> <行號> --kind {k}` 那行;`_drift_plan_followups`/`_drift_print_followups`(26149、26193)另有一套;`_drift_c5` 的 why 文字(26145)還寫著「重跑 lumos guard settle 補完」;scan 輸出(`_drift_scan_print`)與 doctor Z 段(`_drift_doctor_lines`)又各一套。
2. spec 第 9 節列了這五個地點要改成指到 fix,S10 用單一條款綁一個測試,但沒指定「給一筆發現 → 回應該跑的指令」的單一函式。c1「一篇一條」、c2 印兩條、c3 帶佔位這三種規則寫到五處,漂移時測試只驗其中幾處。
3. 對齊做法:一支 `_drift_fix_hint(finding)` 之類的產生函式,五個地點都呼叫它;此外 c5 的 why 文字(26145,存進發現物、之後在 check/scan/doctor 都會印)也要改,spec 第 9 節沒列這一處。

## F5 修復帳事件另開閘名 `drift-fix`,同一族的表態事件卻記在 `drift-check`
severity: minor
blocking: 否 — 不影響行為正確,只影響治理統計把同一批「人處理漂移」的事件拆成兩個閘
引句:「成功後記一筆治理事件,閘名 `drift-fix`」
file: `scripts/lumos:27142`
file: `scripts/lumos:6924`
1. 現況:`cmd_drift_ack` 用 `_gate_event_or_warn(root, "drift-check", "acked", …)`,`_KNOWN_GATES` 註解(6923)把 drift-check 定義成涵蓋「擋下、提醒、跳過、判不了、表態」。
2. spec 讓 `drift fix` 記 `drift-fix`,但 c2 `--keep` 「等同 `drift ack --kind c2`」、drift ack 的 c2/c3 也改成鎖內重判——同一個表態動作,從 `drift ack` 進去記 `drift-check`,從 `drift fix --keep` 進去要記哪個,spec 沒說。
3. 判不準的部分(⚠):鄰居中 `spec-gate`、`note-shape`、`note-audit` 都是每個功能自己一個閘名,所以另開閘名本身有先例;不一致的只是 `--keep` 與 ack 的事件歸屬。

## F6 git 查詢混用兩種呼叫風格,且 c4 的「逾時回 2」用的函式沒有逾時
severity: minor
blocking: 否 — 結構是對的(兩支都是既有函式),但錯誤處理與 spec 宣稱的行為對不上
引句:「git 查詢逾時、不在 git repo 都回 2 並講原因」
file: `scripts/lumos:5843`
file: `scripts/lumos:23351`
file: `scripts/lumos:32017`
1. c1 走 `_nodehome_git`(23351→`_lens_git` 32017,`timeout=20`,逾時、非零結束都回 None)。c4 走 `_plan_first_commit`(5843),它自己 `subprocess.run`、沒有 timeout、只接 OSError、查不到與出錯都回 None。
2. spec 第 1 步說 c1、c4 的 git 查詢「逾時、不在 git repo 都回 2 並講原因」。但 `_nodehome_git` 對逾時、不是 repo、其他失敗一律回同一個 None,分不出原因;`_plan_first_commit` 根本不會逾時(git 卡住就掛在鎖外)。
3. 同一個指令裡 c1、c4 的 git 錯誤處理就此不同;要「講原因」得在共用層加分辨,spec 沒指定。PRIOR-ART 段已說明 c4 刻意沿用 `_plan_first_commit`,所以這裡不是要換函式,是 spec 的錯誤處理宣稱與兩支既有函式的實際回傳對不上。

## F7 同一個子命令裡,「為什麼」旗標一個叫 `--why`、一個叫 `--reason`
severity: minor
blocking: 否 — 不影響結構,只是使用者要記兩個名字
引句:「`--close --status <值> --why」
file: `scripts/lumos:36537`
file: `scripts/lumos:36067`
1. drift 家族現況:`drift ack` 用 `--reason`(36537,必填);guard 家族(`guard plan`、`guard abandon`,36067、36076)與 `decision-add` 用 `--why`。
2. spec 的 c2 兩條路:`--close` 用 `--why`、`--keep` 用 `--reason`,而 `--keep` 又「等同 `drift ack --kind c2`」。同一個 `drift fix` 內同一個概念兩個旗標名。
3. ⚠ 兩個家族各自有慣例,沒有單一答案;至少在 `drift fix` 內應統一,並與 `drift ack` 的 `--reason` 對齊。其餘 `--old/--new`(對照 `guard kill-add`,36094)、`--by`(對照 `set superseded_by`,36227)、`--dry-run`(35872、35879、36298)與鄰居一致,已核對。

## F8 修復帳與表態的 `ts`、`after_sha256` 沒點名專案已有的原語與格式
severity: minor
blocking: 否 — 用哪種寫法都能跑,但「取 ts 最新」在不同格式之間會排錯
引句:「`ts`(ISO 時間到秒)、`path`(repo 相對)」
file: `scripts/lumos:1160`
file: `scripts/lumos:7991`
1. 專案內 ts 寫法不只一種:多數帳(治理帳 1160、規格閘 5917、逃逸帳 8021/8586、canary)用 `datetime.now().astimezone().isoformat(timespec="seconds")`(帶本機時差);`_utc_ts()`(rel-cascade 用)是 UTC;6882 有一處不帶時差。
2. spec 只寫「ISO 時間到秒」,又要拿 `ts` 判「最新一筆」(第 8 節)。若實作者用帶不同時差的字串直接比大小(多工作樹、多機器合併時會出現),排序會錯;對齊做法是點名用哪一種(與治理帳同格式),比較時先解析。
3. `after_sha256` 有現成的 `_sha256_file(path)`(7991,讀位元組算 sha256,OSError 交呼叫端);spec 沒點名,實作者可能另寫一支。

## F9 落點:動到共用寫入原語與簿記名單,但這兩處的家沒進 lands_in
severity: minor
blocking: 否 — 文件落點問題,不改行為;但 pre-commit 只擋「改 code 沒動圖譜」,不會擋動錯篇
引句:「改成追加前檢查最後一個位元組,不是換行就先補一個換行(表態檔、治理帳等共用這支的一起受益)」
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:32`
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:33`
1. `_jsonl_append_verified` 的說明住在 `Systems/loop-convergence-recording`(canary/逃逸帳共用寫完讀回自驗,第 32、34 行)與 `Systems/規格閘`;spec 要改它(追加前補換行)卻不在 lands_in、也不在第 9 節同步清單。
2. `_BOOKKEEPING_FILES` 的說明住在 `Systems/pitfalls-code-loop`(第 33 行「白名單與 code-loop 留痕失效豁免共用同一組常數」);spec 把 `governance/drift-fixes.jsonl` 加進去,同樣沒列那一篇。
3. lands_in 現列五篇(存量漂移守衛、guard-kill、lumos-cli-write、lumos-cli-read、reversibility-governance-ledger)對主要行為對得上,建議補這兩篇;`_STATUS_ENUM` 抽成模組常數落在 lumos-cli-read(`_lint_collect` 的家)已涵蓋。
4. 另外 Systems/存量漂移守衛.md 目前沒有任何一處提到 `drift-acks.jsonl`(我 grep Systems 為空),spec 要寫「表態綁 related」「修復帳」都要新開段落,不是補一句。

## F10 「治理帳等共用這支的一起受益」與程式碼現況不符:治理帳有自己的追加寫法
severity: minor
blocking: 否 — 宣稱錯了會讓人以為治理帳殘行問題已一起修掉;實際那支沒動
引句:「表態檔、治理帳等共用這支的一起受益」
file: `scripts/lumos:1222`
file: `scripts/lumos:8511`
1. `_jsonl_append_verified` 的呼叫端只有 canary 系列(5929、8482、8589、9881、9952)、逃逸帳(10124)、drift ack(27139)、去重帳(29940);治理帳 `.governance-log.jsonl` 是 `_gate_event`(1222–1229)自己 `open(path, "a")` 逐行寫,不經這支。
2. 所以補「檔尾不是換行先補換行」不會影響治理帳;而 spec 自己新增的 `drift-fix` 閘事件正是寫進這本治理帳。專案裡「追加一行 jsonl」目前有 `_jsonl_append_verified`、`_ledger_append`(15557,O_APPEND 單次寫)、治理帳自己的 open-append 三條路,spec 沒說要不要收斂,只把錯誤宣稱寫成已收斂。

---
已看,無 finding(對應四問裡看過且對齊的部分):
- 分層:c2、c3 的表態改在鎖內用 `_drift_state_findings(env, only=…)` 重判,與 `cmd_drift_ack` 現況(27101,先讀 env 再拿鎖包住追加)相比是收緊,不是新層。引句:「`drift ack --kind c2|c3`:改成跟 fix 一樣拿寫入鎖、鎖內重新載入並用 `_drift_state_findings` 算那一篇當下的發現」
- 寫入原語:改筆記走 `atomic_write_verify`,例外照鄰居 settle 的 `(ValueError, RuntimeError)` 轉回 2(12310),與現況一致。引句:「例外照鄰居 settle 的接法轉成回 2」
- PRIOR-ART 的 git 先例說法(`_nodehome_git` 已用 `git log -S`、`_plan_first_commit` 用 `--diff-filter=A`)對得上程式碼(23860、5843)。引句:「直接用既有的 `_plan_first_commit`(`git log --diff-filter=A`」
- `_revisit_lines` 抽出:E5 現況(2216–2224)就是 `_search_visible_lines(…, False)` 加 `_strip_inline_markup` 加 `_revisit_split`,抽成函式行為不變成立;第一層、第二層、`_probe_lines` 各自的迴圈(24852、25398、26438)留著是 spec 明寫的範圍取捨,不另列。引句:「其他地方(乙的 `_probe_lines`、第一層、第二層)各自的逐行迴圈不在本計劃範圍,不動」

不對齊共 10 條,其中需改的(blocking)2 條。
