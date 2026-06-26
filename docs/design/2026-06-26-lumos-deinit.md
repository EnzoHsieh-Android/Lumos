---
title: lumos deinit — 專案層反安裝指令
date: 2026-06-26
status: design-approved
---

# lumos deinit — 專案層反安裝

## 1. 定位與語義

與 `lumos init`(專案層裝)對稱的**專案層卸載**。完全逆轉 `init` 在「本 repo」與「本專案圖譜」留下的東西;**不碰機器共用項**(`~/.claude/hooks/`、`~/.claude/settings.json` 註冊),那些留給機器層的 `lumos uninstall` 處理。

分工:
- `lumos uninstall` = 機器層(全域 `~/.local/bin/lumos`、user-scope skills)— 已存在。
- `lumos deinit` = 專案層(本 repo 的 hooks/工具組/CLAUDE.md 注入/圖譜)— 本 spec 新增。

### 安裝 / 反安裝對照表

| `init` 裝的(來源函式) | `deinit` 處置 |
|---|---|
| `git config core.hooksPath scripts/hooks`(`_install_hooks_py`) | ✅ `git config --unset core.hooksPath` |
| vendored 工具組:`scripts/lumos`、`scripts/test_lumos.py`、`scripts/merge-claude-settings.py`、`scripts/graph-rename.sh`、`scripts/fetch-notesmd.sh`、`scripts/hooks/`、`scripts/templates/`(`_vendor_toolchain` 的 toolkit 清單)| ✅ 逐檔/逐夾移除(白名單;只動 lumos-owned) |
| `CLAUDE.md` 的 `LUMOS:GRAPH-DISCIPLINE:START/END` 區塊(`_scaffold_project`)| ✅ 只剝這段,其餘內容原封不動 |
| `docs/<slug>-knowledge/` 圖譜(`_scaffold_project`)| ✅ **預設刪**(走 §4 安全網);`--keep-graph` 可保留 |
| `~/.claude/hooks/check-graph-sync.py`、`verification-rot-check.py`(`_install_hooks_py`)| ❌ 不動(跨專案共用) |
| `~/.claude/settings.json` hook 註冊(`merge-claude-settings.py`)| ❌ 不動(跨專案共用) |

## 2. 指令介面

```
lumos deinit [--keep-graph] [--dry-run] [-y/--yes] [--source <path>]
```

| Flag | 作用 |
|---|---|
| (無) | 完整逆轉:拆閘 + 移 vendored 工具組 + 剝 CLAUDE.md 區塊 + **刪圖譜**;互動確認 |
| `--keep-graph` | 保留 `docs/<slug>-knowledge/`,其餘照拆 |
| `--dry-run` | 只印「會動到什麼」,不實際改動(預演);與 `--yes` 互不影響 |
| `-y` / `--yes` | 跳過互動確認(CI / 非互動環境用) |
| `--source <path>` | 指定 Lumos 來源以判定 vendored 檔白名單(預設同 `_lumos_src()`) |

行為細節:
- **冪等**:找不到 vault 且無 vendored 工具組 → 印 `✓ 未安裝(此 repo 無 Lumos 專案層)` 並 `return 0`,對齊 `cmd_uninstall` 的空狀態語氣。
- **slug 偵測**:用既有 `_vault_in(root)` 找到實際 vault 路徑,不假設名稱;找不到 vault 時 `--keep-graph` 為 no-op。
- **不自動 commit**:只改 working tree + git config,留可審閱工作區給使用者(`git diff` 可看、`git restore` 可救)。

## 3. 執行順序(設計保證:不被 pre-commit 擋)

pre-commit 閘由 `core.hooksPath → scripts/hooks/` 驅動,而這兩者正是 deinit 要移除的東西。固定順序保證後續 commit 不被擋:

1. **先拆閘** — `git config --unset core.hooksPath`(立即生效)+ 稍後移除 `scripts/hooks/`(雙保險:就算 config 未拆淨,hook 腳本不在 = git 找不到 = 不執行)。
2. 移除 `CLAUDE.md` 的 graph-discipline 區塊。
3. 移除圖譜 vault(走 §4 安全網)。
4. **最後**移除其餘 vendored 工具組(含 `scripts/hooks/`、`scripts/templates/`、`scripts/lumos` 自己)。

> 把 vendored 檔移除放最後,是為了「`python3 scripts/lumos deinit` 刪到自己」的穩妥性:POSIX 上已載入記憶體的腳本被刪不影響執行,但流程其餘步驟此時都已完成。用全域 `lumos`(symlink 到來源)執行則無此顧慮。

事後 `git add -A && git commit` 時閘已不存在 → 刪光圖譜的 commit 暢通。手動路徑(自行 `git config --unset core.hooksPath` 再刪)亦同理成立;deinit 只是把它連同清理一次做好。

## 4. 安全網(防誤刪圖譜)

1. **刪圖譜前三道關卡:**
   - **印清單**:列 vault 路徑 + 檔案數,以及「其中 N 個未 commit(刪了 git 救不回)」,用 `git status --porcelain <vault>` 偵測未追蹤/已修改檔。
   - **互動確認**:預設需打 `y`;`--yes` 跳過。若偵測到未 commit 檔且非 `--yes`,確認語句特別警示。
   - **非互動防呆**:stdin 非 tty(管線/CI)又沒 `-y` → 中止並提示加 `--yes`,絕不默默刪。
2. **只動 Lumos 自己的東西:**
   - vendored 移除走**白名單**(`_vendor_toolchain` 的 toolkit 清單 + `scripts/hooks/`、`scripts/templates/` 兩夾);`scripts/` 底下使用者自有檔一律不碰。`scripts/` 空了才 `rmdir`,否則保留。
   - `CLAUDE.md` 只依 `LUMOS:GRAPH-DISCIPLINE:START/END` 標記剝該段;其餘內容、甚至整個檔(若還有別的內容)都留。若剝完僅剩 `# CLAUDE.md` 樣板殼,仍保留檔案(不臆測使用者意圖)。
3. **來源 repo 自我保護**:若 `root == _lumos_src()`(站在 Lumos 來源本身),**拒絕執行**並提示;對齊 `cmd_init` 的 `root == src` skip 邏輯,否則會把 Lumos 工具組自己刪了。
4. **拆閘優先**:見 §3 step 1。

## 5. 實作落點

- 新增 `cmd_deinit(keep_graph=False, dry_run=False, yes=False, source=None)`,置於 `cmd_uninstall`(`scripts/lumos:3005`)附近。
- 抽出共用白名單:目前 `_vendor_toolchain` 內聯了 toolkit 清單,deinit 需同一份。抽成模組級常數(如 `_VENDORED_TOOLKIT`)或 helper,`_vendor_toolchain` 與 `cmd_deinit` 共用,避免漂移。
- argparse:`sub.add_parser("deinit", ...)` + 上述 flags;`main()` 在 vault-free 早處理區(同 `install/uninstall/update/bootstrap`,`scripts/lumos:3481` 一帶)分派,deinit 不需 vault Env。

## 6. 測試(TDD)

沿用 `scripts/test_lumos.py` 的 hermetic 模式(`scripts/test_lumos.py:111` 那支 hooks 測試為模板):temp root + `git init` + temp HOME。

需覆蓋的案例:
1. **完整 deinit**:init 一個 repo → `deinit --yes` → 斷言 `core.hooksPath` 已 unset、vendored 工具組消失、`CLAUDE.md` 區塊被剝、vault 不存在。
2. **`--keep-graph`**:vault 仍在,其餘皆拆。
3. **拆閘有效**:deinit 後對「改 code 不動圖譜」做 commit 不再被擋(或更輕量:斷言 `core.hooksPath` 為空 + `scripts/hooks/` 不存在)。
4. **冪等**:對沒裝過的 repo 跑 `deinit` → return 0、印「未安裝」、無副作用。
5. **白名單**:`scripts/` 內預先放一個使用者自有檔 → deinit 後該檔仍在。
6. **CLAUDE.md 保留**:CLAUDE.md 內含使用者自有段落 + 注入區塊 → deinit 後自有段落完整、區塊消失。
7. **來源自我保護**:於 `_lumos_src()` 路徑跑 → 拒絕、return 非 0、無副作用。
8. **`--dry-run`**:印清單但檔案/config 全無改動。
9. **非互動防呆**:非 tty 無 `--yes` → 中止、return 非 0、無副作用。

## 7. 文件

- `README.md` / `README.en.md`:第 「卸載」相關段補 `lumos deinit`(專案層)與 `lumos uninstall`(機器層)的分工。
- `ONBOARDING.md`:如有卸載/退場段落,補對照。
- 對齊 [[knowledge-sync-scatter-needs-mechanical-guard]] 的提醒:同步時掃散落的列舉表/清單,別只改最相關段。
