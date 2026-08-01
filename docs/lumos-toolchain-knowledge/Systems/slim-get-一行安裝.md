---
type: system
status: done
created: 2026-07-31
updated: 2026-08-01
tags:
  - type/system
  - status/done
summary: |-
  FLOW:`curl -fsSL <raw-url>/get.sh | bash` → 檢查 `git` 存在(找不到→清楚錯誤訊息+rc2,不留 traceback) → `~/.lumos-slim` 已是合法 git repo(有 `.git`)→ `git pull --ff-only`(冪等更新)｜已存在但非 git repo→拒絕、rc2、印訊息｜不存在→`git clone` 首次安裝 → 檢查 `install.sh` 存在 → 執行 `~/.lumos-slim/install.sh "$@"`(額外參數如 `--force` 原樣轉發)
  KEY:★固定落點理由★——舊版 [[Systems/slim-install-安裝器]] 用 `$(dirname "$0")` 定位自身;透過 `curl | bash` 執行時 `$0` 是 bash 本身/`/dev/stdin`,沒有穩定檔案位置可定位。固定 `~/.lumos-slim` 給包一個穩定的家,也讓 [[Systems/slim-uninstall-一行卸載]] 有東西可以拿來做 sha256 內容比對(見該節點的硬合約)
  KEY:★冪等的精確定義★——「不炸」指的是不出現 `git clone` 對非空目錄的爆炸式錯誤(`already exists and is not an empty directory`)。第二次執行呼叫到的 `install.sh` 仍有自己既有的碰撞保護(未帶 `--force` 時偵測到 `~/.local/bin/lumos` 已存在會拒絕、rc2)——這是 install.sh 既有的、刻意的安全行為,不是 get.sh 冪等性的破口;`get.sh` 本身把 `--force` 原樣轉發即可讓使用者一次到位重跑
  KEY:與本 repo 根目錄既有的 `get.sh`/`get.ps1`(完整版 Lumos 遠端一鍵裝,clone `EnzoHsieh-Android/Lumos` 後委派 `bootstrap`,見 [[Systems/lumos-cli-lifecycle]])是**兩支獨立腳本、不同交付對象**——本節點記的是 `slim/get.sh`,目標 repo 是精簡版交付庫 `citrus-android-developer/Citrus_Lumos`,只做「clone/更新+執行 install.sh」兩件事,不含 bootstrap 的專案層四分流/`_confirm_tty`/hooks 接線等機器層以外的邏輯——★這是刻意的功能子集,不是殘缺★
  KEY:`REPO_URL` 可用環境變數 `LUMOS_SLIM_REPO_URL` 覆蓋(測試用,指向本地 git repo 路徑避免打真網路);生產預設寫死 GitHub URL,不吃命令列參數覆蓋(降低被誤導向惡意 repo 的攻擊面)
  KEY:★2026-08-01 補追加 Task 13——新增 Windows 對應腳本 slim/get.ps1,slim/get.sh 本身邏輯不變★:`slim/get.sh` 呼叫的 `install.sh` 從「承載全部邏輯」改成「薄殼轉發給 `install.py`」(見 [[Systems/slim-install-安裝器]]),但 `get.sh` 自己的 clone/pull/檢查/呼叫邏輯完全沒動——它本來就只負責「把套件放到固定落點+呼叫 install.sh」,install.sh 內部怎麼實作跟它無關。新增 `slim/get.ps1` 逐步對照翻譯同一套邏輯(clone/pull 到 `$HOME\.lumos-slim` → 呼叫 `install.ps1`),先例正是本節點 KEY 行(上)提到的本 repo 根目錄完整版 `get.ps1`(12 行,直接把工作丟給 python)——★這台機器沒有 Windows/PowerShell,`get.ps1` 沒有真機驗證過★,只是逐行對照 `get.sh` 翻譯,見 [[Verification/2026-08-01_slim-python移植]] 的誠實標記。
  DEP:slim/get.sh｜slim/get.ps1(新增,Windows 對應)｜slim/install.sh(被呼叫執行)｜slim/install.ps1(新增)｜scripts/test_lumos.py t_slim_get_idempotent｜t_slim_get_no_git
  TEST:t_slim_get_idempotent 7 checks 全綠——首次執行 rc0(git clone 到位)、第二次執行不出現 clone 式爆炸訊息且 stderr 無 traceback、`.git` 目錄未被破壞、帶 `--force` 轉發給 install.sh 可完整跑完 rc0;t_slim_get_no_git 3 checks 全綠——限縮 `PATH` 模擬 git 缺失,斷言 rc2+清楚錯誤訊息(非 traceback)+`~/.lumos-slim` 未被建立(`python3 scripts/test_lumos.py -k slim_get`)
related:
  - "[[Systems/slim-install-安裝器]]"
  - "[[Systems/slim-uninstall-一行卸載]]"
verified_by:
  - "[[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]]"
  - "[[Verification/2026-08-01_slim-python移植]]"
---
# slim-get-一行安裝

公開精簡版的一行安裝入口(`slim/get.sh`)。解決 [[Systems/slim-install-安裝器]] 原本「必須先手動拿到交付包才能跑 `install.sh`」的問題:`curl -fsSL <raw-url>/get.sh | bash` 把交付包 clone 到固定落點 `~/.lumos-slim`,再自動執行包內的 `install.sh`。已存在時走 `git pull` 冪等更新,不會對非空目錄硬 `git clone` 炸掉;`git` 指令本身不存在時給清楚錯誤訊息而非 Python/bash traceback。詳見 [[Projects/公開精簡版_實作計畫]] Task 6(一行安裝／卸載)。

固定落點 `~/.lumos-slim` 同時是 [[Systems/slim-uninstall-一行卸載]] 判斷「`~/.local/bin/lumos` 是不是我們裝的那份」的比對基準——兩支腳本靠這個路徑耦合,改動路徑常數要兩邊同步。
