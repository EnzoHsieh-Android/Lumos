---
type: verification
status: pass
date: 2026-08-01
valid_under: "分支 feat/public-slim-handoff,slim/install.sh 現行版本(⓪ 注入目標守衛三層設計、--here 逃生閥);Python3 stdlib + bash 零依賴前提不變"
revalidate_when: "改動 slim/install.sh 的第一/二層判定式、TARGET_DIR 或 HOME_PHYS 的路徑解析邏輯、或新增/移除三件套判準檔案時"
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/公開精簡版_計劃]]"
summary: |-
  TEST:`python3 scripts/test_lumos.py -k slim` 217 checks 全綠。六支新測試 `t_slim_install_guard_*` 專測三層守衛;既有 `t_slim_uninstall_backs_up_and_preserves_custom_files`/`t_slim_uninstall_refuses_foreign_bin`/`t_slim_uninstall_idempotent_second_run`/`t_slim_uninstall_removes_claude_md_block`(情境二)/`t_slim_get_idempotent` 補 `.git` fixture 標記,通過新守衛後行為與 Task 11 前 byte-equal(既有行為不退化)。
  VERIFY:[[Systems/slim-install-安裝器]] 新增的合約性 KEY 行(⓪ 注入目標守衛三層)。收尾在本 repo 根目錄實跑重新生成的 `dist/install.sh`,精確重現兩次真實事故的情境:rc=2,訊息「這是 lumos 工具鏈的來源 repo,不是要交接的專案」,`git status --porcelain CLAUDE.md` 全空。
---
# 2026-08-01_slim-install注入目標守衛

## 為什麼要做

`slim/install.sh` 會對 `$(pwd)/CLAUDE.md` 動手,但原本完全沒檢查那個目錄是不是合理的注入目標。★真實事故已咬過兩次★:兩位不同的子代理驗證時忘記先 `cd` 進交付包 clone,直接在 `/Users/enzo/harness/lumos-toolchain`(lumos 工具鏈來源 repo 自己)底下跑 `dist/install.sh`,當場改掉了來源 repo 自己的 `CLAUDE.md`。兩次都當場發現、`git checkout` 還原,但足以說明這支腳本本質上容易誤用。

**關鍵認知**:那兩次事故發生的目錄本身就有 `.git`、`CLAUDE.md`、`docs/*-knowledge/`——單純判斷「像不像專案根」完全擋不住那兩次,必須用更精確的「這是不是 lumos 工具鏈本身的來源 repo」判準才擋得住。

## 修法:三層守衛,各擋不同的東西

1. **第一層(不像專案根就拒絕)**:目標目錄要有 `.git`、或 `docs/*-knowledge/`、或已有 `CLAUDE.md`,三項至少一項成立才放行;一項都沒有 → rc=2,`CLAUDE.md` 不建立。特例:`$(pwd)` 等於 `$HOME` 一律硬擋,就算 `$HOME` 底下剛好有 `.git` 也一樣(用 `pwd -P`/`cd -P` 解 symlink 後比對,避免 macOS `/var`→`/private/var` 這類邏輯/實體路徑不一致誤判)。
2. **第二層(★真正擋住那兩次事故的層★)**:目標目錄同時具備 `skills/lumos-project-notes/`+`scripts/lumos`+`scripts/templates/graph-discipline.md` 三件套 → 判定是 lumos 工具鏈本身的來源 repo,不是要交接的消費端專案 → rc=2。沿用 `scripts/lumos` 裡 `cmd_update`/`cmd_deinit` 的自我保護精神(`root == _lumos_src()` → 拒絕)。
3. **第三層(把目標印大聲)**:不論前兩層過不過,動手前一律先印出「目標專案」與「將修改」的絕對路徑——最後一道人眼防線,擋不住「在另一個合法專案根誤跑」時至少讓人看得見。

逃生閥 `--here`:明示「我知道我在做什麼」,繞過第一、二層(第三層的印出不受影響)。

## TDD:先紅後綠

新增六支 `t_slim_install_guard_*`(見 [[Systems/slim-install-安裝器]] summary DEP/TEST 行)。既有 `t_slim_uninstall_backs_up_and_preserves_custom_files`/`t_slim_uninstall_refuses_foreign_bin`/`t_slim_uninstall_idempotent_second_run`/`t_slim_uninstall_removes_claude_md_block`(proj_b 情境)/`t_slim_get_idempotent` 原本用不帶任何專案標記的裸 tempdir 當 `install.sh` 的 cwd——這在新守衛下會被第一層擋下(空目錄拒絕正是新行為的一部分),故補 `(root / ".git").mkdir()` 讓 fixture 通過守衛,行為本身未改。

## 獨立審計抓到的真缺陷(誠實記錄,非空手放行)

派無脈絡獨立 agent(sonnet)審計五問 rubric,第 4 問(可證偽性)要求**真的去竄改一份暫存副本**驗證綁定測試會不會翻紅,不能只用推理帶過。結果:

- `t_slim_install_guard_rejects_source_repo` 竄改後確實翻紅——合格。
- `t_slim_install_guard_repro_real_incident`(原版)**是稻草人**:原版直接對 `slim/install.sh` 原始檔以 repo 根為 cwd 執行,但 `slim/` 底下沒有 `scripts/lumos`(那份檔案在 repo 根的 `scripts/lumos`,不在 `slim/scripts/lumos`),腳本會先撞上與本守衛完全無關的套件完整性檢查 `[ -f "${PKG}/scripts/lumos" ]` 提前以 rc=2 退出。**把第二層判斷式整段刪掉,這支測試依然通過**——測到的是無關的早退路徑,不是守衛本身。

修法:改用 `scripts/slim-gen.py` 真的生成一份 `dist/install.sh`(PKG 解到 `dist/`,套件完整性檢查會過)再以 repo 根為 cwd 執行,並額外斷言訊息含「來源 repo」字樣確保真的是第二層擋下。修正後複測:把第二層 `if` 判斷式換成 `if false; then` 製造假陽性,綁定測試確實翻紅(rc 從 2 變 0、`CLAUDE.md` 真的被覆寫)——此步驟意外把本 repo 自己的 `CLAUDE.md` 寫髒,已 `git checkout -- CLAUDE.md` 立即復原並確認 `git status --porcelain CLAUDE.md` 清空後才繼續。其餘五支測試審計時逐一確認皆非稻草人。

## 端到端實跑(收尾,精確重現兩次事故的情境)

```
$ python3 scripts/slim-gen.py
✓ 生成 dist/scripts/lumos  保留 154 函式 / 移除 152 / 保住 379 行註解
✓ 交付包: dist

$ HOME=<乾淨假 HOME> bash dist/install.sh   # cwd = 本 repo 根目錄
目標專案: /Users/enzo/harness/lumos-toolchain
將修改: /Users/enzo/harness/lumos-toolchain/CLAUDE.md
ERROR: /Users/enzo/harness/lumos-toolchain 是 lumos 工具鏈的來源 repo,不是要交接的專案——拒絕注入。
  若確定要在這裡安裝,加 --here 明示。
rc=2

$ git status --porcelain CLAUDE.md
(空)
```

`python3 scripts/test_lumos.py -k slim` 217 checks 全綠。完整報告見 `.superpowers/sdd/公開精簡版_實作計畫/task-11-report.md`。
