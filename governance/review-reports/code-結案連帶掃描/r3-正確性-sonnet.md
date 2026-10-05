severity: minor

## F1 格子⑩假綠:拿掉括號配對檢查它照樣綠
severity: minor
blocking: 否
引句:「check("⑩結論括號沒配對:回 2", rc == 2 and "括號" in out and p.read_bytes() == raw, out)」
file: `/home/user/Lumos/scripts/lumos:34571`(_drift_fix_c6_args 的 _drift_parens_balanced 檢查)
失敗場景:
1. 格子⑩對 la 那行下 --settled "括號(沒有收尾"。la 在前面格子①已經補過已裁定括號,所以那一行已不是 c6。
2. 把 _drift_fix_c6_args 裡的 `if not _drift_parens_balanced(...)` 換成 `if False:`(我用 sed 複製一份 lumos 實跑)。
3. 同一個輸入回 2,訊息是「沒有還沒補已裁定括號的待定子句…不是 c6」。這句話本身含「括號」,rc==2、檔案沒動,三個斷言全成立,格子仍綠。
4. 所以 docstring 寫的「不驗結論括號配對 → ⑩紅」不成立。要真釘住,得對一行還沒補的 c6(例如新增一行)下不成對的 --settled,並斷言訊息含「要成對」。

## F2 括號補進行內程式碼(反引號)中間
severity: minor
blocking: 否
引句:「new = [*lines[:line - 1], src[:ends[0]] + add + src[ends[0]:], *lines[line:]]」
file: `/home/user/Lumos/scripts/lumos:32230`(_drift_pending_clauses 只認切點字元,不認反引號或一般括號)
失敗場景:
1. 筆記有一行 `待裁定 [[Projects/Done_計劃]] 見 `a；b` 後`,偵測列為 c6(第一子句有待定詞加連結)。
2. 執行 drift fix --kind c6 --settled "x" 該行,回 0,補完的行是 `待裁定 [[Projects/Done_計劃]] 見 `a(已裁定:… 見 [[Projects/Done_計劃]])；b` 後`,括號和連結被塞進行內程式碼裡(實跑確認)。
3. handled 只看遮罩後的待定連結,不看是否落在行內程式碼或一般括號中間,所以判成「處理到」。連結在程式碼 span 裡,渲染後不是連結。全形括號「（見 x；y）」中間同樣會被插入,只是外觀難看。
4. 偵測與修法對切點的看法一致,所以沒有不一致,問題是修法寫完沒檢查插入點是否在程式碼 span 內。

## 已走過沒問題的範圍
引句:「out[m.start():j] = _DRIFT_MASK * (j - m.start())」
- _drift_mask_settled 以 code point 等長替換,位置與原行一一對應。實跑含表情符號、組合字元的行,插入位置正確。
- 配對只數括號、不分半形全形,與 _drift_parens_balanced 規則一致。結論含「(已裁定:內)」巢狀、含分號與 ——、含待定詞,實跑都補在正確位置,補完那行不再列該目標。
- 行內手寫未收尾的「(已裁定:」遮到行尾,偵測與修法同樣回 2「不是 c6」,沒有分歧。
- 半形收尾全形的混用括號(「(已裁定:2026 好）」)視為已收尾,兩邊一致。
- 單行 summary 擋下、值只有註解不收、同目標兩個待定子句擋下,三者的格子拿掉守衛都會翻紅。

總結:沒有找到修法寫完自判沒處理到或偵測與修法分歧的輸入,只有一格假綠與一個把括號插進行內程式碼的邊角。
