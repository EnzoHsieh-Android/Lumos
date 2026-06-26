---
type: verification
status: pass
feature: lumos deinit 專案層反安裝指令(跨平台)
commit: 5d84629
date: 2026-06-26
valid_under:
  - "scripts/lumos cmd_deinit 現行四重閘 + 五個 _deinit_* helper 結構未變"
  - "Python ≥ 3.8 stdlib(subprocess/pathlib/shutil)"
  - "測試以 t_-prefixed 函式自動發現(scripts/test_lumos.py 框架未換)"
  - "macOS(darwin)+ Windows(cmd/PowerShell/Git Bash)真機"
revalidate_when:
  - "cmd_deinit 的安全網/閘順序變更(新增 flag、改 will_delete_vault 條件)"
  - "_vault_in 三型回傳邏輯變更(影響 vault==root 鐵閘判定)"
  - "測試框架改用 pytest 或換 test profile"
  - "新平台/新終端納入支援(如 WSL、其他 Windows shell)"
tags:
  - type/verification
  - status/pass
---
# 驗證:lumos deinit 跨平台

## 變更範圍
新增 `scripts/lumos` 的 `deinit` 子指令(對稱 `init` 的專案層反安裝):`_VENDORED_TOOLKIT` 常數 + 五個 `_deinit_*` helper + `cmd_deinit` + argparse/dispatch;`README.md`/`README.en.md`/`ONBOARDING.md` 補卸載分工。8 任務 TDD,新增 ~287 行測試。

## 測試結果
| 項目 | 結果 |
|---|---|
| 全套件(macOS) | ✅ 258 passed, 0 failed |
| `t_deinit_*` 各案例(完整 deinit / --keep-graph / --dry-run no-op / 冪等 / 白名單保留使用者檔 / CLAUDE 剝+退化 no-op / 來源自我保護 rc2 / 非互動防呆 rc2 / vault==root 鐵閘 / 拆閘後 commit 不被擋) | ✅ 全綠 |
| 互動 y/n 確認(expect 驅真 tty) | ✅ y→刪、n→保留(rc1) |
| Windows 真機(cmd/PowerShell/Git Bash) | ✅ 驗過;補 EOFError 硬化(isatty 回 True 但 stdin EOF → 拒刪 rc2) |

## 不可逆操作的安全證明
`shutil.rmtree(vault)` 被四重閘擋(任一即不刪):`--dry-run` 提早 return、`--keep-graph`、`vault==root` 鐵閘強制 keep、非互動無 `--yes` → rc2。pre-flight 守衛全在第一個 mutation 之前求值。opus 最終全分支審查逐閘以 diff 行號核過。

## 測試方式
`python3 scripts/test_lumos.py`(homemade check() 框架,hermetic:temp root + git init + temp HOME)。Windows 端 fetch 驗證分支後同指令跑,互動路徑用 expect 驅真 tty。

## 品質關卡
brainstorming → design-loop(5 輪 canary 對抗審計收斂,揪出真 blocker `vault==root`)→ subagent-driven 8 任務(每任務雙審 + 1 Important 修)→ opus 最終審查(1 Important 修:案例10 補警示斷言)。

## 相關模組
- [[Systems/lumos-deinit]]
