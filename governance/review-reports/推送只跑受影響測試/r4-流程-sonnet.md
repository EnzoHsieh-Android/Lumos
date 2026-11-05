severity: major

我只讀了 spec 和對照 repo,沒有建臨時目錄、沒有改任何檔,也沒查 GitHub 即時狀態(分支保護、帳號額度都沒驗)。

**已驗證成立的假設,無 finding**
- PR 事件一律全套:ci.yml 的 `prep` 只在 `push` 事件才改判 docs,`pull_request` 保持 full。
- PR 新推送會取消進行中的舊 run:concurrency 群組鍵 PR 用編號、`cancel-in-progress` 只對 PR 為真。
- 新頭提交會自己跑全套,因為每個新 PR 頭都是新的 run。
- PR 事件與 push main 事件不會共用 run:群組鍵含事件名。
- `lumos ci-wait` 用 `gh run list --commit <sha>` 查,而 PR run 的 head sha 是 PR 頭提交。它等的是 PR 頭那個 sha 的所有 run。
- 全套測試(shards)確實在 PR 上跑。

---

severity: major
blocking: 是(照 spec 流程,兩個會談各自「等綠就合」會讓語意衝突的組合進主線,而 spec 的守衛面沒提這個洞)
spec 段落:做法 3、實務隱患「守衛面」。
問題:「PR 頭提交綠」測的是 GitHub 在觸發當下把 PR 頭和 main 暫時合起來的快照。main 之後前進,PR 的 CI 不會重跑。一人加多個 AI 會談的實況是兩個 PR 各自綠,依序合併,兩者合在一起的組合只在合併後的 push main CI 才第一次被全套測到。
- 以前推 main 前本機全套是在最新 main 上跑的;現在合併由 GitHub 在伺服器端完成,不經本機閘。
- spec 把「合併後通知」列為不做,也沒提合併後的 push main CI 是唯一的補網。結果是 main 變紅沒有人被點名。
- spec 引用的 Mergify 兩段式本身就是為這個洞設計的(merge queue)。分支保護的「要求分支最新」只在 Q2 一語帶過,沒進風險評估。
引句:
引句:「合併一律走 PR,等 PR 最新頭提交的 `lumos ci-wait` 判定是 green(rc 0 不等於綠)才合併」
佐證:
- file: `.github/workflows/ci.yml:20`(PR 以編號分組,只對同 PR 的新推送取消)
- file: `.github/workflows/ci.yml:3`(觸發只有 push main / tag / pull_request,base 前進不觸發 PR 重跑)

---

severity: minor
blocking: 否(文件精度:spec 的描述對網路上的「必過檢查」成立,對本 repo 的 PR CI 不完整)
spec 段落:實務隱患「守衛面」、PRIOR-ART。
問題:spec 說 PR 頭提交「一定有全套結果」,這句對測試成立。但 ci.yml 的後盾閘在 PR 事件整組略過:code-loop gate、note-shape、drift check、reread-check 四步都是 `if: github.event_name == 'push'`。
- 所以「PR 綠」不含這四道。用 `--no-verify` 推的功能分支,審查留痕缺失到合併後 push main 才紅。
- spec 的「現況」與「守衛面」都沒寫這一點,讀者會把「等綠才合併」當成跟舊的主線 CI 等價。
引句:
引句:「PR 事件一律全套、帳本提交會在 PR 頭上再觸發一次全套,所以 PR 頭提交一定有全套結果」
佐證:
- file: `.github/workflows/ci.yml:215`
- file: `.github/workflows/ci.yml:239`
- file: `.github/workflows/ci.yml:268`
- file: `.github/workflows/ci.yml:292`

---

severity: minor
blocking: 否(措辭與操作精度,不判錯方向)
spec 段落:做法 3 訊息、現況「`lumos ci-wait`」。
問題:訊息叫人對「PR 最新頭提交」跑 `lumos ci-wait`,但沒寫要帶 `--sha <PR 頭>`。不帶時 `ci-wait` 用本機 HEAD(`_ci_resolve_sha`),會談的 HEAD 不一定是 PR 頭。這些情況都會回 rc0 加「非綠」,方向安全,但容易被誤讀成「還在等」:
- 同 sha 曾有被取消的舊 run,另有一個成功的新 run。`ci-wait` 把所有 completed run 一起看,有 cancelled 就判 undetermined,不會單看最新那個。
- PR 與 main 有衝突時 GitHub 不建合併快照、PR 事件根本不跑,結果是 no-run。
- 預設 timeout 1800 秒,對照 spec 自己寫的「15–20 分加排隊」餘裕不大。
佐證:
- file: `scripts/lumos:63048`
- file: `scripts/lumos:63119`
- file: `scripts/lumos:63150`

---

severity: minor
blocking: 否(spec 沒釘死合併方式,實際慣例已安全)
spec 段落:範圍「做」④、做法 3。
問題:spec 只說「合併一律走 PR」,沒指定合併方式。本 repo 的 first-parent 歷史全是 merge commit(#155、#154 等),所以目前沒事。但 squash 或 rebase 合併會讓審查與表態留痕失效,因為原提交不再是祖先。這會讓合併後的 push main CI 的 code-loop gate 紅。會談用 `gh pr merge` 時若選了 squash 就會踩到。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:41`

---

severity: minor
blocking: 否(數字未驗,屬精度)
spec 段落:實務隱患「時間」。
問題:「同時執行的工作有上限」沒寫數字,也沒算本 repo 單次 PR run 用幾個工作。matrix 是 8 台 shards 加 prep 加 gates,合計約 10 個工作。若是 GitHub Free 的並行上限(約 20 個,我沒驗證),兩個會談同時有 PR 的 run 就滿了,第三個排隊。再加上帳本提交取消重跑,實際等待會比 15–20 分長。
佐證:file: `.github/workflows/ci.yml:123`

---

**一人加多個 AI 會談的實際走壞方式**
- 「合併前等綠」是靠會談自覺,main 沒有分支保護。被使用者說「可以直接合併」的那個會談不會去等。
- 「合併一律走 PR」與現況不衝突(歷史本來就走 PR),但 spec 沒給出「誰在合併後看 push main CI」的答案。

**實務隱患逐類**
- 守衛面:見 major 與第一條 minor。
- 併發:見 major。
- 外部依賴:見最後一條 minor。
- 金流、對外送出:無,spec 不碰這兩類。

總結:最嚴重等級是 major,共 1 條會擋的問題(blocking 1 條),另有 4 條不擋的 minor。
