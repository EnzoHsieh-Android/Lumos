---
type: issue
status: open
created: 2026-11-05
updated: 2026-11-05
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - priority/P3
  - scope/stack-knowledge
summary: |-
  FLAG:TECHNICAL
  PITFALL:規則檔 files 清單項目後面接行內註解提到 src/main 時,只掃測試碼的規則被誤判成不是,祖先目錄守衛靜默略過 [出處:2026-11-05 code-kotlin規則包 r4 正確性、邊界席] [根因:_files_block_is_test_only 只去整行註解] [repro:check.py 對 files 區塊 `- '**/src/test*/**'  # 不含 src/main` 回 False]
related:
  - "[[Systems/kotlin規則包]]"
---
# Kotlin規則包代碼審放行的小問題

## 症狀

代碼審 code-kotlin規則包 第 4 輪(加開的驗收輪)報了 8 條小問題,為了不讓改動跑出審查範圍而附理由放行,記在這裡下一批一起修(卷證 `governance/review-reports/code-kotlin規則包/r4-intake.md`):

1. 規則檔 files 清單項目後面接行內註解、註解裡提到 src/main 時,只掃測試碼的規則被誤判成不是,自我檢查的祖先目錄守衛靜默略過那條規則(正確性、邊界兩席都報)。
2. 決策表觸發字拆字只認頓號與半形逗號,全形逗號拆不開;「(無),foo」不會被報並列(正確性、邊界兩席都報)。
3. ast-grep 吐出非 JSON 時自我檢查直接 traceback,不是「跑不起來」那種可讀訊息(邊界席)。
4. 型錄 DATA-10 實測欄的搬級理由誤抄了 API-17 的「OkHttp 5 寫法」,該寫「try/runCatching 裡的終端操作」(合約圖譜席)。
5. `kt-long-lived-scope-plain-job` 遇到 `CoroutineScope(x) + (Job() + job)` 這種括號裡再包一層加法仍誤報(通才席,ast-grep 實跑重現)。
6. review-fp- 好例豁免拿掉了「只在自己規則目錄」的條件;正確性席實測行為等價(只讀自己目錄的命中),通才席從機制面提醒放錯目錄的樣本不會被抓(通才席)。

## 根因

1. `_files_block_is_test_only` 只去整行註解,沒處理行尾註解。
2. `dt_triggers` 的分隔字元類 `[、,,]` 兩個逗號都是半形(原有寫法,搬進函式時沒發現)。
3. `scan` 裡 `json.loads` 沒接例外。
4. 型錄補註時兩列共用一句理由,沒分開寫。
5. 規則的加法分支只看加法的直接運算元。
6. 自我檢查只讀「自己目錄 × 自己規則」的好例命中,好例目錄裡命中別條規則本來就沒人看。

## 現在怎麼繞

目前規則包沒有規則用行尾註解、型錄沒有全形逗號(兩席 grep 過),1、2 不會發生;3 會讓自我檢查以非零結束,不會放行;4 是措辭;5 寫法罕見;6 沒有行為差異。

## 什麼條件算修好

1、2、3 各有一條先紅後綠的測試(行尾註解、全形逗號、非 JSON 輸出);4 改完型錄字句;5 的片段補進好例樣本、規則不報;6 決定要不要加「好例目錄命中別條會擋規則也報」的檢查並補測試。
