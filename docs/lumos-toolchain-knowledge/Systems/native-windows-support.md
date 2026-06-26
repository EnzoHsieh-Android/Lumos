---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
tags:
  - type/system
  - area/onboarding
  - area/cross-platform
verified_by:
  - "[[Verification/2026-06-26_native-windows-support_真機]]"
summary: |-
  FLOW:get.ps1(薄遠端入口)→clone repo→python lumos install --force→cmd_install[全域 lumos.cmd shim + _install_skills(junction)]→重啟 session→cd 專案→lumos init→_vendor_toolchain→_scaffold_project(6 夾)+_install_hooks_py(hooksPath+複製 Claude hooks+merge-settings)
  KEY:單一真相源=三支 bash 安裝器(install.sh/install-graph-toolchain.sh/install-hooks.sh)邏輯收進 python CLI 純函式;bash 安裝器瘦成薄殼、get.sh/get.ps1 只是遠端薄入口
  KEY:零權限連結—skills 用 Windows junction(mklink /J,不需管理員)、全域 lumos 用 lumos.cmd shim;os.symlink 需權限故不用;任一失敗 fallback shutil.copytree(失即時更新)
  KEY:git hooks 維持 bash(Git for Windows 自帶 bash 跑),只補 python3→python fallback;不重寫成 python(YAGNI)[test:t_hooks_python_fallback]
  KEY:Claude hooks(L1/L3)不過 bash—由 Claude Code 直呼,Windows 用 Git Bash 跑;merge-claude-settings 寫解析後直呼 "<resolved-python>" "<home>/.claude/hooks/x.py",python 路徑與 home 全正斜線化(W6)、home 用絕對路徑(W3)
  KEY:無 Windows CI—真 Windows 行為靠手動驗證清單(本機 macOS 只測得到 python 邏輯+Unix 分支),此為本設計最大誠實天花板
  DEP:scripts/lumos cmd_install/_install_skills/_scaffold_project/_install_hooks_py/_link_or_copy｜scripts/merge-claude-settings.py(_hook_cmd/_equivalent 按路徑去重)｜get.ps1｜get.sh
  TEST:單元 200 全綠(macOS,含 t_scaffold_project/t_install_hooks_py/t_install_includes_skills/t_hooks_python_fallback);真 Windows 七步手動閘全閉合(L1/L3 真機觸發坐實)
  VERIFY:[[Verification/2026-06-26_native-windows-support_真機]]
decisions:
  - content: "核心策略 S2:安裝邏輯搬進跨平台 python CLI(單一真相源),Windows 經 get.ps1 薄入口進來;bash 安裝器瘦成薄殼/收斂(A)"
    context: lumos CLI 核心已是純 python 標準庫、Windows 原生可跑,卡 Windows 的只有 bash 安裝器 + Unix symlink
    why_chosen: 否決 S1(PowerShell 全套移植=Unix+Win 兩份漂移)與 S3(要求 Git Bash=非純原生);A 完全收斂避免 bash 孤兒 rot,python 成唯一安裝邏輯源
    decided: 2026-06-26
    valid: true
  - content: skills 用 Windows junction(mklink /J)、全域 lumos 用 lumos.cmd shim、任一失敗 fallback 複製;個別 .py(Claude hooks)一律 shutil.copy2 不用 junction
    context: os.symlink 在 Windows 需管理員/開發者模式權限;junction 零權限且是真連結(保「git pull 即更新」);但 mklink /J 只能連目錄,對個別檔必失敗(design-loop r3-F1)
    why_chosen: 零權限是 Windows 安裝可用性的硬需求;真連結保即時更新;fallback 觸發是「mklink 回非 0」非跨碟判斷(junction 可跨碟,r1-F5)
    decided: 2026-06-26
    valid: true
  - content: "Claude hooks 註冊改寫解析後直呼且 python 路徑/home 全正斜線化:command = \"<resolved-python>\" \"<絕對 home>/.claude/hooks/x.py\";按 hook 路徑去重遷移"
    context: 真機揭露三連坑—Claude Code 在 Windows 用 Git Bash 跑 hook(W6:反斜線 C:\\Users 被吃成 C:Users)、${HOME} 只 POSIX 展開(W3:native Windows 不展開→字面路徑→L1/L3 靜默不觸發)、command 格式變了 _equivalent 字串比對失效會雙重註冊(r3-F2)
    why_chosen: shebang #!/usr/bin/env python3 Windows 不認;只 resolve 直譯器不夠,還要 resolve home 且正斜線化(Git Bash 才認);按 hook 檔名去重才能升級時取代舊 entry、不雙觸發
    decided: 2026-06-26
    valid: true
---
# 原生 Windows 支援

讓 lumos 在**原生 Windows(PowerShell,不開 bash)** 也能裝、能用。手段是把原本 bash-only 的安裝邏輯**收斂進跨平台的 python CLI**(單一真相源),Windows 經 `get.ps1` 薄入口進來,Unix symlink 模型換成**零權限**的 junction(skills)+ `lumos.cmd` shim(全域 lumos)。

源起:**未尋得**(grep 2026-06-24~26 governance 日報的 gaps/inspirations 均無 windows/install/onboarding/跨平台 對應項;此功能是可移植性/onboarding 工程決策,非日報研究 gap 觸發)。

## 解決什麼

- `lumos` CLI 核心本就跨平台(純 python 標準庫),**卡 Windows 的只有 ① bash 安裝器 ② Unix `os.symlink`(需權限)**。
- 安裝邏輯原本散在三支 bash:`install.sh`(skills 連結)、`install-graph-toolchain.sh`(專案骨架 + CLAUDE.md 注入)、`install-hooks.sh`(hooksPath + 複製 Claude hooks + settings 註冊 + chmod)。Windows 跑不動。

## 關鍵機制

### 安裝邏輯收進 python(單一源,組件 2)
三支 bash 安裝器的邏輯搬進 `scripts/lumos` 的純 python 函式(Unix+Win 共用):
- `_install_skills()`(取代 `install.sh`):3 個 skill(`lumos-project-notes`/`lumos-core-knowledge`/`lumos-design-loop`)連結 `~/.claude/skills/lumos-*` → repo/skills。Win=junction、Unix=`os.symlink`、失敗 fallback `copytree(dirs_exist_ok=True)`。
- `cmd_install`(機器層一鍵,`@2970`):**= 全域 lumos + skills 兩件一起**(r2-F1 修:原 spec 漏接 skills 會讓 Windows skills 全空)。Win 寫 `lumos.cmd` shim 到 `%USERPROFILE%\.local\bin\`、Unix symlink;PATH 檢查用 `os.pathsep`(非寫死 `:`,r1-F7)。
- `_scaffold_project(root, slug)`(取代 `install-graph-toolchain.sh` 主體):建 **6 資料夾**(`Systems/Verification/Projects/Issues/Sessions/MOC`,r2-F3 補 Sessions——既有 `_INIT_SUBDIRS` 漏 Sessions 的 bug 一併修)+ `MOC/index.md` + `.gitignore` + 注入 CLAUDE.md graph-discipline 區塊;既有 vault 自動 skip。
- `_install_hooks_py(root)`(取代 `install-hooks.sh` 4 件事):① `git config core.hooksPath scripts/hooks` ② **複製 Claude hooks(`check-graph-sync.py`/`verification-rot-check.py`)到 `~/.claude/hooks/`**(r1-F2:漏此步 L1/L3 不啟用)③ `merge-claude-settings.py` 註冊 ④ chmod(Unix)。
- `_vendor_toolchain`:`bash install-graph-toolchain.sh` 換成 `_scaffold_project` + `_install_hooks_py`(純 python、跨平台)。

### 零權限連結(組件 1+helper)
`_link_or_copy(src, dst)`(`@3259`):Win `mklink /J`(目錄 junction,**不需管理員/開發者模式**,且是真連結保「git pull 即更新」),失敗才 fallback `copytree`。**個別 `.py` 檔(Claude hooks)一律 `shutil.copy2`**——junction 只連目錄、對個別檔必失敗。

### 兩類 hook 的 python 解析(組件 3,各自不同解法)
- **git hooks**(`post-commit`/`pre-push`,bash,git 呼叫):`PY="$(command -v python3 || command -v python)"`,git-for-win 自帶 bash 跑,fallback 有效。
- **Claude hooks**(L1/L3,**Claude Code 直呼、不過自家 python**):`merge-claude-settings.py` 的 `_hook_cmd` 寫**解析後直呼**(見 `:16-29`),Windows 上 `"<resolved-python>" "<絕對 home>/.claude/hooks/x.py"`,python 路徑與 home **全正斜線化**(Claude Code 在 Windows 用 Git Bash 跑,反斜線被吃);Unix 保留 `${HOME}`。`_equivalent` 按 **hook 腳本檔名**去重(`:64-73`),升級舊裸路徑格式時取代而非並存。

### bash 安裝器收斂(組件 4)+ 遠端入口(組件 5)
三支 bash 安裝器瘦成薄殼(`exec python … <子命令>`),內部走 python 單一源;`cmd_bootstrap`/`get.sh` 的 `bash install*.sh` 改 `python lumos install --force`。`get.ps1`(`irm …get.ps1 | iex`):clone(判斷測 `scripts\lumos` 本體 + 先建父夾)→ `python lumos install --force`。

## 關鍵決策
見 frontmatter `decisions[]`。design-loop **3 輪皆有真缺陷(major/blocker/major,從未乾淨輪)**,印證「無 Windows CI、紙審難收斂」的天花板;真正接住跨平台缺陷的是**真機**(W2-W6)。

## 已知限制(誠實天花板)
1. **無 Windows CI**:真 Windows 行為只能手動驗(本機 macOS 只測 python 邏輯 + Unix 分支)。測不到 junction/`.cmd` shim/git-for-win 跑 bash hooks/`python3`-vs-`python`。
2. **`.cmd` shim 的 PATH 要手動加**:`%USERPROFILE%\.local\bin` 預設不在 PATH(同 Unix 既有提示行為,不自動改環境變數)。
3. **junction 失敗才 fallback 複製**:觸發是「mklink 回非 0」(權限/路徑/UNC),**非跨碟判斷**(junction 可跨碟,r1-F5)。
4. **hooks 仍需 python on PATH**:pre-push 無則降級放行、post-commit 無則 bypass-log、Claude hooks 無則 L1/L3 不跑。
5. **Claude hooks 註冊靠解析直譯器 + Git Bash 路徑語義**:若 Claude Code 改變 Windows hook 呼叫約定,此處要重驗(屬手動清單)。
6. 不重寫 hooks 成 python、不上 Windows CI、不支援無 git-for-windows 的純 PS git、不處理 WSL `/mnt/c` 邊界、不做 PyPI/winget(均 YAGNI/畢業選項)。

## 相關
- 設計稿:`docs/design/2026-06-26-native-windows-support.md`(design-loop 收斂史在尾段「審計修正紀錄」r1-r3 + 真機驗收 W2-W6)。
- 實作計畫:`docs/superpowers/plans/2026-06-26-native-windows-support.md`(含真機後補的 Task 0「行尾/編碼地基」、Task 8 真機 findings 修)。
- 實作落點:`scripts/lumos`(`cmd_install`/`_install_skills`/`_scaffold_project`/`_install_hooks_py`/`_link_or_copy`)、`scripts/merge-claude-settings.py`(`_hook_cmd`/`_equivalent`)、`get.ps1`、`get.sh`。
