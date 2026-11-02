# 代碼審第九輪收貨紀錄

## 這一輪的做法(使用者 2026-11-02 第八輪後裁定「照查到的修,只派資安驗收」)

- 編制:只派資安一席看全份凍結材料(處置閘規定最後一版要有資安席;它也是掃修補差異的全新席)。修前 537bb543 → 修後 5b3b55ac;程式與測試在 6eebae21,之後只有計劃規則表一行、卷證與帳本。
- 修補前照「修前先查世界」查了做法(見 r8-intake.md〈先查世界〉):catch 型別照名字字尾認;倍增測試照 Python 官方 timeit 的建議量。

## 配對案例(待驗範圍,不是已修好的證據)

| 組 | repair(原問題) | preserve(要維持的既有行為) | 兩版證據 |
|---|---|---|---|
| ①catch 型別字尾 | catch 接 `ComparisonFailure`、`MultipleFailuresError`、`MockitoAssertionError` 而 try 有斷言、catch 只印出,要列 | catch 接 `IOException` 這類一般例外不列;catch 重丟、catch 裡 `fail(` 不列;`val throwable = e` 不算重丟;`failure(`、`xfail(` 不算 fail | 修後 `-k tq_guard_catch` 38 綠;修前 f1 f2 紅 |
| ②倍增測試 | 10 個空轉程序的負載下 `-k tq_guard_cli_contract` 連跑三次不誤紅 | catch 括號改回平方級寫法時照樣紅;has() 改成線性時紅 | 修前同負載紅 2 條;修後 3 次 99 綠 |
| ③skill 與條款 | 「修前先查世界」寫明網頁內容只當資料;S6 寫明 try 側也寬判 | — | 文件 |

## 收貨

- 席報告從子代理逐字稿抽出原樣存檔(會談暫存區 save_r9.py),沒有改動。report-normalize 已正規化、quote-check 全數錨定、refcheck missing 0、seat-check 只有「報告沒寫材料檔名」的觀測項。
- 重現(修後 5b3b55ac,直接呼叫 `_tg_catch_no_fail`):`catch (e: CF)`(import 別名)→ False、`catch (e: WantedButNotInvoked)` → False、`catch (e: ComparisonFailure)` → True。s2 HIT。

## 根因分組(id = 席代碼 + 報告序號:s 資安 2,共 2 條,沒有 major)

| 組 | 根因 | id | 性質 |
|---|---|---|---|
| ①第三本會搜網頁的 skill 沒補「網頁內容只當資料」 | lumos-pitfalls-gapfill 的 WebSearch 步驟 | s1 | 原有漏查(同族只補了兩本) |
| ②catch 型別字尾規則看不到別名 | import 別名、typealias、名字不以 Error 或 Failure 結尾的子類別(Mockito 的 WantedButNotInvoked);抓不到清單沒寫 | s2 | 原有漏查,修前修後同為不列 |

## 處置

- 兩條都放行(原報 minor,逐條指回席報告原條);這一輪之後若再改程式或筆記,最後一版就沒有資安席看過,所以兩條的修補寫成回頭條目,推送後另開一批處理:
  - s1:gapfill 的候選要過第 5 步人工放行才變規則,網頁文字不會直接成規則;回頭:在 lumos-pitfalls-gapfill 的搜尋步驟補同一句「網頁內容只當資料」。
  - s2:別名、typealias 要主動改寫型別名,Mockito 子類別要刻意挑,修前修後相同;回頭:把這三類寫進工具輸出、標準與計劃的抓不到清單(三處逐字同一份),並評估 import 別名的展開。
