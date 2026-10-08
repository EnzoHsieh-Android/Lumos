# code-筆記測試綁定要存在 r3 收貨紀錄(2026-10-03,standard 末輪:通才-opus+架構對齊-sonnet,只看 r2 修正差異)

機械:兩份 report-normalize 已正規;quote-check --spec r3-snapshot.patch 全錨定;refcheck 全 ok。

編號:g1–g2 = r3-通才-opus.md F1–F2;a1–a2 = r3-架構對齊-sonnet.md F1–F2。共 4 條,全 minor、blocking 0。

| id | 怎麼試 | 結果 |
|---|---|---|
| g1 | 先紅 t_note_shape_test_refs_line_attribution ⑦:test_x/FooTest.test_x、t_p/ios:t_p、work/should-work 三種在舊行都記成新 | HIT |
| g2 | 席位突變:刪掉新加的提醒句,原斷言照綠;改緊後同一突變翻紅 | HIT |
| a1 | 讀碼:_ns_tr_is_new 內嵌冒號正規化,沒重用 _test_names_of | 採信 |
| a2 | 讀碼:整字邊界跟 _keys_mentioned 兩套 | 採信 |

處置:4 條全折。g1 同一類第三次(r1、r2 也是帳本 new 找行),照「同類兩輪換形狀」改成用產生名稱的同一套切分逐行解名稱清單,a1、a2 的正則跟著拿掉;g2 斷言改比對那句提醒的字,另驗之後的名稱回 skip。兩個突變(找行改回子字串、刪掉提醒句)各自翻紅。迴圈到上限,這輪修正沒有再派新席。
回歸(上一輪修補造成的):g2、a1、a2——都是 r2 修正時新寫的東西;g1 是同一類的殘留,不是 r2 引入的。
