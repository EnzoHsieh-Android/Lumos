severity: minor

只改了 FLK-1、FLK-2、FLK-3 的引句,改成從審材逐字複製、保留全形標點的單行。其餘判斷與敘述沒動。FLK-1 敘述裡原有一段 ⚠ 說明,是針對舊引句寫的,現在不適用,所以刪掉。FLK-4 的引句本來就逐字吻合,維持原樣。

測試仍真的測到「逾時後清掉 worker」。我跑了 `-k test_model_timeout_stops_worker_without_paid_call`,結果 `Ran 1 test in 5.023s OK`。5 秒預算確實用完,所以是真逾時。假模型睡 60 秒,還是必然逾時。後面的 `alive(pid)` 斷言(`governance/eval/test_test_quality_handbook.py:160-171`)沒動。

**問 1 分層與依賴方向:對齊。** diff 只動測試參數與同節點筆記,沒有新依賴或跨層呼叫。測試仍經 `ev.run_model` 進入,筆記也寫在管這支檔的 Systems 節點(`Systems/test-quality-handbook.md`)。沒有 finding。

**問 2 命名、註解與說明寫法:有兩處不一致。**

ID: FLK-1
severity: minor
blocking: false
引句:「[防回歸:t_test_quality_handbook_controls]。預算放寬到 5 秒，假模型睡 60 秒仍必然逾時；」
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:70`
敘述:同節點其他三條 PITFALL 的 `[防回歸:]` 都指到實際測試函式名。例如第 57 行附近的 `test_model_timeout_stops_worker_without_paid_call`、第 66 行的兩個 `test_...`、第 68 行的 `test_model_output_over_limit_is_invalid_session_not_abort`。這條改指到總入口 `t_test_quality_handbook_controls`(`scripts/test_lumos.py:78644`)。該入口只是把手冊控制接進推送前測試器,不是被修的那個測試。寫法不一致,而且綁定的粒度比別條粗。

ID: FLK-2
severity: minor
blocking: false
引句:「# 全套並行時直譯器啟動可能超過 1 秒，worker 來不及登記就被收掉；」
file: `governance/eval/test_test_quality_handbook.py:154`
敘述:這是 `test_test_quality_handbook.py`、`scripts/test_test_quality_cli.py`、`scripts/test_test_quality_scan.py` 裡唯一一條解釋逾時預算的行內註解。其他逾時參數(cli 的 `timeout=1/10/20`、scan 的 `BACKEND_TIMEOUT = 2`)都不附註解,理由只寫在斷言訊息裡,例如 `scripts/test_test_quality_scan.py:288`。此處的理由已經寫進 PITFALL,註解與筆記重複。寫法有出入,結構沒問題。

**問 3 有沒有引入第二種做法:有,同族測試沒一起處理。**

ID: FLK-3
severity: minor
blocking: false
引句:「# 假模型睡 60 秒，5 秒預算仍一定逾時。」
file: `governance/eval/test_test_quality_handbook.py:242-252`
敘述:同檔 `test_model_timeout_keeps_partial_stream` 呼叫 `ev.model_command([str(fake)], self.root, 1)`,預算仍是 1 秒。它的假模型同樣靠直譯器啟動後才 print `init` 再睡 60 秒,預算同樣貼著啟動時間。若啟動超過 1 秒,partial 內容就是空的,`assertIn('"subtype":"init"', partial)` 會偶發紅。這與被修的測試是同一個 flake 形狀。結果同檔同類控制出現兩種預算(5 秒與 1 秒),又沒有理由說明。

ID: FLK-4
severity: minor
blocking: false
引句:「[根因:逾時預算貼著程序啟動時間]」
file: `scripts/test_test_quality_cli.py:428-438`
敘述:`test_timeout_after_streams_close_keeps_partial_output` 對 `run_capture_command(command, 1)` 用 1 秒預算。它的假命令是 `python -c "...print('partial')...time.sleep(30)"`,同樣靠解譯器啟動後才印出 partial。FLK-3 同一個根因,範圍在 cli 測試而不是手冊測試,所以標 ⚠ 判不準是否該算本次範圍。`scripts/test_test_quality_cli.py:268-273` 的 `test_timeout_not_detection` 只斷言逾時分類,不依賴啟動,不受影響。`scripts/test_test_quality_scan.py:271-288` 用 `BACKEND_TIMEOUT = 2` 並放寬到 `limit = 6`,是另一種策略(上限預算加實測時間斷言),屬既有做法,不算本次引入。

不對齊共 4 條,其中 major 0 條
總結最嚴重 severity: minor;blocking: 0
