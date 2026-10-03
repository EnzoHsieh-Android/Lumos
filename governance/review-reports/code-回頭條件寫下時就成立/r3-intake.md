# r3 收貨(code-回頭條件寫下時就成立)

收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;兩席都沒動 repo。report-normalize 不用改;quote-check 全數錨定;refcheck 對得上。
正確性席 clean(用假 gpg 實做簽章提交驗過修法、走過 R/C/T/U/D、無檔案列合併提交、空輸出、單一提交;`_note_status_seq` 唯一呼叫端與日期輸出端都接 None)。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| Z1 | grep `--no-show-signature`:只在 `_note_versions` 與 `_git_commit_date` 兩處;其他 log/show 呼叫(`--date=short --format=%ad`、`--format=@%cs`、`--format=%cI`)都沒加 | HIT:逐呼叫加旗標,沒集中 |
| Z2 | 讀 `_codeloop_git_ts`(`%cI`、失敗回空字串)、`--date=short %ad`、新 `_git_commit_date`(`%cs`、驗形狀、失敗回 None) | HIT:取提交日期有三種寫法 |

## 處置

- Z1 放行:旗標只對 log/show 有效,放進 `_lens_git` 會讓所有 git 子指令都帶上而報錯;其他呼叫點是既有程式、不在本案範圍。改動只修本案自己會讀錯的兩處。
- Z2 放行:既有兩種回傳格式不同(ISO 時間、帶主旨),改用它們要另外剝殼、而且它們本身也沒關簽章顯示;新函式走 `_lens_git` 與回 None 的慣例,跟 `--date=short` 那處一致。
