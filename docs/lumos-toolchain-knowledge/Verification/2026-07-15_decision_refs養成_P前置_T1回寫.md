---
type: verification
status: pass
feature: decision_refs 自動養成 P前置(reindex --all)+ T1(confirm 回寫 + 不對稱信任雙欄)
commit: 待填
date: 2026-07-15
valid_under:
  - "provenance 雙欄 decision_refs(human/cascade)/decision_refs_ai(AI 填)機械實現不對稱信任"
  - "confirm 回寫走 exact-string dedup(非 link_target——它 strip #dN 會誤合同節點不同決策);值引號化"
  - "E3 firing 讀兩欄聯集(放寬);E2 首判精化抑制只讀 decision_refs(ai 欄碰不到抑制)"
revalidate_when:
  - "T3 AI suggest 落地(decision_refs_ai 開始由 AI 大量填,抽查/剪除工作流成形)"
  - "provenance 欄位語意變更、或 E2/E3 讀側改動"
plan_refs:
  - "[[decision_refs自動養成_實作計畫]]"
tags:
  - type/verification
  - status/pass
---

# 驗證：decision_refs 自動養成 P前置 + T1 回寫

主網雞生蛋的解法起手（[[decision_refs自動養成_實作計畫]]）——落地純機械、低風險的 P + T1，讓 decision_refs 開始自我養成；T3（AI 語意填補）另過 design-loop。

## 變更範圍（scripts/lumos）
- **前置 P：`decision-reindex --all`**（新旗標）：批次套用到所有有 decisions 的節點（顯式指令、非隱式）；每節點沿用 M1 冪等 reindex。本 vault dogfood：38 節點全處理、0 拒絕、doctor 0 issues。
- **T1：`rel-cascade confirm` 回寫 decision_ref**：confirm 成功＝地面真相「鄰居依賴這條決策」→ 把 `from_decision_id`（`<rel>#dN`）append 到被 confirm 鄰居。**prune 不回寫**（判無關＝不記依賴）。回寫失敗＝軟警告不回滾（帳本才是地面真相）。
- **`_append_decision_ref` helper**：**exact-string dedup**（不用 `link_target`——它 `split('#')` 會剝掉 `#dN`、導致同節點不同決策誤合成一條，這是關鍵防護）；值引號化（含 `#`/`/` 安全）；走 `atomic_write_verify`。
- **不對稱信任雙欄接線**：by ai → `decision_refs_ai`、by human → `decision_refs`。**E3 firing 讀兩欄聯集**（放寬：ai 填的也提醒，錯了 advisory 級人一刪）；**E2 首判精化抑制只讀 `decision_refs`**（保守：誤 ai-ref 抑制真落後邊＝靜默漏傳播＝頭號腐爛，故 ai 欄結構上碰不到抑制）。

## 測試項目（11 斷言）
| 面 | 斷言 | 結果 |
|---|---|---|
| P `--all` | 涵蓋多節點、NoDec 不碰、冪等、無參數 rc=2 | ✅ |
| T1 回寫 | by ai→_ai 欄、by human→正欄、prune 不寫、引號+精確 #dN | ✅ |
| T1 精確 dedup | 同節點 #d1 與 #d2 不誤合（link_target bug 防護）、重 confirm 冪等 | ✅ |
| 不對稱信任 | E3 讀 ai 欄觸發、E2 抑制不讀 ai 欄（誤 ai-ref 抑制不了真落後邊） | ✅ |
| dogfood | 本 vault reindex --all 38 節點、doctor 0 issues；全套 1123 passed/0 | ✅ |

## 天花板 / 下一步
- 這兩塊是機械地面真相：只涵蓋「翻案 confirm 掃過的」往前長。背包大宗（52 篇有 plan_refs 的驗證）靠 **T3 AI suggest**——那塊碰 AI 派工 + 誤指決策風險，**另過 design-loop**（設計已釘不對稱信任當安全網）。
- reindex --all 已在本 vault dogfood；LandmarkMember 待套用。

## 相關模組
- [[decision_refs自動養成_實作計畫]]（P✅ T1✅ → T3 design-loop）
- [[關係層主網_實作計畫]]（本功能讓主網從「需要 refs」翻成「自我養成」）
- [[Systems/lumos-cli-write]]（decision-reindex/rel-cascade 寫入面）
