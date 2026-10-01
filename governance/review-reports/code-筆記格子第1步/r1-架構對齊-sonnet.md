severity: minor

整體判斷:這份 diff 照既有結構擴充,沒有引入第二套上線點判法、開關讀法或抽取。有 4 條小地方跟鄰居不一致。我只讀了 diff 和 `rw` 裡的程式碼,沒有跑測試。

## 三問

**① 分層與依賴方向:對齊。**
- 容器傳遞照鄰居做:`_note_shape_eval(..., slots=None)` 收容器,跟 `hints`、`tags` 同一套(`scripts/lumos:27278` 的 `_ns_negation_prepare` 回容器、`:26645` 的 `_ns_tag_hints_prepare` 同形)。違規在 eval 之外由 `_ns_slots_collected` 算,依賴方向是 cmd → prepare → eval → collected → report,跟否定現況句和前綴提醒一致。
- 抽取沒另起爐灶:`_notelines_range_added` 的 `mark2`/`sink` 加在同一趟逐提交,`_notelines_new`、`_notelines_range_cand` 只是把參數往下傳。`_carry` 也把 `by_path2` 一起帶,改名處理跟舊路徑一致。
- 呼叫端的解包方式沒變:`_notelines_range_added` 回傳形狀不動,不帶 `mark2` 的呼叫端照舊。
- 上線點仍用既有的 `_nodehome_golive`(`:24127`),只換了記號。推送時不用 `_nodehome_clamp_base`(`:25336`),因為格子要「找不到就整段不跑」,語意本來就跟 clamp 的「找不到就不過濾」相反。計劃〈擋〉有寫這個差異,所以不算第二套判法。
- 開關讀法 `_note_shape_slots_parse` 跟 `_note_shape_negation_parse`(`:26558`)、`_note_shape_tag_hints_parse`(`:26621`)同形:回 `{mode, warns, bad_value}`,壞值照預設並講一句。docstring 也說明了為何不擴 `_note_shape_config`。
- 總開關合併走 `_ns_slots_mode`,doctor 走 `_ns_slots_doctor_lines`,接在 `_ns_tag_hints_doctor_lines` 後面,位置和做法都對。

**② 命名與錯誤處理:大致對齊,有 4 條小出入。**
- 錯誤處理:提醒失敗的字樣是「提醒:…這次沒跑(…),不影響其他檢查」,git 失敗是 fail-open,都跟鄰居一樣。治理帳走 `_gate_event_or_warn`,`extra` 和 `nodes` 的用法沿用原樣。
- `--slots` 參數永久保留,`main()` 照既有 `ns_*` dest 命名。
- 測試用 `_ns_repo`、`_ns_note`、`_ns`,寫法跟既有一致。

**③ 第二種做法:沒有 major。**
- 唯一接近的是 A1(單次跳過路徑自己再做一次前置)。

## 不對齊條目

**A1 單次跳過路徑自己重推一次前置,選圖譜資料夾的規則跟主流程不同**
- 引句:「        vaults = sorted({_vault_slug_of(p) for p in lst[1]} - {None}) if lst else []」
- 對照:`scripts/lumos:27250` 的 `cmd_note_shape` 會優先選工作目錄所在的圖譜(`wv_rel` / `_vault_in`);`_ns_skip_slot_extra`(`:26803`)直接寫死 `"docs/" + vaults[0]`。
- 影響:多圖譜 repo 裡,跳過帳算的格子違規數可能跟正常路徑看到的不是同一個圖譜。
- 另外 `cfg_text`、`gate_mode`、eval 的前置也在這裡重做一遍。
- 這是 mapping 層的第二種做法,結構上算 major 的邊緣。我沒造出多圖譜的重現,所以降為 minor。⚠
severity: minor
- blocking: 否 — 只影響跳過帳的格子欄位,放行判定不受影響(整段包在 try 裡,失敗回 None)。

**A2 `slots_missing` 靠解析問題字串的文字來算**
- 引句:「            for k in re.findall(r"\[([^\[\]:]+):\]", x):」
- 對照:`_note_shape_negation_parse` 的 docstring(`:26558` 起)明說「doctor 不比對提醒字樣」,結構化欄位要用結構化的來源。`_ns_slot_line_problems` 裡的 `"被取代" in x` 也是比對字樣。
- 實際缺口:`slot_check`(`:3592`)的「test、repro、防回歸 三選一」這類缺漏不是 `[鍵:]` 形狀,不會被 `slots_missing` 算到。PITFALL 缺三選一時,`slots_lines` 計入、`slots_missing` 漏掉。
severity: minor
- blocking: 否 — 只讓治理帳的缺鍵統計偏低。

**A3 只有格子違規時,擋下尾句仍是筆記形狀擋的理由**
- 引句:「        print("內容還在工作目錄,改完再提交(這道檢查不動筆記、不動暫存區)。為什麼擋:筆記只留程式碼推不出來的東西,"」
- 對照:`scripts/lumos:27339` 的尾句固定是「推得出來的一寫進去就會過期——見 Projects/筆記形狀擋_計劃」。`blocked` 為真但 `viol` 和 `errs` 都空時,這句跟實際原因(缺必有格子)對不上。
- 同一個函式的 `_ns_slots_format` 另有自己的收尾句,所以這裡等於印了兩套說明。
severity: minor
- blocking: 否 — 只是字樣誤導,rc 和帳不受影響。

**A4 格子的治理帳 `extra` 沒帶 `check` 鍵**
- 引句:「    kw = {"extra": _ns_slot_extra(sviol)} if sviol else {}」
- 對照:同一個 gate 的 hinted 帳都帶 `check`,`:27314` 是 `{"check": "negation", ...}`,`:26705` 是 `{"check": "tag-hints", ...}`。格子的 blocked、warned、skipped-env 三種帳只有 `slots_lines` 和 `slots_missing`,讀帳的人要靠有沒有這兩個鍵來分辨。
severity: minor
- blocking: 否 — 計劃〈擋〉治理帳只要求這兩個欄位,對齊鄰居是順手的事。

不對齊共 4 條,其中 major 0 條

最高嚴重度 minor,blocking 0 條
