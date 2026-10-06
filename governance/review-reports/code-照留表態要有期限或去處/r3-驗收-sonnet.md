severity: minor

## F1 測試 docstring 的翻紅釘編號沒跟著挪
severity: minor
blocking: 否
引句:「翻紅釘:拿掉 _drift_route_open 的判斷 → ②③④紅;拿掉同一篇檢查 → ⑥紅。」
說明:新增案例後,同一篇檢查的斷言已改成 ⑦,⑥ 變成「已收尾的計劃」;docstring 仍寫「同一篇 → ⑥紅」,也沒提「拿掉 `status not in _DRIFT_CLOSED` → ⑥紅」。只是註解過期,斷言本身沒對錯對象。file: `scripts/test_lumos.py`(t_drift_ack_routed_rejects 的 docstring)

## 件 1 驗證(臨時副本實跑)
severity: clean
blocking: 否
引句:「("Projects/做完_計劃", "已收尾的計劃")), 1):」
說明:在 mktemp 副本把 `_drift_route_open` 的 `and status not in _DRIFT_CLOSED` 拿掉、清 pycache 後跑,⑥ 翻紅(rc=0,表態被寫入),①~⑤ 仍綠;原版 8 條全綠。補的案例確實守住該分支。⑦⑧ 跟著紅是連帶效應:⑥ 多寫了一筆,讓 `len(_ra_rows(root)) == n0` 不成立,同時它們的 rc 都是 2、訊息也對(同一篇、c2 限制),所以不是漏驗。

## 件 2 驗證(編號挪動)
severity: clean
blocking: 否
引句:「check(f"{'①②③④⑤⑥'[i - 1]}--tracked-in 指到{why}:rc2 不寫」
說明:迴圈 6 個元組對應 6 個圈號,新案例在最後一位,i=6 取 ⑥;⑦同一篇、⑧c2 的標籤與其下斷言內容一一對應,沒有錯位或漏驗。

總結:補的案例確實會在拿掉 `status not in _DRIFT_CLOSED` 時翻紅、編號無錯位,只剩 docstring 翻紅釘編號過期一條 minor,無 blocking。
