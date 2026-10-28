# 第四輪收貨(人裁加開的一輪)

兩席(單審-sonnet、架構對齊-sonnet,都是沒參與前三輪的新代理)報告到齊後一次寫入;refcheck 全 ok;兩份都已是正規化格式;審查席沒動 repo(git status 只有工具自己寫的治理帳、reflog 最後一筆是編排者的卷證提交),席位臨時目錄已刪。架構對齊席 clean。單審席 F1 的引句跨兩行,quote-check 錨不到,照規矩先機械重現。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| v1 | 編排者在工作目錄把 runs.popitem(last=False) 改成 last=True,跑 -k android_e2e_flaky_history:14 passed, 0 failed(照綠);還原後 cmp 確認 | HIT |
| v2 | 讀碼:_e2e_print_runs 的工具問題行、截圖與記憶體行、效能行、提醒行原樣 print,沒過 _out_clean(這幾行在 20e1a255 就是這樣) | HIT |

## 根因分組與出處清單

- 組 I(v1):第三輪新寫的「超過 --last 次執行丟最舊的一次」只有「剛好不超過」的案例,方向與「最近 N 次執行」那句的數字都沒被斷言。補兩條:A、B、C(C 第二次才過)--last 2 要列出 C;D、E、E(E 重判)--last 2 要說「最近 2 次執行」沒有。改壞成丟最新、改成數行數,各自翻紅。
- 組 J(v2):judge 印給人看的結果在同一個函式裡有八個印出點,第三輪只把 UI 行改成過 _out_clean。這次在 _e2e_print_runs 裡收成一個 say(),每一行都過 _out_clean;測試的假結果補上帶控制字元的工具問題、截圖畫面名與提醒。出處清單:_e2e_print_runs 全部 print(已全改);history 行、--flaky 行、點名行第二、三輪已是整行出口。lumos 其他子命令(例如 android-e2e select、gate)的輸出不在這次改動範圍,沒動。

## 正式發現處置

| ID | 來源 | 結果 | 處置 |
|---|---|---|---|
| v1 | 單審 F1(major) | HIT(引句跨行錨不到,機械重現成立) | 折:組 I |
| v2 | 單審 F2(minor) | HIT | 折:組 J |

兩項全折;refuted 為 none。

## 修補因果

- v1:有證據的修復回歸——popitem 那段是第三輪修補新寫的(r4-repair.patch),修前用 deque(maxlen) 由標準庫保證方向;產品行為修前修後都對(席位兩版實跑),缺的是測試。
- v2:原有漏查——那幾行在功能提交之前就原樣印出(席位用 745721d8 與 e98debe1 兩版輸出相同)。

## 修補後自查

- 改壞驗證三道全紅(見 r4-repro.txt)。
- 專案 ruff 設定比對修補前後沒有新增告警。
