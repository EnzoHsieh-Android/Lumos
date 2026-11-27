severity: clean

對照結果:設計走既有做法,沒有第二種做法,也沒有跨層直呼。

## A1 CHOICE_TIERS 與自檢的做法跟 check.py 既有慣例一致
severity: clean
blocking: 否
引句:「等級表 `CHOICE_TIERS = {"API": 1, "NUL": 2, "SBR": 2, "AOR": 3, "ROR": 3, "LCR": 3, "UOI": 3}` 放在 `configs/ast-grep/kotlin-android/check.py`,緊鄰 `CHOICE_CATEGORIES`」
既有做法:
- `CHOICE_CATEGORIES`、`CHOICE_ANCHORS`、`CHOICE_PRECONDITIONS`、`CHOICE_SPECIALS` 都是寫死的模組常數,放在 `configs/ast-grep/kotlin-android/check.py:1393-1398`。
- 這些詞表對不上時,`_choice_row` 會往問題清單 append 一句話,見 `configs/ast-grep/kotlin-android/check.py:1435-1438`。
- `choice_tables` 把問題整批回傳,`scripts/lumos:78813` 的 `_choice_tables` 看到任何問題就整張表判壞,見 `configs/ast-grep/kotlin-android/check.py:1490`。
- `choice_tables` 輸出的 dict 已有 `"categories": list(CHOICE_CATEGORIES)` 這個鍵,見 `configs/ast-grep/kotlin-android/check.py:1496`。

差在哪:沒有差別。
- 新增 `tiers` 鍵,跟 `categories` 鍵同位置、同形狀。
- 類別與等級互相對不上就報問題、整張表判壞,跟既有詞表自檢一致。
- 唯一的小注意:`CHOICE_TIERS` 的鍵和 `CHOICE_CATEGORIES` 是兩份同集合的清單,等於兩處要同步。計劃用自檢互擋,風險可控,不構成 major。

## A2 `tiers=None` 具名參數與 partial 傳法跟既有參數傳遞一致
severity: clean
blocking: 否
引句:「`_choice_pick_iter` 與 `_choice_pick` 多一個具名參數 `tiers=None`;`_choice_file_points` 的 partial 傳 `tiers=tables.get("tiers")`」
既有做法:
- `_choice_pick_iter` 的簽名是 `(…, categories, fp, ctx=None)`,見 `scripts/lumos:79358`。
- `_choice_pick` 是 `(…, fp, ctx=None, skip=None)`,見 `scripts/lumos:79383`。
- 可選參數本來就是尾端帶預設值的具名參數。
- `_choice_pick` 內部用位置參數呼叫 `_choice_pick_iter`,見 `scripts/lumos:79388`;`_choice_file_points` 用 `functools.partial` 綁位置參數,見 `scripts/lumos:79494`。
- 測試端 `scripts/test_lumos.py:143866` 與 `scripts/test_lumos.py:148870` 都用不傳可選參數的方式呼叫。

差在哪:
- 加 `tiers=None` 預設值,既有呼叫端不用改,這與 `skip=None` 加進來時的做法相同。
- `partial` 追加一個關鍵字綁定沒問題。
- 讀端用 `tables.get("tiers")`、缺鍵時回到舊挑法,也符合 skip 那條「不給就跟原本相同」的相容做法。
- `_choice_pick` 呼叫 `_choice_pick_iter` 時要記得把 `tiers` 轉傳,這是實作細節,不是架構問題。
- 層次上,等級表由 check.py 交出、`scripts/lumos` 只讀 `tables`,沒有新增跨層直呼;這是 `categories` 既有的路徑。

## A3 型錄只補說明段、不加欄,維持單一等級來源
severity: clean
blocking: 否
引句:「型錄〈選擇點表〉說明段補一句「同一行多類可挑時照三級先後挑,等級表在 check.py 的 CHOICE_TIERS」;型錄表格不加欄」
既有做法:
- 型錄〈選擇點表〉的欄位固定為 `_CHOICE_HEADER` 10 欄,見 `configs/ast-grep/kotlin-android/check.py:1390`;`skills/kotlin-idioms/checks-catalog.md:1654` 起的說明段已經在講挑法(「最多挑一個壞法」)。
- 「已撤列號」也是在說明段裡寫一行,見 `configs/ast-grep/kotlin-android/check.py:1396`。
- 不加欄不會動 `_CHOICE_HEADER`,也避免等級有兩個來源。

差在哪:沒有差別,說明段補文字是既有慣例。

總結:三處都對齊既有做法,沒有第二種做法、沒有跨層直呼。
