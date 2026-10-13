severity: minor

我沒找到 blocking 的問題。查過的範圍如下:
- 新判準 `full-span-v1`:手寫邊界案例,加 20 萬組隨機字串的新舊對照。
- 舊判準 `_quote_rows_legacy`:函式本體逐字等於基準提交的 `_quote_rows`。
- 讀章與處置閘:各條路徑。
- 寫側蓋章與擋下事件:`_quote_block_note` 的 kind、cats、片段、指紋。
- 手動 `quote-check`:拿掉比較模式後的參數處理。
- 殘骸:`scripts/lumos`、`scripts/test_lumos.py`、`skills/` 裡沒有 `--compare-rules` 或比較模式用的常數殘留。
- 效能:最差輸入約 240 萬到 500 萬字,新判準都在 1 秒內。包括 60 萬個未閉合標籤、200 萬層巢狀、300 萬個落單收尾引號。
- 測試:`python3.14 scripts/test_lumos.py -k quote` 173 條全過。

隨機對照中,兩版判準在「零引句回 None」上沒有不一致,也沒有例外或型別錯誤,格式不合列的 kind 都是 `unclosed` 或 `stray`。手動 `quote-check` 缺報告或缺 `--spec` 都回 rc2。`--rule bogus` 被 argparse 擋下,`--rule` 也能正確切換判準。

1. 引句後面緊接第二組括號,後半仍可編造
severity: minor
blocking: 否
引句:「零引句回 None。每一步整份報告只掃一次,總成本與報告長度成正比。」
file: `scripts/lumos:25861`
- 輸入:`引句:「真實片段」「完全編造的後半內容」`,快照只含前半。
- 實測 `full-span-v1` 回 `ok=True`。第二組 `「…」` 是平衡的括號,不算落單收尾引號,也不是引句內容,所以沒人驗。
- 舊判準同樣放行,不算新退步。但這個修補的初衷就是後半可編造,這個形狀沒被擋住。⚠ 設計上「引號外不驗」可能是故意收窄,請規格方確認。

2. 拿掉比較模式後,手動 `quote-check` 的參數宣告還是為它留的形狀
severity: minor
blocking: 否
引句:「p.add_argument("qc_report", nargs="?", default=None, metavar="報告.md")」
file: `scripts/lumos:53321`
- 報告改成選填,`--spec` 的說明還寫「一般模式必填」。
- 現在只剩單一模式,這兩個該回到 `required`;現在靠 `cmd_quote_check` 裡的手動判斷湊出 rc2。
- 行為沒錯(缺任何一個都回 rc2),只是殘骸,而且「一般模式」的說法會誤導下一個讀的人。

3. 診斷行的註解和實作不符
severity: minor
blocking: 否
引句:「整行再過 _esc_clean(路徑裡的控制字元不印到終端;r3 資安席)」
file: `scripts/lumos:26522`
- 註解說整行過 `_esc_clean`,r4 修補後改成「路徑含控制字元或過長就改印說明」,`_esc_clean` 已經不在這條路徑上。
- 行為正確:路徑含特殊字元或超過 1000 字就不印可貼的指令。
- 殘留的舊說法會讓下一輪審查席誤報「沒消毒」。

總結:最高等級 minor,blocking 共 0 條

實驗目錄已刪除,沒有改動 repo 的任何檔案。
