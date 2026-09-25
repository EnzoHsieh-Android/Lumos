severity: major

## F1 決策日期的空字串仍能繞過關卡
severity: major
blocking: yes
引句:「if v is not None and str(v).strip() != "" and not _note_date_ok(str(v)):」
修正只攔住頂層 `created`、`updated`、`date` 的空字串；決策的 `decided: ""` 與 `ended: ""` 仍被 `str(v).strip() != ""` 排除，兩個無效日期都不會產生錯誤，違反「含決策 decided/ended」及「寫了卻空一律報錯」的規則。解析器確實把引號空字串解析成 `""`。  
file: `scripts/lumos:5171`  
file: `scripts/lumos:12378`  
翻紅重現（已實跑）：
`PYTHONDONTWRITEBYTECODE=1 python3 -c 'import runpy,types; m=runpy.run_path("scripts/lumos"); lines=["decisions:","  - content: x","    decided: \"\"","    ended: \"\"","    valid: true"]; d=m["parse_decisions"](lines); env=types.SimpleNamespace(notes={"Systems/x.md":types.SimpleNamespace(fields={"type":"moc"},fm_lines=lines)}); print("parsed=",d); print("new_rules=",m["_lint_new_rules"](env,"Systems/x.md"))'`
實際輸出為 `parsed= [{'content': 'x', 'decided': '', 'ended': '', 'valid': 'true'}]` 與 `new_rules= []`；預期至少回報 `decided`、`ended` 兩項日期錯誤。
