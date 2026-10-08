severity: clean

# 驗收:新出現的綁定站不站得住(判定路徑席,sonnet)

立場:假設「判定說有、其實沒有」,找「一段說明被當成綁定拿掉、兩道檢查都放行」的路。結論:找不到。

## 讀過與推論
- `_nodehome_strip_test_tags` 只拿掉值通過 `_nodehome_test_tag_value_ok` 的標記;凡含字母的值都會被 `_test_names_of` 轉成名稱,新 `[test:]` 名稱還要過 `_NODEHOME_TAG_NAME_RE.fullmatch`(單一識別字,平台前綴只收 `[A-Za-z0-9_-]+:`)加 `_NsTrJudge` 判 yes。拿掉的文字與被核對的名稱是同一份(names 直接從拿掉的 value 算),沒有「拿掉的比核對的多」的縫。
- 唯一不含字母、不被核對的是空名稱(值只有逗號)。它不帶任何說明文字,不構成夾帶。
- `[test-gone:]`:名稱整串(含前綴)要等於上一版某個 `[test:]` 名稱;`@` 後只收小寫 7 到 40 碼十六進位(用逗號切後逐項看)。`@` 前的文字因此只能是上一版已存在的文字。
- 前綴:多平台時未定義的前綴 `_plat` 會 raise ValueError 判 bad-name,連字號英文前綴進不來。

## 實跑(臨時 repo,沿用 `_nh_tag_repo`;每例同時跑 `home check --staged` 與提交後 `home check --diff HEAD~1..HEAD`,兩者結果一致)
放行(rc0,皆無新增說明):真測試名、反引號包真名、逗號重複同名、空逗號 `[test:,]`、tab 或全形空白縮排的真名、大寫鍵 `[TEST:...]`、`[test-gone:舊名@abc1234]`。
擋下(rc1):`never-ever-call-this-twice:test_new`、`Note:test_new`、`python:test_new`、全形冒號前綴、`()`、`TEST_NEW`、單字 `new`、`test_new.`、跨行值、標記後緊接英文 `[test:test_new]now every order...`、`[test-gone:x-y:test_old@abc1234]`。
note-shape 那道因 home check 已先擋下,沒有「home 過、說明被吃掉」的案例可再送進去。

## 唯一觀察(不成立為 finding)
上一版就存在的英文 `[test:一句說明]`,這一版可在別處複製成 `[test-gone:同一句]`(實跑 rc0)。文字上一版已有,沒有新增說明內容,屬於「拿掉綁定不核對」的既定範圍,低於設計〈天花板〉。

引句:「test-gone 要跟上一版的 [test:] 整串一致——不去平台前綴:前綴不核對,去掉它就能用一串連字號英文:舊名夾帶說明」

總結:全份最高等級 clean
