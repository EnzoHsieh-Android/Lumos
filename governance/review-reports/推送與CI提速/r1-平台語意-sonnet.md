severity: major

我沒能做到的事先講:Bash 守衛擋了 `gh api`,所以 Actions 紀錄、`branches/main/protection` 與 rulesets 我都沒查到。下面的平台宣稱只有「讀 spec 與 `ci.yml`」和「已知的 GitHub 文件行為」當佐證,凡是沒實測的我都標明。

**1. PR 與主線測的環境不同,「消掉 2026-10-04 根因」的說法不成立**

severity: major
blocking: 是

引句:「正好消掉那次的根因(使用者 2026-10-14 裁定同意改這條)」

- 該 PITFALL 的根因是測試取「主線 tip 與 tip~1」當範圍(file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:25`)。
- 測試找主線靠 `main@{upstream}`(file: `scripts/test_lumos.py:17987`、`:40886`、`:41006`)。
- PR 事件 checkout `head.sha` 時,`ci.yml` 的「補本機 main」步驟(`git branch --track main origin/main`)補出來的 `main` 是舊的基底頂端,不是被測提交。
- 所以 PR 的 CI 看到的「主線 tip、tip~1」是基底與基底的父提交。
- 快轉後主線 tip 才變成被測提交,tip~1 才是舊基底,範圍並不相同。
- 測試若用 `main..HEAD` 當範圍,PR 裡是整個 PR,快轉後主線上是空範圍。
- 被測提交的 SHA 相同,但「測試看到的 git 環境」不同。這類依賴主線位置的測試,PR 綠不保證主線綠。
- 這正是 spec 想靠略過主線重跑來省掉的那一次風險。
- 建議:
  - 要嘛 PR 的 CI 把本機 `main` 補成「被測提交的父提交」,模擬快轉後的狀態。
  - 要嘛列舉所有讀主線位置的測試,證明它們對這個差異不敏感。
  - 否則 RETIRE-IF 的「主線重跑變紅」會在上線後才被踩到。

**2. 主線的排隊中 run 會被後來的 run 取消**

severity: major
blocking: 是

引句:「只有 PR 事件 `cancel-in-progress`,推到 main 不取消。」

- `cancel-in-progress: false` 並不等於「不取消」。
- GitHub 文件規定同一個 concurrency 群組裡「已排隊(pending)的 run 會被新的取代」,只有進行中的 run 受 `cancel-in-progress` 管。
- 文件:https://docs.github.com/en/actions/using-jobs/using-concurrency
- 若主線群組只用「事件加分支」,連推三次 main 時,第二次推送的 run 會被第三次取消。
- 那個提交就沒有任何主線 CI,後盾閘(code-loop、note-shape、drift check)也沒跑。
- 這和「併發:取消只作用在同一個 PR 分支的舊工作,主線永遠跑完」直接矛盾。
- 現況的 `ci.yml` 完全沒有 concurrency,所以不會發生;spec 加進去才引入。
- 建議:push 事件的群組鍵要帶 `github.sha`(或 `github.run_id`),讓每個主線 run 各自一組。
- 另外,`cancel-in-progress` 寫成 `${{ github.event_name == 'pull_request' }}` 語法可行。
- 但群組鍵要把 PR 與 push 分開,PR 用 `github.head_ref`。`github.ref` 在 PR 事件是 `refs/pull/N/merge`,也可以,只是 spec 沒寫清楚用哪個。

**3. 「查同一提交已成功的 PR run」缺少條件,無法保證那次跑過全套**

severity: major
blocking: 是

引句:「查同一個提交(`head_sha` 等於這次推送的提交)有沒有已成功完成的 PR 事件 CI;有就把範圍判成 `skip`」

- 可用的端點是 `GET /repos/{o}/{r}/actions/runs?head_sha=…&event=pull_request&status=success`,另有 `workflow_id` 與 `branch` 可篩。pull_request run 的 `head_sha` 是 PR 分支頂端,不是合成合併提交,這點與 spec 一致。
- 但 spec 沒寫以下區分:
  - **篩 workflow**:不篩 `workflow_id` 或路徑,同 SHA 上別的 workflow 的成功 run 也會命中。
  - **篩目標分支**:基底不是 main 的 PR(例如疊在另一個分支上的 PR),同一個 SHA 會有 run,但測的是別的基底。
  - **確認真的跑了全套**:`conclusion=success` 只代表整個 run 成功。
    - 目前 `ci.yml` 對 PR 事件永遠判 `full`,所以暫時成立。
    - 但 spec 沒要求去查那個 run 的 jobs,確認 shards 的結論是 success 而不是 skipped。
    - 日後若 PR 也開了文件子集或 `skip`,誤判不會被察覺。
  - **重跑**:`run_attempt` 重跑失敗的 job 後,run 的結論是最新一次的結果,多次 run 取哪一個沒規定。
  - **取消的 run**:被取消的 run 結論是 `cancelled`,`status=success` 已排除,這點沒問題。
- 權限:`ci.yml` 頂層是 `permissions: contents: read`,其餘權限全為 none,所以 prep 必須明確加 `actions: read`,spec 有提到。
- 另一點:`GITHUB_TOKEN` 查 API 的失敗(含 rate limit)一律跑全套,這個保守方向是對的。
- 建議:條款 [S4] 補上篩 workflow 檔名、`base`/`branch`、查 jobs 的 shards 結論,並規定同一 SHA 多個 run 時「只要有一個 run 的 shards 全數 success 就算」。

**4. `git push <sha>:main` 會讓 PR 自動變已合併,但它不是文件保證,主線保護也未驗**

severity: minor
blocking: 否

引句:「GitHub 會自動把 PR 標成已合併」

- 實務上,分支頂端提交進了基底分支,GitHub 會把開啟中的 PR 標成 merged,這是長期已知的行為。
- 但官方文件沒有逐字保證,而且只對「PR 仍開啟、基底是 main」成立。
- 我沒能查 `branches/main/protection` 與 rulesets(`gh` 被擋)。
- 若主線有保護(要求 PR、要求狀態檢查),直接推 main 會被拒。
- 反之沒保護,spec 也沒說要不要保留「PR 綠才准推」的機械擋,這步完全靠手冊紀律。
- 建議:spec 加一條上線前實測的驗收(開 PR、快轉推、看 PR 狀態與 `merged_at`)。

**5. 推 main 的本機 pre-push 全套會讓「全套只跑一次」打折**

severity: minor
blocking: 否

引句:「推 main、tag 或明示環境變數時才跑全套。」

- 這句是下一階段才交付。
- 但本階段的快轉就是「推 main」,現行掛鉤對非輕量改動會再跑一次本機全套(spec 現況寫約 5 到 10 分)。
- 所以本階段實際是本機一次、PR 的 CI 一次、快轉時本機又一次。
- 另外掛鉤是否正確解析 `<sha>:main` 這種「來源不是分支名」的 refspec,spec 沒說。
- 建議:至少寫明這是已知的暫時狀態,並加上「回頭條件」。

**6. 其他平台語意的查證結果**

severity: minor
blocking: 否

- **`github.sha` 的殘留用法**:`ci.yml` 裡的 `SHA: ${{ github.sha }}` 只出現在 push 事件才執行的步驟(prep 的範圍判斷用在 `github.event_name = push` 的分支裡、gates 的四個 push 步驟)。
  - 改測 `head.sha` 後 PR 事件沒有任何步驟還在用合成合併提交,「補本機 main」「文件子集判斷」「code-loop gate」都不受影響。
  - 這部分我判不影響,理由是它們全都被 `if: github.event_name == 'push'` 圍住。
- **快轉後主線提交就是被測提交**:`git push` 快轉不會改寫提交,所以主線的 SHA 與 PR 的 `head_sha` 相同。
  - 這是 git 的語意,GitHub 不會改寫。只有按鈕的 squash 或 rebase 合併才會產生新 SHA。
  - 該 SHA 上的 check 本來就掛在提交上,因此不是問題。
- **checkout 行為**:`actions/checkout@v4` 在 `fetch-depth: 0` 且 `ref: <head.sha>` 時,取出的是分離 HEAD。
  - 同 repo 的 PR 分支 SHA 都可由 `refs/heads/*` 抓到,不會壞。
  - 分離 HEAD 會讓 `--branch`、`git rev-parse --abbrev-ref HEAD` 類的呼叫行為與現況不同,值得跑一次確認。
  - 這些在目前 `ci.yml` 裡只出現在 push 事件的步驟。
- **「先 rebase 再推再等 CI」會形成追逐**:rebase 會換 SHA,舊 PR 的 CI 結果對新 SHA 作廢,主線每動一次就要重等約 12 分。
  - 單人場景影響小,spec 的「由 git 擋」說法成立。

最嚴重等級:major;blocking 共 3 條(第 1、2、3 條)。
