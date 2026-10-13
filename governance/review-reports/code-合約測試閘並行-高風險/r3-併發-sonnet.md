severity: minor

我在臨時目錄用真的 `scripts/lumos`(固定在 54b01b1a)搭了最小重現,連跑 20 次。修補在正常的失敗路徑和單次中斷下都收得乾淨,沒有殘留程序。只剩一個窄窗口,發生在同批有一支測試「已 fork、尚未登記」的時候。

1. 收尾最多只等 2 秒,等不到的程序在程式結束後成孤兒(第二次 Ctrl-C 與 Popen 卡超過 2 秒兩種觸發)
severity: minor
blocking: 否
引句:「deadline = _time_mod.monotonic() + 2」
file: `scripts/lumos:48233`(`_settle_and_reap`),`scripts/lumos:48309`(`_BtProcs.append`)
1. 時序 A,第二次中斷:同批已有測試被領走,Popen 已 fork 但還沒走到 `started.append`。使用者按第一次 Ctrl-C,主流程進 `except BaseException`,`_settle_and_reap` 先 `procs.reap()` 立好 `_stop`,再進 `while ... sleep(0.02)` 等那支登記。此時第二次 Ctrl-C 在等待迴圈裡丟出 KeyboardInterrupt,直接跳出 `_settle_and_reap` 並結束程式。daemon 工作執行緒隨程序消失,`_BtProcs.append` 的「立標記後當場收」永遠沒機會跑,那支測試的程序群組留下當孤兒。
2. 時序 B,Popen 卡住:不用 Ctrl-C,只要登記延遲超過 2 秒,2 秒期限到就放棄等待,之後同樣因程式結束而漏收。
3. 重現(把 `subprocess.Popen` 包一層,讓 `t_slow2` 在 fork 後多睡一段才回傳):
   - 時序 A:睡 1.0 秒,0.5 秒與 0.8 秒各送一次 SIGINT。結果丟出 KeyboardInterrupt,`pgrep -f "job.sh t_slow"` 殘留 1 支,1 秒後仍在。
   - 時序 B:一支測試出錯,另一支 fork 後延遲 3.0 秒才登記。0.5 秒與 1.5 秒的延遲都收乾淨(leftover 0),3.0 秒殘留 1 支。
4. 不加人為延遲時,「fork 後到 append」之間只有幾行,我跑 20 次沒有撞到。所以只標 minor,是機率與負載問題,不是結構性漏洞。
5. 歸因:有證據的修復回歸否定;這是修補新增的等待機制自帶的上限,r2 修補前同一窗口也漏收(沒有任何等待),屬原有漏查。修前版本沒實測,所以「修前一樣會漏」這點是未判定。
6. 修法方向(不附程式):等待迴圈外層用 `try/finally` 或遮蔽第二次中斷,再保證 `reap()` 在 `finally` 內再跑一次;或讓 Popen 與登記在同一把鎖內。

## 三問
1. 原問題的修復效果:
   - 單次錯誤:`err` 模式下,第 1 支丟 OSError、其餘 5 支 `sleep 30 &; sleep 30`,連跑 10 次,殘留皆為 0。
   - 單次中斷:`slow` 模式 1 秒後送一次 SIGINT,連跑 10 次,殘留皆為 0。
   - 登記延遲 0.5 秒與 1.5 秒也收乾淨。
   - 前面一輪我的假測試把 slow 判斷寫錯,job.sh 實際只睡 1 秒,所以那 20 次結果作廢;我已修正 pattern(`t_slow*`)與錯誤項排序,再跑才得到上面的數字。
2. 相鄰呼叫路徑:
   - `_kill_run` 不給 `started` 時行為不變。
   - 同時跑四支真實綁定測試(`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`、`t_reinject_preserves_outside`、`t_bound_tests_parallel_matches_sequential`),全部 rc=0,沒有互踩。
   - 測試檔裡固定路徑 `/tmp/gh-state` 只在沒設 `GH_STATE` 時才用,有用到它的測試都各自設了 `GH_STATE`,所以設 4 不會踩到。
3. 新發現案例的修前修後:上面第 1 條。修前版本未實測,標未判定。

## 其他鏡頭判定(只讀程式,未重現)
- pid 重用誤殺:`_bt_kill_proc` 先 `proc.poll()`,沒結束才 `getpgid`。理論上 poll 之後、`getpgid` 之前,工作執行緒的 `communicate` 可能已把它收走並重用 pid。窗口是微秒級,而且需要 pid 繞圈;未重現,不立 finding。
- 主流程等待:`while th.is_alive() and not errs` 在 errs 出現後逐條跳過,不會死等。
- tally 計數:Popen 已登記後才丟的例外(例如 communicate 丟非逾時例外)會讓 `len(procs)` 與 `failed` 雙算,`_settle_and_reap` 可能提早返回。目前找不到實際觸發路徑,不立 finding。
- leader 已結束但同群組還有背景孫程序時,`poll() is not None` 會直接略過不收。循序跑一樣如此,屬原有行為。

## 圖譜鏡頭
- `Systems/guard-kill`:`_kill_run` 只多一個預設 `None` 的選用參數,rc 優先序與 `--json` 純度不受影響。
- `Systems/bound-tests-gate`:任一紅/懸空/unproven 仍 blocked rc1,結果仍照原項目順序組;secs 改牆上時間不影響判紅綠。這份 diff 沒破壞該節點的行為或合約。
- 其餘固定席(測試假綠形態、lumos-cli-read、lumos-cli-lifecycle、design-loop、loop-convergence-recording、pitfalls-code-loop 等)與這份 diff 無實質牽連,不逐條答。

## 已驗主張與未驗範圍
- 已驗:
  - 單次錯誤收乾淨(入口 `h.py err`,預期殘留 0,實測 0)。
  - 單次中斷收乾淨(入口 `h.py slow`,預期殘留 0,實測 0)。
  - 登記延遲 0.5 秒與 1.5 秒收乾淨。
  - 四支真實測試同時跑全綠。
- 未驗:修前版本的對照結果、pid 重用、雙算 tally。

臨時目錄已刪除,殘留程序為 0。

總結:最高等級 minor
