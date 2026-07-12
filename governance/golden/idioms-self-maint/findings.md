# idioms-self-maint · design-loop findings 語料（3 輪，2026-07-12）

> 狀態：**架構收斂、接縫未收斂**；人裁定收成設計資產、暫停實作（**非** panel gate-clean）。
> spec 快照見同目錄 `spec.md`（＝計劃節點 `Projects/idioms自維護迴路_計劃` 的 C'' 版）。
> 跨家族 Codex（gpt-5.6-sol）否決席 3 輪皆決定性——兩個同家族 sonnet 挖文件內部一致性，Codex 讀 repo 才知真實契約。

## 輪次帳（canary log）

| 輪 | canary（型別） | 抓到? | 有效輪? | 最嚴重存活 | 轉向 |
|---|---|---|---|---|---|
| r1 | C4收集器(a) / --since-last-adopted(b) | 皆漏抓 | 否（判決不採信） | blocker（Codex） | → C' |
| r2 | ANNOTATION_CAP(c) / idioms-rules-index.json(d) | 皆抓到 | 是 | blocker | → C'' 拆層 |
| r3 | proposal-index.json(d) / [S22]壞引用(a) | 皆抓到 | 是 | blocker | 暫停 |

（探針註記：type-b/c 未定義符號在「只給片段」的 haiku 探針下天生易噴，且部分探針 prompt 附了提示汙染；已在對應輪判讀時扣除。）

## 三輪逐層揭露的深層真相（Codex 決定性 findings）

- **r1**：「只借不造」的假設半數與現契約不符——canary-record 是收斂專用（無候選語意）、自主 loop 是 N=1 單工（不容 drain 插槽）、gapfill 反證邏輯綁單專案（與 idioms 跨專案通用相斥）、lint-watch 輸出已被治理層消費。
- **r2**：更深的 infra-fit——LLM 判斷鏈（refuter/草案生成/C3 旁註抽取）接不上零依賴 stdlib 的 cron（`lumos` 不 spawn agent、code-loop reviewer 無結構化 parser、governance daily 只是 shell）。另：`fcntl` 與工具鏈原生 Windows 承諾衝突、lint-upgrades 每日覆寫會漏、C1b 監測對象（kotlin-stdlib≠Compose≠AGP、NuGet≠.NET SDK）不成立。
- **r3**：架構（M/A 拆層）被兩 sonnet 認證站住，但 A 層的整合點在 repo 裡**不存在**：① `autonomous-loop.sh` 無 idioms tick、`lumos-idioms-maintain` skill 未建 ② `lumos code-loop` 無認 `<<<IDIOMS-ANNOTATION>>>` 的 parser/hook ③ `IDIOMS_SELF_REVIEW` 無跨 session 控制面。另：`seen.jsonl` 實際只 `{name,latest,seen}` 扛不起 `from→to`；六態缺 lease/CAS。

## 實作前必解接縫（phase-2 checklist）

完整清單見 spec.md §八。摘要：
- 🔴 A 層觸發入口（phase-1 = 人手動跑 skill）／C3 抽取編排點／跨 session 旗標控制面——三個整合點需真 build。
- 🟠 seen.jsonl 扛不起 stale 身分（需更完整事件源）／並發 lease+CAS／schema 補 from→to·retry_count·rejected理由·proposal-id／跨儲存原子性 reconciliation／portable stale-lock owner token／target_rule 改由 A 層填／自引用只蓋力度②。
- 🟡 C1b 復用 `_registry_latest` 勿另造／§二 diagram staging 誤畫。

## phase-1 MVP 建議

只做 **M 層**（C1a/C1b 版本偵測 → 候選池 → staging，純 lumos stdlib、可無人 cron）+ **人手動跑的 `lumos-idioms-maintain` skill**（refuter/drain）。不碰 C3 code-loop hook、不碰自主 loop 整合。C3 旁註 + 全自動列 phase-2。

## 方法論收穫（meta）

- **跨家族否決席（Codex）三輪皆決定性**：同家族 panel 的共同盲點是「只驗文件內部一致性、驗不出與 repo 真實契約的落差」；讀 repo 的外家模型是接住這類的唯一防線。→ 佐證 `[[canary可信度因spec而異]]` 與 reviewer 跨家族 slot 的設計。
- **design-loop 對「觸及大量既有系統契約的整合型 spec」特別有價值**：它把「這假設了不存在的整合點」逐層逼出，避免帶著錯假設進實作。
