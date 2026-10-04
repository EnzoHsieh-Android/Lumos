---
type: project
status: doing
created: 2026-10-04
updated: 2026-10-04
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/reversibility-governance-ledger
related:
  - "[[Projects/交接2026-10-03_計劃]]"
  - "[[Issues/code-loop-pass自失效追尾]]"
  - "[[Projects/消費專案接入靜默失效_計劃]]"
  - "[[Projects/全repo審視_計劃]]"
summary: |-
  WHY:治理帳分兩本——人或 AI 主動做的決定留在進版控的 docs/.governance-log.jsonl,檢查自動跑出來的例行觀察改寫進 git 資料夾裡的本機帳 [出處:2026-10-04 雲端工作階段每回合被「有沒提交的改動」打斷,根因是每次提交、推送都往進版控的帳寫例行紀錄] [因:例行紀錄只有本機統計在讀,CI 讀的是代碼審留痕與修正關卡,兩者分開後平常提交推送完工作目錄就是乾淨的] [不選:整本帳移出版控(CI 會讀不到代碼審留痕,2026-09-09 已裁定治理帳是 CI 唯一權威來源);本機帳放 docs/ 再用 .gitignore 忽略(本 repo 與舊消費專案都出過 .gitignore 寫錯位置,且要靠 lumos update 補規則才生效)]
---
# 治理帳例行紀錄分流_計劃

白話:`docs/.governance-log.jsonl` 是進版控的治理帳。現在每提交一次、推送一次,工具都會往裡面寫幾行「每支檔有家:通過」「刪除守衛:沒事」「健康檢查跑過一次」,於是工作目錄永遠有一個沒提交的改動——雲端工作階段每回合被提醒打斷,本機的 git status 永遠不乾淨,這些例行紀錄不是被順手夾進不相干的提交,就是一直堆著。這份把帳分兩種:**有人做了決定的**照舊進版控;**檢查自動跑過一次的**改寫到不進版控的本機帳。

依據:2026-10-04 盤點(寫帳約 17 處、讀帳十來處,見〈盤點〉)。

PRIOR-ART: git 本身把每台機器各自的狀態放在 `.git/` 底下不進版控(rerere 紀錄、各種 hook 的暫存),pre-commit 這類工具的執行紀錄也放在使用者自己的快取資料夾而不是專案裡;這裡沿用這個慣例,不自己發明位置。寫帳的分流點借既有的通用寫入器(`_gate_event`、`_append_governance_log` 等),在它們決定寫哪個檔的那一步分,不新增寫帳入口。
RETIRE-IF: 上線滿 8 週後,有讀者要用「別台機器的例行紀錄」,或版控帳裡的例行紀錄又用別的方式長回來,就重新評估要不要合回一本。
REVISIT:2026-12-01 數這 8 週雲端工作階段被「有沒提交的改動」打斷的次數(目標:只剩主動決定之後那幾次);並對照 RETIRE-IF

## 盤點

- 寫帳:直接開這本帳寫的只有四支——`_gate_event`、`_append_governance_log`、`_codeloop_gov_log`、`_codeloop_dispositions_gov_log`;`_loop_gov_mark`、`_bound_tests_log`、`_gate_failopen` 都是轉呼叫它們的包裝。`_append_governance_log` 一次收一批事件,同一批裡可能混著兩種(例如 anchor-approve 與 design-loop 也走它),所以分流要**逐筆**判,不能整批判。觸發點遍布提交前、推送前、`doctor --ci`、代碼審、錨點核可、漂移、筆記形狀、筆記內容審、回頭重讀。
- 其他機器或 CI 一定要讀到的:代碼審留痕 code-loop 的 passed、skipped、dispositions(CI 的乾淨副本沒有本機標記檔,只能讀版控帳);修正關卡 fix-check(換機器或新副本也要讀得到);design-loop 的 converged 等(週回放、改寫血緣、`_escape_released_loops` 要讀;`_loop_close_stamps` 用 design-loop 與 code-loop 的關門事件判「迴圈還開不開」)。
- 只有本機統計、回顧在讀的:`lumos gov` 彙整、doctor 的 spec-gate 比例段、S18 度量、lint-new 自動放行次數。doctor 的帳本成長段量的是版控帳**這個檔**的大小與成長倍數,保護的是整檔讀者,不算統計讀者。
- CI 自己寫的本來就白寫(用完的副本整個丟掉)。

## 範圍

- **做**:寫帳時依「閘名+種類」分流到版控帳或本機帳;整本讀的統計類讀者改成兩本一起讀;本機帳寫不進去時照現有規則在錯誤輸出明講。
- **不做**:不拆版控帳本身(〈全repo審視〉#18 裁定不分檔,理由是四個整檔讀者,這裡不推翻——那四個讀者讀到的主動決定一筆不少);不改雲端平台那支「有沒提交的改動」提醒;不自動提交帳本;不搬舊紀錄。

## 做法

1. **分流規則一句話**:人或 AI 主動做的決定留在版控帳;檢查自動跑出來的觀察寫進本機帳。拿不準的留在版控帳(寧可吵一點,不要讓別台機器讀不到)。
2. **分流表**(唯一定義放在一個常數,列的是明確的「閘名+種類」,不用萬用字元;唯一例外是 check- 開頭的閘名,它們只由 doctor --ci 的提醒段寫;不在表上的一律進版控帳)。分流發生在四支直接寫帳的函式決定路徑那一步;`_append_governance_log` 在逐筆寫的迴圈裡判:

| 留在版控帳(主動決定,或繞道與自動放行的痕跡) | 改寫本機帳(自動觀察) |
|---|---|
| code-loop:passed、skipped、dispositions、recall-miss、skipped-env(繞過代碼審的痕跡,工具承諾「留在治理帳上」) | doctor-run;doctor 各段 check-*(只由 doctor --ci 寫,全是提醒觀察);ledger-growth;daily-wrapper |
| fix-check 全部 | nodehome-check、note-shape、delguard 全部 |
| anchor-approve | drift-check:passed、warned、blocked、skipped-env、skipped、range-unavailable |
| drift-check:acked、fix(真正的表態檔另有一份,這兩種只是紀錄,留著偏保守) | anchor:blocked;bound-tests 全部 |
| lint-new:waived | spec-gate:spec-gate-run |
| design-loop 全部 | note-audit:skipped、skipped-env;note-reread:reminded、covered、none、skipped、skipped-env |
| note-audit:prepare、recorded、blocked、warned;note-reread:recorded | escape-auto:escape-auto-failed;canary:blocked |
| 各閘的 fail-open(工具出錯自動放行的痕跡) | code-loop:blocked |

3. **本機帳的位置**:`<git 共用資料夾>/lumos/governance-local.jsonl`,共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)。不是 git 專案、或取不到共用資料夾時,退回寫版控帳(跟現在一樣,不丟紀錄)。
4. **讀者**:統計類讀者(`lumos gov`、doctor 的 spec-gate 比例段、S18 度量、lint-new 自動放行計數)改用同一支「兩本一起讀」的小工具,依時間合併。**判定類讀者只讀版控帳、一行不改**:代碼審留痕與表態、修正關卡、`_loop_close_stamps`(迴圈開關)、`_escape_released_loops`、改寫血緣、週回放——它們讀的種類全在左欄。doctor 的帳本成長段也只量版控帳那個檔。
5. **寫不進去**:兩條路各照現有行為,不新增語意——走 `_gate_event` 的回 False,呼叫端照舊講 telemetry-write-failed;走 `_append_governance_log` 的照舊靜默(它現在就是 `except OSError: pass`)。判定不受影響。
6. **不在 git 裡或取不到共用資料夾**:`_append_governance_log` 取不到 HEAD 本來就什麼都不寫,維持;`_gate_event` 沒有 docs/ 本來就回 None 不寫,維持;有 docs/ 但取不到 git 共用資料夾時,退回寫版控帳(不丟紀錄)。

## 實務隱患

- **守衛面(本案的主風險)**:分流錯一種主動決定進本機帳,CI 與別台機器就讀不到它——例如代碼審留痕落到本機帳,CI 會判「高風險沒審查留痕」把推送擋下(偏擋,不會偏放);反過來例行觀察留在版控帳只是吵,不影響判定。所以分流表採白名單思路的反面:只有表上明列為例行觀察的才分流,其餘一律留在版控帳;[S2] 用全新副本驗代碼審留痕讀得到。另外,判定本身(擋或放)不讀本機帳,分流不會讓任何閘從擋變放。
- **CI 讀者**:代碼審留痕與表態的讀法不動;CI 端被分流的只有例行觀察,而 CI 寫的本來就丟。
- **相容**:舊紀錄留在版控帳,讀者兩本都讀,統計不斷;消費專案不用改 `.gitignore`。
- **跨機器**:本機帳每台機器各一份,跨機器的例行統計看不到(目前沒有讀者需要)。
- **帳本成長**:版控帳成長變慢;本機帳在 `.git` 裡,`git clone` 不帶,不會變成別人的負擔。
- **回滾**:還原本案提交即可;本機帳留在 `.git/lumos/` 裡不影響任何判定。
- 已排除:金流:只寫本機紀錄檔
- 已排除:對外送出:不呼叫網路
- 已排除:不可逆:兩本帳都只追加,還原提交即回到原行為

## 驗收條款

- [S1] 當一次提交與推送只產生例行紀錄(沒有 pass、approve、ack)時,版控帳 應 一個位元組都不變,例行紀錄 應 出現在本機帳 [test:t_gov_split_routine_goes_local]
- [S2] code-loop pass、skip 與表態 應 照舊寫進版控帳;換一個全新的副本只靠版控帳,code-loop check 應 照樣判得出留痕 [test:t_gov_split_decisions_stay_tracked]
- [S3] `lumos gov` 與 doctor 的統計段 應 把兩本帳合起來算,同一組事件分流前後總數相同;判定類讀者與帳本成長段 應 只讀版控帳 [test:t_gov_split_readers_union]
- [S4] 當本機帳寫不進去時,走 `_gate_event` 的那一路 應 照舊在錯誤輸出講 telemetry-write-failed,判定 應 不受影響 [test:t_gov_split_local_write_failure]
- [S5] 當在 worktree 裡跑時,例行紀錄 應 寫到共用的那一份本機帳;有 docs/ 但取不到 git 共用資料夾時 應 退回寫版控帳 [test:t_gov_split_location]

## 回退

還原本案的單一功能提交(〈實務隱患〉回滾)。本機帳留著不影響任何判定;要清就刪 `.git/lumos/governance-local.jsonl`。

## 天花板

1. 主動決定寫完,工作目錄還是會髒(例如 code-loop pass 之後)。這是刻意的:這些本來就要提交,pass 之後工具也會印出提交指令。
2. 跨機器的例行統計看不到。S18 的度量式撤除條件(`[retire:度量 <閘>.<種類> …]`)用到右欄種類時,計數變成「這台機器的本機帳加版控帳」;用小於或等於比較的,可能在別台機器看不到的情況下判成「該撤」。S18 只是 doctor 的軟提醒、`--ci` 不跑,誤判只會多一句提醒,不會改任何判定。
3. 分流表是人寫的;新增閘名時要記得放進表裡,沒放就照舊進版控帳(偏吵,不偏丟)。
