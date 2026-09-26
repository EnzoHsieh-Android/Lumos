---
type: system
status: done
created: 2026-06-26
updated: 2026-09-26
self_audit: sonnet/2026-08-26
about_code_stamp: claude/2026-08-30/be0e9557e400
tags:
  - type/system
  - status/done
  - risk/守衛面
  - scope/loop-engineering
verified_by:
  - "[[Verification/2026-06-19_loop-convergence-recording]]"
  - "[[Verification/2026-07-16_dloop提效M2_cluster帳]]"
  - "[[Verification/2026-07-28_settle收斂閘]]"
  - "[[Verification/2026-07-28_S2S3壓縮與驗證器]]"
  - "[[Verification/2026-08-04_design-loop重設計落地T1-T7]]"
  - "[[Verification/2026-08-04_design-loop處置閘終審硬化]]"
  - "[[Verification/2026-08-05_流程優化六件落地]]"
  - "[[Verification/2026-08-14_殘餘估計降級與重疊報表落地]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-08-26_roster對帳併入問閘落地]]"
  - "[[Verification/2026-08-26_改制回測落地]]"
  - "[[Verification/2026-08-26_嚴重度綁定寫側硬擋落地]]"
  - "[[Verification/2026-08-27_decision_refs養成T3v4落地]]"
  - "[[Verification/2026-09-07_loop-list開著的迴圈]]"
  - "[[Verification/2026-09-09_審查有沒有用記帳落地]]"
summary: |-
  WHY:[2026-09-26 [[Projects/逃逸帳對得起來_計劃]] d1]逃逸帳對得起來:①新列帶 `loop_kind`(code/design/plan,只看 loop 欄與審查紀錄、規格閘留痕不算,`_escape_loop_kind`);②手動記帳要 --sha 或 --defect-ref,沒有就 --missing-defect-ref 講理由(至少 4 字實字);手動記帳與撤回都上寫入鎖、共用符號連結檢查 `_escape_log_guard`;③`loop escape --withdraw <token> --reason --withdrawn-by` 追加撤回紀錄(撤回者自報不驗身分;token 在 --list 每列印出;token 重複不准撤),`_escape_rows_for` 永遠不回撤回紀錄、預設不回被撤的列,自動記的去重用 include_withdrawn(撤過的不會被同觸發補回),清單照列並標已撤回,rule-gap 保留自己找檔再套同一支判斷;④`loop escape-stats`:列上已記的 loop_kind 為準、sha 與 defect_ref 各自比對歸因;單位是迴圈、分母只認 converged 且審查帳有紀錄、下一站接住(實作/code-loop/push-gate*)另列、歸因不明只在分母母體內比、code 類標明只含手動逃逸 [test:t_escape_withdraw_validation] [test:t_escape_withdrawn_not_resurrected_by_auto] [test:t_escape_stats_rate_unit_is_loop] [test:t_escape_manual_requires_defect_ref]
  WHY:[2026-09-26 [[Projects/審查跑滿上限提示_計劃]] d1]多席迴圈輪數到分級上限、或各輪累計折入超過 20 條時,loop next 與處置閘都在輸出末尾印 `[cap-hint]` 段:每輪折入數(`_review_yield_round` 的折欄;空輪看各席 findings 全 0)、最高嚴重度、閘狀態與一條提示(換做法/可以停/由人裁/判不了)。只印不擋、不寫帳、回放不印,處置閘那邊印的時候任何例外都吞掉(代碼審 r1:帳上某輪欄位壞掉曾讓處置閘噴例外);light、循序單審、2026-08-26 以前的舊迴圈不印。理由:處置閘一輪全部處置完就過關,多跑的輪是過了閘之後自己再開的,問題在「沒人看得到走勢」而不在出口。分輪抽成 `_disposal_round_groups` 與處置閘共用 [test:t_cap_hint_not_declining_reshape] [test:t_loop_next_cap_hint_appended_without_changing_phase] [test:t_disposal_cap_hint_without_changing_verdict] [test:t_cap_hint_breaker_total_folded]
  PITFALL:[2026-09-26 代碼審 code-逃逸帳對得起來 r3]帳本一行合法但巢狀極深的 JSON 解析時丟遞迴過深錯誤(不是 ValueError),逃逸帳家族讀帳、共用寫完讀回自驗 `_jsonl_append_verified`、判門 `_door_for_loop` 都改成一起接;寫完讀回沒接會在已寫入後誤報沒記成功。rule-gap 讀帳時就把規則名與說明過 `_esc_clean`(帳是誰都能記的;★要在讀帳時清、不能在輸出時清★——輸出時才清,--json 會漏清,而且清完撞名的兩條規則在 JSON 裡會只剩一條,讀帳時清則次數合併、兩種輸出同一份;讀帳時★只清不截斷★,截斷會讓前段相同的長名字誤合併;小審 r1–r3 通才席)。其餘讀帳點見 [[Issues/帳本讀取沒接遞迴過深]] [test:t_escape_review_r3_fixes]
  PITFALL:[2026-09-21]★留痕之後手打帳本提交的路徑清單,同一天漏掉簽名檔兩次★——每次 `anchor approve` 都會弄髒簽名檔,而推送前的閘會擋「簽名檔改過了但沒提交」(它擋的是本機綠、CI 會紅)。現在 `code-loop pass|skip` 收尾會把還沒提交的帳本檔列成一行可直接貼的提交指令。★只列帳本檔,不列卷證目錄★:一起列會變成上百個檔、混進別的 session 的卷證,照貼等於提交別人的東西。[test:t_codeloop_pass_lists_dirty_bookkeeping];解析 `git status --porcelain -z` 時改名會吐兩個片段(第二個是裸的舊路徑),拆成 `_porcelain_z_paths` 處理——走完整流程測不出這個(切壞的字串本來就不會命中白名單),所以直接餵合成輸出測解析。
  KEY:[2026-09-17 風險低放行].canary-log.jsonl 多一種 kind=spec-gate(規格閘留痕:door/tests/clause_sha/door_rule/exclusions),不是審查輪:_loop_records 與 loop status 讀帳時略過,不算席數、不使輪無效;寫側走同一支 _jsonl_append_verified+vault 寫入鎖;讀它的只有 [[Systems/規格閘]] 的推送前檢查、_door_for_loop(逃逸帳分門)與 doctor S14 [test:t_round_valid_ignores_spec_gate]
  KEY:[2026-09-09 審查有沒有用記帳]寫側第三道硬擋:席報告沒正規化(檔首檔級行、每條 finding 恰一行獨立 severity、殘留寫法)→ rc2 並在治理帳留 canary/blocked;`reported` 由機器數落帳、--findings 不得多於它;載體必帶 --refuted-set(intake 整字驗);問閘尾一行「席位報→存活/重現不到→折/放行」(觀測不進合取,舊帳印 ?)[test:t_canary_reported_normalized][test:t_canary_refuted_set][test:t_gov_stats_review_yield];單源 [[Projects/審查有沒有用記帳_計劃]]
  KEY:[2026-08-05]`loop canary-stats [<id>]`——d4 跨輪累積帳的★讀取面★(席位×caught/missed×尾端連續 missed;streak≥2 印「升 opus」提示=該升級規則的機械眼);唯讀恆 rc0、壞行跳過註記、不進任何 gate [test:t_loop_canary_stats]。★[2026-08-14 停用制適配]★協議停用(canary-audit d5)後升級訊號改看 quote-check,本報表轉歷史帳回放;對純 none 的停用制 loop 印停用提示而非「無記錄」(終審 F1:原樣會誤讀成什麼都沒發生),none 輪計數顯示但不入 caught/missed 統計 [test:t_loop_panel_none_kind]
  KEY:[2026-07-28]第四模式 settle(opt-in,`--settle 清單檔`)落地——收斂=清單全結清∧G1∧G3(末筆 result=現檔;K-streak/G2 由逐條存在證明取代,G2 印 advisory);caught 輪收緊=kind∈{caught,none}∧auditor 非空(★(2026-08-21 程式碼實證)實作 `is_caught_round` 收 none;程式碼內舊 docstring 4218 行仍寫 caught-only,屬程式碼註解漂移★);貶值=gate 讀時判不回寫;fail-closed 族(壞行 rc2 全檔/零條目/懸空輪);與 panel/light/need/min-seats 互斥 rc2;設計=[[Projects/結清式收斂_計劃]](五輪 design-loop+實質收斂人裁) [test:t_settle_gate];同計劃 [S2] loop compress(規則式白名單壓縮,[PIN] 口頭約定壓不掉)+[S3] loop verify-progress(結構帳覆核原語,note/clusters 散文免疫) 2026-07-28 落地 [test:t_loop_compress,t_loop_verify_progress]
  KEY:[2026-08-04]第五模式 disposal(opt-in,`--disposal`;design-loop 專用,見[[Projects/design-loop重設計]])——與 panel/light/settle/need/min-seats 互斥;四條合取(★2026-09-08 加⑤條款綁定、2026-09-11 加⑥資安席,現為六步——見 Projects/代碼審資安席_計劃★)★全讀側可重算★:G3∧處置集合重算(findings_set/folded/accepted 互斥+聯集+blocker 不得 accepted,輪級不信寫側)∧留痕 sha 重驗(record 完刪改照樣擋)∧quote-check 引句全錨定(對凍結快照防循環自證);★canary caught/missed 不進合取(d4 觀測)★;寫側 record 六選配欄+定錨後留痕強制 [test:t_loop_status_disposal_gate,t_canary_record_disposal_fields_optional];★終審硬化(2026-08-04 code-loop 三輪 panel 對抗審)★——壞行 rc2 fail-closed(訊息附行號;全帳域,同 settle 前例)/round 與 round-less 混用 rc2/round-id 禁 __ 保留字首(撞內部 __seqN 鍵=舊 carrier 冒充判定輪)/round-less 逐筆自成一輪/留痕重驗涵蓋判定輪★全席★(缺欄=FAIL 不跳過)/引句 norm 後 10 字下限+不成對引號(「…』)以格式 miss 入列/留痕路徑以 repo root(_vault_repo_root 向上找 .git,寫讀同根,--repo 顯式覆蓋)相對落帳 [test:t_disposal_gate_r1_panel_hardening,t_disposal_gate_r2_panel_hardening,t_disposal_gate_r3_panel_hardening];★Landmark 真場實測三缺口修(2026-08-04,首次他專案落地即抓到)★——引句標籤容錯(**引句**：/**引句（註記）**：,原只認裸標籤→合規報告抽零條)/CJK 折行空格 fallback(快照句中折行→norm 多一空格,連續引句必 miss;空白全剝再比一次)/blockquote 續行 > 記號剝除(norm 內);首戰績=RSNO r3:4/5 席全錨定、1 條轉寫誤差正確被拒、DISPOSAL GATE PASS [test:t_quote_check_field_test_gaps]
  KEY:[M2 2026-07-16]risk-cluster 三態帳(見[[Projects/design-loop提效_計劃]])——canary record --clusters '名=狀態'(resolved/accepted-minor:理由/disputed-major)→panel gate 首個有效輪定錨後改兩條合取(輪有效∧fold 後無 disputed-major);_round_valid_m2 統一謂詞(caught≥2∧missed=0∧kind 白名單)五處共用;無效輪豁免+警告區列帳;新生 cluster/capture-recapture 降 advisory;★2026-08-14 起無-cluster 帳的 capture 亦降 advisory(合取剩輪有效∧存活,見[[Projects/收斂閘殘餘估計降級_計劃]];原「三條合取不變」作廢)★ [test:t_m2_cluster_gate]
  FLOW:每輪對抗審計 → canary record caught|missed|none --loop <id>(★none=2026-08-14 停用制純處置帳載體(2026-08-21 程式碼實證)★) --severity <max finding> 寫進 .canary-log.jsonl(+loop/+severity 兩選用鍵)→ loop status <id> [--need K] 讀 append 序、篩 loop==id、tail-K(K 預設2,< 1 夾到 max(1,K))滑動窗算收斂 → exit 0/1/2 供編排 skill 讀
  KEY:把 loop 終止判準從「人含糊說看起來收斂了」換成「連 K(預設2)輪 caught 且 severity∈{clean,minor} 這個可重算條件」;留痕=那串 round 記錄本身
  KEY:CONVERGED ⟺ tail-K 滑動窗(append 序最後 K 筆)全為 caught+clean/minor;前面髒輪不影響、只看最後 K 筆[test:t_loop_status]
  KEY:missed 輪 ×tail-K 自然重置——一個 missed 落在窗內就擋收斂,直到隨新輪滑出;無需特例(dogfood R6 逼出)
  KEY:缺 severity 視同未收斂(逼明確宣告、不得當 clean);exit 0=CONVERGED｜1=未收斂(含無記錄=還沒開始)｜2=真錯誤(argparse/IO)
  KEY:★(2026-08-26 嚴重度綁定案落地,舊「severity 自報無寫入端驗證」天花板已拆一半)★寫側硬擋:審查席帳列(loop+auditor;結局帳 --outcome 豁免——★cb3 折入:原 loop+round+auditor 三者齊備觸發=漏打 round 即繞道,已放寬;處置帳另必綁輪次+讀側 round-less 處置帳拒判★)必附 --report,報告要有獨立「severity: <值>」行(逐行 fullmatch,引句/blockquote/跨行天生排除),帳面低於報告最高=拒帳 rc2、高報=放行+提醒;record 並落 spec_path 欄。殘餘天花板(誠實):報告與帳同出編排者之手,擋疏忽不擋共謀,對抗歸 [audit:];severity-check 第四道收貨+問閘尾巴(觀測不進合取,留痕併 roster-alerts.log)當縱深第二層
  KEY:★判定回放(2026-08-26 改制回測案)★:`loop replay --freeze/--golden`——收斂即凍完整輸入閉包(全列帳原文+逐行 sha 集+spec 窗末 sha+卷證 HEAD blob+engine_rev)入 governance/replay/;回放唯讀(治理帳零寫入、無觀測尾巴),差異四分類:邏輯漂移/帳被動/凍結檔被動=紅,帳本長大/golden 過期(engine_rev 分流)=列出不紅;重凍比照 anchor approve 留痕+歸檔不覆寫;週跑 run_replay 補漏+輪替抽查(便宜自動升全跑);CONVERGED 仍非防竄改正確性證明,但「同輸入同判定」自此可每週機械重問
  KEY:[2026-09-17]逃逸帳多了自動模式:lumos loop escape --auto --range a..b(碰到的計劃各記一筆、對不回不記、去重鍵=迴圈/階段/sha);三個來源自動掛——代碼審 code-<主題> 記到 major 以上、推送閘擋下(fail-open)、CI 紅(範圍=上一個綠..這次紅)。歸因守衛在自動模式放寬成「迴圈在審查帳或計劃檔存在」,帳上 attribution 標 ledger|plan-file;door 欄由規格閘留痕填、上線前一律 unknown。單源:[[Projects/規格落成可驗收條件_計劃]] 第五節
  KEY:[2026-09-17]逃逸自動記(三來源掛勾、--auto、precision 欄、CI 步驟名判準)的單源改成 [[Projects/逃逸自動記_計劃]](從規格落成可驗收條件_計劃拆出);上一行提到的「第五節」已搬走
  DEP:scripts/lumos cmd_canary(+loop/+severity)｜cmd_loop_status｜cmd_gov canary mapper(detail 附 loop/sev 放最前)｜.canary-log.jsonl(複用,不新增 log)
  TEST:t_loop_status + t_canary_loop_fields;258 passed
  VERIFY:[[Verification/2026-06-19_loop-convergence-recording]]
decisions:
  - content: 收斂用 tail-K 滑動窗(append 序最後 K 筆全 caught+clean/minor),非「每輪都得乾淨」;排序用檔案 append 序而非 ts
    id: d1
    context: 設計 loop r2 真 major(R2-MAJOR-1):「最後 K 輪」原文義含糊,可讀成全程乾淨;且 ts 只到秒、同秒兩輪會並列無法定序
    why_chosen: tail-K 讓前面髒輪(早期被審計揪出的 blocker)不永久汙染收斂,符合「修了就該往前」;append 序唯一且即時間序,免 ts 秒級碰撞
    decided: 2026-06-19
    valid: true
  - content: 機制定位誠實校正為「可觀測性+摩擦+一個地板」而非「機械自我終止 oracle」;severity 是忠實轉錄審計員 max finding、無寫入端驗證
    id: d2
    context: r1 深層 blocker(R1-BLOCKER-2):原宣稱「機械自我終止」過度;severity 自報、想早收工的編排者可記假 clean——這跟 canary「植入者忠實判定」是同一個沒閉合的迴歸
    why_chosen: 對「無人看顧的自動 loop」夠用(終止從不可查的人判→可查的條件);對「刻意作弊」本就不設防、不該假裝防竄改;誠實標清天花板免下游過度信任
    decided: 2026-06-19
    valid: true
  - content: missed 輪靠 tail-K 機制自然重置乾淨連續數(missed 必 kind!=caught 故落窗內即擋收斂),無需特例
    id: d3
    context: 第六輪 dogfood 實況逼出(R6):一次漏抓 canary 該讓乾淨連續數歸零,否則放水輪被忽略
    why_chosen: tail-K 已天然涵蓋——missed 在窗內就不收斂、隨新輪滑出才放行;加特例反增複雜度
    decided: 2026-06-19
    valid: true
  - content: loop next 要印「帳上最後記到的審查材料(第 rN 輪):<路徑>」,取★最後一筆有 spec_path 的★而不是最後一筆(那個欄位是選配,r1 記了 r2 沒記時取最後一筆會印成「沒記」,語意完全不同);完全沒記要明講不准靜默省略(不然接手的人分不出是帳上沒記還是工具沒印);檔案已不存在要標出來;「少了 --spec」那句提示直接把可貼上的完整指令補完。措辭必須帶輪次——loop next 說「接下來第 N 輪」而帳上那筆是第 N-1 輪的材料,不帶輪次會被誤讀成下一輪要審的東西。
    id: d4
    context: 一個只拿到編號的新 session 跑 loop next,拿到的東西已經夠它直接派工(狀態/分級/第幾輪/幾個人/席位家族全有),唯一斷掉的一步是「在審什麼」——而那個資訊本來就在帳上,只是沒印,接手的人要自己去 tail 帳本。另一個 session 做「新 session 只拿編號能不能接手」的實測時發現的。
    why_chosen: 取最後一筆有值的:實測本庫 209 個迴圈有 0 個落在兩種取法的差異上,所以今天結果一致——但欄位是選配的,一致是現況不是保證,安全取法不花錢。跨輪換過路徑的 10 個迴圈全是每輪各自的快照,取最後一筆是對的(舊輪的路徑對下一輪是過期資訊)。
    decided: 2026-09-07
    valid: true
related:
  - "[[Issues/loop-next吐不可宣告的tier]]"
about_code:
  - scripts/lumos
aliases:
  - canary record
  - loop status --need
  - K-streak 收斂
  - caught missed 記帳
---
# loop-convergence-recording

收斂留痕(Convergence Recording)—— lumos 治理朝 **loop engineering** 方向的 **Component A**(機械層):把對抗審計 loop 的終止判準從「人在判」變成「lumos 從紀錄機械算出、可查詢」。

源起:lumos 治理大方向 memory `lumos-governance-direction-loop-engineering`(朝自主/無人看顧的自我檢查 loop)。非由單日日報 gap 直接觸發——2026-06-19 日報的 gaps/loop_lens 聚焦記憶完整性(STALE/記憶污染/HEARTBEAT),與本功能相鄰但不同路;本設計稿明載其角色來自 loop-engineering 方向。reportProvenance 見回報。

## 定位
- 審計 loop 的終止(「審穩了沒」)原本人在判,無法自我終止、不留痕、無法事後查。
- 收斂留痕 = 每輪審計記下(canary caught/missed + severity)+ 由 lumos 從紀錄算收斂。
- **只做 Component A**(lumos 機械原語)。Component B(編排 skill,讓每個計畫自動進 loop、問 `lumos loop status` 決定停不停)另立子專案,消費 A。

## 資料模型(複用,不新增 log)
複用既有 `.canary-log.jsonl`。`lumos canary record` 的選用鍵（2026-07-21 M1包 起共七類：`loop`/`severity`/`findings`/`round`/`capture_counts`/`clusters`＋M1包 新增 `reviewed_sha256`/`result_sha256`（`--spec`/`--reviewed` 成對）/`tokens`/`wallclock_min`/`tier`（定錨欄），見 [[Projects/loop機械脊椎M1包_計劃]]）＋2026-08-26 自主迴圈結局帳兩鍵：`outcome`（封閉列舉 13 值，主類 converged/unconverged/tier-blocked/skipped/pipeline_fail 帶細類；寫側白名單擋未宣告值）/`usd`（該輪實際美元），供 `run_ledger` 七天彙總回讀，見 [[Projects/自主迴圈修理_計劃]]。初版**兩個選用鍵**:
```
lumos canary record caught|missed|none --loop <id> --severity clean|minor|major|blocker [--auditor] [--token] [--note]
```
- `--loop <id>`:把這輪歸進某設計 loop(slug)。
- `--severity`:這輪審計員自己標的**最嚴重** finding(忠實轉錄其 max,非編排者獨立意見)。
- 寫入時 `if loop: rec["loop"]=loop` / `if severity: rec["severity"]=severity`(沒給就不寫鍵 → 舊 ad-hoc canary 行為不變)。

## 收斂計算(`lumos loop status <id> [--need K]`,K 預設 2,唯讀)
讀 `.canary-log.jsonl` 的 **append 序**(不 ts-sort)、篩 `rec.get("loop")==loop_id` 嚴格等值、tail-K 算收斂:
- **CONVERGED ⟺ tail-K 滑動窗(最後 K 筆)全為 `caught` 且 `severity∈{clean,minor}`**。canary 抓到=審計員醒著;無 blocker/major;**缺 severity 視同未收斂**。
- 否則「⏳ 還需 N 輪」,N = need − (從尾往回連續合格的輪數);最後一輪就髒 → N=need(髒輪不讓 N 虛低)。
- 記錄數 < K(含**無記錄=還沒開始審**)→ 未收斂 exit 1。
- `--need` 防呆:`need = max(1, need)`(< 1 夾到 1,不算參數錯)。
- 輸出:第一行 status,接著每輪一行 tab 分隔(`順位\tkind\tseverity\tts\tnote`)當留痕,讓 B skill 不必 screen-scrape。
- **exit code**(給 B 機器讀):`0`=CONVERGED、`1`=未收斂(含無記錄)、`2`=真錯誤(argparse 錯 / 檔讀不到)。「沒記錄」與「I/O 錯」分開 → B 能分辨「該起一輪」vs「基礎設施壞了」。

## missed × tail-K(無特例的自然重置)
`missed` 也算一輪、且 `kind!=caught` 必不合格 → 一個 missed 落在 tail-K 窗內就擋住收斂,直到它隨新輪滑出窗外。效果 = 一次漏抓 canary 自然重置乾淨連續數(dogfood 第六輪逼出)。

## gov 串接
`cmd_gov` 的第 4 源(canary mapper)`detail` 必附 loop/severity 且**放最前**(避 `[:50]` 截斷):
`f"loop={d['loop']} sev={d.get('severity','?')} · " if d.get("loop")` + auditor/note。舊記錄無 `loop` 鍵 → 前綴空、行為同現在。

## 已知限制(誠實天花板,兩層)
1. **完整性**:收斂只證明「連 K 輪醒著的審計員沒找到 blocker/major」,**不證明沒有更深問題**。完整性靠多輪+多視角的 loop 本身,不靠把門檻調嚴。
2. **整合性**:`severity` ★2026-08-26 起有寫側機械驗證(報告宣告行↔帳面,低報拒帳;見摘要 KEY)★——原「自報、無寫入端驗證」已拆一半;殘餘=報告與帳同出編排者之手,擋疏忽不擋共謀,CONVERGED 仍非防竄改正確性證明、**不是 tamper-proof**。
→ 定位:可觀測性+摩擦+一個地板,**不是 oracle**;對無人看顧 loop 夠用,對刻意作弊不設防(非目標)。

## 相關
- 設計稿:`docs/design/2026-06-19-convergence-recording.md`(canary-護審計 7 輪、用本設計自己的 K=2 判準收斂)。
- 實作落點:`scripts/lumos` `cmd_canary`(+loop/+severity threading)、`cmd_loop_status`、`cmd_gov` canary mapper、`loop` subparser。
- skill 串接:`skills/lumos-project-notes/SKILL.md` canary 協議節(記 round + `loop status` 看收斂)。
- 方向 memory:`lumos-governance-direction-loop-engineering`。

## 載體席的引句要全錨,而且記帳當下就驗(2026-09-06)

**背景**:多席同一輪時,只有一席帶處置清單,它等於宣告自己是全輪的帳本載體。規矩一直寫著「記帳前先跑引句檢查,挑每句都對得回審材的那席當載體」。

**踩到的事**:我三席的引句檢查全跑了,結果也印在眼前——一席全錨、兩席各有句子對不回去。然後我還是挑了對不回去的那席。**跑了檢查,但沒拿檢查結果去做決定。**

**為什麼這個錯特別貴**:帳本是只進不出的。閘在讀側照樣會抓到,但那時帳已經寫進去,撤不掉,**只能換迴圈編號把整輪所有席重記一次**。

**現在的做法**:把讀側那道檢查往前挪到寫帳之前。帶處置清單的那一筆如果有引句對不回快照,記帳當場擋下並指路。**代價從「整輪重記」降成「換一席再敲一次」。**

- **只驗載體席**。其他席的引句本來就允許對不回去——那只是不採信,不擋。
- **零引句的乾淨輪不受影響**(抽不到引句就不進這道檢查)。
- 訊息刻意寫成「這席不適合當載體」而不是「這席在造假」。對不回去最常見的原因是**引了既有程式碼**(用來說明「專案本來就有這個做法」),它不在只含改動的快照裡,這種引句不算編造。

**對測試的連帶影響(值得記,因為它是設計訊號)**:加了寫側擋之後,「載體引句對不回去的帳」用現行指令已經產不出來。而閘讀側那道檢查防的正是這種帳,所以驗它的測試改成**直接把帳寫成壞的**——理由是這種帳現在只可能來自舊版本、手改或竄改,這樣建假資料比繞過寫側更貼近真實威脅。工具是測試檔裡的 `_ledger_patch_last`。

## ★記帳是收工動作,不是中途動作★(2026-09-07,同一天踩三次)

`canary record` 會把 `--report` / `--intake` 這些卷證的 sha256 綁進帳。帳是只能加不能撤的,
**所以記完帳之後再去動那些檔案,整輪的留痕就作廢**,而且救不回來:

- 補記一輪 r2 沒有用——處置閘是**逐輪**看的,r1 壞了就永遠壞著(實測過)。
- 唯一的處置是**換編號重記**(這篇別處已經寫過),但那會在帳上留下作廢的編號。

2026-09-07 一天之內踩三次,三次都是同一個動作「想到什麼再補一句」:

1. `code-batch13` — 綁到的席報告其實是子代理的**完整逐字稿**(我把 `.output` 直接複製過去、
   沒看內容),換成真正的報告本體之後 sha 不符 → 換成 `code-batch13b`。
2. `code-batch13b` — 記完帳又往 intake 追加「帳本編號換過一次」那一段 → sha 不符。
3. `code-batch14` — 記完帳又往 intake 追加「閘過之後又改了一次」那一段 → sha 不符。

最後兩批分別換成 `code-batch13c` / `code-batch14b` 才過閘。帳上留著四個作廢編號,
那是這件事發生過的證據,不刪。

**收束**:按下 `canary record` 之前,intake 要**寫完**——包含「我後來又發現什麼」
「我判錯什麼」「留痕紀律哪裡沒做到」那幾段。這幾段恰恰是最容易事後才想到的,
而它們一補下去就把整輪作廢。想補的時候先問一句:這一輪記帳了沒?

**順帶一條**:存席報告之前**打開看一眼**。子代理的 `.output` 是 JSONL 逐字稿不是報告,
存錯了 `quote-check` 會出現一堆莫名其妙的錨不到(它從逐字稿裡撈到各種中間文字當引句),
而那個症狀很容易被誤判成「席位引錯了」。
