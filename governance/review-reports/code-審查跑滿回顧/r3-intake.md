# code-審查跑滿回顧 r3 收貨紀錄(2026-10-06)

第 3 輪(上限輪):全新 7 席(都沒讀前兩輪席報告),審第二輪修正的差異 `r3-snapshot.patch`(37f2379f..15774a0d,排除帳本與卷證,1382 行,sha256 73dff2f0…)。外家席依 2026-09-30 使用者裁不派。第二輪修正關卡 `loop fix-check --round r2` 第一次因紀錄格式不過(一格多個函式名、重複類別缺 prior),補紀錄後重跑通過(bc95a2e7)。

## 收貨三道
- 七份報告 `quote-check` 對 `r3-snapshot.patch`:全數錨定;`report-normalize`:全部正規。
- 收件前 `git reflog -3` 只有編排者自己的提交。
- 流程觀察:派工詞帶 `LUMOS-IMPACT: ce2a961f..HEAD`(主線分岔點),派工前跑過 `lumos dispatch-lens` 暖快取。

## 編排者重現(佐證通道)
| id | 依據 | 結果 |
|---|---|---|
| K1/P1/S1/B1 | 五席中四席各自實跑重現;編排者讀碼確認讀端 `_retro_gov_events` 走 `_regular_own_fd`(不跟隨符號連結),寫端 `_gate_event` 是 `open(path, "a")`(跟隨) | HIT(多席+讀碼) |
| A1 | 架構席在臨時目錄造上層符號連結,自寫檢查放行、`_repo_path_unsafe` 拒絕 | HIT(單席,可執行證據) |
| A2 | 架構席列出審查帳另五處 `splitlines()` 行號並造 U+2028 帳實跑 | HIT(單席,可執行證據) |
| S2 | 資安席實跑 `--template` 帶出 C1 控制碼 | HIT(單席,可執行證據) |

## 逐條去向(23 條;本輪有 major,accepted 必空,全部折入;使用者 2026-10-06 裁「破例多跑一輪」)
| id | 席 | 嚴重度 | 一句 | 組 |
|---|---|---|---|---|
| K1 | 合約 F1 | major | 治理帳是符號連結時寫得進、讀不到(修補引起) | 1 |
| P1 | 併發 F1 | major | 同 K1 | 1 |
| S1 | 資安 F1 | major | 同 K1,另寫端可往 repo 外追加 | 1 |
| B1 | 邊界 F1 | major | 同 K1 | 1 |
| A1 | 架構 F1 | major | `--write` 落點檢查另寫一套(修補引起) | 2 |
| A2 | 架構 F2 | major | `_ledger_lines` 只接三處,審查帳另五處仍 splitlines(修補引起) | 3 |
| S2 | 資安 F2 | major | `--template` 輸出帶出 C1 控制碼與雙向標記 | 4 |
| K3 | 合約 F3 | minor | 檔太大/讀不動時提示繞圈(修補引起) | 5 |
| G1 | 通才 F1 | minor | 同 K3 | 5 |
| C2 | 正確性 F2 | minor | 同 K3,另回顧檔被刪後提示指向不存在的檔 | 5 |
| C1 | 正確性 F1 | minor | 卷證資料夾是符號連結時提示叫人跑被拒的指令(修補引起) | 5 |
| G2 | 通才 F2 | minor | 同 C1 | 5 |
| B3 | 邊界 F3 | minor | 同 C1 | 5 |
| P2 | 併發 F2 | minor | 建檔中途被殺留空檔、提示無出口 | 5 |
| C3 | 正確性 F3 | minor | `_append_governance_log` 遇無法編碼字串丟堆疊 | 6 |
| B4 | 邊界 F4 | minor | 同 C3 | 6 |
| B2 | 邊界 F2 | minor | 帳尾檢查用 `os.pread`,非 Unix 沒有(修補引起) | 6 |
| A4 | 架構 F4 | minor | `_retro_utf8_bad` 與 `_fix_bad_strings` 兩套 | 7 |
| A5 | 架構 F5 | minor | `_esc_clean` 寫死範圍與 `_PATH_SPECIAL_CATS` 並存 | 7 |
| K2 | 合約 F2 | minor | S18 綁的測試只驗一個承諾 | 8 |
| K4 | 合約 F4 | minor | 筆記與函式說明沒跟上切行改法、新測試沒被引用 | 8 |
| A3 | 架構 F3 | minor | 規格〈誠實界線〉缺口清單過期且不全(修補引起) | 8 |
| G3 | 通才 F3 | minor | 同 A3 | 8 |

修補引起(regression-set):K1、P1、S1、B1、A1、A2、K3、G1、C2、C1、G2、B3、B2、A3、A4、A5。
