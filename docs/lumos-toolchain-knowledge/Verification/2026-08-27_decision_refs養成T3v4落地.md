---
type: verification
status: pass
date: 2026-08-27
valid_under: "六原語(backlog/candidates/add-ai/list/prune/promote)+雙欄不對稱信任(E2 只讀 decision_refs 正欄、E3 讀聯集,T1 已建未動);_dref_same 正規化 tuple 含空-did 守衛;單編排者單次單趟批次;engine=dref-v4 三輪 fold-at-cap 收斂"
revalidate_when: "若日後決定週期性重跑 backlog(非本批一次性回填):必先解「人剪的/AI 判不像的」持久記憶問題(v3 否決記憶想解、引入更貴的洞被砍),重啟前重新設計+重跑 panel;回填覆蓋數若持續 <10 條=T3 ROI 確如凍結所判的小,收尾據實講"
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/decision_refs自動養成_實作計畫]]"
---
# 2026-08-27_decision_refs養成T3v4落地
## 做了什麼

Enzo 2026-08-27 裁「AI 輔助回填一批」,解 decision_refs 雞生蛋(機制 2026-07-15 建好、1103 測綠,但 0 筆在用因回填是語意任務)。撿 2026-07-15 凍結的 T3 v4 方向實作:

- **設計審(dref-v4)三輪 fold-at-cap 收斂**:r1 五席(1 blocker+4 major)→r2 delta+外家(3 major)→r3 delta+外家(2 major),全折;外家 r3 否決解除。挖出並修:砍否決記憶重開的兩種振盪(人剪的/AI 判不像的)、簡寫 vs 正規形逐字打架、promote 蓋章連帶關同節點其他翻案告警(blocker)、批次邊界純靠紀律無機械擋、_dref_same 空-did 誤併。核心折法=單次單趟批次(對上「回填一批」一次性)+正規化契約貫徹每條路+覆蓋掃描含無 id 決策。
- **實作六原語**(scripts/lumos):backlog 集合差、candidates 讀側去重、add-ai 存在性+正規化冪等、list 分欄、prune 正規化定位、promote 雙欄原子+count-check+覆蓋提醒。不動 E2/E3 讀側(不對稱信任 T1 已建)。
- **真回填一批**:8 條 decision_refs across 5 個驗證節點(design-loop折入守衛→#d1、cochange→#d1/d2、refcheck→#d1/d2、anchor-integrity→#d1/d2、multiplatform→#d1),全是「驗證背書它驗的實作的設計決策」高信心匹配。E3 意圖鏈那道檢查因此從「0 筆可查(雞生蛋)」醒成「8 筆在讀」。

## 驗證證據

- 釘測試 t_dref_* 6 支(backlog 集合差補一條仍列/補齊退出、add-ai 存在性+dangling+簡寫等價冪等、promote 雙欄+dangling+簡寫 promote count-check 鑑別、prune 正規化定位真移除 vs 本來不在、不對稱信任 _ai 不碰 E2),含既有 T1 硬化共 30 綠;突變驗 3 發(dangling 拒/prune 逐字/promote count 退化——第三發原假釘,補「簡寫 promote」鑑別案後翻紅)。
- doctor 0 issues(375 篇);E3 讀這 8 條 decision_refs 不 dangling。

## 誠實邊界(天花板)

- ★覆蓋窄★:backlog 164 節點/985 未填槽,但大多是 related 邊的結構巧合(某筆記剛好連到有決策節點,非真背書)。真回填要逐節點讀內容判,判錯=往圖譜塞假連結。本批只做 8 條高信心的(verified_by/plan_refs 邊、驗證背書其實作決策),全量 985 槽的回填=後續語意工程,不硬湊數字。這正是 2026-07-15 凍結時判的「T3 窄覆蓋小加分」,實測證實。
- 單編排者單次單趟純靠協議紀律,無機械擋;禁併發(見 spec)。
- AI GIGO:填哪條靠判斷,誤 ai-ref 只誤觸發 E3 advisory(人 prune),不對稱信任兜住(ai-ref 抑制不了 E2)。
