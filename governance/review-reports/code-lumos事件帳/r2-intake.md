# code-lumos事件帳 r2 收貨紀錄

- 六席全新報告(rebase 到 2aafdcb2 之後的 r2-snapshot.patch;外家兩席依 Enzo 指示缺席)格式正規化、引句全數錨定。
- 編排者格式調整:邊界輸入席 F5 原稿含雙向覆寫與零寬字元本身,存檔改寫成字元代號並在原處註明(把這類字元寫進 repo 正是 Trojan Source 的手法)。
- 編排者自查:修正時發現測試檔新增行裡有三處真的特殊字元(兩處 r2 新測試、一處 r1 新測試),ruff 的 PLE2502、PLE2515 抓到;全部改成跳脫寫法,並對整份新增內容掃 Cf、Zl、Zp、Cs、Cc 確認歸零。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| rc1 / re1 / re2 | 極深巢狀、孤立代理字元讓讀取端崩 | t_events_reader_hostile_lines 先紅:四種輸出都 Traceback | HIT | 折 |
| re3 / rc1 | ok 是列表丟 TypeError | 同上先紅 | HIT | 折 |
| ra1 / re5 / rs4 | 清理函式另起爐灶、漏雙向覆寫與零寬、--json 沒消毒 | 同上先紅;改回舊清理函式再紅(殺傷力確認) | HIT | 折 |
| re6 / rs1 | 塊檔連結被讀 | 同上先紅(OUTSIDE 印出) | HIT | 折 |
| rc2 / re4 / rk1 | 上標數字天數噴 Traceback | t_events_prune_hardening 先紅 | HIT | 折 |
| rs2 | .git 被改成指到別的 repo 時清理刪到別人的事件帳 | 同上先紅(victim 的 OLD 被刪) | HIT | 折 |
| rp2 / rk3 / rc5 | git 卡住拖垮 enforcement | t_enforcement_ledger_row_git_hang 先紅(15.2 秒) | HIT | 折 |
| re7 / rk2 | 只有專案範圍那份時移除誤報、跳過市集 | t_ledger_plugin_teardown_scope_and_messages 先紅 | HIT | 折 |
| rc3 | teardown 的 --source 沒傳到 | 同上先紅 | HIT | 折 |
| rc4 | 救援訊息說錯哪一步失敗 | 同上先紅 | HIT | 折 |
| rp3 | 競態立刻重查看不到 | 同上:修前碰巧通過,修後拿掉等待會紅(殺傷力確認) | HIT | 折 |
| rs3 | 來源不是預設位置時看不到 | 同上先紅 | HIT | 折 |
| ra2 | 擋下印到標準輸出 | t_events_prune_hardening 先紅 | HIT | 折 |
