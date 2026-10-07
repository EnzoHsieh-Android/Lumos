severity: minor

F1：C1 終端控制字元仍可穿過 JSON 輸出

severity: minor  
blocking: 否  
引句:「rendered = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)」  
file: `governance/eval/review_convergence.py:99`

`render_json()` 只跳脫列舉的 Unicode 字元，仍原樣輸出 U+009B（CSI）與 U+009C（ST）。若 ledger 的 `loop` 由攻擊者控制，在會解讀 C1 控制碼的終端或日誌檢視器中，可清畫面或偽造顯示內容。

利用範圍限於輸出顯示完整性；沒有證據顯示可執行命令、讀取額外檔案或提升權限，因此列 minor、不阻擋。

修補三問：

- 原問題：U+202E/U+2028 的固定案例已修好，但「輸出控制字元」同族問題未完整修好。
- 舊路徑：`../outside.json` 的拒絕仍成立。
- 修補歸因：U+009B/U+009C 在 before、after 都存在，不列為 fix-induced；它是修後仍殘留的問題。

證據共同前提：

- before：`8950308b71969f95119c7b2780f7a9ef93f669ac`，實載 module SHA-256 `6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- after：`c909bf980125dc90f1696372205e322e2ac877c7`，實載 module SHA-256 `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- 固定案例來源：`governance/eval/test_review_convergence.py`，SHA-256 `6af875e4b41aa01e368e35aa0b1f09104db31cdaf1655b7b10f90609a13a029b`
- cwd：`/private/tmp/lumos-future-repair-regression-research`
- 命令：`git show <commit>:governance/eval/review_convergence.py | python3.14 -c <inline NUL、../、C1 probe>`
- 兩端 probe 均 executed=true、rc=0；probe 會捕捉案例例外，因此案例結果另列，不能用總 rc 代替。
- 輸入：`{"loop":"code-\u009b2Jspoof\u009c"}`；預期：stdout 字串內不含原始 C1 控制字元。
- before 實際：`u009b=true, u009c=true`
- after 實際：`u009b=true, u009c=true`
- 原始診斷：`{"loop": "code-\\x9b2Jspoof\\x9c"}`

已驗證修好與保留案例：

1. NUL receipt path

   - case_source：`TrialTests.test_nul_path_is_an_invalid_record_not_a_batch_crash`，位於 `governance/eval/test_review_convergence.py:313`
   - 輸入：`receipt.path="bad\0name"`
   - 預期：整批不崩潰，該筆列為 `receipt-path`
   - 固定 paired harness：before executed=true、rc=1，原始輸出為該測試 `ERROR`；after executed=true、rc=0，原始輸出為 `... ok`
   - 獨立 probe：before 為 `ValueError: open: embedded null character in path`；after 為 `[{"record":0,"reason":"receipt-path"}]`
   - 結論：此原問題已修好。

2. 父目錄跳脫拒絕

   - case_source：`TrialTests.test_paths_outside_root_and_duplicate_trial`，位於 `governance/eval/test_review_convergence.py:301`
   - 輸入：`receipt.path="../outside.json"`
   - 預期：`DataError:receipt-path`
   - paired 原始輸出：before、after 該案例皆 `... ok`
   - 獨立 probe：兩端皆 `DataError:receipt-path`
   - 結論：既有正常安全路徑仍成立；不以整體 before rc=1 誤判此案例失敗。

逐類資安結論：

- 注入／路徑：有 F1；NUL 與 `../` 路徑防護案例通過 after。
- 權限：未驗出新增的跨權限操作；工具以目前使用者權限唯讀開檔。
- 秘密／個資：未驗出完整 receipt 回顯；比較資料只投影固定結果欄位。
- 加密：SHA-256 用於一致性核對，不是簽章或獨立執行證明；文件已明示此界線。
- 執行：產品入口沒有執行 manifest、receipt 或外部命令的路徑。
- 行動端：不適用；Windows 原生驗證依指示排除。
- 依賴：新增產品模組僅使用 Python 標準函式庫，未新增第三方供應鏈面。

圖譜硬合約逐條答覆：

1. 測試假綠形態：NUL／控制字元案例確實在 before 翻紅、after 轉綠；路徑保留案例兩端皆綠。鏡頭標示綁定測試「有」。
2. bound-tests gate：未改其判定或 rc；綁定「有」，本席未重跑整套。
3. canary 落盤可讀回：未改相關實作；綁定「有」。
4. second telemetry 不影響 gate：未改相關實作；綁定「有」。
5. guard-kill rc 優先序：未改相關實作；綁定「有」。
6. guard-kill JSON 純度：未改相關實作；綁定「有」。
7. PowerShell ASCII／BOM：未改；綁定「有」，Windows 實機排除。
8. PowerShell `$Args`：未改；綁定「有」，Windows 實機排除。
9. installer 注入位置：未改；綁定「有」。
10. installer 冪等：未改；綁定「有」。
11. 完整版區塊備份：未改；綁定「有」。
12. installer manifest：未改；綁定「有」。
13. installer 目標守衛：未改；綁定「有」。
14. `.cmd` 直譯器選擇：未改；綁定「有」，Windows 實機排除。
15. Windows shim 碰撞：未改；綁定「有」，Windows 實機排除。
16. uninstall bin 身分比對：未改；綁定「有」。
17. 四個清理步驟獨立：未改；綁定「有」。
18. skill 目錄先備份：未改；綁定「有」。
19. sentinel 位元組還原：未改；綁定「有」。
20. `.cmd` 獨立移除：未改；綁定「有」，Windows 實機排除。
21. manifest 清理：未改；綁定「有」。
22. search 保留 stale：未改；綁定「有」。

實讀範圍：

- 使用者提供的 AGENTS／席位 prompt
- `CLAUDE.md`：101 行
- `r2-snapshot.patch`：1235 行，完整
- `security-repair.txt`：123 行，完整
- `r2-graph-lens.txt`：69 行，完整
- 精準擷取：`r2-paired-cases.json`、`r2-source-restore.json`、兩端 paired logs、after 模組行號
- 未讀：所有 r1 席報告、intake、純歷史卷證與無關測試 log

未驗範圍：

- 未在真實終端逐款確認 UTF-8 C1 的呈現；已證明原始控制碼確實進入 stdout，實際視覺效果依消費端而定。
- 沙箱拒絕建立指定暫存目錄，因此沒有重跑落盤版 unittest；改以固定 commit 的無落盤等價 probe 核對，並對照既有原始 paired output。
- 未跑完整 bound-tests 或 Windows 原生案例。
- 單家族資安鏡頭不保證沒有其他回歸。

最高等級：minor  
阻擋條數：0