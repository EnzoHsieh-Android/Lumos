severity: minor

# 正確性-r4-sonnet 報告(第 4 輪,正確性/邏輯 + 資料狀態五問)

範圍:r4 差異 `scripts/lumos` 全部 hunk;`scripts/test_lumos.py` 與筆記當查證材料。方法:讀碼,並用 `scripts/test_lumos.py` 的 `_cr_repo/_cr_loop/_cr_decide` 在臨時目錄造帳實跑(沒碰真帳、沒寫 repo)。

重點驗過、沒問題的項目(不算 finding):
- `_ledger_lines` 換掉約 20 處 `splitlines()`:多出的尾端空字串,每個讀者要嘛先 `strip()` 後 `continue`、要嘛 `json.loads("")` 的 ValueError 被接住,行為沒變;真帳(審查帳 3053 行、治理帳 119933 行)裡 U+2028/U+2029/U+0085/\x0b/\x0c/\x1c-\x1e 都是 0 個,所以凍結的 golden 列不會因切行改變而漂移。
- `_drift_ledger_path_err` 新增的 `is_file()` 檢查:另兩個呼叫者(`_drift_ledger_append`、約 36330 行那處)只會在帳檔是資料夾/管線時多一個更早的擋下,正常檔不受影響。
- `_regular_own_fd(follow=)` 預設 False,其他呼叫者不變;`_ledger_tail_needs_newline` 跟隨捷徑時,不跟隨的寫入器本來就不寫,沒有新的黏行或誤補。
- `_json_text_escaped`:實跑帳上 auditor 含 U+0085、U+202E、非 BMP 的 Cf(U+E0041)、U+2028、BOM、ZWJ 表情,`--template` 輸出與 `--write` 的檔都能 `json.loads` 讀回同值,`--check` 不受影響。
- 治理帳符號連結、硬連結兩種情境實跑:`canary record` 新一輪回 2(cap-gov-bad、不寫治理帳)、處置閘第八步 ✗、`--check/--skip/cap-decision` 回 2、`loop next` 不丟堆疊、`retro-stats --json` 與 doctor 不丟堆疊。
- 卷證資料夾本身是符號連結:`--check`、`--template --write` 回 2 並印 `--skip` 出口;`--skip` 後處置閘轉 ✓、`canary record` 放行,狀態表走得通。
- 新測試 `t_cap_retro_r3_gov_ledger_rule`(17 項)、`t_cap_retro_r3_ledger_lines_everywhere`(6 項)、`t_cap_retro_r3_prompt_table`(30 項)全過。

沒有找到 major 以上的問題,以下三條都是 minor。

### F1 跑滿上限提示與 cap-reached 的記人裁指令在 `loop next` 同一次輸出裡印兩次(修補引起)
severity: minor
blocking: 否 — 只是重複輸出,不影響判定、退出碼與帳。
- 輸入:多席迴圈 3 輪到 standard 上限、折入沒比前一輪少(提示=換做法)、已記 `cap-decision extra-round`、回顧還沒寫,跑 `lumos loop next crx --spec … --repo …`。
- 走到哪:`cmd_loop_next` 在 cap-reached 先印 `_cap_retro_next_lines` 的那行「人裁要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision crx …」,最後印 `_cap_hint_lines(_ch, loop_id=loop_id)`,而 r3 新增的 `[cap-hint]` 段在到上限且不是可以停時再印一行同義的「人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記):lumos loop cap-decision crx …」。
- 壞在哪:實跑輸出裡這兩行相隔 6 行、同一指令各出現一次;人裁都已記了,上面那行仍叫人「先記人裁」,下面那行才補「已記過就不用再記」。計劃〈三〉3 與 S19 都沒說 cap-reached 要出兩條。
- 引句:「    if h["at_cap"] and h["hint"] != "can-stop":」
- 佐證行:file: `scripts/lumos:8985`;file: `scripts/lumos:13622`(`_cap_retro_next_lines`,同樣印記人裁指令);file: `scripts/lumos:14228`(`loop next` 文字輸出末尾印 cap-hint)
- 重現:`LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26 python3 -c` 載入 `test_lumos`,`c=_cr_repo(); _cr_loop(c); _cr_decide(c); print(_cr_next(c).stdout)`,輸出中 `lumos loop cap-decision crx --decision extra-round|accept-risk` 出現兩次。

### F2 治理帳壞時,跑滿上限提示仍叫人去記人裁,而那個指令會被拒(修補引起)
severity: minor
blocking: 否 — 同一段輸出裡另有正確的「換回一般檔」出口,只是多了一條走不通的指令。
- 輸入:迴圈已到上限、有卷證、`docs/.governance-log.jsonl` 是符號連結(或硬連結數不是 1),跑 `lumos loop status crx --disposal --spec … --repo …`(或 `loop next`)。
- 走到哪:第八步印「✗ — 判不了:治理帳…」與出口「把治理帳換回 repo 裡的一般檔…帳修好之前跳過也寫不進去」,FAIL 後 `_cap_hint_print(..., loop_id=loop_id)` 接著印 r3 新增的「人裁:…先記人裁(已記過就不用再記):lumos loop cap-decision crx --decision extra-round|accept-risk …」。
- 壞在哪:照著那行跑 `cap-decision` 會因同一個 `_retro_gov_path_err` 回 2「治理帳…讀寫都不碰;沒有寫帳」。規格〈二〉下一步提示寫「每種狀態照做之後不會回到同一句」、`_cap_retro_fix_cmd` 狀態表對 gov-bad 特地不給 `--skip`(寫不進去);新增的記人裁行沒套同一條規則,gov-bad 時照印。`_cap_retro_next_lines`(`loop next`)也是先印記人裁行、後印 gov-bad 出口,同樣矛盾。
- 引句:「    if h["at_cap"] and h["hint"] != "can-stop":」
- 佐證行:file: `scripts/lumos:13097`(`_retro_gov_path_err` 讓 `cap-decision` 回 2);file: `scripts/lumos:13635`(`_cap_retro_next_lines` 在判 gov-bad 之前就先 append 記人裁行)
- 重現:`_cr_repo/_cr_loop/_cr_decide` 後把 `docs/.governance-log.jsonl` 搬成 `gov-real.jsonl` 並建符號連結,`_cr_gate(c)` 的輸出末段同時有「換回一般檔」與「先記人裁…cap-decision」;`_cr_decide(c)` 回 rc=2。

### F3 治理帳壞時 doctor I2 與 retro-stats 虛構出一個叫「(治理帳)」的「記了人裁的迴圈」(修補引起)
severity: minor
blocking: 否 — doctor 這段只提醒不計入問題數,retro-stats 唯讀;但數字與用詞不實。
- 輸入:repo 裡從沒用過 `loop-retro`,只是 `docs/.governance-log.jsonl` 是符號連結或有別的硬連結(任何一個治理帳壞的 repo)。
- 走到哪:`_cap_retro_scan` 遇到 `gerr` 回一筆 `("(治理帳)", {"error": gerr, "decision": {}, …})`;doctor I2 把它當一個迴圈列出,`cmd_loop_retro_stats` 照迴圈累計。
- 壞在哪:實跑 doctor 印「1 個迴圈記了人裁,但跑滿回顧沒有或過期」「• (治理帳):判不了(…),略過這一個」;`retro-stats --json` 的 `totals.loops` 是 1、`by_decision` 是 `{"?": 1}`、`by_tier` 是 `{"?": 1}`。沒有任何迴圈記過人裁,「1 個迴圈記了人裁」與「略過這一個」(其實是整本帳都判不了)都不實;`loops` 計數也把帳本當成迴圈。
- 引句:「        return [("(治理帳)", {"error": gerr, "decision": {}, "applies": True, "state": None, "problems": []})]」
- 佐證行:file: `scripts/lumos:13488`;file: `scripts/lumos:2314`(doctor I2 逐項列);file: `scripts/lumos:13845`(retro-stats 累計 `totals["loops"]`)
- 重現:同 F2 的符號連結設定,`run(c["vault"], "loop", "retro-stats", "--json", "--repo", str(c["root"]))` 看 `totals.loops == 1`;`run(c["vault"], "doctor", "--verbose")` 看 `[I2]` 段。

總結:最嚴重 minor,blocking 0 條
