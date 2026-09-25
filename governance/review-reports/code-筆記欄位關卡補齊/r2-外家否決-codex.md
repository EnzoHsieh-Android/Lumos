severity: major

## F1 決策日期的空字串仍能繞過關卡
severity: major
blocking: yes
引句:「            if v is not None and str(v).strip() != "" and not _note_date_ok(str(v)):」
修正只涵蓋頂層 `created/updated/date`；`decisions.decided` 與 `decisions.ended` 仍明確略過空字串。`parse_decisions` 會把 `ended: ""` 解析成 `""`，因此開關為 on 時 `_lint_new_rules` 仍回傳空清單。若這是 `valid: false` 的翻案決策，下游連鎖檢查又會因無法解析 ended 而直接跳過，該擋的錯誤及落後依賴都會被放過。
file: `scripts/lumos:5174`
file: `scripts/lumos:1848`
file: `scripts/test_lumos.py:21896`
翻紅重現（已跑）:以 `SourceFileLoader` 載入 `scripts/lumos`，建立 `fm_lines=["decisions:","  - content: x","    decided: \"\""]` 後呼叫 `parse_decisions` 與 `_lint_new_rules`；實際輸出依序為 `[{'content': 'x', 'decided': ''}]` 與 `[]`。把欄位換成 `ended: ""` 走同一漏檢分支。
