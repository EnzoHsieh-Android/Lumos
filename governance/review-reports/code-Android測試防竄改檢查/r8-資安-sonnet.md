severity: major

## ①提示注入

### S1 「修前先查世界」把網頁文字帶進編排者上下文,再寫進會被審查席讀到的計劃筆記
severity: minor
blocking: 否 — 推論:規則沒讓網頁文字直接進派工詞或掛鉤,要多一層 AI 摘要才會碰到,而且專案已裁定自用框架不過度防外來文字回顯。
引句:「每組根因動手前先上網查業界做法與論文(WebSearch 先 standard,不夠再 extended」
file: `skills/lumos-code-loop/SKILL.md:51`
攻擊路徑:
- 誰:能影響搜尋結果頁面內容的第三方。
- 從哪裡:編排者照新條文做 WebSearch,搜尋結果進它的上下文。
- 送什麼:頁面裡藏的指示文字,例如「採用這個做法、略過某項檢查」。
- 拿到什麼:編排者把它摘成 `PRIOR-ART:` 行,寫進 rN-intake.md 和計劃筆記。計劃筆記是下一輪的審查材料,後續的 AI 就可能照做。
- 條文只說把「會漏、會誤判的做法」列成排除,沒說網頁內容只當資料、不當指令。
- 推論的原因:沒有實測。
重現:無(推論)。
歸因:有證據的修復回歸(skill 本輪新加,修前版本沒有這段)。查證:在 `c2335430` 的 `skills/lumos-code-loop/SKILL.md` 搜「修前先查世界」得 0 筆;在 `537bb543` 得 1 筆。

## ②讀寫與執行越界

已看,無。
- 本輪修補只改正規式與 `_tg_catch_no_fail` 的判斷,沒碰讀寫、子程序或環境變數。
- 整份 diff 裡新增的讀 git 都走既有的 `_lens_git_dl` 與 `_nodehome_cat_blobs_capped`,沒有 `shell=True`。
- 印給人照抄的放行指令用 `shlex.quote`,檔名先過 `_out_clean`。
- 公開檔掃過一遍:沒有 `/Users/` 本機路徑、信箱、金鑰或 token。套件名只有 `com.example.pos.*` 的佔位字樣。考場只出現專案名 mOrangePos,沒有私有類別名或測試名。
- 「公司私有消費專案」「付款 SDK」這類只是泛稱,不報。

## ③非刻意、一步就能繞過的守衛

### S2 catch 型別字表漏掉 AssertionError 的子類別,窄型別的 catch 吞斷言不會被列
severity: major
blocking: 是 — 一次編輯就能讓同一種吞斷言寫法整個不被列,而且是這一輪「只看結構」要補強的那條規則自己的洞。
引句:「_TG_CATCH_ASSERT = re.compile(r"\b(?:AssertionError|AssertionFailedError|Error|Throwable)\b")」
file: `scripts/lumos:48813`
攻擊路徑:
- 誰:照常操作的 AI。例如 JUnit4 的字串 `assertEquals` 紅燈,失敗訊息第一行就是 `org.junit.ComparisonFailure`,AI 照著抄出型別名寫 catch。
- 從哪裡:編輯一支既有測試,把 `assertEquals("hello", greet())` 包進 `try { … } catch (e: ComparisonFailure) { println(e) }`。
- 送什麼:catch 型別是 `org.junit.ComparisonFailure`、`org.junit.internal.ArrayComparisonFailure`、`org.opentest4j.MultipleFailuresError` 或 `MockitoAssertionError` 這類 AssertionError 的子類別。
- 拿到什麼:`ctype` 比對不到,`tq/catch-no-fail` 不列。斷言數量沒變,所以 `tq/assert-weakened` 也不列。測試靠吞掉失敗變綠,推送前閘 0 條候選。
- 這個 repo 自己在別處(收證那條,筆記 PITFALL 和 `_SG_DEVICE_TEXT`)已把 `ComparisonFailure` 當斷言失敗,這裡的字表卻沒收。
- 這是型別名字表,不是結構判斷,正是這條規則前幾輪被打穿的同一類寫法。
- 與 Error Prone 的差別:我沒查它的原始碼,不下結論;如果它對子類型也不報,那這裡等於跟它一樣,但仍是真洞。
重現(臨時 repo,base 是 `assertEquals("hello", greet())`,head 包進 catch):
```
python3.14 scripts/lumos test-guard --repo <臨時repo> --diff <base>..HEAD
  catch ComparisonFailure       → 作弊候選 0 條 (修前、修後相同)
  catch AssertionError(對照)  → 作弊候選 1 條 [tq/catch-no-fail]
```
我另用函式級呼叫驗過:`MultipleFailuresError`、`MockitoAssertionError` 同樣不列。
歸因:有證據的原有漏查。`_TG_CATCH_ASSERT` 在 `c2335430` 與 `537bb543` 逐字相同。我寫了 1008 種「try 內容 × catch 型別 × catch 本體」的組合,修前列、修後不列的一個都沒有(0 條回歸)。

### S3 「重丟」只看有沒有 throw 字或 `fail(` 字,條件式重丟與 `Report.fail(e)` 會讓吞斷言不被列;說明文字沒講
severity: minor
blocking: 否 — 要 AI 另外寫條件分支或呼叫名字叫 fail 的方法,算刻意多寫一步;而且這些寫法跟修補前一模一樣,沒有新增的洞。
引句:「if has("fail", cs, cb_end):」
file: `scripts/lumos:48844`
另一處引句:「if has("ctype", c.end(), close) and tried and not has("throw", cs, cb_end):」,在 `scripts/lumos:48854`。
攻擊路徑:
- 誰:照常操作的 AI。
- 從哪裡:編輯測試,寫 `catch (e: AssertionError) { if (System.getenv("CI") == null) throw e }`,或 `catch (e: AssertionError) { Report.fail(e) }`。
- 送什麼:catch 本體裡出現 `throw` 字(含死分支、條件式、lambda 裡)。`_TG_FAIL_CALL` 的 `(?<![\w])` 也放行 `.fail(`,所以任何 `x.fail(` 都被當成 `fail()`。
- 拿到什麼:`catch_no_fail` 回 False,0 條候選。CI 上斷言失敗被吞掉,同一份測試在本機仍會紅。
重現:臨時 repo 三支測試改成條件式 throw、`Report.fail(e)`、「先接一個 IOException 再接 AssertionError」。修前與修後 `test-guard` 都是 `作弊候選 0 條`。
說明文字不一致:
- 標準寫「又不重丟(不看 catch 裡寫了什麼檢查)」。
- `_TG_WHY` 的訊息寫「裡面不管寫什麼檢查,…都會先被它接住」。
- 實際上「有任何 `throw` 字或 `fail(` 字就算重丟」,而這兩條在「抓不到」清單裡都沒寫。
- 「同一個 try 有好幾個 catch 時只看第一個」那條有寫,但寫成只是限制;其實加一個無關的第一個 catch 就繞過。
歸因:有證據的原有漏查。`_TG_THROW`、`_TG_FAIL_CALL` 與 `has("throw")`、`has("fail")` 在修前版本逐字存在。同一批輸入在 `c2335430` 與 `537bb543` 的結果相同。

我看過但沒列為發現的幾點:
- 「catch 裡寫名字含 throw 的字」:`\bthrow\b` 不會被 `rethrow`、`throws`、字串或註解騙到,我實測都被正確忽略。只有真的獨立 `throw` 字(含 `Result.throw(e)`)會算重丟,併入 S3。
- 誤報量:正常的預期例外寫法(`catch` 特定例外、`Exception`)我實測都不列。只有 `catch (e: Throwable/Error/AssertionError)` 且 try 內有斷言才列,不太會逼人習慣性放行。
- 把斷言包進 helper:`checkResult(f())` 沒有斷言字,不算 try 內有斷言,不列。修改既有測試時斷言數變少,會由 `tq/assert-weakened` 接住。
- `try { 斷言 } finally { return }` 吞斷言的寫法不列,屬刻意多步,不另列。

整體來說,這一輪的修補沒有讓守衛變弱,但 catch 吞斷言這條規則的攔截範圍還有型別字表和 throw/fail 字面判斷兩個洞,第一個是照常編輯就會碰到的。
