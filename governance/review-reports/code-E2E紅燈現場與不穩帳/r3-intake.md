# 第三輪收貨

兩席(單審-sonnet、架構對齊-sonnet,都是沒參與前兩輪的新代理)報告到齊後一次寫入;refcheck 全 ok;兩份都已是正規化格式;審查席沒動 repo(git status 只有編排者的第三輪材料、reflog 最後一筆是編排者的卷證提交),席位臨時目錄已刪。單審席 F1 第一句引句「rows = collections.deque(maxlen=last)」在凍結快照錨不到(那一行第二輪改回主線原樣,不在 20e1a255 起算的差異裡),照規矩不直接採信、先機械重現。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| t1 | 編排者造總表 R1(第二次才過)、R2–R5、R5 再兩行,跑 history --flaky --last 5:修後 745721d8 印「最近 5 筆紀錄裡沒有第二次才過的 flow」,修前 150ef621 印「a.yaml  5 次裡 1 次第二次才過」 | HIT |
| t2 | 席位兩個變異(拿掉 judge UI 行與點名行的 _out_clean)測試照綠;編排者讀第二輪處置紀錄的「未驗」那條,確認這兩處當時就沒有測試 | HIT |
| u1 | 讀碼:舊的執行鍵把空字串 run_id 當成沒有 run_id,_ci_latest_attempts 只看 None | HIT |

## 根因分組與出處清單

- 組 F(t1):第二輪把去重移進 _e2e_flaky_tally 之後,_e2e_history_cmd 仍先用 deque(maxlen=last) 截原始行、再交給 tally,重判多寫的行佔走 --last 名額。修法:--flaky 時按執行歸併(OrderedDict 以 _e2e_run_key 為鍵、每次執行留全部行),超過 --last 次執行才丟最舊的一次;tally 照舊判每支 flow 最後一個判出結果。出處清單:_e2e_history_cmd 的 --flaky 分支、_e2e_flaky_report 的「沒有」那句(改成「最近 N 次執行」)、計劃〈不穩帳〉第 3 步與 S6 條款、Systems/android-e2e-acceptance 那條 WHY;點名那條路(_e2e_flaky_counts)本來就按 flow 窗口數不同執行,不受影響。
- 組 G(t2):整行清理的四個出口只有兩個有測試。補 judge UI 行(_e2e_print_runs)與點名行(_e2e_flaky_notify)各一條控制字元斷言(直接載入模組呼叫,假環境造不出名稱帶控制字元的 flow 檔);四個出口現在都有測試。
- 組 H(u1):執行鍵抽成 _e2e_run_key,只有 None 算沒有 run_id、其餘轉字串比,跟 _ci_latest_attempts 的判法一致;說明裡的「同口徑」從 tally 搬到 _e2e_run_key,只講真的相同的那部分;不共用的理由(總表沒有嘗試次數與結論欄位)寫在同一處與 Systems 筆記。

## 正式發現處置

| ID | 來源 | 結果 | 處置 |
|---|---|---|---|
| t1 | 單審 F1(major) | HIT(引句一句錨不到,機械重現成立) | 折:組 F;新斷言修前紅 |
| t2 | 單審 F2(major) | HIT | 折:組 G;兩條新斷言,拿掉清理各自翻紅 |
| u1 | 架構 F1(minor) | HIT | 折:組 H;run_id 不轉字串時翻紅 |

三項全折,未降級、未放行;refuted 為 none。

## 修補因果

- t1:有證據的修復回歸——第二輪修補把去重從 deque 之前搬到之後(r3-repair.patch),修前修後兩版輸出如重現表。
- t2:原有漏查——兩處的清理在第二輪才加,當時處置紀錄已寫明沒有測試;不是修補弄壞行為,是修補沒補齊測試。
- u1:有證據的修復回歸——第二輪新寫的執行鍵與說明不一致(r3-repair.patch)。

## 修補後自查

- 改壞驗證五道全紅(見 r3-repro.txt)。
- 大輸入:十萬行全部重判過,history --flaky --last 20 1.62 秒 / 344MB;--last 100000 2.71 秒 / 888MB(與要求留的次數成正比)。
- 專案 ruff 設定比對修補前後沒有新增告警。
