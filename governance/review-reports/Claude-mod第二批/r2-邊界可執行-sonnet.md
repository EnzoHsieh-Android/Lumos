severity: major

審查範圍:凍結快照 /tmp/Claude-mod第二批-r2.md。假設實查力氣放語意:事件帳寫入端、讀取端、refcheck 抽取函式、install 外掛段、enforcement 事件帳列、dispatch 檔實際形狀、外掛型別檔。

### F1 工作目錄前綴剝除沒有路徑邊界,本 repo 的兩個工作目錄就會互相咬
severity: major
blocking: 是 — 路徑正規化是 S7 判讀的第一步,錯了會系統性誤判「沒讀過」或誤放行。

引句:「絕對路徑去掉這個 repo 任一工作目錄(`git worktree list`)的前綴;換不了的保留絕對路徑原樣比。」

1. 本機兩個工作目錄是 `/Users/enzo/harness/lumos-toolchain` 與 `/Users/enzo/harness/lumos-toolchain-mod-batch2`,前者是後者的字串前綴。
2. 照字面做字串前綴剝除:若先試主工作目錄,`/Users/enzo/harness/lumos-toolchain-mod-batch2/scripts/lumos` 會變成 `-mod-batch2/scripts/lumos`,既不等於 `scripts/lumos`,也不是絕對路徑,後面的「換不了的保留原樣」不會觸發。席位明明 Read 過,卻被列成沒讀過。
3. 條文沒規定:要以 `/` 為界(path component)比對、要取最長前綴;也沒規定 `.`、`./x`、結尾 `/`、`..` 的處理。Grep 的 path 填 `.` 或 repo 根會剝成空字串,是否算「上層目錄」未定。
4. macOS 的 `git worktree list` 吐實際路徑(`/private/tmp/...`),而模型寫的可能是 `/tmp/...`;`/var` 對 `/private/var` 同理。前綴比對對不上,又落入「保留絕對路徑」而永遠對不到相對路徑的 file: 引用。
5. 多個工作目錄的同名檔(spec 說算同一支)是刻意放寬,但條文沒明講這會把「讀了 A 工作樹的 scripts/lumos」當成讀了 B 工作樹那版。引的行號可能是另一版的內容。放行偏寬請在輸出一併印出。

### F2 抽取函式不認 `file:`,也會把絕對路徑靜默丟掉;S7 條文與 RETIRE-IF 因此失真
severity: major
blocking: 是 — 條文描述的行為(只核 file: 引用、保留絕對路徑原樣比)用指定的函式做不出來,而且零條會被當成「沒問題」。

引句:「`file:` 引用的抽取沿用 refcheck 的抽取函式。」
引句:「只核對報告裡 ``file: `路徑:行號` `` 形式的引用,而且只核對不在圖譜資料夾底下的檔」

1. `_node_code_ref_tokens` 只抽反引號內的字串,看不到反引號外的 `file:`。結果是任何散文裡包反引號的路徑(如 `scripts/lumos`、`lumos show` 之類)都會被當引用核對,而不是只核 `file:` 形式。要限定 `file:` 前綴,得另寫抽取。
2. 同一函式在頂層目錄過濾處把不屬於 repo 頂層目錄的路徑丟掉,絕對路徑第一段是空字串必然不在其中,被靜默略過。file: `scripts/lumos:24499`
3. 本專案的審查席常寫絕對路徑(這份派工單自己就要求審材外佐證寫 `路徑:行號`,型別檔在 /private/tmp 下)。絕對路徑一律被丟,抽到 0 條,輸出「0 條」。
4. 後果一:條文「換不了的保留絕對路徑原樣比」是死條文,永遠進不去。後果二:RETIRE-IF ③「seat-check --events 那一行連續一個月都是 0 條——第 3 項撤掉」會因為抽取靜默丟路徑而誤觸發撤掉。0 條無法區分「席位沒引用」與「引用全被丟掉」。
5. 同一函式也丟 `.github/...`、`.claude/...` 這類點開頭資料夾(top_dirs 排除點開頭),也不收含 `*<>?` 的字串。
6. 建議實作者先列一個「輸出 N 條」之外還要印「抽取略過幾條」的欄位,否則第 3 項的「條數」沒意義。

### F3 失敗或被拒的 Read 也算「讀過」,正好漏掉這項要抓的憑印象引用
severity: major
blocking: 是 — 條文字面讓目標缺陷(席位憑印象引用不存在或沒讀的檔)通過檢查。

引句:「判「讀過」:那個子代理對同一檔有 Read;」

1. 事件帳每筆 tool 事件記 `ok` 與 `denied`;Read 一個不存在的路徑會 `isError`,事件仍帶 `paths`。file: `mods/claude/lumos-ledger/hooks/register.ts:71`
2. 場景:席位幻想出 `scripts/lumos_foo.py`,Read 失敗(ok:false),報告仍照樣引 `scripts/lumos_foo.py:12`。條文只看「有 Read」,判讀過,放行。
3. 審查席隔離分支若拒絕某些 Read(denied:true),同樣會被算讀過。
4. 條文應明寫只算 `ok:true 且 denied:false` 的事件,Bash 與搜尋也一樣。S7 的測試要有這兩個案例。
5. 另:Read 的 offset/limit 沒記,讀第 1 到 50 行就能「讀過」引用第 4000 行的檔。這是只能做到檔級的天花板,請寫進放行偏寬的聲明。

### F4 席位標記的組成鍵與真實的派工單形狀對不起來
severity: major
blocking: 是 — 實作者照字面組不出一個能跟 spawn 的 seat 欄比對的值。

引句:「席位標記由派工單組成 `<派工單所在資料夾名>/<round>/<seat>`」

1. 既有 `cmd_seat_check` 讀的派工單是單席形狀:頂層 `round`、`seat`、`materials`。file: `scripts/lumos:23523`
2. repo 內真實的 rN-dispatch.json 有三種形狀(單席檔、`seats` 陣列、頂層 list),而且很多席的鍵是 `auditor` 而非 `seat`(例如 governance/review-reports/筆記測試綁定要存在-r4/r1-dispatch.json 的 seats 只有 auditor,沒有 seat)。對 seats 陣列檔,`disp.get("seat")` 是 None,組出 `資料夾/r1/None`。
3. 「派工單所在資料夾名」未必等於派工詞裡 `LUMOS-SEAT:` 第一段(這次派工是 `Claude-mod第二批`,而卷證資料夾是 governance/review-reports/<loop-id>,loop 欄還可能帶 `-r4` 之類尾碼)。條文沒定誰是正本、如何容錯。
4. `round` 在真實檔是字串 `"r1"`,條文組成已經含 `r`?範本若寫 `r2` 而檔裡是 `2`,雙 `r`。
5. 外家席判定:條文說「外家席(Codex)一律印外家席不適用」,但沒說用什麼判。已有 `_roster_family(auditor)`;沒指定,而且與 S8「找不到那一席」誰先判也沒定。Codex 席找不到會被當帳不完整而不是不適用。file: `scripts/lumos:11909`
6. 實作前請先決定:席位標記由 lumos 產生(例如 `lumos loop next` 直接吐出完整標記)並寫進派工單欄位,seat-check 直接讀該欄位比對,不要靠三段字串拼。

### F5 enforcement 列要逐支列出「有沒有裝上」,與既有「不呼叫外部指令、開場每次都跑」的約束衝突
severity: major
blocking: 是 — 條文要的資訊本機端沒有不叫外部指令就能拿到的來源。

引句:「`lumos enforcement` 既有的事件帳外掛那一列,改成逐支列出外掛清單裡的外掛有沒有裝上」

1. 現行第 ⑪ 列只看事件帳資料夾的修改時間,明講「不呼叫任何外部指令」,且註解說明 enforcement 每次開場都跑、git 要限 3 秒。file: `scripts/lumos:24155`
2. 判「外掛有沒有裝」只能呼叫 `claude plugin list --json`;安裝端同函式的逾時是 30 秒。file: `scripts/lumos:21985`
3. `lumos-context` 只附摘要指示與設環境變數,不寫任何檔,沒有像事件帳那樣可看的落地痕跡,列只能靠叫 claude。
4. 開場每次叫一次 claude 子行程,最壞多等 30 秒;或者把「裝了沒」降成 unknown,那就不達成條文目的。沒有條款綁這一列,卻在做法要點裡寫了改法。
5. 另:狀態詞彙目前只有 active/stale/unknown,「沒裝」要用哪一個沒定;開場提醒只點名 inactive、degraded,沒裝若用 unknown 則永遠不提醒,與「lumos-context 沒裝時看得到」矛盾。

### F6 市集清單與外掛骨架檔沒列入落點,S9 的測試可以綠而實際裝不起來
severity: major
blocking: 是 — install 對市集裡不存在的外掛名會失敗,而 spec 的落點與條款都沒涵蓋。

1. 現況 `.claude-plugin/marketplace.json` 的 plugins 只有 lumos-ledger。新外掛要在這裡加一筆 `lumos-context`(source 指 `./mods/claude/lumos-context`),且 `mods/claude/lumos-context/hooks/hooks.json`、`tsconfig.json`、`register` 檔都要有。落點節、做法要點、條款都沒提。
2. S9 只綁 `lumos install` 對清單每支「各自裝上與移除」,測試若 mock `claude`,就看不出市集清單缺 `lumos-context`。
3. S10 的結構測試只掃原始碼的 `$.env.set` 數,沒檢查市集與 hooks.json 一致。
4. 要有一條機械檢查:`_LUMOS_PLUGINS` 每支都在 marketplace.json 且對應資料夾含 hooks.json;已退役清單每支都不在 marketplace.json。

### F7 外掛清單與已退役清單的邊界沒定:同名、完整 id、部分失敗、市集移除時機
severity: minor
blocking: 否 — 都是可在實作時補的規則,但目前條文沒擋住。

引句:「在裡面的名字已裝就移除。」

1. 現行常數是完整 id `lumos-ledger@lumos-toolchain`,比對用 `x.get("id")`。已退役清單若寫的是「名字」,使用者自己從別的市集裝的同名外掛會被誤移除。清單應存完整 id。file: `scripts/lumos:21987`
2. 同名同時在現役與已退役清單時,條文沒定:裝了又移除,每次 install 都抖一次。應有守衛測試:兩清單不得相交。
3. 現行 `_sync_claude_plugin` 回單一狀態 ok/absent/no-source/failed。清單版第一支裝成、第二支失敗時,回什麼?uninstall 市集要在所有外掛都移完才移,否則留下的外掛成孤兒。條文沒定。
4. 空清單、已退役清單為空(第一版就是空)要有案例。

### F8 「帳不完整就不判」的條件漏了讀取端自己會略過的塊,可能誣賴席位
severity: major
blocking: 是 — spec 自己宣稱「不會用缺帳去誣賴席位」,條件清單卻漏了讀取端會靜默略過的資料。

引句:「帳不完整就不判,只說原因:找不到那一席、那個子代理沒有 `turn_end`(還沒跑完或還沒落盤)、那個會談的帳有寫入錯誤或壞行。」

1. `_events_read` 會略過超過 16MB 的塊檔(回傳 `too_big`)與版本不是 1 的行(`unknown_version`),只計數不報錯。file: `scripts/lumos:23685`
2. 場景:一個大會談的某塊超限被略過,但另一塊裡有子代理 turn_end,便判成完整;被略過的塊裡的 Read 不見了,席位的合法引用被列成沒讀過。
3. 條文應把 `too_big`、`unknown_version`、`bad` 任一非零都納入不判。
4. 反過來,「壞行」是整個會談範圍:任何一行壞(例如更早一個無關席位留下的)讓這個會談所有席位永遠不判。粒度太粗但保守;請至少在輸出說壞行數,讓收貨人決定。

### F9 `--events <會談編號>` 沒有預設與跨會談規則
severity: minor
blocking: 否 — 只影響可用性,輸出會說明找不到。

1. 審查常跨 `/clear`、接續、隔天;spawn 事件寫在派工當時的會談資料夾,收貨時 `$.session.id()` 已不同。條文只能手填編號,找錯就印「找不到那一席」,與真的缺帳無法區分。
2. 沒有說省略時是否用 S5 的取值函式預設,也沒說找不到時是否列出最近會談(`lumos events` 已有列表函式)。
3. 編號驗證:讀取端有 `_EVENTS_SESSION_RE`,空字串、含 `/`、`..` 都該擋下;條文沒說 `--events` 走同一道。file: `scripts/lumos:23654`

### F10 會談編號取值:BASE 來源與併發的安全宣稱都沒有實測依據
severity: minor
blocking: 否 — 實作前實測步驟能補;但目前條文把成立當前提。

引句:「S5 的 BASE 比對在這種情況會退回官方編號(官方編號在同一行程也相同時才會錯)」

1. S4 要外掛「當下看到的 CLAUDE_CODE_SESSION_ID」,即外掛端 `$.env.get`。外掛行程環境有沒有這個變數沒驗過;實測步驟 ① 到 ⑤ 只印 Bash 端的值。若外掛端讀到 undefined,`$.env.set(name, undefined)` 是取消設定,於是 BASE 永遠空、S5 永遠退回官方編號,整項靜默失效且沒有任何紅燈。實測步驟應明列「BASE 非空」為通過條件。
2. 併發段的推論自相矛盾:`$.env.set` 是行程層級,同一行程服務兩個會談時,兩者 BASE 相同,A 的 Bash 讀到 B 寫的 ID 且 BASE 相等,S5 會採用錯的值。條文宣稱會退回官方編號,只在 Bash 子行程的官方編號與 BASE 不同時成立,這個前提沒驗。
3. 正規化:`LUMOS_SESSION_ID` 只要「不空」,純空白字串算非空會被採用;建議 strip 後再過 `_EVENTS_SESSION_RE`,不合就退回。
4. 兩個變數先後 set,中間若被打斷會留下新 ID 配舊 BASE;順序與是否一次設完沒規定。

### F11 spawn 與搜尋判讀的邊角
severity: minor
blocking: 否 — 各自是放行偏寬或報不準,提醒不擋,可接受但應寫進條文。

1. 同一席重派:條文「取最後一筆」。若最後一筆是被拒的派工(`deny`,child 為 null),就會蓋掉前一筆成功的派工,判成找不到那一席。應取最後一筆有 child 的。
2. 子代理再派子代理:`onSpawn` 記的是 `e.agentId`,但 `AgentSpawnInput` 只有 `parentAgentId`,所以 spawn 事件的 agent 欄恆為 null,也記不出誰派的。席位再派的讀檔小幫手所讀的檔不算席位讀過,報告引它的檔會被列沒讀過。條文只沿 `child` 一層,沒說遞迴或不遞迴。file: `mods/claude/lumos-ledger/hooks/register.ts:320`
3. Bash 判讀「前 500 字出現該檔路徑」是子字串比對:`scripts/lumos` 會命中 `scripts/lumos-hooks/x`、`scripts/lumos.py`;命令被截在 500 字,超過的不算。應要求路徑後接空白、引號、結尾或 `:`。
4. 沒帶路徑的 Grep 算整個 repo:Grep 預設只回檔名清單,沒帶 path 但帶 `glob`/`type` 限縮時也算全搜;子代理 cwd 在 repo 外(例如 /tmp 的 seat-work)時「整個 repo」不成立。事件帳每筆只記 `paths`,Glob 的 pattern 與 Grep 的 glob 沒記,所以無法判斷。建議無路徑時只在子代理 cwd 在 repo 內才算。
5. 實務上每席幾乎都會 Grep 一次,這條會讓幾乎所有引用都過,輸出另印「只靠搜尋根目錄」條數是對的;請把該數字同時當第 3 項有沒有在幹活的指標。

### F12 S1 附加段的接續規則與重複判斷未定
severity: minor
blocking: 否 — 實作時能補,但兩種實作會彼此不一致。

引句:「指示裡已有這一行就不重附。」

1. 「已有這一行」是整行比對還是子字串?使用者的 `/compact` 文字若在句中引用標記,子字串會誤判已有。
2. 接在原指示後的分隔未定:原指示不以換行結尾時,直接接上會讓標記不在行首,下一次判斷(整行比對)漏判而重附。
3. 空字串、純空白、undefined 的原指示:前導空行與否沒定。
4. 子代理精簡版的標記行是否同一行(同一個 v1)沒定;若相同,主對話指示被帶進子代理時精簡版會被視為已有而不附。

### 逐節
- 範圍第 1、2 項:見 F10、F12。
- 範圍第 3 項:F1 至 F4、F8、F9、F11。
- 做法要點:F5、F6、F7。
- 條款 S1 至 S3:F12;S4、S5:F10;S6:見 F4 第 1 與 5 點、F11 第 2 點;S7:F1 至 F3;S8:F8;S9:F6、F7;S10:S10 要掃 `$.env.set` 只有兩個,但 S4 還要 `$.env.get("CLAUDE_CODE_SESSION_ID")`,條文沒說允許,實作者可能誤刪(併入 F10 第 1 點)。
- 回退、實務隱患:已讀,無獨立 finding(併發段見 F10)。
- 事件帳讀取端大小:`_events_read` 對單檔 16MB、單行 64KB、巢狀深度 32 都有上限,第 3 項「讀一個會談的事件帳」在大帳下記憶體以全部事件進 list;一般規模沒問題,已讀,無 finding。
- 牽連節點:派工尾端沒有 hook 附上牽連節點,不適用。

總結:最嚴重 major,blocking 7 條
