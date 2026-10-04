# r1 收貨(code-數量標記檢查)

收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;兩席都沒動 repo(實驗都在 /tmp/count-r1-work)。
report-normalize 不用改;quote-check 全數錨定;refcheck 對得上。雲端環境沒裝派工鏡頭 hook,圖譜固定席由編排者在派工詞裡點名。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 跑席位的 /tmp/count-r1-work/t1.py:Flag A=1 B=2 C=3、Enum _priv=1 X=2、_ignore_ | HIT:F 數成 4(Python 3)、E2 數成 1(Python 2)、E4 數成 2(Python 1) |
| F2 | 跑 e2e.py / e2e2.py:標籤 `KINDS = 5`、`=03` 做 drift fix | HIT:句子改了、標籤沒改,寫入後驗證擋下 rc 2,筆記留在改一半 |
| F3 | e2e.py:句子含 F3、行內程式碼裡有同一個標籤 | HIT:F3 被改成 F4;行內程式碼裡的範例標籤也被改 |
| F4 | e2e.py:標籤數字 5000 位 | HIT:scan 丟 ValueError、rc 1,整個 scan 沒結果 |
| F5 | t1.py:`X = {'a'}` 後 `X |= {'b'}` | HIT:數成 1(執行時 2) |
| Z1 | 臨時 vault:WHY 摘要行寫 `[count:a.py::X=3]` 跑 lint | MISS:沒有未知欄位的提醒,散文行抽欄位跟回頭條件同形,不是新做法 |
| Z2 | grep `lumos:count`:doctor N 段的正規式數量標記與新標籤並存,手冊沒講何時用哪個 | HIT |
| Z3 | 讀 `_drift_fix_load`:`if kind == "count"` 字串特例 | HIT |
| Z4 | 讀 `text_of(*paths)`:多參數只預讀、單參數回文字 | HIT |
| Z5 | 讀 `_count_parse`:回 `err` 字串,鄰居 `_probe_parse` 回 `errs` 清單 | HIT |

## 依根因分組與處置(本輪有 major,全折)

- 甲「Python 的列舉特例自己模擬不全」(F1):底線開頭的名稱、_ignore_、Flag 不是單一位元的值一律判不了,不模擬。
- 乙「改寫靠替換固定字串」(F2、F3):標籤整個重寫成 `[count:路徑::名稱=新值]`;句子裡的數字前後不能是英數字或底線;只改行內程式碼以外那一個標籤;寫之前先重抽改好的那一行,標籤真的是現值才寫。
- 丙「輸入沒設上限」(F4):數字限九位數,超過列成寫錯。
- 丁「只看定義那一句」(F5):整支檔有增量指派、會改內容的方法呼叫、下標賦值或刪除就判不了。
- 戊 架構對齊(Z2–Z5):手冊補一句兩種數量標記各管什麼;載入函式改看宣告的種類集合 `_DRIFT_FIX_SELF_JUDGED`;`text_of` 拆成 `prefetch_paths` 與 `text_of(path)`;解析結果改成 `errs` 清單。Z1 不能重現,駁回。

注:第一筆記帳誤用無輪次格式(編號 code-數量標記檢查,帳不可撤),依 code-loop 手冊「換編號重記」改用 code-數量標記檢查-2、帶 --round。
