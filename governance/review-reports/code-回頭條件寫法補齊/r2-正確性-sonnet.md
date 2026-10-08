severity: minor

審查範圍:/tmp/code-revA-r2.patch 全部 hunk(計劃、scripts/lumos、scripts/test_lumos.py)。實跑:`python3.14 scripts/test_lumos.py -k revisit_misplaced / revisit_closed / doctor_revisit / note_shape_ledger` 在審查用 clone 上共 60 支全過(23/17/18/2);另用 /tmp/codeRevA/r2probe.py 逐例呼叫真函式。

**C1 落單引號修法只查「後面有沒有收引號字元」,不查「配不配得上」,同一行後面另有一對真引號時落單的 `5"` 仍把句中 REVISIT 藏起來**
severity: minor
blocking: 否 — 只漏擋一種窄情境(同一行先有落單半形引號、後面又有一對真引號),漏的是提示不是資料損壞,且 doctor 存量清單同樣漏、無不可逆後果
引句:「last = {q: probe.rfind(q) for q in [*_REVISIT_QUOTES.values(), '"']}」

1. 輸入:`長 5" 的管子。REVISIT:2026-10-05 x 他說 "好" 然後`(一行,寫在正文)。
2. 走到 `_revisit_quote_states`:掃到 REVISIT 位置之前出現一次 `"`(5" 的那個),`straight` 為 True;`last['"']` 是行尾 `"好"` 那組的位置,大於命中位置,所以 `straight and last['"'] > i` 成立,判成「在一對引號裡面」。
3. 壞在哪:修法用「後面有任何一個同種引號字元」代替「後面有配對的收引號」。半形 `"` 開閉同形,落單的 `5"` 加上後面一對真引號,奇偶就被錯位,句中 REVISIT 被當成範例放過。這正是上輪發現(落單的 `5"`)的同一個輸入形狀加上一點後文,修法只補到「後面完全沒有 `"`」的版本。
4. 重現(實測輸出):
   `python3.14 /tmp/codeRevA/r2probe.py` 第一例 `長 5" 的管子。REVISIT:2026-10-05 x 他說 "好" 然後` → `_revisit_misplaced` 回 `[]`(應為一處)。對照:同一句拿掉後面的 `"好"` 就回非空(測試 r1 ① 的情境,所以現有測試抓不到)。
5. 影響:提交時 `_ns_revisit_violations` 不報「回頭條件寫在句中」、doctor Z 段(`_revisit_misplaced_lines`)也列不到,這條回頭條件仍是永遠不評估的死條件。計劃〈天花板〉1 只寫「刻意用引號框住的認不到」,沒涵蓋落單引號被後面真引號吃掉的情形。

沒問題的項目(逐項走過,判斷如下)

- `_ns_revisit_violations` 的 `kind == "bad"` 由 return 改成 append:`bad` 行接著會跑 `_revisit_misplaced`,`_revisit_split` 回 `bad`(不是 None)時 head 取行首,行首那一處不被當句中;實測 `REVISIT: 2026-10-05 x`(冒號後空白,判成 bad)單獨一行回 `[]`,沒有對行首自己重報。`REVISIT:2026-9-1 x;REVISIT:2026-10-05 y` 一次報「格式不合」加「寫在句中」兩條,與測試 ④ 宣稱一致。
- 結案文法範圍縮到 `kind in ("date","cond")` 且只在 body/summary 且非表格:`_ns_revisit_violations` 的 `elif` 分支(表格、開頭欄位其他欄)不再進結案檢查;`_revisit_dead_place` 的條件與原本 `elif _PROBE_ANY_RE.search(probe)` 在「非 body/summary 或表格」這個前提下等價(`elif` 本來就只在那個前提下才到),三個呼叫端行為沒變。測試 ⑤⑥ 前後對照成立。
- `_probe_lines` 的 dead 判定換成 `_revisit_dead_place(probe, regs[i-1])`:前面的 `if regs[i-1] in ("body","summary") and not table:` 已 `continue`,所以走到這裡一定滿足「表格或非 body/summary」,結果與原式相同。
- `_revisit_misplaced_lines` 的跳過條件換成 `_revisit_dead_place` 與原式逐字等價。
- Z 段文案「處」改「行」:`_revisit_misplaced_lines` 每行最多回一筆 `(no, ln)`,數的確實是行;「寫在不評估的地方 N 處」那一段維持原樣,測試 ③ 綁住。
- 引號狀態的其他輸入:`「a REVISIT:… x」 再 「沒收 REVISIT:… y` 只報第二處(正確);`他說「好」。REVISIT:…` 報(正確);全形成對的 `『a「b REVISIT:… x』 end 」` 不報(合理)。`last` 每次呼叫 `rfind` 六次、迴圈內每處多三次字典查,仍是線性,t_revisit_misplaced_linear 過。
- 計劃〈驗收條款〉:S5 改「行」與測試 ② 一致;S9 新綁 `t_doctor_revisit_reminder`,該測試實際斷言 E5 提示含「日期改下一次、刪掉,或在那一行加 [closed:日期 理由]」,綁定成立。r1 新測試(①②④⑤⑦)把修法改回去都會紅(①②靠 `straight`/`open_` 無條件為真,④靠 early return,⑤靠結案文法延到開頭欄位),前置斷言 ③⑥ 證明被測路徑有走到。

固定席節點(lens.txt)

- bound-tests-gate(★INVARIANT★:綁定測試逐支真跑)、測試假綠形態(★INVARIANT★:還原翻紅釘要配前置斷言):本次新增的 `t_revisit_misplaced_review_r1` 同時有前置斷言(③⑥)與還原會紅的斷言;現有綁定測試名未被改名或刪除,不影響這兩條合約。
- guard-kill、授權與歸屬、lumos-cli-read、design-loop、lumos-cli-lifecycle:diff 沒碰 guard kill、授權白名單、search 濾網、處置閘、re-inject 的任何程式路徑,宣稱的行為不受影響。
- pitfalls-code-loop(★RISK★)與其餘只列名的節點:diff 未動其牽連的函式(只動回頭條件的偵測與提示文字),判不影響。

最高 severity:minor
