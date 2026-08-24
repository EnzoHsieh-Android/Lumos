# selfaudit-loop r1 架構對齊審查

被審:`/tmp/selfaudit-loop-r1.md`(自足性審計閉環_計劃,75 行)。只判「跟本專案既有做法一不一致」,不找 bug、不評風格。對照對象:`governance/autonomous-loop.sh` 的 `run_nags`/`run_probe`/`run_exam` 三個既有排程函式(週戳/log/LINE/錯誤處理)、同檔案 orchestrator 派工段(`claude -p` 呼叫與 `orchestrator_result` 成本抽取)、`scripts/lumos` 的 `run_doctor` Check S 判定現況、全庫 `LUMOS_*` knob 命名慣例、`governance/pending/`+`governance/review-reports/self-audit/` 既有檔名慣例、`self_audit` 欄位既有值域。

---

## 問一:分層與依賴方向——`run_selfaudit` 的派工邊界、`claude -p` 的權限範圍,跟「判定同源」在 Check S 現況下能不能真的 import

**每篇 `claude -p` 的權限範圍未定,且同一支腳本裡三種既有先例中最貼近用途的那個沒被引用——不對齊,major。**

spec 只寫「對每篇 `claude -p` 派乾淨 agent(sonnet;prompt=今天手動版的同款:只讀該篇+對照 code 抽驗」(`/tmp/selfaudit-loop-r1.md:39`),完全沒提 `--allowedTools`/`--permission-mode`。

引句:「只讀該篇+對照 code 抽驗」(`/tmp/selfaudit-loop-r1.md:39`)

但同一支 `autonomous-loop.sh` 裡,唯一既有的 `claude -p` 呼叫是 orchestrator 派工段,權限是 `--allowedTools "Read,Edit,Bash,Grep,Glob,Agent" --permission-mode acceptEdits`(`governance/autonomous-loop.sh:202-203`)——**含 Edit 與 Bash**,因為 orchestrator 的工作本來就是寫 spec 檔。若實作時就地照抄「這支腳本裡唯一現成的 `claude -p` 範本」,一個被 spec 自己定性為「只讀」且明文「★不動筆記★」(`/tmp/selfaudit-loop-r1.md:44`)、「不自動修筆記(寫入紀律不破)」(`/tmp/selfaudit-loop-r1.md:9`)的審計 agent,會拿到寫檔與跑指令的能力——單靠 prompt 約束「不要寫」,而不是機制擋。本庫其實已有貼合這個用途的先例:`governance/ai-governance-research.sh:135` 的唯讀研究 agent 用 `--allowedTools "Read,WebSearch,WebFetch"`,不含 Edit/Write/Bash。spec 沒有引用這條、也沒有排除 orchestrator 那條,兩個方向都沒交代。

更關鍵的是,這支腳本本身在 2026-07-29 已經留過一次跟「子 agent 權限範圍」直接相關的裁定紀錄:「非 dry-run 停用…子 agent 權限隔離…confused-deputy 已知漏洞…不留可執行入口」(`governance/autonomous-loop.sh:8-10`)。spec 要新增的 `run_selfaudit` 明確會在非 dry-run 場景下常態執行(週排程、非人工觸發),卻沒有對照這條同檔案裡已經存在、且是因為同一類風險而寫下的先例。判為 major:這不是命名或風格問題,是「這個新派工點該用哪一種既有的權限模板」的分層問題,選錯模板會讓 spec 自己宣稱的不可變性(不動筆記)失去機制保障,退化成純自律。

**「判定同源」主張與 Check S 現況不符——不對齊,non-major(但有滑向 major 的風險)。**

spec 設計第 1 條:「讀 doctor 的 Check S 同源判定(sa_missing ∪ sa_stale;★不 shell 出去 grep doctor 輸出,直接 import lumos 模組呼叫同一套判定,單一實作★)」(`/tmp/selfaudit-loop-r1.md:35-36`)。

引句:「直接 import lumos 模組呼叫同一套判定,單一實作」(`/tmp/selfaudit-loop-r1.md:36`)

但實際去看 `sa_missing`/`sa_stale` 的計算邏輯:整段(收集迴圈、PageRank 排序、格式化)都寫在 `run_doctor` 函式體內(`scripts/lumos:459` 定義開始,Check S 本體在 `scripts/lumos:823-851`),是區域變數與區域邏輯,**不是可以從外部 import 呼叫的頂層函式**——目前沒有任何東西可以讓 `selfaudit_pick.py` 直接呼叫到「同一套判定」。本庫對這類「多個呼叫點要共用同一套判定邏輯」的既有慣例是抽成頂層函式:`about_code_expired`(`scripts/lumos:7736` 定義)同時被 `run_doctor` 的 Check S2(`scripts/lumos:888`)與完全獨立的 `cmd_impact`(`scripts/lumos:14128`)呼叫,是同一套判定被兩處引用而不重寫的實際先例。spec 要做到自己講的「單一實作」,勢必要先把 `sa_missing`/`sa_stale` 依同一模式抽成頂層函式(例如 `_doctor_self_audit_gaps(env)`),再讓 `run_doctor` 與 `selfaudit_pick.py` 都呼叫它——但 spec 現在的寫法讀起來像是這個介面已經存在,只差 import 一步,並未把「重構 `run_doctor`」列為工作項。若實作時因為不想動已上線的 `run_doctor`(有既有測試釘住,見 `scripts/test_lumos.py:19609` 對 `run_doctor` 簽名的反事實測試)而選擇繞過抽取、直接在 `selfaudit_pick.py` 裡另寫一份等價的 `sa_missing`/`sa_stale` 計算,就會變成 spec 自己想避免的「第二種做法」(兩處各自維護一份同語意判定)——判定現在還沒發生,標非 major,但這是一個会在實作階段被迫二選一的分岔點,建議 spec 補一句「先抽頂層函式」再進 design-loop 下一輪。

**`run_nags`/`run_probe`/`run_exam` 的週戳/log/LINE 骨架——對齊。**

spec 明寫「週戳記防重跑,同 run_nags 慣例」(`/tmp/selfaudit-loop-r1.md:38`)與「LINE 通知沿 run_nags 慣例(有 FAIL 才通知)」(`/tmp/selfaudit-loop-r1.md:47`)。核對三個既有函式:`run_nags` 用獨立戳記檔 `nags-last-week.txt` 比對 `date +%G-W%V`(`governance/autonomous-loop.sh:118-119`)、`run_probe` 用 grep 既有 history.jsonl 裡本週 seed 是否已記(`governance/autonomous-loop.sh:93`)、兩者都是「非本週才跑,跑完才通知」且全程 `|| true` 包裹、`log()` 記一行——spec 引用的正是這個共用形狀,是本審查範圍裡少數完全站得住的對齊點。唯一沒寫清楚(⚠,不計入下方條數)的是:抽不到 `VERDICT` 行時「當 FAIL 處理(fail-closed)+ log 死因尾段(NO_JSON 教訓同款)」(`/tmp/selfaudit-loop-r1.md:46`)裡的「NO_JSON 教訓同款」,究竟只是借用「把死因塞進 log 行尾」這個記錄手法(orchestrator 段 `scripts/lumos` 呼叫處 `governance/autonomous-loop.sh:213` 的 `NO_JSON:` 字串拼接同款),還是連同 `governance/autonomous-loop.sh:254` 那行「解析不到就 `exit 1`」的**整支腳本中止**行為一起借用。若是後者,會直接違背 `run_nags`/`run_probe`/`run_exam` 三者共通的「絕不讓內部失敗逃出、拖垮當天其餘排程」的紀律(這支腳本開頭 `set -euo pipefail`,三個既有函式內每個有風險的指令都手動 `|| true` 擋)。spec 文字本身兩種讀法都通,判不準。

---

## 問二:命名與錯誤處理

**knob 命名 `SELFAUDIT_WEEKLY_N`——不對齊,non-major。**

spec:「按 PageRank 降冪取前 `N=2`(週配額;knob `SELFAUDIT_WEEKLY_N`,0=關)」(`/tmp/selfaudit-loop-r1.md:37`)。

引句:「knob `SELFAUDIT_WEEKLY_N`,0=關」(`/tmp/selfaudit-loop-r1.md:37`)

全庫 `os.environ.get(...)` 讀到的旋鈕(`scripts/lumos`)清一色掛 `LUMOS_` 前綴:`LUMOS_IMPACT_ABOUT`(`scripts/lumos:878`)、`LUMOS_RANK_MOC_MULT`(`:1507`)、`LUMOS_KILL_TIMEOUT_FLOOR`(`:5745`)、`LUMOS_DELGUARD_DEADLINE`(`:12153`)、`LUMOS_TEST_TIMEOUT`(`:14970`)等十餘例,一個例外都沒有;且 spec 用的「knob」「0=關」措辭本身就是照抄這套慣例的語彙(例如 `LUMOS_IMPACT_ABOUT` 註解「總開關…0=整段略過」,`scripts/lumos:875-878`)——借了語意卻沒借命名格式。另一方面,`autonomous-loop.sh` 自己對「每週配額/上限」這類設定,既有慣例其實是**寫死的區域變數**而非環境變數旋鈕:`SKIP_CAP=3`(`governance/autonomous-loop.sh:139`)、`MAXR="${2:-6}"`(`:7`),整支腳本查無任何 `os.environ.get` 風格的自訂旋鈕。也就是說 `SELFAUDIT_WEEKLY_N` 兩邊都不是嚴格複製:比照 `LUMOS_*` 該叫 `LUMOS_SELFAUDIT_WEEKLY_N`,比照 `autonomous-loop.sh` 自己的配額慣例則該是寫死常數而非環境變數。判非 major(純命名/機制選擇,不影響行為正確性)。

**`self_audit` 值域新增 `-auto` 後綴——不對齊,non-major(是否算「第二種做法」判不準)。**

spec:「`lumos self-audit <篇> --model <agent-model>-auto`(自動蓋章;model 名帶 -auto 供追溯」(`/tmp/selfaudit-loop-r1.md:42`)。

引句:「`lumos self-audit <篇> --model <agent-model>-auto`」(`/tmp/selfaudit-loop-r1.md:42`)

`cmd_self_audit`(`scripts/lumos:7578-7593`)把 `--model` 原樣塞進 `self_audit: <model>/<date>`,argparse 對 `--model` 沒有 `choices` 限制(`scripts/lumos:15616`),Check S 讀值時只用正則抓日期、完全不解析 `/` 前半段(`scripts/lumos:834-838`),`cmd_gov` 的六帳彙整也不讀 `self_audit` 欄位——所以「-auto」後綴技術上不會被任何既有消費端拒絕或誤判,格式上合法。但查全庫既有的「這是自動流程產出/執行的」標記慣例,一律是**前綴**掛在新識別碼上,不是後綴掛在既有值域裡:`auto-$TODAY`(canary loop id,`governance/autonomous-loop.sh:245`)、`auto/spec-$TOPIC-$TODAY`(分支名,`:377`)、`auto-spec: $TOPIC`(commit 訊息與 PR 標題,`:380-381`)、`auto-loop-$TODAY`(暫存目錄,`:19`);`grep -rn "\-auto\b\|_auto\b" scripts/lumos` 在整個 lumos CLI 裡零命中,`self_audit` 目前約 28 筆既有值(如 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:6` 的 `self_audit: claude-fable/2026-08-24`)也沒有一筆帶後綴。是否構成「第二種做法」見結論 ⚠。

**pending 檔名 `<日期>-selfaudit-<篇>.md`——大致對齊,一處自我不一致(non-major)。**

spec:「報告+修正建議寫 `governance/pending/<日期>-selfaudit-<篇>.md`」(`/tmp/selfaudit-loop-r1.md:44`)。`pending/archive/` 既有兩筆真實案例都是「日期-主題.md」加一個「-限定詞尾綴」的伴生檔:`2026-07-14-corrosion-gauge.md` + `2026-07-14-corrosion-gauge-confidence.md`。`selfaudit-<篇>.md` 把「selfaudit」放在日期與篇名**中間**(中綴),不是尾綴,大方向(日期打頭)仍對齊,細節格式不完全同款。更值得注意的是 spec 自己在同一份文件裡,對「同一機制的另一個輸出檔」用了不同格式:`VERDICT: PASS` 產出的報告寫在 `governance/review-reports/self-audit/<日期>-<篇>.md`(`/tmp/selfaudit-loop-r1.md:40`,零中綴),這個路徑本身跟既有真實檔案 `governance/review-reports/self-audit/2026-08-24-lumos-cli-read.md` 完全對得上;但 `FAIL` 分支的 pending 檔卻多插了「selfaudit-」中綴。同一份 spec 對「日期+篇名」這件事,PASS 分支零中綴、FAIL 分支加中綴,兩者本可以是同一個公式。

引句:「`governance/pending/<日期>-selfaudit-<篇>.md`」(`/tmp/selfaudit-loop-r1.md:44`)

---

## 問三:第二種做法——有沒有引入專案裡原本沒有的做法

**`run_selfaudit` 另開一條 `claude -p` 派工迴圈——對齊,不是第二種做法。**

這支腳本目前只有 orchestrator 一處內嵌的 `claude -p` 呼叫,但另一個既有腳本 `scripts/scenario_probe.py` 早就示範過「獨立於 orchestrator 之外、自己組 `claude -p` 指令陣列跑派工迴圈」的做法(`cmd = ["claude", "-p", sc["prompt"], ...]`,`scripts/scenario_probe.py:121-124`),且已被 `run_probe`(`governance/autonomous-loop.sh:90-113`)接進同一支 `autonomous-loop.sh` 當週排程。本庫「同一支腳本裡有多個各自獨立的 `claude -p` 派工點」本來就是既有形狀,`run_selfaudit` 再開一條不算引入新機制。

**成本抽取(`orchestrator_result.extract_cost` + `lumos canary record`)沒被沿用——判不準,⚠,不計入下方條數。**

spec 的「成本護欄」只寫「單篇 timeout 15 分鐘;週配額 N=2;LINE 通知沿 run_nags 慣例」(`/tmp/selfaudit-loop-r1.md:47`),完全沒提是否要把每篇 `claude -p` 的實際花費接進 `orchestrator_result.extract_cost`/`cost_cli_args`/`lumos canary record`(`governance/autonomous-loop.sh:222-252`,同日剛建立、註解自稱「★填既有欄,不建新機制★」)。若比照 orchestrator 派工段,這是明顯漏接;但本庫在這件事上其實**沒有單一慣例**可對照——`scenario_probe.py` 的 `claude -p` 呼叫(既有、比 orchestrator 這段成本抽取更早)本身就完全沒有走 `extract_cost`/`canary record` 這條路,只記通過率。也就是說「新的 `claude -p` 派工點要不要接成本記帳」在本庫現況裡本來就一半一半(orchestrator 接、scenario_probe 不接),不是一個有唯一答案的既有慣例,判不準。

---

## 結論

不對齊共 **5** 條,其中 major **1** 條:

1.(問一)`run_selfaudit` 的 `claude -p` 派工沒有指定 `--allowedTools`/`--permission-mode`;同檔案裡唯一現成範本(orchestrator 段,`governance/autonomous-loop.sh:202-203`)帶 Edit+Bash,若被直接沿用會讓 spec 自己宣稱的「★不動筆記★」(`/tmp/selfaudit-loop-r1.md:44`)失去機制保障,且本庫另有貼合「唯讀審計」用途的先例(`governance/ai-governance-research.sh:135`:`Read,WebSearch,WebFetch`)沒被引用,也沒有明文排除 orchestrator 那條;同檔案 2026-07-29 已對「子 agent 權限範圍」留過因 confused-deputy 風險而下的裁定(`governance/autonomous-loop.sh:8-10`),spec 未對照。**major**。
2.(問一)「直接 import lumos 模組呼叫同一套判定,單一實作」(`/tmp/selfaudit-loop-r1.md:36`)與 Check S 現況不符——`sa_missing`/`sa_stale` 邏輯目前整段寫在 `run_doctor` 函式體內(`scripts/lumos:823-851`),不是可 import 的頂層函式;本庫既有的「多呼叫點共用判定」慣例是抽成頂層函式(`about_code_expired`,`scripts/lumos:7736`,被 `:888` 與 `:14128` 兩處呼叫),spec 沒有把這一步列進工作項。
3.(問二)knob `SELFAUDIT_WEEKLY_N`(`/tmp/selfaudit-loop-r1.md:37`)不掛 `LUMOS_` 前綴,跟全庫十餘個既有環境變數旋鈕(`LUMOS_IMPACT_ABOUT`/`LUMOS_RANK_MOC_MULT`/`LUMOS_KILL_TIMEOUT_FLOOR` 等,`scripts/lumos` 全庫零反例)命名格式不一致;`autonomous-loop.sh` 自己對配額類設定的既有慣例則是寫死常數(`SKIP_CAP=3`,`:139`)而非環境變數,兩邊都對不上。
4.(問二)`--model <agent-model>-auto`(`/tmp/selfaudit-loop-r1.md:42`)在 `self_audit` 值域裡新增後綴標記,本庫既有「這是自動流程產出」的標記全部是前綴掛在新識別碼上(`auto-$TODAY`/`auto/spec-...`/`auto-spec:`,`governance/autonomous-loop.sh:19/245/377/380-381`),`scripts/lumos` 全文查無 `-auto`/`_auto` 後綴用法,`self_audit` 既有約 28 筆值也無此例。
5.(問二)`governance/pending/<日期>-selfaudit-<篇>.md`(`/tmp/selfaudit-loop-r1.md:44`)在「selfaudit」中綴的安排上,跟同一份 spec 裡零中綴的姊妹路徑(`governance/review-reports/self-audit/<日期>-<篇>.md`,`:40`,與既有真實檔 `governance/review-reports/self-audit/2026-08-24-lumos-cli-read.md` 完全對得上)不一致,也跟 `pending/archive/` 既有兩筆真實案例的「日期-主題(-限定詞尾綴)」格式有出入。

另有 **3** 條 ⚠ 交編排者判準,不計入上方 5 條:
- 「抽不到 VERDICT 行…NO_JSON 教訓同款」(`/tmp/selfaudit-loop-r1.md:46`)裡借用的究竟是「死因塞進 log 行尾」的記錄手法,還是連同 `governance/autonomous-loop.sh:254` 的整支腳本 `exit 1` 一起借用——後者會違背 `run_nags`/`run_probe`/`run_exam` 共通的「內部失敗絕不逃逸、不拖垮當天其餘排程」紀律,文字兩種讀法都通,判不準。
- 每篇 `claude -p` 的實際成本要不要接進 `orchestrator_result.extract_cost`/`lumos canary record`(`governance/autonomous-loop.sh:222-252`)——本庫對這件事本身沒有單一慣例:orchestrator 段接了,更早的 `scenario_probe.py` 派工迴圈完全沒接,兩種先例並存,判不準該對齊哪一個。
- 結論 4 的「-auto」後綴要不要算「第二種做法」(major)——它標記的是「誰執行了這次審查」(審計來源),既有 `auto-` 前綴標的是「這個識別碼由自動流程產出」(產物來源),兩者語意目標相近但不完全同一件事,能不能套用同一條先例來定 major/non-major,判不準。
