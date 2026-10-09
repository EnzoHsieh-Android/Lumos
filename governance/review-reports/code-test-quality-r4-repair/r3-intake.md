# r3 intake

preflight-4: ran

編排說明：帳面在 r1 定錨為 codex 編排；本輪實際由 Claude Code 會談編排，四席為新開的 Claude sonnet（回歸正確性、邊界、測試殺傷力、架構對齊），兩位辯方為 Claude opus。未改帳面編排者欄，避免回溯翻動前兩輪的同門/外家判定。四席收齊後才寫入卷證；收貨時被審 repo 無改動（git status 只有本輪派工單）。

收貨機械檢查：四份 report-normalize 皆已正規化；quote-check 只有測試殺傷力席 MUT-2 的跨行引句錨不到，改由編排者機械重現（見下表）；邊界席 BND-2 的佐證行號超出檔長，同一現象由 REG-1 重現。

## 重現與處置

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| REG-1 | 回歸正確性 | minor | HIT | folded | 假 backend 往 stderr 寫 11 MiB 後印合法 JSON：10d40f30 為 scanned、c4982cb1 為 unavailable output exceeds 10 MiB；決策寫進 test-quality-multilang 的 WHY，`test_semgrep_report_over_evidence_limit_is_structured_unavailable` 釘住結構化不完整 |
| BND-2 | 邊界 | minor | HIT | folded | 與 REG-1 同一現象同一處置 |
| BND-1 | 邊界 | minor | HIT | folded | 兩檔掃描、假 backend 卡住，2 秒後 SIGTERM：c4982cb1 rc2 等滿 30 秒且續掃第二檔；10d40f30 rc143 立即結束但留下 backend 子程序。修後 `test_sigterm_during_semgrep_stops_scan_and_backend` 5 秒內非零結束且程序群已清 |
| ARC-2 | 架構對齊 | minor | HIT | folded | Semgrep backend 以訊息字串分類逾時；改為 CaptureTimeout/CaptureInterrupted 型別 |
| MUT-2 | 測試殺傷力 | minor | HIT | folded | 引句錨不到，編排者重現：把逾時比對字串改壞後 scanner 24/24 照綠；修後變異 MB（拿掉逾時分類）紅在 `'unavailable' != 'timeout'` |
| MUT-1 | 測試殺傷力 | major→辯方判 minor | HIT | folded | launcher 退出分支改 break 後該測試照綠、worker 留下（pid 41051 手動清）；辯方乙指出兄弟測試 20/20 抓到同一變異故降 minor。修後測試先證 worker 寫進同一管線再斷言死亡，變異 MA 紅在 `True is not false` |
| MUT-3 | 測試殺傷力 | minor | HIT | folded | 拿掉 backend 的 cwd 後 scanner 24/24 照綠；修後變異 MD/ME 紅在隔離 rules 目錄與 metrics 環境變數斷言 |
| MUT-4 | 測試殺傷力 | minor | HIT | folded | 原有 Semgrep worker 控制只有成功退出、worker 關閉管線；新增成功/非零/逾時三出口、worker 握住管線的子測試 |
| ARC-1 | 架構對齊 | major | HIT | folded | 模型印 done 即退出、留下握管線子程序：model_command 3.0 秒後拋 TimeoutExpired。辯方甲判維持 major（10d40f30 與 c4982cb1 同樣誤判，屬原有漏查）。改走共用 runner 後 `test_exited_model_with_stream_holding_worker_is_not_timeout` 綠 |
| ARC-3 | 架構對齊 | minor | HIT | folded | 只帶 test_quality_scan.py 與 adapter、不帶 core 時純 Python 掃描 ModuleNotFoundError；scanner 改成帶 --semgrep 才載入 adapter，與既有「選配適配器延後載入」決策對齊 |
| ARC-5 | 架構對齊 | minor | HIT | folded | 掃描測試載入 adapter 時多插 sys.path，鄰居 CLI 測試沒有；已移除。存活檢查小工具各測試腳本自帶，repo 沒有共用測試輔助模組，不另建 |
| ARC-4 | 架構對齊 | minor ⚠ | MISS | refuted | 評測外層 50 秒強殺 scanner 時會不會留下 Semgrep 程序群：實跑卡住的假 backend，scanner 在 40.2 秒被自身 backend 預算收掉、早於外層，背景子程序已清；每案只掃一檔，backend 預算 40 秒小於外層 50 秒 |

## 根因分組

- 甲（程序群清理只有一套）：ARC-1、MUT-1、MUT-4。handbook 模型命令改走共用 runner；繼承管線的控制補上 worker 存活斷言與非零、逾時出口。
- 乙（例外靠訊息字串分類）：BND-1、ARC-2、MUT-2。共用 runner 改丟兩個 ValueError 子型別，訊息不變；backend 按型別分類，中斷往上傳。
- 丙（測試沒守到參數與上限）：MUT-3、REG-1、BND-2。假 backend 記錄實際 cwd 與環境變數；上限行為寫成決策並以測試釘住。
- 丁（依賴方向）：ARC-3、ARC-5。

## 歸因

- 有證據的修復回歸：REG-1/BND-2（上限由 c4982cb1 改走共用 runner 帶入）、BND-1（c4982cb1 前 SIGTERM 立即結束，之後被吞）、ARC-3（c4982cb1 在 scanner 主流程頂部匯入 adapter）。
- 有證據的原有漏查：ARC-1（handbook 檔兩版逐位元相同、兩版同樣誤判）、MUT-2、MUT-3（兩版都沒有測試守）。
- MUT-1、MUT-4：本輪新增測試的強度不足；修前沒有同一案例可比，產品行為兩版皆會清 worker，歸因未判定以外不另列回歸。
- regression_set：REG-1、BND-2、BND-1、ARC-3。

## 三問

1. 原問題修復效果：r2 的 Semgrep worker 殘留在 10d40f30 紅、c4982cb1 綠（測試殺傷力席與回歸席各自實跑）；繼承管線不誤判逾時在 10d40f30 紅於 timeout。
2. 正常與相鄰路徑：空輸出、非 UTF-8、形狀錯、越界行號兩版 status 與 reason 相同；CLI capture receipt 的逾時與中斷訊息不變；handbook 逾時仍拋 TimeoutExpired 並保留部分輸出（`test_model_timeout_keeps_partial_stream`）。
3. 新發現同一案例兩版結果見上表。

## 未驗範圍

真 Semgrep 二進位、PGID 重用與 killpg PermissionError（兩席都沒構造出可重現場景，結構在修補前已存在）、Windows。本輪收折後的修補差異尚未經全新席回歸審；loop 為 standard 上限三輪，再審需人裁加輪。
