---
type: project
status: doing
created: 2026-07-16
updated: 2026-07-16
tags:
  - type/project
  - status/doing
related:
  - "[[Systems/外部對照-code衍生wiki]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/design-loop]]"
  - "[[Systems/cochange-guard]]"
  - "[[Projects/decision_refs自動養成_實作計畫]]"
summary: |-
  FLAG:DECISION
  KEY:問題=lumos 唯一塌陷回 openwiki 失效模式的點——from-scratch 重生節點時失去目擊者(primary source)、被迫從 lossy 投影(code 快照)逆向工程 why=synthesis bias;只有 [test:] 合約子集有 oracle 接得住,非合約 prose 裸奔。詳見 [[Systems/外部對照-code衍生wiki]]〈重生塌陷例外〉
  KEY:統一原則=讓 from-scratch 優雅退化成「誠實的、分級的不確定」,不編自信 prose。openwiki 原罪=看不見地填滿每個缺口;lumos 反過來=把缺口變可見+有型別。標「不知道為何是 invariant」勝過捏似是而非的 why(擋假信心+指出人力該花處)
  KEY:裁定=解法不在「生成更好 prose」(那就是 openwiki);只能走三路——找回 provenance / 標出不確定 / 給重建套 oracle。且大半=組合現有機械(不對稱雙欄信任 from decision_refs + cochange git 挖掘 + design-loop 對抗審 + signoff),非造新輪子
  DECISION:MVP 只挑最硬核兩條(provenance 分級隔離 + 拒絕發明無證據合約),其餘(git-rationale 收割/訪談路由)留後續里程碑——避免又一個大機械堆小需求(記取 [[Projects/decision_refs自動養成_實作計畫]] T3 凍結教訓)
  DEP:[[Systems/外部對照-code衍生wiki]]｜[[Systems/design-loop]]｜[[Systems/cochange-guard]]
plan_refs:
  - "[[Systems/外部對照-code衍生wiki]]"
---
# from-scratch重生守衛_計劃

> **狀態**：設計 ideation 收成節點，**尚未過 design-loop**（進實作前需過；碰寫入路徑 + AI 派工 + 靜默填 prose 風險，建議 `--need 3`）。緣起見 [[Systems/外部對照-code衍生wiki]] 對話 co-develop。

## 問題（緣起）

lumos 相對 openwiki 的核心優勢是 **provenance**——決策當下第一手目擊記錄，非事後從 code 逆向工程。但這優勢有**唯一破口**：當一個節點必須 **from-scratch 重生**（目擊記錄佚失/從未存在、或 stale 到需整篇重寫、或接手無人 legacy repo），lumos 那一刻也變成 reconstructor，非合約 prose 吃到 openwiki 同款 synthesis bias，且**只有綁 `[test:]` 的 ★INVARIANT★ 合約子集有 oracle 接得住**，其餘 prose 裸奔。

**openwiki 失效是常態（每輪重生無 oracle）；lumos 同款失效是例外（僅 from-scratch 非合約 prose）**——本計劃＝把該例外壓到最小。

## PRIOR-ART

`PRIOR-ART:` ① 最小解在**組合既有閘層**（不對稱雙欄信任、cochange git 挖掘、design-loop 對抗審、signoff 皆已有）→ borrow-design 自家機制小修，非 build。② 世界解＝openwiki（[[Systems/外部對照-code衍生wiki]]，反例：它選擇不解、用「文件可丟」繞過）；ADR/docs-as-code 傳統（Nygard ADR＝人手寫決策當下記錄，正是 lumos provenance 的思想源，但無「重生」概念）。③ 裁定＝**borrow-design**：借 openwiki「別 fabricate、ground every claim」的 maker 紀律 + ADR 的決策當下捕獲思想，原生實作為「分級隔離 + 拒絕發明 + 對抗審 oracle」。

## 統一原則（脊椎）

**讓 from-scratch 優雅退化成「誠實的、分級的不確定」，而不是編出自信的 prose。**
openwiki 原罪＝看不見地填滿每個缺口（分不出真句假句）；lumos 反過來＝**把缺口變可見 + 有型別**。一個標「這條為何是 invariant 我不知道」的節點，比一段合理的假 why 更值錢——擋假信心、且指出人力該花在哪。

## 解法堆疊（由先做到兜底；大半組合現有機械）

1. **縮面積——對舊節點 diff 重生、不整篇換**。stale 也是拿舊節點當底料、只重寫被證據推翻的部分、輸出 diff 給人審。保住殘存目擊內容，把 synthesis 鎖在真變了的地方。＝把 from-scratch 重定義為 maximal-incremental，面積趨零。（openwiki `OPENWIKI:START` 區塊保留法下沉到 claim 粒度。）
2. **provenance 分級隔離——複用不對稱雙欄信任**。每條 claim 帶證據級：Tier A（現 code 可驗,file:line）/ Tier B（git 史變更事件,sha）/ **Tier C（無直接證據的推論 why→明確標 conjecture、進低信任隔離欄）**。同構複用 `decision_refs` vs `decision_refs_ai`（by:ai 結構上抑制不了 E2）：重生推論 why 進低信任層、**不能背書任何合約直到人 promote**。
3. **git 變更序列救 why——複用 cochange 挖掘**。對變更序列（`git log -p`/revert/「fix,rollback」commit/PR merge msg）重建,非對 code 快照。revert 編碼「試過 A 退回 B」這種快照抹掉的 why。加原語:替目標子系統收割 commit-message rationale + 共改證據餵重生 agent。
4. **殘餘 Tier-C 轉問題問人——走 signoff**。目擊者還在＝問不是推。重生吐**問題清單**（Tier-C conjecture）路由給人確認。＝「重生即結構化訪談準備」,一次 lossy 推論換一次便宜人工確認。
5. **拒絕發明無證據合約——留可見 knowledge-gap 標記**。可衍生導覽（FLOW/DEP/結構）安全重生(Tier A);不可衍生的 ★INVARIANT★ 理由/DECISION why 證據沒了就別重生,老實標「已佚失/未證」。anti-openwiki 核心動作。
6. **兜底 oracle——from-scratch 節點強制過 design-loop 對抗審**。從零重生的節點＝還沒審過的 spec;審計員問「這 claim 證據呢?」→ 無 backing 的 Tier-C 浮出。＝openwiki 結構上沒有、lumos 有的「prose 的 oracle」。規則:incremental update 保留目擊 provenance 可輕放;**from-scratch 重生必過對抗審**。

## 里程碑（收窄,記取 T3 凍結教訓——別大機械堆小需求）

- **M1（MVP,最硬核）**：`provenance 分級隔離` + `拒絕發明無證據合約`。＝解法 2 + 5。純機械 + 紀律,複用既有雙欄信任,無新派工。**這兩條不做,其餘都是沙上樓閣。**
- **M2**：`from-scratch 強制對抗審`（解法 6）——把 design-loop 接成重生的 mandatory gate。複用既有 loop 機械。
- **M3（後續,選配）**：`git-rationale 收割`（解法 3,複用 cochange）+ `diff 重生`（解法 1）。
- **M4（後續,選配）**：`Tier-C→signoff 訪談路由`（解法 4）。
- 收窄理由:M1+M2 已把「重生塌陷」的**可見性 + oracle** 兩件事解決(缺口標出來 + 對抗審接住);M3/M4 是把 provenance **主動找回**(錦上添花、面積更小),真有痛點再做。

## 天花板（誠實）

沒有一條能**從無到有變出 ground truth**。目擊者走了、git 沉默、issue 沒留 → 那 why **永久佚失**,正確輸出是「unknown」不是猜。這條沒得繞——而承認它、標出來,本身就是相對 openwiki 的贏法（openwiki 把「不知道」渲染成「知道」,lumos 該把「不知道」如實留成「不知道」）。

## 進實作前（紀律）

本 spec 完成 → 交 **lumos-design-loop**（建議 `--need 3`:碰寫入路徑 + AI 派工 + 靜默填 prose 風險）到 `loop status --gate --panel` 收斂才實作。落地 Verification 以 `plan_refs` 回指本節點。**先只做 M1**、驗證真解決痛點,再決定 M2+。
