severity: major

整合/知識同步席(第 2 版修訂稿)。姿態:三個月後的接手者,預設文件跟現實已經對不上。派工尾端沒有 hook 附上的牽連節點(收到的派工詞裡沒有那一段),所以牽連節點由我自己查:Systems/lumos事件帳(RULE 與 S8/S9)、Projects/派工鏡頭注入_計劃(d1)、Systems/記憶過期清掃(這版已不做,不受影響)、審查席隔離分支的 lumos-guard。判定見 F1、F3、F4。

## 逐節結果

- frontmatter / d1 / d2 / d3:見 F7(d1 翻案對象沒錯、d2 翻案對象有一處措辭偏、d3 殘留)。
- 範圍:做 1(壓縮前保住交棒狀態):已讀,無 finding(官方型別檔 `session.compact` 四種觸發、`agentId`、`instructions` 可改都對得上)。僅 F9 提到的全域副作用。
- 範圍:做 2:見 F8、F9。
- 範圍:做 3:見 F2、F3、F5、F10。
- 範圍:不做:已讀,無 finding。「Bash 改檔前推筆記」「開場標出驗證不過的記憶」拿掉後,Systems/記憶過期清掃的「唯讀」設計不再被動到,這是對的。
- 落點:見 F4(漏列檔的家)、F1(enforcement 那一列的家是事件帳,不是 lifecycle)。
- 做法要點:見 F1、F3、F4。
- 條款:見 F1(缺條款)、F4(S9 會撞既有測試)。
- 回退:見 F4。
- 實務隱患:見 F9。

### F1 enforcement 那一列的改法違反事件帳節點上現行有效的 RULE,而且既有測試釘著不准
severity: major
blocking: 是 — 照字面實作會讓既有 S8 測試轉紅,並讓沒裝外掛的人每次開場被唸

1. spec 要把 `lumos enforcement` 既有的事件帳外掛那一列改成逐支列出外掛有沒有裝上。「有沒有裝上」只有 `claude plugin list --json` 能答(lumos 自己判外掛是否裝好用的就是 `_ledger_user_plugin`,它跑的是 `claude plugin list --json`)。
2. 現況那一列根本不是「有沒有裝上」,是只看事件帳資料夾修改時間、三值 active/stale/unknown、明講不呼叫外部指令。
   file: `scripts/lumos:24158`
   file: `scripts/lumos:24177`
3. 事件帳節點上有一條寫齊 `[since:2026-10-05][retire:…][confirmed:2026-10-05]`、沒被標作廢的 RULE(在半年內,有挑戰程式碼的效力):那一列只准 active/stale/unknown 三值,除了解主 checkout 的那一次 git rev-parse 之外不呼叫外部指令(尤其不叫 claude);理由是開場提醒只點名 inactive、degraded,且 enforcement 每次開場都跑、叫 claude plugin list 每次約 0.9 秒。retire 條件(開場提醒改成不只點名 inactive/degraded,或分母規則改變)沒有成立。
   file: `docs/lumos-toolchain-knowledge/Systems/lumos事件帳.md:24`
4. 既有條款與測試也釘死:事件帳計劃 S8「不得出現 inactive 或 degraded,且除了解主 checkout 的那一次 git rev-parse 之外不得呼叫外部指令(尤其不叫 claude)」,綁 `t_enforcement_ledger_row`、`t_enforcement_ledger_row_git_hang`、`t_enforcement_ledger_row_symlinks`;另有 `t_enforcement_never_raises_on_missing` 釘「恰 24 列」、`t_enforcement_summary_excludes_unknown` 釘 unknown 列數。逐支加列或改列數會連動這幾支。
   file: `scripts/test_lumos.py:34108`
   file: `scripts/test_lumos.py:34095`
   file: `scripts/test_lumos.py:70729`
5. spec 沒有:說明這是翻案該 RULE(四條 d 裡都沒有)、說明新列的狀態值(「沒裝」只能是 inactive/degraded,正好觸發開場提醒;用 unknown 就看不到,跟「沒裝時看得到」矛盾)、一條綁測試的條款(S1–S10 沒有一條管 enforcement)、也沒說 `claude` 呼叫的逾時與測試隔離(`LUMOS_SKIP_CLAUDE_PLUGIN`)。
6. 落點也錯:該列的家是 Systems/lumos事件帳(它的 responsibility 明寫「enforcement 的 claude-event-ledger 那一列怎麼判」),spec 只把 lifecycle 列為外掛清單的家,沒把這一列落到事件帳。
引句:「既有的事件帳外掛那一列,改成逐支列出外掛清單裡的外掛有沒有裝上」
修法方向(不是要求):不動既有那一列;若要看得到 lumos-context 沒裝,新增獨立一列,只讀檔案系統能答的訊號(例如外掛最近有寫設定檔?)或乾脆砍掉這一句;真要叫 claude,就先寫 decision 翻案該 RULE 並補條款。

### F2 `seat-check` 的席位標記組不出來:真實派工單用 `seats` 清單,沒有 `seat`
severity: major
blocking: 是 — 照字面實作,`<資料夾>/<round>/<seat>` 的 seat 恆為空,第 3 項整項找不到席

1. spec 說標記「由派工單組成 `<派工單所在資料夾名>/<round>/<seat>`」。現行 `cmd_seat_check` 讀的是 `disp.get("seat")`(單席)。
   file: `scripts/lumos:23523`
2. 實掃 repo 內 `governance/review-reports/*/*dispatch.json` 400 份:399 份只有 `seats`(物件陣列,每席 `seat`/`lens`/`auditor`),只有 1 份有頂層 `seat`;`round` 都是字串(如 `r2`)。本輪這份派工單就是 `seats` 形狀:`/Users/enzo/harness/lumos-toolchain-mod-batch2/governance/review-reports/Claude-mod第二批/r2-dispatch.json`。
3. 也就是 seat-check 目前輸入的「報告 + 一份多席派工單」裡,根本沒有「這份報告是哪一席」。spec 沒有說:靠新參數 `--seat`、靠報告檔名(檔名還有 `r3-邊界-r3-sonnet.md` 這類 round 重複出現的形狀,席名有的含 round)、還是靠別的。S7/S8 兩條條款的測試輸入因此無法定義。
4. 「派工單所在資料夾名」只是慣例(`review-reports/<loop-id>/`),外家席或手動放 /tmp 的派工單不成立;而 `LUMOS-SEAT` 的 loop 段是編排者派工時自己填的 `{loop}`,沒有機械綁在資料夾名上(code 迴圈資料夾如 `code-審查席唯讀隔離`、`筆記測試綁定要存在-r4` 與 loop 編號是否一致,沒有查證)。
引句:「席位標記由派工單組成 `<派工單所在資料夾名>/<round>/<seat>`」

### F3 「標記」有兩個定義:事件帳逐行找第一個,審查席隔離只認第一個非空行;範本也還沒帶
severity: major
blocking: 是 — 兩條線合併後,事件帳會替沒被隔離的席位記標記,且兩邊改同一個函式

1. spec 的 `seat` 欄:派工詞逐行找到的第一個 `LUMOS-SEAT:` 行,並說跟派工鏡頭 hook 找標記一樣。
2. 審查席隔離分支(已在 /Users/enzo/harness/lumos-toolchain-seat-guard)定的是:整行符合 `^LUMOS-SEAT:\s*(\S+)$`、第一個非空行、值切成恰好三段、不是 `.`/`..`;標記出現在內文或程式碼區塊不算審查席,第一行像標記卻寫壞要擋。
   file: `/Users/enzo/harness/lumos-toolchain-seat-guard/mods/claude/lumos-guard/hooks/register.ts:37`
   file: `/Users/enzo/harness/lumos-toolchain-seat-guard/docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md:83`
3. 後果:派工詞內文裡夾著一行 `LUMOS-SEAT: x/y/z`(派工詞常貼被審文件或範本片段,`templates.md` 範本本身就有這種行起頭的 `LUMOS-SEAT: {loop}/{rN}/{席名}`)時,隔離外掛判「不是審查席、不擋」,事件帳卻記成那個席;seat-check 再拿它去找「那一席」讀過什麼——兩邊對「這是哪一席」說法不同。spec 說「被拒的派工也記」也沒對上:被擋的是第一行寫壞的,內文那行不會被擋。
4. 主線的 `skills/lumos-design-loop/templates.md` 目前沒有 `LUMOS-SEAT`,隔離分支的範本在四段(§1、§3、§7.6、§7.8)第一行加了標記。spec 說「哪條先上主線就由哪條加範本」——但本計劃的 S6、S7 測試依賴範本會帶標記,先上主線的若是本計劃,第 3 項上線當天事件帳 `seat` 全是 null,而 spec 沒有為這個狀態寫行為(seat-check 看到 null 該印什麼)。
5. 兩邊會改同一段程式:隔離分支已把 `register.ts` 的 `onSpawn` 改成 `spawnFields`/`spawnEvent`/`recordEvent` 三個純函式(並把發起方欄改成 `e.parentAgentId`),主線(本 spec 的基底)的 `onSpawn` 還是直接 `record(st,$,e.agentId,'spawn',{…})`。spec 要在 spawn 事件加 `seat`,在兩個版本上落點不同;隔離分支測試若用整組欄位相等比對,加欄位會轉紅。
   file: `mods/claude/lumos-ledger/hooks/register.ts:319`
引句:「派工詞逐行找到的第一個 `LUMOS-SEAT:` 行後面那串(去頭尾空白、上限 200 字、被拒的派工也記)」
建議:事件帳的 seat 欄改成只認隔離分支同一條判準(第一非空行、整行正規式),或兩邊共用一個匯出函式。

### F4 外掛清單改造:跟隔離分支同一批常數打架,市集檔與既有「只列一個外掛」測試沒列,退役清單的形狀沒定
severity: major
blocking: 是 — 市集檔多一個外掛會讓既有 S9 測試轉紅;兩條線各自改名同一組符號

1. spec 說「安裝端把單一外掛常數改成清單(`_LUMOS_PLUGINS`)」,並加退役清單。隔離分支已經做完,而且形狀比 spec 描述的大:`_LUMOS_MARKET`、`_LUMOS_PLUGINS`(元素是完整 id `lumos-ledger@lumos-toolchain`)、`_PLUGIN_RANK`(回傳取最差)、`_plugin_sync_msg(state, detail, pid)` 三參數、`_lumos_plugin_listed(src)`;主線的 `_LEDGER_PLUGIN`、`_LEDGER_MARKET`、`_LEDGER_MANUAL`、`_ledger_*` 一整組。兩邊對同一批符號各改一次,合併不是「接上」,是第二條重寫第一條的實作。
   file: `/Users/enzo/harness/lumos-toolchain-seat-guard/scripts/lumos:21887`
   file: `scripts/lumos:21921`
2. spec 的退役清單說「名字」,隔離分支清單是完整 id,沒說退役清單用哪一種;`_LEDGER_MANUAL` 的兩行手動指令是寫死 ledger 的,teardown 失敗時只附 ledger 的手動指令;`lumos teardown` 的確認清單那一行寫死「Claude 外掛 lumos-ledger 與市集 lumos-toolchain」;`_plugin_sync_msg` 的字串寫死「Claude 事件帳外掛」。這些都要跟著清單改,spec 沒列。
   file: `scripts/lumos:20033`
   file: `scripts/lumos:21955`
3. `.claude-plugin/marketplace.json` 要加 `lumos-context`。既有測試 `t_ledger_plugin_files_valid` 明確檢查「市集只列 lumos-ledger 一個外掛」(長度等於 1)。S9 的新測試沒有改它;spec 的 S10 只寫了新外掛原始碼掃描,沒提這一支要改。
   file: `scripts/test_lumos.py:71551`
4. 市集檔的家是 Systems/lumos事件帳(它的 about_code 有 `.claude-plugin/marketplace.json`,隔離分支的 lumos-guard 節點也寫「市集檔(lumos事件帳)」)。spec 的落點沒有說市集檔加一列落在哪篇;新節點 `Systems/lumos-context` 若在正文用反引號寫市集檔路徑,違反「節點只准用反引號寫自己家的檔」。
5. 回退寫「搬到已退役清單,下次 install / update 就會移除」:事件帳計劃的回退節講過 install、update、bootstrap、init 才會呼叫外掛同步;spec 沒有確認 update 會走到,也沒有寫「已退役外掛移除」遇到 `LUMOS_SKIP_CLAUDE_PLUGIN=1`、`claude` 不在時的行為(S9 只測「已裝的被移除」)。
引句:「審查席隔離分支也做了同形狀的清單,後上主線的那條接上時合併」
建議:spec 先決定哪條先上主線;後上的那條必須寫明「改用先上那條的符號」,並把市集檔、`t_ledger_plugin_files_valid`、teardown 確認清單、手動指令常數列進改動清單。

### F5 「沿用 refcheck 的抽取函式」跟「只核對 file: 形式」對不上
severity: minor
blocking: 否 — 抽取可以另外加一道過濾,不改變設計方向

1. refcheck 用的抽取是 `_node_code_ref_tokens`:抽報告裡所有行內程式碼的 `路徑:行號`、並用 repo 頂層資料夾名過濾,沒有「前面要有 `file:`」這個概念。要只核對 ``file: `路徑:行號` `` 就得自己再寫一個前綴規則,不是「沿用」。
   file: `scripts/lumos:24439`
2. 抽取函式會連引句行(引句:「…」裡若含行內程式碼)、`函式名 + 行號` 之類一併抽到;spec 說「引句不核對」,但抽取時沒有把引句行排除的步驟。
3. 路徑換成相對 repo 根的寫法時,報告引的是另一個 worktree 的絕對路徑(本輪審的就在 `…-mod-batch2` worktree,主 checkout 是另一處),spec 已說用 `git worktree list` 去前綴;但被刪掉的 worktree、`git worktree list` 取不到時,「保留絕對路徑原樣比」會把整條判成沒讀過——spec 沒說這種狀況算不判還是算列出。
引句:「引用的抽取沿用 refcheck 的抽取函式」

### F6 撤除條件 ③ 在功能運作良好時就會觸發,而且「收貨紀錄那一行」沒有任何條款或範本管
severity: minor
blocking: 否 — 不影響實作能不能做,只是撤除條件寫反

1. RETIRE-IF ③ 寫「收貨紀錄裡 `seat-check --events` 那一行連續一個月都是 0 條——第 3 項撤掉」。「0 條」的意思是列出的沒讀過的引用為 0——審查員都有讀、或放行偏寬(沒帶路徑的搜尋算整個 repo 讀過,見 F10)時都是 0;帳不完整不判時又印另一種話。連續一個月 0 條分不出「功能有效」跟「功能沒在判」。
2. 「收貨紀錄固定寫一行 `seat-check --events: N 條`」:收貨紀錄是 `r1-intake.md` 這類編排者手寫檔,沒有範本;S7、S8 條款只管指令輸出,沒有一條管這一行,也沒有改派工/收貨手冊的項目(`skills/lumos-project-notes/commands/05-設計審查迴圈.md`、`skills/lumos-design-loop/reference.md`、`skills/lumos-code-loop/reference.md` 都列了 seat-check 用法,新旗標 `--events` 與這行要同步寫進去,spec 沒列)。
引句:「③收貨紀錄裡 `seat-check --events` 那一行連續一個月都是 0 條——第 3 項撤掉」

### F7 決策與交叉引用的殘留(d1/d2 翻案對象查證結果,d3 殘留,既有 Issue 的條款編號過期)
severity: minor
blocking: 否 — 文件整理,不改設計

d1/d2 翻案對象查證:
1. d2 說推翻派工鏡頭注入計劃「開案決策裡的不驗」:對。該計劃 d1 原文是「不擋不驗不記不量」,正文「不做」第 10 點也寫「不驗證審查員有沒有讀」。但同一句裡的「不記」(不記治理帳)與 d2 的做法不衝突(事件帳不是治理帳),spec 這一句沒有交代,接手者讀舊節點會以為 d2 同時推翻了「不記」。
2. d2 說「部分推翻 seat-check 自己 repo 查證的 file: 引用一律合法」:對,出處是 `cmd_seat_check` docstring 與輸出末句「引 file:line 當證據一律算合法」;這句話寫在程式裡而不是 decisions,spec 只說在派工鏡頭計劃用 `decision-add` 記一筆,沒有要求把 `cmd_seat_check` 輸出的那句話與 docstring 同步改掉,改完會自相矛盾(輸出仍印「一律算合法」)。
   file: `scripts/lumos:23496`
3. d1「前兩項放新外掛,不放只觀察的事件帳」:跟事件帳 S9(外掛不得改變行為)一致,沒有漏翻案。

殘留:
4. d3 仍留在 frontmatter(`valid: false`),`superseded_by: "#d1"`:既有計劃的寫法是 `superseded_by: d13`(沒有 `#`),而且 d1 並沒有取代 d3(d3 講的是記憶清掃改成寫快取,不是被縮小後的範圍取代),取代對象寫錯會讓 `lumos decisions` 印出「→ #d1」誤導。
   file: `scripts/lumos:16667`
5. 既有 Issue 還指向舊編號:「條款 S2、S3」,現在對應的是 S5、S4;Issue 的「什麼條件算修好」條件需要跟著改。
   file: `docs/lumos-toolchain-knowledge/Issues/會談編號環境變數接續後停在舊值.md`
6. frontmatter 的 `lands_in` 只列 `Systems/lumos-context` 一篇,其餘四篇只在正文「落點」段;專案規範要求計劃的 `lands_in` 寫現況落在哪幾篇。
引句:`superseded_by: "#d1"`

### F8 第 2 項的核心假設(外掛程序讀得到、Bash 讀得到、接續與 /clear 後各是什麼值)沒有判準,且跟既有 Issue 的根因互相拉扯
severity: minor
blocking: 否 — spec 已規定實作前先實測,只是缺判準與失敗出路 ⚠

1. 既有 Issue 的根因寫「環境變數在 Bash 所在的 shell 啟動時就定了,接續或 /clear 時不會更新」。若 Bash 是長駐 shell,外掛後來才 `$.env.set` 的值進不了已啟動的 shell;型別檔的說法是「之後啟動的子程序才繼承」。spec 的 S4 靠「每回合都重設」,但沒說 Bash 每次是新程序還是長駐 shell ⚠(我沒辦法查證,型別檔沒寫)。
2. 外掛「當下看到的 `CLAUDE_CODE_SESSION_ID`」用 `$.env.get` 讀:這個變數是外掛行程環境裡本來就有、還是只塞給 Bash 子程序的?型別檔只保證 `$.env.get` 讀行程環境;若行程環境沒有,BASE 恆為空,S5 恆退回官方編號,功能靜默失效,不會報錯。
3. 實測步驟 ①②③④⑤ 沒有各步的通過判準:只有「①讀不到就整項停下」,②(/clear 後)與③(接續後)若仍讀到舊值、④(子會談)讀到外層值該怎麼辦,沒有寫。
4. `$.session.id()` 與逐字稿檔名是否一致(步驟 ⑤)是 `handoff` 排除自己的前提,放在實測最後一項;若不一致,改走取值函式反而讓 `handoff` 排除錯檔。
引句:「①讀不到就整項停下回報,不走別的備案」

### F9 `lumos-context` 是使用者層外掛,對所有專案生效,spec 的隱患節把它當成只影響 lumos repo
severity: minor
blocking: 否 — 可在實作時補閘或在隱患節講清楚

1. 事件帳外掛會先判斷會談所在 repo 有沒有圖譜(`vaultIn`),沒有就不寫。`lumos-context` 的 S1–S4 沒有任何這種判斷:在任何專案、任何子代理壓縮時都附「計劃節點與步驟、審查席」這類 lumos 專用要求,每回合都設兩個環境變數。
   file: `mods/claude/lumos-ledger/hooks/register.ts:58`
2. 隱患節寫「已排除:不可逆:外掛只附加摘要指示文字、設兩個環境變數,不寫檔;拿掉外掛即回到現狀」。附加的摘要指示會留在被壓縮後的對話裡(逐字保留要求本身)——拿掉外掛不會把已經壓縮進去的結果還原;對沒用 lumos 的專案也一樣。屬輕微,但「回到現狀」字面不準。
3. 手動 `/compact <文字>` 的使用者指示:spec 說接在後面;若使用者指示本身很長(超過摘要器能吃的長度)沒有處理。⚠(沒找到型別檔對 instructions 長度的規定)
引句:「已排除:不可逆:外掛只附加摘要指示文字、設兩個環境變數,不寫檔;拿掉外掛即回到現狀」

### F10 `seat-check --events` 的放行規則實際上會放行幾乎全部,且幾個帳面狀態沒定義
severity: minor
blocking: 否 — spec 已承認放行偏寬並另印條數,以下是沒寫到的狀態

1. 「沒帶路徑的 Grep/Glob 算整個 repo 都搜過」:審查員的 Grep 絕大多數不帶 `path`。事件帳(`toolExtra`)只記 `file_path`、`path`、`notebook_path`,不記 Grep 的 `glob`、Glob 的 `pattern`(Glob 把絕對目錄寫在 `pattern` 裡時,記錄看起來就是「沒帶路徑」)。結果是:只要審查員做過一次不帶 path 的搜尋,所有引用都算「讀過」,「只靠搜尋根目錄才算讀過的條數」會吃掉絕大部分。我這台機器沒有事件帳資料可以量比例(`governance/runtime/events/` 不存在)⚠,spec 也沒有先量。
   file: `mods/claude/lumos-ledger/hooks/register.ts:80`
2. 沒定義的帳面狀態:(a)最後一筆同標記的 spawn 是被拒的(`denied`,`child` 為空)——spec 的「找不到那一席」不涵蓋「找到了但沒子代理」;(b)審查席再派的孫代理做的讀取(隔離分支允許審查席再派一般子代理),spec 只沿 `child` 找一層;(c)`--events` 要編排者自己給會談編號,但編排者在 `/clear`、接續後會談編號會換(正是第 2 項要解的事),spawn 事件在舊會談資料夾裡,seat-check 會判「找不到那一席」且沒說該去哪個會談找;`LUMOS_SESSION_ID` 沒有被定為 `--events` 的預設值。
引句:「沒帶路徑的 Grep/Glob 算整個 repo 都搜過」

## 其他核對(無 finding)

- 事件帳 S9 的 banned 清單(`next\(\{` 等)只掃 lumos-ledger,新外掛要用 `next({...e, instructions})` 不衝突。
- 落點四篇的 about_code:lumos-cli-lifecycle、lumos-cli-read、design-loop 都有 `scripts/lumos`,lumos事件帳有 register.ts、ledger.test.ts、marketplace.json;家的歸屬成立(缺口只在 F1 的 enforcement 列與 F4 的市集檔)。
- `handoff` 是唯一用 `CLAUDE_CODE_SESSION_ID` 的地方:對(`scripts/lumos:46262`;另一處只在測試 `scripts/test_lumos.py:43003`)。
- 計劃對 `lumos-guard` 的引用(另一條分支停在代碼審第二輪)與隔離分支實況相符。

總結:最嚴重 major,blocking 4 條
