severity: minor

severity: minor
blocking: 否 — 只是擋下訊息的字面前後矛盾,不影響 rc、帳或指紋
引句:「改用看頂端版本的舊版判、比不到 prepare 記的新版紀錄——重跑也一樣,所以這幾篇這次不擋、已記帳」
問題:同一次推送若有逾時的篇,又有真正沒對照的篇,`_note_reread_blocking` 會判擋。這時 `_note_reread_print_layer1` 的標頭印「擋下:回頭重讀:」,列表中逾時那幾行卻印「這次不擋」。尾段「其中 N 篇……這次不擋」也一樣。讀的人會以為整次都放行。
具體失敗情境:5 篇沒對照,其中 2 篇逾時。rc 是 1,輸出同時說「擋下」與「這次不擋」。
佐證:``file: `scripts/lumos:37771` ``(`late` 在 block 時照樣印「這次不擋」,沒有跟 `blocking` 分開)。

已讀,無 finding 的部分:
- **`_nodehome_cat_blobs_capped` 的 `sizes` 參數**:其他呼叫端不傳 `sizes`,仍走 `sizes is None` 舊路徑,行為不變。節點認家那條路沒被碰到。
  - 我另外跑過 `sizes=[None]`,回 `[None]`,不讀那一支。
  - 本修補的呼叫端不會傳 None:`_note_reread_fp_file` 先確認每個物件編號都在 sizes 裡,查不到就退 v1。
- **`_NOTELINES_HUNK_RE`**:它有 4 個群組(舊起點、舊行數、新起點、新行數)。新程式取 `k[2]`、`k[3]` 是新側,對得上。
  - 既有的另一個使用者(`scripts/lumos:32292`)沒有改動。
  - 我沒有改動這個正規式,只多了一個使用者,且只解析以 `@@ ` 開頭的行。
- **縮排鏈**:我實跑了這幾種輸入,結果都符合文件寫的規則。
  - 同一個類別裡的兩個方法,鏈分得開。
  - 純刪除(行數 0)的 hunk、CRLF、tab 與空白混用、超出檔尾的位置。
  - 深度 3000 層巢狀花 0.03 秒,40 萬行加 2000 段改動花 0.2 秒,沒有退化。
- **v1 舊紀錄與指紋版本**:`e0da694` 以前的主程式沒有 `_note_reread_hunk_tags` 和「指紋算法 v2」。v2 是這條分支才新增的,標籤算法改了不會讓已發行的紀錄失效。
- **`_note_reread_diff` 與 `_note_reread_v2_cut`**:共用 `_NOTE_REREAD_DIFF_CTX` 與 `_note_reread_diff_fits` 後,回傳值沒變。上下文仍是 3、1、0,最後一種是 0。「是否縮短」的判準仍是 `len(d) > cap`,`ctx[0]` 仍是 3。
- **rc 與帳**:`_note_reread_rc`、印出、`_note_reread_ledger` 三處都走 `_note_reread_blocking`。
  - 只剩逾時的篇時,rc 是 0,帳記 `reminded`,輸出走 stdout 並帶「不擋」尾句,三者一致。
  - 新增的帳欄位 `late` 是追加的;`layer1_fps` 的 `late` 只在成立時才出現,舊的讀取端不會壞。
  - `res.get("late")` 對沒有這個欄位的 res 都安全。
- **reread-prepare**:沒有截止時間,不會產生 `late`,輸出沒被改到。
- 設計取捨(不算 finding):`late` 的條件是 `why == "逾時"`。環境慢到讓每篇都逾時時,整個擋關會變成只提醒、不擋。這是作者在修補說明裡明講的取捨,帳上也有記錄。

實驗暫存已刪。

最高等級 minor,blocking 0 條。
