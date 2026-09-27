# r3 收貨紀錄(筆記內容審,末輪)

凍結材料:r3-snapshot.md(r2 收窄後整份)、r3-delta.patch。6 席全新,同 r1 編制;收齊前沒動被審材料。

## 收貨三道

- report-normalize:併發席總結句寫了「severity: blocker」字樣被判成藏等級,請該席自己改寫總結;其餘已正規化。
- quote-check:5 份首交全錨定;接手席 1 句引句出自程式碼註解,請該席改成 file: 佐證。
- refcheck:missing 皆為還沒建立的判定檔資料夾或範本檔。

## 編排者重現

| 發現 | 重現 | 結果 |
|---|---|---|
| r3b-F1 / r3h-F3 / r3a-F7 / r3g-F3 reflog 判 fetch 新鮮度會卡死 | 席位附的可重跑指令:全新 clone 沒有追蹤參照 reflog;遠端沒變時 fetch 不寫 reflog | HIT |
| r3c-F1 / r3g-F2 起點 40 個 0 會放行 | 在臨時 repo 跑已上線的第一層 `note-shape --diff 0000…0000..<頂端>`:印「範圍在本機找不到,跳過(fail-open)」、rc0 | HIT(另記第一層漏網) |
| r3b-F5 / r3a-F12 / r3g-F4 `decisions_items` 只給行範圍 | 讀碼:回傳 (區塊起訖, 每條決策的起訖, 縮排) | HIT(讀碼確認) |
| r3f-F1 / r3b-F2 / r3h-F2 圍欄門檻 | 讀碼:`_visible_lines` 認三個以上反引號或波浪號、縮排不超過三格 | HIT(讀碼確認;計劃寫「四個以上」是措辭錯) |
| r3h-F1 / r3g-F1 範本要登記 | 讀碼:`_VENDORED_TREE_FILES` 是 update 同步的清單 | HIT(讀碼確認) |
| 其餘條目 | 設計層論證,附 file:line、引句全錨定 | 採信 |

## 處置

31 條全折(輪內有 blocker);refuted 無。另抓到第一層漏網,記逃逸帳並修。

鏡像核對:31 條未處理 0、部分 2、相反 0;新矛盾 3 處,已改(收尾改成逐提交看轉態)。見 r3-mirror.md。
