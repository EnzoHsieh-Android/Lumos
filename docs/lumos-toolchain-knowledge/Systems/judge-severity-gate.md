---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-20_judge-severity-gate]]"
summary: |-
  FLOW:design-loop每輪 sub-step3 派auditor→sub-step4 派獨立judge(明文傳入auditor完整報告+canary token)回 caught/missed + severity(clean/minor/major/blocker,排掉canary後最嚴重真finding)→sub-step4.5 辯方refute(對≥major每條派獨立opus拿file:line反證)→該輪severity=辯方存活findings的max→sub-step5 orchestrator讀此值(不再自評)→sub-step6 canary record --severity <該值>
  KEY:斷開「被審者自填收斂閘」迴路——good(r)=caught AND severity∈{clean,minor}(scripts/lumos:1368)的 severity 維度,從 orchestrator(被審者)自評改由獨立 judge 評定
  KEY:judge 據實評、不加保守偏置——純模糊(拿不準minor/major)時不往高評(否則模糊輪永遠major、進不了收斂窗);堵自填靠評定者獨立、不靠保守加碼
  KEY:唯一保守=客觀二值「沒查證→至少major」——對最嚴重真finding無任一grep/Read查證行才觸發;judge 只數有無、不評打不打中(評就把主觀模糊性請回來、卡收斂)
  KEY:只改 governance/autonomous_loop/orchestrator-prompt.md 的 judge prompt 與數據流;scripts/lumos canary record --severity 介面不動(scripts/lumos:3006);手動 lumos-design-loop skill 不受影響(skill 無 judge 概念)
  KEY:斷開是規範非機制——record --severity 仍由 orchestrator 轉錄 judge 值,無校驗鉤子;靠 dry-run 抽查 judge_rationale 與 record 值一致性偵測違規
  DEP:governance/autonomous_loop/orchestrator-prompt.md(judge prompt sub-step4/4.5/5/6)｜scripts/lumos cmd_loop_status good(r)｜canary record --severity
  TEST:功能改動在 prompt(非 Python),以 design-loop 自跑收斂為驗證(人解張力後重跑 R1 major→R2 major→R3 clean→R4 clean、4輪)
  VERIFY:[[Verification/2026-06-20_judge-severity-gate]]
decisions:
  - content: severity 維度評定者從 orchestrator(被審者)改為已在場的獨立 judge(擴充 judge 輸出含 severity,不新增 agent、不改 CLI)
    context: 觸發 gap(日報 2026-06-20):收斂判準 good(r)=caught AND severity∈{clean,minor}(scripts/lumos:1368)中 caught 已由 judge 判,但 severity 由 orchestrator 自評——被審者控制收斂閘的一半。否決方案B(改述「尚未被駁倒」,問題平移仍落 orchestrator)、方案C(第三個 severity-judge agent,重複 token、邊際信心微乎其微)
    why_chosen: judge 已 spawn 於每輪(判 canary caught/missed),增量僅「明文傳入 auditor 報告 + 多問 severity 一問」;評定者從利益相關方換成較獨立 agent,直接斷開自填迴路
    decided: 2026-06-20
    valid: true
  - content: 刪掉「純模糊性保守取高」,judge 據實評;唯一保留的保守是客觀二值「對最嚴重真 finding 無任一 grep/Read 查證行→至少 major」
    context: 核心張力(autonomous-loop 自動產 spec 撞 6 輪 cap 未收斂後人撈出):原 spec 給 judge 加「拿不準往高評(保守取高)」堵自填,但這讓模糊輪永遠 major、進不了收斂窗(堵自填 vs 可收斂對立)。「保守取高」本就是 R5-F-C2 審出的誤移植 skill strip-discipline 規則。R6-F-D1 曾誤判此為 minor 擱置
    why_chosen: 堵自填靠「評定者獨立」(orchestrator→judge)而非保守加碼;judge 據實評則模糊輪可據實 minor → 能收斂。對「模糊性」的保守(卡收斂)刪、對「auditor 沒做地面查證」的保守(對偷懶的合理懲罰)留;後者收成客觀二值(只數有無查證行、不讓 judge 評足不足)以防模糊性借「查證不足」之名回流
    decided: 2026-06-20
    valid: true
  - content: 二值保守是「用精確換客觀」、有故意留的洞——judge 只數「對最嚴重 finding 有無 ≥1 條查證行」、不評「這條查證打不打中」,故可被「敷衍貼一條無關 grep」規避
    context: design-loop 重跑 R2-F-R2-2 審出:一評「打不打中」就把主觀性、進而模糊性保守請回來、卡收斂——根本取捨無兩全(主觀判卡收斂 / 客觀數可敷衍)
    why_chosen: 本 spec 選客觀數、誠實揭露此洞(誠實天花板 8),靠 dry-run 抽查「查證行是否真打中最嚴重 finding」緩解,不假裝堵死
    decided: 2026-06-20
    valid: true
---
# judge-severity-gate

讓 autonomous design-loop 收斂條件 `good(r) = caught AND severity∈{clean,minor}`(`scripts/lumos:1368`)中的 **severity 維度**,從 orchestrator(被審者)自評改由已在場的獨立 **judge** 評定——斷開「被審者自填收斂閘」的迴路。

> 源起:日報 2026-06-20 gap「收斂門檻只覆蓋部分維度,定理證明優化者必在沒覆蓋處偷工」(借「有限評估均衡定理」)——明指 spec 自己已抓到『severity 自填卻決定收斂』,建議讓 judge 直接覆蓋 severity 這個決定收斂的維度。由 autonomous-iteration-loop 自動選此 gap → brainstorm → design-loop 產出。

## 解決什麼
`good(r)` 的兩個維度中,`caught`(canary 抓到沒)早已由獨立 judge 判,但 `severity`(排掉 canary 後最嚴重真 finding 的等級)由 orchestrator 自評——**被審者控制收斂閘的一半**。利益相關方自填 severity 即可把 major 評成 minor 騙過收斂窗。

## 關鍵機制(只改 prompt,不改 CLI)
唯一改動點是 `governance/autonomous_loop/orchestrator-prompt.md` 步驟 2 design-loop 的 sub-steps:
- **sub-step 4(judge,擴充輸入+輸出)**:judge prompt **明文傳入 auditor 完整報告 + canary token**(judge 不會自動取得 auditor 報告,這是前提),回傳 caught/missed **之外**額外回傳 severity(四級)+ 一句 rationale。
- **sub-step 4.5(辯方 refute,當前實作新增的對稱防假陽性)**:對 judge 評為 severity≥major 的每條 finding,派獨立 opus 辯方(乾淨脈絡、不傳 auditor/judge 結論)強制拿 `file:line` 反證才能降級;**該輪 severity = 辯方裁決後存活 findings 的最高**(機械取 max,非自評)。
- **sub-step 5**:orchestrator **讀 judge/辯方回報的 severity(不再自評)**;仍可讀 auditor 報告決定哪些 findings 折進 spec。
- **sub-step 6**:`canary record --severity <該值>`。

`scripts/lumos` 的 `--severity` 介面(`scripts/lumos:3006`)與 `good(r)`(`scripts/lumos:1368`)語義均**不動**;改的只是 severity 數值的**來源**。手動 `lumos-design-loop` skill 不受影響(skill 無 judge 概念,人在場自評)。

## 關鍵決策(核心張力的解)
原 spec 為堵自填給 judge 加「拿不準往高評」,但這讓模糊輪永遠 major、進不了收斂窗——**堵自填 vs 可收斂對立**。解法:
- **刪「純模糊性保守取高」**(它本是誤移植 skill 的 strip-discipline 規則):堵自填改靠「評定者獨立(orchestrator→judge)」、可收斂靠「judge 據實評」(模糊輪可據實為 minor)。
- **保留「auditor 沒做地面查證→至少 major」**:這是對偷懶的合理懲罰(強制地面查證下正常不觸發),非對模糊性的保守。收成**客觀二值**——對最嚴重真 finding 無任一 grep/Read 查證行才算「沒查證」;judge **只數有無、不評打不打中**(評就把主觀模糊性借「查證不足」之名請回來、卡收斂)。

## 已知限制(誠實天花板)
- **judge 仍是 AI 評定**:換掉「自評」但仍是「AI 評」,不保證正確;judge 讀的是 auditor 敘述、不自己 grep,auditor 輕描淡寫 blocker 時 judge 可能低估(severity 地面錨變弱)。
- **集中化風險**:`good(r)` 兩個維度(caught + severity)現同源於 judge,judge 放水則兩維一起失守,失去原「caught=judge、severity=orchestrator」的雙源交叉檢核。dry-run 需人工抽查同輪兩維對內是否獨立。
- **二值保守可被敷衍規避**:judge 只數「有無 ≥1 條查證行」,可被「敷衍貼一條無關 grep」繞過(用精確換客觀的故意取捨)。
- **斷開是規範非機制強制**:`record --severity` 仍由 orchestrator 轉錄 judge 值,judge 輸出與 record 入參間無校驗鉤子;與「自填」只差一個誠信假設,靠 dry-run 抽查偵測。

## 相關
- 設計稿:`docs/design/2026-06-20-judge-severity-gate.md`(autonomous-loop 自動產出,人解核心張力後重跑 design-loop R1 major→R2 major→R3 clean→R4 clean、4 輪收斂;含 6 輪原始 opus design-loop 史與雙源損益論證)。
- C4 同步點:`docs/design/2026-06-20-autonomous-iteration-loop.md` §3(severity 改由 judge 回報;prompt 為 source-of-truth,兩編輯點無一致性鎖)。
- 相關系統:[[Systems/design-loop]]、[[Systems/loop-convergence-recording]]。
- 落地 commit:`41c548f`(feat 落地)、`ee105a2`(C4 同步)。
