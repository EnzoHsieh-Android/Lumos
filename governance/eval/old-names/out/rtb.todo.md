# rtb 存量舊名清單(量測點 c4daa8fc)

每筆 = 筆記裡還在講、但程式裡已經刪掉的名稱。判準:讀的人照這句去找會找不到東西或做錯事 = 該改;句子本身在講歷史 = 不用改(或補歷史字眼)。

## 第 1 層:已逐筆判過:真或灰(先修這層)(15 筆)

- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:10` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py) — 判灰:2026-09-26 第 2 輪裁定的紀錄;--hold-submit 同一計劃稍後撤除,摘要沒標,讀者可能以為還在
  > WHY: 2026-09-26 第 2 輪設計審與使用者裁定後，第 5 條七日任一天 no_data 即證據不足；DSP 預算調整改單源與 UTC 日期，A/B/C 進度由已提交列重算，AI 複查只定案一次，--hold-submit 攔全部提案出口。出處：本計劃〈使用者裁定〉7、〈審計修正紀錄〉r2。
- `Projects/RTB_Phase15AI找規則模式_計劃.md:9` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py) — 判真:完成計劃的 VERIFY 重驗入口寫 --ai-judge,照做找不到這個參數
  > VERIFY: 本文重驗入口與預定報告指標是 --ai-judge、--batch-id、--demo-id、--ledger、--recordings-dir、--verify、governance/eval/ 下的 phase15-rule-mining.md；涉及的程式路徑以程式碼為準，開場用 `rg --files src/rtb tests` 重驗：investigation_eval.py、investigation_report.py、src/rtb/analy
- `Systems/一鍵展示.md:56` 名稱 `test_the_new_task_counts_as_written_only_once_the_inbox_says_so`(消失於 b2fc5122,原在 tests/demo/test_driver.py) — 判真:稽核 D3:防回歸 [test:] 綁的測試已刪
  > PITFALL: [2026-09-24 第 2 輪代碼審 o1/c3/f1/f2/c1/c2/f4] 「假綠」:展示說照預期,實際上沒驗到該驗的東西。審查員實跑的反例:執行端改成一定重送,F2 照判照預期、摘要照寫「沒有重送」;擋下原因換成規則改了,F4 到 F6 都照預期;分析端把廣告名稱丟掉,F5 照預期;平台寫入比收件口的紀錄早 3 到 7 毫秒,只等平台就斷言會偶發把正確的系統判成對不上。修法:路徑兩份清單加送出次數;F4、F6 斷言舊提案以版本已變擋下、接續原因也
- `Projects/RTB_Phase12一鍵展示與HTML報告_計劃.md:271` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py) — 判真:Phase 12 合約 [S1003] 條文仍寫分析端帶 --ai-judge 時多三個模型變數(稽核 A2 的同一句另一處);有 [test:] 綁定
  > - [S1003] 當驅動程式啟動任何行程時,子行程環境的鍵應只在 PATH、HOME、LANG、USER、PYTHONPATH(值固定為專案 src 的絕對路徑)、該角色需要的金鑰,與有排故障的那一個子行程的 RTB_DEMO_FAULT_NONCE 之內,模型入口另外只多 RTB_MODEL_LIVE、RTB_MODEL、RTB_MODEL_RECORD(與即時模式的登入權杖 CLAUDE_CODE_OAUTH_TOKEN,使用者 2026-09-25 裁定;只在情境列在
- `Projects/RTB_Phase13AI參與決策_計劃.md:433` 名稱 `RenewalSkipped`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py) — 判灰:完成計劃〈租約〉節寫專用例外 RenewalSkipped,沒標歷史,類別已刪
  > - **續租沒成 = 專用例外 `RenewalSkipped`**(〈使用者裁定〉R3-2):
- `Projects/RTB_Phase13AI參與決策_計劃.md:794` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py) — 判灰:完成計劃〈要改寫的既有合約〉寫 runner 帶 --ai-judge 時放寬,沒標歷史,功能已撤
  > - Phase 12 的 [S1003] 放寬成:模型入口照舊多三個模型變數;分析端只在那個情境列在即時清單、而且那次 runner 帶 --ai-judge 時多同樣三個([S1145])。
- `Projects/RTB_Phase15AI找規則模式_計劃.md:133` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py) — 判灰:完成計劃的開工前提「既有 --ai-judge 路徑仍可送提案」;前一個實驗判 NOT_STALE(邊界)
  > - Phase 14 在另一分支持續，這個 main 基底的 `src/rtb/domain/nine_rules.py` 已有九條純函式，但既有 `--ai-judge` 路徑仍可送提案；原 Phase 14 增量 3 文字也保留 AI 提案經規則否決。依本輪代使用者裁定，該增量 3 要移除 runner 的 AI 判斷開關，AI 決策模組只留評估重播；只有含此移除的變更合入 main，並核對 runner 無 AI 判斷開關、展示驅動不再組參數且 F7 走規則路徑，Pha
- `Systems/Mock-DSP.md:84` 名稱 `_is_plain_int`(消失於 ad93430c,原在 src/rtb/dsp/store.py) — 判真:_is_plain_int 在 ad93430 改名成公開的 is_plain_int;照原名 rg 找不到(輕微,同物改名)
  > 型別檢查:2026-09-22 起 `store.py` 與 `server.py` 通過 mypy 嚴格模式。`Operation.params` 與 `expected_version` 都標成未驗證(`dict[str, object]` 與 `object`),`_next_state` 讀預算時用 `_is_plain_int` 收窄,型別檢查因此守得住這條不可信資料的路徑。順手修了兩個真的隱患:`cursor.lastrowid` 可能是 None(現在明確報錯並
- `Systems/一鍵展示.md:123` 名稱 `test_campaign_status_plays_no_part_and_the_standard_does_not_claim_it`(消失於 b2fc5122,原在 tests/demo/test_basis.py) — 判真:Systems 筆記的防回歸清單列了已刪的測試
  > WHY: 分析端的根據不再呼叫規則的私有函式、不再自己另算一次配速:規則公開 `policy.steps`(見 [[Systems/分析行程流程與檢查點]]),`explain` 自己也用它,兩邊不會漂移。根據多一個結論代碼(`BasisCode`),補判斷點依代碼走,改措辭不影響路徑;標準文字只寫規則真的做的事(不看廣告狀態、版本只跟同一批資料比)。出處:代碼審 r1 a1/a6/d1/d8。防回歸:`test_the_basis_uses_only_the_rules_p
- `Systems/分析行程流程與檢查點.md:323` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py) — 判真:稽核 A1:held_rule 與 --hold-submit 的考題結束路徑已撤;held_rule 不是定義名,靠同行 --hold-submit 列到
  > - `ai_judge.py`:退回程式規則時,基本三筆判得出的(暫停、異常、前置過濾那幾道)照規則當場結案;其餘回 `RuleContinue`、退回紀錄的結果代碼記 `rule_round`,開一次新規則輪全量重讀四查詢(AI 期查詢不沿用)。`held_rule` 讓開 AI 時的規則輪定案也照 --hold-submit 攔成考題結束。(原寫「AI 自己答 propose 仍直接建提案、AI 前置過濾不動」已失效:代碼審 r1 起 AI 答 propose 也開規則輪
- `Systems/展示頁面.md:100` 名稱 `test_a_held_twin_that_fell_back_shows_the_rule_path_to_the_exam_hold`、`test_an_untouched_fault_counts_as_finished_and_hides_the_pivot`(消失於 b2fc5122,原在 tests/demo/test_ai_page.py) — 判真:稽核 C2:防回歸兩支測試已刪
  > - WHY:「AI 判不提案、故障沒走到」算進已完成(另標幾個沒走到),列表那一列不寫固定的故障位置;F5 雙胞胎退回之後照規則路徑畫到「只判不送」;這一增量加的頁面文字裡「模型」「提案」照白話規則緊接括號解釋;模型文字的標示統一成「AI 產生、僅供參考」(合約 [S1121] [S1027] 的字面照代使用者裁定改寫)。原先頂端摘要會在沒有對得上錄製時寫出錄製來源,這段頁面顯示已由第二輪裁定撤回,見下段。防回歸:[test:test_an_untouched_fault_c
- `Systems/展示頁面.md:104` 名稱 `test_each_ai_round_shows_evidence_choice_reason_and_takeover`、`test_f5_rounds_keep_each_tasks_takeover_separate`、`test_identical_ai_rounds_show_count_without_hundreds_of_cards`(消失於 b2fc5122,原在 tests/demo/test_ai_page.py、tests/demo/test_page.py) — 判真:稽核 C1:防回歸三支 AI 頁測試已刪
  > WHY: 以下是使用者 2026-09-25 第一輪改版提案的當時安排,第二輪裁定已改掉「摘要先於流程」、「採用限制橫幅」與「下方逐步清單」三處;其餘逐輪配對與流程泳道安排仍適用。當時為了讀者進入詳情就能連起「誰決定、AI 選什麼、最後發生什麼」,把決策摘要、採用限制、獨立的考題結果與預設展開的 AI 逐輪判斷放在預算變化及流程圖之前。逐輪照工作編號與原始順序找程式接手,缺紀錄明寫缺口;相同內容合併標筆數,內容不同則分卡,目的是避免 F7 首屏重複數百張卡。流程圖只保留最後一
- `Systems/展示頁面.md:120` 名稱 `test_ai_cell_does_not_repeat_the_allowed_choices_label`、`test_the_decision_summary_explains_its_jargon_and_says_the_untouched_fault_once`(消失於 b2fc5122,原在 tests/demo/test_ai_page.py、tests/demo/test_page.py) — 判真:稽核 C3:防回歸兩支測試已刪
  > - WHY:浮出框同一格有好幾件工作時只寫「第 N 次」連號;改成「工作 t3 第 2 輪」(AI 那格數輪、其他格數次,按每件工作各自數,跟 AI 逐輪卡一致),沒記工作編號的舊資料照舊連號。AI 格「這一輪允許的選項」欄位值去掉重複的同名開頭。決策摘要不再另寫一次裸詞的「AI 判不提案,故障處理這次沒有走到」(結果摘要已有帶括號解釋的版本;固定標示照情境狀態顯示),白話規則測試補跑故障沒走到的 F2 並掃決策摘要。防回歸:[test:test_repeated_flow_
- `Systems/模型用戶端.md:129` 名稱 `test_the_verification_helper_refuses_outside_the_test_fixture`(消失於 5ec931e0,原在 tests/test_suite_isolation.py) — 判真:稽核 D2:[test:] 綁的測試已刪
  > PITFALL: 帳號家目錄不看 HOME,測試輔助在 pytest 外被呼叫(以為換了 HOME 就隔開)就寫進真的 ~/.rtb:代碼審第 2 輪別的審查席真的寫進了假啟用紀錄與 1055 筆假預留(協調者已移走)。輔助函式現在在共用夾具外拒寫。[test:test_the_verification_helper_refuses_outside_the_test_fixture]
- `Systems/模型用戶端.md:228` 名稱 `preflight_worst_seconds`(消失於 b2fc5122,原在 src/rtb/stepbudget.py) — 判真:Systems 筆記說時限從 preflight_worst_seconds 取,函式已刪
  > - WHY:登入檢查的逾時搬進小常數模組(`LOGIN_CHECK_TIMEOUT_SECONDS`、`preflight_worst_seconds`):展示驅動等分析端的模式行要等到登入預檢做完,時限從這裡取,不從模型後端匯入。

## 第 2 層:過濾最嚴那版列出、還沒判過(照同一標準自己判)(2 筆)

- `Systems/展示頁面.md:106` 名稱 `test_committed_demo_recordings_have_no_ai_fallback_in_f1_to_f6`、`test_demo_recording_guard_catches_a_missing_fake_answer`、`test_f5_rounds_keep_each_tasks_takeover_separate`(消失於 b2fc5122,原在 tests/demo/test_ai_demo.py、tests/demo/test_ai_page.py)
  > WHY: 使用者 2026-09-25 逐項要求第二輪改版:情境標題下先交代觸發與目標,再看流程,結果概述下移;逐步判斷搬到流程格,桌機 hover、觸控點擊、鍵盤可操作且靜態報告離線可用,舊清單移除。每格內容仍用原判斷資料在伺服器端經 `escape_text` 產生,固定雜湊腳本只管顯示與定位;F7 同格同結果合併,不同才分列。AI 輪次依每件工作重數,後續規則判斷帶原有數值與比較結論;詳情橫幅整段移除,頁面只標「AI 產生、僅供參考」,缺錄白話顯示「AI 這次沒有給出回
- `Systems/評估與Jev決策點.md:77` 名稱 `test_the_code_rule_is_scored_per_slice_like_a_candidate`(消失於 b2fc5122,原在 tests/eval/test_evaluation.py)
  > - 計分:逐筆經分析端的路由函式,依退回後的最後有效答案計分;現行規則用同一套(不傳候選)。每格報分子分母、類別正確數、錯誤子型與走了哪條路;「值得加」格的指標是召回率,其他三格是誤提案率,另報類別正確率;無關欄位擾動後答案改變的組數另報。防回歸:[test:test_the_eval_report_is_per_slice_and_marks_thin_slices]、[test:test_irrelevant_fields_do_not_change_the_answer

## 第 3 層:其餘(誤報多,有空再看)(47 筆)

- `Issues/Phase14後筆記漂移清理.md:36` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [[Projects/RTB_Phase13AI參與決策_計劃]] 摘要:最前面加一條 WHY 說明 AI 決策路徑已在 Phase 14 撤除(附重查呼叫者的查詢),四條相關 WHY(--ai-judge、模型只經閘道、續租、F5 的 AI 路徑)前面標「歷史」。原文保留。
- `Projects/RTB_Phase13AI參與決策_計劃.md:162` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > | R3-14 | `--hold-submit` 清單裡的廣告不論 AI 或退回規則判提案,一律不送件、以考題結束結案 | 雙胞胎退回規則時照樣會提案送件,平台多一筆寫入 | 〈F5 對抗案例的預期〉 |
- `Projects/RTB_Phase13AI參與決策_計劃.md:400` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - AI 決策是 runner 的一個開關(`--ai-judge`),加上 `--demo-id`、`--ledger`、`--recordings`、`--batch-id`(錄製批次,見〈錄製批次與入庫〉);沒開就是現在的行為。模式照 Phase 11B:即時開關、展示編號、找得到 claude、啟用紀錄有效,全齊才即時,否則錄製。
- `Projects/RTB_Phase13AI參與決策_計劃.md:416` 名稱 `EXAM_HOLD`(消失於 b2fc5122,原在 src/rtb/analyzer/policy.py、src/rtb/demo/basis.py、src/rtb/demo/driver.py)
  > - **不提案原因用哪個列舉**(〈使用者裁定〉R3-9):AI 的兩個結論沿用 `NoActionReason` 既有的「判不值得加」「判證據不足」;考題結束新加成員 `EXAM_HOLD`(`exam_hold`),也放在 `NoActionReason`。來源(AI、規則或考題)記在調查紀錄。
- `Projects/RTB_Phase13AI參與決策_計劃.md:434` 名稱 `RenewalSkipped`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py)
  > - 續租條件不符(被接手)或等鎖逾時(資料庫忙碌),續租回呼都丟 `RenewalSkipped`。AI 決策函式不接它(它不是模型呼叫失敗類別)。
- `Projects/RTB_Phase13AI參與決策_計劃.md:435` 名稱 `RenewalSkipped`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py)
  > - 流程層處理「分析中」那一步的函式(`_from_analyzing`)在通用的 `except Exception` **之前**先接 `RenewalSkipped`,回「這一步不寫入」(None);沒寫入的路徑照舊用容器裡的收據放掉租約。不呼叫模型、**不轉 FAILED**([S1152])。
- `Projects/RTB_Phase13AI參與決策_計劃.md:437` 名稱 `RenewalSkipped`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py)
  > - **停止旗標**(〈使用者裁定〉R3-3):runner 把「是不是已收到停止」的查詢函式傳給 AI 決策函式;AI 決策函式在**續租前**與**呼叫模型前**各看一次。已經收到停止就不續租、不呼叫模型,丟 `RenewalSkipped`,這一步不寫入([S1161])。runner 回到迴圈頂端看到停止旗標就照舊結束。
- `Projects/RTB_Phase13AI參與決策_計劃.md:445` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - **守衛算式只在帶 `--ai-judge` 時套用**,沒開 AI 時照舊只守 [S1001](一步最多 2 次呼叫 × 逾時 × 2 < 租約);不然現在合法的 `--timeout-seconds 5` 會被拒絕啟動。開 AI 時兩條都要成立,**都逐項加總**(〈使用者裁定〉R3-4):
- `Projects/RTB_Phase13AI參與決策_計劃.md:446` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 蒐集證據那一步 = 取租約等鎖 5 + 讀取次數 6 ×(DSP 逾時 + 呼叫紀錄等鎖 5)+ 提交等鎖 5,要小於租約 60。讀取最多 2 + 4 = 6 次(基本兩次,加上重讀最多 3 個查詢,較長時間窗讀 1 天與 7 天兩次);每次讀 DSP 都在交易外另寫一筆呼叫紀錄,各自可能等鎖 5 秒。DSP 逾時 3 秒(展示用的預設)→ 5 + 6 × 8 + 5 = 58 < 60。反過來說,開 AI 時 DSP 逾時要小於 (60 − 10) ÷ 6 − 5 ≈ 
- `Projects/RTB_Phase13AI參與決策_計劃.md:539` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - **即時模式逐情境開**:驅動收一份「哪些情境即時」清單,預設空的(全部錄製)。只有在清單裡的情境,分析端子行程才拿到三個模型環境變數;而且只在那次 runner 帶 `--ai-judge` 時。Phase 12 的 [S1003] 照這個粒度放寬([S1145])。錄製目錄與批次見〈錄製批次與入庫〉的「即時清單裡的情境」。
- `Projects/RTB_Phase13AI參與決策_計劃.md:564` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - **F5**:受攻擊廣告與雙胞胎都走同一條通用規則(雙胞胎因為 `--hold-submit`,結局一定是不提案:考題結束或 AI/規則判的不提案)。F5 的程式層斷言照舊:名稱不變,金額、廣告、動作種類不變,平台上的寫入只可能是受攻擊廣告照公式的那一筆或沒有寫入。模型考題另列(見〈F5 對抗案例的預期〉)。
- `Projects/RTB_Phase13AI參與決策_計劃.md:591` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 做法:雙胞胎建成一件真的任務,由 F5 的 runner(主執行緒、有租約、有調查紀錄)照一般路徑判。runner 加一個參數 `--hold-submit <廣告清單>`:清單裡的廣告**不論是 AI 判 `propose`,還是退回程式規則(逾時、沒有錄製、登入預檢沒過、「AI 已用過」)後規則判提案**,一律不產生送件,這一步直接以不提案結案,不提案原因是 `NoActionReason` 的新成員「考題結束」(`exam_hold`);調查紀錄照記是誰判的提案([
- `Projects/RTB_Phase13AI參與決策_計劃.md:614` 名稱 `--ai-judge`、`--hold-submit`、`EXAM_HOLD`、`RenewalSkipped`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py、src/rtb/analyzer/policy.py、src/rtb/analyzer/runner.py、src/rtb/demo/basis.py、src/rtb/demo/driver.py)
  > - 範圍:模擬 DSP 兩張新表、兩支唯讀端點與展示種子(逐日趨勢、過去調整,裁定 10;回應格式寫死);domain 指標模組的精確比率函式與收據格式化函式(分數精確算、百分比刻度、金額 2 位、`na`、負零寫 `0.0`、狀態寫短代號);四種收據證據與分析端新讀法(較長時間窗、操作歷史、逐日趨勢、過去調整);調查原始資料表(證據來源回外包型別、經提交函式同交易寫);模擬 DSP 只給種子用的過去日期寫法;固定選項與輪數上限(整件工作累計);回答驗證與證據核對;退回(只接
- `Projects/RTB_Phase13AI參與決策_計劃.md:620` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 範圍:驅動給開 AI 的情境起 runner 帶模型參數;「哪些情境即時」清單與逐情境的環境變數([S1003] 照本計劃改寫),F7 永遠錄製;情境時限依 AI 輪數放寬;F3 照一般情境(驅動不匯入 AI 決策模組);驅動改成依每件工作的結局選預期組的通用規則(等待、路徑核對、故障斷言,F1–F7 全部照它,取代逐情境改法);即時清單情境的專屬錄製目錄與 `demo-live-<展示編號>` 批次;F5 雙胞胎建成真任務、runner 帶 `--hold-submit
- `Projects/RTB_Phase13AI參與決策_計劃.md:661` 名稱 `EXAM_HOLD`(消失於 b2fc5122,原在 src/rtb/analyzer/policy.py、src/rtb/demo/basis.py、src/rtb/demo/driver.py)
  > - 展示流程圖的列舉覆蓋測試:只掃 `MAPPED_ENUMS` 裡的十八個列舉;新的不提案原因(`EXAM_HOLD`)在其中一個列舉裡,沒補圖主線 CI 會紅,新的退回原因列舉要先加進清單才會被擋([S1024] 的「十八個」跟著改)。Phase 10 [S705] 要求現行規則走得到 `NoActionReason` 每個成員,加 `EXAM_HOLD` 會紅,要改寫(見〈調查紀錄與狀態同一交易〉)。
- `Projects/RTB_Phase13AI參與決策_計劃.md:690` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [S1113] 當分析端驅動命令列帶 --ai-judge 啟動、而且蒐集證據一步的最壞耗時(取租約等鎖加 6 次讀取各自的 DSP 逾時與呼叫紀錄等鎖加提交等鎖)不小於租約,或從續租讀時鐘之後算起 AI 那一步的最壞耗時(模型逾時 15 加行程群組清理加 4 次花費帳等鎖加送出前記次等鎖加提交等鎖)不小於租約時,驅動命令列應拒絕啟動,算式的每個數字應取自真常數;沒帶 --ai-judge 時應照舊只守 [S1001]。(2026-09-26 [[Projects/RTB
- `Projects/RTB_Phase13AI參與決策_計劃.md:693` 名稱 `--ai-judge`、`AiWorld`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py、tests/analyzer/test_investigation_e2e.py)
  > - 2026-09-26 代使用者裁定：保留執行端／收件口不得讀調查紀錄及提案不得帶模型欄位；原 `test_the_executor_never_sees_model_rounds` 中用 `AiWorld` 帶 `--ai-judge` 送件那半改用純規則提案，靜態匯入檢查保留。 見 [[Projects/RTB_Phase14正式規則照九條判斷_計劃]]〈拆增量〉3 翻案索引。
- `Projects/RTB_Phase13AI參與決策_計劃.md:709` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [S1124] 當 F5 開了 AI 決策時,驅動程式應照樣斷言程式層不變量與全平台只可能有受攻擊廣告那一筆寫入;雙胞胎應是 runner 照一般路徑判的真任務、列在 --hold-submit 清單裡不送件,考題結果應比對兩件任務調查紀錄的選項序列與結論後另外記下。 [test:test_f5_adversarial_name_preserves_rule_and_traceable_narrative]
- `Projects/RTB_Phase13AI參與決策_計劃.md:727` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [S1136] 當分析端驅動命令列帶 --ai-judge 時,展示啟動器停它的寬限時間應用跟守衛同一組匯入的常數算出,而且不小於續租等鎖加上續租後 AI 那一步的最壞耗時。(2026-09-26 照 [[Projects/RTB_Phase14正式規則照九條判斷_計劃]] [S1419] 改寫:沒帶 --ai-judge 的舊 7 秒寬限撤掉,改取 max(舊兩讀寬限, 規則輪 A/B/C 最壞秒數),預設 50 秒;帶 --ai-judge 再跟 AI 步取最大值。)
- `Projects/RTB_Phase13AI參與決策_計劃.md:743` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [S1145] 驅動程式應只給列在即時清單裡、而且那次帶 --ai-judge 的情境的分析端子行程三個模型環境變數;即時清單預設應是空的,F7 應不准放進清單。 [test:test_only_listed_scenarios_get_live_model_env_for_their_entries] [test:test_the_server_refuses_only_unknown_codes_in_the_live_list]
- `Projects/RTB_Phase13AI參與決策_計劃.md:744` 名稱 `test_only_listed_scenarios_get_live_model_env_and_f7_never_does`(消失於 b2fc5122,原在 tests/demo/test_ai_demo.py)
  > - 2026-09-26 代使用者裁定：改寫：分析端不拿模型環境變數；即時清單只給說明／假說入口。F7 的 AI 慢限制與 `NEVER_LIVE` 明確撤除，若規則提案需說明仍按普通即時／錄製政策；`server.py` 同步不拒 F7。舊 `test_only_listed_scenarios_get_live_model_env_and_f7_never_does` 與 server 拒 F7 測試改綁入口環境和未知代碼拒收。理由與落地測試見 [[Projects/RT
- `Projects/RTB_Phase13AI參與決策_計劃.md:746` 名稱 `_verdict`(消失於 b2b17ea8,原在 src/rtb/eval/investigation_eval.py)
  > - 2026-09-26 代使用者裁定：改寫：評估執行器直接呼叫 Judge，含錄製重播與授權即時錄製；`RuleContinue` 分支的 AI `propose` 留原始值得加、退回用 `rule_verdict(case)`，其他結果由 `_verdict(outcome)` 轉成原始結論；沒有記憶體 `TaskStore`、flow 續租或 A/B/C 輪。原 `test_the_investigation_eval_runs_the_same_ai_judge` 改
- `Projects/RTB_Phase13AI參與決策_計劃.md:754` 名稱 `RenewalSkipped`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py)
  > - [S1152] 當續租條件不符或等鎖逾時時,續租回呼應丟 RenewalSkipped,流程層應在通用例外處理之前接住它、這一步不寫入並放掉租約,應不呼叫模型,這件工作應不轉失敗。 [manual:核對 Phase 14 增量 3 已刪除此入口與舊測試,見 Verification/Phase14增量3驗證紀錄]
- `Projects/RTB_Phase13AI參與決策_計劃.md:760` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [S1156] 當分析端驅動命令列帶 --hold-submit 而清單裡的廣告被判值得加時,不論是 AI 判的還是退回程式規則判的,都應不產生送件,這一步應以不提案結案、原因是考題結束,調查紀錄應照記是誰判的(2026-09-26 [[Projects/RTB_Phase14正式規則照九條判斷_計劃]] 增量 2b:退回改走規則輪後,規則輪定案也照清單攔;純規則路徑與全部出口的集中攔截 [S1421] 是增量 3);清單外的廣告應照舊送件。 [manual:核對 Pha
- `Projects/RTB_Phase13AI參與決策_計劃.md:836` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 實作者解讀(2026-09-25):[S1102] 的「開了 AI 決策的分析端驅動命令列」那半要等增量 2 有 `--ai-judge` 才測得到;增量 1 綁說明與假說兩支命令列。
- `Projects/RTB_Phase13AI參與決策_計劃.md:860` 名稱 `__setattr__`(消失於 0e36970a,原在 src/rtb/analyzer/policy.py)
  > - 實作者解讀(2026-09-25,代碼審 r3 後):共用的錄製檔驗證也核對呼叫者是合法成員。呼叫者的靜態檢查再補:三個收呼叫者的名字(`open_gate`、`ModelRequest`、`Gate`)帶 `**` 展開一律不准;`replace(…, caller=…)`、送出點裡帶 `**` 的 `replace`、`__setattr__`/`setattr(…, "caller", …)`、把 Caller 攤開來挑成員(`list(Caller)[…]`、`n
- `Projects/RTB_Phase13AI參與決策_計劃.md:867` 名稱 `--ai-judge`、`--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 實作者解讀(2026-09-25):`--hold-submit` 收逗號分隔的廣告編號;只在帶 `--ai-judge` 時可用,沒帶就拒絕啟動(只判不送是 AI 考題用的,沒開 AI 時沒有調查紀錄可記「誰判的」)。攔在 AI 決策函式的出口:不論 AI 判、退回規則判、「AI 已用過」或登入預檢沒過後規則判的提案,都改成不提案、原因 `exam_hold`,調查紀錄照記。
- `Projects/RTB_Phase13AI參與決策_計劃.md:873` 名稱 `RenewalSkipped`、`renew_lease`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py、src/rtb/analyzer/task_store.py)
  > - 實作者解讀(2026-09-25):續租等鎖逾時由任務模組的 `renew_lease` 回 None(跟條件不符同一個出口),續租回呼一律丟 `RenewalSkipped`。
- `Projects/RTB_Phase13AI參與決策_計劃.md:945` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 實作者解讀(2026-09-25):「哪些情境即時」清單是驅動程式的 `live` 參數,展示伺服器的 `--live F1,F5` 給它(預設空的);F7 或不認得的情境建驅動時就拒。分析端的三個模型變數由啟動器在「情境列在清單而且這次參數帶 --ai-judge」時才給([S1145]);說明與假說兩支命令列是模型入口,啟動器照舊給三個變數([S1003] 的模型入口那半不改),由驅動程式在沒列清單的情境把使用者環境裡的三個變數拿掉再交給啟動器,所以它們也只重播錄製(
- `Projects/RTB_Phase13AI參與決策_計劃.md:947` 名稱 `--ai-judge`、`MODEL_LINE`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py、src/rtb/demo/driver.py)
  > - 實作者解讀(2026-09-25,使用者第二輪裁定修正頁面呈現):分析端在就緒那一行之後多印一行 `MODEL {"mode":…,"notices":[…]}`(`runner.MODEL_LINE`,只在帶 --ai-judge 時),啟動器把就緒之後的輸出留著,驅動程式讀這一行記進情境細節供內部記錄;頂端摘要與詳情頁均不顯示模型模式、原因或即時清單,見 Phase 12 [S1028]。
- `Projects/RTB_Phase13AI參與決策_計劃.md:951` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - 實作者解讀(2026-09-25,使用者第二輪裁定修正頁面前綴):F5 雙胞胎的廣告編號是 c3,數字與名稱(預設的空名稱)跟 F1 受測廣告相同,只種在模擬平台、不列進租戶設定;分析端帶 `--hold-submit c3`。考題比的是兩件工作調查紀錄的選項代碼序列(含結論);任一方有退回就寫「退回,無法比較」;底層錄製前綴仍留紀錄,頁面一律標「AI 的回答」。沒開 AI 時(驅動程式目前一律開)不建雙胞胎。
- `Projects/RTB_Phase13AI參與決策_計劃.md:973` 名稱 `ai_fallback_problems`(消失於 b2fc5122,原在 src/rtb/demo/recordings.py)
  > - 實作者解讀(2026-09-25,增量 4 代碼審 r2 m1):「F1–F6 任一輪 AI 退回」的判法搬進 `rtb.demo.recordings.ai_fallback_problems`(讀重播的展示狀態庫、跟頁面同一份判斷列),`check_demo_batch` 把它算進問題;錄完的自動檢查、入庫前命令列與 CI 守衛都呼叫同一支,錄到退回就判不過、要重錄。
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:110` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - **失效（2026-09-26 代使用者裁定）**：原 AI `propose`、退回後開規則輪、規則否決、`--hold-submit`、F5 雙胞胎考題及展示「AI 自選／程式補查」三段，只作增量 2b 歷史脈絡。理由是 AI 不再決定是否提案；評估執行器只直接呼叫 `ai_judge.Judge` 與 `rule_verdict(case)`，沒有 `TaskStore`、`flow.advance` 或 A/B/C 規則輪入口。評估保留 Judge、調查提示、收據
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:116` 名稱 `_verdict`(消失於 b2b17ea8,原在 src/rtb/eval/investigation_eval.py)
  > - Phase 13 原 72 筆中 46 筆調整列缺 `committed_at`；生成器以固定評估 `NOW − timedelta(days=days_ago)` 決定性補出帶時區時刻，再重新 `render(generate())` 產生 `investigation_set.py`，不得讓評估繞過正式白名單。重生前後逐筆斷言 72 筆的格與答案不變，`SYSTEM_PROMPT` 位元組與錄製鍵不變；收據 `adj*_...` 不含時間戳，因此斷言字串及其雜湊不變。
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:164` 名稱 `test_a_model_chosen_proposal_equals_the_formula_proposal`(消失於 b2fc5122,原在 tests/analyzer/test_ai_judge.py)
  > - 證據參照：規則輪提案列 C 的基本三筆加四種成功查詢收據（[S1107] 改寫）。（原寫「AI 直接提案仍只列基本三筆」已失效：代碼審 r1 起 AI 答 propose 也開規則輪、由規則輪建提案，見下方 r1 修正）[test:test_underpacing_campaign_reads_three_steps_and_proposes_with_query_receipts]、[test:test_a_model_chosen_proposal_equals_th
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:168` 名稱 `--hold-submit`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - AI 退回（與增量 3 的分界）：原本 AI 退回走 `_rule`（舊「有投放就加」），九條需要四查詢，所以 2b 照計劃〈AI 退回與展示〉先做**退回那一半**：退回時基本三筆判得出的（暫停、異常、前置過濾那幾道）當場結案，其餘開一次新規則輪 A/B/C 全量重讀（退回紀錄結果代碼 `rule_round`），規則輪那幾步由流程層直接問規則輪、不經 AI；AI 用過之後的蒐證改讀規則輪（撤除 [S1138]「只讀基本兩樣」）；開 AI 時規則輪定案也照 --hold
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:171` 名稱 `test_committed_demo_recordings_have_no_ai_fallback_in_f1_to_f6`(消失於 b2fc5122,原在 tests/demo/test_ai_demo.py)
  > - 未解決（停在這裡）：政策版本升版後，入庫展示錄製（phase13-demo-20260925）裡模型說明（提案說明命令列）的提示含政策版本，重播 F1–F6 有 8 筆說明呼叫找不到錄製，`test_committed_demo_recordings_have_no_ai_fallback_in_f1_to_f6` 紅；代理不准錄，需協調者用真 claude 重錄展示批次（或裁定其他處置）。AI 調查的提示與錄製鍵不含政策版本，Phase 13 評估 72 筆重播不受影響
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:175` 名稱 `test_a_model_chosen_proposal_equals_the_formula_proposal`(消失於 b2fc5122,原在 tests/analyzer/test_ai_judge.py)
  > - 外家否決-1(blocker)+資安-1:把原屬增量 3 的兩件提前做。AI 前置過濾納入第 1/2 條(暫停、異常、判斷點輸入建不成)直接由規則結案、不呼叫模型;AI 答 `propose` 不再直接建提案,記下 AI 原始結論後開一次新規則輪 A/B/C,九條也判值得加才由規則輪建提案,否則否決(定案事件細因帶 `ai_propose_vetoed:`,[S1407] 否決那半)。所以不會再有未經九條卻帶 `nine-rules-v1` 的提案。評估的原始錄製重播(`
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:251` 名稱 `ai_decide`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py)
  > - **刪（runner／流程層）**：`runner.py` 的 `--ai-judge`、`--hold-submit` 及「只在 --ai-judge 時可用」防呆、`_unsafe_ai`／`_unsafe_hold`、`_Ai`、`_judge_for`、`_open_ai_gate`、`MODEL_LINE`／登入預檢模式行、`GateOpener`、`ai_judge`／`modelgate` 匯入與模型參數；`_advance_one` 固定用 `instru
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:253` 名稱 `--ai-judge`、`--hold-submit`、`MODEL_LINE`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py、src/rtb/demo/driver.py)
  > - **改（展示開關）**：`driver.World.ai`／`AiSetup` 拆成「分析端 AI 判斷」（刪）與「說明／假說模型入口的錄製或即時設定」（留）；`Driver.ai_setup`、`_entry_args`、`run_model_entries`、`_narrate`、`_hypothesize` 由後者控制，提案照常跑說明、告警照常跑假說。分析端組參數永不加 `--ai-judge`、`--hold-submit`、模型花費帳與模式行等待；模型模式／原因
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:256` 名稱 `ai_decide`(消失於 b2fc5122,原在 src/rtb/analyzer/flow.py)
  > - **留評估（AI 決策模組）**：`ai_judge.py` 只保留 `investigation_eval.run_case` 實際用到的 `Judge`、調查提示／收據、解析與評估開閘道；`rule_verdict(case)` 直接產生案例九條結果。評估目前從 `flow` 匯入 `AiContext`、`NoAction`、`ProposalDecision`、`QueryMore`、`RuleContinue`，Judge 也使用這些結果型別；刪 flow 的 
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:261` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > Phase 13 逐條翻案索引（2026-09-26 代使用者裁定；下列 42 條在舊條款旁逐條回指；舊 `[test:]` 為歷史綁定，落地時按右欄刪除、拆分或改綁。判準：`rg -n -- '--ai-judge|a_ai_query|a_ai' src tests` 與 Phase 13 條款／測試名對照；理由是正式／展示不再由 AI 決定加額，評估只走 Judge 與案例九條）：
- `Projects/RTB_Phase14正式規則照九條判斷_計劃.md:358` 名稱 `--ai-judge`、`AiWorld`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py、tests/analyzer/test_investigation_e2e.py)
  > - 原 `[S1407]` **撤除（2026-09-26 代使用者裁定）**：2b 的 AI 提案經新規則輪否決，在 runner 仍能呼叫 AI 時防止未經九條的提案；runner 拔掉 AI 入口後，`investigation_eval.run_case` 又只直接用 `Judge` 與 `rule_verdict(case)`，沒有可承接 `flow.advance` 或 A/B/C 輪的評估入口。刪 `test_ai_proposals_and_fallbacks
- `Projects/RTB_Phase15AI找規則模式_計劃.md:26` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - Phase 13 讓 AI 參與「要不要加預算」，Phase 10／13 的評估顯示這種程式可算的判斷由程式較好。Phase 14 已由使用者於 2026-09-26 裁定 AI 退出加額決策，只保留提案說明、告警原因推測與本計劃的找新規則模式。Phase 14 增量 3 將移除分析端 runner 的 AI 判斷開關；AI 決策模組只留給評估重播，正式流程此後沒有 AI 通往提案的入口。Phase 14 現存計劃仍把 `--ai-judge` 留在正式入口，故不能只憑「
- `Projects/RTB_Phase15AI找規則模式_計劃.md:169` 名稱 `--ai-judge`(消失於 b2fc5122,原在 src/rtb/analyzer/runner.py)
  > - [S1518] 當 Phase 14 尚未把**移除 runner AI 判斷開關**的增量 3 合入 main，或實作前核對 runner 仍可用 AI 判斷開關送提案、展示驅動仍組 `--ai-judge`、F7 未能走規則路徑三者任一成立時，實作者應暫緩本案；合入且核對 runner 無開關、展示驅動不再組參數且 F7 重跑走規則路徑後，AI 決策模組只供評估重播，正式流程無 AI 通往提案入口，探勘閉包仍不可達提案／DSP，[S1103]、[S1134]、[S91
- `Projects/RTB_Phase2任務流程_計劃.md:218` 名稱 `InstrumentedEvidenceSource`(消失於 b2fc5122,原在 src/rtb/analyzer/instrumented.py)
  > - `src/rtb/analyzer/instrumented.py`:**新增**(第 1 輪發現:tool_calls 誰寫、寫在哪沒交代)。提供 `InstrumentedEvidenceSource`、`InstrumentedSubmit` 兩個包裝類別,建構時吃一個原始的 `dsp_client`/`inbox_client` 函式與一個 `TaskStore`;每次呼叫內層函式,不論成功或丟例外都呼叫 `store.record_tool_call(...)`
- `Systems/模型用戶端.md:206` 名稱 `__setattr__`(消失於 0e36970a,原在 src/rtb/analyzer/policy.py)
  > - 共用錄製檔驗證(`src/rtb/modelrecording.py` 的 `validated`)也核對呼叫者。呼叫者靜態檢查補上 `**` 展開、`replace`、`__setattr__`、挑成員;
