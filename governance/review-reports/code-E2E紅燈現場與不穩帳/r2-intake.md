# 第二輪收貨

兩席(單審-sonnet、架構對齊-sonnet,都是沒參與第一輪的新代理)報告到齊後一次寫入;引句全數錨定、refcheck 全 ok(2、21 處)、兩份都已是正規化格式;審查席沒動 repo(git status 只有編排者自己的第二輪材料、reflog 最後一筆是編排者的 amend),席位臨時目錄已刪。

## 根因分組

- 組 A(s1、s2、b1):第一輪為了「同一次執行重判只算一次」自寫的窗口去重。列級去重讓被擋下的空重判行蓋掉真判定(s1),重判多時逐筆掃窗口變平方級(s2),而且是同檔 _ci_latest_attempts 之外的第二套「同 run_id 留最後」(b1)。統一修法:點名與 history --flaky 共用一支 _e2e_flaky_tally,每支 flow 用 OrderedDict 以執行鍵記「最後一個判出結果的那次」,run_id 照 _ci_latest_attempts 的口徑轉字串;_ci_latest_attempts 是 CI 的「嘗試次數大的贏、同一次取比較糟的結論」、吃整份清單、掛鉤裡有逐字複本,語意不同不共用,理由寫進 Systems/android-e2e-acceptance 的 WHY 與函式說明。出處清單:_e2e_flaky_counts、_e2e_flaky_report、_e2e_history_cmd(--flaky 分支)三處呼叫點全改,_e2e_window_put 刪除。
- 組 B(b3):外來文字清理只蓋新增的欄位。統一規則:從總表讀出的整行在印出口過一次 _out_clean。出處清單:_e2e_history_line、_e2e_flaky_report、_e2e_flaky_notify、_e2e_print_runs 的 UI 行。
- 組 C(b4):evidence 一個鍵三種形狀。judge UI 結果改名 fail_evidence;steps.json 每次嘗試的 evidence 與總表的 evidence(run 目錄,這次之前就有)不動。出處清單:_e2e_judge_ui、_e2e_print_runs、_e2e_judge_ui 說明、計劃〈一次 UI 流程多留什麼〉第 4 步;skill、README 沒寫這個鍵(grep 過)。
- 組 D(b2):情境項目在寫總表處補 flaky。保留這個位置(查證紀錄綁版本、不放不穩帳是計劃〈不做〉的規則,補在產生處就得在寫查證紀錄時再拿掉),在 _e2e_case_results 說明加一句指過去,加欄位時一起看。
- 組 E(b5):step() 的 after 回呼是第一輪修補引入的第二種機制。第一輪架構對齊席嫌「在 step() 外改最後一步再存」,這一輪架構對齊席指出那正是這支腳本既有的慣例(collector_override 同樣直接補進 st.data 再存),而且回呼丟例外時那一步整筆不進 steps.json。兩輪意見相反;照腳本既有慣例改回直接補欄位再存,step() 拿掉 after,註解寫明這一步已先存過、收閃退紀錄出錯也不會丟掉它。

## 正式發現處置

| ID | 來源 | 重現與證據 | 結果 | 處置 |
|---|---|---|---|---|
| s1 | 單審 F1(minor) | 新斷言修前紅:同一 R1 先判出第二次才過、再寫一行項目空的重判,history --flaky 印「沒有第二次才過」 | HIT | 折:組 A |
| s2 | 單審 F2(minor) | 編排者實測:十萬行、每個 run_id 兩行、--last 100000,修後 2.63 秒;席位量到修前 2 萬行 1.7 秒、每翻倍乘 4 | HIT | 折:組 A |
| b1 | 架構 F1(major) | 讀碼確認 _e2e_window_put 與 _ci_latest_attempts 都是「同 run_id 留最後」、run_id 口徑不同(只認字串 vs 轉字串) | HIT | 折:組 A;新斷言(數字與字串 run_id 算同一次)修前紅 |
| b2 | 架構 F2(minor) | 讀碼確認 | HIT | 折:組 D |
| b3 | 架構 F3(minor) | 新斷言修前紅:一般 history 的「沒過或沒判完」清單印出控制字元 | HIT | 折:組 B |
| b4 | 架構 F4(minor) | 讀碼確認;judge 測試改讀 fail_evidence 修前紅 | HIT | 折:組 C |
| b5 | 架構 F5(minor) | 讀碼確認 | HIT | 折:組 E |

七項全折,未降級、未放行;refuted 為 none。

## 修補因果

- s1、s2、b1、b2、b3、b5:有證據的修復回歸——出問題的程式(_e2e_window_put、case_results 補欄位、只清新欄位、after 回呼)都是第一輪修補才加的,修前版本 4e26f7bf 沒有這些行(r2-repair.patch);s1 另有單審席的兩版輸出(修前 1 次裡 1 次、修後沒有)。
- b4:原有漏查——judge 的 evidence 鍵在功能提交就叫 evidence(當時是一串路徑),第一輪改成兩欄但沒改名,三種形狀並存在修前就有。

## 修補後自查

- 每道新守衛改壞一次(見 r2-repro.txt):od 的執行鍵不轉字串、拿掉判出判斷、拿掉窗口上限、拿掉整行清理(兩處)、judge 讀回舊鍵,都翻紅;「同一次執行換到最後」那行拿掉不紅——查明它只影響排列、不影響計數,是多餘的,已刪;flows 篩選拿掉不紅是等價變異(結果本來就只取 flows,篩選只省記憶體)。
- 大輸入:十萬行全部重判過,history --flaky --last 100000 2.63 秒(佔 876MB,與要求留的筆數成正比;預設 20 筆不受影響);點名那條路 3.87 秒、峰值 297KB(逐行讀)。
- 專案 ruff 設定比對修補前後:沒有新增告警(測試裡 import 拆成兩行,避開 I001)。
- 未驗:點名那行與 judge UI 行的整行清理沒有專門測試(假環境造不出名稱帶控制字元的 flow 檔)。
