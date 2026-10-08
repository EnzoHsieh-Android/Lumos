# 筆記測試綁定要存在 r2 收貨紀錄(2026-10-02,4 席)

機械:四份 report-normalize 已正規;quote-check --spec r2-snapshot.md:正確性、整合、架構對齊全錨定,邊界 F8 引句「自己的寬鬆正則」不足 10 字錨不到(該條講自寫正則的平方時間,本輪改用 slot_parse 後整條不成立,隨形狀改變一起處理);refcheck 整合 2 條 missing 是縮寫路徑、架構對齊 1 條行號超出(佐證行,不是發現依據)。

編號:o1–o8 = r2-正確性-opus.md F1–F8;e1–e9 = r2-邊界-sonnet.md F1–F9;g1–g10 = r2-整合-sonnet.md F1–F10;h1–h6 = r2-架構對齊-sonnet.md F1–F6。blocking 14(o 4、e 4、g 4、h 2)。

| id | 怎麼試 | 結果 |
|---|---|---|
| h1 / e1 / g1 / o3 | 席位實測:`git grep -w -F` 不限檔案時對不存在的名稱命中計劃筆記與帳本;加 `_dispositions_check_test` 的副檔名與排除後不命中 | HIT(兩席實測一致) |
| e2 | 席位實測:被測函式名在測試檔整字找得到(3/5) | HIT |
| o1 / e3 / g4 | 正確性席小 repo 重現:合過主線後推送,主線那段的名稱算成新加 | HIT |
| o2 | 讀碼:`_classify_test_refs` 對 Class.Method 只看方法名,grep 拿整串 | HIT |
| o4 | 正確性席實測:新文法 PITFALL 只把 test 改成 test-gone,格子當舊行放行 | HIT |
| e4 / o6 / h3 / g10 | 讀碼:`_ns_text_key` 存在、逐字比對遇重排折行差一個空白 | HIT |
| h2 | 讀碼:`slot_parse` 吃任意字串、已處理全形冒號與反引號 | HIT |
| g3 / h6 | 讀碼:推送時單次跳過在讀範圍前返回 | HIT |
| 其餘 minor | 讀碼核對 | 採信 |

處置:33 條全折,無放行、無駁回。判新加與判存在兩類 r1 已換過形狀、r2 又出 major,照「同類兩輪換形狀」改用外層既有機制(`_notelines_new`、`_dispositions_check_test`、`slot_parse`),見計劃〈審計修正紀錄〉r2;提交時改回只提醒(o8 與 Enzo 原裁)。regression-set:o1、e3、g4(r1 改的兩側相減造成)、h1、e1、g1、o3、e2(r1 新增的 grep 複查造成)、o4(r1 把 test-gone 登記成鍵造成)。

另外(不是席位發現,rtb 2026-10-02 清理回傳 return-to-toolchain.md 第 3.1 節 5、10 項):1c 原本略過條款定義行,會漏掉 rtb 那 12 條(就是計劃條款)→ 1c 照查條款行與合約行(S24);`[test:browser:…]` 是人工驗證 → 擋下訊息提示改用 `[manual:]`(S25)。
