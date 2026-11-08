severity: major

先說對照基準:被審的修補差異動到 check.py 的 `pending_problems` 與 `stats_problems` 這一組新函式。我把它對到同檔鄰居 `catalog_problems`、`main_rows`、`catalog_unverified`、`template_problems`、`_abbr_table`。repo 的 check.py 已含這段修補,下面行號取自現行檔案。

## 問 1:分層與依賴方向

大致對齊,沒有跨層直呼。

- **位置**:新函式緊接在 `catalog_problems` 後面、情境樣本自測區之前。`catalog_problems` 在尾端用 `problems += pending_problems(text, rows) + stats_problems(text, rows, rules)` 呼叫它們,跟既有的 `problems += template_problems(rows)` 同一個接法。
  - 引句:「+    problems += pending_problems(text, rows) + stats_problems(text, rows, rules)」
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:403-404`
- **讀主表**:不另讀,直接吃 `catalog_problems` 用 `main_rows` 讀好的 `rows`,切欄用 `_cells`,認列用 `_MAIN_ROW_RE`,查證格式用 `_VERIFIED_RE`。這跟 `template_problems(rows)` 一致。
  - 引句:「+    return {m.group(1): _cells(ln) for ln in sec.splitlines() for m in [_MAIN_ROW_RE.match(ln)] if m}」
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:302-304`
- **規則陣列**:新函式讀 `rules` 的 `r.get("dir")`,跟 `catalog_problems` 內 `r.get("dir")` 的用法相同,`rules` 為 None 時略過規則包那幾項。這部分對齊。
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:376`
- **參數預設**:`template_problems(rows=None)` 預設自己呼叫 `main_rows()`,新函式的 `rows` 是必填。這不算結構差異。

## 問 2:命名與錯誤處理

- **函式命名**:`pending_problems`、`stats_problems` 對上 `catalog_problems`、`template_problems`、`message_problems`。內部輔助用 `_pending_table`、`_pending_need`、`_stats_expected` 加底線前綴,跟 `_abbr_table`、`_main_names` 一致。
- **回傳形狀**:是 `(編號, 訊息)` 元組清單,跟鄰居一樣。
- **docstring 與註解**:中文,並用 `[[Projects/…]]` 指到計劃,跟 `catalog_unverified` 同一種寫法。
- **差異一**:切節方式不同。鄰居 `_abbr_table` 的節尾是「下一個 `\n## `」,新的 `_pending_table` 寫死用 `\n## 統計` 當節尾。`catalog_problems` 自己對〈待查證〉的邊界只管到〈情境決策表〉之前。
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:282`
- **差異二**:`_abbr_table` 讀列時有 `len(c) >= 2` 的防呆,`main_rows` 有欄數檢查與重複編號回報。`_pending_table` 的 `pc[1]` 沒有防呆(`pc[2]` 倒是有防),重複編號只靜默收成一筆。
  - 引句:「+        for want, cell, what in ((code, pc[1], "待查的規則代號"), (src, pc[2] if len(pc) > 2 else "", "待核對的來源")):」
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:288-289`
  - 同一族還有一處:`pending_problems` 的 `pend is None` 分支是死碼。`catalog_problems` 在 `check.py:344-346` 沒找到〈待查證〉就已先回傳,走不到這裡。
- **差異三**:`stats_problems` 回報的占位編號是 `<統計>`,鄰居的占位編號都是 `<catalog>` 或 `<templates>`,是英文標籤。

## 問 3:第二種做法

有一處常數重複,另一處是有註明理由的重複。

- **重複常數**:新常數 `_STAT_TOPICS` 又寫了一份九個主題前綴清單,鄰居 `_MAIN_ROW_RE` 的正規式裡已經有同一份清單。現在新增第十個主題,只改 `_MAIN_ROW_RE`,〈統計〉的各主題列數就不會被核對,也不會報錯。
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:98`
- **重複字樣**:`_PENDING_SRC` 把 `_WEAK_SRC` 的前兩個字樣用字面再抄一份。註解有講明刻意排除「無網址」,這點有理由。但同一組字樣現在是兩處字面維護,可以用 `_WEAK_SRC[:2]` 派生,或在鄰居旁加註互相指認。
  - 對照 file: `configs/ast-grep/kotlin-android/check.py:104`
- **重數與讀表**:其他沒有第二種做法。「逐列查證」的重數用的是同一個 `_VERIFIED_RE`,不是另寫一套判斷。用正規式讀〈統計〉手寫數字是鄰居沒有的新讀法,但鄰居沒有〈統計〉節的讀法,所以不算第二種做法。
- **規則與樣本**:前兩輪已看過,修補差異沒有動到,不再審。

### 發現

1. 另寫一份主題前綴常數,鄰居 `_MAIN_ROW_RE` 已有同一份清單。
   引句:「+_STAT_TOPICS = ("API", "FLOW", "STATE", "CO", "UI", "ARCH", "DATA", "TEST", "PERF")」
severity: major
   blocking: 是
   不整合的後果:主題清單從一處變兩處,新增主題時只改其中一處不會有任何檢查報錯。
   建議:從 `main_rows` 讀到的 `rows` 前綴派生。若要連零列主題都核對,就從 `_MAIN_ROW_RE.pattern` 取出前綴,避免兩份手抄。

2. 〈待查證〉的切節方式跟鄰居 `_abbr_table` 不同,讀列也少了防呆、重複編號回報。
   引句:「+    i, j = text.find("\n## 待查證"), text.find("\n## 統計")」
severity: minor
   blocking: 否
   建議:節尾改成「下一個 `\n## `」,同 `_abbr_table`。對 `pc[1]` 補 `len(c)` 防呆,重複編號也報出來。`pending is None` 那個走不到的分支可以拿掉。

3. `_PENDING_SRC` 用字面重抄 `_WEAK_SRC` 的兩個字樣。
   引句:「+_PENDING_SRC = ("未開頁核對", "搜尋摘要")」
severity: minor
   blocking: 否
   建議:改成 `_WEAK_SRC[:2]` 派生,或加註明互相指認。

4. 占位編號 `<統計>` 的形狀,鄰居用的是 `<catalog>`、`<templates>`。
   引句:「+            out.append(("<統計>", f"{label} 寫 {got},重數是 {n}"))」
severity: minor
   blocking: 否
   建議:改成 `<catalog>`,把標籤寫進訊息;或照 `<統計>` 的寫法,把 `<catalog>` 一類也改成中文(後者動到鄰居,不建議)。

不對齊共 4 條,其中 major 1 條。
