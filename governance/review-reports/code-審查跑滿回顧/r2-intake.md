# code-審查跑滿回顧 r2 收貨紀錄(2026-10-06)

第 2 輪:全新 7 席(都沒讀第一輪席報告),審第一輪修正的差異 `r2-snapshot.patch`(754c17e8..37f2379f,1592 行)。外家席依 2026-09-30 使用者裁不派。

## 收貨三道
- 七份報告 `quote-check` 對 `r2-snapshot.patch`:全數錨定;`report-normalize`:全部正規。
- 收件前 `git reflog -1` 只有編排者自己的提交;工作目錄多出的 `.escape-log`、`.kill-log`、治理帳改動是編排者跑 `guard kill` 與記帳產生的。
- 流程觀察:這輪派工詞仍帶 `LUMOS-IMPACT:`,但 `lumos dispatch-lens 754c17e8..HEAD` 回「base 不在主線歷史上」,所以改用主線分岔點 ce2a961f 當範圍;各席回報仍沒收到 hook 附加,自己跑 `lumos impact --diff`。

## 編排者重現(佐證通道)
| id | 依據 | 結果 |
|---|---|---|
| A1/A2/A3 | 架構席指出補換行、讀回顧檔、終端跳脫各有第二份實作,附對照 file:line;編排者對照 `_drift_ledger_append`、`_regular_own_fd`、`_esc_clean` 確認存在 | HIT |
| S1 | 資安席實跑:卷證資料夾是符號連結時 `--template --write` 在 repo 外建檔(腳本 /tmp/sec_r2_repro.py) | HIT(單席,可執行證據) |
| B1/P1 | 邊界、併發兩席各自實跑:孤立代理字元讓 --template 丟堆疊、--write 留 0 位元組殘檔 | HIT(多席) |

## 逐條去向(25 條;本輪有 major,accepted 必空,全部折入)
| id | 席 | 嚴重度 | 一句 | 組 |
|---|---|---|---|---|
| A1 | 架構 F1 | major | 檔尾補換行兩份、判準不同(修補引起) | 1 |
| A2 | 架構 F2 | major | 讀回顧檔自寫開檔,只比既有少擁有者檢查(修補引起) | 1 |
| A3 | 架構 F3 | major | 終端跳脫兩套並存(修補引起) | 1 |
| A4 | 架構 F4 | minor | fix-check 範本仍用重導向 | 規格〈誠實界線〉記為範圍外 |
| A5 | 架構 F5 | minor | 第三套治理帳讀法、缺一般檔守衛 | 6 |
| G1 | 通才 F1 | minor | 讀檔失敗訊息的指令沒加引號(修補引起) | 1 |
| G2 | 通才 F2 | minor | 其他帳寫入器沒補換行(修補引起) | 規格〈誠實界線〉記為範圍外 |
| G3 | 通才 F3 | minor | 回顧檔已存在時提示走死路(修補引起) | 4 |
| S1 | 資安 F1 | major | 卷證資料夾是符號連結時寫到 repo 外(修補引起) | 3 |
| S2 | 資安 F2 | minor | cap-decision 印原樣輪次 | 1 |
| C1 | 正確性 F1 | minor | 切行只修一半、讀者間分歧(修補引起) | 5 |
| C2 | 正確性 F2 | minor | 同 G3 | 4 |
| P1 | 併發 F1 | minor | --write 遇代理字元留殘檔(修補引起) | 2 |
| P2 | 併發 F2 | minor | 補換行先 stat 再 open 的競態(修補引起) | 1 |
| P3 | 併發 F3 | minor | 輪次含代理字元讓 cap-decision 丟堆疊 | 2 |
| B1 | 邊界 F1 | major | 帳上欄位含代理字元讓 --template 丟堆疊、留殘檔(修補引起) | 2 |
| B2 | 邊界 F2 | minor | 非 UTF-8 的 --note 讓 cap-decision/--skip 丟堆疊 | 2 |
| B3 | 邊界 F3 | minor | 同 S2 | 1 |
| B4 | 邊界 F4 | minor | 回顧檔是資料夾或符號連結時提示繞圈 | 4 |
| B5 | 邊界 F5 | minor | 只有 \r 行尾的帳被當空帳(修補引起) | 5 |
| B6 | 邊界 F6 | minor | 筆記宣稱代理字元已涵蓋、實際只涵蓋一處 | 8 |
| K1 | 合約 F1 | minor | 筆記說只讀自己的檔、程式不要求擁有者 | 8 |
| K2 | 合約 F2 | minor | 同 G3 | 4 |
| K3 | 合約 F3 | minor | 規格與圖譜沒跟上第一輪修補(修補引起) | 規格同步(編排者已改計劃,新增 S18) |
| K4 | 合約 F4 | minor | 幾支新測試守衛偏弱 | 7 |

修補引起(regression-set):A1、A2、A3、G1、G2、G3、S1、C1、P1、P2、B1、B5、K3。
