---
type: project
status: doing
created: 2026-09-03
updated: 2026-09-03
tags:
  - type/project
  - status/doing
  - scope/governance
summary: |-
  FLAG:DECISION
  KEY:主 session 動手前被 impact-hook 推到眼前的固定席節點,★有沒有被碰★今天零數字。本案第一段★只量不加義務★,r1 後重寫量測核心:★不設門檻★,只出分佈+人工抽樣判讀;先量「推送有沒有發生」(r1 實測:本 session 372 次 Bash、0 次 Edit,家規用 Bash 改檔→PreToolUse Edit hook 幾乎不 fire)
  KEY:r1(2026-09-03,3 席 opus+架構 opus+外家 Codex;sonnet 500/529 過載改 opus)62 條/blocking 43/11 blocker 全折。三個結構性錯:①時間窗「Edit 之前」與注入時機互斥(推送發生時 Edit 已提出)→改「推送之後到回合結束」②既有 extract_bash_file_paths 只認 rm/mv/cp,cat/sed 全漏→自寫收集器③分母隨檔案圖譜密度浮動、跳過是合規、30 筆信賴區間跨兩門檻→門檻全砍
  KEY:定義 v2=證據全從逐字稿取(有序、UTC):Read 筆記路徑/Bash 指令含筆記路徑/Bash 的 lumos context|show|contracts|search <節點>;只算推送 ts 之後;每次推送記二值「有沒有碰任一篇」+碰了哪些;推送前就碰過的另記 pre-touched
  KEY:儀器=hook 不寫帳,經 lumos lens push/tally 子命令寫獨立帳 docs/.lens-log.jsonl(gitignored,同 ci-log;UTC Z;含 session_id/mode full|incidents-only/is_subagent/pinned 清單);登 gov 第八源;對帳=薄殼 lens-tally-hook 掛 Stop+SubagentStop、放在任何閘之前、★結果不印給模型★(印回=干預)
  KEY:前置修正=impact-hook 的 hook_decide 不認無副檔名檔(scripts/lumos 永不入樣,合約最密);收集器獨立於 collect_turn_actions(併進去會靜音 Stop 的圖譜同步閘);test_lumos.py 是錨點檔要 approve;REVISIT:2026-09-17 先看主 session 推送次數<20→改題為「Bash 改檔路徑沒有動手前鏡頭」
  KEY:姐妹題=[[Projects/派工鏡頭注入_計劃]](子代理側,裁不量成效);本案量的是行為不是成效
related:
  - "[[Projects/派工鏡頭注入_計劃]]"
  - "[[Projects/主動影響幅度偵測_計劃]]"
  - "[[Projects/指令索引與情境測試_計劃]]"
  - "[[Projects/收斂閘漏項敏感度v2_計劃]]"
  - "[[Systems/retrieval-ranking]]"
decisions:
  - content: 開案:第一段只量不加義務——impact-hook 記推送、Stop hook 對帳印一行、usage-log 多兩種事件;兩週後拿命中率裁第二段(必答/不做)
    id: d1
    context: Enzo 提「推到眼前不等於利用到」;同日派工鏡頭注入案裁子代理側不量成效;主 session 側今天零數字
    why_chosen: 成效量不出來、行為量得出來(碰沒碰);先量現況再建,避免同日五份計劃死在「想證明有用」的形態;三處都是既有機制各加一小段
    decided: 2026-09-03
    valid: true
  - content: r1 後重寫量測核心:去比率去門檻(只出分佈+人工抽樣)、時間窗改「推送之後」、證據全從逐字稿、hook 經 lumos lens push/tally 寫獨立 gitignored 帳、對帳不印給模型、先量推送發生率
    id: d2
    context: r1 五席 62 條/11 blocker:時間窗與注入時機互斥、分母隨圖譜密度浮動、跳過是合規、30 筆信賴區間跨兩門檻、extract_bash_file_paths 不認 cat/sed、使用帳無 session/無時區/會 merge 衝突、Stop hook 早退閘吃掉對帳、印回=干預、本 session 0 次 Edit
    why_chosen: 第一版把量測儀器的假設全寫成事實(同日第三次:肯定斷言沒開檔看);重寫後每個宣稱都對應一個開檔核過的現況;門檻砍掉是因為沒有刻度的尺不能切
    decided: 2026-09-03
    valid: true
---
> 白話:主 session 動手改 code 前,hook 會把「這個檔牽連到哪些帶合約的筆記」推到眼前——推了之後有沒有被看、被用,今天沒有任何數字,只有反例(2026-09-03 編排者自己把推到眼前的硬約束撤掉兩次)。本案★第一段只量現況、不加任何義務、不設門檻★:先確認推送到底有沒有發生,再記「推了之後有沒有碰」,兩週後人讀分佈、抽樣判讀,才裁第二段。★r1 五席把第一版量測設計整個拆掉了(62 條、11 blocker),本節以下是重寫版★;跟同日的 [[Projects/派工鏡頭注入_計劃]] 是姐妹題——那邊是子代理、這邊是主 session;那邊裁「不量成效」,這邊量的是「碰沒碰」的行為,不牴觸。

PRIOR-ART: ① 最小解層級——推送方 `impact-hook.py`(PreToolUse Edit|Write)、逐字稿(Claude Code 每行帶 UTC 時戳、tool_use 有序)、Stop hook 讀逐字稿的既有形態(`check-graph-sync.py`)、薄殼 hook+lumos 子命令的形態(同日 `dispatch-lens-hook.py`)、獨立 gitignored 帳(`docs/.ci-log.jsonl`)、gov 七源的 `kind` 慣例、`governance/eval/<主題>/recount.py` 的唯讀重算慣例——全是既有。② 世界解過沒——「推到眼前的東西被忽略」是 2026 年 LLM judge 研究主結論(清單在眼前仍漏六成,[[Projects/收斂閘漏項敏感度v2_計劃]] 轉引);對主 session 的處方世界只有「必答式提問」一種量到效果,是本案第二段候選。「量測儀器本身是干預」(Hawthorne)→對帳結果不印給被量者。③ 裁定=borrow-design,零依賴。

## 一句話

★先量「推送發生了幾次、之後有沒有碰」,兩週後人讀分佈、抽樣判讀,再裁要不要「必答」。★

## r1 推翻的三件事(留給下一個想量這題的人)

1. **「那次 Edit 之前碰過」量不到**:impact-hook 是那次 Edit 的 PreToolUse,推送發生時 Edit 已經被提出;被推的東西只可能影響★之後★的動作。時間窗改成「推送 ts 之後、到回合結束」。
2. **命中率=碰過/推了 這個比值量到的是圖譜密度不是行為**:同樣查 2 篇,改 A 檔推 4 篇=50%、改測試檔推 20 篇=10%;注入文字自己寫「不相關的跳過」,跳過是合規;固定席精確度本專案沒量過;30 筆時的二項信賴區間 [0.19,0.54] 同時跨過 20% 與 50%。★門檻全砍★,改每次推送記二值+明細,人讀分佈。
3. **推送本身可能很少發生**:本 session 逐字稿 372 次 Bash、0 次 Edit、1 次 Write(家規:bypass 模式用 cat/sed/heredoc 改檔);最近 12 份逐字稿只有 2 份(走 Edit 工具的)有 Edit。★第一週先只看推送次數★。

## 「利用到」的定義 v2

- **推送事件** P:impact-hook 真的注入那一刻,{ts(UTC Z), session_id, file, mode: full|incidents-only, pinned 節點清單, is_subagent}。
- **碰觸事件**(★全部從逐字稿取★,有序、UTC;不用使用帳——它沒 session_id、時間無時區;`contracts`/`search` 本來就不寫使用帳,但它們是 Bash 指令、逐字稿裡有,所以第③種證據不需要任何帳):①Read 工具的 file_path 在圖譜根下 ②Bash 指令任一 token 是圖譜根下的路徑(cat/sed/grep/head 都算)③Bash 指令是 `lumos context|show|contracts|search <詞>` 且 <詞> 對上 pinned 節點名或其檔名主幹。
- **命中**:同一逐字稿、碰觸 ts > 推送 ts、路徑/節點 ∈ pinned。每次推送記 {touched:[…], any: bool, pre_touched:[推送前已碰的]}。★不算比率、不設門檻★。
- 量的是「碰沒碰」,不是「懂沒懂」;推送前已碰過的另記,不算命中也不算沒碰。

## 現況(2026-09-03 開檔核過,r1 修正後)

- `impact-hook.py`:只留 TTL 冷卻標記(`<tmpdir>/lumos-impact-<session>/`),★沒記推了哪些節點★;TTL 20 分鐘內同檔改走 `--incidents-only`(只推事故);`hook_decide` 用副檔名過濾,★無副檔名的 `scripts/lumos` 永遠不推★(近 14 天改動第二多、固定席 27 篇)。
- `check-graph-sync.py`(Stop):`collect_turn_actions` 回兩個扁平 list(Edit 路徑、Bash 指令),無順序、不收 Read;它餵四道閘,其中三道提前 return;只註冊 Stop,子代理的 SubagentStop 沒有。
- 逐字稿:每行 `timestamp` 為 UTC 帶 Z;tool_use 有序。
- `docs/.usage-log.jsonl`:被 git 追蹤、`{ts(本地無時區),node,cmd}`、只 `context`/`show` 寫;`.gitattributes` 無 jsonl union driver(每回合都寫會讓分支合併衝突變常態)。★本案不動它★。
- `scripts/test_lumos.py` 是錨點檔:加測試要 `lumos anchor approve --note`。

## 第一段:量(零義務、零門檻)

### 儀器(hook 薄殼,邏輯進 lumos——同 [[Projects/派工鏡頭注入_計劃]] 的分層)

1. **推送記帳**:`impact-hook.py` 在 `inject_ranked_context` 真的輸出時,subprocess 呼叫 `lumos lens push --session <id> --file <f> --mode full|incidents-only --pinned <名單> [--subagent]`(best-effort,失敗靜默,不影響注入)。★hook 不自己開帳檔★(arch:hook 一律經 lumos 子命令;唯一直接寫帳的先例已撤)。
2. **獨立帳**(將建,檔名候選 docs/.lens-log.jsonl):★gitignored★(同 `.ci-log.jsonl`;進 init 的 .gitignore 清單與 `_BOOKKEEPING_FILES`);★位置由 lumos 決定★(同其他帳:vault 的上一層,standalone vault 也走同一個定位函式;hook 只傳 `--repo`,不自己算路徑——mirror 補:s1-f20/s3-f14/arch-f6)。事件形狀★一列一次推送★:`{ts: UTC Z, kind: lens-push|lens-tally, session_id, file, mode, pinned: [節點…], touched: [節點…], pre_touched: [節點…], any: bool, is_subagent: bool}`——不沿用使用帳「一列一節點、cmd=子命令名」的形狀,因為這是另一本帳、另一種語意(arch-f3/f4);登進 `lumos gov` 第八源(`kind` 慣例)。不進使用帳(它是檢索語料)。
3. **對帳 hook**(將建,檔名 lens-tally-hook.py):薄殼,註冊 ★Stop 與 SubagentStop★,payload 拿 `session_id`+`transcript_path`,subprocess `lumos lens tally --session <id> --transcript <path>`;★放在任何判斷之前★(不與 check-graph-sync 合體,免得被它的早退閘吃掉、也免得污染它的兩個 list);★stdout 什麼都不印★——印回給模型就是干預。
4. **`lumos lens tally`**:讀該 session 的 lens-push 事件(本回合=最後一則 user 訊息之後),用★獨立收集器★ `collect_turn_touches(transcript)`→有序 [(ts, kind, path|cmd)](共用逐字稿逐行迭代的 helper,不改 `collect_turn_actions` 的回傳形態),對每筆推送算 {touched, any, pre_touched},寫 lens-tally 事件(含每筆明細,分佈要用)。
5. **前置修正**:`hook_decide` 對無副檔名檔,首行是 python shebang 也算 code(否則合約最密的檔永不入樣);加測試。
6. **兩週後**(=REVISIT:2026-09-17 那天要跑的東西,arch-f8):一支唯讀重算腳本(將建,住 governance/eval/lens-utilization/,同席間覆蓋率那支 recount.py 慣例)出:推送次數(分 主/子代理、full/incidents-only)、有推送的 session 數、每次推送 any 的分佈、分檔型分佈、pre_touched 比例;★不出單一命中率★。
7. **人工抽樣**:隨機抽 10 筆推送,人讀逐字稿判「跳過對不對」——跳過合規與否只有人判得出。

### 裁定規則(REVISIT:2026-09-17)
- 主 session(非子代理)推送 <20 次或 session 數 <5 → ★樣本不存在,改題★:「Bash 改檔路徑沒有動手前鏡頭」,另開計劃(候選:PreToolUse Bash 對 heredoc/sed 目標檔算 impact)。
- 樣本夠 → 讀分佈+抽樣,由 Enzo 裁第二段;本案不預設任何數字門檻。

## 第二段:候選(不預作)

- **必答落在閘會讀的地方**:每個被推過的合約節點,commit 時要嘛動了那篇筆記,要嘛 commit message 帶一行確認(候選格式 `LENS-ACK: <節點>=不影響,<理由>`,新造標記名)。★攔截點是 commit-msg hook 不是 pre-commit★(pre-commit 拿不到訊息檔)。先只提醒、只數遵守率。
- **擋**:2026-08-02 裁定在前(擋 standard 逼人繞);沒有第一段+提醒期的數字不開。
- ★不做★:改推送措辭、加粗、重推——世界實證無效。

## 同步清單(mirror 補:s1-f8/s3-f11/s3-f12——整份重寫時漏的)

- 圖譜:[[Projects/主動影響幅度偵測_計劃]](hook 從「只注入」變「注入+經子命令記帳」,它 §5 hook 段要補一句)、[[Systems/lumos-cli-lifecycle]](多一支 hook 的生命週期)、[[Systems/retrieval-ranking]](明寫使用帳不動)、本案 Verification。
- 文件:ARCHITECTURE.md 與 `skills/lumos-project-notes` 裡描述 impact hook「只提醒不寫」的句子要改;命令數 66→67(`lens`);`commands/INDEX.md` 子檔加一行;`HELP_WHEN` 加 `lens`。
- 登記:`_GLOBAL_CLAUDE_HOOKS`、`HOOK_ENTRIES`(Stop+SubagentStop)、enforcement 六元組、`.gitignore` 清單、`_BOOKKEEPING_FILES`。★不進 ANCHOR_FILES★:tally hook 不改寫任何輸入,依同日裁定只有會改寫子代理輸入的 hook 才錨。
- 測試:`test_lumos.py`(錨點檔,approve)——收集器、tally 對帳、hook 薄殼、閘前順序、`hook_decide` shebang、gov 第八源。

## 誠實界線

- 量的是「碰沒碰」,不是「懂沒懂」;碰了才跳過 vs 沒看就跳過,分佈分不出來,只有人工抽樣能。
- 逐字稿只到本回合;更早讀過的算 pre_touched,不進命中也不進沒碰。
- ★只量 impact-hook 這一個鏡頭★:Stop hook 的「該動卻沒動」點名與 pre-commit 的同步提醒也是推到眼前的鏡頭,本案不量(s1-f17);要量另開。
- TTL 窗內只推事故子集(mode 記著,分開報);冷卻窗跨回合,第 2 回合起同檔多半 N=0。
- 帳是單機 gitignored;多機不合併(量測用,不是治理紀錄)。
- 逐字稿整檔讀進記憶體(實測 55MB 0.26 秒),不是「O(回合)」。
- 子代理推送與主 session 分開報;子代理逐字稿無 isSidechain 標記,靠 SubagentStop 事件分辨。

## 實務隱患

- **self-governance**:改治理觀測層。緩解=零義務、不印給模型、獨立帳、fail-open。
- **併發**:多 session 同時 append 同一份 jsonl——單行 append 行級原子(同 ci-log 慣例);git 層無衝突(gitignored)。
- **效能**:hook 多一次 subprocess(lumos 啟動約 0.1 秒);tally 整檔讀逐字稿 <1 秒;Stop/SubagentStop 各一次。
- **回滾**:移除兩支 hook 登記+兩個子命令+帳檔;錨點:test_lumos.py 動了要 approve(進場、回滾各一次)。
- **安全**:帳裡記節點名與檔名(repo 內部路徑),不記 diff 內容;不改任何注入文字。
- ★沒有機械守衛的部分★:推送發生率若本來就低,兩週後只會得到「樣本不存在」——這本身就是答案,REVISIT 那條會改題。

## 審計修正紀錄(lumos-design-loop)

- r1(2026-09-03,通才/量測效度/接手的人 三席 opus+架構對齊 opus+外家 Codex;★sonnet 連續 500/529 過載,四席改 opus,記於 r1-dispatch.json★):62 條(21+13+14+8+6)/blocking 43(13+11+10+3+6)/11 blocker;全折——量測核心重寫(時間窗、去比率去門檻、證據全從逐字稿、獨立帳經子命令、對帳不印給模型、放閘之前、SubagentStop、無副檔名檔入樣、先量推送發生率)。★密度遠超「建議整份重寫」門檻;核心「只量不加義務」未被推翻,編排者在同編號折入,重寫與否留 Enzo★。
- 席報告與收貨:`governance/review-reports/主session鏡頭利用率/`。
