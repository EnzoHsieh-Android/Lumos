severity: major

## b1 S8「依列號」測試分不出「放行取最後一筆」與「殺掉優先於存活」
severity: major
blocking: 是(能指出具體合理的改壞而測試照綠,被保護的是 S8 條款明寫的行為)

走到 `_gov_choice_counts` 的 `row_waive` 挑選,以及 `_gov_choice_by_row` 的終態判定。`t_gov_stats_choice_by_row` 只用一個列號 C-32。丙的兩筆放行標籤都是「等價」,乙的事件順序是先存活後殺掉。於是以下兩種改壞測試都照綠(在我的臨時副本改 `scripts/lumos`,跑 `python3.14 scripts/test_lumos.py -k gov_stats_choice_by_row`,兩次都是 `2 passed, 0 failed`):
- 把 `ts >= c["row_waive"][wk][0]` 改成 `ts < …`,變成「取最早一筆放行」。S8 條款寫「同一行多筆放行只算最後一筆」,這項沒人守。
- 終態改成「取最後一筆事件」(`row_mut` 存 list、用 `seen[-1]`)。乙剛好最後是 killed,所以照樣得到殺掉 2。「曾殺掉就算殺掉」只在「先殺掉、後又存活」時才分得出來,測試沒有這個順序。
- 附帶:`sorted(by_row, key=…)` 換成 `key=lambda x: x` 也照綠,因為只有一個列號,C-9、C-10 的數字排序沒被守。

實測 `_render_gov_choice` 餵 `killed` 再 `survived`,輸出「殺掉 1、存活 0」,行為本身是對的,只是測試釘不住。

預期:fixture 要有兩筆標籤不同的放行(早的「不適用」、晚的「等價」),加一個先殺掉後存活的壞法,以及至少兩個列號(C-9 與 C-10)。
引句:「wv("c1", t1, "丙", "等價", row="C-32"), wv("c2", t2, "丙", "等價", row="C-32"),」
file: `scripts/test_lumos.py`(`t_gov_stats_choice_by_row`);`scripts/lumos`(`_gov_choice_counts`、`_gov_choice_by_row`)

## b2 `已撤列號:` 只認第一個、頂格的那一行,其他寫法讓守衛無聲失效
severity: minor
blocking: 否(守衛靜默關閉,但要作者自己把格式寫歪才會發生)

走到 `_choice_retired`:`_CHOICE_RETIRED_RE.search` 只取第一個 `^已撤列號:` 那一行,沒比到就回「視同空」。我拿真型錄把那行換掉再跑 `kp.choice_tables`:
- `已撤列號:C-31`:正常報「C-31 已撤…」。
- `- 已撤列號:C-31`、`  已撤列號:C-31`、`**已撤列號:**C-31`:回 `[]`,C-31 還在表和 `api.yml`,沒有任何問題。
- 在原本那行後面再加一行 `已撤列號:C-31`:同樣回 `[]`。第二次撤列時順手追加一行,舊行以外的列號全被忽略,列號就能被重用。

預期:有「已撤列號」字樣卻沒被認進去的行應報看不懂,或同節出現多行時合併。
引句:「m = _CHOICE_RETIRED_RE.search(text[i:j if j >= 0 else len(text)])」
file: `configs/ast-grep/kotlin-android/check.py`(`_choice_retired`、`_CHOICE_RETIRED_RE`)

## b3 「依列號」排序用 `isdigit()` 擋不住上標數字,`gov --stats` 整段當掉
severity: minor
blocking: 否(要帳上有手改過的怪列號才會觸發)

`_render_gov_choice` 的排序鍵是 `int(x[2:]) if x[:2] == "C-" and x[2:].isdigit() …`。帳上 row 是字串 `"C-²"` 時,`"²".isdigit()` 為真,`int("²")` 丟 `ValueError`。重現:`_render_gov_choice([{"gate":_CHOICE_KILL_GATE,"kind":_CHOICE_KILL_GATE,"row":"C-²","verdict":"killed","ck":{"file":"a.kt","fp":"f"},"attempt":1,"via":"run","ts":"t"}])`,輸出「依列號…」標題行之後丟 `ValueError: invalid literal for int() with base 10: '²'`,後面其他段都印不出來。
預期:壞列號排到最後,不拖垮整段統計。改用 `isdecimal()`,或包 try。
引句:「for row in sorted(by_row, key=lambda x: (int(x[2:]) if x[:2] == "C-" and x[2:].isdigit() else 10 ** 9, x)):」
file: `scripts/lumos`(`_render_gov_choice`)

## b4 引數錨點的邊界差一沒被測試守住
severity: minor
blocking: 否(只是測試缺口,實作本身是對的)

`_choice_anchor` 的 `range(hit["line"], hit["end_line"] + 1)` 改成不含右括號那行,`-k choice_points_compose` 仍是 `6 passed`。S4 測試只試了改動行 7(中間行)和 99(範圍外),沒有「只改右括號那行」。這個情境在派工鏡頭點名,也是 `) { items.size + k }` 這種寫法的真實形狀。
預期:加一條改動行集合只含 `)` 那行的斷言。
引句:「anchor, _op = m._choice_anchor(bb, h, rem, {7}, starts)」
file: `scripts/test_lumos.py`(`t_choice_points_compose`);`scripts/lumos`(`_choice_anchor`)

## 規格對照與其他查過沒問題的點
- S1–S4、S6 預期值表各列:`probe` 跑真 ast-grep,輸出與表一致。實跑結果:
  - `a ?: b ?: c ?: d` 挑出一個壞法,不當掉。
  - `?:` 換行加註解、區塊註解內的 `?:`、字串樣板裡的 `?.`、CRLF 的 `!!` 位置都對。
  - `?.` 前面是行註解或區塊註解(跟在 lambda、字串、索引、括號、`this` 之後)一律不命中。
  - `"a\$b"`、三引號字串當字面值不命中。
  - 深度 800 的 elvis 鏈掃描 0.14 秒、挑點 0.01 秒,沒有效能問題。
- S7:`CHOICE_CATEGORIES` 在尾端加 NUL,`_choice_pick` 洗牌前先濾出該行有的類別,沒 NUL 的行相對順序不變。`_choice_plus_nodes` 只用運算子列,不受 `category == "NUL"` 分支影響。
- 小的觀察,不標 finding:`LaunchedEffect('a')` 與 `LaunchedEffect(-1)` 會被當非字面值,產生等價壞法(字元、負號不在計劃列的字面值清單,符合規格字面);ck_waive 的 file/fp 缺欄位時多筆放行會併成同一鍵(寫入端總會帶,屬帳被手改才有的情況)。
- S9 是 `[manual:]`,這份 diff 看不出量測數字。圖譜鏡頭固定席筆記因鏡頭超時沒附,我無法逐條判固定席節點。

最嚴重:major;blocking 共 1 條
