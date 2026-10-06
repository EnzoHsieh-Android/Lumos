severity: clean

## 審查結果

沒有發現需要標等級的問題。`python3.14 scripts/test_lumos.py -k t_summary_line` 在 `/Users/enzo/harness/lumos-d1` 跑出 27 passed, 0 failed。

### 鏡頭 1 正確性
- `(x + "x").splitlines()`:空字串變 `["x"]` 為 1 行;`"abc\n"` 變兩行被擋;只含 `\r\n` 的字串變 `["", "x"]` 被擋;結尾換行也被擋。舊片段為空字串先被 `not old` 擋掉。這個寫法判對。
  引句:「if not old or len((old + "x").splitlines()) > 1 or len((new + "x").splitlines()) > 1:」
- 新片段 None 在檢查前已被 `new = new or ""` 轉成空字串。舊新相同的判斷放在換行檢查之後,但舊片段一定非空,所以順序不影響結果。
  引句:「if old == new:」
- `_node_not_found` 回傳值是 2(`scripts/lumos:12154` 的函式,結尾 `return 2`),寫入側後半句也有印。測試裡的「找不到叫「Systems/不存在」的筆記」跟它實際輸出一致。
  引句:「return _node_not_found(env, node, write_side=True)」
- 拿掉 `== "summary:"` 後:我用 `_notelines_regions` 實測,`summary: |-` 那一行的區是 `other`,不會被 `_summary_line_hits` 當成出現處,所以舊片段不可能把標頭行改成 `summary:`。刪行只會發生在區塊內的行,拿掉的判斷原本就是死碼,行為不變。剩下的 `not ln.lstrip().startswith("summary:")` 也是無害死碼。
  引句:「delete = not new_line.strip()」

### 鏡頭 2 測試假綠
- 新增的換行類字元測試用 `\r`、`\x85`、` `、`\x0b` 當新片段,舊片段取有效值「一條」,同時驗 rc2、原檔不動、訊息含「不能含換行」。若改回只擋 `"\n"`,這幾條會變成真的寫入,測試會紅。
  引句:「for bad in ("\r", "\x85", " ", "\x0b"):」
- 「新行跟另一行一樣」的案例驗結果是 `["KEY:甲", "KEY:甲"]`,有斷言實際內容。
  引句:「check("⑤新行跟另一行一樣:照改", r2.returncode == 0」
- 小遺漏(不標問題):舊片段含非 `\n` 換行類字元沒有測試,只有新片段有。兩邊走同一個表達式,沒有具體失敗場景。

### 鏡頭 3 圖譜
沒有附固定席節點,備援段不逐條答。計劃筆記已寫明單行值摘要不支援、換行類字元一律擋、舊新相同擋,跟程式碼一致。
  引句:「摘要寫成單行值 `summary: 一句` 的不支援(會報找不到),要改就手改或先改成區塊寫法。」

本輪 r1 的五項修正都正確落地,沒有看到修補本身引入的新問題。
