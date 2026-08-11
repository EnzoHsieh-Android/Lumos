---
type: verification
status: pass
date: 2026-08-11
valid_under: |-
  lumos 現行 pitfalls --diff 排除規則(governance/review-reports/ 字串前綴)、
  lumos-project-notes skill 現行結構(退場自問節在「常見工作流」與「資料夾/位置」之間)、
  maestro profile 現行行為(綁 flow name: 欄位、Check T 不看目錄)
revalidate_when: |-
  pitfalls --diff 的排除路徑變更
  退場自問節被改寫或搬移
  maestro profile / MAESTRO_NAME_RE 變更
  B 段(mOrangePos)實跑後帶回與本段假設不符的事實
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Android側UI測試綁圖譜工作流_計劃]]"
  - "[[Android側UI測試綁圖譜工作流_實作計畫]]"
summary: |-
  TEST:t_precommit_whitelist_drift_guard 新增路徑同源斷言(先紅 27/1 → 後綠 28/0);全量套件 0 failed
  VERIFY:[[Android側UI測試綁圖譜工作流_實作計畫]] A 段 Task 1-4
  KEY:A 段=本 repo 三處落地(慣例節點證據路徑+Android 通道／skill 退場自問第 4 問／reference.md 派工要求)+圖譜收尾;B 段(mOrangePos,需真裝置)未動
  KEY:★本段只證明「本 repo 這三處寫對了」,不證明工作流有效★—工作流是否真的接得上,要 B 段在 mOrangePos 實跑(雙平台 config→bind/audit→flow 檔案形式跑→回歸釘翻紅)才算
---
# 2026-08-11_AndroidUI工作流A段落地

驗證對象：[[Android側UI測試綁圖譜工作流_實作計畫]] 的 **A 段（lumos-toolchain 側，不需裝置）**。

## 落地內容

| Task | 動的東西 | 驗證方式 |
|---|---|---|
| 1 | `Systems/pitfalls-code-loop` 的 UI 驗收慣例：證據路徑補 `governance/` 前綴＋補 Android（maestro MCP）通道含前置條件 | 新增路徑同源斷言（`t_precommit_whitelist_drift_guard` 內）先紅後綠 |
| 2 | `skills/lumos-project-notes/SKILL.md` 退場自問加**第 4 問**（動到畫面→補可重放 flow 並綁回節點） | 落點 grep 驗證：在第 3 問後、`⚠ 連結不算同步` 行前，該節仍在「常見工作流」與「資料夾／位置」之間 |
| 3 | `skills/lumos-project-notes/reference.md` 新增〈產 maestro UI flow 的派工要求〉 | 節標題與 SKILL.md 第 4 問指向一致；fence 配對（全檔偶數、節內偶數）；七坑表 7 條 |
| 4 | 本節點＋雙向 `verified_by`／`plan_refs` | `lumos lint` 各節點 0 問題、`lumos doctor` 0 issues |

## 測試證據

- **路徑同源斷言先紅後綠**：Task 1 實作者留痕 RED `(27, 1)` → GREEN `(28, 0)`（斷言：`scripts/lumos` 仍含 `governance/review-reports/` 排除字串 ∧ 節點不含無前綴的舊寫法 `存 review-reports/`）。
- **全量套件**：Task 1／2／3 各跑一次，皆 `0 failed`（數字隨版本演進，本節點不做數字快照——查證入口＝各 task 的 commit 與 `.superpowers/sdd/` 報告）。

## 流程事件（誠實記錄）

1. **Task 2 的 implementer 在主 repo（main）commit 而非 worktree**——已 cherry-pick 到 `feat/android-ui-workflow`，main 精準 reset 回原 commit 並還原兩檔（main 未推，無外溢）。之後派工加了「動手前先 `git rev-parse --show-toplevel` 驗身」的防呆。
2. **Task 3 的 implementer 停等一個不存在的背景測試**——控制器親核 fence 配對／節界／表格內容、跑全量、代 commit（無內容修改）。本 loop 第二例同型死法。

## ★天花板（本段只證明了什麼）★

- **只證明「本 repo 這三處寫對了」**——慣例散文、skill 問句、派工要求都是**紀律不是機械閘**，忘了就是忘了。
- **不證明工作流有效**：`[test:maestro:名]` 真的綁得上、Check T 真的認得、flow 真的可重放，全部要等 **B 段在 mOrangePos 實跑**（雙平台 config → bind／audit → 檔案形式跑 → **回歸釘翻紅**）才算數。
- spec 天花板列的東西一條都沒解決：`name:` 唯一性無守衛、`[kill:]` 在 UI 層走不通、版面一改要重錄、時機那格只做到「有人問」。
