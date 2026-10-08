# code-lumos事件帳 r1 收貨紀錄

- 六席報告(正確性、併發資源、邊界輸入、合約圖譜、架構對齊、資安;外家 finder 與外家否決依 Enzo 2026-10-05 指示缺席)全數格式正規化、引句全數錨定 r1-snapshot.patch。
- 編排者格式調整(只動格式、不動內容):邊界輸入席原稿引句行前的列表符號「- 」拿掉;邊界輸入席總結句以 `report-normalize --write` 拆行;正確性席 F2 原稿含一個 U+2028 字元、傳遞時顯示成換行,存檔改寫成字元代號並在原處註明。
- 兩席(正確性、邊界輸入)報固定席沒附上,派工鏡頭快取在派工時可能已過期;合約圖譜席自行跑 impact 逐條答了固定席,架構對齊席有收到。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| c1 / e1 | claude 列表吐 null 時 install、uninstall 丟 TypeError | 新測試 t_ledger_plugin_bad_json_and_races 先紅:`EXC TypeError`(null、42),`{}`、`[1, 2]` 誤判 ok | HIT | 折 |
| k1 | bootstrap --lumos-home 沒傳進安裝子行程 | 新測試 t_ledger_plugin_messages_and_bootstrap 先紅:假 claude 沒收到任何 marketplace add | HIT | 折 |
| a1 | 另寫 repo 根解析、壞 --repo 誤報沒有事件帳 | 新測試 t_events_session_name_and_repo_validation 先紅:rc=0 印「沒有事件帳」 | HIT | 折 |
| e2 / s2 / k4 | --session 可跳出事件帳資料夾、空字串與連結行為不一 | 同上先紅:絕對路徑讀到外面事件、空字串 rc0 列全部、LNK rc0 | HIT | 折 |
| c2 / c3 / e3 / s1 | U+2028 斷行、缺 ok 標 ✗、v:true 當 1、控制字元原樣印 | 新測試 t_events_reader_edge_lines 先紅 5 條 | HIT | 折 |
| c4 / k7 / p1 / s3 | --days 超大 OverflowError、刪失敗中斷、上層連結導到 repo 外 | 新測試 t_events_prune_edge_cases 先紅 5 條 | HIT | 折 |
| k5 | 專案範圍裝過就不裝使用者層 | t_ledger_plugin_bad_json_and_races 的範圍案例先紅 | HIT | 折 |
| p2 / p3 | 先移除後加失敗沒有救援訊息;兩支 install 同時跑 | 同上的救援訊息與「做完卻回錯」案例先紅 | HIT | 折 |
