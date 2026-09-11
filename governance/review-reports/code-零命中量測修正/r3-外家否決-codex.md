severity: major

1. 巢狀 shell 內的背景搜尋仍會配錯查詢
severity: major
blocking: 是
引句:「amp = any(_LONE_AMP_RE.search(ln) for ln in _shell_lines(cmd))」
file: `governance/eval/lens-utilization/recount.py:1016`
重現（已跑）：`bash -c 'python3 scripts/lumos search README & python3 scripts/lumos search __R3_NO_HIT__; wait'` 的真實計數順序是 `[0, 85]`，解析結果卻是 `README=zero`、`__R3_NO_HIT__=hit`。內層 `&` 被外層引號隱藏，程式誤以為可以依輸出順序配對。

2. `-c` 前帶合法 shell 選項時整筆漏算
severity: major
blocking: 是
引句:「if os.path.basename(tk) in _SHELLS and i + 2 < len(toks) and _SHELL_C_RE.match(toks[i + 1]):」
file: `governance/eval/lens-utilization/recount.py:930`
重現（已跑）：`bash -o pipefail -c 'python3 scripts/lumos search __R3_OPTION_NO_HIT__'` 真實輸出 `(共 0 篇候選…)`，但 `_search_segments` 與 `_search_events` 都回 `[]`。實作只接受 shell 後緊接 `-c`，因此少算這次零命中。

3. 只是參數的 `bash -c` 會被當成真的巢狀 shell
severity: major
blocking: 是
引句:「out += _search_segments(toks[i + 2])   # bash -c "…" 那串字會被另一個 shell 真的執行」
file: `governance/eval/lens-utilization/recount.py:930`
重現（已跑）：`printf '%s\n' bash -c 'lumos search fake'; python3 scripts/lumos search __R3_NO_HIT__` 只執行後一個搜尋，輸出 `bash`、`-c`、`lumos search fake` 與一行零命中；解析器卻產生 `fake` 和 `__R3_NO_HIT__` 兩筆，並把零命中記成無法歸屬。它在整段任意位置找 shell 名稱，沒有確認那是實際被執行的命令。

4. 控制運算子後無空白的註解仍會冒充搜尋
severity: major
blocking: 是
引句:「if ch == "#" and (i == 0 or bare[i - 1].isspace()):」
file: `governance/eval/lens-utilization/recount.py:893`
重現（已跑）：`python3 scripts/lumos search __R3_COMMENT_NO_HIT__;# lumos search fake` 的 Bash 輸出只有真搜尋的一行零命中，但解析結果包含 `__R3_COMMENT_NO_HIT__`、`fake` 兩筆，零命中被降成 `zero_unattributed`。Bash 在 `;` 後會把 `#` 當註解起點，這裡卻只認行首或空白後的 `#`。

5. 偶數個反斜線前的 `$` 仍會展開，卻被當成字面
severity: major
blocking: 是
引句:「if _VAR_QUERY_RE.search(re.sub(r"\\\$", "", _SINGLE_QUOTED_RE.sub("", after))) or "{}" in after or _XARGS_RE.search(before):」
file: `governance/eval/lens-utilization/recount.py:935`
重現（已跑）：`python3 scripts/lumos search \\$HOME` 實際傳給 Bash 子命令的查詢是 `\/Users/enzo`，並輸出零命中；解析器卻記成字面查詢 `\$HOME` 並判零命中。無條件刪除 `\$` 沒有依反斜線奇偶判斷 `$` 是否真的被跳脫。

6. git 探測失敗會把私密查詢寫到未忽略的版控位置
severity: major
blocking: 是
引句:「try:   # git 失敗照本檔慣例當非阻斷訊號(r2 架構 E1):判不出在不在工作樹 → 當不在;在工作樹裡但判不出有沒有 ignore → 當會進版控」
file: `governance/eval/lens-utilization/recount.py:1213`
重現（已跑、以 print 代替真正寫檔）：`PATH=/no-git /opt/homebrew/bin/python3 -c 'import runpy; from pathlib import Path; m=runpy.run_path("governance/eval/lens-utilization/recount.py"); g=m["write_archive"].__globals__; g["_atomic_json"]=lambda p,d: print("WOULD_WRITE",p); m["write_archive"]({"summary":{},"budget_hit":False,"rows":[],"searches":[{"ts":"T","query":"secret","verdict":"zero"}]},"2026-W37",Path("unignored-archive"))'` 印出 `WOULD_WRITE unignored-archive/local/2026-W37-queries.json`。`rev-parse` 失敗回 `False` 使安全檢查 fail-open，正好把不該進版控的查詢檔寫進工作樹。

全份最高嚴重度是 major,blocking 共 6 條