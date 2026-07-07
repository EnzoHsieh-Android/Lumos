---
type: issue
status: done
created: 2026-07-07
updated: 2026-07-07
related:
  - "[[lumos-cli-lifecycle]]"
  - "[[code-loop必用守衛_計劃]]"
pitfall_when:
  - "content:HOOK_ENTRIES"
  - "content:_install_hooks_py"
tags:
  - type/issue
  - status/done
summary: |-
  FLAG:ORIGIN
  KEY:現場事故——code-loop-guard.py 被工具鏈更新刪除(落實 2026-07-06 ADR 撤 Stop nag),但 ~/.claude/settings.json 的 Stop 註冊沒清 → 每回合報「檔案不存在」(無害但吵);使用者手動擦屁股
  KEY:root cause=merge-claude-settings「冪等只加不減」設計無移除路徑——hook 生命週期只有安裝端,卸載端(刪腳本)與註冊端(settings)不對稱;ADR commit 當時已自知此債(「既有機器需手動移除」),債如期咬人
  KEY:二次教訓(誠實)=清理前的 settings 殘留檢查回報「無」是假陰性(檢查方寫的 python 遍歷可能沒對齊實際巢狀結構)→ 檢查通過≠真乾淨,結構性修法(自動 prune)優於一次性檢查
  DECISION:[2026-07-07] 修=merge-claude-settings 加 _prune_dangling:merge 前剪掉「command 含 .claude/hooks/ 且腳本檔不存在」的註冊(懸空只會報錯,剪除普遍安全);使用者自訂(指向他處)不碰;[test:t_merge_settings_prunes_dangling]
  KEY:通則=凡「A 端刪除、B 端引用」的成對資源(腳本↔註冊/檔案↔複製清單),守衛要嘛做成對稱操作、要嘛在 B 端做懸空自癒;同型前例=C1/T12(註冊了沒複製)的鏡像(複製了沒註冊→刪了沒解註冊)
---
# hook 卸載殘留註冊(現場事故)

## 現象
2026-07-06 ADR 撤除 code-loop-guard Stop nag → 2026-07-07 工具鏈更新刪了 `~/.claude/hooks/code-loop-guard.py`,但 `~/.claude/settings.json` 的 Stop 註冊沒清 → 另一 session 每回合結束報一次「檔案不存在」(non-blocking 但吵)。使用者手動移除該筆註冊解決;code-loop 把關不受影響(活在 pre-push,ADR 設計意圖)。

## Root cause(兩層)
1. **機制層**:`merge-claude-settings.py` 的「冪等只加不減」沒有移除路徑——hook 生命週期不對稱:安裝有機械(copy+register),卸載只刪了腳本、沒解註冊。ADR commit 註記當時已自知(「既有機器需手動移除」),known debt 如期咬人。
2. **操作層(誠實)**:刪檔前跑過 settings 殘留檢查、回報「無」——**假陰性**(遍歷寫法未對齊實際結構的可能性最大)。教訓:一次性檢查通過 ≠ 真乾淨;結構性自癒 > 儀式性檢查。

## 修法
`_prune_dangling(settings)`:merge 前剪掉「command 含 `.claude/hooks/` 且 `HOOKS_DIR/<script>` 不存在」的註冊(懸空註冊唯一的作用是報錯,剪除普遍安全);**使用者自訂 hook(command 指向他處)一律不碰**。`_install_hooks_py` 每次 init/update 都跑 merge → 任何機器下次 update 自動自癒,不再手動。綁 `[test:t_merge_settings_prunes_dangling]`(懸空剪/有效留/自訂不碰)。

## 通則(pitfall_when 的存在理由)
凡「A 端刪除、B 端引用」的成對資源——腳本↔settings 註冊、hook 檔↔複製清單——守衛要嘛做**對稱操作**(刪必解註冊),要嘛在 B 端做**懸空自癒**(引用失效自動剪)。同型事故族譜:C1/T12「註冊了沒複製」(silent no-op)↔ 本次「刪了沒解註冊」(noisy error)——同一面鏡子的兩面。
