# r1 收貨紀錄(code-規則包樣本不當產品碼)

## 收貨

- 第 1 輪,分級 standard(換基底到主線 95e8dca 後 `pitfalls --diff` 判定;換基底前用落後的本機 main 算成 high,範圍夾帶別人的改動),派正確性一席加架構對齊一席,全 sonnet;外家預設不派,結論照實寫成「單家族視角下」。
- 本機 main 停在舊提交、所在工作樹有別的會談未提交的檔,派工鏡頭不認新基底(擋下:base 不在主線 main 的歷史上);改在派工詞指名 Systems/kotlin規則包、Systems/test-guard、Systems/room-guard、Systems/pitfalls-code-loop 讓席位自己讀。
- 兩席都交回後一次從逐字稿存檔(完成通知會把角括號轉成跳脫字)。兩份都已是正規化格式,引句全錨定。
- 席位沒有改 repo:收貨時 `git status` 只有本輪卷證目錄與治理帳。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 正1 | 正確性 #1 | 席位用 ast-grep 0.51.1 掃 `CoroutineScope(Dispatchers.Main) + (job)` 與兩層巢狀加法 | HIT(席位原輸出):兩種都報 kt-long-lived-scope-plain-job;一層括號加法不報 |
| 正2 | 正確性 #2 | `sed -n '39p;43p' docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` | HIT:第 39 行只列風險分級、棧別題、每支檔有家;第 43 行只列兩處 |
| 架1 | 架構對齊 #1 | `grep -n _ci_strip_comment scripts/lumos` | HIT:scripts/lumos 有同形的行尾註解剝除函式 |

refuted: none

## 先查世界

- PRIOR-ART: 零依賴獨立工具重複小函式(架1)——圖譜 Systems/kotlin規則包 已寫明「自我檢查程式是零依賴的獨立檔,不 import 單檔主程式」;Python 慣例上獨立腳本為了不引入對大型主程式的匯入依賴而複製十幾行小工具是常見取捨(主程式沒有 .py 副檔名、數萬行,匯入要動 importlib 載入整支)。採用:照既有做法保留獨立實作,放行。
- PRIOR-ART: 文件同步(正2)——同族掃描:`grep -rln "_RULEPACK_SAMPLE_RE" docs/` 命中三篇:Systems/kotlin規則包(補第 39、43 行)、Issues/Kotlin規則包代碼審放行的小問題(修好紀錄第 7 項已寫兩個守衛,不用改)、Projects/Android協程與API寫法機械檢查標準_計劃 第 136 行(只說「不當產品碼掃」、沒列哪幾道閘,仍成立)。用功能詞寫的 pitfalls-code-loop、test-guard、room-guard 三篇本次已更新。

## 歸因

- 正1:原有誤報,修補只宣稱修一層括號加法(議題第 5 項),不是修補造成。
- 正2:原有漏改(本次讓兩個守衛共用正規式,但規則包那篇沒跟上)。
- 架1:本次新增的函式,屬既有「獨立工具不依賴主程式」做法下的取捨。

## 逐條去向(1 折、2 放行、0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 正1 | 正確性 #1 | 放行:修補前就有的誤報、不在這次宣稱範圍;登記進 Issues/Kotlin規則包代碼審放行的小問題 的 REVISIT:2026-12-04 |
| 正2 | 正確性 #2 | 折:Systems/kotlin規則包 第 39、43 行補上測試防竄改比對與 Room 守衛 |
| 架1 | 架構對齊 #1 | 放行:規則包自檢程式零依賴、不 import 主程式是圖譜已記的既有做法,不算第二種做法 |
