severity: major

# r1 架構對齊-sonnet(對照面:scripts/lumos 現況,行號以套用 diff 後的檔為準)

## 三問

1. 分層與依賴方向:大部分對齊,一處不對齊。
   - 對齊:新指令 `cmd_loop_cap_decision` / `cmd_loop_retro` / `cmd_loop_retro_stats` 擺在 `cmd_loop_fix_check` 後、`cmd_loop_next` 前,argparse 註冊緊貼 `escape-stats`、dispatch 緊貼 `escape-stats` 分支(`scripts/lumos:46926`、`:47906`),跟 `cmd_loop_escape_stats`(`:11457`)同層。處置閘第八步 `_disposal_retro_step` 的接法(回 "fail"/"ok"/"skip"、banner 的 `_extra` 清單加一項、`fails.append`)與 `_disposal_landing_step`(`:23377`)、`_disposal_clause_step`(`:23316`)同形。五個呼叫端共用 `_cap_retro_status` 一支判定,方向乾淨。
   - 不對齊:讀審查帳與讀治理帳各另寫一支(見 F1、F2);`cmd_loop_status` 讀帳層直接印處置閘 FAIL 橫幅(見 F3)。
2. 命名與錯誤處理:大致對齊。
   - 對齊:rc 0/1/2 與三段式「擋下:…」訊息同鄰居(`cmd_canary` 的 `擋下:` 一族、`fix-check` 的 `沒記到`);`--template` 骨架走 stdout、提示走 stderr,跟 `fix-check --record-template`(`:12455` 起)同一分流;canary 寫側擋下落 `canary blocked` 帶 `id=<隨機碼>` 與 `hard=True`,跟 `:9333`、`:9534` 同形;閘名 `loop-retro` 進 `_KNOWN_GATES`(`:7980` 一帶)。doctor [I2] 用 `warn_soft`、except 用 `warn_soft([], "這一段算不出來…")`,跟 `:2298` 同句。
   - 不對齊:報告路徑正規化另寫一支(見 F4,minor)。
3. 第二種做法:有三處(F1 審查帳讀取、F2 治理帳讀取、F4 路徑正規化),另有 F3 橫幅印在讀帳層。

## Findings

### F1 另寫一支讀審查帳的函式,既有 `_loop_records` 已有同功能
severity: major
blocking: 是 — 引入第二種讀審查帳的做法,既有的單一讀法註解就是為了防這個
- 輸入:任何走新路徑的指令(`canary record` 的人裁擋點、`loop cap-decision`、`loop retro`、`retro-stats`、doctor [I2])。
- 走到哪:`_retro_canary_load`(`scripts/lumos:12975`)自己 `read_bytes` → decode → `splitlines` → `json.loads` → 跳過壞行與 `kind=="spec-gate"` → 依 loop 分組;`_retro_canary_rows`(`:13008`)包一層。這跟 `_loop_records`(`:11849`)的「讀 canary-log、壞行跳過、濾掉 spec-gate」是同一件事。
- 壞在哪:專案已經為「兩份逐行相同的讀帳迴圈會各自漂」收斂成單一讀法——`_loop_records` 的 docstring 寫明「單一讀法」,`cmd_loop_next` 的呼叫處(`:13602`)註解「架構席 s2 r1 major:曾與 helper 逐行重複」,是同型 finding 曾被判 major 的先例。新碼的理由(`_loop_records` 遇非 UTF-8 會丟 `UnicodeDecodeError`、不分組、不看輪次型別)是對既有函式加參數或加一層的理由,不是另寫一支的理由;而且這次同一個差異還在 `cmd_loop_status` 另補了一處 `except UnicodeDecodeError`(`:11550`),讀審查帳的口徑現在有三處。
引句:「讀治理帳直接讀原始 jsonl、檔內順序、壞行跳過——不經 gov 的載入器」
引句:「既有 _loop_records 會冒解碼錯誤、」
- 佐證:file: `scripts/lumos:11849`、file: `scripts/lumos:13602`、file: `scripts/lumos:12975`
- 重現:`grep -n "def _loop_records\|def _retro_canary_load" scripts/lumos` 得 `11849` 與 `12975` 兩支;`grep -n "單一讀法" scripts/lumos` 得 `11850`、`13602` 兩處註解指向前者為唯一讀法。(結構性 finding,無可翻紅的行為測試;未能以行為重現,但引入第二種做法的判準是結構本身,維持 major——若你方認定必須有行為重現則自降為 minor。)

### F2 治理帳讀取另寫 `_retro_gov_events`,鄰居已有多支讀治理帳的載入器 ⚠
severity: minor
blocking: 否 — 計劃內有明講理由(載入器以提交與種類去重),但是鄰居本身口徑也不一(⚠)
- 輸入:`_cap_retro_status` / `_cap_retro_scan` 取人裁與回顧事件。
- 走到哪:`_retro_gov_events`(`scripts/lumos:13031`)直接 `read_bytes` 逐行解析 `GOV_LOG_NAME`,不讀 `GOV_LOCAL_LOG_NAME`。既有 `cmd_gov` 的 `load(GOV_LOG_NAME, _gov_row)` 與 `load(GOV_LOCAL_LOG_NAME, _gov_row)`(`:8376`–`:8377`)兩本都讀。
- 壞在哪:新讀法只認版控帳。目前 `loop-retro` 事件都以 `hard=False` 寫入、能否被 `_gov_routes_local` 導到本機帳取決於 `_GOV_LOCAL_PAIRS`(`:1436`);該集合現在沒有 loop-retro,所以今天不會走偏。判不準的是:鄰居自己也有 `_gov_tail_bytes`(`:3874`)、`_gov_metric_events`(`:4003`)、`:4046` 幾支各讀各的,所以標 ⚠ 不升 major。
引句:「治理帳裡 gate=loop-retro 的事件,檔內順序;壞行(不是 UTF-8、不是 JSON、不是物件)跳過」
- 佐證:file: `scripts/lumos:8376`、file: `scripts/lumos:1436`、file: `scripts/lumos:4003`

### F3 讀帳層 `cmd_loop_status` 直接印處置閘 FAIL 橫幅並 return 1,繞過 `_loop_status_disposal` 的收尾
severity: minor
blocking: 否 — 結構上是跨層直呼(major 判準),但未能構造出行為上的錯結果,依錨紀律自降一級
- 輸入:有人裁紀錄的迴圈,審查帳非 UTF-8 或某列輪次不是字串,跑 `loop status <id> --disposal`。
- 走到哪:`cmd_loop_status` 在 `except UnicodeDecodeError`(`scripts/lumos:11550`)與分輪前(`:11578`)呼叫 `_disposal_retro_ledger_bad`(`:13366`),後者自己 `print("⛔ DISPOSAL GATE FAIL (...)")`(`:13379`)後回 True,呼叫端 `return 1`。
- 壞在哪:全檔「DISPOSAL GATE FAIL」本來只有 `_loop_status_disposal` 一個印處(`:23732`),且該處後續做 `result_out`、`_cap_hint_print(gate=…)`;新路徑印出同一句橫幅卻沒走這些收尾,橫幅與判定出口分成兩處維護。鄰居在讀帳壞時的做法是印「擋下:…」回 2、把判定印出留給處置閘函式。
引句:「print(f"⛔ DISPOSAL GATE FAIL ({loop_id}: 跑滿回顧)")」
- 佐證:file: `scripts/lumos:23732`、file: `scripts/lumos:11550`
- 重現:`grep -n "DISPOSAL GATE FAIL" scripts/lumos` 得 `13379` 與 `23732` 兩個印處。未能構造出行為錯誤。

### F4 另寫 `_retro_norm_path` 做報告路徑正規化 ⚠
severity: minor
blocking: 否 — 只在新比對用,未見與既有解析結果分歧的具體輸入
- 輸入:回顧檔 `evidence` 與帳上 `report_path` 比對。
- 走到哪:`_retro_norm_path`(`scripts/lumos:13055`)自己處理絕對/相對、`resolve`、`normpath`。既有處置閘讀 `report_path` 用 `_prov_path`(非絕對路徑以 repo root 為根解析,`_loop_status_disposal` 內)。
- 壞在哪:同一個欄位 `report_path` 現在有兩套解讀法(一套 join root、一套轉 repo 相對並 normpath)。鄰居對「路徑要不要正規化再比」本身沒有共用函式(`governance/review-reports/<編號>` 這個路徑字串在 `:8620`、`:11972`、`:12350`、`:12356` 也各自內聯,新的 `_retro_dir` 是第五份),所以標 ⚠。
引句:「證據與帳上 report_path 比對前的正規化:repo 內的絕對路徑轉成 repo 相對,再 normpath」
- 佐證:file: `scripts/lumos:11972`、file: `scripts/lumos:12350`

不對齊共 4 條,其中 major 1 條

總結:最嚴重 major,blocking 1 條
