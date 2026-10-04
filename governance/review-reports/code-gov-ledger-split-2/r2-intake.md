# r2 收貨(code-gov-ledger-split-2)

7 席全部 sonnet。完整 diff 1904 行超過建議上限,所以拆開審:五個鏡頭席與架構對齊席主審第一輪之後的修補差異(466 行),資安席看完整 diff。收齊才動工作目錄。report-normalize 都不用改;quote-check 回滾席 3 句有 1 句錨不到(它引的是計劃筆記原文,審材外,報告裡已註明;該條由編排者自己對照計劃筆記驗過),其餘全數錨定。本輪沒有重大。

## 去重後的發現

| id | 來源席 | 一句話 |
|---|---|---|
| U1 | 正確性 F1、整合 F1、邊界 F1、回滾 F1 | 唯讀但已齊全的 docs/.gitignore 一律用可寫方式開檔,被誤報「開不了」並叫人手動加 |
| U2 | 併發 F1、邊界 F2 | 補 .gitignore 追加用無緩衝寫入,短寫(磁碟快滿)被當成補上 |
| U3 | 回滾 F2 | 〈回退〉只講帳檔衝突才取聯集,沒衝突時 git revert 會靜默刪掉帳檔裡這個提交加的行 |
| U4 | 架構對齊 F1 | 追加寫入用緩衝檔案物件,既有帳本寫入器用單次 os.write 核對長度 |
| U5 | 架構對齊 F2 | 「確認是一般檔案」又多抄一份,而且比既有那份少了擁有者檢查 |
| U6 | 資安 F1 | 偽造並強制提交的本機帳可誤導度量撤除條件的軟提醒(推論) |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| U1 | 以 nobody 身分跑舊程式與新程式:唯讀且已齊全的 .gitignore | HIT:舊程式印警告,新程式安靜。測試 t_gov_split_review2_r2_fixes ① 在 root 底下跑,root 可以開唯讀檔,所以那條斷言在舊程式上也是綠的,翻紅靠這次的 nobody 實跑 |
| U2 | 同測試 ②:把 os.write 換成少寫三個位元組 | HIT:舊程式沒有這段核對 |
| U3 | 回滾席讀 git diff --stat:版控帳 +375 行等 | HIT |
| U4 | 對照 _ledger_append | HIT |
| U5 | 對照 _drift_m1_ledger_miss 那段 | HIT |
| U6 | 讀 _doctor_metric_lines | HIT(只影響本機 doctor 軟提醒,不影響任何放行或擋推) |

## 處置

- U1、U2、U4、U5 折入:新增 _regular_own_fd(開檔即擋捷徑與管線、確認是自己的一般檔案,照 _drift_m1_ledger_miss 那段寫法);_local_ledger_append 用它加單次 os.write 核對長度,三支寫入器改用它;補 .gitignore 先唯讀讀內容,已齊全就不開成可寫,缺行才用 _regular_own_fd 開寫入並核對長度。既有 _drift_m1_ledger_miss 那段照留,不在本案動。
- U3 折入:〈回退〉改成帳檔一律 `git checkout HEAD -- <帳檔>` 保留還原前的內容,不分有沒有衝突。
- U6 放行:只影響本機 doctor 的軟提醒文字,不影響任何閘的放行或擋推,也不外洩資料;本機帳被強制提交時 doctor 已經會提醒「已被版控追蹤、git rm --cached」(code-gov-ledger-split r1 X3)。
