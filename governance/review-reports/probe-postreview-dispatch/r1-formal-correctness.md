severity: major

Finding F1：子程序「正常回傳但沒有結果檔」的事故只存在記憶中；下一次純合併會洗成成功。

severity: major  
blocking: 是  
引句:「先以單次原子取代釘住事故，再歸檔舊資料；歸檔中斷不能讓下次重跑吃回成功外觀。」  
file: `governance/eval/ablation_lumos_first.py:248`

`run_job` 只在 `subprocess.run` 拋出例外時寫 fatal tombstone。子程序回傳 rc1／rc3／被訊號終止且沒有產出檔案時，`unreadable` 分支只設定本進程的 `stop`；`_run_locked_batch` 產生的「本次派工」失效訊號沒有落成逐題檔。下一次 `--merge-only` 因目錄中沒有 fatal 檔而退出 0，與 `Systems/ablation-lumos-first` 所記「缺檔只停派仍不夠」相衝突。

最小重現：建立題目 `{"id":"a","prompt":"q","expect":["Bash"],"target":[["definitely/not-here.py"]]}`，真 CLI 首跑因腐爛 target 回 rc3、summary 有 poisoned；同一目錄再跑 `--merge-only`。實測結果：

```text
first_rc=3, first_poisoned=true
persisted_attempts=[]
second_rc=0, second_poisoned=false, second_missing=1
```

應翻紅斷言：`second_rc == 3 and second_poisoned`。

Finding F2：`--max-per-window` 沒有限制單一工作的 `--runs`，單路仍可任意超過窗口配額。

severity: major  
blocking: 是  
引句:「五小時窗口滿就留待下次補缺；本批只准單路派工，避免並行 TOCTOU 多開模型。」  
file: `governance/eval/ablation_lumos_first.py:188`

判斷只比較已完成場數是否達上限，沒有比較或裁切 `已完成 + n`。空目錄下使用 `--max-per-window 50 --runs 1000`，第一個工作會把 `--runs 1000` 原樣交給探針；單路只限制同時工作的數量，沒有守住「五小時內最多開幾場」。

最小重現：

```python
run_job("with", "a", 1000, [], 1, 1, outdir, 0, max_per_window=50)
assert int(captured_cmd[captured_cmd.index("--runs") + 1]) <= 50
```

實測 child `--runs` 為 `1000`，斷言翻紅。這也反駁附加表態中「單路保留配額語意」的宣稱。

Finding F3：鎖只由父 CLI 持有；父程序被終止後，仍在跑的探針子程序不再受互斥保護。

severity: major  
blocking: 是  
引句:「同一輸出目錄的另一個 CLI 可能已在跑模型；其 stop 旗標不會跨進程共享。」  
file: `governance/eval/ablation_lumos_first.py:424`

目錄鎖與舊鎖檔 fd 沒有傳給探針子程序。父 CLI 收到 SIGTERM／SIGKILL 後，核心會釋放兩把鎖，但 `scenario_probe.py` 或它啟動的模型程序可繼續執行；第二個 CLI 隨即取得鎖並啟動另一批，形成設計想消除的在途重疊。

最小重現：第一個批次取得鎖後啟動 30 秒子程序，向父批次送 SIGTERM；確認子程序仍存活，再以相同 out-dir 呼叫第二個 `main`。實測：

```text
first_parent_exit=-15
probe_still_alive=true
second_entered_batch=1
```

應翻紅斷言：`probe_still_alive implies second_entered_batch == 0`。

Finding F4：歸檔中斷測試沒有證明故障注入真的發生，刪除整段歸檔邏輯仍會全綠。

severity: major  
blocking: 是  
引句:「歸檔被中斷也須留下掃描得到的致命嘗試」  
file: `scripts/test_lumos.py:37994`

測試最後只驗 fatal tombstone 可掃描且 `needed == 1`；這兩項在歸檔前便已成立。測試沒有用旗標或 mock call count 斷言 `.failed` 路徑確實被呼叫，因此違反 `Systems/測試假綠形態` 的 ★INVARIANT★「前置斷言證明現場成立」。

最小重現：在記憶內建立刪除 `_atomic_write_bytes(out.with_suffix(".failed"), prior_result)` 的 mutant，再執行相同 oracle。實測：

```text
archive_step_removed=true
archive_interrupt_observed=false
current_test_oracle_still_passes=true
```

應新增會翻紅的前置斷言，例如 `archive_interrupt_observed is True`。

圖譜鏡頭逐條核對：

- `Systems/ablation-lumos-first`：已讀；F1、F2、F3 直接影響其失效判定、配額與互斥責任。
- `Verification/2026-10-04_探針停派與失敗留痕`：已讀；F1、F3、F4 收窄或推翻其部分 PASS 結論。
- `Systems/codex-harness`：已讀；F1 可由其腐爛 target 真入口觸發。
- `Systems/測試假綠形態`：已讀；F4 違反其硬合約。
- `Systems/lumos-cli-read`：已讀，無 finding。
- `Systems/canary-audit`：已讀，無 finding。
- `Systems/design-loop`：已讀，無 finding。
- `Systems/bound-tests-gate`：已讀，無 finding。
- `Systems/guard-kill`：已讀，無 finding。
- `Systems/lumos-cli-lifecycle`：已讀，無 finding。
- `Systems/slim-get-一行安裝`：不受本 patch 行為影響，已讀，無 finding。
- `Systems/slim-install-安裝器`：不受本 patch 行為影響，已讀，無 finding。
- `Systems/slim-uninstall-一行卸載`：不受本 patch 行為影響，已讀，無 finding。
- `Projects/規格落成可驗收條件_計劃`：不受本 patch 行為影響，已讀，無 finding。
- `Systems/lumos-deinit`：不受本 patch 行為影響，已讀，無 finding。
- `Projects/逃逸自動記_計劃`：不受本 patch 行為影響，已讀，無 finding。
- `Systems/節點範圍與索引守衛`：不受本 patch 行為影響，已讀，無 finding。
- `Systems/cochange-guard`：不受本 patch 行為影響，已讀，無 finding。
- `Systems/check-r-guard`：不受本 patch 行為影響，已讀，無 finding。

現有 `python3.14 scripts/test_lumos.py -k probe_boundary_postreview` 為 18 passed、0 failed；上述四條均位於其未覆蓋或假綠的路徑。

最嚴重 severity: major；blocking: 4 條
