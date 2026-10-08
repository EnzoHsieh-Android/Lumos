severity: major

審查範圍:`scripts/lumos` 的 `_ns_text_key`、`_ns_slot_key`、`_ns_old_keys`、`_ns_is_old`、`_ns_slot_line_problems`、`_ns_slots_violations`(cont 回頭查整條)、`_note_shape_report`(check 欄)。每條都在 `rw` 副本上用 `_slot_try` 實跑過。

**R3C1 只放連結的舊 DEP 後面接續行,新內容整段躲過格子檢查**
severity: major
blocking: 是 — 這正是 r2 通才席那個洞(舊句後接續行躲檢查),修法只堵了文字鍵,只放連結的鍵沒堵。
引句:「is_old, old_sup = _ns_is_old(_ns_slot_key(head), old, "phys")」
- 原因:`_ns_old_keys` 把只放連結的舊行全收進同一個 `old["ptr"]`,沒分 text/phys 欄(`scripts/lumos:26942`)。`_ns_is_old` 遇到 ptr 鍵就不看 `bucket` 參數,直接查 `old["ptr"]`(`scripts/lumos:26955`)。所以 HEAD 版本的舊行也算在「第一個實體行」的比對裡,「第一行對上只比 phys」對 ptr 鍵不成立。
- 重現:HEAD 有 `DEP:[[Systems/甲]]`,暫存改成
  ```
  DEP:[[Systems/甲]]
    後面新接的一大段沒有來源的敘述
  ```
  `_slot_try(..., root=root)` 回 `A rc 0`,沒擋。對照 WHY 版(`WHY:舊的一句話` 後接續行)回 `B rc 1`,有擋。
- 函式層重現:`_ns_slot_line_problems("DEP: [[Systems/甲]] 後面新接…", old, True, head="DEP: [[Systems/甲]]")` 回 `[]`。不傳 head 時回 `缺 [來源:]、[confirmed:]`。
- 修法方向:`ptr` 也依來源分欄(logical 一欄、phys 一欄),head 比對只查 phys 欄。
- 現有 ⑦ 測試只釘 WHY,沒釘 DEP,所以這個洞測試抓不到。

**R3C2 只放連結的舊 DEP 補別名文字也算舊行**
severity: minor
blocking: 否 — 這道目前只在「看到 --slots 的掛鉤」才跑,而掛鉤範本刻意不帶 --slots;但同樣是只改連結就放行的洞。
引句:「if "[[" in core and not _NS_PTR_SEP_RE.sub("", _NS_SLOT_LINK_RE.sub("", core)):」
- `_NS_SLOT_LINK_RE` 認別名與段落,因此 `DEP:[[Systems/甲|…一串現況描述…]]` 的 ptr 鍵還是 `{甲}`,`old <= new` 成立,算舊行。
- 實跑:這個例子被另一條形狀規則(帶別名的 DEP 要寫來源)擋下 `rc 1`,所以目前格子層面沒漏出去。兩條規則一旦脫鉤(形狀規則調整或 warn),格子這一層就不擋。
- 第一輪修法「從寬認別名」只該用在舊行那一側。新行那一側仍應拿嚴格版 `_NS_POINTER_ONLY_RE` 判。

**R3C3 只改續行會回頭查整條:舊的缺格條目改一個字就被擋**
severity: minor
blocking: 否 — 這是設計選擇(r2 通才席),行為與單行改字一致。
引句:「i = cont.get(i0, i0)        # 只改了續行:回頭查它所屬的整條」
- 實測 `WHY:長句前半\n  第二行\n  第三行`(無格子,已在 HEAD),只把第三行改成「第三行改」,`rc 1` 缺 [出處:]、[因:]。
- 這是沒有格子的舊條目被修錯字,新增一個要擋的場景;跟單行舊句改字被擋同一標準。
- 已驗沒問題:
  - 多條、連續續行用 `seen` 去重,同一條只報一次。
  - 只補欄位在第三行不擋。
  - 刪一條續行加新續行、有格子的條目改續行都不擋。
  - 中文重折行與英文重折行(`alpha beta gamma\n  delta` → `alpha beta\n  gamma delta`)不擋。
  - 只刪續行沒有新增行就不進檢查。這跟「只改欄位的舊行不算新寫」同一標準,不報。

**R3C4 文字鍵的邊界(已驗,判不是問題)**
severity: clean
blocking: 否 — 沒找到具體誤擋或誤放的場景。
- `_ns_text_key` 的幾組對照:
  - `a bc` 與 `ab c` 不同。
  - `中 文` 與 `中文` 相同,`A和B` 與 `AB` 不同,`A 和 B` 與 `A和B` 相同。
  - `版本 v2 規則` 與 `版本v2規則` 相同。
- 只有半形與全形括號、連字號 `foo-bar` 對 `foo bar`、`x/y` 對 `x y` 這類不在去掉清單的符號,改寫算新寫。這是保守方向,不會誤放。
- 文字鍵把連結整個去掉,所以 `[[A]]` 換成 `[[B]]` 的文字行算舊行。計劃說只放連結的行才要比連結,文字行換連結不算新寫,與設計一致。

**R3C5 治理帳 check 欄**
severity: clean
blocking: 否 — 兩種組合都寫對了。
- `kw` 在 `sviol` 為真時,`check` 是 `slots`(只有格子違規)或 `shape+slots`(兩種都有)。
- `check` 欄位型別為字串。`scripts/lumos:7709` 的去重鍵把 `check` 算進去,不衝突。
- 全 repo 沒有讀者依賴 `check == "slots"` 來篩選。`blocked` 與 `warned` 兩條路徑都用同一個 `kw`。

**圖譜鏡頭**
- 這批改的是 `scripts/lumos` 的摘要格子比對與提交閘,不是業務規則。我只讀了 diff 和計劃節點〈擋〉〈回退〉的描述,沒另外跑 `lumos impact`。
- 未見與計劃合約衝突的改動,除了 R3C1:計劃寫「新寫的摘要行」要查格子,而 DEP 加續行這個洞讓新內容被當舊行。
- 掛鉤範本不帶 `--slots`,所以 R3C1 目前只影響已手動帶 `--slots` 的環境。開擋前須先修。

最高嚴重度 major,blocking 1 條
