severity: blocker

### f1 表態核對例外把已查出的違規整批吞掉,壞設定讓該擋的推送靜默放行
severity: blocker
blocking: 是
file: `scripts/lumos:21424`
引句:「pidx = _platform_test_index(Path(repo_root))」
敘述:`.lumos/config.json` 帶 `platforms` 但語意不合法(如兩個平台沒設 `default_platform`——仍是合法 JSON,`cfg_broken` 只驗 JSON parse 抓不到)時,這行呼叫的 `load_platforms` 會拋 `ValueError`,一路穿出 `_dispositions_verdict`,被 `_codeloop_guard_verdict` 外層 `except Exception`(scripts/lumos:21572-21574)整包接住、把已收集的 `problems`(例如另一題 kt-coroutines 缺表態)整批丟棄、回傳 `blocked:false`。實測:同一份改動(kt-coroutines 缺表態、kt-dispatchers 用 `test:` 證據)在合法設定下 `lumos code-loop check` 正確判 `rc1` BLOCKED,把設定換成上述壞 `platforms` 後同一份改動變 `rc0`「✅ code-loop check: OK——可以推」,人讀輸出完全看不出設定壞掉、也看不出原本該擋的那題還缺表態。

### f2 code-loop dispositions 寫入時遇到同一種壞設定直接整支崩潰
severity: major
blocking: 是
file: `scripts/lumos:21690`
引句:「pdata = load_platforms(repo_root)」
敘述:`_cmd_codeloop_dispositions` 在驗證表態 JSON 形狀前先呼叫 `load_platforms(repo_root)` 且外面沒有 try/except;同一種壞 `platforms` 設定(合法 JSON、缺 `default_platform`)會讓它拋 `ValueError` 直接穿出 `main()`,印出完整 Python traceback、rc=1,不是文件承諾的「壞就 rc2 不寫並講原因」。實測:對著這種設定跑 `lumos code-loop dispositions disp.json --repo <repo>` 得到 unhandled `ValueError: 設定了 2 個平台,但沒說預設是哪個…` 的完整 traceback,使用者連表態都寫不進去、訊息也看不出是設定檔的問題。

### f3 治理帳裡缺 issue 的 todo 表態會把 dispatch-lens 整支打爆
severity: major
blocking: 是
file: `scripts/lumos:19622`
引句:「e.get("issue") + " " + str(e.get("reason") or "")」
敘述:`_lens_dispositions_lines` 對 `status=="todo"` 的表態做 `issue + " " + reason` 字串相加,若 `issue` 缺失(None)會直接 `TypeError`;marker 檔不在時「退治理帳按 kind 重建」這條路(`_codeloop_read_dispositions`,設計本身支援的正常路徑,`t_codeloop_dispositions_ledger_fallback` 就在測它)不會重新驗證形狀,一筆缺 `issue` 的歷史或外部寫入紀錄就會讓 `dispatch-lens` 整支拋錯而非優雅降級。實測:手灌一筆缺 `issue` 的 todo 表態進 `docs/.governance-log.jsonl`、刪掉 `governance/code-loop` marker 目錄後跑 `lumos dispatch-lens main..HEAD --repo <repo>`,得到 `TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'`、rc=1。

### f4 pre-push 逃生路文案把「表態沒答」的標準風險推送也講成「高風險」
severity: minor
blocking: 否
file: `scripts/hooks/pre-push:215`
引句:「高風險缺審查留痕的逃生路:先表態(上面的 dispositions 指令)」
敘述:表態閘 3.5 步不看 tier,tier=standard 的推送一樣能單純因為表態不完整被 `code-loop check` 判 `blocked`(reason_kind=dispositions);pre-push 現在對每個分支 ref 無條件叫 check,凡是 `cl_rc==1` 都印這行固定文案,把單純「效能檢核題沒答」的標準風險推送講成「高風險缺審查留痕」,跟真正的擋下原因對不上。

### f5 表態閘擋下時仍套用「合約測試真的紅了才該給」的 --skip-bound-tests 提示
severity: minor
blocking: 否
file: `scripts/lumos:21831`
引句:「真的跑不了(外部 DB 不在、環境缺)→ 留痕跳過」
敘述:這段只判斷 `bt.status=="red"` 與整體 `blocked`,沒檢查 `blocked` 是不是因為 bound tests 本身;`bound_advisory=True` 時 bt 紅本來就不會造成擋下,但若同一次 check 是因為表態閘(reason_kind=dispositions)才 `blocked=True`,`elif _st == "red":`(scripts/lumos:21830)一樣會印「留痕跳過:--skip-bound-tests」,對使用者是文不對題的補救指令——真正該做的是填表態,不是跳過合約測試。

### f6 --dispositions-template 沒比照 check 的 high-only 短路,對標準風險推送多要求答題
severity: minor
blocking: 否
file: `scripts/lumos:17190`
引句:「if cfg["mode"] == "off" or not data.get("stack_questions_applicable"):」
敘述:`_dispositions_verdict`(scripts/lumos:21376)在 `gate=high-only` 且 tier 非 high 時直接跳過、不要求表態,但 `cmd_pitfalls` 的 `--dispositions-template` 分支只檢查 `mode=="off"`,沒比對 tier;`gate=high-only` 的專案對一個 tier=standard 的改動仍會印出「要答的題 N 題」樣板,要求填答一項 `code-loop check` 根本不會強制的東西。

圖譜鏡頭:
- Issues/code-loop守衛main-direct盲區:這份 diff 讓 pre-push 對每個 `refs/heads/*` ref 一律叫 `code-loop check`(不再只在 tier=high 時走嚴格路徑),方向是進一步收斂而非重開這個盲區——沒發現讓 main-direct 推送繞過 check 的新路徑,不影響。
- Systems/bound-tests-gate ★INVARIANT★:「紅→blocked=True rc1」在 tier=high(不帶 `--bound-tests-advisory`)分支仍然原樣呼叫,沒被 f1/f2 的例外路徑短路(bt 是在表態閘之前算好、存進 `_codeloop_guard_verdict.last_bound`,不受表態核對例外影響);新增的 advisory 分流只是把既有 2026-09-07 人裁的「低風險只提醒不擋」搬進 `code-loop check` 內部執行,不是新開的例外,不影響合約。
- Systems/canary-audit ★INVARIANT★、Systems/design-loop ★INVARIANT★、Systems/guard-kill ★INVARIANT★、Systems/lumos-cli-lifecycle ★INVARIANT★、Systems/lumos-cli-read ★INVARIANT★、Systems/slim-get-一行安裝 ★INVARIANT★:皆因共用 `scripts/lumos`/`pre-push`/`test_lumos.py`/`ci.yml` 檔案而被固定席點名,但這份 diff 沒有觸及各自宣稱的合約邏輯(canary 回報 readback、design-loop 處置閘 d3/d4、guard kill rc 優先序與 JSON 純度、CLAUDE.md re-inject byte-equal、search 排除 superseded 不排除 stale、`.ps1` ASCII/無 BOM 與保留名)——不影響。

最嚴重 severity: blocker,blocking 條數 3
