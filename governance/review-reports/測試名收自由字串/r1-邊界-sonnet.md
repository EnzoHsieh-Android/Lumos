severity: major

審查鏡頭:邊界可執行。已讀全文並逐項查證 `scripts/lumos`。F1 的 `_strip_test_comments` 失敗場景已實際執行,其餘各條由程式碼閱讀得出。實驗放在 `/tmp/lumos-seat-work/測試名收自由字串/邊界-sonnet/t.py`,只有這一個檔。

## 做法 2 掃描

**F1**
severity: major
blocking: 是(照字面實作會收進不存在的假測試名,又漏掉真測試)
引句:「c-style 註解照舊先剝;字串裡的假呼叫不另處理」
- 位置:做法 2「掃描收整個字串字面」與〈實務隱患〉。
- 問題:`discover_test_methods` 先跑 `_strip_test_comments` 的 c-style。它的 `//[^\n]*` 與 `/\*.*?\*/`(re.S)不分字串內外。舊規則只收識別字名,字串裡幾乎不會有 `//`。收句子名之後,標題含 URL、glob、`/*` 就會被破壞。
- 具體例(實跑輸出):
  - `it('GET http://x/api 回 200', …)` 被剝成 `it('GET http:`,字串沒閉合,這支測試漏掉。
  - `it('glob src/**/*.ts 被忽略')` 的 `/**/` 被當註解剝掉,變成 `glob src*.ts 被忽略`,收進一個不存在的假名字。
  - `it('a/* 開頭')` 的 `/*` 一路吃到後面某個 `*/`,中間 `it('中間的測試')` 整支消失,收進假名 `a 符號`。
- 照 spec 實作:條款綁真名字判懸空;綁假名字反而判「綁好了」,而測試工具跑出零支。
- S1 到 S3 沒有含 `//` 或 `/*` 的標題,測不到這個洞。
- 佐證:file: `scripts/lumos:6264`(`_strip_test_comments`)。

**F2**
severity: major
blocking: 是(新規則把一般程式碼收成假測試,製造假綠的綁定)
引句:「不是前半段;部分擷取的假證據不會出現」
- 位置:做法 2,「收第一個引數的完整字串字面」。
- 問題一,`.test(` 方法呼叫:三條正規式都以 `\btest\(` 起頭,沒排除前面的 `.`。`expect(/^\d+$/.test('hello world'))` 在 JS 測試檔很常見。
  - 舊規則要求單一識別字所以幾乎不誤收;新規則任何字串都收,`'hello world'` 會進測試集合。
  - 靜態綁定檢查(Check T、doctor S20、條款綁定)會判「存在」。實跑零支雖會判弱證據,但靜態檢查已放行。
- 問題二,第一個引數不是單純字面:`it('a' + suffix, …)`、`it('a'.repeat(3), …)`。spec 沒寫字面後面必須緊接 `,` 或 `)`,照字面實作會擷取 `'a'`,這正是舊設計理由 2 要防的部分擷取假證據。
- 具體例:輸入 `it('下單' + suffix, …)`,預期不收,照 spec 會收進名字 `下單`。
- 〈實務隱患〉只講「字串裡長得像 `it('…')`」,漏了這兩種。S1 到 S3 沒有反例輸入。

**F3**
severity: major
blocking: 是(殺傷力配方的 test 欄在多平台會被截斷)
引句:「跑的時候照做法 4 跳脫」
- 位置:做法 1 冒號規則、做法 6 guard kill 列、S20。
- 問題:`_kill_method_name` 在多平台時,只要 test 字串含 `:`,就切掉第一個冒號前面的部分。
- 具體例:
  - 配方 `platform: web`、`test: "API: 逾時"`,多平台。實際跑的名字變成 ` 逾時`。
  - 同時 `_kill_test_binding` 用 `resolve_test_refs` 把 `[test:web:API: 逾時]` 解成 `API: 逾時`,兩邊失配。
- 做法 6 只說 `_KILL_METHOD_OK_RE` 換成 `_test_name_ok`,沒提 `_kill_method_name` 與 `resolve_test_refs` 的切法要統一。S20 只測不含冒號的句子名。
- 佐證:file: `scripts/lumos:18489`(`_kill_method_name`)。

**F4**
severity: major
blocking: 是(單平台的 `_test_names_of` 會改壞名稱)
引句:「切法對齊做法 1;壞名判法換成」
- 位置:做法 1,「`_test_names_of` 改成跟 `resolve_test_refs` 一樣」,以及做法 6 note-shape 列。
- 問題:`_test_names_of(sp, key)` 沒有平台模式資訊。現在它對每個值都用 `_NS_TR_PREFIX_RE` 剝前綴,並去掉冒號後的空白。
- 具體例:單平台筆記寫 `[test:API: 逾時]`(`Error: …` 這類 JS 標題很常見)。
  - `_test_names_of` 產出 `API:逾時`(空白被吃掉)。
  - 後面 `_NsTrJudge._plat` 交給 `resolve_test_refs`,單平台整串當名字,比對 `API:逾時` 對不上真名,doctor S20 誤列。
- spec 只說「切法對齊」,沒說簽名要加平台表、單平台不剝前綴。S22 和 S23 沒有含冒號名稱的案例。
- 佐證:file: `scripts/lumos:36169`(`_test_names_of`)。

**F5**
severity: major
blocking: 是(違反 S24 與「C#/Kotlin 判法不變」)
引句:「掃描照樣比對到,但還原出來的名稱過不了」
- 位置:做法 2,「還原出來的名稱過不了 `_test_name_ok` 就丟掉」與 `discover_test_methods` 改用 `_test_name_of_match`。
- 問題:`discover_test_methods` 是所有 profile 共用的。`KOTLIN_TEST_RE` 的反引號分支 `` `[^`]+` `` 現在就收含逗號或方括號的名字。
- 具體例:Kotlin 測試 `` fun `when offline, shows banner`() `` 現在是合法真測試。若全域套 `_test_name_ok` 會被丟掉,已綁它的合約變懸空,推送前閘轉紅。
- spec 沒寫過濾只限 JS/Dart 三條,S24 也沒有帶逗號的 Kotlin 反例。

## 做法 4 跑測試與條款可執行性

**F6**
severity: minor
blocking: 否(影響罕見,弱證據判定兜底)
引句:「名字比對一律整串相等(去頭尾空白後),不做大小寫或空白正規化」
- 位置:做法 4「篩選是子字串比對」與做法 1 的比對規則。
- 問題:`_spec_gate_declared` 用區分大小寫的 `m in nm` 數宣告數。就我所知,Jest 的 `-t` 與 Playwright 的 `-g` 建正規式時帶 `i` flag;Vitest 我不確定。⚠ 實作前請查實,我無法離線驗證。
- 具體例:`it('Login')` 與 `it('login')` 各一支,綁 `Login`。declared=1、工具選到 2 支,`_spec_gate_verdict` 的 `declared == 1` 分支把它當參數化放行,判綠。

**F7**
severity: minor
blocking: 否(掃描與實跑落差,兜底判定會擋)
引句:「改成收第一個引數的完整字串字面:單引號、雙引號、不含」
- 位置:做法 2,「字面裡的跳脫還原」。
- 問題:JS 的 `\n`、`\u4e2d`、`\x41` 沒還原。Dart 的 `'$x'`、`'${x}'` 是插值(動態名,不該收),`\$` 也沒提。
- 具體例:`it('a\u4e2d')` 掃到字面 `a\u4e2d`,實際標題是 `a中`。綁定判「綁好」,篩選選到零支(判成沒證明,誤導但不是假綠)。

**F8**
severity: minor
blocking: 否(舊容錯消失,全庫筆記 0 處受影響)
引句:「值裡用全形逗號或全形冒號的 0 處,改了不影響舊筆記」
- 位置:做法 1,「全形逗號、全形冒號不再切」。
- 問題:`scripts/test_lumos.py` 有既有測試鎖定全形容錯:第 92057 行 `[test:test_alive，test_dead3]`、第 92065 行 `[test:py：test_alive]`、第 92370 行 `[test:x：t_pre]`。改完會紅,spec 沒列要改的既有測試。
- 中文輸入法打出全形冒號的使用者,`[test:web：下單]` 會變成預設平台下的懸空名,沒有明確報錯。

**F9**
severity: minor
blocking: 否(驗收條款精度問題)
引句:「實作後拿 1MB、全是未閉合引號的測試檔量一次掃描時間」
- 位置:S24、S10 與〈實務隱患〉效能段。
- 問題:
  - S24 的「跟改前一樣」沒有固定輸入,寫不出會紅的測試,需列黃金輸入(`Class.Method`、含點與空白的 Kotlin 名、C# 識別字)。
  - `_test_name_ok` 的 200 字上限沒有 199/200/201 邊界測試,空字串、純空白也沒有。
  - 效能檢查沒有通過門檻。同一行(minified 檔)有很多 `it('` 起點時,每個起點掃到行尾,整體是 O(n²),spec 沒要求量這種輸入。
  - S25 是 `[manual:]`,只剩 grep 說明文字。

## 已讀無 finding

- 做法 3(`⚠` 印法、擋不擋不變)、做法 5(`_apply_test_overrides`)。
- 做法 6 其餘各列:歸檔邊界、`guard trace`、處置帳。
- 〈不做〉、〈回退〉。
- 風險類:
  - 守衛面:收緊與放寬都有碰到,見 F2、F5。
  - 舊資料相容:見 F8。
  - 已在途分支:無需重新表態,舊寫法判法不變(識別字部分見 F5)。
  - 跟其他計劃交界:無,`d1` 多根多 profile 不受影響。

最嚴重:major,blocking 共 5 條(F1 到 F5)。
