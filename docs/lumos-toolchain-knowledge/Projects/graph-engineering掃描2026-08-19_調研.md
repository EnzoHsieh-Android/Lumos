---
type: project
status: doing
created: 2026-08-19
updated: 2026-08-19
tags:
  - type/project
  - status/doing
related:
  - "[[Issues/散文紀律沒有退場機制]]"
  - "[[Projects/閘觸發帳統計_計劃]]"
---
# graph-engineering掃描2026-08-19_調研

> 白話:第二次去外面看「圖譜工程」在講什麼、有哪些可以直接抄回來。**本節點是掃描結論的落帳處**——上一次(2026-08-17)只把三條靈感開成節點,掃描本身的結論留在對話裡蒸發,導致這次得重掃一遍。這次把「已經看過、不用再看」的部分一併寫死。

## 為什麼會有第二次掃描

[[Projects/結構訊號補鏈D3_計劃]] 的〈靈感出處〉留了一句「完整掃描結論見當日對話」——那份對話沒了。★教訓:掃描類工作的產出不只是開出來的候選節點,還有「哪些已經確認不用做」,後者不落帳等於下次重付一次搜尋成本。★

## 上次三條的下場(2026-08-17 掃描)

| 條目 | 現況 |
|---|---|
| 結構訊號 D3(code 耦合當補鏈第三訊號) | [[Projects/結構訊號補鏈D3_計劃]] gap 佔位,等一筆實證 miss 才啟動 |
| 派工編制資料化(org graph 版控化) | [[Projects/派工編制資料化_計劃]] 已落地 |
| 宣稱級時間戳(Graphiti 型失效) | [[Projects/宣稱級時間戳_計劃]] 2026-08-18 準入三問裁定**不做**,有硬啟動條件 |

## 本次掃描:確認已被覆蓋的(不用再看)

- **typed edge / 邊型即知識**:世界主張邊型是知識本身(`:supersedes`/`:contradicts`/`:elaborates` 小封閉集)。本專案 2026-07-15 已建 typed-edge 反向索引([[Verification/2026-07-15_主網M2_typed-edge索引]]),frontmatter 具名欄位即邊型。
- **時效/雙時間軸(valid_at、as-of 查詢、supersession chain)**:decisions 翻案鏈 + Verification `valid_under`/`revalidate_when` + `lumos stale` 已覆蓋;宣稱粒度那層已裁不做。
- **goldset + precision/recall 評測**:[[Verification/2026-07-11_檢索goldset評測]] 已做(含 IDCG 自證偏差修正)。
- **narrow schema 而非通用本體**:本 vault 五資料夾 + 標籤家族值域 lint 即窄 schema。
- **org graph 與 work graph 分離**:派工編制案已落地。
- **code 結構圖(Tree-sitter KG,token 省 10x)**:即 D3,啟動條件未滿足。

## 本次掃描:兩條活的直接借鑑

### 借鑑一:建之前先寫好「什麼時候拆」(kill rule)

外界作法(wavect graph economics):圖譜/機制**試辦前**先定 kill rule 與 baseline——「若已驗證答案的時間、任務成功率、審查者工時的改善不足以覆蓋維護成本就停」。

對照本專案:**新機制準入三問(Growth test)只管該不該建,沒有一問管什麼觀測到了就撤。** 而「散文紀律沒有退場機制」已是立著的 Issue([[Issues/散文紀律沒有退場機制]]):全 repo 零常設退場規定,唯一前例明令禁止刪規則,且被前後量過效果的紀律=0 條。

最小解形狀(未立案,待裁):准入三問加第四問「退場判準」,答案一行寫進計劃節點,與 `PRIOR-ART:` 同格。零新機制、零新指令。

### 借鑑二:用既有治理帳算閘的觸發帳,給退場一把尺

外界作法(agent memory 的 forgetting 判準):剪枝訊號=多久沒被取用、取用後有沒有促成好結果;背景 consolidation 常態化。

★本專案已經有資料可以算,只是沒人算★(2026-08-19 實測 `docs/.governance-log.jsonl`,20,139 筆):

- 全帳只出現 **5 種** gate/kind 組合:`check-s/warned` 18,283、`check-e1/warned` 1,637、`anchor-approve/approved` 142、`code-loop/passed` 56、`code-loop/skipped` 21。
- 另有八個閘名整本帳沒出現過——★2026-08-19 查證後分成兩群,不可並列★:`check-r`/`check-j`/`check-k`/`check-e2`/`check-e3` 確實接了本帳(doctor 內 `gov_events.append`,`--ci` 時落帳),516 次 `--ci` 零筆=**真的沒響過**;`canary`/`signoff`/`kill` **寫自己的帳檔**(canary 448 筆、signoff 8 筆、kill 帳檔不存在),零筆與觸發與否無關。
- `check-s`(自足性審計提醒)18,283 筆只落在 **42 個節點**、46 個有紀錄的日子,平均每節點被念 **400+ 次**。★這不是提醒,是背景噪音——會響但不收斂的閘,等同沒有閘。★

最小解形狀(未立案,待裁):`lumos gov` 加一段觸發統計(每閘筆數/涉及節點數/是否收斂),恆觀測不進閘;零觸發清單與高噪音清單即退場討論的素材。

✅ 已查證(2026-08-19,原標「未查證」):見上一則的兩群拆分。★初判把八個並列成「都沒觸發」是錯的,已推翻★——寫別本帳 ≠ 沒觸發。已立案:[[Projects/閘觸發帳統計_計劃]](含「零觸發」措辭必須自曝此限制的規格)。

## 次要(可選,價值較低)

- **證據包裝**:世界主張回答要引**來源記錄**而非只引邊,且路徑含推測/過期邊時要能答「證據不足」。本專案的 `[src:]`/`[git:]`/`推測:`/`佚失:` 只對 regen 節點課,普通節點不課——要不要外推是開放問題,無事故支撐。

## 來源

- wavect「Graph Engineering for AI Agents: When the Graph Earns Its Cost」(kill rule、provenance layer、narrow schema)
- truefoundry「Graph Engineering for Multi-Agent Systems」(org graph vs work graph,上次已借)
- 2026 agent memory forgetting/consolidation 文獻群(temporal decay、frequency-based pruning、outcome salience)
- supermemory / TOKI / temporal validity 論文群(雙時間軸,已裁不做)
