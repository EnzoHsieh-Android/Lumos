---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/每支檔有家
related:
  - "[[Issues/推新分支時風險分級拿空樹當起點]]"
  - "[[Issues/推送前其他閘的範圍在合過主線時會多算]]"
summary: |-
  WHY:推送前掛鉤在「新分支首推、或遠端舊值本機找不到」時,會擋或決定擋不擋的那幾步(波及計算、分支路徑的風險分級、雙向門放行、code-loop check、逃逸記帳、給 doctor 的「碰到哪些檔」清單)改用 lumos 的 `_push_range_start` 算出的真起點(跟主線的分岔點),由新指令 `lumos push-range` 印給掛鉤;一般增量推送照舊用遠端舊值 [出處:2026-10-06 rtb 會談回報 cap-retro 首推被 715 條「新增告警」誤擋;Enzo 2026-10-06 裁「修工具」;舊單 [[Issues/推新分支時風險分級拿空樹當起點]] 2026-09-03 已記同一件事;設計審 r1 三席獨立指向改走 `_push_range_start`] [因:新分支首推時掛鉤拿空樹當起點,整個 repo 被當成新改動;`_push_range_start` 是「起點只在這裡算一處」的那支,存量漂移檢查與回頭重讀已在用,它跟主線比、合過主線與 --no-verify 推過的別的遠端分支都算得對] [不選:在掛鉤用「不在任何遠端分支上的最早提交」當起點(設計審 r1 實測:合過主線會多算、遠端追蹤分支過期會少算、--no-verify 推到別的遠端分支再改名推能繞過);只改擋下訊息(誤擋照舊);一般增量推送也改走 `_push_range_start`(那是另一張 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 的範圍,本案不擴)]
---
# 新分支首推會擋的閘改用真起點_計劃

白話:推送前的掛鉤在推「遠端還沒有的分支」時,沒有舊版本可以比,就拿空樹(什麼都沒有)當起點,等於把整個 repo 當成這次的新改動。只提醒的檢查多掃無妨,但會擋的那幾步因此誤擋:風險分級被整個 repo 的舊寫法拉成高風險、新增告警閘把全 repo 的舊告警算成新的(rtb 2026-10-06 推 cap-retro 被 715 條擋下)、doctor 把別人逾期的預告合約當成你碰到的。lumos 裡已經有一支「起點只在這裡算一處」的函式,會跟主線比、找出這次真正的新改動,存量漂移檢查一直在用。這次給它開一個指令,讓掛鉤在新分支首推時用它算起點。

依據:Enzo 2026-10-06 裁「修工具」;rtb 會談同日回報的重現(本機 `lumos code-loop check` 自己算 merge-base 時沒有新增告警、可以推;同一個頂端經推送前掛鉤就被擋)。

PRIOR-ART: lumos 的 `_push_range_start`(推送閘接漂移檢查時定下「起點只在這裡算一處」,存量漂移檢查與 `note-audit reread-check` 經 `--push-remote/--pushed-ref` 在用;CI 的 code-loop check 對全零起點走的 `_lens_push_base` 也是跟主線分岔點同一個想法)。本案只給它開一個印範圍的指令,掛鉤照漂移檢查的帶法傳遠端名與遠端 ref。
RETIRE-IF: 掛鉤所有閘(含每支檔有家、筆記形狀擋、一般增量推送)都改走 `_push_range_start` 時([[Issues/推送前其他閘的範圍在合過主線時會多算]] 的收斂路),本案「只在新分支首推時呼叫」這個分支判斷撤掉,一律呼叫。

## 範圍

- 做:新指令 `lumos push-range --diff <遠端舊值>..<頂端> --push-remote <遠端名> --pushed-ref <遠端 ref>`:呼叫 `_push_range_start`,stdout 印一行範圍——有起點印 `起點..頂端`;頂端已在主線上(沒有新東西)印 `頂端..頂端`;git 查詢失敗(判不了)印 `空樹..頂端`(寧可多擋,同今天);說明印到 stderr。參數錯 rc2。
- 做:掛鉤新函式 `pp_block_range_for <遠端舊值> <本地頂端> <遠端 ref>`:遠端舊值不是全零而且本機有那個物件 → `舊值..頂端`(一般增量,同今天);否則呼叫 `lumos push-range`,rc0 而且印出形狀對的一行就用它,其他情況(舊版 lumos 沒有這個指令、失敗、印出怪東西)退回 `空樹..頂端`(同今天)。
- 做:吃 `pp_block_range_for` 的:`pp_touched_file`(餵 doctor 的 `--touched-from`,會擋)、`impact_once`(結果經 `--from-json` 餵 code-loop check 的受波及合約測試,高風險時會擋)、分支與標籤共用的那次 `pitfalls --diff --json`(決定分級、測試子集與 advisory 旗標)與高風險列命中那次、`spec-gate --push-check`、`code-loop check --diff`、兩處 `loop escape --range`。
- 不做:標籤路徑的風險提醒(`pitfalls` 第三處)、`bound_tests_advisory`、`test-layers` 照舊用 `pp_range_for`——只提醒;它們讀的波及結果跟著變小,無害。
- 不做:每支檔有家與筆記形狀擋(各有自己的起點推導 `_hrange` 加 lumos 端截到上線點;改它們是 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 的範圍)。
- 不做:存量漂移檢查、回頭重讀(已經自己帶 `--push-remote/--pushed-ref`)。
- 不做:CI(CI 對新分支傳全零給 code-loop check,lumos 端 `_lens_push_base` 已從跟主線的分岔點算)。
- 不做:一般增量推送的範圍(照舊 `舊值..頂端`)。

## 做法

1. lumos 新增 `cmd_push_range(repo, diff_range, push_remote, pushed_ref)`:`--diff` 照 `_lens_range_ok` 解析(左端可以是全零),頂端轉完整 sha,呼叫 `_push_range_start`;None → 印 `頂端..頂端`;`_PUSH_START_UNKNOWN` → 印 `空樹..頂端`(空樹照本 repo 的雜湊算法,`_drift_empty_tree`);其他印 `起點..頂端`。`--push-remote` 與 `--pushed-ref` 必帶(少一個 rc2),同 `drift check` 的參數規矩。不寫治理帳(唯讀指令)。
2. 掛鉤新增 `pp_block_range_for`(見範圍);印出的那一行要符合 `^[0-9a-f]{40,64}\.\.[0-9a-f]{40,64}$` 才用,否則退回空樹。
3. 迴圈裡每個 ref 算一次 `_brange`(推刪除 ref 的那一行本地頂端是全零,迴圈開頭就跳過,不會呼叫);上面「範圍」列的呼叫改吃 `_brange`。`pp_touched_file` 改呼叫 `pp_block_range_for`(它要遠端 ref,從同一行 stdin 讀)。
4. `_range` 那段註解改寫:只列真的只提醒的幾道;寫明會擋的用 `_brange`、為什麼。每支檔有家那段「兩套刻意不同」的註解補一句:本案的 `_brange` 是第三個呼叫點,三者收斂路見那張 Issue。
5. 舊單 [[Issues/推新分支時風險分級拿空樹當起點]] 結案:寫明採用的方向、當初擔心的「解析預設分支會變鬆」怎麼被 `_push_range_start` 的主線候選與失敗退回空樹處理掉。
6. 寫回:`push-range` 指令的家(`scripts/lumos` 的家,先查是哪篇)、[[Systems/每支檔有家]](掛鉤範圍推導那一段)、[[Systems/bound-tests-gate]](它描述 impact_once 的範圍)。

## 實務隱患

- **舊版 lumos**:消費專案先拿到新掛鉤、lumos 還是舊版時,`push-range` 不存在 → 退回空樹(同今天),不會更鬆。
- **遠端名是網址或空的**(直接推網址、手動跑掛鉤):`_push_range_start` 找主線的方式跟存量漂移檢查同一套;找不到主線時全零起點回空樹(同今天)。
- **標籤推送**:標籤的頂端通常已在主線上 → 範圍是空的 → 分級判成只動文件、推送前不跑全套測試。發版標籤打在已推過、CI 跑過的提交上,接受;寫進天花板。
- **時間**:每個新分支首推多一次 lumos 啟動加幾個 git 查詢(`pp_touched_file` 與迴圈各一次),跟存量漂移檢查同量級。
- 已排除:金流:只改推送前掛鉤的範圍推導與一個唯讀指令,不碰任何金流
- 已排除:對外送出:不連網、不送任何東西出去
- 已排除:不可逆:只改掛鉤與一個唯讀指令,退回提交即恢復
- 守衛面:新分支首推時會擋的那幾步看的範圍變小(從整個 repo 變成跟主線的分岔點之後);起點由存量漂移檢查已在用的那支算,失敗一律退回空樹(多擋);CI 的 code-loop check 照舊當後盾(功能分支推送時 CI 也跑 code-loop check,對全零起點從跟主線的分岔點算;用的是 `_lens_push_base`,跟本機這支 `_push_range_start` 在一般情形算出同一個分岔點,合過主線的形狀才可能不同——CI 端改用同一支屬收斂 Issue 的範圍)。

## 驗收條款

- [S1] 當推一個遠端還沒有、只比主線多一個乾淨提交的新分支,而主線本身有大量會被當成新增告警的舊寫法時,推送前掛鉤 應 放行,而且風險分級只算那一個提交 [test:t_prepush_new_branch_block_range]
- [S2] 當新分支裡那一個新提交真的帶進新告警時,推送前掛鉤 應 照擋 [test:t_prepush_new_branch_block_range]
- [S3] 當新分支先合過主線(主線在分岔後又多了會被當成告警的提交)再首推時,推送前掛鉤 應 只算分支自己的提交、放行 [test:t_prepush_new_branch_block_range]
- [S4] 當遠端已有那個分支(一般增量推送)時,會擋的那幾步的範圍 應 跟改之前一樣是「遠端舊值..頂端」 [test:t_prepush_new_branch_block_range]
- [S5] 當 `lumos push-range` 不存在或失敗時,掛鉤 應 退回空樹起點(同改之前) [test:t_prepush_new_branch_block_range]
- [S7] 當遠端舊值在本機找不到(別人 force-push 過、本機沒 fetch)時,會擋的那幾步 應 改用 `lumos push-range` 算的起點,不再從空樹 [test:t_prepush_new_branch_block_range]
- [S6] 當 `lumos push-range` 收到頂端已在主線、找得到分岔點、git 失敗三種情形時,應 各印「頂端..頂端」「分岔點..頂端」「空樹..頂端」;少帶 --push-remote 或 --pushed-ref 應 rc2 [test:t_push_range_cli]

## 回退

退回本案的提交即可:只改推送前掛鉤與新增一個唯讀指令,退回後新分支首推恢復從空樹算(會再被誤擋)。消費專案要重跑 `lumos update` 才拿到新掛鉤;退回也一樣要更新一次。

## 天花板

1. 只修新分支首推與舊值本機找不到;一般增量推送合過主線時的多算照舊(另一張 Issue)。
2. 每支檔有家與筆記形狀擋仍用各自的起點推導;掛鉤裡同時有兩種起點,直到收斂。
3. 標籤推送的範圍通常是空的,推送前不跑全套測試。

## 審計修正紀錄

- r1(2026-10-06,6 席):33 條/blocking 15/方向改了——原本在掛鉤層用「不在任何遠端分支上的最早提交」當起點,三席實測出合過主線多算、追蹤分支過期少算、--no-verify 推到別的遠端分支再改名推能繞過,另三席指出那跟「起點只在 `_push_range_start` 算一處」的既有決定相反;改成新指令 `lumos push-range` 包那支函式、掛鉤只在新分支首推與舊值找不到時呼叫,失敗退回空樹。另補:`pp_touched_file` 其實餵會擋的 doctor、標籤與分支共用那次風險分級、合過主線與舊值找不到的條款。放行 2 條(本機與 CI 起點兩支並存、掛鉤裡三個範圍名)。例:新分支先合過主線、主線之後多了 700 條告警的提交,再首推 → 修改前擋,修改後只算分支自己的提交、放行。
- 卷證:governance/review-reports/新分支首推會擋的閘改用真起點/
