severity: blocker

已讀全文。以下每條都附了查證出處。

### F1 席位標記的格式規則要求每段首字是 ASCII,實際約七成席名與四分之一資料夾名會被判成「沒有標記」
severity: blocker
blocking: 是 — 外掛在大多數真實派工上完全不啟動,而且不報錯(不擋就是 fail-open),等於沒有隔離。
引句:「任一段不合就當沒有標記(不擋;派工範本有測試盯著格式)」
- 規則 `[A-Za-z0-9][A-Za-z0-9._一-鿿-]*` 的首字只准英數,中文只准出現在第二字起。
- 我用同一條規則掃了 `governance/review-reports/` 的現況。
  - 342 個資料夾裡 87 個以中文開頭,例如「接手視圖」「推筆記認家」「檢核收緊五件」。
  - 2622 份席報告裡 1779 份的席名以中文開頭,例如「架構對齊-sonnet」「資安-sonnet」「併發與資源-sonnet」「邊界-sonnet」。
  - 把首字限制拿掉(`[A-Za-z0-9._一-鿿-]+`)後,資料夾全數通過。
- 手冊 §7.8 寫「席名固定寫 `資安-<模型>`」,以 `資安-sonnet` 派工,標記就被判格式不合。
- S10 的模板測試用「同一條格式規則」檢查,所以會對自己要求的標準席名紅燈。
- 修法:首字也放開中文,或改成禁字單(不含 `/`、空白、換行)。
file: `governance/review-reports/`(用上述正則實測,見上方計數);`skills/lumos-design-loop/templates.md:327`

### F2 `Grep`、`Glob` 的範圍規則會擋掉每一次「省略 path 的全 repo 搜尋」
severity: major
blocking: 是 — 審查席最常用的查證動作(在 repo 根目錄搜)幾乎全被誤擋,席位會被迫繞路或放棄查證。
引句:「`Grep`、`Glob` 的搜尋範圍若涵蓋這個卷證資料夾也擋」
- spec 規定 `path` 省略時看會談 cwd,而 cwd 通常是 repo 根。
- repo 根、`governance/`、`governance/review-reports/` 都「涵蓋」卷證資料夾,所以 `Grep path=<repo 根>` 或不給 path 一律被擋。
- spec 沒有說明可以用 `glob` 參數排除,也沒有說明改成「只在結果過濾掉卷證檔」。
- 修法:不整個擋,改成不擋範圍、擋結果,或要求 `path` 明確。

### F3 `Grep` 的 `path` 直接指到別席報告「檔案」就繞過了,因為檔案不「涵蓋」資料夾
severity: major
blocking: 是 — 同一條規則同時有誤擋(F2)與漏擋,漏的正是它要防的那件事。
引句:「`Grep`、`Glob` 的搜尋範圍若涵蓋這個卷證資料夾也擋」
- 失敗輸入:`Grep pattern="." path=governance/review-reports/<loop>/r1-通才.md`。範圍是單一檔案,不「涵蓋」資料夾而放行,回傳該報告全文。
- 相對的 `Glob pattern`(如 `governance/review-reports/<loop>/r1-*.md`,`path` 省略)也放行,因為 spec 只看「絕對路徑的 pattern」。
- 修法:對 `Grep`、`Glob` 的 `path`、`pattern`、`glob` 統一做「與卷證資料夾有交集」的判斷,不管相對或絕對、檔案或目錄。

### F4 「同輪 `rN-` 開頭的檔一律擋(除三種)」會擋掉真實卷證裡的共用材料
severity: major
blocking: 是 — 但 ⚠ 我沒有確認派工詞是否讓席位讀這些檔,所以誤擋的實際頻率未定。
引句:「檔名以 `<這席的輪次>-` 開頭、而且不是 `<輪次>-snapshot.*`、`<輪次>-dispatch.json`」
- 真實資料夾同輪的共用檔不只 snapshot 和 dispatch,還有 `r2-delta.patch`(39 份)、`r2-delta.md`(18 份)、`r2-delta.diff`(11 份)、`r1-sha256.txt`、`r1-roster-note.md`、`r1-snapshot-s1.md`(不符合 `snapshot.*`)、`r1-dispatch-common.md`、`r1-codex-prompt.txt`。
- 手冊規定第二輪起「只重審 delta」,若席位被指到 `rN-delta.*`,審查做不下去。
- 判準應改成「檔名是 `<輪次>-<席名>.md` 型的席報告,或 `-intake.md`」,而不是「`rN-` 開頭減三種」。
- 「自己的報告」只比對 `<輪次>-<席名>.md`,實際檔名常是 `通才-opus.md` 這類帶模型尾碼,標記席名若不帶模型,席位連自己的報告都被擋(影響較小)。
file: `governance/review-reports/條款綁測試算進度/`、`governance/review-reports/接手視圖/`(現有檔名)

### F5 路徑比對只做字串正規化,macOS 的 `/tmp` 連結、大小寫不分、上層目錄是連結都會讓「寫 repo」放行
severity: major
blocking: 是 — S1 的核心判斷在本專案實際環境下可被一般路徑繞過;S11 的暫存 repo 本身就會踩到。
引句:「路徑是連結時看它自己的位置,不跟連結(寫到 repo 裡的連結本身就算寫 repo)」
引句:「比對前正規化(去 `.`、`..`、重複斜線)」
- 實測:`git rev-parse --path-format=absolute --show-toplevel` 在 `/tmp/x` 建的 repo 回 `/private/tmp/x`,而 `/tmp -> private/tmp` 是連結。席位 `Write /tmp/x/f` 字串前綴不符而放行;S11 的暫存 repo(`/tmp` 或 `$TMPDIR`)兩條都會判錯。
- 沒有大小寫處理:APFS 預設不分大小寫,`/Users/enzo/Harness/…` 指到同一檔卻放行;Unicode NFC/NFD 差異同理(卷證資料夾名是中文)。
- 「不跟連結」只處理最後一段。上層目錄是連結(例如 `/tmp/l -> <repo>`,席位可用 `ln -s` 造,Bash 的 `ln` 不在擋單裡)時,`Write /tmp/l/f` 被判成 repo 外而實際寫進 repo。
- 修法:路徑與 repo 範圍都用 realpath 取上層,比對時折疊大小寫與 Unicode 正規化。
file: `scripts/lumos:21886`;`mods/claude/lumos-ledger/hooks/register.ts:44-46`(`pickMain` 直接吃 git 回的實體路徑)

### F6 Bash 切段只認「段首是 git」,環境變數前綴、子殼層、`bash -c`、全路徑、`--git-dir` 空白寫法都漏
severity: major
blocking: 是 — S3 的「含夾在後面的、前面帶全域選項的」只涵蓋最乾淨的寫法。
引句:「`Bash` 指令依 `&&`、`;`、`|`、換行切成各段,每段若是 `git` 指令,跳過全域選項」
- 漏擋的輸入:`GIT_AUTHOR_NAME=x git commit -m y`(環境變數前綴,spec 完全沒提)、`(git commit -m x)`、`$(git push)`、反引號、`{ git rm f; }`、`bash -c 'git commit …'`、`env git …`、`command git …`、`/usr/bin/git …`、`xargs git …`、`git -c alias.ci=commit ci` 與使用者 `~/.gitconfig` 別名。
- 全域選項解析有洞:`git --git-dir .git commit`、`--work-tree <路徑>` 的空白寫法與 `-Cpath` 黏寫,路徑被當成子指令就放行。
- 切分字元不含 `&`(背景),`||` 切出空段。
- 修法:真正的 shell 語法剖析,或整串指令掃 token,不靠段首比對。

### F7 擋單是封閉列舉,漏掉會寫 repo 的 git 子指令;spec 白話講的「開 PR」也沒覆蓋
severity: major
blocking: 是 — 白話層宣稱要防的事,有一半不在條款裡。
引句:「被審的文件如果藏了惡意指令,審查員可以被誘導去改 repo、開 PR」
引句:「而且沒有 `-C` 指到 repo 以外的路徑 → 擋」
- 沒列到:`git fetch`、`git remote add|set-url`、`git submodule update --init`、`git bisect`、`git symbolic-ref`、`git replace`、`git reflog expire`、`git hash-object -w`、`git commit-tree`、`git read-tree`、`git checkout-index`,以及直接寫檔的 `git diff --output=<檔>`、`git format-patch -o`、`git archive -o`、`git log --output=`。
- 「開 PR」靠 `gh pr create`、`gh api`、`curl`,完全不在規則內,上線後仍會成功。這與 nested-agent-permission-scope d4 的解禁條件「唯讀子代理隔離落地」直接相關;spec 要在「不做」明寫 `gh` 與網路指令是缺口,並說清這份隔離不構成解禁依據。
- `-C` 只看字串:`git -C /tmp --git-dir=<repo>/.git commit` 放行但實際寫 repo;`git -C $PWD commit`、`git -C "$(git rev-parse --show-toplevel)" commit` 無法在攔截點展開,spec 沒交代;多個 `-C` 疊用(spec 只說「另外記下」,單數)。

### F8 誤擋:`cd <臨時目錄> && git commit`、heredoc 內的文字行、引號內的分隔符
severity: minor
blocking: 否 — 擋的理由訊息會告訴席位改用 `-C`,換做法即可。
引句:「而且沒有 `-C` 指到 repo 以外的路徑 → 擋」
- `cd /tmp/exp && git init && git add . && git commit -m x`:沒有 `-C`,判成 repo 內而擋,實際 cwd 已不在 repo。
- Bash cwd 跨呼叫持續,席位前一次 `cd /tmp/x`,下一次裸 `git add` 也被擋,因為判定用「會談 cwd」。
- heredoc 內容以換行切段,`cat <<EOF > /tmp/repro.sh` 裡的 `git commit …` 行單獨成為 git 段被擋。
- 引號內有 `;`、`|`、`&&` 時錯誤切段,例如 `rg "a; git push" f`。

### F9 「啟動中」清單的等待沒有逾時、也沒寫出錯路徑要清掉,可能卡住同會談所有未登記子代理
severity: major
blocking: 是 — 一次中斷就能讓之後的辯方、implementer 等非席位子代理每次工具呼叫都被拖延。
引句:「先等它們都回報完再查表(子代理的工具呼叫一定在它啟動之後,等這一下不會互卡)」
- spec 只說「被拒則不記」,但 `next(e)` 丟錯(例如使用者中斷)時要不要從「啟動中」移除沒寫。範例 `register.ts:359-369` 的 `tool.call` 有 try/catch,這份 spec 的 `agent.spawn` 沒有等價交代。清單不清,就留下永遠不回報的項目。
- 等待條件是「同一會談還有啟動中的派工」,所有「查不到的子代理」(含沒有標記的辯方與 implementer)都被拖。型別檔說 hook 超過預算會被略過(fail-open),結果是每次呼叫白等到預算耗盡再放行。
- 「不會互卡」是未驗證的斷言:型別檔只說 `next(e)` 在子代理啟動後回,沒保證先前的 `tool.call` 不會在回前就來;S12 也沒涵蓋這個假設。
- 修法:清單項目用 try/finally 移除,加等待上限,只讓「發起方或標記有關」的呼叫等待。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:359-396`

### F10 `/clear` 後、背景席位的對應表會被清掉,席位從那一刻起無保護
severity: minor
blocking: 否 — 需要「席位仍在背景跑而編排者 `/clear`」的罕見時序,與已列的「熱重載會忘掉席位」同類。⚠ 型別檔沒說 `/clear` 時背景子代理是否還活著,無法確認。
引句:「會談結束(`session.end`)時清掉那個會談的對應」
- 型別檔說 `session.end` 的 `reason` 含 `/clear`;背景席位續跑時 `tool.call` 找不到表,視為非席位。此缺口沒出現在「誠實界線」。`--resume` 的會談表同樣為空。
file: `…/claude-code.d.ts:4262-4275`

### F11 範圍判定以「會談 cwd」為準,但子代理可有自己的 cwd;worktree 清單快取 10 分鐘
severity: minor
blocking: 否 — 要靠特定時序才發生。
引句:「判定以會談的 cwd 為鍵快取 10 分鐘」
- `AgentSpawnInput.cwd` 可讓子代理跑在別的目錄,相對路徑以「會談 cwd」補全,與子代理實際基準可能不同,兩個方向都會判錯。
- 快取期間內編排者新開的 worktree(`git worktree add ../x`)不在清單,席位寫進去放行。
- 審查對象是另一個 repo(消費專案、`--repo` 指到別處)時,寫入與 `git -C <那個 repo> commit` 都被當成「repo 外」放行。
file: `…/claude-code.d.ts:350-355`

### F12 安裝流程:既有使用者的市集已登記,新外掛是否可裝未驗
severity: minor
blocking: 否 — 失敗只影響 guard 本身且訊息會印出。⚠ 未實跑 `claude plugin install`,無法確認市集目錄在 install 時是否重讀。
引句:「任一支裝失敗只影響它自己」
- `_ledger_ensure_market` 在市集路徑相同時什麼都不做;已裝過事件帳的使用者若市集是舊快照,`plugin install lumos-guard@…` 可能找不到新外掛。spec 沒寫要不要先 `marketplace update`。
- `_ledger_fail_hint` 寫死「事件帳暫時停寫」,對 guard 失敗是錯訊息;`scripts/lumos:19998`、`:23851` 的說明也寫死只提 `lumos-ledger`。
file: `scripts/lumos:21886`、`scripts/lumos:22012`、`scripts/test_lumos.py:70179`

其餘各節:`回退`、`實務隱患`、`誠實界線` 已讀,無 finding。第 7 項(事件帳 `spawn` 改取 `parentAgentId`)與型別檔 `AgentSpawnInput`(有 `parentAgentId?`、無 `agentId` 欄位)相符,已讀,無 finding。

總結:最嚴重 blocker,blocking 8 條
