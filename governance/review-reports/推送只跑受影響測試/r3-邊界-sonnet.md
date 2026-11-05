severity: major

**Finding 1**
severity: major
blocking: 是(照 spec 字面做,機械放行的「合併前 ci-wait 為綠」可以只代表文件子集綠,漏掉合約)
段落:做法 1、實務隱患「守衛面」、RETIRE-IF 與現況的 `lumos ci-wait`。
問題:CI 的範圍判定是每次推送自己的 `BEFORE..SHA`,不是整條分支對主線。`ci-wait` 是按提交編號查 run,不是按分支。本 repo 的收尾慣例是功能提交之後再推一個只動帳本的提交,而且 spec 自己提到會有「之後再推的帳本提交」。帳本提交只改 `docs/.governance-log.jsonl`,屬於記帳檔,所以 prep 判成 docs,只跑文件子集。分支頂端的 run 因此是快速變綠的文件子集。功能提交那次全套若是紅的或還沒跑完,`lumos ci-wait` 對頂端提交看到的卻是 green。spec 把「合併前 ci-wait 判定要是 green」當成唯一守衛,而且 main 沒有分支保護(Q2 待查),所以這個漏洞沒有任何機械守衛。
同樣的前提也讓 RETIRE-IF 的「紅的比例」被稀釋,因為文件子集的 run 會算進分母。
引句:「合併前 `lumos ci-wait` 的判定要是 green(rc 0 不等於綠)」
佐證:
- `.github/workflows/ci.yml:70-85`:`python scripts/lumos pitfalls --diff "$BEFORE..$SHA"`,docs 就只跑文件子集。
- `scripts/lumos:62971-62990`:`_ci_list_runs` 用 `gh run list --commit <sha>`。
- `git show --stat 11952c06f`:帳本提交只改 `docs/.governance-log.jsonl`。
- `scripts/lumos:61721-61728`:`_DOCS_ONLY_NEVER` 只涵蓋 `governance/anchor-baseline.json` 與 `governance/code-loop/`。
- 修法方向:CI 在非 main 的 push 一律全套,或範圍改成對主線的 merge-base。

**Finding 2**
severity: major
blocking: 是(照字面實作,main 可能被當功能分支而跳過本機全套)
段落:做法 2、S4。
問題:`pushed_mainline` 的判法完全靠候選清單裡「找得到的」追蹤 ref。候選為空,或候選指不到被推那條,結果就是 false。「git 查詢失敗 → true」只涵蓋 git 跑壞,不涵蓋「查得到、沒有候選」。
- 推 `main` 到一個尚未 fetch 的新遠端,或 fork 遠端首推 main:`refs/remotes/fork/main` 不存在,`fork/HEAD` 沒設,`main@{upstream}` 指向 origin/main,與 `refs/remotes/fork/main` 不相等。候選裡沒有等於被推那條的,結果 false,main 被降成 light。
- 遠端 HEAD 未設,`main@{upstream}` 與 `master@{upstream}` 都沒設,遠端 `main` 追蹤 ref 又被刪或過期:候選清單為空,同樣 false。
- `_push_mainline_full` 回 `(None, False)`(遠端 HEAD 不是捷徑)時,該候選被默默略過,不算失敗。
- 同檔已有先例:`_NOTE_REREAD_MAINLINE_NAMES = ("main", "master")`。它是為了「查候選失敗或本機把候選刪掉時,推 main/master 照樣算主線」而加的(代碼審 r4 資安 1、邊界 1)。spec 沒沿用,也沒有對應測試:S4 只列「含遠端 HEAD 指的分支」、其他分支、標籤三種。
- 修法方向:固定名 `main`/`master` 與候選取聯集,同時補「候選為空」「fork 首推 main」兩個測試。
引句:「被推的 ref 對應的那條(`refs/remotes/<--push-remote>/<被推分支>`)等於其中任一 → true」
佐證:`scripts/lumos:65263-65294`(`_push_mainlines`)、`scripts/lumos:53729-53752`(`_note_reread_mainline_names`)。

**Finding 3**
severity: minor
blocking: 否(影響一部分提交的 CI 排程,守衛仍在)
段落:做法 1 的 concurrency。
問題:群組鍵 `ci-push-<sha>` 只含提交編號,不含分支名。同一個提交被推到多個 ref 時共用一組:功能分支推送後 fast-forward 合進 main、同一個提交又打 tag、一次推多個指向同一提交的分支。`cancel-in-progress: false` 時同組只保留一個排隊中的 run,新的會取代舊的排隊 run。結果是 main 上「合併後那一次」可能完全沒跑,tag 的 `security_tag` 也可能被擠掉。spec 的 PRIOR-ART 把「推到 main 的 CI 全套照舊是合併後那一次」當成第二層保證,這一點受影響。fast-forward 時提交已經綠過,所以多半無害,但 spec 沒承認這個情境。
引句:「push 事件以提交編號分組、不取消,之後再推的帳本提交不會取消功能提交那一次」
佐證:`.github/workflows/ci.yml:19-21`。

**Finding 4**
severity: minor
blocking: 否
段落:做法 3 的版本錯開、實務隱患「版本錯開」。
問題:新掛鉤對舊 lumos 會帶 `--push-remote` 與 `--pushed-ref`。舊版 argparse 不認得,`pitfalls` 回非 0,掛鉤用 `|| true` 吞掉,`pf_json` 變空。spec 只寫「舊版沒有這個欄位」,實際是旗標被拒。後果是這台機器上純文件的推送也退回全套,比現況更慢,不只是功能分支。這個方向仍然安全,但 spec 的描述與行為不符。
引句:「版本錯開:新掛鉤配舊 lumos(沒有 `pushed_mainline`)→ 全套」
佐證:`scripts/hooks/pre-push:540-545`(`pf_json=... || true`,空則 `_suite_this="full"`)。

**逐項走過,沒有新增洞**
- 只刪分支:`pre-push:481-483` 遇到 local_sha 全零就 `continue`。若整次推送只有刪除,`_SUITE_SEEN` 為 0,維持全套,與 spec 現況段一致。刪除加功能分支同時推時,刪除不進判定,功能分支降級,行為可接受。
- 一次推十幾個分支:每個 ref 各呼叫一次 `pitfalls`,成本線性增加,沒有正確性問題。CI 會各觸發一次全套,吃 runner 併發。spec 的機器時間段沒提這種批次推送,但這只是用量問題。
- 特殊字元的分支名:掛鉤用 `pp_q` 引號包住 `$_rref`,lumos 端用字串前綴去掉 `refs/heads/`,沒有 shell 注入面。分支名帶斜線沒問題。
- force push:`pushed_mainline` 與舊值無關。CI 端 `git cat-file -e "$BEFORE^{commit}"` 失敗會落到全套,方向保守。force push 到 main 判 true,維持全套。
- 標籤:不是 `refs/heads/` 就判 true,不降級。這個方向正確,S4 也有覆蓋。
- dependabot 或其他自動分支:`push` 加 `pull_request` 會各跑一次,spec 已承認。權限只有 `contents: read`,沒有新的權限面。

實務隱患逐類:
- 守衛缺口:見 Finding 1、2。
- 資源:見 Finding 3 與批次推送。
- 版本錯開:見 Finding 4。
- 金流、對外送出、不可逆:同意 spec 的「已排除」。

總結:最嚴重等級為 major,會擋的問題 2 條(Finding 1、2),另有 2 條 minor 不擋。
