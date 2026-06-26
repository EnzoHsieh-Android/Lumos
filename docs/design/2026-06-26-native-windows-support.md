---
type: project
status: doing
created: 2026-06-26
tags:
  - type/project
  - area/onboarding
  - area/cross-platform
summary: |-
  FLAG: 設計 spec — 原生 Windows 支援(無 bash 安裝、PowerShell + 純 python 單一源)
  KEY: 決策 = S2(安裝邏輯搬進 python CLI) + junction/.cmd shim(零權限) + hooks 維持 bash(git-for-win 跑) + A(完全收斂、刪 bash 安裝器冗餘)
  KEY: 真單一源 = install.sh/install-graph-toolchain.sh/install-hooks.sh 的邏輯收進 python;get.sh/get.ps1 只是薄遠端入口
  KEY: Windows 坑 = hooks 叫 python3(Win 常只 python)→ 補 fallback;claude hooks 由 Claude Code 直跑要 resolved-python 註冊;.cmd shim PATH 要手動加;junction 失敗才 fallback 複製(可跨碟);無 Windows CI=手動驗
---

# 原生 Windows 支援(純 python 單一源 + PowerShell 薄入口)

## 目標(一句話)

讓 lumos 在**原生 Windows(PowerShell,不開 bash)** 也能裝、能用——把現在 bash-only 的安裝邏輯**收斂進跨平台的 python CLI**(單一真相源),Windows 經 `get.ps1` 薄入口進來,symlink 模型換成**零權限**的 junction(skills)+ `.cmd` shim(全域 lumos)。

## 前提與既驗事實(grep/Read 坐實)

- **`lumos` CLI 核心是純 python 標準庫**:`scripts/lumos` 本身跨平台,Windows 原生 python 直接能跑。卡 Windows 的只有 **bash 安裝器** + **Unix symlink**。
- **安裝器全是 bash**(`#!/usr/bin/env bash`):`get.sh`/`install.sh`/`scripts/install-graph-toolchain.sh`/`scripts/install-hooks.sh`/`scripts/hooks/*`。
- **`install-hooks.sh` 做 4 件事**(r1-F2 更正,原 spec 漏第 2 件):① `[1/3]` `git config core.hooksPath scripts/hooks`(`:90`)② `[2/3]` **複製 Claude hooks(`check-graph-sync.py`/`verification-rot-check.py`)到 `~/.claude/hooks/`**(`:103-145`,`ln -s`/`cp`)③ `[3/3]` `~/.claude/settings.json` hook 註冊(`merge-claude-settings.py`,**已 python**,`:151`)④ chmod +x。→ `_install_hooks_py` **必須涵蓋第 2 件**(複製 Claude hooks),否則 L1/L3 不啟用。
- **`install.sh`**:`ln -s ~/.claude/skills/lumos-* → repo/skills`(`:40`)。
- **`_vendor_toolchain`**(`scripts/lumos:3013` 定義,bash 呼叫 `@3031`):**仍 shell 去 bash**(`subprocess.run(["bash", install-graph-toolchain.sh])`);其「結尾自癒」段已純 python(`shutil.copy2`/`filecmp` 複製 toolkit)。
- **`python3` 依賴盤點(真 Windows 坑;Windows 常只 `python` 無 `python3`)**:
  - `post-commit:81`(inline `python3` heredoc)、`pre-push:22`(`command -v python3 || true`,無則降級放行)——**過 bash,可加 `$PY` fallback**。
  - `install-graph-toolchain.sh:141`(inline `python3` heredoc,CLAUDE.md 注入)——r1-F4;但 **A 把這段邏輯收進 python(`_scaffold_project`)後此 call 消失**,薄殼須 `exec python` 不可 exec 回 `.sh`。
  - **`claude/*.py` shebang `#!/usr/bin/env python3`,由 Claude Code 直接跑(不過 bash)**——r1-F6;bash `$PY` fallback **救不到**,需另解(見組件 3)。
- **要更新的 caller**(A 刪/瘦 bash 安裝器):`_vendor_toolchain`(`@3031` bash 呼叫)、`cmd_bootstrap`(`@3103` `bash install.sh`、`@3115` `bash install-hooks.sh`)、`cmd_init`(`@3180`)、`cmd_update`(`@3061` 文檔)、toolkit 自癒清單(`@3034-3035` vendor install-hooks.sh + install-graph-toolchain.sh 進專案)、`get.sh`(install 呼叫 `@24`;`@11` 是 if 判斷,r2-F6 更正)。
- **`cmd_install(force=False)`**(`scripts/lumos:2961`):Unix symlink `~/.local/bin/lumos`;Windows 需 `.cmd` shim(無副檔名檔 Windows 不直接跑)。
- **junction 零權限**:Windows `mklink /J`(目錄 junction)不需管理員/開發者模式,且是真連結(保「git pull 即更新」)。`os.symlink` 才需權限。
- **無 Windows CI**:repo 無 `.github/workflows`,本機是 macOS——**真 Windows 行為只能手動驗**(本 spec 最大的誠實天花板)。

## 決策(brainstorm 定案)

| 軸 | 決策 | 否決 |
|---|---|---|
| 核心策略 | **S2:安裝邏輯搬進 python CLI + 薄 PS 入口** | S1(PowerShell 全套移植=兩份漂移)、S3(要求 Git Bash=非純原生) |
| symlink | **junction(skills)+ `.cmd` shim(全域 lumos),fallback 複製** | os.symlink(要權限)、純複製(失去即時更新) |
| git hooks | **維持 bash**(git-for-win 自帶 bash 跑);只 `git config core.hooksPath` 改 python | 重寫 python hooks(YAGNI、動已驗證邏輯) |
| 收斂範圍 | **A 完全收斂**:python 成唯一安裝邏輯源,bash 安裝器刪/瘦成薄殼 | C(留 bash 孤兒會 rot、離線理由假)、B(Unix+Win 兩份=漂移) |

## 邊界 / 非目標(YAGNI)

- ❌ **不重寫 hooks 成 python**:維持 bash,只補 `python3 → python` fallback(讓 git-for-win 跑得動)。
- ❌ **不上 Windows CI**:本 spec 不建 GitHub Actions Windows runner(可留後續);Windows 行為靠**手動驗證清單**。
- ❌ **不支援「無 git-for-windows 的純 PowerShell git」**:前置明寫 Git for Windows(自帶 bash 跑 hooks)。
- ❌ **不處理 `/mnt/c` 跨 WSL 邊界**:WSL 用戶照 Linux 路徑(已有);本 spec 專注**原生 Windows**。
- ❌ **不做 PyPI/winget 套件**:畢業選項。

## 架構:組件

### 組件 1:平台 helper(`scripts/lumos`)
```python
import os
_IS_WIN = os.name == "nt"
```

### 組件 2:安裝邏輯收進 python(單一源)
把三支 bash 安裝器的邏輯搬進 `scripts/lumos` 的純 python 函式(Unix+Win 共用):

- **`_install_skills()`**(取代 `install.sh`):對 **3 個 skill(`lumos-project-notes`/`lumos-core-knowledge`/`lumos-design-loop`,同 `install.sh:28` 的 `SKILLS`)** 連結 `~/.claude/skills/lumos-*` → repo/skills。Win=junction(`subprocess.run(["cmd","/c","mklink","/J",dst,src])`)、Unix=`os.symlink`、任一失敗 fallback `shutil.copytree(..., dirs_exist_ok=True)`(r2-F7:目標已存在不報錯;**前置 Python ≥ 3.8**,寫進前置)。
- **`cmd_install`**(機器層一鍵,擴充 @2961):**= 全域 lumos + skills 兩件一起做**(r2-F1 修:原 spec 只接全域、漏接 skills → get.ps1「install=全域+skills」會斷、Windows skills 全空)。① 全域 lumos:Unix symlink、Win 寫 `lumos.cmd`(`@echo off` + `python "<repo>\scripts\lumos" %*`)到 `%USERPROFILE%\.local\bin\` ② **呼叫 `_install_skills()`** ③ PATH 提示。**順修 r1-F7**:PATH 檢查 `@2982` 寫死 `.split(":")` → 改 `os.pathsep`(否則 Windows 永遠誤警告)。get.sh/get.ps1 只需 `python lumos install --force` 一條。
- **`_scaffold_project(root, slug)`**(取代 `install-graph-toolchain.sh` 主體):mkdir **6 資料夾**(`Systems/Verification/Projects/Issues/Sessions/MOC`,r2-F3:對齊 install-graph-toolchain 的 6 夾 + README;**Jenny `_INIT_SUBDIRS` 漏 Sessions 是既有 bug,一併補**)+ `MOC/index.md` + `.gitignore` + 注入/更新 CLAUDE.md `LUMOS:GRAPH-DISCIPLINE` 區塊(`scripts/templates/graph-discipline.md`)。toolkit 複製沿用既有 python 自癒。
- **`_install_hooks_py(root)`**(取代 `install-hooks.sh` 的 4 件事,r1-F2):① `git config core.hooksPath scripts/hooks`(`subprocess` git,跨平台)② **複製 Claude hooks(`check-graph-sync.py`/`verification-rot-check.py`)到 `~/.claude/hooks/`**——**個別 `.py` 檔一律用 copy(`shutil.copy2`),不用 junction**(r3-F1:`mklink /J` 只能連目錄、對個別檔必失敗;junction 只用於 skills 目錄)。Unix 維持 cp(原 install-hooks.sh `:103-145`)③ `merge-claude-settings.py` 註冊 ④ chmod +x(Unix;Win no-op)。**漏②則 L1/L3 不啟用**。
- **`_vendor_toolchain`**(改 @3018):把 `bash install-graph-toolchain.sh` 換成 `_scaffold_project` + `_install_hooks_py`(純 python、跨平台、順手修掉「python 包 bash」脆弱)。

### 組件 3:`python3` 解析的兩類 hook(各自不同解法)
hook 分兩類,Windows 上跑法不同,**不能用同一招**(r1-F6 修正原本以為都過 bash 的錯):

- **git hooks(`post-commit`/`pre-push`,bash,git 呼叫)**:把 `python3` 解析改 `PY="$(command -v python3 || command -v python)"`,後續用 `"$PY"`。git-for-win 用自帶 bash 跑,fallback 有效。
- **Claude hooks(`check-graph-sync.py`/`verification-rot-check.py`,L1/L3)**:由 **Claude Code 直接依 `~/.claude/settings.json` 註冊呼叫、不過 bash**——`#!/usr/bin/env python3` shebang **Windows 不認**。解法:command 寫成**解析後的直呼**(`<resolved-python> <hook-path>`,resolved = `shutil.which("python3") or "python"`),不靠 shebang。
- **r2-F2 實作路徑(關鍵——原 spec 沒指定)**:`merge-claude-settings.py` 的 `HOOK_ENTRIES`(`:14-32`)現在把 command **寫死**成 `${HOME}/.claude/hooks/xxx.py`(裸路徑、靠 shebang)。要達成上面的 resolved 直呼,**得改 `merge-claude-settings.py`**:把 command 從寫死常數改成**啟動時組 `f"{resolved_python} {hook_path}"`**(resolved 在該檔內 `shutil.which`)。
- **r3-F2 去重遷移(必修,否則既有機器雙重註冊)**:command 格式一變,`_equivalent()`(`:46-48`)純字串比對會把舊格式 entry 當「不同」→ 新舊**並存、L1/L3 雙觸發**。修:`_equivalent`/合併改成**按 hook 路徑(`.py` 檔名)去重**——同一支 hook 只留一筆,升級時用新格式**取代**舊 entry。⚠ 動到既有 Unix 合併邏輯——**Unix 等效 + 回歸測試**(既有 settings 重跑後同 hook 只一筆、L1/L3 正常觸發)。
- **效果**:兩類各自在 Windows 找得到直譯器;hook 檔本身不重寫;Unix 行為等效(回歸守住)。

### 組件 4:刪/瘦 bash 安裝器(A 收斂)
- **`install.sh` / `install-graph-toolchain.sh` / `install-hooks.sh`**:邏輯已進 python → **瘦成薄殼**(`exec python3 "$(dirname "$0")/scripts/lumos" <對應子命令>`)或刪除。保留薄殼較安全(舊文檔/肌肉記憶仍可用),但內部單一源。
- 更新 caller(r3-F5 明確化,避免雙裝):
  - `cmd_bootstrap`:**刪 `:3103` `bash install.sh`** 與 **`:3115` `bash install-hooks.sh`**,改 `cmd_install`(=全域+skills)+ `_install_hooks_py`;skills 只裝一次。
  - `get.sh`:**刪 `:21` `bash install.sh`**,只留 `:24` `python3 lumos install --force`(已含 skills)。
  - toolkit 自癒清單(@3034)移除 install-hooks.sh/install-graph-toolchain.sh——專案只需 vendored `scripts/lumos` + hooks/ + templates/。

### 組件 5:`get.ps1`(新,Windows 遠端入口)
```powershell
# get.ps1 — 用法:  irm https://raw.githubusercontent.com/.../get.ps1 | iex
$home_dir = if ($env:LUMOS_HOME) { $env:LUMOS_HOME } else { "$HOME\harness\lumos-toolchain" }
$url = if ($env:LUMOS_URL) { $env:LUMOS_URL } else { "https://github.com/EnzoHsieh-Android/Lumos" }
if (-not (Test-Path "$home_dir\scripts\lumos")) {   # r2-F5:測 lumos 本體非 install.sh(更可靠)
  New-Item -ItemType Directory -Force -Path (Split-Path $home_dir) | Out-Null   # 先建父夾
  git clone $url $home_dir
}
python "$home_dir\scripts\lumos" install --force           # = 全域 lumos.cmd + skills(cmd_install 兩件一起,見組件2)
Write-Host "✓ 機器層裝好。重啟 Claude Code session;進專案 cd <專案>; lumos init"
```
（r2-F5:clone 判斷改測 `scripts\lumos` 本體 + 先 `New-Item` 建父夾,避免目標夾已存在非空時 `git clone` 失敗。)
(`get.sh` 對稱瘦成 clone + `python3 lumos install --force`,讓兩入口都只 clone+叫 python。`get.sh` 真正的 install 呼叫在 `:24`(非前提誤寫的 `:11`,那是 if 判斷)。)

### 組件 6:文檔 + 測試
- README/ONBOARDING 加 **Windows 段**:前置(Git for Windows 自帶 bash + python on PATH + Claude Code)、`irm …get.ps1 | iex` + `lumos init`、PATH 提示。
- `test_lumos.py` 加跨平台測(platform-guard `if _IS_WIN`):`_scaffold_project` 建對資料夾、`_install_hooks_py` 設對 hooksPath、skills 連結建立(Unix 測 symlink、Win 測 junction—但**本機 macOS 只能測 Unix 分支 + 純邏輯**)。

## 誠實天花板

1. **無 Windows CI = 真 Windows 行為只能手動驗**(最大缺口)。本機 macOS 測得到:python 邏輯、Unix 分支、scaffold/hooksPath。測**不到**:junction、`.cmd` shim、git-for-win 跑 bash hooks、`python3`-vs-`python`。→ spec 附**手動 Windows 驗證清單**,放行前在真 Windows 跑一遍。
2. **`.cmd` shim 的 PATH 要手動加**:`%USERPROFILE%\.local\bin` 預設不在 Windows PATH;同 Unix 既有「提示加 PATH」,不自動改使用者環境變數(避免驚嚇)。
3. **junction 失敗才 fallback 複製**(r1-F5 更正:junction **可跨碟**,不能跨碟的是 hardlink)。fallback 觸發條件是「`mklink /J` 回非 0」(權限/路徑/UNC 等任何原因),**不是**跨碟判斷;失敗則複製、失去即時更新、印警告。實作勿寫「跨碟就 fallback」的錯判。
4. **hooks 仍需 `python`/`python3` on PATH**:補 fallback 後仍要有其一;pre-push 無則降級放行(CI 兜底),post-commit 無則 bypass-log 失敗(不擋 commit);Claude hooks 無則 L1/L3 不跑。Windows 前置明寫「python on PATH」。
5. **bash 薄殼仍需 bash**:Windows 上若有人直接跑 `install.sh` 薄殼仍要 bash;但主路徑(`get.ps1` + `lumos init`)純原生不碰它。
6. **Claude hooks 註冊靠解析直譯器**(r1-F6):`#!/usr/bin/env python3` Windows 不認;`settings.json` 註冊要寫 `<resolved-python> <path>`。若 Claude Code 在 Windows 改變 hook 呼叫約定,此處要重驗(屬手動清單)。

## 測試策略

`scripts/test_lumos.py`(platform-guard):
1. **`_scaffold_project`**:temp 專案 → 建 **6 資料夾**(含 Sessions)+ `MOC/index.md` + `.gitignore` + CLAUDE.md 有 `LUMOS:GRAPH-DISCIPLINE` 區塊;重跑不覆寫既有 vault(idempotent)。
2. **`_install_hooks_py`**:temp git repo → ① `core.hooksPath == scripts/hooks` ② **Claude hooks 複製到 `~/.claude/hooks/`**(r3-F6:測步驟②)③ **settings.json 重跑不雙重註冊**(r3-F2:同 hook 路徑只一筆,測去重)。
3. **`_install_skills` Unix 分支**:macOS 測 symlink 建立 + 指對。
4. **`cmd_install` Unix 分支**:symlink `~/.local/bin/lumos` + **連帶裝 skills**(r2-F1 回歸:install 後 skills 也在)。
5. **hooks python fallback**:`command -v python3 || command -v python` 解析(bash 單元;或 grep 斷言 hook 檔含 fallback 形)。
6. **merge-claude-settings 去重遷移**(r3-F2):mock 既有 settings 含舊格式 command → 跑改版 merge → 斷言**同 hook 路徑只剩一筆**(非新舊並存)。
7. **手動 Windows 驗證清單**(放行前在真 Windows 跑;每步附判準):
   1. `irm https://raw.githubusercontent.com/.../get.ps1 | iex` → 印 `✓ 機器層裝好`,無報錯。
   2. 新開 PowerShell 打 `lumos` → 找得到指令(`.cmd` shim + PATH 生效;若報「找不到」=PATH 沒加,照提示加)。
   3. `dir %USERPROFILE%\.claude\skills\lumos-project-notes` → 是 junction(`dir` 顯示 `<JUNCTION>`)、內容指對。
   4. `cd <新專案>; lumos init` → 建 `docs\<slug>-knowledge\` **6 夾(含 Sessions)** + `MOC\index.md` + `.gitignore`;`git config core.hooksPath` == `scripts/hooks`;`%USERPROFILE%\.claude\hooks\` 有 check-graph-sync.py。
   5. 故意改一個 .py 不更新圖譜 → `git commit` 被 **pre-commit 擋**(git-for-win 用自帶 bash 跑 hook;若沒擋=hook 沒生效或 python 沒 on PATH)。
   6. `lumos doctor` → 綠(新骨架乾淨)。
   7. 重啟 Claude Code session → 動 code,L1 軟提醒出現(claude hook 的 resolved-python 真跑)。
   任一步失敗即不放行,記在 spec 審計紀錄。

## 知識同步影響

| 文件 | 同步 |
|---|---|
| `README.md` + `ONBOARDING.md` | 加 Windows 段(前置 + `irm get.ps1` + lumos init);4b 補 Windows 分支 |
| `scripts/lumos` help | install/init 說明補 Windows 行為(.cmd shim/junction);無其他散落 |
| 方法論 `圖譜即合約.md` | **無**(安裝 UX、非治理機制/Check/Tag) |

## 審計修正紀錄

- **r1**(type=a, sonnet, severity=major): canary(組件 7 懸空引用)抓到。**4 個 major 經辯方查證全坐實、已折**:
  - F2:`install-hooks.sh` 實做 **4 件事**(原 spec 漏「複製 Claude hooks 到 `~/.claude/hooks/`」`:103-145`)→ `_install_hooks_py` 補此步,否則 L1/L3 不啟用。
  - F5:**junction 可跨碟**(spec「限同碟」寫錯;不能跨碟的是 hardlink)→ fallback 觸發改為「mklink 回非 0」非跨碟判斷。
  - F6:`claude/*.py` 是 `python3` shebang、**由 Claude Code 直跑不過 bash**,bash `$PY` fallback 救不到 → settings.json 註冊改寫 `<resolved-python> <path>`。
  - F7:`cmd_install:2982` PATH 檢查寫死 `.split(":")` → 改 `os.pathsep`(否則 Windows 永遠誤警告)。
  - 另折 minor:F3/F9(行號更正 3115/3180/3031/3013)、F4(`install-graph-toolchain.sh:141` python3 heredoc;A 收進 python 後消失、薄殼須 exec python)、F8(手動驗證清單具體化成 7 步附判準)。
  - **本輪 canary 抓到但真 severity=major**(全真缺陷、非假陽性)→ 不算乾淨輪;已折待 r2 再驗。
- **r2**(type=b, sonnet, severity=blocker): canary(`-SkipSkills` 未定義旗標)抓到。**又揪出 2 個真 blocker(辯方查證坐實)+ 已折**:
  - F1(blocker):`cmd_install` 不叫 `_install_skills` → Windows 機器層裝完 **skills 全空**。修:`cmd_install` = 全域 lumos + skills 兩件一起,get.ps1/get.sh 一條 `install --force` 搞定。
  - F2(blocker):`merge-claude-settings.py` 的 command 寫死裸路徑(靠 shebang)→ r1-F6 的 resolved-python 註冊**無實作路徑**。修:改 `merge-claude-settings.py` 啟動時組 `<resolved-python> <path>`(Unix 等效、要回歸)。
  - F3(major):scaffold 夾數 **5→6**(補 Sessions + `MOC/index.md`;Jenny `_INIT_SUBDIRS` 漏 Sessions 是既有 bug 一併補)。
  - minor:F5(get.ps1 clone 判斷改測 lumos 本體 + 先建父夾)、F6(get.sh install 在 :24 非 :11)、F7(copytree `dirs_exist_ok` + 前置 Python≥3.8)、F8(frontmatter KEY 殘留「junction 同碟」已更正)。
  - **canary 抓到但真 severity=blocker** → 仍不算乾淨輪;r1+r2 連兩輪都有真缺陷,**手寫 spec 的跨平台盲點被逐輪挖出**(design-loop 正發揮);已折待 r3 再驗。
- **r3**(type=c, sonnet, severity=major): canary(`_SKILL_MANIFEST` 未定義常數)抓到。又折真 findings:
  - F1(major):`mklink /J` 目錄專用,Claude `.py` 個別檔該用 `shutil.copy2`、非 junction(原設計對檔案必失敗)。
  - F2(major):改 command 格式後 `_equivalent()` 字串比對去重失效 → 既有機器**雙重註冊**;改按 hook 路徑去重、新格式取代舊。
  - F3(major):**測試策略 + 手動清單還寫「5 夾」**(r2 只改正文)——knowledge-sync-scatter 在同份 spec 內第 3 次咬;已全改 6 夾。
  - minor:F5(明確刪 cmd_bootstrap `:3103`/`:3115`、get.sh `:21` 的 bash install,避免雙裝)、F6(測試補 `_install_hooks_py` 步驟②③ + 去重)、F4(canary 吃 spec 含糊→`_install_skills` 明列 3 skill 名)。
  - **連 3 輪都有真缺陷**(major/blocker/major)。觀察:findings 逐輪變**局部/細節**(r1 整段漏+事實錯 → r3 junction-檔案、去重遷移、stale 數字),架構穩定、剩技術細節;但**仍未有乾淨輪**——印證最大誠實天花板「無 Windows CI、紙上審難收斂」。
