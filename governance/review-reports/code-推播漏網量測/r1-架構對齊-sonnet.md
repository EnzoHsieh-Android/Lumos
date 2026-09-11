severity: major

# 架構對齊審查——推播漏網量測

## 問一:分層與依賴方向

新碼分兩層,跟鄰居一致:shell(`autonomous-loop.sh` 的 `run_lens_weekly`,週跑觸發層)→ python 模組(`governance/autonomous_loop/lens_weekly.py`,單次執行入口)→ 量測引擎(`governance/eval/lens-utilization/recount.py` 裡新增的 `run_misses` 等函式)。呼叫方向與既有的 `run_replay` → `replay_weekly.py` 完全同構,沒有反向依賴(`scripts/lumos`、`scripts/hooks/*` 都沒有反過來 import 這批新碼)。

- 子行程叫 lumos:`Relater.impact()` 用 `subprocess.run([sys.executable, str(self.lumos), "--vault", ..., "impact", "--file", f, "--json"], ...)`,跟 `replay_weekly.py` 的 `_run()`(`governance/autonomous_loop/replay_weekly.py:78-81`,`subprocess.run(["python3", str(repo / lumos), *args], capture_output=True, text=True, timeout=timeout, cwd=str(repo))`)同款(呼叫 `scripts/lumos` 子指令、`--json`、有 timeout)。差一個細節:新碼用 `sys.executable` 不是鄰居寫死的 `"python3"`,不影響行為,判 minor 不獨立列條。
- SourceFileLoader 載 impact-hook 的判斷函式:`recount.py` 新增的 `_hook_filter()`(`governance/eval/lens-utilization/recount.py:928-936`)用 `SourceFileLoader` 載 `scripts/hooks/claude/impact-hook.py` 借 `_decide_one`,跟本檔既有的 `_load_hook_helpers()`(同檔 `34-40` 行,借 `check-graph-sync.py`)手法、路徑深度(`parents[3]`)、回傳 lambda 的風格完全一致。`lens_weekly.py` 的 `_load_recount()` 也是同一招借 `recount.py` 本身。三處手法一致,沒有另立新的模組載入方式。
- git log:`Existence.__call__`(`recount.py:746-780`)用 `subprocess.run(["git", "-C", str(self.repo), "log", "--follow", ...], capture_output=True, text=True, timeout=20)`,跟本檔既有 `git worktree list`(`recount.py:123`)與全 repo 其他 `subprocess.run(["git", "-C", ...])` 呼叫(`refresh_labels.py`、`build_goldset.py` 等)同一套慣例(`-C` 指 repo、`capture_output=True, text=True`)。
- 誰呼叫它:只有 `autonomous-loop.sh` 新增的 `run_lens_weekly()` 呼叫 `lens_weekly.py`,擺在 `run_replay` 之後(`governance/autonomous-loop.sh:467`),跟 `run_nags`/`run_replay` 平行擺放同一節,沒有被其他非週跑路徑(hook、CLI 子指令)呼叫。

這一問沒有 blocking 項——層次與呼叫方向跟鄰居一致。

## 問二:命名與錯誤處理

- 函式命名跟鄰居的 `scan_file`/`scan_codex_file`/`parse_pins`/`classify_bash` 一樣走 snake_case 動詞開頭(`run_misses`、`build_miss_rows`、`parse_push`、`relate_from`、`analyze_claude`、`analyze_codex`),風格一致。
- `main()` 對「一份壞逐字稿」的處理是 try/except 包住單檔、印 `跳過 {f}: {type(e).__name__}`、計進 `broken`(`recount.py:1044-1046`、`1052-1054`)。`run_misses` 對 Claude 與 Codex 兩段檔案迴圈也照抄同一句訊息與 `broken` 計數器(`recount.py` 新增段落尾端兩處 `except Exception as e: broken += 1; print(f"跳過 {f}: ...")`),錯誤處理跟既有 main() 一致。
- 原子寫入:`_atomic_json`(`recount.py:1009-1016`)跟同層最近的 `governance/eval/refresh_labels.py:42-48` 的 `_atomic_write_json` 做同一件事(寫 tmp、`os.replace`),但兩處實作细節不同——見下方 B4(minor)。
- shell 端失敗記帳:`run_lens_weekly` 對「模組沒印出 JSON」的處理跟 `run_replay` 一致(不蓋週戳、log 一句「模組失敗無輸出...明天重試」),但少了 `run_replay` 有的「印原始 JSON 一行」與「MSG:/LINE 通知」兩段——見下方 B5(minor)。

## 問三:第二種做法(引入專案裡原本沒有的做法)

發現兩處「第二種做法」,都在同一支 `recount.py` 裡,跟本檔既有機制重疊:

### B1
severity: major
blocking: 是
新增的 `_search_segments()` 為了抓「這段 Bash 裡有沒有 `lumos search`」,自己另外正規表達式切指令段、再用 `shlex.split` 逐段找 `lumos`+`search` 詞——但本檔的 `classify_bash()` 早就在做幾乎一樣的事:用已借入的 `_segment_command`(`_load_hook_helpers` 借自 `check-graph-sync.py`)切段、`_safe_tokens` 斷詞,並且已經有 `elif sub == "search": search_terms.update(terms)` 這條分支在抓 search 的查詢詞。新函式沒有重用 `_segment_command`,而是自訂 `_CHAIN_RE` 再切一次。以後改「怎麼切一段指令」(例如子殼、更多重導向樣式)得記得兩處都改,兩套邏輯已經有差(`_search_segments` 刻意不切 `|`,`classify_bash` 走的 `_segment_command` 會切 `|`)。
引句:「_CHAIN_RE = re.compile(r";|&&|\|\|")」
file: `governance/eval/lens-utilization/recount.py:51`(既有 `_segment_command` 借入處)與 `governance/eval/lens-utilization/recount.py:183,220`(`classify_bash` 已用它切段、已有 search 分支)

### B2
severity: major
blocking: 是
`run_misses()` 對 Claude 與 Codex 逐字稿各自重新寫了一段「讀檔案→逐行 `json.loads`→用 cwd 篩本 repo」的邏輯,跟本檔既有的 `scan_file()`(Claude,`recount.py:349-361`)與 `scan_codex_file()`(Codex,`recount.py:225-244`)的開頭前奏幾乎逐字重複,卻沒有呼叫或重構共用那段前奏,而是平行再寫一份。cwd 篩選那一行甚至完全相同(逐字比對 `cwds = {str(Path(o.get("cwd")).resolve()) for o in objs if isinstance(o, dict) and o.get("cwd")}` 在兩處出現)。更值得注意的副作用:Codex 那段新前奏漏掉了 `scan_codex_file` 既有的 `cli_version not in CODEX_TRANSCRIPT_VERSIONS` 版本白名單擋(`recount.py:241-243` 的「不在認得的表...不猜格式」),這正是「兩套各自维护、會漂」的具體例子——以後有人修 cwd 篩選或版本擋的規則,大概率只改到其中一份。
引句:「for ln in Path(f).read_text(encoding="utf-8", errors="ignore").splitlines():」
file: `governance/eval/lens-utilization/recount.py:350-351,361`(`scan_file`/`scan_codex_file` 既有前奏,`225-244` 含版本白名單擋)

### B3
severity: minor
blocking: 否
新增的 `Relater`/`Existence` 用 class(`__init__` 存 `self.cache`,`__call__` 當函式用)做「帶預算/逾時的記憶化子行程呼叫」,但本檔沒有 class 先例(整支 `recount.py` 在這次改動前是純函式),而這個「一次 CLI 內快取、閉包記狀態」的需求在鄰近程式碼(`scripts/lumos`)已有慣用寫法是 closure 回傳內層函式,不是 class。結構仍對(沒有跨層、沒有第二套核心邏輯),只是跟最近的同型範例用了不同的語言慣用法。
引句:「class Relater:」
file: `scripts/lumos:8486-8497`(`methods_for`/`hay_for` closure 記憶化寫法)

### B4
severity: minor
blocking: 否
`_atomic_json` 的暫存檔命名(隱藏檔+固定 `.tmp` 尾碼)跟同層最近的 `refresh_labels.py:_atomic_write_json`(`{name}{原suffix}.tmp.{pid}`)、`backlog.py:_save`(`{name}.{pid}.tmp`)三種命名都不同;新函式多做了「寫完讀回 `json.loads` 自驗」這步,`refresh_labels.py`/`backlog.py` 兩處都沒有。方向偏更嚴謹(貼近 canary/build_goldset 那派的「寫後自驗」精神),不是引入新技術(還是 tmp+`os.replace`),但命名與是否自驗這件事三處各寫各的,不是照抄同層最相似檔。
引句:「tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")」
file: `governance/eval/refresh_labels.py:42-48`

### B5
severity: minor
blocking: 否
`run_lens_weekly` 的註解寫「完全照 run_replay 的慣例」,但實際只抄了「週戳+模組失敗不蓋章+逐行印 `LOG:`」這段;`run_replay` 還有「印一行原始 JSON 摘要」(`log "回放週跑原始:..."`)與「有 `MSG:` 才發 LINE 通知」兩段,`run_lens_weekly` 兩段都沒有——`lens_weekly.py` 本身也沒有印 `MSG:` 行。可能是刻意(README 講這段「只出清單與分佈,不設門檻」,不需要告警),但跟自稱「完全照慣例」有落差,是否要補一條 LINE 通知路徑判不準。
⚠ 判不準:是否該補 MSG:/LINE 通知留給編排者裁,若確認這條量測本來就不需要告警,這條可降為不對齊。
引句:「echo "$out" | sed -n 's/^LOG://p' | while IFS= read -r _l; do log "推播漏網週跑:$_l"; done」
file: `governance/autonomous-loop.sh:438,441-446`(`run_replay` 的原始 JSON 行與 MSG/LINE 區塊)

不對齊共 5 條,其中 major 2 條,全份最高嚴重度是 major。
