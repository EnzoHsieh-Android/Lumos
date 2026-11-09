# r1 收貨紀錄(code-android範本兩專案實跑,light)

- 一席架構對齊(sonnet)交回後從逐字稿存檔;已是正規化格式,quote-check 兩句全錨定,refcheck 兩處都存在。收貨時 git status 只有本卷證目錄,席位沒動 repo;席位沒建臨時目錄。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| A1 | 四篇計劃改成 done 時沒更新 updated | HIT:四篇開頭欄位 updated 仍是 11-06;前例提交 277977ea5 收尾時有改 | 折:四篇 updated 改成 2026-11-09 |
| A2 | 驗證紀錄用的錯誤寫法跟計劃預期值表指定的(沒包 remember 的 mutableStateOf)不同又沒交代 | HIT:預期值表 S5 列寫 RememberMissing,紀錄只跑了缺 modifier 參數 | 折:在 AGP 9 那組補跑指定寫法,lint 報 UnrememberedMutableState、detekt 報 RememberMissing,兩邊都失敗;紀錄補兩列並寫明主要範例為什麼選缺 modifier 參數 |

## 先查世界

- PRIOR-ART:A1、A2 都是筆記寫法與驗證範圍的一致性,沒有外部做法可查;A2 的判準照計劃自己的預期值表(compose-rules 規則頁 RememberMissing)直接實跑,不另找標準。
