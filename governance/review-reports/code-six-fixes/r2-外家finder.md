severity: major
blocking: 是
引句:「"fake_sync": fake, "degraded": False}, ensure_ascii=False))」
file: `scripts/lumos:14294`
場景: 可翻紅重現：測試中令 `_delguard_vault_scan` 到 deadline 後回傳部分結果，再以 `--json` 執行；治理帳記為 `timeout-partial`，但輸出仍宣稱 `"degraded": false`，自動消費端會把不完整掃描誤判為完整成功。

severity: minor
blocking: 否
引句:「additionalContext": TIMEOUT_NOTE.format(what="(Codex 席:--claim)", cmd="--status", n=10)」
file: `scripts/hooks/claude/dispatch-lens-hook.py:79`
場景: Codex 的 `--claim` 超時後提示使用 `dispatch-lens --status`「看它算不算得出來」，但 `--status` 只讀武裝狀態、不重算也不認領鏡頭，因此操作者可能得到正常狀態後誤以為超時問題已排除。

max severity: major
