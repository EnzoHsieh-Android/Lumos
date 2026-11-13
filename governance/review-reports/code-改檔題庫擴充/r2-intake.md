# r2 收貨紀錄

兩席(單reviewer-r2-sonnet、架構對齊-r2-sonnet)同輪交回後一次寫進卷證;`git status` 確認 repo 沒被審查席動過。完成通知把 `>=` 轉成跳脫字元,存檔時照原字還原(引句才錨得到)。架構對齊席報告全數錨定;單審查員那條的引句是執行輸出、不在凍結快照,quote-check 判錨不到,改由編排者機械重現(見 `r2-repro.txt`),重現得出才採信。

## 重現表

| id | 結果 | 說明 |
|---|---|---|
| R2-1 | HIT | 沒有掛鉤時 `--append` 拋 FileNotFoundError,題庫檔未動;裸跑防護照樣擋下(`r2-repro.txt`) |

## 判讀

| id | 席 | severity | 判讀 | 去向 |
|---|---|---|---|---|
| R2-1 | 單reviewer-r2-sonnet | minor | 屬實;修前 d613ce4f 也是延後載入、同樣會崩,席位歸因「原有漏查」,不是修補回歸 | 放行 |
| F1 | 架構對齊-r2-sonnet | minor | 屬實;`HOOK` 與 `ROOT` 算的是同一個根,值相同,行為無差 | 放行 |
| F2 | 架構對齊-r2-sonnet | minor | 屬實但刻意:`_run_append` 的預先過濾是為了省下每題兩次影響查詢,最後把關在 `append_edit_cases`,註解已寫明;資料結構已共用 `_edit_quota` | 放行 |

放行理由:三條都是 minor、本輪沒有 major 或 blocker 席;都不影響出題結果或題庫資料;再修要開第 3 輪(上限)。

修補因果:本輪三條都不是 r1 修補造成——R2-1 修前同樣崩潰(席位讀修前原始碼比對、編排者重現修後),F1、F2 兩行在修前 d613ce4f 就已存在(`git show d613ce4f5:governance/eval/build_goldset.py` 可見 `HOOK =` 定義與 `_run_append` 預先過濾)。regression_set 填 none。

## 先查世界

本輪三條全放行、沒有修補,不適用。
