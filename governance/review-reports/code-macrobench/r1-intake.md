# code-macrobench r1 收貨紀錄

| id | 席 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | 正確性-sonnet | 把容差改成只在基準大於 0 時按比例算、或把絕對容差寫死成 1,跑 `python3.14 scripts/test_lumos.py -k nonpositive` | 修正前舊測試照綠(席報告);補測試後兩種改壞各紅 2 條、1 條,HIT | 折:補測試 |
| F2 | 正確性-sonnet | 基準檔某項只留 median,跑 `lumos macrobench` | 修正前 rc1、KeyError: 'maximum',HIT | 折:基準檔逐項驗形狀,壞了整份當讀不了 |
| F3 | 正確性-sonnet | 同一份結果檔放兩個子目錄,跑 `--update-baseline` | 修正前印「一個結果檔都沒讀成功」,HIT | 折:訊息分開重複與讀不了,補測試 |
| A1 | 架構對齊-sonnet | 讀 compose-metrics 沒設定檔時的輸出 | 鄰居印空字串,新碼印一句說明,HIT | 放行 |
| A2 | 架構對齊-sonnet | 對照兩個指令的 JSON 鍵名 | 鍵名不同,HIT | 放行 |
| A3 | 架構對齊-sonnet | 對照測試檔既有載入器 | 已有快取版載入器,HIT | 折:改用既有載入器 |
