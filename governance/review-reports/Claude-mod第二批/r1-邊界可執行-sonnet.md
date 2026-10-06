severity: major

# Claude-mod第二批 r1 邊界可執行席(sonnet)

派工尾端沒有 hook 附上的牽連節點,故無逐條判斷。已讀:front matter 與決策 d1~d3、範圍 1~5、做法要點、條款 S1~S9、回退、實務隱患。文件內交叉引用的節點(Systems/lumos事件帳、design-loop、記憶過期清掃、改檔前推播、lumos-cli-lifecycle、Projects/派工鏡頭注入_計劃)都存在;「handoff 是唯一讀 CLAUDE_CODE_SESSION_ID 的地方」屬實。

## 範圍 1(S1)

### F1
severity: minor
   blocking: 否 — 實作者可自行補決定,不會做出錯的東西
   - 「三種觸發都附,含預先計算 `precompute`」:型別檔 SessionCompactTrigger 有四種(manual、auto、plugin、precompute),「三種」是哪三種沒寫;plugin(別的外掛呼叫 `$.session.compact`)附不附,實作者要猜。
   - 「已附過就不重附」沒說怎麼判:若比對整段固定文字,`/compact` 使用者原指示自己含這段文字就被判已附;若 precompute 先附、之後 manual 帶新指示,兩次的 `instructions` 不同,但 precompute 結果被沿用時真正生效的是前一份指示。
   - 子代理附精簡版:`agentId` 也會是引擎自己的分支(型別檔說明壓縮、記憶的分支帶不在清單裡的 id),這些也會被附「保留審查席、計劃節點」。
   file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:10313`
   引句:「當對話壓縮(`session.compact`)時,外掛應在摘要指示後附上交棒要求段;原本有指示時接在後面、原文不變;子代理附精簡版」

## 範圍 2(S2、S3)

### F2
severity: minor
   blocking: 否 — 補一句「非空才採用、並驗格式」即可
   重現:S3 若實作成 `os.environ.get("LUMOS_SESSION_ID", os.environ.get("CLAUDE_CODE_SESSION_ID"))`,外掛在會談編號為空時 `$.env.set("LUMOS_SESSION_ID", "")`(或編號帶不合規字元)會讓 get 回空字串、不退回後備;既有 `_handoff_find_transcript` 寫法是 `me and p.stem == me`,空值就等於沒排除自己。另一條路:`LUMOS_SESSION_ID` 會被子行程繼承——編排者在 Bash 裡開 `claude -p`(本 repo 的 headless 探針)而子會談沒載入 `lumos-context`(`--bare`、設定目錄不同、外掛沒裝),子會談的 handoff 讀到父會談的編號、排除錯的逐字稿,正是這項要修的毛病又回來,而且比舊行為更隱蔽(舊值至少是自己會談的接續前編號)。條款 S3 只說「先讀 LUMOS_SESSION_ID」,沒有非空、格式、與 `CLAUDE_CODE_SESSION_ID` 衝突時的處理。
   file: `scripts/lumos:46262`(`me = os.environ.get("CLAUDE_CODE_SESSION_ID", "")`)
   引句:「當 lumos 需要會談編號時,應先讀 `LUMOS_SESSION_ID`,沒有才讀 `CLAUDE_CODE_SESSION_ID`」

### F3
severity: minor
   blocking: 否 — 備案才會走到,實測後才定
   「改成外掛把編號寫進以 `CLAUDE_PID` 為名的小檔」:小檔放哪、誰清、`CLAUDE_PID` 在 lumos 的環境裡是否讀得到(Bash 子行程不一定繼承)、pid 被作業系統重用時舊檔被新的 claude 讀成自己的,全沒寫。⚠ 只在備案觸發才成立,判不準是否會用到。
   引句:「讀不到就改成外掛把編號寫進以 `CLAUDE_PID` 為名的小檔(`CLAUDE_PID` 在接續後不變),lumos 讀檔」

## 範圍 3(S4、S5)

### F4
severity: major
   blocking: 是 — 事件帳在 seat-check 跑的當下常常還沒寫到磁碟,「從沒讀過」會系統性誤報
   重現:外掛的 `add` 只進記憶體緩衝,滿 50 筆(`FLUSH_AT`)或主會談 `turn.complete`(`onTurnEnd` → `flushSession`)才寫檔。編排者收到席報告後,在**同一個回合**用 Bash 跑 `lumos seat-check --events`:此時席最後不到 50 次工具呼叫(正是席最近讀的檔)還在緩衝裡,磁碟上沒有。結果:那幾個檔被列成「席位從沒讀過」。條款只有「事件帳找不到那一席時說清楚」,沒處理「找得到但不完整」。同類:`ledger_error`(寫失敗、路徑含符號連結)、`dropped`(緩衝超過 500 筆丟最舊)、`session.end` 只用快取位置判定而放棄、讀取端 `_EVENTS_MAX_FILE` 16MB 整檔跳過、單行超過 64KB 當壞行略過。這些都會讓「讀過」的證據消失,而寬口徑只保護「有證據就算讀過」那一邊。實作者照字面做會對任何有缺帳的席印假警告;至少要讀到 ledger_error / 壞行 / too_big 就把整份結果降級標「帳不完整」,並且文件要寫 flush 時機(例如收貨流程先等到回合結束,或 seat-check 提醒「可能還沒落盤」)。
   file: `mods/claude/lumos-ledger/hooks/register.ts:231`
   file: `mods/claude/lumos-ledger/hooks/register.ts:315`
   file: `scripts/lumos:23694`
   引句:「事件帳找不到那一席時說清楚、不擋」

### F5
severity: major
   blocking: 是 — 條款 S4 的核心判定(引句所在檔)沒有可執行的定義
   重現:報告寫 引句:「…」(例如引自凍結快照 /tmp 下的 spec,或 repo 內任一檔)。既有 `_quote_rows` 需要呼叫端先給一份 `stext`(單一檔文字),`seat-check` 現有實作靠派工單 materials 提供檔案清單。新條款說「引句所在檔」,但沒說到哪裡找:(a) 掃整個 repo?`scripts/lumos` 單檔近 5 萬行,governance 下有大量事件帳與重播檔,同一句話常同時出現在筆記、帳本、快取;(b) 只掃席讀過的檔?那「從沒讀過」永遠不成立(定義上找得到的都讀過);(c) 引句出自 repo 外(/tmp 快照、型別檔)怎麼找?引句同時出現在多個檔時是「任一檔讀過就不列」還是「全部都沒讀才列」?沒寫。`file:` 引用有同樣問題:行號超出檔案長度(捏造的行號)是最直接的偽造證據,卻只靠事件帳判定,沒有檢查。
   引句:「抽報告裡 ``file: `路徑:行號` ``(新寫一套抽取;既有的只抽引句)與引句所在檔,列出席位從沒讀過的」

### F6
severity: major
   blocking: 是 — 路徑比對規則缺,實作者會寫出大量誤判或誤放
   重現:事件帳 `paths` 存的是工具參數字面值(Read 通常是絕對路徑),`cmd` 是 Bash 指令前 500 字,事件**沒有存 cwd**(`base()` 只有 `worktree`,主 checkout 時為 null)。報告引用是 `scripts/lumos:46257` 這類相對路徑。要比對必須有:(a) 相對路徑相對於誰(席的 cwd 在本專案常常是主 checkout,而審的是 `-mod-batch2` 這種 worktree;兩邊同名檔內容不同);(b) Bash 指令裡 `cat scripts/lumos` 是相對、`cat "/Users/enzo/harness/…/my file.md"` 帶空白或中文;(c) 後綴比對會讓 `register.ts`、`README.md`、`lumos`(`scripts/lumos` vs `mods/.../lumos`)撞名;(d) 「沒帶路徑就算會談工作目錄底下全部」要的 cwd 事件裡根本沒有。條款需要的資料(cwd)在條款 S5 欄位清單之外,也沒列入「不記其他內容」的例外。
   file: `mods/claude/lumos-ledger/hooks/register.ts:252`
   file: `mods/claude/lumos-ledger/hooks/register.ts:107`
   引句:「同一檔有任何一次 Read、或在某次 Grep/Glob 的搜尋根目錄底下(沒帶路徑就算會談工作目錄底下全部)、或出現在 Bash 指令前 500 字裡,就算讀過」

### F7
severity: major
   blocking: 否 — 設計已承認寧可漏報,但要寫清楚代價,否則 S4 對主要威脅等於關掉
   重現:審查席幾乎都會做至少一次不帶路徑的 Grep(「沒帶路徑就算會談工作目錄底下全部」),此後 cwd 底下每個檔都算「讀過」;席憑印象引用 `scripts/lumos:99999` 這種沒開過的檔,完全不會被列。d2 要抓的正是「席位偽造或憑印象引用」。建議至少:Grep 只在 `output_mode` 回內容或有帶具體 path 時算數,或另列「只靠搜尋根目錄放行」的數量讓收貨人看得到放行有多寬。⚠ 這是設計取捨,判不準是否算 blocker,故標否。
   引句:「寧可漏報不誤報;那一席有 Bash 指令被截斷時,結果標「可能誤報」」

### F8
severity: minor
   blocking: 否 — 條款可補
   重現(S5/S4 的席位標記):
   - spec 寫「派工詞第一行的席位標記」,既有 `dispatch-lens-hook.py` 的 `find_marker` 是逐行掃、每行先 strip 才比對,派工詞標記不在第一行(前面有空行或別的前綴)在該 hook 認得、在本項認不得,得到 null。
   - 沒寫標記長度上限:`cmd` 有 `slice(0,500)`,標記沒有;第一行若是上萬字的單行派工詞,事件行超過讀取端 64KB(`_EVENTS_MAX_LINE`)被當壞行丟棄,整筆 spawn 事件消失,seat-check 找不到那一席。
   - 重複標記:同一席被重派(r1 失敗重跑、同名 r1)時 spawn 有兩筆同標記,「用席位標記找到那一席的子代理」取哪一個沒寫;取聯集會讓前一次讀過的檔替後一次掩護。
   - 「有沒有派工鏡頭附加段」:鏡頭 hook 失敗路徑也會附 `LUMOS-LENS:這次沒附固定席節點…` 的說明段,依「有附加文字」判定會把「沒附到節點」記成「有」。需區分有節點 / 只有失敗說明 / 沒有。
   file: `scripts/hooks/claude/dispatch-lens-hook.py:146`
   file: `scripts/hooks/claude/dispatch-lens-hook.py:39`
   file: `scripts/lumos:23709`
   引句:「事件帳的 spawn 事件加記派工詞第一行的席位標記(`LUMOS-SEAT:` 後面那串)、有沒有派工鏡頭附加段、派工詞長度,不記其他內容」

### F9
severity: minor
   blocking: 否 — `seat-check` 簽章與標記來源要補一句
   現有 `cmd_seat_check(report, dispatch, ledger=None, ...)` 的 `dispatch` 是 JSON(round、seat、materials、lens),沒有標記字串。新旗標 `--events <會談編號>` 要靠標記找席,標記從 dispatch 的哪個欄位、怎麼組(`Claude-mod第二批/r1/邊界可執行-sonnet` 是計劃名/輪/席名模型)沒寫;`--events` 的會談編號給錯(接續或 `/clear` 後事件帳在舊編號資料夾,收貨在新編號)時只有「找不到」。與既有「vacuous 豁免」(materials 為空直接收工)的先後也沒寫:`--events` 在 materials 為空時跑不跑?
   file: `scripts/lumos:23490`
   引句:「`lumos seat-check` 加 `--events <會談編號>`(既有的 `--ledger` 是越界帳,不共用),用席位標記找到那一席的子代理」

## 範圍 4(S6)

### F10
severity: major
    blocking: 是 — 照字面改 matcher 會同時弄壞 Codex 與升級後的 Claude 註冊
    重現 A(Codex):`_codex_entries` 用 `e.get("matcher") == "Edit|Write|MultiEdit"`(精確字串)才把 matcher 換成 `apply_patch`。把 Claude 的 matcher 改成 `Edit|Write|MultiEdit|Bash` 後這個比對不成立,Codex 註冊表拿到 `Edit|Write|MultiEdit|Bash`,`apply_patch` 不再命中,Codex 的改檔前推筆記整個停擺;「Codex 那邊不動」反而動了。
    重現 B(升級):`_equivalent` 比 matcher 字串,新舊 matcher 不同就判為不同 entry;已裝使用者跑 `lumos install` 時舊的 `Edit|Write|MultiEdit` entry 保留、新增一條含 Bash 的,之後每次 Edit/Write 兩條都命中,impact-hook 跑兩次(第二次 TTL 冷卻窗已被第一次標記,走 `--incidents-only` 但仍多一次行程與一次注入)。自癒去重也不會清,因為 matcher 不同。
    spec 提到「連同安裝端把觸發條件…加上 Bash」,沒提這兩處也沒提遷移。
    file: `scripts/merge-claude-settings.py:271`
    file: `scripts/merge-claude-settings.py:324`
    file: `scripts/merge-claude-settings.py:212`
    引句:「連同安裝端把觸發條件從 `Edit|Write|MultiEdit` 加上 `Bash`,讓它也認 Bash」

### F11
severity: major
    blocking: 是 — 「寫檔形狀」的判法沒有可實作的邊界,實作者會寫出兩邊都錯的正則
    `impact-hook.py` 的 `main()` 現在以 `tool_name not in EDIT_TOOLS` 提早返回,`extract_paths` 只吃 `tool_input.file_path` 或 apply_patch 的 patch;Bash 的 `tool_input.command` 沒有任何解析器可沿用,spec 沒說用 `shlex` 還是正則。字面清單下的具體輸入:
    - 假陽性(讀的指令被當寫):`grep -E "a>b" f.py`、`awk '$1 > 5' f.py`、`python3 -c "print(1>0)"`、`echo "a -> b.py"`、`[ $n -gt 3 ]`、`2>&1`、`>/dev/null`、`>&2`;heredoc 本體裡的 `>`、`tee`、`cp`(寫腳本的 `cat > run.sh <<'EOF' … tee x.py … EOF` 本體會被當指令掃)。
    - 假陰性:`sed -i '' 's/a/b/' f.py`(macOS 的 BSD 形式,第一個非旗標參數是空字串 `''`,不是檔名)、`sed -i.bak`、`sed -i -e … f1 f2`(多檔)、`cp -t dest src`、`cp a.py dir/`(目的端是目錄,實際寫入 `dir/a.py`;`_decide_one` 對沒副檔名路徑只在是檔案且有 shebang 時才放行)、`mv a.py b.py`(來源檔被改名也是改動)、`> "$OUT/x.py"`、`> ~/x.py`、路徑含空白或中文(`> "我的 檔.py"`)、`install`、`dd of=`、`git checkout -- f.py`、`git apply`、`perl -pi`、`python -c "open('f.py','w')"` 全不在清單。
    - 相對路徑:`cd sub && echo x > a.py`,hook 以 `repo`(`CLAUDE_PROJECT_DIR`)為底解析相對路徑(`_impact_for_file`),解成 `<repo>/a.py` 而非 `<repo>/sub/a.py`,查一個不存在的檔、TTL 標記也記在錯的絕對路徑上。
    - 命令長度:`extract_delta_text` 有 2MB 上限,路徑抽取沒有;一個 5MB 的 heredoc 寫檔指令整份丟給掃描器。
    - 「只用路徑當查詢詞」:`extract_delta_text`/`extract_delta_query` 對 Bash 回空字串,以內容觸發(`delta_text`)的規則對 Bash 寫檔全部不會觸發,事故比對只剩路徑層;條款 S6 說「跟 Edit/Write 同一套」,實際少了這一半,應寫明。
    條款 S6 的測試名 `t_impact_hook_bash_writes` 只能綁一組代表輸入,沒說哪些形狀必須過、哪些必須不誤報。
    file: `scripts/hooks/claude/impact-hook.py:777`
    file: `scripts/hooks/claude/impact-hook.py:84`
    file: `scripts/hooks/claude/impact-hook.py:833`
    引句:「指令裡有寫檔形狀(`>`、`>>`、`tee`、`sed -i`、`cp`/`mv` 的目的端、heredoc 寫檔)時,對目的路徑做同樣的推送」

### F12
severity: major
    blocking: 否 — 數字可以實作時量,但量的對象與副作用要改寫,否則量出的數字低估
    spec 把代價寫成「不帶寫檔形狀的 Bash 多付一次 Python 啟動」。實際 `impact-hook.py` 是包在 `_hookevent.guard` 裡:`guard` 每次先 `git rev-parse --show-toplevel`(最多 3 秒)、`main()` 提早返回後仍 `record(...ok)`,對 `governance/runtime/hook-events.jsonl` 追加一行,檔案過 512KB 就整檔讀進記憶體、砍一半、重寫。掛上 Bash 後,每個 Bash 呼叫(含純讀)都付 Python 啟動 + 一次 git + 一次追加寫,而且「ok 事件」被灌滿:`lumos enforcement` 把「最近有沒有真的跑過」當活著證據,Bash 灌帳會讓「近期跑過 N 次」失去鑑別力。還有並行:同一回合多個 Bash 並行工具呼叫會同時追加與修剪同一檔。回退一節也沒寫這條。
    file: `scripts/hooks/claude/_hookevent.py:127`
    file: `scripts/hooks/claude/impact-hook.py:928`
    引句:「第 4 項每次 Bash 都多一次 Python 啟動,只在帶寫檔形狀時才查圖譜(數字實作時量)」

## 範圍 5(S7、S8)

### F13
severity: major
    blocking: 是 — S8 要寫的「哪幾篇、什麼原因」現有程式沒有這份結構化資料,也拿不到會談編號
    重現:`memory-sweep.py` 的結果只存在 `tally.lines` 這種人讀字串(「✗ 檔名」「    對不上了:…」「? … 這條驗不了」、跨檢查的 `(檔名, kind, detail)`),檔名已經過 `_clean`(截長、控制字元換空格),不保證等於真實檔名,中文或長檔名可能被截成對不上索引的連結。`main()` 不讀 stdin,拿不到 hook payload 的 `session_id`(外層又有 watchdog 子行程,stdin 要先在父層讀完才能轉給子層);子行程超時被砍時什麼都不會寫。「沒事也寫」與現有提早返回衝突:`memory_dir` 不存在直接 `return 0`、`--quiet` 無發現直接 `return 0`,兩處都在 `_emit` 之前。要寫的分類也沒定:「✗ 對不上了」(過期)、「? 驗不了」(未知,不是過期)、「記狀態圖譜已有一份」(shadow,不是過期)、「指到不存在的節點」各自該不該標?標記文字固定寫「已過期或與圖譜對不上」,對 shadow 與 unknown 是不實的。
    file: `scripts/hooks/claude/memory-sweep.py:937`
    file: `scripts/hooks/claude/memory-sweep.py:953`
    file: `scripts/hooks/claude/memory-sweep.py:855`
    引句:「記憶清掃 hook 每次跑完(沒事也寫)把結果(會談編號、哪幾篇記憶檔、什麼原因)寫進 lumos 自己的快取資料夾」

### F14
severity: major
    blocking: 是 — 索引行解析與標記位置的邊界沒定,實作會破壞索引或標錯行
    輸入與壞處:
    - 索引行 `- [標題](檔名.md) — 說明`:「在那幾行行首加上 `⚠ …`」若真的加在行首,變成 `⚠ … - [標題](…)`,markdown 清單項目被打斷,這份索引自己的規範格式就是每條一行 `- [..](..)`。
    - 同一記憶檔在索引出現兩次:兩行都標還是只標一行,沒寫。
    - 索引行沒有檔名連結(純文字行、分節標題、`## 回報與溝通`)或連結帶 `./`、`#錨點`、`%E4%B8%AD…` 百分比編碼、`<含 空白.md>`:對不到,沒寫跳過。連結指向的檔不在清掃結果裡也沒寫(已被 `MAX_FILES` 截掉或是符號連結被跳過的檔,其過期狀態是「沒驗」,不是「沒問題」)。
    - 開場只載入索引前 200 行或 25KB(取小的):`instructionFiles[].content` 是載入器處理過的文字還是原檔?若是處理後,第 150 行以後的檔本來就看不到,標記沒意義;若標記後文字被載入器再截,每行多出數十字元會把原本剛好在 200 行或 25KB 內的最後幾條擠出去,條款沒說標記要不要算進預算。
    - `instructionFiles` 在上游外掛改寫了 claudeMd 文字時是 `undefined`(型別檔明說),也可能有多個 `kind: 'memory'` 檔(其他專案的記憶、使用者層記憶)。「記憶索引那一份」靠什麼認(kind、路徑結尾 `/memory/MEMORY.md`、與結果檔記的記憶目錄是否同一個)沒寫;`undefined` 時實作者若直接 `.find` 會丟錯,而 `prompt.context` 失敗等於整個開場內容受影響(「a failed hook passes through」尚可,但行為沒寫)。
    - 記憶目錄 slug 取自 `Path.cwd()`,在專案子資料夾啟動時 sweep 的 `here` 不是 Claude 載入的那份;sweep 靜默退出、不寫結果,外掛整份不動;但在 worktree(cwd 是 `-mod-batch2`)啟動時,sweep 與外掛各自推出的記憶目錄可能不同卻都存在,標記會貼到別專案的索引。
    file: `scripts/hooks/claude/memory-sweep.py:437`
    file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:8063`
    引句:「改 `instructionFiles` 裡記憶索引那一份的內容,用索引行裡的檔名連結對到記憶檔,在那幾行行首加上 `⚠ 已過期或與圖譜對不上:<原因>`」

### F15
severity: major
    blocking: 否 — 失敗是靜默且整個會談,但可以用文件已有的 `$.ui.invalidate` 補
    重現:型別檔說 `prompt.context` 「每個會談只算一次」,快取到 `$.ui.invalidate("prompt.context")` 或壓縮、`/clear` 重讀。spec 承認外掛與 sweep 誰先跑不明、外掛先跑就「整份不動」,但沒有補救:若 sweep 稍慢(它自己有 watchdog 到外層預算 85%,最壞十來秒)或外掛先跑,這個會談從開頭到壓縮前永遠沒有標記,而且沒有任何訊號(不是錯誤)。實作者沒有被要求在 sweep 結果檔出現後 `$.ui.invalidate("prompt.context")` 一次,也沒有被要求用輪詢。此外結果檔在整個會談只算一次的前提下,長會談中途新增的過期記憶不會被標到。
    引句:「記憶清掃 hook 跟 `prompt.context` 誰先跑型別檔沒說,實作前實測;外掛先跑就讀不到檔、整份不動,不會標錯」

### F16
severity: minor
    blocking: 否 — 補一句即可
    - 「快取資料夾」是哪個路徑沒寫(`~/.lumos/…`?repo 的 `governance/…`?),外掛端要自己再組一次同一路徑,是第三份要跟 Python 對齊的規則(事件帳的會談編號規則已有「兩邊用 rules-fixture 對齊」前例,這裡沒提)。
    - 檔名用會談編號,Python 從 payload 取的 `session_id` 可能為空或含 `/`、`..`;事件帳寫入端有 `SESSION_RE` 擋,這裡沒要求同一道。空編號時 S7「會談編號不同整份不動」的比對變成 `'' == ''` 通過。
    - 實務隱患節寫「不刪不改既有檔」,但決策 d3 的做法「先寫暫存再原子換名」會覆寫同會談的舊檔(壓縮、`/clear` 後重跑),「只留七天內的檔」要刪檔;誰刪、何時刪沒寫,與該句自相矛盾。
    引句:「唯一的寫檔是 lumos 快取資料夾裡的衍生結果,不刪不改既有檔;拿掉外掛即回到現狀」

## 範圍 6(S9、回退)

### F17
severity: minor
    blocking: 否 — 條款補「各自獨立」即可
    重現:現有 `_sync_claude_plugin` / `_teardown_claude_plugin` 全部寫死 `_LEDGER_PLUGIN`,`_ledger_user_plugin(claude)` 也不吃外掛名;`_ledger_ensure_plugin` 在「ledger 已裝」時直接 return。照字面「外掛清單含 lumos-context」若只把名稱改成清單迴圈,仍有:(a) 已裝 ledger 的人升級時 `lumos-context` 沒裝成但回報 `ok`(部分失敗的狀態語意沒定);(b) teardown 以 ledger 是否已裝為門,ledger 已手動移除而 context 還在時 context 不會被移除,接著市集被移除、context 變成孤兒;(c) 訊息文字與 `lumos events` 空狀態仍只說「事件帳外掛」。S9 的測試名 `t_install_registers_context_plugin` 只檢查裝與移。
    file: `scripts/lumos:21921`
    file: `scripts/lumos:22063`
    file: `.claude-plugin/marketplace.json:3`
    引句:「當 `lumos install` 與 `uninstall` 執行,外掛清單應含 `lumos-context`,各自裝上與移除」

18. 已讀,無 finding:範圍「不做」四條、PRIOR-ART、RETIRE-IF、實務隱患的金流與對外送出兩條、REVISIT 兩行。

總結:最嚴重 major,blocking 7 條
