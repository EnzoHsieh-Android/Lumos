severity: major

### F1 子代理沒有 turn_start,spec 的事件表與 S1 對不上
severity: major
blocking: 是 — 照做後 S1 的「子代理的事件帶 agent 編號、回合對得起來」無法成立,而且是引擎型別檔已寫明的事實。
spec 段落:做法 1 事件與格式。
問題:spec 說每筆有 `turn`、`agent`,且子代理有自己的回合。但 `turn.start` 的輸入只有 `text`、`turnId`,沒有 `agentId`,而且子代理的回合根本不會觸發 `turn.start`。只有 `turn.complete` 帶 `agentId`。
具體情境:實作者照表寫 `turn_start` 取 `e.agentId` 會得到 undefined。主會談的 `turn_start` 全記成 agent=null,子代理的回合只出現 `turn_end`。`lumos events` 的「回合數」若數 `turn_start`,會漏掉所有子代理的回合,數字與 `turn_end` 數不相等。
引句:「`turn`(回合編號,子代理也有自己的)、`agent`(子代理編號,主會談為 null)」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:12642-12654` 該處寫明「a subagent's run raises no `turn.start`, its steps carry it」,`agentId` 只在 `TurnCompleteFields`。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:12721-12732` `TurnStartInput` 只有 `text`、`turnId`。

### F2 `origin` 說是字串,型別檔是物件;「最近一筆 session.append」沒有可行的取法
severity: minor
blocking: 否 — 只影響單一欄位的內容,不影響其他事件。
spec 段落:做法 1 的 `turn_start` 列。
問題:`session.append` 的 `origin` 是物件(`{kind:'composer'}`、`{kind:'model',model}`、`{kind:'tool',tool}` 等),不是字串。`session.append` 對主會談與每個子代理的每一列都會觸發,模型回應區塊、工具結果也走這條。spec 沒說怎麼從這串列中認出「這一回合的 prompt 列」。
具體情境:實作者取「最近一筆」,很容易取到上一回合子代理或工具結果的 origin,`turn_start.origin` 記成 `tool` 或 `model`。spec 說實測看過 `unclassified`、`task-notification`、`coordinator`,而型別檔裡 PromptOrigin 的欄位是 `kind`,字串到底是 `kind` 還是別的欄位沒有交代。⚠ 我沒有實機驗證 prompt 列的 `door` 值。
引句:「取最近一筆 `session.append` 的 prompt 列的來源原樣字串」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:10101-10120` `SessionAppendOrigin` 為物件聯集。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:10023-10051` 該輸入有 `door` 與 `agentId` 可篩,spec 沒用。

### F3 塊序號放在記憶體,模組熱重載或換 session 時會從頭編號,而 `$.fs.write` 是整檔覆寫
severity: major
blocking: 是 — 會靜默覆蓋已寫出的塊檔,造成事件遺失,與「不重寫舊塊」的承諾相反。
spec 段落:做法 2 寫入。
問題:spec 說序號遞增、補零 6 位,但沒說序號從哪來。`$.fs.write` 的語意是「whole new content」,同路徑就是覆寫。型別檔指出外掛的熱重載會讓模組狀態重來(要跨重載活下來的資料得放特定的持久儲存)。`/clear` 後行程繼續跑,session id 換新、且不再觸發 `session.start`。
具體情境:使用者在會談中跑 `claude plugin update` 加 `/reload`(或 reload mod)。模組變數的序號歸零,下一塊寫成 `000001.jsonl`,蓋掉原本的第 1 塊。`/clear` 後若緩衝、序號、頂層快取仍是模組全域,新舊 session 的事件會混進同一個資料夾或同一條序號。
引句:「把緩衝寫成一個新塊檔(序號遞增、補零 6 位),清空緩衝。不重寫舊塊。」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3270-3278` 說明某種儲存才是「data that survives a hot reload」。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:4268-4280` `/clear` 與 resume 後行程以另一個 session id 繼續。
修法方向:第一次寫該 session 前先 `$.fs.list` 該夾取最大序號,而且所有狀態以 session id 為鍵。

### F4 相對路徑相對的是會談工作目錄,不是 git 頂層;頂層又被快取一輩子
severity: major
blocking: 是 — 會把事件寫到錯的資料夾(例如子目錄底下新建 governance/runtime/),或是寫進已離開的 repo。
spec 段落:範圍 3、做法 2 寫入。
問題:spec 的寫入路徑是 `governance/runtime/events/...`,但 `$.fs.write` 的相對路徑是在會談工作目錄下。spec 要求先 `git rev-parse --show-toplevel`,卻沒說要把頂層拼成絕對路徑再寫。另外「結果記在模組變數,不每次查」把頂層與「有沒有 `*-knowledge`」整個會談只算一次。型別檔有 `CwdChanged`(`old_cwd`/`new_cwd`),會談中途換目錄(進另一個 worktree、cd 到別的 repo)是常態。
具體情境一:會談在 `scripts/` 子目錄啟動,若用相對路徑寫,就會在 `scripts/governance/runtime/events/` 建出一棵樹,而且 `.gitignore` 也在那裡,頂層的 `governance/` 看不到,`lumos events` 讀不到、enforcement 的 7 天偵測也看不到。
具體情境二:會談先在無圖譜目錄啟動、後來進圖譜 repo,因為快取「不寫」,整場都沒帳。反過來則把別的 repo 的事件寫進舊 repo。
引句:「沒有就整個會談都不寫(結果記在模組變數,不每次查)」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3114-3120` 相對路徑在 session's working directory 下。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3523-3527` `CwdChanged` 事件。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3406` `$.process.run` 的 cwd 預設是 session 的。

### F5 session.end 的 flush 排在 next(e) 之後,但引擎對結束有很短的共用時間上限
severity: minor
blocking: 否 — 損失只限最後一個 turn_end 之後的幾筆,且 spec 已承認當機會掉緩衝。
spec 段落:做法 2 寫入(最後一條)與寫入第一條的 session.end 觸發。
問題:spec 一面說「所有 hook 一律先 `next(e)`」,一面說遇到 `session.end` 要把緩衝寫出。型別檔說結束步驟共用一個短的時間上限(`next.budget`),範例是在 `next(e)` 前先存。先 `next` 再寫,引擎可能已經結束行程。
具體情境:使用者 `/exit`,最後一個 `turn_end` 後才進來的 `tool`/`spawn` 事件(例如背景通知)留在緩衝,沒寫出。spec 把這個放在「沒實測」清單,但沒有寫順序要怎麼定。
引句:「所有 hook 一律先 `next(e)`、照原樣回傳結果;mod 例外時引擎本來就會跳過它(fail-open)。」
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:4266-4272` 「Exits stay fast whatever is loaded: the whole chain shares one short wall-clock bound」與 `await save(next.budget), next(e)` 的範例(先存再 next)。

### F6 enforcement 新增列會直接踩到釘死列數的測試,而且既有測試會真的呼叫本機 claude
severity: major
blocking: 是 — 實作完第一次跑測試就紅,而 spec 的測試清單沒有這一條。
spec 段落:範圍 6、做法 5、S8。
問題一:`t_enforcement_never_raises_on_missing` 釘「恰 23 列」,加一列或兩列(「Claude 列」與「Codex 列」是一列還是兩列,spec 沒講,層名也沒定)就紅。這是 CLAUDE 記憶裡「純新增也動邊界」的同一類。
問題二:`enforcement_status(root, home)` 為了可測試而注入 `home`,但 spec 的第二層判斷是 `claude plugin list --json`,不受 `home` 注入控制。既有約十支呼叫 `enforcement_status` 的測試在沒有事件塊時都會走到這一步,真的在本機跑 `claude`(約 0.9 秒一次),CI 上沒有 `claude` 則回「無法判斷」。S8 只寫「近期有事件時不得呼叫 claude」,沒說怎麼注入假的 claude、怎麼讓其他測試不呼叫。
具體情境:實作者加一列後,既有的 23 列測試與 `total = 非unknown列數` 一類的計數測試翻紅;且本機測試慢數秒、與機器上有沒有裝 mod 有關而不穩定。
引句:「近期有事件時不得呼叫 `claude` 指令 [test:t_enforcement_ledger_row]」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py:31327` 釘 `len(rows) == 23`。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:20281` `enforcement_status(root=None, home=None)`,全函式都以注入的 `home` 為準。

### F7 安裝時以來源 repo 路徑註冊市集:從 worktree 或別的 clone 安裝會撞名或留下懸空路徑
severity: major
blocking: 是 — 本 repo 實際就大量用 worktree 工作,照 spec 會讓使用者層設定指向會被刪的路徑。
spec 段落:做法 4 安裝與移除。
問題:`claude plugin marketplace add <來源 repo>` 加的是一個本機路徑,市集名固定 `lumos-toolchain`。`cmd_install` 的來源是 `Path(__file__).resolve().parent.parent`,從 worktree 跑(例如本審查的 `lumos-toolchain-event-ledger`)就是那個 worktree。spec 只處理「已加過」這一種,沒有處理「同名市集已存在、但指向另一個路徑」。
具體情境一:先從主 clone 裝過,後來在 worktree 重跑 `lumos install --force`(`install.sh` 就是等價於這個),`marketplace add` 要嘛因同名失敗(只印一行,繼續)、要嘛換掉路徑。
具體情境二:worktree 路徑被登記後使用者刪 worktree,市集與外掛來源懸空,之後 `claude plugin update` 失敗,而 spec 的失敗處理是「只印一行、不改回傳碼」,使用者不會發現。
spec 自己也承認「已加過市集怎麼判成功,實作時才量」,這等於關鍵分支沒有定。⚠ 我沒有實測本機路徑市集是否複製到快取,只確認 `claude plugin marketplace add --help` 接受 URL、路徑或 GitHub repo。
引句:「「已加過市集」怎麼判成功,以退出碼加輸出判斷,實際訊息在實作時用真的 `claude` 量一次、寫進 Systems 節點」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:16908` `cmd_install` 開頭;`:16956` 附近 `_src_repo = Path(__file__).resolve().parent.parent` 以執行檔位置為準。

### F8 回退與 uninstall:沒裝 claude 的人每次拆都被印失敗;程式回退後裝過的機器無法再由 lumos 清掉外掛
severity: major
blocking: 是 — 回退節照做會讓已裝過外掛的每台機器殘留會繼續寫事件帳的外掛,而 lumos 已不具備移除它的程式。
spec 段落:做法 4(uninstall)、回退、實務隱患「不可逆」。
問題一:install 有「claude 在不在、來源有沒有市集檔」兩道前置判斷,uninstall 沒有任何前置判斷,S7 只寫「失敗只印一行並附上兩個手動移除指令」。只用 Codex、沒裝 claude 的機器每次 `lumos uninstall` 與 `teardown` 都會印兩個失敗。`teardown` 的確認提示與 `cmd_uninstall` 輸出的清單也沒有把「外掛」列進去,使用者不知道會動 `~/.claude` 的外掛設定。
問題二:`claude plugin marketplace remove` 在不帶 `--scope` 時會移除所有範圍(user、project、local)的宣告,spec 沒帶 `--scope user`,範圍比它宣稱的「使用者層」更大。
問題三(回退):回退節的「程式」一條是刪 mod 與市集檔、拿掉 install/uninstall 的呼叫。這之後 `lumos uninstall` 再也不會移除外掛。已經跑過 `lumos install` 的每台機器(別台機器、其他工作樹)都留著外掛;市集指向的 repo 路徑失去 `mods/` 後,外掛從快取繼續載入並寫事件帳。回退節只有「手動兩個指令」,沒有排序(必須在程式回退之前、在每台機器上先跑 `lumos uninstall`),也沒有說怎麼知道哪些機器裝過。
引句:「`lumos uninstall`(`teardown` 第三步就是呼叫它):`claude plugin uninstall lumos-ledger@lumos-toolchain`、`claude plugin marketplace remove lumos-toolchain`,失敗只印一行,並附上這兩個手動移除指令。」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:17044-17093` `cmd_teardown` 的確認提示只列 pre-commit/pre-push、CLAUDE.md、vendored、~/.local/bin/lumos、skills、全域 hooks。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:16969` `cmd_uninstall` 現行只清 symlink 與 skills,沒有 claude 前置判斷。
file: `claude plugin marketplace remove --help` 輸出「Omit to remove it from every」scope。

### F9 「重跑 install 拿新版 mod」靠 `claude plugin update`,但 spec 沒有定義新版怎麼被判成新
severity: minor
blocking: 否 — 只影響升級,第一次安裝不受影響;但沒有任何守衛會抓到「mod 落後」。
spec 段落:做法 4。
問題:`update` 只更新到市集目前宣告的版本,spec 沒有要求 `plugin.json`/`marketplace.json` 的 `version` 隨 mod 改動而遞增,也沒有先跑 `claude plugin marketplace update lumos-toolchain`。`lumos update` 與 bootstrap 又明確不碰外掛。本機 `claude plugin list --json` 顯示其他外掛的版本是 git 短 sha,而本 repo 的版本欄位如何決定沒有寫。
具體情境:使用者 `lumos update` 拉到修過的 mod,外掛仍是舊版;enforcement 只看「已安裝、近期有事件」,回 `active`,舊 mod 的事件格式(`v:1` 之外的欄位變動)與讀取端對不上也不會被抓到。⚠ 我沒有實測 `update` 對本機路徑市集的行為。
引句:「`claude plugin list --json` 已列出這個外掛時改跑 `claude plugin update lumos-ledger@lumos-toolchain`(讓重跑 install 能拿到新版 mod)」
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18608` `_sync_global_hooks` 是 update/bootstrap 唯一的全域同步,沒有外掛步驟。

### F10 知識與註冊的落點漏項
severity: minor
blocking: 否 — 屬於提交前閘會擋的同步項,但 spec 的落點清單沒寫,接手的人會多繞一輪。
spec 段落:範圍、落點。
問題與佐證:
1. 新指令 `lumos events` 要在指令說明表(`scripts/lumos:36716` 附近的說明字典)、argparse 與分派(`scripts/lumos:37485`、`:37788` 同型的位置)、`skills/lumos-project-notes/commands/INDEX.md` 登記;落點只寫了 `Systems/lumos-cli-read`。
2. enforcement 那一列的家寫成 `Systems/codex-harness`(一個 Codex 的節點),但該節點只在 DEP 行提到 enforcement 的 Codex 列;Claude 側的事件帳列、狀態值語意(`active/stale/unknown` 與分母規則)沒有對應的節點管,接手者不會去那裡找。
3. 本次還會動到 `docs/lumos-toolchain-knowledge/Systems/slim-*`(slim 的一行安裝與一行卸載是另一條安裝路徑,不會裝或移除外掛);spec 沒有說「只用 slim 安裝的人沒有事件帳」,誠實界線漏了這條。
4. `mods/` 與 `.claude-plugin/` 是新的頂層路徑,spec 沒有說明 `lumos init/vendor`、`slim` 建置、`anchor` 的名單是否要排除或收錄。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/docs/lumos-toolchain-knowledge/Systems/codex-harness.md:37` 只在 DEP 行提到 enforcement Codex 列。
file: `/Users/enzo/harness/lumos-toolchain-event-ledger/install.sh:63` `install.sh` 直接 `exec ... scripts/lumos install --force`,這條路徑要自己確認是否也會跑到外掛段。

### 實務隱患逐類
- 金流:無。只記回合與工具呼叫,不碰計費(同 spec)。
- 對外送出:無新增,但 `cmd` 前 500 字會進本機檔,spec 已承認。補充:`paths` 與 `cmd` 在 `.gitignore` 缺失時有外洩風險,見 F4(路徑寫錯處就沒有那份 `.gitignore`)。
- 不可逆:使用者層設定會被改;見 F7、F8(回退的順序與範圍)。
- 守衛面:不改既有 hook;enforcement 加列會碰測試計數,見 F6。
- 效能與併發:同一 repo 多場會談各寫各的 session 資料夾,無互相覆蓋;但 F3 的同一 session 內覆蓋成立。`claude plugin list` 約 0.9 秒由進場 hook 在「近 7 天沒事件」時才付,spec 已處理,F6 補的是測試端。

已讀,無 finding 的節:誠實界線(其中「型別檔只讀過」的清單已涵蓋 `session.end`、`$.process.run`、`$.fs.list`)、條款 S4–S5、S9 的測試名稱與計劃交叉引用(`Verification/2026-10-05_Claude-mod能力實測` 存在)。

總結:最嚴重 major;blocking 共 5 條(F1、F3、F4、F6、F7、F8 中 blocking 為「是」的共 6 條:F1、F3、F4、F6、F7、F8),minor 4 條(F2、F5、F9、F10)。

更正總結:blocking 共 6 條。
