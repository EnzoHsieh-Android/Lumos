# code-macrobench r3 收貨紀錄

| id | 席 | 重現 | 結果 | 歸因 | 去向 |
|---|---|---|---|---|---|
| H1 | 正確性-sonnet | 用 KDS 真結果檔存基準,再把滑動類 P50 改成 NaN 跑 `lumos macrobench` | 印「比了 2 個情境,0 項變慢」,NaN 沒被報,HIT;引句引的是既有的數值判斷函式、不在凍結快照內,quote-check 錨不到,以機械重現採信 | 原有漏查(席位修前修後兩版同結果) | 放行 |
| K1 | 架構對齊-sonnet | 對照 compose-metrics 與 macrobench 的 JSON 鍵名與 failed 項形狀 | 鍵名不同,HIT | 原有(第一輪起就是這個形狀,第一輪 A2 已放行同一件事) | 放行 |
| K2 | 架構對齊-sonnet | 讀方法論文件的轉接工具總表 | 沒有 macrobench 一列,HIT | 原有漏查(第一輪起就沒補) | 放行 |

regression-set:none——本輪三條都有兩版或歷史證據顯示不是上一輪修補造成的。
