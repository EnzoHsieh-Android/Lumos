# code-代碼審修正關卡第0步 r1 收貨紀錄(2026-10-02,3 席)

材料拆兩份(r1-part-a.patch 主程式 1383 行、r1-part-b.patch 測試手冊筆記 1016 行),整份 r1-snapshot.patch 2399 行當指紋。機械收貨:3 份都已是正規化格式、quote-check 全數錨定。通才A席說派工詞尾端沒附到固定席筆記(鏡頭沒接上),本輪沒有逐節點判讀——下一輪派工前一刻再暖一次快取。

id 對照:a=架構對齊-sonnet(F1–F6)、g=通才A-sonnet(F1)、b=通才B-sonnet(F1–F4)。

### 依根因分組

- 測試釘不住條款(b1 恆真斷言、b2 七處沒驗到,兩條 major,席位在 clone 逐一改壞實作附輸出):補測試、改掉恆真斷言;編排者翻紅驗證新加 8 處全紅。折。
- 重造鄰居已有的小工具(a1 major、a2):改走 `_nodehome_git`/`_nodehome_split_z`、`_lens_full_sha`(加 --end-of-options)、`_sha256_file`。折。
- 輸入錯變當掉(g1 空字元):讀紀錄時擋、回 2。折。
- 設定讀不懂沒警告(a6):補警告。折。
- 測試夾具繼承外面的跳過變數(b3):夾具清掉 LUMOS_SKIP_*。折。

### 放行

- a3(處置範本小函式重算 --round/--tier,record_cmd 仍用舊的一份):record_cmd 的字面有既有測試釘著,這次只把處置範本收成一支,兩份旗標算法一致;不擴大改動。
- a4(⚠ 檔內第一個 __enter__ 類別):類別讓 ok/err/path 三個結果有名字,guard kill 與修正關卡都直接讀屬性;contextmanager 版要 yield 元組,且檔頂沒有 contextlib 匯入——兩種寫法等價,不構成第二種做法。
- a5(⚠ 清殘骸借用 lint 的時限常數):計劃明定「同前綴、超過 _LINT_NEW_STALE_SEC 就清」沿用同一個時限,不另訂。
- b4(手冊、速查、筆記與主程式對照一致;S5 字面寫 no-config 判不過、實作設定壞會在先決條件更早回 2):實作對 no-config 仍判不過,只是設定壞多半在先決條件先擋下;無須動作。

### 機械重現不到

無。
