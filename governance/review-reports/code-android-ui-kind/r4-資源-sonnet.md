severity: minor

資源鏡頭的結論:這輪修補在分析工具不存在(`OSError`)、被 Ctrl-C 兩條路徑上有效。我在 `ab35a0f8` 上實跑,測試約 0.7 秒,只多 3 次 `sh` 子程序,沒有成本問題。查詢本體這輪沒改,沒有新增退化。沒有 blocking 項目。以下兩條是仍存的缺口,兩條都是修補前就有、修補沒碰到。

## 1. 分析工具沒有逾時,卡住就永遠卡住
severity: minor
blocking: 否
引句:「r = subprocess.run([tp, trace, '-q', f.name], capture_output=True, text=True, errors='replace')」
file: `scripts/templates/android-receipt-rerun.sh:58`
歸因:有證據的原有漏查
失敗場景:`trace_processor` 讀到壞掉或超大的 Trace 而卡住。`subprocess.run` 沒帶 `timeout`,重跑腳本會一直等,暫存查詢檔也一直留著。`capture_output` 還會把整份 stdout 收進記憶體。我用 `TP` 指到一支 `sleep 300` 的假工具,腳本就等了整整 300 秒,沒有任何逾時出口。
查證:
- 修前 `e3ea2c16`:同一行同樣沒有 `timeout`,結果相同。
- 修後 `ab35a0f8`:同上,沒改善。
- 最小重現:`TP=<睡 300 秒的腳本> sh rerun.sh`。

## 2. 腳本收到 SIGTERM(CI 逾時、`kill`)時,暫存檔與子程序都留下
severity: minor
blocking: 否
引句:「finally:        os.unlink(f.name)」(原檔此處為換行縮排,內容同)
file: `scripts/templates/android-receipt-rerun.sh:62`
歸因:有證據的原有漏查
失敗場景:`try/finally` 只接得住 `KeyboardInterrupt` 和例外,接不住 SIGTERM。Python 收到 SIGTERM 會直接死掉,`finally` 不會跑。
- 我實跑:用 `start_new_session` 起腳本,對它的 process group 送 SIGINT,暫存 `.sql` 被刪、`sleep 300` 子程序被收掉,修補對 Ctrl-C 有效。
- 改對腳本 pid 送 SIGTERM:`tmp*.sql` 留在 `TMPDIR`,`sleep 300` 變孤兒繼續跑。
- 影響:CI 逾時殺掉重跑腳本時,會留下一個小暫存檔和一個仍在讀 Trace 的 trace_processor。
- 其他小點:`NamedTemporaryFile(...)` 在 `try` 之外,`f.write` 若失敗(例如磁碟滿),檔案也會留下。這種情況很少見,不另列一條。

查證:
- 修前 `e3ea2c16`:`os.unlink` 不在 `finally` 內,Ctrl-C 與 SIGTERM 兩種都會留檔。
- 修後 `ab35a0f8`:Ctrl-C 已修好,SIGTERM 仍會留檔。

## 三問
- 修補有沒有把分析工具逾時、Ctrl-C、例外時的暫存檔與子程序收乾淨?
  - Ctrl-C:有,暫存檔刪掉,子程序被 `subprocess.run` 殺掉。
  - 分析工具不存在或不能執行(`OSError`):有,回 2 且不留暫存檔,測試也釘住了。
  - 逾時:沒有逾時機制(第 1 條)。
  - SIGTERM:沒收乾淨(第 2 條)。
- 測試新增的子程序次數與整體時間有沒有問題?沒有。相關 54 項測試共約 2.2 秒,`receipt_rerun` 約 0.7 秒。
- 查詢在大資料量的成本有沒有退化?沒有。這輪沒動查詢,重跑腳本的解析是單趟線性,沒有二次方的工作。

總結:最高嚴重度 minor
