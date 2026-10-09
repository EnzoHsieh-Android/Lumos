# r4 intake

preflight-4: ran

編排說明：Enzo 2026-10-08 在對話中裁定加開一輪（cap-decision extra-round 已記，跑滿回顧已 --record）。帳面定錨 codex 編排；本輪由 Claude Code 會談編排，四席為新開的 Claude sonnet。四席收齊後才寫入卷證；收貨時被審 repo 只有本輪派工單未追蹤。

收貨機械檢查：邊界資源與測試殺傷力兩席首行總結句寫了「整份沒有 blocker 或 major」，report-normalize 判成總結藏更高等級，退回兩席只改這一句措辭（其餘逐字不變）後重收，兩份皆已正規化。架構對齊席 ARC4-4、ARC4-5 的引句取自審材外的既有程式，quote-check 錨不到；兩條描述的程式事實由編排者直接讀 a2f30b19 核對成立（見下表），不採其引句作憑據。本輪四席最高皆為 minor。

## 重現與處置

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| REG4-1 | 回歸正確性 | minor | HIT | folded | 假 claude 印 11 MiB：a2f30b19 的 run_model 拋 ValueError、場次紀錄未寫；改為無效場次並照樣寫檔，`test_model_output_over_limit_is_invalid_session_not_abort` 先紅後綠，變異 N2 紅 |
| BND4-2 | 邊界資源 | minor | HIT | folded | 與 REG4-1 同一現象；另更正驗證紀錄中「超過 10 MiB 仍回結構化錯誤」對模型命令不成立的句子 |
| MUT4-1 | 測試殺傷力 | minor | HIT | folded | 與 REG4-1 同一現象同一處置 |
| BND4-1 | 邊界資源 | minor | HIT | folded | 注入 killpg EPERM：a2f30b19 的 run_capture_command 讓 PermissionError 漏出；清理容忍 EPERM 後 `test_zombie_only_group_permission_error_is_not_fatal` 先紅後綠，變異 N1 紅 |
| MUT4-2 | 測試殺傷力 | minor | HIT | folded | 拿掉 model_command 的 cwd，三套照綠；補模型回報工作目錄的斷言，變異 N3 紅 |
| MUT4-3 | 測試殺傷力 | minor | HIT | folded | 第二逾時出口改回普通 ValueError，三套照綠；`test_timeout_after_streams_close_keeps_partial_output` 對變異 N4、N5 皆紅 |
| MUT4-4 | 測試殺傷力 | minor | HIT | folded | 中斷訊息改字，三套照綠；`test_cancelled_capture_stops_child` 補 receipt reason 斷言，變異 N6 紅 |
| MUT4-5 | 測試殺傷力 | minor | HIT | accepted | 從 repo 根以 python -m unittest 跑掃描測試 4 errors；專案入口一律以腳本形式執行（t_test_quality_scan_cli 跑 python scripts/test_test_quality_scan.py），鄰居 governance/eval/test_test_quality_handbook.py 也直接 import 同目錄模組、依賴 sys.path[0] |
| ARC4-1 | 架構對齊 | minor | HIT | accepted | 先例帶 noqa E402；repo 無 ruff 設定，全域規則對這行的 noqa 報 RUF100 未啟用，去掉 noqa 才與實際生效的規則一致 |
| ARC4-2 | 架構對齊 | minor | HIT | accepted | 例外名不帶 Error 後綴；沿用標準庫 subprocess.TimeoutExpired 的命名，改名要動三支產品檔與四篇筆記，收益只是命名 |
| ARC4-3 | 架構對齊 | minor | HIT | accepted | model_command 不轉換 CaptureInterrupted；它仍是 ValueError 子類，修前此處也是未接的 ValueError 往上傳，型別家族與傳播行為不變；全 repo 沒有比對 model interrupted 字串的呼叫端 |
| ARC4-4 | 架構對齊 | minor ⚠ | HIT | accepted | handbook 的 run_test 仍用 subprocess.run：它執行的是 handbook 自身 --child 模式，受測碼先過 AST 白名單、不允許建立程序，沒有需要清理的後代 |
| ARC4-5 | 架構對齊 | minor | HIT | accepted | corpus 外層 subprocess.run 50 秒：r3 實跑卡住的假 backend，scanner 在 40.2 秒由自身 backend 預算收掉、早於外層，背景子程序已清；屬既有、本輪未改 |

## 根因分組

- 甲（改走共用 runner 帶入的錯誤出口）：REG4-1、BND4-2、MUT4-1、BND4-1。
- 乙（控制沒守到的參數與出口）：MUT4-2、MUT4-3、MUT4-4。
- 丙（放行）：MUT4-5、ARC4-1 至 ARC4-5。

## 歸因

- 有證據的修復回歸：REG4-1/BND4-2/MUT4-1（修前自寫版無上限，修後拋錯）。
- 有證據的原有漏查：BND4-1（修前 runner 與 handbook 自寫版都只容忍 ProcessLookupError，300 次競態修前 21 次、修後 15 次）、MUT4-2、MUT4-4。
- MUT4-3：本輪新增的型別分類在第二逾時出口缺測，修前同一出口也無測試。
- MUT4-5：測試可攜性差異來自上一輪移除 sys.path 插入，屬上一輪修補帶出，已放行。
- regression_set：REG4-1、BND4-2、MUT4-1、MUT4-5。

## 未驗範圍

真 claude CLI、真 Semgrep 二進位、Windows、PGID 重用與 finally 首行後的 SIGTERM 時序窗口（四席與編排者都沒構造出可重現場景）。本輪折入的修補差異未再經全新席回歸審；迴圈已用掉人裁加開的一輪。
