# 設計審 r2 收貨紀錄(筆記標籤-過時判定與按需載入)

## 收貨三道(六席)

- report-normalize:六份都已正規化,沒改。
- quote-check(對 r2-snapshot.md):六份全數錨定(整合 38、架構 33、邊界 23、正確性 21、資源併發 20、回滾 18 句)。
- refcheck:架構對齊席一處 `Systems/check-n-recomputable.md:101` 行號超出檔案長度(檔案 89 行);其餘全部存在。

## 編排者重現

| 席位 id | 重現 | 結果 |
|---|---|---|
| R2A6 | 行號超界;機械重現:該篇存在、內容是 doctor N 的可重算數字段(關鍵字命中 5 處),「動 doctor N 重算要寫進這篇」的宣稱成立,只有行號錯 | HIT 採信(行號不採) |
| R2C1 | `_drift_probe_judge` 判的是「終點成立而起點沒有同一條或還不成立」——方向是不成立變成立 | HIT 採信 |
| R2C4 R2I3 | `_drift_cond_split` 用 `rsplit("::", 1)`(席位實跑 `src/x.rs::Client::connect` 切成 `src/x.rs::Client` 與 `connect`) | HIT 採信 |
| R2C3 R2B1 R2R1 | `cmd_drift_check` docstring:判不了算要處理 | HIT 採信 |
| 其餘 | 引句全數錨定,佐證行都附 file:line 且 refcheck 全過;同一現象多席獨立指出 | 採信 |

refuted-set:none。

## 處置

66 條全部折入(散文設計審)。Enzo 裁「拆」:依賴欄位的機械判定整段搬到 [[Projects/依賴欄位_過時判定_計劃]],欄位相關的發現(R2A1–A6、R2B1–B6、R2B8、R2B9、R2B12、R2B16、R2C1–C5、R2C7、R2C9–C11、R2I1–I5、R2I7、R2I10、R2K1–K4、R2R1–R7)逐條列在那份的〈待解問題〉,本篇以刪除該範圍折掉;非欄位的發現(R2A7–A11、R2B7、R2B10、R2B11、R2B13–B15、R2C6、R2C8、R2C12–C14、R2I6、R2I8、R2I9、R2I11、R2I12、R2K5、R2K6)在本篇第三版折掉:到期提醒改走 doctor、紀律範本兩處說法對齊、W4 與開關第 0 步一起上線、RETIRE-IF 不宣稱有擋、已作廢訊息改寫、搜尋行模式 `--top` 預設全給並帶 `hidden_lines`、`--about` 改用既有「每支檔有家」對照、範例反引號說明、W2 與不評估區提醒拿掉。同時依兩次分類實驗與 Enzo「分類要有規律」改以分類為主軸。
