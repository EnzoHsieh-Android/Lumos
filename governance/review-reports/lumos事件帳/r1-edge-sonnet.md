severity: major

### F1 工具事件的 `turn` 欄位沒有來源,子代理的 `turn_start` 根本不會觸發
severity: major
blocking: 是 — 共同欄位 `turn` 在 tool 事件上無法照 spec 填,S1 與日後消費端會得到錯誤的回合歸屬
- spec 段落:做法 1 事件與格式
引句:「`turn`(回合編號,子代理也有自己的)」
- 問題:型別檔裡 `tool.call` 的輸入只有 `tool`、`tool_use_id`、工具參數與 `agentId`,沒有 `turnId`。`turn.start` 的輸入有 `turnId`,但型別檔明說子代理的執行不會觸發 `turn.start`,只有 `turn.complete` 與 `turn.step` 帶 turnId。spec 沒寫 tool 事件的 turn 怎麼來,也沒說子代理的 `turn_start` 從哪來。
- 失敗場景:主會談一回合內派 3 個並行子代理,各自跑數十次工具。mod 若用「模組變數記目前回合」,子代理的 tool 事件全被標成主回合的 turnId,或標成上一個子代理回合的 turnId。子代理沒有 `turn_start` 事件,`turn_end` 卻有,事件帳裡出現只有結尾沒有開頭的回合。收工檢查想算「這一輪做了什麼」會把子代理的動作歸錯回合。
- file: `claude-code.d.ts:12103` `ToolCallInput = ToolCallEnvelope & AgentLoop`,只多一個 `agentId`;`claude-code.d.ts:12645` 寫「a subagent's run raises no `turn.start`」;`claude-code.d.ts:12721` 是 `TurnStartInput`。

### F2 緩衝與塊序號在並行子代理下沒有定義,會丟事件或覆蓋塊檔
severity: major
blocking: 是 — 預設的「大量平行子代理」場景會讓寫入競態,事件遺失或舊塊被覆寫,spec 沒有任何對策
- spec 段落:做法 2 寫入
引句:「遇到 `turn_end`、緩衝滿 50 筆、或 `session.end` 時,把緩衝寫成一個新塊檔(序號遞增、補零 6 位),清空緩衝。」
- 問題:`$.fs.write` 是 async,而且是整檔覆寫,沒有「檔案已存在就失敗」的模式。多個子代理的 hook 在同一個行程裡並行跑,spec 沒寫兩件事:序號何時取、緩衝何時清空。
- 失敗場景 A:緩衝剛好 50 筆時 flush 在 `await write` 中途,另一個子代理的 `tool` 事件同時進來。若「寫完才清空」,新事件被一起清掉。若「先快照後清」,就看實作怎麼取序號。
- 失敗場景 B:兩個子代理的 `turn_end` 同時 flush,各自讀「目前序號」再 +1。兩個 `await` 之間都拿到 000007,後寫的覆蓋先寫的,整塊事件靜默消失。子代理每個回合都會觸發 `turn_end`,所以並行子代理下這個條件很容易成立。
- 場景 C:`session.end` 在 /clear 或 resume 時只有 1.5 秒的共用上限。flush 若用 `$.session.id()`,拿到的是新的會談編號,舊事件寫進新資料夾。型別檔明說 `e.sessionId` 才是結束中的那一個。
- 這些在 spec 的 S1 到 S3 都沒有條款盯著(都是人工驗,且只跑單一會談)。
- file: `claude-code.d.ts:3121` 起 `fs.write: (path, text) => Promise<void>`,「creating it ... the whole new content」;`claude-code.d.ts:10519` `sessionId` 說明「(`$.session.id()` until now)」。

### F3 寫入路徑沒寫成絕對路徑;頂層判定失敗會永久快取成「不寫」
severity: major
blocking: 是 — 會談 cwd 在子目錄、或 git 判定失敗時,會在錯的位置建 `governance/` 或整場靜默不記
- spec 段落:範圍 3、做法 2 寫入
引句:「沒有就整個會談都不寫(結果記在模組變數,不每次查)」
- 問題 1:`$.fs.write` 的相對路徑解析自會談當下的工作目錄,不是 git 頂層。spec 只說「寫在會談所在 git repo 頂層」,沒寫要用 `git rev-parse` 的輸出組絕對路徑。
- 失敗場景 1:使用者在 `repo/scripts/` 下開 claude。mod 若寫相對路徑 `governance/runtime/events/...`,會在 `repo/scripts/governance/runtime/events/` 建出一棵樹。那棵樹裡的 `.gitignore` 內容 `*` 只蓋住 events 底下,`repo/scripts/governance/` 本身會出現成未追蹤目錄。
- 問題 2:`$.process.run` 在 git 失敗時是 resolve 帶 `exitCode`(例如 128),不是 reject。spec 只講「找頂層」,沒處理非零退出碼與逾時。型別檔預設逾時 30 秒,而 hook 預算是 10 秒。
- 失敗場景 2:首次寫入時 git 報 `dubious ownership`(退出碼 128,例如 repo 在共享磁碟),或超時。mod 把「找不到」記成模組變數,之後整個行程都不寫,也沒有 `ledger_error`。S2 的情境(非 git)與這個瞬態失敗在實作上分不開。
- 問題 3:頂層快取是行程層級,不是會談層級。/clear、resume 或熱重載之後,若 cwd 改了(`CwdChanged`、`EnterWorktree`、`agent.spawn` 的 `cwd`),快取仍指向舊頂層。
- file: `claude-code.d.ts:3396-3415` 寫「resolves `{ exitCode, stdout, stderr }` ... any exit code」「timeout 30 s by default」;`claude-code.d.ts:4927` `HookBudget.ms: 10_000`;`claude-code.d.ts:3523` `CwdChangedHookInput`。

### F4 圖譜判定比 lumos 自己的 `_vault_in` 窄,`docs/knowledge` 與獨立 vault 專案會靜默不寫
severity: minor
blocking: 否 — 只是漏記,資料不會壞,但 S2 的判準與程式現況不一致
- spec 段落:範圍 3、S2
引句:「只在頂層有 `docs/*-knowledge/` 時寫」
- 問題:lumos 認得的圖譜有三種:`docs/*-knowledge`、`docs/knowledge`、以及 `MOC/` 加 `Systems/` 或 `Verification/` 的獨立 vault 根。mod 只認第一種。
- 失敗場景:專案用 `docs/knowledge/` 佈局,lumos 的 `lumos doctor` 運作正常。`lumos enforcement` 的事件帳那列卻永遠 `stale` 或 `unknown`,`lumos events` 印「沒有事件帳」,「可能原因」裡的 repo 沒有圖譜也不對。
- 另外:`$.fs.list("docs")` 回傳的是 entry 陣列,「`*-knowledge`」要自己用 `kind === "dir"` 加後綴比對,spec 沒寫。
- file: `scripts/lumos:19116-19128` `_vault_in` 處理 `docs/knowledge` 與獨立 vault。

### F5 多個 git worktree 下,事件帳跟著 worktree 走,刪 worktree 即遺失,`lumos events` 看不到
severity: major
blocking: 是 — 使用者全域規則要求每個任務開獨立 worktree,這是主流程,不是邊角
- spec 段落:範圍 3、做法 3 讀取
引句:「寫在會談所在 git repo 頂層的 `governance/runtime/events/<會談編號>/<塊序號>.jsonl`」
- 問題:worktree 內 `git rev-parse --show-toplevel` 回的是該 worktree 的路徑,事件帳就寫進該 worktree 的 `governance/runtime/events/`。`.gitignore` 內容 `*` 讓這些檔是「已忽略」,`git worktree remove` 不會擋。
- 失敗場景 1:任務在 `../repo-任務` 的 worktree 做完、合併、刪 worktree。整份事件帳一起消失。RETIRE-IF 預期的消費端(接手視圖、推播量測)事後要查這個任務的事件帳,查不到。
- 失敗場景 2:在主 checkout 跑 `lumos events`(沒給 `--session`,列最近 10 個),只看得到主 checkout 的會談,worktree 的會談全不見。使用者會以為 mod 沒運作。
- 失敗場景 3:`lumos enforcement` 在主 repo 的 `governance/runtime/events/` 看「最近 7 天有塊檔」。使用者整週都在 worktree 工作時恆為 `stale`,每次開場被唸。
- spec 的 PRIOR-ART 與實務隱患都沒提 worktree。
- 子模組同理:`--show-toplevel` 回子模組根,子模組沒有 `docs/*-knowledge`,整個會談靜默不寫,而父 repo 有圖譜。

### F6 塊序號的起點沒定義;行程重啟、熱重載或 resume 到同一個會談資料夾會從 000001 覆蓋舊塊
severity: major
blocking: 是 — 序號若靠模組變數起算,重載後第一次寫入就覆蓋既有事件,且 `fs.write` 不會報錯
- spec 段落:做法 2 寫入、做法 3 讀取
引句:「序號遞增、補零 6 位」
- 問題:spec 沒寫序號初值怎麼定。模組變數的計數器在以下情況歸零:mod 熱重載(前提實驗用的就是熱重載)、`claude plugin update` 後的新行程、同一會談編號被再次載入(resume 若沿用編號)。`fs.write` 是整檔覆寫,不會因檔案已存在而失敗,所以 `000001.jsonl` 被新內容靜默取代。
- 失敗場景:一場跑了數千次工具呼叫、已有 120 個塊的會談,中途 `lumos install` 重跑觸發 `claude plugin update` 並熱重載。新載入的 mod 計數器從 0 開始,下一次 `turn_end` 就覆蓋 `000001.jsonl`,這場會談最早的 50 筆事件永遠消失。讀取端「依塊序號合併」看不出缺漏,也不會計數。
- 要修的方向:首次寫入某個會談資料夾時先 `$.fs.list` 取最大序號再接續,並在 spec 補一條對應條款。現有 S3 只涵蓋寫失敗。
- ⚠ resume 是否沿用同一個 sessionId,型別檔只說 `e.resume.id` 是 `--resume` 所取的 id,沒有明講新會談編號是否相同;即使不沿用,熱重載與 update 這條路已足夠成立。
- file: `claude-code.d.ts:10519` `SessionEndInput.sessionId`、`claude-code.d.ts:10499` 起 resume 說明。

### F7 `origin` 取「最近一筆 session.append」會在並行子代理下取錯主體,且每一列都被這個 hook 走一遍
severity: minor
blocking: 否 — 只污染 `origin` 欄位與增加開銷,不會讓事件帳壞掉
- spec 段落:做法 1 事件與格式(`turn_start` 列)
引句:「取最近一筆 `session.append` 的 prompt 列的來源原樣字串」
- 問題:`session.append` 對主會談與每個子代理的每一列都會觸發,事件帶 `agentId`。spec 沒寫要依 `agentId` 過濾,也沒寫要用 door 或 type 縮小訂閱範圍。
- 失敗場景:主會談要 `turn.start` 時,最近一筆 prompt 列恰好是某個子代理的 `coordinator` 指示。`turn_start.origin` 記成 `coordinator`,實際上是人類提示。收工檢查若靠 origin 分辨「人類回合」會誤判。
- 效能:數千次工具呼叫的會談,每次工具結果與每個回應區塊都經過這個 hook,spec 沒限定只掛 prompt 類的列。
- file: `reference.md:107-115` 寫 `session.append` 涵蓋「each block of the model's response, a tool's result」,且主會談與每個子代理都走。

### F8 `spawn` 事件沒有定義 `agent` 欄位指誰,也沒記到被派出的子代理編號
severity: minor
blocking: 否 — 事件帳可用,但消費端無法把 spawn 和該子代理的後續事件串起來
- spec 段落:做法 1 事件與格式
引句:「|共同欄位:`v`(固定 1)、`ts`(ISO 8601 帶時區)、`session`、`turn`(回合編號,子代理也有自己的)、`agent`(子代理編號,主會談為 null)、`kind`。」(對應 `spawn` 列只有 `agent_type`、`model`、`denied`)
- 問題:`agent.spawn` 的輸入沒有子代理編號,只有 `parentAgentId`。被派出者的 `agentId` 要從 `next(e)` 的結果拿。spec 的 `spawn` 列沒有欄位存它,共同欄位 `agent` 在這一列到底是父還是子也沒寫。
- 失敗場景:主會談一次派 5 個同型子代理(`general-purpose` + `haiku`)。事件帳裡 5 筆 `spawn` 完全相同、`agent` 都是 null,無法對應到後面哪個 `agent` 編號的 tool 事件是它的。
- file: `claude-code.d.ts:263-364` 的 `AgentSpawnInput` 只有 `parentAgentId`;`AgentSpawnResult.agentId` 才是子代理編號。

### F9 市集名固定為 `lumos-toolchain`,來源是本機路徑:換來源、搬家、刪 worktree 都會讓安裝殘留或指錯
severity: major
blocking: 是 — 開發本 repo 的標準流程(在 worktree 跑 install)就會踩到
- spec 段落:做法 4 安裝與移除
引句:「依序跑 `claude plugin marketplace add <來源 repo>`、`claude plugin install lumos-ledger@lumos-toolchain`;」
- 問題:市集 `lumos-toolchain` 登記的是一個本機路徑(`Path(__file__).resolve().parent.parent`,即 `cmd_install` 內的 `_src_repo`)。這個 repo 本身目前就在 worktree `lumos-toolchain-event-ledger` 裡開發。
- 失敗場景 1:使用者從 worktree 跑 `lumos install`,市集指向 worktree 路徑。任務合併、worktree 刪除後,市集來源不存在,`claude plugin update` 與之後 Claude 啟動時的更新都失敗。spec 只說「失敗只印一行、回傳碼不變」,使用者不會知道 mod 已經凍結在舊版。
- 失敗場景 2:機器上有兩份 lumos clone(例如 `~/harness/lumos-toolchain` 與另一份)。第二份的 `marketplace add` 與同名市集衝突,spec 要靠「退出碼加輸出判斷」,且「實際訊息在實作時用真的 `claude` 量」,即這個關鍵分支目前完全沒有行為定義。
- ⚠ `claude plugin update` 是否在 `plugin.json` 版本沒變時仍會重新取檔,spec 沒寫;若不會,「重跑 install 能拿到新版 mod」不成立,而 spec 沒要求每次改 mod 都要升 `plugin.json` 的 version。
- file: `scripts/lumos:16908-16945` `cmd_install` 目前沒有任何外掛處理;`scripts/lumos:16940` 起 `_src_repo` 用法。

### F10 無保留期限,事件帳目錄無限增長;讀取與 enforcement 的掃描成本沒設上限
severity: minor
blocking: 否 — 短期無礙,但「數千次工具呼叫的會談」與長期使用會讓掃描變慢
- spec 段落:做法 2 寫入、做法 3 讀取、做法 5 enforcement
引句:「沒給 `--session` 就列最近 10 個會談(會談編號、最後事件時間、回合數、工具呼叫數、失敗數)」
- 問題:每個 `turn_end` 一個塊檔,不論只有 2 筆事件。長會談一個目錄就有數百到數千個小檔,沒有合併、輪替或刪除。
- 失敗場景:一年後 `events/` 底下有數百個會談資料夾、數萬個塊檔。`lumos events` 要算每個會談的回合數與失敗數,必須讀完所有塊檔才能列出最近 10 個,沒說靠目錄 mtime 先排序再只讀 10 個。`lumos enforcement` 每次開場都跑,「最近 7 天有塊檔」若遞迴走完整個樹,常態路徑反而變慢,與 spec 自己寫的「常態路徑不該付這筆」衝突。
- 另外:誠實界線只承認緩衝最多 49 筆在當機時遺失,沒承認磁碟滿時連續失敗後 `ledger_error` 本身也寫不進去(「只記一次」之後就沒有任何痕跡)。

### 逐節核對
- 前言與 front matter:已讀,無 finding。`lands_in` 四個節點在落點段有交代。
- 範圍:F3、F4、F5 命中第 3 項。
- 做法 1:F1、F7、F8。
- 做法 2:F2、F3、F6。
- 做法 3:F5、F10。
- 做法 4:F9。已核對 `_refuse_if_probe` 與 `cmd_install` 開頭、`cmd_teardown` 第三步呼叫 `cmd_uninstall`,與 spec 寫法一致,無 finding。
- 做法 5:F5、F10。
- 條款 S1 到 S9:S1、S3 只驗單一會談,F1、F2、F6 沒條款覆蓋(見各條)。S4 到 S9 已讀,無額外 finding。
- 回退:已讀,無 finding。
- 實務隱患:列出的四類已讀;補一條 spec 沒列的風險類。並行與資料完整性:有,見 F2、F5、F6。
- 誠實界線:已讀,F10 末段補一點。

最嚴重 severity:major,blocking 共 6 條(F1、F2、F3、F5、F6、F9)。
