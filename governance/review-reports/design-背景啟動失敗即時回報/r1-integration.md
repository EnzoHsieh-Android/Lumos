severity: minor

F1：非 JSON CLI 模式未納入啟動失敗契約，照規格實作可退化成 rc 2 且沒有任何提示。

severity: minor

blocking: 否

引句:「應立即回 rc 2 與 JSON `spawn_error=true`、本次 `lock_path`、原 `range`」

file: `governance/review-reports/design-背景啟動失敗即時回報/r1-snapshot.md:31`

重現/因果：現行公開參數允許 `lumos dispatch-lens <range> --deadline 秒` 不帶 `--json`；隔離注入 `subprocess.Popen -> OSError("SECRET injected raw exception")` 後呼叫 `_lens_wait_or_warm(..., as_json=False, deadline=.01)`，目前得到 rc 5 並印出可操作的人話。S1 只定義 JSON 輸出，若依字面在失敗時一律回 rc 2，非 JSON 分支沒有任何必印文字，也沒有測試約束。應補非 JSON 固定提示及同一測試的 `as_json=False` 對照，且提示不得含原始例外。

CLI JSON／hook 分流、角色卡保留、原始例外隔離、舊鎖與 timeout 行為：已讀，除 F1 外無 finding。既有 `t_lens_stale_lock_reports_uncertainty` 與 hook timeout 測試通過。

總結: 最嚴重 severity medium，blocking 0 條。
