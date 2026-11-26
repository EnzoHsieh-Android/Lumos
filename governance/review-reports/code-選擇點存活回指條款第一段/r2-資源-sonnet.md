severity: minor

**finding 1**
severity: minor
blocking: 否
`scripts/lumos:29295` 與 `scripts/lumos:29531`。不掛覆蓋的重跑自己被剩下時限截斷後,逾時結果被當成這支的真基準寫進 `baselines`。
引句:「plain = _kill_run(self._cmd[n], self.c.run_dir, min(self.full, max(self.prep.remaining(), 1.0)), merge=self.prep)」
失敗場景:
- 外層 `cap` 取到 `full`(剩餘時限 ≥ 600 秒時),掛覆蓋跑紅。
- 這一趟跑掉大半剩餘時間後,重跑的上限變成 `min(full, remaining)`,小於 `full`。
- 重跑在這個上限內逾時。`red_rerun` 回傳的 `plain[3]` 為真。
- `_kill_measure_singles` 只拿外層 `cap` 判斷是否被截斷(`scripts/lumos:29531` 的 `if b_to and cap < full`),外層 `cap` 等於 `full`,所以不認這是截斷。
- 這支測試被寫成「逾時的基準」,之後 `cmd_guard_kill` 對它的壞法判 abort,理由是「baseline 非綠」,但它其實是綠的。
影響範圍:此時總時限已所剩無幾,多半也跑不了壞法,所以只是紀錄錯誤,不會讓判定出錯。修法是 `red_rerun` 在重跑被截斷而逾時時,也回報「被截斷、不寫基準」。未能重現,所以降為 minor。

**finding 2**
severity: minor
blocking: 否
`scripts/lumos:29292`。掛覆蓋逾時且 `cap` 等於 `full` 時,不算被截斷,會再跑一趟不掛覆蓋的,而斷路要連續 3 支才跳。
引句:「if res[3] and cap < self.full:」
失敗場景:
- 覆蓋設定讓測試卡死,每支吃 `full`(600 秒)的逾時,不掛覆蓋再跑一趟。
- 斷路器要連續 3 支才跳,3 × (600 + t) 已經超過預設 1800 秒的總時限。
- 到斷路時剩餘時限幾乎用完,壞法階段拿不到時間。這反而比不開覆蓋更慢,和計劃第 185 行「最壞不會比現在慢超過前 5 支多 1.4 秒 + 總時限四分之一」的上限不符。
- 掛覆蓋就逾時是比掛覆蓋就紅更強的訊號,可以改成第一支掛覆蓋逾時就斷路,或把這種逾時快速記進斷路器。
未能重現,所以降為 minor。

另外查過、沒有再發現的位置:
- 訊號收程序:`_kill_signal_marked` 涵蓋覆蓋基準、重跑、分析三種呼叫,`after` 先看 `interrupted` 才進 `red_rerun`。
- 分析逾時:有 `cap`,並先檢查剩餘時限是否夠。
- 讀大檔:單份覆蓋資料檔和分析輸出的讀取上限是 8MB,超過會判不明,不會出錯。
- 快取長大:`_choice_cov_prune` 每次 choice-kill 開頭只留 2 個 `at_sha`。
- 二次方:`_lines` 裡的 list 成員判斷實測 30 萬列只要約 1.9 秒,可忽略。
- `choice-points` 路徑:只查存活行並帶 300 秒期限。

總結:最高等級是 minor
