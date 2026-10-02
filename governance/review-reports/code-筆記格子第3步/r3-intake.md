# code-筆記格子第3步 r3 收貨(上限輪)

審材:r2 修正差異(r3-snapshot.patch)。七席(5 席+架構對齊+資安)全部 blocking 0、沒有 major;上一輪的修正各席逐項驗收都成立(架構對齊席:第二套 stderr 處理、S16 第二條讀法、fail-open 寫法、先記後印與鄰居相反四條都收斂)。共 19 條 minor。
這是 high 的上限輪(3/3),照末輪規矩新 minor 附理由接受、不觸發折返;要做的歸進 Issues/筆記格子第3步末輪遺留(七項)。
合約圖譜席與正確性席交完報告後各補了一兩則「背景測試跑完」的通知,沒有新內容;存檔用的是完整那份。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| R3B3 | stderr 壞掉時「印到一半出錯」那句 print 再拋、冒出去、帳沒寫 | 席位以會拋 BrokenPipeError 的 stderr 實跑 | HIT | 接受:鄰居 m1 與 c1 到 c5 同樣不防;Issue 第 1 項 |
| R3K1 | 同 R3B3 | 同上 | HIT | 接受;Issue 第 1 項 |
| R3U1 | 同 R3B3 | 同上 | HIT | 接受;Issue 第 1 項 |
| R3G2 | 同 R3B3,筆記「各自只講一句」此時不成立 | 讀程式 | HIT | 接受;Issue 第 1 項(含筆記加限定) |
| R3S1 | S18 fail-open 印例外全文沒清字元 | 讀程式;席位追過例外來源,外人控制不到 | HIT | 接受;Issue 第 2 項 |
| R3C2 | 同 R3S1 | 同上 | HIT | 接受;Issue 第 2 項 |
| R3U2 | 同 R3S1 | 同上 | HIT | 接受;Issue 第 2 項 |
| R3G3 | 同 R3S1 | 同上 | HIT | 接受;Issue 第 2 項 |
| R3A2 | 帳增速段註解還寫 _drift_jsonl_parse | 讀程式 | HIT | 接受;Issue 第 3 項 |
| R3C4 | 筆記與註解的函式名過期、逐筆版說明偏滿 | 讀筆記 | HIT | 接受;Issue 第 3 項 |
| R3G1 | 同 R3C4 | 同上 | HIT | 接受;Issue 第 3 項 |
| R3K2 | 逐筆版只省 dict 清單,整份解碼字串仍在 | 席位 tracemalloc:124MB → 58MB | HIT | 接受:24MB 上限封頂、doctor 人工偶爾跑;Issue 第 3 項 |
| R3B4 | _esc_clean 讓 U+2028 通過(引句錨不到,引的是既有共用函式) | 編排者實跑 _esc_clean('a b‮c\x1bd') → U+2028、U+202E 都在、ESC 被清 | HIT | 接受:既有共用函式、非這次引入;Issue 第 4 項 |
| R3S2 | _esc_clean 不擋雙向文字控制字元 | 同上 | HIT | 接受;Issue 第 4 項 |
| R3B1 | 兩個 summary 鍵時行號取第一個、值取最後一個 | 席位實跑 | HIT | 接受:重複鍵本身是壞 YAML;Issue 第 5 項 |
| R3C3 | 引號跨行與單行接續行仍漏判(改前也漏) | 席位實跑 | HIT | 接受:非回歸;Issue 第 5 項 |
| R3A1 | drift 側不補單行 summary,doctor 側補了 | 讀程式 | HIT | 接受:只會漏判不會誤擋;Issue 第 5 項 |
| R3B2 | 路徑超過 300 字時原因被截掉 | 席位實跑 350 字路徑 | HIT | 接受;Issue 第 6 項 |
| R3C1 | S16 的 _esc_clean 拿掉測試仍綠 | 席位臨時 clone 實跑 | HIT | 接受:行為本身對;Issue 第 7 項 |
