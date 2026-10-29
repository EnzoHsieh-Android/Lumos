severity: minor

審查席:code-原生配置排行/r2/邊界-sonnet。版本 07642d8e,修補鏡頭 84b487f2 → 23c0d065。鎖檔 `.warming` 不存在,沒有要處理的。

整體判斷:正式程式碼我找到一條小問題,沒有 major 或 blocker。查詢範本、收集腳本的各個分支、lumos 的驗證與列印,拿極端輸入走過都沒壞。

### 1. 時間預算的「跑不跑」判斷與「每次驅動剩幾秒」用不同的保留量,在小預算下會啟動一段必定失敗的第二段
severity: minor
blocking: 否。只在 `LUMOS_STABILITY_STEP_BUDGET_S` 小於 190 秒且第一段不到 30 秒時出現,後果是第二段寫成 failed,不影響第一段結果。
引句:if budget and elapsed + (2 * elapsed + 120) > float(budget):
file: `scripts/templates/android-stability-collect.sh:583`、`scripts/templates/android-stability-collect.sh:593`、`scripts/templates/android-stability-collect.sh:676`
- 預估放行的條件是 `3e + 120 <= b`(`e` 是第一段已用秒數,`b` 是預算)。每次驅動的上限卻是 `deadline - now`,而 `deadline = t_start + b - 180`,最低夾到 1.0 秒。
- 兩個保留量差 60 秒(120 對 180),所以 `3e + 120 <= b < e + 180` 時,預估說跑得完,實際驅動上限只剩 1 秒。
- 具體輸入:`b=150`、`e=10`。第二段照樣強制停 App、重啟,然後暖機驅動被砍成 1 秒逾時。
- 結果寫成 failed「驅動失敗:…逾時(1.0 秒)」,看起來像驅動壞了,不像預算不夠。
- 我用替身直接呼叫 `native_phase` 重現:`b=150,e=10` 時兩次驅動的上限是 `[1.0, 1.0]`;`b=300,e=60` 是 `[60.0, 60.0]`;`b=3600,e=1000` 是 `[1800.0, 1800.0]`。
- 預設 e2e 上限 3600 秒碰不到這個窗口。
- 歸因:有證據的修復回歸(局部)。修前 84b487f2 沒有 `left()` 與 `NATIVE_MARGIN`(`git show "84b487f25d1143c83c697ca18299a34b7d8ddc5c:scripts/templates/android-stability-collect.sh"` 搜不到),驅動一律用 `T_LONG`,不會被砍到 1 秒。修後 23c0d065 才有這個窗口。修前沒有上限會把整步推過 e2e 的上限,所以這不是反向回歸。

### 修補鏡頭:兩種結果分開報

**repair(原問題修好了)**
- G2 的 ERROR 偽框架當呼叫者:用同一份假表跑修前後的查詢。
  - 修前 84b487f2:`[('bar','ERROR 7'), ('foo','ERROR 7')]`
  - 修後:`[('bar','zzz'), ('foo','?')]`
  - 並列時有名字的排在「?」前面,也成立。
- G1 的超大整數:`retained=10**4000` 不丟例外,完整印出整數(算式用整數,不轉 float)。
- G1 的長名字:函式名剛好 200 字完整保留,201 字截成 200 字加「…」,「還留著」的大小段都還在。
- G1 的形狀不對:bool、float、負數、`enabled` 不是 bool、`status` 不在三值內、`sites` 是 dict 或 None、項目是 list、`func` 不是字串,全部寫成 failed「結果檔形狀不對:…」,不丟例外。
- G4 的 sdk 邊界:30 回 None(照跑),29 與 None 回 unsupported。
- G3 的預算值:我只用 `native_skip` 驗了預估規則,`b=300,e=60` 放行,`299.9` 擋下。`nan`、`inf`、`0`、負數與非數字的擋下,只讀程式確認,沒有跑完整收集腳本。
- G5/G6/G8/G9 沒跑修前版本,歸「未判定」。修後我用替身驗過:驅動失敗、開錄失敗、拉不回追蹤檔、行程換了、讀不到結束紀錄、pid 兩次都是 None,都得到對的 failed 原因與順序。

**preserve(要維持的既有行為)**
- `tp_rows` 抽出後,`cycle_numbers` 與 `heap_counts` 的切法等價(`startswith('"cycle"')` 對 `cells[0]=="cycle"`,`splitlines()[1:]` 對 `rows[1:]`),我只讀程式比對,沒跑。
- `fresh_launch` 的順序跟原本 `measure` 一致(force-stop、讀結束紀錄、monkey、SETTLE、pidof)。
- 印前 20 個,以及控制字元、ESC、雙向字元清成空格。
- 沒打開的情境不印。
- 20 個以上的情境(250 個輸入)只印 20 個、共 200 個。

### 鏡頭 1 已驗的極端輸入(無 finding)
- **查詢範本,用 Python sqlite3 假表跑**:
  - mapping 名:空字串、NULL 都記「?」。
  - mapping 名多個「!」取最後一個之後,尾端「!」或「/」得到空 `so`、函式名成 `+0xff`。真實 mapping 名不會這樣結尾,規格也沒定義,所以不標。
  - 函式名:`ERROR` 不帶空白的當真名;含引號、換行、逗號、日文的都經 hex 往返正確。
  - 呼叫鏈:只有 malloc 一框、整條在 libart、整條是配置器,都得到「? / ? / ?」或規格預期的列。
  - 大小邊界:剛好 1048576 入列,1048575 不入列,兩個 callsite 各半加總剛好 1 MiB 入列;250 個並列取字典序前 200 個;函式名 600 個中文字截成 500 個字元。
  - 其他:同名函式、系統與非系統同名 .so 分兩列;其他 heap_name 不算排行但算 `rows`;負值(釋放)沖淡後低於門檻的不入列;stats 只收 error/data_loss 且值非 0。
  - `rel_pc` 為負數時印成 `fffffffffffffffb`,規格沒定義,不標。
- **規模**:30000 個葉子乘 40 層,耗時 10 秒、記憶體 232 MB;5000 乘 30,耗時 1.5 秒。
- **收集腳本**:
  - `native_query` 的輸出:奇數長度 hex、非 hex、整數帶小數點都走「看不懂」;`rows=0`、空輸出、逾時、`rc≠0`、`stat` 列,檢查順序都正確。
  - 非法 UTF-8 用 replace 解回。
  - 欄數不是 7 的 `site` 列會被靜默丟掉、仍回 ok。TP 輸出固定 7 欄,不標。
  - `native_phase` 的各個失敗分支與意外例外路徑,用替身驅動都不崩。
  - 上限值:`float(" 30 ")` 合法;`"0x10"`、`" "` 走 ValueError 到 nan 而被擋;`"1e309"` 變 inf 被擋。
  - e2e 傳 `f"{T_LONG:g}"`:T_LONG 為 inf 時收集腳本會擋,但 e2e 的 `communicate(timeout=inf)` 本來就丟 OverflowError,不是新問題。
- **lumos 設定**:`native_retained` 試過空清單、`"@default"`、重複、空字串、純空白、非字串、巢狀清單、`null`、字串、dict、名字不存在、大小寫不同、尾端空白、`stability_scenarios` 為 `null`。全部該擋的回 2、該過的過;跨段檢查拿得到 `stability_scenarios`,沒有未驗證型別就進 `in` 的路徑。
- **未驗範圍**:沒有真實 trace_processor 與裝置,heapprofd 實際輸出的 ERROR 偽框架形狀、stats 的 severity 分級都沒驗;沒有跑完整收集腳本與 e2e;`SIGTERM` 落在 `except Exception` 處理器內 `abort_record` 的期間(錄製已從 state 拿掉,cleanup 可能誤報裝置已收乾淨)是雙重故障加訊號時序,依派工當併發類不標。

### 鏡頭 2:pitfalls manifest(16 條)
| 條目 | 判定 | 理由 |
|---|---|---|
| `scripts/test_lumos.py:18990` ruff RUF059 | 真隱患(輕微) | 迴圈裡 `r, d, fake, _ = …`,`d` 後面沒用到,是新增告警,會被新增告警閘點名。該檔舊帳已有 335 條,屬測試席範圍,改成 `_d` 即可。 |
| `android-stability-collect.sh:261` 的 `open(` | 誤報 | `tp_rows` 內 `open(...).read()` 立即讀完,沿用原 `heap_counts` 與 `cycle_numbers` 寫法。 |
| `android-stability-collect.sh:314` 的 `open(` | 誤報 | `start_record` 的 `open(...).read()` 是舊行,只是參數化。 |
| `android-stability-collect.sh:487` 的 `time.sleep` | 誤報 | 在 `fresh_launch` 裡,不在迴圈,只睡一次 `SETTLE`。 |
| `android-stability-native.sql` 行 18、21、23、52、61、75、78、81、84、88、90、92 的 N+1 提醒(12 條) | 誤報 | 這是單一語句的 CTE 與 UNION,沒有逐筆迴圈查詢。 |

### 鏡頭 3:圖譜
這次沒附固定席筆記(`LUMOS-LENS` 寫明沒附),沒有逐條判的對象。我沒有自己跑 `lumos impact`。

### 鏡頭 4:規格〈排行怎麼算〉第 1、2 條與〈打算怎麼做〉第 2、3、6 步
- 〈排行怎麼算〉第 1、2 條:so 取法(最後一個「!」、路徑最後一段、空名記「?」)、配置器名單與 GLOB 前綴、ERROR 前綴、呼叫者跳過 libart、無符號的 `+0x`、截 500、系統旗標六個路徑,以及歸併鍵、1 MiB 只篩一次、排序、並列取前 200、呼叫者取加總最大,逐一對照實作,都一致。
- 〈打算怎麼做〉第 2 步:判斷順序(未打開、`test_data`、sdk 讀不到、sdk 小於 30、第一段沒跑成、時間不夠)與實作一致。
- 〈打算怎麼做〉第 3 步:
  - 失敗原因的順序(驅動失敗、結束紀錄讀不到、App 結束、行程換了)與規格一致。
  - 預算值驗證與預估公式照規格;每次驅動與查詢的上限也照規格寫。小預算窗口見上面第 1 條,屬規格兩個保留量(120 對 180)本身的落差。
  - 例外那一條的 `except Terminated: raise` 在前,也一致。
- 〈打算怎麼做〉第 6 步:固定鍵、未給 `--stability`、舊結果檔、`enabled` 為 false 不印、非 ok 印一行、形狀不對寫成 failed 並印同一行、兩條輸出路徑都印、不改回傳碼,都一致。

### 三問
1. **原問題修復效果有何行為證據?** ERROR 呼叫者和 sdk 30 有修前修後對照,超大整數與長名字只驗了修後。見上面「repair」。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立。`tp_rows` 抽出後的兩個舊呼叫端、`fresh_launch` 的順序、signature 變動的呼叫點(`load_config`、`preflight`、`driver`、`start_record`、`stop_record`)都對得上。只有第 1 條是修補新引入的邊界不一致。
3. **新發現的同一案例在修前、修後各是什麼結果?** 第 1 條案例(`b=150,e=10`):修前沒有 `deadline`,驅動用 `T_LONG`,不會被砍到 1 秒;修後兩次驅動上限都是 1.0 秒,第二段寫成 failed。

暫存放在 `/tmp/lumos-seat-work/code-原生配置排行/邊界-sonnet/`,由編排者收貨後刪除。

最嚴重:minor;blocking 條數:0。
