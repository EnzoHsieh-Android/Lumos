---
type: verification
status: pass
feature: nested-agent-permission-scope
commit: 19ced27
date: 2026-06-23
valid_under:
  - "design-loop 走 opus auditor/judge + canary 偷植,連 2 輪 caught 且無 blocker/major 才算收斂"
  - "orchestrator-prompt.md 尚未實作改動(本驗證是對 spec 的審計收斂,非對 running code)"
revalidate_when:
  - "orchestrator-prompt.md §2 round sub-steps 3/4 實作後(改 claude -p 子程序)——需補對 running loop 的 smoke test 驗證"
  - "claude CLI 的 --allowedTools / --permission-mode dontAsk / --model 旗標語義變更"
tags:
  - type/verification
  - status/pass
---
# Verification: nested-agent-permission-scope(design-loop 收斂)

對 `docs/design/2026-06-23-nested-agent-permission-scope.md` 的審計收斂驗證(commit `19ced27`)。**驗的是 spec 品質,非 running code**——orchestrator-prompt.md 尚未實作。

## design-loop 收斂(opus,5 輪)
| 輪 | canary type | 結果 | severity | 折入真 finding |
|---|---|---|---|---|
| R1 | a 壞§ref | CAUGHT | blocker | B1 $SCRATCH 未 export / B2 父 allowedTools 不傳播 + M1/M3/M4 |
| R2 | b 未定義旗標 | CAUGHT | major | M1 `--input-file` 旗標不存在(移除)+ m1 |
| R3 | c 未定義常數 | **MISSED** | major | 不採信收斂;仍折 F1 cwd/Grep 搜索根未指定 + m1/m2 |
| R4 | a 壞§ref | CAUGHT | minor | m1 cwd 機制在架構命令區塊補編碼 |
| R5 | b 未定義旗標 | CAUGHT | minor | m1/m2(已標 known limitation)→ **CONVERGED(R4+R5 連 2 輪 caught+minor)** |

## 核心機制實證(R2)
auditor 子程序實際執行 `claude -p ... --allowedTools "Read,Grep,Glob" --permission-mode dontAsk` 並嘗試 Write 工具 → **被拒絕、`/tmp/canary-write-test.txt` 不存在**。harness 層機械強制核心(--allowedTools + dontAsk 阻斷 Write)實證有效。

## 跨家族複核(qwen3-max via cross_audit)
qwen 真審(SSL 修後)回 worst=blocker、提兩 finding,經人代下輪 opus 逐條 grep 反證 **全為 false positive、駁回、verdict 應為 endorsed**:
- 「blocker:cwd 修復依賴 spec 自身被採納」→ 駁回:spec L122 已編碼 `(cd "<REPO>" && claude -p …)`;「spec 未實作」是所有未 merge spec 的本質,非缺陷。
- 「major:`__SCRATCH__` orchestrator 取不到」→ 駁回:spec 已明確 `__SCRATCH__` 是 autonomous-loop.sh:L35 sed 替換 token(展開為字面絕對路徑),非 `$__SCRATCH__` env 引用。

意義:cross-family-audit 首次真審即 false positive,印證「qwen 也是 AI、會誤判」+ 設計 `disputed → opus 驗證` 步驟的必要。

## 未驗(待實作後補)
- running loop smoke test:`auditor-r1.json` 存在、`.result` 取出非空、`.delegation-log.jsonl` 每輪 auditor+judge 各一行 tools=`"Read,Grep,Glob"`——orchestrator-prompt 改動實作後才能驗。
