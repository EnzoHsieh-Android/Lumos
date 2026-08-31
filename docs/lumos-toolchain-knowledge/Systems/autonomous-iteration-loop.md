---
type: system
status: done
created: 2026-06-26
updated: 2026-08-30
self_audit: sonnet/2026-08-30
about_code_stamp: claude/2026-08-30/6964ab246141
tags:
  - type/system
  - status/done
  - risk/守衛面
verified_by:
  - "[[Verification/2026-06-20_autonomous-iteration-loop]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-08-21_工具鏈體檢修復批]]"
  - "[[Verification/2026-08-26_自主迴圈三症修理落地]]"
  - "[[Verification/2026-08-27_自主loop遷處置閘]]"
summary: |-
  FLOW:daily-governance.sh(launchd 09:30 單次喚醒,★原獨立 cron 10:10 已棄——自足審計 2026-08-30 抓到 FLOW 殘留舊述★)→ autonomous-loop.sh:驗當日日報存在(真模式無報即跳;dry-run fallback 最近一份)→ backlog 每日衰減(冪等按日差;淘汰先歸檔 backlog-archive.jsonl 讀回自驗才刪)→ gap_select(日報 gaps + backlog 去重排序選 top-1,三鍵排序=分數/last_seen/source_date 新者先;N=1 gate:有 pending/open PR 則只進 backlog)→ claude -p orchestrator(真執行:brainstorm spec → design-loop ≤6 輪[opus auditor + canary a/b/c + judge 判 caught 並回報 severity + 強制地面事實查證]→ loop status --disposal 收斂(★2026-08-27 遷處置閘 d7,舊 --need 2/--gate K-streak 退役★)→ §2.5 qwen3-max 跨家族複核)→ 收斂+endorsed/degraded → 放行閘(dry-run 寫 governance/pending/;真模式 branch+PR+LINE)→ 停等人放行
  KEY:[2026-08-31]daily-governance.sh 第 4 步=lumos doctor --ci(2026-08-30 intake 案加線;08-31 回訪案補 --ci——治理事件每日入帳,gov --nags 14 天空轉升級鏈才有電;裸 doctor 不寫帳=鏈斷路)
  KEY:★2026-08-26 修理(auto-loop-repair-v2)★:①失敗不丟件——trap EXIT 涵蓋全部早退點,未處置 gap 原分放回+pipeline_failures 滿 3 熔斷 covered+LINE(先前 NO_JSON/anchor 早退真丟件,08-24/25 兩筆實丟)②結局帳結構化——canary 帳新欄 outcome(五主類+細類)/usd,trap 統一落帳與成本抽取解耦③七天產出一行(run_ledger.py,失敗日照印,loop id 過濾=auto-日期形狀)④連兩個有跑日全管線死→LINE 素訊息(不套「備好待放行」模板)
  KEY:★事故(2026-08-21 體檢 #2)★ N=1 閘被 pending/ 兩個 07-14 舊檔卡死 **38 天**,每日 launchd 準時跑、rc=0、「無可展開 gap」——排程有跑/什麼都沒做/回報成功;處置=舊檔歸檔 pending/archive/+pending >3 天即發 LINE 喊人(見 [[Verification/2026-08-21_工具鏈體檢修復批]])
  KEY:定調=自動備料+自審+停在放行閘等人,不是無人迭代;放行(merge PR)永遠人手動,人從「每天發起鏈」變「每天 review 1 個 PR」
  KEY:N=1 同時只 1 個待放行 spec——上一個未清(pending 條目/open auto/spec- PR)前,新 gap 只進 backlog 不展開,PR 永不堆
  KEY:全自動判收斂仍是沒閉合的迴歸——judge/cross-family 只把自評推遠一層未消滅,末端人 review PR 是最後也唯一真兜底(誠實天花板)
  KEY:dry-run≠模擬——orchestrator 必須真執行所有工具(canary record/cross_audit),收尾前自查 scratch spec+canary-log 必須存在,否則本輪無效重做(06-23 真機抓到「全程腦內模擬」幻覺後硬化)
  KEY:claude -p 走 $0 OAuth token(CLAUDE_CODE_OAUTH_TOKEN,非 API key);避開 OAuth 被禁 model
  KEY:tier 收檔守衛(2026-07-24 L4 審計補漏——本節點原漏這道會否決自報收斂的機械閘):orchestrator 自報 converged=True+cross_verdict=endorsed 後,wrapper(autonomous-loop.sh L130-190)仍①驗 spec_path 存在②用自算 difficulty.assess_spec() 的 tier 重跑 loop status --disposal 機械重驗(★2026-08-27 遷,原 --gate★)③tier=high 要求 cross_verdict 必須乾淨 endorsed——任一不過→requeue 不放行+LINE;機制本體見 [[Systems/risk-tiered-review]]
  KEY:週期任務第四支 run_replay(2026-08-26 改制回測 S4):每週補漏凍結+新凍必跑+存量輪替抽 5(游標檔)+預算 300s+便宜(單包×存量≤60s,首測 0.24s/包)自動升全跑;紅(邏輯漂移/帳被動/凍結檔被動)與 golden 過期分開喊,build_message('regime-replay') 帶重查指令(★訊息在 python 端組單行——與 run_exam 家族 bash 組裝不同,刻意新慣例:通知文字進得了單元測試網;後續新週期任務照此;cb3 arch-f1★);模組炸掉不蓋週戳(明日重試);fail-open
  KEY:★抽掉人之前必辦清單(觸發條件=迴圈能不經人放行寫圖譜/開 PR 那天,今天人在放行點故全部不建)★——①提案者≠寫入者結構分離(Mnemosyne arXiv 2607.00269,2026-07-24 裁定:語意合約唯一真獨立寫入閘=真跑測試或人,LLM judge=換皮提案者)②PoE 型防竄改帳+逐筆授權+可重播(arXiv 2607.05397,2026-07-25 裁定:價值不靠敵人成立——無人 loop 自己的遙測可不可信;現成便宜前例 2.7ms;07-26 再添 PROJECTMEM arXiv 2606.12329:本機零依賴 append-only 指紋鏈+寫入前驗內容實證可行,「要裝東西太重」藉口拿掉)③日報吸收管線升格為不可信輸入面(調研員每天真讀外部網頁,今天靠人眼把關,無人化後=夾帶指令/假結論的真通道)。框架修正(使用者 2026-07-25):「內部系統無敵意下毒」對——敵意攻擊框架(IssueTrojanBench 66.5%)不適用單人私有 repo;但無人化後「幻覺 agent 寫錯圖譜+改自己成績單」效果同下毒,主角不需是敵人。同日拒:審計加對抗步(design-loop d4 前置加重一律拒,可審≠審得出=07-23 已記天花板換新引用)/spec 夾帶掃描(spec 作者=自己人,威脅不成立)
  KEY:紀律抗壓縮(Governance Decay arXiv 2606.22528,2026-07-26 對帳)=長跑對話的摘要壓縮會悄悄刪安全規矩(違規率 0→65-95%)——lumos 架構已結構性counter:規矩不住對話記憶(CLAUDE.md 每輪重注入/圖譜在硬碟/impact hook 每次動手前重推合約/orchestrator 每日 fresh spawn),「每輪從硬碟重讀紀律」該篇藥方=本設計既有形狀。殘餘面(誠實):對話中途的口頭約定(未落圖譜者)確實隨壓縮衰減——正是「退場必寫」存在的理由,重要裁定必須離開對話住進硬碟
  DEP:governance/daily-governance.sh(真入口:launchd com.enzo.lumos.daily-governance 09:30 單次喚醒,腳本內串接呼叫——原「兩支獨立 cron 09:30/10:10」因 Mac 閉蓋睡眠中途醒不來已棄,見該檔頭註)｜governance/autonomous-loop.sh(被 daily-governance.sh:26 以 --dry-run 6 呼叫)｜autonomous_loop/{gap_select,backlog,cross_audit,confidence_report,line_notify,orchestrator_result,run_ledger}.py + orchestrator-prompt.md｜scripts/lumos canary record / loop status｜gh CLI｜LINE curl broadcast
  TEST:scripts/test_autonomous_loop.py 全綠(2026-08-30 機械數=106;08-21 時為 53;★原記 27(2026-08-21 程式碼實證)★);dry-run 端到端真機跑通 06-20→06-26(入口現=daily-governance 09:30;測試數 2026-08-30 為 106 條)
  VERIFY:[[Verification/2026-06-20_autonomous-iteration-loop]]
decisions:
  - content: 定調為「自動備料 + 自審 + 停在放行閘等人」,而非「無人迭代」;放行(merge PR)永遠人手動,自動只到「備好待放行 spec」,絕不自動實作 / 自動 merge
    id: d1
    context: user 願景是「永遠在迭代的 lumos」;但全自動判收斂仍是沒閉合的迴歸(judge/cross-family 也是 AI、也會錯),且自動 brainstorm 沒人回澄清、AI 自選 gap 有自我強化偏誤
    why_chosen: 放大放行帶寬不等於消滅放行;末端人 review PR 是全鏈唯一外部錨點、最後真兜底,對齊「AI 全工人只驗證撐不起、人只在最高槓桿放行點」
    decided: 2026-06-20
    valid: true
  - content: dry-run≠模擬——orchestrator-prompt 加「執行紀律」塊強制真執行所有工具,收尾前自查 scratch spec + .canary-log.jsonl 必須存在,否則本輪無效重做;dry-run 與 --pr 唯一差別在收尾(寫 pending vs 開 PR),過程完全相同
    id: d2
    context: 06-23 真機發現 orchestrator 把 dry-run 誤解成「腦內模擬、什麼都不真做」——report converged/endorsed 但 scratch spec 空、無 canary-log,canary/judge/cross-family 全是它自說自話的幻覺,架空整個 loop(很可能從 06-20 上線起一直如此)
    why_chosen: 防放水的 canary、judge severity、跨家族補盲若被「模擬」架空,收斂報告全失真;唯有強制可驗證證據(真檔案產出)收尾自查才接得住此類幻覺
    decided: 2026-06-23
    valid: true
  - content: severity 改由獨立 judge 據實回報、不再 orchestrator 自填(judge-severity-gate);收斂門檻 = 連 2 輪 canary caught 且 severity ∈ {clean,minor}
    id: d3
    context: design-loop R3 揪出「severity 自報 = 收斂門檻自填」是全自動判收斂最弱環——被審者自填收斂了沒;此缺口本身就是 loop 上線後自己選中、自己 brainstorm 出 judge-severity-gate spec 來修的(自指)
    why_chosen: 把「收斂了沒」從被審者手裡移到獨立 judge,斷開自填閘;但這只把最弱環推進一層未消滅(judge 集中掌 caught+severity、只讀 auditor 文字不自 grep),仍須人工抽查
    decided: 2026-06-20
    valid: true
  - content: 放行前加 qwen3-max 跨家族複核(§2.5):收斂後開 PR 前,opus 取材餵 ground-truth、qwen 跨家族判;endorsed/degraded 放行、disputed(major+ 異議)退回 opus 續審,達 2 次升給人;API 不可用 → degrade 回 opus 放行(fail-open)
    id: d4
    context: backlog gap「judge 抗自偏漏了換家族解法」;真機側證 opus 單家族 canary missed 2/6 ≈ 33%,正是同門盲點;前提「換家族 $0 OAuth 做不到」被 qwen API 破
    why_chosen: 補 opus 同門盲點是收斂可信度最實在的一道補強;fail-open 確保 qwen 不可用時 loop 不卡死(降級回 opus 並標註)
    decided: 2026-06-22
    valid: true
  - content: 暫停每日自主 loop(launchctl disable com.enzo.lumos.daily-governance;plist 保留)
    id: d5
    context: 使用者指示暫停接下來的日報 loop
    why_chosen: 恢復指令:launchctl enable gui/$UID/com.enzo.lumos.daily-governance && launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.enzo.lumos.daily-governance.plist
    decided: 2026-07-07
    valid: false
    superseded_by: 2026-07-11 使用者裁示重啟(launchctl enable+bootstrap 已執行,每日 09:30);重啟時點的安全網比暫停時厚:panel near-perfect 閘/跨家族否決席/guard kill/落成核對均已上線
    ended: 2026-07-11
  - content: 重啟每日自主 loop(dry-run 模式維持:收斂備 pending 等人放行,絕不自動 merge)
    id: d6
    context: 使用者明示「重啟」;7/7 暫停期間補齊 canary 生成硬化/near-perfect/panel/guard kill/落成核對
    why_chosen: 人放行閘=最高槓桿不動;恢復後首輪吃到全部新紀律
    decided: 2026-07-11
    valid: true
  - content: 自主 loop 記帳+收斂閘遷處置閘、對齊手動 loop(Enzo 2026-08-27 裁):step-6 canary caught/missed → record none+處置帳(--findings-set/folded/accepted/accept-reason/--refute-verdict + --report/snapshot/spec/reviewed);step-8 與 runner(autonomous-loop.sh)的 --need/--gate → --disposal;辯方降級改走「放行清單+辯方反證+refute-verdict evidence」不壓低 --severity;canary 植入退為 auditor 醒著訊號、不再閘折入
    id: d7
    context: loop 2026-08-27 自報三卡點:①step-6 記帳指令照字面跑不動(2026-08-26 [S1] 起審查席帳列必附 --report)②step-6 記「辯方後 max」撞 [S1] 硬擋(帳不得低於報告宣告最高)→ r3 辯方降級進不了帳、只能記 blocker → --gate 永遠收斂不了(隱形燒錢)③網搜無人看顧被權限擋。根因=記帳+收斂閘整段停在 2026-08 前的舊協議(caught/missed+--gate/K-streak+severity 當收斂訊號),沒跟上手動 loop 2026-08-04/08-25 改的處置閘 d5
    why_chosen: 遷處置閘一次根治①②:severity 忠實記報告最高([S1] 滿意),辯方降級用處置帳(accepted-set+辯方反證+refute-verdict evidence)表達,收斂看『每個發現折或放行』不看 severity 高低——[S1] 與辯方降級不再對撞、辯方降級的輪能收斂。且處置閘單輪比 K-streak 省輪(降本)。對齊既有已測協議、非自建。相對選項:只補 --report 不解②(治標燒錢照舊)、或立待議不動(維持看不見的卡死)——都比遷移差。實跑一個 round 全序列(record+disposal gate PASS)驗過。③網搜是 harness 限制,prompt 標明用日報二手 fallback(loop 已自為)
    decided: 2026-08-27
    valid: true
  - content: orchestrator-prompt 三修(2026-08-30):①claude -p 活性紀律——派 Agent 後必須同一回合等到結果,散文收尾=本輪死亡(2026-08-30 實錄:編排者派 r1 審計員後交進度報告就 end_turn,$9.59/28 分鐘白燒,帳記 pipeline_fail;頂層 JSON=end_turn/completed/success,非錯誤而是互動模式習慣帶進 headless)②審計員派工補錨定引句紀律(每條 finding 附逐字引句 ≥10 字單獨一行)——處置閘「引句全錨定」關驗的就是它,沒有=收斂結構性過不了(2026-08-29 r6 實錄)③PRIOR-ART 第二問第一站改翻自家治理日報 JSON 的 articles 欄(headless 下 WebSearch 被權限擋實測兩次;要查的論文摘要就在日報裡沒人翻,r5 實證)
    id: d8
    context: d7 遷處置閘後首輪真跑(2026-08-30 10:16)以新死法陣亡:NO_JSON/pipeline_fail。診斷=d7 修好記帳對撞(昨輪三卡點之一已消)但沒遷完整:閘換了、沒教它產閘要的材料(引句),也沒補 headless 特有的活性紀律。七天帳 8 跑/$207.70/收斂 0
    why_chosen: 三個死因全出自迴圈自己的遺言與頂層紀錄(非猜測):活性=死因實錄逐欄可查;引句=r6 notes 逐字點名;日報=r5 自己發現的。修法全在 prompt 紀律層,不動閘不動 code;明晨排程即免費驗收。G3 時序經查 d7 已修對(昨輪跑的是舊 prompt),不重複動
    decided: 2026-08-30
    valid: true
about_code:
  - governance/autonomous-loop.sh
  - governance/autonomous_loop/cross_audit.py
  - governance/autonomous_loop/gap_select.py
  - governance/daily-governance.sh
---
# autonomous-iteration-loop

每天日報產出後,**自動備好一份已自審的 lumos 改進 spec、停在放行閘等人**的閉環。

## 定位(一句話)
日報(9:30)→ 抽當日最高價值 gap → 自動 brainstorm 成 spec → 跑 design-loop 審到收斂 → 跨家族複核 → 把「收斂 spec + 可信度報告」備好(dry-run 寫本地 / 真模式開 PR + LINE),**停,等人放行**。人從「每天發起這條鏈」變成「每天 review 一個 PR」。

> **這是放大放行帶寬,不是無人迭代。** 自動化「發起 + 篩選 + 自審備料」;把「判斷收斂可不可信 + 放行」留人。放行 = 人手動 merge PR,系統絕不自動 merge / 自動實作。

> **源起:日報 2026-06-18 gap**——「整套把關預設『每次 commit 都有人在旁邊看 stderr』,但無人看顧的自主迴圈已成主流,這個前提正在崩。」對齊治理大方向 loop engineering(朝自主 / 無人看顧的自我檢查 loop)。

## 架構(5 組件 + cron 入口)
- `governance/autonomous-loop.sh` — **由 `daily-governance.sh` 串接呼叫**(launchd 09:30 單次喚醒同腳本內接續;舊「獨立 cron 10:10」已棄——閉蓋睡眠醒不來,2026-07-24 L4 審計修真)。驗當日 `governance/reports/governance-<date>.json` 存在(真模式無報即跳、不視為錯;dry-run fallback 最近一份)→ gap_select → 派 orchestrator → 解析回傳 → 收斂則放行閘。主流程包 `while`(skip → continue 選下一個,`SKIP_CAP=3` 防空燒)。
- `autonomous_loop/gap_select.py` — 讀日報 `gaps[]`(真 schema `{weakness, suggestion}`)+ `backlog.jsonl`,去重排序選 top-1;**N=1 gate**(`pending_exists`:dry-run 查 `governance/pending/*.md`、真模式 `gh pr list head:auto/spec-`);`covered.jsonl` 永久排除已被既有 spec 覆蓋的 gap。
- `autonomous_loop/backlog.py` — backlog 讀寫 / value_score 衰減 / 淘汰 / 排序。(★covered.jsonl 的讀寫**不在此檔**,全在 `gap_select.py`(2026-08-21 程式碼實證)★)
- `autonomous_loop/cross_audit.py` — qwen3-max(DashScope 國際 endpoint)跨家族複核;回 `{status, worst_severity, ...}`,`status==degraded` 為 fail-open(no_key / http / timeout)。
- `autonomous_loop/orchestrator-prompt.md` — `claude -p` orchestrator 的 prompt 模板(brainstorm + design-loop + §2.5 跨家族 + 輸出單一 JSON)。
- `autonomous_loop/run_ledger.py` — 結局帳讀側(七天彙總+連續失敗日判定;逐筆遍歷不以 loop id 當鍵,舊格式列歸桶明示)。
- `confidence_report.py` / `line_notify.py`(含 `build_alert` 素警示,不套好消息模板)/ `orchestrator_result.py`(含 `classify_death` 死因分類、`cost_cli_args` 含 --usd) — 可信度報告 body、LINE 傳輸層復用 + 待放行訊息 body、從 orchestrator result 文字提取最後一個合法 JSON(容錯敘述夾雜 `{clean,minor}` 干擾)。

## 收斂與放行門檻
- **CONVERGED**(★2026-08-27 遷處置閘,見 d7★)= `lumos loop status <topic> --disposal --spec <spec> --repo <REPO>` exit 0 = **這一輪每個發現都折入或附理由放行**(G3 雜湊鏈 ∧ 處置全清 ∧ 留痕 sha 可重算 ∧ 引句全錨定;單輪,不再 K-streak)。**收斂看處置、不看 severity 高低**:辯方降級記在放行清單(accepted-set+辯方反證+refute-verdict evidence),severity 忠實記報告宣告最高——這樣才不撞 [S1] 寫側硬擋(帳不得低於報告),而舊制記「辯方後 max」會被 [S1] 逼記高、讓辯方降級的輪永遠收斂不了。舊制(`--need 2 --gate`=連 2 輪 caught+severity∈{clean,minor})2026-08-27 退役。失控保護:max cap = 6 輪、N=1、撞 cap → 停 + LINE 告警(★2026-08-21 程式碼實證:**單次**撞 cap 即發 LINE 並 exit 0,無「連續」計次邏輯★)。
- 收斂後走 **§2.5 跨家族複核**:`endorsed`/`degraded` → 放行;`disputed`(major+ 異議)→ 退回 opus 續審,`cross_reject_count` 達 2 → 停、不放行、`cross_verdict=disputed`(必伴 `converged:false`)。
- 放行閘:dry-run 寫 `governance/pending/<date>-<topic>.md`(+ confidence);真模式(`--pr`)commit 到 `auto/spec-<topic>-<date>` branch、`gh pr create`(★(2026-08-21 程式碼實證)--pr 分支**不發 LINE**,LINE 只在 dry-run 分支;autonomous-loop.sh:268-275★)。**⚠ --pr 模式 2026-07-29 起在入口直接拒跑**(autonomous-loop.sh 頭部硬擋,nested-agent-permission-scope 裁定;解禁條件=read-only child isolation+過 code-loop)——不是「可切換但未驗」而是「擋死」;branch+PR+LINE 路徑亦尚未真機驗證——Verification 節點的 pass 範圍僅涵蓋 dry-run;切換至 --pr 前須重驗放行閘全路徑(見 [[Verification/2026-06-20_autonomous-iteration-loop]] `revalidate_when`)。

## design-loop 對 skill 預設的覆寫(autonomous 版)
- **opus auditor 起手**(覆寫 skill「sonnet 起手、連 2 missed 才升 opus」)。
- **canary 限 type a/b/c、禁 type d**(覆寫 skill a/b/c/d 固定輪換;type d 對 self-contained 新功能不公平)。
- **獨立 judge**:判「canary 抓到沒」+ 據實回報排掉 canary 後最嚴重真 finding 的 severity(severity 不再 orchestrator 自填)。
- **強制地面事實查證**:auditor 對 spec 每個現況假設(欄位 / 簽名 / 檔案 / 常數)必須實際 grep/Read 驗過、列查證清單。

## 誠實天花板(必寫進 PR 可信度報告)
1. **末端人 review PR 是全鏈唯一外部錨點、最後真兜底**。全自動判收斂仍是沒閉合的迴歸:judge-severity-gate 把「收斂自填」推進一層未消滅(judge 集中掌 caught+severity、只讀文字不自 grep、規範非機制強制);cross-family 補同門盲點但 qwen 也是 AI。
2. 自動 brainstorm 沒人回澄清 → spec 品質天花板低於有人在場。
3. AI 判「哪個 gap 值得做」= AI 決定改自己的方向,有自我強化偏誤。

## 已知限制 / 真機教訓
- **orchestrator「模擬」幻覺**(06-23,已硬化):曾把 dry-run 誤解成腦內模擬、report converged 但 scratch 全空——已加執行紀律塊 + 收尾自查強制可驗證證據。屬「無人看顧下無聲寫壞狀態」的活例。
- **未收斂但有價值的 gap 處置**:撞 cap / cross disputed 的 gap 由 `requeue_unconverged` 降分(×0.7)+ 累計 `unconverged` 回 backlog,達上限 3 → covered(放棄自動、留人手動)。
- opus 單家族 canary missed ≈ 33%(06-22 真機)——跨家族複核的存在理由,但 canary 自評弱仍是已知。

## 相關
- 設計稿:`docs/design/2026-06-20-autonomous-iteration-loop.md`(canary-護 design-loop 5 輪、K=2 收斂;自指閉環)。
- 實作計畫:`docs/superpowers/plans/2026-06-20-autonomous-iteration-loop.md`。
- 下游產物(loop 自己選中、brainstorm 出來的):`docs/design/2026-06-20-judge-severity-gate.md`、`docs/design/2026-06-22-cross-family-audit.md`。
- 真機觀察日誌:`governance/autonomous_loop/DRYRUN-OBSERVE.md`、spike 結果 `SPIKE-RESULT.md`。

## 近期修正

- 2026-08-30 **prompt 三修(d8,d7 首輪真跑陣亡後的續修)**:①★claude -p 活性紀律★——派 Agent 必須同一回合等到結果,散文收尾=本輪死亡(實錄:d7 後首輪派了審計員就交進度報告 end_turn,$9.59 白燒;頂層 JSON=end_turn/completed/success——不是錯誤,是互動模式的「等通知」習慣帶進 headless)②審計員派工補錨定引句紀律——處置閘「引句全錨定」關沒有引句=收斂結構性過不了(r6 實錄)③PRIOR-ART 第一站=自家治理日報 articles 欄(headless 網搜被擋;論文摘要就在日報裡沒人翻)。G3 時序經查 d7 已修對不重複動。驗收=下一次每日排程真跑。

- 2026-08-27 **記帳+收斂閘遷處置閘(d7,對齊手動 loop)**:loop 自報三卡點——step-6 記帳指令照字面跑不動([S1] 起審查席帳列必附 --report)、記「辯方後 max」撞 [S1] 硬擋致辯方降級的輪永遠收斂不了(隱形燒錢)、網搜被權限擋。根因=記帳/收斂整段停在 2026-08 前舊協議(caught/missed + --gate/K-streak + severity 當收斂訊號)。修:`orchestrator-prompt.md` step-6 改 `record none`+處置帳(findings-set/folded/accepted/accept-reason/**--refute-verdict** + report/snapshot/spec/reviewed)、step-8 與 `autonomous-loop.sh` 的 --need/--gate → **--disposal**、step-4.5 辯方三選一且降級走放行清單不壓 severity、step-7 折入看存活不看 caught/missed、canary 植入退為 auditor 醒著訊號。**實跑一個 round 全序列(record + disposal gate PASS)驗過**;網搜是 harness 限制,prompt 標明用日報二手 fallback(loop 已自為)。★未移除 canary 逐輪植入(2026-08-14 協議停用的殘留)——本次只解耦其閘折入功能,全移除留追蹤★。詳 [[Verification/2026-08-27_自主loop遷處置閘]]。

- 2026-08-26 **三症修理(auto-loop-repair-v2,設計審 24 條全折後實作)**:①丟件根治——`pop_top` 消費後任何早退(anchor 失敗/PARSE_FAIL/NO_JSON)由 trap EXIT 原列原分放回、`pipeline_failures` 滿 3 轉 covered+LINE;log「下輪自然重抽」假話同步修正。②選題退化根治——`decay_and_prune` 寫了兩個月無人呼叫(153/160 筆凍 0.5 分=FIFO),接上每日冪等衰減(sidecar `decay-state.json` 記日差)+再現回血到初始+三鍵排序;淘汰先歸檔 governance/backlog-archive.jsonl(首次淘汰才建檔,至今 pruned=0 尚未存在) 讀回自驗才刪。③結局帳——canary 帳 `outcome`/`usd` 結構化欄,trap 統一落帳(先前 record 在收斂判定前執行+被成本抽取分支包住,PARSE_FAIL 連帳都沒有);autonomous.log 每輪印七天產出一行。順手修一個潛伏生產 bug:run_probe 的 grep|tail 無命中時 pipefail+set -e 殺整支腳本於選題之前(沙箱測試觸發抓到)。

- 2026-08-18 token 傳遞硬化(code-loop code-標註刷新 r1 另案收尾):六處 LINE 通知的 token(★原記七處,commit 9fcb761 實為六處(2026-08-21 程式碼實證)★) 由 shell 內插(`t='$(cat …)'`,token 含引號會炸 python 且被 || true 吞)改為 `LINE_TOKEN` 環境變數傳遞+`os.environ.get`,行為不變、注入面拆除。
