severity: major

## 發現

### F1 類別宣告後接一大段空白時,判「有沒有本體」的略過空白迴圈變成「類別數 × 空白長度」,1 MB 檔跑 62 秒
severity: major
blocking: 是 — 超過計劃 S11 與「資安」段承諾的 30 秒效能上限,病態輸入會讓推送卡住
引句:「while k < n and stripped[k] in " \t\n":」
file: `scripts/lumos:48507-48514`(`_tg_supertype_next_line`;呼叫端 `scripts/lumos:48480` 在 `_tg_class_has_body`)

失敗場景:`_tg_class_has_body` 對每個 `class X` 記號,在行尾沒有 `,` 或 `:` 時呼叫 `_tg_supertype_next_line`。它用 Python 逐字元迴圈略過後面所有的空白與換行。`_tg_next_stop` 有快取,這個迴圈沒有。一行放約 2400 個 `class Ai`(不到 2 萬字),後面接 240 行各 19,999 個空白(約 4.8 MB,行數遠低於 10 萬行),最後才是 `{`。每個記號都要略過同一大段空白,而且最後都回傳 True。單檔成本約 2400 × 4.8M,推估 6 分鐘以上。比對在一支檔內不看截止時間,CLI 路徑完全沒有截止時間。這種輸入不會被「單行超過 2 萬字」或 10 萬行上限擋下。

重現(CLI,1 MB 檔,1000 個類別記號 × 50 行 19,999 個空白):
```
python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/ws2.py 1000 50 after
-> bytes 1010944 lines 55 maxline 19999
-> after  {'rc': 1, 't': 62.15, ...}
python3.14 .../ws2.py 1000 50 before
-> before {'rc': 1, 't': 61.32, ...}
```
函式層級的縮放:100 個記號 × 200 KB 花 0.61 秒,200 個記號 1.21 秒,400 個記號 2.36 秒,與記號數成正比,與空白長度成正比,合起來是平方級。

歸因:有證據的原有漏查。修前與修後耗時相同(62.15 秒對 61.32 秒)。這輪沒有碰這個迴圈,但這輪改寫了 `_tg_class_has_body` 的呼叫路徑,第四輪的「類別數 × 距離」平方級修補漏掉了這一處。

### F2 `catch (` 後面一直沒有 `)` 時,`_TG_CATCH` 的 `[^)]*` 對每個 try 都掃到檔尾,52 萬字元的檔跑 59 秒
severity: major
blocking: 是 — 超過 30 秒效能上限;5 MB 的同形檔推估要好幾個小時
引句:「_TG_CATCH = re.compile(r"\s*catch\s*\(([^)]*)\)\s*\{")」
file: `scripts/lumos:48789`(使用處 `scripts/lumos:48818`,`_tg_catch_no_fail`)

失敗場景:`try{}catch(` 連寫 N 次,後面接 N 個 `)`。括號個數相等,所以不會被判成 `tq/unparsable`。對每個 try,`_TG_CATCH.match(b, tb_end+1)` 的 `[^)]*` 都要掃到第一個 `)`,那個位置都在檔尾。N 個 try 的總成本是 N × 檔長,平方級。這輪新增的 `_TG_NONSPACE` 判空只改了後面的切片,沒有碰這個正規式。

重現:
```
python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/tc.py
(單支函式 _tg_catch_no_fail,after) 2000 次 0.15 秒;4000 次 0.59 秒;8000 次 2.32 秒;16000 次 9.22 秒(每次加倍,時間乘 4)
python3.14 -u .../tc2.py 40000 after   (CLI,檔案 520137 字元、40047 行)
-> after {'rc': 1, 't': 59.09, ...}
```
一行放 1600 個 `try{}catch(`、每行不超過 2 萬字,5 MB 內可到約 45 萬次,時間以小時計。

歸因:有證據的原有漏查。修前 8000 次 2.29 秒,修後 2.32 秒,幾乎相同。這輪新增的 `check` 與 `infix` 位置表是線性的,沒有讓它變差。

### F3 類別本體判斷在三種寫法下丟掉類別路徑(行尾註解、行尾空白、CRLF 夾空行)
severity: minor
blocking: 否 — 只讓函式鍵少了類別前綴,同名測試改用 `#2` 編號;刪除、改名、換斷言照樣被列出,沒有漏報或誤擋
引句:「if stripped[max(j, p - 50):p].rstrip().endswith((",", ":")):」
file: `scripts/lumos:48477`(視窗);`scripts/lumos:48510`(`_tg_supertype_next_line` 的空白集合少了 `\r`)

失敗場景:
- 視窗只看換行前 50 字,而註解與字串已被換成空白。`class A : B(), // 超過 50 字的說明` 換行接 `C {`,視窗全是空白,`rstrip()` 後是空字串,判成沒有本體。
- 行尾逗號後面接 60 個空白也一樣。
- CRLF 檔案裡 `class A` 空一行再 `{`,或 `class A` 空一行再 `: B() {`,`\r` 不在 `" \t\n"` 裡,判成沒有本體。
- 另外兩種:7 個以上的父型別各佔一行,會用完 8 段上限;Java 的 `extends` 在行尾、`B {` 在下一行也判錯。

重現(直接呼叫 `_tg_functions` 看函式鍵,`k.py`):
```
comma-eol(短註解)         after=['A.t'] before=['t']
comma-eol-comment-long    after=['t']   before=['t']
comma-eol-trailing-spaces after=['t']   before=['t']
crlf-blank                after=['t']   before=['t']
crlf-sup-next-blank       after=['t']   before=['t']
```

歸因:行尾註解與行尾空白這兩種是修補不完整:有證據的修復回歸類(修前根本不認行尾逗號,修後認了但視窗太短)。CRLF 夾空行是有證據的原有漏查,兩版相同。

### F4 catch 內「算有檢查」放寬後,改成只要出現 `should*` 識別字或 `check(true)`,就不再列出吞掉斷言失敗的 catch
severity: minor
blocking: 否 — 要靠刻意或湊巧的字眼才會漏;專案威脅模型不防 AI 刻意偽造。同形的 `assertTrue(true)` 修前就逃得掉
引句:「catch_checks = has("assert", c.end(), cb_end) or has("infix", c.end(), cb_end) or has("check", c.end(), cb_end)」
file: `scripts/lumos:48822`;`_TG_INFIX_RE` 在 `scripts/lumos:48573`(`\bshould[A-Z]\w*\b(?!\s*=)`)

失敗場景:
- 漏報:try 裡有斷言再接 `fail("x")`,catch 接 Throwable 或 AssertionError 卻吞掉。catch 內只要有 `check(true)`、`val shouldRetry: Boolean = false`(後面是 `:`,不是 `=`)、`logger.shouldLog(e)`,`catch_checks` 就為真,第二條「吞掉」判斷被跳過。
- 誤報:`try { cleanup() } catch (e: Exception) { logger.shouldReport(e) }` 後面有斷言,以前不列,現在因為 `should*` 被當成 catch 裡的斷言而列出。

重現(`c1.py`,同一個測試各跑修前、修後):
```
C2 catch{ val shouldRetry: Boolean = false }  before: tq/catch-no-fail   after: 不列
C3 catch{ check(true) }                       before: tq/catch-no-fail   after: 不列
C4 catch{ logger.shouldLog(e) }               before: tq/catch-no-fail   after: 不列
C6 try{cleanup()} catch{ logger.shouldReport(e) } + 後面有斷言   before: 不列   after: tq/catch-no-fail
C1 catch{ println(e) }  before、after 都列(有 fail 的 try 加吞掉的 catch 仍抓得到)
C5、C10 空 catch(含 CRLF)都列(判空沒壞)
```

歸因:有證據的修復回歸。C2、C3、C4、C6 的修前與修後結果不同。

### F5 assume 敘述身分裡,字串常值開頭或結尾的空白永遠被去掉,`"CI"` 改成 `"CI "` 不列
severity: minor
blocking: 否 — 要在字串邊界加空白才能讓 assume 條件改變語意;修前同樣不列(修前去掉全部空白),不是回歸
引句:「return re.sub(r"\s*([^\w\s])\s*", r"\1", text), k」
file: `scripts/lumos:48915`

失敗場景:引號本身是標點,所以字串常值裡緊貼引號的空白一定被去掉。`assumeFalse(System.getenv("CI") == null)` 改成 `"CI "` 或 `" CI"` 後,環境變數查不到,條件變成永遠為真,測試被略過,但兩版身分相同。`"a, b"` 改成 `"a,b"` 也相同。docstring 與計劃寫的「字串常值多一個空白要列」只在字詞中間成立(`"ci"` 改 `"c i"` 會列)。

重現(`a1.py`,A1、A2、A3):
```
A1 "CI" -> "CI "   before: 不列   after: 不列(rc 0)
A2 "a, b" -> "a,b"  before: 不列   after: 不列
A3 "ci" -> "c i"    before: 不列   after: 列 tq/skip-added   (這是修補生效的部分)
```

歸因:有證據的原有漏查。修前修後都不列。

### F6 `lumos test-guard` 的說明文字仍寫會比對「放寬 Gradle 或 CI 的測試設定」,但這個能力這輪已拿掉
severity: minor
blocking: 否 — 只是說明文字過期;程式末尾印的「抓不到」清單已改對,計劃與筆記也都改了
引句:「寫出沒斷言的測試、放寬 Gradle 或 CI 的測試設定(推送前新增告警閘也會跑)」
file: `scripts/lumos:70965`(`what-to-use` 對照表);`scripts/lumos:72187`(子命令 help 寫「建置或 CI 的測試設定被放寬」)

失敗場景:AI 或人讀 `lumos --help` 與 `lumos test-guard --help`,看到建置與 CI 放寬會被比對,改了 `ignoreFailures`、`-x test` 之後就以為有人把關。實際上這批完全不比。

重現:
```
python3.14 scripts/lumos test-guard --help
-> 什麼時候用:AI 改了測試或建置設定之後,想知道有沒有……放寬 Gradle 或 CI 的測試設定
```

歸因:有證據的修復回歸。縮範圍時拿掉了規則與 `_TG_LIMITS`,沒有同步改這兩處文字。

## 圖譜鏡頭

- 我在 repo 目錄跑了 `lumos impact --diff 047031883..5516466e...`。固定席只有 4 個受影響檔,指到 `test-quality-cli`、`測試假綠形態`、`pitfalls-code-loop`、`Android測試防竄改檢查_計劃` 等筆記。
- `Systems/測試假綠形態` 有一條 ★INVARIANT★:修 bug 的還原翻紅釘必須配前置斷言,證明現場真的走到被測分支。我是用 `lumos context --brief` 讀到的,沒有逐條對這輪的新測試。
- `Systems/test-guard` 與 `Systems/room-guard` 沒有登記合約。
- `Systems/test-guard` 已同步寫建置與 CI 移到第二批,並留了 `REVISIT:2026-12-15`。
- `_TG_LIMITS` 與測試品質標準的「抓不到」逐字相符,我用腳本逐條比對過。
- `-k tq_guard` 173 條全綠,我自己跑的。

## 三問

1. 原問題修復有行為證據嗎?有。
   - 縮範圍:`.gradle`、`.gradle.kts`、`.kts`、`buildSrc`、`build-logic` 底下的程式全部回傳 None,沒有崩掉,也沒有殘留引用(舊名稱 grep 全為 0)。
   - 深巢狀:2 萬層每層一支測試,耗時 2.0–3.0 秒(類別名 150 字時 2.97 秒)。行程峰值比空跑基線多約 40 到 50 MB,基線是 355 MB。
   - 摘要路徑:剛好 200 字不變,201 字換成摘要(長度 118),一路巢狀到 60 層沒有碰撞。
   - 敘述擷取:字串裡的左括號與字元常值 `'('` 以前會多列,現在不列;`"ci"` 改成 `"c i"` 現在會列。
   - catch:Kotest 中綴斷言和 `check(` 算有檢查,判空仍然正確。
   - 父型別行尾逗號:函式鍵從 `t` 變成 `A.t`(短註解版本)。
2. 修補處的正常、錯誤、相鄰路徑還成立嗎?大致成立,例外是 F3 與 F4。
   - 多行 assume 改條件、CRLF 的 `&&` 換行、跨行 Truth 鏈、`assumeTrue(cond) { "msg" }`、斷言換行重排、assume 搬到另一支函式、只改下一行不列,結果都正確(`a2.py` 的 A6、A7、B2、B5–B8、B10)。
   - 超過 2000 字的 assume 尾段不進身分,這是已寫進限制的行為;B9 在修前修後都不列。
   - F3 和 F4 是這輪修補自己的缺口,見上。
3. 新發現的同一案例,修前與修後各是什麼?
   - F1 與 F2:修前修後都慢(62.15 秒對 61.32 秒;2.29 秒對 2.32 秒),屬原有漏查。
   - F3:comma-eol 長註解的結果相同,屬修補不完整。
   - F4:C2、C3、C4 修前列、修後不列;C6 修前不列、修後列,屬修復回歸。
   - F5:修前修後都不列。
   - F6:說明文字是這輪縮範圍後才過期。

我的臨時目錄 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/邊界-sonnet/` 內有 `lumos_before`、`lumos_after` 與 `ws2.py`、`tc.py`、`tc2.py`、`k.py`、`c1.py`、`a1.py`、`a2.py`、`deep.py`、`deep2.py`,以及多個臨時 repo;我沒有刪,留給編排者收貨後用字面絕對路徑刪。

總結:F1(類別後接大段空白,1 MB 檔 62 秒)和 F2(`catch (` 一直沒有 `)`,52 萬字元檔 59 秒)是兩個超過 30 秒上限的病態輸入,修前修後相同,屬原有漏查;F3 到 F6 是範圍較小的缺口,其中 F3 的視窗不足與 F4 的放寬是這輪修補自己帶進來的。
