---
type: project
status: doing
created: 2026-07-15
updated: 2026-07-15
summary: |-
  FLAG:DECISION
  KEY:解決 decision_refs 的雞生蛋——工作流沒東西產生它,故 E3 與主網 Systems 牙口全睡著(真圖 259 節點/39 有決策/0 reindex/0 decision_refs)。目標=讓系統自我養成 decision_refs,讓 [[關係層主網_實作計畫]] 賺回工
  KEY:實測揭露「補哪條」大部分機器判不了——驗證→決策的連結無結構替身(308 方向邊只 9 條巧合指到決策節點,低召回);故自動判斷=T1 帳本地面真相(機械)+T3 AI 語意填補(讀內容),純機械只是零頭
  KEY:信心階梯 前置P reindex決策節點 → T1 confirm回寫(地面真相,機械) → T3 AI自動填背包(2026-07-15拍板放手:AI自動填+by:ai+人抽查翻案,同主網auto-confirm不對稱安全)
  KEY:核心安全風險=AI誤指決策 → 不對稱信任:ai-ref 對 E3 firing 生效(加法/advisory/一刪),但對 E2 suppression 不生效(誤ref抑制真落後邊=靜默漏傳播=頭號腐爛;suppression 只認 by:human/cascade-confirmed)
  DEP:[[關係層主網_實作計畫]]｜[[Systems/lumos-cli-write]]｜[[Systems/lumos-cli-read]]
  DECISION:進實作前過 lumos-design-loop(碰寫入路徑+AI派工+靜默抑制風險);本節點 spec 完成即交 loop
tags:
  - type/project
  - status/doing
plan_refs:
  - "[[關係層主網_實作計畫]]"
---
# decision_refs自動養成_實作計畫

## 問題（緣起）

主網（[[關係層主網_實作計畫]]）實測揭露：它的真實牙口卡在 `decision_refs` 採用，而**工作流裡沒有任何環節產生 decision_refs**——雞生蛋死鎖。E3（意圖鏈斷義）與主網對 Systems 節點的直接點名都因此永久睡著。

**真圖數據（LandmarkMember 259 節點，2026-07-15 實測）**：39 節點有決策、**0 reindex 過**、**0 decision_refs**。方向邊 308 條，只 **9 條**指向「有決策的節點」。

**關鍵誠實發現**：「哪些節點缺 decision_refs」**大部分機器偵測不到**——因為缺的那個「實作了哪條決策」是語意連結、無結構替身（一篇驗證實作 `POS-API#d3`、卻只有 `plan_refs→某計劃`，跟 POS-API 之間沒有邊）。機械只看得到 9 條巧合對齊的（低召回）。故「自動判斷需要補」＝ **T1 地面真相（機械）＋ T3 AI 語意填補（讀內容）**，純機械只是零頭。

## 信心階梯（三層 + 前置）

- **前置 P：`decision-reindex` 決策節點** — decision_refs 需 `<節點rel>#dN`、目標決策先要有 id。機械、一次性、每個決策節點跑一次（39 個，現 0 個）。M1 已交付 reindex 指令，此處是套用。
- **T1 帳本回寫（地面真相，機械）**：`rel-cascade confirm` 成功 → 把 `from_decision_id` append 到被 confirm 鄰居的 `decision_refs`，provenance 沿 `--by`（ai/human）。**`prune` 不回寫**（判無關＝不記依賴）。走 `atomic_write_verify`。往前自我養成。
- **T3 AI 語意填補（背包，AI-auto-liberal，2026-07-15 拍板）**：`lumos decision-refs suggest <驗證>`（或掃描）→ 派 AI 讀驗證內容 + 候選決策（該驗證 plan_refs 指的計劃的 decisions、或關聯 Systems 的 decisions）→ AI 判實作哪條 → **自動 append + 標 by:ai** → 人透過 `lumos decision-refs --by ai` 抽查、剪錯的。覆蓋背包大宗。
- **T2 結構缺口（零頭）**：那 9 條「邊指到決策節點卻無 ref」折進 T3 的候選選取（決定對哪些驗證派 AI），**不做獨立 doctor 檢查**（低召回、不值得一道常設檢查）。

## 釘死的合約

- **不對稱信任（核心安全）**：AI 誤指決策（V 實作 d3、AI 填 d2）的緩解——`by:ai` 的 ref **對 E3 firing 生效**（加法、advisory warn、錯了人一刪、低 harm），但**對 E2 suppression 不生效**。因為誤 ref 拿去抑制 E2 ＝把真落後邊靜默藏掉 ＝本守衛要防的頭號腐爛（危險方向）。**E2 帳本抑制只認 by:human 或 cascade-confirmed 的 ref**；ai-ref 升級成可抑制需人抽查蓋章。這是把主網「auto-confirm 放寬 / auto-prune 保守」的不對稱，套到 ref 的「firing 放寬 / suppression 保守」。
- **provenance 格式（定案 ③，2026-07-15）**：ai 填的進獨立欄位 **`decision_refs_ai`**、human 確認/cascade-confirmed 的進 **`decision_refs`**。**這個雙欄結構本身就是不對稱信任的機械實現**：E3 firing 讀「兩欄聯集」（放寬）、E2 suppression 只讀 `decision_refs`（保守，ai 欄結構上碰不到抑制）。人抽查蓋章＝把某條從 `decision_refs_ai` 搬進 `decision_refs`（升級成可抑制）。比平行 by 欄（易漂移）與富格式行內 `by:ai`（改動既有解析）都乾淨。E2/E3 讀側各自明確吃哪欄，無隱式合併歧義。
- **回寫的節點範圍**：confirm 可 confirm 任何鄰居（含 Systems）；decision_refs 寫到被 confirm 的節點上（與 E2 首判精化讀任何鄰居 decision_refs 一致，非只 Verification）。
- **reindex 前置**：suggest/回寫前目標決策必須有 id；無 id 的目標 → 先提示跑 reindex（同 supersede `#dN` 查無的處置），不自動 reindex（避免隱式改別的節點）。
- **audit surface**：`lumos decision-refs [--by ai] <節點>` 列 ref + 來源；剪錯的走既有寫入原語（或補 `decision-refs prune`）。

## 天花板
- **T3 是 AI GIGO**：AI 判實作哪條決策，判錯 = 填錯 ref。緩解靠不對稱信任（firing 可容錯、suppression 不容錯）+ by:ai 可抽查，非靠準度。
- **不追求高召回的機械偵測**：機器只保證「翻案掃過的（T1）」+「AI 讀過的（T3）」長出 ref；沒人碰的驗證背包靠增量清。
- decision_refs 對就對、錯了 advisory 級提醒，不污染業務邏輯——這是敢放手 auto-fill 的前提。

## 落地順序
> **進度（2026-07-15）**：P ✅（`decision-reindex --all`，本 vault 38 節點 dogfood）+ T1 ✅（confirm 回寫 + 不對稱信任雙欄，[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]，1123 tests 綠）→ **T3 待 design-loop**。

1. **前置 P**：套 `decision-reindex` 到決策節點（機械，可先在 lumos-toolchain 自身跑、再 LandmarkMember）。
2. **T1 confirm 回寫**（機械、地面真相、現成可建）——主網從「需要 ref」翻成「一邊動一邊長 ref」。
3. **T3 AI suggest**（含不對稱信任、provenance、audit）——覆蓋背包；design-loop 重點審這塊。

## 進實作前（紀律）
本 spec 完成 → 交 **lumos-design-loop**（碰寫入路徑 + AI 派工 + E2 靜默抑制風險，建議 `--need 3`）到 `loop status --gate --panel` 收斂才實作。落地 Verification 以 `plan_refs` 回指本節點。
