severity: major

severity: major  
blocking: 是  
引句:「先確保同一消融批次內事故後沒有第二個由本批次啟動的模型在途」  
finding: 單路限制只約束單一 Python 進程；`threading.Event` 不跨進程，`out_dir` 也沒有互斥鎖。兩個 CLI 同時指向同一批次目錄時，各自仍會啟動模型；其中一批設 stop，另一批不會看到。Python 官方文件也只保證單一 executor 內的取消行為，不能形成跨進程停止協定。[Python concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)  
file: `governance/eval/ablation_lumos_first.py:313`  
file: `governance/eval/ablation_lumos_first.py:338`  
file: `scripts/test_lumos.py:37693`  
最小重現: 以兩個 OS 進程、相同 `--out-dir`、各自 `--workers 1` 啟動 `main()`，把 `run_job` 換成 barrier stub；實測兩進程 `exitcodes=[0,0]`，`peak_run_job_processes=2`。需加入批次目錄或全域探針互斥鎖，並用雙進程故障注入證明事故後另一進程不會繼續派工。

severity: major  
blocking: 是  
引句:「缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕，預設僅開一路」  
finding: S9 的測試只覆蓋明寫 `--workers 1` 與 `--workers 2`，沒有驗證省略參數時的預設值；目前預設仍是 2。實作者若只加入 `>1` 拒絕而漏改預設，兩項既有測試都可通過，但正常不帶參數的命令會直接被拒絕。`0` 和負數也未被驗證，可能落入 executor 例外或產生與旗標不符的行為。  
file: `governance/eval/ablation_lumos_first.py:299`  
file: `scripts/test_lumos.py:37703`  
file: `scripts/test_lumos.py:37718`  
最小重現: 省略 `--workers` 執行 `main()` 後讀 `meta.json`，目前 `workers` 為 2；新增測試應同時要求省略值為 1，並拒絕 `-1`、`0`、`2`。

S8 子程序啟動例外與失效 summary：已讀，無 finding。  
S9 單一進程內的逐工作停止測試：除上述缺口外，已讀，無 finding。

總結: 最嚴重 severity major，blocking 2 條。
