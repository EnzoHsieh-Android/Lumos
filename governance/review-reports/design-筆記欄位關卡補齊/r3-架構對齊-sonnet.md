severity: major

## 四問逐答

### 1. 分層與依賴方向

L 段目前是「純運算聚合」寫法:走訪 `notes.items()`,只讀早就在 `load_vault` 時算好的 `n.lint`(frontmatter 解析指紋),再交給 doctor 自己的 `warn()/ok()` 印(`scripts/lumos:1192-1202`)。而設計要的「跑 lint 的錯誤等級規則」目前只活在 `cmd_lint(env, node)` 這個 CLI handler 裡——它自己做 `env.find(node)` 名稱解析、自己讀檔算 decisions 結構、自己 `print()`、自己回退出碼(`scripts/lumos:4790-5033`)。設計沒講 L 段要怎麼拿到這份 errs 清單:直接呼叫 `cmd_lint` 等於 doctor(全圖層)對每篇筆記各呼叫一次「CLI 指令層」的列印函式,557 篇會印 557 段 lint 輸出、蓋掉 doctor 自己的 warn 格式;不呼叫它就得在 L 段另抄一份同樣的 status/日期/decisions/about_code/lands_in 規則——那就是引入第二套做法。這一步的呼叫方向design裡完全沒交代,見 F2。

### 2. 命名與錯誤處理

新規則的訊息格式(「每條訊息要講怎麼修」,`governance/review-reports/design-筆記欄位關卡補齊/r3-snapshot.md:46`)跟 `cmd_lint` 現有 errs 的寫法(例如 `scripts/lumos:4834` 的 type 錯誤訊息:先講問題、破折號接怎麼修)一致;開關的三態訊息(on/warn/off/看不懂當 on)也跟 `_nodehome_config` 的訊息風格(`scripts/lumos:21437-21444`)一致。這部分對齊,不成問題。但 [S11] 把「新開節點那支判斷」(`_nodehome_resp_ok`)在 `set` 這個入口改成看開關擋或提醒,跟同一支判斷在 `new` 入口的既有用法(無條件擋,不看任何開關)不一致——見 F1,這屬於「分級方式跟鄰居不一樣」。

### 3. 第二種做法

設計明確不比上一版、不接碰到清單、不讀提交內容(`governance/review-reports/design-筆記欄位關卡補齊/r3-snapshot.md:71-73`),這三處都對齊既有否決過的形狀,沒有另開新做法。但 `note_lint.gate` 這個設定本身在提交前要怎麼讀(讀工作目錄磁碟、還是像 `node_home.gate` 一樣讀 git 提交快照)完全沒交代——見 F3,這是一個「該用既有讀法卻沒講清楚會不會變成另一種讀法」的缺口。

### 4. 落點合不合理

lint 既有的規則本來就記在 `Systems/lumos-cli-read.md`(例如裡面已有一條 `RULE:[since:2026-09-21]` 專講 lint 的四個脈絡前綴規則),`doctor`/`lint`/`set` 三個函式家族也分別歸在 `lumos-cli-read`/`lumos-cli-write` 管——落到這兩篇本身不算離譜。但 `note_lint.gate` 是一個新的、橫跨提交前/健檢/`set` 三個入口的**開關機制**,形狀直接照抄 `node_home.gate`;而 `node_home.gate` 這個同形狀的機制本身沒有塞進 `lumos-cli-read`/`lumos-cli-write`,是另開了一篇 `Systems/每支檔有家.md` 專門管(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` grep 得到 `_nodehome_config`/`node_home.gate`)。這篇設計借了它的「開關形狀」卻沒有比照借「開一篇新節點管開關」——判不準是不是真的该另開,標 ⚠(見 F4)。

## F1 responsibility 的開關擋法跟既有 new 入口不一致

severity: major
blocking: yes

[S11] 要求 `set` 寫 responsibility 時,`_nodehome_resp_ok` 判不過要看 `note_lint.gate`(on 擋、warn 提醒)。但同一支判斷函式在 `new --code --responsibility` 的既有入口是無條件擋,完全不看任何開關(`scripts/lumos:15052` 只有 `if responsibility is not None and not _nodehome_resp_ok(responsibility):` 就直接印「擋下」回 2,不查 `_nodehome_config`)。`_nodehome_resp_ok` 在其餘所有呼叫點(`scripts/lumos:22162`、`22167`、`22175`、`22445`、`22463`)也都活在已經先查過 `cfg["mode"]` 的 `_nodehome_evaluate` 家族裡,唯獨 `new` 是唯一「永遠擋、沒開關」的例外。設計把 PRIOR-ART 寫成「負責範圍長度直接用新開節點那支判斷」,卻沒提到要不要連 `new` 那個入口的無條件擋法也一併改,或者刻意保留兩種不同嚴格度——同一顆判斷函式,一個入口永遠擋、另一個入口看開關可以放行,這是沒有交代的行為分裂。
引句:「當 `lumos set` 寫 responsibility 而新開節點那支判斷不過,開關 on 時寫入應被擋下、檔案不變,warn 時應寫入並提醒」
引句:「負責範圍長度直接用新開節點那支判斷(`_nodehome_resp_ok`)」
file: `scripts/lumos:15052`
file: `scripts/lumos:22162`

## F2 doctor L 段怎麼取得 lint 錯誤等級規則,設計沒講清楚呼叫方向

severity: major
blocking: yes

「對圖譜裡每篇筆記跑 lint 的錯誤等級規則」這句話沒有指明實作路徑。現況唯一算得出 status/日期/decisions/about_code/lands_in 這批新規則(errs)的地方是 `cmd_lint(env, node)`——它是單節點 CLI handler:先 `env.find(node)` 做名稱解析、再逐項算 errs/warns、最後直接 `print()` 並回傳退出碼(`scripts/lumos:4790-5033`),跟 doctor 目前 L 段「走訪全部 notes、把結果交給 `warn()/ok()` 統一格式印」的聚合寫法(`scripts/lumos:1192-1202`)是兩種不同東西。doctor 對 557 篇圖譜逐篇呼叫 `cmd_lint` 會印出 557 段各自的 `lint <rel>` 輸出,蓋掉 L 段自己的呈現格式;要維持 doctor 的呈現格式,就得把 `cmd_lint` 裡這批規則的計算拆成一支不列印的純函式,兩邊共用——但設計完全沒提到要不要做這個拆分,也沒說如果不拆分,L 段打算自己重寫一份等價規則(那就是又一套做法)。
引句:「對圖譜裡每篇筆記跑 lint 的**錯誤等級**規則(提醒等級不跑),有錯的列出篇名與第一條錯誤」
file: `scripts/lumos:4790`
file: `scripts/lumos:1192`

## F3 note_lint.gate 在提交前讀磁碟還是讀提交快照,沒有交代

severity: major
blocking: yes

`node_home.gate` 的既有讀法明確分兩種:提交前讀 git 提交索引、推送前讀終點提交,刻意不讀工作目錄——理由寫在函式說明裡:「工作目錄裡沒暫存的『關掉』不得關掉提交索引的檢查」(`scripts/lumos:21405`,`_nodehome_config` 的 `from_snapshot` 參數與其呼叫點 `scripts/lumos:22418`/`22530`)。這防的是同一種手法:有人在提交前把設定檔在工作目錄改成寬鬆值但不 stage,讓檢查讀到「已關閉」而放行,提交本身卻沒留下任何痕跡。設計只交代 `note_lint.gate` 存在 `.lumos/config.json`、on/warn/off 三態,完全沒說提交前讀它時是走磁碟(跟現有 pre-commit hook 對筆記內容本身的讀法一致)還是比照 `node_home.gate` 讀提交快照——這正是同一形狀的機制,在同一個「提交前」時機點,防護等級可能悄悄比它抄的對象弱一截,設計裡一個字都沒提。
引句:「`.lumos/config.json` 的 `note_lint.gate`,一個開關同時管二與一的新增部分,以及四:」
file: `scripts/lumos:21405`
file: `scripts/lumos:22418`

## F4(⚠判不準)note_lint.gate 這個橫跨三入口的開關機制要不要比照每支檔有家另開一篇

severity: minor
blocking: no

`node_home.gate` 同一種「on/warn/off 三態、看不懂當 on、橫跨提交前/推送前/健檢」的機制,落點是獨立一篇 `Systems/每支檔有家.md`,不是塞進 `lumos-cli-read`/`lumos-cli-write` 這兩篇通用讀寫原語清單。這篇設計只借了 `node_home.gate` 的形狀,`lands_in` 卻只寫 `lumos-cli-read`/`lumos-cli-write`,沒有比照借「開一篇新節點管這個新開關」。另一方面,lint 既有的規則(四個脈絡前綴那條 `RULE:`)本來就直接記在 `lumos-cli-read.md` 裡,不是每次都另開一篇——落點precedent 兩邊都有,哪一種才是這次該照的,不容易單靠程式碼裁定,標不對齊、標 ⚠。
引句:「這些新東西擋不擋看專案開關 `note_lint.gate`(沒設只提醒),提交前與推送前同一個開關」
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:1`

不對齊共 4 條,其中 major 3 條。
