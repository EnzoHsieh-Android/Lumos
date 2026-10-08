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
  WHY:例行操作(提交、推送、查筆記)不再弄髒版控檔——治理帳裡「檢查自動跑出來的觀察」改寫進被忽略的本機帳 docs/.governance-local.jsonl,主動決定、擋人紀錄、繞道與自動放行的痕跡照舊進版控帳;使用紀錄帳改寫進被忽略的 docs/.usage-local.jsonl,舊檔原地凍結不再寫 [出處:2026-10-04 雲端工作階段每回合被「有沒提交的改動」打斷;設計審 r1、r2 各六席] [因:例行紀錄只有本機統計在讀,CI 讀的是代碼審留痕與修正關卡] [不選:整本治理帳移出版控(CI 讀不到代碼審留痕,2026-09-09 裁定治理帳是 CI 唯一權威來源);本機帳放 .git/lumos/(專案第一個放在 .git 底下的狀態檔,第二種做法;r1 架構對齊席判 major,使用者裁沿用 .ci-log 的做法);分流用「種類黑名單」(r2 四席指出觀察型閘新增的略過、擋人種類會漏進本機帳);本 repo 對舊使用紀錄帳停止追蹤(r2 三席實測:別台機器 pull 時磁碟上的檔會被刪、檔被寫過時 pull 會中止)]
---
# 治理帳例行紀錄分流_計劃

白話:現在提交一次、推送一次、查一篇筆記,工具都會往進版控的帳裡寫幾行(「每支檔有家:通過」「刪除守衛:沒事」「健康檢查跑過一次」「某篇筆記被查過」),於是工作目錄永遠有沒提交的改動——雲端工作階段每回合被提醒打斷,本機 git status 永遠不乾淨,這些紀錄不是被順手夾進不相干的提交,就是一直堆著。這份讓**例行操作之後工作目錄保持乾淨**:檢查自動跑出來的觀察改寫進被忽略的本機帳;有人做了決定、有人被擋、有人繞過或工具自動放行的紀錄,照舊進版控。

依據:2026-10-04 盤點(〈盤點〉);設計審 r1、r2(〈審計修正紀錄〉)。

PRIOR-ART: 沿用專案既有的本機流水帳做法——`docs/.ci-log.jsonl` 放在 docs/、根 `.gitignore` 忽略,檔名一個具名常數、路徑一支取路徑函式(`CI_LOG_NAME`、`_ci_log_path`),消費專案由 init 寫進 `docs/.gitignore`;合併讀帳沿用 `cmd_gov` 裡既有的 `load`。不新增本機狀態的位置,也不新增寫帳入口。
RETIRE-IF: 上線滿 8 週後,有讀者要用「別台機器的例行紀錄」,或例行紀錄又用別的方式長回版控帳,就重新評估要不要合回一本。
REVISIT:2026-12-01 比較上線前後各 8 週裡「只動帳本檔的提交」數量(`git log --since` 加 `--name-only` 篩),上線後應明顯變少;並對照 RETIRE-IF

## 盤點

- **進版控的帳**:本 repo 追蹤 7 本——治理帳、使用紀錄帳、canary、bypass、kill、signoff、escape。例行操作會寫的只有兩本:治理帳(提交前、推送前、`doctor --ci` 的檢查)與使用紀錄帳(每次 `lumos show`、`lumos context`,寫入點 `_usage_log`)。其餘五本只在主動操作時寫,照舊進版控。
- **使用紀錄帳**:程式裡**沒有任何讀者**(只寫不讀),是留給未來「最近常查」排序的語料種子([[Systems/retrieval-ranking]]、[[Verification/2026-08-21_工具鏈體檢修復批]] 的 REVISIT 2026-11-19)。2026-08-21 之後建的消費專案 `docs/.gitignore` 忽略它;更早建的 vault 沒有 `docs/.gitignore`(那時忽略檔寫在 vault 裡);本 repo 一路追蹤它。
- **治理帳的寫入**:直接開檔寫的只有四支——`_gate_event`、`_append_governance_log`、`_codeloop_gov_log`、`_codeloop_dispositions_gov_log`;`_loop_gov_mark`、`_bound_tests_log`、`_gate_failopen`、`_delguard_log_result` 都是轉呼叫它們的包裝。hooks 與 CI 不直接寫。
- **治理帳的判定類讀者**(只讀版控帳):`_codeloop_read_from_ledger`、`_codeloop_read_dispositions`、`_fix_check_events` 與 `_fix_check_status`、`_loop_close_stamps`、`_escape_released_loops`、`cmd_loop_rewrite` 的血緣、`governance/autonomous_loop/replay_weekly.py`。它們讀的全是 code-loop、fix-check、design-loop 三個閘,本案不分流這三個閘的任何種類。
- **治理帳的統計類讀者**(只出提醒):`lumos gov`(含 `--stats`、`--nags`;`autonomous-loop.sh` 每週也跑 `--nags`)、doctor 的 spec-gate 段後半(紅綠弱證據,讀 spec-gate-run;前半的比例讀 canary 帳,不受影響)、S18 度量式撤除條件、lint-new 自動放行計數(只讀 fail-open,留版控,不改)。doctor 的帳本成長段量的是版控帳這個檔,另算。
- 本 repo 不是淺層副本;淺層副本每次推送寫的 skipped-env 是略過痕跡,照舊進版控(〈天花板〉)。

## 範圍

- **做**:①治理帳在寫入那一刻逐筆分流;②使用紀錄帳改寫新檔;③兩本本機帳的檔名與忽略規則(本 repo 與消費專案);④統計類讀者兩本一起讀;⑤改到的既有測試、圖譜筆記、手冊、程式註解同步(〈做法〉7)。
- **不做**:不拆版控帳本身(〈全repo審視〉#18);不對任何已追蹤的檔停止追蹤;不動 canary、bypass、kill、signoff、escape 五本;不改雲端平台那支提醒;不自動提交帳本;不搬舊紀錄。

## 做法

1. **分流規則(白名單)**:一筆治理帳事件寫進本機帳,要**同時**符合兩件事,否則一律進版控帳:
   - 「閘名+種類」在本機名單 `_GOV_LOCAL_PAIRS` 上(兩個欄位都要精確相等;任一欄位不是字串就不算);
   - `hard` 恰好是 `False`(缺欄位、不是布林都不算)。

   本機名單只收「乾淨通過」或「純提醒觀察」的組合:

   | 閘 | 收的種類 |
   |---|---|
   | doctor-run | ran |
   | doctor 寫的 check-* 各閘(以 `_KNOWN_GATES` 裡 check- 開頭的閘名為準,實作時逐一列進常數,不用前綴比對) | warned |
   | ledger-growth | fast |
   | daily-wrapper | unreadable、stale、step-failed、watchdog-absent、watchdog-stale |
   | nodehome-check、drift-check | passed |
   | note-shape | hinted |
   | delguard | ok |
   | bound-tests | green |
   | note-reread | reminded、covered、none |
   | spec-gate | spec-gate-run |

   不在名單上的一律進版控帳,包括:擋人(blocked、red-blocked、unfilterable)、略過與繞道(skipped、skipped-env、skipped-flag、shallow-skip)、提醒模式下放行(warned 之於 nodehome-check、drift-check、note-shape)、放寬設定(relaxed)、自動放行與降級(fail-open、degraded、red-advisory)、判斷不了(range-unavailable、diff-unavailable、no-config、whole-suite-deferred)、主動決定(acked、fix、recorded、waived、approved、prepare),以及 code-loop、fix-check、design-loop 等閘的全部種類。**新增的閘或種類沒加進名單,就照舊進版控帳**——分錯只會偏吵。
2. **防漂移釘**:一支測試釘住三件事——本機名單的閘名都在 `_KNOWN_GATES` 裡;本機名單的每個種類在程式裡真的有人寫;判定類讀者讀的三個閘(code-loop、fix-check、design-loop)不出現在本機名單裡。比照既有的 `t_gov_stats_gate_drift`。
3. **本機帳的檔名與路徑**:比照 `CI_LOG_NAME`:常數 `GOV_LOCAL_LOG_NAME = ".governance-local.jsonl"`、`USAGE_LOCAL_LOG_NAME = ".usage-local.jsonl"`;取路徑的函式吃「docs 資料夾」一個參數(三個寫入器各自已經算得出 docs 資料夾:`_gate_event` 用 `root / "docs"`、`_append_governance_log` 用 `vault.parent`),回傳同一層的本機帳。docs/ 不存在時跟現在一樣不寫。每個 worktree 各一份,不需要新資料夾。
4. **寫入器怎麼分**:`_gate_event` 一次一筆,決定路徑後照舊寫;`_append_governance_log` 一次一批,在迴圈裡逐筆決定,兩本各自開檔、各自吞錯——本機帳寫不進去不得連累同一批要進版控帳的事件。寫不進去的處理維持現狀(`_gate_event` 回 False、呼叫端講 telemetry-write-failed;`_append_governance_log` 靜默)。`_usage_log` 改寫 `USAGE_LOCAL_LOG_NAME`,舊的 `.usage-log.jsonl` 不再寫入、原地凍結(已追蹤的照舊追蹤,不會從任何人的磁碟消失)。
5. **忽略規則**:
   - 本 repo:根 `.gitignore` 加 `docs/.governance-local.jsonl` 與 `docs/.usage-local.jsonl`。
   - 新建 vault:`_scaffold_project` 寫的 `docs/.gitignore` 加這兩行。
   - 既有 vault:`_init_additive_setup` 處理 `docs/.gitignore`——不存在就照 `governance/.gitignore` 的先例建一份(內容同新建 vault 的那份;已追蹤的檔不受 .gitignore 影響);存在就逐行比對(去頭尾空白、容許 CRLF,整行相等才算有),缺的追加到尾端,原檔最後一行沒換行時先補一個換行。抽成一支小函式,只加不改既有行。
   - 全域工具更新後到專案跑 `lumos update` 之前,本機帳會以未追蹤檔出現(偏吵);`lumos doctor` 加一行軟提醒:本機帳存在但沒被忽略時,提示跑 `lumos update`。
6. **讀者**:`cmd_gov` 的 `load` 多讀本機帳(跟它讀 .ci-log 一樣,檔不在就跳過,欄位對應共用治理帳那一套);S18 度量改用擴充後的 `_gov_metric_events` 讀兩本,「最舊一筆」取兩本的最小時間;spec-gate 段後半讀 spec-gate-run 時,兩本合起來**依時間排序**後再取最後一筆。**判定類讀者一行不改**。帳本成長段照舊只量版控帳;本機帳另加一行只看大小的軟提醒(超過版控帳同一個大小上限才提醒,不看成長倍數)。
7. **同步範圍**(實作時逐條改,改完在計劃裡打勾):
   - 測試:r2 整合席報告列出的既有測試(斷言例行事件寫進 `docs/.governance-log.jsonl`、斷言 `.usage-log.jsonl` 被寫的),改成讀對應的本機帳。
   - 圖譜:[[Systems/reversibility-governance-ledger]] 的來源本數(含它的 `lumos:count` 正則)、唯一寫者、「帳檔都進版控」的說法;[[Systems/retrieval-ranking]]、[[Systems/lumos-cli-read]] 與 [[Verification/2026-08-21_工具鏈體檢修復批]] 裡使用紀錄帳的檔名;兩條近期到期的 REVISIT(合約測試閘、守檔筆記對照改動)若讀的是本機名單上的種類,改成用 `lumos gov` 查。
   - 手冊:`skills/lumos-project-notes/reference.md` 講治理帳寫在哪裡的段落。
   - 程式註解:scaffold 與 `_init_additive_setup` 的忽略清單註解。

## 實務隱患

- **守衛面(本案的主風險)**:分錯一筆擋人紀錄或略過痕跡進本機帳,CI 與別台機器就看不到。三道保險:本機名單是白名單,只收列名的「閘+種類」;`hard` 必須恰好是 False;防漂移釘守住判定類讀者的三個閘永遠不在名單上。判定類讀者一行不改,所以分流不會讓任何閘從擋變放。
- **相容**:舊紀錄留在版控帳,統計讀者兩本都讀;舊使用紀錄帳凍結不刪;沒有任何檔停止追蹤,所以別台機器 pull、合併都不會刪檔或衝突。
- **跨機器**:本機帳每台機器、每個 worktree 各一份(〈天花板〉)。
- **帳本成長**:版控帳成長變慢;本機帳由大小軟提醒看管。
- **回滾**:還原本案提交即可。舊版不讀本機帳,上線期間的例行觀察在統計裡看不到(判定不受影響);本機帳留在磁碟、仍被忽略。已經被 init 補過 `.gitignore` 的消費專案,多出的兩行忽略規則無害。
- 已排除:金流:只寫本機紀錄檔
- 已排除:對外送出:不呼叫網路
- 已排除:不可逆:兩本帳都只追加,不停止追蹤任何檔,還原提交即回到原行為

## 驗收條款

- [S1] 當一次提交、推送與幾次 `lumos show`、`lumos context` 都只產生例行紀錄時,所有進版控的檔 應 一個位元組都不變,例行紀錄 應 出現在本機帳 [test:t_gov_split_routine_goes_local]
- [S2] 當事件的「閘名+種類」不在本機名單上、或 hard 不是恰好 False(含缺欄位與非布林)時,這筆 應 寫進版控帳;skipped-flag、unfilterable、shallow-skip、warned 之於 drift-check 都 應 進版控帳;code-loop 的留痕與表態在全新副本只靠版控帳 應 照樣判得出 [test:t_gov_split_decisions_stay_tracked]
- [S3] `lumos gov` 與 S18 度量、spec-gate 段後半 應 把兩本帳合起來、依時間排序後算,同一組事件分流前後結果相同;判定類讀者與帳本成長段 應 只讀版控帳 [test:t_gov_split_readers_union]
- [S4] 當同一批事件裡本機帳寫不進去時,同批要進版控帳的事件 應 照樣寫進去,走 `_gate_event` 的那一路 應 照舊講 telemetry-write-failed [test:t_gov_split_local_write_failure]
- [S5] 當對既有 vault 跑 init 時,`docs/.gitignore` 不存在 應 建一份,存在而缺行 應 補上(原檔尾沒換行時先補換行)、已有 應 不重複 [test:t_gov_split_ignore_rule]
- [S6] 本機名單的閘名 應 都在 `_KNOWN_GATES` 裡、種類 應 都有寫入點,code-loop、fix-check、design-loop 應 不在名單上 [test:t_gov_split_pairs_drift]

## 回退

還原本案的單一功能提交(〈實務隱患〉回滾)。兩本本機帳留在磁碟、仍被忽略,不影響任何判定;要清就刪 `docs/.governance-local.jsonl` 與 `docs/.usage-local.jsonl`。

## 天花板

1. 主動決定、擋人、略過與提醒模式放行之後,工作目錄還是會髒。這是刻意的:這些本來就要提交。
2. 跨機器的例行統計看不到。`gov --stats` 的「從沒觸發的閘」在全新副本上會把觀察型閘算成沒觸發;`autonomous-loop.sh` 每週跑的 `--nags` 只看得到排程所在那份副本的本機帳。S18 度量用到本機名單上的種類時,計數變成「這台機器的本機帳加版控帳」,用小於或等於比較的可能在別台機器判成「該撤」——S18 只是軟提醒、`--ci` 不跑。
3. 淺層副本每次推送寫的 skipped-env 照舊進版控帳(略過痕跡),那種環境下 [S1] 不成立。
4. 本機名單是人寫的;新增的「乾淨通過」種類沒加進名單,只會留在版控帳(偏吵)。

## 審計修正紀錄

- r1(2026-10-04,6 席:正確性、邊界、整合、併發、回滾各 sonnet 加架構對齊 sonnet):43 條/blocking 14 條/範圍擴大到使用紀錄帳、本機帳改沿用 .ci-log 做法、分流改成三道規則。卷證 `governance/review-reports/gov-ledger-split/`。
- r1 主要折入:繞道與自動放行痕跡全數留版控(多席一致);check-r 等擋人紀錄靠 hard 規則留版控;使用紀錄帳讓目標達不到(三席一致,使用者裁一起處理);本機帳位置改沿用 `.ci-log`(架構對齊 major,使用者裁);同批兩本各自吞錯;讀者沿用 `cmd_gov` 的 `load`;既有測試與文件同步列入範圍;REVISIT 改成量得到的指標;本機帳加成長軟提醒。
- r2(2026-10-04,同 6 席):41 條/blocking 11 條/種類條件改白名單、使用紀錄帳改寫新檔不停止追蹤、舊 vault 補建 .gitignore。卷證同上 r2-*。
- r2 主要折入:種類黑名單漏掉 skipped-flag、unfilterable、shallow-skip 與提醒模式的 warned(正確性、邊界、併發、整合四席一致)→ 改成「閘名+種類」白名單、hard 必須恰好 False、加防漂移釘 [S6];停止追蹤使用紀錄帳會讓別台機器 pull 刪檔或中止(回滾、邊界實測,併發一致)→ 改寫新檔、舊檔凍結;舊 vault 沒有 docs/.gitignore(邊界、整合、正確性)→ 不存在就建,存在逐行比對、補換行(邊界、併發);兩本合併讀依時間排序、S18 最舊取最小(回滾、併發、正確性);使用紀錄帳實為只寫不讀、同步範圍擴大到 REVISIT 與 count 標記(整合、正確性);取路徑函式吃 docs 資料夾(架構對齊、邊界);本機帳成長只看大小(邊界);更新後未跑 update 的軟提醒(回滾)。
