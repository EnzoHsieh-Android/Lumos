# r3 收貨紀錄(code-回合結束檢查認Codex回合)

- 兩席(審查三、架構對齊三)交回後一次存檔;審查三第一版說明行寫了等級字樣,退回該席只改那一行重交,存檔取自逐字稿;兩份對 r3-snapshot.patch 全數錨定、已是正規化格式。
- 兩席都沒留臨時目錄。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| i1 | 審查三 | minor | 測試 ⑦ 說明寫「讀起點紀錄不接壞檔 → ⑦紅」,但 ⑦ 兩個壞紀錄都不丟例外,拿掉 _read_turn_rec 的例外攔截照綠 | HIT:讀碼,負數時刻是合法 JSON、深層巢狀在 3.14 解成清單,都走不到 except | 折:⑦ 加「不是 JSON」那種壞紀錄;改壞「拿掉 _read_turn_rec 的例外攔截」→ ⑦ 全紅,-k stop_lint 73 passed |
| j1 | 架構對齊三 | minor | _read_turn_rec 定義在呼叫它的 _kept_start 後面,跟檔內先定義被呼叫者的順序不同 | HIT:讀碼 | 折:把 _read_turn_rec 移到 _kept_start 前面,內容不變 |

--regression-set:i1、j1(都出在 r2 修補新加的 ⑦ 與抽出的 _read_turn_rec)。--refuted-set none。

## 先查世界

- PRIOR-ART:i1——Python 3.14 json 模組行為已在 r2 實測(深層巢狀不丟例外);非 JSON 內容丟 ValueError 是標準庫文件寫明的行為(https://docs.python.org/3/library/json.html#json.JSONDecodeError),採用。
- PRIOR-ART:j1——鉤子檔既有寫法,沒有要另查的。
