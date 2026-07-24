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
  KEY:bootstrap 一鍵對稱(2026-07-25)=step3 升級專案層四分流:有vault+vendored→接hooks｜中間態(有vault無vendored,_vault_in 只看名稱防假陽性疊動作)→提示補齊不自動動｜無vault→_confirm_tty 確認(印完整路徑+預設N)y 才 cmd_init(--init 免確認;一律 force=False+no_pull=True,LUMOS_HOME env 傳導自訂 home)｜非git→只機器層。get.sh 迴圈解析 --pull/--init 後整段委派 bootstrap;各步查 rc 失敗尾端彙報 rc1 不吞錯。與 teardown 成鏡像(bootstrap 不刪vault、teardown 不建vault,圖譜兩邊不碰)。設計 [[Projects/bootstrap一鍵對稱_計劃]]、驗證 [[Verification/2026-07-25_bootstrap一鍵對稱]]
  KEY:_confirm_tty(curl|bash 安全確認)三階=①stdin.isatty→input(),EOFError 落②非當 False ②os.open('/dev/tty',O_RDWR) 低階 fd(r+ 對 tty 炸 not seekable,Codex 真機實證)+os.write+select timeout 30s+os.read(有控制終端≠有人回答) ③None=跳過;答案嚴格 y/yes 預設 N;測試接縫 LUMOS_TTY/LUMOS_TTY_TIMEOUT
  KEY:teardown(2026-07-24)=一鍵反安裝,跨兩層:全域hook清理→deinit(keep_graph=True)→uninstall,★永遠保留圖譜文件★;範圍=當前 repo+機器全域(非全機所有 repo,deinit 只吃當前 toplevel)。順序「全域先」因 deinit 會刪 vendored merge-claude-settings.py 而 _teardown_global_claude 要用它;全域清理走 merge --prune-only(只剪懸空不 re-add)+壞 settings JSON 先驗跳過不刪 .py。設計/審計 [[Projects/teardown一鍵拆機_計劃]]、[[Verification/2026-07-24_teardown一鍵拆機]]
  KEY:安全守衛(2026-07-24,改共用函式故 deinit/uninstall 直呼也受惠)——_deinit_unbar_gate 只在 core.hooksPath 指向本 repo scripts/hooks 才 unset(不誤殺使用者 githooks)｜cmd_uninstall 只移 symlink 不刪 ~/.local/bin/lumos 同名一般檔。繼承殘留(deinit 老 bug,teardown help 明列):F9 scripts/hooks|templates 整夾 rmtree 刪使用者檔=★已修 2026-07-24★(逐檔白名單,見 [[Issues/deinit整夾刪使用者檔]]);未修=F4 剝 CLAUDE.md 正規化 sentinel 外空白/CRLF、F12 uninstall 移全部 skills 非只 lumos-*(影響更小,未開票)
  KEY:全域 lumos 與 skills 走 symlink/junction 指向來源 clone(非 copy)→ git pull 來源即吃到 CLI+skills 更新;graph-discipline.md 是 per-project 注入,重跑 init/update 會刷新 CLAUDE.md 紀律區塊(2026-07-06 起真的成真:注入已與 _scaffold_project 的 vault-skip 解耦、無條件 re-inject;見 [[2026-07-06_CLAUDE注入re-sync]])
  KEY:★INVARIANT★ re-inject 只覆蓋 sentinel 之間 body、sentinel 之外 CLAUDE.md 內容 byte-equal 保留(改=毀使用者手寫內容=breaking) [test:t_reinject_preserves_outside] [audit:sonnet/2026-07-06]
  KEY:★DEBT★ CLAUDE.md START sentinel 的版本戳(LUMOS_VERSION)=人可讀標籤/advisory nudge,非正確性守衛(內容比對 doctor Check D 才是;版本在 body 外、bump 不觸發守衛)
  KEY:install 全域指令 Unix=symlink、Win=lumos.cmd shim;skills 經 _link_or_copy(Unix symlink / Win junction / 失敗 fallback copytree)
  KEY:_VENDORED_TOOLKIT 白名單=5檔(scripts/lumos、test_lumos.py、merge-claude-settings.py、graph-rename.sh、fetch-notesmd.sh)+scripts/hooks/+scripts/templates/兩夾,為 vendor(_vendor_toolchain)與 deinit(_deinit_remove_vendored)共用,避免漂移;★2026-07-25 pre-commit 圖譜閘也豁免此白名單★(精確路徑非 scripts/* 整夾,專案自有 scripts/foo.py 仍擋)——vendored .py 誤中 code 副檔名判定,致每次 lumos update 例行更新都撞閘、bypass 帳被灌水稀釋真訊號;豁免住兩個 hook(pre-commit 擋+post-commit 記 bypass 帳)★必須對齊★——只修前者時 post-commit 照記假 bypass 灌水(2026-07-25 實測踩過);且★源 repo 守門★:偵測 skills/lumos-project-notes(=Lumos 源)時豁免失效(源 repo 內這些檔=產品碼,豁免會弄弱自家閘)。bash 清單↔常數↔兩 hook 對齊靠 [test:t_precommit_whitelist_drift_guard]+行為測試 t_precommit_vendored_exempt(放行 vendored/仍擋使用者檔/源 repo 內仍擋)
  KEY:vendor 結尾 diff 自癒——逐檔 filecmp 比對 src↔target 差異即 shutil.copy2 覆補(installer 漏檔的安全網)
  KEY:來源 repo 自我保護——update/deinit 偵測 root==_lumos_src() 即 return 2(不可在 Lumos 源本身跑專案層指令)
  KEY:_scaffold_project 既有 vault 自動 skip(保護圖譜資料不被 init/update 動)
  KEY:cmd_init slug 決定順序=①--name ②既有 vault 資料夾名(去 -knowledge)③repo basename;②先於③是硬要求——否則既有 vault 上 --force 用 basename 建錯空 vault + 寫錯 CLAUDE.md {{KG}} 路徑(見 [[init-force-slug誤用basename]]) [test:t_init_force_uses_existing_vault_slug]
  DEP:scripts/lumos cmd_install/cmd_uninstall/cmd_bootstrap/cmd_init/cmd_update/cmd_deinit/cmd_teardown｜_vendor_toolchain/_install_skills/_install_hooks_py/_sync_global_claude/_teardown_global_claude/_link_or_copy/_scaffold_project｜merge-claude-settings.py(--prune-only)｜_VENDORED_TOOLKIT/_SKILLS 常數｜_lumos_src/_vault_in
  TEST:258 passed(t_install_skills/t_install_includes_skills/t_install_hooks_py/t_scaffold_project/t_link_or_copy_idempotent/t_hooks_python_fallback + t_deinit_*)
decisions:
  - content: 機器層 vs 專案層二分:install/uninstall/bootstrap 動機器共用項(~/.local/bin 全域 lumos、~/.claude skills+hooks);init/update/deinit 只動本 repo
    id: d1
    context: 同事 onboarding 與多 repo 使用需要分清「一輩子裝一次的機器設定」與「每個 repo 各自要做的」;deinit 反安裝若誤碰機器共用項會傷到其他 repo
    why_chosen: bootstrap 一鍵把機器層全裝(clone Lumos+全域+skills+repo hooks);init/deinit 對稱只在本 repo 增刪,deinit 明確不碰 ~/.claude,降低反安裝爆炸半徑
    decided: 2026-06-26
    valid: true
  - content: 全域 lumos 與 skills 用 symlink/junction 指向來源 clone(非 copy),graph-discipline.md 則 per-project 注入
    id: d2
    context: 工具更新如何傳到夥伴機器;若全 copy 則每次更新都要重裝
    why_chosen: symlink 那條 git pull 來源 clone 即吃到 CLI+skills 更新、免重裝;graph-discipline 速查必須跟專案 CLAUDE.md 走故只能 per-project 注入,刷新要重跑 init/update(雷:bootstrap 不加 --pull 不會更新)
    decided: 2026-06-26
    valid: true
  - content: _VENDORED_TOOLKIT(5 檔常數)為 vendor 端與 deinit 端共用白名單;vendor 結尾以 filecmp 逐檔 diff 自癒
    id: d3
    context: 安裝端與移除端各自列舉檔名會漂移(漏移/漏裝);installer 子流程可能漏檔
    why_chosen: 單一常數消除安裝/移除白名單漂移;結尾自癒比對 src↔target 差異即覆補,把「installer 漏檔」收斂成可驗證的最終一致
    decided: 2026-06-26
    valid: true
related:
  - "[[CLAUDE注入re-sync與版本標籤_計劃]]"
verified_by:
  - "[[Verification/2026-07-06_CLAUDE注入re-sync]]"
  - "[[Verification/2026-07-25_bootstrap一鍵對稱]]"
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
- `bootstrap [--lumos-url --lumos-home --pull --init]`:一鍵裝好機器層全部 + 專案層自動接線(2026-07-25 四分流:已是專案接 hooks/中間態提示/無 vault 經 `_confirm_tty` 確認後 auto-init、`--init` 免確認/非 git 只機器層);預設**不** pull 既有 clone(要 `--pull`)。
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
- 圖譜讀指令群:`scripts/lumos` `new`/`set`/`lint`/`doctor` 等:[[Systems/lumos-cli-read]]。
- 圖譜寫指令群(`new`/`set`/`rename` 等):[[Systems/lumos-cli-write]]。
- 原生 Windows 支援細節(junction、lumos.cmd shim、OEM 碼頁處理):[[Systems/native-windows-support]]。
- 實作落點:`scripts/lumos` `cmd_install`/`cmd_uninstall`/`cmd_bootstrap`/`cmd_init`/`cmd_update`/`cmd_deinit` + helper `_vendor_toolchain`/`_install_skills`/`_install_hooks_py`/`_link_or_copy`/`_scaffold_project` + 常數 `_VENDORED_TOOLKIT`/`_SKILLS`/`_INIT_SUBDIRS_FULL`。`_INIT_SUBDIRS_FULL` 是 vault 六夾:Systems、Verification、Projects、Issues、Sessions、MOC。`_SKILLS` 是 install 時裝入 user-scope 的三個 skills:lumos-project-notes、lumos-core-knowledge、lumos-design-loop。
- 分發機制脈絡:user-memory `lumos-update-distribution`。
