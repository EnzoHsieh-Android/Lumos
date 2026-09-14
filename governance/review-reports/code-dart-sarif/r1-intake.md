# code-dart-sarif r1 收貨紀錄(2026-09-14)

七席全部收齊才動樹;報告存 repo 外、收齊後搬進卷證。`report-normalize` 七份都已是正規格式;`quote-check` 對 r1-snapshot.patch 六份全錨定(資安席 clean、無引句)。

## 發現對帳(id → 處置)

| id | 席 / 原編號 | 等級 | 內容 | 編排者重現 | 處置 |
|---|---|---|---|---|---|
| a1 | 正確性 F1 | major | 診斷清單混進非物件元素 → 略過、rc0 零告警(假乾淨) | HIT:`{"diagnostics":[42]}` → rc0、results [] | 折:形狀任何一處不對一律 ValueError → rc2 不寫檔;測試三種壞形狀 |
| a2 | 正確性 F2 | minor | 巢狀欄位型別不對 → AttributeError 追蹤訊息 rc1 | 讀碼確認 | 折:同 a1 的逐層型別檢查 |
| a3 | 正確性 F3 | minor | 「給不存在的檔印用法說明」與宣告 2>/dev/null 對不上 | HIT:用法說明在 stderr | 折:docstring、筆記、測試案例改寫 |
| b1 | 架構對齊 F1 | major | `_dart_rel` 另立第三套路徑正規化 | 讀碼確認 | 折:刪 `_dart_rel`,路徑原樣交給適配器;共用正規化補「比真實路徑」 |
| b2 | 架構對齊 F2 | minor | 從第一個 { 重解的分支沒測試、沒交代 | 讀碼確認 | 折:刪掉重解,只認整段 JSON |
| c1 | 整合同步 F1 | major | 文件教的宣告讓 `lint-check --smoke` 誤報跑不動 | HIT:同一台有 dart,冒煙判跑不動;ruff 宣告冒煙通過 | 折:冒煙把 {LINT_FILES} 換成專案裡真有的該棧檔 |
| c2 | 整合同步 F2 | minor | README.en 把 09-14 的 Dart 放進「As of 2026-09-13」 | 讀檔確認 | 折:改句標兩個日期 |
| d1 | 邊界可執行 F1 | minor | 前導雜訊含 { 時救不回 | HIT | 折:刪掉救援,混雜輸出一律讀不懂(有測試) |
| d2 | 邊界可執行 F2 | minor | 尾隨雜訊判讀不懂 | HIT | 折:同 d1,文件寫明只認整段 JSON |
| d3 | 邊界可執行 F3 | minor | --out 父目錄不存在 → 追蹤訊息 rc1 | HIT | 折:接 OSError → rc2 講清楚(這輪有 major,不走放行) |
| e1 | 合約一致 F1 | minor | 同 a3 | 同 a3 | 折:同 a3 |
| x1 | 外家finder F1 | major | 快照缺 Dart 套件解析 → 新碼上報假錯誤 | HIT:真 Dart 套件(collection 依賴+相對 import),專案內分析 1 條、快照多 1 條假 undefined_function | 折:轉換器不收 COMPILE_TIME_ERROR;重跑同一專案只剩真的那條 |
| x2 | 外家finder F2 | major | 同 a1 | 同 a1 | 折:同 a1 |
| x3 | 外家finder F3 | minor | 圖譜綁的測試沒走新增告警閘 | 讀碼確認 | 折:新增 t_dart_gate_with_fake_analyzer(假 dart 走 _lint_new_verdict,CI 無 dart 也跑) |
| x4 | 外家finder F4 | minor | 兩篇筆記 updated 沒更新 | 讀檔確認 | 折:lumos set updated 2026-09-14 |

資安席:clean(逐類已看,無)。refuted:none。accepted:none(這輪有 major)。

## 翻紅驗證(拆修正 → 對應測試紅)

- 看不懂的項目改回略過 → t_dart_sarif_bridge 紅
- 編譯期錯誤照收 → t_dart_sarif_bridge、t_dart_gate_with_fake_analyzer 紅
- 共用正規化不比真實路徑 → t_dart_sarif_bridge(符號連結案例與真機端到端)紅
- 冒煙不換檔 → t_lintcheck_smoke_fills_lint_files 紅
- 寫檔保護拆掉 → t_dart_sarif_bridge 紅
