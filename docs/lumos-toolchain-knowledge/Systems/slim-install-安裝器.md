---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
summary: |-
  FLOW:`slim/install.sh` 用 `$(cd "$(dirname "$0")" && pwd)`(先解 symlink 鏈)定位交付包 → 檢查 `scripts/lumos`/`skills/lumos-project-notes` 存在(找不到即 rc2)→ 只做兩件事:複製 `scripts/lumos` 到 `~/.local/bin/lumos`(chmod +x)、實體複製(`cp -R`,非 symlink)`skills/lumos-project-notes` 到 `~/.claude/skills/` → 碰撞語意:目標已存在且無 `--force` → rc2 拒絕;帶 `--force` 時 bin 直接覆寫、skill 目錄先備份成 `.bak.<timestamp>` 才覆寫 → 結尾檢查 PATH 是否含 `~/.local/bin`,非阻斷提示
  KEY:★只動 $HOME,絕不碰專案層★——不 scaffold 圖譜、不注入/更新 CLAUDE.md、不 vendor 工具進專案、不設 core.hooksPath、不裝任何 Claude hook(對比完整版 install.sh 尾端 `_sync_global_claude` 會把 4 支被禁 hook 裝回去,精簡版安裝器刻意不繼承這段)
  KEY:skill 碰撞語意是新寫,不是沿用完整版 `_link_or_copy`(對既有實體目錄直接 rmtree、無備份無拒絕,牴觸本安裝器自己的反誤傷測試)
  KEY:★symlink 呼叫邊界(2026-07-31 實測,spec [S4-c] 明列未經審計必須實測)★——`$(dirname "$0")` 素樸寫法解析到 symlink 所在目錄而非真實包目錄,實測必壞(rc2 報「找不到 scripts/lumos」);裁定採(a)修正寫法而非(b)只寫錯誤訊息:開頭加手捲 symlink 解析迴圈(macOS 無 `readlink -f`,逐層 readlink 接回所在目錄再判斷是否還是 symlink)。已實測 3 種邊界全過:絕對路徑 symlink/相對路徑 2 層 symlink 鏈/路徑含空白
  KEY:2026-07-31 Task 6 補上一行安裝／卸載入口——本腳本本身未改動(`$(dirname "$0")` 定位、碰撞語意皆維持原樣),但新增的 [[Systems/slim-get-一行安裝]](`slim/get.sh`)把交付包 clone 到固定落點 `~/.lumos-slim` 再呼叫本腳本,解掉「使用者把交付包搬走/刪掉,全域指令就斷了」的既有問題;新增的 [[Systems/slim-uninstall-一行卸載]] 用本腳本複製出去的 `~/.local/bin/lumos` 與 `~/.lumos-slim/scripts/lumos` 做 sha256 比對,判斷卸載對象是不是本腳本裝的那份
  DEP:scripts/test_lumos.py t_slim_install_no_project_touch
  TEST:8 checks 全綠(`python3 scripts/test_lumos.py -k slim_install`)——安裝器 rc0、專案 worktree porcelain 空、.git/config 不變、全域指令已裝、skill 實體複製非 symlink、不裝 Claude hook、既有一般檔碰撞拒絕 rc2、既有檔內容未被動
verified_by:
  - "[[Verification/2026-07-31_slim-install安裝器落地]]"
  - "[[Verification/2026-07-31_公開精簡版交付]]"
  - "[[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]]"
related:
  - "[[Systems/slim-get-一行安裝]]"
  - "[[Systems/slim-uninstall-一行卸載]]"
---
# slim-install-安裝器

公開精簡版交付前的機器層安裝器。隨交付包一起走(`$(dirname "$0")` 定位自身,不吃路徑參數),只做兩件事:①裝全域 `lumos` 指令 ②實體複製 `skills/lumos-project-notes` 到 `~/.claude/skills/`(非 symlink,交付包可被刪掉/搬走後 skill 仍在)。**只動使用者 `$HOME`,絕不碰任何專案 repo**——本 Task 最重要的產出是反誤傷測試 `t_slim_install_no_project_touch`,證明跑完後專案 worktree porcelain 為空、`.git/config` 前後相同。明確不做:不 scaffold 圖譜、不注入/更新任何 CLAUDE.md、不 vendor 工具進專案、不設 `core.hooksPath`、不裝任何 Claude hook。詳見 [[Projects/公開精簡版_實作計畫]] Task 3。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-3-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此);spec [S4-c] 見 [[Projects/公開精簡版_計劃]]。
