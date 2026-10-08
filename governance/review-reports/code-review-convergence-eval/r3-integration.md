severity: clean

本席未發現可重現、可歸因於本輪修補的具體 bug；阻擋數 0。

已驗行為 CLEAN-01：129 字合法 receipt 路徑由 fail 轉 pass。

引句:「判準應對原問題跑 fail-to-pass，對既有行為跑 pass-to-pass；保留命令、環境、退出碼與原始輸出。」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:179`

- input：建立長度 129、且確實存在的 receipt 檔名。
- expected 出處：測試先斷言 `len(name) == 129`、`is_file()`，再要求 `valid_trials == 1`、`invalid_records == []`。file: `governance/eval/test_review_convergence.py:285`
- case_source：`cd0ae310ccf1609a56a2552374eab47b13c55882:governance/eval/test_review_convergence.py`；SHA-256 `03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`。
- 修前 command：`/opt/homebrew/opt/python@3.14/bin/python3.14 -c <r3-paired-cases.json 內完整 paired runner> <after/review_convergence.py> <fixed_r2/test_review_convergence.py>`。
- 修前 cwd：`…/review-eval-source-restore-d0_i6ykl/after`；載入 module SHA-256 `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`；Darwin、Python 3.14.6、network none、executed=true；rc=1。
- 修前原始輸出：該案 `FAIL`，整體 `FAILED (failures=4)`。file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:54`
- 修後 command：同一 runner／同一 case source，module 改為 `fixed_r2/review_convergence.py`。
- 修後 cwd：`…/review-eval-source-restore-d0_i6ykl/fixed_r2`；載入 module SHA-256 `4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`；相同環境、executed=true；rc=0。
- 修後原始輸出：該案 `ok`，23 案全部 `OK`。file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:24`
- 可比／歸因界線：同一測試來源、輸入與環境，可判此症狀已修好；直接修補與逐行解析配套沒有獨立中間版本，不能再細分至單一修改行。

已驗行為 CLEAN-02：原正常品質判準保留。

引句:「輪數差只算雙方品質通過的場次，成本有完整資料才给均值，另列覆蓋數與split分層。」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:42`

- input：兩個 repeat；baseline `rounds=3`，candidate `rounds=1` 但 `preserve=false`。
- expected 出處：`paired_trials=2`、candidate 品質通過數 0、`quality_delta=-1.0`、共同成功輪數差為 `None`。file: `governance/eval/test_review_convergence.py:379`
- case_source、commands、cwd、載入 SHA、環境與前案相同。
- 修前原始輸出：`test_faster_but_regressed_is_not_improvement ... ok`，但整體 rc=1 來自其他四案。file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:14`
- 修後原始輸出：同案 `ok`，整體 rc=0。file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:14`
- 可比／歸因界線：這是 pass-to-pass 保留證據；總 rc 不代替單案結果。

修補三問：

- 原問題是否修好：指定 23 案中的四個原失敗均轉綠；129 字路徑案有現場成立前置斷言。
- 原正常案例是否保留：抽查的「更快但破壞 preserve 不算改善」案例兩端均通過。
- 新問題能否歸因修補：本席未找到；這只表示指定案例家族與已讀範圍未見回歸，不保證全域無回歸。

graph lens 硬合約逐條答：

1. 測試假綠／現場成立：129 字路徑案符合；其他三個 cohort 修補案未逐案重讀前置斷言。
2. bound-tests 紅、懸空、偽證據、不可過閘：本席未執行 `code-loop check`，未驗。
3. canary record 落盤可讀回：未改其實作，未驗。
4. canary second 不影響 gate：未改其實作，未驗。
5. guard-kill rc 優先序：未改其實作，未驗。
6. guard-kill JSON 純度：未改其實作，未驗。
7. 三支 PowerShell ASCII-only／無 BOM：Windows 原生能力排除，未驗。
8. PowerShell 不使用 `$Args`：Windows 原生能力排除，未驗。
9–15. slim-install 的內容保留、冪等、備份、manifest、目標守衛、直譯器與 shim 碰撞七條：未改相關 runtime，未驗。
16–21. slim-uninstall 的獨立清理、skill 備份、精確還原、shim 獨立移除、manifest 清理等六條：未改相關 runtime，未驗。
22. search 排除 superseded、不排 stale：未改讀取入口，未驗。

其他界線：

- `py-memory` 維持 `tension`、`chosen=suggested`；16 MiB／十萬筆是輸入上限，不是總 RAM 保證。未量測峰值記憶體，依計劃於 2026-10-21 回看。
- 唯讀實體 fixture 的修前、修後 `compare` 均 rc=0，結果均為 4/4 valid、2 paired、無缺場、無重複、無 invalid；這只證正常 fixture 保留，不是模型實輪。
- receipt 一致性不是獨立重執行證據；metadata 為合成工具資料。
- Windows 原生相容性未驗，不宣稱通過。
- 單家族視角不保證無回歸。
- 未全文讀：r1/r2 席報告與 intake、完整 167 行 repair patch、完整 1281 行 snapshot、超出 graph lens 上限的節點、其他席材料。
- 審材實讀約 1,080 行；另有定向索引、binding 摘要與實際命令輸出。最高等級 clean；阻擋條數 0。