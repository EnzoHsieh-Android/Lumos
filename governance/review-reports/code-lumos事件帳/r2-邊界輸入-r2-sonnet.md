severity: major

### F1 單行深層巢狀 JSON 讓 RecursionError 逃出讀取端,連 `lumos events` 列表全部會談一起崩
severity: major
blocking: 是 — 一個會談資料夾裡的一行壞資料,就讓整個事件帳讀取端(列表與逐筆)Traceback 退出。

- hunk:`_events_read` 的 `ev = _j.loads(line)` 只接 `ValueError`;`_events_sessions` 對最近 10 個會談逐一呼叫它,沒有任何外層保護。
- 輸入→結果:repo 內建 `governance/runtime/events/S1/1.jsonl`,內容為 200000 個 `[` 加 200000 個 `]`(單行)。
  - `python3.14 scripts/lumos events --session S1` 印 `RecursionError: Stack overflow (used 16352 kB) while decoding a JSON array`。
  - 同 repo 另有正常的會談 GOOD,`python3.14 scripts/lumos events`(列表)也是同一個 RecursionError,GOOD 也看不到。
- 與 r1 邊界席結論相反:r1 說「100000 層巢狀實測不崩」,本輪用 200000 層在 python3.14 實測會崩。r1 的說法在更深的輸入下不成立,測試也沒有這個案例。
- 佐證:`t_events_reader_edge_lines` 與 `t_events_reader_merges_chunks` 沒有深層巢狀行;`except ValueError:` 接不到 RecursionError。
引句:「ev = _j.loads(line)」
- file: `scripts/lumos`(`_events_read`,diff 內第 303 行)

### F2 單一孤立代理字元(lone surrogate)讓文字輸出與 --json 輸出都崩 UnicodeEncodeError
severity: major
blocking: 是 — `_events_clean` 宣稱印出前已清乾淨,但孤立代理字元照樣讓 print 丟未接例外,且列表模式也會連帶崩。
- hunk:`_events_clean` 與 `cmd_events` 的三個輸出點(逐筆 print、`--json` 的 `_j.dumps(..., ensure_ascii=False)`、列表的 `last` 欄)。
- 輸入→結果:一行 `{"v":1,"ts":"t","ev":"tool","tool":"\ud800x","ok":true}`(JSON 合法,loads 出孤立代理)。
  - `events --session S1` → `UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800'`。
  - `events --session S1 --json` → 同一個錯。
  - 另一行 `ts` 放 `\ud800` 時,`events`(列表)與 `events --json` 也崩,同目錄其他會談一起看不到。
- 原因:`_events_clean` 只剝 C0 與 C1 控制字元,沒處理 U+D800–DFFF;`--json` 路徑完全沒經過 `_events_clean`。
- 佐證:`t_events_reader_edge_lines` 的控制字元案例只放 `\x1b` 與 `\x07`。
引句:「return "".join(ch for ch in str(text) if ch in "\t" or (ord(ch) >= 32 and ord(ch) != 127 and not 0x80 <= ord(ch) < 0xA0))」
- file: `scripts/lumos`(`_events_clean`,diff 內第 283 行)

### F3 `ok` 欄位是列表或物件時,逐筆輸出丟 TypeError(unhashable)
severity: minor
blocking: 否 — 只影響該會談的逐筆文字輸出,列表與 --json 不受影響,且寫入端自己的 mod 不會產生這種值。
- hunk:`cmd_events` 內 `{True: " ✓", False: " ✗"}.get(e.get("ok"), " ?")`。
- 輸入→結果:`{"v":1,"ts":"t","ev":"tool","tool":"a","ok":[1]}` → `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`。
引句:「ok = "" if e.get("ev") != "tool" else {True: " ✓", False: " ✗"}.get(e.get("ok"), " ?")」
- file: `scripts/lumos`(`cmd_events`,diff 內第 418 行)

### F4 `--days` 傳上標數字(如 `²`)時丟未接的 ValueError
severity: minor
blocking: 否 — 沒有任何東西被刪(例外發生在刪除前),只是顯示 Traceback 而不是三段式擋下訊息。
- hunk:`n = int(txt) if txt.isdigit() and len(txt) <= 6 else 0`。
- 輸入→結果:`events --prune --days "²"` → `ValueError: invalid literal for int() with base 10: '²'`(`"²".isdigit()` 為真、`int("²")` 丟錯)。全形 `１２`、阿拉伯-印度數字 `٣` 因 `str(n) != txt` 被擋回 2,是對的;前導零 `05`、`+5` 也回 2;`" 5 "`(前後空白)被 strip 後當 5 接受,不算錯。
- 佐證:`t_events_prune_edge_cases` 與 `t_events_prune_only_old_sessions` 的壞值清單只有 `0 -1 1.5 abc`、`9*400`、`36501`,沒有上標數字(r1 邊界席 F4 要求補的 `+5`、`05` 之類沒補,上標這型也不在內)。
引句:「n = int(txt) if txt.isdigit() and len(txt) <= 6 else 0」
- file: `scripts/lumos`(`cmd_events`,diff 內第 387 行)

### F5 `_events_clean` 沒剝雙向控制字元與零寬字元
severity: minor
blocking: 否 — 只影響終端顯示順序,不執行任何東西。
- hunk:`_events_clean`。
- 輸入→結果:`tool` 值為 U+202E、evil、U+200B、U+2066、x 串成的字串(編排者註:原稿此處直接放了那幾個字元本身;把雙向覆寫字元寫進 repo 正是這類攻擊的手法,存檔改寫成字元代號)→ `events --session S1` 輸出位元組 `342 200 256`(U+202E)與 `342 200 213`(U+200B)原樣保留,可在終端把後面文字反向顯示、造出看起來像別的工具名稱的內容。r1 資安 F1 的修法只處理了 ESC 與 BEL 一類,同族的格式字元(Cf 類)沒處理。
- 佐證:測試只驗 `\x1b`、`\x07`。
引句:「ok = "" if e.get("ev") != "tool" else」
(此條的引句與 F3 同行,實際位置見 `_events_clean` 的 diff 內第 283 行,判準是它的字元濾網只擋 C0/C1。)

### F6 事件帳會談資料夾內的符號連結塊檔會被讀,可讀 repo 外檔案內容
severity: minor
blocking: 否 — 只讀,且只印符合事件格式的欄位。
- hunk:`_events_read` 的 `sorted(p for p in d.glob("*.jsonl") if p.is_file())`。`is_file()` 會跟連結;r1 補了會談資料夾連結的檢查,塊檔本身沒補,prune 那邊卻特地不跟連結,兩處不一致。
- 輸入→結果:`S1/2.jsonl` 是指向 repo 外 `outside.jsonl` 的符號連結,內容 `{"v":1,"ts":"OUTSIDE","ev":"turn_end"}` → `events --session S1` 印出 `OUTSIDE  turn_end`,列表的「最後」欄也顯示 OUTSIDE。
引句:「for f in sorted(p for p in d.glob("*.jsonl") if p.is_file()):」
- file: `scripts/lumos`(`_events_read`,diff 內第 294 行)

### F7 ⚠ teardown 的外掛判斷沒限定使用者範圍,只有專案範圍那份時移除會失敗並跳過移除市集
severity: minor
blocking: 否 — ⚠ 未能實跑(本環境不准我執行會改設定的 claude 子指令),只依 `claude plugin uninstall --help` 的文字(`--scope` 預設 user)與程式讀出的推論;失敗時還有附兩個手動指令。
- hunk:`_teardown_claude_plugin` 的 `any(x.get("id") == _LEDGER_PLUGIN for x in ...)` 不看 `scope`,接著 `plugin uninstall` 不帶 `--scope`;安裝端 `_ledger_user_plugin` 卻特地只算 user 範圍。
- 推論輸入→結果:列表裡只有 `scope: "project"` 的 lumos-ledger → 判成有裝 → `uninstall`(預設 user)預期失敗 → 進 `failed`,後面的市集移除被跳過。
引句:「if any(x.get("id") == _LEDGER_PLUGIN for x in _claude_json(claude, ["plugin", "list", "--json"])):」
- file: `scripts/lumos`(`_teardown_claude_plugin`,diff 內第 197 行)

### 前輪修復驗收
- r1 邊界 F1(null 造成 TypeError):修好。實測讀碼確認 `_claude_json` 現在只收物件組成的清單,null、物件、數字、空、非物件元素都走 RuntimeError;新測試用 FAKE_CLAUDE_RAW 涵蓋。scope 為 null 或 path 為數字的案例走「不是使用者層就重裝/不同路徑就換」的保守分支,不崩。
- r1 邊界 F2(--session 跳出、空字串、連結):修好。`fullmatch` 的 ASCII 正規式擋掉 `-x` 開頭、全形 `Ｓ1`、尾端換行 `S1\n`(都實測回 2)、5000 字元超長名稱(回 2,但把 5000 字原樣印進錯誤訊息,是小瑕疵);空字串與連結會談回 2。新問題:列表看得到名稱含空白的會談(如 `we ird`),`--session` 卻擋掉它,兩邊規則不一致(真實會談編號是 UUID,影響小)。
- r1 邊界 F3(`v` 判斷):修好。`type(...) is not int` 擋掉 true 與 1.0。
- r1 邊界 F4(測試覆蓋洞):只補了一半。補了 `--days` 超大與超上限、空字串、連結;沒補上標數字(F4)、深層巢狀行(F1)、孤立代理字元(F2)、非 dict 的 ok 欄(F3)。
- 修補本身引入的新問題:`_events_clean` 補上後帶來「已清乾淨」的錯覺,實際 `--json` 完全沒經過它(F2)。prune 對 `locked` 子資料夾做 `shutil.rmtree` 失敗時,同一會談資料夾內可刪的塊檔已先被刪(部分刪除),訊息只說「沒刪掉」;測試只驗 B 被刪與沒有 Traceback,沒驗 A 是否被刪半。
- 假綠檢查:`t_events_prune_edge_cases` 的「有說哪個沒刪掉」用 `"A" in r.stdout + r.stderr`,輸出裡只要有任何一個 A 字母就過,太鬆(目前輸出含 `: A` 才為真,但判準沒鎖那個位置)。`t_runner_isolates_claude_plugin` 在非隔離模式(消費專案直接跑)下仍成立,不是假綠,但只驗環境變數而非 install 真的沒碰真 claude。
- 其他極端輸入實測結果:`LUMOS_HOME=""` 退回預設路徑(`or` 鏈),沒問題;非 UTF-8 塊檔 `errors="replace"` 不崩;`--session` 的 Unicode、全形、超長、尾端換行都回 2。裸 repo、子模組、worktree、Windows 路徑只讀碼,未實測(worktree 與一般 repo 有既有測試涵蓋)。

### 圖譜鏡頭
- 固定席節點逐條:`Systems/lumos-cli-read` 的 ★INVARIANT★(search 預設排除 superseded)與本 diff 無牽連,無矛盾。`Systems/lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只動 sentinel 內)與 install/uninstall 加外掛步驟無牽連,但 `cmd_uninstall` 現在第一個動作就是外掛移除,F7 若成立會在移除失敗時印錯誤後繼續(不早退),不破壞該合約。`Systems/design-loop` 的處置閘條款與本 diff 無牽連。`Systems/每支檔有家` 要求 `scripts/lumos` 的家節點寫到新行為,本 diff 未改圖譜筆記,是否另有提交補上我無法從 diff 判斷(⚠)。`Issues/code-loop守衛main-direct盲區` 為事故背景,與本 diff 無牽連。
- 表態記錄「py-eventloop na」我檢查過:`scripts/lumos` 的新程式沒有 async,成立。

總結:最嚴重 major,blocking 2 條
