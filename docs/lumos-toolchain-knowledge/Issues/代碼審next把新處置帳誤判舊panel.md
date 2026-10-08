---
type: issue
status: open
created: 2026-10-04
updated: 2026-10-04
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/loop-engineering
summary: |-
  FLAG:TECHNICAL
  DECISION: 新多席代碼審暫用 loop status --disposal 判定，後續輪人工派工並保存快照；修正 next 讀帳後撤除。
  PITFALL: 2026-10-04 code-probe-boundary-remediation 的 r1 處置閘 PASS，loop next 卻把帶 round 的新帳送進已退場 panel 閘而 rc2。出處本案命令重現；回歸入口為同帳的 next 與 status --disposal 對照。
related:
  - "[[Projects/探針隔離與清理收斂_計劃]]"
---
# 代碼審next把新處置帳誤判舊panel

症狀：`python3 scripts/lumos loop status code-probe-boundary-remediation --disposal --spec docs/lumos-toolchain-knowledge/Projects/探針隔離與清理收斂_計劃.md --repo .` 對 r1 顯示 `DISPOSAL GATE PASS`；同帳執行 `python3 scripts/lumos loop next code-probe-boundary-remediation --spec docs/lumos-toolchain-knowledge/Projects/探針隔離與清理收斂_計劃.md --repo .` 卻 rc2，印「panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放」。日期同本次驗證，兩個命令使用同一個已記錄的迴圈。

根因線索：`cmd_loop_next` 只見有 `--round` 就把帳判成 `panel_fmt`，在查下一輪時仍走 `_loop_status_panel` 的退場檢查；新處置帳為了多席全輪清點又必須帶 `--round`。這是 `next` 的讀帳路由與 `--disposal` 收斂閘不一致，不能以修改 append-only 帳本掩蓋。暫時以明確的 `loop status --disposal` 判定，每輪另凍結快照、人工指定席位；不把 `next` rc2 說成代碼審 FAIL 或新增審查輪。

修正時以同帳形狀建立測試：一輪只有一筆處置載體、其餘席只留嚴重度/報告，`status --disposal` 可判而 `next` 應吐後續動作或已收斂狀態，不應呼叫退場 panel 閘。重驗入口是下次修改 `cmd_loop_next` 或再開新多席代碼審；兩命令一致且測試通過後關閉本 Issue。
