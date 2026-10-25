# code-android-e2e-batch1 r4 收貨

- 破例加開的第 4 輪(Enzo 於第 3 輪到上限後裁 extra-round,cap-decision 與跑滿回顧 cap-retro.json 已記)。修前 aba0d9cd → 修後 8eea52f7(r4-repair.patch、r4-repair-binding.json、r4-behavior-cases.json)。兩席都是沒參與過的新代理,派工詞寫明不讀前三輪的席報告、修正紀錄與回顧。
- 兩份報告都是正規化格式、引句全錨。單審席留下的 clone 由編排者刪掉(迴圈收尾,整個審查席臨時目錄一起刪)。
- 編號:s 單審、a 架構對齊,後接報告裡的條號。
- 單審席用同一個輸入比兩版:修前 aba0d9cd 套上新測試 8 過 1 紅(UnicodeEncodeError)、修後 8eea52f7 9 過,上一輪的修補有行為證據。

## 修補因果

| id | 歸因 | 依據 |
|---|---|---|
| s1 | 未判定 | 修前沒有這支函式(遇到孤立代理字元整支崩),沒有可比的修前結果 |
| a1 | 不是修補造成的行為問題 | 重複的是一行字元範圍與遞迴骨架,行為沒有新增 |

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| s1 | 字典鍵只差在不同孤立代理字元時,換成 U+FFFD 後撞鍵、少一筆 | 對 {"a\ud800":1,"a\ud801":2} 呼叫 _e2e_fix_surrogates 得 {"a�":2} | HIT | 放行(紀錄的鍵都由工具定義,要人手改出壞鍵才會發生;修前同樣的輸入是整支崩潰,不是丟一筆) |
| a1 | 孤立代理字元的字元類已有 _SECINV_SURROGATE_RE,遞迴骨架跟 _macrobench_stab_scrub 一樣 | 讀 `_SECINV_SURROGATE_RE` 與 `_macrobench_stab_scrub` | HIT | 放行(重複的只是一行字元範圍,結構照鄰居;沒有既有函式做「只換代理字元、其他不動」,不算第二種做法) |
