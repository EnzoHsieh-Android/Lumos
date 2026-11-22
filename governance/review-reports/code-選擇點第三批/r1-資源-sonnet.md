severity: minor

## r1 C-54、C-55 的「整個呼叫」樣式讓巢狀或串接的 retry 輸出量平方成長
severity: minor
blocking: 否

引句:「pattern: $A.retry($$$B)」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(diff 第 418–428 行的 C-54;C-55 同形)

失敗場景:樣式命中整個呼叫,每筆命中的 `text` 和 `$A` 都帶完整接收者文字。同一個運算式裡有 N 層 retry 時,每層都帶著內層全部的字,輸出量隨 N 平方成長。這條路徑沒有雙重否定可外包,因為樣式沒有關聯規則。
- 輸入:單行 `a.retry(3).retry(3)…` 串 N 次。
- 量測:實跑真規則(未改動的 `configs/ast-grep/kotlin-choice/sgconfig.yml`),N=300 輸出 2.26MB、N=1000 輸出 23.3MB、N=2000 輸出 91.6MB。拿掉第三批規則的基準設定同輸入輸出 0 位元組。
- 巢狀引數 `a.retry(a.retry(…))` 深 300 層,輸出 2.27MB,同樣平方。
- 超過 `_LINT_SARIF_MAX_BYTES`(64MB)會走到 `_choice_scan_batch` 回 None。這一次輸入約 1500 個以上的 retry 串接,檔案不到 20KB。
- 退回逐檔後,`_choice_scan_one` 對那支檔 raise「ast-grep 輸出超過讀取上限」,那支檔算不出來。
- 整批 `_choice_scan_batch` 失敗時,所有檔都要再逐檔重掃一遍,吃掉掃描時限的後半。
- 真實程式碼很少有這種深度,所以只標 minor。要根治可以限制命中形狀,例如只命中方法名那一段,把 `$A` 改成只取結尾位移。

## r2 S9 只守 C-39 一條,其餘 17 條規則拿掉雙重否定抓不到
severity: minor
blocking: 否

引句:「row = next((r for r in tables["choice"] if r["id"] in _CB3_IDS and r["candidates"] == ["supervisorScope"]), None)」
file: `scripts/test_lumos.py`(diff 第 1197–1236 行的 `t_choice_scope_rule_output`)

失敗場景:測試只取 `candidates == ["supervisorScope"]` 那一列(C-39)。C-38 的 `rule:` 與 C-39 一字不差,但 C-38 沒被測;C-40~C-53 這 14 條也不在測試範圍內。以下是這些規則拿掉雙重否定的「正面寫」對照組實測。
- 我用同一個 `_cb3_positive` 邏輯,把規則改成正面寫,輸入是深 200 層的巢狀:
  - C-53 的 `withContext(NonCancellable)` 巢狀:有雙重否定 116KB,正面寫 3.86MB。
  - C-48 的 `MutableSharedFlow(replay = 1)` 巢狀:有雙重否定 108KB,正面寫 5.74MB。
  - C-40 的 `x.singleOrNull().let {…}` 巢狀:有雙重否定 110KB,正面寫 242KB。
- 這些規則只用一個巢狀深度 200 的輸入就能翻紅。測試現在沒帶這類輸入,日後有人把這幾條改回正面寫,測試全綠。
- C-39 本身有被守住:我實跑 `python3.14 scripts/test_lumos.py -k choice_scope_rule_output`,5 條全過。巢狀 100 層時,有雙重否定輸出 76,548 位元組,正面寫 45,912,340 位元組,門檻 1MB 抓得到。
- 現況每條規則外層都確實有 `not: {not: …}`,diff 第 44–386 行逐條看過,所以這是日後回歸的守衛缺口,不是現在的洞。

## r3 新規則在深層巢狀上的掃描時間約為既有規則包的 3 倍,但量級可接受
severity: minor
blocking: 否

引句:「# 本身是子協程,或往下(不越過下一層 lambda)有子協程」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(diff 第 119–123 行的 `has-co`)

量測:作用域大括號 L 底下,每個節點都要測 `has-co`,節點數乘子樹大小就是平方。輸入是 `supervisorScope { val x = foo(foo(…1…)) ; launch{} }`,巢狀深 800 層,基準 0.66 秒,加上第三批規則後 2.18 秒。深 400 層是 0.18 秒對 0.56 秒。

其餘各項沒有放大:
- 平鋪 5000 個 `launch`、3000 到 20000 條 retry 的大檔,時間和基準相同。這幾個輸入的 14 秒或 5 秒都是既有 C-18 的平方成本。
- 巢狀 800 層 coroutineScope 與每層大量陳述,第三批只多 0.05 到 0.1 秒。
- 新規則沒有讓時間預算被吃光或被放行的新路徑。

## 其餘三問與圖譜鏡頭的結論

- 子程序:新增的程式碼沒有新開子程序。`_choice_scan` 沿用既有的 `_choice_sg_run`、`TemporaryDirectory` 和 `_lint_wt_*` 登記。S9 測試用 `subprocess.run(timeout=120)`,逾時會殺子程序。測試的 `tempfile.mkdtemp` 沒包 try/finally,逾時例外時暫存目錄會留下,是很小的洩漏。
- 記憶體:`_choice_anchor` 的 `_CHOICE_GAP_SKIP_RE.match(b, pos, endpos)` 是貪婪匹配,後面沒有失敗條件,不會回溯爆炸。`_choice_file_points` 的 ERROR 判定改成從錨點行起算,仍走既有二分查找,沒有平方。
- 冪等:`drop_call` 只回 `[(mv["A"][1], e, b"")]`,同一輸入重跑結果相同。
- 圖譜鏡頭:LUMOS-IMPACT 的固定席節點沒有附上(鏡頭計算超時),這條只能留空。我只對照了 diff 本身:新增的錨點「整個呼叫」只是加在 `CHOICE_ANCHORS` 尾端,沒有動既有順序。

總結:最高嚴重度 minor,blocking 共 0 條
