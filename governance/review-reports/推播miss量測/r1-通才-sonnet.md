severity: blocker

# 逐節審查

## Frontmatter / summary
已讀,無 finding。summary 三條 KEY 與正文條款(S1-S4)、緣起段落敘述一致,交叉引用(`Projects/GraphRAG對節點關聯_調研`、`Projects/主session鏡頭利用率_計劃`、`Systems/retrieval-ranking`)已查證存在。

## 緣起
已讀,無 finding。「既有儀器已經從逐字稿對到每次推播與之後的讀取…但把讀取跟推播清單取交集,沒推卻被讀的那一半直接丟掉;而且只解析『必看』那一段」——查證 `governance/eval/lens-utilization/recount.py:148-166`(`parse_pins`)屬實:只認 `HDR_OLD`/`HDR_NEW`(即「必看」標頭),找到後逐行收 `PIN_LINE` 直到遇到非兩格縮排行才停,對「可能相關」「另外 N 篇」兩段完全不掃描。這段對現況的描述本身是準的,問題出在後面 S1 打算怎麼補(見 A1、A2)。

## PRIOR-ART
已讀,無 finding。「借用觀念、自建小段;零新依賴」與實作規模(擴充既有 500 行腳本)相稱。

## [S1] 推播清單解析三段

A1
severity: blocker
blocking: 是
引句:「推播清單解析三段都認」
`file: \`scripts/hooks/claude/impact-hook.py:630-669\``
`file: \`scripts/hooks/claude/impact-hook.py:870\``
S1 只認「必看/可能相關/另外 N 篇」三段,但 `build_ranked_context`(真正餵進 PreToolUse:Edit/Write/MultiEdit 的函式)還會印第四段「守衛面參考」(`lane`,pin-denoise-a-v4 的軟合約樞紐),且 `inject_ranked_context` 明文承認「lane-only 也注入」——存在完全沒有「必看」段、只有守衛面參考段的真實注入。這段不被 S1 解析,等於把「確實推了」的節點算成「沒推」,直接製造假 miss。

A2
severity: blocker
blocking: 是
引句:「新舊標頭都認,解析不到的段落記 `pushed_complete=false`,不猜」
`file: \`governance/eval/lens-utilization/recount.py:114\``
現有唯一解析器 `PIN_LINE = r"^\s+\S+(?:\s+★[^★]+★)?\s+(.+?\.md)(?:\s|$)"` 是為「必看」段的單一前綴詞格式(`{標記}{★合約★} 節點.md`)寫的。「可能相關」「另外 N 篇」兩段每行卻是雙前綴詞格式(`{分數} {kind} 節點.md`,見 `impact-hook.py:649-659`)。我用該正則實測(python3 re 模組):對 `"  0.72 直接 Systems/xxx.md"` 這一行,捕獲組吃出來的是 `"直接 Systems/xxx.md"`,不是 `"Systems/xxx.md"`——多出的 kind 標記字串被併進節點路徑,永遠比對不上真實節點路徑。`pushed_complete` 只用行數(`len(pins) >= n`)判斷,行數對得上、內容卻是壞字串,不會被這條完整性檢查抓到。若字面沿用這支正則解析新兩段,那兩段的推播清單形同雜訊,凡是被推到「可能相關」或「另外 N 篇」而事後被讀的節點,全部會被誤判成漏推。

## [S2] miss 偵測與三類分類

已讀關於「`lumos impact --file F --json` 的兩條直連規則(反引號完整路徑/裸檔名唯一比對)」——查證 `scripts/lumos:19819-19892`(`_impact_reverse_lookup`)與 `20256-20308`(`cmd_impact`)屬實,JSON 輸出確實有 `direct` 頂層鍵、每項含 `node` 欄(`scripts/lumos:20624-20628`)。這段對程式現況的描述正確。

A3
severity: major
blocking: 是
引句:「這個欄位只拿來排序、不建連結,所以不會跟規則內重複」
`file: \`scripts/lumos:11076-11086\``
「about_code 不建連結」這個事實成立(它只是排序訊號,不進 `_impact_reverse_lookup`),但這推不出「不會跟規則內重複」——一篇筆記的 `about_code` 是否剛好也被同一位作者寫進本文反引號,是內容巧合,跟 about_code 的功能語意無關。我對本庫現有節點實測:98 篇有 `about_code` 的節點裡,15 篇(約 15%)同一路徑同時被本文反引號引用(如 `scripts/lumos`、`scripts/hooks/claude/impact-hook.py`、`governance/autonomous-loop.sh`)。這些節點會同時滿足「規則內」與「關於欄」兩條判準,而 spec 沒給優先序或去重規則——沒有優先序,兩條判準各自獨立跑就會把同一筆 miss 記兩次;隨便挑一條當優先序,分類結果就看實作順序決定,不是 spec 定的,分類結果不穩定。

A4
severity: major
blocking: 是
引句:「由 `governance/eval/refresh_labels.py` 維護;走它既有的流水線」
`file: \`governance/eval/retrieval_eval.py:124-144\``
`file: \`governance/eval/retrieval_eval.py:174-184\``
查了 `refresh_labels.py`+`retrieval_eval.py` 的既有流水線:`edit` 卷每一題的「待標母體」不是外部可以塞任意候選進去的容器,是 `edit_universe(case)` 現場跑 `lumos impact --file <file> --ranked --top 50 --json`、`_touched_edit()` 取 `free[:8]+pins+lane` 算出來的——候選集由「圖譜現在的排序演算法自己覺得該推什麼」決定。`collect_unjudged`(`retrieval_eval.py:223-250`)也只在這個母體裡找「有沒有標」。而 S2「判不出」這一類的定義正是「impact 抓不到規則內、about_code 也沒有」——它本來就是 impact 演算法現在接不到的節點,幾乎不會落在 `edit_universe` 算出的 top-50 母體裡。就算真的把這篇筆記加進 `gs["edit"]`,`collect_unjudged` 掃到的還是演算法自己選的候選,那篇「判不出」的筆記大機率不會被判成「未標」,也就永遠不會被 `delta`/`repin` 流程撈出來要求人工標註——「標完進 edit 卷」這條承諾在目前的 `edit_universe` 設計下基本不會生效。

## [S3] 搜尋零命中

已讀,無 blocking finding。查證 `cmd_search`(`scripts/lumos:2891-3178`):文字模式下「共 N 篇候選」那行(`scripts/lumos:3171`)只在 `ranked=True` 且非 `--files-only`、非 `--regex/--legacy` 時印出,且只走 stdout(所有 fallback/提示訊息都在 `file=sys.stderr`),0 命中時仍會印「(共 0 篇候選…)」——我逐行核對過這條件邏輯,行為與 spec 描述一致。`--json` 模式的 `candidates` 鍵(`scripts/lumos:3146`)只在 `ranked` 分支內,`--legacy --json` 組合會落回舊迴圈、完全不輸出 JSON(`--json` 被靜默忽略)——這會讓該次呼叫的輸出無法解析成「共 N 篇候選」也無法解析成合法 JSON,但這剛好落進 spec 自己定義的「判不出」桶,不算誤判零命中,只是命中率會被低估(而不是算錯)。多詞回退(`_fb_used`)觸發後「幾乎不可能再回 0」是刻意設計(讓真零命中的殘量更精準),跟 S3「先知道零命中有多少」的目標一致,不是缺陷。

## [S4] 每週留存

A5
severity: minor
blocking: 否
引句:「在每日治理那支排程的週期觀測段加一步」
`file: \`governance/daily-governance.sh:243-249\``
`file: \`governance/autonomous-loop.sh:420-474\``
查證:「週期觀測」這個概念實際住在 `governance/autonomous-loop.sh`(第 467 行註解自稱「上面那五段便宜的週期觀測」,含回放週跑、情境探針、空轉提醒、backlog 衰減,各自用 `date +%G-W%V` 週戳記做冪等)。`daily-governance.sh` 本身只是無條件呼叫 `autonomous-loop.sh --dry-run 6`(第 244-248 行),它自己沒有「週期觀測段」這個結構。若字面照 S4 去改 `daily-governance.sh`,容易找錯地方、跳過 `autonomous-loop.sh` 既有的週戳記冪等慣例,自己另開一套判斷「本週跑過沒」的邏輯,徒增維護分裂;不算 blocking 是因為只要打開 `autonomous-loop.sh` 讀一眼就會發現正確位置,不會導致 miss/零命中算錯。

## [S5] README 同步
已讀,無 finding。目標檔 `governance/eval/lens-utilization/README.md` 存在,現有結構(重跑指令段+Codex 段)容得下再加三段。附帶一提(不算 finding,因為跟本案範圍無關):README 現寫「`cli_version` 不在 `CODEX_TRANSCRIPT_VERSIONS`(目前 `0.144.1`)」,但程式碼表已是 `['0.144.1', '0.153.2']`——這是既有 README 的既存落後,不是本 spec 造成的,S5 沒有要求順手修它。

## 邊界與不做
已讀,無 finding。「只量本 repo 的逐字稿(沿用既有 `cwd` 篩法)」——查證 `scan_file` 現有的 cwd 篩選(`recount.py:360-363`)本來就在每份逐字稿的最前面擋,S1-S4 新增邏輯若掛在同一個函式體內會自動繼承這條篩選,沒有繞過的空隙。「不改 `docs/.usage-log.jsonl`」「結果不回灌排序」等排除項與計劃本文一致,沒有語意漂移。

## 承認的限制

A6
severity: major
blocking: 是
引句:「search 輸出措辭一改就會數錯」
`file: \`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md\``(CLAUDE.md 鐵則四:回頭條件要接電)
這一條限制跟前三條(位置偏差、用現在的圖譜判當時的推播、量不到 Bash 改檔)不一樣——前三條每條都附了獨立一行 `REVISIT:YYYY-MM-DD …`,這一條完全沒有,只給了一條「驗收要有測試釘住」的緩解(pinning test 只能防止未來悄悄改壞而不出聲,不能回答「這個偵測法本身夠不夠用」這個問題,例如 `--files-only`/`--regex` 呼叫比例上升會讓「判不出」桶系統性膨脹,零命中數字被低估到什麼程度沒人會去查)。CLAUDE.md 鐵則四明寫「純散文的回頭條件=沒人會回頭」,這條缺 REVISIT 正是那個模式,是本 spec 自己違反了它所屬專案的硬規則,不是我在挑格式。

## 實務隱患

已讀併發段,無 blocking finding。「週跑寫的是本週一個檔、寫暫存、自驗讀得回來、再整個換名…同週重跑覆寫」——原子寫入(暫存+驗證+換名)這件事查證過(本 repo `daily-governance.sh` 的 `write_health` 走同一套慣例),能保證「兩個週跑同時跑」時不會寫出半份壞檔,最壞情況是白算一次(TOCTOU:兩邊都讀到「本週沒檔」再各自跑),不算資料錯誤,只是浪費——結合 A7 的成本數字,一次白算是幾十秒到一分半鐘等級,值得留意但不到 blocking。

A7
severity: major
blocking: 是
引句:「現在一次約數秒到十幾秒;放在週跑、本週跑過就跳過」
`file: \`governance/eval/lens-utilization/recount.py:433-459\``
兩點實測都跟這句宣稱對不上。①現在的基準本身就已經超出宣稱區間:我直接對本機 `~/.claude/projects`(2478 份逐字稿+Codex rollout)跑一次 `recount.py --repo .`,`/usr/bin/time -p` 量到 `real 25.64s`——不是「數秒到十幾秒」。②S2 要求對每個 miss 候選跑 `lumos impact --file F --json`,我單獨測一次冷啟動(含全圖重新載入+對每篇筆記做 `_refcheck_scan`)量到 `real 1.55s`;本庫目前這批逐字稿只涵蓋 38 個 distinct 被改動的檔案,光是這些就要多跑 38 次、約 59 秒——而且這個掃描範圍是「全部歷史逐字稿」,沒有任何時間窗篩選,語料只會越積越多,子行程開銷只會隨時間增加、不會因為「本週跑過就跳過」而封頂(那句只擋「同一週不重算」,不擋「歷史語料每週都重算一次」)。這個落差會讓實作者用錯誤的成本預算做決定(例如沒設超時、沒想過要幫 impact 呼叫做快取/批次化)。

A8
severity: major
blocking: 是
引句:「資源:只開檔讀;不開連線。」
`file: \`scripts/lumos:20256-20308\``(`cmd_impact` 每次呼叫重建 `Env(vault)`)
這句話本身就跟同一份 spec 的 S2 條款互相矛盾:S2 明寫「規則內」miss 要用 `lumos impact --file F --json` 判——那是另開一個 python3 子行程、重新載入整個知識圖譜(`Env(vault)`)、對 vault 內每一篇筆記重新讀檔掃描 inline-code(`_impact_reverse_lookup` 逐篇 `md_path.read_text()`)。這不是「只開檔讀」的等級,是每次呼叫都要重做一次近乎全圖掃描的 CPU/記憶體工作(實測單次 1.55 秒,見 A7)。「實務隱患」這節本該是把 S1-S4 全部條款的真實成本攤開來看,這句話只回答了「S4 本身讀逐字稿」這一半,漏掉了 S2 引入的子行程成本。

A9
severity: major
blocking: 是
引句:「只存推導列(節點名、檔名、計數、零命中查詢字串),不存原文」
`file: \`governance/eval/lens-utilization/2026-09-04-first-report.json\`(git 已追蹤,`git ls-files` 確認)`
「零命中查詢字串」被歸進「安全的推導列」,但它跟節點名/檔名/計數本質不同——那三者是這個 repo 自己的結構事實,查詢字串卻是使用者或 agent 在那一刻自己選的自由文字,跟 spec 前一句自己承認的風險「逐字稿可能含其他專案內容」完全同源(agent 把別的專案脈絡的字眼寫進搜尋詞是這個功能設計上就會發生的事,不是邊緣情境)。而且 S4 明寫週報表比照「2026-09-04 那份首報進版控的慣例」——我核對過,`2026-09-04-first-report.json`/`.txt` 確實被 `git ls-files` 列出、已進版控,代表這份週報表一旦寫入就會被提交、永久留在 git 歷史裡(即使日後從 HEAD 刪掉也還在)。把帶著跨專案內容風險的自由文字永久寫進版控,跟「不存原文」這句話講的隱私邊界是衝突的。

## 驗收(測試先行)
已讀,無 finding。五條驗收案例(三段全認/miss 三分類/零命中配對/週跑冪等+不含原文/既有測試全綠)本身作為測試骨架是合理的動作描述;它們沒有回答「怎麼解析」「怎麼跟 edit 卷對接」這些會不會算對的問題,那些缺口已經在 A1-A4、A9 標出。

# 固定席節點逐條判(計劃牽連/直接連結節點)

- `Systems/retrieval-ranking.md`(計劃連結):本案不改排序演算法本身、不回灌排序(邊界與不做已明寫),只是新增一支讀逐字稿的量測腳本。不影響——它宣稱的排序行為完全沒被這份 spec 的任何條款碰到。
- `Systems/canary-audit.md`(間接相依,★INVARIANT★ ×2):兩條 INVARIANT 都在講「canary record/second 這個機制」——record 落盤要驗證讀得回來、second 只是 telemetry 不影響 gate/rc。本案完全沒有寫 canary、沒有呼叫 `lumos canary record`/`second`,summary 第三條 KEY 也明寫「這改動儀器『不寫任何帳』的約定」且不進 `lumos gov`。不影響——這份 spec 的寫入路徑(週報表)跟 canary 記錄是兩條完全不相交的機制。
- `Issues/canary-record未落盤事件.md`(事故):同上,本案不碰 canary 落盤路徑。不影響。
- `Issues/code-loop守衛main-direct盲區.md`(事故):在講 code-loop 對「直接推 main」這種繞過 PR 的盲區,是 pre-push/CI 守衛邏輯的既有洞。本案不改 code-loop 守衛,只是待實作的評測腳本本身仍要走正常的 code-loop 審查再推送。不影響。
- `Issues/hook卸載殘留註冊.md`(事故):在講 hook 安裝/卸載生命週期殘留登記。本案不碰 hook 的安裝/卸載機制(只讀 hook 已經寫進逐字稿的注入內容)。不影響。
- `Issues/init-force-slug誤用basename.md`(事故):在講 `lumos init --force` 的 slug 算法誤用 basename。本案不碰 init/slug。不影響。
- `Issues/vendored測試套件在消費端假紅.md`(事故):在講消費專案 vendored 這個 repo 的測試套件時的假紅問題。本案新增的測試(`t_lens_recount_*`)加在既有 `scripts/test_lumos.py`,跟既有測試同一套 vendored/skip 機制,沒有另開新的測試載入路徑。不影響——但如果實作時新測試需要讀 `~/.claude/projects` 之類的機器本地路徑而在消費端沒有這個目錄,要留意跟既有「消費端假紅」同一類坑(現有 `t_lens_recount_classify` 已經是用臨時目錄構造 fixture,不依賴機器本地逐字稿,新測試若跟進同一模式就不會踩到)。
- `Systems/known-pitfall-refresh-token.md`(牽連 `retrieval-goldset.json`):是前端 refresh-token 並發設計的一般性坑知識,跟本案的 `retrieval-goldset.json` 使用方式(當作 edit/search 評測題庫)在主題上不相關,只是文件本身用了 `retrieval-goldset.json` 這個檔名字串被連結工具帶進來。不影響。

# 總結

全份最高嚴重度是 blocker。blocking 共 8 條(A1、A2、A3、A4、A6、A7、A8、A9);非 blocking 1 條(A5,minor)。核心問題:S1 的「三段都認」漏了 impact-hook 真實會印的第四段(守衛面參考/lane,且有 lane-only 注入的真實路徑),而且沿用現有 `PIN_LINE` 正則解析新增的兩段會把分數/標記字串吃進節點路徑、產生比對不到的壞字串——這兩點加起來會讓「推了」清單系統性失真,miss 計數從源頭就算錯;S2 的「關於欄不會跟規則內重複」被本庫實際資料反證(15/98 重疊),「判不出候選進 edit 卷既有流水線」跟該流水線「候選母體由演算法自己算」的既有設計互斥,基本不會生效;實務隱患節低估了 S2 帶來的子行程成本(實測數字已附)且把「零命中查詢字串」誤歸類成安全的推導資料、卻又要求它進版控永久留存。
