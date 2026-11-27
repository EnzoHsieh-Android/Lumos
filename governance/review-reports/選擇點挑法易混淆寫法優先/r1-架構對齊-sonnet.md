severity: minor

## A1 計劃寫「只改 _choice_pick_iter」,但等級表要經兩個函式傳進去,有三處要動
severity: minor
blocking: 否
引句:「挑壞法那支函式(_choice_pick_iter,`scripts/lumos`)排類別時:每一級各自取出這一行有的類別」

既有做法:categories 是從 `tables["categories"]` 當位置參數,經 `functools.partial` 傳給 `_choice_pick`,再傳給 `_choice_pick_iter`。
- 呼叫點:`scripts/lumos:79494`
- `_choice_pick` 定義:`scripts/lumos:79383`
- `_choice_pick_iter` 定義:`scripts/lumos:79358`

差在哪:
- 挑法邏輯確實只在 `_choice_pick_iter` 一處,沒有第二套挑法,這點對得上。
- 但等級表要走同一條路進去,至少會動 `choice_tables` 輸出、呼叫點的 partial、`_choice_pick` 和 `_choice_pick_iter` 的簽名。
- 計劃〈做法〉和〈回退〉都只提 `_choice_pick_iter`。照樣走既有的參數傳遞路徑就沒問題,只是改動範圍比字面寬。回退「一次 git revert」仍成立。
- S3 要在測試裡「假造」類別,可能繞過 `choice_tables`,這也要明寫。

## A2 〈落點〉寫「型錄等級欄」,〈做法〉只說補一句說明,兩處對型錄的改法不一致
severity: minor
blocking: 否
引句:「型錄等級欄寫在 kotlin-idioms 型錄」

既有做法:
- 型錄〈選擇點表〉的欄位是固定的十欄,「類別」是其中一欄:`skills/kotlin-idioms/checks-catalog.md:17`。
- 表頭寫死在 `configs/ast-grep/kotlin-android/check.py:1389` 的 `_CHOICE_HEADER`。
- 若真的加一欄「等級」,就會在 `_CHOICE_HEADER`、`_choice_row` 與型錄之外,再多一個「每列一份」的等級來源,而且 55 列重複同一類別的值。這會變成第二種做法,也會跟〈做法〉說的「一處是唯一來源」衝突。
- 〈做法〉本身只寫「〈用詞〉補一句說明三級」,這樣沒問題。

差在哪:〈落點〉的「等級欄」字面容易讓實作者去加欄。建議改成「型錄〈用詞〉補一句說明」,並寫明不加表格欄。

## 對照過、沒有問題的部分
- **等級表放在 check.py 的 categories 旁、由 choice_tables 交出**,跟既有讀法同一套:
  - `CHOICE_CATEGORIES`(`configs/ast-grep/kotlin-android/check.py:1393`)就是寫死在 check.py 的類別層級常數。
  - 它由 `choice_tables` 在 `check.py:1496` 以 `out["categories"]` 交出。
  - `scripts/lumos` 的 `_choice_tables`(`scripts/lumos:78813`)只借 `mod.choice_tables` 讀表,不自己讀。
  - 類別詞表、錨點詞表、型別前提詞表也都是同樣寫法(`check.py:1393`、`1396`、`1399`)。
  - 「類別層級」屬性放這裡正合適;若放型錄欄,每列重複值,反而是新做法。
- **型錄裡沒有別的「類別層級」屬性寫法可沿用**:型錄表格欄都是每列屬性,類別層級的東西都寫在 check.py 的常數。
- **挑法沒有第二套**:合批編譯換候選與 skip 集合都從 `_choice_pick_iter` 往下取(`scripts/lumos:79383`、`79388`)。計劃〈做法〉末句同樣這麼寫。
- **沒有跨層直呼**:`scripts/lumos` 仍經 `_kt_pack_check` 借 check.py,沒有自己重讀型錄。

⚠ 判不準:`choice_tables` 目前會驗類別在詞表內(`check.py:1435`)。計劃沒說等級表的鍵要不要也驗是 `CHOICE_CATEGORIES` 的子集。這是補強,不是第二種做法,所以不列為 finding。

最嚴重 severity:minor,blocking 共 0 條。
