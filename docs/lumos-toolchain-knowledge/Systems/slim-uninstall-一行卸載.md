---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
summary: |-
  FLOW:`curl -fsSL <raw-url>/uninstall.sh | bash`(或裝好後直接跑 `~/.lumos-slim/uninstall.sh`)→ ①`~/.local/bin/lumos` 與 `~/.lumos-slim/scripts/lumos` sha256 比對,符合才 `rm -f`,不符→印訊息+rc2(除非 `--force`) → ②`~/.claude/skills/lumos-project-notes/` 先 `mv` 成 `.bak.<timestamp>` 備份,不直接 `rm -rf` → ③`~/.lumos-slim` 確認內含 `scripts/lumos`+`install.sh`(長得像我們的包)才 `rm -rf`,不像→保留印警告 → 全程只動 `$HOME` 下這三個路徑
  KEY:★INVARIANT★ 移除 `~/.local/bin/lumos` 前必先 sha256 內容比對 `~/.lumos-slim/scripts/lumos`,不符即拒絕(rc2)——防的是「使用者自己另外裝了一支同路徑的 lumos/或完全不相干的東西」被本卸載腳本誤刪;帶 `--force` 才允許跳過比對強制移除 [test:t_slim_uninstall_refuses_foreign_bin] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把移除改成無條件執行,綁定測試確實翻紅,非稻草人)
  KEY:★INVARIANT★ `~/.claude/skills/lumos-project-notes/` 移除前必先備份成 `.bak.<timestamp>`,不得 `rm -rf` 未備份——使用者可能在 skill 目錄裡塞過自己的筆記/修改,直接砍會造成不可逆資料損失 [test:t_slim_uninstall_backs_up_and_preserves_custom_files] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把備份改成直接 rm -rf,綁定測試確實翻紅)
  KEY:★絕不碰★清單(功能範圍外,不是「忘了做」)——任何專案目錄/repo、`~/.claude/settings.json`、`~/.claude/hooks/`、除了 `lumos-project-notes` 以外的任何其他 skill。三步判斷式全部只讀寫 `BIN`/`SKILL`/`PKG` 三個路徑常數,沒有任何一行觸及上述四類路徑,這是設計時的硬邊界,不是巧合
  KEY:判定 ① 失敗(sha256 不符且無 `--force`)時**立即 `exit 2` 中止全流程**,不會接著繼續備份 skill / 移除 `~/.lumos-slim`——「使用者的 `~/.local/bin/lumos` 疑似不是我們裝的」是強烈訊號,代表接下來對 `$HOME` 其餘路徑的假設也可能不成立,選擇整體保守而非「能刪的先刪」
  KEY:sha256 比對用 `command -v sha256sum`(Linux 常見)或退回 `shasum -a 256`(macOS 常見)——兩者都沒有時視同無法安全驗證,直接 rc2 中止,不會用「找不到就當作不符」或「找不到就跳過比對硬刪」這種降級路徑
  DEP:slim/uninstall.sh｜slim/install.sh(產生比對基準與備份對象)｜scripts/test_lumos.py t_slim_uninstall_backs_up_and_preserves_custom_files｜t_slim_uninstall_refuses_foreign_bin
  TEST:t_slim_uninstall_backs_up_and_preserves_custom_files 11 checks 全綠——先裝、塞使用者自訂檔進 skill 目錄、跑 uninstall,斷言備份存在、自訂檔內容原封不動地在備份裡、`settings.json`/`hooks/` 卸載前後皆不存在(從未被建立);t_slim_uninstall_refuses_foreign_bin 6 checks 全綠——把 `~/.local/bin/lumos` 換成使用者一般檔,不帶 `--force` 跑 uninstall 斷言 rc2 且該檔內容未被動、skill 目錄未被連帶備份/搬動,帶 `--force` 才允許移除(`python3 scripts/test_lumos.py -k slim_uninstall`)
related:
  - "[[Systems/slim-install-安裝器]]"
  - "[[Systems/slim-get-一行安裝]]"
verified_by:
  - "[[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]]"
---
# slim-uninstall-一行卸載

公開精簡版的一行卸載入口(`slim/uninstall.sh`)。給接手者「不想要就乾淨移除」的路,不用自己猜要刪什麼——安全紀律是這支腳本的重點,比功能本身重要,見上方兩條 ★INVARIANT★。用法與 [[Systems/slim-get-一行安裝]] 對稱:`curl -fsSL <raw-url>/uninstall.sh | bash`,或裝好後直接跑 `~/.lumos-slim/uninstall.sh`。詳見 [[Projects/公開精簡版_實作計畫]] Task 6(一行安裝／卸載)。

只動三個路徑(`~/.local/bin/lumos`、`~/.claude/skills/lumos-project-notes/`、`~/.lumos-slim`),每個路徑都先驗證「這真的是我們裝的東西」才動手——`~/.local/bin/lumos` 靠與 [[Systems/slim-get-一行安裝]] 固定落點下的 `scripts/lumos` 做 sha256 內容比對,`~/.lumos-slim` 靠結構特徵(含 `scripts/lumos`+`install.sh`)判斷。
