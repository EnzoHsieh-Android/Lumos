severity: major

**Finding 1:新增分支觸發後,gates 工作的各道後盾閘第一次在功能分支上跑,spec 沒分析**

severity: major
blocking: 是(照字面實作會讓功能分支首推的 CI 行為改變,可能誤紅;spec 的「CI 會綠」前提沒查證)

spec 段落:做法 1、實務隱患。

問題:做法 1 只講「prep 判範圍照現行」。`ci.yml` 的 `gates` 工作另有五個 `if: github.event_name == 'push'` 的步驟:code-loop gate、note-shape、drift check、reread 提醒,加上不分事件的自主迴圈測試、doctor、anchor。`branches: [main]` 改成所有分支後,這些步驟就會在功能分支上跑。spec 通篇沒提到它們。

最危險的是 code-loop gate:
- 它在新分支首推時拿到的 BEFORE 是全零。
- 全零時 lumos 走 `_lens_push_base`,那支只認 `main@{upstream}`(`_mainline_ref(remote_only=True)`)。
- 這個 gates 工作在 push 事件下不會建本機 `main`。只有 PR 事件有「補上本機 main」那一步,而 note-shape 才建 main,排在 code-loop gate 之後。
- 所以找不到主線,落到「找不到主線,從空樹算」。整個 repo 被當成新增,tier 會被判高風險,要求留痕。
- 以前這步只在 `main` 上跑(本機 main 就是 checkout 的分支),這個缺口一直沒踩到。
- 影響:功能分支首推的 CI 可能誤紅,或判了跟本機掛鉤不同的範圍。
- RETIRE-IF 的紅燈比例會被這種「結構性誤紅」污染,量不出真正的測試紅。

引句:「`ci.yml` 的 `push` 觸發從 `branches: [main]` 改成所有分支(標籤照舊另走 `security_tag`)。prep 判範圍照現行(push 事件問 lumos,只改文件就文件子集,其他全套)。」

佐證:
- `.github/workflows/ci.yml`:gates 工作的 code-loop gate 與 note-shape 步驟(`if: github.event_name == 'push'`),以及只在 PR 事件執行的「補上本機 main」步驟。
- `scripts/lumos:65184`(`_lens_push_base` 的空樹退路)。
- `scripts/lumos:65710`(`_mainline_ref` 的 `remote_only=True` 只認 upstream)。
- `scripts/lumos:70230-70245`(code-loop check 全零起點的換算)。

建議:spec 要逐步驟列出 gates 在功能分支上的行為(含首推全零起點),並決定這些步驟要不要補本機 main,或限定只在 main 跑。

**Finding 2:會被改成紅的既有測試與註解沒列進做法 5**

severity: major
blocking: 是(做法 5 號稱「逐處」同步,卻漏列必然紅的守衛測試;照字面實作,推送閘會紅)

spec 段落:做法 5、驗收條款 S6、回退。

問題:`t_secev_s32_ci_tag_job` 用正規式釘死 `on:\n  push:\n    branches: \[main\]\n ... tags: ['*']`。`t_secev_s61_doctor_ci_template` 的三個樣本也含 `branches: [main]`。改成所有分支後,前者必紅。做法 5 與回退段都沒列要改這些既有測試。S6 只加新測試 `t_ci_yml_push_all_branches`。

S6 後半「concurrency 以提交編號分組且不取消」現在就成立(`ci.yml` 現行就是 `github.sha` 且 push 不取消)。這半條不會翻紅,是空條款。

引句:「`push` 觸發 應 涵蓋所有分支、push 事件的 concurrency 應 以提交編號分組且不取消 [test:t_ci_yml_push_all_branches]」

佐證:
- `scripts/test_lumos.py:116399`(`t_secev_s32_ci_tag_job` 的 `branches: \[main\]` 正規式)。
- `scripts/test_lumos.py:117578`(`t_secev_s61_doctor_ci_template` 的樣本)。
- `scripts/test_lumos.py:31017`(`t_ci_yml_speed_shape` 對 concurrency 的現行守衛,S6 後半與它重複)。

**Finding 3:文件同步清單漏了會變成說謊的註解與筆記**

severity: minor
blocking: 否(文件精度)

spec 段落:做法 5。

問題:以下幾處改完會跟現況不符,清單沒列。
- `ci.yml` 的 note-shape 步驟註解寫「本 workflow 只在推 main 時跑這步」。
- `ci.yml` 檔頭與 concurrency 註解寫「推到 main 每個提交各自一組」。
- `skills/lumos-project-notes/commands/08-自動跑的.md` 的 CI 列寫「CI(push 後)」。這列要補「功能分支也跑」,不只改 pre-push 那句。
- [[Systems/bound-tests-gate]] 的 WHY「分支與合併請求的 CI 拆成三個工作」、`ci.yml` 家的敘述。
- [[Systems/pitfalls-code-loop]] 要新增 `pushed_mainline` 與兩個旗標。這在 lands_in,但做法 5 沒列為同步項目。

引句:「**說明文字同步**(逐處):紀律範本 `scripts/templates/graph-discipline.md` 那句「全套留給推送前的閘」改寫」

佐證:`.github/workflows/ci.yml`(note-shape 步驟註解)、`skills/lumos-project-notes/commands/08-自動跑的.md:9`、`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:21`。

**Finding 4:重新注入的檔案名稱不完整,可能漏掉第二層同步**

severity: minor
blocking: 否

spec 段落:做法 5、S7。

問題:「全套留給推送前的閘」同句也出現在 `scripts/templates/graph-discipline.md:59`、`CLAUDE.md:61`、`AGENTS.md:62`。spec 有點名這三處,其他引用處(例如 `Projects/Codex行為精修_計劃.md:76` 的歷史描述、`全repo審視_計劃.md:566` 的教訓)屬歷史紀錄可不改。但 spec 沒寫「歷史紀錄不改」的取捨。S7 只守這三處。

引句:「`CLAUDE.md` 與 `AGENTS.md` 的紀律區塊(sentinel 之間)應 跟範本逐字一致、不再有「全套留給推送前的閘」」

佐證:`scripts/templates/graph-discipline.md:59`。

**lands_in 評估**

- `Systems/bound-tests-gate`:合理。它管 `ci.yml`、`scripts/hooks/pre-push`、`governance/anchor-baseline.json` 三支檔。
- `Systems/pitfalls-code-loop`:合理,放 `pushed_mainline` 與旗標。
- 缺口:`ci.yml` 的 gates 在功能分支的行為(Finding 1)。這一塊該落在 bound-tests-gate 的 CI 拆工作那條 WHY。
- 安全證據閘節點管 `t_secev_s32_ci_tag_job`,spec 沒連過去(Finding 2)。

**既有合約影響**

- bound-tests-gate 的 ★INVARIANT★ 說 code-loop check 對 impact 固定席的綁定測試逐支真跑,紅或懸空就擋。本計劃不動這一條。
- CI 的 `LUMOS_SKIP_BOUND_TESTS=1` 讓 gates 不重跑綁定測試,功能分支也一樣。這個設計仍成立,因為全套在 shards 跑。
- 做法 3 把功能分支降成 light 時,本機也不跑合約測試真跑以外的全套。code-loop check 在 pre-push 照叫,所以合約閘不受影響。已讀,無 finding。

**實務隱患**

- 守衛面:Finding 1。
- 機器時間:spec 有寫。
- 併發:spec 有寫,但沒提 gates 在多個功能分支下的行為。
- 其他類(金流、對外送出、不可逆):已排除,spec 的理由成立。

總結:最嚴重等級為 major,會擋的問題共 2 條(Finding 1、2)。
