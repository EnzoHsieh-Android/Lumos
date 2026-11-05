severity: major

我讀了 spec 全文,對照 `.github/workflows/ci.yml`、`scripts/hooks/pre-push` 第 544–584 行、`scripts/lumos` 的 `cmd_ci_wait` 和 `_ci_list_runs`。

### F1:合併前要 `lumos ci-wait` 綠,但 rc0 不等於綠
severity: major
blocking: 是。照字面實作會讓「全套已由 CI 驗過」的承諾落空,而這個承諾正是整份 spec 的安全前提。
spec 段落:〈做法〉第 3 點訊息、〈實務隱患〉守衛面。
引句:「合併前要 `lumos ci-wait` 綠」
問題:`cmd_ci_wait` 在很多情況下回 rc0 卻沒有綠。
- 未定(cancelled 等)、逾時(預設 1800 秒)、no-run、disabled、unavailable(gh 失敗時 fail-open)全部 rc0。
- AI 看 rc0 就合併,是這個流程最可能的走壞方式。
- 這些非綠情況原本由本機全套兜底,現在本機不跑全套,就沒有東西兜了。
- spec 沒有定義「綠」是 verdict 等於 green,也沒要求印出的訊息或腳本據此判斷。
佐證:
- file: `scripts/lumos:63063`(`cmd_ci_wait` 的 docstring:「綠 rc0/紅 rc1/未定·逾時·no-run·工具缺席 rc0」)
- file: `scripts/lumos:62933`(`_CI_GREEN` 只含 success、neutral、skipped)

### F2:cancel-in-progress 加上「代碼審通過後再提交一個帳本提交」,會讓被等的 sha 永遠是 cancelled
severity: major
blocking: 是。這條讓上一條的 rc0 陷阱從偶發變成每個過審功能的常態。
spec 段落:〈範圍〉做、〈做法〉第 2 點。
問題:
- 專案規矩是過代碼審後必須再推一個 `chore(lumos): 記錄代碼審通過` 帳本提交。這是新推送,會取消進行中的 PR 全套 CI。
- 第一次推送的 sha 因此永遠只有 cancelled。
- 在這之前,本機全套是被取消 CI 的備援;現在不是了。
- 手上若記著功能提交的 sha 去跑 `lumos ci-wait`,拿到的是 undetermined(rc0)。
- 帳本提交本身又因為 PR 事件一律全套,CI 再重跑一次。所以「省時間」只省在本機。
- spec 沒說要等的是推送後的最新頂端 sha,也沒說被取消後要重等或重跑。
佐證:
- file: `.github/workflows/ci.yml:19`(`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`)
- file: `scripts/lumos:63063`(`_ci_list_runs` 用 `--commit sha` 過濾,舊 sha 查到的只有被取消的那份)

### F3:推功能分支不一定有 CI 在跑,「全套由 PR 的 CI 跑」只在已開 PR 時成立
severity: major
blocking: 是。訊息會誤導,本機和 CI 兩邊都沒有全套。
spec 段落:〈做法〉第 3 點訊息、〈實務隱患〉守衛面。
引句:「全套由 PR 的 CI 跑」
問題:
- `ci.yml` 只在 `push` 到 main(或 tag)和 `pull_request` 時觸發,功能分支單純被推上去不會跑 CI。
- 很多會談是先推再決定開不開 PR,或先推了就回報完成。這時本機只跑小子集、CI 完全沒跑。
- 這個訊息會讓 AI 或使用者以為有人在跑全套。
- spec 沒要求訊息先檢查有無開啟的 PR,也沒有「沒 PR 就不降級」的條件。
佐證:
- file: `.github/workflows/ci.yml:4-9`(`on:` 只有 push 到 main、tag 和 pull_request)

### F4:使用者全域 CLAUDE.md〈推送前〉跟新行為衝突,Q1 又被擱在「待查」
severity: major
blocking: 是。上線瞬間規則就互相矛盾,而 AI 會讀到全域規則。
spec 段落:`pending_questions` Q1、〈做法〉第 5 點說明文字同步。
問題:
- 全域規則第一條寫「不要只跑針對性測試或守衛測試就推」,現在本機閘本身就只跑子集,按字面讀就是「推了就違規」。
- 同一節還寫「全套測試在對話裡跑不完時,……要等 CI 結果出來才回報完成」。這一條本來就和新做法相容,可以引為依據。
- 〈做法〉第 5 點只改專案範本、專案 CLAUDE.md、AGENTS.md,沒有動全域檔,也沒有交付時機。
- 全域檔在 repo 外,不能由 repo 內的 S4 測試守住。
- 記憶裡的「推前本機跑完整閘」一條同理會過期,spec 沒提。
佐證:file: `/Users/enzo/.claude/CLAUDE.md`〈推送前〉第一、二條。

### F5:多會談同時合併沒有合併佇列,PR 的 CI 測的是過時的合併結果
severity: minor
blocking: 否。多數情況由推到 main 的 CI 事後補抓,但 spec 的守衛面應該寫明。
spec 段落:〈實務隱患〉併發。
問題:
- 隱患只寫「本機負載比現在低」,沒談兩個會談的 PR 各自綠、先後合併後互相衝突。
- PR 事件測的是建立時的合併結果,不會因為 main 前進而重測。
- 以前本機全套是在最新本機 main 之上跑的,現在這個保險沒了。
- 事後只剩推到 main 的 CI 全套(每個提交各自一組,不被取消)。紅的時候 main 已經壞了,而且沒有人被通知。
佐證:file: `.github/workflows/ci.yml:19-21`(推到 main 以 sha 為群組,不取消)。

### F6:紅燈沒有主動通知,RETIRE-IF 的度量又只計入有跑過 `ci-wait` 的 PR
severity: minor
blocking: 否。度量偏誤和 Q2 懸而未決的組合是風險,但 spec 已把 Q2 列為待決。
spec 段落:RETIRE-IF、Q2。
引句:「`lumos ci-status` 記進治理帳的 PR 結果,對照同提交的推送前檢查紀錄」
問題:
- 帳只在有人跑 `ci-wait` 時才寫。沒等就合併的 PR 不在帳裡,紅燈不被計入。
- 結果會低估「CI 紅、本機綠」的比例,退場條件會偏晚觸發。
- 掛鉤是否留有同提交的推送前檢查紀錄,spec 沒查證也沒指向。
- 〈實務隱患〉說分支保護是補救,但 Q2 沒有期限,在那之前沒有任何機制擋「沒綠就合併」。
佐證:file: `scripts/lumos:63063`(`ci-wait` 才呼叫 `_ci_record` 寫帳)。

### F7:功能分支的判定只認 `main`/`master`,跟 lumos 自己認的主線不一致
severity: minor
blocking: 否。多數情況沒影響,但 spec 沒說明排除的理由。
spec 段落:〈做法〉第 1 點。
引句:「目的是 `refs/heads/<名>` 而且名字不是 `main` 或 `master` → 這個 ref 算功能分支」
問題:
- `release/*`、`develop` 之類的長壽分支會被當功能分支。
- 這類分支的 CI 只在 PR 或 push 到 main 時才會跑,推上去本機和 CI 都不跑全套。
- `_push_mainlines` 的候選還包含 `refs/remotes/<遠端>/HEAD` 指向的那條,語意比硬寫兩個名字寬。
- spec 沒有說明為何不沿用,也沒有把「其他長壽分支」列進〈不做〉。
佐證:file: `scripts/lumos:65263`(`_push_mainlines`)。

### 其他節
- 〈現況〉〈範圍〉〈驗收條款〉〈回退〉:已讀,無 finding。
- 〈實務隱患〉的金流、對外送出、不可逆三類已排除,理由成立。

整份最高等級為 major,共 4 條 blocking(F1–F4)、3 條 minor 不擋。
