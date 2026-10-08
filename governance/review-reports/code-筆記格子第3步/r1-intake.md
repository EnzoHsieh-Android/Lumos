# code-筆記格子第3步 r1 收貨

席位(high,5 席+架構對齊+資安):正確性 5 條、併發資源 1 條、邊界輸入 5 條(major 1)、合約圖譜 6 條(major 2)、通才 1 條、架構對齊 7 條(major 2)、資安 1 條。共 26 條,major 5 條。
本輪有 major → accepted 必空,26 條全折。5 條 major 都有可執行證據且編排者自己重現過(G1 另有 U1、C2 兩席獨立同報),不派辯方。

## 依根因分組(一組一次修完所有相似路徑)

1. doctor 對筆記與帳的輸入要自己重驗(B1、B2、B4、C5):度量先過提交時同一支 _slot_retire_err,寫不合列成提醒不判;治理帳時間的 astimezone 包進 try;帳增速那段同族一起改。
2. 輸出清控制字元(S1、B5):三段組字串一律過 _esc_clean。
3. S17 範圍(G1、U1、C2、C5、A2):只看標了作廢的行、空值不判;決策引用改用 _dref_parse / _dref_norm,[[X#dN]] 也查決策。
4. 設定讀法(A1、B3、C1):三份抄寫的「捷徑不跟」讀法抽成 _doctor_cfg_bytes,度量段共用;lint-new 鍵名改 mode;拿掉吞例外。
5. 推送那支的兜底(K1、A7):rc 判完就定、先記帳再印,記帳與印出各自兜、stderr 壞了也不拋;分法與 m1 不同的理由寫進說明。
6. 跟鄰居對齊(A3、A4、A5、A6):S16 改用同一支續行接回;_slot_superseded 拿掉改用 _ns_superseded;S19 不自截 20 條;S18 整段包住;帳增速那段改用 _drift_jsonl_parse。
7. 文件(G2、G3、G4、G5、G6):計劃 [S13] 與表格三列、程式註解、skill 子檔 04、兩篇系統筆記、Issue 改回 doing。
8. 測試(C3、C4):新測試 t_slots_doctor_reminders_edges,補五種比較中沒走過的、週與月、naive 時間、出界時間、lint-new、--ci、清字元、檔尾截斷、S16 續行;記帳拋非 OSError 例外的情境進 t_slots_retire_issue_followups。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| G1 | S17 對散文提到鍵名的行誤報(工具鏈自己的 lumos-cli-read 第 14 行) | 對本 repo 圖譜呼叫 _doctor_replacement_lines,回 1 條「寫法認不出」 | HIT | 折(第 3 組) |
| U1 | 同 G1 | 同上 | HIT | 折(第 3 組) |
| C2 | 同 G1 | 同上 | HIT | 折(第 3 組) |
| A1 | 度量段自己讀設定檔,沒有捷徑防護;設定讀法第三種 | 讀 _doctor_metric_lines 對照 _drift_gate_doctor_lines | HIT | 折(第 4 組) |
| A2 | 節點#dN 另寫一套解析 | 讀 _slot_replacement_dead 對照 _dref_parse | HIT | 折(第 3 組) |
| B1 | 近 99999999999 週讓 doctor 崩 | t_slots_doctor_reminders_edges ②;拿掉重驗即崩 | HIT | 折(第 1 組) |
| G2 | [S13] 與表格字面跟程式、綁定測試相反 | 讀計劃第 137、141、212 行 | HIT | 折(第 7 組) |
| B2 | 帳裡 9999 年的時間讓度量段崩 | ⑤;astimezone 拿出 try 即紅 | HIT | 折(第 1 組) |
| B3 | lint-new 關掉認不得 | ④ | HIT | 折(第 4 組) |
| C1 | 同 B3 | 同上 | HIT | 折(第 4 組) |
| B4 | 拼錯閘名當成零筆而成立 | ② | HIT | 折(第 1 組) |
| B5 | 三段沒清控制字元 | ⑧ | HIT | 折(第 2 組) |
| S1 | 同 B5 | 同上 | HIT | 折(第 2 組) |
| C3 | 多個變異拿掉測試仍綠 | 席位實跑;補測試後各自翻紅 | HIT | 折(第 8 組) |
| C4 | 週與月沒有斷言 | ⑦ | HIT | 折(第 8 組) |
| C5 | [[X#d9]] 只查節點不查決策 | ① | HIT | 折(第 3 組;「無理由」與「無…開頭的路徑」照 lint 既有的 _slot_replacement_err 同一判法,不另立) |
| K1 | 記帳拋 OSError 以外的例外整支冒出去 | ②b | HIT | 折(第 5 組) |
| A3 | S16 逐實體行、S17 到 S19 接續行;_slot_superseded 重複 | ⑩ | HIT | 折(第 6 組) |
| A4 | S19 自截 20 條是第二套截斷 | 讀 warn_soft | HIT | 折(第 6 組;計劃表格同步改) |
| A5 | S18 沒包住,帳讀失敗整個 doctor 中斷 | 讀程式對照帳增速段 | HIT | 折(第 6 組) |
| A6 | 帳增速段與度量段切行規則不同 | 讀程式 | HIT | 折(第 6 組) |
| A7 | 推送那支的兜底分法與 m1 不同 | 讀程式 | HIT | 折(第 5 組,理由寫進說明) |
| G3 | 程式註解還說 scan 先不列 retire | 讀程式 | HIT | 折(第 7 組) |
| G4 | skill 子檔 04 沒補 retire 與 S17 到 S19 | 讀檔 | HIT | 折(第 7 組) |
| G5 | 「doctor 不評估條件」與 S18 字面有張力 | 讀筆記 | HIT | 折(第 7 組) |
| G6 | Issue 審查前就結案 | 讀筆記 | HIT | 折(第 7 組,改回 doing,推上主線後結案) |
