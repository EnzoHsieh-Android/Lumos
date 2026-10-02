# code-筆記格子第3步 r2 收貨

審材:r1 修正差異(r2-snapshot.patch)。席位(high,5 席+架構對齊+資安):正確性 5、併發資源 2、邊界輸入 1、合約圖譜 6(報告用 1 到 6 編號,這裡記成 R2G1 到 R2G6)、通才 1、架構對齊 6(major 1)、資安 2。共 23 條,major 1 條。
本輪有 major → accepted 必空,23 條全折。R2A4(major)有可執行證據、編排者自己查過(整個 repo 只有這一支吞 stderr 錯誤的小工具),不派辯方。
併發資源席與架構對齊席的報告格式退回原席改過(總結句提到更高等級、檔級等級低於報告內最高),內容未動。

## 依根因分組

1. S16 讀法與單行 summary(R2B1、R2U1、R2C1、R2A1):S16 與 S17 到 S19 共用一支 `_note_summary_entries`(從開頭行重組、續行接回,summary 寫在同一行時整個值當一條)。
2. 輸出清字元(R2S1、R2A3):S16 也過 `_esc_clean`;300 改成具名常數 `_DOCTOR_LINE_MAX`。
3. 推送那支的 stderr 與順序(R2A4、R2A5、R2A6、R2G3、R2C4、R2G5):拿掉 `_drift_retire_quiet`,印出照 m1 與 c1 到 c5 直接 print;順序改回先印後記(同鄰居,也就是 Issue 第 2 項原本提的做法);兜底分法與 m1 不同的理由寫進說明。順序跟鄰居一致後,不再有「先記後印」的宣稱要釘;印出出錯時帳照樣記一筆由 ② 釘住。
4. S18 的 fail-open(R2A2、R2G2、R2C5 前半):照帳增速段的寫法整段包進 try、`ok(f"…跳過(fail-open:{e})")`;測試注入例外驗 doctor 不中斷。
5. lint-new 的設定讀法(R2S2、R2G6):`_lint_new_config` 加 `text` / `from_snapshot`(同 `_nodehome_config`),度量段用 `_doctor_cfg_bytes` 讀好的那份。
6. 記憶體(R2K1):`_drift_jsonl_iter` 逐筆給,`_drift_jsonl_parse` 改成包它;帳增速段與度量段用逐筆版。
7. 二次方(R2K2):`_ns_summary_logical` 收片段最後一次接。
8. 測試(R2C2、R2C3、R2C5 後半):新測試 t_slots_doctor_reminders_r2,補單行 summary、S17 與 S18 清字元、`[[X#d2|別名]]`、S18 fail-open、`_doctor_cfg_bytes` 捷徑、lint-new 吃已讀好的設定;每項翻紅已驗。
9. 文件(R2G1、R2G4):[S13] 補綁兩支新測試;計劃天花板第 13 條與效能那行限定 `when-*`;兩篇系統筆記與 Issue 同步。

## 重現表

| id | 現象 | 怎麼重現 | 結果 | 去向 |
|---|---|---|---|---|
| R2A4 | 另寫一支吞 stderr 錯誤的小工具,整個 repo 只有這裡 | grep 全檔 | HIT | 折(第 3 組) |
| R2A5 | 先記後印跟 m1、c1 到 c5 相反 | 讀三支 report | HIT | 折(第 3 組) |
| R2A6 | 兜底分法與 m1 不同 | 讀程式 | HIT | 折(第 3 組,理由寫進說明) |
| R2G3 | 先記後印沒有測試釘住 | 席位對調實跑仍綠 | HIT | 折(第 3 組:順序改回與鄰居一致,宣稱拿掉) |
| R2C4 | 同 R2G3 | 同上 | HIT | 折(第 3 組) |
| R2G5 | Issue 第 2 項改法與實作相反、沒寫理由 | 讀 Issue | HIT | 折(第 3 組,Issue 補理由) |
| R2B1 | 單行 summary 的 RULE S16 不再列 | t_slots_doctor_reminders_r2 ① | HIT | 折(第 1 組) |
| R2U1 | 同 R2B1 | 同上 | HIT | 折(第 1 組) |
| R2C1 | 同 R2B1 | 同上 | HIT | 折(第 1 組) |
| R2A1 | S16 重組全文是第二條路 | 讀程式 | HIT | 折(第 1 組) |
| R2S1 | S16 沒清控制字元 | 讀程式 | HIT | 折(第 2 組) |
| R2A3 | 同 R2S1;300 是魔術數 | 讀程式 | HIT | 折(第 2 組) |
| R2A2 | S18 fail-open 寫法跟帳增速段不同 | 讀程式 | HIT | 折(第 4 組) |
| R2G2 | S18 的 try 沒測試釘住 | 席位拿掉實跑仍綠 | HIT | 折(第 4 組,④) |
| R2C5 | S18 的 try 與 `_doctor_cfg_bytes` 捷徑檢查沒測試釘住 | 席位拿掉實跑仍綠 | HIT | 折(第 4、8 組,④⑤) |
| R2S2 | lint-new 自己讀設定、捷徑會跟 | 讀 `_lint_new_config` | HIT | 折(第 5 組,⑥) |
| R2G6 | 「統一走 _doctor_cfg_bytes」說得太滿 | 同 R2S2 | HIT | 折(第 5 組) |
| R2K1 | 帳增速段改成整份解析後尖峰翻倍 | 席位 tracemalloc 實量 58MB → 124MB | HIT | 折(第 6 組) |
| R2K2 | `_ns_summary_logical` 接續行二次方 | 席位實量 2MB 8 秒 | HIT | 折(第 7 組) |
| R2C2 | `[[X#d2|別名]]` 的別名切除沒測試釘住 | ③ | HIT | 折(第 8 組) |
| R2C3 | S17、S18 清字元沒測試釘住 | ② | HIT | 折(第 8 組) |
| R2G1 | 新測試沒綁進條款 | 讀計劃 [S13] | HIT | 折(第 9 組) |
| R2G4 | 計劃兩處仍寫「doctor 不評估條件」沒限定 | 讀計劃 | HIT | 折(第 9 組) |
