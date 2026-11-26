severity: minor

我只讀了修補差異和相關程式碼,沒有實際跑測試或重現。上一輪的資源修補(斷路、截斷、`after` 回 6 項、快取、`_write_bytes_atomic`)看起來都接得起來,沒有新的 major。只有一個 minor。

修補三問:
- **修到沒:** 掛覆蓋跑滿單支上限會當場斷路。不掛的重跑被截斷時回 `cut` 為真、不寫基準。`after` 固定回 6 項,而且 `_kill_measure_singles` 只有 `wrap=cb.wrap, after=cb.after` 這一個呼叫點,所以回傳形狀改了沒有別的呼叫端受影響。`_choice_cov_prune` 保留的一個算這次的 at_sha。Robolectric 0 的資料不進快取,快取讀到也會刪掉。存快取改走 `_write_bytes_atomic`,例外(含 Ctrl-C)會清暫存檔。
- **有沒有引入新問題:** 只有下面那條 minor。
- **同類位置還有沒有:**
  - `robo_zero` 在 `cached()` 裡讓每份快取多解析幾次(`_choice_cov_exec_classes` 加 `proj_hits` 加 `exec_robo`),但都是線性、單檔上限 8MB,不會變二次方,不構成問題。
  - scratch 檔名用 `len(self.got)` 算,`got` 只增不減,不會互相蓋掉。
  - `choice-cov/<at_sha>/` 底下每支測試一份檔,at_sha 之外的資料夾由 prune 控制在 2 個,不會無限長大。
  - 分析 JSON 的 `noclasses`、`nolines` 兩個欄位在 `scripts/lumos:79657` 一律輸出,新增的 `type(...) is not bool` 嚴格檢查不會誤判正常輸出。

severity: minor
blocking: 否
`scripts/lumos:29298`:`red_rerun` 在掛覆蓋跑滿單支上限(`res[3]` 為真且 `cap == full`)時,先斷路,再跑不掛覆蓋的重跑。如果那支測試本來就卡住或超過上限(不掛覆蓋也逾時),斷路原因仍寫成「覆蓋設定讓測試卡住」。其餘測試因此全部不再掛覆蓋,這次壞法都跑全部守的測試,等於為一支本來就很慢的測試放掉整次加速。還要多燒一趟最多 600 秒的重跑。這只是少省時間,判定結果仍正確。建議先跑重跑,確認不掛覆蓋時綠才斷路。
引句:「if res[3] and not self.tripped:   # 掛覆蓋跑滿單支上限:比掛覆蓋紅更強的訊號,當場斷路,不等連續 3 支」

總結:最高等級是 minor
