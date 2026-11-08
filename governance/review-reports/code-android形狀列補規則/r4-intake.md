# r4 收貨紀錄(code-android形狀列補規則,人裁多開的一輪)

## 收貨

- 兩席(正確性四、架構對齊四)交回後從逐字稿原樣存檔;兩份都已是正規化格式,quote-check 全數錨定。正確性四的那條標 severity major 卻寫 blocking 否,兩欄矛盾;編排者自己重現確認是會誤擋推送的真問題,照 major 折,不退回重判。收貨時 git status 沒有席位造成的 repo 改動;兩席都說沒留臨時路徑。

## 編號與處置

編號照報告順序:正確性四 s1、架構對齊四 a1–a3。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| s1 | map 那條的 .asFlow() 排除只認接收者結尾,`ds.asFlow().buffer().map { it.await() }` 被當成清單擋下 | HIT:C222、C223 修前紅 | 折:排除改成「鏈裡有 .asFlow() 而且後面沒有 toList/toSet/toCollection」,補 C222~C226;列舉驗樣式與三個收集選項拿掉都紅,手動驗拿掉 asFlow 那行也紅 |
| a1 | rules-hints/ 多了「出處只有建議語氣」這種用途,規則包節點的檔案說明沒改;規格 r1 的舊說法沒標更正 | HIT | 折:規則包節點寫成兩種用途,規格 r1 那行補更正 |
| a2 | 規格範圍 4 寫「等級改 error」,結果表 ARCH-59 是 warning | HIT | 折:範圍 4 改成 error 或照 rules/ 既有用法用 warning,兩者都擋 |
| a3 | 型錄檢查只驗現成規則欄,沒釘這次真正改的通電批次欄 | HIT | 折:_KTSHAPE_CATALOG_IDS 改成 id 對通電批次的表,逐列驗兩欄 |

--refuted-set none。

## 先查世界

- PRIOR-ART:s1——kotlinx.coroutines Flow 的 buffer、flowOn 是中間算子(回傳 Flow),toList/toSet/toCollection 是終端算子(收成集合);以終端算子分界,不靠列舉中間算子名字。
