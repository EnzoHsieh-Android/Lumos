severity: major

# r1 回滾席審查:治理帳例行紀錄分流_計劃

立場:上線後要退回去、或上線途中出事。已讀全文;5 個 `[[連結]]` 與 `lands_in` 目標檔都存在。intake 已修的 7 條與存在類修正不重報。

## 逐節

- frontmatter / 白話 / 依據 / PRIOR-ART / RETIRE-IF:見 finding 7(REVISIT 量不到)。其餘已讀,無 finding。
- 盤點:「寫帳直接開檔的只有四支」核對屬實(`scripts/lumos:1358`、`scripts/lumos:1426`、`scripts/lumos:42423`、`scripts/lumos:43253`)。判定類讀者清單核對:`_codeloop_read_from_ledger`(`scripts/lumos:42313`)、dispositions 讀者(`scripts/lumos:43295`)、`_fix_check_events`(`scripts/lumos:12366`)、`_escape_released_loops`(`scripts/lumos:11141`)、`_loop_close_stamps`(`scripts/lumos:10198`)、改寫血緣(`scripts/lumos:1250`)都只讀版控帳且只讀左欄種類。我另查過沒有任何判定路徑讀右欄種類(grep `get("gate") ==` 對 drift-check/note-audit/note-reread/bound-tests/anchor/nodehome-check 無判定用途)。此段已讀,無 finding。
- 範圍:已讀,無 finding。
- 做法 / 分流表:finding 1、2、4。
- 做法 3、5、6(本機帳位置、寫不進去、非 git):finding 6。
- 實務隱患 / 回退:finding 5、8。
- 驗收條款:finding 3(S1 過了目的仍沒達成)。
- 天花板:已讀,無 finding(S18 的失真已自承)。

## Findings

1. 
severity: major
   blocking: 是——分流表的前提句寫錯,照表實作會把硬擋紀錄搬進本機帳,違反本案自己的規則一。
   spec 段:〈做法〉第 2 點與分流表右欄「doctor 各段 check-*(只由 doctor --ci 寫,全是提醒觀察)」。
   引句:「doctor 各段 check-*(只由 doctor --ci 寫,全是提醒觀察)」
   問題:check-* 不全是提醒。check-r 會寫 `kind: blocked`、`hard: True`(標了不可逆卻沒寫回退的硬擋),表上又不逐項列,實作者只能照「check- 開頭」整類分流,於是這類「擋人」紀錄從版控帳消失;同一份表裡 note-audit:blocked 反而留左欄,待遇不一致。
   佐證:file: `scripts/lumos:1908`、`scripts/lumos:1912`(`"gate": "check-r", "kind": "blocked", "hard": True`);file: `scripts/lumos:1394`(`_gate_event_or_warn` 的承諾是「擋人時一定有帳」)。

2. 
severity: major
   blocking: 是——繞道痕跡是否留版控帳,spec 自己在 m5 已裁定要留,表右欄卻放了一批同性質的。
   spec 段:分流表右欄「note-audit:skipped、skipped-env;note-reread:…skipped、skipped-env」「drift-check:…skipped-env、skipped」「nodehome-check、note-shape、delguard 全部」。
   引句:「note-audit:skipped、skipped-env;note-reread:reminded、covered、none、skipped、skipped-env」
   問題:左欄標題寫「繞道與自動放行的痕跡」且 code-loop skipped-env 因「工具承諾留在治理帳上」留左欄,但這些閘的使用者面承諾同樣是「會留帳」:LUMOS_SKIP_NOTE_SHAPE 單次跳過(note-shape skipped-env/skipped 在「全部」裡)、`note-audit skip`(要人給理由、「會留帳」,是人做的決定)、drift-check skipped-env。分流後這些繞道只存在做繞道那台機器的 `.git/` 裡,別台機器與 CI 看不到,也隨 clone/新 worktree 外的環境消失;印給使用者的「會留帳」變成「只留在你這台」。
   佐證:file: `scripts/lumos:28915`(「LUMOS_SKIP_NOTE_SHAPE=1 單次跳過(留帳)」)、`scripts/lumos:29585`、`scripts/lumos:29663`(note-shape skipped-env)、`scripts/lumos:44948`(「note-audit skip … 要理由、會留帳」)、`scripts/lumos:35581`(drift-check「單次略過(會留帳)」)、`scripts/lumos:43966`(spec 自己引為 m5 依據的同型承諾)。

3. 
severity: major
   blocking: 是——本案要解的症狀(工作目錄永遠髒)在本 repo 不會消失,驗收 S1 與 REVISIT 的目標都會落空。
   spec 段:〈白話〉「工作目錄永遠有一個沒提交的改動」、S1、REVISIT。
   引句:「平常提交推送完工作目錄就是乾淨的」
   問題:本 repo 版控了 7 本帳(`git ls-files docs` 列出 .usage-log、.canary-log、.bypass-log、.kill-log、.signoff-log、.escape-log、.governance-log)。唯讀的 `lumos show` / `lumos context` 每次都 append 版控的 `docs/.usage-log.jsonl`;canary 記帳寫版控的 `docs/.canary-log.jsonl`。我現在的 `git status` 就有 `M docs/.canary-log.jsonl`。S1 只斷言「版控帳(.governance-log.jsonl)位元組不變」,過了也不代表 git status 乾淨;雲端工作階段看圖譜就會再髒一次,REVISIT 的「被打斷次數」不會降到目標。spec 的〈不做〉也沒把這些帳劃為已知殘留。
   佐證:file: `scripts/lumos:16181`、`scripts/lumos:16197`、`scripts/lumos:16256`(唯讀指令寫 usage-log);file: `scripts/lumos:20553`(同一個症狀 2026-09-06 已因 update 被擋記過);`git ls-files docs` 輸出含 `docs/.usage-log.jsonl`。

4. 
severity: major
   blocking: 是——同一筆事件依哪一欄解讀會往不同帳寫,實作者無從決定。
   spec 段:分流表兩欄互相覆蓋。
   引句:「各閘的 fail-open(工具出錯自動放行的痕跡)」
   問題:左欄寫「各閘的 fail-open」留版控帳,右欄同時寫「bound-tests 全部」「nodehome-check、note-shape、delguard 全部」。`_gate_failopen` 對任一閘都寫 `kind=fail-open`,bound-tests 與 nodehome-check 都走它,所以 bound-tests:fail-open 同時在兩欄。另外 bound-tests 「全部」包含 `red-blocked`(`hard=True` 的真硬擋)。〈做法〉2 又說「不用萬用字元」,但「全部」「各閘」「check-」都是萬用字元,spec 內部對「不在表上一律進版控帳」與「全部」的優先序沒有定義。
   佐證:file: `scripts/lumos:43083`(`_gate_failopen` 寫 `fail-open`)、file: `scripts/lumos:42943`(bound-tests 走它)、file: `scripts/lumos:42464`(`"hard": kind == "red-blocked"`)。

5. 
severity: minor
   blocking: 否——只影響統計連續性與軟提醒,不改任何判定。
   spec 段:〈實務隱患〉回滾、〈回退〉。
   引句:「還原本案提交即可;本機帳留在 `.git/lumos/` 裡不影響任何判定」
   問題:判定確實不受影響,但「統計不斷」的承諾(〈相容〉)在回滾後不成立:上線期間的右欄事件全在 `.git/lumos/governance-local.jsonl`,舊版 `cmd_gov`、S18、`_lint_new_autopass_count`(`scripts/lumos:25543` 只讀版控帳)都不讀它;上線 N 週內回滾,右欄種類的近 N 週計數會從有料掉回只剩上線前的舊資料,`[retire:度量 … <= …]` 一類條件會被判成「該撤」(天花板 2 只講了跨機器,沒講回滾)。spec 說「不搬舊紀錄」,也沒給回滾時把本機帳併回版控帳的步驟(append-only JSONL 本可直接併),且〈回退〉把「刪本機帳」當清理選項,刪了就永久少一段統計。
   佐證:file: `scripts/lumos:3867`(S18 只讀版控帳)、file: `scripts/lumos:8161`(gov 只 load 版控帳)、file: `scripts/lumos:3822`(度量吃檔尾事件與最舊時間)。

6. 
severity: minor
   blocking: 否——spec 只差一句「用絕對路徑」,實作時才會踩,且踩到的後果是紀錄寫錯位置而非判定錯。
   spec 段:〈做法〉3。
   引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
   問題:該指令在 repo 根目錄回傳相對路徑 `.git`,在 `sub/` 回 `../.git`,只有 worktree 才回絕對路徑(我在暫存 repo 實測:根目錄 `.git`、子目錄 `../.git`、worktree `/tmp/gt/r/.git`)。`_gate_event` 與 `_append_governance_log` 的 git 呼叫都是 `git -C <repo_root>` 或 `cwd=vault`,而寫檔的 cwd 是行程 cwd;若把相對結果直接接在行程 cwd 上,hook 或 `lumos` 從別的目錄被呼叫時會在錯的目錄長出 `.git/lumos/` 或寫到別專案。spec 沒要求「對 repo_root 解析成絕對路徑」,S5 只測 worktree 一種情形,抓不到。
   佐證:file: `scripts/lumos:1418`(`cwd=str(vault)`)、file: `scripts/lumos:1330`(`_sp_run_text(["git","-C",...])`);暫存 repo 實測輸出如上。

7. 
severity: minor
   blocking: 否——是事後評估指標,不卡實作,但目前量不出來。
   spec 段:頭部 REVISIT 與 RETIRE-IF。
   引句:「數這 8 週雲端工作階段被「有沒提交的改動」打斷的次數」
   問題:這個次數來自雲端平台的提醒,不在任何本 repo 的帳裡;spec 也在〈不做〉明說不改那支提醒。沒有資料來源,2026-12-01 到期時無人能數,只能憑印象。本機帳還在 `.git/` 內,雲端工作階段的容器結束後消失,更不能當量測來源。
   佐證:spec 〈範圍〉「不改雲端平台那支「有沒提交的改動」提醒」;`scripts/lumos` 內無此提醒的記錄點(grep 無相關事件名)。

8. 
severity: minor
   blocking: 否——只影響本機磁碟與統計讀取成本,不影響判定。
   spec 段:〈實務隱患〉帳本成長。
   引句:「本機帳在 `.git` 裡,`git clone` 不帶,不會變成別人的負擔」
   問題:doctor 成長段(`scripts/lumos:2238`)只量版控帳,本機帳沒有任何上限或輪替;現在被分流走的正是量最大的例行事件(doctor-run、bound-tests、nodehome-check 每次提交/推送都寫),成長壓力整個轉進一個沒人量的檔。`lumos gov` 與 S18 改成合併讀之後要整檔讀它(`cmd_gov` 現在整檔 `read_bytes`,`scripts/lumos:8153`)。spec 沒給本機帳的大小守衛或「讀檔尾」要求,也沒說合併讀小工具要不要沿用 S18 的檔尾讀法(`_gov_tail_bytes`)。
   佐證:file: `scripts/lumos:2238`、file: `scripts/lumos:8153`、file: `scripts/lumos:3822`。

## 實務隱患逐類

- 版本混用(一台新版一台舊版、CI 新版本機舊版):舊版機器照舊把全部寫版控帳(超集),新版機器只把右欄寫本機;判定類讀者只讀版控帳左欄,兩種版本寫入的左欄格式不變,所以判定不分歧。CI 跑的是 vendored 的 `scripts/lumos`,讀的永遠是版控帳。統計面會出現「同一台機器之前在版控、現在在本機」的合併讀需求,spec 已寫兩本合併,無額外 finding。
- 帳本被手動刪 / 沒隨 clone 帶走 / git gc:本機帳在 `.git/lumos/` 的未追蹤路徑,`git gc` 不碰;新 clone 與每個雲端容器從空開始(見 finding 7、5);判定不受影響,成立。
- worktree 刪除:共用資料夾在主 `.git`,不隨 worktree 消失,成立;但路徑解析見 finding 6。
- 回滾:見 finding 5。
- 金流 / 對外送出 / 不可逆:同 spec 的「已排除」,核對屬實(兩本都只追加、不連網),無 finding。
- 守衛面:判定不讀右欄屬實;但分流表本身對「擋人 / 繞道」紀錄分類有誤(finding 1、2、4)。

最嚴重 severity:major;blocking 條數:4(finding 1、2、3、4)。
