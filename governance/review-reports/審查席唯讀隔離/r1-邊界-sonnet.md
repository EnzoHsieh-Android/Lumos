severity: blocker

審查範圍:凍結快照 r1-snapshot.md 全文。佐證用真實卷證(342 個迴圈資料夾、1025 筆 dispatch.json 席名)、docs/.canary-log.jsonl、事件帳外掛 register.ts、引擎型別檔。未改 repo 任何檔。

### F1 席位標記格式的首字限制 ASCII,真實席名與迴圈名多數過不了,隔離會靜默全關
severity: blocker
blocking: 是 — 設計宣稱的主路徑在真實資料上多數不成立,且失敗時不擋、不報,沒有任何隔離
引句:「三段都要符合 `[A-Za-z0-9][A-Za-z0-9._一-鿿-]*`(迴圈編號與席名常帶中文)」
- 正規式首字元只收 `[A-Za-z0-9]`,後面才收中文。真實席名如「併發-sonnet」「正確性-sonnet」「回滾-sonnet」「外家否決」都以中文開頭,不符合。
- 我用同一條正規式掃 governance/review-reports/*/*dispatch.json:1025 個席名只有 403 個通過(39%)。迴圈資料夾 342 個只有 255 個通過(75%),例如「審查席唯讀隔離」(本案自己)首字是中文,不通過。
- 標記要三段都合格才算,所以合格率是兩者相乘,實際遠低於 39%。
- 失敗場景:編排者照範本寫 `LUMOS-SEAT: 審查席唯讀隔離/r2/正確性-sonnet`,外掛判「格式不合 = 沒有標記」,S4 規定完全不擋。
- 本案的 REVISIT 只盯「派工有沒有帶標記」,盯不到「帶了但被判不合格」。
- S10 說用「外掛同一條格式規則」檢查範本,範本裡的佔位符 `<loop>/<rN>/<席名>` 用什麼值代入也沒講,測試可能綠、真實派工全紅。
- 另外席名帶括號、斜線、逗號、空白的情形(canary 帳上有「panel(s1,s2,s3)」「sonnet/V1-白名單生成」)也全部被判無標記。這類是彙總帳名,不是派工席名,所以只算旁證。
file: `governance/review-reports/審查席唯讀隔離/r1-dispatch.json:9`(席名「正確性-sonnet」)
file: `docs/.canary-log.jsonl`(auditor 欄含「併發-sonnet」「回滾-sonnet」等)

### F2 「讀同輪別席報告」擋的位置,在實際流程裡那時檔案還不在
severity: major
blocking: 是 — 防的主要場景(別席報告在 repo 內卷證目錄被讀到)與實際收貨流程錯位,條款 S2 綠了也沒保護到東西 ⚠(依據是記憶檔,不是圖譜節點)
引句:「檔名以 `<這席的輪次>-` 開頭、而且不是 `<輪次>-snapshot.*`、`<輪次>-dispatch.json`、也不是這席自己的」
- 記憶檔 seat-reports-outside-repo-while-running 記載:席位還在跑時,先到的報告存在 `$CLAUDE_JOB_DIR/tmp`(repo 外),全部交回才搬進卷證目錄。照這個流程,同輪別席報告在席位跑的時候根本不在 `governance/review-reports/<迴圈>/`,本條擋的是一個當時空的位置。
- 該記憶檔提到的真實洩漏是 Codex 席用 `ls/sed` 讀 repo 內卷證,那是 Bash 加外家席,都在「不做」清單。
- 另一個沒講清楚的地方:路徑比對的是「主 checkout 的卷證目錄」還是「任何 worktree/clone 底下的同名相對路徑」。審查在 worktree 或 clone 裡跑時(本次審查的 repo 就是獨立 clone),規則落不落得到沒有定義。
- 要請作者明講:保護的是哪個實際路徑,編排者收貨期間報告放在哪裡。
file: `/Users/enzo/.claude/projects/-Users-enzo-harness-lumos-toolchain/memory/seat-reports-outside-repo-while-running.md:5`

### F3 Grep/Glob 省略 path 就是 cwd,在 repo 根會被一律擋,審查員最常用的搜尋被打掉
severity: major
blocking: 是 — 高頻誤擋,審查員最基本的 repo 內搜尋全被擋,逼出繞法或讓守衛被關掉
引句:「`Grep`、`Glob` 的搜尋範圍若涵蓋這個卷證資料夾也擋:範圍是 `path`(省略時是會談 cwd)」
- 審查席 cwd 通常是 repo 根(或 worktree 根),`Grep pattern=foo` 不帶 path 的範圍就涵蓋 `governance/review-reports/<迴圈>/`,依本條一律擋。`path` 指向 `governance/`、repo 根、`~`、`/` 也一樣。
- 擋的理由是「範圍涵蓋」,不是「實際會掃到同輪別席報告」;資料夾裡此時往往只有 snapshot 與 dispatch。
- 本條沒寫擋下時的理由文字要教席位改用哪個 path(§三 的例句只講寫入)。
- `Glob` 的 `pattern` 為 `**/*.md` 這類相對模式,涵蓋判定是否看 pattern 也沒寫。只寫了「pattern 本身是絕對路徑」的情形。
- 要請作者決定:是否只在「資料夾裡真有同輪別席報告檔」時才擋,或對 Grep/Glob 只擋明確指向卷證資料夾的 path。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,範圍·做·3)

### F4 同輪檔名規則兩頭誤判:真實卷證檔名不只 snapshot/dispatch/報告
severity: major
blocking: 是 — 擋掉驗收輪必讀的材料,又放過字首不同的別席報告
引句:「同輪的收貨紀錄 `<輪次>-intake.md` 也擋」
- 規則是「檔名以 `<輪次>-` 開頭且不在白名單就擋」,白名單只有 snapshot.*、dispatch.json、自己的 `<席名>.md`。
- 真實檔名見 governance/review-reports:`r2-delta.patch`、`r3-delta.patch`(修正差異,下一輪席位要看)、`r3-work.md`、`rN-<席名>.stdout`、`r3b-intake.md`、`roster-alerts.log`。前三種會被擋,代碼審「修正驗收」席拿不到 delta。
- 反向:真實別席報告也有 `code-r1-資安-sonnet.md`、`v2-r1-回滾-sonnet.md`、`r1-arch-架構對齊.md`、`r1-s1-通才.md`。字首不是 `rN-` 的(前兩種)不會被擋,等於這條規則只對最標準的檔名有效。
- 輪次 `r3b` 這種寫法,不符合快照說的「一律寫成 `rN`」。標記裡寫 `r3b` 能過正規式,但檔名比對會把 `r3-` 與 `r3b-` 的前綴關係搞混。
- 自己的報告以席名精確比對:兩席名互為前綴(「通才」與「通才-sonnet」)不會誤放,這點沒問題。
file: `governance/review-reports/筆記不存程式碼推得出的事/r3-delta.patch`
file: `governance/review-reports/代碼審資安席/`(沒有 `r1-` 之外的前綴樣式可參照時對照 `code-r1-資安-sonnet.md` 所在資料夾)

### F5 派工詞「第一行 LUMOS-SEAT」的取法,遇到內嵌材料、程式碼區塊、縮排、CRLF 都會取錯或漏取
severity: major
blocking: 是 — 標記判定可被派工詞內容左右,誤殺實作者或讓席位身分被冒用
引句:「派工詞 `e.prompt` 逐行找 `LUMOS-SEAT: ` 開頭的行,取第一行」
- 非審查席子代理(implementer、辯方)的派工詞常整段貼入設計或範本原文。貼入的行若恰好以 `LUMOS-SEAT: x/r1/y` 開頭(含放在程式碼區塊裡的範例),整個實作者被當成審查席,從此寫不了 repo;S5 還會讓它再派的孫代理一路繼承。實作本案自己時,測試夾具與範本就會有這種行。
- 反向:標記行縮排、前面有 `- `、在程式碼圍欄裡被縮排、或行尾有 `\r`(最後一段含 `\r` 過不了正規式)就漏掉,不擋也不報。
- 同一個派工詞有兩行標記(貼入的被審文件裡有一行,編排者自己的一行在後面)時取第一行。若被審材料排在標記前面,材料作者可決定席名,進而控制「自己的報告可讀」那條豁免。快照沒有規定標記必須放在派工詞第幾行,也沒有規定出現兩行時應拒絕而不是取第一行。
- 主會談帶標記:主迴圈沒有 `agentId`,S4 已涵蓋,不另算。
file: `mods/claude/lumos-ledger/hooks/register.ts:371`(agent.spawn 掛點,與本案同一掛法)

### F6 repo 範圍只用「會談 cwd」判定,子代理自己的 cwd、cwd 不在 repo、子模組、裸 repo 都會落空
severity: major
blocking: 是 — 保護範圍取決於啟動目錄這個偶然條件,落空時完全放行且不報 ⚠(子模組與裸 repo 兩項未實測,只依 git 行為推導)
引句:「git 判定失敗(不在 repo、逾時):這一次照常放行,不擋(外掛一律 fail-open)」
- 引擎的 `AgentSpawnInput.cwd` 允許子代理跑在與會談不同的目錄。快照用「會談 cwd」補相對路徑、判 repo,子代理 cwd 是 repo 內另一個 worktree、而會談 cwd 不在 repo 時,範圍判定失敗而全放行。
- 編排者在不是 repo 的上層資料夾(例如 `~/harness`)啟動,底下有多個 repo:`rev-parse` 失敗,審查席對任一 repo 用絕對路徑都能寫。
- 子模組:`--show-toplevel` 回子模組根,`pickMain` 因 `git-common-dir` 形如 `<super>/.git/modules/<n>` 不以 `/.git` 結尾而取 toplevel。審查席寫上層專案其他位置不在範圍。
- 裸 repo:`--show-toplevel` 會出錯,走 S6 全放行。
- 要請作者明講:範圍判定應以「發出工具呼叫的子代理自己的 cwd」還是「會談 cwd」,以及 cwd 不在 repo 時是否改用 spawn 時看到的路徑。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:350-355`
file: `mods/claude/lumos-ledger/hooks/register.ts:44-46`

### F7 路徑只做字串正規化,/tmp 與 /private/tmp、祖先目錄連結、大小寫、Unicode 正規化都能繞過或誤判
severity: major
blocking: 是 — 在本機(macOS)日常路徑形狀下就會失配,且全部失配方向都是放行
引句:「比對前正規化(去 `.`、`..`、重複斜線)。路徑是連結時看它自己的位置,不跟連結(寫到 repo 裡的連結本身就算寫 repo)」
- `git rev-parse` 回的是真實路徑。repo 或 worktree 放在 `/tmp/x`(macOS 實際是 `/private/tmp/x`)時,工具輸入若寫 `/tmp/x/f.md`,字串比對不在 `/private/tmp/x` 底下,放行。
- 只處理「最後一段是連結」。祖先目錄是連結(`/tmp/mylink -> <repo>`)時,寫 `/tmp/mylink/f.md` 字串上在 repo 外,放行。席位可用 Bash `ln -s` 造連結;`ln` 不在 git 指令清單,也不被擋。「誠實界線」寫不防有心人,但上一點是一般路徑形狀,不需要惡意。
- macOS APFS 大小寫不敏感:`governance/Review-Reports/...` 命中同一檔卻不符字串。檔名 NFD 與 NFC 也同理(中文多數不受影響,康熙部首、相容漢字、重音字會受影響)。
- 要請作者明講比對前是否做 realpath(祖先)、大小寫與 NFC 正規化,以及 realpath 失敗(目標檔還不存在)時如何退回。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二)

### F8 Bash 內 git 判定的切段與包裝詞有多條旁路
severity: major
blocking: 是 — S3 宣稱「夾在後面的也擋」,切段規則沒涵蓋常見寫法,同時有誤擋
引句:「`Bash` 指令依 `&&`、`;`、`|`、換行切成各段,每段若是 `git` 指令」
- 沒列 `&`(背景):`git status & git commit -m x` 整段第一個子指令是 status,放行。
- 段首不是 `git` 字樣就不看:`env git commit`、`command git commit`、`/usr/bin/git commit`、`(git commit)`、`{ git commit; }`、`$(git commit)`、`xargs git`、`sh -c "git commit"`、`bash -c`。
- 全域選項 `--git-dir <路徑>`、`--work-tree <路徑>`、`--namespace <名>` 的空白分隔寫法沒寫,後面的路徑會被當成子指令,放行。快照只列了 `=` 寫法。
- 子指令清單缺 `fetch`(會改 ref)、`init`、`clone`、`submodule`、`remote`、`bisect`、`sparse-checkout`、`replace`、`symbolic-ref`、`filter-branch`、`read-tree`、`hash-object -w`、`commit-tree`、`reflog expire`。快照說「唯讀的 diff/log/show 照常」,但 `git diff --output=<檔>`、`git log --output=`、`git format-patch -o` 寫檔也在「照常」之列。這點與「不做:擋 Bash 一般寫檔」同族,可接受,但需寫明。
- 誤擋:heredoc 裡行首是 `git commit` 的文字(寫筆記或寫測試)、引號內的 `;`,以及 `cd /tmp/x && git commit`(沒有 `-C` 但實際在 repo 外)。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,範圍·做·3)

### F9 `-C` 指到 repo 以外怎麼判,快照沒定義:變數、波浪號、相對、多個 -C、引號
severity: major
blocking: 是 — 席位的合法實驗寫法(`git -C "$TMP" ...`)能不能過,規格沒答案,實作會自己挑一個 ⚠(實際席位寫法未逐筆驗證)
引句:「而且沒有 `-C` 指到 repo 以外的路徑 → 擋」
- `-C "$T"`、`-C $(mktemp -d)`、`-C ~/x`:靜態無法展開。判放行就是旁路(`-C "$REPO"` 同寫法);判擋就誤擋所有用變數的合法實驗。
- 相對 `-C ../x` 要以哪個 cwd 解:Bash 的當前目錄可能因先前的 `cd` 變過,外掛看不到。
- 多個 `-C` 會逐個疊加(`-C /tmp -C ../repo`),快照寫「另外記下」但沒說取哪個或如何疊加。
- `-C` 指到 repo 外但那個目錄本身是 repo 的 worktree 或 repo 內的連結(F7)怎麼算。
- `-C` 指到 `<repo>/.tmp` 這種 repo 內臨時目錄,依本條擋;席位範本若建議把暫存放 repo 內會互相打架(範本沒說)。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,範圍·做·3)

### F10 「啟動中」等待沒有逾時與清理規則,可能卡死無關的子代理;「不會互卡」沒有證明
severity: major
blocking: 是 — 一個沒結案的登記會讓同會談其他子代理的每次工具呼叫無限等待,而且與「外掛一律 fail-open」互相矛盾 ⚠(引擎是否真會造成死鎖型別檔沒寫,但沒有逾時是確定的)
引句:「先等它們都回報完再查表(子代理的工具呼叫一定在它啟動之後,等這一下不會互卡)」
- `agent.spawn` 被引擎拒絕、`next(e)` 丟例外、或根本不回,「啟動中」項目何時移除沒寫,S12 只測「等到回報」。
- 等的是「同一會談所有啟動中的派工」,不是「這個 agentId 對應的那一筆」。同時派十席時,第一個先啟動的席要等完九個別人;已登記的席查表直接過,但表裡查不到的呼叫(非席位子代理、引擎的 fork 與 workflow 代理,型別檔註明這類 id 沒有任何清單命名,即 AgentLoop.agentId 的說明)每次都會碰到這段等待。
- 等待是在 `tool.call` 掛點裡等一個 `agent.spawn` 掛點的 `next(e)` 結果。引擎是否會因為前一個呼叫還沒放行而延後啟動回報,型別檔沒說,快照直接斷言「不會互卡」,沒有任何測試或型別檔出處。
- 沒有 `session.end`(行程被殺、`claude -p` 非正常結束)時登記表只在行程記憶體,不會外洩,這點無問題。但「很快結束的子代理」:`next(e)` 還沒回它就已跑完,登記晚到,表項在 session.end 前留著,量小但未規範。
- 要請作者加:等待逾時、逾時後的行為(放行或擋,與 S6 一致)、spawn 失敗必清、以 agentId 而不是整批等待。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:198-205`
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:359-398`

### F11 同輪重派同名席,「自己的報告可讀」豁免讓兩個同名子代理互通
severity: minor
blocking: 否 — 影響限於同名席,且同名本就是同一席位的重跑,風險低
引句:「多個審查席同時跑,各自以子代理編號查表,不共用可變狀態。」
- 鍵是子代理編號,沒問題。但「這席自己的 `<輪次>-<席名>.md`」以席名比對:重派同名席(失敗重跑)時舊席與新席互相可讀對方報告,與「各自獨立」相違。
- 併發節說「不共用可變狀態」,但「啟動中」清單與 10 分鐘 repo 範圍快取正是共用可變狀態(F10、F12)。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,實務隱患·併發)

### F12 repo 範圍快取 10 分鐘:新增的 worktree 在窗口內不受保護,並行首次判定可能同時起多個 git
severity: minor
blocking: 否 — 窗口有界(10 分),且需要席位剛好寫進剛建的 worktree
引句:「判定以會談的 cwd 為鍵快取 10 分鐘。」
- 全域規則叫並行會談開新 worktree(`git worktree add ../<repo>-<任務>`),建好後 10 分鐘內,快取裡還沒有它,席位對它的寫入放行。
- 快取沒命中時,同時十席的第一次呼叫各自跑 `rev-parse` 與 `worktree list`,沒有單飛(single-flight)描述;每次 fail-open 的逾時值也沒寫(S6 說逾時,卻沒給秒數)。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二)

### 已讀,無 finding
- 前言、PRIOR-ART、RETIRE-IF:論述與出處一致;未驗證 nested-agent-permission-scope 的內容(不在審查範圍)。
- 範圍·不做 清單、回退節、實務隱患的「已排除」三項、誠實界線:與設計邊界一致。誠實界線已承認 Bash 與標記漏寫,F5、F7、F8 提的是「不需要惡意就會發生」的部分,不是重複。
- 條款 S8、S9、S13、S14(安裝流程、檔案合法、事件帳 parentAgentId、pickMain 逐字比對):未發現問題。S13 對應型別檔 `parentAgentId` 欄位(約 307-314 行)吻合。

總結:最嚴重 blocker,blocking 10 條
