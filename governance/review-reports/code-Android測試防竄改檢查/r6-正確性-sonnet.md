severity: major

## 摘要

比起上一版,這一輪的修補有三處行為變了,其中一處(catch 判讀的 Kotest 認法收窄)用端到端的 `lumos test-guard --diff` 重現出新舊結果對調:修前列出真正的作弊,修後改列正常寫法。其餘修補(身分只在字串外整理空白、catch 括號改用對應表、類別名後判本體、效能三項)我挑了具體輸入逐條走過,行為成立。

所有實驗放在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet/`:`before/` 是修前 5516466e、`after/` 是修後 34bef2d8、`g2/` 是端到端的小 repo。

### F1 catch 判讀改用窄的 Kotest 認法,點號呼叫的 `.shouldBe(...)` 不再算檢查:修前列對的、修後列錯的,正常寫法被誤列
severity: major
blocking: 是 — 讓真作弊(try 沒丟例外就放過)不再被列,同時把有檢查例外的正常寫法誤列成吞斷言,守衛行為對調
引句:「_TG_INFIX_STRICT = re.compile(r"(?<=\s)should[A-Z]\w*(?=\s+[^\s=:])")」
file: `scripts/lumos:48824`(窄認法定義)、`scripts/lumos:48835`(`pos["infix"]` 換成它)

失敗場景:`_TG_INFIX_STRICT` 要求 `should…` 前面是空白、後面空白再接值,所以下面幾種真的 Kotest 斷言都被認成「沒檢查」。
- `e.message.shouldBe("x")`(前面是 `.`)
- `e.shouldBeInstanceOf<X>()`(前面是 `.`)
- `e.message shouldBe("x")`(後面是 `(`)
- `shouldThrow<X> { … }`(後面是 `<`)

這個窄認法同時管 `_tg_catch_no_fail` 的兩個子句,兩邊都出錯。
1. **子句 1(try 沒有 fail、catch 裡有斷言)漏列**:`try { foo() } catch (e: Exception) { e.message.shouldBe("x") }` 在 foo() 不丟例外時整支測試照綠,這是 S6 要抓的作弊。修前列,修後不列。
2. **子句 2(接得住 AssertionError 的 catch 不檢查)誤列**:`try { foo(); fail("x") } catch (e: Throwable) { e.shouldBeInstanceOf<IllegalStateException>() }` 的 catch 明明檢查了例外,修後卻被當成吞斷言。修前不列,修後列。

同一份程式裡「這支測試有沒有斷言」的 `_TG_INFIX_RE`(`scripts/lumos:48597`、`:48643`)仍把 `x.shouldBe(5)` 當斷言,所以兩處對同一個寫法的認定不一致。Systems/test-guard 的 WHY(行 33)自己也承認 `x.shouldBe(5)` 是斷言(「不選」欄寫著寬判法會把這種呼叫寫法誤列)。計劃 S6 只點名中綴 `e.message shouldBe "x"`,所以點號呼叫不算驗收條款明文承諾的形狀,但行為確實比修前退化。

重現(端到端,兩版同一個 repo `/tmp/lumos-seat-work/code-Android測試防竄改檢查/正確性-sonnet/g2`,base 只有 a(),head 新增 b 與 c):

```
b: try { foo(); fail("x") } catch (e: Throwable) { e.shouldBeInstanceOf<IllegalStateException>() }
c: try { foo() } catch (e: Exception) { e.message.shouldBe("x") }

python3.14 before/scripts/lumos test-guard --diff HEAD~1..HEAD --repo g2
  → FooTest.kt:9 [tq/catch-no-fail]   (c 被列,對)
python3.14 after/scripts/lumos test-guard --diff HEAD~1..HEAD --repo g2
  → FooTest.kt:5 [tq/catch-no-fail]   (b 被列,錯;c 不列,漏)
```

直接呼叫 `_tg_catch_no_fail` 的結果,依序為修前、修後:
- `rule1_dot`(`try{foo()}catch(e:Exception){e.shouldBeInstanceOf<…>()}`)= True、False
- `rule1_dot2`(`e.message.shouldBe("x")`)= True、False
- `dotcall_catch_instanceof`、`dotcall_catch_notnull`、`dotcall_catch_fail_try` = False、True
- `infix_paren_nospace`(`e.message shouldBe("x")`)= False、True
- `shouldThrow_in_catch`(`catch (e: Throwable) { shouldThrow<X> { bar() } }`)= False、True

歸因:有證據的修復回歸。兩版同一輸入結果相反,差異只來自這一輪把 `pos["infix"]` 從 `_TG_INFIX_RE` 換成 `_TG_INFIX_STRICT`。

### F2 函式名正規式把泛型限 400 字,超過就整支測試不被切出來;修前找得到
severity: minor
blocking: 否 — 要在測試函式宣告上寫超過 400 字的泛型參數才觸發,實際測試碼幾乎沒有
引句:「_TG_NAME_RE = re.compile(r"\bfun\s+(?:<[^>\n]{0,%d}>\s*)?" % _TG_MAX_GENERIC_CHARS」
file: `scripts/lumos:48416`

失敗場景:`@Test fun <T0, T1, …共 533 字> t() { assertEquals(1, f()) }` 在修後的 `_tg_functions` 找不到函式名,這支測試不進比對,改弱、刪除、沒斷言都不會被列,也不會列成 `tq/unparsable`。靜默漏掉,沒有留下紀錄。

重現:`list(_tg_functions(src, False)[0])` 修前得到 `['A.t']`,修後得到 `[]`。

另外,`fun <T : List<Int>> t()` 這種巢狀角括號,兩版都找不到(`[^>\n]` 在第一個 `>` 停下,接著要的是名字卻遇到 `>`)。這是原有漏查,不是這一輪造成的,同樣靜默。

歸因:400 字上限造成的漏判是有證據的修復回歸;巢狀角括號是有證據的原有漏查(兩版同為 `[]`)。

### F3 S6 的新測試沒有「合法的 Kotest 檢查」這一類反例,F1 因此測不到
severity: minor
blocking: 否 — 覆蓋面缺口,不是被保護的條款明文承諾的形狀
引句:「check("S6 r4 catch 用 shouldBe、check(、require( 檢查不列", not ({"s7", "s8", "s9"} & got5), got5)」
file: `scripts/test_lumos.py`(`t_tq_guard_catch_no_fail` 的 r4、r5 段)

失敗場景:r4 的「不列」反例只有中綴 `e.message shouldBe "x"`、`check(…)`、`require(…)`。r5 新加的 w1–w6 全是「要列」或「try 沒斷言才不列」。`.shouldBe(…)`、`.shouldBeInstanceOf<…>()`、`shouldThrow<…> {}` 在 catch 裡的行為沒人釘住,所以 F1 在 `-k tq_guard` 193 條全綠的情況下混過去了。測試前置斷言與獨立判準本身沒問題。

歸因:有證據的原有漏查。這個缺口早於這一輪,但這一輪的窄認法讓它開始有影響。

## 圖譜鏡頭

我讀了 `Systems/test-guard`,並用 grep 對 `pitfalls-lint-adapter`、`room-guard`、`測試假綠形態`。
- **test-guard**:節點把建置檔與 CI 寫成「不負責、移到第二批」,與這一輪的說明縮範圍一致。`_TG_LIMITS` 與標準的「抓不到」逐句對得上,`-k tq_guard` 的 cli_contract 通過。唯一對不上的是 WHY(行 33)的「不選」欄:它承認 `x.shouldBe(5)` 是斷言,卻讓 catch 判讀把它排除,這就是 F1。
- **room-guard**:只共用 `_rg_bracket_map`、`_rg_methods`,這一輪沒動它們,`-k rg_methods` 27 條通過,不受影響。
- **pitfalls-lint-adapter**:只提到 `tq/` 候選併進告警閘,這一輪沒碰閘的整合,不受影響。
- **測試假綠形態**:沒有提到 test-guard 的內部認法,不受影響。

## 三問

**① 原問題的修復效果有何行為證據?**
- **assume 身分**:`assumeTrue(env == " ci")`、`"ci "`、`"a,b"` 的身分與原版不同(列);`assumeTrue( env==\"c i\" )` 與原版相同(不列)。
  - 修前 `-k tq_guard_skip` 紅 3 條,修後綠。
  - `_tg_ident` 對沒收尾的字串、三引號、字元常值 `'"'`、反引號名、2000 字上限切在字串中間都不丟例外,輸出與預期相符。
- **類別名後判本體**:長註解、行尾空白、冒號後接空行與註解行、CRLF 空行、CRLF 冒號,修前得到 `['t']`,修後得到 `['FooTest.t']`。
  - 修前 `-k rg_methods` 紅 4 條,修後綠。
  - 對 8 段上限、Java `extends` 換行、body-less 類別後接下一個宣告也跑過,沒有新增誤判。
  - 快取鍵 `("ws", k)` 與 `("last", p)` 都只依文字位置決定,一次 `_tg_class_at` 內不會跨宣告給錯答案。
- **catch 括號**:型別含括號 `catch (e: Foo<(Int)->Unit>)`、`catch` 後不是 `{`、括號配不到,都不丟例外也不誤列;多個 catch 只看第一個,是已記載的限制。
- **效能**:`fun <` 沒收尾的 250 行各 3990 個 2.8 秒;250 支測試各帶一行這種長行 2.8 秒。
- **check(true) 與恆成立**:`check(true)`、`require(true)`、`val shouldRetry`、`logger.shouldLog(e)` 的 catch 修後被列,修前不列(`-k tq_guard_catch` 修前紅 6 條,修後綠)。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 字串、類別、括號、效能這幾處成立。
- catch 判讀的 Kotest 認法收窄這一處不成立,見 F1。
- 函式名的 400 字上限這一處不成立,見 F2。
- 修後 `-k tq_guard` 193 條、`-k rg_methods` 27 條全綠。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- F1:同一個 g2 repo 的兩支新測試,修前列 c、不列 b,修後列 b、不列 c(輸出見 F1 重現)。
- F2:同一個 533 字泛型輸入,修前 `['A.t']`,修後 `[]`。
- F3:無修前修後差異,屬原有缺口。

## 未驗範圍

- 我沒跑全套 3700 多條測試,只跑了 `-k tq_guard`、`-k rg_methods`,以及用修後測試檔對修前程式碼跑 `tq_guard_catch`、`tq_guard_skip`、`rg_methods` 確認新測試修前會紅。
- 這一輪的文件補丁(`r6-repair-docs.patch`)只對照了 Systems 節點與 `_TG_LIMITS` 的一致性,沒有逐字審。
- 新舊放行指紋互讀:test-guard 是這個分支新增的指令,沒有已發出的舊放行,所以身分算法改變沒有相容問題。

這一輪修補整體可用,但 catch 判讀改用窄的 Kotest 認法後,點號呼叫的檢查不再算數,造成真正的作弊漏列、正常寫法被誤列,這一條需要先處理;另有兩條覆蓋面上的小缺口。
