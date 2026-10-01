severity: minor

我對這份 diff 餵了 BOM、CRLF、NFD 檔名、改名加改內容、空提交、沒有 HEAD 的首次提交、全 0 起點、壞設定檔、複數行 YAML 續行、合併中跳過等輸入。結果沒有 blocker 或 major。下面三條是實測得到的 minor,各有最小重現。

沒有出問題的輸入:
- 整篇改 CRLF 後,推送不重查舊行,rc=0。
- 帶 BOM 的筆記、NFD 檔名加改名加改內容,提交時都照常擋新違規。
- 複數行 RULE 的續行會接回前一行,不誤擋。
- 設定檔壞掉、BOM 設定檔、`"BLOCK"` 大寫、`note_shape` 是陣列、頂層是 `[1]`,都照預設 block 或印提醒。
- 首次提交沒有 HEAD 時照常擋。
- 全 0 起點會被截到上線點,只擋新寫的行。
- 全形冒號開頭的 `WHY：` 不算前綴,沿用既有前綴規則。
- 行內程式碼裡的方括號不算欄位。
- 10 萬字超長行沒有例外。
- `-k slots` 子集 88 項全過。

**B1**
引句:「        return m.group(1), "\x00只放連結"」
- 只放連結的行,比對鍵是同一個常數 `(前綴, "\x00只放連結")`(`_ns_slot_key`)。所以舊集合(HEAD 版、同次刪掉的行、推送範圍起點的版本)裡只要有任何一條只放連結的 DEP 或 FLOW,同前綴的全新只放連結行也被當成「改過的舊行」放行。
- 重現:筆記裡已有 `DEP:[[Systems/B]]`,暫存新增一行 `DEP:[[Systems/C]]`,再跑 `lumos note-shape --staged --slots`。結果沒有任何缺漏。
- 對照:先把舊 DEP 拿掉並提交,再加同一行,就擋下「只放連結的 DEP 改寫成 SEE」。
- 同一個放行口也讓整行複製一條已存在的裸行通過。我在推送路徑重現過,複製 `WHY:legacy裸行` 沒被擋。
- 計劃 [S4] 說只放連結的新寫 DEP/FLOW 應被擋,[S6] 只說舊行改連結算舊行。程式把「舊行」放寬成「同前綴有任何只放連結的行」,兩條互相打架。
- ⚠ 計劃 [S6] 的字面可以讀成這樣,所以標 minor。
severity: minor
blocking: 否 — 只漏擋一種窄形狀(只放連結的 DEP/FLOW),不影響其他格子規則。

**B2**
引句:「            for k in re.findall(r"\[([^\[\]:]+):\]", x):」
- `slots_missing` 只數「帶方括號的缺鍵」。PITFALL 缺「test、repro、防回歸 三選一」的訊息沒有方括號,抓不到。
- 重現:跑 `m._ns_slot_extra([("p",1,"PITFALL","x", m._ns_slot_line_problems("PITFALL:x [出處:a] [根因:b]", {}, True))])`。輸出是 `{'slots_lines': 1, 'slots_missing': {}}`,行數算進去了,缺什麼鍵卻是空的。
- 影響:治理帳按鍵統計缺漏時,少算了防回歸這一格。
severity: minor
blocking: 否 — 只讓治理帳統計少一類,不影響擋或放。

**B3**
引句:「        extra = _ns_skip_slot_extra(root) if (staged and slots_flag) else None」
- 單次跳過在 `MERGE_HEAD` 檢查之前,所以合併進行中也會算格子違規。正常路徑在合併中根本不查(印「合併提交跳過」並回 0),跳過卻把整個合併暫存內容當新寫的來數。
- 重現:側枝加 3 行裸 `WHY:`,在 main 上 `git merge --no-commit side`,再跑 `LUMOS_SKIP_NOTE_SHAPE=1 lumos note-shape --staged --slots`。治理帳最後一行是 `"slots_lines": 3, "slots_missing": {"出處": 3, "因": 3}`。
- 影響:這 3 行本來就不會被檢查,卻記成「跳過前本會違規」。計劃用 RETIRE-IF 配對這些跳過事件,數字會被灌水。
severity: minor
blocking: 否 — 放行不受影響,只讓逃生口的帳不準。

**圖譜鏡頭(固定席)**
- 我跑了 `lumos impact --diff 24f08d48..c5fc9870`,只有 `scripts/lumos` 和 `scripts/test_lumos.py` 兩個程式檔進入影響面。派工時沒有附固定席筆記,所以我只看了影響清單裡跟本變更直接相關的幾篇。
- `Systems/筆記內容閘.md`:家節點,diff 已新增 WHY 行。引用的 `[test:t_slots_own_golive]` 存在而且跑過綠。不影響。
- `Projects/筆記格子寫法與過期檢查_計劃.md`:diff 已寫進度行。
  - 我對照了〈擋〉治理帳段、[S4]、[S6]。B1 是 [S4] 與 [S6] 的接縫,B3 是「只在提交時」的邊界沒涵蓋合併。
  - 這篇計劃沒有寫格子該不該在合併中跳過,所以我沒有拿計劃去推翻程式。
- `Systems/存量漂移守衛.md`、`Systems/每支檔有家.md`:`_notelines_range_added` 的簽名只加了預設值參數,不帶 `mark2` 的呼叫端行為不變。我實測推送路徑沒帶記號時結果沒變,不影響。
- 其餘固定席節點(INVARIANT 或 RISK 的 `Systems/*`):diff 沒動它們各自的守衛面。我沒逐篇展開,判不影響。

最高嚴重度 minor,blocking 0 條
