# code-審查跑滿回顧 r1 收貨紀錄(2026-10-06)

編排者:claude。分級 high(`pitfalls --diff` 命中風險型樣與新告警)。凍結 patch `r1-snapshot.patch`(2038 行,sha256 2f1ca201…),base_commit 754c17e8。7 席:正確性、併發資源、邊界、合約圖譜、通才(原外家名額)、架構對齊、資安;外家席依 2026-09-30 使用者裁不派——收斂結論照實寫「單家族視角下未發現」。

## 收貨三道

- 七份報告 `quote-check` 對 `r1-snapshot.patch`:全數錨定。`report-normalize`:七份都已正規。
- 收件前 `git reflog -2` 核對:只有編排者自己的兩筆提交;合約圖譜席自述誤建一個空目錄後已 `rmdir`,`git status` 確認只剩卷證資料夾未追蹤。
- 流程觀察(不是 finding):派工詞帶了 `LUMOS-IMPACT:` 與 `LUMOS-ROLE-CARDS: on`,但七席回報尾端都沒有附固定席筆記與角色卡;正確性、併發資源、邊界、合約圖譜、通才五席自己跑 `lumos impact --diff` 補做固定席判讀。派工前有跑 `lumos dispatch-lens` 暖快取(輸出「外部碼表補選因時間上限中止」)。原因沒查:可能是工具鏈工作樹的 hook 沒裝、或派子代理的路徑沒觸發 hook。

## 編排者重現(佐證通道)

各席 major 都附了實跑重現(席報告內有指令與輸出);編排者採信理由:
| id | 依據 | 結果 |
|---|---|---|
| g1/c1/b4/k1 | 四席各自實跑:照貼提示指令把已記回顧蓋成骨架 | HIT(多席獨立一致) |
| a1/c2/b1 | 架構席指出另寫讀帳;正確性、邊界兩席各自實跑 U+2028 讓輪數少算 | HIT(多席) |
| p1 | 併發席實跑治理帳缺尾換行後 cap-decision 黏行、擋點失效(腳本 /private/tmp/claude-501/scratch/e1.py) | HIT(單席,可執行證據) |
| b2 | 邊界席實跑孤立代理字元讓 retro-stats 炸 | HIT(單席,可執行證據) |

## 逐條去向(22 條;本輪有 major,依 code 迴圈規則 accepted 必空,全部折入)

| id | 席 | 嚴重度 | 一句 | 組 |
|---|---|---|---|---|
| s1 | 資安 F1 | minor | 印到終端的編號控制字元沒跳脫 | 6 |
| s2 | 資安 F2 | minor | 治理帳事件與 drafted_by 可偽造(推論) | 寫進計劃〈誠實界線〉 |
| a1 | 架構 F1 | major | 另寫一套讀審查帳 | 2 |
| a2 | 架構 F2 | minor | 只讀主治理帳 | 9 |
| a3 | 架構 F3 | minor | 帳壞時第二個印 FAIL 橫幅處 | 10 |
| a4 | 架構 F4 | minor | 第二套路徑正規化 | 11 |
| p1 | 併發 F1 | major | 治理帳缺尾換行時人裁黏行、擋點失效 | 3 |
| p2 | 併發 F2 | minor | 回顧檔換成 FIFO/符號連結會卡住 | 7 |
| p3 | 併發 F3 | minor | --record 驗與算指紋兩次讀檔 | 8 |
| g1 | 通才 F1 | major | 提示指令照貼清空回顧檔 | 1 |
| g2 | 通才 F2 | minor | 含 NUL 路徑讓無人裁迴圈的處置閘丟堆疊(回歸) | 5 |
| c1 | 正確性 F1 | major | 同 g1 | 1 |
| c2 | 正確性 F2 | minor | splitlines 劈開帳列、輪數少算 | 2 |
| b1 | 邊界 F1 | major | 同 c2 | 2 |
| b2 | 邊界 F2 | major | 孤立代理字元讓 retro-stats 炸 | 4 |
| b3 | 邊界 F3 | minor | evidence 含 NUL 讓 --check 丟堆疊 | 5 |
| b4 | 邊界 F4 | minor | 同 g1 | 1 |
| k1 | 合約 F1 | major | 同 g1 | 1 |
| k2 | 合約 F2 | minor | 提示與手冊叫不適用的迴圈也記人裁 | 12 |
| k3 | 合約 F3 | minor | accept-risk 帳壞時訊息說 --skip 是出口 | 13 |
| k4 | 合約 F4 | minor | S14 綁的測試守不到新閘名 | 14 |
| k5 | 合約 F5 | minor | S5 測試沒綁回放三處參數 | 15 |
