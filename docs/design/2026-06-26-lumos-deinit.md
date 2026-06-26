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
| `--dry-run` | 只印「會動到什麼」,不實際改動(預演)。**唯讀,完全不觸發確認機制**(§4 第 1 條的互動確認與非互動中止皆豁免);CI 非 tty 下無需 `--yes` 即可預演 |
| `-y` / `--yes` | 跳過互動確認(CI / 非互動環境用) |
| `--source <path>` | 指定 Lumos 來源(預設 `_lumos_src()`),**僅供 §4 第 3 條 `root == _lumos_src()` 自我保護比對用**;vendored 白名單是 hardcoded 常數(見 §5),不隨 source 變動 |

行為細節:
- **冪等**:找不到 vault 且無 vendored 工具組 → 印 `✓ 未安裝(此 repo 無 Lumos 專案層)` 並 `return 0`(措辭仿 `cmd_uninstall:3030` 的空狀態**語氣**,非逐字)。
- **root 與 slug 偵測**:`root` 走 `git rev-parse --show-toplevel`(同 `cmd_init:3255-3260`,獨立輸入);再用 `_vault_in(root)` 找實際 vault 路徑(輸出),不假設名稱、**不從 vault 反推 root**(勿學 `cmd_update:3097` 的 `vault.parent.parent`,該寫法在 standalone vault 會推錯)。找不到 vault 時 `--keep-graph` 為 no-op。
- **不自動 commit**:只改 working tree + git config,留可審閱工作區給使用者(`git diff` 可看)。**已 tracked 的刪檔可 `git restore` 救回;untracked 檔(未 commit 的新筆記)刪了救不回**——正是 §4 第 1 條印清單要警示的對象。

## 3. 執行順序(設計保證:不被 pre-commit 擋)

pre-commit 閘由 `core.hooksPath → scripts/hooks/` 驅動,而這兩者正是 deinit 要移除的東西。固定順序保證後續 commit 不被擋:

1. **先拆閘** — `git config --unset core.hooksPath`(立即生效)+ 稍後移除 `scripts/hooks/`(雙保險:就算 config 未拆淨,hook 腳本不在 = git 找不到 = 不執行)。`--unset` 採 **best-effort**:對不存在的 key git 回 rc 5(= 本來就沒設 = 拆閘目標已達成),視為成功不中止;真正的保險是「缺 hook 檔 git 直接放行不報錯」這條 git 語義(實機驗證:`core.hooksPath` 指向已刪目錄時 commit 仍 rc 0)。
2. 移除 `CLAUDE.md` 的 graph-discipline 區塊。
3. 移除圖譜 vault(走 §4 安全網)。**`--keep-graph` 時整個 step 3 跳過**(連 §4 第 1 條三道關卡都不進)。
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
3. **來源 repo 自我保護**:若 `root == _lumos_src()`(站在 Lumos 來源本身),**拒絕執行 + 印 stderr + `return 2`**,否則會把 Lumos 工具組自己刪了。對齊的是 **`cmd_update` 的 root==src 模式**(`scripts/lumos:3099-3101`:`print("ERROR…", file=sys.stderr); return 2`),**不是 `cmd_init`** —— cmd_init 的 root==src 只跳過 vendor/hooks、仍繼續 scaffold 且 rc 0(`scripts/lumos:3273-3274`),語義相反,deinit 套它會變成「在來源 repo 只跳部分動作、仍刪別的」,正好違反本條安全網。
4. **拆閘優先**:見 §3 step 1。

## 5. 實作落點

- 新增 `cmd_deinit(keep_graph=False, dry_run=False, yes=False, source=None)`,置於 `cmd_uninstall`(`scripts/lumos:3005`)附近。
- 抽出共用白名單:目前 `_vendor_toolchain` 內聯了 toolkit 清單(`scripts/lumos:3064-3069`),deinit 需同一份。抽成模組級常數(**示意命名** `_VENDORED_TOOLKIT`,實作時新建,型態同 `_SKILLS:3107` 的 `tuple/list[str]` 範式)或 helper,`_vendor_toolchain` 與 `cmd_deinit` 共用,避免漂移。
- argparse:`sub.add_parser("deinit", ...)` + 上述 flags;`main()` 在 vault-free 早處理區(同 `install/uninstall/update/bootstrap`,`scripts/lumos:3481` 一帶)分派,deinit 不需 vault Env。

## 6. 測試(TDD)

沿用 `scripts/test_lumos.py` 的 hermetic 模式(`t_install_hooks_py`,`scripts/test_lumos.py:110` 為模板):temp root + `git init` + temp HOME。

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

## 8. 審計修正紀錄(design-loop)

> 註:本紀錄提到的 §N 是當輪審計時的編號;canary 為刻意植入後已移除,真檔不含。引用 §4 第 N 條一律指 §4 編號清單的第 N 項(本 spec 無 `### 4.N` 子標題)。

- **r1**(canary type a:植入 §9 壞引用,caught):存活真 finding 與折入:
  - **F2 [major]**:§4 第 3 條原寫「對齊 `cmd_init` 的 root==src skip」誤導——cmd_init root==src 仍 scaffold 且 rc 0(語義相反),已改為對齊 `cmd_update:3099-3101` 的拒絕+`return 2`。
  - **F4→minor**(辯方降:root 走 git toplevel 非 vault 反推):§2 補明 root 來源 + 勿學 `cmd_update:3097` 的 `vault.parent.parent`。
  - **F5→minor**(辯方降:git 缺 hook 檔放行、unset rc5 無害):§3 step 1 補 best-effort 說明。
  - **F3→minor**(辯方降:`_VENDORED_TOOLKIT` 是示意命名、有 `_SKILLS` 先例):§5 標明示意命名。
  - **F6/F7/F8 [minor]**:§2 dry-run 豁免非互動中止、冪等措辭標「語氣非逐字」、§6 測試行號修正。
- **r2**(canary type b:植入未定義旗標 `--keep-claude`,caught):存活全 minor,已折入:
  - **F2→minor**(辯方降 major→minor:`§N.M` 在編號清單無歧義):§2 的 `§4.1` 等改寫為「§4 第 N 條」。
  - **F4→clean**(辯方駁回 major:deinit 直接用 `_vault_in` 回傳路徑刪、不需 slug;standalone 案例已被 §4 第 3 條 `root==src` 守衛攔截;白名單與 vault 型別/slug 解耦):不折,僅留紀錄。
  - **F5 [minor]**:§2 `--source` 改述為「僅供自我保護比對」,白名單為 hardcoded 常數。
  - **F6 [minor]**:§2 `--dry-run` 明定完全不觸發確認機制。
  - **F7 [minor]**:§3 step 3 補「`--keep-graph` 時整步跳過」。
  - **F8 [minor]**:§2 `git restore` 改述為「tracked 可救、untracked 不可救」。
