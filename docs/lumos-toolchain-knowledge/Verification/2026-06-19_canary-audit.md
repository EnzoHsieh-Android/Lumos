---
type: verification
status: pass
feature: canary-audit
commit: 58ae539
date: 2026-06-26
valid_under:
  - "macOS,Python test_lumos.py 全綠(258 passed)"
  - "vault.parent 可寫(.canary-log.jsonl append)"
revalidate_when:
  - "cmd_gov dedup key 或 mapper 變動(尤其 token 第 5 鑑別子)"
  - "cmd_canary 寫入 schema 或 argparse 結構變動"
  - "新增第 5 個 gov 讀取來源"
tags:
  - type/verification
  - status/pass
summary: |-
  canary-audit 的 record helper + gov 第 4 源彙整,經 t_canary / t_canary_loop_fields 回歸(258 passed)+ 設計稿 4 輪 Sonnet 對抗審計收斂。
---
# Verification: canary-audit(2026-06-19)

驗證對象:[[Systems/canary-audit]] —— `lumos canary record` + `lumos gov` 第 4 源。

## 測試證據(`scripts/test_lumos.py`,258 passed / 0 failed,macOS)
`t_canary`:
- `canary record missed --auditor sonnet`(帶 `--vault`)→ rc0,`<vault.parent>/.canary-log.jsonl` 寫入該筆含自動鑄 `token` + `missed`。
- `lumos gov` 出現 `canary/missed` 列。
- 兩筆 `--token CANARY-A` / `CANARY-B` → `gov` 各自一列(`canary/caught` 計數 == 2),**不被 dedup 折成一列**(驗第 5 鑑別子 `token`)。
- `canary record bogus`(非 caught/missed)→ rc2(argparse choices)。

`t_canary_loop_fields`(後續 `--loop`/`--severity` 延伸):
- `record caught --loop L --severity major --token zz` → rc0,寫入含 `loop` + `severity`。
- `gov` 該筆 `detail` 開頭含 `loop=L` / `sev=major`。

回歸:既有測試全綠,確認 gov 加第 4 源未弄爆舊三源(`r.get("token","")` 對舊事件回 `""`,crash-free)。

## 設計收斂證據
設計稿 `docs/design/2026-06-19-canary-audit.md` 經 **4 輪 Sonnet 對抗審計**收斂(CONVERGED, implementable as-is):r1 揪 token 非機械證明(blocker)+ 純加性 canary 限制;r2 auto-mint 改 secrets(blocker)+ argparse 結構(major);r3 dedup `.get` 防 KeyError(唯一 must-fix);r4 四源 dedup crash-free 確認、無 blocker/major。
