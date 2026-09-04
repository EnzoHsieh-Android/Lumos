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
  KEY:主 session 動手前被 impact-hook 推到眼前的固定席節點,★有沒有被碰★今天零數字。本案第一段★只量不加義務、不設門檻、零新元件★:一支唯讀腳本讀逐字稿,只出分佈+分層抽樣兩評判;歷史推送現在就能跑(本專案主 session 44 筆=16 舊標頭+28 新;子代理全機重數 0,r2 的 42/70 撤回)
  KEY:r1(62 條/11 blocker,4 席 opus+Codex)拆掉第一版:時間窗與注入時機互斥、比率量到圖譜密度、跳過是合規、門檻無刻度、extract_bash_file_paths 不認 cat/sed、使用帳無 session/時區。r2(57 條/8 blocker)再拆第二版的儀器:量測效度席乾跑歷史逐字稿發現★推送本來就在逐字稿裡★(hook_additional_context 附件帶 toolUseID+全文)→帳/hook/子命令/gov 源/SubagentStop 全砍(d3)
  KEY:定義 v3=推送=逐字稿附件(去重 toolUseID;pinned 從注入全文解析;pinned 空不進分母;scratch/repo 外目標檔不進分母);碰觸=同逐字稿、那次 Edit 之後的 Read/Bash 含圖譜路徑/lumos context|show|contracts|search 逐詞對節點名(路徑正規化);寫回(git add/heredoc)不算讀;any 只能分 |pinned| 型讀(基準率差 5 倍)
  KEY:前置修正(鄰居 impact-hook 兩個既有缺陷,否則樣本偏)=hook_decide 認 python/bash shebang 無副檔名檔(scripts/lumos 27 篇、pre-push 7 篇現況永不入樣)、TTL 標記改注入後才寫(零注入也開冷卻窗);各配測試,test_lumos.py 錨點要 approve
  KEY:REVISIT:2026-09-17 先跑歷史:主 session 非空固定席非 scratch 的推送 <20→改題「Bash 改檔路徑沒有動手前鏡頭」(本 session 372 Bash/0 Edit);夠→Enzo 讀分佈+抽樣裁第二段(必答落 commit-msg hook,先提醒只數遵守率)
  KEY:姐妹題=[[Projects/派工鏡頭注入_計劃]](子代理側,裁不量成效);本案量的是行為不是成效
  KEY:r3(27 條/blocking 18/11 blocker,上限到)定:推送=附件且 hookName∈Edit|Write|MultiEdit(否則吃進 SessionStart/Agent 注入)、標頭新舊雙版都認、掃全部 projects 目錄以 cwd 篩含 worktree、heredoc 三分法(腳本內讀該路徑=讀)、抽樣不足 10 全抽/每 session≤5、前置修正①簽名重排+安全讀首行 ②拆 TTL 判定/寫並改 t_impact_hook_ttl
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
  - content: r2 儀器歸零:推送本來就在逐字稿裡(hook_additional_context 附件,帶 toolUseID 與全文,歷史 70 次)——不加帳、不加 hook、不加子命令,量測=一支唯讀腳本讀逐字稿;歷史資料現在就能跑
    id: d3
    context: r2 量測效度席拿歷史逐字稿乾跑 r1 版演算法,發現注入附件已含全部所需;r2 其他四席對新帳/hook/gov/timeout/命名的 20 餘條發現隨元件移除而消失
    why_chosen: 量模型真的看到的文字比量 hook 算的名單更對;零新元件=零併發、零 Hawthorne 出口、零登記同步;剩下的只有鄰居 hook 兩個既有缺陷要先修(樣本偏)
    decided: 2026-09-03
    valid: true
verified_by:
  - "[[Verification/2026-09-04_主session鏡頭利用率第一份報表]]"
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

- **推送事件** P:逐字稿裡 `attachment.type == hook_additional_context` ★且 `hookName ∈ {PreToolUse:Edit, PreToolUse:Write, PreToolUse:MultiEdit}`★ 的附件(r3 三席:不篩 hookName 會吃進 SessionStart 注入——它的 toolUseID 字面就是 "SessionStart",本機 36 筆——與姐妹案 dispatch-lens 的 Agent 注入);`content` 可能是 list,逐元素轉字串接起來。pinned 清單從注入全文解析,★要同時認兩種標頭★:2026-08-22 前 `必看(合約/事故固定席 N):`、之後 `必看——這 N 篇帶著不能破壞的合約或出過事故:`(本機 44 筆=16 舊+28 新;只認一種漏三成),節點名取標頭下方帶 ★TAG★ 的行;標頭寫「還有 N 篇」省略的,pinned 記為「不全」另計。pinned 空的不進分母。
- **碰觸事件**(★全部從逐字稿取★,有序、UTC;不用使用帳——它沒 session_id、時間無時區;`contracts`/`search` 本來就不寫使用帳,但它們是 Bash 指令、逐字稿裡有,所以第③種證據不需要任何帳):①Read 工具的 file_path 在圖譜根下 ②Bash 指令任一 token 是圖譜根下的路徑(cat/sed/grep/head 都算)③Bash 指令是 `lumos context|show|contracts|search <詞>` 且 <詞> 對上 pinned 節點名或其檔名主幹。
- **命中**:同一逐字稿、碰觸發生在 toolUseID 對應的那次 Edit/Write/MultiEdit tool_use 之後(行序,不用時鐘;對不到 tool_use 的附件另計「無錨點」不進分母——resume 切檔會有)、正規化後的路徑/節點 ∈ pinned。每次推送記 {touched, any, pre_touched};同一篇推送前後都碰→算 touched 也列 pre_touched(兩欄獨立,不互斥)。★不算比率、不設門檻★;二值 any 在不同 |pinned| 下基準率差 5 倍(乾跑:4 篇型 1.2% vs 20 篇型 5.8%),所以只能分型讀,不能合併。
- 量的是「碰沒碰」,不是「懂沒懂」;推送前已碰過的另記,不算命中也不算沒碰。

## 現況(2026-09-03 開檔核過,r1 修正後)

- `impact-hook.py`:只留 TTL 冷卻標記(`<tmpdir>/lumos-impact-<session>/`),★沒記推了哪些節點★;TTL 20 分鐘內同檔改走 `--incidents-only`(只推事故);`hook_decide` 用副檔名過濾,★無副檔名的 `scripts/lumos` 永遠不推★(近 14 天改動第二多、固定席 27 篇)。
- `check-graph-sync.py`(Stop):`collect_turn_actions` 回兩個扁平 list(Edit 路徑、Bash 指令),無順序、不收 Read;它餵四道閘,其中三道提前 return;只註冊 Stop,子代理的 SubagentStop 沒有。
- 逐字稿:每行 `timestamp` 為 UTC 帶 Z;tool_use 有序;★hook 注入本身就是一行 `hook_additional_context` 附件(toolUseID+全文)★;子代理逐字稿獨立在 `<session>/subagents/agent-*.jsonl`,每行 `isSidechain: true`;自動壓縮會插一行字串型 user 訊息(用回合切點會被切碎,本案不用回合切點)。
- `docs/.usage-log.jsonl`:被 git 追蹤、`{ts(本地無時區),node,cmd}`、只 `context`/`show` 寫;`.gitattributes` 無 jsonl union driver(每回合都寫會讓分支合併衝突變常態)。★本案不動它★。
- `scripts/test_lumos.py` 是錨點檔:加測試要 `lumos anchor approve --note`。

## 第一段:量(零義務、零門檻、★零新元件★——r2 重寫)

r2 量測效度席把 r1 版的演算法拿歷史逐字稿乾跑,發現★推送本來就寫在逐字稿裡★:每次 impact-hook 注入,逐字稿多一行 `attachment.type == hook_additional_context`,帶 `hookName: PreToolUse:Edit`、`toolUseID`(對得上是哪一次 Edit)、注入全文(模型真的看到的那份「必看」清單)、UTC 時戳。r2 效度席全機乾跑得 70 次(主 28、子 42);★編排者只在本專案目錄重數:主 session 44 次(含 Write)、子代理目錄 0 次★——兩邊範圍與過濾不同,子代理那 42 次在本專案重現不了,列為腳本第一件要釐清的事(不把 70 當事實)。★所以 r1 版的推送記帳、獨立帳、gov 第八源、lens 子命令、tally hook、SubagentStop、gitignore、timeout、撞名——整批不需要★,r2 其他席對那些元件的 20 幾條發現隨元件一起消失(留痕見 r2-intake)。

### 儀器=一支唯讀腳本(將建,住 governance/eval/lens-utilization/,同席間覆蓋率那支 recount.py 慣例)

1. **輸入**:`~/.claude/projects/*/` ★全部專案目錄★的 `*.jsonl`(主)與 `*/subagents/agent-*.jsonl`(子代理),★用逐字稿行裡的 `cwd` 篩「在本 repo 或它的 `git worktree list` 路徑之下」★(r3 極端席:projects 目錄依 cwd 切,worktree session 在另一個頂層目錄);主子靠檔案位置與 `isSidechain` 分。★r3 效度席全機重數:子代理逐字稿 1404 份、任何 hookName 的注入附件都是 0★——r2 的「子代理 42/全機 70/60%」撤回,r2-intake 補更正;歷史樣本=本專案主 session 44 筆。
2. **推送事件**:定義見上(hookName 篩、雙標頭、list content);★去重鍵=toolUseID★;pinned 為空(只有自由席或守衛面參考)→★不進分母★,另計「空固定席注入」數。
3. **碰觸事件**(同一份逐字稿;★錨點=toolUseID 對到的那次 Edit/Write/MultiEdit tool_use 的行序★,碰觸必須在它之後——不是在附件那行之後,附件落地比 Edit 晚中位 2.4 秒):①Read 的 file_path ②Bash 指令★動詞是讀★(cat/sed -n/head/tail/less/grep/rg)且任一 token 是圖譜路徑 ③Bash 的 `lumos context|show|contracts <詞>`:<詞> 對節點名主幹★精確相等★,或★把連續 token 串起來★再比(口語會打成「主 session 鏡頭利用率」,stem 無空白;r3 極端席);stem 撞名(doctor 有「同檔名」檢查)→記「歧義」不算命中;`lumos search <詞>` 另計一欄「search 碰」——逐詞對 stem 子字串,弱證據,不併進 any。★heredoc 三分法★(r3 效度席:1293 次含筆記路徑的 `python3 - <<`,44% 先 read_text 再 write_text):腳本內對該路徑有 `read_text`/`open(...)` 讀→算★讀★;`cat > 筆記 <<`/`> 筆記`/只 `write_text`→寫回(wrote_back);`cat <<EOF` 只是拼字串裡提到路徑(如 commit message)→兩者都不算。★路徑正規化★:絕對→圖譜相對、去掉 `docs/<slug>-knowledge/` 前綴、比對 `.md` 檔名。背景 Bash(`run_in_background`)的內容何時真的可見量不到,列界線(本專案 287 次背景 Bash,含圖譜路徑讀動詞的至少 1 次)。
4. **每筆推送記**:{session_id, is_subagent(檔案在 `subagents/` 且 isSidechain:true), hook_name, header_version(old/new), file, |pinned|, pinned_complete, touched, any, pre_touched(資訊欄,不進裁定), wrote_back, search_touched, ambiguous, 檔型(test/code)};★scratchpad 與 repo 外的目標檔不進分母也不進抽樣池★(另計一個數;r3 效度席:分母外還列進分層是自相矛盾)。壞行/缺欄位跳過並計數(同 recount.py 慣例)。
5. **輸出**(★不出單一命中率、不設門檻★):印到 stdout(同 recount.py 慣例;`--out` 可另存檔):推送數(主/子、標頭版、pinned 空/非空/不全、檔型)、|pinned| 分佈、每型 any 的計數、pre_touched/wrote_back/ambiguous 另列、session 叢聚度。★歷史資料現在就能跑★(本專案主 session 44 筆:16 舊標頭+28 新),不必等兩週;之後每兩週重跑。
6. **人工抽樣**:★母體不足 10 筆(有 pinned 且非 scratch)就全抽★;夠則每 session 至多 5 筆、抽到 10(r3 效度席:歷史只有 2 個 session 有 pinned,「每 session 至多 3」在算術上抽不到 10)。兩個評判者(Enzo+一個乾淨 agent,判準=「這篇 pinned 節點的合約,對這次 diff 改的行為有沒有牽連」,agent 派工詞不帶本案結論)各判「跳過對不對」,不一致的列出來,不做一致性係數。
7. **★前置修正(鄰居 hook 的兩個缺陷,量測前修,否則樣本偏)★**(★code-loop r1 改:TTL 標記在判定當下先寫、最後沒注入才撤 `_ttl_unmark`——「拆判定/寫」會把並發窗口拉寬到整段 subprocess,兩席一致★):①`hook_decide` 認無副檔名檔:★main 改成先算 repo(CLAUDE_PROJECT_DIR→cwd)、把絕對路徑傳給 hook_decide★(簽名加參數,既有呼叫點與 `t_impact_hook_*` 測試同步);repo 算不出→只看副檔名;檔存在且首行 `#!` 含 python 或 bash 才算 code,★首行讀取包 try/except、只讀前 128 bytes、二進位/讀不到→不算★(r3 極端席:無副檔名二進位檔會讓現役 fail-open hook 炸);Write 新檔(不存在)→只看副檔名。②TTL:判定當下照舊先寫標記(窗口不變寬),★最後沒注入才撤★(`_ttl_unmark`,標記帶擁有權 token 只撤自己的;早退路徑也撤)——零注入的 Edit 不再開 20 分鐘冷卻窗;`_ttl_should_inject` 預設 `mark=True` 保留舊語意,既有 `t_impact_hook_ttl` 不動,新增接線測試覆蓋五個出口。★TTL 界線★:冷卻窗仍存在(同檔 20 分鐘內只推事故),分母偏向「第一次碰這支檔」。
REVISIT:2026-09-17 第一次重跑時把 incidents-only 期間的 Edit 次數另列,若佔多數則裁是否把冷卻窗縮短或關掉
8. **Hawthorne**:腳本輸出只落檔案(governance/eval/…/ 下的報表),不進 `lumos gov`、不印進任何 hook,模型跑 `lumos gov` 看不到。

### 裁定規則
REVISIT:2026-09-17 依下列規則裁:先跑歷史,樣本不足改題,足則讀分佈+抽樣
- 先跑歷史:主 session 非空固定席、非 scratch 的推送若 <20 → 樣本不存在,改題為「Bash 改檔路徑沒有動手前鏡頭」(本 session 372 次 Bash、0 次 Edit),另開計劃。
- 樣本夠 → 讀分佈+抽樣,由 Enzo 裁第二段;不預設任何數字門檻。

## 第二段:候選(不預作)

- **必答落在閘會讀的地方**:每個被推過的合約節點,commit 時要嘛動了那篇筆記,要嘛 commit message 帶一行確認(候選格式 `LENS-ACK: <節點>=不影響,<理由>`,新造標記名)。★攔截點是 commit-msg hook 不是 pre-commit★(pre-commit 拿不到訊息檔)。先只提醒、只數遵守率。
- **擋**:2026-08-02 裁定在前(擋 standard 逼人繞);沒有第一段+提醒期的數字不開。
- ★不做★:改推送措辭、加粗、重推——世界實證無效。

## 同步清單(r2 縮減後)

- 圖譜:[[Projects/主動影響幅度偵測_計劃]](兩個前置修正:shebang 入樣、TTL 標記改注入後寫;`t_impact_hook_ttl` 改)、本案 Verification(本專案主 session 44 筆的第一次報表——不是 70)。
- 文件:不加命令、不加 hook,命令數與登記點★全部不動★;該目錄的 README(將建)寫重跑步驟。
- 測試:`test_lumos.py`(錨點檔,approve)——`hook_decide` shebang 兩型、TTL 標記時機;腳本本身照席間覆蓋率那支慣例不進測試(唯讀、可重跑)。

## 誠實界線

- 量的是「碰沒碰」,不是「懂沒懂」;碰了才跳過 vs 沒看就跳過,分佈分不出來,只有人工抽樣能。
- 逐字稿只到本回合;更早讀過的算 pre_touched,不進命中也不進沒碰。
- ★只量 impact-hook 這一個鏡頭★:Stop hook 的「該動卻沒動」點名與 pre-commit 的同步提醒也是推到眼前的鏡頭,本案不量(s1-f17);要量另開。
- TTL 窗內只推事故子集(mode 記著,分開報);冷卻窗跨回合,第 2 回合起同檔多半 N=0。
- 只讀本機逐字稿;多機不合併(量測用,不是治理紀錄)。逐字稿會被 Claude Code 依 cleanupPeriodDays 清掉(預設 30 天),歷史窗有限。
- 子代理推送與主 session 分開報;本機全機重數子代理注入為 0(r2 的 42/60% 撤回);主子靠檔案位置分。
- 「碰觸」與「收工寫回」的界線靠指令形態判(git add/heredoc=寫回),會有誤判;抽樣時人看。
- 只量 impact-hook 這一個鏡頭(Stop 點名、pre-commit 提醒不量)。

## 實務隱患

- **self-governance**:改治理觀測層。緩解=零義務、不印給模型、唯讀不寫任何帳、前置修正 fail-open。
- **併發**:無(唯讀腳本,不寫任何被 hook 共用的東西)。
- **效能**:離線腳本掃全機逐字稿(786 份子代理+主),一次幾秒到一分鐘;不在任何 hook 路徑上。
- **回滾**:唯讀腳本刪掉即可;★impact-hook 本體保留(它是現役鏡頭,不屬本案)★,只 revert 前置修正那兩段+對應測試;錨點:test_lumos.py 動了要 approve。
- **安全**:報表只含節點名與檔名(repo 內部路徑),不含 diff 內容;不改任何注入文字;腳本唯讀。
- ★沒有機械守衛的部分★:推送發生率若本來就低,兩週後只會得到「樣本不存在」——這本身就是答案,REVISIT 那條會改題。

## 實作紀錄 第一段(2026-09-04 早,r3 過閘後動工)

- 唯讀腳本 `governance/eval/lens-utilization/recount.py`+README;第一份報表存同目錄,數字與解讀在 [[Verification/2026-09-04_主session鏡頭利用率第一份報表]]。
- 解析教訓:事故節點行沒有 ★TAG★(「⚠事故 Issues/x.md (trigger: …)」),正規式要允許可選 TAG——第一次乾跑因此漏 6 筆。
- 前置修正兩處落地(shebang 入樣/TTL 注入後才寫),TDD 一支新測試;既有 hook 測試全綠;`lumos install` 同步安裝副本。
- ★人工抽樣(第 6 步)未做★——留給 Enzo 與一個乾淨 agent。
REVISIT:2026-09-17 跑 recount 讀分佈、做 10 筆人工抽樣、裁第二段(或依裁定規則改題)

## 審計修正紀錄(lumos-design-loop)

- r3(2026-09-03 深夜,上限輪,3 席 sonnet+架構 sonnet+外家 Codex):27 條(3+6+11+5+2)/blocking 18(3+5+7+2+1)/11 blocker;2 條引句錨不到不採信(s2-f5 背景 Bash、s3-f9 前置修正①簽名——內容照折)。折入=推送按 hookName 篩(Edit/Write/MultiEdit)、雙標頭解析(16 舊+28 新)、掃全部 projects 目錄用 cwd 篩含 worktree、r2 子代理 42/70/60% 撤回(全機重數 0)、抽樣改「不足 10 全抽/每 session ≤5」、heredoc 三分法、stem 精確+串接+歧義、scratch 出抽樣池、前置修正①簽名重排+安全讀首行、②拆判定/寫並改既有測試、殘留「獨立帳」字句清掉、輸出 stdout 同 recount 慣例。★上限已到;r3 折入無第四輪,攤 Enzo★。
- r1(2026-09-03,通才/量測效度/接手的人 三席 opus+架構對齊 opus+外家 Codex;★sonnet 連續 500/529 過載,四席改 opus,記於 r1-dispatch.json★):62 條(21+13+14+8+6)/blocking 43(13+11+10+3+6)/11 blocker;全折——量測核心重寫(時間窗、去比率去門檻、證據全從逐字稿、獨立帳經子命令、對帳不印給模型、放閘之前、SubagentStop、無副檔名檔入樣、先量推送發生率)。★密度遠超「建議整份重寫」門檻;核心「只量不加義務」未被推翻,編排者在同編號折入,重寫與否留 Enzo★。
- 席報告與收貨:`governance/review-reports/主session鏡頭利用率/`。
