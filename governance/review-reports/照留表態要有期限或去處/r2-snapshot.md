---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/存量漂移守衛
related:
  - "[[Projects/交接2026-10-03_計劃]]"
  - "[[Projects/回頭條件寫下時就成立_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
summary: |-
  WHY:回頭條件與 RULE 撤除條件成立後的「照留」表態要嘛綁一篇還開著的 Issue 或計劃(`--tracked-in`,那篇收尾就失效),要嘛 30 天後失效重新列;推送時新寫就已成立的條件,照留只認綁了去處的表態 [出處:2026-10-06 rtb 第三輪提案 B1、B2 與 rtb 會談回覆的實例;Enzo 2026-10-06 裁「兩種都給、至少選一」「舊表態從上線日起算 30 天」] [因:照留沒期限等於永久消音——rtb 有 11 筆理由寫「還沒補/還沒評估」,表態後 drift scan 不再列、也沒排進任何地方;推送時「新寫就已成立」雖然會擋,同一次推送補一筆照留就放行(rtb 一次改寫 33 行、當場照留 11 行)] [不選:只給 30 天(到期後理由照貼再表態一次,等於延長消音);只收綁去處(「還沒評估」這種得先硬開一篇 Issue);新寫就成立的一律不收照留(條件已成立但真的排進某篇計劃時沒路走)]
---
# 照留表態要有期限或去處_計劃

白話:回頭條件(某個事件發生就該回頭看的提醒)成立之後,如果事情還沒做,可以用 `lumos drift ack` 表態「這行照留」,之後健檢就不再列。問題是這個表態永遠有效,等於把提醒關掉。這次改成:照留時要嘛說清楚「排進哪一篇」(那篇收尾,照留就失效、重新列出來),要嘛不說,30 天後自動失效、重新列。另外,推送時新寫進去、寫下時就已成立的條件,本來就會擋,但補一筆照留就能過——這種只認說清楚排進哪一篇的照留。期限只在 drift scan(健檢清單)算;推送檢查不看日期,同一個提交什麼時候重跑結果都一樣。

依據:Enzo 2026-10-06 裁定兩題(做法:兩種都給、至少選一;舊表態:從上線日起算 30 天)。rtb 會談回覆的實例:Systems/Mock-DSP 第 80 行、Systems/共用行程基礎 第 57、60 行(rtb repo),都是「條件成立了但事還沒做」的照留。

PRIOR-ART: 同工具 c2/c3/c6 的照留已經綁「當時連著的已收尾計劃」,清單多了新的就重新列(`_drift_split_acked` 的 related/seq);REVISIT 本身有 `[by:日期]` 期限、doctor 到期會唸。本案沿用兩者的形狀:綁一篇節點的狀態、或一個日期,不另造第三種失效機制。表態檔、讀提交裡的筆記(`_drift_cat`)、frontmatter 解析(`split_frontmatter`/`parse_frontmatter`)、寫下時就成立的判定(`_drift_born_annotate`、`_drift_probe_judge` 的新寫分支)都沿用。
RETIRE-IF: 2027-01-05 量一次(見文末 REVISIT 的量法):所有消費專案的 probe/retire 照留到期重列後,全是理由照貼再表態(沒有任何一筆改綁去處、或那一行被處理掉)——表示期限只增加操作、不改行為,改回單純的照留並另想辦法。

## 範圍

- 做:`lumos drift ack --kind probe|retire` 多一個 `--tracked-in <節點>`;沒帶就自動記 30 天後的期限 `until`。
- 做:drift scan 判斷 probe 與 retire 的照留還算不算數:要「綁的那篇還開著」或「期限還沒到」;舊表態(`until`、`tracked_in` 兩個欄位都沒有)在 2026-11-05(本案設計日 2026-10-06 + 30 天)當天以前照舊有效,之後失效。
- 做:推送檢查(`drift check`)裡「這次新寫(或改了條件)、條件已經成立」的發現,只認綁了去處、而且那篇在被推送的版本裡還開著的照留;★推送檢查不看日期★(期限、舊表態寬限都不算),同一個提交任何時候重跑結果一樣。這次推送讓既有條件成立的那種發現,照留規則不變(認任何照留,同今天)。
- 做:「綁的那篇還開著」只認 Issue(狀態在 `_DRIFT_OPEN_ISSUE`)與計劃(狀態在 `_STATUS_ENUM["project"]` 扣掉 `_DRIFT_CLOSED`,即 todo、doing);綁驗證紀錄、Systems 節點、沒有狀態欄的筆記、或那一行所在的同一篇,表態時擋、判斷時當失效。
- 做:失效的照留在發現下面多印一句(沿用 c2 的 `prev_ack` 與 `_drift_prev_ack_line`):以前照留過、理由、為什麼失效、要繼續照留怎麼帶 `--tracked-in`。推送檢查裡新寫就成立的發現,改法提示直接寫「照留要帶 --tracked-in <排進的那篇>」(不靠有沒有舊照留)。
- 做:同步說明文字:改法提示裡教人照留的固定句(probe、retire、drift check 擋下訊息、`drift ack` 的 help 與說明字典)、`skills/lumos-project-notes` 兩處講 drift ack 的地方、[[Systems/存量漂移守衛]]。
- 不做:drift scan 不另外對「寫下時就已成立」收緊照留(那個標記判不了的情況多,收緊會跟判不了打架;scan 的照留一律有 30 天期限或去處,已足夠讓它重新出現)。
- 不做:c1–c6、m1、count 的照留(c2/c3/c6 已經綁 related;其餘改掉才會消失;rtb 這輪沒有實例);doctor(不評估回頭條件、只數條數)。
- 不做:讓期限可以自己選天數(固定 30 天;要更長就綁一篇去處)。
- 不做:把失效的照留從表態檔刪掉(表態檔只追加;失效只在判斷時算)。

## 做法

1. 常數:`_DRIFT_ACK_DAYS = 30`、`_DRIFT_ACK_LEGACY_UNTIL = "2026-11-05"`、`_DRIFT_EXPIRING_KINDS = ("probe", "retire")`(命名照 `_DRIFT_BOUND_KINDS`)。「開著」不另寫狀態表:Issue 用 `_DRIFT_OPEN_ISSUE`,計劃用 `_STATUS_ENUM["project"] - set(_DRIFT_CLOSED)`。
2. 表態寫入:argparse 的 `drift ack` 加 `--tracked-in`;`_drift_ack_args_err` 多收 tracked_in:kind 不在 `_DRIFT_EXPIRING_KINDS` 又帶了擋 rc2。`cmd_drift_ack`:帶了就 `env.find` 解析——找不到擋、是那一行所在的同一篇擋、type 不是 issue/project 或狀態不算開著擋——記 `tracked_in` 成 repo 相對路徑(跟 `path` 同形,NFC);沒帶就記 `until` = 表態日 + 30 天。成功訊息印綁哪篇或到哪天。`drift fix --keep` 也呼叫 `cmd_drift_ack`,kind 固定 c2、不帶 tracked_in,行為不變。
3. 判斷一筆照留還算不算數:新增純函式 `_drift_ack_live(a, today, status_of) -> (活著?, 失效原因)`,只對 kind 在 `_DRIFT_EXPIRING_KINDS` 的照留有意義:
   - `tracked_in` 存在:要是字串、不帶 `..`、在圖譜資料夾底下,否則失效(「綁的節點寫壞了」);`status_of(路徑)` 回 (type, status) 或 None——None → 「綁的 X 不在了」;不算開著 → 「綁的 X 已收尾或不是 Issue/計劃(type/status)」。
   - 沒有 `tracked_in`:`until` 存在時要是 ISO 日期字串、不早於表態日 `date`、不晚於 `date` + 30 天,否則失效(「期限寫壞了」);沒有 `until` 就用 `_DRIFT_ACK_LEGACY_UNTIL`。`today` 晚於期限 → 「已過期限 YYYY-MM-DD」(期限當天還算有效)。
   - 任何型別不對都回失效,不丟例外。
4. `status_of` 用呼叫端手上的圖譜物件:`env.notes` 取 NFC 路徑(去掉圖譜資料夾前綴)的筆記,`_drift_str(n, "type")`、`_drift_str(n, "status")`;讀不出(`_note_unreadable`)回 None。不另讀檔、不另解析 frontmatter。
5. `_drift_split_acked(findings, acks, vault_rel, today=None, status_of=None)`:
   - 不傳 `today`(推送檢查):kind 在 `_DRIFT_EXPIRING_KINDS` 的照留不看期限;發現帶 `born_now` 時只認有 `tracked_in` 而且 `status_of` 判開著的照留(`status_of` 由呼叫端傳;沒傳就當沒有綁去處的照留)。
   - 傳 `today`(drift scan):照第 3 點判活著;同一個鍵有多筆時,任何一筆活著就算已表態(兩個工作樹各自追加後合併也一樣)。
   - 沒算上、但有同鍵照留的發現帶 `prev_ack={reason, dead}`(取 seq 或檔內順序最後一筆);`_drift_prev_ack_line` 對有 `dead` 的印「以前照留過(理由:…),{dead};還沒做就 lumos drift ack … --tracked-in <排進的那篇>」;有 `prev_ack` 的不再印「以前表態過、後來改了或搬了」那句舊理由。
6. 新寫就成立的標記:`_drift_probe_check` 的 must 裡 `old` 不為真(起點沒有同一條,或沒有起點)的發現加 `born_now: True`——跟它被擋的條件完全一致(`_drift_probe_judge` 的新寫分支)。
7. 呼叫端:`cmd_drift_check` 的 probe 路徑、`_drift_retire_guarded` 不傳 today;要 `status_of` 時,retire 用手上的 tenv,核心路徑在「有 born_now 的發現而且有同鍵帶 tracked_in 的照留」時才 `_drift_tree_env(root, tip, …)` 建一次(大部分推送不會建)。`cmd_drift_scan` 傳 `today=date.today()` 與 tenv 的 `status_of`;失效的發現照既有「要處理」區印,`_drift_scan_print` 那裡也印 `_drift_prev_ack_line`。考試與歷史重放(`_drift_check_core` 的其他呼叫點)不扣表態,不受影響(先 grep 確認)。
8. 改法提示與說明:`_drift_fix_hint` 的 probe/retire 兩句、`drift check` 擋下時印的照留指令、`drift ack` 的 help 與說明字典補 `--tracked-in` 與 30 天;`skills/lumos-project-notes/commands/04-自檢與健康.md` 那一列改寫(寫下時就已成立的,推送時照留要綁去處;scan 的照留 30 天後重列)、`commands/03-寫回圖譜.md` 提到 drift ack 的那句補期限。
9. 寫回 [[Systems/存量漂移守衛]]:照留失效規則、兩個新欄位、推送不看日期的理由。

## 實務隱患

- **日期取本機**:只用在 drift scan(不擋推送),本機日期就是看清單的人的日期;CI 不跑 scan 的期限。台北比 UTC 早,同一刻台北可能已算過期而 UTC 還沒——只影響清單早一天出現,不影響任何閘。
- **舊表態一起到期**:2026-11-05 之後消費專案舊的 probe/retire 照留同時在 drift scan 重列(rtb 11 筆);不進推送檢查。比 11-05 更晚才升級的專案,升級當下就看到重列——那正是要修的情況,不另給寬限。
- **綁的節點改名**:改名後舊路徑讀不到 → scan 判「不在了」重列;推送檢查若剛好遇到新寫就成立的那一行,照擋並印理由,重綁一次即可。不追改名(同 c2 的 related 不追)。
- **退回提交**:舊程式忽略新欄位,所有照留恢復永久有效、推送檢查也恢復認裸照留——是放寬,退回時要知道。
- 已排除:金流:只改筆記治理工具,不碰任何金流
- 已排除:對外送出:不連網、不送任何東西出去
- 已排除:不可逆:表態檔只追加,失效只在判斷時算;退回提交即恢復舊行為
- 守衛面:推送檢查多擋一種情況(新寫就成立 + 沒綁去處的照留),屬收緊;不引入日期,重跑結果不變。

## 驗收條款

- [S1] 當 `drift ack --kind probe` 沒帶 `--tracked-in` 時,表態檔那筆 應 記 `until` 為表態日 + 30 天、不記 `tracked_in`;帶了指到一篇還開著的 Issue 或計劃 應 記 `tracked_in`、不記 `until` [test:t_drift_ack_routed_fields]
- [S2] 當 `--tracked-in` 指到不存在的筆記、已收尾的 Issue、驗證紀錄、Systems 節點、沒有狀態欄的筆記、或那一行所在的同一篇時,drift ack 應 rc2 不寫;`--kind c2` 帶 `--tracked-in` 應 rc2 [test:t_drift_ack_routed_rejects]
- [S3] 當照留的期限已過、綁的那篇已收尾或不在了、或欄位寫壞(期限不是日期、期限超過表態日 30 天、綁的路徑帶 ..)時,`_drift_ack_live` 應 判失效並給原因;期限當天、綁的那篇開著 應 判活著;任何型別錯誤 應 回失效不丟例外 [test:t_drift_ack_live_rules]
- [S4] 當 drift scan 遇到失效的 probe 照留時,那一行 應 列回要處理並印舊理由與失效原因;同一行一筆失效一筆活著時 應 算已表態 [test:t_drift_ack_routed_expiry]
- [S5] 當表態沒有 `until` 也沒有 `tracked_in`(舊表態)時,drift scan 應 以 2026-11-05 為期限(當天有效、隔天失效) [test:t_drift_ack_routed_legacy]
- [S6] 當推送新寫一條寫下時就已成立的回頭條件、同一次推送補了沒綁去處的照留時,drift check 應 照擋並在改法提示印「照留要帶 --tracked-in」;照留綁了一篇在被推送版本裡還開著的筆記 應 放行;綁的那篇在被推送版本裡已收尾 應 擋 [test:t_drift_check_born_needs_routed_ack]
- [S7] 當推送讓既有的回頭條件成立、照留沒綁去處時,drift check 應 照舊放行(只收緊新寫的);同一個提交把本機日期往後調 60 天重跑 drift check 應 結果相同 [test:t_drift_check_routed_no_date]

## 回退

退回本案的提交即可:表態檔的新欄位舊程式不讀(多出來的鍵忽略),舊程式把所有照留當永久有效、推送檢查也恢復認裸照留(這是放寬,見實務隱患);不需要搬資料。

## 天花板

1. 「綁的那篇還開著」只看類型與狀態欄,不驗那篇真的提到這件事;綁一篇無關但長期開著的 Issue 一樣能消音。
2. 期限固定 30 天,到期後理由照貼再表態一次就能再消音 30 天——只能讓它每月在 drift scan 出現一次,不能逼人處理。
3. 推送檢查只收緊「這次新寫就成立」的;既有條件在這次推送變成立時,裸照留照樣放行(到期只在 scan 才算)。
4. 沒有起點的推送(全新 repo 的第一次推送)裡,所有已成立的條件都算新寫,照留都要綁去處——跟今天「全部都會被擋」一致,只是出口變窄。

REVISIT:2026-11-06 舊表態寬限已過,拿掉 `_DRIFT_ACK_LEGACY_UNTIL` 與舊表態分支(之後沒欄位的照留直接當失效),[S5] 改成驗失效
REVISIT:2027-01-05 量 RETIRE-IF:在各消費專案的 governance/drift-acks.jsonl 數「同路徑同原文、沒綁去處的 probe/retire 照留連續兩筆以上」的行數,對照改綁去處或行已消失的行數

## 審計修正紀錄

- r1(2026-10-06,6 席:正確性、邊界、整合、回滾、簡化、架構對齊):36 條/blocking 18/四個根因——判定用了「今天」(推送檢查改成不看日期,期限只在 drift scan 算)、另寫一套讀筆記狀態的方法(改用呼叫端的圖譜物件,推送時有需要才建)、drift scan 的寫下時就已成立收緊跟判不了打架(拿掉,B2 只在推送檢查做)、零碎邊界(壞欄位、同鍵多筆、綁自己那篇、說明同步、舊表態日期 11-05)。放行 3 條(舊版工具寫的裸照留在 scan 享寬限、晚升級專案不另給寬限、until 照存)。例:新寫 `REVISIT:[when-file:src/a.py] …` 而 src/a.py 已在,同一次推送 `drift ack … --kind probe --reason "排程中"` → 修改前放行,修改後擋並印「照留要帶 --tracked-in」。
- 卷證:governance/review-reports/照留表態要有期限或去處/
