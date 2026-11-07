severity: minor

沒有會擋的問題。16 條修補大致站得住,以下 F1 到 F6 都只是次要發現。

驗了什麼:
- **範本實跑**:我另組實驗專案,把 T0、T1、T2、T5 共 57 格全跑一遍,矩陣不符 0 項,含新增的 TEST-18 會掛起、API-31 永久快取、FLOW-23 不查回 null、DATA-74 字串三格。
- **API-31(上一輪 F2)**:我另寫八種變形實跑。四種合法寫法全綠:`invokeOnCompletion` 清除、不用 mutex 的 `isCompleted`、`finally` 清除、鎖外 await。四種壞寫法全紅:快取字串、`!isCancelled` 永久保留、真實時間快取、只串行不合併。「一共打兩次」沒有誤紅合法寫法,因為第一批已結束,不存在「合併到仍在途」。
- **`t_kotlin_template_fence_parity`(上一輪架 F2)**:真的在比兩份。我改壞 check.py 那份,用 `<=4`、`>` 取代 `>=`、拿掉同字元判斷、拿掉退回寬鬆、拿掉 info string 判斷五種,都紅。改壞 scripts/lumos 那份,用 `<=4` 和 `run >`,也都紅。另對兩份 `_visible_lines` 做 30000 組隨機輸入,差異 0。四反引號與 `~~~` 輸入(上一輪其他審 F1)判定都對。10 萬行輸入約 0.08 秒,沒有效能問題。
- **本機測試**:在 HEAD 的複本上跑 `-k kotlin`,235 通過、0 失敗。
- **12 個禁用方法**:用 `javap` 對 Turbine 1.2.1 核對,會丟 `TurbineAssertionError` 的方法沒有漏列。

F1
severity: minor
blocking: 否
引句:「for mt in _re.finditer(r"\.test\s*\{", code):」
`.test` 區塊守衛只認 `.test {`,`.test(timeout = 5.seconds) {` 或 `test(name = "x") {` 整塊不受檢查。實跑 `x.test(timeout = 5.seconds) {\n cancelAndConsumeRemainingEvents()\n}` 回傳 `[]`,既沒推進也沒收尾都過。同理用 `testIn(...)` 取事件、不經 `.test {` 的寫法,「取事件前要推進」這道也不管。只有禁用方法那道仍會抓到 `awaitItem`。守衛只針對範本檔這一份文字,實際紅綠另有矩陣擋,所以我降到 minor。

F2
severity: minor
blocking: 否
引句:「code = _re.sub(r"//[^\n]*", "", code)   # 註解裡說「不用 awaitComplete()」不算用了」
只剝 `//` 註解,`/* advanceUntilIdle() */` 或字串裡的 `"advanceUntilIdle()"` 仍算作推進,會讓守衛誤放。程式區塊內字串含不成對大括號(例 `"{"`)時,`_kt_block_after` 配錯,可能誤判或漏判。實跑 `x.test {\n advanceUntilIdle()\n val s="}"\n val e = cancelAndConsumeRemainingEvents()\n}` 誤報「沒用 cancelAndConsume 收尾」。真範本 235 項全綠,目前沒踩到。`awaitItem ()`(多一個空白)、反引號包名、`::awaitItem` 都不會被抓,屬罕見寫法。

F3
severity: minor
blocking: 否
引句:「        emit(SaveEvent.Saving)
        delay(100)   // 真的儲存通常會掛起(等網路或磁碟);正確寫法,測試要照綠」
〈測試〉三支 save 相關測試對合理改壞照綠,這是規格第 3 點「斷言實際行為」的缺口。我對〈好寫法:TEST-18 save 會掛起〉實跑三種改壞:
- 把 `emit(Saved)` 搬到 `repo.save(name)` 之前:兩支都綠。這是「還沒存好就先報成功」。
- 呼叫 `repo.save` 兩次:兩支都綠。
- 拿掉 `repo.save`:`save_emits_saving_then_saved_once` 仍綠,只有空白名字那支紅,而且紅的原因是沒拋出錯誤,不是沒存。

測試沒有檢查 `repo` 實際收到幾次、收到什麼。不過這些不在型錄 TEST-18 那一列的範圍,所以只算 minor。

F4
severity: minor
blocking: 否
引句:「依 Turbine 1.2.1 原始碼 `channel.kt`、`ReceiveTurbine.kt`、`flow.kt` 列全」
範本檔文字寫來源是 `flow.kt`,test_lumos.py 裡的註解寫 `Turbine.kt`,兩邊對不上。我用 `javap` 看到實際是 `ChannelKt`、`ReceiveTurbine`、`FlowKt`、`TurbineKt`,方法清單本身是對的,只是出處措辭不一致。

F5
severity: minor
blocking: 否
引句:「        indent = len(ln) - len(ln.lstrip(" "))
        s = ln.lstrip(" ")
        if not (indent <= 3 and not ln.startswith("\t") and s.startswith(("```", "~~~"))):」
`not ln.startswith("\t")` 是死碼。`s = ln.lstrip(" ")` 後 tab 開頭的行本來就不以圍欄字元開頭。我把這個子句拿掉,`t_kotlin_template_fence_parity` 仍 11 條全綠,證明這個子句沒有被驗到。行為上沒有影響。

F6
severity: minor
blocking: 否
引句:「        if lines[a].lstrip(" ").lstrip("`~").startswith("kotlin"):」
`_kt_kotlin_blocks` 只讀嚴格圍欄,沒有像 `_visible_lines` 那樣在未閉合時退回寬鬆讀法。目前每個小節的圍欄都有閉合,不影響結果。若將來某小節漏掉收尾圍欄,內容會被當成沒有 kotlin 區塊而靜默略過,Turbine 守衛因此不檢查那一段。

總結:最嚴重是 minor(`.test(...) {` 帶參數的寫法繞過區塊守衛,以及 save 測試對「先報成功再存」照綠),會擋 0 條。

臨時目錄 `/tmp/lumos-seat-work/code-android行為測試範本/驗收審-sonnet/` 已刪。
