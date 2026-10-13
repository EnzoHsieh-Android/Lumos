severity: minor

我實際載入 `scripts/lumos` 跑過比較模式、擋下事件的片段、處置閘診斷和新舊兩版判準,沒找到 blocking 級的錯。fd 洩漏、`fstat`、讀上限加一、decode 與換行統一的順序都沒問題。實驗目錄已刪。

驗證過的項目:
- **比較模式 `_read`**:對管線、指向管線的符號連結、目錄、不存在的路徑、repo 外路徑、`/dev/zero`、含 NUL 的路徑、孤立代理字元路徑、非 UTF-8 檔,都在 10 秒內正確歸入「讀不到」或「非 UTF-8」,沒有卡住。
- **`UnicodeDecodeError` 傳遞**:解碼在 `with` 之後做,例外照常傳到呼叫端,被算成非 UTF-8,沒有被轉成 `OSError`。
- **fd 關閉**:所有錯誤路徑都在 `with` 內,fd 會關。
- **單獨 `\r`**:換行統一與 `read_text` 一致,補的測試在還原後會翻紅。
- **擋下片段**:控制字元、`\u202e`、全是控制字元、孤立代理字元、換行偽造 `report=` 的輸入,都被清掉或排在 note 最後。清光時記 `-`。
- **新判準本體**:在 5.4 MB 快照、20 萬個未閉合標籤、50 萬層巢狀、10 萬個落單收尾引號下,每項約 0.2 秒,沒有 O(n²)。

1. 舊判準遇到大量未閉合開引號會平方級變慢
severity: minor
blocking: 否
引句:「quotes = [m.group(1) if m.group(1) is not None else m.group(2)」
file: `scripts/lumos:25912`
- 輸入:報告含 N 個 `引句:「` 而沒有任何 `」`。
- 實測:N=5000(2 萬字元)0.28 秒,N=10000 1.09 秒,N=20000(8 萬字元)4.3 秒,N=20 萬字元超過 2 分鐘。
- 原因:`「([^」]+)」` 在每個開引號處都掃到檔尾。
- 影響:這支舊判準是照規定一字不改的,所以不是本輪引入。但比較模式現在對帳上每份報告都跑舊判準,一份惡意或壞掉的報告會讓整本比較報表卡死,新判準那一側沒有這個問題。
- 建議:不改舊判準,在比較模式對報告長度設上限,或照 `_QUOTE_COMPARE_MAX_BYTES` 的做法另設一個報告大小上限。

2. 寫側和比較模式的記憶體不足路徑沒有測試守住
severity: minor
blocking: 否
引句:「except MemoryError:   # 資源不足不是判準的錯,三處」
file: `scripts/lumos:25832`
- 補的測試只用 `exc="MemoryError"` 打處置閘。
- 把 `_quote_block_note` 裡的 `except MemoryError: raise` 刪掉,`except Exception` 會把它吞成 `kind=unknown cats=err`。
- 我沒有實際還原跑測試,這條是讀 `r3-repair.patch` 的測試段推出來的,所以標 ⚠。

3. 開頭是 `-` 的路徑補 `./` 沒有測試守住
severity: minor
blocking: 否
引句:「_qarg = lambda x: _sh_quote(("./" + str(x)) if str(x).startswith("-") else str(x))」
file: `scripts/lumos:26518`
- 新增的測試只覆蓋含空白的路徑要加引號,沒有開頭是 `-` 的路徑。
- 把補 `./` 那段拿掉,測試仍然全綠。
- 另外這是 `lambda` 賦值,ruff 的 E731 會報。但這個 repo 沒有 ruff 設定,同檔已有多處同樣寫法,所以只提醒不當成問題。

總結:最高等級 minor,blocking 共 0 條
