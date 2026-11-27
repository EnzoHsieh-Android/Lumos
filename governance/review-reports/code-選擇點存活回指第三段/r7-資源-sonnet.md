severity: clean

我沒有發現這一輪的資源問題,三個問題都沒踩到。

**`_choice_reader_lines` 的集合與時間(沒問題)**
- `_choice_reader_lines` 把區間展開成行號集合,大小頂多等於計劃的行數。
- 它在 `_choice_plan_sections` 和 `_choice_plan_view` 裡每份計劃只算一次,不在逐行迴圈裡重算。
- 區間來自兩個讀取器各自的節,節與節不重疊,所以集合不會比總行數大,時間是線性的,不必擔心很多節。
- 我只讀碼推論,沒有拿大計劃實測。

**`spans` 參數對呼叫端的成本(沒變)**
- `_h2_section_lines` 的 `spans` 預設是 None。
- 其他呼叫端(`_HAZARD_H2_RE`、`_NOGO_H2_RE`、`_EXPECTED_H2_RE` 等)不帶它,所以只多一個 `if spans is not None` 判斷,實際成本沒有變。
- 只有 `_choice_reader_lines` 會帶 `spans`,這條路徑不在門判定的掃描上。

**`_DOOR_RULE_VERSION` 升到 17 的重算成本(有限)**
- 升版並不會讓既有留痕全部重算。
- `scripts/lumos:16395` 的 `rec.get("door_rule") == _DOOR_RULE_VERSION` 只影響「風險低、已綠」那條放行判斷,版本不符時那份計劃會多跑一次規格閘。
- 另一處在 `scripts/lumos:3604`,版本不符的留痕只是不計入前 30 份的統計,不會觸發重算。
- 這是升版時一向的行為,不是這次修補新引入的。

**`spans` 三處收尾(邏輯沒洞)**
- 遇到同名新節、`## ` 或 `# ` 節尾、檔尾,三處都有收尾。
- 三級標題不切節,和原本一致。
- 沒有看到重複 append,也沒有漏掉最後一節。

總結:最高等級是 clean
