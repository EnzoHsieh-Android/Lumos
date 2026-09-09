severity: major

### raw 旗標讓整題舊 pattern 一起改看字串,log/錯誤訊息裡的關鍵字重新變成假命中

severity: major
blocking: 是
file: `scripts/lumos:15306`
引句:「        {"id": "cs-data", "raw": True, "q": '查詢有沒有 N+1/SELECT * 進大表?大結果集有分頁、過濾聚合下推到資料層嗎?',」
`raw` 是整個 spec 一個布林(`hay = norm_raw if raw else norm`),於是 cs-data 原本就有的 `\bSELECT\b` 也跟著新加的反面詞一起改看未剝字串的原文。實測 `logger.LogError("SELECT query failed, retrying with backoff");` 在改前(`keep_strings=False`)不命中、改後(`keep_strings=True`)命中 cs-data;同款寫法在 node-eventloop(`console.log("remember to call JSON.parse on the config file")`→命中)、node-data(`throw new Error("db.query(...) failed, check createPool settings")`→命中)一樣重現。這正是 `_strip_string_literals` 當初要擋的「訊息文字不算」被 raw 旗標整題一起繞掉,而非只有反面詞本身在看字串。

### `\bstatic\b.*Context` 對 Android 最常見的靜態工具函式(只傳參數、不持有)照樣亮

severity: minor
blocking: 否
file: `scripts/lumos:15119`
引句:「         "when": ['\\bContext\\b', 'companion object', 'WeakReference', '\\bActivity\\b', '\\bView\\b', 'WeakReference', '\\bstatic\\b.*Context', 'TimerTask', 'registerReceiver']},」
`.java`/`.kt` 都算 kt 棧,`public static void showToast(Context context, String msg) { ... }` 這種到處都是、Context 只當參數傳遞不持有的寫法會亮 kt-leaks(實測命中)。這題本來就該問「是不是持有」,人一眼能判掉,成本低,列為誤傷但不到擋合併的程度。

### `.Open()` 在任何物件上都亮,不限資料庫連線

severity: minor
blocking: 否
file: `scripts/lumos:15119`
引句:「         "when": ['SqlConnection', 'DbConnection', 'IDbConnection', 'OpenAsync', 'BeginTransaction', 'using\\s*\\(', 'new SqlConnection\\(', '\\.Open\\(\\)', '\\.Close\\(\\)', 'OleDbConnection', 'OdbcConnection']},」
`response.Body.Open();`(非 DB 物件)實測命中 cs-connection,dispatch 本身也點名這條規則太寬。單獨看是可快速判掉的誤傷,不影響其他題。

### viewDidLoad 讓每個 UIKit 畫面都亮出問 SwiftUI 措辭的題目

severity: minor
blocking: 否
file: `scripts/lumos:15119`
引句:「         "when": ['var body', '@Observable', '@State\\b', '@StateObject', '@ObservedObject', 'ForEach', '\\bList\\s*[({]', 'AnyView', 'GeometryReader', '\\.animation\\(', 'withAnimation', 'UITableViewDataSource', 'cellForRowAt', 'reloadData\\(\\)', 'UICollectionView', 'viewDidLoad']},」
`override func viewDidLoad() { super.viewDidLoad() }` 這行每支 UIKit 畫面都有,實測命中 swift-swiftui,但題目原文問的是 body/ForEach/GeometryReader 這些純 SwiftUI 概念,對只有 UIKit、完全沒有 SwiftUI 的檔案讀起來文不對題。判斷成本低,不到擋合併等級。

### `[LR]TRIM\(` 沒有 `\b`,匹配到不相干識別字尾端

severity: minor
blocking: 否
file: `scripts/lumos:15119`
引句:「         "when": ['CONVERT\\(', 'CAST\\(', 'ISNULL\\(', 'COALESCE\\(', 'LOWER\\(', 'UPPER\\(', 'DATEADD\\(', "LIKE\\s*'%", "\\+\\s*'%", "'%'\\s*\\+", '\\bYEAR\\(', '\\bMONTH\\(', 'SUBSTRING\\(', '[LR]TRIM\\(']},」
`SELECT dbo.fn_TotalTrim(name) FROM Users` 這種自訂函式名尾端是「…lTrim(」,`[LR]TRIM\(` 因為前面沒有 `\b` 或非字母錨定,配上 re.I 照樣命中 sql-sargable,但這根本不是 LTRIM/RTRIM。命名撞上這個尾綴的機率低,列 minor。

## 圖譜鏡頭(lens 7,LUMOS-IMPACT: 6de9721..HEAD)

以下固定席節點只是因為和這份 diff 共用 `scripts/lumos`/`scripts/test_lumos.py` 同一個檔而被 impact 抓進來,判斷下來都不影響:

- `lumos-cli-read.md`(search 排除 superseded/不排除 stale):diff 沒碰 search/query 任何程式碼路徑,只動 `_STACK_QUESTION_SPECS`/`_STACK_TRIGGERS`/`_stack_applicability` 及其呼叫端,不影響。
- `bound-tests-gate.md`(code-loop 對固定席合約測試真跑):diff 沒動 code-loop check 邏輯,新增的測試也全數綠(`python3 scripts/test_lumos.py -k stack_question` 60 passed, 0 failed),不影響該閘的判定機制。
- `canary-audit.md`(record/second readback 與 rc 語意):diff 未觸及 canary 相關函式,不影響。
- `design-loop.md`(處置閘第五步):diff 未觸及 design-loop 判定邏輯,不影響。
- `guard-kill.md`(rc 優先序、--json 純度):diff 未觸及 guard kill,不影響。
- `slim-get/slim-install/slim-uninstall`(BOM/`$Args`/CLAUDE.md 注入等):diff 完全不在安裝器/卸載器路徑上,不影響。

## pitfalls manifest 判定

lens 6 讀 `r1-pitfalls.txt` 逐條核對:manifest 列了 `scripts/usage_scan.py:64` 與 `:91` 兩處「檔案 handle 有沒有 with/確定 close?」。逐行核對原始碼,第 64 行是 `with open(path, "rb") as f:`,已經用 with 包好,manifest 這條是誤報。第 91 行是 `for line in open(f, errors="replace"):`,確實沒有 `with` 也沒有顯式 close,是真隱患(雖然 CPython 迴圈結束通常靠 refcount 隨手關檔,不保證所有實作都這樣)。這支是唯讀量測腳本,影響面小。

最嚴重 severity: major,blocking 條數: 1
