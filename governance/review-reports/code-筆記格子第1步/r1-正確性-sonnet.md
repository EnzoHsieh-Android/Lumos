severity: major

我把 diff 逐 hunk 讀完,再用 `rw/scripts/test_lumos.py` 的測試輔助函式(`_ns_repo`、`_ns`、`_nh_commit`)在暫存專案裡跑端到端重現。重現腳本是 `scratchpad/c1/e2e.py`,比對鍵的單點驗證在 `scratchpad/c1/h.py`。沒改 repo 任何檔。

**C1 推送時把「提交時放行」的欄位補寫誤擋(格子上線前寫的舊行,上線後只改欄位)**
severity: major
blocking: 是 — 提交時過、推送時擋,同一行兩道閘判法不一致,使用者只剩 --no-verify 或單次跳過可走。
引句:「                      if reg == "summary" and ln.strip() not in live2.get(nfc(p), ())]」
- 推送時「格子還沒上線的提交寫的行」只從終點版本的 rows 收。這些行在終點版本裡文字不在 `live2`,才會進舊行集合。
- 格子上線前寫的舊行,若在上線後的提交被補了欄位,終點版本的文字就在 `live2` 裡,舊文字不會進任何舊行來源:
  - `old_by` 只收筆記形狀擋上線前的提交。
  - 範圍起點版本沒有這行。
  - 淨差異沒有刪除。
- 所以比對鍵對不上,這行被當成新寫。
- 重現(`e2e.py` 的 E3):
  1. 提交 C1(`WHY:舊的一句話`),掛鉤此時沒有格子記號。
  2. 提交 golive(掛鉤加 `--slots`)。
  3. 暫存 `WHY:舊的一句話 [出處:2026-09-01 審查]`。
  4. `note-shape --staged --slots` 回 `(0, '')`。
  5. 提交 C2 後跑 `note-shape --diff base..tip`,回 rc=1,輸出:`A.md:15 缺 [因:]`,範本是 `WHY:舊的一句話 …`。
- 影響:使用者在升級掛鉤前後各有未推提交時會踩到。
- 修法:`_notelines_range_added` 要把「掛鉤沒帶 mark2 的提交」寫的文字另外收進舊行,不能只靠終點版本反推。

**C2 只放連結的舊行讓整個前綴的所有只放連結新行都豁免**
severity: major
blocking: 否 — 漏的是「新寫只放連結的 DEP/FLOW/RULE」這條規則,不會誤擋;格子還沒開擋,先降一級。
引句:「        if "[[" in core and _NS_POINTER_ONLY_RE.match(core):」
- `_ns_slot_key` 對所有只放連結的行回傳同一個鍵 `(前綴, "\x00只放連結")`,不分連到哪個節點。
- 只要被動到的筆記的舊版(或這次刪掉的行)裡有任何一行同前綴的只放連結行,所有新寫的同前綴只放連結行都命中 `key in old_keys`,直接回 `[]`。
- 重現(E1):
  - 舊版有 `DEP:[[Systems/甲]]`,暫存加上全新的 `DEP:[[Systems/全新乙]]`,`--staged --slots` 回 `(0, '')`。
  - 對照組:舊版沒有只放連結的 DEP,同一個新行回 rc=1,訊息是「改寫成 SEE」。
- 測試 `t_slots_edited_old_line` ③ 只驗了「補連結算舊行」,沒驗「全新連結被放過」。
- 修法:鍵要帶連結集合(舊連結是新連結的子集才算補連結),不能共用一個萬用鍵。

**C3 換行重排的舊行被當成新寫**
severity: minor
blocking: 否 — 只是提交時的誤擋,有 `LUMOS_SKIP_NOTE_SHAPE` 和 `note_shape.slots=warn` 兩個逃生口。
引句:「    bare = _NS_SLOT_SEP_RE.sub(" ", core).strip()」
- 分隔字(含空白)被換成空格而不是刪掉。
- 續行用 `" ".join` 接回,中文在任意位置折行就會多出一格空白。
- 舊的一整行 `WHY:這是一個很長的舊句子還沒有格子`,重排成兩行(`WHY:這是一個很長的` 加續行 `舊句子還沒有格子`)後:
  - 鍵變成「這是一個很長的 舊句子還沒有格子」,對不上舊鍵。
  - 暫存後回 rc=1,輸出 `缺 [出處:]、[因:]`(E2)。
- 同一個原因,跨篇搬移時被刪掉的行只有第一個實體行(`_ns_deleted_summary_lines` 逐實體行取),也對不上帶續行的新邏輯行。
- 修法:比對鍵把空白整個刪掉,不要換成空格。

**我試過、沒找到洞的路徑**
- `_ns_summary_logical` 跟 `_notelines_rows` 用同一個 `split("\n")` 和 `_notelines_regions`,行號一致。
- 只在續行補欄位時,該實體行不在 `logical` 裡,會被跳過(放行,不會誤擋)。
- 新舊互讀、fail-open:
  - `_notelines_live_sets` 回 `None` 時,呼叫端接得住。
  - `_ns_slots_collected` 對 git 失敗與例外都回空清單。
  - `_ns_slots_prepare` 找不到格子記號就不跑。
  - 單次跳過的 `_ns_skip_slot_extra` 整段有例外防護。
- 作廢例外:`_ns_slot_line_problems` 用 `"被取代" in x` 過濾,檢查過所有相關訊息字串,沒有誤收。
- 未來日期:只在提交時檢查,推送時不查。這是設計(計劃 r3),不是缺陷。
- 掛鉤範本與 repo 自己的 `scripts/hooks/pre-commit` 都沒有 `note-shape --staged --slots` 字樣,golive 記號沒有被註解提前觸發。

**圖譜鏡頭(固定席)**
`lumos impact --diff` 列出 `scripts/lumos` 與 `scripts/test_lumos.py` 的家,主要是 `Systems/筆記內容閘.md`(1.00)和 `Projects/筆記格子寫法與過期檢查_計劃.md`(0.84),其餘多是 ★INVARIANT★ 的泛用節點。
- 我沒逐一重驗各 INVARIANT 的綁定測試,對這些節點不下「不影響」的結論。
- 筆記內容閘裡新增的 WHY 說「只改欄位的舊行不套必有鍵(提交對 HEAD、推送對範圍起點,再加範圍裡刪掉的行與格子上線前的提交寫的行)」。這句跟 C1 的實作行為不符:推送時格子上線前寫的行只收到「終點版本裡不在 `live2` 的文字」。
- 計劃第 1 步還列了「工具樣板豁免清單」,diff 裡看不到對應實作,也沒有說明刻意延後。

最高嚴重度 major,blocking 1 條
