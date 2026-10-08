severity: major

審材驗證：已逐行讀完 538 行凍結 patch；SHA256 為 `02c08f6f714de48446e232a8da34169ce096c71ddef3901dbe28914ad6cf4563`，與派工一致。對照真碼並執行 `probe_boundary_postreview` 子集，結果 18 passed、0 failed；下列反例未被該子集覆蓋。

finding 1：異常退出碼只留在本輪記憶，下一次純合併會接納該失敗程序留下的成功外觀資料。

severity: major  
blocking: 是  
引句:「先以單次原子取代釘住事故，再歸檔舊資料；歸檔中斷不能讓下次重跑吃回成功外觀。」  
file: `governance/eval/ablation_lumos_first.py:248`  
具體失敗場景：探針寫出 schema 合法、含成功列的 JSON，隨後以 rc2 退出。`run_job` 只設記憶中的 `stop`，沒有把該檔改成 fatal；本輪 summary 因 `live_failed` 回 3，但下一次 `--merge-only` 看不到退出碼，將該列計入統計並回 0。  
最小重現：stub 依 `--out` 寫入 `fatal=false/inconclusive=false/skills_health_bad=[]` 與一筆 `passed=true`，回傳 `returncode=2`；第一次 `main()` 得 `rc=3, poisoned=true`，同目錄再跑 `--merge-only`，實測得到 `rc=0, poisoned=false, with.n=1, needed=0`。這可由 `t_probe_boundary_postreview_nonzero_result_persists` 直接翻紅。

finding 2：結果 schema 只驗「每列是 dict」，錯型純量可被靜默當成成功，另一些錯型會令純合併崩潰。

severity: major  
blocking: 是  
引句:「if (not isinstance(rows, list) or not all(isinstance(x, dict) for x in rows)」  
file: `governance/eval/ablation_lumos_first.py:238`  
具體失敗場景：舊檔或損毀檔把 `passed` 寫成字串 `"false"`。健康掃描回空，Python 又把非空字串視為真，摘要遂得到 `m1_passed=1, m1_rate=1.0` 並抵掉缺場。若 `id` 是 list，健康掃描同樣回空，但 `merge()` 在集合成員檢查拋 `TypeError`，可能留下新版 meta 配舊 summary。題庫的非字串 qid 也未在 `load_ids` 邊界拒絕，會在 `qid.encode()` 才崩。  
最小重現：在空目錄放入：
```json
{"arm":"with","results":[{"id":"a","passed":"false","reason":"ok","limit_hit":false}],"fatal":false,"inconclusive":false,"skills_health_bad":[]}
```
呼叫 `collect_skills_health(dir)` 與 `merge(dir, ["a"], 1)`；實測為 `poisoned=[]、n=1、m1_passed=1、m1_rate=1.0、needed=0`。把 `id` 改成 `[]` 則實測 `TypeError: cannot use 'list' as a set element`。

finding 3：`--arms` 未限制合法集合或去重，會重複派模型，亦可把 log 寫出輸出目錄。

severity: major  
blocking: 是  
引句:「for arm in a.arms.split(","):」  
file: `governance/eval/ablation_lumos_first.py:364`  
具體失敗場景：`--arms with,with --runs 1` 建 jobs 時兩份工作都依同一份舊 `by_arm` 算出缺 1 場，故同題派兩次；結果會有兩場並被 `_arm_stats` 全數計入，既多花模型配額也改變組別權重。另因 arm 直接進檔名，`--arms ../escaped` 會先在 `out_dir` 外建立 log，300 字元 arm 則在寫 log 時以 `ENAMETOOLONG` 崩潰。  
最小重現：以計數 stub 取代 `run_job`，設定 `argv=[..., "--runs","1","--arms","with,with"]` 後呼叫 `main()`；實測 `rc=0` 且 jobs 為 `[("with","a",1), ("with","a",1)]`。另直接呼叫 `run_job("../escaped", "a", ...)`，實測在 `out_dir` 的父目錄產生 `escaped-q-*.log`。

finding 4：互斥鎖只由 runner 持有；runner 被單獨終止後，仍活著的探針不再持鎖，第二批可以同時派工。

severity: major  
blocking: 是  
引句:「同一輸出目錄的另一個 CLI 可能已在跑模型；其 stop 旗標不會跨進程共享。」  
file: `governance/eval/ablation_lumos_first.py:425`  
具體失敗場景：runner A 已啟動 `scenario_probe`，服務管理器只對 A 送 SIGTERM。鎖 fd 預設不傳給子程序，A 結束即釋鎖，但 probe A 繼續執行且尚未寫結果。runner B 隨即取得鎖，因磁碟仍顯示缺場而再派同題；兩個探針最後都落有效檔，`--runs 1` 的摘要卻計入兩場。這反駁 `py-parallel satisfied` 的證據完整性：既有測試只證正常存活的父程序互斥。  
最小重現：以會先寫 marker、sleep 2 秒、再寫有效 JSON 的 stub 作 `PROBE`；啟動 A，見 marker 後只 SIGTERM A，再啟動 B。實測 `A rc=-15、B rc=0、probe starts=2、result files=2、summary with.n=2`。

finding 5：歸檔中斷測試未證明中斷點真的被執行，違反固定席的「現場成立前置斷言」合約。

severity: major  
blocking: 是  
引句:「舊碼會在 Path.replace 原結果時中斷。兩版都在歸檔處故障。」  
file: `scripts/test_lumos.py:37992`  
具體失敗場景：測試吞掉可有可無的 `KeyboardInterrupt`，最後只驗 fatal tombstone；若把整段 `.failed` 歸檔動作刪掉，既不會發生中斷，也不會保存舊內容，但 tombstone 仍使最後兩項斷言全綠。這正中 `Systems/測試假綠形態` 的第④型，測試名稱宣稱的歸檔故障現場沒有被前置斷言釘住。  
最小重現：在記憶中把 `if prior_result is not None:` 下的歸檔區塊替換成 `pass`，執行同一 fixture。實測 `interrupt_observed=false、failed archive files=[]`，但現有測試 oracle 仍為 `true`。至少需斷言故障 hook 確實被呼叫，再驗 fatal 仍可掃到。

finding 6：fatal 原子寫入本身遇到 ENOSPC 時，成功外觀的舊結果仍留在原位。

severity: minor  
blocking: 否  
引句:「_atomic_write_text(out, json.dumps(tombstone, ensure_ascii=False))」  
file: `governance/eval/ablation_lumos_first.py:221`  
具體失敗場景：探針先留下合法結果，再走 `TimeoutExpired` 分支；若建立或寫入 tombstone 暫存檔時磁碟滿，`OSError(ENOSPC)` 直接冒出，`stop` 尚未設定，原 JSON 仍是可採信外觀。實測故障注入得到 `errno=28、poison=[]、accepted=1、needed=0`。目前外層尚未設定 timeout，因此主要是已預留 timeout 分支與未來加 timeout 時的缺口；一般啟動 `OSError` 未產生舊結果時不會誤算，故列 minor。

固定席圖譜逐條判：

- `Systems/codex-harness`：已讀,無 finding。
- `Systems/測試假綠形態`：finding 5 違反 ★INVARIANT★。
- `Systems/lumos-cli-read`：已讀,無 finding。
- `Systems/canary-audit`：已讀,無 finding。
- `Systems/design-loop`：已讀,無 finding。
- `Systems/bound-tests-gate`：已讀,無 finding。
- `Systems/guard-kill`：已讀,無 finding。
- `Systems/lumos-cli-lifecycle`：已讀,無 finding。
- `Systems/slim-get-一行安裝`：已讀,無 finding。
- `Systems/slim-install-安裝器`：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載`：已讀,無 finding。
- `Projects/規格落成可驗收條件_計劃`：已讀,無 finding。
- `Systems/lumos-deinit`：已讀,無 finding。
- `Projects/逃逸自動記_計劃`：已讀,無 finding。
- `Systems/節點範圍與索引守衛`：已讀,無 finding。
- `Systems/cochange-guard`：已讀,無 finding。
- `Systems/check-r-guard`：已讀,無 finding。
- `Systems/ablation-lumos-first`：findings 1–4、6 與其失敗拒收、結果有效性、互斥及原子落檔邊界直接相關。

表態判讀：`py-eventloop na` 成立；`py-parallel satisfied` 的同一父程序串行部分成立，但其測試不足以證明父程序異常退出後仍維持單路，finding 4 已實測反例。

總結：最嚴重 severity major；blocking 5 條。
