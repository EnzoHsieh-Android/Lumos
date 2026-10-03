severity: minor

## 三問

**1. 分層與依賴方向**
沒有跨層。新增的 `_system_ref_blank` 是 `_system_ref_item` 上方的純函式,由 `_system_ref_item` 與 `_verification_system_targets` 共用,取代原本內嵌的判法,方向是 doctor 檢查呼叫共用小函式,跟鄰居 `_typed_link_target` / `_system_ref_item` 一致。warn 的 cap 現在走 `_verbose`(`scripts/lumos:1443-1457`),跟 `warn_soft`(`scripts/lumos:1469-1483`)讀同一個閉包變數,同層、不新增依賴。上一輪的「兩套封頂規則」已收斂,驗收通過。
引句:「shown = list(lines) if (cap is None or _verbose) else list(lines)[:cap]   # --verbose/--ci 全列,同 warn_soft」
file: `scripts/lumos:1453`

**2. 命名與錯誤處理**
`_system_ref_blank` 的命名與 `_system_ref_item` 同前綴,docstring 帶代碼審出處,跟鄰居慣例一致。錯誤處理仍是回 `(None, 原因與改法)` 的元組,不丟例外,同既有做法。兩處小差異:(a) warn 的結尾句用「另 N 項」,warn_soft 用「另 N 條」(`scripts/lumos:1457` 對 `scripts/lumos:1481`),同一支 doctor 內兩種量詞;(b) `_system_ref_item` 開頭新增的空判斷與後面 `kind == "skip"` 分支(`scripts/lumos:31` 附近)訊息完全相同,形成兩條出口。
引句:「print(f"      … 另 {len(lines) - len(shown)} 項(lumos doctor --verbose 看全部)")」
file: `scripts/lumos:1457`

**3. 第二種做法**
照貼指令的處理:鄰居有 `scripts/lumos:31783` 用 `_esc_clean(…, 300)`、`scripts/lumos:33783` 用 `_esc_clean(…, 2000)`,兩者都仍是截斷(只是上限大)。本 patch 用 `100000` 等同「不截斷」,而把說明文字另外用 `_DOCTOR_LINE_MAX`(300)截。`100000` 在 `scripts/lumos:11925` 有先例(非指令場景),所以不算全新做法,但「指令一個上限、說明另一個上限」在 doctor 其他行(`scripts/lumos:3623`、`3746` 等一律整行 `_DOCTOR_LINE_MAX`)是新拆法,且 100000 是魔術數字、沒有具名常數。結構對(截斷在引號中間確實會害照貼卡住),屬 minor。

## F1 照貼指令用 100000 當「不截斷」,與鄰居 300/2000 的上限做法並存
severity: minor
blocking: 否
引句:「+ "改法:" + _esc_clean(f"lumos remove {_drift_sh(sys_rel[:-3])} verified_by {_drift_sh(a)}", 100000)」
file: `scripts/lumos:1610`
- 鄰居照貼指令用 300(`scripts/lumos:31783`)、2000(`scripts/lumos:33783`),本處用 100000,三個數字三種口徑,無具名常數。
- 建議:抽具名常數(例如 `_PASTE_CMD_MAX`)或註明為何此處必須不截斷;不擋。

## F2 warn 與 warn_soft 結尾量詞不同(項/條)
severity: minor
blocking: 否
引句:「…(lumos doctor --verbose 看全部)」
file: `scripts/lumos:1457`
- 對照 `scripts/lumos:1481` 是「另 N 條」。上輪要求「結尾句同 warn_soft」,措辭只對了一半(括號指路一致、量詞不同)。純文案,不擋。

不對齊共 2 條,其中 major 0 條
