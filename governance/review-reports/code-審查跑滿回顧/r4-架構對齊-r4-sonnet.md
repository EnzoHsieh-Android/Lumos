severity: major

席名:架構對齊-r4-sonnet(第 4 輪)。鏡頭:只判寫法跟專案既有做法一不一樣。材料:/tmp/code-capretro-r4.patch 全文讀完,並以 repo 現檔 scripts/lumos 查證。

已看過、判定沒有第二套做法而不列的地方:`_retro_path_unsafe` 走共用 `_repo_path_unsafe`(scripts/lumos:32040);`_fix_bad_strings(nul=False)` 取代 `_retro_utf8_bad` 後 repo 內已無殘留呼叫;`_drift_ledger_path_err` 新增「不是一般檔」判斷對其他呼叫者(scripts/lumos:35477、35483、36330)無行為差異,`t_note_audit_drift_share_repo_path_guard`、`t_note_audit_repo_path_guard_outside_and_recheck` 實跑全綠;`_ledger_tail_needs_newline` 的 lseek+read 與既有 `_ensure_local_ignore` 檔尾判法(scripts/lumos:22335)同一寫法;審查帳讀者 `.splitlines()` 殘留只剩逃逸帳、簽核帳、CI 帳等計劃明講不在範圍的帳;`_esc_clean` 與 `_json_text_escaped`、`_kill_esc` 三者的分工有 docstring 說明理由,不算兩套。

### F1 治理帳與審查帳還有第二套切行規則,跟 _ledger_lines 自稱的「唯一規則」打架 (修補引起)
severity: major
blocking: 是 — 同一件事(切治理帳/審查帳的行)現在有兩套實作,而且新加的 docstring 與測試都宣稱只有一套,r3 修補的目標(同一列在不同讀者眼中行數相同)沒達成。
- 輸入:治理帳(或審查帳)用 CR 當行尾的檔(整本 `\r` 分隔,正是 r2 為 `_ledger_lines` 加 `\r` 支援的情境)。
- 走到哪:`_retro_gov_events`(跑滿回顧一族)走 `_ledger_lines`,認得兩筆事件;`lumos gov` 的載入器(`load(GOV_LOG_NAME, _gov_row)`、`load(".canary-log.jsonl", …)`,scripts/lumos:8372 `for d in _drift_jsonl_parse(_raw)`)、`_gov_ledger_rows_by_time`(scripts/lumos:1408)、度量與 doctor 帳增速(scripts/lumos:2456、4045)、`_fix_check_events`(scripts/lumos:12687 自己 `raw.split(b"\n")`)讀同兩本帳,走的是只在 `\n` 切行的 `_drift_jsonl_iter`(scripts/lumos:35182)。
- 壞在哪:同一檔,閘讀到 2 筆人裁/回顧事件,gov 統計與 fix-check 事件讀到 0 筆;`_ledger_lines` 的 docstring 說「讀者一律走這一支」、r3 筆記說「兩本帳其餘讀者共 20 處全部換掉」,實際上治理帳至少五個讀者沒換。`t_cap_retro_r3_ledger_lines_everywhere` 只掃 `.read_text(...).splitlines()` 樣式,掃不到 `_drift_jsonl_*` 與 `raw.split(b"\n")`,所以綠。對照既有做法:`_drift_jsonl_parse` 的 docstring(scripts/lumos:35175-35180)寫的是另一條「只在 \n 切行」的規則,兩條規則並存。
引句:「★審查帳(.canary-log.jsonl)與治理帳(.governance-log.jsonl)的讀者一律走這一支★」
file: `scripts/lumos:8372`、`scripts/lumos:1408`、`scripts/lumos:12687`、`scripts/lumos:35182`
重現(當場跑出):
```
python3 - <<'E'
import importlib.machinery, importlib.util
l=importlib.machinery.SourceFileLoader("lumosm","scripts/lumos"); s=importlib.util.spec_from_loader("lumosm",l); m=importlib.util.module_from_spec(s); l.exec_module(m)
raw=b'{"gate":"loop-retro","kind":"cap-decision","loop":"a"}\r{"gate":"loop-retro","kind":"skipped","loop":"a"}\r'
print(len([x for x in m._ledger_lines(raw) if x.strip()]), len(m._drift_jsonl_parse(raw)))
E
```
輸出 `2 0`。

### F2 loop next 到 cap-reached 時,記人裁的同一句提示被兩套實作各印一次 (修補引起)
severity: major
blocking: 是 — 同一個提示有兩個產生處、措辭不同、守衛不同,同一次輸出重複出現;計劃 S6 與 S19 各自守一處,沒人守兩處合起來的輸出。
- 輸入:標準分級、帳上 3 輪、處置閘沒過(審後又改了規格)的代碼審迴圈,跑 `loop next --spec …`,階段 cap-reached。
- 走到哪:`emit` 文字輸出先印 `cap_retro`(`_cap_retro_next_lines` 的第一行,scripts/lumos:13631),最後再印 `_cap_hint_lines(_ch, loop_id=loop_id)`(scripts/lumos:14228),後者這次新增了同一條指令。
- 壞在哪:同一份輸出裡記人裁的指令出現兩次(措辭一句「人裁要破例再開一輪…先記人裁:」、一句「人裁:要破例再開一輪…先記人裁(已記過就不用再記):」);已記人裁且回顧已記時,`_cap_retro_next_lines` 印「回顧已記」,`_cap_hint_lines` 仍印「先記人裁」,同一輸出自相矛盾。對照既有做法:`_retro_cmd` 的 docstring(scripts/lumos 的 `_retro_cmd`)規定印給人照貼的指令只由一支組,而 `lumos loop cap-decision` 指令現在在 scripts/lumos:8989、13537、13547、13631、13733 五處各自手組字串,r3 又添一處。
引句:「lines.append(_esc_clean(P + "人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記):"」
file: `scripts/lumos:13631`、`scripts/lumos:14200`、`scripts/lumos:14228`
重現(當場跑出,用 test_lumos 的 `_cr_repo`、`_cr_loop` 造帳,LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26,等同 `t_cap_retro_loop_next_hint` 前置):`loop next crx --spec <改過的規格> --repo <根>` 輸出尾段依序為
```
  note: 跑滿 3 輪還沒收斂——停下來,剩下的交給人裁決,別無限燒下去
  人裁要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision crx --decision extra-round|accept-risk --note "<理由>"
[cap-hint] 已經跑了 3 輪,到了分級 standard 的上限 3 輪。…
  人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記):lumos loop cap-decision crx --decision extra-round|accept-risk --note "<理由>"
```

### F3 把「治理帳壞」塞成一個假迴圈編號放進迴圈清單,retro-stats 把它算成一個有人裁紀錄的迴圈 (修補引起)
severity: minor
blocking: 否 — 只影響統計與提醒的數字,不影響擋點判定。
- 輸入:docs/.governance-log.jsonl 是符號連結(指到 repo 內的檔),跑 `loop retro-stats`。
- 走到哪:`_cap_retro_scan` 回 `[("(治理帳)", {...})]`,清單型別是 [(迴圈編號, 判定)],呼叫端 `cmd_loop_retro_stats`(scripts/lumos:13845)與 doctor I2(scripts/lumos:2314)把它當迴圈處理。
- 壞在哪:實跑輸出 `[retro-stats] 有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)`,`totals.loops` 與 `by_decision["?"]` 各 +1,--json 的 `loops` 陣列多一筆 `"loop":"(治理帳)"`;doctor 標題「N 個迴圈記了人裁」也把它算進 N。對照既有做法:同一函式對「單一迴圈判壞」用的是帶真實編號的 error dict(scripts/lumos:13507),帳級錯誤沒有獨立通道。
引句:「return [("(治理帳)", {"error": gerr, "decision": {}, "applies": True, "state": None, "problems": []})]」
file: `scripts/lumos:13488`、`scripts/lumos:13845`
重現:
```
python3 - <<'E'
import importlib.machinery, importlib.util, tempfile, os, types, pathlib
l=importlib.machinery.SourceFileLoader("lumosm","scripts/lumos"); s=importlib.util.spec_from_loader("lumosm",l); m=importlib.util.module_from_spec(s); l.exec_module(m)
d=pathlib.Path(tempfile.mkdtemp()); (d/"docs").mkdir(); (d/"real.jsonl").write_text("")
os.symlink(d/"real.jsonl", d/"docs"/".governance-log.jsonl")
m.cmd_loop_retro_stats(types.SimpleNamespace(vault=d/"docs"/"v"), repo=str(d))
E
```
首行輸出 `有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)`。

### F4 帳上字串印進 JSON 骨架有兩種做法:跑滿回顧用 _json_text_escaped,同型的 fix-check --record-template 仍原樣印
severity: minor
blocking: 否 — 既有指令的既有行為,r3 新增的跳脫沒有擴到同型輸出。
- 輸入:`canary record … --findings-set $'F1\x9b2J'`(發現 id 沒有字元集檢查,scripts/lumos:9344 一帶只拆逗號與查重複),折入後跑 `loop fix-check <編號> <輪> --record-template`。
- 走到哪:`_fix_check_template` 用 `json.dumps({...}, ensure_ascii=False, indent=2)` 直接 print(scripts/lumos:12575),`groups[].findings` 帶著帳上的 id。
- 壞在哪:`json.dumps(["F1\x9b2J"], ensure_ascii=False)` 輸出 `'["F1\x9b2J"]'`,C1 字元原樣進終端;r3 為了同一類問題在 `--template` 新寫了 `_json_text_escaped`(類別走共用 `_PATH_SPECIAL_CATS`),但它只掛在回顧骨架,沒成為「帳上字串印成 JSON」的共用做法,同一類輸出現在兩套行為。
引句:「text = _j.dumps(obj, ensure_ascii=False, indent=indent)」
file: `scripts/lumos:12575`、`scripts/lumos:13240`

總結:最嚴重 major,blocking 2 條
