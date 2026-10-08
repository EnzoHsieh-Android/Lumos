# code-新寫句子寫法提醒 r1 收貨

席報告 2 份(正確性 3 條 minor、架構對齊 3 條 minor,另一處 ⚠ 交編排者)。quote-check 全錨、refcheck 全對得上。正確性席第 3 行原寫法被格式檢查退回、由該席自己重寫(只改那一句)。

彙整 id:正確性 c1–c3、架構對齊 a1–a3;架構對齊的 ⚠(另寫 `_ns_wd_paren_groups`)併進 c1 一起處理。

## 根因分組

- 括號判定只看最外層:c1(巢狀與沒收尾的左括號);架構對齊的 ⚠ 同一支函式。
- 定義段的判定另寫一份:a2(只認單一目標)、c2(解析時漏出 SyntaxWarning)、c3(三引號字串裡的假定義)。
- 數字邊界另寫一份:a3(少了 / : -,跟 drift fix 不一致)。
- 收尾步驟切法:a1(少了 collected 那一步)。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| c1 | 新測試 t_note_wording_paren_any_depth:「說明甲(見別篇(更正:第 3 項…))」「說明乙 :-( 然後 (更正:第 3 項…)」 | 修前兩句都沒提醒(①②紅) | HIT |
| c2 | 新測試 t_note_wording_def_shapes ③:定義含 "\d+" | 修前輸出含 SyntaxWarning | HIT |
| c3 | 同上 ②:FAKE 寫在三引號字串裡 | 修前印出 [count:src/shapes.py::FAKE=3] | HIT |
| a1 | 讀碼:`_ns_tag_hints_collected` 與 `_ns_negation_collected` 都有、wording 沒有 | 結構不同 | HIT |
| a2 | 同上 ①:`CHAIN = ALIAS = (...)` | 修前沒提醒,`_count_eval` 數得到 3 | HIT |
| a3 | t_note_wording_count_quiet 新增 O/P/Q:「r1-3 種」「a/3 種」「x:3 種」 | 修前 O 被提醒 | HIT |

## 處置

全折(6 條):
- c1:括號群改成每一層都吐(右括號配最近的左括號,沒收尾的左括號不吃掉後面的群)。
- a2、c2:定義那一段整段交給 `_count_eval` 判與數,解析時關警告。
- c3:落在跨行字串裡的行首定義不算(標準庫 tokenize 斷詞,一支檔只斷一次、要找名稱時才斷);中途試過「數三引號奇偶」的捷徑,效能測試抓到普通字串裡的三引號會讓整支檔之後的定義全被誤判,改掉。
- a3:抽出 `_COUNT_NUM_EDGE`,drift fix 的 `_count_rewrite` 與數量提醒共用。
- a1:補 `_ns_wording_collected`,收尾照前綴提醒兩步。
修後重量最壞情況:2.5 秒、265 MB。故意改壞四處(只看最外層、不排除字串、不關警告、邊界只看英數)全部翻紅。
