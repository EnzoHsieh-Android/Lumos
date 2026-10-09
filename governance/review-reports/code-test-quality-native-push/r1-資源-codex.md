severity: major

finding ID:r1  
severity: major  
blocking: 是  
引句:「proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)」  
file: `scripts/test_quality.py:155`  
`capture` 收到 SIGTERM／Ctrl-C 時沒有 `finally` 終止新 session；父程序退出後測試程序繼續執行。  
翻紅命令: `/usr/bin/python3 /tmp/lumos-seat-work/code-test-quality-native-push/resource/repro_capture_sigterm.py`  
重現結果: `{"capture_returncode": -15, "child_alive_after_sigterm": true}`，rc=1。

finding ID:r2  
severity: major  
blocking: 是  
引句:「proc = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=timeout)」  
file: `governance/eval/test_quality_handbook.py:234`  
模型逾時只殺直接 `claude` 程序；其 worker 可繼續存活，逾時回報後仍可能持續工作或消耗額度。  
翻紅命令: `/usr/bin/python3 /tmp/lumos-seat-work/code-test-quality-native-push/resource/repro_run_model.py`  
重現結果: `{"run_model_returncode": null, "worker_alive_after_timeout": true}`，rc=1。

finding ID:r3  
severity: major  
blocking: 是  
引句:「out, err = stdout.read(LIMIT + 1), stderr.read(LIMIT + 1)」  
file: `scripts/test_quality.py:163`  
10 MiB 上限在子程序結束後才檢查；執行期間 `TemporaryFile` 可無界增長。正常但輸出繁多的可信測試可先耗盡暫存磁碟，之後才被判 invalid。  
翻紅命令: `/usr/bin/python3 /tmp/lumos-seat-work/code-test-quality-native-push/resource/repro_output_limit.py`  
重現結果: 限制為 10,485,760 bytes，但程序先成功寫入 33,554,432 bytes，rc=1。

finding ID:r4  
severity: major  
blocking: 是  
引句:「code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),」  
file: `scripts/lumos:44162`  
`governance/eval/results/` 未被視為卷證目錄；固定 range 中 773 份 `.txt/.xml/.log/.trx/.zip` 被當成 code seed，之後逐檔執行 diff 與 ranked impact，使 push 前閘長時間無輸出。  
file: `scripts/lumos:44042`  
file: `scripts/lumos:44225`  
翻紅命令: `/usr/bin/python3 /tmp/lumos-seat-work/code-test-quality-native-push/resource/repro_impact_attachments.py`  
重現結果: 875 份結果附件中 773 份被收為 code seed：641 txt、86 XML、32 log、7 trx、7 zip，rc=1。固定 range 的 20 秒受限重現仍未產生 stdout；`repro_impact_timeout.py` rc=1。

授權合約：已讀,無 finding。新增 vendored sidecar 均有 SPDX，且未將 LICENSE／COPYING／NOTICE 加入 `_VENDORED_TOOLKIT`。

歷史 fixture、HOME 還原與鎖 context：已讀,無 finding。

對應 CLI 子集 `scripts/test_test_quality_cli.py`：22 tests 全綠；現有 timeout 測試只驗 invalid reason，未驗子程序清理或執行期間輸出界線。

總結：最嚴重 severity: major；blocking: 4 條