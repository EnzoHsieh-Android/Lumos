severity: minor
審材：governance/review-reports/探針隔離與清理收斂/r1-snapshot.md
severity: minor
blocking: 否
引句:「所有題目及重試改用各自副本，跑完在 `finally` 刪除」
finding: 設計把逐次副本與清理擴大到所有題目，但現有抽象仍叫 `SourceProbeCleanupError`、`_remove_source_sandbox`、`_run_source_attempt`。實作時應抽成通用 attempt／sandbox 清理層，再由 source-probe 包裝標記注入；否則普通題的清理錯誤會穿過讀碼題專用命名，責任邊界會混淆。file: `scripts/scenario_probe.py:400`、file: `scripts/scenario_probe.py:447`、file: `scripts/scenario_probe.py:454`。

1. 分層依賴：已讀，無 finding。副本建立、Git 邊界驗收、runner 編排與事件判讀都留在情境探針內，無跨層直呼。file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:6`、file: `scripts/scenario_probe.py:466`、file: `scripts/scenario_probe.py:829`。
2. 命名／錯誤處理：除上述 minor 外，無 finding。清理失敗 fatal 語意沿用現有摘要與主程式錯誤處理。file: `scripts/scenario_probe.py:447`、file: `scripts/scenario_probe.py:786`、file: `scripts/scenario_probe.py:921`。
3. 第二種做法：已讀，無 finding。將 source-probe 已有的逐次獨立副本提升為共同路徑，移除普通題共用副本加 checkout/clean。file: `scripts/scenario_probe.py:454`、file: `scripts/scenario_probe.py:945`。
4. lands_in：已讀，無 finding。`Systems/codex-harness` 與 `Systems/測試假綠形態` 是兩支改動檔案既有的家。file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:8`、file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:42`。

總結最嚴重 severity: minor；blocking 0 條。
