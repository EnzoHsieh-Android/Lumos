severity: minor

本席假設 `_TG_KOTEST_CHECK` 與 catch 型別位置表在某些輸入下出錯。三個 finding 都是 minor,沒有 major。我跑了作者的 6 個配對案例,修補本身成立。我在臨時目錄各 clone 一份修前(`34bef2d8`)和修後(`c2335430`),跑下面三組實驗。「歸因」裡的重現都是在這兩份 clone 上用 `scripts/lumos` 的 `_tg_functions` 加 `_tg_catch_no_fail` 跑的。

### F1 名字前綴寫成萬用字尾,一般的 should 開頭變數和方法被算成 Kotest 檢查
severity: minor
blocking: 否 — 只讓個別測試被多列一條或少列一條候選,放行有理由欄可處理,不會損壞資料或破壞合約
引句:「_TG_KOTEST_CHECK = re.compile(r"(?<!\w)should(?:Be|Not|Have|Contain|Start|End|Match|Throw|Exist)\w*(?!\w)(?!\s*[=:])")」
file: `scripts/lumos:48822`

失敗場景:
- 這條正規式只認前綴,後面接什麼都放行。`shouldNotifyUser`、`shouldBeep`、`logger.shouldBeLogged(e)`、`shouldHaveRetried`、`shouldEndSession()` 這類一般變數或方法,只要後面不是 `=` 或 `:`,就被當成檢查。
- 計劃 S6 明寫「名字以 should 開頭的一般變數或方法不算檢查」,這與條文衝突。
- 輸入 A:`try { foo() } catch (e: Exception) { if (shouldNotifyUser) notify(e) }` 加後面一句 `assertEquals(1,f())`。走到 `catch_checks = ... has("infix", cs, cb_end)`,規則一(try 沒有 fail、catch 裡有檢查)誤列。
- 輸入 B:`try { if (shouldHaveRetried) run() } catch (e: Throwable) { println(e) }`。try 側的 `tried` 被它點亮,規則二(吞斷言)誤列。
- 輸入 C:`try { foo(); fail("x") } catch (e: Throwable) { if (shouldNotifyUser) notify(e) }`。這個 catch 沒檢查,應該被規則二列出來。但 `shouldNotifyUser` 被當成檢查,規則二被擋住而漏列。

重現(兩版各跑一次,回傳值代表有沒有被列):
```
python3.14 -c "import importlib.machinery as M,importlib.util as U;l=M.SourceFileLoader('x','<repo>/scripts/lumos');s=U.spec_from_loader('x',l);m=U.module_from_spec(s);l.exec_module(m);b='try { foo() } catch (e: Exception) { if (shouldNotifyUser) notify(e) }\nassertEquals(1,f())';f=list(m._tg_functions('class T {\n    @Test\n    fun t() {\n'+b+'\n    }\n}\n',False)[0].values())[0];print(m._tg_catch_no_fail(f))"
```
- 輸入 A:修前 False,修後 True。輸入 B:修前 False,修後 True。輸入 C:修前 True,修後 False。

歸因:有證據的修復回歸。三個輸入的結果都是修前和修後不同。作者的測試 d6 只用 `shouldRetry`,剛好避開了這個前綴,所以沒有任何測試釘住它。

### F2 清單漏掉真的 Kotest 匹配器(shouldInclude、shouldEqualJson、舊版 shouldEqual、單獨的 should),正常的預期例外寫法被誤列
severity: minor
blocking: 否 — 只多列一條候選,放行有理由欄可處理
引句:「# Kotest 匹配器照名字認(shouldBe、shouldNot…、shouldHave…、shouldContain…、shouldStart…、shouldEnd…、shouldMatch…、shouldThrow…、」
file: `scripts/lumos:48819`

失敗場景:
- 輸入 D:`try { foo(); fail("x") } catch (e: Throwable) { e.message shouldInclude "boom" }`。try 有 fail,catch 用 Kotest 做了真檢查,是正常的預期例外寫法。
- 修前的窄中綴正規式把它認作檢查,不列。修後 `catch_checks` 為 False,又因為 `Throwable` 在型別位置而 `tried` 為 True,規則二誤列。
- 同形的輸入 `shouldEqualJson`、舊版 `shouldEqual`、單獨的 `should startWith(...)` 結果相同。
- 相反方向也受影響:`try { foo() } catch (e: Exception) { e.message shouldInclude "a" }` 的規則一,修前列,修後不列(漏列)。
- `shouldInclude`、`shouldEqualJson` 是 Kotest 字串與 JSON 匹配器,這點是我憑印象寫的,沒上網查。⚠

重現:同 F1 的指令,把 `b` 換成輸入 D。
- 輸入 D:修前 False,修後 True。
- 同形的 `shouldEqualJson` 與 `shouldEqual`:修前 False,修後 True。
- 單獨的 `should startWith(...)` 兩版都是 True。這個形狀的 catch 檢查一直沒被認,不是新增的問題。

歸因:有證據的修復回歸。修前把任何 `should[A-Z]\w*` 中綴都當成檢查,修後改成九個前綴的白名單,不在名單內的真匹配器掉了出去。

### F3 這一輪新增的幾個行為分支,拿掉後測試仍全綠
severity: minor
blocking: 否 — 現在的程式行為正確,只是有幾條分支沒有測試釘住,日後被改壞不會紅
引句:「if has("ctype", c.end(), close) and tried and not catch_checks and not has("throw", cs, cb_end):」
file: `scripts/lumos:48851`

我把下面每一種改壞各套用到修後的 clone 上,跑了相關測試。都沒有紅:
- **M1**:拿掉 `(?!\s*[=:])`。`-k tq_` 215 passed,`-k test_guard` 87 passed。唯一碰過宣告的測試 w3 用的是 `shouldRetry`,前綴本來就不符。
- **M2**:前綴清單只留 `Be|Not`,砍掉 `Have|Contain|Start|End|Match|Throw|Exist`。`-k tq_guard_catch` 26 passed。測試檔裡完全沒有這七類名字。
- **M3**:`_tg_next_nonspace` 退回只認 ASCII 空白。`-k rg_methods` 31 passed。r6 的 FF、VT、全形空白三條案例都放在行尾逗號之後,只釘得到 `_tg_line_last` 那半。把 `_tg_line_last` 退回去才紅(M4 紅 3 條)。
- **M6**:catch 型別範圍從 `close` 改成 `cb_end`,等於連 catch 本體裡的 `Error` 字都算進型別。`-k tq_` 與 `-k test_guard` 全綠。
- 這個改壞會讓 `try { assertEquals(1,f()) } catch (e: IllegalStateException) { foo(Error()) }` 被誤列成吞斷言。型別位置表是這一輪新寫的,唯一測它的是 1 萬 2 千層的耗時斷言,沒有測正確性。

有翻紅的確認項(對照用):M4 退回 `rstrip(" \t\r")` 紅 3 條,M5 退回舊泛型正規式紅 1 條。

歸因:有證據的原有漏查。這些分支是這一輪才加的,所以測試缺口也是這一輪才有。

## 圖譜鏡頭
- 我在 repo 目錄跑了 `lumos show Systems/test-guard`,這份 diff 的文件修補只動 WHY 行,沒有破壞它宣稱的行為。
- 其餘節點沒有讀,判斷根據是這份 diff 沒有動到它們的程式:
  - `Systems/pitfalls-lint-adapter`、`Systems/room-guard`、`Systems/測試假綠形態` 的程式沒動。
  - 對 Room 守衛有影響的是 `_TG_NAME_RE` 與 `_tg_line_last`,但它們屬於 test-guard 自己的 `_tg_*` 函式。
  - 指紋不含 `extra`:`_tg_cand` 的 key 只用 rule、file、ident、nth,所以 `tq/too-large` 補上「這支整支沒比對」不會讓舊放行失效。
- 節點的 WHY 與 S6 條文一致,但都寫「照名字認」,沒有揭露前綴是萬用字尾的取捨。這就是 F1 的來源。

## 三問
**①原問題的修復效果**
- 我在修前和修後各跑了 d1 到 d6 六個案例。修前全紅(`got` 與 `want` 全部相反),修後全綠。
- 巢狀 catch 型別:輸入是 `"try{}catch(\n"*12000 + "x\n" + "){p()}\n"*12000`,修前 13.93 秒,修後 0.08 秒。
- 泛型:`fun <T : List<Int>> t()`,修前找不到名字,修後找到 `t`。`fun <T, R> t()` 兩版都找得到。
- 行尾空白字:FF、VT、全形空白、NBSP、NEL(U+0085)、LS(U+2028)接在行尾逗號之後,修前類別路徑掉成 `['t']`,修後為 `['FooTest.t']`。
- 「這支整支沒比對」與參考頁說明:`-k tq_guard_cli` 59 passed。

**②修補處的正常路徑與相鄰路徑**
- 全形空白或 NBSP 在行尾的正常類別沒有被誤判。有本體、沒本體、介面、下一行接大括號等九種形狀,兩版輸出相同或只修好 FF、VT、NEL、LS 那幾條。
- 泛型正規式的耗時:8 種病態輸入(400 組巢狀、沒收尾、全是 `fun <`),兩版都在 3 毫秒內,沒有變慢。
- 兩層以上的巢狀泛型(`<T : Map<String, List<Int>>>`)仍然找不到名字,這是作者清單已寫的限制。
- 補充觀察:這種函式如果本體裡有區域 `fun inner()`,函式鍵會被記成 `A.inner`,而不是整支不比。這在修前已是如此,不算新增問題。
- `fun <T> List<T>.t()`(泛型接收者)兩版都找不到名字。JUnit 無法執行擴充函式,實際影響很小。
- catch 型別位置表與舊的範圍搜尋,在字詞命中區間上等價。型別寫在註解或字串裡、括號配不到、`java.lang.Error`、`MyError` 我都跑過,結果都合理。
- 新增 `Throwable`/`Error` 同族的 `ComparisonFailure` 沒被當成可吞斷言的型別,這是原有狀況,不是這一輪的範圍。

**③新發現的同一案例,修前與修後**
- F1 輸入 A、B、C 的修前與修後是 False→True、False→True、True→False。
- F2 輸入 D 與同形輸入是 False→True。
- F3 的四個改壞(M1、M2、M3、M6)修後 clone 上都沒有測試翻紅。

未驗範圍:
- 完整的 `-k tq_` 與 `-k test_guard` 只在改壞時各跑過一次,沒有在乾淨修後版本上單獨記錄。
- 沒有端對端跑新增告警閘整合。
- 沒有確認 Kotest 實際 API 清單。
- 我沒有跑完整的 3700 案例閘。

這一輪的修補本身站得住,但 Kotest 名字前綴既會把 `shouldNotifyUser` 這類一般變數誤當檢查,也漏掉 `shouldInclude` 這類真匹配器,而且新分支的測試沒有釘牢。
