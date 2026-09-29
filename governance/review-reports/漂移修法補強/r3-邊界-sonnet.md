severity: major

# r3 邊界-sonnet 報告

逐節讀完。合約行:guard-kill 兩條 ★INVARIANT★(rc 優先序、`--json` 純度)只管 `guard kill`,這份設計只改 c1/settle 的訊息字樣,不碰 kill 的 rc 與 JSON 輸出,不影響。`Systems/lumos-cli-write` 與 `Systems/delguard` 在 r3 快照 repo 的節點裡沒有 ★INVARIANT★ 行,無可逐條判。

## F1 delguard 新參數名 skip 與函式內既有區域變數 skip 同名
severity: major
blocking: 是
引句:「加 `skip` 參數(預設空集合),抽 `-` 行名稱與收 `+` 行回收表兩遍都跳過 `skip` 裡的路徑」
file: `scripts/lumos:29253`
1. `_delguard_parse_diff` 的第一遍已經有一個區域變數叫 `skip`(`added, cur, skip, in_binary = {}, None, True, False`),每遇 `diff --git` 行就被重設成布林(`skip = (cur is None) or is_v or is_e or cur.endswith(".md")`)。
2. 照 spec 字面把參數也叫 `skip`:第一個 `diff --git` 行之後參數就被布林蓋掉,之後 `cur in skip` 會丟 `TypeError: argument of type 'bool' is not iterable`;連工具鏈本身(`skip` 傳空集合)也一樣中招,因為蓋掉發生在傳入之後。
3. `cmd_delguard_check` 外層 `except Exception` 會把它吞成「內部錯誤」降級、放行、寫一筆 `reason=error:TypeError`,所以是靜默壞:每次有 diff 的提交刪除守衛都失效,只有治理帳多一筆 degraded。只有 `t_delguard_skips_vendored_toolkit` 恰好走到才會抓到。
4. 修法:spec 要點名把參數改成別的名字(例如 `vendored`),並寫明不能沿用函式內既有的 `skip` 區域變數。這正是「補丁與原文銜接處」的不一致。

## F2 同提交與計劃名兩份清單的「兩者」比對沒定義正規化,也沒查目錄現在還在不在
severity: minor
blocking: 否
引句:「只收路徑至少四段、形如 `governance/review-reports/<目錄>/<檔>` 的第三段目錄名,去重」
file: `scripts/lumos:23634`
1. 同提交名單來自 `git show -z` 的位元組解碼(`_nodehome_split_z` 不做 NFC),計劃名名單來自 `Path.iterdir()` 的 `d.name`。中文目錄在 macOS 上一邊 NFC 一邊 NFD 時,字串不相等:同一個目錄被列兩次(一次「同提交」、一次「計劃名」),沒有被標「兩者」,也就不會被排到最前面。中文目錄名的專案這是常態輸入。
2. 「去重」與「兩者」都沒說用 NFC 比;`_drift_c4_key` 有 `nfc()`,但它只用在計劃名那一邊。
3. 同提交名單只看那個提交當時加進來的檔,目錄後來被改名或刪掉也仍會列出,證據頁沒標「現在磁碟上沒有」;人挑了寫進 valid_under,就是指向不存在的卷證目錄。範本不自動填只擋了照貼,擋不住挑錯。
4. 建議:兩邊都先 NFC 再比、顯示用原字串;同提交名單加一個「現存」檢查或標記。

## F3 範本句寫的 <已知就填 sha> 不是第 2 節擋的佔位字
severity: minor
blocking: 否
引句:「提交 <已知就填 sha>;代碼審見 <卷證>」
file: `scripts/lumos:27957`
1. 若照字面把 `<已知就填 sha>` 當成印出去的文字,它不等於 `<sha>`,`_SET_COND` 三個字串一個都不含,也不被 `_DRIFT_PLACEHOLDER_RE`(只認 `<sha>`)抓到;人只換掉 `<卷證>` 就照貼,`lumos set` 放行,這串描述文字被寫進驗證紀錄前提。
2. 若意思是「有 sha 就填、沒有就印 `<sha>`」(現行程式行為),spec 的寫法要改成這個意思,S1 也要補「沒有 sha 時印 `<sha>`」。
3. 相關的小邊界:大小寫(`<SHA>`)與全形角括號(`＜卷證＞`)不會被擋,但工具從不印這兩種,只有人手打才會出現,不算缺陷。

## F4 證據頁目錄清單被 _esc_clean 一併截斷,「另標」提示可能被切掉
severity: minor
blocking: 否
引句:「目錄名印到終端前過 `_esc_clean`」
file: `scripts/lumos:27957`
1. 現行證據頁把整串目錄用「、」接起來再過 `_esc_clean(...,300)`,超過 300 字尾端被截成「…」。新版每個目錄還要加來源標記,同提交 4 個以上、中文長目錄名時,尾端幾個目錄與「可能含別的計劃的卷證」那句會被截掉;卷證整批匯入的提交(超過 3 個的那種)正是最容易被截的情境。
2. 排序把「兩者」放最前,所以最強線索還在,但「超過 3 個」的警告是這份設計專為那種情境加的,被截掉就等於沒加。
3. spec 沒定義是逐個目錄過還是整串過、上限多少;建議寫成逐目錄各自消毒、警告句獨立一行不進截斷範圍。
4. 邊角:shallow 或 sha 查不到時同提交那行寫「查不到(git 失敗或沒有)」,把「shallow 根本沒查」講成「沒有」,措辭可沿用 first 那一行的 shallow 說明。

## 已讀、無 finding 的檢查點
- 卷證目錄 0 個:同提交與計劃名都空,證據頁兩行都寫查不到、範本 `<卷證>`,行為明確。
- 1 個、3 個:不超過 3 不標警告;4 個標。邊界「超過 3」與「至少四段」寫得一致。
- 路徑剛好三段(例如 `governance/review-reports/x.md`,檔直接放在 review-reports 底下):「至少四段」把它排除,不會把檔名當目錄名。已驗證邏輯成立。
- 空白與中文目錄名:`-z` 拆、`core.quotePath` 不影響;`_drift_sh` 對範本只用在 `lumos set` 指令,目錄名不進去,沒有引號問題。
- set 三個佔位字在值中間:用 `in` 子字串判斷,「提交 <sha>;…」這種中間出現會被擋;訊息點名哪一個由實作決定,S2 已要求。
- c3 理由 4 字、200 字剛好通過,3、201 字被 `_drift_fix_reason_ok` 擋;去頭尾空白後才算長度,`"   "` 被擋;含換行(含 U+2028)被 `_drift_one_line` 擋。`--reason ""` 不會被當成沒給,而是報「4 到 200 字」,與「沒給照舊」不衝突。
- c3 理由文字進 `_drift_fix_shape_err` 的形狀檢查(texts 已含這一行),理由帶反引號路徑或行號會被擋,是既有行為、訊息清楚。
- 刪除守衛:只碰工具檔(名稱不抽、note 記支數、無命中)、只碰專案檔(行為不變)、兩者都碰(只跳工具檔,回收表是 per-file,互不影響)、工具檔被刪(`b/` 路徑與 `a/` 同名,會命中)——都成立,除了 F1。工具檔「改名進來/出去」:改名 100% 相似沒有內容行,不抽任何名稱;帶修改的改名 `b/` 是新名字,不在 `_VENDORED_ALL` 內、照舊抽,是可接受的窄邊界(消費專案不該改名工具檔),不標。

最高等級:major;blocking 共 1 條
