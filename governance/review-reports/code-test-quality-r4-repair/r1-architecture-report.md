severity: major

## A1：同一套 test-quality 程序群清理仍分成兩種語意

severity: major
blocking: true
引句:「if proc is not None:」
file: `governance/eval/test_quality_handbook.py:249`

與既有對照：本次將 handbook runner 改為父程序已退出後仍呼叫 `killpg`，但同層 CLI runner 的 `terminate_group()` 仍只在 `proc.returncode is None` 時清理，見 file: `scripts/test_quality.py:49`。兩者都以 `start_new_session=True` 執行外部測試程序，卻維持不同的 descendant 清理保證；日後從 CLI 收證時，launcher 先退出仍會留下 worker，形成實質維護分岔。

最小重現：launcher 啟動關閉 stdout/stderr 的長跑 worker 後 rc1；`run_capture_command()` 返回後 worker 仍存活。應讓兩個 runner 共用同一項程序群清理政策，或同步修正 `scripts/test_quality.py` 並加入 launcher 已退出、worker 仍存活的 CLI 控制。

## 其他已讀，無 finding

- Semgrep 結果仍由既有 `backend_findings()` 轉換，沒有新增第二套 parser；責任寫入真正的 `Systems/test-quality-multilang.md`。
- sidecar 指紋沿既有 `_TEST_QUALITY_BUNDLE_DIGESTS` 管理；`Systems/lumos-cli-lifecycle.md` 與 `Systems/test-quality-cli.md` 都確實擁有 `scripts/lumos`。
- JUnit 錯誤 reason 的測試只收緊既有合約，沒有新增錯誤回傳通道。
- handbook 程序控制及測試都歸 `Systems/test-quality-handbook.md`，檔案家庭對應正確。

總結：最嚴重 severity 為 major，blocking 共 1 條。
