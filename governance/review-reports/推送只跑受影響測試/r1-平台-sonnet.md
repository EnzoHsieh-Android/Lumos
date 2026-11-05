severity: major

平台語意共 5 條:3 條會擋,2 條不會擋。我實測了 git 的 `@{upstream}` 解析。GitHub Actions 的行為(permissions、`GH_TOKEN`、標籤、合併方式、schedule)沒有在本席連網核對,是依 GitHub 官方文件記憶寫的,每條附文件網址,請收貨時對一次。

### 1. notify 工作的權限與紅測試名來源沒講清楚
severity: major
blocking: 是(照字面實作,notify 取不到「紅的測試名」,S5 的內文要求做不出來)
段落:做法 4 末條、驗收條款 S5
引句:「這個工作要 `issues: write` 權限,只給它,不給其他工作。」
- 現行 `ci.yml` 頂層是 `permissions: contents: read`。工作層一寫 `permissions:`,就整個取代頂層。notify 只寫 `issues: write` 的話,`contents` 等其餘權限全變 none。
- notify 要 checkout 來重算子集(做法 5),所以至少要 `contents: read`。
- 「紅的測試名」在別的工作(shards)的日誌裡,notify 拿不到。
  - 要靠 `gh run view --log-failed` 或 API 讀日誌,就還要 `actions: read`。
  - 要靠 artifact,就要改 shards 去上傳,spec 沒提。
- spec 沒寫用哪一條路,也沒寫 `needs: [prep, shards, gates]` 搭配 `if: always() && contains(needs.*.result,'failure')`。不寫的話,上游紅了 notify 會被連帶略過,Issue 永遠開不出來。
- 官方文件:https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#permissions(工作層覆蓋頂層、沒列的權限設為 none)。
- 佐證:`.github/workflows/ci.yml`:14(頂層 permissions)

### 2. gh 開 Issue 的兩個前置條件沒寫,安全網自己可能失靈
severity: major
blocking: 是(第一次主線紅時 notify 自己先紅,Issue 開不出來,而且沒人知道)
段落:做法 4
引句:「新工作 `notify` 用 `gh issue create` 開 Issue」
- `gh` 在 ubuntu-latest runner 上預裝,可用。但它不會自動用 `GITHUB_TOKEN`,步驟要寫 `env: GH_TOKEN: ${{ github.token }}`,否則回 auth 錯誤。
  - 文件:https://docs.github.com/en/actions/using-github-hosted-runners/using-github-hosted-runners 、 https://cli.github.com/manual/gh_help_environment
- `gh issue create --label main-red` 在標籤不存在時會直接失敗(「could not add label」)。`main-red` 與 `subset-miss` 是新標籤,spec 沒寫誰建、何時建。
  - 要嘛 notify 先 `gh label create ... || true`,要嘛上線前手動建。
- 「同標籤已有開著的 Issue 就改成留言」要靠 `gh issue list --label main-red --state open`,這同樣要標籤已存在。
- 用 `GITHUB_TOKEN` 開 Issue 不會觸發其他 workflow(文件:https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)。本 repo 也沒有 `issues` 觸發的 workflow(`grep` 過 `.github/workflows/`),這點無風險。

### 3. 漏抓統計用「第一個父提交」,只在合併提交成立
severity: minor
blocking: 否(目前 repo 用 merge commit 合併,近期 `git log` 全是 `Merge pull request #…`;標籤判錯只影響 RETIRE-IF 的計數,且 spec 已要求撤除前由人看過)
段落:做法 5
引句:「notify 工作拿合併提交的第一個父提交到合併提交這段(就是整個 PR 的改動)重算一次」
- merge 方式:第一個父提交是合併前的 main,成立。
- squash 方式:單一新提交,父提交是舊 main,也成立。
- rebase 方式:PR 的多個提交逐一接在 main 後面,`github.sha` 只是最後一個。`sha^..sha` 只剩最後一個提交,會把子集算小,讓更多紅被標成「子集漏抓」。
- 更穩的口徑是 push 事件自帶的 `github.event.before..github.sha`。這三種合併方式都等於「這次推進 main 的全部內容」。
  - 現行 ci.yml 的 code-loop、note-shape 等步驟早就用這個。
  - 直推 main 的多提交也一併涵蓋。
- 官方文件:https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges
- 佐證:`.github/workflows/ci.yml`:217 一帶(BEFORE..SHA 的現行寫法)

### 4. PR 事件的分岔點沒說用哪個提交當「PR 頭」
severity: major
blocking: 是(照字面做,PR 範圍可能算錯、或工作需要的輸入來源不存在)
段落:做法 4 prep
引句:「範圍 `origin/main` 與 PR 頭的分岔點..PR 頭,目的 ref 視為功能分支」
- `pull_request` 事件預設 checkout 的是 `refs/pull/N/merge` 這個合併預覽提交。它不在任何分支上,`github.sha` 就是它。ci.yml 現有註解(「PR 事件取出的是不在任何分支上的合併提交」)已經踩過。
- 真正的 PR 頭是 `github.event.pull_request.head.sha`(也等於合併預覽提交的 `HEAD^2`)。spec 沒寫取哪個。
  - 若誤把 `github.sha` 當「PR 頭」,`merge-base(origin/main, 合併預覽)` 等於 main 頂端,範圍剛好是 PR 的改動,看似能用。
  - 但「目的 ref」要的是頭分支名(`github.head_ref`),跟「是不是 main/master」的比對是兩回事。fork 來的 PR,頭分支名可能就叫 `main`,會被誤判成直推 main 而退回全套。這不是安全問題,是省不到時間。
  - 合併預覽提交是 GitHub 在建立或更新 PR 時算的。base 後來前進時,它不一定即時重算,所以 PR 的 CI 看到的 main 可能比當下舊。
- 建議寫明:範圍用 `${{ github.event.pull_request.base.sha }}...${{ github.event.pull_request.head.sha }}`(三點),目的 ref 用固定值(例如 `refs/heads/pr-head`)。不要靠分支名判斷。
- 文件:https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#pull_request(含 GITHUB_SHA 是合併提交、GITHUB_REF 是 `refs/pull/N/merge`)
- 佐證:`.github/workflows/ci.yml`:42 附近的註解

### 5. 表態閘改認遠端主線:措辭有歧義,且沒說追蹤分支新鮮度
severity: minor
blocking: 否(S6 的測試場景與現況吻合,日常路徑可行;新鮮度問題只讓範圍偏大,結果是多審而不是漏審)
段落:做法 7、S6
引句:「取跟頂端分岔點最新的那個,都沒有才用本機 main。」
- 實測:在臨時 repo 設 `branch.main.remote=origin`(遠端其實叫 `Lumos`)、`branch.main.merge=refs/heads/main`,再跑 `git rev-parse main@{upstream}`。得到 `fatal: upstream branch 'refs/heads/main' not stored as a remote-tracking branch`,rc=128。spec 描述的現況成立。
- `@{upstream}` 是靠 `branch.<name>.remote` 與 `remote.<remote>.fetch` 把 merge 的 ref 映射到 `refs/remotes/...`。映射不上就報錯。`_lens_full_sha` 會吞掉這個錯,所以才會退回本機 main。
- 「分岔點最新」可以有兩種讀法:`merge-base(頂端, 候選)` 最晚的,或候選本身最新。兩種可能選到不同的 ref,請寫成一種。
- 遠端追蹤分支只在 `git fetch` 或對那個遠端 `git push` 時更新。pre-push 掛鉤沒有 fetch(`grep fetch scripts/hooks/pre-push` 只有一句註解)。別的會談或 GitHub 上合併後,追蹤分支仍是舊的,本機 main 落後的問題只會從「落後本機 main」換成「落後追蹤分支」。S6 的測試把「遠端 main」造得夠新,抓不到這個差異。
  - 掛鉤的第一個參數就是正在推的遠端名,優先用它的 `refs/remotes/<該遠端>/main`,比盲掃所有候選準。
  - 或明寫「不 fetch,新鮮度由使用者負責」。
- 文件:https://git-scm.com/docs/gitrevisions(`@{upstream}` 定義)
- 佐證:`scripts/lumos`:65710(`_mainline_ref`)

### 其他假設的查證結果
- **schedule 事件的 ref/sha 與 before**:`github.event.before` 為空,`github.sha` 是預設分支最新提交,`ref` 是預設分支。ci.yml 現有 `[ "${{ github.event_name }}" = push ]` 的守衛,在 schedule 下落到全套,這點 spec 說對了。
  - `prep` 的條件 `github.ref_type == 'branch'` 在 schedule 下成立,能跑。
  - 其他步驟都有 `if: github.event_name == 'push'`,schedule 時會略過。
  - 文件:https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule 。
  - 注意:schedule 只在預設分支上的 workflow 檔生效。排程可能延遲,整點(`0 19`)尤其壅塞,偶爾被丟棄。公開 repo 60 天沒活動會被停用。這些屬可接受風險,spec 可以補一句。
- **concurrency 鍵**:`ci-${{ event_name }}-${{ pull_request.number || sha }}`。schedule 下是 `ci-schedule-<sha>`,跟同一提交的 push 事件不同組,不會互相取代。`cancel-in-progress` 對 schedule 是 false,多個排程不會被中途取消。已讀,無 finding。
- **GITHUB_TOKEN 開 Issue 的連鎖觸發**:不會觸發其他 workflow(見上第 2 條連結)。無風險。

總結:最嚴重等級為 major,共 5 條,其中會擋的 3 條(第 1、2、4 條),不會擋的 2 條(第 3、5 條)。
