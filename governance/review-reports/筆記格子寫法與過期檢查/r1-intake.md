# 設計審 r1 收貨紀錄(筆記格子寫法與過期檢查)

preflight-4: ran

## 首輪前掃(haiku;報告原文 r1-preflight.md)

- ① 未定義的詞 0、② 壞引用 0、③ 範圍矛盾 0。
- ④ 機械宣稱:note-shape 擋 FACT 沒帶來源、LUMOS_SKIP_NOTE_SHAPE、parse_rule_fields、drift_check.old_sentence 子開關先例、既有斷連結檢查——成立。`note_shape.slots` 與來源預設週期「查不到」:兩者是本篇要新增的東西,不是錯誤宣稱;已在計劃裡標明「新增」「本篇新訂」(修真檔,不算 finding)。

## 收貨三道

- report-normalize:六份都已正規化,沒改。
- quote-check(對 r1-snapshot.md):六份全數錨定(正確性 32、資源併發 29、回滾 27、架構 21、整合 20、邊界 19 句)。
- refcheck:六份引的 file:line 全部存在。

## 編排者重現

| 席位 id | 重現 | 結果 |
|---|---|---|
| B1 K2 C1 R3 I7 | `_NOTE_SHAPE_GOLIVE_MARK` 是 `note-shape --staged`;格子規則若共用,範圍從既有上線點截斷 | HIT 採信 |
| B2 K1 C4 I2 R5 | `RETIRE_REF_RE` 為 `[^\]]*`,`[retire:事件 [[Projects/a]] 狀態=done]` 會在第一個 `]` 截斷(席位實跑) | HIT 採信 |
| K6 C3 | `lumos guard plan` 寫出 `WHY:[{today}]預告這條合約但還沒做` 樣板 | HIT 採信 |
| K5 I10 | `_plan_system_links` 只讀 `DEP:` 行的連結 | HIT 採信 |
| 其餘 | 引句全數錨定,佐證行都附 file:line 且 refcheck 全過;同一現象多席獨立指出 | 採信 |

refuted-set:none。

## 處置

67 條全部折入:格子自己的上線點、改到舊行(同前綴同核心一句只改欄位)不算新寫、新的欄位解析器認雙括號、撤除條件改用 `when-*` 語法與新寫抽取段、lint 與擋同一張表並逐字釘住、工具樣板豁免、SEE 第 0 步註冊並改讀連結的程式、擋下訊息上限與清理、總開關與子開關關係、recheck 與日期格式、度量白名單、skill 舊格式清單、治理帳記格子違規;Enzo 裁「不留(LOG)、不擋(取代鏈只提醒)、合(觀測日期併進 confirmed)」,`by` 改名 `[取代:]`;分類計劃三處同步修訂、依賴欄位計劃標成已併入。
