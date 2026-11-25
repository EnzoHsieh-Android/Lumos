# code-選擇點變異加速第二段 第 3 輪收貨(2026-11-25,7 席,上限輪)

材料:修補差異 r3-repair.patch(95977c1 → 28543fb,345 行)給六席;完整快照 r3-snapshot.patch(dd8729f..28543fb,2166 行)給資安席,也是各席記帳的審查版本。來源綁定 r3-repair-binding.json;派工單 r3-dispatch.json。配對案例:r2-fix.json 各組測試當 repair 案例,preserve 由席位自選。席報告從各席執行紀錄最後一則回覆原樣存檔。

圖譜鏡頭:這輪派工前暖快取、背景輪詢到 14:35:40 命中才派,七席報告都寫 hook 有附上固定席段,逐節點判 guard-kill、lumos-cli-read、bound-tests-gate、pitfalls-code-loop、loop-convergence-recording、測試假綠形態、design-loop、lumos-cli-lifecycle 不受影響。

資安席第一次交的涵蓋範圍寫明完整快照只讀了與修補重疊的部分,請該席讀完整份再重交;重交版逐行讀完 scripts/lumos、兩篇 Systems、手冊與修補差異,測試檔與三份舊計劃用關鍵字掃,判 clean。

## 機械收貨

| 席 | 檔級 | 條數 | 引句 |
|---|---|---|---|
| 正確性 | minor | 1 | 全錨 |
| 資源 | clean | 0 | 零條發現無引句 |
| 邊界 | minor | 1 | 全錨 |
| 整合 | major | 2 | 全錨 |
| 通才 | minor | 1 | 全錨 |
| 架構對齊 | minor | 1 | 全錨 |
| 資安 | clean | 0 | 零條發現無引句;重交後涵蓋全部檔 |

審查席暫存目錄收齊後已刪。

## 發現與處置(全折)

| id | 席 | 等級 | 一句 | 處置 |
|---|---|---|---|---|
| n1 | 整合 | major | `t_choice_kill_merge_off_reasons` 驗「時限到時 run.interrupted 為假」用手建的 kr,恆真;把 `_ChoiceKillRun` 的 interrupted 改成總時限到也算,205 支照綠(實跑重現) | 折:改用真的 `_ChoiceKillRun` 跑到總時限到,讀它的 interrupted 與 merge_off |
| n2 | 整合 | minor | 計劃 S10 預期值表來源欄「e1;、正確性」殘字 | 折 |
| g1 | 通才 | minor | 同 n2;另 S10 條款連列兩次「平台不穩或筆記未提交」易誤讀 | 折:來源欄改寫、條款標明對應兩案 |
| a1 | 架構對齊 | minor | 原因字串只有斷路器抽常數,中斷、時限到仍字面 | 折:同一張原因表的字串一起抽成常數 |
| c1 | 正確性 | minor | 訊號處理裝好之後、`st.on_first` 設好之前的極窄空窗,訊號落在這裡會記成時限到而 run.interrupted 為真(讀碼推得,未重現) | 折:讓 mg 在建 st 時就接上 on_first,或分類時改讀 st.got |
| b1 | 邊界 | minor | `_kill_merge_base` 的「基準量不齊」「合併道不足 2 支」兩個 return 不看停止旗標,停下時記錯原因並印「照逐支跑」(實跑重現) | 折:兩個 return 前先看停止旗標,停下時記中斷或時限到、不印 |

## 歸因(修補鏡頭)

- n1、n2、g1:有證據的修復回歸(r2 修補新加的斷言與表格欄,兩版差異可見)。
- a1:r2 修補只抽了斷路器,未判定是否算回歸。
- c1:未判定(讀碼推得;修前一律記中斷,這個空窗在修前剛好記對)。
- b1:有證據的原有漏查(修前同樣只在 except 處記中斷)。
- regression_set:n1(有證據:修補新加的斷言恆真,重現命令見整合席報告)。

## 先查世界

- n1:測試獨立判準,照 lumos-project-notes `commands/03-寫回圖譜.md`〈實作測試品質〉與 Systems/測試假綠形態(斷言要走真路徑、前置斷言證明現場成立),不另查。
- a1、b1、c1:專案內常數與停止旗標既有寫法,不另查。
- 方向:這組根因(停下原因的分類)在 r2(e1)與 r3 連兩輪出現,但 r3 那組沒有 major(major 是測試假綠,另一組);測試假綠這組是新組。不查方向。
