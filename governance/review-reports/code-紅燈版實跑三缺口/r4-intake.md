# r4 收貨紀錄(code-紅燈版實跑三缺口)

## 收貨

- r3 到頂後人裁加開的驗收小輪(cap-decision extra-round,2026-11-03 Enzo 裁「拿掉這段、換形狀(推薦)」)。兩席全新(單reviewer-sonnet、架構對齊-sonnet)審 r4-repair-review.patch(修前 e0603d082 → 修後 374e77519,405 行;來源 r4-repair-binding.json;待驗案例 r4-behavior-cases.md)。報告從逐字稿原樣存檔,兩份都已是正規化格式,引句全數錨定。
- 兩席交回期間 repo 沒被席位改動:`git status` 只有兩份新報告;`git reflog` 頂端是編排者自己的提交 a0f17202a。兩席都自己清了暫存(單審席另刪了一個自己留下的 gctl-run 現場)。
- 本輪仍有 major,依規停下攤人;2026-11-03 Enzo 裁「修完派一小輪驗收(推薦)」。

編號:單審席 F1–F5 記 H1–H5;架構對齊席 Finding 1–2 記 K1–K2。共 7 條;major 2 條(H1、K1),其餘 minor。全數折入,沒有放行,沒有重現不到的。

## 編排者重現

| id | 案例 | 結果 | HIT/MISS |
|---|---|---|---|
| H1 | 設定改回單平台、實作已綠:照擋下訊息「重跑規格閘」或「改一個字讓留痕過期再重跑」 | 讀碼:`_spec_gate_low_not_red` 條款沒變且全綠時回 0 不寫留痕;改字後全綠判「實作後才跑」擋下。席位兩版實跑 PUSH1/RERUN_SAME/RERUN_CHANGED 成立 | HIT |
| H2 | `assertTrue("""\n assertEquals mention\n """, f() > 0)` 取代 `assertEquals(1, f())` | 讀碼:`_tg_strong` 用 `_TG_LIT_PAT` 剝字串,認不得跨行原始字串;斷言文字現在保留換行 | HIT |
| H3 | 帶 `.trimIndent()` 的多行原始字串整檔重新縮排 | 讀碼成立;Kotlin 官方:trimIndent 去掉共同最小縮排,整段重新縮排執行時值不變 → 多報一條可放行的 tq/expected-changed | HIT |
| H4 | 第二個呼叫點(中綴斷言那行)改回整段壓空白,-k tq_guard 照綠 | 讀碼成立 | HIT |
| H5 | cfg_gone 的已完成計劃路徑拿掉 `not done`,-k spec_gate 照綠 | 讀碼成立 | HIT |
| K1 | `_tg_ws_keep_strings` 的掃描迴圈是 `_tg_ident` 的複製版 | 讀碼成立 | HIT |
| K2 | cfg_gone 擋下訊息句型跟 bad_plat 不同 | 讀碼成立 | HIT |

## 歸因(修前 e0603d082、修後 374e77519)

| id | 歸因 | 依據 |
|---|---|---|
| H1 | 有證據的修復回歸 | 修前放行、修後擋下且訊息教的路走不通(席位兩版實跑) |
| H2 | 有證據的修復回歸 | `_tg_strong` 對同一敘述修前 0、修後 1(席位兩版實跑) |
| H3 | 有證據的修復回歸(設計取捨) | 修前空、修後列 tq/expected-changed(席位兩版實跑) |
| H4 | 有證據的原有漏查(測試覆蓋) | 同族兩個呼叫點只測了一個 |
| H5 | 未判定 | 修前沒有這條路;現行行為席位探針驗過正確 |
| K1 | 有證據的修復回歸 | r3 修補新寫的函式 |
| K2 | 有證據的修復回歸 | r3 修補新寫的訊息 |

regression_set:H1、H2、H3、K1、K2(H5 未判定,原因:修前沒有對應路徑可比)。

## 先查世界(r4 修補前,2026-11-03;字串處理這一族 r1–r4 都出現,依 Enzo「兩輪都碰到就上網找」)

- Kotlin 官方 `trimIndent()`:去掉所有非空白行的共同最小縮排、頭尾空白行拿掉、輸出一律 LF(https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.text/trim-indent.html);所以帶 trimIndent 的多行字串整段重新縮排執行時值不變。社群另有編譯期外掛處理模板值帶縮排的情形(https://github.com/bennyhuo/kotlin-trim-indent),表示要精確模擬還得處理模板,本案不模擬。
- H1 的出路沿用規格閘既有的「實作後才跑」補法(`_spec_gate_low_not_red` 印的步驟),不另立機制。

## 根因分組與處置

| 組 | 根因 | id | 處置 |
|---|---|---|---|
| 1 | 換形狀後擋下訊息承諾的「重跑」在實作已綠時無效 | H1、K2 | 訊息改講兩條實際可行的路:照規格閘「實作後才跑」的補法(先提交、把實作換回空殼讓測試紅、跑規格閘、換回)或把計劃改成 plan_risk: high 走設計審;句型對齊 bad_plat;補「實作已綠時訊息講補跑、不講單純重跑」的斷言 |
| 2 | 新函式複製了 `_tg_ident` 的掃描迴圈 | K1 | `_tg_ident` 加選填的字串外壓法參數,`_tg_ws_keep_strings` 改成呼叫它(一支掃描迴圈) |
| 3 | 斷言文字保留換行後,剝字串改用單行樣式的 `_tg_strong` 認不得跨行原始字串 | H2 | `_tg_strong` 改用 `_tg_strip`(同一支 `_C_STRIP_PAT`,認得三引號跨行)清空字串內容再數;補案例 |
| 4 | trimIndent 字串重新縮排多報 | H3 | 計劃寫成已知限制(只多報一條可放行的候選、不漏擋),附 REVISIT 與官方語意出處 |
| 5 | 同族兩個呼叫點/兩條路只測一條 | H4、H5 | 補中綴斷言字串裡多一格空白、已完成計劃 cfg_gone 降成提醒兩個案例 |
