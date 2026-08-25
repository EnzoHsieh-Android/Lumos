---
type: verification
status: pass
date: 2026-08-04
valid_under: scripts/lumos 單檔架構;canary-log JSONL schema v8+六選配欄;python3 stdlib;quote-check 引句樣式=「引句：「…」」
revalidate_when: canary-log schema 改版;_quote_norm 正規化規則變更;disposal 閘合取增減;skill 派工模板引句樣式改
plan_refs:
  - "[[Projects/design-loop重設計_實作計畫]]"
  - "[[Projects/design-loop重設計]]"
tags:
  - type/verification
  - status/pass
summary: |-
  TEST:六包中 T1-T7 全數落地(T8 收尾=本節點+終審)。新測試 5 支:t_canary_record_disposal_fields_optional(10 斷言)/t_quote_check_normalization_and_verdict(6)/t_disposal_snapshot_provenance(3,反循環合約)/t_loop_status_disposal_gate(10)/t_disposal_loop_requires_provenance+t_loop_next_disposal_cmd_actually_runs+t_calibration_smoke。每支:紅→綠→還原翻紅釘實測+現場成立前置
  VERIFY:相容鐵則逐包驗訖——零新參舊呼叫 rc0 無新鍵、舊 panel 閘同帳輸出不變、未定錨 loop 不受收緊影響;d4 落地實證=missed 席在場 disposal 閘照樣 rc0;反循環實證=同一報告對現檔 rc0(假 ok)對凍結快照 rc1;讀側重驗實證=record 完竄改報告→FAIL
  KEY:過程抓到的新假綠變體 2 例:①T1 翻紅釘假紅(斷言重疊:目標檢查被拔後鄰近檢查代打 rc2)②T4 測試被 T6 新規則正確咬到(定錨後每席須留痕)——皆已修並留痕
  KEY:T2 附帶觸發漂移守衛(六份文件「53 個頂層命令」→54);中途 Xcode license 失效使 git 全掛(124 假紅),恢復後全綠——★環境紅與代碼紅的區分靠「紅的形狀」(越跑越多且全在 git 依賴測試)★
decision_refs_ai:
  - "Projects/design-loop重設計.md#d3"
---
# design-loop 重設計落地 T1–T7（驗證紀錄）

**spec**：[[Projects/design-loop重設計]]（r1 panel 自審收斂＋人裁放行）
**計畫**：[[Projects/design-loop重設計_實作計畫]]（逐包進度與教訓記於該節點〈進度〉）

## 交付與驗證對照

| 包 | 交付 | 關鍵驗證（全部實跑） |
|---|---|---|
| T1 | record 六選配欄＋集合核對 | 零新參舊呼叫不變；聯集／互斥／blocker 線／理由逐 id rc2；翻紅釘（修過一次假紅） |
| T2 | `quote-check`＋`_quote_norm` | 粗體／反引號／跨行正規化 ok；編造 miss；零引句 rc2；單一實作機械代理 |
| T3 | 凍結快照反循環合約 | ★對現檔假 ok 先證明、對快照必 miss 後釘死★ |
| T4 | `--disposal` 四條合取閘 | missed 席在場照樣收斂（d4）；舊閘不動；竄改→FAIL；跨席 blocker 輪級重算 |
| T5 | `loop next` disposal 模板＋skill 三檔 | 模板真跑 oracle rc0；gate 模板 rc∈{0,1} |
| T6 | 定錨後留痕強制 | 缺 report rc2；未定錨自由；翻紅釘 |
| T7 | 離線校準腳本 | 冒煙 caught/mentioned/missed 三態；「不進任何 gate」聲明 |

全套 test_lumos.py：**2262 預期全綠**（T7 完成後最終回歸，數字以 commit 訊息為準）。

## 誠實天花板（沿 spec，未因落地抬高）

「錨得住的廢話」中間態仍在（形式閘天花板）；處置帳 folded/accepted 仍編排者自報（集合核對買摩擦非防竄改）；隨機植入的隨機性不可稽核；離線校準是寬判訊號需人抽驗。
