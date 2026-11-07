preflight-4: ran

# r1 收貨紀錄(android寫法型錄逐列查證:2026-11-08 人裁落地)

## 首輪前掃

便宜代理四類前掃。①②③直接修真檔:「取捨提醒」補定義、做法第 4 點補人裁後的現況、「三件」改成「三項(API-14、TEST-31、DATA-12)」。④語意類:

| 編號 | 修改前 | 修改後 | 依據 |
|---|---|---|---|
| P1 | S3 綁 t_kotlin_rulepack_unwired_dir,但測試沒點名三條規則、沒驗兩列標記 | 測試加 ⑧(兩列名稱有出處不全)、⑨(三條規則都在 rules-unwired/)、⑩(假規則放 rules/ 要報);改壞驗證:拿掉 API-14 標記 → ⑧紅;一條搬回 rules/ → ⑥⑦⑨紅 | 前掃代理讀測試 |
| P2 | 預期值表 S3 第二列「假規則放 rules/」測試裡沒有這種輸入 | ⑩ 補上 | 同上 |
| P3 | t_kt_catalog_security_lint_ids 說明字串還寫「維持 2 列」 | 改成 0 列 | 同上 |

## 收貨

四席全數交回後寫進卷證;報告從逐字稿取最後一則。通才席第 3 條原本把快照外的 linter 目錄原文寫成引句,退回改走佐證通道,存重交版(編排者在重交版到之前已開始修,修的內容不依賴那條引句的位置)。架構對齊席用 report-normalize --write 純格式搬移。四份 quote-check 全數錨定。

編號:通才 G1–G3、邊界 B1–B3、整合 I1–I6、架構對齊 A1–A4,共 16 條,全是 minor。

## 根因分組與處置

| 組 | 成員 | 處置 |
|---|---|---|
| DATA-12 改寫的語意 | G1 B3 I5 A4 | 不用新詞「取捨提醒」,改成型錄既有口徑的人裁列(名稱標(人裁)、接電方式只寫表態對程式、不盲判);標準寫法與後果補「新值要靠目前值算的不要拆成先讀再寫,會讓併發更新互相蓋掉」;D-42 同步 |
| 承認少擋卻沒回頭條件 | G2 I6 | 補 REVISIT 2027-02-08 重查兩列出處(附 JetBrains Redundant async 線索),找到就搬回 |
| 舊說法舊數字 | G3 I1 I2 A1 A3 | linter 目錄範例改 `[API-15]`;規則包節點補第二批搬移;覆核級計劃撤除條件與那批說明補註;型錄第 11 行改成已裁;計劃 updated 日期;依據來源補人裁一列 |
| 決策表引用出處不全列 | G3 B2 I4 | D-1、D-2 來源格加註 API-14 出處不全只當參考 |
| 出處不全沒定義 | I3 | 型錄〈輸入與口徑〉補定義(有查證紀錄卻標出處不全=那一頁只支持部分主張) |
| 原有檢查缺口 | B1 | 放行:STATE-9 那型是這次以前就有的缺口(檢查只看規則訊息編號);補 REVISIT 回頭看要不要也比現成規則欄 |
| 決策欄位 | A2 | 放行:專案裡已有同樣只寫四鍵的決策(覆核級計劃 d3),不算偏離 |

## 先查世界

- PRIOR-ART:DATA-12:官方 DataStore 參考頁(https://developer.android.com/reference/kotlin/androidx/datastore/core/DataStore)寫 updateData 是 atomic read-modify-write、所有操作依序執行、transform 是協程可做重活;據此補「新值靠目前值的不要搬出去」。其餘是文件一致性,不查外部。

## 重現

| id | 驗法 | 結果 |
|---|---|---|
| G1 | 讀官方頁 atomic read-modify-write | HIT |
| B1 | STATE-9 列與 rules/state.yml 的 kt-statein-lazily-or-no-timeout | HIT |
| I1 | rules-unwired/ 數 14 條、來源 | HIT |
| I3 | 數出處不全又有查證紀錄的列 | HIT:22 列 |
| 其餘 | 讀碼與讀型錄 | HIT |

修後:型錄自檢 0 個問題、還沒逐列查證 0 列;`-k kt_catalog` 48、`-k kotlin_rulepack_unwired` 11、`-k kt_situation` 135、`-k kotlin_catalog` 59 全綠。
