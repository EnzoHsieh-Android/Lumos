severity: major

我已開 clone 逐條走過修補差異。這輪「只看結構」的主體(列/不列的規則)大致照宣稱運作,A、B、C、F、V 的結果見最後的「已驗主張」。新增的倍增耗時測試在有負載的機器上會偶發誤紅。測試也留下幾個沒釘住的缺口,結構判法本身有三處可繞過。

### F1 倍增耗時測試在有負載時偶發誤紅
severity: major
blocking: 是 — 推送前閘與 CI 會因機器忙碌而誤擋,而這個測試正是 S11 的驗收項
引句:「small, big = max(t1 - t0, 0.02), t2 - t1」
file: `scripts/test_lumos.py`(S11 r7 倍增迴圈,`t_tq_guard_cli_contract` 內)
失敗場景:
- 每個觸發字只量一次小輸入(6 千個觸發字)和一次大輸入(4 倍),整段只有幾毫秒到幾十毫秒。
- 小輸入的下限是 0.02 秒,沒有取中位數、沒有重試。
- 只要大輸入那一次剛好被排程或垃圾回收拖慢,就超過 8 倍而紅。
- 無負載時最壞比值 4.87。
- 本機另有別的會談的 `test_lumos.py --shard 1/4` 四個工作程序在跑,推送前閘本身也是 4 片並行,所以忙碌是常態。
重現(修後版):
- 同時開 10 份 `python3.14 scripts/test_lumos.py -k tq_guard_cli_contract`:8 份紅,例如 `S11 r7 倍增 'fun <':輸入 4 倍、耗時不超過 8 倍  (0.02, 0.209)`。
- 同時開 4 份,分兩批:共 8 份中紅 1 份。
- 在 19 種觸發字上另開 10 個空轉程序(約 1 倍負載)跑同一個量法:114 次量測紅 13 次。
- 無負載跑:97 項全綠。
歸因:有證據的修復回歸(測試是這輪新增的)。修前版(c2335430)沒有這個測試,無法比較;修後版的失敗只在有負載時出現,屬不穩定。

### F2 「catch 有沒有重丟、有沒有 fail」只看字面出現,三種寫法能繞過
severity: minor
blocking: 否 — 要刻意寫才繞得過,後果是漏列一條候選,不會讓判讀出錯或崩潰
引句:「if has("ctype", c.end(), close) and tried and not has("throw", cs, cb_end):」
file: `scripts/lumos:48851`(`_tg_catch_no_fail`;`has("fail", cs, cb_end)` 在同函式更上面)
失敗場景(try 裡有 `assertEquals`、catch 接 `AssertionError`,函式皆在修前與修後版各跑一次):
- `catch (e: AssertionError) { if (false) throw e }`:throw 在條件裡,修前與修後都不列。
- `catch (e: AssertionError) { val g = { throw e } }`:throw 在沒被呼叫的 lambda 裡,修前與修後都不列。
- catch 裡的 `try { x() } catch (z: Exception) { throw z }`:throw 屬於內層,修前與修後都不列。
- `catch (e: AssertionError) { promise.fail(e) }`:`_TG_FAIL_CALL` 的 `(?<![\w])` 放行任何 `物件.fail(`(例如 Vert.x 的 promise),修前與修後都不列。
- 反過來,`failure(e)`、`val throwable = e`、註解或字串裡的 throw 都正確判成吞掉(都有列),字面比對這幾步沒問題。
歸因:有證據的原有漏查。修前版 c2335430 與修後版結果相同(兩版各跑同一批輸入),修補沒碰這兩個判斷。

### F3 新增測試沒釘住的幾個角落
severity: minor
blocking: 否 — 現行程式碼的行為是對的,只是改壞了測試不會紅
引句:「每行都在單行上限內」, max(map(len, mk(4 * n).split("\n"))) <= m._TG_MAX_LINE_CHARS, tok)」
file: `scripts/test_lumos.py`(S6 r7 的 e1–e5 與 S11 r7 倍增迴圈)
失敗場景(在 clone 上改壞再跑 `-k tq_guard_catch` 或 `-k tq_guard_cli_contract`):
- 把 `_TG_THROW` 的字尾 `\b` 拿掉,`val throwable = e` 就被當成重丟而不列。結果 31 項全綠,沒有測試用到 `throwable` 這種識別字。
- 把 `_TG_FAIL_CALL` 的 `(?<![\w])` 拿掉。結果 31 項全綠。
- 把 `has()` 的二分查找改成線性掃描。`try{assertEquals(1,2)}catch(e:Exception){throw e};` 重複 2.4 萬次要 30.7 秒,原版 0.29 秒。整個 `-k tq_guard_cli_contract` 的 97 項仍全綠。原因是 19 種觸發字沒有一個同時含 try 和斷言字,`has` 的位置清單都是空的。
- 倍增測試的前置斷言只查行長,沒查 `fns` 非空。我量過現況是 1 支,所以現在不是空轉,但沒有被釘住。
歸因:有證據的原有漏查(`has()` 二分的效能性質在修前版也沒有測試釘住,新的倍增網沒補上);其餘兩項是這輪新增判斷沒有對應測試。

### F4 try 側也被 should 寬判,文件只說 catch 那半
severity: minor
blocking: 否 — 多一條可放行的候選,屬於使用者接受的代價類別,但行為與文字不符且沒測試
引句:「tried = has("assert", t.end(), tb_end) or has("infix", t.end(), tb_end)」
file: `scripts/lumos:48849`
失敗場景:`try { if (shouldRetry) foo() } catch (e: Throwable) { println(e) }` 在修後版被列為 `tq/catch-no-fail`,修前版不列。catch 接 `Exception` 時兩版都不列(因為接不到 `AssertionError`)。文件(計劃 WHY、diff 內註解)寫的是「try 沒 fail、catch 有斷言那半」才寬判,但兩側共用同一份 `infix` 位置清單,try 側也跟著放寬。沒有測試釘這一側,用窄判法換回 try 側也不會紅。
歸因:有證據的修復回歸(修前不列、修後列,兩版各跑同一個輸入)。

### F5 catch 型別字表有 AssertionFailedError、漏掉 AssertionError 的常見子類
severity: minor
blocking: 否 — 只漏列一種寫法,放行機制不受影響
引句:「AssertionError|AssertionFailedError|Error|Throwable」
file: `scripts/lumos:48813`(`_TG_CATCH_ASSERT`)
失敗場景:
- `try { assertEquals("a", f()) } catch (e: ComparisonFailure) { println(e) }` 不列。JUnit4 的字串 `assertEquals` 失敗丟的正是 `ComparisonFailure`,所以測試會被吞成綠。
- `catch (e: MultipleFailuresError)` 同樣不列。
- 同一份字表卻收了 `AssertionFailedError`,標準不一致。
- 反方向:`catch (e: Result.Error)` 這種自訂巢狀型別會被 `\bError\b` 誤列。這個代價可接受。
歸因:有證據的原有漏查。修前版 c2335430 兩版結果相同(未列)。

## 圖譜鏡頭
- 本席沒拿到固定席節點。我沒有再讀 `Systems/test-guard` 與 `Systems/測試假綠形態`,只比對了計劃的 S6、S11、S16 和這輪改動的文件差異。
- S6 條文與程式一致:try 有斷言或 `fail`、catch 接得住 AssertionError/Error/Throwable、catch 不重丟,就列;catch 型別只看括號裡。
- S6 條文漏寫 try 側同樣放寬(F4)。
- S11 的「十幾種觸發字倍增 8 倍」條文實作了,但有 F1 的不穩定和 F3 的覆蓋缺口。
- S16 的「換行後全部空白字」:我拿修前版驗過,它本來就通過(程式沒改,測試是新增釘住),`\v`、`U+2028`、`U+00A0` 在兩版也都通過。
- 這份差異沒有破壞 `Systems/test-guard` 宣稱的其他行為。
- `_TG_LIMITS` 刪掉「恆成立的檢查算有檢查」那句,與新行為一致,`-k tq_guard_cli_contract` 的比對測試綠。

## 三問
1. 原問題的修復效果:
   - 輸入:`try{ h(); fail("x") }catch(e:Throwable){ assertTrue(e is ISE) }`(S)。預期:列(只看結構)。
   - 修前版不列,修後版列。命令:用 `_tg_functions` 加 `_tg_catch_no_fail` 在兩版各跑一次。
   - 輸入:`AssertionError` 加 `shouldNotify(e)`(e1)、Kotest 點號呼叫(d2–d4)。預期:列。修後版全列(`-k tq_guard_catch` 31 項綠)。
   - 輸入:`Error()` 只出現在 catch 本體(Q、e3)。預期:不列。兩版皆不列。
   - 「只看結構」確實生效:catch 型別只看括號裡,把範圍改成整個 catch 本體時 e3 會紅。
   - 沒看出被修好的:F2、F5 在兩版結果相同,屬原有缺口,不是這輪修補造成。
2. 修補處的正常、錯誤與相鄰路徑:
   - 輸入:`try{assertEquals}catch(e:AssertionError){ throw e }`、`catch(e:Throwable){ if (e !is ISE) throw e }`(V)、`catch(e:AssertionError){ fail("wrapped") }`(e4)。預期:不列。兩版皆不列。拿掉 `has("fail")` 的略過,e4 與 c5 會紅,測試有效。
   - 輸入:catch 接 `Exception`,或 `catch(e:IOException){...} catch(e:AssertionError){...}`。預期:不列。兩版皆不列;後者是已寫明的「只看第一個 catch」限制。
   - 輸入:try-with-resources。預期:不列(已寫明的限制)。
   - 例外:F4 的 try 側 should 寬判是修後才多出來的行為差。
3. 新發現的同一案例修前修後:
   - F1:修前沒有這個測試,修後有負載時紅,無負載時綠。
   - F2:D、E、P、G 兩版結果相同(皆不列)。
   - F3:三種改壞都只在修後版的測試裡驗證,修前版無對應測試。
   - F4:H 修前不列、修後列。
   - F5:J、K 兩版結果相同(皆不列)。

## 已驗與未驗範圍
- 已驗主張的證據:
  - 修後版 `-k tq_guard_cli_contract` 在無負載下 97 項全綠。
  - 修後版 `-k tq_guard_catch` 31 項全綠。
  - 對 `_TG_THROW`、`has("fail")`、catch 型別範圍三處做改壞實驗:拿掉 fail 略過會紅,catch 型別範圍改到 catch 本體 e3 會紅,改掉 `_TG_THROW` 的字尾 `\b` 不紅(F3)。
- 未驗:
  - CI 上每台機器跑兩片,我沒在真實 CI 上量 F1 的機率。
  - 完整的圖譜固定席節點沒有逐條讀。
  - Java 的 `catch` 多型別寫法只用了 3 個輸入驗過(J1–J3),沒有更多變體。
  - 全套 3700 案例沒跑。

倍增耗時測試在有其他程式搶 CPU 時會偶發誤紅,這是這一輪最要處理的;結構判法本身有幾個刻意才能繞過的洞,其餘是測試沒釘住的角落。
