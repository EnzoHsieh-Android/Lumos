severity: minor

固定席圖譜筆記這次沒附(鏡頭計算超時),我沒補算。能做的判斷是:改動範圍只在 `scripts/lumos` 的選擇點段、`check.py` 的型錄檢查、`kotlin-choice` 規則與樣本、型錄一節。新增的 `category`、錨點和 `row` 欄位都是在表尾或新增分支上擴充,第一版的相對順序沒動。我實跑了真 ast-grep 加真型錄,第一版列的行為沒看到被弄壞。圖譜對照沒有發現合約被破壞,但筆記本身我沒逐篇讀。

## g1 「已撤列號」那行用全形冒號寫就整條守衛靜默失效
severity: minor
blocking: 否(守衛對半形寫法有效,全形漏掉只是疏漏,沒有弄壞既有行為)

走的路徑:`choice_tables` 呼叫 `_choice_retired_problems`,再呼叫 `_choice_retired`。後者只認 ASCII 的 `已撤列號:`。中文輸入法最常打出的 `已撤列號:C-37`(全形冒號)讓正規式不匹配,`_choice_retired` 的 `if not m:` 分支回空集合,沒有任何問題訊息。
- 預期:撤掉的 C-37 又出現在表和 `api.yml`,要擋(規格 S5)。
- 實際:不擋。

重現是在臨時 clone 裡把型錄那行換掉再呼叫 `check.choice_tables`:
- `已撤列號:C-37`(半形)回兩筆「列號不准重用」。
- `已撤列號：C-37`(全形)的撤號相關問題是 `[]`。
- 同一行寫成 `已撤列號: C-37 (原因)` 會報「看不懂」,所以只有「整行標籤被認成沒有這行」這一條路是靜默的。

引句:「_CHOICE_RETIRED_RE = re.compile(r"^已撤列號:(.*)$", re.M)」
file: `configs/ast-grep/kotlin-android/check.py:1395`、`configs/ast-grep/kotlin-android/check.py:1522`

這條守衛要防的就是「撤掉的號被悄悄重用」,卻會被一個常見的打字差異繞過。可以改成 `[::：]`,或在說明段內看到含「已撤列號」但正規式沒匹配的行就報問題。

## g2 引數類兩列的「全是常數」判定漏了負數與字元字面值,會產出等價壞法
severity: minor
blocking: 否(只造成多餘的存活與放行,不會做出錯的行為;規格只說「數字」,沒明講負數)

規則 C-36 與 C-37 的 `literal-arg` 只列了 boolean、null、integer、real、long、hex、bin、unsigned、不含插值的字串與 `Unit`。`-1` 是 prefix 運算式,`'c'` 是 character_literal,都不在清單裡。

我拿真型錄和真 ast-grep 對下面這段跑 `_choice_file_points`:
```
LaunchedEffect(-1) { a() }
val r = remember(-1) { 3 }
LaunchedEffect('c') { a() }
```
三行都挑出壞法:C-36 的 `LaunchedEffect(Unit)`、C-37 的 `remember { 3 }`、C-36 的 `LaunchedEffect(Unit)`。
- 預期:規則自己註解寫「全是常數的 key 換成 Unit 必然等價」,應該不產生。
- 實際:產生。這個壞法測試殺不掉,會逼人寫放行。

引句:「字面值:Unit、true、false、null、數字、不含 $ 的字串」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-36、C-37 的 `utils.literal-arg`)

## g3 重複貼上的規則片段沒有同步守衛
severity: minor
blocking: 否

`literal-arg` 在 C-36 和 C-37 各貼一份,`value-pos` 貼了一份自 `sbr.yml` 進 C-34。同步只靠註解「照抄一份,改 sbr.yml 時一起改」。
- 我 grep `scripts/test_lumos.py` 找 `literal-arg` 和 `value-pos`,沒有任何比對三份是否一致的測試。
- 具體失敗情境:有人像 g2 那樣補一個字面值種類,只改 C-36,C-37 靜默漂移,兩列的「全是常數」定義就不同。

引句:「ast-grep 的 utils 只在同一份規則文件裡有效,所以照抄一份,改 sbr.yml 時一起改」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`、`configs/ast-grep/kotlin-choice/rules-choice/sbr.yml`

## 逐角度結論(沒有其他會出錯的 finding)
- **編輯順序**:`_choice_identity` 以 `(起, 迄)` 由大到小套編輯,所以 `!!.` 的兩個編輯在同一位置時是先換 `?.` 再插 `!!`,結果正確。
- **註解守衛**:`?.` 前面有行註解或區塊註解時不挑,我實測 `foo() // c` 後換行 `?.bar`、`/* c */` 兩種都沒產出壞法。
- **串接鏈**:`?.bar?.qux` 前一個被註解擋掉時改挑後一個,輸出 `?.bar!!.qux`,沒錯。
- **其他壞法形狀**:`$A!!` 的括號、`x ?: null` 與 `null ?: x` 的排除、`x ?: y ?: z`、`?:` 換行都對。
- **引數錨點**:`LaunchedEffect(...)` 範圍內取第一個改動行,行號是 1 起算,與 `_choice_scan_parse` 一致;`_choice_plus_nodes` 呼叫 `_choice_anchor` 不傳 `changed`,對引數列沒影響。
- **統計與「已撤列號」**:`gov --stats` 依列號用的 `row`、`file`、`fp` 欄位都真的在統計列裡(`row` 在頂層,`file`、`fp` 在 `ck`),`_CHOICE_BASE_RED` 與判定處的字面字串一致。
- **取捨**:`.let` 的值被用到判定在 lambda 最後一句是 `forEach` 時會多收等價壞法,跟 `sbr.yml` 同樣取捨,不另報。
- **其他**:沒有重用、效率或慣例上的違規可逐字引出。
- **跑過的**:只在臨時 clone `/tmp/lumos-seat-work/code-選擇點第二批/通才-sonnet/` 跑實驗腳本,沒跑 `test_lumos.py`,也沒動 repo。

最嚴重:minor;blocking 共 0 條
