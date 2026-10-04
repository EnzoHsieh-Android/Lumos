# r3 收貨(code-數量標記檢查-2)

收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;兩席都沒動 repo(實驗在 /tmp/count-r3-work)。report-normalize 不用改;quote-check 全數錨定;refcheck 對得上。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 跑 /tmp/count-r3-work/t2.py:標籤裡夾雙反引號或單反引號 | HIT:改寫結果含 \x00,寫前把關只比數字照樣通過 |
| F2 | 跑 repro.py:函式預設值、裝飾器、類別基底裡的海象 | HIT:lumos 回 3,執行後 X 已被換掉 |
| F3 | repro.py:match 捕捉、except as | HIT:lumos 回 3,執行後 X 是 7 或已解除綁定 |
| Z1 | 讀 `_count_visible` 與 `_strip_inline_markup` | HIT:同一套判定寫了兩份,違反「全檔唯一」 |
| Z2 | grep `iter_child_nodes`:只有 `_count_module_nodes` 一處 | HIT:第三種走模組層的寫法 |

## 依根因分組與處置(本輪有 major,全折)

- 甲「列綁定寫法,列一輪漏一輪」(F2、F3,也是 r2 F3 的同一類):改成反過來列「哪些出現方式不算綁定」——讀取、屬性名、關鍵字參數名、字串常數、import 的模組路徑以外,名稱的每次出現都算一次綁定,超過定義那一次就判不了。手寫的模組層走訪 `_count_module_nodes` 因此拿掉(順帶收掉 Z2)。
- 乙「標籤原文取自遮過的字串」(F1):標籤裡夾行內程式碼就擋下;標籤左半改從原行同位置取。
- 丙「行內可見判定兩份」(Z1):抽出唯一本體 `_inline_mask`,`_strip_inline_markup` 與位置不動的 `_inline_visible_mask` 都從它導出;30 萬組隨機輸入跟舊的 `_strip_inline_markup` 結果 0 筆不同,另加 t_inline_visible_single_source 釘兩邊一致。

注:這是 standard 分級的第 3 輪(上限)。本輪修法沒有再派全新席驗收;收斂與否交給人裁(見計劃〈審計修正紀錄〉)。
