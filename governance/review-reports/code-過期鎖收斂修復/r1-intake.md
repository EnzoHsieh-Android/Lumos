# code-過期鎖收斂修復 r1 收貨與處置

審材：`r1-snapshot.patch`，`2db51cc4..80b13355` 的程式／hook／測試／錨點差異，1527 行，SHA256 `1aebbc4ffa3edd43e512da6bc24e267dcd12d2c134c9225fe6aabf41a4b300ca`。分支全部差異另含圖譜與治理卷證；風險分級按全部 `2db51cc4..HEAD` 算為 standard。兩席在收齊前沒有改審材。正確性席與架構席報告原文各存 `r1-single-reviewer.md`、`r1-architecture.md`。

## 重現與去向

| ID | 觀察及編排者重現 | 去向 |
|---|---|---|
| F1 | HIT。無 `getuid`、私有快取目錄被連結到外部目錄時，舊讀取回 `{'text':'ATTACKER-CONTROLLED'}`；`t_lens_cache_read_rejects_untrusted_path_without_getuid` 前置成立、核心斷言先紅，讀取端補私有目錄／檔案檢查後轉綠。 | 折入；major，code。 |
| F2 | HIT。最後一次輪詢後模擬背景完成且清鎖，舊碼回 rc5、`lock_uncertain=true`；`t_lens_deadline_final_cache_read` 前置成立、核心斷言先紅，逾時分類前最後讀快取後轉綠。 | 折入；minor，code。 |

修後兩支新測試共 6 條斷言全綠；`lens_warmer` 13、`lens_stale_lock_reports_uncertainty` 9、真背景 `lens_timeout_keeps_warming_cache` 8 條全綠，零 skip。修後累積程式差異為 `r1-result.patch`；下一輪只審 r1 之後的修補差異並回看周邊回歸。

`quote-check` 兩句引文均錨在凍結 patch；`refcheck` 三個座標有效；`report-normalize` 已符合規格。正確性席的 `seat-check` 有 7 個派工材料未逐字提及的觀測提醒，沒有超出範圍引句；架構席獨立覆核模組邊界、hook、三份計劃的條款綁定，回 clean。r2 派工須明列快取讀取與期限末修補的相鄰路徑，不把 r1 clean 架構席當成修後審查。

外家否決席未取得；standard 編制為一位正確性席加一位架構席，結論只稱同家族審查與本地實測。
