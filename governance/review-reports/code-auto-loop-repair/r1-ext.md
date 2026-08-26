### ext-f1 處置寫入失敗仍標記完成，已 pop 的 gap 會永久丟失

severity: major

引句：「GAP_DISPOSED=1   # 已記 covered=有去向,trap 不再放回」

佐證:file: `governance/autonomous-loop.sh:328`

說明：`mark_covered` 明確以 `|| true` 吞掉失敗，下一行卻無條件設 `GAP_DISPOSED=1`；未收斂與三個 tier-blocked 分支也在 requeue 回傳 `?` 時照樣如此。這會阻止 EXIT trap 補放回，造成 backlog 丟件，且 log 還會誤報已永久 covered／已處置。

### ext-f2 pending 寫入失敗仍消化 gap，並發送「已備好」假成功通知

severity: major

引句：「GAP_DISPOSED=1   # 收斂=有去向(gap 已消化成 spec),trap 不放回」

佐證:file: `governance/autonomous-loop.sh:443`

說明：`cp` 失敗只改 outcome，後續仍無條件設 `GAP_DISPOSED=1`，因此 trap 不會把 gap 放回；spec 仍只在 scratch，退出後隨目錄清理而丟失。接著程式還印「spec + 可信度報告寫入」並發送「待你看 pending」通知，形成可操作的假成功。

### ext-f3 跳過壞 JSONL 行後的任何正常寫入都會把原始壞行無聲刪除

severity: major

引句：「逐行讀 backlog;壞行跳過並在 stderr 記一句」

佐證:file: `governance/autonomous_loop/backlog.py:12`

說明：`load_backlog` 不保留無法解析的原始行，而 `add_gaps`、`pop_top`、衰減及 requeue 隨後都會用 `_save` 整檔覆寫。於是原本只是「跳過並警告」的半寫入資料，在下一次正常操作時變成不可恢復的永久刪除；新增測試也只驗證讀取結果，未驗證壞行在後續寫入後仍可復原。

### ext-f4 backlog 與 decay state 非同一原子提交，中斷後會重複衰減甚至提前歸檔

severity: major

引句：「自驗過才縮 live——中斷最壞重複、不會遺失。」

佐證:file: `governance/autonomous_loop/backlog.py:110`

說明：程式先 `_save(path, kept)` 改寫 live backlog，之後才用非原子 `state.write_text` 更新日期。若兩步之間中斷或 state 寫入失敗，下次仍按舊日期的完整天數再次衰減已衰減過的分數，可能讓項目過早跌破 floor 並被歸檔；這不只是允許的 archive 重複，而是排序與存活資料本身被錯改。

### 試過但乾淨的攻擊面

- `run_ledger` 逐筆統計同日多筆、七日邊界及舊格式列隔離。
- `consecutive_fail_days` 對混合成功／失敗日與無跑日的處理。
- `outcome`／`usd` 的 CLI 型別與值域驗證。
- `pop_top` 的分數、`last_seen`、`source_date` 三鍵排序。
- archive append 失敗時保持 live backlog 不動。
- NO_JSON／PARSE_FAIL 死因分類與成本抽取解耦。
- trap 的一次性重入防護及 canary record 失敗後繼續七天彙總。
