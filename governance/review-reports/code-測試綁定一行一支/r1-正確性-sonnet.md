severity: major

我逐一檢視了 diff 中 scripts/lumos 的每個 hunk,並用 `/tmp/lumos-seat-work/code-測試綁定一行一支/正確性-sonnet/p.py` 與 `q.py` 載入 repo 版本做了探針實驗。`python3.14 scripts/test_lumos.py -k note_wording` 為 38 passed、0 failed。

### F1 `[test:` 前置檢查比 slot_parse 窄,大小寫與全形冒號的寫法整條漏掉
severity: major
blocking: 否 — 只提醒不擋,但這是新規則的主要漏洞:合法寫法完全不出綁定提醒。
引句:「    at = tail.find("[test:")」
失敗場景:`slot_parse` 的文件寫明「鍵名英文不分大小寫、冒號收全形」。實測 `slot_parse("a [Test:t_a,t_b]")` 與 `slot_parse("a [test：t_a,t_b]")` 都解出 `['t_a','t_b']`,同一行的 `[TEST:t_a,t_b]` 也一樣。但 `_ns_wd_binding_hit` 先用字面 `find("[test:")` 過濾,三種寫法全部回 None,不會有提醒。同一批資料走 `_test_names_of` 的路徑(doctor S20、note-shape 的其他檢查)會認得它們,所以「同一行綁兩支」的判準在兩處不一致。
最小重現:`h("a [Test:t_a,t_b]")` 回 None,而 `m._test_names_of(m.slot_parse("a [Test:t_a,t_b]"))` 回 `(['t_a','t_b'], False)`。
佐證行:`scripts/lumos:31503`

### F2 行內程式碼遮罩把 `[test:]` 值裡的反引號名稱換成 NUL,提醒會印出亂碼,且不同名稱會被誤併
severity: major
blocking: 否 — 只提醒不擋,但輸出直接錯,而且有誤漏報。
引句:「    names, _empty = _test_names_of(slot_parse(tail))」
失敗場景:`masked` 是 `_inline_visible_mask` 的結果,反引號 span(含 `[test:` 值裡包名稱的反引號)已換成 `\0`。`_test_names_of` 要去掉包名稱的反引號,但這時反引號已不在,拿到的是一串 NUL。
- 輸入 `a [test:`t_a`,t_b]`:名稱清單為 `['\x00\x00\x00\x00\x00','t_b']`。提醒會印出「這行綁了 2 支(\0\0\0\0\0、t_b)」,終端上看不到名稱。
- 輸入 `a [test:`k a`,`k b`]`(Kotlin 反引號測試名,`_test_names_of` 自己註解說要支援):兩個名稱都變成同長度的 `\0\0\0`,`dict.fromkeys` 去重後剩 1 支,綁定提醒漏報。
- 輸入 `a [test:`t_a`,t_a]`(同名一支反引號一支不反引號):被誤算成 2 支。
修法方向:名稱要從原行(未遮罩)取,遮罩只拿來決定哪些區段看得見。
佐證行:`scripts/lumos:31503`,遮罩來源 `scripts/lumos:389`(`_inline_blank`)

### F3 名稱清單不設上限,一行寫很多支時會洗版
severity: minor
blocking: 否 — 只是輸出品質。
引句:「f"      → 這行綁了 {len(tag)} 支({'、'.join(tag)}):拆成一支一行,每行寫那支測試守的是哪一點"」
失敗場景:一行 `[test:]` 寫 203 支名稱時,探針的 `h()` 回傳的清單有 203 項,印出時全部用「、」接成一行。單行對應多行提醒時,一次提交就可能刷出好幾 KB。預設只需要印前幾支再加「等共 N 支」。
佐證行:`scripts/lumos:31571`

### F4 同一行數量或位置先命中時,綁定提醒被吞掉而且之後不會再出
severity: minor
blocking: 否 — 作者說明是刻意的取捨,但文案會讓人誤會。
引句:「不是在數那個清單、不是在指清單裡的項目、或那幾支測試確實守同一件事,就不用理;這次提交之後這幾行不會再提醒。」
失敗場景:一行同時有數量(或位置)命中與 `[test:a,b]` 時,`_ns_wd_line_hit` 在 `for` 迴圈內先 return,不會走到 `_ns_wd_binding_hit`。使用者照提醒修好數量後,這行成了舊行,綁定提醒永遠不出。文案「這幾行不會再提醒」只是在說這幾行,沒有說明其中可能有一條規則被吞,使用者會以為這行沒綁定問題。hinted 帳的 `rules` 也只記先命中的那條。
佐證行:`scripts/lumos:31495`

### F5 新規則的例外隔離沒有測試
severity: minor
blocking: 否 — 現有的外層 try/except 能接住,但沒有釘子。
引句:「def t_note_wording_binding_quiet():」
失敗場景:`_ns_wd_binding_hit` 如果丟例外(`slot_parse` 遇到怪輸入),會被 `_ns_wording_collect` 的 try 接住,`box["items"]=[]`,結果是「這次提交的所有寫法提醒(含數量、位置)都被丟掉」並印一句沒跑完。這個行為和 `_ns_wording_emit` 的註解一致,否定現況句與筆記前綴提醒不受影響,rc 也不變。但 `t_note_wording_isolated` 沒有針對 `slot_parse` 或 `_test_names_of` 注入例外的案例。我用 `\0`、未閉合方括號、大量名稱探測,沒找到會丟例外的輸入,所以風險只在測試覆蓋。
佐證行:`scripts/lumos:31561`

### 其餘審查項目(無需報 finding)
- **舊行尾補括號**:`cut` 之後的 tail 若切在 `[test:` 中間(例如舊行 `x [test:t_a`、新行 `x [test:t_a,t_b]`),tail 為 `,t_b]`,不含 `[test:`,回 None,不丟例外。補的括號裡沒有完整方括號時同樣回 None。
- **新寫括號裡的綁定**:舊行 `甲 [test:t_a]` 補上 `(另 [test:t_b,t_c])`,仍會正確提醒 `t_b、t_c`。
- **空 `[test:]`、`[test-gone:]` 混寫、佔位名稱**:待補、todo 都被過濾。`[test:t_a][test-gone:t_b,t_c]` 正確回 None。
- **平台前綴**:`ios:t_a` 與 `android:t_a` 視為兩支,`ios:t_a` 與 `t_a` 也視為兩支。這是 `_test_names_of` 的既有行為,不算本 diff 的問題。
- **hinted 帳多一個 `binding`**:`scripts/lumos` 裡沒有讀 wording 帳的 `rules` 的程式(`32112` 行的 `rules` 是另一個結構),新舊互讀不會出錯。
- **pitfalls manifest**:`/tmp/lumos-seat-work/code-測試綁定一行一支/manifest.json` 共 2693 條 claims,以訊息內容與函式名搜尋,沒有任何一條落在 diff 新增行上。
- **圖譜鏡頭**:固定席節點的 INVARIANT(search 排除 superseded、guard kill rc 優先序等)與本 diff 無牽連。家筆記 `Systems/筆記內容閘.md` 有同步改動。

總結:共 5 條,最高 major
