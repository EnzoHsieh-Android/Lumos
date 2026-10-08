---
type: project
status: doing
created: 2026-10-02
updated: 2026-10-02
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/guard-kill
  - Systems/代碼審修正關卡
related:
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Projects/殺傷力配方修補體驗_計劃]]"
  - "[[Projects/殺傷力配方失配提醒_計劃]]"
  - "[[Systems/guard-kill]]"
  - "[[Systems/代碼審修正關卡]]"
---
# 殺傷力配方當場試跑_計劃

白話:殺傷力配方是「故意把程式改壞,看綁定的測試會不會紅」。現在重加一條配方之後,要跑整篇的 `lumos guard kill` 才知道新寫的那條殺不殺得掉;健康檢查(doctor 的 P2 段)只看配方原文還對不對得上程式,看不出「原文對得上、真跑卻殺不掉」。這份計劃做四件小事:①`guard kill` 能只跑指定短身分的那幾條;②`kill-add --try` 寫完當場只跑新加的那一條;③P2 段另外列出「最近一次真跑判 survived」的配方;④修正關卡在修正改到配方指著的檔時,提醒重跑那幾條。全部只提醒,不擋。

依據:
- rtb(另一個使用 lumos 的消費專案)2026-10-01 修 10 條失配配方的回報(rtb 提交 c531ac7,記在 rtb 的 `Issues/存量筆記漂移等工具修復`):①第一次驗證有 2 條重寫時選錯位置而 survived,要跑整篇才發現——想要重加後當場試跑那一條;④另外撞到一條不在 10 條裡的既有配方 survived(核可有兩道防護,拿掉一道測試照綠),「P2 只看原文對不對得上,看不出這種對得上卻殺不掉」。第 2、3 點已在 [[Projects/殺傷力配方修補體驗_計劃]] 做完。
- Enzo 2026-10-01 裁路線圖順序「1a-4 → 修正關卡 → 1a-3 → 1b」,本計劃是 1a-3([[Projects/漂移防治路線圖_計劃]]);第 ④ 件「修正改到配方指著的檔時提醒重跑」是 [[Projects/代碼審修正關卡_計劃]] 設計審時轉來的。

PRIOR-ART: 全部沿用 lumos 既有零件——配方短身分 `_kill_recipe_id`(kill-rm 與 guard kill 結果行已在用)、kill-rm 不帶 --id 時的列表 `_guard_kill_rm_list`、殺傷力帳本讀法 `_backing_kill_rows`(合約背書已在用:欄位型別擋、對回筆記現有配方)、「之後只動簿記檔」判法 `_codeloop_record_valid_ex`、P2 段的軟提醒與 `check-p2` 事件。突變測試工具(mutmut、cargo-mutants)都有「只跑指定突變」的選項,做法同 ①。
RETIRE-IF: rtb 10-15 回報與本 repo 下一次修配方時都沒用到 `--try` → 拿掉 `--try`,保留 `--id`(guard kill 本來就該能挑;kill-log 沒有「這次是不是只跑一條」的欄位,用量只能靠問);P2 列出的 survived 配方連續一個月都被判成「本來就殺不掉、配方該拿掉」而不是真漏洞,就把那段降到 `--verbose` 才印。
REVISIT:2026-10-15 跟 rtb 的殺傷力回報同一天:問 rtb 有沒有用 `--try`、P2 的 survived 清單有沒有幫到(那條核可兩道防護的執行迴圈 F7 是怎麼處理的)。

## 名詞

- **短身分**:kill-rm 與 guard kill 結果行印的那 12 碼十六進位,是配方完整身分(`_kill_recipe_id`,由節點、合約、檔、原文算出)的前段。比對照 kill-rm:收 8 碼以上十六進位、用前段比對、對到零條或兩條以上不同完整身分都擋。
- **判定**:guard kill 每條配方的 verdict(killed、killed_unattributed、timed_out_weak、survived、drifted、abort、error)。**證據弱**:kill-log 每行的 `weak` 欄(整套一起跑、flaky 平台、筆記有未提交改動、修改時間沒錯開會設 true),跟判定是兩回事。
- **配方指的檔**:配方的 `file`,路徑相對配方平台所在 repo 的最上層(guard kill 用 `_kill_plat_top` 找那一層)。

## 範圍

- 做:`guard kill <節點> --id <短身分>`;`cmd_guard_kill` 多兩個選用參數(要跑的完整身分清單、把逐條結果交回呼叫端的清單)——判法、回傳碼、kill-log、`--json` 都不變;`kill-add --try`;kill-add 寫完印試跑那一條的指令;doctor P2 另列最近一次真跑判 survived 的配方;`loop fix-check` 印「這幾條配方指著改過的檔」;P2 的跳過規則與 kill-rm 列表的逐行格式抽成共用小函式。
- 不做:P2 不自動跑 guard kill(doctor 要快);survived 不擋任何閘;不改 kill-log 欄位,也就不處理「身分不含壞法本身」那件事(見〈實務隱患〉)。

## 做法

### 共用的小整理

- P2 掃配方時的跳過規則(verification 型、status 是 superseded/stale、沒有 `kill_recipes` 欄)抽成 `_kill_p2_skips(note)`,P2、survived 清單、修正關卡提醒三處共用,行為不變。
- kill-rm 不帶 --id 時列表的逐行格式抽成 `_guard_kill_rm_rows(rel, recipes)`(回文字行),`_guard_kill_rm_list` 照舊印到標準輸出、結尾照舊印「移除」;guard kill 找不到短身分時用同一個逐行格式、印到標準錯誤、結尾改印「只跑某一條:lumos guard kill <節點> --id <短身分>」。

### ① `guard kill <節點> --id <短身分>`

- 新旗標 `--id`(可重複,也收逗號分隔)。每個值照 kill-rm 的規則比對(見〈名詞〉):不是 8 碼以上十六進位、對到零條、或對到兩條以上不同完整身分 → 回 2,印是哪一個、為什麼,接著用共用逐行格式列出這篇每條配方(印到標準錯誤)。
- 比對在合約片段過濾之後、「沒有配方可跑」判斷之前;兩個條件都要符合。完整身分相同的重複配方(手改造成)會一起跑。
- `cmd_guard_kill` 的新參數 `ids`(完整身分清單,CLI 由 `--id` 前段解析出來後傳入)與 `results_out`(呼叫端給一個清單,跑完把每條的判定、證據弱、短身分放進去);兩個都不給時跟現在一模一樣。

### ② `kill-add` 寫完後的試跑

- 新配方的短身分:寫入鎖裡已經算出這條的完整身分(判重用的那把),經既有的 `warn_box` 帶到鎖外再取前 12 碼。
- 不帶 `--try`:寫入成功時,原本那行「下一步: lumos guard kill 跑殺傷力驗證」改成「下一步:只跑這一條 lumos guard kill <節點> --id <短身分>」(節點用 `_kill_node_arg` 的寫法)。只更新 covers 的那條路照舊(已查過沒有測試釘這兩行字面)。
- 帶 `--try`:寫入成功(含只更新 covers)後,在鎖外、提醒印完之後呼叫 `cmd_guard_kill(env, node, ids=[完整身分], results_out=[])`,結果照 guard kill 的人讀格式印。回傳碼:寫入失敗照舊 2、不試跑;寫入成功時用 guard kill 的回傳碼——有強證據的 killed 回 0;任一 survived 或全部只拿到弱判定(killed_unattributed、timed_out_weak)回 1;drifted、abort、error 回 2。
- 判定是 survived 時另印:「配方已寫進筆記;換位置重寫就 lumos guard kill-rm <節點> --id <短身分> 再重加」。全部只拿到弱判定時另印:「紅燈沒歸因到綁定測試或逾時,不是殺不掉;看結果行的說明」。判定是 drifted 時另印:「試跑是對 HEAD 跑的,程式改了還沒提交時原文對不上——先提交程式再試」。
- 預先講清楚的現象:kill-add 剛把筆記改成未提交,`--try` 一定會先印 guard kill 那行「repo 有未提交變更」的警告,而且這次 kill-log 的 `weak` 是 true(筆記未提交,guard kill 既有規則)。

### ③ doctor P2 列出最近一次真跑判 survived 的配方

- `_kill_p2_scan` 多回一個「這次已列出問題的配方完整身分」集合(`_kill_p2_one` 判出來不是 ok 的),survived 清單跳過它們,不重複列。
- 讀殺傷力帳本一次(`_backing_kill_rows`:型別不對、`head_sha` 不是完整 sha、對不回筆記現有配方的行都略過),照 `_kill_p2_skips` 跳過不該看的筆記,每條配方取**檔內順序最後一筆**(跟合約背書 `_backing_judge_groups` 一致,不比 `ts`);最後一筆判定是 survived 的列出來。
- 一行寫:筆記、短身分、合約前段(取筆記那條配方的 `invariant`、經 `_kill_show`,不取帳檔那一行的)、那次跑的日期(`ts` 要是字串,取前 10 字、只留數字與連字號)、版本前 8 碼、兩個指令(重跑 `lumos guard kill <節點> --id <短身分>`;確定這條本來就殺不掉就 `lumos guard kill-rm <節點> --id <短身分>`)。
- 行尾附註(都只是提示,不改判斷):
  - 那次的 `weak` 是 true → 「(那次證據弱,先重跑)」。
  - 配方指的檔在那次的版本到現在的 `HEAD` 之間改過,或判不了 → 「(配方指的檔之後改過,先重跑)」。判法:用配方平台的 repo 最上層(`_kill_plat_top`)跑 `git diff --quiet <head_sha> HEAD -- <file>`;非 0 或出錯都算改過。每個(版本、檔)只判一次;整段時間上限沿用 `_BACKING_BUDGET`(20 秒),超過的直接加這句;設定檔讀不了、平台找不到時也直接加這句。
- 另開一個軟提醒(不跟「原文對不上」擠同一段:每段預設只印 3 條、標題語意也不同),標題「有 N 條殺傷力配方最近一次真跑判 survived(原文對得上卻殺不掉;不擋)」;每篇涉及的筆記各記一筆 `check-p2` 事件,kind 用 `survived`(跟原文對不上的 `warned` 分開)。設定檔讀不了時這段照樣算(它不靠設定檔判對不對得上)。整段包例外保護,算不出來只印一行,不影響原文對不上那段。
- 只看最後一筆而不是「同一版本上任何一次 survived」:合約背書是閘,寧嚴;P2 是提醒,只要指出現在還殺不掉的,重跑後殺得掉就不該再吵。

### ④ 修正關卡提醒重跑

- `lumos loop fix-check` 算出 `base..修正後` 改到的檔之後(只在這輪有要修正紀錄、沒早退時跑到),逐篇看筆記(`_kill_p2_skips` 跳過的不看)的每條配方:配方平台的 repo 最上層要等於修正關卡的 repo 最上層(不同 repo 的跳過,免得同名路徑誤報),`file` 在改過的檔裡就收。
- 有收到時,提醒段加一條說明「這幾條殺傷力配方指著這次改過的檔,原文可能對不上或殺不掉了,重跑:」,接著每條配方各一條提醒(`lumos guard kill <節點> --id <短身分>`),最多 10 條,其餘一條「還有 N 條」。只印,不影響過不過、不寫事件欄位(`--json` 的 notes 陣列會多這幾項)。

## 條款

- [S1] 當 `guard kill <節點> --id <短身分>` 給了那篇某一條配方的短身分(8 碼以上前段)時,應只跑那一條;給兩個時應只跑那兩條;給了對不到的、不是十六進位的、或對到兩條不同配方的短身分時應回 2、在標準錯誤印出原因與這篇每條配方的短身分(結尾是「只跑某一條」的指令,不是「移除」);跟合約片段一起給時兩個條件都要符合;不給 `--id` 時行為跟現在一樣 [test:t_guard_kill_only_ids]
- [S2] 當 `kill-add` 不帶 `--try` 寫入成功時,輸出應包含 `lumos guard kill <節點> --id <新配方的短身分>`;帶 `--try` 而新配方有強證據殺得掉時應印出判定並回 0;判定是 survived 時應回 1、印出 `kill-rm` 指令,而且配方仍留在筆記裡;寫入失敗時應照舊回 2、不試跑;只更新 covers 時帶 `--try` 也應試跑那一條 [test:t_guard_kill_add_try]
- [S3] 當殺傷力帳本裡某條現有配方的最後一筆判定是 survived 時,doctor P2 應在另一段列出它的短身分與重跑、移除兩個指令,並記一筆 kind 是 `survived` 的 `check-p2` 事件;最後一筆是 killed(即使更早有 survived)時應不列;帳上那一行對不回筆記現有配方時應不列;原文已經對不上、已在「原文對不上」那段列過的應不重複列;那次 `weak` 是 true 時行尾應帶「(那次證據弱,先重跑)」;配方指的檔在那次之後改過時行尾應帶「(配方指的檔之後改過,先重跑)」,檔沒改過、只有別的檔改過時應不帶 [test:t_doctor_p2_lists_survived]
- [S4] 當 `loop fix-check` 這一輪有要修正紀錄的折入、而 `base..修正後` 改到某條殺傷力配方指著的檔時,輸出應有「這幾條殺傷力配方指著這次改過的檔」與那條的 `guard kill … --id …` 指令,而且過不過不受影響;沒改到時應不印;配方的平台在別的 repo 時應不收 [test:t_fix_check_recipe_rerun_note]

## 回退

- revert 實作提交:四件都消失,kill-log 與筆記不受影響(只讀不寫新欄位)。
- revert 之後本計劃條款綁的 `[test:]` 會懸空,status 改 superseded 或在〈實作紀錄〉記一句「已撤回」。

## 實務隱患

- **配方身分不含壞法本身**:kill-log 的 `recipe_id` 由節點、合約、檔、原文算出,不含 `new`;同一處重寫壞法(原文沒變)之後身分不變,P2 會一直列著舊的 survived,直到重跑一次。提示本來就叫人重跑,重跑之後最新一筆就換掉了。不在這次改帳本欄位。
- **時間**:`--try` 等於跑一次只有一條的 guard kill(baseline 一次加配方一次,加上 1a-4 的「等到新的一秒」;rtb 實測每條約多 0.75 秒);P2 多讀一次 kill-log、每個(版本、檔)判一次 git,整段上限 20 秒。
- **本機才有帳**:消費專案的 kill-log 不進版控,survived 清單只在跑過 guard kill 的那台機器有東西可列;CI 上這段多半是空的。
- **弱證據**:剛 kill-add 還沒提交就 `--try`,結果會是弱證據(筆記有未提交改動)——這是 guard kill 既有的規則,印出來的判定照實。
- **既有測試**:guard kill 的 `--json` 純度、rc 優先序兩條合約(見 [[Systems/guard-kill]])不能動——新參數不給時行為一模一樣;kill-add 的「下一步」那兩行已查過沒有測試釘字面;P2 段的軟提醒計數、`check-p2` 事件、kill-rm 不帶 --id 的列表輸出(`t_guard_kill_rm_lists_ids`)要照舊。
- **要同步的文件**:[[Systems/guard-kill]] CLI 一節補 `--id` 與 `--try`、P2 段補 survived;[[Systems/代碼審修正關卡]] 補重跑提醒;指令速查第 06 子檔 guard kill 那列。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只在本機跑測試與讀帳本,不連網
- 已排除:不可逆:只讀帳本與筆記、試跑在隔離工作樹;revert 回得去
- 守衛面:只多提醒與一個挑選旗標,不改任何閘的判定。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- 前掃(2026-10-02):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/殺傷力配方當場試跑/r1-intake.md`,其中 2 條動到做法(`--try` 要拿到逐條判定才分得出 survived 與全弱證據 → guard kill 多一個交回結果的選用參數;「之後程式改過」原本用代碼審留痕那套、只要有任何提交就算 → 改成只看配方指的那支檔)。
