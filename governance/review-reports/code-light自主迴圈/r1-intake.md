# r1 收貨(2026-09-18;standard:通才 + 架構對齊)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| G1 | 單reviewer-sonnet | major | HIT:改 app/db.py 函式體一行,pitfalls 給 affected_keys=[]、light_ok=true;掛鉤只跑自主迴圈一條、沒有任何提示 | 折:lumos `_autoloop_full_for`:抽不出關鍵字就整支跑;斷言 ⑩b |
| G2 | 單reviewer-sonnet | minor | HIT:grep -qw 把 key 裡的 . 當萬用字元 | 折:同 A1(掛鉤不再自己比對) |
| A1 | 架構對齊-sonnet | major | HIT:同一個 key "main.py",執行器 re.escape 判不命中、掛鉤 grep -qw 判命中 | 折:整字比對收成 lumos `_keys_mentioned` 一支;執行器 `--suite keys` 改用它;pitfalls 多 autoloop_full 欄,掛鉤只讀結果、不再 grep;斷言 ⑩a 與接線「掛鉤裡沒有 grep -qw」 |
