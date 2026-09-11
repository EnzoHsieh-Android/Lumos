# r1 收貨紀錄(編排者)

標準分級:一席單一審查(sonnet)+一席架構對齊(sonnet,不佔人數)。兩席都收齊之後才動工作目錄。
報告本體一律從各席的輸出紀錄(tasks/<id>.output)抽,不從完成通知抄(通知會把 < > 轉碼);兩份檔內 `&gt;`/`&lt;`/`&amp;` 各 0 次。
兩份報告都已是正規化格式(report-normalize 不用改);quote-check 全數錨定;refcheck 全數對得上。
架構對齊席:clean,0 條。單一審查席:2 條(F1 major、F2 minor)。

## 去重後的發現

| id | 等級 | 一句話 | 哪一席 |
|---|---|---|---|
| F1 | major | 測試分層那一處的修法沒有測試釘住,整行拿掉測試照樣全綠 | 單一審查 F1 |
| F2 | minor | 刪除守衛自己的全域搜尋(git grep)用文字模式讀、沒跟著修 | 單一審查 F2 |

## 編排者機械重現(修改前的程式=本輪凍結版本)

| id | 怎麼重現 | 結果 |
|---|---|---|
| F1 | 暫存副本逐一拿掉九處修法中的一處,跑 t_diff_readers_survive_non_utf8_content | HIT:測試分層那處拿掉照樣 7 passed 0 failed;而且不只它——九處裡只有三處(風險掃描、波及計算逐檔差異、共用 git 包裝)拿掉會翻紅,另外六處(不可逆提示掃描、共改檢查、測試分層、測試地圖包裝、波及計算檔名清單、代碼審留痕有效性)拿掉都照樣綠 |
| F1 判準 | 席位說「只讀檔名、不含內容,不可能觸發」:暫存 repo 用 git 底層指令提交一支 Big5 檔名 src/中文.py,`git -c core.quotePath=false diff --name-only` 以嚴格 UTF-8 解碼 | MISS(判準不成立):UnicodeDecodeError 'utf-8' codec can't decode byte 0xa4——那一處刻意叫 git 不轉義檔名,非 UTF-8 檔名會原樣吐出來。所以正解不是「拿掉多餘的修法」,是補測試釘住 |
| F2 | 新測試:暫存區裡有一行含 deleteMe 又含非 UTF-8 位元組,呼叫 _delguard_confidence(["deleteMe"], …) | HIT:UnicodeDecodeError。後果比席位寫的重一點:外層接住後守衛整個放棄(降級 rc0),那個名字其實還在用、該出的警告就不見 |

## 判讀

- F1、F2 都折。逐處補、逐處找已經證明會漏(本輪一席就追出七處),改成機器保證:
  - 工具裡每一個文字模式讀 git 輸出的呼叫都加 errors="replace"(守衛認得 61 處,原本 3 處已有,這次共補 58 處)。
    UTF-8 正常的輸出加了結果一模一樣,所以不設例外清單。
  - 新增守衛測試 t_every_text_mode_git_call_tolerates_undecodable_output:讀原始碼找出「文字模式、跑 git、沒帶 errors=」的呼叫,
    有一個就翻紅;守衛自己餵一段壞的、一段好的,證明它會翻紅。
  - 行為測試兩支:內容型(既有那支加上不可逆提示掃描、刪除守衛)、檔名型 t_git_readers_survive_non_utf8_filenames
    (測試分層照樣給提醒、波及計算、共改檢查跑得完 rc0、測試地圖包裝、使用者關掉轉義時代碼審留痕有效性判得出來)。
- code 迴圈:輪內有 major,accepted 必須是空的——兩條全折。

## 編排者自己抓到的(不是席位發現,不進處置清單)

- O1(追 F1 範圍時):全檔掃出另外 49 處文字模式 git 呼叫沒帶 errors=。其中共改檢查挖歷史那一步(git log --name-only、刻意不轉義檔名)
  碰到 Big5 檔名直接中斷——新檔名測試在全面補之前實跑:cochange check rc=1、Traceback。已一併修進上面的全面補。
- O2(寫檔名測試時):我自己第一版把指令名寫成 cochange-check(不存在),「沒中斷」那條因此空轉變綠;改成 cochange check 並要求 rc0 後才真的翻紅。
