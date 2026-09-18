severity: major

## 逐節審查

### 起因 / 實測證據 / 根因(第 26–70 行)
已讀,無 finding。九情境實測與四道閘門的重述跟 `scripts/hooks/claude/check-graph-sync.py` 對得上(閘門 2 空清單直接 `return 0`,見 `file:\`scripts/hooks/claude/check-graph-sync.py:808-812\``)。

### 方案:快照機制值得嗎(問題 1、2)

severity: major
blocking: 是 — 判準:同一支 hook 檔裡已經有一條「工作樹 vs 上次提交、零快照」的路在跑同類任務且從未被判壞,計劃完全沒評估直接沿用它,就跳去蓋一套新狀態機。
引句:「拿工作樹跟上次提交比,會把**所有**未提交的改動都算進來」
`_impact_missing`(gate 3 用)就是呼叫 `lumos impact --diff HEAD --sync-check --json`,`--diff HEAD` 沒有終點即工作目錄(`file:\`scripts/lumos:15282-15285\``,注解寫「終點 None=工作目錄」),等於「全量、零快照」,而且這條路徑的 JSON 輸出本來就帶一個 `files` 欄位(即這次 diff 動到的檔案清單,`file:\`scripts/lumos:25333\``)。gate 2 要的「這輪改了哪些程式碼檔」可以直接讀這個既有欄位,不必列舉工具名也不必蓋快照,而這條路徑今天就在跑、沒人挑出它「把別人的未提交檔算進去」是問題。

severity: major
blocking: 是 — 判準:計劃拿「多報」的代價去跟「維護快照」比,但沒把「多報訊息其實只會被模型看到一次」這個既有護欄算進成本對比,代價被算錯了會導致方案選型錯。
引句:「少報最毒的地方就是看起來像正常運作,退回全量時不能重蹈覆轍」
`stop_block_decision` 用 `O_EXCL` 建立 session 標記檔,同一 session 只擋一次;擋過一次之後,同 session 後續所有 Stop 呼叫都只印到 stderr,而 hook 檔自己的 docstring 明講「那條只進除錯日誌」模型看不到(`file:\`scripts/hooks/claude/check-graph-sync.py:719-729\``,`file:\`scripts/hooks/claude/check-graph-sync.py:865-874\``)。也就是說,「全量比對可能把別人的未追蹤檔算進去」這個代價,在模型看得到的那一次訊息裡最多發生一次,而且可以直接在那一次訊息裡老實加一句「可能含非本輪改動」來對沖,不需要靠快照把它變精確。

### PRIOR-ART(第 87–91 行)

severity: minor
blocking: 否 — 判準:這是敘述精確度問題,不影響驗收條件是否可測,只影響「這個類比有多站得住」。
引句:「同一個 repo 裡已經有兩處在用正確作法,只有收工這一處在用列舉法」
`pre-commit` 量的是**staged 索引**(`STAGED="$(git -c core.quotePath=off diff --cached --name-only)"`,`file:\`scripts/hooks/pre-commit:43\``),`pre-push` 量的是**特定 commit range**(`_hrange`,`file:\`scripts/hooks/pre-push:187-190\``),兩者都不是計劃要採用的「工作樹 vs 上次提交」;真正同款的既有作法是本檔自己的 `_impact_missing`(見上一節),PRIOR-ART 卻沒點名它——把論據安在不夠貼切的兩道閘上,反而漏了最貼切的第三個。

severity: minor
blocking: 否 — 判準:數字對不上實測環境,但方向(把版本控制量測建在真實規模上、不是憑空假設超大 repo)是對的,不影響是否要蓋快照這個核心決策。
引句:「本 repo 4074 個追蹤檔實測跑一次 30 毫秒」
本機在這個 worktree 實測 `git status --porcelain` 約 170ms(`time git status --porcelain > /dev/null` → `0.173 total`),跟計劃寫的 30ms 有數倍落差,可能是機器或 worktree 開銷不同;不影響論證方向,但既然計劃逐字寫死一個數字當佐證,數字本身該可重現。

### 問題 3:有沒有在解一個還沒發生的問題
已讀,無 finding。計劃沒有主張超大 repo、時鐘漂移或權限問題,量測基準就是這個 4074 檔的真專案而非假想規模,`file:\`scripts/lumos:15345\``(`porcelain=v1 -z` 一次算全量)顯示既有作法本就扛得住這個規模;這一題在本份計劃裡找不到「解未發生問題」的條款。

### 問題 4:哪一條是為了機制本身(條款 S4–S6)

severity: major
blocking: 是 — 判準:S4 保護的「不重複算上一輪」只在模型看得到訊息的那一次才有意義,而那一次只發生一次,S4 要對付的「跨輪重複」場景結構上到不了模型面前。
引句:「基準要每一輪重取,不是整個 session 取一次」
如上一節所述,同 session 只會有一次模型可見的「N 個程式碼檔」訊息(`stop_block_decision` 的 O_EXCL 一次性標記),之後每輪的計算結果只寫 stderr,而 `_hookevent.py` 明講「不記『注入 N 次』…本批只做『活著沒』」(`file:\`scripts/hooks/claude/_hookevent.py:26-27\``)——沒有任何地方會讀取或記錄「第二輪起是否重複算了第一輪的檔」。S4 解決的是一個沒有觀眾的頻道。

severity: major
blocking: 是 — 判準:S6 要求的「內容雜湊、不只比 mtime+size」只有在自建快照/差集機制時才需要防,若改用 git 原生 diff(如上面 `_impact_missing` 那條路),racy-git 保護本來就內建在 git 的 stat 快取機制裡,S6 描述的坑不會發生。
引句:「判定比內容雜湊,不只比時間與大小」
計劃把 S6 的同族前例接到 Python bytecode cache 的教訓(`[[Systems/記憶過期清掃]]` 那條),但那是 CPython `.pyc` 快取的行為,不是 git 的行為;git 的 index 本來就有「index mtime 落在同一秒就強制回去比內容」的保護(racy git),用 `git diff`/`git status` 取代自建快照後,S6 描述的失敗模式不會出現,S6 因而變成純粹是為了「自己重新實作一套快照差集」這個機制本身而寫的條款,不是原始「少報」問題的一部分。

severity: minor
blocking: 否 — 判準:S5(基準檔不能放工作樹裡)只有在真的存在一份需要落地的基準檔時才成立,但一旦真的要存狀態,這條本身便宜且必要,不構成額外負擔,只是印證「這條款的存在前提是快照機制本身」。
引句:「主體應把它寫在被檢查的 repo 工作樹之外」
若採用上面建議的「直接讀 `lumos impact --diff HEAD --json` 的 `files` 欄位、不落地任何基準檔」的做法,S5 整條連同它要防的坑(基準檔變成未追蹤檔汙染別的會談)一起消失,不需要另外裁決要不要留。

### 問題 5:RETIRE-IF 寫得夠具體會被執行嗎

severity: major
blocking: 是 — 判準:兩條退場條件都要「跟舊作法比較」或「算誤報比例」,但全 repo 唯一會記錄這支 hook 有沒有跑過的地方明講不記內容只記活著沒,沒有任何機制能在四週後回答這兩個問題,寫了等於沒寫。
引句:「連續四週,收工點名一次都沒有比舊作法多抓到檔」
`_hookevent.py` 的設計原則是「★不記『注入 N 次』★…本批只做『活著沒』(跑過/逾時/失敗),不做『有沒有用』」(`file:\`scripts/hooks/claude/_hookevent.py:26-27\``);要回答「連續四週有沒有多抓到檔」或「誤報是否多過真報」,需要一份「新舊兩法各自算出什麼、誰對誰錯」的逐次記錄,而這正是 `_hookevent.py` 明文拒絕記的東西。計劃沒有在別處新增這份記錄,四週後不會有人、也沒有東西能去檢查這兩個條件是否成立——這符合 CLAUDE.md 鐵則四「純散文的回頭條件沒人會回頭」講的那種情況。

### lands_in / 驗收條件 / 已知的坑(其餘四條)/ 實務隱患 / 回退
已讀,無 finding。驗收條件 1–4 都可對應成具體的重跑指令與可觀察輸出,不是散文宣稱;已知的坑第 1、2、4、5 條在採用「直接讀 `lumos impact --diff HEAD` 的 `files` 欄位」的簡化方案後大多自動失效(不再需要基準,也就不再需要顧慮基準何時取、放哪裡),但這是問題 1/2/4 的推論結果,這裡不重複記分。回退段落誠實交代「退回後問題依舊存在但不會更糟」,無 finding。

## 總結

最嚴重等級:major。blocking 共 5 條(方案節 2 條、S4 1 條、S6 1 條、RETIRE-IF 1 條);minor 非阻塞 4 條(PRIOR-ART 類比精確度、30ms 數字、S5)。核心意見:計劃要解的「少報」问题本身成立,但選定的解法(逐輪快照+內容雜湊+跨輪基準管理)比同一支 hook 檔裡已經在跑、沒人挑出毛病的既有作法(`_impact_missing` 呼叫 `lumos impact --diff HEAD` 拿到的全量工作樹 diff)重,S1–S3 直接對應原始問題,S4–S6 主要是為了維護這套新機制本身而存在;建議先評估「gate 2 直接沿用 gate 3 那條路徑算改動清單、不留狀態檔,只在訊息裡老實加一句可能含非本輪改動的但書」是否已經夠用,再決定要不要蓋快照。
