---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/done
summary: |-
  FLOW:機器層一次裝(bootstrap=clone Lumos源→install全域lumos+user-scope skills→repo hooks｜或單獨 install/uninstall)→專案層每repo(init 建vault+vendor工具組+裝閘｜update 刷新vendored｜deinit 對稱反安裝)
  KEY:兩層分工——機器層(install/uninstall/bootstrap)動 ~/.local/bin + ~/.claude(全域lumos、user-scope skills、Claude hooks);專案層(init/update/deinit)只動本 repo(docs/<slug>-knowledge、scripts/ vendored、CLAUDE.md 注入、core.hooksPath)
  KEY:全域 lumos 與 skills 走 symlink/junction 指向來源 clone(非 copy)→ git pull 來源即吃到 CLI+skills 更新;graph-discipline.md 是 per-project 注入,要重跑 init/update 才刷新
  KEY:install 全域指令 Unix=symlink、Win=lumos.cmd shim;skills 經 _link_or_copy(Unix symlink / Win junction / 失敗 fallback copytree)
  KEY:_VENDORED_TOOLKIT 5檔常數為 vendor(_vendor_toolchain)與 deinit(_deinit_remove_vendored)共用白名單,避免漂移
  KEY:vendor 結尾 diff 自癒——逐檔 filecmp 比對 src↔target 差異即 shutil.copy2 覆補(installer 漏檔的安全網)
  KEY:來源 repo 自我保護——update/deinit 偵測 root==_lumos_src() 即 return 2(不可在 Lumos 源本身跑專案層指令)
  KEY:_scaffold_project 既有 vault 自動 skip(保護圖譜資料不被 init/update 動)
  DEP:scripts/lumos cmd_install/cmd_uninstall/cmd_bootstrap/cmd_init/cmd_update/cmd_deinit｜_vendor_toolchain/_install_skills/_install_hooks_py/_link_or_copy/_scaffold_project｜_VENDORED_TOOLKIT/_SKILLS 常數｜_lumos_src/_vault_in
  TEST:258 passed(t_install_skills/t_install_includes_skills/t_install_hooks_py/t_scaffold_project/t_link_or_copy_idempotent/t_hooks_python_fallback + t_deinit_*)
decisions:
  - content: 機器層 vs 專案層二分:install/uninstall/bootstrap 動機器共用項(~/.local/bin 全域 lumos、~/.claude skills+hooks);init/update/deinit 只動本 repo
    context: 同事 onboarding 與多 repo 使用需要分清「一輩子裝一次的機器設定」與「每個 repo 各自要做的」;deinit 反安裝若誤碰機器共用項會傷到其他 repo
    why_chosen: bootstrap 一鍵把機器層全裝(clone Lumos+全域+skills+repo hooks);init/deinit 對稱只在本 repo 增刪,deinit 明確不碰 ~/.claude,降低反安裝爆炸半徑
    decided: 2026-06-26
    valid: true
  - content: 全域 lumos 與 skills 用 symlink/junction 指向來源 clone(非 copy),graph-discipline.md 則 per-project 注入
    context: 工具更新如何傳到夥伴機器;若全 copy 則每次更新都要重裝
    why_chosen: symlink 那條 git pull 來源 clone 即吃到 CLI+skills 更新、免重裝;graph-discipline 速查必須跟專案 CLAUDE.md 走故只能 per-project 注入,刷新要重跑 init/update(雷:bootstrap 不加 --pull 不會更新)
    decided: 2026-06-26
    valid: true
  - content: _VENDORED_TOOLKIT(5 檔常數)為 vendor 端與 deinit 端共用白名單;vendor 結尾以 filecmp 逐檔 diff 自癒
    context: 安裝端與移除端各自列舉檔名會漂移(漏移/漏裝);installer 子流程可能漏檔
    why_chosen: 單一常數消除安裝/移除白名單漂移;結尾自癒比對 src↔target 差異即覆補,把「installer 漏檔」收斂成可驗證的最終一致
    decided: 2026-06-26
    valid: true
---
# lumos-cli-lifecycle

`scripts/lumos` 的生命週期原語群:`install` / `uninstall` / `bootstrap` / `init` / `update` / `deinit`。管「Lumos 工具鏈如何裝上機器、裝進專案、更新、反安裝」。圖譜讀寫指令(`new`/`set`/`lint`/`doctor` 等)不在此節點。

## 兩層分工(本節點核心心智模型)
| 層 | 指令 | 動到哪 | 頻率 |
|---|---|---|---|
| **機器層** | `install` / `uninstall` | `~/.local/bin/lumos`(全域指令)+ user-scope skills(`~/.claude/skills/`) | 每台機器一次 |
| **機器層(一鍵)** | `bootstrap` | 上面全部 + 自動 clone Lumos 源 + 該 repo hooks(`~/.claude/hooks/` + settings 註冊) | 同事 onboarding |
| **專案層** | `init` / `update` / `deinit` | 本 repo:`docs/<slug>-knowledge/` vault、`scripts/` vendored 工具組、`CLAUDE.md` 注入區塊、`git core.hooksPath` | 每個 repo |

deinit(專案層反安裝)**不碰機器共用項**;細節見 [[Systems/lumos-deinit]]。

## 各指令一句話
- `install [--force]`:全域 lumos(Unix symlink / Win `lumos.cmd` shim)+ 連帶裝 user-scope skills;檢查 `~/.local/bin` 在不在 PATH。
- `uninstall`:對稱移除全域指令 + skills(symlink/junction/複製夾都清,junction 用 `os.rmdir` 只移連結不跟進 target)。
- `bootstrap [--lumos-url --lumos-home --pull]`:給「剛 clone 專案、機器還沒設定」的人,一行裝好機器層全部 + 本 repo hooks;預設**不** pull 既有 clone(要 `--pull`)。
- `init [--name --force --no-hooks --no-pull]`:在當前 repo 建 vault(6 資料夾 + `.gitignore` + `MOC/index.md` + CLAUDE.md 注入)+ 預設 vendor 工具組 + 裝 pre-commit/pre-push 閘。
- `update [--source --no-pull]`:從 Lumos 唯一源刷新「本專案」vendored 工具組(= git pull 源 + 重 vendor);圖譜資料受 skip 保護不動。
- `deinit`:對稱反安裝(見 [[Systems/lumos-deinit]])。

## 關鍵機制
- **分發=symlink 指向源**:`install`/`_install_skills` 把全域 lumos 與 skills 連到來源 clone(`$LUMOS_HOME`,預設 `~/harness/lumos-toolchain`)。`git pull` 來源 clone 即吃到 CLI 行為 + skill 更新,免重裝;但 `graph-discipline.md` 速查是 `_scaffold_project` per-project 注入專案 `CLAUDE.md`,要重跑 `init`/`update` 才刷新。
- **`_link_or_copy` 跨平台 + 冪等**:Unix `symlink_to`、Win `mklink /J` junction(輸出走 OEM 碼頁,`errors="replace"` 防 UnicodeDecodeError)、皆失敗 fallback `copytree`(失去 pull 即更新)。重跑須冪等且絕不刪來源(`t_link_or_copy_idempotent`)——junction/空夾用 `os.rmdir` 只移連結本身、不跟進 target。
- **vendor 共用白名單 + 結尾自癒**:`_VENDORED_TOOLKIT`(`scripts/lumos`、`scripts/test_lumos.py`、`scripts/merge-claude-settings.py`、`scripts/graph-rename.sh`、`scripts/fetch-notesmd.sh`)+ `scripts/hooks/`、`scripts/templates/` 兩夾。`_vendor_toolchain` 收尾以 `filecmp.cmp(shallow=False)` 逐檔比對 src↔target,差異即 `copy2` 覆補(自癒 installer 漏檔)。
- **資料保護**:`_scaffold_project` 偵測 vault 已存在即 skip;`init --force` 也只重裝 hooks/工具組,vault 內容不動。
- **來源自我保護**:`update`/`deinit` 偵測 `root==_lumos_src()` 即 `return 2`(不可在 Lumos 源本身跑專案層指令)。
- **hooks 安裝**(`_install_hooks_py`):①`git config core.hooksPath scripts/hooks` ②Claude hooks `.py` copy 進 `~/.claude/hooks/`(個別檔不用 junction,因 `mklink /J` 只連目錄)③`merge-claude-settings.py` 用 resolved python 註冊 settings。

## 已知限制 / 雷
- `bootstrap` 不加 `--pull`,既有 clone 會跳過更新 → 直接 `git pull` 來源 clone 最乾脆。
- `_link_or_copy` fallback 到 copytree 後就失去「pull 即更新」(該機器無法建連結時)。
- bootstrap/init 裝完 hooks 需**重啟 Claude Code session** 才載入 L1/L3 hooks。
- 源起:CLI 核心非日報觸發(基礎設施原語,非由 governance 日報 gap/inspiration 驅動;`governance/reports/*` 無對應項)。

## 相關
- 對稱反安裝細節:[[Systems/lumos-deinit]](唯一有獨立設計稿 `docs/design/2026-06-26-lumos-deinit.md` 的生命週期指令)。
- 實作落點:`scripts/lumos` `cmd_install`/`cmd_uninstall`/`cmd_bootstrap`/`cmd_init`/`cmd_update`/`cmd_deinit` + helper `_vendor_toolchain`/`_install_skills`/`_install_hooks_py`/`_link_or_copy`/`_scaffold_project` + 常數 `_VENDORED_TOOLKIT`/`_SKILLS`/`_INIT_SUBDIRS_FULL`。
- 分發機制脈絡:user-memory `lumos-update-distribution`。
