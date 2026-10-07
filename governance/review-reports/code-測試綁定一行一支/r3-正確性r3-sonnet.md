severity: minor

我查了 repair(原問題有沒有修好)和 preserve(原本正確的行為有沒有被改壞)兩類選例。結論是 repair 成立,preserve 只差建議句尾。另有一條原有漏查的 minor。

我在 `/tmp/lumos-seat-work/code-測試綁定一行一支/正確性r3-sonnet/` 下分別 clone 了修前 590dfeac 與修後 1fc27e38。我直接呼叫 `_ns_wd_binding_hit`,兩版吃同樣的輸入;修前版吃 `_inline_blank(ln,q)` 遮過的行,修後版吃原行加 quotes。

### F1 欄位值裡有一段引號跨過逗號時,綁定提醒會把引號內的字當成多支名稱
severity: minor
blocking: 否 — 只是提醒,不影響回傳碼;要寫出這種值才會碰到,實際上很少見。
引句:「and not any(nm.startswith(qa) and nm.endswith(qb) and len(nm) > 1 for qa, qb in _NS_NEG_QUOTES)))」
失敗場景:
- 輸入是 `a [test:t_a,「t_b,t_c」]`。`_test_names_of` 先以逗號切開,得到 `t_a`、`「t_b`、`t_c」`。
- 後兩個名稱各自只有開頭或只有結尾的引號,過不了「整個被引號包住」的排除條件。
- 結果印出「這行綁了 3 支(t_a、「t_b、t_c」)」。引號那一段是在舉例,不該算成名稱。
- 修後版的建議句語意沒壞,但名稱帶著殘缺的引號。
- 修前版對同一行印出「2 支(t_a、\x00…)」,同樣不對。
歸因:有證據的原有漏查。修前版就算錯,修補把亂碼換成殘缺引號,沒有變差也沒有變好。
佐證行:兩版查證用 `python3.14 -I /tmp/lumos-seat-work/code-測試綁定一行一支/正確性r3-sonnet/t.py`(修後)與 `tb.py`(修前),結果如上。程式在 `scripts/lumos:31506`。

### 已驗主張與證據

**① 原問題的修復效果(repair)**
- 輸入 `a [test:t_a,「x」]`:修前印「2 支(t_a、\x00\x00\x00)」,修後回 None。
- 輸入 `x [test:t_a,t_b,"t_c"]`:修前印「3 支(t_a、t_b、\x00…)」,修後印「2 支(t_a、t_b)」。
- 測試 `t_note_wording_binding_quiet` 的 J(`[test:t_one,「x」]`)與 `t_note_wording_binding_hint` 的 ⑨,都對得上上面的行為。
- 我在 clone 裡跑 `python3.14 scripts/test_lumos.py -k note_wording`,結果 45 passed、0 failed。

**preserve(沒被改壞)**
- 我跑了 15 個既有輸入,包括大小寫、全形冒號、反引號名稱、`t_a[0]`、`[ test : t_a , t_b ]`、平台前綴、`[test:]` 空欄位、`test-gone` 混入、連續兩個欄位、行內程式碼裡的欄位。
- 修前與修後比對,命中位置、有沒有提醒、名稱數量全部相同。唯一差別是建議句尾多了「:拆成一支一行…」,這是預期內的改動。
- 引號範圍涵蓋整個欄位時(`說「舉例 [test:t_a,t_b]」 然後 [test:t_c]`)仍不提醒,另外那個欄位照算。

**② 座標一致性與其他呼叫路徑**
- `_slot_scan(raw[cut:])` 吐的座標是 cut 之後那一段的相對座標。程式用 `cut + a` 與 quotes 比對,quotes 來自 `_inline_visible_mask(ln)` 這份等長遮罩,所以座標是對的。
- 我驗了兩個舊行補括號的案例:
  - `舊句「x」 [test:t_a](更正:[test:t_c,t_d])`,cut 在舊欄位之後,位置回 20,對得上原行。
  - 一對引號橫跨 cut(`舊句「x [test:t_a](更正:[test:t_c,t_d]) y」`),整段不算,符合「整行成對引號」的語意。
- 值沒收尾的欄位(`a [test:t_a,t_b`、`[test:t_a] [test:t_b,`):`_slot_scan` 吐出帶錯誤的欄位後停止,`_test_names_of` 略過帶錯誤的欄位,回 None,不丟例外。
- 數量與位置兩條的建議句改放第三欄後,emit 的字串與修前逐字相同。count 是 `掛上 {c[1]},清單改了 lumos drift scan 會列出來`,position 是 `改成引那一項…`,中間的箭頭與縮排沒變。
- 名稱超過 5 支時的字樣改成「 等 N 支」,與 `scripts/lumos:7754`、`scripts/lumos:36429` 既有寫法一致。

**③ 新發現案例(F1)的修前與修後**
- 修前:`a [test:t_a,「t_b,t_c」]` 印「2 支(t_a、\x00\x00…)」。
- 修後:同一行印「3 支(t_a、「t_b、t_c」)」。

**④ 只提醒不擋的隔離**
- `_ns_wording_collect` 的 try 會把例外收進 `box["error"]`,並清空 `box["items"]`。
- `_ns_wording_emit` 整段包在 try 裡,出錯只印一句,不改回傳碼。
- 測試 `t_note_wording_isolated` 用 `_neg_inproc(root, _ns_wd_binding_hit=_boom)` 注入例外,該測試通過。
- 綁定規則丟例外時,數量與位置的結果會跟著清空,因為是同一個收集箱。這是既有設計,測試有涵蓋。
- `_slot_scan` 與 `_test_names_of` 本身沒有會丟例外的路徑。

**pitfalls manifest 與圖譜鏡頭**
- 我沒找到落在新增行上的 manifest 項目。
- 本改動只動 `scripts/lumos` 與 `scripts/test_lumos.py`,固定席列出的合約沒有被改到的跡象。

**未驗範圍**
- 我沒有跑全套測試,也沒有做大型輸入的效能量測。新增的逐行掃描只對含 `[test:` 的行做一次 `_slot_scan`,複雜度是線性。
- 我沒有驗 hinted 帳實際寫入的欄位內容,只讀了程式。`rules` 與 `lines` 的組法沒有被這次修補改動。

總結:共 1 條,最高 minor
