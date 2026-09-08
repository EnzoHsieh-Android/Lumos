# 世界調研:設計審清單的「認領→實作→勾除」怎麼防不同步(2026-09-08)

> 來源:乾淨 agent(無本專案脈絡,只用 WebSearch/WebFetch),題目逐字:「設計審查會產出一份條款/驗收清單。實作階段:認領某一項→實作→完成後勾掉。世界上有沒有現成工具/方法論/研究是這樣運作的?它們怎麼防止『做完了但清單沒勾、或勾了但沒做』?」派工者:handoff-view session。以下為報告原文。

## 1. AI coding agent 的任務追蹤(markdown/git 儲存,有 claim/complete)

**Beads (bd)** — Steve Yegge 做的,agent 專用的圖狀 issue tracker。
- 狀態存在 `.beads/issues.jsonl`,跟著 code 一起進 git commit;背後是 Dolt 資料庫,支援跨機器同步。
- 認領:`bd update <id> --claim`;完成:`bd close <id>`。`bd ready` 只列出「沒有未解阻塞」的任務。
- 防不同步機制是「**存起來的**」——claim/close 都是明確寫入的狀態欄位,不是從測試結果推導。漂了怎麼發現:靠 git 版本歷史 + dolt push/pull 同步時的衝突偵測,本質上還是人/agent 要主動去對帳。
- 來源:https://pkg.go.dev/github.com/steveyegge/beads 、https://betterstack.com/community/guides/ai/beads-issue-tracker-ai-agents/

**TASKS.md** — 單一 Markdown 檔放 repo 根目錄。
- 認領:agent 在任務行後面加 `(@agent-id)`。完成:**整段任務刪掉**,歷史只活在 git log。
- 有選填的 Acceptance / Verification 欄位,但**沒有機械閘檔**——官方自己承認:「沒有防止假完成的內建機制,取決於 agent 是否誠實」。
- 來源:https://tasksmd.github.io/tasks.md/

**beans** — 純 Markdown + GraphQL 查詢層;同樣是「存起來」的狀態,沒查到自動核對機制。來源:https://github.com/hmans/beans

## 2. Spec-driven development 工具

**GitHub Spec Kit** — `/specify → /plan → /tasks → /implement`。
- 狀態存在 repo 裡的 `tasks.md`,任務用 checkbox,agent 邊做邊把 `[ ]` 改成 `[X]`。
- 社群公認的破口:官方 issue 上有人提案 `/speckit.verify`,理由是「`/speckit.implement` 跑完後沒有結構化驗證步驟確認 tasks.md 上的項目真的做完」——目前是**人工事後補驗**。
- 來源:https://github.com/github/spec-kit/discussions/1662 、https://github.com/github/spec-kit/issues/1862 、https://github.com/github/spec-kit/issues/1745

## 3. 需求追溯(requirements traceability)

- 商用工具(TestCollab、Parasoft DTP)做條款↔測試案例↔程式碼矩陣,大多「半自動算出來」:測試結果自動回填,但條款↔測試的連結本身還是人工建立。來源:https://testcollab.com/features/requirements-traceability-matrix 、https://www.parasoft.com/solutions/requirements-traceability/
- 學術界(Traceability Link Recovery)公認痛點:「連結會腐朽」——需求或程式碼改了,舊連結沒人更新,變成看似有覆蓋其實誤導。2026 *ReqToCode* 想把需求 ID 嵌進型別系統,讓連結成為程式碼結構的一部分。來源:https://arxiv.org/html/2603.13999 、https://arxiv.org/html/2606.11834

## 4. BDD / living documentation

**Cucumber / Gherkin(+ SpecFlow、Behave、Serenity BDD)**
- 驗收條款直接寫成 Gherkin 情境,就是測試腳本;文件是**測試跑完自動產生的報告**。
- 本次少數「**完全算出來、不存狀態**」的例子:條款做完了沒 = 對應測試綠了沒,沒有可漂移的獨立 checkbox。
- 限制:Gherkin 步驟含糊或跟實作脫節時,「通過」只代表腳本邏輯通過,不保證覆蓋業務意圖——條款品質問題,非同步問題。
- 來源:https://cucumber.io/docs/bdd/better-gherkin/ 、https://technology.lastminute.com/living-doc-bdd-cucumber-serenity/

## 5. Issue tracker 自動化

- **GitHub「Closes #123」**:PR 合併進預設分支時自動關閉 issue——關閉動作綁在 merge 這個既有事件上。來源:https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
- **GitHub Task List / Sub-issues**:子 issue 關閉,父項目 checkbox **自動**勾、「N/M 完成」自動算——勾選狀態鏡射子 issue 開關,不是獨立欄位。來源:https://docs.github.com/enterprise-server@3.0/issues/tracking-your-work-with-issues/about-task-lists

## 共同模式

能真正防住不同步的例子,結構都收斂到一句話:**狀態不另外存,而是從一個已經存在、有代價偽造的產物直接讀出來**——BDD 讀測試結果、GitHub task list 讀子 issue 的開關狀態、「Closes #」讀 merge 事件。凡是「存起來的」欄位(Beads、TASKS.md、Spec Kit),**清一色沒有機械對帳機制**,全部承認靠自律,頂多用 git 歷史留痕方便事後追查。能不能防漂移,取決於「完成」這個動作本身有沒有被綁在一個必然留下客觀痕跡的事件上。

## 沒找到的

- 沒找到「設計審查清單」專用、原生把每條 claim/complete 綁 CI 測試結果的現成工具——BDD 最接近,但綁的是驗收條款,不是設計審條款。
- 沒找到專門研究「AI agent 認領清單項目的同步機制設計」的論文(有「AI agent 假完成」的失敗模式論文:https://arxiv.org/pdf/2606.09863)。
- Requirements Traceability 領域沒有工具聲稱「條款狀態 100% 由產物自動推導、零人工連結」。
