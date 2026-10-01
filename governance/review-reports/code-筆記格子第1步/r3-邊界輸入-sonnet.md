severity: minor

審查範圍:第 2 輪之後的修正差異(`/tmp/code1-r3.patch`)。鏡頭是邊界與輸入。我把 `_ns_slot_key`、`_ns_text_key`、`_ns_summary_logical`、`_ns_slot_line_problems`、`_ns_slots_format` 載進 python3.14,用怪輸入直接跑,沒有改 repo。腳本在 `/tmp/r3b_t.py`、`/tmp/r3b_t2.py`、`/tmp/r3b_t3.py`。沒有找到會做出錯行為的 blocking 問題,下面是 5 條 minor。

**R3B1 只放連結的行夾英文連接詞或符號時,兩邊的鍵都縮成同一個短詞,全新的連結行被當成舊行放過**
引句:「if "[[" in core and not _NS_PTR_SEP_RE.sub("", _NS_SLOT_LINK_RE.sub("", core)):」
severity: minor
blocking: 否 — 要上一版剛好有同樣形狀的怪行才會漏,漏掉的是缺格新行,不會誤擋。
- 「只放連結」的判斷只認 `見→,，、。;；與和及|｜` 和空白。連結之間夾 `and`、`+` 這類字,就不算只放連結,改走文字鍵。文字鍵去掉連結後只剩 `and` 或 `+`。
- 重現:`P("DEP:[[c]] and [[d]]", ["DEP:[[x]] and [[y]]"])` 回 `[]`,等於不擋。
- 對照:上一版是空的時候,同一行回 `缺 [來源:]、[confirmed:]`,有擋。`+` 的情況同樣放過。
- 影響:只要上一版(HEAD、起點版本或被刪的行)有一條這種怪行,之後任何連到別的節點、同形狀的新 DEP/FLOW 行都不擋。

**R3B2 文字鍵把連結整個去掉,混了文字的行只換連結目標也算舊行**
引句:「t = _NS_SLOT_PUNCT_RE.sub(" ", _NS_SLOT_LINK_RE.sub(" ", core))」
severity: minor
blocking: 否 — 漏的是缺格新行,而且混文字行換連結目標算不算新寫,計劃沒明講。
- 計劃〈擋〉只說「只放連結的 DEP/FLOW」換連結算新寫。diff 的註解也寫「換了連結通常是換了指的對象」。
- 但混了文字的行不受這條管。重現:`P("WHY:依賴 [[b]] 的行為", ["WHY:依賴 [[a]] 的行為"])` 回 `[]`。
- 這一行等於指向另一個節點,卻不必補 `[出處:]`、`[因:]`。
- 要不要把這個放行寫進計劃天花板第 7 條,請作者決定。

**R3B3 「空白跟中日韓字相鄰就去掉」實際寫成「跟任何非 ASCII 字元相鄰」**
引句:「return re.sub(r"(?<=[^\x00-\x7f]) | (?=[^\x00-\x7f])", "", t)」
severity: minor
blocking: 否 — 只影響帶重音字母、表情符號、全形引號的英文句,而且是放過新寫、不是誤擋。
- 計劃和 docstring 都寫「空白跟中日韓字相鄰」,程式的字元類別是 `[^\x00-\x7f]`。
- 跑出來:`P("WHY:café au", ["WHY:caféau"])` 回 `[]`。這兩句的文字鍵都是 `caféau`。
- 同樣的道理,`😀 hi` 和 `😀hi` 撞成同一個鍵,不換行空白(NBSP)和全形空白也都被吃掉。
- 這跟 r2 邊界席說的「`a bc` 與 `ab c` 不能撞」是同一條原則。ASCII 英文已經守住了,帶重音的英文沒守住。
- 問題在字元類別寫得太寬。要嘛收窄到中日韓區段,要嘛把計劃的措辭改成「非 ASCII」。
- 日韓文、中英混排、數字加單位都照預期:`取 5 公斤` 和 `取5公斤` 同鍵,`limit 12 ms` 和 `limit 1 2ms` 不同鍵。

**R3B4 續行用「字元數」比縮排,tab 縮排的續行接不回去,欄位寫在續行會被誤擋**
引句:「elif s and last is not None and ind > last_ind:」
severity: minor
blocking: 否 — 誤擋會被當場看到,有單次跳過和 warn 可用;檔案要有 tab 縮排的續行才會觸發。
- `ind` 是 `len(ln)-len(ln.lstrip())`,一個 tab 算 1 格。前綴行是兩格空白縮排時,tab 開頭的續行 `ind=1`,不大於 2,所以不被認成續行。
- 重現:
  ```
  summary: |
    WHY:新句
  <TAB>[出處:2026-10-01 對話] [因:原因]
  ```
  `_ns_summary_logical` 回 `{4:'WHY:新句'}`,`cont` 是空的。
- 結果:`_ns_slot_line_problems` 回 `缺 [出處:]、[因:]`,但欄位其實寫在續行上。
- 只改 tab 續行時,`i not in logical` 會讓這一行被整個略過,那一行完全沒被查。
- 補充:CRLF 和「續行在摘要最後一行」我都跑過,結果正確(`strip()` 吃掉 `\r`,最後一行的續行也接得回去)。

**R3B5 擋下訊息的 SEE 範本在 120 字截斷,長的只放連結行會被切在連結中間**
引句:「out.append("      範本:" + tpl.format(core=_esc_clean(core, 120) or "<一句話>"))」
severity: minor
blocking: 否 — 範本只是要人改的示範,錯在複製貼上會得到壞連結。
- SEE 範本的核心一句就是整排連結,超過 120 字會被截成 `…[[Systems/很長的節點…`。
- 重現:8 個長節點名的 `DEP:` 行,印出的範本末尾是 `[[Systems/很長的節點…`。
- 這個範本是要人直接複製的。連結被切斷後,不是合法的 `[[…]]`。
- 影響只限核心超過 120 字的情況。核心一句為空時範本顯示 `<一句話>`,正常。其他前綴的範本截斷沒有問題。

**圖譜鏡頭(固定席必答)**
- `lumos impact --diff` 列出的固定席,主要是 `Systems/lumos-cli-read.md`、`Systems/pitfalls-code-loop.md`、`Systems/lumos-cli-lifecycle.md`、`Systems/測試假綠形態.md`、`Systems/bound-tests-gate.md`,加上 `Projects/筆記格子寫法與過期檢查_計劃.md`。
- 我從邊界輸入角度判斷,這批修正沒有違反這些合約,理由有三:
  - 合併中、單次跳過、算格子失敗,三條路徑都保持 fail-open。我讀了 `cmd_note_shape` 和 `_ns_skip_slot_extra`,跳過前的計算包在 `try` 裡,合併中不記帳。
  - 計劃寫「掛鉤範本這次不帶 `--slots`」,diff 沒有碰掛鉤範本。
  - 計劃與實作對得上的有三處:`"被取代" in x[0]` 的比對、治理帳 `check` 欄位、路徑經 `_esc_clean` 清過控制字元。我沒找到對不上的地方。
- 計劃只有一處措辭與程式不合,就是 R3B3 的「中日韓」。

最高嚴重度 minor,blocking 0 條
