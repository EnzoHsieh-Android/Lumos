severity: clean

clean-id: SEC-R3-01
severity: clean
blocking: 否
結論: 修前 stdout 會原樣帶出 C1 控制字元；修後改為 JSON 跳脫，解碼後資料不變。
引句:「self.assertNotIn(chr(point), result.stdout)」
file: `governance/eval/test_review_convergence.py:207`

input: `/tmp/review-eval-r3-seats/fixtures/controls.jsonl`
input_sha256: `1c4d69aad3868dff15da24b3a9e7229e9ce7622e62e98dba3a881d0bf4c35428`
expected出處: raw DEL/C1、U+202E、U+2028 不得出現在 stdout；JSON round-trip 必須還原原值。
case_source: `governance/eval/test_review_convergence.py:193`
case_source_sha256: `03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`
前提: Darwin、Python 3.14.6、network=none、同一唯讀 fixture。

before:
command: `/opt/homebrew/opt/python@3.14/bin/python3.14 /var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/after/governance/eval/review_convergence.py cohort /tmp/review-eval-r3-seats/fixtures/controls.jsonl`
cwd: `/private/tmp/lumos-future-repair-regression-research`
loaded_sha256: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
executed: true
rc: 0
原始stdout repr關鍵片段: `"loop": "code-\x9b\\u2028"`
獨立固定測試原始輸出: `AssertionError: '\x7f' unexpectedly found`
file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:27`

after:
command: `/opt/homebrew/opt/python@3.14/bin/python3.14 /var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/fixed_r2/governance/eval/review_convergence.py cohort /tmp/review-eval-r3-seats/fixtures/controls.jsonl`
cwd: `/private/tmp/lumos-future-repair-regression-research`
loaded_sha256: `4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
executed: true
rc: 0
原始stdout repr關鍵片段: `"loop": "code-\\u009b\\u2028"`
固定測試原始輸出: `test_render_control_characters_without_changing_data ... ok`
file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:10`

可比界線: 兩端使用同一 fixture、case source、Python及 cwd，只替換載入模組。修補將單一 U+0085 擴為 U+007F–U+009F；輸出差異可直接對到該 hunk。
file: `governance/eval/review_convergence.py:98`
歸因界線: parse-jsonl等配套與直接修補同提交，沒有獨立中間版本；但單筆 controls 案例不會觸發十萬筆上限，未見配套可造成此跳脫差異。

clean-id: SEC-R3-02
severity: clean
blocking: 否
結論: 修補沒有放寬既有的 `..` 路徑逃逸或 NUL 路徑拒絕。
引句:「path 是 receipts 目錄內相對路徑，不接受連結或跳出目錄」
file: `governance/eval/review_convergence.md:17`

input:
- `receipt.path="../outside.json"`
- `receipt.path="bad\0name"`

expected出處:
- `..` 回傳 receipt 路徑錯誤，重複 slot 不得變成有效 trial。
- NUL 路徑列為 `receipt-path`，不得令整批崩潰。
case_source: `governance/eval/test_review_convergence.py:340`
case_source_sha256: `03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`

兩端實際 command、cwd及環境逐字 argv:
file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:4`
file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:26`

before:
loaded_sha256: `f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
executed: true
suite_rc: 1
單案原始輸出: `test_paths_outside_root_and_duplicate_trial ... ok`
單案原始輸出: `test_nul_path_is_an_invalid_record_not_a_batch_crash ... ok`
file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:21`

after:
loaded_sha256: `4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
executed: true
suite_rc: 0
單案原始輸出: `test_paths_outside_root_and_duplicate_trial ... ok`
單案原始輸出: `test_nul_path_is_an_invalid_record_not_a_batch_crash ... ok`
file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:21`

可比界線: before總rc=1來自四個修補目標案例，不能代替本案判定；上述兩個安全邊界各自有兩端 `ok`。
歸因界線: 修補只移除 receipt path 的128字識別欄位上限；NUL、anchor、`..`及逐段 symlink 檢查仍保留。
file: `governance/eval/review_convergence.py:568`

修補三問:
1. 原問題是否修好: 是。C1終端控制字元已轉義，且解碼資料保持相同。
2. 原正常案例是否保留: 本席定向核對的路徑逃逸及NUL案例兩端皆通過；其餘固定23案中，修前已通過的19案在修後仍通過。
3. 新增問題可否歸因修補: 本席未重現可利用的新資安洞。這只涵蓋控制字元與路徑家族，不代表全域無回歸。

來源閉包:
- 修前commit: `c909bf980125dc90f1696372205e322e2ac877c7`
- 修後commit: `cd0ae310ccf1609a56a2552374eab47b13c55882`
- 修後tree: `e588725a66a969f9f019c70d5d36312c2e833894`
- bundle從無alternates物件庫實際fetch，restored commit與tree吻合，rc=0。
file: `governance/review-reports/code-review-convergence-eval/r3-repair-binding.json:2`
file: `governance/review-reports/code-review-convergence-eval/r3-source-restore.json:5`
- 固定正文SHA與實際載入SHA一致：module `4b8a83…`、tests `03ebe1…`。

graph lens硬合約逐條回答:
- 測試假綠形態: controls案例有真實修前翻紅、修後轉綠及JSON round-trip；現場分支已證明執行。
- bound-tests-gate: 本席未執行 `code-loop check`，不宣稱該閘通過。
- canary-audit兩條: persist/readback與second telemetry皆無相關實作hunk；未重驗。
- guard-kill兩條: rc優先序與JSON purity皆無相關實作hunk；未重驗。
- slim-get兩條: PowerShell ASCII/BOM及保留名規則未觸及；Windows原生驗證排除。
- slim-install七條: sentinel保留、冪等、完整備份、manifest、目標守衛、直譯器、shim碰撞均未觸及；未重驗。
- slim-uninstall六條: bin比對、四步獨立、skill備份、精確還原、shim獨立、manifest清理均未觸及；未重驗。
- lumos-cli-read一條: stale/superseded搜尋語意未觸及；未重驗。
- py-memory: 維持 `tension / chosen=suggested`；十六MiB、十萬筆及receipt上限只是輸入限制，不是總RAM保證。純資源耗盡不提升為資安阻擋。
- 回看日期: `2026-10-21`，需核對實輪資料量、記憶體及receipt完整性。
- py-eventloop、py-parallel、py-external: 同步離線入口，未發現反證。
- py-hotpath: 只採信固定測試結果，不外推大規模效能。

未驗範圍:
- Windows原生路徑與終端行為能力不可得，明確skip。
- 未做惡意本機程序並行替換中間目錄的競態實驗；文件已明示此工具不是惡意程序隔離邊界。
- 未做模型真實試輪、全RAM峰值或十萬筆壓測。
- 單家族視角不能保證無回歸。
- repo原先已有編排材料及治理帳變更；本席唯讀，未寫入。
- 一次 repair關鍵字搜尋誤命中內嵌archive且被工具截斷；其中舊席／intake文字已隔離，不用於任何判定或引句。若程序要求零暴露，應重派全新席。

最高等級: clean
阻擋條數: 0
有效採信實讀: 1790行，包括完整snapshot 1281行、AGENTS/CLAUDE/skills/graph lens及77行module-only repair delta。
嚴格全工具輸出計帳: 因上述archive誤命中而超過1800行；這是本席流程偏差。