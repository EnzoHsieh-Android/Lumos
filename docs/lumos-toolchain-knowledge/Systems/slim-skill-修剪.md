---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
summary: |-
  FLOW:`cp -R skills/lumos-project-notes slim/skills/` 建交付源目錄副本 → 跑 `slim-scan.py` 出 129 條候選 → 逐條人工裁(改寫句子/刪整段/判假陽性)→ 重跑掃描器剩 14 條、逐條可指出假陽性理由(全是「明講某指令未交付」的誠實揭露句,被裸 token/prefixed 形態誤判成教學) → SKILL.md 本身收斂到 0 候選
  KEY:修剪原則=只修懸空引用,紀律語氣照舊不動(spec 已裁定①)——語氣豁免保的是「話」不是「話所在的段落」,如 SKILL.md 原 ci-wait bullet 整段圍繞已砍指令展開,但「紅燈不過夜…不得靜默收工」這句的主詞是「CI 紅燈」不是工具,拆出來留、工具子句砍
  KEY:reference.md「子命令全覽」行(原列 53 支)整行改寫成只列 24 支保留指令,分四類(讀取/導航 12＋巡檢/治理 4＋寫入 7＋合約守衛 1=24)
  KEY:整段刪除的三處=①`pitfall_when` 欄位說明(通篇依附已砍 `impact`)②「對抗設計審計的 canary」整節(依附已砍 design-loop/canary/loop,無可拆的獨立紀律)③「安裝/生命週期」指令表(四支已砍指令的完整用法列)
  KEY:★DEBT★ 剩 14 條候選全是誠實揭露句(如「本精簡版無 `signoff` 指令,人工記錄即可」),故意保留這些句子讓讀者知道某功能不存在,不算懸空引用;唯一一條真正的假陽性形態不同=reference.md:340 的 `npx playwright install` 撞到裸散文 `install` 比對,與 lumos 指令無關
  DEP:scripts/slim-scan.py｜slim/skills/lumos-project-notes/{SKILL.md,reference.md}
  TEST:掃描器對修剪後兩檔重跑 rc1(候選 14/129,SKILL.md 單獨掃 rc0)——本身無自動化 t_slim_* 測試(內容裁決是人工判斷,機械層只有掃描器,已在 [[Systems/slim-scan-掃描器]] 覆蓋),verified_by 見下
verified_by:
  - "[[Verification/2026-07-31_slim-skill與readme落地]]"
---
# slim-skill-修剪

公開精簡版交付前,對「直接複製」的 `skills/lumos-project-notes/`（`SKILL.md` + `reference.md`）做懸空引用修剪——原始檔教了大量已被精簡版砍掉的指令（`pitfalls`／`impact`／`canary`／`loop`／`self-audit`／`signoff`／`spec-trace`／`install`／`bootstrap` 等 29 支)與不交付的 skill（`lumos-design-loop`／`lumos-core-knowledge` 等)，直接複製給接手者會教他們去用不存在的東西。詳見 [[Projects/公開精簡版_實作計畫]] Task 4。

裁決統計(129 條候選逐條裁):改寫句子 50 條、整段/整列刪除 78 條、初裁即判假陽性 1 條(reference.md:340,`npx playwright install` 撞裸散文 `install` 比對,與 lumos 指令無關)。重跑掃描器後剩 14 條候選——其中 13 條是改寫後仍含指令名的「明講某功能未交付」誠實揭露句(如「本精簡版無 `signoff` 指令,人工記錄即可」),掃描器的裸 token/prefixed 形態無法分辨「教你用」與「告訴你沒有」而誤判,連同前述 1 條合計剩餘候選 14 條、逐條可指出假陽性理由,詳見 [[Verification/2026-07-31_slim-skill與readme落地]]。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-4-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此)。
