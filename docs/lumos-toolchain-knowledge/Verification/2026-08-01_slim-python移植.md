---
type: verification
status: pass
date: 2026-08-01
valid_under: "分支 main;slim/install.py + slim/uninstall.py 現行版本(IS_WIN = os.name==\"nt\" or LUMOS_SLIM_SIMULATE_WINDOWS==\"1\");slim/install.sh、slim/uninstall.sh、slim/install.ps1、slim/uninstall.ps1、slim/get.ps1 現行版本;scripts/slim-gen.py 組包清單含全部新檔;Python3 stdlib 零依賴前提不變。★2026-08-03 更新:本標記已兌現——真機三輪驗證(v1.3/v1.4/v1.5)完成,v1.5 一次通過;逐項「有證據 vs 仍無證據」對照見 [[Verification/2026-08-03_Windows真機三輪驗證通過]] 與 slim/README.md。★本節點原文保留不改★(它記的是當時的狀態),但★不得再拿本段當「Windows 未驗證」的依據★。★ ★Windows 分支僅靠環境變數注入驗過分支邏輯,未在真機 Windows 上跑過★,見下方〈測不到什麼〉"
revalidate_when: "改動 install.py/uninstall.py 的 IS_WIN 分支(_install_cli 的 shim 產生邏輯、PATH 提示訊息)、改動 install.sh/uninstall.sh/install.ps1/uninstall.ps1/get.ps1 五支薄殼的參數轉發方式、改動 scripts/slim-gen.py 的組包清單、或未來真的拿到 Windows 機器做真機驗證後(屆時要把本節點與 slim/README.md 的『未驗證』標記一併更新,不能讓已驗證的部分繼續掛著誠實標記)"
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/公開精簡版_實作計畫]]"
summary: |-
  TEST:`python3 scripts/test_lumos.py -k slim` 253 checks 全綠(40 支 t_slim_* 函式;`t_slim_(install|uninstall|get)*` 系列 19→24,新增 5 支:2 支薄殼轉發參數獨立單元測試 + 3 支 Windows 分支邏輯測試)。既有 19 支斷言一條未鬆——逐條改成驗 Python 實作(`bash install.sh`/`uninstall.sh` 透過薄殼呼叫 `install.py`/`uninstall.py`),行為斷言字串/rc/檔案狀態全部保留原樣。
  VERIFY:[[Systems/slim-install-安裝器]]、[[Systems/slim-uninstall-一行卸載]]、[[Systems/slim-gen-生成器]]、[[Systems/slim-get-一行安裝]]、[[Systems/slim-readme]] 的安裝/卸載邏輯從 bash-only 搬成 Python(stdlib only)+ 薄殼(`.sh`/`.ps1`),讓 Windows 真的能用——完整搬移對照表、Windows 分支測到什麼/沒測到什麼、發現的一個真 bug(備份路徑秒級時間戳碰撞)見報告 `.superpowers/sdd/公開精簡版_實作計畫/task-13-report.md`。
related:
  - "[[Verification/2026-08-03_Windows真機三輪驗證通過]]"
---
# 2026-08-01_slim-python移植

## 為什麼要做

精簡版要交給離職接手者,接手者不保證用 macOS/Linux。原本 `slim/install.sh`(293 行)、`slim/uninstall.sh`(246 行)、`slim/get.sh`(56 行)**全是 bash**,Windows 上跑不了——這是原設計的已知缺口(當時裁定「凍結快照,Windows 待補」)。

## 搬移原則:單一邏輯來源,`.sh`/`.ps1` 只當薄殼

不接受「盲寫一份 PowerShell,兩份邏輯各自維護」——那會複製 Task 8~12 六輪代碼審抓到的同一類問題(邏輯只改一邊、另一邊悄悄漂移),而且這台開發機沒有 PowerShell,寫了也驗不了。改成:

- `slim/install.py`、`slim/uninstall.py` ★承載全部邏輯★(stdlib only)。
- `slim/install.sh`、`slim/uninstall.sh`、`slim/install.ps1`、`slim/uninstall.ps1` 都只做兩件事:①定位套件目錄(`.sh` 保留原本解 symlink 鏈的迴圈;`.ps1` 用 `$MyInvocation.MyCommand.Path`)②挑一支可用的 `python3`/`python` 直譯器,把參數原樣轉發過去。
- `slim/get.sh` 邏輯不變(呼叫 `install.sh`);新增 `slim/get.ps1`,邏輯逐步對照 `get.sh` 翻譯(clone/pull 到固定落點 `~\.lumos-slim` → 呼叫 `install.ps1`),先例是本 repo 完整版根目錄的 `get.ps1`(12 行,直接把工作丟給 `python scripts/lumos`)。

**移植到 Python 順帶消掉的 bug 類別**:
1. 原 bash 版本 `install.sh:207` 曾因為算 CLAUDE.md 寫入路徑用素樸 `$(pwd)`、守衛用 `$(pwd -P)`(見 Task 12 修復)兩處路徑表示法不一致翻過車。Python 的 `Path.cwd()` 底層就是 `os.getcwd()`,一律回傳實體路徑,沒有第二種「邏輯路徑」表示法可以拿來跟它打架——這整類 bug 結構性消失,不是修好,是問題不存在了。`t_slim_install_symlink_cwd_audit_path_matches_write_path` 保留下來當反事實確認(docstring 已更新說明)。
2. `uninstall.py` 原本沿用 bash 版「找不到 sha256sum/shasum 就 rc2」的分支;Python `hashlib` 是標準庫必然存在,這個失敗模式不會發生,故未保留對應分支。

## Windows 支援與★測不到什麼★(誠實邊界)

讀 `scripts/lumos` 的 `_IS_WIN`/`cmd_install`/`_link_or_copy` 分支照做:

- 全域指令:Unix 直接複製 `scripts/lumos` 到 `~/.local/bin/lumos`(chmod +x)。Windows 額外複製一份同內容到 `~/.local/bin/lumos`(不 chmod)、再產生 `~/.local/bin/lumos.cmd` shim——shim 內容用 `%~dp0`(自己所在目錄)相對定位,★不寫死 PKG 絕對路徑★,維持與 Unix 版一致的「複製後與交付包解耦」特性。manifest 的 `bin_sha256` 記的是 `lumos`(內容副本)的雜湊,兩平台語意一致。
- skill 目錄:精簡版一律實體複製,不像完整版建 symlink/junction,Windows/Unix 共用同一段程式碼;備份時用 `Path.rename()`(只動目錄項本身,不像 `shutil.move` 可能跟進 junction target)。
- PATH 缺失提示訊息分平台(Windows 講「系統環境變數」,Unix 講 shell 設定檔)。

這台開發機是 macOS,沒有 Windows/PowerShell,**Windows 路徑沒有做過真機驗證**。`install.py`/`uninstall.py` 的 `IS_WIN` 可透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 環境變數注入,讓同一份 Python 程式碼在非 Windows 機器上走 Windows 分支——`t_slim_install_windows_creates_cmd_shim`/`t_slim_install_windows_path_hint_message`/`t_slim_uninstall_windows_removes_paired_files` 三支測試驗證的是**分支邏輯本身**(產生 `.cmd` shim、不呼叫 chmod、PATH 提示文字分平台、成對移除),★測不到★:`mklink`/真實 junction、`cmd.exe`/PowerShell 執行 `.cmd` 的真實行為、Windows PATH 環境變數的真實生效方式、`install.ps1`/`uninstall.ps1`/`get.ps1` 這三支 `.ps1` 薄殼本身有沒有語法錯誤或執行原則(ExecutionPolicy)問題。`slim/README.md`〈支援平台〉與本節點 `valid_under`/`revalidate_when` 都留了同款誠實標記。

## 發現的真 bug:備份路徑秒級時間戳碰撞

`_install_skill`/uninstall 的 skill 目錄備份原本用 `time.strftime("%Y%m%d%H%M%S")`(秒級解析度)組 `.bak.<timestamp>` 路徑,直接沿用 bash 版 `date +%Y%m%d%H%M%S` 的做法。但 bash 的 `mv SRC DST` 若 `DST` 已存在且是目錄,語意是把來源「搬進」該目錄(不報錯);Python 的 `Path.rename()` 對「目的地是已存在的非空目錄」語意不同——直接拋 `OSError: Directory not empty`。`t_slim_install_backup_survives_idempotent_reinstall`(先 `--force` 重裝一次觸發一次備份、緊接著跑一次卸載觸發第二次備份,兩次可能落在同一秒)實測踩到這個碰撞。修法:`_unique_backup_path()` 遇碰撞時遞增後綴(`.bak.<timestamp>.1`、`.2`…),不改變既有測試依賴的 `.bak.*` glob 樣式。`install.py`/`uninstall.py` 都套用同一個 helper。

## 怎麼驗證的

- `python3 scripts/test_lumos.py -k slim`:253 checks 全綠(見上方 summary TEST:)。
- 手動 end-to-end smoke test(不在自動化套件內,人工跑一次):`scripts/slim-gen.py` 重新生成 `dist/`,在隔離的假 `$HOME`+假專案(`git init`)下跑 `dist/install.sh` → 確認 `lumos --help` 可執行、CLAUDE.md 精簡版區塊已插入 → 跑 `dist/uninstall.sh` → 確認 CLAUDE.md 回到安裝前原文、`~/.local/bin/` 清空。跑完即刪暫存目錄。
- `scripts/slim-gen.py` 組包清單機械鎖(`t_slim_gen_dist_ships_entrypoints`)含全部新檔(`install.py`/`uninstall.py`/`install.ps1`/`uninstall.ps1`/`get.ps1`),防重蹈 Task 6 漏 `get.sh`/`uninstall.sh` 的覆轍。
