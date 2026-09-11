severity: major

# 推播漏網量測(recount.py run_misses)r1 單 reviewer 審查

方法:逐 hunk 讀完整份 diff;在 /tmp/lens-review/repo(clone 自本 repo)跑 `python3 scripts/test_lumos.py -k lens_recount`(57 案例全綠);另外用真實 `~/.claude/projects` 逐字稿(169358 則 assistant 訊息)與 `~/.codex/sessions`(501 份 rollout)做經驗頻率查證;用真 git repo 手動驗證 `git log --follow --diff-filter=A` 對改名筆記的行為。

## A1

severity: major
blocking: 是

⚠ 判不準(見敘述末段的經驗頻率說明,但邏輯錯誤本身是確定的、有可翻紅重現):`build_miss_rows` 把「讀取歸給最近一次有關的編輯」實作成 `prior = [e for e in edits if e["idx"] < rd["idx"]]`(嚴格小於),但 `idx` 是逐字稿物件在陣列裡的位置——**同一則 assistant 訊息裡的多個 tool_use(例如一次訊息同時 Edit fileA 又 Read 筆記,或同時 Edit 兩支檔)全部共用同一個 idx**。我用 `analyze_claude`+`build_miss_rows` 直接重現:一則訊息同時含 `Edit(src/a.py)` 與 `Read(Systems/x.md)`,`relate()` 回真(有關)——結果那筆 Read 完全消失,不進任何一列的 `misses`(`rows[0]["misses"] == []`,即使 `zero_push=True`)。再加一則更早、不相關的獨立 Edit(`src/old.py`)之後重跑:這次 Read 沒有消失,但被**錯配給不相關的 `src/old.py`**、分類降成 `unknown`(判不出),而真正有關、且同一批次發生的 `src/a.py` 那列 `misses` 仍是空的。這直接違反本段自己寫的規則(往前找「最近一次有關」的編輯,找不到才退回最近一次)——因為嚴格 `<` 把「同一批次」的編輯直接排除在候選之外,不是漏算就是算錯檔。頻率查證:掃本機 `~/.claude/projects` 全部逐字稿(169358 則 assistant 訊息),多 tool_use 共存一則訊息的案例為 0;抽樣 Codex `~/.codex/sessions`(1152 個 custom_tool_call)也沒找到同一 idx 同時含 apply_patch 與 exec 的真案例(唯一一個字串命中是誤判,input 本身是測試腳本裡引用的字串)。目前本機資料沒有踩到,但這是演算法本身對其自訂契約的違反,不是資料剛好沒踩到就代表邏輯是對的。
引句:「prior = [e for e in edits if e["idx"] < rd["idx"]]」
file: `governance/eval/lens-utilization/recount.py:648`
引句:「每筆讀取只算一次:往前找最近一次「跟這篇有關」的編輯,都沒有才給最近一次」

## A2

severity: minor
blocking: 否

計劃〈過閘時的誠實界線〉點名「當時是否存在(git --follow 與檔案建立時間)」是 r2 才補進、還沒被任何席位審過的段落,S2 的驗收也明寫「筆記在編輯之前建、之後改過名→仍算 miss」「編輯之前就寫好、之後才提交→仍算 miss」兩條。但新增的測試裡,所有會走到 `existed` 判斷的案例全部用 lambda mock 掉真正的 `Existence` 類別(`existed = lambda node, ts: node != "Systems/late.md"` 與 `existed=lambda n, t: True`),`t_lens_recount_weekly_archive` 雖然是真的透過 subprocess 跑 `lens_weekly.py`(會用到真的 `Existence`),但唯一用到的分支是「檔案一開始就存在、一路都 existed=True」,改名與編輯後才建檔兩條驗收案例都沒有真測試覆蓋。我另外手動起了一個 git repo,對照 `Existence.__call__` 的邏輯(`git log --follow --diff-filter=A` 取改名前的原始新增時間)驗證:重命名後查新檔名,`git log --follow --diff-filter=A` 正確回到改名前的原始加入時間(2026-01-01,而非改名的 2026-06-01),所以**目前的邏輯本身是對的**——這條只是測試覆蓋缺口,不是行為錯誤,列 minor 不列 major。
引句:「git 最早加入時間(--follow,改名不洗掉)或檔案系統建立時間,任一早於編輯就算存在」
file: `governance/eval/lens-utilization/recount.py:746`

## A3

severity: minor
blocking: 否

⚠ 判不準(目前真實圖譜沒有踩到,純屬潛在缺口):`_about_map` 抓 `about_code` 欄位的正規式只認 YAML dash-list 格式(`about_code:\n  - a\n  - b`),`about_code: [a, b]` 這種合法的 flow-style 單行寫法完全比對不到,會被靜默當成沒有 about_code(不拋錯、不記警告)。查過本 repo 全部 `docs/lumos-toolchain-knowledge/`:flow-style 的 `about_code:` 只有 `about_code: []`(空的)這一種用法,dash-list 有 78 篇非空,沒有任何一篇是非空的 flow-style,所以現階段不會量錯任何一篇筆記的「關於欄」分類。但這正規式沒有防呆,以後如果有人(或工具)寫出非空 flow-style,會悄悄漏算成「判不出」而不是「關於欄」,而且沒有測試會抓到。
引句:「r"(?m)^about_code:\s*\n((?:[ \t]+-[^\n]*\n?)+)"」
file: `governance/eval/lens-utilization/recount.py:699`

## LUMOS-IMPACT: 1f28cd6b..HEAD

- `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md`、`slim-install-安裝器.md`、`slim-get-一行安裝.md`、`guard-kill.md`、`canary-audit.md`(★INVARIANT★ 群):不影響——這份 diff 完全沒有修改 `scripts/lumos`,也沒有修改 `scripts/hooks/claude/impact-hook.py`(`recount.py`/`lens_weekly.py` 只用 `SourceFileLoader` 唯讀載入它們的既有函式,不改動它們的程式碼);`scripts/test_lumos.py` 裡這批 diff 唯一動到既有測試的地方,是替 3 支既有 `t_lens_recount_*`/`t_codex_s3_*` 測試前面加一行 `_need_src(...)` 守門(見 diff `scripts/test_lumos.py` 的 hunk),其餘全是在檔尾新增獨立的 `t_lens_recount_*` 測試函式;上述 INVARIANT 綁定的測試(`t_reinject_preserves_outside`、`t_canary_record_persist`、`t_canary_second`、`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`、`t_slim_install_*` 等)本體都沒被這份 diff 改到。
- `docs/lumos-toolchain-knowledge/Systems/design-loop.md`、`bound-tests-gate.md`(★INVARIANT★,關於審查流程本身的閘):不影響此次程式碼行為——這兩篇管的是「這份 PR 該怎麼過閘」的流程機制(散文審回歸處置閘、code-loop 對固定席合約測試逐支真跑),不是 `recount.py`/`lens_weekly.py` 執行時會違反的執行期不變量;本次審查已依 `bound-tests-gate` 的精神實跑了 `-k lens_recount` 全部 57 案例(綠),沒有發現閘本身被繞過的跡象。
- `docs/lumos-toolchain-knowledge/Issues/canary-record未落盤事件.md`:不影響——這份 diff 不寫 canary 帳(`recount.py`/`lens_weekly.py` 明確不呼叫 `lumos canary`,自主迴圈只把 `run_lens_weekly` 的 LOG 行寫進既有 log 檔,不寫治理帳),不涉及該事故描述的「回報成功未落盤」路徑。

## 總結

全份最高嚴重度是 major,blocking 共 1 條。
