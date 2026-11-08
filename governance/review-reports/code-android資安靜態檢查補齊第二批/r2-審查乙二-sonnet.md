severity: minor

我逐項查過重數、批四七列、新正規式和測試。重數與正規式都沒出錯。有 3 條 minor,都不阻擋。

## 查過且乾淨的項目

- **〈統計〉各數重數**:我用 `check.py` 的 `main_rows` 與 `load_rules` 另寫程式重數。
  - 總列數 532,各主題 API 51、FLOW 32、STATE 28、CO 44、UI 111、ARCH 91、DATA 98、TEST 38、PERF 39,全部吻合。
  - 各級「含該字母」A 242、B 226、C 68、D 58,「以第一個字母計」A 242、B 196、C 52、D 42,吻合。
  - 級的組合 13 種全部吻合。
  - 規則包 227 條,error 46、warning 119、info 12、hint 50,不接閘 29 條,吻合。
  - 逐列查證 519 列、被會擋的規則守到的列數 128,吻合。
  - 引句:「各級(列的級含該字母就算一次,可複選所以加總大於總列數):A 242、B 226、C 68、D 58」
- **新正規式有沒有取錯行**:`各級\(列的級含該字母…` 只命中「含該字母」那一行。「以第一個字母計」那行不含「含該字母」,不會被取到。規則包 `error/warning/info/hint` 的 lazy 比對各取到對的數;「逐列查證」那行也取到 `519 列`,不是前面的日期。
  - 引句:「各級(以第一個字母計,加總等於總列數):A 242、B 196、C 52、D 42」
  - `t_kt_catalog_stats_consistent` 與 `t_kt_catalog_security_lint_batch2` 實跑全綠(`-k kt_catalog`:54 passed,`-k kotlin_rulepack_security_rules`:150 passed)。
- **批四七列**:DATA-27、DATA-79、DATA-82、DATA-83、DATA-85、ARCH-89、DATA-95 的現成規則欄都真的登了 `內建:` 或 `資安包:` 檢查,通電批次欄都含批四。
  - 沒有多列。現成規則欄含 Android Lint 檢查卻沒寫批四的列有 DATA-30、TEST-23、PERF-2、ARCH-4、ARCH-44,都是舊列,不在這批範圍,計劃 REVISIT 2026-12-08 已記。
  - 引句:「for rid in ("DATA-27", "DATA-79", "DATA-82", "DATA-83", "DATA-85", "ARCH-89", "DATA-95"):」
- **C72~C86 新增案例**:每條規則一壞一好,訊息都有預期值,實跑全綠。
  - 引句:「("src/main/kotlin/C79.kt", 'val g = KeyPairGenerator.getInstance("RSA")\n    g.initialize(1024)', "kt-weak-key-size", 1),」
- **〈待查證〉列的覆蓋**:主表現成規則欄含「待查」的 48 列,與〈待查證〉列裡含「待查」的 48 列一致。
  - 引句:「手寫(沒有程式產生,改主表時一起改):列「現成規則」欄含「待查」的規則代號」
- **圖譜鏡頭**:這次沒附固定席節點,不逐條答。我看到的改動只有型錄手寫節、測試與計劃筆記,不碰規則檔與 `check.py`,不破壞 Systems/kotlin規則包 的規則放置合約。

## Finding 1

severity: minor
blocking: 否

file: `skills/kotlin-idioms/checks-catalog.md:791-848`(〈待查證〉表)與 `skills/kotlin-idioms/checks-catalog.md:858`(〈統計〉待查證那行)

〈待查證〉表的「待核對的來源」欄有 17 列還寫著未核對的來源,但主表那列的來源欄已經沒有「未開頁核對」「搜尋摘要」字樣,已有〔查證 …〕。

- 例子:API-9 在〈待查證〉列 `AND-BP#create-coroutines-data-layer(未開頁核對); PAD-LIFE(搜尋摘要)`,主表 API-9 來源欄是 `…〔查證 2026-11-05:https://…〕`。
- 其他 16 列同況:API-11、CO-2、CO-3、CO-39、UI-1、ARCH-49、ARCH-67、DATA-15、DATA-18、DATA-24、DATA-30、DATA-43、DATA-71、PERF-2、PERF-32、PERF-35。
- 我的重數程式比對〈待查證〉每列的來源欄與主表來源欄,表上有來源欄位的列共 20 列,主表仍有字樣的只有 3 列。
- 〈統計〉寫「來源待核對 3 列」,是拿主表重數的值。照〈待查證〉表人工重數會得 20,兩者對不上。
- 新測試抓不到,因為 `_kt_pending_problems` 對每列用 `待查 in c[5] 或 weak in c[11]` 的 OR,代號待查那半一成立就放行,不比對表上來源欄。
- 後果:照〈待查證〉表去「開頁核對來源」的人會重做已查證的 17 列。

引句:「| API-9 | 待查(資料層研究的 detekt 候選 GlobalCoroutineUsage) | AND-BP#create-coroutines-data-layer(未開頁核對); PAD-LIFE(搜尋摘要) |」

佐證:`skills/kotlin-idioms/checks-catalog.md:799`(〈待查證〉表的 API-9 列)

## Finding 2

severity: minor
blocking: 否

file: `scripts/test_lumos.py`(`_kt_pending_problems`,patch 內 `@@ -129267` 那段)

測試只判〈待查證〉裡多列了不該列的,不判主表有「待查」或「未開頁核對」「搜尋摘要」的列有沒有漏列在〈待查證〉。

- 具體輸入:在主表任一列的現成規則欄加「待查」,不動〈待查證〉。
- 走法:`_kt_pending_problems` 只逐行走〈待查證〉表,從不掃主表。`want` 裡「待查證 N 列」的期望值是 `len(pend)`,也取自〈待查證〉表,不是主表,所以數字照樣一致,測試全綠。
- 這個缺口我只從讀程式推得,沒有實跑改壞。
- 型錄新寫的「手寫」說明只說「已解決卻還列著會被擋」,沒說漏列不擋。計劃 S4 只要求前者,所以只算覆蓋可以更完整。

引句:「〈待查證〉不列主表已不含待查與未核對字樣的列」

佐證:`scripts/test_lumos.py:129288`(`_kt_pending_problems` 的迴圈只掃 `pend`)

## Finding 3

severity: minor
blocking: 否

file: `scripts/test_lumos.py`(`_kt_stats_extra_problems`,patch 內 `@@ -129243` 那段)

`_kt_stats_extra_problems` 的「來源待核對」判準用 `("未開頁核對", "搜尋摘要", "無網址")`,多了「無網址」,跟 `_kt_pending_problems` 的字樣(只有「未開頁核對」「搜尋摘要」)不一致。

- 具體輸入:主表有 UI-103、ARCH-3 兩列,來源欄含「無網址」但不含「未開頁核對」或「搜尋摘要」(我用 `main_rows` 查到)。
- 若把其中一列放進〈待查證〉:`_kt_stats_extra_problems` 把它算成來源待核對,`_kt_pending_problems` 則判「已解決卻還列著」。同一列兩支檢查結論相反。
- 現況不會出事,因為這兩列沒放進〈待查證〉。〈待查證〉節的定義寫的也是「搜尋摘要」「未開頁核對」兩個字樣。

引句:「weak = ("未開頁核對", "搜尋摘要", "無網址")」

佐證:`skills/kotlin-idioms/checks-catalog.md` 主表 UI-103、ARCH-3 的來源欄

總結:最高等級 minor,blocking 0 條(共 3 條 minor)。

臨時目錄 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查乙二-sonnet/` 留著不刪,裡面只有我的 `recount.py`。
