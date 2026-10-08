severity: major

## F1 留痕有效性的「程式檔」判法只接半套既有分類器,沒副檔名的可執行腳本搬進簿記資料夾照樣豁免
severity: major
blocking: 是
引句:「(f.startswith(_BOOKKEEPING_DIRS) and _nodehome_code_kind(f) != "ext") for f in files):」
file: `scripts/lumos:6538`(_is_code_file:專案裡「這支是不是程式檔」的完整判準,先 _nodehome_code_kind 再對 "shebang?" 讀首行認 #!)
file: `scripts/lumos:23663`(_nodehome_code_kind:沒副檔名回 "shebang?",自己不下結論)
1. 專案既有的「需要有家的程式檔」判準是 `_is_code_file`:副檔名清單命中算是,沒副檔名則再讀首行 `#!`。這次修正只拿了第一半 `_nodehome_code_kind(f) != "ext"`,把 "shebang?" 一律當簿記——等於在代碼審留痕這個消費者另寫一套較窄的判準(只看副檔名清單),跟 pitfalls 分級、每支檔有家用的不同。
2. 重現(臨時 repo,記錄提交 A 之後只新增 `governance/replay/run`,內容 `#!/bin/sh` + `rm -rf /`,chmod +x):
   `_codeloop_record_valid(".", A, B)` 輸出 `(True, '祖先 cfe7fed3+簿記豁免(其後 1 檔皆簿記)')`。本該判失效的「程式改動搬進簿記資料夾」在這條路上仍過,r1 資安席 F4 要堵的洞沒堵乾淨(副檔名清單外的 .rb/.php/.pl 之類、大小寫不同的 `.PY` 也同樣因清單大小寫敏感而漏)。
3. 修法方向:這裡是「簿記資料夾底下的檔該不該信」,想嚴就用白名單(只豁免已知紀錄副檔名 .json/.md/.patch/.txt/.jsonl/.log…)而不是用「程式副檔名清單的補集」;或至少對 "shebang?" 也判為非簿記(保守,同 _is_code_file 讀不到就當程式檔的慣例)。

## F2 新增第三份「從 repo 根逐層擋符號連結並確認 resolve 後在 repo 內」的路徑守衛,沒重用既有那份
severity: minor
blocking: 否
引句:「    從 repo 根往下每一層已存在的都不准是符號連結、要是資料夾;建好之後再確認解析後還在 repo 根底下(同一份程式別處」
file: `scripts/lumos:28776`(_drift_ledger_path_err:同樣的逐層 is_symlink + resolve().is_relative_to(repo 根),docstring 明寫照 _mkdir_trusted_under_home)
file: `scripts/lumos:36041`(_mkdir_trusted_under_home:家目錄版的逐層建+檢查,另有 _mkdir_private_layer)
1. `_note_audit_safe_dir` 自己寫逐層檢查,docstring 只說「別處已有 resolve 後 is_relative_to 守衛」,沒說為何不重用。`_drift_ledger_path_err` 邏輯同形但針對「帳檔」多查硬連結數(目錄的 st_nlink 本來就 ≥2,不能直接套),所以不能原樣呼叫;合理做法是把「逐層不得為符號連結+解析後在 repo 內」抽成一支共用的小函式,兩邊各自加自己的額外檢查,而不是再複製一份。現在 repo 裡同一個 repo 根逐層守衛有兩份寫法,日後一邊補洞(例如 Windows junction、W4 在 18142 已處理過 junction)另一邊不會跟。
2. 行為上沒有矛盾、未見錯誤輸出,故只列 minor;若日後要再加第四個寫入點,應先抽共用。

最高等級:major
