severity: minor

# 通才-r4-sonnet 第 4 輪報告

範圍:第三輪修正的 scripts/lumos 全部 hunk。實跑過的東西:`python3 scripts/test_lumos.py -k t_cap_retro_r3`(74 過 0 敗)、在臨時 repo(`_cr_repo` 造的,不碰真帳)裡打治理帳硬連結、捷徑、資料夾三種壞法,跑 `loop next`、`loop status --disposal`、`loop retro-stats`、`loop retro --skip`、`loop cap-decision`、`--template` 跳脫。

重點檢查結論(沒找到問題的):
- `_retro_gov_path_err` 與 `_drift_ledger_path_err` 新增的「不是一般檔就當帳壞」:drift 帳的呼叫者(`_drift_ledger_append`、`_DRIFT_FIXES` 那處)原本對非一般檔就會卡住或寫壞,新規則只是提前擋,沒有誤擋正常情況。正常的一般檔、帳不存在、docs/ 不存在都放行。
- `_ledger_tail_needs_newline` 改跟隨捷徑:不跟隨捷徑的寫入器遇到捷徑本來就不寫,跟不跟隨不影響;管線、資料夾、指到管線的捷徑都回 False 不卡住。
- 約 20 處讀者改走 `_ledger_lines`:空尾段由各讀者原有的 `strip()` 空行跳過或 `json.loads("")` 的 ValueError 吃掉,逐一對過,沒有行為變動;`read_text` 已做換行轉換,`\r` 對這些讀者不會出現。
- `_json_text_escaped`:DEL、C1、U+202E、超出 BMP 的 Cf、孤立代理字元、U+2028 都轉成合法 `\uXXXX`,讀回值不變。
- `_cap_retro_fix_cmd` 狀態表:空檔、非 JSON、超過 256KB、捷徑、資料夾、卷證資料夾是捷徑各走一遍,每種的下一步指令照做不會回到同一句。
- `_fix_bad_strings(nul=False)`:`_retro_utf8_bad` 已無殘留引用(grep 全 repo)。
- 筆記引的 `[test:…]` 名稱全部存在於 scripts/test_lumos.py。

### F1 loop next 到 cap-reached 會印兩行幾乎一樣的記人裁指令 (修補引起)
severity: minor
blocking: 否 — 只是輸出重複,不影響判定與退出碼
- 輸入:多席迴圈帳上 3 輪(standard 上限 3)、處置閘沒過(審後改了規格),跑 `lumos loop next crx --spec <規格> --repo <根>`(環境變數 `LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26`)。
- 走到:phase 是 cap-reached,`emit` 文字輸出先印 `cap_retro` 清單(`_cap_retro_next_lines` 的記人裁那行),最後再印 `_cap_hint_lines`,r3 在後者新增了同一條記人裁指令。
- 壞在哪:實測輸出末尾連續兩行都叫人去記人裁:`人裁要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision crx --decision extra-round|accept-risk --note "<理由>"` 與 `人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記):lumos loop cap-decision crx …`,中間隔著整段 `[cap-hint]` 表。cap-reached 路徑上第二行是多餘的。
- 引句:「人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記)」
- file: `scripts/lumos:8955`(`_cap_hint_lines` 新增段)、`scripts/lumos:13622`(`_cap_retro_next_lines`)、`scripts/lumos:14228`(兩者都在 emit 文字分支印出)
- 重現:在 `_cr_repo()` + `_cr_loop(c)` 的臨時 repo,把規格檔多寫一行,`loop next crx --spec … --repo …`,數輸出裡含 `cap-decision` 的行數得 2。

### F2 治理帳壞時 retro-stats 把「治理帳」當成一個有人裁紀錄的迴圈計入 (修補引起)
severity: minor
blocking: 否 — 唯讀統計,帳壞本身有標出來;只是總數與分布會說謊
- 輸入:臨時 repo 沒有任何 cap-decision,把 `docs/.governance-log.jsonl` 做一個硬連結(或換成捷徑),跑 `lumos loop retro-stats --repo <根>`。
- 走到:`_cap_retro_scan` 的 `gerr` 分支回傳 `("(治理帳)", {...})`,`cmd_loop_retro_stats` 把它當一個迴圈:`totals["loops"] += 1`、`by_decision["?"] += 1`、`by_tier["?"] += 1`。
- 壞在哪:實測輸出 `[retro-stats] 有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)`,而這個 repo 一筆人裁紀錄都沒有;`--json` 的 `totals.loops` 也是 1,`names.error[0].loop` 是 `(治理帳)`。拿 JSON 做回頭統計(計劃 RETIRE-IF 靠 retro-stats 數字)的人會把幻影迴圈算進分母。另外判不了的原因在文字輸出被截到 80 字(`c(';'.join(e['problems'][:2]))`),實際該怎麼修(換回一般檔)在被截掉的尾端,畫面上看不到。
- 引句:「return [("(治理帳)", {"error": gerr, "decision": {}, "applies": True, "state": None, "problems": []})]」
- file: `scripts/lumos:13485-13490`(`_cap_retro_scan`)、`scripts/lumos:13845`(`cmd_loop_retro_stats` 迴圈,`totals["loops"] += 1` 在其後)
- 重現:`LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26`,`c=_cr_repo(); _cr_loop(c); os.link(docs/.governance-log.jsonl, root/"hl.jsonl")`,`loop retro-stats --repo root`,輸出第一行如上。

### F3 「兩本帳所有讀者一律走 _ledger_lines」不成立:治理帳還有三處用只認換行的切法 (修補引起)
severity: minor
blocking: 否 — 只有帳列用單獨的 CR 結尾時才分歧,現行寫入端不會產生
- 輸入:治理帳檔內兩筆事件之間只用 `\r` 分隔(`{"gate":"x","n":1}\r{"gate":"x","n":2}\n`)。
- 走到:跑滿回顧一族與 r3 換掉的讀者走 `_ledger_lines`(認 `\r`),看到 2 筆;`_gov_ledger_rows_by_time`(`lumos gov` 統計)、doctor 治理帳尾段、`_drift_jsonl_iter` 的第三處讀者走 `_drift_jsonl_iter`(只認 `\n`),看到 0 筆。
- 壞在哪:同一本帳同一列,在兩組讀者眼中行數不同,正是 r3 要消除的「口徑分岔」;r3 新寫的文字(`_ledger_lines` docstring、計劃〈誠實界線〉「所有讀者(20 處…)」、loop-retro 筆記)都寫成已一律統一,守衛測試只掃 `.read_text().splitlines()` 樣式,抓不到這三處。實測 `list(m._drift_jsonl_iter(b'{"gate":"x","n":1}\r{"gate":"x","n":2}\n'))` 回 `[]`,`m._ledger_lines(同一串)` 回 3 段(含空尾段)。
- 引句:「★審查帳(.canary-log.jsonl)與治理帳(.governance-log.jsonl)的讀者一律走這一支★」
- file: `scripts/lumos:1408`(`_gov_ledger_rows_by_time`)、`scripts/lumos:2456`(doctor 治理帳段)、`scripts/lumos:4045`、`scripts/lumos:35182`(`_drift_jsonl_iter`,docstring 寫明只在 \\n 切行)
- 重現:上面兩行 python 一次載入 scripts/lumos 即可。

### F4 治理帳壞時,處置閘與 loop next 的 [cap-hint] 仍叫人去記人裁,而記人裁當場回 2 (修補引起)
severity: minor
blocking: 否 — 錯誤訊息會講原因,沒有走死路
- 輸入:迴圈到上限、有卷證,治理帳有別的硬連結(或是捷徑),跑 `loop status crx --disposal --spec … --repo …`。
- 走到:第八步印 `✗ — 判不了:治理帳 … 讀寫都不碰`(正確),FAIL 橫幅後 `_cap_hint_print` 照印 r3 新增的 `人裁:…先記人裁(已記過就不用再記):lumos loop cap-decision crx --decision extra-round|accept-risk …`;`loop next` 的 cap-reached 輸出同理。
- 壞在哪:同一份輸出前半說帳壞到連跳過都寫不進去,後半叫人去記人裁;照貼(換掉佔位字之後)`cap-decision` 在 `_retro_gov_path_err` 那關回 2「擋下:治理帳 … 讀寫都不碰」。兩句互相矛盾,新使用者會先試後者。`_cap_hint_lines` 不知道治理帳狀態,沒有辦法在帳壞時換成指向修帳的句子。
- 引句:「if h["at_cap"] and h["hint"] != "can-stop":」
- file: `scripts/lumos:8955`(`_cap_hint_lines`)、`scripts/lumos:13665`(`cmd_loop_cap_decision` 的 `_retro_gov_path_err` 檢查)
- 重現:`exp4`:`_cr_repo`+`_cr_loop`+`_cr_decide` 之後 `os.link(governance-log, 別處)`,`loop status crx --disposal --spec … --repo …`,輸出同時含「✗ — 判不了:治理帳」與「先記人裁」。

總結:最嚴重 minor,blocking 0 條
