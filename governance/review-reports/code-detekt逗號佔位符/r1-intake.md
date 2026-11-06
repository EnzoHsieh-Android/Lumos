# r1 收貨紀錄(code-detekt逗號佔位符)

## 收貨

- 第 1 輪,分級 standard(`pitfalls --diff c10f1714d..8d63aa1d` 判定)。整份 1960 行超過 1800,拆甲包(程式與 CI,863 行)、乙包(測試與文件,1069 行)各派一位正確性席,架構對齊看程式加文件(1366 行);全 sonnet。外家預設不派,結論照實寫成「單家族視角下」。
- 本機 main 停在舊提交,派工鏡頭不認新基底(擋下:base 不在主線 main 的歷史上);改在派工詞指名 Systems/pitfalls-lint-adapter、Systems/pitfalls-code-loop、Systems/lint-declaration-health、Systems/linter精選目錄、Projects/Android的detekt規則說實話_計劃 讓席位自己讀。
- 三席都交回後一次從逐字稿存檔(完成通知會把角括號轉成跳脫字)。三份都已是正規化格式,quote-check 全錨定、refcheck 全 ok。
- 席位沒有改 repo:收貨時 `git status` 只有本輪卷證目錄與治理帳。乙席臨時複本在 /tmp/lumos-seat-work/ 底下,存完報告後已刪。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 甲1 | 正確性甲 F1 | 席位以模組載入 lumos,檔清單 `x{LINT_FILES}.kt`、`b.kt` 交給帶逗號佔位符的命令跑 `_lint_run_and_parse` | HIT(席位原輸出):回 `([], False)`;一般檔名回 `([], True)` |
| 甲2 | 正確性甲 F2 | `grep -n 'T3' docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md` | HIT:天花板第 2 點與兩條 REVISIT 寫 T3,程式 `_DETEKT_ADVICE_ORDER` 是 T4 |
| 乙1 | 正確性乙 F1 | 同甲2 | HIT:同甲2(兩席獨立抓到同一處) |
| 架1 | 架構對齊 F1 | `grep -n 'fail_info' scripts/lumos` | HIT:`_lint_spawn`、`_lint_run_and_parse` 用選填字典帶回參數太長 |
| 架2 | 架構對齊 F2 | `grep -n '"separator-path"\|"oversize" + _LINT_NEW_SEP' scripts/lumos` | HIT:兩支函式各寫一份同形指紋 |
| 架3 | 架構對齊 F3 | `grep -n 'pip install\|sha256sum' .github/workflows/ci.yml` | HIT:CI 其他工具走 pip,detekt 走下載加比對雜湊 |

refuted: none

## 先查世界

- PRIOR-ART: 代號更正(甲2/乙1)——純文件代號對不上,不是做法問題,沒有業界做法可查;照專案既有慣例「條款凍結後不改字、在審計修正紀錄寫更正」處理(條款 [S7] 原文保留,天花板與 REVISIT 改成 T4,審計修正紀錄加一行實作更正)。
- PRIOR-ART: 放行的四條不動手修,不查。

## 歸因

- 甲1:改動前就有(舊碼是 `_LINT_NEW_FILES_TOKEN in cmd`),這次只是把判斷搬進共用函式。
- 甲2/乙1:實作時改了代號,計劃天花板與 REVISIT 沒跟上。
- 架1、架2、架3:本次新增的寫法。

## 逐條去向(1 組折、4 條放行、0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 甲1 | 正確性甲 F1 | 放行:改動前就有、檔名剛好含佔位符字樣極少見,威脅模型不防刻意取名;登記進 Issues/detekt逗號佔位符代碼審放行的小問題 第 1 項 |
| 甲2 | 正確性甲 F2 | 折:計劃天花板第 2 點與兩條 REVISIT 改成 T4,審計修正紀錄加實作更正一行 |
| 乙1 | 正確性乙 F1 | 折:同甲2 |
| 架1 | 架構對齊 F1 | 放行:結構同層、失敗最後進同一份清單,行為正確;登記議題第 2 項 |
| 架2 | 架構對齊 F2 | 放行:沿用同一份清單與同形指紋,不是第二套機制;登記議題第 3 項 |
| 架3 | 架構對齊 F3 | 放行:detekt 不在 PyPI,pip 走不通;比既有下載腳本多驗雜湊、註解寫明是新慣例;登記議題第 4 項 |
