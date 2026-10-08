# 設計審第 3 輪(上限輪)收貨紀錄:殺傷力配方失配提醒

6 席全收齊後才動計劃;四道機械檢查全正規化、全錨定;reflog 無異動。finding 編號:k=併發、a=架構對齊、h=接手、r=回滾、b=邊界、c=正確性,後接 F 編號。全部折進計劃。

| 編號 | 等級 | 折在哪 |
|---|---|---|
| k1 | major | 做法 3、4 kill-add 與 kill-rm 都上 `_vault_write_lock` |
| a1 b2 c1 | major/minor | 做法 1 解析器照「暫存資料夾/wt」重演:迴圈與長鏈算開檔失敗(missing)、經 wt 爬回來算在內 |
| a2 b1 | minor/major | 做法 1 解析結果等於 wt 本身 → outside |
| h1 | major | RETIRE-IF 只看 rtb 兩次回報 |
| r1 r2 | minor | 實務隱患〈文件測試〉兩個注意點 |
| b3 | minor | 做法 1 `.`、空段、不存在的中間段、尾端斜線的語意 |
| b4 | major | 做法 3 判斷包例外保護 |
| b5 | major | 做法 4 kill-rm 寫後自驗自己寫一支 |
| c2 | minor | S5 每格獨立 repo 與筆記 |
| c3 | minor | 做法 1 不在 git 追蹤清單(沒提交、被忽略、子模組)→ missing;誠實界線改寫 |
| c4 | minor | S4 設定錯誤字面跟整段兜底分開 |
| c5 | minor | 做法 1 路徑不存在 → missing;做法 3 判斷包例外保護 |
| c6 | minor | PRIOR-ART 改成解析器說法 |
| c7 | minor | 做法 4 移除多條時逐條印完整內容 |

重現不到而沒折的:無。放行的:無。
