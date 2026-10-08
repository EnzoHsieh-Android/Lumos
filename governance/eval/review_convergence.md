# 審查收斂 eval

把跑滿回顧當案例線索，把固定案例的成對試行當成效證據。工具只讀本機檔案、印 JSON，不執行模型、測試或檔案中的命令。

```sh
python3 governance/eval/review_convergence.py cohort docs/.canary-log.jsonl
python3 governance/eval/review_convergence.py template code-你的題目
python3 governance/eval/review_convergence.py compare manifest.json trials.jsonl --receipts receipts
```

`cohort` 收集帳上所有 code 迴圈，包括沒有滿輪人裁的迴圈。這是觀察到的編號數；同一任務換編號、遺失的帳本、沒有記帳的審查都會影響分母。回顧分類與狀態仍用 `lumos loop retro-stats` 查；分類不證明修補因果。輪次混用、成本缺件及 token 衝突均保留未知。

`template` 所有待核對值留 null。請人工確認同根因案例的 group，使用 `split_for(group)` 決定 train/held；同一 group 不跨集合。雜湊分組不能證明模型沒看過題目。

manifest 格式：version=1、cases 非空陣列、repeats=1..20、arms 含 baseline/candidate。每個 case 需要 id/group/split/loop/finding/start_commit（完整40位commit）、case_sha256/grader_sha256/environment_sha256（64位 SHA）。每個 arm 需要相同的固定 model，以及各自 workflow_sha256/dispatch_sha256。先凍結 manifest 再跑試行；最多100題，字串識別欄位最多128字元。

每行 trial 索引需要 case_id/arm/repeat，以及 receipt={path,sha256}。path 是 receipts 目錄內相對路徑，不接受連結或跳出目錄；不套用識別欄位的128字元上限，檔案系統限制另由讀檔結果判定。原始 receipt JSON 需要相同 case_id/arm/repeat、案例四個指紋欄位、arm 三個設定欄位，另附：

- status：completed；cancelled/失敗的工具執行不當產品失敗。
- result_commit/loaded_start_commit/loaded_result_commit：完整版本，記錄真正載入的來源。
- repair/preserve：布林；new_defects：非負整數（最多一百萬）。實際驗收不通過仍是有效負例；沒驗不能填 false 或零。
- rounds：1到一百萬的整數；tokens/wall_seconds：0到10的15次方的有限值，缺資料填 null。

判準應對原問題跑 fail-to-pass，對既有行為跑 pass-to-pass；保留命令、環境、退出碼與原始輸出。此入口核對 receipt 宣告與 SHA，**沒有重新執行驗收，也不證明宣告是真的**。判準指紋需包含如何界定新增缺陷；沒有該檢查就應填未知。真實輸出及人工標註另外留存，成本單位要一致。

`compare` 拒絕同 slot 重複，不取最好一次。expected_trials 是預先排定分母；missing_slots 是完全沒送件，invalid_records 是送件但不能判讀。valid_trials 包括產品負例。quality_delta 只比較同題同 repeat 兩側有效的場次；round_delta_on_joint_success 僅比較雙方品質通過的子集，可能有選擇偏差，必須先看成對品質、缺場及無效資料。排定slot缺場、重複、無效或成本缺一筆就不報該組均值，另列已知筆數；train/held 分開列。

最小反例驗證：`python3 governance/eval/test_review_convergence.py`。這些是合成工具測試，不能當模型效果測量。manifest上限1MiB、receipt JSON上限256KiB、帳與trial索引16MiB且最多十萬筆；逐行解析避免短行一次展開。這是輸入約束，不是程序RAM上限；無法解析、重複 JSON key 或非有限值直接回錯。工具不是惡意程序隔離邊界，操作時應用固定的可信本機檔案。
