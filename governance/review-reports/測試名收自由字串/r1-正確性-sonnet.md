severity: major

審查範圍:凍結審材全文,另用 `scripts/lumos` 逐項核對計劃對程式現況的假設。工作樹是 `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps`。

**風險類**
- 守衛面:會碰,見 F2、F3、F4、F5。
- 舊資料與舊帳:無。舊筆記的識別字名走同一條路,F1 到 F5 都不影響它們。
- 已在途分支:無。判定只會從「懸空」變成「綁到」,不會變嚴。
- 跟其他會談或其他計劃的交界:`_kill_method_name` 與 `_dispositions_split_test` 是別的計劃寫的函式,見 F3、F4。

## F1 掃描前先剝 `//` 註解,標題含 `//` 或 `/*` 的句子名會被吃掉
severity: major
blocking: 是——照 spec 實作,含網址或路徑的標題掃不到,或誤吃後面的真測試,實作者會做出漏綁的壞系統。

- spec 段落:做法 2 掃描收整個字串字面,與〈實務隱患〉的註解剝除那句。
- 問題:`discover_test_methods` 先跑 `_strip_test_comments`,再用 `method_re` 比對。node-jest、dart 的 `comment_strip` 是 `c-style`,Playwright 沒設,預設也是 `c-style`。剝註解的規則是 `//[^\n]*`,以及 `/\*.*?\*/` 加上 `re.S`。
- 具體例:
  - 輸入:`it('GET https://x.io/a 回傳 200', () => {});`
  - 預期:收進 `GET https://x.io/a 回傳 200`。
  - 實際:我實測,剝註解後剩 `it('GET https:`,字面沒有閉合引號,整支掃不到,條款綁它永遠懸空。
  - 另一種:標題含 `/*`(例如 `'glob src/*.ts'`),會和後面某個 `*/` 配成一段,把中間的真測試整段剝掉。
  - 識別字名不可能含 `//` 或 `/*`,舊設計沒這問題;句子名放開後,網址和路徑在 Web 測試標題裡很常見。
- spec 沒有說明、也沒有條款覆蓋這件事,S1 到 S3 的例子都沒有斜線。
- 佐證:file: `scripts/lumos:6264-6274`(剝註解先於比對);file: `scripts/lumos:6294-6296`。
- 引句:「c-style 註解照舊先剝;字串裡的假呼叫不另處理(Java 那條同類問題用剝字串解,JS 不能剝字串,否則名字就沒了)」
- 需要補:剝註解必須字串感知(跳過引號內的 `//`),或換成可以處理字面的單趟詞法掃描。另加驗收條款:標題含 `://` 與 `/*` 的標題要被收到,同檔的後續測試不受影響。

## F2 spec 倚賴的「篩到 N 支就判弱證據」對 JS 三家與 Dart 不存在
severity: major
blocking: 是——spec 以為擋得住的假綠,在這幾個平台上沒有擋,句子名又特別容易撞名。

- spec 段落:做法 4 末段、〈實務隱患〉守衛面的假綠。
- 問題:`_RAN_EVIDENCE` 只有 swift-xctest、csharp-xunit、node-jest、python 四筆,且只有 python 有 `count_re`。所以:
  - node-jest 的 `_ran_count` 回 `(None, False)`。
  - node-vitest、playwright、dart 連證據樣式都沒有,見 `TEST_PROFILES["node-vitest"]` 與 `_ran_evidence_re`。
  - `_spec_gate_verdict` 的 `n >= 2` 判斷永遠不觸發,選到好幾支照判 `green`。
- 具體例:
  - 輸入:綁定名 `登入`,程式裡另有 `it('登入 失敗')`;Jest 的 `-t` 是子字串、對完整名稱(describe 加 test)比對,所以兩支都被選中。
  - 預期:判弱證據。
  - 實際:綁的那支是 `it.skip`、另一支 passed 時,摘要行 `Tests: 1 skipped, 1 passed` 命中 `Tests:.*?[1-9]\d*\s+passed`,判綠。
  - 句子名彼此互為前綴比識別字名常見得多,綁到 describe 標題時一次會選中整組。
- spec 的 S-條款也沒有一條要求選到兩支以上判弱,條款只有 python 路徑可測。
- 佐證:file: `scripts/lumos:54259-54278`(`_RAN_EVIDENCE` 只有 4 筆,只有 python 有 `count_re`);file: `scripts/lumos:8816-8830`(`_spec_gate_verdict`)。
- 引句:篩選是子字串比對:短句名可能同時選中別支。這不用新規則
- 需要補:regex 型的過濾可以錨定尾端,例如跳脫後的名稱接 `$`,Jest、Vitest 的完整名稱是 describe 加 test 用空白連接,所以前端要允許行首或空白。或者誠實寫下這幾家不判撞名,並把驗收條款縮到 python。

## F3 `_kill_method_name` 的冒號切法沒列進改動
severity: major
blocking: 是——S20 在多平台設定下會跑錯測試。

- spec 段落:做法 6 表格 guard kill、kill-add、doctor P2 那一列;做法 1 的冒號規則。
- 問題:`_kill_method_name(test, multiplatform)` 在多平台下只要 `":" in test` 就直接丟掉第一個冒號之前的全部,不驗前綴是否為已定義平台。舊規則下名稱不可能含冒號,所以含冒號等於有前綴。做法 1 讓冒號變成合法的名稱字元後,這支函式沒有跟著改,spec 的表格只列了三處 `_KILL_METHOD_OK_RE`。
- 具體例:
  - 輸入:多平台設定,配方 `test: "API: 逾時 顯示重試"`,配方的 `platform` 欄寫 `web`。
  - 預期:跑名稱 `API: 逾時 顯示重試`。
  - 實際:`_kill_method_name` 回 ` 逾時 顯示重試`,過了 `_test_name_ok`,殺傷力配方拿子字串去篩,可能選中別支測試而得到偽證據。
- 影響範圍:file: `scripts/lumos:18311`、`:18494`、`:19556`、`:56147` 都吃 `_kill_method_name` 的結果。
- 佐證:file: `scripts/lumos:18042-18046`。
- 需要補:這支函式要用跟 `resolve_test_refs` 同一套前綴判法,前綴未定義就不當前綴;並補一條多平台下含冒號名稱的 guard kill 條款。

## F4 `_dispositions_split_test` 的冒號切法在單平台和 `resolve_test_refs` 不同
severity: major
blocking: 是——spec 寫切法相同,單平台時不成立,句子名在處置帳一律被擋。

- spec 段落:做法 6 表格代碼審處置帳 `test:<名>` 證據那一列。
- 問題:`resolve_test_refs` 在 `platforms` 為空(單平台)時整串當名字,不管有沒有冒號。`_dispositions_split_test` 只要 `":" in body` 就先切,單平台時回「這個專案沒開多平台…不支援平台前綴」。spec 說冒號前綴的切法跟 `resolve_test_refs` 相同並且只加 `_test_name_ok`,實作者不會去改這個差異。
- 具體例:
  - 輸入:單平台專案,處置帳證據 `test:API: 逾時 顯示重試`。
  - 預期:跟筆記綁定同規則,整串當名稱。
  - 實際:報沒開多平台,拒收。
- 佐證:file: `scripts/lumos:54977-54990`;`resolve_test_refs` 見 `scripts/lumos:6011-6030`。
- 需要補:列出這個差異,並寫明單平台時整串當名稱;加對應條款。

## F5 部分擷取的假證據不會出現,這個保證沒有落實
severity: minor
blocking: 否——最壞是多收幾個不存在的名字,實際跑時會被零支或多支的證據判定接住。

- spec 段落:做法 2、〈舊決策與為何翻案〉理由 2。
- 問題:spec 說新的掃描擷取整個字串字面,不是前半段,但沒要求字面後面必須緊接 `,` 或 `)`。幾種仍會半收或收到不存在的名字:
  - 串接:`it('登入 ' + role, …)`。舊正規式也會收,但舊的只能是識別字;新的會把 `登入 ` 去空白後收成 `登入`。
  - Dart 的 `'$name 失敗'`、`'${x}'` 插值。spec 只排除了 JS 的 `${` 樣板,沒提 Dart 插值。
  - `RegExp.test('…')` 這類成員呼叫:`\btest\(` 會命中 `/\s/.test('a b')`,句子名放開後多收一批不是測試的字串,spec 的假呼叫段只談了字串裡的 `it('…')`。
- 需要補:字面後必須是 `,` 或 `)` 才收;Dart 的 `$` 插值比照 `${` 排除;對 `.test(` 這種被別的物件呼叫的形式加前導限制(如前一字元不是 `.`)。

## F6 Playwright 的 `-g` 與 Vitest 沒有被 spec 的零支判法覆蓋
severity: minor
blocking: 否——spec 的結論(不會誤綠)大致成立,但理由不是它寫的那一條。

- spec 段落:〈實務隱患〉守衛面,跳脫寫錯會選中零支、被既有的跑過的證據判法判成沒證明那一句。
- 問題:`_RAN_EVIDENCE` 沒有 playwright、node-vitest、dart,這三家沒有跑過的證據,零支靠兩樣東西接住:測試工具本身回非零(Playwright 找不到回 1),或過濾探針(Vitest `-t` 不命中通常回 0,探針會判整個指令不可信)。這和 spec 寫的理由不同,驗收條款也無法對這三家造零支判沒證明。
- ⚠ 我沒能在本機實測 Playwright:它的 `--grep` 內部我記得是大小寫不分的 `gi` 旗標,且會把 `/…/g` 形式的字串當成正規式字面。若屬實,跳脫字元集(沒跳 `/`)與整串精確比對的語意會有落差,交編排者查文件確認。

## F7 反引號名稱的前後處理
severity: minor
blocking: 否——只影響標題頭尾本來就有反引號的少數句子名。

- spec 段落:做法 1 的 Kotlin 反引號先拆殼再判。
- 問題:`discover_test_methods` 對每個名稱做 `.strip("`")`,`_kill_norm_method` 與 `_test_names_of` 也會拆頭尾反引號。標題恰好以反引號開頭或結尾(如 `` `useFoo` 回傳 x ``)時,索引裡那個名字被剝掉,綁定名卻留著(或兩邊拆的深度不一致),比對不上。
- 佐證:file: `scripts/lumos:6296`。
- 需要補:拆殼只在 Kotlin 反引號 profile 做,JS 的名字不該動。

## 其他節
- 〈舊決策與為何翻案〉、做法 5(多平台 `method_regex`)、做法 7(文件與舊筆記)、〈回退〉:已讀,無 finding。
- 做法 1 的 `_test_names_of` 與 `resolve_test_refs` 切法對齊:已讀,現況描述與程式相符(全形逗號與冒號確實被切),無 finding。
- 做法 3(`_clause_check` 的 ⚠ 與列表)、驗收條款 S1 到 S28 的可寫性:已讀,無 finding。
- 歸檔與 `guard trace` 的邊界規則:已讀。中文不屬 ASCII 的 `\w`,現行 `\b` 對中文頭尾確實永遠配不到,spec 的診斷成立。

最嚴重 severity:major;blocking 共 4 條(F1、F2、F3、F4)。
