---
type: verification
status: pass
date: 2026-10-08
valid_under: macOS、Python 3.14、以 os.openpty 建立的無控制終端 session；不包含 Windows
revalidate_when: 改動 _confirm_tty 的 tty 開啟旗標、select 等待或 t_confirm_tty_unit 時
tags:
  - type/verification
  - status/pass
  - scope/platform
plan_refs:
  - "[[Projects/bootstrap一鍵對稱_計劃]]"
---
# TTY確認不取得控制終端驗證

## 結論

`t_confirm_tty_unit` 在修補前穩定走到第 2 階 pty 成功路徑後收到 SIGHUP，測試 runner 以 129 結束，第四個 timeout 控制沒有執行。原因是無控制終端的 session leader 用 `os.open(..., O_RDWR)` 開 pty slave 時可能取得它作 controlling terminal；關閉 pty 後 kernel 對該 session 發 SIGHUP。

`_confirm_tty` 開 tty 時加入平台有提供才使用的 `O_NOCTTY`。同一條既有測試修後完成六項斷言並以 rc0 結束，涵蓋 isatty 輸入、EOF fallback、pty 提示與 timeout；這不是以新測試重抄實作，而是讓原本已能翻紅的端到端控制跑到底。

本輪只建立 POSIX/macOS 資格。Windows 不使用這個旗標，仍沿既有平台驗證邊界。
