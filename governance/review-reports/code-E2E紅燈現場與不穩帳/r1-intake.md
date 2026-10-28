# 第一輪收貨

兩席(單審-sonnet、架構對齊-sonnet)報告到齊後一次寫入;引句全數錨定、refcheck 全 ok、審查席沒動 repo(git status、reflog 核過)。單審席原報告最後一行總結句被收貨工具當成第二個嚴重度宣告,退回該席只改那一行重交,其他字未動。

## 正式發現處置

| ID | 來源 | 重現與證據 | 結果 | 處置 |
|---|---|---|---|---|
| u1 | 單審 F1(major) | 編排者讀碼確認:按情境跑時總表 case_results 的項目由 _e2e_case_results 重組、不帶 flaky;新斷言修前紅(history --flaky --case 印「沒有第二次才過」、history --case 那行少「第二次才過」) | HIT | 折:總表寫 case_results 時照整次 UI 結果補 flaky(查證紀錄那份不帶,照計劃〈不做〉);S4、S6 條款與綁定測試補情境那份 |
| u2 | 單審 F2(minor) | 新斷言修前紅:同一 run 目錄重判兩次後 history --flaky 印 3 次裡 3 次、點名被湊到 | HIT | 折:不穩帳窗口依 run_id 去重(同一次執行只算最後一行);S5、S6 條款補這句 |
| a1 | 架構 F1(minor) | 讀碼確認點名與 history --flaky 各寫一份篩選 | HIT | 折:抽成 _e2e_ui_judged 共用;改壞成只判 dict 時原測試不紅,另補「沒判到不算進分母」斷言 |
| a2 | 架構 F2(minor) | 讀碼確認兩支腳本的 date 格式沒有比對守衛 | HIT | 折:測試抽出兩支腳本的 date 格式比相等,改壞一邊會紅 |
| a3 | 架構 F3(minor) | 讀碼確認 judge 的 evidence 是一串路徑、印時靠 .crash.txt 結尾分 | HIT | 折:judge 改帶 {dirs, crashes} 兩欄,印時照欄位;測試用不照慣例的閃退檔名驗 |
| a4 | 架構 F4(minor) | 新斷言修前紅:一般 history 的第二次才過清單印出控制字元 | HIT | 折:點名與 history 清單的 flow 名稱都過 _out_clean |
| a5 | 架構 F5(minor) | 讀碼確認 UI 迴圈在 step() 外改最後一步再存 | HIT | 折:step() 加 after(rc) 併進同一筆、只存一次;改壞成不併時 S2 測試紅 |

七項全折,未降級、未放行、沒有機械重現不到的(refuted 為 none)。

## 修補後自查

- 依全域規則對大輸入量測:十萬筆總表、`history --flaky --last 20000` 第一版去重寫法 49.5 秒(每筆掃整個窗口,平方級),改成另記窗口裡的 run_id 只在撞到重判時才掃,降到 1.9 秒;點名那條路十萬筆 1.6 秒;記憶體與改動前同基準(約 344MB,工具本身)。總表照舊逐行讀、不整本載入。
- 用專案 ruff 設定比對修補前後,沒有新增告警。
- 每道新守衛各改壞一次,都翻紅(共 10 次)。
