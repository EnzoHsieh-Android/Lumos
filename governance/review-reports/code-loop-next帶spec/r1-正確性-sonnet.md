severity: minor

## F1 loop next 改問處置閘後,唯讀指針會在治理資料夾追加寫 roster-alerts.log,重跑重複寫
severity: minor
blocking: 否
引句:「rc = cmd_loop_status(env, loop_id, spec=spec, repo=repo, disposal=True)」
file: `scripts/lumos:22775-22830`(`_loop_status_disposal` 內的 `_roster_tail` / `_severity_tail`,`readonly` 預設 False 時以 append 模式寫 `governance/review-reports/<編號>/roster-alerts.log`)
file: `scripts/lumos:12861`(`cmd_loop_next` 的 docstring 自稱「唯讀指針」,delegation 註解寫「靜默跑」)
1. 舊路徑問 panel 閘(`_loop_status_panel`),全檔唯二寫 roster-alerts.log 的地方都在處置閘裡,所以舊 loop next 不落任何檔。
2. 新路徑對新編號呼叫 `cmd_loop_status(..., disposal=True)`,沒傳 readonly,走到 `if not readonly: _roster_tail(); _severity_tail()`。
3. 重現:臨時 vault 記一輪 `canary record none`(報告標成輕微),再把報告檔改成重大,設 `LUMOS_PANEL_RETIRE_CUTOFF=2000-01-01`,連跑兩次 `lumos loop next <編號> --spec … --repo … --json`(兩次都 rc1、phase=plant-canary)。
4. 結果:`governance/review-reports/<編號>/roster-alerts.log` 出現兩行相同的 `2026-10-04 r1 severity_underreport:正確性-s`——每次呼叫 loop next 追加一行。這份帳是兩季覆核的計數來源,輪詢式使用 loop next 會把同一件異常灌水;而且 loop next 在 rc 非 0 時仍會留下這個副作用,使用者以為只是在問下一步。
5. 手動跑 `loop status --disposal` 本來就會寫,所以判定一致;問題只在 loop next 這個「靜默代問」原本不寫檔、現在變會寫。

## 已走過沒問題的範圍
- 判定一致性:loop next 的 `rounds`(`_loop_records`)與 cmd_loop_status 的 `rounds` 都濾掉 `kind=spec-gate`,`_panel_retired_for(rounds)` 看的 `rounds[0].ts` 兩邊同一筆,新舊判定不會分歧。
- 參數:處置閘需要的 spec、repo 都有傳;env 有傳(留痕、資安席、roster 尾端用);need/min_seats 傳了會被處置閘互斥擋,所以不傳是對的。roster 旗標只影響印出,不進判定。
- light:`not light` 擋掉,走原路徑;light 帶 round 在更前面已 rc2。legacy(無 round)與循序 code∧standard 帳 `panel_fmt` 為 False,原樣走舊 gate。混用帳在前面 `n_round not in (0,len)` 已 rc2。零筆帳在 `if not rounds` 先回 plant-canary,不會走到新判定。垃圾 ts(非日期)`_panel_retired_for` 回 False,走舊路徑。
- rc 對映:處置閘 rc2(壞行、一輪多處置帳、spec 讀不到)原樣 stderr + return 2;rc1 往下接 cap-reached / plant-canary,與舊路徑結構相同;rc0 才標 converged。
- converged 事件:disposal 與非 disposal 兩支互斥,每次呼叫只寫一筆,不重複;重跑 loop next 在 converged 時每次寫一筆是舊行為,非本 diff 引入。
- 測試:在舊程式上第一個 check(rc0 且無「panel 閘」字樣)會因 rc2 翻紅;新程式 3 項全綠(實跑 `-k loop_next_spec_uses_disposal`)。第三項(舊編號)新舊程式都會綠,只當回歸保護,不是翻紅釘,但有擋「誤把舊編號判成新」的方向。
- 圖譜鏡頭:未附固定席筆記段,不逐條答;本 diff 沒碰合約行文字。

只發現一處不影響判定、只影響副作用的缺口,其餘路徑走查後行為與手動 `loop status --disposal` 對得上。
