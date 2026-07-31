---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
plan_refs:
  - "[[Projects/公開精簡版_計劃]]"
summary: |-
  FLOW:`slim/install.sh` 用 `$(cd "$(dirname "$0")" && pwd)`(先解 symlink 鏈)定位交付包 → 檢查 `scripts/lumos`/`skills/lumos-project-notes` 存在(找不到即 rc2)→ 做三件事:①複製 `scripts/lumos` 到 `~/.local/bin/lumos`(chmod +x)②實體複製(`cp -R`,非 symlink)`skills/lumos-project-notes` 到 `~/.claude/skills/`③(★2026-07-31 Task 9 裁定第三次變更★)讀取隨包帶的 `claude-block.md` 範本,在執行目錄(專案根)的 `CLAUDE.md` 裡放策展過的精簡版紀律區塊(`<!-- LUMOS-SLIM:START/END -->`)——專案若已有完整版 `LUMOS:GRAPH-DISCIPLINE` 區塊,先把原文 base64 編碼進備份標記再**原地整段取代**;沒有就插在檔首「# 標題」之後(沒標題插最前面);CLAUDE.md 不存在就直接建立 → ①②碰撞語意:目標已存在且無 `--force` → rc2 拒絕;帶 `--force` 時 bin 直接覆寫、skill 目錄先備份成 `.bak.<timestamp>` 才覆寫;③不設碰撞閘,靠比對「有無完整版區塊/精簡版區塊已存在」三態決定行為 → 結尾檢查 PATH 是否含 `~/.local/bin`,非阻斷提示
  KEY:★只動 $HOME 與專案 CLAUDE.md 這一份檔案,不碰專案其餘任何東西★(★2026-07-31 使用者裁定推翻原「不注入/更新任何 CLAUDE.md」的裁定,範圍刀見下條★)——仍不 scaffold 圖譜、不 vendor 工具進專案、不設 core.hooksPath、不裝任何 Claude hook(對比完整版 install.sh 尾端 `_sync_global_claude` 會把 4 支被禁 hook 裝回去,精簡版安裝器刻意不繼承這段)
  KEY:★裁定演進三階(spec [S3],別誤讀成一次到位)★——①原裁定:絕不碰 CLAUDE.md ②Task 8:只准附加、檔尾、絕不覆蓋完整版區塊、兩套規則並存 ③**Task 9(本次)**:兩套規則並存本身是問題——完整版那段自稱「優先級最高/第一個工具呼叫必須是 lumos」,接手者的 Claude 會先讀到它、照著它引用的 design-loop/code-loop/pitfalls 等 13 處本包沒交付的指令去撲空。裁定改成:有完整版區塊就**整段移除、原地換成精簡版區塊**(不是繼續並存);移除前先策展吸收完整版裡仍然有效的內容(合約鏈/可逆性標記/regen 重生標記/frontmatter 欄位,見 `slim/claude-block.md`),只拿掉依賴已移除指令才有意義的段落。詳見 [[Projects/公開精簡版_計劃]] [S3]〈裁定第三次變更〉
  KEY:★INVARIANT★ CLAUDE.md 注入必須原地取代/檔首插入,sentinel(`<!-- LUMOS-SLIM:START/END -->`)以外的既有內容 byte-equal 保留(改=毀使用者/其他工具寫進 CLAUDE.md 的內容=breaking);有完整版區塊就在它原本的位置換掉,沒有就插在檔首標題之後,都不是搬到檔尾 [test:t_slim_install_no_project_touch,t_slim_install_replaces_full_discipline_block_in_place] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把寫入改成整檔覆寫,綁定測試確實翻紅,非稻草人)
  KEY:★INVARIANT★ CLAUDE.md 注入必須冪等——重跑安裝器只更新自己 sentinel 之間那塊內容,不疊出第二塊、不因重跑而漂移,備份標記(FULL-BACKUP)也不會被重新編碼或洗成 NONE [test:t_slim_install_claude_md_idempotent,t_slim_install_backup_survives_idempotent_reinstall] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把「已存在 sentinel 則替換」的分支關掉,強迫每次都走插入路徑,綁定測試確實翻紅——第二次跑完出現兩塊 sentinel)
  KEY:★INVARIANT★ 完整版區塊被取代前必須先把原文(含它自己的 sentinel)位元組級備份——base64 編碼藏進精簡版區塊自己的 HTML 註解裡(`<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->`),解碼後須與原文逐位元組相同,這是 [[Systems/slim-uninstall-一行卸載]] 能精確還原的前提 [test:t_slim_install_replaces_full_discipline_block_in_place] [audit:sonnet/2026-07-31](備份設計理由:自足、隨 CLAUDE.md 本身走,不新增檔案到使用者專案、`~/.lumos-slim` 被刪掉也還原得了)
  KEY:skill 碰撞語意是新寫,不是沿用完整版 `_link_or_copy`(對既有實體目錄直接 rmtree、無備份無拒絕,牴觸本安裝器自己的反誤傷測試)
  KEY:★symlink 呼叫邊界(2026-07-31 實測,spec [S4-c] 明列未經審計必須實測)★——`$(dirname "$0")` 素樸寫法解析到 symlink 所在目錄而非真實包目錄,實測必壞(rc2 報「找不到 scripts/lumos」);裁定採(a)修正寫法而非(b)只寫錯誤訊息:開頭加手捲 symlink 解析迴圈(macOS 無 `readlink -f`,逐層 readlink 接回所在目錄再判斷是否還是 symlink)。已實測 3 種邊界全過:絕對路徑 symlink/相對路徑 2 層 symlink 鏈/路徑含空白
  KEY:2026-07-31 Task 6 補上一行安裝／卸載入口——本腳本本身未改動(`$(dirname "$0")` 定位、碰撞語意皆維持原樣),但新增的 [[Systems/slim-get-一行安裝]](`slim/get.sh`)把交付包 clone 到固定落點 `~/.lumos-slim` 再呼叫本腳本,解掉「使用者把交付包搬走/刪掉,全域指令就斷了」的既有問題;新增的 [[Systems/slim-uninstall-一行卸載]] 用本腳本複製出去的 `~/.local/bin/lumos` 與 `~/.lumos-slim/scripts/lumos` 做 sha256 比對,判斷卸載對象是不是本腳本裝的那份
  DEP:scripts/test_lumos.py t_slim_install_no_project_touch｜t_slim_install_claude_md_idempotent｜t_slim_install_replaces_full_discipline_block_in_place｜t_slim_install_backup_survives_idempotent_reinstall｜t_slim_claude_block_curation｜slim/claude-block.md(策展範本,slim-gen.py 組包清單已補)
  TEST:187 checks 全綠(`python3 scripts/test_lumos.py -k slim`)。t_slim_install_no_project_touch 覆蓋沒有完整版區塊情境(改斷言為插檔首標題後、既有內容 byte-equal、附加而非覆蓋);t_slim_install_claude_md_idempotent 覆蓋冪等;t_slim_install_replaces_full_discipline_block_in_place(新)覆蓋有完整版區塊情境——原地取代、備份 base64 解碼後與原文逐位元組相同;t_slim_install_backup_survives_idempotent_reinstall(新)覆蓋「重跑安裝器不把備份洗掉/不二次包裹」;t_slim_claude_block_curation(新)斷言策展範本不含 design-loop/code-loop/core-knowledge/pitfalls/spec-trace/signoff/lumos init/lumos update 字串、且含合約鏈標記/[test:/FLOW:/KEY:/valid_under/佚失: 等仍有效內容
verified_by:
  - "[[Verification/2026-07-31_slim-install安裝器落地]]"
  - "[[Verification/2026-07-31_公開精簡版交付]]"
  - "[[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]]"
  - "[[Verification/2026-07-31_slim-claude-md注入]]"
  - "[[Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原]]"
related:
  - "[[Systems/slim-get-一行安裝]]"
  - "[[Systems/slim-uninstall-一行卸載]]"
---
# slim-install-安裝器

公開精簡版交付前的機器層安裝器。隨交付包一起走(`$(dirname "$0")` 定位自身,不吃路徑參數),做三件事:①裝全域 `lumos` 指令 ②實體複製 `skills/lumos-project-notes` 到 `~/.claude/skills/`(非 symlink,交付包可被刪掉/搬走後 skill 仍在)③(★2026-07-31 Task 9 裁定第三次變更★)在執行目錄(專案根)的 `CLAUDE.md` 裡放策展過的精簡版紀律區塊,取代掉完整版(若有)。**裁定演進三階**:①原裁定絕不碰 CLAUDE.md ②Task 8 開放只准附加、檔尾、絕不覆蓋完整版區塊、兩套規則並存 ③Task 9(本次)發現「兩套規則並存」本身是問題(完整版那段自稱優先級最高、引用一堆本包沒交付的指令),裁定改成:有完整版區塊就整段移除、**原地換成**精簡版區塊(不是搬到檔尾);移除前策展吸收完整版裡仍然有效的內容、先把原文位元組級備份(base64 藏進精簡版區塊自己的 HTML 註解裡),`uninstall.sh` 能精確還原。**只動使用者 `$HOME` 與這一份 CLAUDE.md,不碰專案其餘任何檔案**——反誤傷測試 `t_slim_install_no_project_touch`(本次再次換形狀:斷言插入點在檔首標題後而非檔尾,其餘不變)。仍明確不做:不 scaffold 圖譜、不 vendor 工具進專案、不設 `core.hooksPath`、不裝任何 Claude hook。詳見 [[Projects/公開精簡版_實作計畫]] Task 3、Task 8、Task 9(CLAUDE.md 注入裁定第三次變更)。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-3-brief.md`／`task-9-report.md`(SDD 產出,非圖譜路徑,依計畫落地於此);spec [S3] 裁定第三次變更、[S4-c] 見 [[Projects/公開精簡版_計劃]]。
