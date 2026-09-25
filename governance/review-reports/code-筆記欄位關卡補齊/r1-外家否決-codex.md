severity: major

## F1 monorepo 深層圖譜會忽略外層設為 on 的開關

severity: major
blocking: yes
引句:「+    mode, cfg_warns = _note_lint_config(_repo_root_from_env(env))」
`_repo_root_from_env` 遇到 `repo/subdir/docs/x-knowledge` 會回傳 `repo/subdir`，只查該處的 `.lumos/config.json`；若實際設定放在 Git 根目錄 `repo/.lumos/config.json`，`note_lint.gate: on` 會被靜默忽略並退成 `warn`，因此 lint 與 doctor 都放過本應阻擋的錯誤。既有設定讀取器與測試已明確把這種深層 monorepo 佈局列為支援情境。
file: `scripts/lumos:10613`
file: `scripts/lumos:4753`
file: `scripts/test_lumos.py:35876`
翻紅重現（已實際執行、全程只讀）:
```text
env.vault = /Users/enzo/harness/lumos-toolchain/subdir/docs/demo-knowledge
_repo_root_from_env(env) -> /Users/enzo/harness/lumos-toolchain/subdir
_note_lint_config(...) -> ('warn', [])
```
同一個 repo 根目錄現有 `.lumos/config.json` 明明把 gate 設為 `on`。最小修復驗證應建立 `repo/subdir/docs/x-knowledge`、只在 `repo/.lumos/config.json` 設 `on`，放入缺 status 的筆記，斷言 `lumos lint` 非零且 doctor 也阻擋。

## F2 引號包住的空日期會完全繞過日期規則

severity: major
blocking: yes
引句:「+        if v is not None and str(v).strip() != "" and not _note_date_ok(str(v)):」
`created: ""`、`updated: "   "`，以及決策中的 `decided: ""`、`ended: ""` 都因空字串條件被直接略過，沒有交給 `_note_date_ok`。這違反「日期必須是真實年-月-日」的新關卡；尤其空 `created` 還會讓既有 aliases 與 status 值域規則的日期 cutoff 失效，因此 `created: ""` 搭配非法非空 status 也可能一起放過。
file: `scripts/lumos:4907`
file: `scripts/lumos:4929`
file: `scripts/lumos:5119`
file: `scripts/lumos:5141`
翻紅重現（已實際執行、直接呼叫新增規則判定）:
```text
fields = {"type":"system","status":"doing","created":"","updated":"   "}
_lint_new_rules(env, "Systems/empty-date.md") -> []
```
應補測 `created: ""`、`updated: "   "`、`decided: ""` 與 `ended: ""` 均產生日期錯誤；若空值代表欄位缺失，也仍須報錯而不能靜默略過。
