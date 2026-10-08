severity: blocker

審材：`r1-snapshot.patch`，SHA-256 `09bf4aa0cdfbaae297e274250d66887dc8898b832e24be23b3c282a2b5e64b9b`，1307 行。

finding B1

severity: blocker

blocking: 是

引句:「if name == ".git" or name == ".gitmodules":」

file: `scripts/scenario_probe.py:549`

具體輸入→路徑→錯誤：在目前 macOS 大小寫不敏感檔案系統，巢狀 repo 的 `.git` 改名為 `.GIT` → `os.walk` 回傳 `.GIT`，大小寫敏感字串比較漏過 → `_check_gitlinks` 又早於 `git add -A`，當時外層索引尚無 gitlink → 副本保留巢狀 remote，且不受頂層 pre-push hook 保護，可 dry-run push 成功。這直接違反 S1。

最小重現：在臨時外層 Git repo 建 `lib/.GIT` 巢狀 repo，後者 remote 指臨時 bare repo。`make_sandbox(src)` 回 ACCEPTED；副本 `git -C lib push --dry-run origin main` 回 0，stderr 沒有「探針沙盒:禁止 push」。

finding B2

severity: major

blocking: 是

引句:「remote = subprocess.run(["git", "remote"], cwd=str(work), env=genv,」

file: `scripts/scenario_probe.py:593`

具體輸入→路徑→錯誤：父環境設 `GIT_TRACE=<真來源檔>` → `_git_env` 只移除 `GIT_CONFIG*` 與部分定位變數，保留 `GIT_TRACE*` → `make_sandbox` 執行 Git 命令時，Git 直接向指定來源檔追加 trace → 真來源在複製與模型啟動前已被改寫。這違反 S3 的來源／外部 byte 不變要求。

最小重現：臨時 repo 的來源檔 `actual-source-byte` 原為 9 bytes，設 `GIT_TRACE` 指向它後呼叫 `make_sandbox(src)`；結果 4577 bytes，`actual_source_changed=True`，新增行含 `trace: resolved executable path`。

驗證：`python3.14 scripts/test_lumos.py -k probe_boundary` 得到 `29 passed, 0 failed`；現有測試未涵蓋上述兩個入口。

S1：finding B1。S2：已讀,無 finding。S3：finding B2。表態記錄 `py-eventloop na`：已讀,無 finding；改動仍是同步命令列流程。

`Systems/codex-harness`：finding B1、B2。`Systems/測試假綠形態`：finding B1、B2；現有邊界子集全綠但兩個反例仍成立。`Systems/lumos-cli-read`、`Systems/bound-tests-gate`、`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`、`Systems/lumos-cli-lifecycle`：已讀,無 finding。

總結：最嚴重 severity=blocker，blocking=2 條。
