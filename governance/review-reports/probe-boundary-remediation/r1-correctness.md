severity: blocker

審材：`r1-snapshot.patch`。

Finding 1 — 巢狀 bare Git 倉庫繞過檢查，仍可推出副本外

severity: blocker
blocking: true
引句:「副本不接受另一套Git資料或指到副本外的工作樹連結。」
file: `scripts/scenario_probe.py:535`
file: `scripts/scenario_probe.py:543`
具體輸入→路徑→錯誤：外層正常 repo 內含 `nested.git/` bare repo，且其 `origin` 指向副本外；bare repo 沒有名為 `.git` 的入口，因此 `_check_worktree_entries` 放行，外層 `core.hooksPath` 也不約束它。模型執行 `git -C nested.git push origin main:refs/heads/leak` 可寫出副本。
最小翻紅測試：新增 `t_probe_boundary_nested_bare_git`，建立 outer、seed、外部 sink 三個臨時 repo；以 `git clone --bare seed outer/nested.git` 建巢狀 bare repo，設定其 origin 為 sink，呼叫 `make_sandbox(outer)` 後從副本推送，斷言建置應拒絕且 sink 不得新增 ref。
實際輸出：`make_sandbox=accepted`；`nested_remote=/tmp/.../sink.git`；`push_rc=0`；`external_ref_created=True`。

Finding 2 — 白名單設定沒有保存宣稱的假身分

severity: major
blocking: true
引句:「只保留 Git 歷史所需的檔案格式欄位、設定副本專用 hooksPath、假身分」
file: `scripts/scenario_probe.py:580`
file: `scripts/scenario_probe.py:632`
具體輸入→路徑→錯誤：來源 repo 有本機身分；`_reset_copied_git_config` 重寫設定時只寫 `core`、`extensions` 與 hooksPath，而 `probe@local` 只透過 `git -c` 套用於儀器自己的快照提交。模型之後在 `_git_env()` 下提交時，副本沒有 `user.name`／`user.email`；本機實測 Git 改用作業系統帳號與主機名，在不能自動推導身分的環境則會直接提交失敗。
最小翻紅測試：新增 `t_probe_boundary_fake_identity`；`work = make_sandbox(src)` 後斷言 `git -C work config user.name == probe`、`user.email == probe@local`，再提交並核對作者。
實際輸出：`sandbox_user_name=<missing>`；`commit_rc=0`；`author=<本機帳號> <本機帳號@主機名>`。

Finding 3 — `--keep` 遇到讀碼題排最後時不保留任何普通題副本

severity: major
blocking: true
引句:「讀碼標記的現場永不保留；普通題只保留最後一場通過隔離驗收的副本。」
file: `scripts/scenario_probe.py:1042`
file: `scripts/scenario_probe.py:1043`
具體輸入→路徑→錯誤：情境順序為一個普通題後接一個 `source_probe`，並帶 `--keep`；普通題因不是整批 `final_attempt` 而被刪除，最後讀碼題又因 `token` 禁止保留，結果與 S4 宣稱的「最後一個普通題副本」不符。
最小翻紅測試：新增 `t_probe_boundary_keep_before_source_probe`，stub 兩個 runner 成功後斷言普通題副本仍存在、讀碼題副本已刪除，且 stderr 有保留路徑。
實際輸出：`rc=0`；`ordinary.exists=False`；`source-last.exists=False`；`retained_line=[]`。

表態記錄 `py-eventloop na`：已讀，無 finding。程式是同步 CLI 批次，未使用事件迴圈；串行流程承擔逐場隔離、限額重試與 fatal 停批語意。

固定席逐條核對：`Systems/codex-harness`、`Systems/測試假綠形態` 直接受上述 findings 影響；`Systems/lumos-cli-read`、`Systems/bound-tests-gate`、`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`、`Systems/lumos-cli-lifecycle`、`Systems/slim-get-一行安裝`、`Systems/slim-install-安裝器`、`Systems/slim-uninstall-一行卸載`、`Projects/規格落成可驗收條件_計劃`、`Systems/lumos-deinit`、`Projects/逃逸自動記_計劃`、`Systems/節點範圍與索引守衛`、`Systems/cochange-guard`、`Systems/check-r-guard`：已讀，無 finding。

其餘審過範圍：凍結 patch 1307 行與 SHA-256 相符；S1–S7、實際 `scenario_probe.py`、setup fatal、逐場 cleanup fatal、限額重試、JSON/history 新舊欄位及 `source_evidence` 空 ID 路徑均已讀。`python3.14 scripts/test_lumos.py -k probe_boundary_` 現況為 29 passed、0 failed。

總結：最嚴重 severity blocker，blocking 3 條。
