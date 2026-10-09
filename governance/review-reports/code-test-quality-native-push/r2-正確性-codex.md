severity: major

F1 更新中斷後，舊 sidecar 只因檔名仍存在便通過前置檢查，會恢復 aggregate 假綠  
severity: major  
blocking: 是  
引句:「missing = [p for p in required if not (folder / p).is_file()]」  
file: `scripts/lumos:49225`  
file: `scripts/lumos:22144`  
file: `scripts/lumos:22440`  
file: `scripts/lumos:22561`  

具體失敗：vendor 依白名單逐檔覆寫，`scripts/lumos` 排在三個 `test_quality*.py` 前。已有舊版 sidecar 的消費專案若在複製新版 `lumos` 後中斷，三個舊檔仍存在，`_test_quality_deployment_ready` 便回傳成功，沒有核對版本或內容身分。

最小重現：組合凍結前版 `5d8f0ec7` 的三個 sidecar 與凍結 HEAD `598e41b2` 的 `scripts/lumos`，執行：

```sh
python3.14 scripts/lumos test-quality capture \
  --out ../mixed-evidence \
  --source scripts/lumos \
  --test-source scripts/test_quality.py \
  --language fixture \
  --framework control \
  --junit-stdout -- \
  python3.14 -c 'print("<testsuite tests=\"1\" failures=\"1\"><testcase name=\"x\"/></testsuite>")'
```

結果為 exit 0、`status: executed`、案例 `status: passed`，即 suite 宣告失敗卻收成綠證據。全 HEAD 對照同一命令為 exit 2，理由是 `suite summary inconsistent with testcase rows: failures`。另一個逐檔中斷點——新版 `lumos`、新版 `test_quality.py`、舊版 scanner——執行 `test-quality capabilities` 會直接以 `ImportError: cannot import name 'add_scan_arguments'` traceback 結束。

修補因果：F1 aggregate 問題在完整一致部署下已修好；正常 capture/check 與 scanner 行為亦由子集測試保留。這是既有非原子逐檔更新的「寫一半」角落，被本輪只驗存在性的 b1 修補漏掉，並非 aggregate 修法新造成的正常路徑退化。它違反 `Systems/lumos-cli-lifecycle` 所述「新的不完整命令要求 update」之修補目的。

完整一致部署下的 JUnit aggregate、root/suite 計數與正常控制：已讀,無 finding。  
capture/check 的 target 身分、案例集合、tests/context 快照、restore 與 refactor 分離：已讀,無 finding。  
舊有效 receipt 互讀、無效 aggregate 拒收、衍生狀態與不可覆寫輸出：已讀,無 finding。  
輸出上限、單調逾時、SIGTERM/process-group 清理：已讀,無 finding。  
deinit bytecode 白名單、使用者快取及 symlink 外側保留：已讀,無 finding。  
impact 對 eval 附件與實際程式的分類：已讀,無 finding。

已讀材料：`r2-runtime.patch` 全 1128 行、`r2-repair-binding.json`、`r1-fix.json`、`r1-intake.md`，並查證 `r1-evidence.patch` 原始 F1/b1；binding 的 repair patch SHA-256 與實檔相符。已讀 `/tmp/lumos-r2-manual-lens.txt` 前八篇固定席合約：vendored 測試假紅、lifecycle re-inject、deinit、CLI read、bound-tests、guard-kill、授權與歸屬、測試假綠形態；除 F1 對 lifecycle 不完整部署目的的影響外，其餘合約無 finding。另完整核對 `Systems/test-quality-cli`、`Systems/授權與歸屬`、`Systems/lumos-cli-lifecycle`。

驗證：`t_test_quality_cli` 1 passed、`t_test_quality_scan_cli` 1 passed；上述混版最小重現仍翻紅本輪。

總結：最嚴重 severity: major；blocking 條數: 1
