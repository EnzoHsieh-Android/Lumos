---
type: moc
status: doing
about_code_stamp: batch-2026-08-23/2026-08-23/70a11d6e2e82
---
# lumos-toolchain 知識圖譜總索引

Lumos 工具鏈(`scripts/lumos` + skills + governance 自動化)自身的知識圖譜。節點現況以 code 為準,完整設計史/收斂史指回 `docs/design/`。

**2026-09-08 起按「研究方向」九類排**(定義、邊界規則、回填數字的單源:[[Projects/工具分類_計劃]])。每篇節點都掛一個 `scope/<類>` 標籤;要列某一類的全部成員(含計劃/事故/驗證):

    lumos query --tag scope/<類>

下面只列 Systems(機制)節點。狀態以各節點 `status` 為準,這裡標 `[planned]`=設計收斂未落地、`[deferred]`=擱置、`[rejected]`=評估後不做、`[superseded]`=已被取代;無標=已實作。

> **慣例**:節點內嵌的 `scripts/lumos:行號`(或 `@行號`、`:行號`)是**近似導航參考**,code 重構後可能漂移——以 code 現況與函式名為準,行號僅供快速定位。

## 節點內容與標籤(`scope/node-content`)

研究題:一篇節點該長什麼樣、怎麼標,下一個 AI 才用得上

- [[Systems/棧別提問表態閘]] — 推送前每一題效能檢核都要有機器讀得懂的交代
- [[Systems/節點範圍與索引守衛]] — doctor 的三道提醒:計劃條款的測試名找不找得到、索引有沒有列全、有沒有哪篇合約多到讀不完
- [[Systems/check-j-regen-guard]] — Check J:from-scratch 重建節點 provenance 分級(regen 蓋章+[src:]/[git:]/推測:/佚失: 標身分;拒發明無證據合約、假指針機械擋)。
- [[Systems/check-n-recomputable]]
- [[Systems/check-u-overgeneralization]]
- [[Systems/check-y-symbol-existence]]
- [[Systems/lumos-cli-write]] — 寫:set/append/new/archive/decision-add/decision-supersede/self-audit;T1 寫後自驗 atomic。
- [[Systems/外部對照-code衍生wiki]] — langchain-ai/openwiki(11.6k★ code 衍生 wiki)反例世界解:站在 lumos 導覽層、賭注相反(code 衍生+可丟 vs 圖譜手寫+機械守);核心論點=重生保新鮮≠正確、無輸出 oracle(maker-only),反證 lumos「圖譜即真相/合約驗證層」的必要。
- [[Systems/節點還原]]

## 節點檢索與推薦(`scope/retrieval`)

研究題:給一個任務,哪些節點該浮上來、排序對不對

- [[Systems/lumos-cli-read]] — 讀/巡檢:doctor/context/contracts/search/links/backlinks/map/export/decisions/stale/recent/stats。
- [[Systems/retrieval-ranking]] — BM25F 排序+圖分融合推薦+impact 降噪(search 與 hook 面均已轉正——§6 七盞全綠;recommend 面 dormant)。

## 迴圈工程(`scope/loop-engineering`)

研究題:一輪審查什麼時候算過、過得可不可信

- [[Systems/autonomous-iteration-loop]] — 日報 gap→brainstorm→design-loop→收斂備 pending 的無人看顧自主迭代。
- [[Systems/canary-audit]] `[deferred]` — test-the-tester:每輪偷植已知假錯驗審計員有沒有認真抓(防假陰性/放水)。
- [[Systems/convergence-evidence-gate]]
- [[Systems/design-loop]] — canary-護的設計審計 loop;Claude 編排、lumos 出原語,連 2 輪 caught 才放行實作。
- [[Systems/finding-refute]] — 辯方 refute:對 ≥major finding 派獨立 opus 強制 file:line 反證才降(防假陽性,對稱 canary)。
- [[Systems/judge-severity-gate]] — 讓 judge 覆蓋 severity 維度,堵「收斂門檻沒覆蓋處偷工」。
- [[Systems/loop-convergence-recording]] — `canary record --loop/--severity` + `loop status --need` 算收斂、可機械終止多輪。
- [[Systems/lumos-refcheck]]
- [[Systems/pitfalls-code-loop]]
- [[Systems/risk-tiered-review]]
- [[Systems/開發工作流總覽]]

## Agent DAG 工程(`scope/agent-dag`)

研究題:誰跑、什麼順序、帶什麼脈絡、什麼權限、能不能平行

- [[Systems/arch-alignment-lens]]
- [[Systems/cross-family-audit]] — 換模型家族複核(qwen3-max),解 opus 審 opus 的自我偏好偏心。
- [[Systems/heterogeneous-finder-ensemble]]
- [[Systems/nested-agent-permission-scope]] `[planned]` — 子 agent 權限收窄(maker≠checker 的審計員不繼承主對話權限)。

## 評測 Evals(`scope/evals`)

研究題:怎麼量這些機制到底有沒有用

- [[Systems/drift-history]]
- [[Systems/judge-perturbation-stability]] `[rejected]` — 評審擾動穩定性;評估後改走輕量 confidence_report.py。
- [[Systems/verification-rot-eval]] `[superseded]` — 從圖譜史抽衝突測試集定期回測 L3 腐化偵測(設計收斂未落地)。

## 合約守衛與閘門(`scope/guards-gates`)

研究題:什麼機制會機械地擋下壞改動

- [[Systems/anchor-integrity]]
- [[Systems/bound-tests-gate]]
- [[Systems/check-r-guard]] — Check R:不可逆動作(★IRREVERSIBLE★)動手前要有實質 `[rollback:]`/`[guard:]`。
- [[Systems/check-t-sentinel]] — Check T:★INVARIANT★ 合約綁可執行測試 `[test:]`(+ stub 紅燈哨兵)。
- [[Systems/cochange-guard]] — co-change 漏改守衛:git 歷史挖共改規則(ROSE 非對稱 confidence),pre-commit Gate CC 警告漏改夥伴(advisory)。
- [[Systems/core-invariant-baseline]] `[deferred]` — 核心節點已知良好快照 + 可回退(pivot 為 content-baseline,擱置)。
- [[Systems/delguard]]
- [[Systems/doctor-irreversible-hint]] — `[H]` 軟提醒:掃 diff 碰 prod/外部 API → 是否漏標 ★IRREVERSIBLE★。
- [[Systems/graph-sync-coverage]]
- [[Systems/guard-kill]] — 殺傷力驗證:宣告壞法→worktree 隔離→綁定測試必翻紅;survived=稻草人證據(合約鏈最後一哩)。
- [[Systems/reversibility-governance-ledger]] — 可逆性綁定 + gov 治理事件帳(某節點被哪幾道閘攔過)。
- [[Systems/test-profile-multiplatform]]

## 技術棧知識與 linter 橋接(`scope/stack-knowledge`)

研究題:工具對某個技術棧知道什麼、接了哪些外部檢查器

- [[Systems/compose-metrics-adapter]]
- [[Systems/known-pitfall-refresh-token]]
- [[Systems/lint-declaration-health]]
- [[Systems/lint-version-watch]]
- [[Systems/linter精選目錄]]
- [[Systems/pitfalls-lint-adapter]]
- [[Systems/效能檢核目錄]]

## 平台、分發與生命週期(`scope/platform`)

研究題:怎麼裝到機器上、跟 Claude/Codex 怎麼接、怎麼更新怎麼拆

- [[Systems/codex-harness]]
- [[Systems/hook信任邊界]]
- [[Systems/hook逾時預算]]
- [[Systems/lumos-cli-lifecycle]] — install/uninstall/update/bootstrap/init/deinit;機器層 vs 專案層分工。
- [[Systems/lumos-deinit]] — 專案層反安裝指令(對稱 `lumos init`);四重閘保護不可逆的 vault rmtree。
- [[Systems/native-windows-support]] — 原生 Windows(get.ps1 / mklink / junction / hook 路徑正斜線化)。
- [[Systems/slim-gen-生成器]]
- [[Systems/slim-get-一行安裝]]
- [[Systems/slim-install-安裝器]]
- [[Systems/slim-readme]]
- [[Systems/slim-scan-掃描器]]
- [[Systems/slim-skill-修剪]]
- [[Systems/slim-uninstall-一行卸載]]
- [[Systems/授權與歸屬]]

## 介面、文件與工程紀律(`scope/ux-docs-hygiene`)

研究題:沒脈絡的人或 AI 進來找不找得到路;工具自己的測試與流程可不可信

- [[Systems/測試假綠形態]]
- [[Systems/診斷迴圈先行]]

## 外部設計 / 計畫文件(圖譜外,但屬本工具鏈)
- `docs/design/` — 各功能設計稿(含 design-loop 收斂紀錄)。
- `docs/superpowers/plans/` — 實作計畫(TDD 任務分解)。
- `docs/methodology/` — 「圖譜即合約」方法論。
- `governance/reports/` — AI 治理日報(研究 → gap → 觸發上述功能的 provenance,各 Verification/Systems 節點內有溯源)。
