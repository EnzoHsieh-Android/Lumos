severity: major

審材：`r1-snapshot.patch`。

審材 SHA-256 已核對：`09bf4aa0cdfbaae297e274250d66887dc8898b832e24be23b3c282a2b5e64b9b`。

1. 分層／依賴方向：對齊。CLI 邊界負責編排，同檔 helper 負責 Git 與檔案系統操作，未跨層直呼測試或圖譜。此形狀與既有腳本一致。file: `scripts/scenario_probe.py:608`、`scripts/slim-gen.py:318`、`scripts/slim-scan.py:143`、`scripts/usage_scan.py:230`。已讀,無 finding。

2. 命名與錯誤處理：不對齊。錯誤在底層保留原因、在 CLI 邊界轉成結果，做法對齊；但 `_remove_source_sandbox` 已用於普通題及批次基線，名稱仍限定 source probe。

severity: minor
blocking: false
引句:「讀碼標記的現場永不保留；普通題只保留最後一場通過隔離驗收的副本。」
file: `scripts/scenario_probe.py:1052`
`_remove_source_sandbox` 同時由普通逐場副本與批次基線呼叫，建議改成反映通用沙盒生命週期的名稱；對照既有腳本的 `build`、`collect_edits`、`scan_python_file`、`scan` 均按實際責任命名。file: `scripts/scenario_probe.py:1096`、`scripts/slim-gen.py:62`、`scripts/slim-scan.py:121`、`scripts/usage_scan.py:72`。

3. 是否引入第二種做法：不對齊。正式 `main()` 已另寫 token 建立、逐場複製、遮罩、清理與 fatal 分類，但舊 `_run_source_attempt` 仍存在且由測試獨立維護，形成兩套嘗試生命週期。

severity: major
blocking: true
引句:「baseline 已套用 arm；每場從它複製，不能讓前場或來源的後續修改滲入。」
file: `scripts/scenario_probe.py:1018`
對照：舊入口仍在 `scripts/scenario_probe.py:455`，只剩測試呼叫於 `scripts/test_lumos.py:36841`；正式路徑自行實作於 `scripts/scenario_probe.py:1011`、`scripts/scenario_probe.py:1019`、`scripts/scenario_probe.py:1052`。應刪除舊 helper 與其專屬測試，或讓 `main()` 共用一個能表達基線、保留策略及 fatal 分類的單一 attempt helper。

最小重現：以 AST 檢查 main 是否呼叫 _run_source_attempt；若沒有，且 main 同時直接呼叫 make_sandbox、secrets.token_hex、_remove_source_sandbox，退出 1。實跑結果：`RED: main 已另做 token/建副本/清理，_run_source_attempt 無生產呼叫，形成兩套嘗試生命週期`；`rc=1`。

固定席逐條：`codex-harness` 不對齊，節點記錄「批次凍結後每場複製」，舊 helper 仍保留直接從來源建場的另一條路。`測試假綠形態` 對齊，新隔離測試具現場前置斷言。`lumos-cli-read`、`bound-tests-gate`、`canary-audit`、`design-loop`、`guard-kill`、`lumos-cli-lifecycle`：已讀,無 finding。

總結: 最嚴重 severity major，blocking 1 條。
