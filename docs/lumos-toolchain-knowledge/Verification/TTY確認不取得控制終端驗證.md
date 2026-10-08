---
type: verification
status: pass
date: 2026-10-08
valid_under: macOS、Python 3.14;修補的防回歸只在測試子程序以新 session 啟動且沒有控制終端時才走得到(t_confirm_tty_no_ctty_session_survives 先斷言此現場);不包含 Windows
revalidate_when: 改動 _confirm_tty 的 tty 開啟旗標、select 等待、t_confirm_tty_unit 或 t_confirm_tty_no_ctty_session_survives,或測試執行器改變啟動 session 的方式時
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

**第五輪審查更正（2026-10-08）**：上段「同一條既有測試……讓原本已能翻紅的端到端控制跑到底」只在測試執行器本身是「沒有控制終端的 session leader」時成立。在一般終端機裡跑 `t_confirm_tty_unit`，拿掉 `O_NOCTTY` 仍是六項全綠（合約圖譜席與平台席各自重現）。所以另加 `t_confirm_tty_no_ctty_session_survives`：子程序以新 session 啟動，先斷言自己是 session leader 且開不了 `/dev/tty`，再走 pty 確認並關閉；拿掉 `O_NOCTTY` 時子程序收到掛斷、測試翻紅，修後通過。證據見 [[Verification/持久用量帳第五輪審查修補驗證]]。

本輪只建立 POSIX/macOS 資格。Windows 不使用這個旗標，仍沿既有平台驗證邊界。
