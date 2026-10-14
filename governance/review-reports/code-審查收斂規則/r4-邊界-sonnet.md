severity: minor

我用 `-k residual` 跑了子集,274 筆全過。另外在 scripts 的複本上做了四個破壞實驗,對應測試都翻紅:
- 指紋改成只剝 Cf。
- 編號正規化拿掉「字母與數字之間的分隔符」那條。
- 審計先後改用最早那筆問答比。
- `added` 恆為空。

實驗目錄和 gctl 暫存都已刪。

severity: minor
blocking: 否 — 只影響手改或重複列的極端情境,正常寫帳不會出現,且最糟是少升一次 high
引句:「return len(brows - hrows)」
問題:刪帳偵測把兩版的 residual-ask 列轉成 set 再相減,重複的整列只算一筆。
具體失敗情境:起點帳裡同一筆 testable 問答列出現兩次(位元組完全相同)。頂端只刪掉其中一份,實測 `dup->one` 回 0,不升 high。只有兩份都刪,才會偵測到少一筆。
佐證:我在暫存 git repo 裡呼叫 `_residual_ask_rows_dropped`,結果如上。`_gate_event` 的 ts 精確到秒,所以程式自己寫不出完全相同的兩列;只有手改或 merge 重複才會出現。改用 Counter 相減就能補上。
另外兩個方向相反的誤升,是更保守的偏差,不算 finding:
- 第一行帶 BOM:BOM 被 `.strip()` 留下,整列當成讀不出的列,跟沒 BOM 的版本對不上,實測回 1。
- 帳裡 JSON 欄位順序不同但內容相同:當成另一列,實測回 1。

severity: minor
blocking: 否 — 要手改帳裡的 ts 才會觸發,而且只是多一個堆疊追蹤,不會誤放行
引句:「t if t.tzinfo else t.astimezone()」
問題:`_residual_ev_order` 的 `astimezone()` 在 try 外面。沒帶時區、年份是 0001 的 ts,會丟出 `ValueError: year must be in 1..9999, not 0`,沒被攔住。
具體失敗情境:帳裡有一筆問答或審計列的 ts 是 `0001-01-01T00:00:00`,沒帶時區。`guard residual --add` 會直接崩出堆疊追蹤。函式說明和測試都寫「ts 讀不出也擋」,這條路徑卻走不到那句擋下訊息。
佐證:我直接呼叫 `_residual_ev_order({"ts":"0001-01-01T00:00:00"})` 得到 ValueError。帶時區的 `0001-01-01T00:00:00+08:00`、毫秒、`Z`、`20261014` 都正常,`x` 回 None。把 `astimezone()` 放進 try,出錯回 None 即可。

已讀,無 finding:
- 編號正規化:`c-1`、`c_1`、`C1`、`c 1`、`c--1`、全形都等於 `c1`;`c1.1` 等於 `c1-1` 等於 `c-1.1`;`c11` 與 `c1-1`、`a-bc` 與 `ab-c` 不撞。我找不到會誤把應該分開的編號併起來的例子。`a-1b`、`a1-b` 這類併在一起是設計內的取捨。
- 指紋:Cf、Cc 先剝再壓空白,`a \u200b b` 不會留雙空白;tab、換行先當空白;`ab` 與 `a b`、`1.5` 與 `15` 仍不同。
- 列集合比對:CRLF 與重新排序回 0,刪列回 1,NUL 或截斷列回 1。起點帳不存在回 0,頂端不存在則全算刪除。
- 審計先後的 ts:毫秒、`Z`、有無時區、日期-only 都能解析。比較用 (時間, 帳內序號),同一秒靠序號分先後,`<=` 與 `<` 實際等價。
- `touched` 和 `head_bad` 的新條件、`added` 以 (節點, 指紋, 指標) 為鍵,讀起來邏輯一致。
- 測試的行為覆蓋,上面四個破壞實驗都會紅。

最高等級 minor,blocking 0 條。
