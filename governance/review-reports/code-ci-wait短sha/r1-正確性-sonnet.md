severity: minor

## F1 新測試對短 sha 走真的 30 秒 grace 窗,單支慢 32.5 秒
severity: minor
blocking: 否 — 只拖慢測試,不影響正確性;但同檔其他 ci-wait 測試通常帶 --grace 縮短
引句:「r = _ci_run(root, v, env, "ci-wait", "--json", "--sha", full[:8])」
file: `scripts/test_lumos.py:27037`
實測:`python3.14 scripts/test_lumos.py -k ci_wait_short_sha` 通過(2 passed),但最慢榜顯示 32.5s。原因:全綠前固定再等一個 grace(預設 30 秒),①沒帶 --grace 0。建議加 "--grace", "0"。翻紅釘本身有效(不換完整 sha → d.sha != full → ①紅;找不到照查 → stub 回綠 rc0 → ②紅)。

## F2 git 缺席/逾時/短碼歧義時,一律講成「本機找不到」,且給了 --sha 時從 fail-open 變 rc2
severity: minor
blocking: 否 — 失敗方向是擋下並講話(不是假綠),訊息略不精確
引句:「if not _CI_FULL_SHA_RE.fullmatch(full):」
file: `scripts/lumos:41840`
走法:_git_out 在 git 缺席、30 秒逾時、rev-parse 因短碼歧義(多個提交同前綴)失敗時都回空字串,於是都走「在本機找不到對應的提交」。歧義時使用者被叫去 git fetch,其實該加長碼。另外 `_git_out` 註解寫「git 缺席/逾時也 fail-open」,但給了短 sha 時現在是 rc2、不再是 rc0 unavailable;沒給 sha 時仍 fail-open,行為不一致(方向偏安全,可接受)。

## 已讀無 finding 的項目(逐項走過)
- 40 碼大寫:不符小寫正則,走 rev-parse 被正規化成小寫完整 sha(實測 git 回小寫),帳本與 gh --commit 都拿到小寫。引句:「_CI_FULL_SHA_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")」
- 以 - 開頭、帶前導空白、`<sha>x`:rev-parse 實測 rc=1 → rc2 擋下;--end-of-options 擋住旗標注入,且通過後的值一定是純十六進位,不可能再被 gh 當旗標。引句:「full = git_out("rev-parse", "--verify", "-q", "--end-of-options", f"{sha}^{{commit}}")」
- 分支名/tag/HEAD~0:實測會解成完整提交 sha;這是合理且有益的(帳本記完整 sha),不是缺陷。
- 完整 40/64 碼本機沒有(遠端有、本機沒抓)原樣放行,不驗證:這是刻意保留(推出去的別人提交可查),本機有但遠端沒有的提交仍走原來的 no-run 路徑,屬已知另案([[Issues/ci-wait未推送sha誤導訊息]])。引句:「if _CI_FULL_SHA_RE.fullmatch(sha):」
- --repo-dir 指到別的 repo:_git_out 用 root 的 `git -C`,解析與查詢同一個 repo,一致。
- 同族:全檔只有 `_ci_list_runs` 一處把使用者 sha 交給 gh(`--commit`),呼叫者只有 cmd_ci_wait;ci-status 沒有 --sha 參數;`--sha` 其餘出現在 escape 記帳(不碰 GitHub)。無漏網。
- 帳本 sha 欄位:_ci_record 收到的是換過的完整 sha,emit 的 json sha 也是完整的。
- 資料狀態五問:空(--sha "" 視為沒給取 HEAD)、單筆、大小寫、非預期形狀(旗標開頭/空白)、不存在(rc2)皆判過,無問題。
- 圖譜鏡頭:Systems/CI回流開場提醒 的 about_code 新增 scripts/lumos、responsibility 已劃界(只管 cmd_ci_wait/cmd_ci_status 與輔助);Issue 筆記為純文字且帶 REVISIT;固定席其餘節點(INVARIANT 皆與 search/guard-kill/re-inject 等無關)判不受影響,因為只動 ci-wait 前置解析。
- 新測試會不會改壞照綠:不會,已逐項推演兩個翻紅釘。

總結:兩條皆為低風險,短 sha 修法對各種輸入走法正確。
