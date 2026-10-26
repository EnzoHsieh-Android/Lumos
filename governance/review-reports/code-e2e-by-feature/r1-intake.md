# code-e2e-by-feature r1 收貨紀錄

七席全交回(2026-10-26):正確性、資源、邊界與輸入、合約與圖譜一致、通才、資安、架構對齊。引句全數錨定;通才席總結句寫了「沒有 major 以上」被格式檢查當成藏等級,退回該席只改那一句後重存。git reflog 核過,席位沒動 repo。

編號:正確性 C1–C11、資源 R1–R2、邊界 B1–B7、合約 K1–K9、通才 G1–G7、資安 S1–S2、架構 A1–A5,共 43 條,blocking 6 條(C1 C2 C3 B1 K1 A1)。

## 根因分組與重現

重現方式:把新測試放進修正前的版本(9e21d491 的乾淨副本)跑,紅=重現到;另對修正後的版本故意改壞三處(拿掉分岔點差異、記憶體情境讀不到結果、預檢改回舊條件),各自有測試翻紅。

| 組 | 編號 | 重現 | 去向 |
|---|---|---|---|
| 文件說法:按功能跑「不寫紀錄」與實作相反 | C1 K1 K2 K5 G7 C10 | HIT:grep 命中手冊、help、docstring、範本檔頭、S22/S24 | 折:改成「不寫整套的紀錄,乾淨時按情境寫 feature_runs」,手冊補單獨重判要加 --no-record |
| 測試沒守住分岔點與記憶體情境 | C2 C3 K8 | HIT:三處故意改壞在修正前的測試全綠,新測試各自翻紅 | 折:t_android_e2e_changed_pick、t_android_e2e_memory_by_case,補沒判完回 1 與被中斷記總表 |
| --changed 挑漏 | B1 B6 B7 | HIT:新測試在修正前紅(沒追蹤目錄、只改 flow、寫法不同跑兩次) | 折:沒追蹤的檔逐檔列;改到情境列的 flow 也算那個功能;去重用 _e2e_norm |
| 設定檢查太晚或太鬆 | C4 C5 B2 B3 R1 G4 | HIT:#foo、含空白、cycles 10^9 在修正前 check-config 回 0 | 折:方法名規則搬進設定檢查(收 $、擋開頭 #);情境輪數上限 10000 |
| 旗標解析 | C11 B4 G3 G6 | HIT:--chaged、單獨 --no-memory 在修正前回 0 並整套跑 | 折:不認得的 - 開頭參數與沒配挑法的兩個旗標在動 App 前回 2;終端照情境列(C11 前半) |
| 紀錄可信度 | S1 G2 C9 S2 | HIT:開跑時髒、判讀時乾淨寫了 feature_runs;只列效能記成 pass、complete;不完整蓋掉完整 | 折:dirty 不是 false 就不寫;沒有會判項目記 unjudged、不完整;同一版完整的不被蓋 |
| 總表寫讀 | A1 A2 C7 C8 R2 G5 B5 K3 | HIT:擋下的那次不進總表、--last 0 列全部、半行黏行 | 折:追加走 _local_ledger_append 加補換行、讀走 _canary_ledger_rows 加 deque、擋下也記、--last 要正整數 |
| 整套跑涵蓋 | C6 G1 | HIT:整套只收 stability 段本身;兩個效能方法只剩最後一個的結果 | 折:整套收每個 stability_scenarios 並各判一次;每個方法跑完就收進自己的子目錄,補 S28 |
| 架構重複 | A3 A4 A5 | HIT:讀設定兩份手寫、兩種錯誤前綴、欄位清單無守衛 | 折:按功能跑讀設定改走 _macrobench_config;情境設定先驗、只在有時併入;補兩邊清單比相等的測試 |
| 文件與 skill 補述 | K4 K6 K7 K9 | HIT:讀文件對照程式 | 折:reference、skill、README、圖說明照程式改 |
| 舊紀錄格式語意 | C10 | HIT:docstring 寫只有放行 runs 是 null | 折:docstring 說明兩種 runs 是 null 的情形 |

沒有機械重現不到的條目(refuted 為 none)。同輪有 major,所以 minor 也全折、沒有放行。
