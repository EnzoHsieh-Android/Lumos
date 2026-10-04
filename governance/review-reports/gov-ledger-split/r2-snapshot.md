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
  WHY:例行操作(提交、推送、查筆記)不再弄髒版控檔——治理帳裡「檢查自動跑出來的觀察」改寫進被忽略的本機帳 docs/.governance-local.jsonl,主動決定、擋人紀錄、繞道與自動放行的痕跡照舊進版控帳;本 repo 的使用紀錄帳停止追蹤(消費專案本來就忽略它) [出處:2026-10-04 雲端工作階段每回合被「有沒提交的改動」打斷;設計審 r1 六席] [因:例行紀錄只有本機統計在讀,CI 讀的是代碼審留痕與修正關卡] [不選:整本治理帳移出版控(CI 讀不到代碼審留痕,2026-09-09 裁定治理帳是 CI 唯一權威來源);本機帳放 .git/lumos/(專案第一個放在 .git 底下的狀態檔,第二種做法;r1 架構對齊席判 major,使用者裁沿用 .ci-log 的做法)]
---
# 治理帳例行紀錄分流_計劃

白話:現在提交一次、推送一次、查一篇筆記,工具都會往進版控的帳裡寫幾行(「每支檔有家:通過」「刪除守衛:沒事」「健康檢查跑過一次」「某篇筆記被查過」),於是工作目錄永遠有沒提交的改動——雲端工作階段每回合被提醒打斷,本機 git status 永遠不乾淨,這些紀錄不是被順手夾進不相干的提交,就是一直堆著。這份讓**例行操作之後工作目錄保持乾淨**:檢查自動跑出來的觀察改寫進被忽略的本機帳;有人做了決定、有人被擋、有人繞過或工具自動放行的紀錄,照舊進版控。

依據:2026-10-04 盤點(〈盤點〉);設計審 r1 六席(〈審計修正紀錄〉)。

PRIOR-ART: 沿用專案既有的本機流水帳做法——`docs/.ci-log.jsonl` 放在 docs/、根 `.gitignore` 忽略,檔名一個具名常數、路徑一支取路徑函式(`CI_LOG_NAME`、`_ci_log_path`),消費專案由 init 寫進 `docs/.gitignore`;合併讀帳沿用 `cmd_gov` 裡既有的 `load`。不新增本機狀態的位置,也不新增寫帳入口。
RETIRE-IF: 上線滿 8 週後,有讀者要用「別台機器的例行紀錄」,或例行紀錄又用別的方式長回版控帳,就重新評估要不要合回一本。
REVISIT:2026-12-01 比較上線前後各 8 週裡「只動帳本檔的提交」數量(`git log --since` 加 `--name-only` 篩),上線後應明顯變少;並對照 RETIRE-IF

## 盤點

- **進版控的帳**:本 repo 追蹤 7 本——治理帳、使用紀錄帳、canary、bypass、kill、signoff、escape。例行操作會寫的只有兩本:治理帳(提交前、推送前、`doctor --ci` 的檢查)與使用紀錄帳(每次 `lumos show`、`lumos context`)。其餘五本只在主動操作時寫(記審查帳、繞過推送閘、跑殺傷力配方、簽核、記逃逸),照舊進版控。
- **使用紀錄帳**:只有本機的使用統計在讀,沒有任何判定讀它。消費專案的 `docs/.gitignore` 從建 vault 起就忽略它;只有本 repo 因為早年忽略規則寫錯位置(寫在 vault 裡而不是 docs/)被一路追蹤下來。
- **治理帳的寫入**:直接開檔寫的只有四支——`_gate_event`、`_append_governance_log`、`_codeloop_gov_log`、`_codeloop_dispositions_gov_log`;`_loop_gov_mark`、`_bound_tests_log`、`_gate_failopen`、`_delguard_log_result` 都是轉呼叫它們的包裝。hooks 與 CI 不直接寫。
- **治理帳的判定類讀者**(其他機器或 CI 一定要讀到,只讀版控帳):`_codeloop_read_from_ledger`(code-loop 的 passed、skipped)、`_codeloop_read_dispositions`、`_fix_check_events` 與 `_fix_check_status`、`_loop_close_stamps`(迴圈開關)、`_escape_released_loops`、`cmd_loop_rewrite` 的血緣、`governance/autonomous_loop/replay_weekly.py`。它們讀的全是 code-loop、fix-check、design-loop 三個閘,本案不分流這三個閘。
- **治理帳的統計類讀者**(只出提醒,不擋):`lumos gov`(含 `--stats`、`--nags`)、doctor 的 spec-gate 比例段、S18 度量式撤除條件、lint-new 自動放行計數。doctor 的帳本成長段量的是版控帳**這個檔**的大小與倍數,另算(〈做法〉5)。
- CI 寫的紀錄本來就白寫(用完的副本整個丟掉)。

## 範圍

- **做**:①治理帳在寫入那一刻逐筆分流;②本機帳的檔名、忽略規則(本 repo 與消費專案);③統計類讀者兩本一起讀;④本 repo 停止追蹤使用紀錄帳;⑤改到的既有測試、圖譜筆記與手冊同步。
- **不做**:不拆版控帳本身(〈全repo審視〉#18 裁定不分檔,四個整檔讀者讀到的主動決定一筆不少);不動 canary、bypass、kill、signoff、escape 五本;不改雲端平台那支提醒;不自動提交帳本;不搬舊紀錄。

## 做法

1. **分流規則**:一筆事件寫進本機帳,要**同時**符合三件事,否則一律進版控帳:
   - 閘名在「觀察型閘」名單上:doctor-run、doctor 各段 check-*、ledger-growth、daily-wrapper、nodehome-check、note-shape、delguard、drift-check、bound-tests、spec-gate、note-reread;
   - 這筆不是擋人的紀錄(`hard` 為假);
   - 種類不在「留痕種類」名單上:skipped、skipped-env、fail-open、relaxed、degraded(略過、繞道、放寬設定、工具出錯自動放行的痕跡),以及 acked、fix、recorded、waived、approved、prepare(主動決定)。

   兩份名單是唯一定義,各放一個常數,寫入器查它們決定路徑。新增的閘或種類沒放進名單,就照舊進版控帳——分錯只會偏吵,不會偏丟。code-loop、fix-check、design-loop、anchor、anchor-approve、canary、escape-auto、lint-new、note-audit 這幾個閘整個不在觀察型名單上。
2. **本機帳**:檔名常數 `GOV_LOCAL_LOG_NAME = ".governance-local.jsonl"`,取路徑的函式跟版控帳同一個資料夾(`<docs>/.governance-local.jsonl`),照 `CI_LOG_NAME`/`_ci_log_path` 的樣子寫。docs/ 不存在時跟現在一樣不寫;本機帳跟版控帳同一層,所以每個 worktree 各有一份,不需要 `git rev-parse --git-common-dir`,也不需要建新資料夾。
3. **寫入器怎麼分**:`_gate_event` 一次一筆,決定路徑後照舊寫;`_append_governance_log` 一次一批,在迴圈裡逐筆決定,**兩本各自開檔、各自吞錯**——本機帳寫不進去不得連累同一批要進版控帳的事件。寫不進去的處理維持現狀:`_gate_event` 回 False、呼叫端講 telemetry-write-failed;`_append_governance_log` 靜默。寫法沿用各寫入器現有的(本案不改它們的原子性;兩本帳跟今天一樣是同一層、同一批寫者,併發樣貌不變)。
4. **忽略規則**:本 repo 在根 `.gitignore` 加 `docs/.governance-local.jsonl` 與 `docs/.usage-log.jsonl`,並對使用紀錄帳做一次停止追蹤(`git rm --cached`,檔案留在磁碟)。消費專案:新建 vault 的 `docs/.gitignore` 加一行 `.governance-local.jsonl`;既有 vault 由 `_init_additive_setup` 補——`docs/.gitignore` 存在而缺這一行就在尾端追加,不存在就不建(維持「只加不覆寫」)。
5. **讀者**:`cmd_gov` 的 `load` 多讀一本本機帳(跟它讀 .ci-log 一樣,檔不在就跳過);doctor 的 spec-gate 比例段與 S18 度量改成讀兩本(抽一支模組層級的小函式給它們共用,`cmd_gov` 的 `load` 不搬);lint-new 自動放行計數只讀 fail-open,而 fail-open 留在版控帳,所以不改;**判定類讀者一行不改**。帳本成長段照舊只量版控帳,另外對本機帳加一行同門檻的軟提醒(超過上限只提醒,不擋)。
6. **既有測試與文件**:實作時 grep 測試裡斷言「例行事件出現在 docs/.governance-log.jsonl」的地方,改成讀本機帳;`Systems/reversibility-governance-ledger` 裡「來源幾本」「唯一寫者」「帳檔都進版控」的說法、手冊提到治理帳寫在哪裡的段落、scaffold 的註解,一起改。

## 實務隱患

- **守衛面(本案的主風險)**:分錯一筆擋人紀錄或繞道痕跡進本機帳,CI 與別台機器就看不到。三道保險:觀察型名單之外一律留版控;`hard` 為真一律留;略過、繞道、自動放行與主動決定的種類一律留。判定類讀者讀的三個閘整個不分流,所以分流不會讓任何閘從擋變放。
- **相容**:舊紀錄留在版控帳,統計讀者兩本都讀。消費專案的使用紀錄帳本來就被忽略,不受影響;本機帳的忽略規則靠 init 補,沒補到的專案只會看到一個未追蹤的檔(偏吵,不偏丟)。
- **跨機器**:本機帳每台機器、每個 worktree 各一份,跨機器的例行統計看不到(〈天花板〉)。
- **帳本成長**:版控帳成長變慢;本機帳由成長段的軟提醒看管。
- **回滾**:還原本案提交即可。舊版不讀本機帳,上線期間的例行觀察在統計裡看不到(判定不受影響);使用紀錄帳要恢復追蹤得手動 `git add -f`。
- 已排除:金流:只寫本機紀錄檔
- 已排除:對外送出:不呼叫網路
- 已排除:不可逆:兩本帳都只追加,停止追蹤不刪磁碟上的檔,還原提交即回到原行為

## 驗收條款

- [S1] 當一次提交、推送與幾次 `lumos show`、`lumos context` 都只產生例行紀錄時,所有進版控的檔 應 一個位元組都不變,例行紀錄 應 出現在本機帳 [test:t_gov_split_routine_goes_local]
- [S2] 當觀察型閘寫的是擋人紀錄(hard 為真)、略過或繞道痕跡、自動放行或主動決定時,這筆 應 寫進版控帳;code-loop 的留痕與表態在全新副本只靠版控帳 應 照樣判得出 [test:t_gov_split_decisions_stay_tracked]
- [S3] `lumos gov` 與 doctor 的 spec-gate 比例段、S18 度量 應 把兩本帳合起來算,同一組事件分流前後計數相同;判定類讀者與帳本成長段 應 只讀版控帳 [test:t_gov_split_readers_union]
- [S4] 當同一批事件裡本機帳寫不進去時,同批要進版控帳的事件 應 照樣寫進去,走 `_gate_event` 的那一路 應 照舊講 telemetry-write-failed [test:t_gov_split_local_write_failure]
- [S5] 當對既有 vault 跑 init 時,`docs/.gitignore` 缺本機帳那一行 應 補上、已有就不重複,`docs/.gitignore` 不存在時 應 不建 [test:t_gov_split_ignore_rule]

## 回退

還原本案的單一功能提交(〈實務隱患〉回滾)。本機帳留在磁碟不影響任何判定;要清就刪 `docs/.governance-local.jsonl`。

## 天花板

1. 主動決定、擋人與繞道之後,工作目錄還是會髒(例如 code-loop pass 之後)。這是刻意的:這些本來就要提交。
2. 跨機器的例行統計看不到。`gov --stats` 的「從沒觸發的閘」在全新副本上會把觀察型閘算成沒觸發過。S18 度量式撤除條件用到本機帳的種類時,計數變成「這台機器的本機帳加版控帳」,用小於或等於比較的可能在別台機器判成「該撤」——S18 只是 doctor 的軟提醒、`--ci` 不跑,誤判只會多一句提醒。
3. 兩份名單是人寫的;新增的閘或種類沒放進名單就照舊進版控帳。

## 審計修正紀錄

- r1(2026-10-04,6 席:正確性、邊界、整合、併發、回滾各 sonnet 加架構對齊 sonnet):約 43 條/blocking 14 條/範圍擴大到使用紀錄帳、本機帳改沿用 .ci-log 做法、分流改成三道規則。卷證 `governance/review-reports/gov-ledger-split/`。
- r1 主要折入:繞道與自動放行痕跡全數留版控(多席一致);check-r 等擋人紀錄靠 hard 規則留版控;fail-open 與觀察型閘的衝突由「留痕種類優先」解掉;使用紀錄帳讓目標達不到(三席一致,使用者裁一起處理);本機帳位置改沿用 `.ci-log`(架構對齊 major,使用者裁),連帶消掉相對路徑、建目錄、worktree 共用併發三條;同批兩本各自吞錯;讀者沿用 `cmd_gov` 的 `load`、lint-new 計數不改、`gov --nags` 經 load 自動涵蓋;既有測試與文件同步列入範圍;REVISIT 改成量得到的指標;本機帳加成長軟提醒;天花板補 `gov --stats` 與 S18 的限制。
