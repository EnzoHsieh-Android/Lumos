---
type: system
status: done
created: 2026-07-10
updated: 2026-07-24
self_audit: sonnet/2026-07-24
tags:
  - type/system
  - status/done
summary: |-
  FLOW:git log(no-merges,quotePath=off,--diff時挖到range左端)→transaction過濾(>20檔tangled排除+exclude glob雙試)→pair計數→conf(A⇒B)=shared/freq(A)→rules列表/check對變更集警告漏改
  KEY:ROSE非對稱confidence(borrow-design,TSE 2005 error-prevention);門檻conf≥0.8/support≥3(config可覆寫,support硬底線2全域);警告型恆不擋(rc0;git失敗rc2);警告走stdout(hook 2>/dev/null只吞診斷)
  KEY:pre-commit Gate CC接線(STAGED後Gate 1前——後面每路徑顯式exit,末段=死碼;docs-only在Gate 2早退,唯此點覆蓋主場景);vendored路徑+python3→python fallback
  KEY:★DEBT★ rename-following未做(改名檔訊號重置,與ROSE/Code Maat同限,警告型假陰性成本低)｜Gate 0限縮(無vault repo不跑,hook由init裝、init必建vault)｜shallow clone靜默截斷
  DEP:[[Systems/lumos-cli-lifecycle]]
  TEST:30/30通過(2026-07-10,t_cochange,含 mutation M3 邊界殺手測試)+全套895綠+code-loop panel r1 收斂(3/3 canary caught) | VERIFY:[[Verification/2026-07-10_cochange守衛]]
related:
  - "[[Projects/cochange守衛_計劃]]"
  - "[[Systems/lumos-cli-lifecycle]]"
verified_by:
  - "[[Verification/2026-07-10_cochange守衛]]"
---
# cochange-guard（共改漏改守衛）

## 概述

解「知識同步散落」缺口的機械守衛：從 git 歷史挖「改 A 歷史上 X% 同改 B」的關聯規則，commit 時警告漏改的夥伴檔。警告型、不擋人。設計全程見 [[Projects/cochange守衛_計劃]]（3 輪 canary-護 panel 審計 + golden 凍結於 `governance/golden/cochange-guard/`）。

## CLI

- `lumos cochange rules [--all] [--repo] [--json]` — 預設輸出=check 會告警的規則集；`--all` 解除 confidence 門檻（support 硬底線 2 全域不解除）。
- `lumos cochange check [--staged|--diff <A..B>] [--repo] [--json]` — 皆缺 rc 2、同給 `--diff` 優先；`--diff A..B` 挖掘母體到 A 為止（被查 commit 不自我豁免）。
- config：`.lumos/cochange.json`（`min_support`/`min_confidence`/`max_changeset`/`exclude` 與預設合併；fail-open，提示走 stdout）。

## 實作位置

- 挖掘/命令：`scripts/lumos` 的 `_cochange_*` 函式群 + `cmd_cochange_rules`/`cmd_cochange_check`。
- hook：`scripts/hooks/pre-commit` Gate CC 段。
- 測試：`scripts/test_lumos.py` 的 `t_cochange`（30 斷言）。

## 相關模組

- [[Projects/cochange守衛_計劃]]
- [[Systems/lumos-cli-lifecycle]]
