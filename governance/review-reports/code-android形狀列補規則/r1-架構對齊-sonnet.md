severity: major

**第 1 問:分層與依賴方向**

規則檔、共用判斷、樣本、check.py 和測試的分層都和鄰居一致,沒有跨層直呼。有一處讀取是自己另寫的,見第 3 問的 F1。

- 規則放 `rules/`、`rules-unwired/`,放置登記進 `_KTSEC_PLACE`,和既有資安批做法相同。
- 共用判斷 `utils/has-registration-call.yml` 的檔頭是 `id:` 加 `rule:`,和 `utils/debug-only.yml:5` 同形。規則用 `matches:` 引用,UI-32 和 UI-33 共用,沒有複製字表。
- 樣本路徑是 `samples/{bad,good}/<id>/src/main/kotlin/<id>.kt`,和 `samples/bad/kt-zip-slip/...` 一致。

**第 2 問:命名與錯誤處理**

整體一致,有三處小差異。

- 規則 id 都以 `kt-` 開頭。message 句式「[編號]錯在哪;改用…」符合 `check.py:886` 的 `message_problems`(要有分號和「改用/改成」)。路徑排除八項和 `rules/api.yml:253` 逐字相同。
- 樣本的 `// BAD` 標記和「容易誤報」註解,與 `samples/bad/kt-zip-slip` 及其他 108 支 good 樣本同寫法。
- 圖譜摘要的 WHY 行帶 `[出處][因][不選][test]`,和既有 WHY 一致。
- 型錄「現成規則欄」寫「自寫 ast-grep <id>」,和既有 34 列同寫法。

severity: minor
blocking: 否

F2:規則頂端註解句式和鄰居不同。鄰居是先寫計劃連結,再寫「範圍 N:會擋/不接閘(樣本外 N 處誤報 M)」,例如 `rules/api.yml:273`。這次搬來的規則先寫日期:
引句:「# 2026-11-09 樣本外 294 處抽 40 處誤報 3(7.5%),過升級條件搬來會擋」
`rules/architecture.yml` 的 ARCH-59 同樣日期在前。`rules-unwired/compose.yml` 沒有寫「不接閘(原因)」,鄰居 `rules-unwired/data.yml:1,22,90` 都有。UI-33 的規則本體裡還夾了一行過程紀錄「樣本內調形狀(2026-11-09)」,鄰居的註解寫的是規則行為,不寫過程。

severity: minor
blocking: 否

F3:`_KTSEC_CASES` 的案例編號沒照順序。C148 排在 C138 後面,C149 到 C152 又排在 C139 到 C147 前面。既有表是連號往下排。另外,S3 檢查的標籤文字從「報一次/不報」改成了「報 n 次」,這是順手改動了既有檢查的輸出。
引句:「check(f"S3 {rel} 報 {n} 次({rid}):{head[:60]}", got_n == n, f"命中 {got_n}")」

**第 3 問:第二種做法**

severity: major
blocking: 是

F1:新增的 S4(形狀列)檢查另寫了一套型錄主表的讀法:
引句:「cells = [c.strip() for c in ln.split("|")]」
專案已有唯一讀法:`check.py:765` 的 `main_rows`(用 `_cells`,第 164 行,配 `_CELL_RE` 讓反引號內的直線不算分隔)。圖譜 `Systems/kotlin規則包.md:40` 明寫:
- 「主表只有 main_rows 一條讀法」
- 「測試端呼叫同名函式不另抄」

同一支測試函式的前面幾行(新碼上方)也寫了「讀法只有 check.py 的 load_rules 一套(代碼審 r1 架構對齊 F1)」。純 `split("|")` 遇到反引號裡有直線的列會錯位;`cells[6]` 這個寫死的欄位索引也不是 `main_rows` 的 `c[5]`。這和先前審查已經定下的規矩正面衝突。建議改成 `m.main_rows()[code][5]`。

severity: minor
blocking: 否

F4 ⚠:`scan` 加了 `with_lines=False` 參數,同一個函式依旗標回傳 2 元組或 3 元組:
引句:「def scan(sg, cfg, target, with_lines=False):」
`check.py:914` 的既有呼叫端(第 1045、1077 行)都只收 2 元組,這個函式本來回傳形狀固定。專案裡沒有先例是用旗標切換回傳形狀。這算不算「第二種做法」,請編排者判:它向下相容、只有測試用,所以我只判 minor。

severity: minor
blocking: 否

F5 ⚠:逐例表加了選填第五欄,內容是 dict(`{"top": True, "lines": (...)}`),用 `*opt` 解包。例如:
引句:「"kt-map-await-deferred", 1, {"top": True, "lines": (3,)}」
`_KTSEC_PLACE` 的選填是第四個位置元素(裸 tuple),用 `*extra` 解包。兩者一個靠位置、一個靠鍵,同一支測試裡出現兩種選填寫法。這裡有兩個獨立選項,用 dict 可以說得通,所以我標 ⚠ 交編排者。

severity: minor
blocking: 否

F6:`rules-unwired/api.yml` 的 diff 只動了檔尾,沒有實質改動。檔尾換行被拿掉:
引句:「\ No newline at end of file」
這是和本功能無關的改動,也和其他規則檔(都以換行結尾)不一致。

不對齊共 6 條,其中 major 1 條

我沒有在 `/tmp/lumos-seat-work/code-android形狀列補規則/架構對齊-sonnet/` 建過任何路徑,全程只讀。
