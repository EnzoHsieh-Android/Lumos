---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
summary: |-
  FLOW:先寫 `t_slim_readme_assertions`(紅)→ 寫 `slim/README.md` 滿足 7 項必要內容 → 跑測試轉綠 → 跑 `slim-scan.py` 掃 README 本身,調整措辭到 rc0(README 不像 skill 文件允許留假陽性候選,測試斷言死板要求 rc0)
  KEY:7 項必要內容=①怎麼裝(`install.sh`)+怎麼確認(`lumos --help`)②進場三步 search→context→contracts ③frontmatter 四鐵則(逐字轉錄自 reference.md)④合約鏈是什麼+doctor 為什麼擋+怎麼解 ⑤範圍聲明(功能子集,不含對抗審計;「移除的是入口不是全部程式碼」逐字句)⑥明講不要跑 install-hooks.sh、不要照 CLAUDE.md clone 完整版跑 install.sh,且誠實承認「本 README 壓不住專案自己的 CLAUDE.md」⑦凍結聲明(逐字句「凍結快照」)
  KEY:★掃描器對 README 要求 rc0,比 skill 文件嚴格★——skill 文件允許重跑後留候選只要能逐條說假陽性理由,但 README 的測試斷言直接判 `r.returncode == 0`,不接受任何候選殘留
  KEY:2026-07-31 Task 5 修正 `slim-scan.py` 的 prose 形態假陽性(見 [[Systems/slim-scan-掃描器]])後,安裝指令已改回慣用的 `./install.sh`——原本因「`/` 緊貼 `install` 前面、`.sh` 緊貼後面」撞裸散文誤判,遷就掃描器改寫成「用 `bash` 執行 `install.sh`」,那條遺留債已隨掃描器修正解除(舊 DEBT 標記已移除)
  DEP:scripts/test_lumos.py t_slim_readme_assertions｜scripts/slim-scan.py
  TEST:t_slim_readme_assertions 9 checks 全綠(`python3 scripts/test_lumos.py -k slim_readme`);`slim-scan.py slim/README.md` 獨立驗證 rc0(候選 0 條)
verified_by:
  - "[[Verification/2026-07-31_slim-skill與readme落地]]"
  - "[[Verification/2026-07-31_公開精簡版交付]]"
related:
  - "[[Systems/slim-scan-掃描器]]"
---
# slim-readme

公開精簡版交付內容之一:`slim/README.md`,新人 clone 到精簡版後唯一的自足說明文件(★不假設讀過完整版任何文件★)。涵蓋安裝、進場三步、frontmatter 鐵則、合約鏈與 doctor 解法、範圍聲明(功能子集非全部)、明講不要跑哪些(含「本 README 壓不住專案 CLAUDE.md」的誠實界線)、凍結聲明七項必要內容,每項都被 `t_slim_readme_assertions` 的內容斷言鎖住。詳見 [[Projects/公開精簡版_實作計畫]] Task 4。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-4-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此)。
