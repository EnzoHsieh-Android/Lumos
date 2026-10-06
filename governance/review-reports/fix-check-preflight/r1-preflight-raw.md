severity: major

finding severity: major  
原文：「應照常跑修正與合約測試，綠才通過，任一真紅應回 1 且不得略過另一段。」file: `docs/lumos-toolchain-knowledge/Projects/修正關卡先驗便宜條件_計劃.md:41`；測試只斷言「兩段 runner 都啟動」且 `launches == 2`。file: `scripts/test_lumos.py:69656`。症狀：同一段錯跑兩次、另一段完全漏跑仍可能假綠。判準：日誌須區分修正測試與合約測試，並各自斷言恰有執行。這是核心安全宣稱的機械驗證缺口，但不必改核心裁定。

finding severity: minor  
原文：「輸出兩段未執行與修好紀錄後重跑提示。」file: `docs/lumos-toolchain-knowledge/Projects/修正關卡先驗便宜條件_計劃.md:31`；測試僅檢查任一 note 同時含「未執行」與「重跑」。file: `scripts/test_lumos.py:69627`。症狀：一條籠統提示即可通過，未證明修正測試與受波及合約測試兩段都被明示。判準：分別斷言兩種測試的未執行提示，並包含修好紀錄後重跑指示。