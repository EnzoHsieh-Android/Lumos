severity: minor

1. 中斷路徑的「收掉子程序」沒有會翻紅的測試
severity: minor
blocking: 否
引句:「        except BaseException as e:   # Ctrl-C 只會丟在主流程:先讓工作執行緒停止派新的,再往外丟」
這條 finding 對應 `scripts/lumos` 的 `_run_bound_tests` 中斷分支(修補新增 `_settle_and_reap()`),和 `scripts/test_lumos.py` 的 `t_bound_tests_parallel_interrupt_stops_dispatch`。
1. 輸入:同時跑時在測試開跑後送 SIGINT。
2. 我在臨時副本把 `_BtProcs.append` 的 stop 判斷固定為 False、`reap()` 改成空清單,等於中斷和出錯路徑都不收子程序。
3. 結果:`t_bound_tests_parallel_error_stops_fast` 三次都紅(兩種排序各一條),所以出錯路徑有保護。
4. 同一份副本跑 S7 `t_bound_tests_parallel_interrupt_stops_dispatch` 照樣全綠(開跑 2 支)。S7 只數開跑了幾支,不查孤兒。
5. 修補差異的 behavior_cases 第 1 條寫「出錯或中斷」都收掉,證據只列 S5(出錯)。中斷路徑的收尾因此沒有行為證據。
6. 歸因:有證據的原有漏查。S7 在修補前後都不查孤兒,不是修補造成的回歸。
7. 補法:S7 在送 SIGINT 前先斷言 `pids/` 非空,中斷後像 S5 一樣輪詢 `_bt_alive_pids` 要全空。

2. S5 缺「現場成立」的前置斷言
severity: minor
blocking: 否
引句:「            check("並行 S5(%s):同批已開跑的慢測試被收掉,不留孤兒" % name, not _bt_alive_pids(d), _bt_alive_pids(d))」
1. 兩個工作執行緒中,出錯那支(`bad`,root 不存在,Popen 立刻丟 `OSError`)若先設好 `errs`,另一條執行緒會在 `if errs: return` 直接退出。
2. 這時沒有任何慢測試開跑,`pids/` 是空的,「不留孤兒」空轉通過。
3. 沒有 `pids/` 非空的前置斷言。這違反 `Systems/測試假綠形態` 的 INVARIANT:還原翻紅釘要配一條證明現場成立的前置斷言。
4. 我連續三次變異都紅,所以多數情況下現場是成立的。但「出錯那支排第一」這個排序在調度偏斜時會空轉,且它的 `took < 5` 斷言也同樣空轉。
5. 歸因:修補新增的測試弱點(未判定是否實際發生過)。
6. 補法:每個排序都先 `check(len(list((d/'pids').iterdir()))>=1)`。因為被收掉的程序可能還沒寫 pid 檔,這個前置斷言本身可能在快速收掉時假紅,要先留 pid 檔再收,或在假測試啟動後再放行錯誤那支。

我審了但沒找到出錯輸入的部分:
- `_BtProcs.append` 與 `reap` 的鎖:`stop` 在鎖內讀,`_bt_kill_proc` 在鎖外執行,沒有死鎖。
- `_bt_kill_proc` 的各個分支:
  - `poll()` 已結束就直接回傳。
  - `getpgid` 丟 `ProcessLookupError` 時退回 `proc.kill()`,而 `Popen.kill` 內部會先 `poll`,不會殺到重用的 pid。
  - Windows 的 `AttributeError` 在 try 內,會被接住。
  - 模組頂層有 `import os`。
- `_settle_and_reap` 的等待條件 `len(procs)+failed >= taken`:
  - 每個領走的工作要嘛註冊程序、要嘛進 `failed`。
  - 唯一算重的情況是 `_kill_run` 在 `started.append` 之後才丟例外,此時條件會提早成立。
  - 但「領走了工作但還沒登記」的那條執行緒之後登記時,`_BtProcs` 會當場收掉,只剩主程序在這個瞬間結束的極窄窗口。
  - 我給不出一個實際會觸發的輸入,所以不標。
  - 等待上限固定 2 秒,不會死等。
- `_kill_run(started=None)` 的其他呼叫者(`guard kill` 等):`started` 預設 None,只多一個 `is not None` 判斷,逐字不變。
- `parallel: 1.0`:`type(v) is int and v == 1` 讓 `1.0`、`True` 會提醒,整數 1 不提醒,與測試值一致。
- 序列路徑:`procs` 只被 append、從不 reap,與修補前行為相同。

三問:
① 原問題(出錯時同批子程序變孤兒)的行為證據。
- 在臨時副本拿掉 `_BtProcs.append` 的 stop 判斷與 `reap`,S5 兩種排序都紅。
- 修補後在本機 `python3.14 scripts/test_lumos.py -k bound_tests_parallel` 結果是 46 passed、0 failed。
- 中斷路徑沒有行為證據(finding 1)。

② 修補處的相鄰路徑:
- 正常路徑沒有呼叫 `reap`,結果不受影響。
- 循序路徑只多 append。
- 中斷與出錯共用 `_settle_and_reap`。
- `_one` 傳 `started=procs` 給每支,與設計一致。

③ 新發現案例在修前、修後各是什麼結果:
- 中斷後孤兒:修前(3daa00a8)的 `except BaseException` 分支沒有收尾程式,理論上會留孤兒。我沒有另跑修前版本做行為對照,標未判定,原因是缺修前證據。
- 修後有 `_settle_and_reap`,但如上沒有會翻紅的測試。

案例證據(正向主張):
- claim:出錯時同批慢測試被收掉。
- input:S5 兩種排序。
- expected:`pids/` 內的 pid 在 2 秒內都不存活。
- case_source:修補差異。
- after:命令 `python3.14 scripts/test_lumos.py -k bound_tests_parallel` 通過。
- comparison:變異版(無 reap、無當場收)三次皆紅,等於修前行為。
- attribution:有證據的修復有效。

圖譜鏡頭(固定席逐條判定):
- guard-kill 的 INVARIANT(rc 優先序、`--json` 純度):不影響。`_kill_run` 只多選用參數,不傳時邏輯不變,輸出與回傳形狀不變。
- 測試假綠形態:不衝突。我在 finding 2 引用它的規則,指 S5 缺前置斷言。
- lumos-cli-read、lumos-cli-lifecycle:不影響,沒動搜尋與 re-inject。
- bound-tests-gate 的 INVARIANT(任一紅、懸空、不合法、unfilterable 就 rc1):不影響。`results` 的組裝與順序沒動。
- design-loop、loop-convergence-recording、pitfalls-code-loop 與其他只列名的節點:未發現牽連。

角色鏡頭:派工沒附角色卡,略過。

清理:我的臨時目錄 `/tmp/lumos-seat-work/code-合約測試閘並行-高風險/正確性-sonnet/` 已刪;變異期間留下的測試子程序已不在。repo 根只做了讀取與跑測試,沒有寫入。

總結:最高等級 minor
