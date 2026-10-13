severity: minor

我看了判準本體、處置閘每條新分支、比較模式的 `_read` 和擋下事件的 note,也實際跑了。`python3.14 scripts/test_lumos.py -k quote_full_span` 結果是 79 項全過。另外手寫了 14 組刁鑽輸入跑 `_quote_rows_full_span_v1` 和舊判準對照:巢狀、混型、前後落單開引號、引句內嵌標籤、空引句、CRLF、兩條都沒閉合、落單收尾引號的位置。結果都符合設計。

在比較模式另外造了一份帳來跑,涵蓋符號連結迴圈、管線檔、目錄路徑、`..` 路徑、孤立代理字元和 NUL 路徑。全部走「讀不到」,沒有 traceback,也沒有卡住。`UnicodeDecodeError` 在 `except ValueError` 裡先判 `isinstance` 再原樣重丟,順序正確。

1. 比較模式改用 `read_bytes().decode`,換行處理跟處置閘、`quote-check` 單檔不同
severity: minor
blocking: 否
引句:「return fp.read_bytes().decode("utf-8")」
file: `scripts/lumos:26696-26710`
- 本輪修補把原本的 `read_text(encoding="utf-8")` 換成這一行。處置閘和 `cmd_quote_check` 仍用 `read_text`,會把單獨的 `\r` 換成 `\n`。
- 比較模式的位元組讀法保留 `\r`。`_quote_norm` 剝 blockquote 記號用的是 `(?m)^\s*>`,而 `^` 只認 `\n` 後面。
- 我造了一份快照:`第一行\r> 甲乙丙丁戊己庚辛壬癸子丑寅卯\r尾`,報告引句是 `第一行 甲乙丙丁戊己庚辛壬癸子丑寅卯`。
  - 用 `read_text` 讀(處置閘的讀法)時,舊判準判 ok。
  - 用位元組讀法(比較模式現在的讀法)時,舊判準判 miss。
- 所以含單獨 `\r` 的檔,比較模式的「兩版都錨定」等格數字會跟閘實際判的不同。
- 這份交叉表是第一條 REVISIT 的依據。CRLF(`\r\n`)沒有影響,單獨 `\r` 的檔很少見。
- 修法:解碼後再 `.replace("\r\n","\n").replace("\r","\n")`,或讀檔時用 `newline=None`。

2. 處置閘「判準丟例外照常往外丟 MemoryError」沒有測試守住
severity: minor
blocking: 否
引句:「except MemoryError:      # 資源不足不是判準的錯,照常往外丟」
file: `scripts/lumos:26523`
- `scripts/test_lumos.py` 裡搜不到 `MemoryError`,上一輪新增的測試也沒有涵蓋。
- 把 `except MemoryError: raise` 刪掉,測試照綠,因為 `MemoryError` 會被下面的 `except Exception` 接住,改判 quote 失敗。
- 邏輯本身正確,缺的是一支「把它拿掉會紅」的測試。
- 判準丟一般例外、讀檔失敗、零引句、章不認得這幾條路徑的 fails 和輸出,我讀程式確認是對的。零引句和讀檔失敗現在也會印診斷指令。

沒有找到其他會讓判定出錯的問題。以下幾點記一下:
- 引句後面緊接另一對平衡的引號,例如 `引句:「真實」「編造」`,會判通過,因為括號是平衡的。計劃已明講「引號外的文字不算引句」,所以這是設計取捨,不是 bug。
- `snippet` 先過濾控制字元,再 `.strip()[:60]`。全被濾光時 note 結尾是空的 `quote=`,不影響欄位順序。
- `_quote_block_note` 的 `kind` 計算出例外時,`cats` 被整個覆蓋成 `err`,會丟掉原本的 `cats`。這是計劃寫明的行為。

實驗目錄已刪除。

總結:最高等級 minor,blocking 共 0 條
