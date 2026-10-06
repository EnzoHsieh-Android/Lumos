severity: blocker

審稿席:整合知識同步(Sonnet)。對照 repo:/Users/enzo/harness/lumos-toolchain-mod-batch2。只讀;沒有改任何檔。
派工尾端沒有附 hook 牽連節點,所以沒有逐條判牽連節點的項目;下面〈決策與合約對照〉自己查了與本案相關的節點。

## 逐節

- 範圍 做 1(壓縮前):見 finding 11。
- 範圍 做 2(會談編號):見 finding 2、10。
- 範圍 做 3(審查員有沒有照實讀):見 finding 6、7。
- 範圍 做 4(Bash 改檔前推筆記):見 finding 1、9、13。
- 範圍 做 5(記憶標記):見 finding 2、3、4、8、11、14。
- 範圍 不做:已讀,無 finding(「壓縮後重新注入」判斷成立:lumos-entry-hook、ci-status-hook、memory-sweep 在 `scripts/merge-claude-settings.py:164` 的 SessionStart 區都沒有 matcher)。
- 做法要點:併入上面各 finding。
- 條款:見 finding 12。
- 回退:見 finding 5。
- 實務隱患:見 finding 3(不刪)、finding 4(注入)、finding 10(並行)。這節沒有「並行、路徑、注入」三類的表態。
- RETIRE-IF / REVISIT:見 finding 5(量不到)。

## Findings

### 1. Bash 擴充 matcher 會弄壞 Codex 註冊,也會讓舊用戶的 settings 重複註冊
severity: blocker
blocking: 是 — 照做後 Codex 端改檔推播整條失效,Claude 端升級後同一支 hook 對 Edit 跑兩次

引句:「連同安裝端把觸發條件從 `Edit|Write|MultiEdit` 加上 `Bash`」
引句:「Codex 那邊不動。不用 mod:官方 hook 做得到」

重現:
- Codex 註冊表是由 Claude 註冊表轉出來的,轉換靠「matcher 字串完全等於 `Edit|Write|MultiEdit`」才改成 `apply_patch`。matcher 一改成 `Edit|Write|MultiEdit|Bash`,等號不成立,Codex 那條會原樣帶著 `Edit|Write|MultiEdit|Bash` 寫進 `~/.codex/hooks.json`。Codex 的改檔工具叫 apply_patch,這個 matcher 對不上,整條推播靜默失效。「Codex 那邊不動」這句因此做不到:不動 `_codex_entries` 就是 Codex 被改壞。
  file: `scripts/merge-claude-settings.py:271`
- 合併器判斷「這條已存在」用 `_equivalent`,第一個條件就是兩邊 matcher 相等。已安裝的用戶 settings 裡是舊 matcher,新註冊表是新 matcher,兩條不等價,所以舊的留著、新的另外加一條;末尾的自癒去重也用 `_equivalent`,同樣不會把舊的收掉。結果同一支 impact-hook 對每次 Edit 觸發兩遍(冷卻窗雖有,第二條會吃到「冷卻中」,但仍多一次啟動;Codex 同理)。要回退(第 4 項改回舊 matcher)時又會重複一次。
  file: `scripts/merge-claude-settings.py:324-331` 與 `:335-370`
- spec 的落點只寫「安裝端觸發條件」,沒寫要在合併器加「舊 matcher → 新 matcher」的遷移,也沒列要改 `_codex_entries` 與 `t_` 開頭的合併器測試。

### 2. 記憶清掃 hook 拿不到會談編號,S7/S8 的「會談編號相同」前提在 SessionStart 時成立不了
severity: major
blocking: 是 — 第 5 項在會談接續、`/clear` 或單純開場時可能整份不生效,而 S8 的測試仍能綠

引句:「把結果(會談編號、哪幾篇記憶檔、什麼原因)寫進 lumos 自己的快取資料夾,按會談編號分檔」

重現:
- `memory-sweep.py` 全檔沒有讀 stdin,也沒有讀任何會談編號環境變數;`main()` 只認 `--dir`、`--budget`、`--quiet`、`--harness`。SessionStart 的 JSON 有 `session_id`,但這支沒接。spec 沒說編號從哪來。
  file: `scripts/hooks/claude/memory-sweep.py:937-957`
- 若退而讀環境變數:`LUMOS_SESSION_ID` 要等第一個 `turn.start` 才會被外掛設,SessionStart 比它早,讀不到;`CLAUDE_CODE_SESSION_ID` 正是 spec 自己說接續後停在舊值的那個。接續後 hook 寫「舊編號」檔,外掛用 `$.session.id()`(新編號)去讀,S7 的「編號不同 → 整份不動」把標記整個關掉,而且不報錯。
  file: `docs/lumos-toolchain-knowledge/Issues/會談編號環境變數接續後停在舊值.md`(本案 S2 要修的就是這個症狀)
- 看門狗結構還有一層:`--budget` 模式真正的清掃在子行程,超時時父行程只印「超時」不寫檔;所以「沒事也寫」要分清三條路徑(子行程正常跑完、看門狗超時、`memory_dir` 不存在就提前 return)各自寫不寫。spec 只講「每次跑完」。
  file: `scripts/hooks/claude/memory-sweep.py:873-897`、`:953`

### 3. 「只寫快取資料夾」沒有說資料夾在哪,也沒有機械守衛;既有的唯讀守衛測試與錨點核可沒列
severity: major
blocking: 是 — d3 的安全論證(路徑由 lumos 組、不碰記憶資料夾)無法審,現有守衛會紅

引句:「這次寫的路徑由 lumos 自己組、不從記憶內容推、不碰記憶資料夾」
引句:「唯一的寫檔是 lumos 快取資料夾裡的衍生結果,不刪不改既有檔」

重現:
- 全文沒有給出快取資料夾的路徑。事件帳是寫進 repo 的 `governance/runtime/events/`(要先解主 checkout、逐層驗不是連結);`_hookevent.py` 也是寫 repo 內 `governance/runtime/`。如果快取資料夾放 repo 裡,路徑就是 repo 內容控制的:事件帳設計審已經因此訂了「從 repo 根往下每層不能是連結」的規則(RULE,見 `Systems/lumos事件帳`),也正是 d3 說要避開的「符號連結導到目錄外」那一類 blocker。如果放家目錄,就得說放哪、權限、檔名驗證(從 stdin 來的 session_id 要過跟 `SESSION_RE` 同一套規則)。沒有路徑,「不碰記憶資料夾、只寫快取」只是意圖,不是可審的條款。S8 的測試名只驗「有寫、沒寫別處」的快樂路徑。
  file: `mods/claude/lumos-ledger/hooks/register.ts:121-136`、`scripts/hooks/claude/_hookevent.py:35`
- 另在 worktree 內開的會談:hook 的 cwd 是 worktree、外掛 `$.session.cwd()` 也是,但事件帳的規則是寫主 checkout。若兩邊各算各的「快取資料夾」,對不上就是整份不動、靜默無標記。spec 沒說沿用哪套位置判定。
- 現有守衛會紅:`t_memory_sweep_core` 的 ⓪ 用正則禁止原始碼出現 `write_text(`、`.write(`、`open(...'w'|'a')`;S8 一加寫檔就紅。spec 沒說是放寬 ⓪、還是把寫檔放獨立模組(後者也要處理 hook 複製到 `~/.claude/hooks/` 時多一個檔的白名單 `_GLOBAL_CLAUDE_HOOKS`)。放寬 ⓪ 等於拿掉 d3 唯一的結構性守衛,卻只換來「S8 測試」。
  file: `scripts/test_lumos.py:49305-49335`
- `memory-sweep.py` 與 `impact-hook.py` 都在 ANCHOR_FILES;改它們推送前要 `lumos anchor approve --note`。spec 的做法與回退都沒提這一步。
  file: `scripts/lumos:22485-22500`
- 輸出字串「記憶過期清掃(唯讀,沒有改任何檔):」與測試 `split("記憶過期清掃(唯讀")` 綁在一起;`Systems/記憶過期清掃` 的 responsibility 寫「不負責:改任何檔(2026-09-14 起唯讀)」。spec 落點有列這篇,但沒說這幾處要一起改,也沒有在該節點記 d3 的部分翻案(那篇的決策只在正文,沒有 decisions 欄,沒有地方標 superseded)。
- 「不刪」與「只留七天內的檔」互相矛盾:見 finding 8。

### 4. 標記的「原因」文字來自記憶與圖譜內容,直接寫進 memory 層指令檔,繞過現有的安全框
severity: major
blocking: 是 — 注入邊界是這個 repo 反覆審出 blocker 的老題目,新增一條未框的路徑

引句:「在那幾行行首加上 `⚠ 已過期或與圖譜對不上:<原因>`」

重現:
- 現有清掃的報告一律過 `_frame_injected` 加 `_plain_label`,理由寫在檔頭:內容來自專案裡的人寫得動的地方(圖譜節點名、記憶 claim),所以要框起來並聲明是資料不是指令。這條新路徑把同一批字串(`_sweep_one` 的 claim 與 `why_unknown`、`cross_check` 的節點名與 detail)改放在 `instructionFiles` 的 memory 層內容裡,進到比「機器附加的參考資料」更高信任的位置、而且沒有框。clone 一個圖譜節點名帶指令句的 repo,節點名就會出現在每個會談的記憶索引行首。
  file: `scripts/hooks/claude/memory-sweep.py:60-100`、`:830-870`、`:790-815`
- 修法方向:原因只用固定列舉(例如 stale / unknown / conflict),不帶任何來自內容的字串;細節仍走原本有框的那段開場報告。spec 沒有這條限制。

### 5. RETIRE-IF 與 REVISIT 要用「事件帳」量的東西,事件帳不記;回退寫法也不成立
severity: major
blocking: 是 — 回頭條件量不到等於沒有回頭條件;回退方案照做會留下殘件

引句:「事件帳看得到壓縮事件」
引句:「用事件帳比對上線前後同長度會談的快取命中」
引句:「用事件帳數這一個月壓縮次數、seat-check 抓到幾條沒讀過的引用、Bash 改檔推送次數」
引句:「把 `lumos-context` 從外掛清單與市集檔拿掉,下次 install / update 就會移除」

重現:
- `register.ts` 掛了 session.append、turn.start、turn.complete、tool.call、agent.spawn、session.end,沒有 `session.compact`,也沒有 token 或快取用量欄位;`turn_end` 只有 `reason`。所以「壓縮事件」「快取命中」兩項事件帳現在都沒有。spec 的 S5 只加 spawn 欄位,沒有加這兩類事件,REVISIT 2026-11-06 到期時沒有資料可比。
  file: `mods/claude/lumos-ledger/hooks/register.ts:240-262`、`:333-381`
- 「seat-check 抓到幾條」:`cmd_seat_check` 只印到終端(觀測恆 rc0),沒有寫帳;只有 `--ledger` 才 append,而且那是越界帳、spec 明說不共用。「Bash 改檔推送次數」:事件帳只記 Bash 的前 500 字,不記 hook 有沒有推;impact-hook 的 hook-events 記的是跑過,不是推了。三個數字都沒有來源。
  file: `scripts/lumos:23490-23575`
- 回退:`_sync_claude_plugin` 只「確保清單裡的外掛在」,`_teardown_claude_plugin` 只移除清單裡寫死的那一個外掛名(`_LEDGER_PLUGIN`);沒有任何「清單沒有的就移除」的邏輯。把 lumos-context 從清單拿掉,已裝過的機器上該外掛仍留著,而市集檔不再列它,下次 `claude` 載入可能報錯或繼續跑舊外掛。真正的回退需要一段「移除已知曾經發布過、現在不在清單的外掛」。
  file: `scripts/lumos:22063-22100`(`_teardown_claude_plugin`)、`:21992`(`_sync_claude_plugin`)

### 6. seat-check `--events` 的「從沒讀過」口徑會在最常見的收貨情境誤報,而且與既有 seat-check 契約相衝
severity: major
blocking: 是 — 條款 S4 自稱「寧可漏報不誤報」,實作口徑做不到,而且會逼審查席為了過檢查而去多讀檔

引句:「寧可漏報不誤報」
引句:「沒帶路徑就算會談工作目錄底下全部」

重現(逐條可造):
- 席位引用的內容常不是自己 Read 來的:(a)派工尾端由 dispatch-lens hook 附上的牽連節點全文,席位直接引用其中的 `file:` 路徑與引句,事件帳裡沒有任何 Read;(b)席位用 `python3.14 scripts/lumos show|decisions|contracts <節點>` 看圖譜,Bash 指令字串裡只有節點名、沒有 `docs/…/X.md` 路徑,但報告引用 `docs/…/X.md:12`;(c)`git -C … show`、管線組合的指令超過 500 字被截斷時,spec 只在「那一席有 Bash 指令被截斷時,結果標可能誤報」才標註,其餘 Bash 讀法(`lumos search` 命中)沒有標註。以上三種都會被列成「從沒讀過」。
  file: `mods/claude/lumos-ledger/hooks/register.ts:66-78`(Bash 只記 `cmd.slice(0, 500)`,路徑只取 `file_path`/`path`/`notebook_path`)
- 「沒帶路徑就算會談工作目錄底下全部」:事件帳寫出去的事件沒有 cwd 欄(`base()` 只有 session、agent、worktree、ts、ev);cwd 只用在位置判定、沒落檔。子代理還可能在 spawn 時指定自己的 `cwd`。reader 沒有資料可判。S5 只加了席位標記等三欄,沒有加 cwd。
  file: `mods/claude/lumos-ledger/hooks/register.ts:225-227`(`base`)
- 路徑正規化沒寫:報告 `file:` 多半是相對 repo 根(`scripts/lumos:123`)或絕對路徑指向 worktree;事件帳 Read 記絕對路徑,Bash 記原字串。比對規則(相對對絕對、worktree 對主 checkout、`..`、符號連結)spec 沒定。
- 「引句所在檔」怎麼找:引句要先在某個檔裡定位才知道「所在檔」,spec 沒說去哪些檔掃(整個 repo?只掃席位讀過的?掃全 repo 找到 2 個檔、其中 1 個讀過算不算讀過?)。
- 既有契約相衝:`cmd_seat_check` 的說明明寫「只驗引句錨定,不碰 file:line 證據;repo 查證引用恆合法」與「射程:席一致地說謊抓不到」。S4 新抽 `file:` 並判不合法,翻了「repo 查證引用恆合法」這條設計;d2 只講推翻「不驗不記」,沒提這條。design-loop 節點的 WHY 也提到「合法材料仍只觀測,不擴張責任」。
  file: `scripts/lumos:23490-23510`

### 7. `LUMOS-SEAT:` 席位標記與「派工鏡頭附加段」都不是現成約定,派工範本與判定方法沒落
severity: major
blocking: 是 — 沒有範本會帶標記,S4/S5 在真實派工上全部「找不到那一席」

引句:「席位標記(`LUMOS-SEAT:` 後面那串)」
引句:「有沒有派工鏡頭附加段」

重現:
- repo 全域搜尋(scripts、docs、mods、skills)`LUMOS-SEAT` 只出現在這份 spec。現有的派工標記是 `LUMOS-IMPACT:`、`LUMOS-SPEC:`、`LUMOS-ROLE-CARDS:`,由 dispatch-lens-hook 逐行比對,範本在 `skills/lumos-design-loop/templates.md` 與 `skills/lumos-code-loop/SKILL.md` 等。新增第四個標記要改這些範本,否則編排者不會寫;落點沒有列 skills 範本,也沒有說標記放第一行與 dispatch-lens-hook 的逐行比對有沒有互相干擾(它只認自己的三個,理論上不干擾,但沒驗)。
  file: `scripts/hooks/claude/dispatch-lens-hook.py:25-31`、`skills/lumos-design-loop/templates.md:148`、`:272`
- 「有沒有鏡頭附加段」沒有可判的形狀:hook 的輸出有多種(固定席內容、`LUMOS-LENS:` 超時說明、鎖錯誤說明、0 篇不注入、設計審另一種),spec 沒定哪些算「有」。另外 spec 自己的 PRIOR-ART 也沒有確認 `agent.spawn` 看到的是改寫前還是改寫後(只在做法要點寫「實作前先實測」)。
  file: `scripts/hooks/claude/dispatch-lens-hook.py:46-75`
- 外家席(Codex)沒有 Claude 事件,S4 永遠回「找不到那一席」;而外家席正是最需要核對的獨立視角。spec 沒有承認這個範圍界線。

### 8. 「不刪」與「只留七天內」互相矛盾,而且沒指定誰負責刪
severity: major
blocking: 是 — 要嘛快取無限長,要嘛得在 hook 加刪檔,與 d3 的風險論證衝突

引句:「快取資料夾只留七天內的檔」
引句:「不刪不改既有檔」

重現:
- 兩句出自同一份 spec。事件帳設計審 r2 已裁:清理放讀取端、要人或排程跑,因為寫入端 mod 沒有刪除功能;新機制要嘛沿用(`lumos` 子指令清),要嘛另寫。spec 沒說「只留七天」是誰做:hook(要新增刪檔,d3 當年三輪 blocker 全在寫/改檔,刪檔也是同族)、外掛(沒刪除功能)、還是某個 lumos 指令(沒列)。
  file: `docs/lumos-toolchain-knowledge/Systems/lumos事件帳.md`(WHY 2026-10-05 設計審 r2)

### 9. 若把 "Bash" 加進 impact-hook 的 `EDIT_TOOLS`,`lumos handoff` 會漏掉所有 Bash 指令
severity: minor
blocking: 否 — 是實作時才會踩的條件式地雷,現有 `t_handoff_view` 很可能會抓到

重現:
- impact-hook 入口是 `if tool_name not in EDIT_TOOLS: return 0`,最自然的做法就是把 Bash 加進 `EDIT_TOOLS`。但 `lumos handoff` 用 importlib 借這個集合,`if name in edit_tools: … elif name == "Bash":`;Bash 一進集合,`elif` 永遠到不了,指令摘要清空,且 Bash 項目被當成沒有 `file_path` 的改檔。
  file: `scripts/hooks/claude/impact-hook.py:777`、`scripts/lumos:46364-46387`
- spec 沒說 Bash 與 EDIT_TOOLS 的關係(另開一個 BASH_TOOLS 才安全)。

### 10. `LUMOS_SESSION_ID` 優先於 `CLAUDE_CODE_SESSION_ID` 的規則,在巢狀會談與同行程多會談下會讀到別人的編號
severity: major
blocking: 是 — S3 的優先序是單向的,錯值不會被後備修正(⚠ 同行程多會談那條我判不準)

引句:「應先讀 `LUMOS_SESSION_ID`,沒有才讀 `CLAUDE_CODE_SESSION_ID`」
引句:「每個回合開始時用 `$.env.set` 把 `$.session.id()` 設進 `LUMOS_SESSION_ID`」

重現:
- 巢狀:在一場 Claude 會談的 Bash 裡再叫 `claude -p`(本 repo 的 headless 探針與自動迭代都這樣做)。外層的 `LUMOS_SESSION_ID` 會被子行程繼承;若子行程沒載入 lumos-context(隔離設定目錄、`LUMOS_SKIP_CLAUDE_PLUGIN`、外掛沒裝),它的 `CLAUDE_CODE_SESSION_ID` 是正確的新值,但 lumos 先讀到外層繼承來的 `LUMOS_SESSION_ID`,於是 handoff 排掉的是外層會談的逐字稿而不是自己的。
- ⚠ 同行程多會談:`$.env.set` 的型別說明是「this process 的環境,之後啟動的 Bash、MCP、`$.process.run` 都繼承」;事件帳自己的緩衝以會談編號為鍵、每筆帶自己的 cwd,表示作者假設一個外掛行程可能同時服務多個會談。A、B 兩個會談交錯時,B 的 `turn.start` 把全行程的值改成 B,A 之後的 Bash 讀到 B。型別檔沒有說明是不是每會談一份環境,我判不準,需要實測。
  file: 型別檔 `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3475-3510`
- 做法要點裡的實測流程:「`claude -p` 派一個回合,再 `/clear` 或接續後印一次」,`-p` 沒有 `/clear`;只能測 `--resume`,/clear 那條測不到。另外 `$.session.id()` 與逐字稿檔名 stem 是否一致沒驗(handoff 用 `p.stem == me` 比對),接續後逐字稿是新檔還是沿用舊檔,spec 沒有確認。
  file: `scripts/lumos:46262-46275`

### 11. 壓縮與開場重算的時序:precompute、`instructionFiles` 未定義、索引上限
severity: minor
blocking: 否 — 各自有保守退路,但 spec 該寫下來

引句:「三種觸發都附,含預先計算 `precompute`;已附過就不重附」
引句:「外掛先跑就讀不到檔、整份不動,不會標錯」

重現:
- precompute 的結果「保留給下一次壓縮」;附加段是固定文字,沒問題,但摘要的內容(審查席在跑、未提交的改動)是 precompute 當下的對話狀態,真正壓縮時可能已過時。這是引擎行為,不是本案造成,但「保住交棒狀態」的承諾因此不是壓縮當下的狀態,spec 該講。
- `prompt.context` 的輸入 `instructionFiles` 在上游 hook 改寫過 `claudeMd` 時是 undefined;S7 的「整份不動」條件沒列這一種,也沒列「索引不在 `kind: memory`」。
  file: 型別檔 `…/claude-code.d.ts:8063-8080`
- 壓縮或 `/clear` 後 prompt.context 重算:SessionStart 的記憶清掃同時重跑,誰先誰後 spec 只談了開場。壓縮重算時若外掛先跑,讀的是上一輪的結果檔,已修好的記憶仍被標,到下一次重算前不會更正。
- 標記加長索引行:記憶清掃自己有「索引只載入前 200 行或 25 KB」的 RULE,標記是在載入後加的(`instructionFiles` 之後),不影響引擎截斷,但接近上限時模型看到的實際字數比 `index_size_note` 量的多;沒有大礙,記下即可。
  file: `docs/lumos-toolchain-knowledge/Systems/記憶過期清掃.md`(RULE 2026-09-25)

### 12. 條款有五條只能人跑,CI 沒有 Claude;既有外掛的機械守衛沒有等價物
severity: minor
blocking: 否 — 設計審的「綁定」成立,但保護力弱於事件帳那批

引句:「[manual:claude plugin test mods/claude/lumos-context 的 S1 測試全綠]」

重現:
- S1、S2、S5、S7 四條外掛行為條款靠 `claude plugin test`,事件帳節點明寫「CI 沒有 Claude」。事件帳那批有 Python 端的 `t_ledger_plugin_files_valid`(市集、描述檔、`$.fs.write` 只出現一次、禁用會改行為的介面)與 `t_ledger_rules_match_reader`(兩端規則對齊)當機械守衛。lumos-context 刻意要用 `prompt.context`、改 `instructions`,沒有對應的 Python 側結構測試(例如「只寫 `LUMOS_SESSION_ID` 這一個環境變數」「不呼叫網路」),spec 的「已排除:對外送出」只靠敘述。
  file: `scripts/test_lumos.py:71541-71580`
- S2 另有備案路徑(`CLAUDE_PID` 小檔)沒有條款;一旦走備案,S2、S3 的描述就變了,沒說條款怎麼跟著改。

### 13. Bash 改檔路徑的解析:相對路徑、`cd`、假陽性
severity: minor
blocking: 否 — S6 已寫「只讀的 Bash 不推」與預算內失敗放行,屬補強

重現:
- 目的路徑若是相對路徑,現有邏輯用 `repo`(`CLAUDE_PROJECT_DIR` 或 payload cwd)解析;Bash 指令裡常見 `cd sub && sed -i … f.py`,真正的目的檔在 `sub/` 下,解析會指到錯的路徑或查無。
- 寫檔形狀的正則會誤判:`2>&1`、`> /dev/null`、`[ a > b ]`、`git commit -m "... > ..."`、`python -c "print(1 > 0)"`。S6 只列了正例。
  file: `scripts/hooks/claude/impact-hook.py:147-160`(`_decide_one` 只看副檔名與排除路徑)
- 另外 `主session鏡頭利用率` 計劃把「推送」定義成 hookName 屬於 `Edit|Write|MultiEdit` 的附件;Bash 推送出現後,該量測的過濾條件要確認不把 `PreToolUse:Bash` 混進去(該計劃在 `Projects/主session鏡頭利用率_計劃`,spec 沒列為牽連)。

### 14. 標記語意與清掃輸出的對照不齊:「驗不了」「沒驗完」「超時」
severity: minor
blocking: 否 — 屬行為定義缺口,實作時會被迫自己決定

引句:「`⚠ 已過期或與圖譜對不上:<原因>`」

重現:
- 清掃的結果有四種:對不上(`✗`)、驗不了(`?`)、沒驗完/超時、跨檔衝突/影子副本。「已過期或與圖譜對不上」只涵蓋第一與第四;「驗不了」(例如 verify 寫法看不懂)要不要標、「結果不完整」時是否整份不標,spec 沒說。
- 結果裡只有已經過 `_clean(f.name)`(上限 120 字)格式化的字串行,沒有 `(檔, 原因)` 的結構;要寫「哪幾篇、什麼原因」得改 `Tally` 與 `_sweep_one`、`cross_check` 三處,而不是「寫出結果」一句話的份量。
  file: `scripts/hooks/claude/memory-sweep.py:595-604`、`:752-790`

### 15. 落點與決策登記缺項;新外掛沒有健康檢查那一列
severity: minor
blocking: 否 — 屬收尾缺項

重現:
- 落點節點與檔對得上(`Systems/lumos事件帳` 的 about_code 含 `register.ts`、`Systems/lumos-cli-lifecycle` 含 `scripts/lumos` 與 `merge-claude-settings.py`、`Systems/記憶過期清掃`、`Systems/改檔前推播`、`Systems/design-loop` 的 about_code 是整支 `scripts/lumos`)。但有幾個節點也會被動到卻沒列:`Systems/lumos-cli-read`(`lumos handoff` 與 `lumos events` 的家)、`Systems/hook信任邊界`(finding 4)、`Systems/派工鏡頭`(標記與附加段)、`Projects/Codex完全支援_計劃`(合併器對照表,finding 1)、`Issues/會談編號環境變數接續後停在舊值`(要結案)。
- 翻案的登記:`Projects/派工鏡頭注入_計劃` 與 `Systems/記憶過期清掃` 目前都沒有登記「動了會壞」的合約(`lumos contracts` 回空),翻案靠 decisions 欄與正文;spec 只在本計劃寫了 d2、d3,沒有說要用 `lumos decision-add` 在被翻案的節點記一筆(標 superseded 或附「部分翻案」),三個月後只讀舊節點的人會照舊決策做事。
- 事件帳有 enforcement 的 `claude-event-ledger` 列判斷「外掛有沒有在寫」;lumos-context 失敗(沒裝、載入錯)時標記與編號都靜默消失,沒有對等的一列,與 `Projects/消費專案接入靜默失效` 同型。

## 決策與合約對照

- 派工鏡頭注入計劃「不驗不記」:spec 對這條的翻案描述正確(開案決策寫「不擋不驗不記不量」,正文第 10 條寫「不驗證審查員有沒有讀、不記治理帳、不量成效」)。但漏了同一計劃「鏡頭不是閘」與 dispatch-lens-hook 在 ANCHOR_FILES 內:S5 只讀 spawn 不改派工詞,不影響該 hook;判不影響。漏列的是 seat-check 自己的契約(finding 6)。
- 記憶過期清掃「唯讀」:翻案理由寫得準(三輪 blocker 都落在寫檔),但同一節點第八輪的裁定「同一類發現連續兩輪修了但沒修乾淨,就該問這一類值不值得留」與 d3 要新增寫檔點同族;新增的寫檔需要 finding 3 的守衛與位置說明才算閉合。
- 事件帳「只觀察」:S5 只往 spawn 事件多記三欄,不違反;lumos-context 是另一個外掛,不繼承 `t_ledger_plugin_files_valid` 的禁用清單(finding 12)。事件帳節點沒有合約行可破壞;其 RULE「印到終端的內容過 `_esc_clean`」要求新欄位(席位標記)走同一個清理,spec 沒提,seat-check 讀它時要過。
- `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只動 sentinel 內):本案不碰,判不影響。
- `Systems/design-loop` 的 ★INVARIANT★ 處置閘第五步(條款綁測試與句式):本計劃的條款句式與 `[manual:]` 對風險高的計劃可通過;S2 一條裡含兩個「應」子句(換編號後下一回合應換新值),在複合觸發檢查下可能被擋,建議拆成兩條(⚠ 我沒跑 spec-gate,判不準)。

總結:最嚴重 blocker,blocking 9 條
