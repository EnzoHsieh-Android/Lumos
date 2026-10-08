# code r1 收貨紀錄(併發與效能表態背書)

## 收貨三道(八席)

- report-normalize:四份(併發資源、邊界輸入、合約圖譜、通才)總結句寫成「max severity:」被當成嚴重度宣告,編排者只把總結句開頭改成「最高嚴重度:」,嚴重度值與內容不動;其餘四份已正規化。
- quote-check(對 r1-snapshot.patch):七份全數錨定;對答案席六條中四條引的是計劃原文不是 patch,見下表機械重現。
- refcheck:八份引的 file:line 全部存在。

## 編排者重現

| 席位 id | 重現 | 結果 |
|---|---|---|
| C1 C2 C3 C4 C5 C6 | 對答案席引句逐字 grep 審查當時的計劃(git show HEAD 的計劃檔),六句各命中 1 次 | HIT 採信 |
| N1 | gov --stats 預設窗口 90 天、測試 ts 寫死;加 --since 9999 後綠 | HIT 採信 |
| K2 B4 | `_backing_judge_groups` 對缺 weak 的行 KeyError(席位直接呼叫重現) | HIT 採信 |
| AA4 AA5 | repo 既有讀法 `cmd_canary_second`、`_jsonl_append_verified` 皆 errors=replace 逐行讀;既有追加寫者都不補換行 | HIT 採信 |
| B1 B2 B3 | 席位在臨時 clone 改壞程式後測試照綠 | HIT 採信 |

refuted-set:none。整輪有 major 席(通才、架構對齊),依規則 accepted 必空,全部折入。

## 折入備註

- G2(guard-kill 的 FLOW 行沒提新欄位):改 FLOW 行被筆記形狀擋擋下(FLOW 是程式碼推得出的現況、沒來源不准新寫),改以同篇已寫的 WHY 行記新欄位,FLOW 不動。
