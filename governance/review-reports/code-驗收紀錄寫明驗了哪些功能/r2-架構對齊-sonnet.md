severity: minor

## 第 1 問 分層與依賴方向
結構對。三條上輪的發現都已收斂:`lumos stale` 改走 `_verification_status`,跟 doctor 同一支口徑;孤兒推薦改成呼叫端解析一次、以 `vt=` 傳入。多掛提醒呼叫 `_drift_sh`/`_esc_clean`:兩者都在同一支單檔 CLI 裡,doctor 內已有大量 `_esc_clean(..., _DOCTOR_LINE_MAX)` 先例(`scripts/lumos:3614`),`_drift_sh` 由 drift 段定義(`scripts/lumos:33333`)、doctor 段(`scripts/lumos:1601`)跨段呼叫,同檔單向、無新依賴,不算跨層。
對照引句:「vt=_vt)」前一行 `sug = _suggest_systems_for_orphan(env, o, notes[o], vt=_vt)`。

## 第 2 問 命名與錯誤處理
`cap`、`vt`、`_cap` 與鄰居命名(`_vt`、`_SOFT_CAP`、`_verbose`)風格一致。`system_refs` 濾空值只在 `_verification_system_targets` 做一次,空清單仍走既有「讀不出任何一項」寫壞路徑,沒有另起錯誤處理。多掛提醒套 `_esc_clean(..., _DOCTOR_LINE_MAX)` 與同段 `sr_bad` 一致。
對照引句:「sr_extra.append(_esc_clean(f"{sys_rel} 掛了 [[{vrel[:-3]}]]」。

## 第 3 問 第二種做法
`warn(cap=)` 與 `warn_soft` 的 `_SOFT_CAP`/`_verbose` 確實是兩套封頂:`warn_soft` 預設封 3、`--verbose`/`--ci` 全列、尾行「另 N 條(lumos doctor --verbose 看全部)」;`warn(cap=20)` 固定數字、不看 `_verbose`、尾行「另 N 項」且不提 `--verbose`。這是 F1。但行為等同舊的呼叫端寫法(本來就固定 20、不看 verbose),且 `warn` 與 `warn_soft` 本來就分「硬/軟」,所以只列 minor。
其餘:status 判斷口徑只剩 `_verification_status` 一套;孤兒解析只剩一次;沒有新增第三種。

## F1 warn 的 cap 不看 _verbose,尾行措辭也跟 warn_soft 不同
severity: minor
blocking: 否
引句:「shown = list(lines) if cap is None else list(lines)[:cap]」
file: `scripts/lumos:1435`(對照 `scripts/lumos:1469` 與 `scripts/lumos:1456`)
1. `warn_soft` 的封頂受 `_verbose = verbose or ci` 控制(註解寫「CI 日誌要完整」);`warn(cap=20)` 在 `--ci` 下仍會截成 20 項,CI 日誌拿不到全部寫壞的 system_refs。舊寫法也這樣,但現在變成通用參數,往後別段會沿用。
2. 尾行「… 另 N 項」vs `warn_soft` 的「… 另 N 條(lumos doctor --verbose 看全部)」,同一支 doctor 內兩種措辭。
3. 建議:`cap` 在 `_verbose` 時視為 None(`warn` 定義在 `_verbose` 之前,需把 `_verbose` 提到 `warn` 前),尾行措辭對齊。
⚠
判不準是否要升 major:若專案把「CI 日誌完整」視為載重規則,`--ci` 下被截就是第二種做法;我只看到註解宣稱,沒查到有測試釘它。

不對齊共 1 條,其中 major 0 條
