severity: minor

## 1 import 排在程式碼之後、被一行計算隔開
severity: minor
blocking: 否
引句:「    import datetime
+    # gov 預設只看近 90 天:帳的日期寫死會隨日子過去掉出窗外(2026-10-23 同天翻紅),取今天往前幾天」

說明:兩個函式都先 `import datetime`,接著放註解和 `day = ...` 計算,最後才 `import json as _j`。同一段的 import 被計算式隔開了。既有寫法是 import 連在一起放在函式最前面:`scripts/test_lumos.py:2983`、`:7451`、`:7487`(`import datetime, re as _re`),`:8709` 也是 import 之後才出現計算。這只是排列不一致,結構是對的。

## 對三件事的對照

1. 位置、用了什麼、被誰用:一致。
   - 日期都是在測試函式本體開頭算出來,函式內才 `import`,沒有抽成共用 helper,也沒有放到模組層。
   - 既有的是 `:2983-2984`、`:7451-7455`、`:8709-8710`。其中 `:8710` 處理的是同一個問題:gov 只看近 90 天,寫死的日期會過期。它用 `days=5` 往前推,和這份改動做法相同。
   - 日期變數只給這個函式自己用。
   - 文件側的 PITFALL 筆記寫在 `test-quality-handbook.md` 的 summary。該節點的 `about_code` 已列 `scripts/test_lumos.py`,所以家的歸屬沒問題。
2. 命名、匯入、取日期:大致一致。
   - 取日期用 `datetime.date.today() - datetime.timedelta(days=N)).isoformat()`,和 `:7331`、`:7528` 等處一樣。
   - 用 `import datetime` 而不是 `as _dt`,與 `:2983`、`:7451` 同款。`:8709` 用 `_dt`,同檔本來就有兩種,不算新增。
   - 變數名 `day` 以前沒出現過,其他測試用 `today`、`old`、`past`。`day` 是被減過的日期,意思不同,所以不算偏離。
   - 唯一的小偏離就是上面第 1 條的 import 位置。
3. 有沒有帶進專案原本沒有的另一種做法:沒有。
   - 沒有新依賴,沒有 mock 或凍結時間,也沒有改動被測的 gov 程式。
   - 過濾用的 `day[:5]` 取年份前綴,取代原本寫死的 `"2026-"`,只是同一個 `startswith` 換成相對今天的版本,不是新手法。

不對齊共 1 條,其中 major 0 條
