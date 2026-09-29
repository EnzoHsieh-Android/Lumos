severity: major

三問結論:
1. 分層與依賴方向:新碼(_drift_row_unread、_DriftNames 改版)都放在 _drift_* 同一段、由 _drift_probe_check/_drift_probe_candidates/_drift_probe_scan 呼叫,借用 _esc_clean、_note_unreadable、link_target,沒有跨層直呼。已看,無 finding。
2. 命名與錯誤處理:_drift_row_unread、_drift_bad_note 命名與 _drift_* 一族一致;讀不出一律回 None/空清單的編碼與 _DriftProbeTree 一致。已看,無 finding。
3. 第二種做法:見 F1、F2。

## F1 「完整提交編號」的判定式又在 _drift_list 內聯寫了第三份
severity: major
blocking: 是 — 同一件事(認 40/64 碼提交編號)兩處以上各寫一份而無機械守一致,接手的人要猜哪份為準
引句:「if not (isinstance(where, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", where)):」
1. 專案已有模組層常數 _LENS_SHA_RE(認 40 或 64 碼)與 _ZERO_SHA_RE(SHA-1/SHA-256 全零),專門處理「兩種雜湊都要認」,還有 _lens_full_sha 包裝。
2. 這份 diff 為了同一需求(SHA-256 也算)不重用它,改在函式內聯手寫另一條正則;日後再有第三種寫法或改法,這兩處不會一起動,也沒有測試守它們一致。
3. 修法:直接用 _LENS_SHA_RE.fullmatch(where)(模組層常數在呼叫時已定義,不涉及先後順序)。
file: `scripts/lumos:31912`(_LENS_SHA_RE)、`scripts/lumos:31942`(_ZERO_SHA_RE)、`scripts/lumos:26530`(_drift_list)

## F2 _drift_row_unread 把「條件指到哪個檔或筆記」的解析又抄了一份
severity: major
blocking: 是 — 「一個條件碰到哪支檔/哪篇筆記」的規則現在散在四處各自手寫,改一處另幾處不會跟著變(這份 diff 前一輪就是因為點名範圍與判定範圍不一致才被抓)
引句:「rel = env.resolve(link_target(v.partition("=")[0].strip())) if env is not None else None」
引句:「path = v.rsplit("::", 1)[0].strip() if "::" in v else ""」
1. status 那段(resolve + notes.get + _note_unreadable)與 _drift_probe_one 的 status 分支逐步相同;帶路徑 symbol/test 的拆 path 與 _DriftProbeTree.prefetch、_drift_probe_cond_candidate、_DriftProbeTree.one 的 `rsplit("::", 1)` 是同一件事的第三、第四份。
2. 這份新函式只是「判不了」時的點名,但它要跟真正判定的邏輯完全同範圍才點得準;現在靠人記得兩邊一起改,沒有共用函式也沒有測試守一致(t_drift_code_review_yi_r4_regressions 只驗特定情境)。
3. 修法:從 _drift_probe_one 與 _DriftProbeTree.one 抽出「條件 → 指到的路徑/筆記」一支共用函式,判定與點名都用它。
file: `scripts/lumos:26706`(_drift_probe_one status 分支)、`scripts/lumos:26631`(prefetch)、`scripts/lumos:26768`(_drift_probe_cond_candidate)

不對齊共 2 條,其中 major 2 條
