severity: major

### 問題一:分層與依賴方向

`_review_yield_round`(讀側,scripts/lumos:5090)是純函式,只吃已經寫進 `.canary-log.jsonl` 的 dict 列(`r.get("reported")`、`r.get("findings_set")` 等既有欄位),不重新解析報告全文——跟寫側 `cmd_canary` 解析報告原文(`_report_severities`/`_report_normalize_issues`,scripts/lumos:5563/5580)是「解析同一類文字」與「消費解析結果」的正常上下游關係,不是各自平行解析同一種東西。`_render_gov_stats`(scripts/lumos:4444)與 `_loop_status_disposal`(scripts/lumos:14190-14193)兩處呼叫端都只用 `_review_yield_round` 這一份計算,呈現各自另寫,符合鄰居 `_severity_check_row` 那種「單一判定函式、呈現分開」的慣例。這條沒有問題。

但 `cmd_report_normalize` 本身放錯層:

### a1 新指令被派進「需要 vault」那一層,實際上它不需要 vault

severity: major
blocking: 是
file: `scripts/lumos:5056`、`scripts/lumos:22606-22607`、`scripts/lumos:22507-22511`
引句:「def cmd_report_normalize(env, path, write=False):」

`cmd_report_normalize` 的 `env` 參數從頭到尾沒被函式本體用到(只操作 `Path(path)` 讀寫)。但 `main()` 把它的 dispatch(`scripts/lumos:22606-22607`:`if args.cmd == "report-normalize": return cmd_report_normalize(env, args.path, write=args.write)`)放在 `vault = args.vault or find_vault(Path.cwd())`(scripts/lumos:22507)這道閘**之後**——這道閘找不到 `docs/*-knowledge` 就直接 `print("擋下:找不到知識圖譜…")` 並 `return 2`。本檔對「純吃一個 markdown 檔路徑、不碰圖譜」這種指令有明確且大量的既有慣例:`fold-check`(22161,help 寫明「vault-free」)、`prose-lint`、`refcheck`(22168)、`quote-check`、`severity-check`、`seat-check`——全部的 dispatch 都刻意排在這道 vault 閘**之前**(22384-22465),讓它們在沒有圖譜的 repo 也能跑。`report-normalize` 跟 `fold-check`/`prose-lint` 是同款「單一 markdown 檔路徑 → 讀/轉/印」,卻被接到 canary 那組(需要 `env` 讀圖譜)後面,继承了不必要的 vault 硬性依賴。測試(`t_report_normalize_cmd`)全程用 `mkvault()` 起手、`run()` 固定帶 `--vault`,沒有任何一條測過「沒有圖譜的 repo 也能跑 report-normalize」,所以這個錯位沒被撞出來。下一個接手的人看到 `env` 參數,合理會以為這支指令要吃圖譜狀態,是「該放哪層」判斷失準的典型後果。

### 問題二:命名與錯誤處理

rc 值全部沿用既有慣例(0 成功、1 部分需人改、2 讀不到/用法錯),跟 `cmd_quote_check`(0 全過/1 有 miss/2 IO 或零引句)同款;stderr 只用在硬錯誤(`OSError`),rc1 的「還有殘留」訊息走 stdout,跟 `cmd_quote_check` 對 miss 訊息的處理一致。`--refuted-set` 的 `id=理由` 解析(`item.partition("=")`)、理由長度門檻沿用既有 `_MANUAL_MIN_CHARS`(scripts/lumos:3060,4246 已有前例)、`re.search(r"[^\W_]", v)` 判「有實字」也是抄既有寫法,不是自創門檻。`_gate_event_or_warn` 呼叫方式(repo_root/gate/kind/note/hard=True)跟既有呼叫點同款。governance-log mapper 對 `canary`+`rejected` 條件式塞 `token=ts` 當第五鑑別子(scripts/lumos:4704),跟既有 `.kill-log.jsonl` mapper「同節點多合約不互吞,自己算 token 當第 5 鑑別子」(scripts/lumos:4713)是同一招,不是第二種去重規則——去重鍵本身(`commit, nodes, gate, kind, token`)只有一份,這裡只是決定 token 填什麼。

### a3 治理帳 kind="rejected" 沒有前例,鄰居用的字是「blocked」

severity: minor
blocking: 否
file: `scripts/lumos:5423`、`scripts/lumos:5583`(對照 `scripts/lumos:14799`、`scripts/lumos:21082`)
引句:「_gate_event_or_warn(_vault_repo_root(env), "canary", "rejected", f"refuted-set-missing loop={loop or ''} auditor={auditor or ''}", hard=True)」

`_gate_event_or_warn` 既有呼叫點對「這次動作被擋下」統一用 `kind="blocked"`(anchor、code-loop 兩處都是),這支是全檔第一次用 `"rejected"` 表達同一種語意(寫側拒收)。因為 `canary` 這個 gate 本來就有自己的 kind 值域(caught/missed/none/second),不是跨 gate 混用一套值域,所以不到「引入第二套判準」的程度,只是同義詞不統一,往後查治理帳要記得「canary 的擋下叫 rejected,別的 gate 叫 blocked」。

### a4 新增子指令參數沒有 help 文字

severity: minor
blocking: 否
file: `scripts/lumos:21850-21851`
引句:「rn.add_argument("--write", action="store_true")」

同檔幾乎每一個 `add_argument` 都帶 `help=`(即使是最簡單的 `path`,鄰居 `fold-check`/`prose-lint` 也寫了 `help="要核對的 markdown 檔路徑"`/`help="要掃的 markdown 檔路徑"`)。這兩行沒有,`--help` 印出來這個子指令會比其他子指令少一截說明。

### 問題三:第二種做法

### a2 同一條「`severity: <值>` 獨立宣告行」正則被逐字複製四次,而不是共用一份

severity: major
blocking: 是
file: `scripts/lumos:4984`、`scripts/lumos:4990`、`scripts/lumos:5020`、`scripts/lumos:5048`(對照原有 `scripts/lumos:4961`)
引句:「if i >= len(lines) or not re.fullmatch(r"severity:[ \t]*(clean|minor|major|blocker)[ \t]*", lines[i]):」

`_report_severities`(scripts/lumos:4952)的 docstring 自稱「★單一 parse 實作★(寫側+severity-check 共用)」,同檔 `_visible_lines`/`_strip_inline_markup` 也各自寫明「★全檔唯一★,別在別處自寫第二份」——這是本專案對「判斷一行文字是不是合法宣告」這件事的明文鐵則。這份 diff 新增的 `_report_normalize_issues`、`normalize_report_text` 裡,`r"severity:[ \t]*(clean|minor|major|blocker)[ \t]*"` 這串正則被原樣手打了四次(而不是抽成一個共用的已編譯正則常數給五處一起用)。功能上四處目前語意一致(靠新測試 `t_report_normalize_cmd` 撐住沒有立即分裂),但這正是鐵則想防的情況:往後只要合法值域改一個字(例如新增一個嚴重度等級、或允許全形冒號),要記得同步改五個地方,漏改一處會靜默造成「正規化器判定合法」但「_report_severities 判定不合法」這種兩套標準打架——而這正好是本專案自己反覆強調要避免的第二套實作。

### a5(⚠ 判不準,交編排者)`report-normalize --write` 與 code-loop skill 「編排者改席報告等於改證據」的既有鐵律之間的界線

severity: minor
blocking: 否
file: `skills/lumos-code-loop/SKILL.md`(對照同檔既有句「編排者改席報告等於改證據」)
引句:「動的是宣告放在哪一行,不是宣告了什麼;轉不了的它印行號,那就退回該席」

skill 文件裡緊接著既有的「不要自己動手改它的報告——編排者改席報告等於改證據」那句話之後,就交代了一個明確會改動席報告位元組內容的工具(`report-normalize --write`),並自行畫線「動的是宣告放在哪一行,不是宣告了什麼」試圖與前句相容。這個界線本身有講清楚、也有測試釘(轉不了的留給人),不是沒交代就硬改——但它畢竟是對一條寫成近乎絕對禁令的既有規則開了一個沒有回頭改寫那句原話的例外,是否算「引入第二種做法」見仁見智,標 ⚠ 交編排者判斷要不要連原句一起修。

---

不對齊共 5 條,其中 major 2 條。
