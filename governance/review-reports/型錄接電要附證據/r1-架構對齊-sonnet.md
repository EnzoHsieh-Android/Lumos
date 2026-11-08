severity: major

**第 1 問 分層:是第二種做法**

型錄現在有兩個放查證的地方,都在型錄檔裡面:
- 主表來源欄的〔查證 日期:網址〕。`_VERIFIED_RE` 認這個格式(`configs/ast-grep/kotlin-android/check.py:679`),`catalog_unverified` 靠它找出還沒查證的列(`check.py:683`)。
- 〈待查證〉節。`_pending_table`(`check.py:426`)與 `pending_problems`(`check.py:447`)跟主表做雙向比對,同一份檔、同一套讀法。

設計要把「壞例、官方頁逐字一句、網址、查證日期」另放一支新的 TSV 檔。repo 裡沒有任何 `.tsv` 檔(`git ls-files` 只見 md、json、jsonl 與程式檔)。型錄也已經有「列編號、網址、日期」的查證載體,新檔等於為同一件事(每列的查證證據)再開一個放處。

計劃自己也承認兩支檔會漂,所以得另寫雙向比對來補。型錄內部的〈待查證〉做法本來就不需要這道補丁。

finding 1
引句:「`skills/kotlin-idioms/checks-catalog-wiring.tsv`(新增),每列一筆:型錄列編號、檢查、擋得到的壞例、官方頁或原始碼逐字一句、網址、查證日期」
引句:「證據表與型錄分兩支檔會漂:自檢雙向比對(型錄有證據沒有、證據有型錄沒有都報)。」
對照:`configs/ast-grep/kotlin-android/check.py:679`、`check.py:426`、`check.py:447`
severity: major
blocking: 是

**第 2 問 命名與寫法:大致一致,有一處不一致**

- 檔名 `checks-catalog-wiring.tsv` 沿用同目錄 `checks-catalog.md` 的前綴,命名一致。
- 錯誤訊息的形狀沒問題。既有問題一律回 `(列編號, 一句中文)`,例如 `check.py:454` 的 `(rid, "主表還有待查或待核對的來源,〈待查證〉沒列")`。計劃寫的「要補哪一列、補到證據表」也是指名列編號,沒有不一致。
- 不一致在格式:`.tsv` 是專案裡沒有的新資料格式。鄰居的輔助資料是 `.kt.txt`,由專屬讀取函式處理(`situation_samples`,`check.py:536`),放在 `configs/ast-grep/kotlin-android/samples/situation/`。型錄本身是 `|` 分欄的 markdown 表,用 `_cells`(`check.py:153`)讀。
- 這個證據檔放在 `skills/kotlin-idioms/`,卻由 `configs/` 下的 check.py 讀。

finding 2
引句:「每筆的網址要是 https 開頭、日期是 YYYY-MM-DD、壞例與原文欄不空」
對照:`configs/ast-grep/kotlin-android/check.py:679`。這條要求在 `_VERIFIED_RE` 已經有一套格式驗證(網址要 `https?://`、日期要 `\d{4}-\d{2}-\d{2}`),新檔另寫一套,兩邊會漂。
severity: minor
blocking: 否

**第 3 問 第二種做法:⚠ 判不準,計劃沒寫清楚**

- 型錄這一側大概會沿用既有讀法。計劃說「宣稱接電的列」「自帶證據的列」要讀通電批次欄(第 10 欄)與情境欄(第 8 欄),通電批次欄與情境欄都屬主表,可以走 `main_rows`(`check.py:656`,註解寫「主表的唯一讀法」)。接電段判斷走 `batch4_expected_tags`(`check.py:124`),計劃沒說要換掉。
- TSV 這一側沒有任何既有讀法可用,必須新寫一個 tab 分欄的讀取器,計劃沒交代它放哪裡、錯誤怎麼處理。
- 計劃沒說明自檢要接進 `catalog_problems`,還是另起獨立函式。`catalog_problems` 目前把主表、〈待查證〉、統計各自接成 `pending_problems(text, rows)`、`stats_problems(text, rows, rules)` 這類函式,接受 `main_rows` 讀出的 rows。

這一問沒有證據顯示違反,所以不列 major。只要實作時型錄側不改走自己的切分(例如不另用 `split("|")` 讀型錄),就不算第二套讀法。建議計劃補一句「型錄側一律用 `main_rows`」。

finding 3
引句:「宣稱接電的列,要不是自帶證據的列、就要在證據表有一筆;證據表的每一筆要對得到一列宣稱接電的列」
severity: minor
blocking: 否

不對齊共 3 條,其中 major 1 條
