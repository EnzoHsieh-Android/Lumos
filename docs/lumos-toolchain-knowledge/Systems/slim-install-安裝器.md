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
  FLOW:`slim/install.sh` 用 `$(cd "$(dirname "$0")" && pwd)`(先解 symlink 鏈)定位交付包 → 檢查 `scripts/lumos`/`skills/lumos-project-notes` 存在(找不到即 rc2)→ 做三件事:①複製 `scripts/lumos` 到 `~/.local/bin/lumos`(chmod +x)②實體複製(`cp -R`,非 symlink)`skills/lumos-project-notes` 到 `~/.claude/skills/`③(★2026-07-31 裁定變更★)在執行目錄(專案根)的 `CLAUDE.md` 檔尾,用 `<!-- LUMOS-SLIM:START/END -->` sentinel append-only 附加圖譜標籤教學 → ①②碰撞語意:目標已存在且無 `--force` → rc2 拒絕;帶 `--force` 時 bin 直接覆寫、skill 目錄先備份成 `.bak.<timestamp>` 才覆寫;③不設碰撞閘(本質上不會覆蓋任何非自己寫的內容,見下方合約說明)→ 結尾檢查 PATH 是否含 `~/.local/bin`,非阻斷提示
  KEY:★只動 $HOME 與專案 CLAUDE.md 這一份檔案,不碰專案其餘任何東西★(★2026-07-31 使用者裁定推翻原「不注入/更新任何 CLAUDE.md」的裁定,範圍刀見下條★)——仍不 scaffold 圖譜、不 vendor 工具進專案、不設 core.hooksPath、不裝任何 Claude hook(對比完整版 install.sh 尾端 `_sync_global_claude` 會把 4 支被禁 hook 裝回去,精簡版安裝器刻意不繼承這段)
  KEY:★裁定範圍刀★——原裁定禁的是「覆蓋」:完整版 `lumos init`/`lumos update` 會用範本整段重新注入、覆蓋掉 `<!-- LUMOS:GRAPH-DISCIPLINE:START -->` sentinel 之間既有的紀律區塊(會把 Landmark 那類已引用 `lumos-project-notes` 9 次的既有紀律段沖掉)。新裁定開的是「附加」:只在檔尾用**專屬且與完整版不同名**的 sentinel `<!-- LUMOS-SLIM:START/END -->` 加一段「怎麼解析圖譜標籤」教學,不觸碰 `LUMOS:GRAPH-DISCIPLINE` 那塊、也不觸碰 sentinel 以外任何既有內容;內容只教標籤語意(summary 符號/KEY 行合約性前綴/合約鏈括號/frontmatter 欄位/進場三步),design-loop/code-loop 那套機械對抗審計紀律依舊不給(見 [[Projects/公開精簡版_計劃]] [S4-b])
  KEY:★INVARIANT★ CLAUDE.md 注入只准附加、絕不覆蓋——寫在檔尾,sentinel(`<!-- LUMOS-SLIM:START/END -->`)以外的既有內容 byte-equal 保留(改=毀使用者/其他工具寫進 CLAUDE.md 的內容=breaking) [test:t_slim_install_no_project_touch] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把寫入改成整檔覆寫,綁定測試確實翻紅,非稻草人)
  KEY:★INVARIANT★ CLAUDE.md 注入必須冪等——重跑安裝器只更新自己 sentinel 之間那塊內容,不疊出第二塊、不因重跑而漂移 [test:t_slim_install_claude_md_idempotent] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把「已存在 sentinel 則替換」的分支關掉,強迫每次都走插入路徑,綁定測試確實翻紅——第二次跑完出現兩塊 sentinel)
  KEY:skill 碰撞語意是新寫,不是沿用完整版 `_link_or_copy`(對既有實體目錄直接 rmtree、無備份無拒絕,牴觸本安裝器自己的反誤傷測試)
  KEY:★symlink 呼叫邊界(2026-07-31 實測,spec [S4-c] 明列未經審計必須實測)★——`$(dirname "$0")` 素樸寫法解析到 symlink 所在目錄而非真實包目錄,實測必壞(rc2 報「找不到 scripts/lumos」);裁定採(a)修正寫法而非(b)只寫錯誤訊息:開頭加手捲 symlink 解析迴圈(macOS 無 `readlink -f`,逐層 readlink 接回所在目錄再判斷是否還是 symlink)。已實測 3 種邊界全過:絕對路徑 symlink/相對路徑 2 層 symlink 鏈/路徑含空白
  KEY:2026-07-31 Task 6 補上一行安裝／卸載入口——本腳本本身未改動(`$(dirname "$0")` 定位、碰撞語意皆維持原樣),但新增的 [[Systems/slim-get-一行安裝]](`slim/get.sh`)把交付包 clone 到固定落點 `~/.lumos-slim` 再呼叫本腳本,解掉「使用者把交付包搬走/刪掉,全域指令就斷了」的既有問題;新增的 [[Systems/slim-uninstall-一行卸載]] 用本腳本複製出去的 `~/.local/bin/lumos` 與 `~/.lumos-slim/scripts/lumos` 做 sha256 比對,判斷卸載對象是不是本腳本裝的那份
  DEP:scripts/test_lumos.py t_slim_install_no_project_touch｜t_slim_install_claude_md_idempotent
  TEST:t_slim_install_no_project_touch 16 checks 全綠(`python3 scripts/test_lumos.py -k slim_install`)——安裝器 rc0、除 CLAUDE.md 外 porcelain 無其他新增/修改檔案、.git/config 不變、sentinel 外既有內容 byte-equal(含嚴格前綴比對)、sentinel 確實附加、全域指令已裝、skill 實體複製非 symlink、不裝 Claude hook、既有一般檔碰撞拒絕 rc2、既有檔內容未被動;t_slim_install_claude_md_idempotent 5 checks 全綠——重跑(帶 --force)後仍只有一塊 sentinel 且與第一次 byte-equal
verified_by:
  - "[[Verification/2026-07-31_slim-install安裝器落地]]"
  - "[[Verification/2026-07-31_公開精簡版交付]]"
  - "[[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]]"
  - "[[Verification/2026-07-31_slim-claude-md注入]]"
related:
  - "[[Systems/slim-get-一行安裝]]"
  - "[[Systems/slim-uninstall-一行卸載]]"
---
# slim-install-安裝器

公開精簡版交付前的機器層安裝器。隨交付包一起走(`$(dirname "$0")` 定位自身,不吃路徑參數),做三件事:①裝全域 `lumos` 指令 ②實體複製 `skills/lumos-project-notes` 到 `~/.claude/skills/`(非 symlink,交付包可被刪掉/搬走後 skill 仍在)③(★2026-07-31 使用者裁定變更,推翻原「不注入/更新任何 CLAUDE.md」的裁定★)在執行目錄(專案根)的 `CLAUDE.md` 檔尾,用專屬 sentinel `<!-- LUMOS-SLIM:START/END -->` append-only 附加一段「怎麼解析圖譜標籤」教學。**裁定範圍刀**:舊裁定禁的是完整版 `init`/`update` 那種「覆蓋 sentinel 之間既有紀律區塊」;新裁定開的是「只在檔尾附加、sentinel 以外一個位元組都不動」,且 sentinel 刻意與完整版不同名,不會被完整版 `init`/`update` 誤判成自己的區塊而覆蓋。**只動使用者 `$HOME` 與這一份 CLAUDE.md,不碰專案其餘任何檔案**——本 Task 最重要的產出是反誤傷測試 `t_slim_install_no_project_touch`(2026-07-31 換形狀:原斷言「worktree porcelain 為空」已因裁定變更不成立,改斷言「除 CLAUDE.md 外無其他新增/修改檔案 + sentinel 外內容 byte-equal + `.git/config` 前後相同」)。仍明確不做:不 scaffold 圖譜、不 vendor 工具進專案、不設 `core.hooksPath`、不裝任何 Claude hook。詳見 [[Projects/公開精簡版_實作計畫]] Task 3、Task 8(CLAUDE.md 注入裁定變更)。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-3-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此);spec [S4-c] 見 [[Projects/公開精簡版_計劃]]。
