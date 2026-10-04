# r2 收貨(code-數量標記檢查-2)

收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;兩席都沒動 repo(實驗在 /tmp/count-r2-work)。report-normalize 不用改;quote-check 全數錨定;refcheck 對得上。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 跑 /tmp/count-r2-work/t4.py 的 multi / tuple / ifbody | HIT:A = B = 1 數成 0(實際 1)、A, B = 1, 2 數成 0(實際 2)、if 區塊裡的成員數成 1(實際 2) |
| F2 | t4.py 的 autodup / autoflag | HIT:IntEnum auto() 撞 1 數成 2(實際 1)、Flag 數成 3(實際 2) |
| F3 | t4.py 的 globalrebind / tryrebind / unpack / del / setattr | HIT:都回 3,實際 1、刪掉或 4 |
| F4 | t1.py:標籤後有未閉合反引號、雙反引號裡的數字 | HIT:改到看不見的數字,重抽照樣通過 |
| F5 | 報告的 `2026-10-04 起共十種 [count:a.py::X=10]` | HIT:日期的月份被改成 11 |
| Z1 | 讀 `prefetch` 與 `prefetch_paths` | HIT:收尾那一行重複 |
| Z2 | 讀 `_count_eval` 與 `_drift_py_names` 的例外清單 | HIT:少接 MemoryError |

## 依根因分組與處置(本輪有 major,全折)

- 甲「看不懂的寫法被略過、當成沒有」(F1–F3):列舉本體只認方法、pass、說明字串與單一名稱指派,其餘判不了;auto() 混明寫值判不了;名稱在模組這一層被寫入超過定義那一次、被 global/nonlocal 宣告、被 import 或同名 def/class 蓋掉、呼叫只讀白名單以外的方法、下標賦值或刪除,一律判不了。原則寫進計劃與家節點:看不懂就判不了,不略過、不模擬。
- 乙「看得見的判定兩套」(F4、F5):drift fix 的看得見判定改用跟抽標籤同一套(雙反引號、單反引號、未閉合反引號之後),句子數字前後不能是英數字、底線、點、斜線、冒號、連字號(日期、分數、時間裡的數字不算)。
- 丙 架構對齊(Z1、Z2):prefetch 改呼叫 prefetch_paths;解析接 MemoryError。
- 副作用:測試夾具的 Color 原本混用 auto() 與明寫值,新規則判不了(正確),夾具改成全 auto();類別裡同名屬性原本被算成重新綁定模組名稱,名稱寫入改成只看模組這一層。
