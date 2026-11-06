severity: clean

r2 這份修補和專案既有做法對得上,沒有找到不對齊的地方。

**① 分層與依賴方向**
- `--all` 只改了 `main()` 的 `lint-new` 子指令,一路經 `cmd_lint_new` 傳到 `_lint_new_cli_items`。這條 `main` → `cmd_` → 輔助函式的鏈,跟其他子指令一樣,沒有新增跨層呼叫。對照:`scripts/lumos:74326`、`scripts/lumos:74721`。
- 提示文字從 `code-loop check` 改指回 `lint-new --all`。這是同一支指令自己指向自己,依賴方向反而變單純,沒有新增依賴。

**② 命名與錯誤處理**
- 旗標寫法對齊:`add_argument("--all", dest="ln_all", action="store_true", ...)` 跟 `ll.add_argument("--all", dest="ll_all", action="store_true", ...)` 同形,對照 `scripts/lumos:73797`。`dest` 前綴也跟 `waive_all`、`coch_all` 一樣各子指令自帶前綴,對照 `scripts/lumos:74337`、`scripts/lumos:74463`。
- 參數名 `show_all` 是新取的,倉庫裡沒有同義詞慣例可比。⚠ 不列為不對齊。
- 狀態詞對齊:`not-run` 改成 `skipped`。合約測試跳過分支(`_bound_tests_check`)已經用 `skipped`,回傳形狀是 `{"status": "skipped", "ran": 0, "reason": ...}`,對照 `scripts/lumos:70361`。`mech_only` 分支現在用同一個詞,下游 `_cl_say_bound` 的 `green`/`red`/`unfilterable` 判斷也不受影響,對照 `scripts/lumos:72699`。
- 這個狀態詞的變更只修了命名,不影響擋或不擋。`mech_only` 的 `skipped` 沒有 `ran`、`red` 等鍵。⚠ 這是結構差異,不是命名差異,不屬於本席的審查範圍。

**③ 第二種做法**
- 「列全部」沿用既有的「預設截斷加 `--all` 展開」模式,對照 `scripts/lumos:74463`。沒有新增另一條輸出路徑(例如新的 `--json` 或環境變數)。
- 測試用 `_lnc_run`、`_lnc_gov`、`check(...)` 這組現有輔助函式,沒有自建一套。

不對齊共 0 條,其中會擋的 0 條
