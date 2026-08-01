---
type: verification
status: pass
date: 2026-07-31
valid_under: "分支 feat/public-slim-handoff,slim/install.sh 與 slim/uninstall.sh 現行版本(manifest 身分證 + 四步驟互不阻擋設計);Python3 stdlib + bash 零依賴前提不變"
revalidate_when: "改動 slim/install.sh 的 manifest 寫入邏輯、slim/uninstall.sh 的四步驟判斷式、或 uninstall rc 語意三段式時"
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/公開精簡版_計劃]]"
summary: |-
  TEST:`python3 scripts/test_lumos.py -k slim` 198 checks 全綠(修復前先用 `git stash` 還原成舊版 install.sh/uninstall.sh 重跑同一批新測試,確認翻紅——`t_slim_uninstall_direct_install_restores_claude_md`/`t_slim_uninstall_bin_refusal_does_not_block_claude_md_restore`/`t_slim_uninstall_refuses_foreign_bin` 共 8 checks 失敗,非稻草人;`git stash pop` 回補修復後同批測試全綠)。端到端實跑(dist/ 重新生成,clone 一份 Landmark 到 /tmp、跑 `dist/install.sh`、再跑 `dist/uninstall.sh`):CLAUDE.md 與安裝前 byte-equal、`git status --porcelain` 全空——見 `.superpowers/sdd/公開精簡版_實作計畫/task-10-report.md` 完整輸出。
  VERIFY:[[Systems/slim-uninstall-一行卸載]] 的兩條新合約(bin 比對基準改用 manifest+備援、四步驟互不阻擋)與 [[Systems/slim-install-安裝器]] 的新合約(manifest 身分證寫入)。
---
# 2026-07-31_slim-uninstall步驟獨立化與manifest基準修復

## 缺陷(端到端實測重現,非推論)

`slim/uninstall.sh` 舊版用 `~/.local/bin/lumos` 與 `~/.lumos-slim/scripts/lumos` 的 sha256 比對當 bin 安全檢查,且把這個檢查失敗當一票否決(`exit 2` 中止整支腳本)。但 `~/.lumos-slim` 只有走 `get.sh`(一行安裝)才會存在——接手者若照 README 也在教的另一條路(直接 clone 交付包、跑包內 `install.sh`),`~/.lumos-slim` 不存在,①的比對基準必然缺失,腳本在還沒碰到步驟④(CLAUDE.md 完整版還原)前就整支中止。接手者從此卸載不掉,而且舊訊息說「這可能是你自己的東西」在這個情境下是誤導。

## 修法

①`slim/install.sh` 裝 bin 時多寫一份身分證 manifest(`~/.local/share/lumos-slim/manifest.json`,含安裝當下的 `bin_sha256`),不放使用者專案、不依賴 `~/.lumos-slim` 存在。②`slim/uninstall.sh` 的四個清理步驟(bin／skill 目錄／`~/.lumos-slim`／CLAUDE.md sentinel)改成各自獨立判斷、各自執行、互不阻擋,全部跑完才彙總報告、決定 rc(語意比照 `lumos doctor --ci` 三段式:0=全成功/本來沒裝,1=安全性跳過非硬錯誤,2=真正錯誤)。錯誤訊息同步修正:「基準缺失」與「內容真的不符」分開講。

## 紅→綠(TDD)

新增/改版測試詳見 [[Systems/slim-uninstall-一行卸載]] 的 summary TEST 行。修復前(`git stash` 還原舊版腳本)重跑 `python3 scripts/test_lumos.py -k slim_uninstall`:8 checks 失敗,涵蓋核心回歸(直接跑 install.sh 不經 get.sh 場景)、步驟互不阻擋(bin 拒絕不擋 CLAUDE.md 還原)、既有測試的 rc 語意改版斷言。修復後(`git stash pop`)同批全綠。

## 端到端實跑(收尾)

重新生成 `dist/`,clone 一份 Landmark 到 `/tmp`(用完即刪,未寫回 `/Users/enzo/backend/LandmarkMember`),直接跑 `dist/install.sh` 再跑 `dist/uninstall.sh`,斷言 CLAUDE.md 與安裝前 byte-equal、`git status --porcelain` 全空。完整輸出見 `.superpowers/sdd/公開精簡版_實作計畫/task-10-report.md`。
