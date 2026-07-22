---
type: project
status: doing
created: 2026-07-22
updated: 2026-07-22
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/code-loop必用守衛_計劃]]"
  - "[[Systems/lumos-cli-lifecycle]]"
summary: |-
  FLAG:DECISION
  KEY:問題=只有全域裝 lumos(無 lumos 專案)的機器,沒有任何一條指令能自我清全域 settings/hooks——`install --force`(全域,不需專案)只 symlink CLI+skills,不碰 ~/.claude/settings.json/hooks;`update`(會 copy 全域 hooks+跑 merge-claude-settings 清懸空)卻綁專案 vault(find_vault 失敗即 rc2)。實例:另一台舊版 machine pull 最新後全域 Stop 註冊仍舊(code-loop-guard nag 2026-07-06 已撤但註冊沒清),彈訊息
  KEY:根因=分工沒接好——全域成品(~/.claude/settings.json 是 merge 產物、hooks/*.py 是 copy)pull 不碰,要跑安裝器;而全域安裝器 cmd_install 偏偏不做這步(只做 symlink)。symlink 類(skills/CLI)pull 即活,copy/merge 類要重跑安裝——後者在 install 缺席
  KEY:修法=cmd_install 尾端加「全域 hooks/settings 同步」——抽 `_sync_global_claude(src_repo)`:①copy src/scripts/hooks/claude/*.py → ~/.claude/hooks/ ②跑 src/scripts/merge-claude-settings.py(_prune_dangling 自動剪懸空 code-loop-guard Stop 註冊)。`_install_hooks_py(root)`(update 用,綁專案)的 ②③改委派同一函式(來源=root 的 vendored copy),消雙寫。install 用來源 repo 自身(__file__ 上溯)當 src
  KEY:★風險面★machine-global 設定寫入(~/.claude/settings.json 是使用者全域 config,2026-07-07 事故正是此檔被弄壞)——但本改動只「多呼叫既有且已測的 _prune_dangling/copy」,不新增寫邏輯;_prune_dangling 只剪指向不存在 .py 的懸空註冊、不碰使用者自訂(指他處的 command)。blast radius=每台跑 install 的機器,故 TDD 重測「settings 既有內容保留/冪等/不誤剪使用者 hook」
  KEY:懸空 vs 真檔——舊機 ~/.claude/hooks/code-loop-guard.py 若真檔還在,_prune_dangling 不剪(非懸空);install 的 hooks copy 清單(check-graph-sync/verification-rot-check/impact-hook)不含 code-loop-guard→不會覆寫或刪它。**須加:install 主動刪除已撤除的 code-loop-guard.py 舊檔**(對稱 2026-07-06 撤除,否則真檔在→_prune 不剪→nag 不停)。刪後註冊變懸空→merge 清掉,一條龍
  DECISION:分工=install 擁全域(hooks copy+settings merge+撤除檔清理)、update 擁專案 vendor+委派同一全域同步函式;不重疊
  TEST:t_install_syncs_global_hooks(copy 三 hook+跑 merge)/t_install_prunes_stale_stop(植假 code-loop-guard Stop 註冊+真檔→install 後檔刪+註冊剪)/settings 既有內容(使用者自訂 hook)保留/冪等(跑兩次同結果)/update 委派同函式不迴歸
  DEP:scripts/lumos cmd_install/_install_hooks_py/merge-claude-settings.py
  PRIOR-ART:①最小解=抽既有 ②③ 成函式+install 呼叫,零新機制;撤除檔清理對稱 2026-07-06 ADR ②世界解=無需外求(內部分工重構) ③裁定=borrow-design(既有 _prune_dangling/copy 復用)
---
# install全域hook同步_計劃

> **狀態**：設計完成，TDD 待實作。緣起：另一台只全域裝 lumos 的機器 pull 最新後，全域 Stop hook 舊註冊（code-loop-guard nag，2026-07-06 已撤）仍在彈訊息——查明 `install` 不碰全域 settings、`update` 綁專案 vault 跑不了，全域機器無自癒路徑。

## 問題

lumos 兩類更新方式：**symlink 類**（skills/CLI，`git pull` 即活）vs **copy/merge 類**（`~/.claude/settings.json` 是 merge 產物、`~/.claude/hooks/*.py` 是 copy）——後者要**跑安裝器**才更新，pull 不碰。但：
- `cmd_install`（`install.sh`，全域、不需專案）：只 symlink CLI＋`_install_skills`——**不碰全域 settings/hooks**。
- `cmd_update`：`_vendor_toolchain`→`_install_hooks_py` 有做全域 hooks copy＋跑 merge-claude-settings（`_prune_dangling` 清懸空）——**但 `cmd_update` 需 `find_vault`，無 lumos 專案即 rc2**。

→ 只全域用 lumos 的機器：`update` 沒地方跑、`install` 不管全域設定＝**無指令能自我清全域舊註冊**。

## 修法

### 抽 `_sync_global_claude(src_repo: Path)`（全域同步，不需專案）
1. **copy 全域 hooks**：`src_repo/scripts/hooks/claude/{check-graph-sync,verification-rot-check,impact-hook}.py` → `~/.claude/hooks/`。
2. **撤除檔清理（新，對稱 2026-07-06 ADR）**：`rm -f ~/.claude/hooks/code-loop-guard.py`——已撤除的舊 Stop nag 真檔若殘留，主動刪（否則 `_prune_dangling` 因它「非懸空」不剪、nag 不停）。以「已撤除 hook 清單」常數維護。
3. **跑 merge**：`src_repo/scripts/merge-claude-settings.py`——步驟 2 刪檔後，該註冊變懸空 → `_prune_dangling` 剪掉。一條龍。

### 接線
- `cmd_install`：尾端（`_install_skills` 後）呼叫 `_sync_global_claude(<repo of __file__>)`（`Path(__file__).resolve().parent.parent`）。
- `_install_hooks_py(root)`：② ③ 改委派 `_sync_global_claude(root)`（來源＝專案 vendored copy），消雙寫；① core.hooksPath 仍專案本地保留。

## 明確不做（範圍刀）
- 不動 `_prune_dangling` 本體（既有且已測 `t_merge_settings_prunes_dangling`）。
- 不動 symlink 類（skills/CLI）安裝路徑。
- 不做全域 settings 的內容改寫（只 prune 懸空＋merge 註冊我方三 hook，沿現行 merge 語意）。
- 不碰使用者自訂 hook（`_prune_dangling` 只剪指向 `~/.claude/hooks/` 下不存在 .py 的項）。

## 測試策略
1. `t_install_syncs_global_hooks`：假 HOME＋repo src → `install` 後 `~/.claude/hooks/` 有三 hook、`~/.claude/settings.json` 註冊我方 hook。
2. `t_install_prunes_stale_codeloop`：假 HOME 植「`code-loop-guard.py` 真檔＋Stop 註冊」→ `install` 後**檔被刪 ∧ 註冊被剪**。
3. `settings 保留`：植使用者自訂 Stop hook（指他處）→ install 後仍在（不誤剪）。
4. `冪等`：install 跑兩次，settings/hooks 結果一致。
5. `update 委派不迴歸`：既有 `t_install_hooks_py`/`t_merge_settings_*` 全綠（委派後行為不變）。

## 實務隱患
- **machine-global 寫入 blast radius**：`~/.claude/settings.json` 是使用者全域 config，改壞會影響該機所有 Claude Code 專案（2026-07-07 事故前例）。緩解＝只復用既有已測 `_prune_dangling`＋merge、TDD 重測「既有內容保留/冪等/不誤剪」、假 HOME 隔離測試。
- **假 HOME 測試**：測試須 `env HOME=<tmp>` 隔離，**嚴禁碰真 `~/.claude/settings.json`**（跑測試的開發機自己會被改）。既有 install 測試的假 HOME 慣例沿用。
- **撤除清單維護**：「已撤除 hook 主動刪」清單（現只 code-loop-guard）未來撤別的 hook 要補——與 merge-claude-settings 的移除註解對稱，漂移風險記。
