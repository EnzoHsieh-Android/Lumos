severity: minor

## 1. 其中一支開不起來時,同批已開跑的兄弟測試會變成孤兒,而呼叫端可能繼續往下走
severity: minor
blocking: 否
引句:「已開跑的子程序在自己的程序群組裡跑到自己的逾時為止(跟循序時按 Ctrl-C 一樣成為孤兒),不卡住前景。」
file: `scripts/lumos:48151`(`_run_bound_tests`)
file: `scripts/lumos:13317`(修正關卡呼叫端,`except Exception` 之後繼續往下走)

1. 時序:四個工作執行緒各自在跑一支(各自的 `_kill_run`)。其中一條因為 Popen 失敗丟例外,`errs.append(e)`。主流程在 0.1 秒內看到並 `raise errs[0]`。其他三條的 `_kill_run` 還卡在 `proc.communicate`,子程序在獨立 session 裡繼續跑。
2. 實測:我在模擬器裡讓一條丟 OSError,其他三條各睡 8 秒。主流程 0.33 秒丟出例外。之後 `ps` 看到三個 ppid=1 的子程序,存活到各自結束。
3. 循序版的差別:出錯那支之前的測試都已收尾,不會留任何活著的子程序。所以「出錯 → 殘留孤兒」是並行才有的新行為。「中斷 → 孤兒」才是文件寫的、與循序相同的那一種。
4. 實際影響:修正關卡的 `except Exception` 會把例外轉成 `bt={"status":"error"}` 然後繼續跑。孤兒測試仍在那棵隔離工作樹或 repo 裡跑,同時工作樹被清掉。孤兒的 `gctl-run-*` 暫存根沒有 `.finished` 標記,要一天後才會被修剪。
5. 殘留檔實測:我試過在工作樹被移除的當下,孤兒還在往該目錄寫檔,沒有留下殘骸目錄。所以只有孤兒存活這件事確定,殘骸 ⚠ 未能重現。
6. 歸因:有證據的原有漏查。修前(d3ac862a)與修後(3daa00a8)的並行路徑都一樣,出錯時沒有收掉兄弟。這是並行功能本身的設計,不是這次修補造成的。可能的修法是出錯時對已開跑的程序群組補送 SIGTERM,但那會改成「出錯也殺子程序」的語意,所以只列為 minor。

## 三問
1. 原問題的修復效果:
   - 等待不空轉:16 條並行、每條睡 3 秒,主程序 CPU 0.069 秒、牆上 3.14 秒。
   - 出錯快停:例外 0.33 秒內浮出,程式 0.42 秒內結束,沒有卡住或印錯。
   - 中斷停派:`t_bound_tests_parallel_interrupt_stops_dispatch` 通過。
   - 單調時鐘:`t_bound_tests_secs_monotonic` 通過。
   - `-k t_bound_tests_parallel` 41 支全綠。
2. 修補處的相鄰路徑:
   - 結果組裝:`plan` 與 `seen` 在最後照原項目順序組,tails 也照寫。
   - 去重:同一個 key 只跑一次。
   - 讀寫排序:我排了 `errs`、`seen`、`todo` 的最壞交錯。工作執行緒設 `errs` 後才 return,主流程結束迴圈後再查 `errs`,所以不會漏。
   - 兩處未驗:`th.start()` 迴圈在 `try` 之外,SIGINT 在這個毫秒級窗口到達時不會通知工作執行緒,我沒能重現。呼叫端接住 KeyboardInterrupt 並繼續的情況,我也沒找到實例。
3. 同一案例的修前修後:
   - 孤兒案例兩版相同(見 finding 1)。
   - 修前的空轉與出錯延遲案例,我沒有另外建修前的環境重跑。修前證據未判定,原因是 `d3ac862a` 的實跑環境沒有建,只做了修後行為驗證。

## 資源與併發的實測
- 同時 8 支不同的 `scripts/test_lumos.py -k`:全 rc0,repo 無寫入。
- 同時 4 支重測試(t_impact、t_pitfalls、t_spec_gate、t_code_loop):全過。
- 同時 8 支(含 60 秒的 `t_bound_tests_parallel_config_values`):全過,該支 60.8 秒,離 180 秒上限仍有餘裕(本機 10 核)。
- 隔離做法:`_isolate_environment` 每個程序用 `mkdtemp` 建自己的暫存根、假 HOME 與 `.gitconfig`。修剪只碰有 `.finished` 或超過一天的目錄,所以同時跑不會互踩。
- 驗證邊界:只有 10 核機器。CI 小機器上並行 4 的逾時邊際沒有實測。

## 圖譜鏡頭
- guard-kill:`_kill_run`、`_kill_cap` 本體沒改,rc 優先序與 `--json` 純度合約不受影響。
- bound-tests-gate:
  - 判定仍由 `_run_bound_tests` 逐項依 `tail` 判,unproven/unfilterable 仍擋,沒破壞合約。
  - secs 改牆上時間,不影響判定。
  - 記帳多的 `secs_kind` 是新增欄位。
- 測試假綠形態:新測試 S7 有「INTERRUPTED」前置斷言,現場成立有證明。
- 其餘固定席(lumos-cli-read、lumos-cli-lifecycle、design-loop 等)與此 diff 無行為交集。
- 我的實驗目錄已刪除,沒有留下殘留程序。

總結:最高等級 minor
