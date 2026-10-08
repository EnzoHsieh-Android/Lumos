severity: blocker

檔級判定：不能放行。找到兩個可繞過 Git 副本隔離的既有漏洞；都屬舊漏報，未發現由 r4 新增的資安回歸。

ID: R4-S1  
severity: blocker  
blocking: true  
引句:「不改HOME或真設定檔；探針Git只讀副本自己的設定。」  
file: `scripts/scenario_probe.py:395`  
file: `scripts/scenario_probe.py:550`

Git 的 worktree-scope 設定可同時保留有效 remote 並覆蓋防推 hook。

`_git_env()` 關閉 command/global/system 設定，但仍保留副本內的 `.git/config.worktree`。當 `extensions.worktreeConfig=true` 時：

- `remote.escape.url` 可放在 worktree scope。
- `core.hooksPath` 可在 worktree scope 指向空目錄。
- `git remote remove` 與未帶 `--worktree` 的 `git config core.hooksPath ...` 操作 local scope；worktree scope 優先級更高。
- 程式沒有在設定後重新檢查「有效 remote 必須為空」及「有效 hooksPath 必須等於專用 hooks 目錄」，且 remote remove 的退出碼未檢查。

因此一般的 `git push escape ...` 不需要 `--no-verify`，即可取得有效目標且避開專用 pre-push。這是 Git 設定隔離漏洞，不是要求 OS 沙盒防禦惡意程式。

重現交父代理：

1. 在暫存普通 clone 啟用 `extensions.worktreeConfig=true`。
2. 用 `git config --worktree` 寫入指向本機 bare repo 的 `remote.escape.url`，並把 `core.hooksPath` 指向空目錄。
3. 呼叫目前的 `make_sandbox(src)`。
4. 在回傳副本查 `git remote` 與 `git config --get core.hooksPath`。
5. 對本機 bare 執行 `git push --dry-run escape HEAD:refs/heads/probe`，不得真推送。

通過判準：有效 remote 為空、有效 hooksPath 精確等於 `<sandbox-parent>/hooks`、dry-run 非零且 stderr 顯示專用 hook 阻擋。若 remote 仍有 `escape`、hooksPath 仍是空目錄且 dry-run 為零，即重現。

來源分類：舊漏報。`637989b1` 已採相同的單一頂層 repo 清理方式；r4 只新增 command/global/system 測試，沒有首次引入此洞。  
實檔重現：未判定；唯讀席不能建立暫存 repo，上述為需父代理執行的 filesystem 重現。

ID: R4-S2  
severity: blocker  
blocking: true  
引句:「複製可能保留絕對gitfile、commondir或core.worktree；Git寫入前重驗。」  
file: `scripts/scenario_probe.py:518`  
file: `scripts/scenario_probe.py:540`  
file: `scripts/scenario_probe.py:542`

Git 路徑、metadata 與 remote/hook 清理只涵蓋副本根 repo；子模組或巢狀 repo 完全未隔離。

`_check_copied_git_paths(work, ...)` 只對頂層 `work` 執行一次 `rev-parse`。後續 `git remote`、`remote remove` 與 `core.hooksPath` 也只在頂層執行。它沒有檢查：

- 工作樹內其他 `.git` gitfile／目錄；
- `.git/modules/*` 內各子模組自己的 config；
- 巢狀 gitfile 是否以絕對路徑指回來源 metadata。

結果有兩條可利用路徑：

1. 正常子模組的 remote 仍存在，且不使用頂層專用 pre-push hook；在子模組內普通 push 可繞過頂層防線。
2. 若子模組或巢狀 repo 的 `.git` 是指回來源 `.git/modules/...` 的絕對 gitfile，副本內執行 `git config`、commit 等操作會直接修改來源 metadata。

重現交父代理：

1. 建立暫存父 repo、子 repo 與本機 bare target，把子 repo 加成 submodule。
2. 將子模組 remote 指向本機 bare，呼叫 `make_sandbox(parent)`。
3. 查副本子模組的有效 remote 與 hooksPath；執行本機 `push --dry-run`。
4. 第二組把副本前的子模組 `.git` 改為指向來源 `.git/modules/<name>` 的絕對 gitfile。
5. 記錄來源 metadata byte hash，建立副本後在副本子模組執行 `git config probe.escape 1`，再比對來源。

通過判準：所有巢狀 repo 必須被拒絕，或逐一驗證其 gitdir/common-dir/toplevel 均位於副本、remote 為空且 hooksPath 為專用阻擋 hook。任何子模組 dry-run 成功，或副本操作使來源 metadata 改變，即重現。

來源分類：舊漏報。r4 前的 `rsync`、頂層 remote 清理與頂層 hooksPath 設定已有相同行為；r4 新增的路徑檢查仍只看頂層。  
實檔重現：未判定；唯讀席無法建立子模組 fixture，須由父代理執行上述本機重現。

固定席合約逐項回答：

- Git 配置：不通過；R4-S1 顯示仍有較高優先級的 repo worktree scope 可繞過。
- 路徑與 metadata：不通過；R4-S2 顯示檢查只涵蓋頂層 Git administrative directory。
- 副本寫入逸出：不通過；絕對巢狀 gitfile 可把寫入導回來源。
- runner 環境：兩個 runner 都收到 `_git_env()`，command/global/system 清洗的記憶體內檢查成立；但 r4 測試 mock 了外層 subprocess，未驗真 Claude/Codex 子工具是否完整保留這些環境值，此項未判定。
- 本輪回歸：未找到；兩項均為舊漏報／r4 修補不完整。
- OS 沙盒邊界：未把刻意使用 `--no-verify`、任意 host command 或顯式外部 URL 當 finding；這些不在本產品承諾內。

補充：`/tmp/r4-lens.txt` 所列八個 Systems 節點逐條回答。以下依已讀凍結材料補齊合約對照，不新增 finding；「未見影響」不代表本席已執行綁定測試。

1. `Systems/codex-harness`（家）

   Lens 未在此節點列出 ★INVARIANT★ 條文，因此不補造正式合約。其相關職責是探針副本建立、Git 隔離及兩個 runner 的環境。回答：隔離要求未滿足，對應原 R4-S1、R4-S2；兩項的 filesystem 重現仍待父代理執行。既有環境清洗測試不能擴張為所有 Git 設定層級與巢狀 repo 都已安全。

2. `Systems/測試假綠形態`（家）

   合約：修 bug 的還原翻紅測試，必須有前置斷言證明被測路徑在現場確實成立。回答：r4 路徑測試具備「來源 Git 目錄在來源內」前置斷言；設定測試實際查詢兩個 runner 收到環境下的 remote、hooksPath 與 dry-run 結果，覆蓋已列出的輸入。但這些測試没有覆蓋 R4-S1、R4-S2 的現場，不能由既有綠燈推論兩項已被守住。本席未執行還原翻紅或該節點的綁定測試，殺傷力未獨立驗證。

3. `Systems/lumos-cli-read`（直接相依）

   合約：search 預設排除 superseded，但不得排除 stale；`--include-superseded` 保留逃生路徑，濾網位於命中確認後、三路分岔前。回答：本次 code patch 修改探針與其測試，未修改 search 的篩選與排序實作；未見此合約受到行為影響。綁定測試未由本席重跑。

4. `Systems/lumos-cli-lifecycle`（直接相依）

   合約：re-inject 只覆蓋 sentinel 之間的 body，sentinel 外的 `CLAUDE.md` 位元組必須保持相同。回答：本次未修改 re-inject 實作。探針 `arm="without"` 的文字刪除是副本消融路徑，並非 re-inject；未見本次 diff 改變上述 sentinel 保留合約。`t_reinject_preserves_outside` 未由本席重跑。

5. `Systems/bound-tests-gate`（間接相依）

   合約：code-loop check 必須逐支執行固定席合約綁定測試；紅燈、懸空、偽證據、非法方法名或證不出執行皆阻擋；指定無法適用情況則不擋但記帳。回答：本次未修改 bound-tests 執行或判定程式，未見合約語意被更動。本報告與歸檔綠測試均不能替代此閘；本席未執行 code-loop check，不能聲稱本轮固定席綁定測試已過。

6. `Systems/canary-audit`（間接相依）

   第一條合約：record／second 只有在紀錄已落盤且可讀回時才能回報成功；讀回失敗須 rc2 且不印成功行。回答：本次未修改記帳與讀回實作；未見合約影響。本席未執行記帳，未驗落盤。

   第二條合約：second 只是 telemetry，永不影響 loop status 的 gate 輸出與退出碼。回答：本次未修改 second 與 gate 的連接或判定；未見此合約受影響，綁定測試未重跑。

7. `Systems/design-loop`（間接相依）

   合約：符合指定 loop 類型及首筆帳時間條件的設計審，處置閘要求 `.md` 計劃審材，不能以 `.patch` 替代，並按條款規則判定。回答：本案 `code-repair-pilot-01` 是 `code-` 開頭的代碼審，不適用該設計審材分支；本次亦未修改該閘。Lens 中條款後段被截斷，對未展示部分不補作完整驗證宣稱；綁定測試未重跑。

8. `Systems/guard-kill`（間接相依）

   第一條合約：退出碼優先序為 survived→rc1、drifted／abort／error→rc2；弱證據不得放行執行錯誤。回答：本次未修改 guard kill 判定；探針的儀器例外分類不等於 guard kill 的退出碼分支，未見合約影響。

   第二條合約：`--json` 成功完成時（rc0／rc1）stdout 恰為一行合法 JSON，診斷走 stderr；rc2 早退不在此保證內。回答：本次未修改 guard kill 的輸出路徑，未見合約影響。兩條合約的綁定測試均未由本席重跑。

材料與限制：

- 完整讀取 `r4-code.patch`、`r4-context.patch`、`r4-delta.patch`、目前完整 `scripts/scenario_probe.py`。
- `r4-archive-security.patch` 僅作歷史證據，讀取 section inventory、既有安全重現與 r4 回歸輸出；未把歷史結論當 HEAD 權威。
- `r4-snapshot.patch` SHA256 已驗為 `2e8dae39bcabc1d4793e43e096995d79e84bbcf4edb9c83dea009bdfeb0c2734`；code/context/archive 各 section 均可逐段精確錨回 snapshot。為遵守禁令，未讀 snapshot 內其他 r4 席報告內容。
- `/tmp/r4-lens.txt` 已完整讀取。
- `/tmp/r4-test-layers.txt` 不存在；審材目錄的 `r4-test-layers.txt` 為 0 bytes。
- 未執行真模型、真 push、網路或 filesystem fixture；既有 `207 passed` 只視為歸檔證據，沒有冒稱本席重跑。
- HEAD 仍為 `8922c3c9c11e4234554d94695c31c93973679a99`；離場工作樹狀態與進場相同，本席未修改任何檔案。