severity: major

收到通知:背景變異實驗已被我自己停掉並刪除臨時目錄(`/private/tmp/lumos-seat-work/code-推送只跑受影響測試/合約圖譜-sonnet`)。刪除前 lsof 顯示還有兩個程序(PID 40758、40759)的 cwd 在那個目錄裡,我沒有等它們結束。第一組變異結果已經拿到,第二組(`-k prepush_docs_and_light`)沒跑完,下面沒有用到它。

## Finding 1:S6 後半句沒有測試守,改壞照綠

severity: major
blocking: 是

引句:「原本就判 light 的功能分支推送 應 不印降級那行 [test:t_prepush_feature_branch_light_ok_false]」

file: `docs/lumos-toolchain-knowledge/Projects/推送只跑受影響測試_計劃.md:76`(S6 條款)、`scripts/test_lumos.py` 的 `t_prepush_feature_branch_light_ok_false`

- 條款 S6 有兩半:功能分支 `light_ok` 假時也降成子集;**原本就判 light 的功能分支推送不印降級那行**。
- 綁定的測試只驗前半(`all("--suite" in c ...)`),並對照推 main 是全套。它沒有推「原本就判 light(spec-gate 判 light)的功能分支」,也沒斷言訊息不含「推功能分支:」。
- 重現:在臨時 clone 的 `scripts/hooks/pre-push` 把 spec-gate 那段的 `_suite_this="light"` 改成 `_suite_this="light"; _SUITE_BRANCH_DOWN=1`。這樣原本就是 light 的推送也會印「推功能分支:…全套由 PR 的 CI 跑」。跑 `python3.14 scripts/test_lumos.py -k prepush_feature_branch`,結果 `16 passed, 0 failed`,六支功能分支測試全綠。
- 影響:原本就判 light 的推送(推 main 的 light 或功能分支的 light)會被誤印降級訊息,條款明寫不該有。
- 低影響註記:誤印的只是一行提示,不會改變實際跑哪些測試。但條款明寫了、測試沒守,依判準仍算 major。

## Finding 2:bound-tests-gate 同一行新舊句子並存

severity: minor
blocking: 否

引句:「+  KEY:[2026-09-18]推送前與 CI 的全套測試,純文件改動只跑文件子集」

file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:47`

- 這次只在該行尾端插入了新的功能分支說明,沒動它前面的舊句。
- 舊句「keys 每片都 rc3(沒對到)不擋、講明 CI 會跑全套當後盾」描述的訊息,掛鉤這次已改成「全套由 CI 跑(推 main 有主線 CI;功能分支要開 PR 才有 CI)」。
- 舊句「CI 對 light 照跑全套當後盾」對沒開 PR 的功能分支不成立,CI 只在 main push、tag、PR 觸發。
- 接手的人照這行會以為功能分支推上去就有 CI 全套。

## Finding 3:CLAUDE.md 同一段第一句沒跟著改

severity: minor
blocking: 否

引句:「改完程式先跑跟改動相關的子集,全套(約 8 分鐘、3700+ 案例)留給推送前的閘:」

file: `CLAUDE.md:98`

- 這是被改動段落的第一句,出現在 diff 的 context 行,沒被改。
- 它說全套留給推送前的閘,但下一段已改成功能分支的閘不跑全套。
- 上下文能讀懂,只是同段前後說法不一致。

## Finding 4:README 的「不能調的」清單沒同步

severity: minor
blocking: 否

引句:「+推功能分支:本機只跑文件子集與關鍵字子集(關鍵字空的就只有文件子集);全套由 PR 的 CI 跑——」

file: `README.md:481`

- 該行寫著「不能調的:…Lumos 自己 repo 的全套測試沒過」,沒說明現在只在推 main 時本機跑全套。
- 功能分支推送時,全套是否通過要等 PR 的 CI,不是本機閘。

## Finding 5:全套路徑仍印「嫌久可 --no-verify,CI 會兜底」

severity: minor
blocking: 否

引句:「echo "推送前先跑全部測試(約 8 分鐘;嫌久可 --no-verify,CI 會兜底)…" >&2」

file: `scripts/hooks/pre-push`(全套兩個 `elif/else` 分支,diff 中為 context 行)

- 降級分支那句拿掉了,但推 main 的全套路徑兩句都還在。
- 推 main 時 CI 是會跑,但這句鼓勵 `--no-verify`,而且 push 事件的 CI 是推完才跑。這與計劃目標「拿掉『嫌久可 --no-verify,CI 會兜底』」不完全一致。
- 計劃做法 3 只列了降級那一句,所以這屬於計劃與審查指示的出入。

## 逐篇圖譜鏡頭回答(合約與事故)

下列合約與事故筆記,我用 `scripts/lumos contracts` 逐篇看過。

1. Issues/code-loop守衛main-direct盲區:沒讀全文,diff 沒動 `code-loop check` 與逐 ref 範圍推導,pre-push 只在 pitfalls 呼叫加旗標和降級判斷。判不影響,但沒有逐行核對。
2. Systems/pitfalls-code-loop:已新增 `--pushed-ref` 的 WHY 行並綁 `t_pitfalls_pushed_mainline`,沒有硬合約被破壞。
3. Systems/bound-tests-gate:`★INVARIANT★` 綁 `t_bound_tests_gate`(code-loop check 對合約綁定測試真跑)。diff 沒動那支函式,不影響。文件有 Finding 2 的舊句問題。
4. Systems/lumos-cli-read:`★INVARIANT★` 是 `search` 預設排除 superseded,diff 完全沒碰,不影響。
5. Systems/design-loop:`★INVARIANT★` 是處置閘第五步,diff 沒動,不影響。
6. Systems/guard-kill:兩條 `★INVARIANT★`(rc 優先序、JSON 純度)diff 沒碰 guard kill,不影響。
7. Systems/lumos-cli-lifecycle:`★INVARIANT★` 是 re-inject 不動 sentinel 外內容。diff 改的是 CLAUDE.md sentinel 外的段落,沒動 re-inject 邏輯,不影響。
8. Systems/測試假綠形態:`★INVARIANT★` 要求翻紅釘配前置斷言證明現場成立。新測試多半有現場斷言:`old_lumos` 檢查字樣不在、`skips_full` 檢查帶 `--suite`。`failclosed` 那支沒斷言替換後的 `computed` 真的是 false,但替換沒套上時會變紅而不是綠,所以不構成假綠。

## 設計對照與回頭條件

- 驗收條款 [S1]–[S8] 各有綁測試,實作對照沒有多做。除 Finding 1 外沒找到少做。
- RETIRE-IF 與 `REVISIT:2026-12-31` 都已寫進計劃。
- 父計劃的 `REVISIT:2026-11-14` 已加 `[closed:]`。
- Q1(全域 CLAUDE.md)與 Q2(分支保護)留為待查,符合「不由 AI 改」。
- `scripts/templates/graph-discipline.md` 那句「全套留給推送前的閘」刻意不改。對消費專案仍成立,因為它們的推送前掛鉤本來就不跑全套。

## 沒有找到的問題

- 掛鉤降級條件(`pushed_mainline` 為 false 且 `suite_computed` 為 true)方向正確:缺欄位、舊版、推 main、算不出範圍都落回全套。
- `_pitfalls_pushed_mainline` 對標籤和空字串回 true 與計劃一致。
