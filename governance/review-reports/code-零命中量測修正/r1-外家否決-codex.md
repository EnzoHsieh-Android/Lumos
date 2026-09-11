severity: major

B1
severity: major
blocking: 是
引句:「_VAR_QUERY_RE = re.compile(r"\$\{?[A-Za-z_]")」
file: `governance/eval/lens-utilization/recount.py:867`
位置參數 `$1` 不在正則涵蓋範圍，函式包裝會記下假查詢。重現：`f(){ python3 scripts/lumos search "$1" --json; }; f __NO_HIT_POSITIONAL_9F38B7__`；輸出是 `"candidates": 0`，但 `_search_events` 回傳 `query: "1"`，不是實際查詢 `__NO_HIT_POSITIONAL_9F38B7__`。

B2
severity: major
blocking: 是
引句:「if _VAR_QUERY_RE.search(seg.split("search", 1)[-1]):」
file: `governance/eval/lens-utilization/recount.py:884`
檢查沒有 shell quoting 語意，單引號保護的字面 `$FOO` 也會被當成變數而抹掉。重現：`python3 scripts/lumos search '$ZZZQXJ_NO_HIT_9F38B7' --json`；真輸出是 `"candidates": 0`，parser 卻回 `query: ""、verdict: undetermined、zero_unattributed: 1`。

B3
severity: major
blocking: 是
引句:「if not w.startswith("-"):」
file: `governance/eval/lens-utilization/recount.py:891`
帶值旗標的值會被併進查詢字串，常用的 `--path`、`--top` 都會污染本機零命中清單。重現：`python3 scripts/lumos search __NO_HIT_FLAG_9F38B7__ --path Systems --top 2 --json`；輸出 `"candidates": 0`，parser 卻記成 `__NO_HIT_FLAG_9F38B7__ Systems 2`。

B4
severity: major
blocking: 是
引句:「if len(segs) == 1 and segs[0] is not None:」
file: `governance/eval/lens-utilization/recount.py:942`
單一搜尋直接走 `_search_verdict`，不檢查同一次 Bash 呼叫裡是否另有舊計數輸出，因此前面的無關零命中會蓋掉真正結果。重現：`sed -n 5572p governance/review-reports/design-cjk-nospace-fallback/r1-codex-raw.txt; python3 scripts/lumos search "推播 miss" --json`；實跑計數依序為 `[0, 141]`，parser 卻把唯一真正搜尋 `"推播 miss"` 判成 `zero`。

B5
severity: major
blocking: 是
引句:「_atomic_json(local, {"week": week, "zero_hit_queries": sorted」
file: `governance/eval/lens-utilization/recount.py:1142`, `governance/autonomous_loop/lens_weekly.py:42`
`--archive-dir` 可指向 repo 內任意位置，但只有預設 `governance/eval/lens-utilization/local/` 被忽略，因此自由文字查詢可能成為可提交檔。唯讀重現：對預設與 `governance/review-reports/recount-smoke/local/2026-W37-queries.json` 分別跑 `git check-ignore -v`，輸出為 `default_rc=0`、`custom_rc=1`；後者會被 `write_archive` 寫入但不受 gitignore 保護。

圖譜鏡頭：

- `Systems/bound-tests-gate.md`：不破壞；變更只新增量測測試，未改固定席測試執行、懸空判定或 rc。
- `Systems/canary-audit.md`：不破壞；未碰 canary record、second、落盤或 readback。
- `Systems/design-loop.md`：不破壞；未改 loop 類型辨識、計劃審材或條款綁測試閘。
- `Systems/guard-kill.md`：不破壞；未碰 kill 結果優先序或 JSON stdout 合約。
- `Systems/lumos-cli-lifecycle.md`：不破壞；未碰 CLAUDE.md re-inject 或 sentinel 外內容。
- `Systems/slim-get-一行安裝.md`：不破壞；未修改任何 PowerShell 檔、編碼或參數名稱。
- `Systems/slim-install-安裝器.md`：不破壞；未碰安裝、manifest、目標守衛、shim 或備份流程。
- `Systems/slim-uninstall-一行卸載.md`：不破壞；未碰獨立清理、內容比對、備份或 manifest 移除。

全份最高嚴重度是 major,blocking 共 5 條。